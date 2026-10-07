# 184.780 Advanced Database Systems: notes

Ordered index, following the three blocks of the course [S1]. Each topic note
has definitions, a worked example with the actual query text and its result,
pitfalls, five exam-style questions with answers, and pointers into
`../src/py`. Every claim is cited `[S<n>]` into
[`../refs/SOURCES.md`](../refs/SOURCES.md); the course-topic to note map is
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

**Course state, 2026-09-28** [S1]: offered in **summer semesters**; take it after 184.686
Database Systems ([`../../../ss2027/database-systems/`](../../database-systems/index.md)).
The 2028S TISS page is not published; the facts here are the 2026S pattern:
three blocks with recordings on TUWEL and in-person kick-off, Q&A and summary;
three exercise sheets (15/15/10 %) discussed with tutors over Zoom; three
written block exams (20 % each; >= 30/60 from the exams and >= 50/100 overall);
an optional bonus exam that repeats one block. The 2027S exams are already
booked (16.04, 21.05, 23.06.2027, bonus 27.09.2027), so 2028S should look the
same. Registration mid-February to early March. Lecturers Pichler, Lanzinger et al.
CSE Elective; needs bachelor database knowledge and EP1-level programming.

**Start with [00 Exam focus](00-exam-focus.md).** Student reports [S2] say the
block exams have been multiple choice only since SS25, all-or-nothing per
question: the notes are written for exact hand simulation.

| # | note | block | one line |
|---|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | all | course facts, the two hurdles, reported exam format and topics per block, bonus-exam tactic, what to verify in early 2028 |
| 01 | [Procedural SQL](01-procedural-sql.md) | 1 | PL/pgSQL blocks, `SELECT INTO`/`STRICT`, exceptions and rollback to block start, cursors, functions vs procedures, triggers and their return values |
| 02 | [CTEs and window functions](02-window-functions-and-ctes.md) | 1 | `WITH`, materialisation, "for all" with `NOT EXISTS`; ranking, frames, RANGE vs ROWS, LAST_VALUE trap |
| 03 | [Recursive queries](03-recursive-queries.md) | 1 | `WITH RECURSIVE` as a fixpoint, working table, termination, UNION vs UNION ALL, transitive closure, shortest paths, bill of materials, same generation |
| 04 | [Datalog](04-datalog.md) | 1 | syntax, safety, $T_P$, naive vs semi-naive, linear vs nonlinear, stratified negation, Datalog vs recursive SQL |
| 05 | [MapReduce](05-mapreduce.md) | 2 | model, HDFS, combiners, failures, cost model (r, q), relational operators, joins, matrix multiplication and its lower bound |
| 06 | [Spark](06-spark.md) | 2 | RDDs, lineage, transformations vs actions, narrow vs wide, stages, partitioning, DataFrames and Catalyst, when Spark beats MapReduce |
| 07 | [Distribution and consistency](07-distribution-and-consistency.md) | 2/3 | distributed DBMS, semi-join, 2PC, CAP, PACELC, consistency models, quorums N/R/W, Lamport and vector clocks |
| 08 | [NoSQL storage](08-nosql-storage.md) | 3 | four data models, consistent hashing, LSM trees, Bigtable, column stores and compression |
| 09 | [MongoDB, Cassandra, Neo4j](09-mongodb-cassandra-neo4j.md) | 3 | find and aggregation pipeline, embedding vs referencing, replication and sharding; query-driven CQL tables; Cypher patterns |

Changes: CHANGELOG.md.

**What was not executed.** PL/pgSQL (note 01), PySpark (06), CQL and Cypher
(09) are traced by hand against the manuals; the corresponding semantics are
executed in SQLite or in the Python models where possible (see
[`../src/README.md`](../src/README.md)).
