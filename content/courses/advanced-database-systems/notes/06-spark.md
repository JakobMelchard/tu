# 06 Spark: RDDs, lineage, stages, DataFrames

> **Sourcing.** Zaharia et al., NSDI 2012 [S19] (RDDs, lineage, narrow/wide
> dependencies, stages, PageRank); Spark RDD programming guide, Spark 4.2 docs
> [S20]; Armbrust et al., SIGMOD 2015 [S21] (Spark SQL, Catalyst); Spark SQL
> guide and tuning page [S22]. Block-2 emphasis (lazy DAG, narrow vs wide,
> stages, reduceByKey vs groupByKey, DataFrame/SQL equivalences) from the 2026
> cheat sheet [S4] and the 2020 exam [S6]. **Real Spark is not available here**
> (no pyspark in the venv, no Java runtime): `spark_like.py` imitates the
> semantics and the PySpark snippets below are not executed.

## Why Spark

MapReduce materialises every job's output in the replicated DFS. Iterative
algorithms (PageRank, k-means, gradient descent) and interactive queries reread
the same data every round. Spark keeps working sets **in memory** across
operations and recovers from failures by **recomputation** instead of
replication: up to 20x faster than Hadoop on iterative ML and graph jobs [S19].
For a single pass over data larger than memory the advantage is small.

## RDDs [S19 2]

A **Resilient Distributed Dataset** is an immutable, partitioned collection
created only by deterministic, coarse-grained **transformations** of stable
storage or other RDDs. Each RDD records its **lineage**: parents, the function,
and the partitioner. A lost partition is rebuilt from lineage.

Architecture [S20]: the **driver** runs `main` and holds the `SparkContext`;
**executors** on worker nodes run **tasks**, one task per partition per stage.
An **action** triggers a **job**; a job is split into **stages** at shuffles.

| transformations (lazy, return an RDD) | actions (run a job, return to the driver or write) |
|---|---|
| `map`, `flatMap`, `filter`, `mapValues`, `union`, `sample` | `collect`, `count`, `first`, `take(n)`, `reduce(f)`, `fold`, `aggregate` |
| `groupByKey`, `reduceByKey`, `aggregateByKey`, `distinct` | `countByKey`, `saveAsTextFile`, `foreach` |
| `join`, `cogroup`, `sortByKey`, `partitionBy`, `repartition` | |

`reduceByKey` is a *transformation* (returns an RDD); `reduce` is an *action*.

## Narrow vs wide dependencies [S19 4]

- **Narrow**: each parent partition is used by **at most one** child partition
  (`map`, `filter`, `flatMap`, `mapValues`, `union`, `join` of co-partitioned inputs).
  Narrow transformations are **pipelined** inside one stage on one node, and a
  lost partition needs only its own parent partitions.
- **Wide**: a parent partition feeds **many** child partitions (`groupByKey`,
  `reduceByKey`, `distinct`, `join` of differently partitioned inputs,
  `partitionBy`, `sortByKey`). Requires a **shuffle**, ends a stage; recovery
  may need all parent partitions.
- **Stages**: walk the lineage from the final RDD; every wide dependency starts
  a new stage. Number of stages = 1 + number of shuffles on the longest path
  (`RDD.num_stages`).

### Worked example: word count (`spark_like.demo`)

```python
lines  = sc.parallelize(["to be or not", "to be", "that is the question"], 2)
counts = lines.flatMap(str.split).map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b)
counts.collect()
```

After the three transformations nothing has run (0 partitions computed). Lineage:

```
reduceByKey          narrow <- shuffle<reduceByKey>   (stage 2)
shuffle<reduceByKey> wide   <- map                    (stage boundary)
map                  narrow <- flatMap                (stage 1, pipelined)
flatMap              narrow <- parallelize
```

2 stages. Result `be 2, to 2`, the other six words 1. `reduceByKey` combines
per partition before the shuffle: **8** records shuffled; `groupByKey` shuffles
all **10** pairs. Prefer `reduceByKey`/`aggregateByKey` for associative
aggregations [S20].

## Persistence and partitioning

- `rdd.cache()` = `persist(MEMORY_ONLY)` [S20]: kept after the first action;
  worth it only if the RDD is used by at least two actions.
- `partitionBy(HashPartitioner(n))` fixes where each key lives. `mapValues` and
  `filter` keep the partitioner; `map` drops it (it may change keys).
- **Co-partitioned join**: both inputs share a partitioner, so partition $i$ of
  the result needs only partition $i$ of each side: narrow, no shuffle
  (`test_join_narrow_when_co_partitioned`).
