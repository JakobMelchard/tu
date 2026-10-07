# Sources: 184.780 Advanced Database Systems

Register of every source used to write and check `../notes` and
`../src`. Notes cite `[S<n>]`, optionally with a section. All
retrieved **2026-09-28** unless stated. Access column: **vendored** = copy in
`vendor/` (licence permits redistribution); **cite-only** = free to
read, downloaded by [`fetch-sources.sh --papers`](fetch-sources.sh) into the
git-ignored `cite-only/` for personal study, never committed; **web** = live page.

No TUWEL material was used: TUWEL needs a login. TISS says "No lecture notes" exist [S1]; the course's own slides
and recordings sit on TUWEL. Everything course-specific beyond TISS is therefore
**student material from VoWi** (S2-S6), labelled as such wherever it is used.

## Course

| # | source | access | used for |
|---|---|---|---|
| S1 | TISS 184.780, 2026S page, <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184780&semester=2026S>, transcribed in [`../docs/tiss.md`](../docs/tiss.md) and `../docs/tiss-api.md` (2026-09-28) | web | blocks, teaching method, grading 15/15/10 + 3x20, hurdles 30/60 and 50/100, bonus exam, lecturers, 2026S dates, 2027S exam dates, prerequisites, ECTS breakdown |
| S2 | VoWi, *Advanced Database Systems VU (Pichler)*, <https://vowi.fsinf.at/wiki/TU_Wien:Advanced_Database_Systems_VU_(Pichler)> | web | student reports: MC-only since SS25 (350+ registrations), SS26 exam-1 format (1..all correct, no partial, no negative points) and topics, older format (MC 20 %, theory 20 %, practice 60 %, A4 sheet), tips |
| S3 | VoWi upload *ADBS Exam prep Block 1 SS2026.pdf* (student notes, March 2026) | cite-only | block-1 topic list and order: PL/pgSQL, triggers, Datalog (INFER, semi-naive, stratification), CTEs, materialisation; the ancestor example |
| S4 | VoWi upload *Adbs-exam2-cheatsheet-2026.pdf* (hand-written, C. Scherling) | cite-only | block-2 topics 2026: MR model, HDFS, combiners, failures, r/q cost model, RA and joins in MR, matrix multiplication and lower bound, top-k, Spark operations, narrow/wide, stages, DF/SQL equivalences, 2PC, semi-join |
| S5 | VoWi upload *Adbs-ex3-cheatsheet.pdf* (hand-written, uploaded 19.03.2025) | cite-only | block-3 topics: distributed DBMS, NoSQL/BASE, CAP/PACELC, ROWA/majority, clocks, KV/document/graph/column/wide-column stores, MongoDB modelling rules, Cypher, compression |
| S6 | VoWi upload *Exam 2020-06 (reference solution).pdf* (the one-exam-for-all-blocks COVID semester) | cite-only | question shapes: T/F items, MapReduce algorithm with communication cost, Spark SQL vs DataFrame, document denormalisation, Cypher evaluation |

## Block 1: procedural SQL, CTEs, recursion, Datalog

