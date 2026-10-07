# 00 Exam focus: status, assessment, what to expect

Written 2026-09-28 for a course that is **not running**: 191.022 is
cancelled in 2026W and expected again from **2027W**. Everything below is
either what a TISS page or VoWi states (cited), or marked as inference.
TUWEL was not used (course material there is not ours to copy).

## Status

| fact | value | source |
|---|---|---|
| 2026W offering | **cancelled**: "This course will not be offered this semester (2026W)! Expected to be offered again from 2027W onward." | [S2] |
| Next offering | **2027W**, the earliest possible slot | [S2] |
| Curriculum | **mandatory, CSE (066 646) 3rd semester**; also mandatory 1st semester in 066 938 Computer Engineering, mandatory elective in 066 525, 066 645, 066 937 | [S2] [S3] |
| Type | VU 4.0 h, 6.0 ECTS, presence, English, mode of examination **immanent** (continuous assessment) | [S2] [S3] |
| Assessment | "Exercises (hand-ins), project, oral or written exam" | [S2] [S3] |
| Teaching | "Lectures and discussion, active participation, blackboard exercises, project work." | [S2] |
| Lecturer | 2026W page: **Hunold, Sascha** (E191). 2025W: Träff, Hunold, Felber | [S2] [S3] |
| Book | Herlihy & Shavit, *The Art of Multiprocessor Programming*, revised 1st ed. 2012 or later; plus slides and papers | [S2] |
| Registration | 2026W page: **"Not necessary"**. But 2025W had a TISS course registration (15.09.2025-10.10.2025, deregistration until 27.10.2025) and a separate exercise-group registration (15.10.-22.10.2025) | [S2] [S3] |
| Previous knowledge | "Introduction to Parallel Computing"; preceding course 184.710 VU Parallel Computing; the "Precon." column of the curricula table is **empty** for CSE, so it is not a formal precondition | [S2] [S3] |

**Reading of the registration line (inference):** "Not necessary" is what a cancelled page shows; the last real offering needed registration in TISS. Expect a window from mid-September to early October 2027 and a group registration in October. Verify on the 2027W page.

**Risk (inference):** the course is mandatory and was cancelled once. If it is not offered in 2027W either, a CSE 3rd semester has a mandatory gap. Watch the TISS page from July 2027.

## The last real schedule: 2025W [S3]

Read 2026-09-28 from the public TISS page (it needs JavaScript; WebFetch returned only the loading shell, so it was read in a rendering browser).

- **Lecture** Mon 12:00-14:00, EI 11 HS - INF: 06.10, 13.10, 20.10, 27.10, 03.11, 10.11, 17.11, 24.11, 01.12, 15.12.2025, 12.01, 19.01, 26.01.2026 (13 dates). "First Lecture: 6.10.2025 (Attendance MANDATORY)"; "Attendance Required!".
- **Exercise extra date** Thu 11.12.2025 14:00-17:00, Seminarraum Techn. Informatik.
- **Exercise groups** (weekly, 5 weeks): 1-3 Thu 13-15 / 15-17 / 17-19, Sem.R. DA grün 04, 23.10.-20.11.2025; 4-5 Fri 08-10 / 10-12, Sem.R. DA grün 06B, 24.10.-21.11.2025; 6 Fri 12-14, Sem.R. DB gelb 09.
- **No exam dates** on the page.
- The predecessor **184.726** (same title and subject text, 4.5 ECTS, offered 2012S-2024W) had in 2024W: lecture Mon 11:00-13:00 EI 11 HS - INF, four Friday exercise afternoons, and "Exercises (hand-ins), project, oral project presentation" [S4]. The renumbering to 191.022 in 2025W raised the ECTS to 6.0 and added "oral or written exam" and 16 h exam preparation [S3] [S4].


## Workload [S2]

150 h = overview 1.5 h + lectures 15 x 2 h + preparation and digestion 15 x 1.5 h + **projects and exercises 80 h** + exam preparation 16 h. More than half the credit is the practical part.

## What the assessment has looked like

From VoWi (student reports, not official) [S5]:

- **Exercises**: two theoretical sheets, worked at home, presented at the blackboard in exercise sessions (volunteers, closer to a discussion); they must be handed in and should be written up cleanly.
- **Project**: in pairs. First get the course's framework running, then implement one concurrent data structure (most were lock- or wait-free, one had to use locks). Deliverable: a detailed report with the data structure, a theoretical analysis (linearisability, deadlock- and starvation-freedom) and benchmarks. The effort of the project is easy to underestimate; AddressSanitizer and Valgrind help with crashes.
- **Exam**: oral, essentially a discussion of the project report with the lecturers and the project partner. SS2021: project plus basic questions (definition of lock-free, wait-free, ABA problem, TSO). WS2025: 30-40 minutes, questions on the implementation and the theory behind it, then one lecture topic (in that report: the list-based sets and lock-free vs wait-free); weighting reported as **70 % project, 30 % theory**; advice: know every slide set conceptually (no proofs), and know your own code.

From a public student repository of the 2013 predecessor [S37] (old, but the only primary material found):

