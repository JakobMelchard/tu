# Sources - 191.022 Advanced Multiprocessor Programming

Register of every source used to write and verify [`../notes`](../notes/README.md)
and [`../src`](../src/README.md). Notes and code comments cite these as `[S<n>]`.
Retrieval date = the day the page or file was read. All PDFs marked "free"
were downloaded on 2026-09-28 and the cited statements checked against their
text (`pdftotext`); [`fetch-sources.sh`](fetch-sources.sh) re-downloads them.

**Vendoring policy.** None of these sources carries a licence that permits
redistribution (the free PDFs are author or course copies of ACM, IEEE,
Elsevier or university-copyright works), so **nothing is vendored**. Free
PDFs go to the git-ignored `cite-only/`. No TUWEL material was used.

## Course-authoritative

### S1 - Herlihy & Shavit, *The Art of Multiprocessor Programming*
- Revised reprint (revised 1st ed.), Morgan Kaufmann, June 2012, ISBN 9780123973375, 536 pp. The edition TISS names [S2]. **Not free: cited by chapter, never copied.**
- Chapter list verified 2026-09-28 on the O'Reilly catalogue page (<https://www.oreilly.com/library/view/the-art-of/9780123973375/>): 1 Introduction; Part I Principles: 2 Mutual Exclusion, 3 Concurrent Objects, 4 Foundations of Shared Memory, 5 The Relative Power of Primitive Synchronization Operations, 6 Universality of Consensus; Part II Practice: 7 Spin Locks and Contention, 8 Monitors and Blocking Synchronization, 9 Linked Lists, 10 Concurrent Queues and the ABA Problem, 11 Concurrent Stacks and Elimination, 12 Counting, Sorting, and Distributed Coordination, 13 Concurrent Hashing and Natural Parallelism, 14 Skiplists and Balanced Search, 15 Priority Queues, 16 Futures, Scheduling, and Work Distribution, 17 Barriers, 18 Transactional Memory; Appendix B Hardware Basics. Section titles verified for chapter 2 only (§2.1 Time, §2.2 Critical Sections, §2.3 2-Thread Solutions, §2.4 The Filter Lock, §2.5 Fairness, §2.6 Lamport's Bakery Algorithm, §2.7 Bounded Timestamps, §2.8 Lower Bounds on the Number of Locations) and chapter 3's first five (3.1-3.5).
- 2nd edition: Herlihy, Shavit, Luchangco, Spear, 2020/2021, ISBN 9780124159501 (Google Books: "Second Edition", 2020, 576 pp.). **Chapter list not verified** (O'Reilly and ScienceDirect returned 403; the browser page timed out). Note 12's "manual memory management chapter" rests on this unverified edition.
- Used for: the topic order of every note, the proofs of notes 01, 02, 04, the algorithms of 05-11.

### S2 - TISS 191.022, 2026W (cancelled)
- <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191022&semester=2026W>, transcribed in [`../docs/tiss.md`](../docs/tiss.md) on 2026-09-28 (logged-in browser). Public.
- Used for: cancellation text, "expected to be offered again from 2027W onward", VU 4 h / 6 ECTS, immanent, mandatory CSE 3rd semester, subject list, book, teaching methods, examination modalities, ECTS breakdown, lecturer Hunold, "Course registration: Not necessary", previous knowledge and preceding course.

### S3 - TISS 191.022, 2025W (last real offering)
- <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191022&semester=2025W&locale=en>. Read 2026-09-28. **WebFetch received only the JavaScript loading shell (no dates)**; the page was then rendered in the Claude browser pane (public, not logged in), including "Show single appointments". API record of the same offering: `../docs/tiss-api.md`.
- Used for: lecture Mon 12:00-14:00 EI 11 HS - INF, 13 single dates 06.10.2025-26.01.2026; exercise extra date Thu 11.12.2025 14:00-17:00; exercise groups 1-6 (Thu 13-15/15-17/17-19 Sem.R. DA grün 04, 23.10-20.11.2025; Fri 08-10/10-12 Sem.R. DA grün 06B and Fri 12-14 Sem.R. DB gelb 09, 24.10-21.11.2025); course registration 15.09.2025 00:00-10.10.2025 23:59, deregistration end 27.10.2025 23:59; group registration 15.10-22.10.2025; lecturers Träff, Hunold, Felber; "First Lecture: 6.10.2025 (Attendance MANDATORY)", "Attendance Required!"; curricula table with an empty "Precon." column; no exams table.

### S4 - TISS 184.726 Advanced Multiprocessor Programming, 2024W (predecessor number)
- <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184726&locale=en>, read 2026-09-28 in the browser pane. Public.
- Used for: offerings 2012S-2024W, VU 3 h / 4.5 ECTS, same subject text and book, lecture Mon 11:00-13:00 EI 11 HS - INF (07.10.2024-27.01.2025), Übung Fri 13-19 on 25.10, 08.11, 29.11.2024 and 17.01.2025, "Exercises (hand-ins), project, oral project presentation", lecturers Träff, Felber.

### S5 - VoWi: Advanced Multiprocessor Programming VU (Träff)
- <https://vowi.fsinf.at/wiki/TU_Wien:Advanced_Multiprocessor_Programming_VU_(Tr%C3%A4ff)>, read 2026-09-28 in the browser pane. Public, student-written; summarised, not copied.
- Used for: 2 theory sheets presented at the blackboard; pair project on a provided framework with a detailed report (description, linearisability, deadlock/starvation freedom, benchmarks); oral exam as project discussion (SS2021 and WS2025 reports; 30-40 min; 70 % project, 30 % theory); last offering 2025W; "Materialien": no attachments.

## Primary sources (free author or course copies; cite only)

| S | reference | URL (all HTTP 200 on 2026-09-28 unless noted) | used for |
|---|---|---|---|
| S6 | M. Herlihy, J. Wing, "Linearizability: A Correctness Condition for Concurrent Objects", ACM TOPLAS 12(3), 1990 | <https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf> | definition, locality §3.1, non-blocking property (notes 02, 07) |
| S7 | M. Herlihy, "Wait-Free Synchronization", ACM TOPLAS 13(1), 1991 | <https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf> | consensus number (Def. 1), hierarchy (Fig. 1), queue = 2 (Thm. 7, §3.3), universality (note 04) |
| S8 | R. Blumofe, C. Leiserson, "Scheduling Multithreaded Computations by Work Stealing", JACM 46(5), 1999 | <https://www.csd.uwo.ca/~mmorenom/CS433-CS9624/Resources/Scheduling_multithreaded_computations_by_work_stealing.pdf> (MIT supertech copy 404) | greedy bound, $T_1/P + O(T_\infty)$, space $S_1 P$, communication bound, delay-sequence argument (note 11) |
| S9 | D. Chase, Y. Lev, "Dynamic Circular Work-Stealing Deque", SPAA 2005 | <http://www.dre.vanderbilt.edu/~schmidt/PDF/work-stealing-dequeue.pdf> (https timed out, http works) | the deque (note 11, `work_stealing.cpp`) |
| S10 | G. L. Peterson, "Myths About the Mutual Exclusion Problem", Inf. Proc. Letters 12(3):115-116, 1981 | **paywalled**, <https://doi.org/10.1016/0020-0190(81)90106-X>; no free copy found | Peterson's lock (note 01); the algorithm as given in [S1 §2.3] |
| S11 | L. Lamport, "A New Solution of Dijkstra's Concurrent Programming Problem", CACM 17(8), 1974 | <https://lamport.azurewebsites.net/pubs/bakery.pdf> | bakery algorithm (note 01) |
| S12 | R. K. Treiber, "Systems Programming: Coping with Parallelism", IBM Research Report RJ 5118, April 1986 | <https://dominoweb.draco.res.ibm.com/reports/rj5118.pdf> (listed by search; **timed out 2026-09-28**, not read) | the Treiber stack (note 08); statement as given in [S1 ch. 11] and [S14] |
| S13 | J. Mellor-Crummey, M. Scott, "Algorithms for Scalable Synchronization on Shared-Memory Multiprocessors", ACM TOCS 9(1), 1991 | <https://www.cs.rochester.edu/u/scott/papers/1991_TOCS_synch.pdf> | MCS lock, $O(1)$ remote references, local spinning (note 05) |
| S14 | M. Michael, M. Scott, "Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms", PODC 1996 | <https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf> | MS queue, two-lock queue, counted pointers, free list, ABA (note 07, `ms_queue.cpp`) |
| S15 | T. Harris, "A Pragmatic Implementation of Non-Blocking Linked-Lists", DISC 2001 | <https://www.cl.cam.ac.uk/research/srg/netos/papers/2001-caslists.pdf> | marked `next`, logical vs physical deletion (note 06) |
| S16 | S. Heller, M. Herlihy, V. Luchangco, M. Moir, W. Scherer III, N. Shavit, "A Lazy Concurrent List-Based Set Algorithm", OPODIS 2005 | <https://people.csail.mit.edu/shanir/publications/Lazy_Concurrent.pdf> | lazy list (note 06) |
| S17 | D. Hendler, N. Shavit, L. Yerushalmi, "A Scalable Lock-free Stack Algorithm", SPAA 2004 | <https://people.csail.mit.edu/shanir/publications/Lock_Free.pdf> | elimination backoff (note 08) |
| S18 | O. Shalev, N. Shavit, "Split-Ordered Lists: Lock-Free Extensible Hash Tables", JACM 53(3), 2006 | <https://people.csail.mit.edu/shanir/publications/Split-Ordered_Lists.pdf> | recursive split ordering, dummy nodes, MSB trick (note 09) |
| S19 | H.-J. Boehm, S. Adve, "Foundations of the C++ Concurrency Memory Model", PLDI 2008 | <https://rsim.cs.illinois.edu/Pubs/08PLDI.pdf> (the HP tech-report link on hboehm.info is dead) | SC for data-race-free programs (note 03) |
| S20 | cppreference, "std::memory_order" | <https://en.cppreference.com/w/cpp/atomic/memory_order> (HTML, CC BY-SA 3.0 / GFDL site) | definitions of release-acquire, seq_cst total order, relaxed example, data race = UB, strongly-ordered platforms (note 03) |
| S21 | J. Preshing, blog posts 2012-2013: "Memory Reordering Caught in the Act", "Acquire and Release Semantics", "Memory Barriers Are Like Source Control Operations", "The Happens-Before Relation" | <https://preshing.com/20120515/memory-reordering-caught-in-the-act/>, <https://preshing.com/20120913/acquire-and-release-semantics/>, <https://preshing.com/20120710/memory-barriers-are-like-source-control-operations/>, <https://preshing.com/20130702/the-happens-before-relation/> | SB experiment on x86 (about one reordering per 6600 iterations on a Xeon W3520), readable intuition (note 03) |
| S22 | H. Sutter, "atomic<> Weapons: The C++ Memory Model and Modern Hardware", C++ and Beyond 2012 | <https://herbsutter.com/2013/02/11/atomic-weapons-the-c-memory-model-and-modern-hardware/> (links to two videos and slides) | recommended viewing; hardware mappings for x86, ARM, POWER (note 03) |
| S23 | P. Sewell, S. Sarkar, S. Owens, F. Zappa Nardelli, M. Myreen, "x86-TSO: A Rigorous and Usable Programmer's Model for x86 Multiprocessors", CACM 53(7), 2010 | <https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf> | store-buffer model, only SB reordering (note 03) |
| S24 | C. Pulte, S. Flur, W. Deacon, J. French, S. Sarkar, P. Sewell, "Simplifying ARM Concurrency: Multicopy-Atomic Axiomatic and Operational Models for ARMv8", POPL 2018 | <https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf> (draft) | ARMv8 model, other-multicopy atomicity (note 03) |
| S25 | N. M. Lê, A. Pop, A. Cohen, F. Zappa Nardelli, "Correct and Efficient Work-Stealing for Weak Memory Models", PPoPP 2013 | <https://fzn.fr/readings/ppopp13.pdf> | C11 orderings of the Chase-Lev deque, Fig. 1, used verbatim in `work_stealing.cpp` (note 11) |
| S26 | M. Michael, "Hazard Pointers: Safe Memory Reclamation for Lock-Free Objects", IEEE TPDS 15(6), 2004 | <https://www.cs.otago.ac.nz/cosc440/readings/hazard-pointers.pdf> | HP algorithm, $R = H + \Omega(H)$, ABA and GC (notes 07, 12) |
| S27 | K. Fraser, "Practical lock-freedom", PhD thesis, Cambridge TR UCAM-CL-TR-579, 2004 | <https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-579.pdf> | epoch-based reclamation §5.2.3 (note 12) |
| S28 | L. Lamport, "How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs", IEEE TC C-28(9), 1979 | <https://lamport.azurewebsites.net/pubs/multi.pdf> | definition of sequential consistency (notes 02, 03) |
| S29 | M. Fischer, N. Lynch, M. Paterson, "Impossibility of Distributed Consensus with One Faulty Process", JACM 32(2), 1985 | <https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf> | FLP (note 04) |
| S30 | W. Pugh, "Skip Lists: A Probabilistic Alternative to Balanced Trees", CACM 33(6), 1990 | <https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf> | expected cost $\le L(n)/p + 1/(1-p)$ (note 10) |
| S31 | ISO C++17 working draft N4659, 2017 | <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf> | [intro.races], [atomics.order] (note 03) |
| S32 | H.-J. Boehm, "How to miscompile programs with 'benign' data races", HotPar 2011; and "Why undefined semantics for C++ data races?" | <https://www.hboehm.info/boehm-hotpar11.pdf>, <https://www.hboehm.info/c++mm/why_undef.html> | no benign races (notes 01, 03) |
| S36 | J. Burns, N. Lynch, "Bounds on Shared Memory for Mutual Exclusion", Information and Computation 107(2), 1993 | **not fetched** (paywalled); bibliographic data from memory, not checked; cited only for the statement of the $n$-register lower bound that [S1 §2.8] proves | note 01 |

## Prerequisite and planning records

| S | what | URL / file | used for |
|---|---|---|---|
| S33 | TISS 184.710 Parallel Computing, 2026S (**cancelled**) | <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184710&semester=2026S&locale=en>, browser pane 2026-09-28 | learning outcomes (work/time, PRAM, threads, OpenMP, MPI, task parallelism), language German, Träff, literature (Träff LNCS 14600; Rauber & Rünger; Schmidt et al.), curricula (not CSE); lists 184.726 AMP as continuative |
| S34 | TISS 191.114 Basics of Parallel Computing, 2026S | <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191114&semester=2026S&locale=en>, browser pane 2026-09-28 | VU 2 h / 3 ECTS, English, Hunold, Thu 10-12, assignments + closed-book written exam, curricula only 066 645, lists 184.726 AMP as continuative |
| S35 | This machine: Apple M3 Pro (6 P + 6 E cores, `hw.cachelinesize` 128), macOS 26 (Darwin 25.6), Apple clang 21.0.0 | measured 2026-09-28 with `make test`, `make tsan`, `make bench`; codegen by `clang++ -O2 -S` (and `-target x86_64-apple-macos`) on a 10-line file of atomic operations | every measured number and the codegen table (notes 01, 03, 05-09, 11, 12) |
| S37 | Student repository "VU Advanced Multiprocessor Programming, TU Wien, SS 2013" (github.com/schuay) | <https://github.com/schuay/advanced_multiprocessor_programming>, read via the GitHub API 2026-09-28; **no licence**: summarised only | 2013 exercise sheets as selections of book exercise numbers; project tasks (counting network, cuckoo hash set, pheet framework, C++11 atomics) and expectations (note 00) |