| # | source | access | used for |
|---|---|---|---|
| S7 | Abiteboul, Hull, Vianu, *Foundations of Databases*, Addison-Wesley 1995, <http://webdam.inria.fr/Alice/> ("one copy for personal use but not for distribution") | cite-only | ch. 12 Datalog syntax and semantics, 13.1 semi-naive, 15.2 stratified negation, ch. 5 algebra/calculus |
| S8 | Green, Huang, Loo, Zhou, *Datalog and Recursive Query Processing*, FnT Databases 5(2), 2013; copy at <http://blogs.evergreen.edu/sosw/files/2014/04/Green-Vol5-DBS-017.pdf> | cite-only | Datalog survey, evaluation, negation |
| S9 | PostgreSQL 18 manual, 7.8 *WITH Queries*, <https://www.postgresql.org/docs/18/queries-with.html> | vendored | recursive evaluation algorithm (working table), UNION vs UNION ALL, SEARCH/CYCLE, LIMIT caveat, materialisation rules |
| S10 | PostgreSQL 18 manual, ch. 41 PL/pgSQL: 41.5.3 single-row results, 41.6 control structures (41.6.8 trapping errors), 41.7 cursors, 41.8 transaction management, 41.10 trigger functions; <https://www.postgresql.org/docs/18/plpgsql.html> | vendored (41.6, 41.7, 41.10) / web | SELECT INTO / STRICT / FOUND, rollback-to-block rule, cursors, procedures with COMMIT, trigger return values |
| S11 | PostgreSQL 18 manual, 9.22 window functions and 3.5 tutorial, <https://www.postgresql.org/docs/18/functions-window.html> | vendored (9.22) | window function list, frames |
| S12 | PostgreSQL 18 manual, *CREATE TRIGGER* and *Overview of Trigger Behavior*, <https://www.postgresql.org/docs/18/sql-createtrigger.html>, <https://www.postgresql.org/docs/18/trigger-definition.html> | web | row vs statement (statement triggers fire on 0 rows), alphabetical firing order, INSTEAD OF only on views |
| S13 | SQLite, *The WITH Clause*, <https://www.sqlite.org/lang_with.html> (SQLite 3.53 in the venv) | vendored | queue algorithm, recursive table exactly once, no aggregates in the recursive select, LIMIT, depth/breadth first |
| S14 | SQLite, *Window Functions*, <https://www.sqlite.org/windowfunctions.html> | web | default frame `RANGE ... CURRENT ROW` including peers |
| S15 | SQLite, *CREATE TRIGGER*, <https://www.sqlite.org/lang_createtrigger.html> | web | RAISE(IGNORE) / RAISE(ABORT), row-only triggers, INSTEAD OF on views |

## Block 2: distributed data processing

| # | source | access | used for |
|---|---|---|---|
| S16 | Dean, Ghemawat, *MapReduce: Simplified Data Processing on Large Clusters*, OSDI 2004 | cite-only | model, partitioning `hash(key) mod R`, fault tolerance (3.3), backup tasks (3.6), combiner (4.3) |
| S17 | Leskovec, Rajaraman, Ullman, *Mining of Massive Datasets*, ch. 2, <http://infolab.stanford.edu/~ullman/mmds/ch2n.pdf> | cite-only | DFS, RA operators in MR (2.3.3-2.3.8), matrix multiplication (2.3.9-2.3.10), communication cost (2.5), r and q (2.6.1), lower bound and two-pass comparison (2.6.7) |
| S18 | Afrati, Das Sarma, Salihoglu, Ullman, *Upper and Lower Bounds on the Cost of a Map-Reduce Computation*, PVLDB 2013, arXiv:1206.4377 | cite-only | replication-rate lower bounds |
| S19 | Zaharia et al., *Resilient Distributed Datasets*, NSDI 2012 | cite-only | RDD definition (2), PageRank (3.2.2), narrow/wide dependencies and stages (4-5), "up to 20x" |
| S20 | Apache Spark, *RDD Programming Guide* (docs "latest" = 4.2.0), <https://spark.apache.org/docs/latest/rdd-programming-guide.html> | web | transformations vs actions, laziness, reduceByKey vs groupByKey, MEMORY_ONLY default |
| S21 | Armbrust et al., *Spark SQL: Relational Data Processing in Spark*, SIGMOD 2015 | cite-only | DataFrames, Catalyst's four phases (Figure 3) |
| S22 | Apache Spark, *Spark SQL guide* and *Performance Tuning*, <https://spark.apache.org/docs/latest/sql-performance-tuning.html> | web | `spark.sql.autoBroadcastJoinThreshold` = 10 MB |
| S23 | Apache Hadoop, *MapReduce Tutorial*, <https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html> | web | HDFS/MapReduce terminology |

