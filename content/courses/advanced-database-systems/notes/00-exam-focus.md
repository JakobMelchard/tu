# 00 Exam focus: what the three block exams ask

> **Status 2026-09-28.** 184.780 is offered in **summer semesters**; it builds on
> 184.686 Database Systems ([`../../../ss2027/database-systems/`](../../database-systems/index.md)).
> The 2028S TISS page is **not published**; everything below is the **2026S
> pattern** [S1], plus the 2027S exam dates that the 2026S page already lists
> [S1], plus student reports on VoWi [S2]-[S6]. Treat every VoWi statement as
> hearsay until the 2028S kick-off confirms it.

## Course facts (TISS 2026S [S1])

| item | 2026S pattern / known value |
|---|---|
| type | VU 4.0 h, 6.0 ECTS, English, hybrid; **CSE: Elective** (mandatory in Data Science, 2nd semester) |
| lecturers | Pichler, Lanzinger, Ganepola Achchige, Unalan (E192 Logic and Computation) |
| structure | three blocks: (1) advanced relational processing: procedural SQL, CTEs, recursion, Datalog; (2) distributed data processing: MapReduce, Spark; (3) NoSQL |
| teaching | recordings on TUWEL; in-person kick-off, Q&A and summary per block (also streamed and recorded); block-1 lectures packed into the first week (2026S: 02.-06.03) |
| exercises | three sheets, one per block, **15 % / 15 % / 10 %**; each discussed with a tutor **over Zoom** |
| exams | three written block exams, **20 % each**, in person in large lecture halls; no late registration by e-mail |
| pass | **>= 30/60 from the three exams together** and **>= 50/100 overall** |
| bonus exam | optional, late September, repeats **one** block |
| registration | mid-February to early March (2026S: 16.02.-02.03.2026, deregistration until 16.03.2026) |
| prerequisites | bachelor "Database Systems" knowledge "absolutely necessary"; programming at the level of "Introduction to Programming 1" |
| workload | 42 h lectures, 60 h exercise sheets, 2 h interviews, 40 h exam preparation, 6 h exams |

**2027S exams already booked** on the 2026S page [S1]: block 1 Fri 16.04.2027,
block 2 Fri 21.05.2027, block 3 Wed 23.06.2027, bonus Mon 27.09.2027; each with
its own registration window (block 1: 01.03.-14.04.2027). **2028S is expected
to have the same shape**: mid-April, late May, late June, late September.

## The two hurdles

Let $e_1, e_2, e_3 \in [0, 20]$ be the exam points and $x \in [0, 40]$ the exercise points.

$$\text{pass} \iff e_1 + e_2 + e_3 \ge 30 \;\wedge\; e_1 + e_2 + e_3 + x \ge 50.$$

- The exam hurdle is on the **sum**, not per exam: 15 + 5 + 10 passes it.
- With full exercise points (x = 40) the binding constraint is still $\sum e \ge 30$.
- The cheapest pass is $\sum e = 30$ with $x = 20$, i.e. half of every component.
- Grade bands are not on TISS (unverified; check the kick-off slides).

## Exam format as reported on VoWi [S2]

| semester | format (student reports, not official) |
|---|---|
| up to SS24 | per block: 4 true/false MC items with minus points (20 %), one theory question (20 %), practical tasks (60 %) "mostly very similar to the exercise sheets and old exams"; one hand-written A4 sheet (both sides) allowed; strict grading, no points for small slips |
| SS25 | "due to many registrations (350+)" **multiple choice only**, no free text |
| SS26, exam 1 | entirely MC; **1 to all options may be correct; a question scores only if exactly the right set is ticked; no partial and no negative points** |

The 2020 exam [S6] (old format, all three blocks in one paper) shows the
question *shapes* that survive into MC: true/false statements on combiners and
HDFS, a MapReduce algorithm with its communication cost, Spark SQL to DataFrame
translation, document-store denormalisation pros and cons, and evaluating
Cypher queries on a given graph.

**Consequence of all-or-nothing MC:** every option must be decided, so the
skill tested is *exact simulation*: run the recursive query by hand, trace the
trigger, stratify the program, count the shuffled pairs. The `src/py` modules
exist so each hand trace can be checked.

## What each block exam asks (inferred from [S2]-[S6])

