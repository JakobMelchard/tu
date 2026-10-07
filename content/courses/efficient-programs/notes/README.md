# 185.190 Efficient Programs: notes

One note per section of the lecturer's slide deck [S3], in deck order (the
map is [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md)). Each
note: what the topic is, definitions and results with formulas, a worked
example with numbers measured on [`../src/c`](../src/README.md), pitfalls,
five interview-style questions with answers (the exam is oral [S1] [S2]), and
pointers into the code. Assumed background: a physics master's; computer
science terms are defined, calculus is not.

Every factual claim about the course cites [`../refs/SOURCES.md`](../refs/SOURCES.md)
as `[S<n>]`; slides as `[S3 p.<n>]` with the number printed bottom right of the
slide. Changes are in `CHANGELOG.md`.

| # | note | one line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | exercises + oral interview, what the 2025W sheets asked, the unexplained InfLab dates, how to weight the notes |
| 01 | [Why efficiency, and the method](01-why-efficiency-and-method.md) | when efficiency is needed, its kinds and costs, latency budgets, the other goals, the 80/20 rule, the test-measure-profile-transform loop, what compilers can and cannot do, Amdahl for one program |
| 02 | [Measurement and profiling](02-measurement-and-profiling.md) | `time`, `gprof`, `gcov`, `perf stat`/`record`/`annotate`, counters and `:u`, multiplexing, TopDown, instrumentation, what each output column means |
| 03 | [Hardware: latency and throughput](03-hardware-latency-and-throughput.md) | the latency table, out-of-order execution, recurrences and the cycles-per-iteration bound, accumulators, branch prediction cost, forms of parallelism |
| 04 | [Memory hierarchy](04-memory-hierarchy.md) | lines, sets, ways, tag/index/offset arithmetic, miss types, TLB reach, prefetchers, strided miss rates, measuring cache and TLB parameters |
| 05 | [Algorithms, specification, languages](05-algorithms-specification-languages.md) | O(...) and its blind spots, constant vs logarithmic factors, abstraction cost, under/over-specification (memmove/memcpy), Hyrum's law, inherent vs idiomatic inefficiency |
| 06 | [Vectorisation and the compiler](06-vectorisation-and-the-compiler.md) | SIMD registers, the vectorisable-loop recipe, reductions and associativity, aliasing and `restrict`, flags (`-O2/-O3`, `-march`, `-ffast-math`), what `-O3` does not do, SWAR |
| 07 | [Source-level transformations](07-source-level-transformations.md) | Bentley's catalogue from slides 39 to 68: condition and effect of each, cost models for test reordering and flag arithmetic, where the TSP steps fit |
| 08 | [TSP worked example](08-tsp-worked-example.md) | greedy nearest neighbour, tsp1 to tsp9 with the script's cycle counts, tspi4, our four versions and why the "obvious" step was slower |
| 09 | [Matrix multiply worked example](09-matmul-worked-example.md) | loop order and the six nestings, the add recurrence, TLB misses at n = 700, explicit vectors, unrolling, recursion as blocking, ATLAS/OpenBLAS, our five versions |
| 10 | [Memory, energy and I/O efficiency](10-memory-energy-io.md) | packing and factoring, $P = CU^2 f$ and race-to-idle, system-call cost model, buffering, zero-copy, asynchronous I/O and io_uring |

**Sources.** Unusually for a TU course, the lecturer publishes everything
except the exam: the English slides [S3] (primary), the 2022W German script
[S4], last year's three exercise sheets [S5] [S6] [S7], the matmul [S8] and
TSP [S9] example programs, all linked from the course homepage [S2]. The
literature the script names is Bentley's *Writing Efficient Programs* (1982)
[S11], Abrash's Black Book [S12], Agner Fog's manuals [S13], Intel's
Optimization Reference Manual [S14] and Granlund's timing tables [S15]. None
of it is redistributable, so nothing is vendored and no lecturer code is
copied; see [`../refs/README.md`](../refs/README.md). TUWEL was not accessed:
the 2026W TISS page shows no TUWEL link yet [S1], so every TUWEL claim
in these notes is unverified.

**Course facts, as of 2026-09-28** [S1] [S2]: VU, 2.0 h, 3.0 ECTS = 75 h
(20 h lectures, 50 h exercises, 5 h exam), English, blocked: seven Monday
lectures 16:00 to 18:00 in EI 2 on 05.10, 12.10, 19.10, 09.11, 16.11, 23.11
and 30.11.2026 (none on 26.10 and 02.11);
registration and deregistration until 13.10.2026 23:59; grade from the
exercises and an oral exam that is an interview about the material and about
how the exercise results were obtained; measurements on
`g0.complang.tuwien.ac.at` (Rocket Lake [S7]), accounts in Tuesday batches.
New and unexplained in 2026W: InfLab bookings "Test 1" Wed 04.11 10:00 to
14:00 and "Test" Fri 20.11, 04.12, 18.12 09:00 to 13:00 [S1], absent in 2025W
[S10]. For CSE the VU is an elective [S1]. The
PR (194.189) holds its presentations on Mondays 16:00 to 18:00 in EI 2 on
14.12.2026, 11.01, 18.01 and 25.01.2027 (its TISS page, transcribed in
[`../../efficient-programs-project/docs/tiss.md`](../../efficient-programs-project/docs/tiss.md)),
attendance required [S2], and is not in the CSE curriculum at all (that page
lists only 066 937 Software Engineering).

**Versions and host.** Every measured number in these notes comes from
`make -C ../src/c bench` (ranges over four runs on 2026-09-28; most kernels
differ by about 10 % between runs, the 8 to 32 MB points of the memory sweep
by up to 2×) on an Apple M3 Pro (P-core L1d 128 KB, L2 16 MB,
128 B lines, macOS 26.7, Apple clang 21.0.0, `-O2 -std=c11`) [S19]. What
was **demonstrated** here: the six programs, `/usr/bin/time -l`, `gcov`
(`make gcov`), clang's `-Rpass=loop-vectorize` remarks, reading the generated
assembly (`cc -O2 -S`). What is **only described** because macOS lacks the tool: `gprof`
(`-pg` compiles but writes no `gmon.out`), `perf stat`, `perf record`,
`perf annotate`, TopDown, and every hardware counter. Cycle figures marked
"~" are ns × 4.05 GHz, an **assumed** P-core clock (macOS exposes neither a
cycle counter nor the frequency), and are estimates; on g0 read `cycles:u`
instead. The slides' own numbers are from a Rocket Lake [S3 p.16
to 18], a Skylake [S3 p.21] and an Ivy Bridge i3 [S8]; the script's from a
Celeron [S4]. Shapes transfer, constants do not.
