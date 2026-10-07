# Reference implementations: 184.686 Database Systems

Pure Python 3.12 with the standard library (`sqlite3`, `heapq`, `itertools`);
`networkx` for graph tests (precedence and waits-for graphs). No network at
test time: every database is sqlite in memory, every dataset is generated or
typed in. Each module has a docstring naming its sources, runs as a script with
a demo, and has a pytest file; where a textbook prints a number, a test
reproduces it, and otherwise the test compares against sqlite or a brute-force
search.

```sh
cd <repo root>    # repo venv from the root pyproject.toml
python -m pytest content/courses/database-systems/src -q          # all tests, offline, about 2 s
python content/courses/database-systems/src/py/<module>.py         # each module's demo
```

| File | Note | What | Checked against |
|---|---|---|---|
| `py/er.py` | 01, 03 | ER schema as data, `transform` to relations (one rule per construct), `ddl` with PK/UNIQUE/NOT NULL/FK/ON DELETE | DDL loaded into sqlite; cascade, SET NULL, 1:1 UNIQUE, total participation, ISA FK exercised |
| `py/fd.py` | 04 | closure, implication, candidate keys, minimal cover, projection of FDs, 2NF/3NF/BCNF tests, 3NF synthesis, BCNF decomposition, chase, dependency preservation | brute-force key search; minimal-cover equivalence and minimality; chase vs the binary criterion; synthesis/decomposition properties on random FD sets |
| `py/relalg.py` | 05 | relational algebra over Python sets (basic, derived, division, outer join, grouping), TRC and DRC over the active domain | every operator vs the equivalent SQL in sqlite on 25 random databases; division four ways |
| `py/sql_lab.py` | 06, 08, 13 | lab database (schema, data), 16 exercises with expected rows, DDL/DML demo, `EXPLAIN QUERY PLAN` demo | sqlite 3.53.1; NULL/3VL, dialect and plan tests |
| `py/storage.py` | 07 | blocking factor, slotted page with stable rids, heap/sorted cost table, external merge sort with pass and I/O counts | closed forms of [S6] ch. 15; random insert/delete on a page |
| `py/bplustree.py` | 08 | B+ tree ([S6] convention: $n$ = max pointers): insert with leaf/inner splits, search, range, invariant checker | every invariant after random inserts for $n = 3..10$; height bound; hand trace |
| `py/hashing.py` | 08 | extendible hashing (global/local depth, split, doubling), bitmap index | dict on random keys; hand trace; bitmap vs scan |
| `py/joins.py` | 09 | nested loop, block nested loop (page counting), index nested loop, sort-merge, Grace hash join; [S6] cost formulas | all five vs sqlite (bags); simulated BNLJ pages vs formula; [S6]'s printed numbers |
| `py/optimizer.py` | 10 | selectivities (incl. Selinger defaults), join-size estimate, $C_{out}$ cost, DP join ordering (left-deep/bushy, with/without products), plan counts | DP vs exhaustive enumeration on 180 random queries; counts by enumeration; estimates vs sqlite counts |
| `py/transactions.py` | 11, 12 | schedule parser, precedence graph, CSR, serial orders, VSR, recoverable/ACA/strict, 2PL legality, undo/redo/undo-redo log replay | CSR vs brute-force conflict equivalence (400 schedules); recovery vs committed state (900 random crashes) |
| `py/locking.py` | 11 | strict 2PL scheduler with waits-for deadlock detection, wait-die, wound-wait, timestamp ordering (+ Thomas), snapshot isolation | emitted schedules conflict-serialisable and strict; no waits-for cycles; SI prevents lost update, allows write skew |
| `py/recovery.py` | 12 | ARIES in miniature: WAL, pageLSN, fuzzy checkpoints, analysis/redo/undo with CLRs, crash during undo | 150 random crash-restarts + 100 double crashes vs committed state; hand trace |
| `py/practice.py` | 13 | 18 MC items, 58 statements, each answered by calling the modules above | answer key pinned in `test_practice.py` |
| `py/test_note_pointers.py` | all | every backticked `module.name` / `file.py::name` / `.py` path and relative link in the notes and READMEs resolves; every cited `S<n>` exists in `refs/SOURCES.md` | the code |

sqlite is the engine because it ships with Python and needs no server. The
184.686 SQL exam's DBMS is not public (note 00); the differences that matter
are listed in note 06 and several are pinned by tests.