| block | reported topics | notes | code |
|---|---|---|---|
| 1 | PL/pgSQL: blocks, variables and scope, `SELECT INTO`, loops, exceptions and their propagation, cursors, functions vs procedures | [01](01-procedural-sql.md) | - (no PostgreSQL here) |
| 1 | triggers: BEFORE/AFTER/INSTEAD OF, ROW vs STATEMENT, `RETURN NULL`, side effects | [01](01-procedural-sql.md) | `triggers.py` |
| 1 | CTEs, materialisation, universal quantification with `NOT EXISTS` | [02](02-window-functions-and-ctes.md) | `window_functions.py` |
| 1 | recursive CTEs: step-by-step simulation, termination, UNION vs UNION ALL, cycles, growing columns | [03](03-recursive-queries.md) | `recursive_cte.py` |
| 1 | Datalog: syntax, safety, $T_P$ and naive/semi-naive rounds, negation, stratification | [04](04-datalog.md) | `datalog.py` |
| 2 | MapReduce model, HDFS, combiners, failures, cost model (r, q, communication), RA operators, joins, matrix multiplication and its lower bound | [05](05-mapreduce.md) | `mapreduce.py`, `mr_algorithms.py` |
| 2 | Spark: RDDs, lazy DAG, transformations vs actions, narrow vs wide, stages, caching, DataFrame/SQL equivalences | [06](06-spark.md) | `spark_like.py` |
| 2 or 3 | distributed DBMS: fragmentation, replication, 2PC, semi-join cost (on the 2026 block-2 sheet [S4] *and* the 2025 block-3 sheet [S5]) | [07](07-distribution-and-consistency.md) | - |
| 3 | CAP, PACELC, BASE, consistency models, ROWA and majority quorums, Lamport and vector clocks | [07](07-distribution-and-consistency.md) | `nosql.py` |
| 3 | data models, consistent hashing, LSM trees, column stores and compression, Bigtable | [08](08-nosql-storage.md) | `nosql.py` |
| 3 | MongoDB (embedding vs referencing, aggregation, replication, sharding), Cassandra, Neo4j/Cypher | [09](09-mongodb-cassandra-neo4j.md) | `document_store.py` |

Note: the VoWi "Inhalt" section still lists the pre-2021 block 1 (storage,
indexing, query optimisation) [S2]. The TISS subject [S1] and the 2026 notes
[S3] replace it with procedural SQL, CTEs and Datalog. Query-optimisation
basics (pushing selections, canonical vs optimised relational algebra) still
appear in [S3] and belong to 184.686 anyway.

## Bonus-exam tactic

- It repeats **one** block. Write all three block exams seriously; the bonus is
  insurance for the weakest one, not a second attempt at everything.
- Whether the bonus result **replaces** the block result or the **better** one
  counts is not stated on TISS (unverified). If it replaces, only sit it when
  the block result was clearly weak.
- It falls in late September, after the summer; the registration window opens
  around the end of June (2027S: 29.06.-13.09.2027 [S1]). Put it in the
  calendar when the block results arrive.
- Pick the block by marginal points: the block whose exercise sheet you did
  properly is the cheapest to raise, because the exams resemble the sheets [S2].

## Verify in early 2028

1. TISS 2028S page: dates, registration window, exam dates and registration windows, grading text. Update `../docs/tiss.md`.
2. **TUWEL access**: recordings and exercise sheets live on TUWEL. Check access before the registration opens.
3. Exam format: still MC only? all-or-nothing? cheat sheet allowed?
4. Bonus rule: replace or max?
5. Exercise infrastructure (VoWi: servers and the cluster get congested near deadlines; start early [S2]).
6. Block 2 vs block 3 boundary for distributed DBMS topics (2PC, semi-join).

## Preparation plan (backwards from mid-April 2028)

| when | what |
|---|---|
| 2027S | 184.686 Database Systems: SQL, relational algebra, transactions are prerequisites |
| Feb 2028 | notes 01-04, rerun every `src/py` block-1 demo, predict outputs before running |
| first week of term | block-1 lectures are compressed into this week; sheet 1 follows |
| April | block-1 exam; notes 05-06 in parallel |
| May | block-2 exam; notes 07-09 |
| June | block-3 exam; decide on the bonus exam |