- **PageRank** [S19 3.2.2]: partition `links` once and cache it; each iteration
  joins `links` with `ranks` (narrow) and shuffles only the contributions.
  [S19] updates $r \leftarrow \alpha/N + (1-\alpha)\sum c_i$ ($\alpha = 0.15$);
  `spark_like.pagerank` uses the same update scaled by $N$ (ranks start at 1,
  $r \leftarrow 0.15 + 0.85 \sum c_i$) and matches networkx times $N$.

## DataFrames, Spark SQL, Catalyst [S21], [S22]

A **DataFrame** is a distributed table with a schema (named, typed columns).
DataFrame calls and SQL strings both build a **logical plan**; nothing runs
until an action. **Catalyst** compiles it in four phases [S21, Figure 3]: (1) analysis
(resolve names and types), (2) logical optimisation (rule-based: predicate
pushdown, constant folding, projection pruning), (3) physical planning
(cost-based choice, e.g. broadcast hash join when a side is below
`spark.sql.autoBroadcastJoinThreshold`, default 10 MB [S22]), (4) code generation.

| DataFrame API (PySpark) | SQL |
|---|---|
| `df.filter(df.age > 30)` (before `groupBy`) | `WHERE age > 30` |
| `df.groupBy("dept").agg(F.count("*").alias("n"))` | `SELECT dept, COUNT(*) AS n ... GROUP BY dept` |
| `.filter(F.col("n") >= 2)` (after `agg`) | `HAVING COUNT(*) >= 2` |
| `a.join(b, a.id == b.aid, "inner")` | `FROM a JOIN b ON a.id = b.aid` |
| `.select("x").distinct()` | `SELECT DISTINCT x` |
| `.orderBy(F.desc("n")).limit(5)` | `ORDER BY n DESC LIMIT 5` |
| `a.subtract(b)` / `a.exceptAll(b)` | `EXCEPT` / `EXCEPT ALL` |

Equivalence checks: filter position relative to `groupBy` (WHERE vs HAVING),
join condition and join type, `distinct` presence, ordering before `limit`.

## When Spark beats MapReduce

| workload | winner | reason |
|---|---|---|
| iterative (PageRank, k-means, logistic regression) | Spark | working set cached, no DFS write per iteration |
| multi-stage pipelines | Spark | one DAG, narrow steps pipelined, no job-per-step |
| interactive queries on the same data | Spark | cached RDDs/DataFrames |
| one pass over data much larger than memory | similar | both stream from disk; Spark spills |

## Pitfalls

- `collect()` on a large RDD pulls everything to the driver.
- A transformation "does nothing" until an action; `take(3)` computes only as many partitions as needed.
- `flatMap` flattens one level: `[1,2].flatMap(lambda x: [x, 10*x])` = `[1, 10, 2, 20]`.
- `union` keeps duplicates (bag); `intersection` and `distinct` shuffle and dedup.
- Lineage recomputation re-runs the functions: they must be deterministic.

## Exam-style questions

1. *`rdd.map(f).filter(g).reduceByKey(h).mapValues(k).collect()`: how many stages and which operations are in each?* Two: {map, filter, map side of reduceByKey}, {reduce side, mapValues}.
2. *`a` and `b` were both `partitionBy(HashPartitioner(8))`. Is `a.join(b)` narrow? And `a.map(lambda kv: kv).join(b)`?* Yes; no, because `map` drops the partitioner, so `a` is reshuffled.
3. *Transformation or action: `reduce`, `reduceByKey`, `count`, `countByKey`, `flatMap`?* action, transformation, action, action, transformation.
4. *Why does Spark not replicate RDD partitions for fault tolerance?* Lineage allows recomputing a lost partition from its (narrow) parents; coarse-grained transformations make lineage small [S19].
5. *Translate `df.groupBy("c").agg(F.sum("x").alias("s")).filter("s > 10")` to SQL.* `SELECT c, SUM(x) AS s FROM t GROUP BY c HAVING SUM(x) > 10`.

## Code

- `spark_like.Context`, `spark_like.RDD` (`map`, `flatMap`, `filter`, `mapValues`, `union`, `partitionBy`, `groupByKey`, `reduceByKey`, `distinct`, `join`, `collect`, `count`, `reduce`, `take`, `cache`, `lose_partition`, `lineage`, `num_stages`), `spark_like.HashPartitioner`, `spark_like.pagerank`.
- `test_spark_like.py` checks laziness, shuffle counts, stages, narrow joins, cache, recovery and PageRank vs networkx.
