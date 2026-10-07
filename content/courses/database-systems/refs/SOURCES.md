# Sources: 184.686 Database Systems

Register of every source used to write and verify `../notes` and
`../src`. Notes cite these as `[S<n>]`. Retrieval dates are the day
the page or file was fetched (all 2026-09-28 unless stated).

**Status of this folder.** 184.686 is offered in summer semesters. The 2027S TISS
page is **not published** as of 2026-09-28; [S1] transcribes the 2026S page.
Every course fact in the notes is therefore the 2026S pattern and must be
re-checked when the 2027S page appears (checklist in
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)).

**Vendoring policy.** Only the SQLite documentation pages in
`vendor/sqlite/` are in the tree: SQLite's code and
documentation are public domain [S21]. Everything else is copyrighted without a
redistribution grant, so it is cited here and, where a free copy exists,
downloaded by [`fetch-sources.sh`](fetch-sources.sh) into the git-ignored
`cite-only/` for personal reading. No TUWEL material was fetched (TUWEL is not ours to copy).

## Course-authoritative

### S1 TISS course page, 2026S (transcription) ★

- File: [`../docs/tiss.md`](../docs/tiss.md), transcribed 2026-09-28 from
  <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184686&semester=2026S>
  in a logged-in browser.
- Used for: VU 4.0 h, 6.0 ECTS; lectures in German, all materials and exams
  also in English; lecturers (Hose, Jakubowski, Winter, Schrott, Skritek,
  Merkl, Ahmed Maher Sobhi; E192); the 2026S weekly pattern; 32 exercise groups
  (three English ones); the assessment (exercises + SQL exam in the
  Informatiklabor, 50 points, at least half required, two dates + written MC
  exam, 100 points, at least half required, two dates; latest attempt counts);
  the exam table that already lists 22.04.2027, 21.06.2027 and 20.09.2027 in
  lecture halls; curricula (mandatory 2nd semester in the informatics BSc
  curricula, Elective in 066 646 CSE); ECTS breakdown; "No lecture notes";
  EP1 and GDS recommended.

### S2 TISS API record, 2026S

- File: `../docs/tiss-api.md` (rendered from
  `https://tiss.tuwien.ac.at/api/course/184686-2026S`).
- Used for: the nine learning outcomes and the thirteen-item subject list that
  fix the note order; the examination-modalities text quoted in note 00.


### S4 DBAI course pages for 184.686

- URLs: <https://www.dbai.tuwien.ac.at/education/dbs/>,
  <https://www.dbai.tuwien.ac.at/education/dbs/current/index.html> (both found
  by web search with the title "Datenbanksysteme - VU 184.686 (6.0 ECTS)").
- Access: **HTTP 403 Forbidden** to WebFetch and to curl on 2026-09-28. Nothing
  from them is used. They are the most likely public home of slides, exercise
  sheets and SQL-exam rules; retry when planning the semester.

### S5 VoWi pages on Datenbanksysteme VU

- URLs: <https://vowi.fsinf.at/wiki/TU_Wien:Datenbanksysteme_VU_(Skritek)>,
  its subpages "Alte Prüfungsangaben", "Zusammenfassung Test 1/2".
- Access: served a bot-detection (proof-of-work) page on 2026-09-28; **not
  read**, and deliberately not bypassed. Nothing from them is used. Past MC
  papers, if any, would be there; read them in a normal browser.

## Textbooks and slides

### S6 Silberschatz, Korth, Sudarshan: Database System Concepts, 7th ed., slides

- URL: <https://www.db-book.com/slides-dir/index.html>; PDFs of chapters 2, 3,
  4, 6, 7, 13, 14, 15, 16, 17, 18, 19 fetched into `cite-only/`.
- Licence: "authorized for personal use" (slides page, copyright note);
  **not redistributable**, so cite-only.
- Used for: ER model and mapping (ch. 6), relational algebra (ch. 2), SQL
  (ch. 3-4), FDs and normal forms (ch. 7), storage (ch. 13), B+ trees (ch. 14:
  occupancy bounds, split procedure, height bound $\lceil\log_{\lceil n/2\rceil}K\rceil$),
  query processing (ch. 15: cost measures, external sort, nested-loop numbers
  2,000,100 / 1,000,400, merge $b_r+b_s$, hash $3(b_r+b_s)$, hybrid hash),
  optimisation (ch. 16: $V(A,r)$ estimates, join-size estimate, $(2(n-1))!/(n-1)!$
  join orders, $O(3^n)$ bushy DP), transactions (ch. 17: conflict/view
  serialisability, precedence graph, recoverable, cascadeless), concurrency
  (ch. 18: 2PL phases, lock point, strict and rigorous 2PL, wait-die,
  wound-wait, waits-for graph, timestamp ordering), recovery (ch. 19:
  repeating history, PageLSN, RecLSN, CLR with UndoNextLSN, analysis pass).
- Note: the block nested-loop slide is an image in the PDF; its formula in note
  09 is derived there, not quoted.

### S7 Kemper, Eickler: Datenbanksysteme. Eine Einführung (De Gruyter Oldenbourg)

- Commercial; **not consulted in this pass**. Named because it is the standard
  German text for this kind of course and older 184.686 offerings are commonly
  associated with it; that association is unverified (S4, S5 unreadable). Its
  B-tree convention ("degree $k$") is mentioned in note 08 as a warning only.

### S8 Garcia-Molina, Ullman, Widom: Database Systems. The Complete Book, 2nd ed. (Pearson 2008)

