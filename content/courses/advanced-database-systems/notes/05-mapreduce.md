# 05 MapReduce: model, patterns, cost

> **Sourcing.** Dean and Ghemawat, OSDI 2004 [S16]; Leskovec, Rajaraman,
> Ullman, *Mining of Massive Datasets* ch. 2 [S17] (the cost model, relational
> operators, matrix multiplication); Afrati et al. [S18] (lower bounds); Hadoop
> tutorial [S23]. Block-2 emphasis (cost model with r and q, joins, matrix
> multiplication, combiners, failures) from the 2026 block-2 cheat sheet on VoWi
> [S4] and the 2020 exam [S6]. Everything below runs in `mapreduce.py` and
> `mr_algorithms.py`.

## Setting

- **Cluster**: many commodity machines (nodes) in racks; failures are normal.
- **Distributed file system** (GFS, HDFS): huge files cut into large **chunks**
  (HDFS blocks 64 or 128 **MB**) replicated (default 3x, on different racks).
  A master (**NameNode**) holds metadata (which chunk where); **DataNodes** store
  chunks [S17 2.1], [S23].
- **Data locality**: the scheduler runs a map task on (or near) a node that holds its chunk.

## The model [S16 2], [S17 2.2]

$$\text{map}: (k_1, v_1) \mapsto [(k_2, v_2)],\qquad \text{reduce}: (k_2, [v_2]) \mapsto [v_3].$$

1. **Split** the input into $M$ pieces; one **map task** per split calls `map` on each record.
2. **Partition**: each output pair goes to reduce task $\text{hash}(k_2) \bmod R$ [S16 3.1]; map output is written to the mapper's **local disk**, one region per reducer.
3. **Shuffle and sort**: each reduce task pulls its region from every mapper and sorts by key, so all values of a key are adjacent.
4. **Reduce**: one call per key with the full value list; output to the DFS.

The user writes `map` and `reduce` (and optionally a combiner and a
partitioner); the framework does parallelisation, scheduling, shuffle and
fault tolerance.

### Worked example: word count (`mapreduce.word_count`)

```
map(line):        for w in line.split(): emit(w, 1)
combine(w, cs):   emit(w, sum(cs))           # per map task, before the shuffle
reduce(w, cs):    emit(w, sum(cs))
```

Input: 12 lines `"a a a b"`, `"a b b"`, `"a a c"` repeated 4 times, 3 map tasks
of 4 lines each. Map output 40 pairs. **Without combiner** all 40 cross the
network and the reducer for `a` receives 24 ones. **With combiner** each map
task sends one pair per distinct word it saw: 3 tasks x 3 words = **9 pairs**;
the largest value list shrinks from 24 to 3 (`test_combiner_reduces_shuffle_not_result`).

## Combiners [S16 4.3]

- A combiner is a local reduce on one map task's output, run before the shuffle.
  It moves part of the **reduce** work to the map side, cutting communication.
- Valid only if applying it any number of times (0, 1, many) cannot change the
  result: in practice the reduce function is **associative and commutative**
  and the combiner's output type equals the map's output type.
- **Average** is the classic counterexample: $\text{avg}(1,2,3,6) = 3$, but the
  average of the per-task averages $\text{avg}(2, 6) = 4$. Fix: emit $(x, 1)$,
  combine to $(\sum x, \sum c)$, divide in the reducer (`mapreduce.mean_by_key`).
- Combiners do not remove duplicates across map tasks: a dedup combiner in a
  projection still leaves one copy per task that saw the tuple.

## Failures [S16 3.3, 3.6]

| failure | what is redone | why |
|---|---|---|
| map worker | **all** its map tasks, completed or not | their output sat on its local disk |
| reduce worker | only its **in-progress** reduce tasks | completed output is in the replicated DFS |
| master | the job is restarted (or resumed from a checkpoint) | single point of coordination |
| straggler (slow task) | a **backup copy** near the end; first to finish wins | tail latency |

Re-execution is correct because map and reduce are deterministic functions of
their input (`run_job(..., fail_map={...})` gives the same result).

## Cost model [S17 2.5-2.6]

- **Communication cost** of a task = size of its input; of an algorithm = sum
  over all tasks. In practice: the number of key-value pairs **shuffled**
  (the map input is read locally).
- **Replication rate** $r$ = map output pairs / input records.
- **Reducer size** $q$ = maximum length of one key's value list (must fit in
  memory; small $q$ = more parallelism).
- Trade-off: making $q$ small forces inputs to be sent to many reducers, so $r$
  grows. Wall-clock time is the slowest task: skewed keys ("hot keys") hurt.

## Relational algebra in one round [S17 2.3.3-2.3.9]

