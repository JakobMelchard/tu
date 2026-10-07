# 03 Recursive queries: WITH RECURSIVE, fixpoints, termination

> **Sourcing.** PostgreSQL 18 manual 7.8.2 [S9] and SQLite `lang_with` section 3
> [S13] (both vendored), fixpoint semantics [S7 ch. 12-13]; exam emphasis
> (simulate step by step, termination, UNION vs UNION ALL, cycles, growing
> values) from the VoWi SS26 report [S2]. Every query and every number below is
> executed by `recursive_cte.py` and checked in `test_recursive_cte.py`.

## Syntax and restrictions

```sql
WITH RECURSIVE r(cols) AS (
    base_query                   -- non-recursive term: must not mention r
  UNION [ALL]
    recursive_query              -- mentions r exactly once
)
SELECT ... FROM r;
```

- **Linear recursion only**: SQLite requires the recursive table to appear
  "exactly once in the FROM clause" of each recursive SELECT [S13 3]
  (`path p1 JOIN path p2` fails with "multiple references to recursive table");
  PostgreSQL likewise rejects a second self-reference (from its error message;
  the manual states the one-reference form in [S9 7.8.2]).
- No aggregates or window functions in the recursive term [S13 3]; aggregate in
  the outer query instead.
- PostgreSQL also rejects the recursive reference inside an outer join's
  nullable side, `EXCEPT` or `INTERSECT`, i.e. positions where the step would
  stop being monotone (its parser errors; not spelled out in [S9]).

## Semantics: iteration to a fixpoint

Write the query as $X = B \cup f(X)$ with base $B$ and step $f$ (a join of $X$
with base tables; monotone: $X \subseteq Y \Rightarrow f(X) \subseteq f(Y)$).
The answer is the **least fixpoint**: the smallest set with $X = B \cup f(X)$.
PostgreSQL computes it with a *working table* $W$ [S9 7.8.2]:

$$R_0 = W_0 = B,\qquad W_{k+1} = f(W_k) \setminus R_k,\qquad R_{k+1} = R_k \cup W_{k+1},$$

stopping when $W_{k+1} = \emptyset$. With `UNION ALL` the "$\setminus R_k$" (and
the dedup inside $W$) is dropped. Because $f$ is applied to $W_k$ only, not to
$R_k$, this *is* semi-naive evaluation (note 04). SQLite uses a queue with the
same result set [S13 3.3].

**Termination.** With `UNION`, if every value in the output comes from the
input (no arithmetic, no string building), $R_k$ lives in the finite set
$\text{adom}^{\text{arity}}$ and grows strictly each round, so the loop stops
after at most $|\text{adom}|^{\text{arity}}$ rounds. It does **not** terminate when

1. `UNION ALL` on cyclic data: the same rows keep coming back;
2. a column grows: `depth + 1`, `dist + w`, `path || x`. Every row is new, so
   even `UNION` never sees a duplicate (`recursive_cte.depth_counter_rows`).

Remedies: `UNION` without growing columns; a bound (`WHERE depth < 10`); cycle
detection by a path column (`WHERE instr(path, x) = 0`, or PostgreSQL's
`CYCLE id SET is_cycle USING path` [S9 7.8.2.2]); an outer `LIMIT` (works in
PostgreSQL and SQLite because rows are produced lazily, but "not recommended"
and useless once the outer query sorts or joins [S9]).

## Worked example 1: transitive closure with a cycle

Edges `a->b, a->c, c->b, b->d, c->d, d->e, e->c` (cycle c, b, d, e).

```sql
WITH RECURSIVE tc(x, y) AS (
    SELECT src, dst FROM edge
  UNION
    SELECT tc.x, e.dst FROM tc JOIN edge e ON e.src = tc.y
)
SELECT x, y FROM tc;
```

| round | working table (new rows) | size |
|---|---|---|
| 0 | the 7 edges | 7 |
| 1 | (a,d) (b,e) (c,e) (d,c) (e,b) (e,d) | 6 |
| 2 | (a,e) (b,c) (c,c) (d,b) (d,d) (e,e) | 6 |
| 3 | (b,b) | 1 |
| 4 | nothing new: stop | 0 |

Result: 20 pairs (a reaches b, c, d, e; each of b, c, d, e reaches all four,
itself included). Round $k$ holds pairs whose *shortest* path has $k+1$ edges.
With `UNION ALL` the same query never stops (`working_table_trace(EDGES, union=False)`).

## Worked example 2: shortest paths (growing column, so cycle check needed)