## Block 3: NoSQL and distribution

| # | source | access | used for |
|---|---|---|---|
| S24 | DeCandia et al., *Dynamo*, SOSP 2007 | cite-only | consistent hashing and virtual nodes (4.2), replication and preference list (4.3), vector clocks D1-D5 (4.4), R + W > N (4.5), hinted handoff (4.6), (3,2,2) |
| S25 | Chang et al., *Bigtable*, OSDI 2006 | cite-only | data model (2), tablets, memtable/SSTables (5.3), compactions (5.4), Bloom filters |
| S26 | Gilbert, Lynch, *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*, SIGACT News 2002 (text layer of the free PDF is garbled), and the same authors' *Perspectives on the CAP Theorem*, IEEE Computer 2012, <https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf> | cite-only | CAP definitions (atomic = linearizable register, availability = every request eventually answered, partitions = lost/delayed messages) and the theorem statement, checked in the 2012 paper section 2 |
| S27 | Brewer, *CAP Twelve Years Later: How the "Rules" Have Changed*, IEEE Computer 2012 (InfoQ reprint) | web | "2 of 3" is misleading |
| S28 | Abadi, *Consistency Tradeoffs in Modern Distributed Database System Design*, IEEE Computer 2012 | cite-only | PACELC, classification of Dynamo/Cassandra/Riak, VoltDB, MongoDB, PNUTS |
| S29 | Bailis et al., *Highly Available Transactions: Virtues and Limitations*, PVLDB 7(3) 2013 | cite-only | which isolation/session guarantees are achievable with (sticky) availability |
| S30 | Bailis et al., *Probabilistically Bounded Staleness*, arXiv:1204.6082 | cite-only | staleness with partial quorums |
| S31 | Lamport, *Time, Clocks, and the Ordering of Events*, CACM 1978 | cite-only | happened-before, clock condition |
| S32 | Karger et al., *Consistent Hashing and Random Trees*, STOC 1997 | cite-only | consistent hashing |
| S33 | O'Neil, Cheng, Gawlick, O'Neil, *The Log-Structured Merge-Tree*, Acta Informatica 1996 | cite-only | LSM components C0/C1, rolling merge |
| S34 | MongoDB manual: aggregation pipeline, data modelling, atomicity and transactions, replication, write concern, sharding, <https://www.mongodb.com/docs/manual/> | web | everything MongoDB in note 09 |
| S35 | Apache Cassandra docs: data modelling intro and queries, Dynamo architecture (consistency levels), storage engine, <https://cassandra.apache.org/doc/latest/> | web | query-driven modelling, partition/clustering keys, consistency levels |
| S36 | Neo4j docs: Cypher manual introduction and basic queries, *What is a graph database*, <https://neo4j.com/docs/> | web | property graph, pattern syntax, "no JOINs", match modes |
| S37 | Vogels, *Eventually Consistent*, 2008, <https://www.allthingsdistributed.com/2008/12/eventually_consistent.html> | web | eventual consistency, BASE vocabulary |

## Repository and licences

| # | source | access | used for |
|---|---|---|---|
| S38 | SQLite copyright page <https://www.sqlite.org/copyright.html> (public domain); PostgreSQL licence <https://www.postgresql.org/about/licence/> | web | basis for vendoring (see [`README.md`](README.md)) |
| S40 | Abadi, Madden, Ferreira, *Integrating Compression and Execution in Column-Oriented Database Systems*, SIGMOD 2006 | cite-only | RLE, dictionary, bit-vector; operating on compressed data |
| S41 | Gray, Lamport, *Consensus on Transaction Commit*, ACM TODS 31(1) 2006 (MSR-TR-2003-96), <https://www.microsoft.com/en-us/research/uploads/prod/2004/01/twophase-revised.pdf> | cite-only | 2PC (section 3), blocking, Paxos Commit |