| operator | map emits | reduce | notes |
|---|---|---|---|
| $\sigma_C(R)$ | $(t, t)$ if $C(t)$ | identity or none | map-only suffices |
| $\pi_L(R)$ | $(t[L], t[L])$ | emit key once | reducer removes duplicates |
| $R \cup S$ | $(t, t)$ | emit once | |
| $R \cap S$ | $(t, R)$ / $(t, S)$ | emit $t$ if both tags | needs a reducer to see both |
| $R - S$ | $(t, R)$ / $(t, S)$ | emit $t$ if only tag R | |
| $\gamma_{A, \text{agg}(B)}(R)$ | $(a, b)$ | $(a, \text{agg}(bs))$ | combiner ok for sum/min/max/count |
| $R(A,B) \bowtie S(B,C)$ | $(b, (R, a))$ / $(b, (S, c))$ | pair every R-value with every S-value | communication $|R| + |S|$ |

**Broadcast (map-side) join**: if $S$ fits in memory, ship it to every map task,
build a hash table, probe with $R$: no shuffle, but traffic $|S| \times M$
(`mapreduce.broadcast_join`). **Co-partitioned join**: if $R$ and $S$ are
already partitioned by $B$ with the same function, join locally, no shuffle.

## Matrix multiplication [S17 2.3.9-2.3.10, 2.6.7]

$P = MN$, $n \times n$, $p_{ik} = \sum_j m_{ij} n_{jk}$.

- **Two rounds**: job 1 is the join on $j$: map $m_{ij} \mapsto (j, (M, i, m_{ij}))$,
  $n_{jk} \mapsto (j, (N, k, n_{jk}))$; reduce emits $((i,k), m_{ij} n_{jk})$.
  Job 2 groups by $(i,k)$ and sums (combiner allowed).
- **One round**: map $m_{ij} \mapsto ((i,k), (M, j, m_{ij}))$ for **all** $k$, and
  $n_{jk} \mapsto ((i,k), (N, j, n_{jk}))$ for all $i$. Reducer $(i,k)$ gets row $i$ of
  $M$ and column $k$ of $N$: $r = n$, $q = 2n$ (`test_matmul_against_numpy`).
- With $g \times g$ blocks per reducer: $r = g$, $q = 2n^2/g$, so $r = 2n^2/q$; and
  **any** one-round algorithm needs $r \ge 2n^2/q$ [S17 2.6.7], [S18]: a reducer
  with $q$ inputs covers at most $q^2/(4n^2)$ outputs, and all $n^2$ outputs must be covered.
- Total communication: one round $4n^4/q$; two rounds (blocked) $3\sqrt2\, n^3/\sqrt q$,
  smaller for $q < 8n^2/9$; near the minimum $q = 2n$ the two-round algorithm
  wins by a factor $O(\sqrt n)$ [S17 2.6.7]. Both do the same $O(n^3)$ arithmetic.

## Top-k (pattern)

Each map task keeps a local top-k (a heap) and emits it under one constant key;
a single reducer merges $M \cdot k$ candidates instead of all $N$ records.

## Limits (why Spark, note 06)

Two phases only; an iterative algorithm is a chain of jobs, each writing its
full result to the replicated DFS and rereading it. Batch only.

## Pitfalls

- Combiners push *reduce* logic to the map side, not map logic to the reducer.
- A map-only job has zero shuffle but may still ship data (broadcast).
- $R = 1$ reducer: globally sorted output, no parallelism; one reducer per key: huge overhead.
- HDFS block size is megabytes, not kilobytes.

## Exam-style questions

1. *Design one-round MapReduce for $R - S$ and give its communication cost.* Map: $(t, \text{'R'})$ or $(t, \text{'S'})$; reduce: emit $t$ iff the tag list contains only 'R'. Cost $|R| + |S|$.
2. *Can a combiner compute the per-key maximum? The median?* Max yes (associative, commutative); median no.
3. *A map worker dies after its tasks completed but before the reducers fetched everything. What is rerun?* All its map tasks; reducers read the new output.
4. *One-round matrix product, $n = 1000$, reducer size $q = 2 \cdot 10^5$. Minimum replication rate?* $r \ge 2n^2/q = 2 \cdot 10^6 / 2\cdot 10^5 = 10$.
5. *$R$ has $10^9$ tuples, $S$ has $10^4$, $M = 500$ map tasks. Reduce-side or broadcast join by communication?* Reduce-side $\approx 10^9$; broadcast $10^4 \cdot 500 = 5 \cdot 10^6$: broadcast.

## Code

- `mapreduce.run_job` (phases, `JobStats` with `shuffled`, `replication_rate`, `max_reducer_size`, `fail_map`), `mapreduce.word_count`, `mapreduce.inverted_index`, `mapreduce.mean_by_key`, `mapreduce.reduce_side_join`, `mapreduce.broadcast_join`.
- `mr_algorithms.selection`, `mr_algorithms.projection`, `mr_algorithms.union`, `mr_algorithms.intersection`, `mr_algorithms.difference`, `mr_algorithms.group_by`, `mr_algorithms.matmul_one_round`, `mr_algorithms.matmul_two_rounds`; tests against pandas and numpy.