- Commercial; **not consulted**. Listed as the standard English alternative.

## Papers

### S9 Codd 1970, "A Relational Model of Data for Large Shared Data Banks", CACM 13(6)

- Free course copy: <https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf> (cite-only).
- Used for: relations as sets of tuples, data independence as the motivation (note 02).

### S10 Abiteboul, Hull, Vianu: Foundations of Databases (1995)

- URL: <http://webdam.inria.fr/Alice/> ("one copy of the book draft for
  personal use but not for distribution"); cite-only.
- Used for: calculus and domain independence (Def. 5.3.7), safe-range calculus
  equivalent to the algebra (Thm. 5.4.6), Armstrong's axioms sound and complete
  (Thm. 8.2.11), the chase (ch. 8.4), BCNF and 3NF definitions (Def. 11.2.1, 11.2.11).

### S11 Chen 1976, "The Entity-Relationship Model: Toward a Unified View of Data", ACM TODS 1(1)

- First five pages on the author's site: <https://www.csc.lsu.edu/~chen/pdf/erd-5-pages.pdf> (cite-only).
- Used for: origin of the ER model (note 01).

### S12 Bernstein 1976, "Synthesizing Third Normal Form Relations from Functional Dependencies", ACM TODS 1(4)

- Not fetched (ACM DL refuses scripted access). Named as the origin of the
  synthesis algorithm in note 04; the algorithm itself is taken from [S6] ch. 7.

### S13 Bayer, McCreight 1972, "Organization and Maintenance of Large Ordered Indexes", Acta Informatica 1

- Not fetched. Origin of the B-tree; note 08 uses [S6] ch. 14 for all details.

### S14 Selinger et al. 1979, "Access Path Selection in a Relational Database Management System", SIGMOD

- Free course copy: <https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf> (cite-only).
- Used for: Table 1 selectivity factors (1/ICARD, 1/10, linear interpolation,
  1/3, 1/4, IN-list capped at 1/2), interesting orders, dynamic programming over
  join orders, deferring Cartesian products (note 10).

### S15 Fagin, Nievergelt, Pippenger, Strong 1979, "Extendible Hashing", ACM TODS 4(3)

- Not fetched. Origin of extendible hashing (note 08).

### S16 Hellerstein, Stonebraker, Hamilton 2007, "Architecture of a Database System", FnT Databases 1(2)

- Authors' copy: <https://dsf.berkeley.edu/papers/fntdb07-architecture.pdf> (cite-only).
- Used for: the overall process/storage/query/transaction architecture as
  orientation in note 07.

### S17 Eswaran, Gray, Lorie, Traiger 1976, "The Notions of Consistency and Predicate Locks in a Database System", CACM 19(11)

- Not fetched. Origin of two-phase locking and phantoms (note 11).

### S18 Bernstein, Hadzilacos, Goodman: Concurrency Control and Recovery in Database Systems (1987)

- Free from the author: <https://www.microsoft.com/en-us/research/people/philbe/book/>
  (HTTP 403 to scripted access on 2026-09-28; not fetched). The strict-schedule
  definition in note 11 follows this book's usage; **not re-read in this pass**.

### S19 Berenson et al. 1995, "A Critique of ANSI SQL Isolation Levels", SIGMOD

- arXiv: <https://arxiv.org/abs/cs/0701157> (cite-only).
- Used for: phenomena P0 (dirty write), P1 (dirty read), P2 (fuzzy read), P3
  (phantom) in their broad history form, snapshot isolation, first committer
  wins, write skew (notes 11, 12).

### S20 Mohan et al. 1992, "ARIES: A Transaction Recovery Method ...", ACM TODS 17(1)

- Course copy: <https://cs.stanford.edu/people/chrismre/cs345/rl/aries.pdf> (cite-only).
- Used for: WAL, pageLSN, analysis/redo/undo, repeating history, CLRs that are
  redo-only and carry UndoNxtLSN, fuzzy checkpoints (note 12).

## Systems documentation

### S21 SQLite documentation ★ (vendored)

- Files in `vendor/sqlite/` with `SHA256SUMS`: `nulls.html`,
  `queryplanner.html`, `optoverview.html`, `isolation.html`,
  `atomiccommit.html`, `fileformat2.html`, `eqp.html`, `copyright.html`.
- Licence: public domain ("All of the code and documentation in SQLite has been
  dedicated to the public domain", `copyright.html`).
- Used for: NULL handling across engines (NULLs distinct in UNIQUE, not
  distinct in DISTINCT/UNION), EXPLAIN QUERY PLAN output (SCAN vs SEARCH),
  b-tree page layout (fileformat2), rollback journal and WAL (atomiccommit,
  isolation). The running engine in `src/py` is sqlite 3.53.1.

### S22 PostgreSQL 18 documentation

- Pages `transaction-iso.html`, `mvcc-intro.html`, `using-explain.html`,
  `indexes-types.html`, `functions-comparison.html`, `queries-order.html` under
  <https://www.postgresql.org/docs/current/>; fetched into `cite-only/`
  (PostgreSQL Licence; cited rather than vendored to keep the tree small).
- Used for: Table 13.1 of isolation levels and phenomena, Read Committed as the
  default, Repeatable Read without phantoms in PostgreSQL, Read Uncommitted
  behaving as Read Committed, Repeatable Read implemented as snapshot
  isolation (note 11); `IS DISTINCT FROM`; NULLs sort as larger than any
  value by default (note 06).