- Exercise sheets were **selections of book exercises by number**: "any 12 of {6, 7, 9-15, 34-36, 38-43}" and "any 10 of {21-24, 27, 32, 51-54, 58, 62, 65, 68}" from the revised 1st edition.
- Projects: a periodic **counting network** compared against fetch-and-increment, and a concurrent **cuckoo hash set**, both in C++11 atomics inside the TU Wien task-parallel framework *pheet*; expected: an efficient and correct implementation, a theoretical analysis (invariants, linearisability, progress guarantees), a benchmark analysis, and a 2-4 page document.

## What the book's exercises look like

By the content of the 2013 selections and the solutions in the same repository [S37] (the book is not free; exercise texts are only paraphrased):

| numbers (rev. 1st ed.) | chapter by content | typical task | our note |
|---|---|---|---|
| 6 (7 probably) | 1 | Amdahl's law: a method that cannot be parallelised takes 40 % of the time; what speedup? | NSSC I 07 |
| 11-15 (9, 10 not checked) | 2 | a modified lock ("Flaky", Filter, "FastPath"): prove or refute mutual exclusion, deadlock-freedom, starvation-freedom | 01 |
| 21-32 | 3 | why quiescent consistency is compositional (21); a queue whose `enq()` has no fixed linearisation point (32) | 02 |
| 34-43 | 4 | register constructions (safe, regular, atomic MRSW) and Peterson with weaker registers (40) | 01, 03 |
| 51-68 | 5 | from: binary consensus impossible implies $k$-valued consensus impossible (51), to consensus numbers of `getAndSet`/`getAndIncrement` (68) | 04 |

The answer format is the one practised in notes 01-04: a precedence chain $a \to b \to \dots$ leading to a contradiction, or a concrete interleaving as counterexample. Each note ends with five exam-style questions with answers.

## How the 80-hour project usually looks

Combining [S2] [S5] [S37] (the 2027W task is not known):

1. **Get the harness running** on the course machine: a provided benchmark framework (pheet in 2013; whatever it is now), C or C++ with pthreads or C++ atomics, or Java [S2].
2. **Implement one structure** from the book's catalogue: a lock-free or wait-free set, queue, stack, priority queue, hash set, counting network, or a lock-based one for comparison.
3. **Argue correctness in writing**: representation invariant, linearisation points for every method and outcome, progress guarantee (lock-free / wait-free / deadlock-free / starvation-free) with a proof sketch.
4. **Benchmark**: throughput vs threads for several operation mixes and key ranges, against a coarse-locked baseline, with the machine described. The `--bench` modes in `../src/cpp` are this kind of table.
5. **Discuss it orally**, in the pair.

Rehearsal with our code: extend `lists.cpp` to a lazy skiplist (note 10), with the same `test_set` checks plus a per-level structural check, a linearisability argument, and a thread-scaling table. That is a project-sized, self-checked exercise.

## Prerequisite: 184.710 Parallel Computing is not a formal precondition

What 184.710 covers (TISS 2026S page, itself **cancelled** that semester; taught in German by Träff) [S33]: asymptotic running time and work of parallel algorithms; the PRAM model; thread models; programming in OpenMP and MPI; task-parallel models (Cilk); performance measurement. Literature: Träff, *Lectures on Parallel Computing* (Springer LNCS 14600); Rauber & Rünger; Schmidt et al.

A smaller, English sibling exists: **191.114 Basics of Parallel Computing** (Hunold, VU 2 h, 3 ECTS, summer term; 2026S: Thu 10-12, written closed-book exam plus two assignments; lists 184.726 AMP as a continuative course) [S34]. It runs in the summer term, so it **can be taken in the summer before** AMP. Its curricula table lists only 066 645 Data Science; whether it counts for CSE (e.g. as a free elective) is **not known**: check before relying on it.

What AMP actually uses from it, and where to self-study instead (inference from the AMP syllabus [S2]):

| needed for AMP | self-study here |
|---|---|
| threads, shared memory, races, locks, OpenMP tasks, Amdahl | [NSSC I note 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md) and its `threads_cpp.cpp` |
| caches, coherence, false sharing, latency | Efficient Programs 03, 04 |
| work and span, greedy scheduling | note 11 here (derived from [S8]) |
| C++ atomics and memory orders | note 03 here |
| MPI, PRAM algorithms | **not needed** for AMP's syllabus [S2] |

## Verify when the 2027W page appears

1. Offered at all? Lecturers? (Träff, Hunold, Felber in 2025W; Hunold alone on the cancelled page.)
2. Course registration window and exercise-group registration (2025W: 15.09-10.10 and 15.10-22.10).
3. Lecture slot (2025W Mon 12-14) and group slots.
4. First lecture date: attendance mandatory in 2025W.
5. Examination modalities: still "oral or written exam"? Exam dates listed?
6. ECTS breakdown (80 h projects/exercises) and project language/framework.
7. Whether 184.710 or 191.114 appears in the "Precon." column.
8. TUWEL access before the semester.

Sources: [S1] [S2] [S3] [S4] [S5] [S8] [S33] [S34] [S37].
