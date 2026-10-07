# Course topic map: 184.780 topics -> notes -> code -> sources

TISS lists no lecture notes [S1] and the slides live on TUWEL (not used). The
topic list per block is therefore reconstructed from TISS's subject and
learning outcomes [S1] and from student material on VoWi: the 2026 block-1
exam-prep notes [S3], the 2026 block-2 cheat sheet [S4], the 2025 block-3
cheat sheet [S5] and the 2020 exam [S6]. Column "seen in" says which of these
shows the topic. Replace this table with the real lecture list after the
2028S kick-off.

## Block 1: advanced processing of relational data

| topic | seen in | note | code | primary source |
|---|---|---|---|---|
| procedural DB languages, advantages | S1, S3 | 01 | - | S10 ch. 41 |
| PL/pgSQL blocks, variables, scope, `SELECT INTO` / `STRICT` / `FOUND` | S2, S3 | 01 | - | S10 41.5.3 |
| exceptions, propagation, rollback to block start | S2, S3 | 01 | - | S10 41.6.8 |
| conditionals, loops, labels | S2, S3 | 01 | - | S10 41.6 |
| cursors (bound/unbound, FETCH, WHERE CURRENT OF, returning refcursor) | S3 | 01 | - | S10 41.7 |
| functions vs procedures, OUT/INOUT, SETOF | S3 | 01 | - | S10 41.6.1-41.6.3, 41.8 |
| triggers: BEFORE/AFTER/INSTEAD OF, ROW/STATEMENT, NEW/OLD/TG_OP, RETURN NULL, audit triggers, event triggers | S2, S3 | 01 | `triggers.py` | S10 41.10, S12 |
| Datalog syntax, EDB/IDB, safety | S2, S3 | 04 | `datalog.parse`, `datalog.check_safety` | S7 12.1 |
| model, fixpoint ($T_P$), proof semantics | S3 | 04 | `datalog.evaluate` | S7 12.2-12.4 |
| naive ("INFER") and semi-naive evaluation, linear vs nonlinear | S3 | 04 | `datalog.evaluate` | S7 13.1 |
| negation, dependency graph, stratification | S2, S3 | 04 | `datalog.stratify` | S7 15.2 |
| Codd's theorem, SQL to relational algebra, pushing selections | S3 | 04 (brief); 184.686 | - | S7 ch. 5 |
| CTEs, multiple CTEs, `NOT EXISTS` for "for all", data-modifying CTEs | S3 | 02 | - | S9 7.8.1, 7.8.4 |
| CTE materialisation (`MATERIALIZED` / `NOT MATERIALIZED`), temporary tables, materialised views | S3 | 02 | - | S9 7.8.3 |
| `WITH RECURSIVE`: evaluation, UNION vs UNION ALL, termination, cycles | S2, S3 | 03 | `recursive_cte.py` | S9 7.8.2, S13 3 |
| window functions (not reported for the exam; used by 03) | - | 02 | `window_functions.py` | S11, S14 |

## Block 2: distributed data processing

| topic | seen in | note | code | primary source |
|---|---|---|---|---|
| DFS, HDFS blocks, NameNode/DataNode, locality | S4, S6 | 05 | - | S17 2.1, S23 |
| MapReduce model, partitioning, shuffle/sort | S4 | 05 | `mapreduce.run_job` | S16 2-3 |
| failures, stragglers, backup tasks | S4 | 05 | `run_job(fail_map=...)` | S16 3.3, 3.6 |
| combiners, when valid, the average trap | S4, S6 | 05 | `mapreduce.mean_by_key` | S16 4.3 |
| cost model: communication, r, q, wall clock | S4 | 05 | `JobStats` | S17 2.5, 2.6.1 |
| RA operators in MR (selection ... grouping) | S4 | 05 | `mr_algorithms.py` | S17 2.3.3-2.3.8 |
| joins: reduce-side, broadcast, co-partitioned, semi-join, theta | S4, S6 | 05, 07 | `reduce_side_join`, `broadcast_join` | S17 2.3.6, 2.5 |
| matrix multiplication, one and two rounds, lower bound $r \ge 2n^2/q$ | S4 | 05 | `matmul_one_round`, `matmul_two_rounds` | S17 2.3.9-2.3.10, 2.6.7; S18 |
| top-k | S4 | 05 | - | - |
| Spark: lazy DAG, transformations vs actions, driver/executor | S4 | 06 | `spark_like.py` | S19 2, S20 |
| narrow vs wide, stages, pipelining | S4 | 06 | `RDD.num_stages`, `RDD.lineage` | S19 4-5 |
| reduceByKey vs groupByKey, cache, pre-partitioning | S4 | 06 | `RDD.reduceByKey`, `RDD.cache`, `RDD.join` | S20 |
| DataFrame/SQL equivalences, Catalyst | S4, S6 | 06 | - | S21, S22 |
| 2PC, semi-join cost (listed on the block-2 sheet) | S4 | 07 | - | S41 3 |

## Block 3: NoSQL

| topic | seen in | note | code | primary source |
|---|---|---|---|---|
| distributed DBMS: architectures, fragmentation, replication, transparency | S5 | 07 | - | - (textbook topic; no free source used) |
| distributed concurrency control, deadlock detection | S5 | 07 (short) | - | - (only S5) |
| 2PC and recovery | S5 | 07 | - | S41 |
| why NoSQL, BASE, aggregates | S5 | 08 | - | S37 |
| CAP, PACELC | S5 | 07 | - | S26, S27, S28 |
| ROWA, majority quorums, R + W > N | S5 | 07 | `nosql.QuorumStore` | S24 4.5 |
| Lamport and vector clocks | S5 | 07 | `nosql.VectorClock` | S31, S24 4.4 |
| key-value stores (Riak) | S5 | 08 | `nosql.ConsistentHashRing` | S24 |
| document stores, MongoDB modelling, replication, sharding, write concern | S5, S6 | 09 | `document_store.py` | S34 |
| graph databases, Neo4j, Cypher | S5, S6 | 09 | - | S36 |
| column stores, compression, late materialisation | S5 | 08 | `nosql.rle` etc. | S40 |
| wide-column stores, Bigtable | S5 | 08 | `nosql.LSMTree` | S25 |
