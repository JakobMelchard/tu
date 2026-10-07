# Topic map - what the course says it covers, and where we cover it

The structural index is the TISS subject list [S2] (identical text in 2024W
under 184.726 [S4], 2025W [S3] and 2026W [S2]), ordered as the book's
chapters [S1]. There are no public slides (TISS: "No lecture notes are
available" [S3]); the course's own slides are in TUWEL, which was not used.

## TISS topic → book → note → code

| TISS subject item [S2] | book chapter [S1] | our note | primary sources | our code |
|---|---|---|---|---|
| synchronisation problems | 2 Mutual Exclusion | [01](../notes/01-mutual-exclusion.md) | [S10] [S11] [S36] | `peterson_filter.cpp` |
| (correctness conditions, implied by "lock- and wait-free") | 3 Concurrent Objects | [02](../notes/02-concurrent-objects-and-linearisability.md) | [S6] [S28] | `ms_queue.cpp` (checker) |
| memory models | 3 (Java memory model), App. B Hardware Basics | [03](../notes/03-memory-models-cpp.md) | [S19] [S20] [S21] [S22] [S23] [S24] [S31] [S32] | `memory_model.cpp` |
| operations and primitives, atomic operations | 4 Foundations of Shared Memory, 5 Relative Power of Primitive Synchronization Operations | [04](../notes/04-consensus-and-universality.md), [03](../notes/03-memory-models-cpp.md) | [S7] | (CAS everywhere in `src/cpp`) |
| consensus, impossibility and universality results | 5, 6 Universality of Consensus | [04](../notes/04-consensus-and-universality.md) | [S7] [S29] | |
| locks | 7 Spin Locks and Contention (8 Monitors: not covered) | [05](../notes/05-spin-locks-and-contention.md) | [S13] | `spinlocks.cpp` |
| lock- and wait-free data structures: lists | 9 Linked Lists | [06](../notes/06-linked-lists.md) | [S15] [S16] | `lists.cpp` |
| queues | 10 Concurrent Queues and the ABA Problem | [07](../notes/07-queues-and-the-aba-problem.md) | [S14] | `ms_queue.cpp` |
| stacks | 11 Concurrent Stacks and Elimination | [08](../notes/08-stacks-and-elimination.md) | [S12] [S17] | `treiber_stack.cpp` |
| hashtables | 13 Concurrent Hashing and Natural Parallelism | [09](../notes/09-hash-sets.md) | [S18] | `striped_hashset.cpp` |
| search structures | 14 Skiplists and Balanced Search (15 Priority Queues: touched) | [10](../notes/10-skiplists-and-search-structures.md) | [S30] | (techniques of `lists.cpp`) |
| work-stealing | 16 Futures, Scheduling, and Work Distribution | [11](../notes/11-work-stealing.md) | [S8] [S9] [S25] | `work_stealing.cpp` |
| (needed for the C/C++ project [S2]) | 2nd ed. only (unverified, see S1) | [12](../notes/12-memory-reclamation.md) | [S26] [S27] | `hazard_pointers.cpp` |
| practical implementation project | | [00](../notes/00-exam-focus.md) | [S5] [S37] | all `--bench` modes |

Book chapters with no note: 8 (monitors and blocking synchronisation), 12
(counting networks and diffracting trees; the 2013 project was a counting
network [S37]), 15 (priority queues), 17 (barriers; a sense-reversing barrier
is in `src/cpp/common.hpp`), 18 (transactional memory). None is named in the
TISS subject list [S2].

## Where the exercises come from

The only primary evidence (2013) shows exercise sheets as selections of
book exercises from chapters 1-5 [S37]; the 2025W student report describes two
theory sheets [S5]. So chapters 2-5, i.e. notes 01-04, carry the exercise
part; chapters 7-16, notes 05-12, carry the project and the oral questions
(SS2021: definitions of lock-free and wait-free, the ABA problem, TSO;
WS2025: list-based sets and lock-free vs wait-free [S5]).