```sql
WITH RECURSIVE sp(node, dist, path) AS (
    SELECT 'a', 0, ',a,'
  UNION ALL
    SELECT e.dst, sp.dist + e.w, sp.path || e.dst || ','
    FROM sp JOIN edge e ON e.src = sp.node
    WHERE instr(sp.path, ',' || e.dst || ',') = 0        -- simple paths only
)
SELECT node, MIN(dist) FROM sp GROUP BY node;
```

Weights `a-b 4, a-c 1, c-b 2, b-d 1, c-d 5, d-e 3, e-c 1`. Result
`a 0, b 3 (a,c,b), c 1, d 4 (a,c,b,d), e 7 (a,c,b,d,e)`; equals Dijkstra
(`test_shortest_paths_match_networkx`). The number of simple paths is exponential
in general: correct but not efficient.

## Worked example 3: bill of materials, where UNION is wrong

`contains(assembly, part, qty)`: bike = 2 wheel + 1 frame; wheel = 32 spoke +
1 rim + 1 hub + 2 bolt; frame = 3 tube + 4 bolt; hub = 2 bearing.

```sql
WITH RECURSIVE need(part, qty) AS (
    SELECT part, qty FROM contains WHERE assembly = 'bike'
  UNION ALL
    SELECT c.part, need.qty * c.qty FROM need JOIN contains c ON c.assembly = need.part
)
SELECT part, SUM(qty) FROM need
WHERE part NOT IN (SELECT assembly FROM contains) GROUP BY part;
```

Result: bearing 4, bolt 8, rim 2, spoke 64, tube 3. With `UNION`, the row
`(bolt, 4)` is produced twice (2 wheels x 2 bolts, 1 frame x 4 bolts) and
**deduplicated**, giving bolt 4. Rule: when the rows are *contributions to be
summed*, use `UNION ALL` (the part graph is a DAG, so it terminates).

## Worked example 4: same generation (two joins, still linear)

$sg(x,y)$: $x$, $y$ have the same parent, or their parents are of the same generation.

```sql
WITH RECURSIVE sg(x, y) AS (
    SELECT p1.child, p2.child FROM par p1 JOIN par p2 ON p1.parent = p2.parent
  UNION
    SELECT p1.child, p2.child
    FROM sg JOIN par p1 ON p1.parent = sg.x JOIN par p2 ON p2.parent = sg.y
)
SELECT * FROM sg;
```

Tree a -> {b, c}, b -> {d, e}, c -> {f}, d -> {g}, f -> {h}: generations
{b, c}, {d, e, f}, {g, h}, so $4 + 9 + 4 = 17$ pairs. `sg` occurs once: linear.

## Ordering the output

PostgreSQL: `SEARCH DEPTH FIRST BY id SET ordercol` or `SEARCH BREADTH FIRST ...`
adds a sort column [S9 7.8.2.1]. SQLite: `ORDER BY` inside the recursive term
controls the queue (`ORDER BY depth DESC` gives depth first) [S13 3.4].

## Pitfalls

- `UNION` dedups against *all* previous rows, not just the last round.
- `UNION` does not save a query with a growing column.
- `UNION` silently undercounts multiplicative aggregations (BOM).
- Outer `ORDER BY` or a join defeats the `LIMIT` guard.
- Iteration count = longest *shortest* derivation, not the number of rows.

## Exam-style questions

1. *Edges 1->2, 2->3, 3->1. How many rows does the TC query with UNION return, and in how many rounds (non-empty working tables)?* 9 rows (every ordered pair, including (x,x)), rounds of 3, 3, 3: three non-empty rounds.
2. *Same query with UNION ALL?* Does not terminate: each round again produces 3 rows.
3. *Add a column `len + 1` and use UNION. Terminates?* No: `(1,2,1)` and `(1,2,4)` differ, so no round is ever empty.
4. *Why can `SELECT x, count(*) FROM r GROUP BY x` not be the recursive term?* Aggregates are not allowed there (and would break monotonicity); aggregate outside the CTE.
5. *A CTE computes all ancestors of 'eve' via `parent(child, parent)`. Write it.*
   `WITH RECURSIVE anc(a) AS (SELECT parent FROM par WHERE child = 'eve' UNION SELECT p.parent FROM par p JOIN anc ON p.child = anc.a) SELECT a FROM anc;`

## Code

- `recursive_cte.transitive_closure`, `recursive_cte.working_table_trace` (the PostgreSQL loop in Python), `recursive_cte.shortest_paths`, `recursive_cte.bill_of_materials` (`op="UNION"` shows the pitfall), `recursive_cte.same_generation`, `recursive_cte.depth_counter_rows`.
- The same programs in Datalog: `test_datalog.py` compares `datalog.evaluate` with these results.
