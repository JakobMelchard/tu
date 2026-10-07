# 00 Exam focus: what is assessed

**State 2026-09-28.** 184.686 is offered in summer semesters. The TISS page for 2027S
is **not published**; every fact below is the **2026S pattern** read off the
2026S page [S1]. Re-check all of it when the 2027S page appears (last
section).

## What TISS states [S1], [S2]

| item | 2026S value |
|---|---|
| components | exercises, an **SQL exam** during the semester, a **written multiple-choice exam** at the end |
| SQL exam | computer-assisted, in presence in the **Informatiklabor**; max **50** points; **at least half required** to pass the course; two dates; up to two attempts; the **latest attempt counts** |
| MC exam | in presence in a lecture hall; covers **all topics** ("as announced in the course"); max **100** points; **at least half required**; two dates; up to two attempts; latest counts |
| exercises | part of the evaluation; points and weight **not stated** in the public text |
| language | lectures German; materials, exercises and exams also English, so the course can be completed without German |
| groups | 32 groups (about 30), two hours weekly Wed or Thu from the second week to mid-June; three English groups |
| ECTS breakdown | 18 h lectures, 18 h lecture preparation, 52 h exercises, **12 h SQL exam**, **50 h exam** |
| lecture notes | "No lecture notes" |
| prerequisites | none formal; EP1 and GDS strongly recommended |

### The exam table already lists 2027 dates [S1]

| date | time | label on TISS | rooms |
|---|---|---|---|
| Thu **22.04.2027** | 18:00-20:00 | 1. Test | ten lecture halls (EI 7, FH 1, HS 18, FH 6, GM 5, GM 2, GM 1, Informatikhörsaal, HS 17, FH 5) |
| Thu 13.05.2027 | 18:00-20:00 | "Test - delete me" | same halls; a placeholder, **ignored** |
| Mon **21.06.2027** | 18:00-21:00 | 2. Test | eleven lecture halls |
| Mon **20.09.2027** | 18:00-20:00 | Schriftlicher Test Wiederholung | five lecture halls |

How "1. Test" and "2. Test" map onto the two components is **not stated**. The
SQL exam is in the Informatiklabor, not in lecture halls [S1], so the
hall bookings are more likely MC sittings (inference). A first "Test" in
late April would sit mid-semester, which does not fit "MC exam at the end";
possibly the MC exam is split, or the April slot is something else. **Unknown;
ask in the first lecture.**

## What public sources say about the formats

Almost nothing beyond the table above.

- The DBAI course pages [S4] returned **HTTP 403** on 2026-09-28; VoWi [S5]
  served a bot check and was not read. So: no public past MC paper, no
  statement of how wrong answers are scored, no statement of which DBMS the SQL
  exam uses, no statement of what is allowed in the lab.
- Therefore everything in the next two subsections is **our inference**.

### MC exam: what to expect (inference)

- A statement-level format ("which of the following are true") suits exactly
  the content that has crisp answers: normal-form membership, key sets,
  closure, lossless/dependency-preserving, algebra equivalences, NULL
  semantics, B+ tree shapes after inserts, cost formulas, serialisability,
  recoverability, 2PL legality, ARIES passes. Note 13 is built this way.
- If wrong ticks cost points, guessing is not free: only tick what you can
  derive. Check the scoring rule the moment it is announced.
- 100 points at a 50 % hurdle over thirteen subject items [S2]: breadth beats
  depth. Every note has five questions in this style.

### SQL exam: what to expect (inference)

- Computer-assisted in a lab [S1]: you write queries against a given schema and
  the result is checked. Practise writing correct SQL **fast**, without an
  optimiser to hide mistakes: note 06 and the SQL half of note 13
  (`sql_lab.EXERCISES`, sixteen exercises with asserted results).
- The DBMS is unknown. `sql_lab.py` uses sqlite3; the dialect differences that
  matter (no `ALL`/`ANY` in sqlite, foreign keys off by default in sqlite,
  integer division, `NULLS FIRST` order) are pinned by tests and listed in
  note 06. If the lab uses PostgreSQL, install it before the exam and rerun the
  exercises there (unverified which one it is).
- 12 h of the ECTS breakdown for 50 points: the course expects it to be the
  cheaper hurdle, but it is a hard hurdle (25/50).

## How to weight the notes

The learning outcomes [S2] map onto the notes one to one:

| learning outcome [S2] | notes | exam |
|---|---|---|
| conceptual models with ER diagrams | 01 | MC, exercises |
| ER to relational; analyse with normal forms | 03, 04 | MC |
| simple queries in relational algebra and calculus | 05 | MC |
| SQL for queries, definition, manipulation | 06, 13 | **SQL exam**, MC |
| physical data organisation | 07 | MC |
| index structures (B-trees) and their effect on execution | 08 | MC |
| join algorithms in simple plans | 09 | MC |
| query optimisation, efficiency of simple plans | 10 | MC |
| transactions, multi-user synchronisation, error handling | 11, 12 | MC |

Priority by payoff per hour, given two independent 50 % hurdles:

1. **SQL (06, 13)**: it is a hurdle on its own and appears in the MC exam too.
   Division, `NOT IN` with NULL, outer joins with `COUNT`, `GROUP BY`/`HAVING`,
   correlated subqueries.
2. **FDs and normal forms (04)**: closure, keys, minimal cover and NF membership
   are mechanical and yield sure MC points. `fd.py` checks any drill.
3. **Transactions (11)** and **recovery (12)**: precedence graphs,
   recoverability classes, 2PL legality, deadlock schemes, ARIES passes.
4. **Algebra (05)**, **B+ trees and hashing (08)**, **joins (09)**,
   **optimisation (10)**: formula and trace questions.
5. **ER (01, 03)** and **storage (07)**: definitions; the exercises probably
   exercise ER more than the exams do (inference).

## Planning context

- 184.686 is a **bachelor course** (mandatory 2nd semester in the informatics
  BSc curricula); for CSE it is an **Elective** [S1]. Expect a very large
  audience (the 2026S lecture was in the Audimax with a livestream overflow)
  [S1].
- 2026S registration ran 27.01.2026 09:00 to 09.03.2026 23:59, group
  registration 02.03.2026 19:00 to 09.03.2026 23:59, deregistration until
  16.03.2026 [S1]. If 2027S follows the pattern, course registration opens in
  **late January 2027** and group registration right after the first lecture
  (inference). English groups are few (three of 32) and have priority for
  non-German speakers [S1].
- The course runs on TUWEL [S1]; check TUWEL access before registration.

## When the 2027S TISS page appears: check

1. Dates and rooms of lectures, and the first lecture (was 02.03.2026 14:00).
2. Registration window, group registration, deregistration deadline.
3. The examination text: still exercises + SQL exam (50) + MC exam (100), both
   with a 50 % hurdle, latest attempt counts?
4. The exam table: are 22.04.2027, 21.06.2027, 20.09.2027 still there, and which
   is MC, which is SQL? Is there a new Informatiklabor booking for the SQL exam?
5. Exercise points and whether they enter the grade.
6. Lecturers (2026S: Hose et al., E192) and whether the English groups remain.
7. Literature section (2026S: none).
8. Then update `../docs/tiss.md` (refetch the API record from
   `https://tiss.tuwien.ac.at/api/course/184686-<semester>`) and this note, and log it in
   CHANGELOG.md.
