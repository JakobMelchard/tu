# 184.686 Database Systems: notes

Ordered index. Each topic note has definitions and results, a worked example,
pitfalls, five exam-style questions with answers (true/false or single-answer,
because the final exam is multiple choice [S1]), and pointers into
`../src/py`. The order follows the TISS subject list [S2]; note 13
is the practice set, note 00 the examination.

## Course facts (state 2026-09-28)

| item | value | source |
|---|---|---|
| semester | offered in summer semesters | [S1] |
| TISS 2027S page | **not published** as of 2026-09-28; everything below is the **2026S pattern** | [S1] |
| type | VU 4.0 h, 6.0 ECTS, presence, LectureTube livestream | [S1] |
| language | lectures in **German**; all materials in English; exercises and exams in both languages | [S1] |
| lecturers (2026S) | Hose, Jakubowski, Winter, Schrott, Skritek, Merkl, Ahmed Maher Sobhi; E192 Logic and Computation | [S1] |
| 2026S lectures | Mon 14:00-16:00 and Thu 08:00-10:00, GM 1 Audimax; first lecture 02.03.2026 14:00 | [S1] |
| exercise groups | 32 in 2026S (about 30), Wed or Thu; groups 14, 15, 27 in English | [S1] |
| assessment | exercises + **SQL exam** in the Informatiklabor (computer-assisted, **50 points, at least 50 % required**, two dates, up to two attempts, latest counts) + **written multiple-choice exam** in a lecture hall (**100 points, at least 50 % required**, two dates, up to two attempts, latest counts) | [S1], [S2] |
| exam table on the 2026S page | already books **22.04.2027** 18:00-20:00 "1. Test" (ten lecture halls), **21.06.2027** 18:00-21:00 "2. Test", **20.09.2027** 18:00-20:00 repeat; a 13.05.2027 row labelled "Test - delete me" is ignored | [S1] |
| curricula | bachelor course: mandatory in the **2nd semester** of the informatics BSc curricula; **Elective** in 066 646 CSE | [S1] |
| recommended before | EP1 and GDS (no formal prerequisite) | [S1], [S2] |
| contact | dbs-course@list.tuwien.ac.at only | [S1] |
| lecture notes | "No lecture notes" on TISS | [S1] |

**Start with [00 Exam focus](00-exam-focus.md)**: what is assessed, what is
known about the two exam formats (little), and the checklist for the day the
2027S page appears.

## Sources

Every claim is cited `[S<n>]` into [`../refs/SOURCES.md`](../refs/SOURCES.md).
The course's own public pages (DBAI site [S4]) returned HTTP 403 and VoWi [S5]
served a bot check on 2026-09-28, so **nothing here comes from 184.686's own
slides, sheets or past papers**. The technical content rests on the
Silberschatz/Korth/Sudarshan slides [S6], Abiteboul/Hull/Vianu [S10], the
classic papers [S9], [S14], [S19], [S20], and the SQLite and PostgreSQL
documentation [S21], [S22]; the numbers in the worked examples are produced by
the code in `../src/py` and pinned by its tests. Kemper and Eickler [S7] is
listed but was not consulted. Changes: CHANGELOG.md.

| # | Note | One line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | What is assessed, MC and SQL exam formats as far as public sources say, weighting, what to check in 2027S |
| 01 | [ER modelling](01-er-modelling.md) | Entities, attributes, relationships, cardinalities, participation, weak entities, ISA |
| 02 | [Relational model](02-relational-model.md) | Domains, relations as sets, keys, integrity constraints, NULL |
| 03 | [ER to relational](03-er-to-relational.md) | One mapping rule per construct, ISA strategies, DDL that enforces the diagram |
| 04 | [Functional dependencies and normal forms](04-fds-and-normal-forms.md) | Armstrong, closure, keys, minimal cover, 1NF-BCNF, 3NF synthesis, BCNF decomposition, lossless join, dependency preservation |
| 05 | [Relational algebra and calculus](05-relational-algebra-and-calculus.md) | Operators, derived operators, division, TRC and DRC, safety, Codd's theorem |
| 06 | [SQL](06-sql.md) | Queries, joins, aggregation, nested queries, NULL and three-valued logic, DDL/DML, views, constraints |
| 07 | [Physical organisation](07-physical-organisation.md) | Pages, records, slotted pages, heap and sorted files, cost model, external sort |
| 08 | [Index structures](08-index-structures.md) | B+ trees (search, insert, split), extendible hashing, bitmap indexes, effect on plans |
| 09 | [Join algorithms](09-join-algorithms.md) | Nested loop, block nested loop, index nested loop, sort-merge, hash join, costs |
| 10 | [Query optimisation](10-query-optimisation.md) | Algebraic rewriting, selectivity and size estimation, cost model, DP join ordering |
| 11 | [Transactions and concurrency](11-transactions-and-concurrency.md) | ACID, schedules, conflict/view serialisability, recoverability, 2PL, deadlocks, timestamps, MVCC and SI, isolation levels |
| 12 | [Recovery](12-recovery.md) | Failure classes, WAL, steal/force, undo/redo logging, checkpoints, ARIES |
| 13 | [Practice set](13-practice-set.md) | 18 MC items (58 statements) answered by running code; SQL lab exercises with expected results |
