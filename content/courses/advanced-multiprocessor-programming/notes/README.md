# 191.022 Advanced Multiprocessor Programming - notes

Preparation for **2027W**: the course is cancelled in 2026W and TISS expects
it "from 2027W onward" [S2]. One note per topic of the TISS subject list [S2],
in the chapter order of the course book, Herlihy & Shavit, *The Art of
Multiprocessor Programming* [S1] (not free: cited by chapter, never copied).
Each note: definitions (every CS term defined), the book's proofs as
derivations, a worked example that traces a history, pitfalls, five
exam-style questions with answers, and pointers into
[`../src`](../src/README.md). Numbers are measured on an Apple M3 Pro
(6 performance + 6 efficiency cores, 128-byte cache lines), Apple clang 21,
`-O2`, on 2026-09-28 [S35].

**Course facts** (details in [00-exam-focus.md](00-exam-focus.md)):
mandatory CSE 3rd semester; VU 4 h, 6 ECTS, immanent; exercises (hand-ins) +
project + oral or written exam; lecturer Hunold (2025W: Träff, Hunold,
Felber); the cancelled 2026W page says no registration is necessary, but
2025W had a TISS registration window [S2] [S3]. Previous knowledge:
184.710 Parallel Computing, **not a formal precondition**; what it covers and what to
self-study instead is in 00, including the English 3-ECTS sibling 191.114
that runs in summer terms [S33] [S34].

Every claim carries `[S<n>]` into [`../refs/SOURCES.md`](../refs/SOURCES.md);
inferences and unverified items are marked in place. Changes:
`CHANGELOG.md`. Already covered elsewhere and only linked
here: OpenMP, threads, races, Amdahl in
[NSSC I 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md);
latency, store buffers, caches in
Efficient Programs 03
and 04.

| # | note | book [S1] | one line | code |
|---|---|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | | status (cancelled 2026W, expected again 2027W), assessment per TISS and VoWi, the 2025W schedule, what book exercises and the 80 h project look like, the missing prerequisite, what to verify in 2027 | |
| 01 | [Mutual exclusion](01-mutual-exclusion.md) | ch. 2 | Peterson, Filter, Bakery with proofs; the $n$-register lower bound; weakened Peterson measured | `peterson_filter.cpp` |
| 02 | [Concurrent objects and linearisability](02-concurrent-objects-and-linearisability.md) | ch. 3 | histories, quiescent / sequential consistency / linearisability, locality, linearisation points, progress conditions, a history checker | `ms_queue.cpp` |
| 03 | [Memory models: C++ and hardware](03-memory-models-cpp.md) | ch. 3, app. B | happens-before, data races as UB, acquire/release, seq_cst, fences; x86-TSO vs ARMv8; codegen table; litmus statistics | `memory_model.cpp` |
| 04 | [Consensus and universality](04-consensus-and-universality.md) | ch. 4-6 | valence proofs: registers 1, queues 2, CAS $\infty$; the hierarchy; universal construction with helping | |
| 05 | [Spin locks and contention](05-spin-locks-and-contention.md) | ch. 7 | TAS, TTAS, backoff, CLH, MCS; coherence traffic; throughput vs fairness measured | `spinlocks.cpp` |
| 06 | [Linked lists](06-linked-lists.md) | ch. 9 | coarse, hand-over-hand, optimistic, lazy, lock-free (Harris marks); invariants and linearisation points | `lists.cpp` |
| 07 | [Queues and the ABA problem](07-queues-and-the-aba-problem.md) | ch. 10 | bounded two-lock queue, Michael-Scott, helping, ABA and counted pointers | `ms_queue.cpp` |
| 08 | [Stacks and elimination](08-stacks-and-elimination.md) | ch. 11 | Treiber stack, deterministic ABA replay, exchanger, elimination backoff | `treiber_stack.cpp` |
| 09 | [Hash sets](09-hash-sets.md) | ch. 13 | coarse, striped, refinable; resize; split-ordered lists derived | `striped_hashset.cpp` |
| 10 | [Skiplists and search structures](10-skiplists-and-search-structures.md) | ch. 14 | expected cost derived; lazy and lock-free skiplists | (`lists.cpp` techniques) |
| 11 | [Work stealing](11-work-stealing.md) | ch. 16 | work, span, greedy bound, Blumofe-Leiserson, Chase-Lev deque with C11 orderings, a fork-join scheduler | `work_stealing.cpp` |
| 12 | [Memory reclamation](12-memory-reclamation.md) | 2nd ed. (unverified) | hazard pointers, epochs, a test that makes use-after-free observable | `hazard_pointers.cpp` |

Not covered by a note: book ch. 8 (monitors, condition variables, readers-writers locks), ch. 12 (counting networks, diffracting trees), ch. 15 (priority queues, touched in 10), ch. 17 (barriers; the sense-reversing barrier is in `src/cpp/common.hpp`), ch. 18 (transactional memory). TISS's subject list does not name them [S2]; the 2013 project was a counting network [S37], so read ch. 12 if the 2027W project list includes one.

Suggested order with 80 h of project time in mind: 00, 03 (the language of every other note), 01, 02, 04 (the theory the exercises test), then 05-12 with the matching program open.
