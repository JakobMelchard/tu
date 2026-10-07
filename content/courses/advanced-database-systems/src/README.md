# Reference implementations: 184.780 Advanced Database Systems

Pure Python 3.12 plus the standard library's `sqlite3` (SQLite 3.53). pandas,
numpy and networkx appear only as cross-checks in tests. No network access at
test time, nothing to install.

**What could not be run here.** PostgreSQL (so PL/pgSQL), Spark (no pyspark in
the venv; a stray `spark-submit` wrapper exists on this machine but no Java
runtime), MongoDB, Cassandra and Neo4j are **not installed**. The SQL parts run
in SQLite, which shares the recursive-CTE, window-function and trigger semantics
the exam asks about; the distributed systems are imitated by small
single-process models that reproduce the *counted* quantities (shuffled
records, stages, quorum overlaps, SSTable probes). Nothing here is a
production implementation.

```
cd <repo root>    # repo venv from the root pyproject.toml
python -m pytest content/courses/advanced-database-systems/src -q      # all tests, < 2 s
python content/courses/advanced-database-systems/src/py/<module>.py    # each module has a demo
```

| file | note | what | tested against |
|---|---|---|---|
| `py/recursive_cte.py` | 03 | SQLite `WITH RECURSIVE`: transitive closure, shortest paths with a path-string cycle check, bill of materials (and the UNION undercount), same generation, a non-terminating growing column stopped by `LIMIT`; `working_table_trace` replays PostgreSQL's working-table loop in Python | BFS closure, networkx Dijkstra, hand totals, generation depth |
| `py/window_functions.py` | 02 | nine window queries (ROW_NUMBER/RANK/DENSE_RANK, AVG OVER, RANGE vs ROWS, moving average, LAG/LEAD, the LAST_VALUE frame trap, top-k, NTILE) with hand-computed `EXPECTED` rows | pandas `rank`, `cumsum`, `rolling`, `diff`, `transform` |
| `py/triggers.py` | 01 | BEFORE-row skip (`RAISE(IGNORE)`, PostgreSQL `RETURN NULL`), statement abort (`RAISE(ABORT)`), AFTER-row audit, INSTEAD OF on a view; header maps SQLite to PostgreSQL semantics | row counts, audit contents, rollback |
| `py/datalog.py` | 04 | Datalog engine: parser (facts, rules, `not`, comparisons, strings, integers), safety check, stratification, naive and semi-naive evaluation with per-round trace and derivation counts | `recursive_cte` in SQLite (transitive closure, same generation; linear and nonlinear rules), hand strata |
| `py/mapreduce.py` | 05 | local MapReduce: map, optional combiner, hash partitioning, shuffle, sorted reduce; `JobStats` (shuffled pairs, replication rate r, reducer size q), simulated map-task failures; word count, inverted index, mean with correct and wrong combiner, reduce-side and broadcast joins | pandas `value_counts`, `merge`, `groupby` |
| `py/mr_algorithms.py` | 05 | relational algebra in one round (selection, projection, union, intersection, difference, grouping) and matrix multiplication in one and two rounds | Python sets, pandas, numpy `@`; r = n and q = 2n for dense matrices |
| `py/spark_like.py` | 06 | RDD-like lazy datasets: lineage, narrow vs wide dependencies, shuffle files, `reduceByKey` map-side combine vs `groupByKey`, co-partitioned (narrow) joins, cache, partition loss and recomputation, stage count; PageRank as in the RDD paper | `mapreduce.word_count`, networkx PageRank |
| `py/nosql.py` | 07, 08 | consistent-hash ring with virtual nodes and preference lists, quorum store with N/R/W and read repair, exhaustive quorum-intersection check, vector clocks (Dynamo's D1..D5), LSM tree with memtable, SSTables, tombstones, Bloom filters and merge compaction, RLE/dictionary/bitmap encodings | key-movement fractions, R + W > N for all N <= 5, a dict model under 2 000 random operations |
| `py/document_store.py` | 09 | JSON document store: `find` with MongoDB operators and array semantics, aggregation pipeline (`$match $project $addFields $unwind $group $sort $limit $skip $lookup $count`) | pandas groupby, a SQLite join for `$lookup` |
| `py/test_note_pointers.py` | all | every backticked module attribute, script name, test name and relative link in the notes, this README and `refs/` resolves | |

Tests are `py/test_<module>.py`; `py/conftest.py` puts `py/` on `sys.path`.
Where a test asserts a hand-computed number, the same number appears in the note.
