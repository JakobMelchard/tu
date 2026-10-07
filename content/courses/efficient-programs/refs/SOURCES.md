# Sources: 185.190 VU Efficient Programs (and 194.189 PR)

Register of every source used to write and verify [`../notes`](../notes/README.md)
and [`../src`](../src/README.md). Notes cite these as `[S<n>]`, slides as
`[S3 p.<slide number>]` (the number printed bottom right of each slide).
Retrieval date for everything: **2026-09-27**. The lecturer's page says the
slides "change during the course of the semester" [S2], so re-check before the
exam.

**Vendoring policy.** Nothing is vendored. Every lecturer file (slides, script,
exercise sheets, TSP and matmul programs) carries no redistribution licence, so
it is fetched into the git-ignored `cite-only/` by
[`fetch-sources.sh`](fetch-sources.sh), cited, quoted at most in short
fragments, and never copied into `notes/` or `src/`. All code under `src/` is
ours. The free literature (Agner Fog, Granlund) is likewise cite-only: a free
download with no licence statement is all rights reserved.

**What exists and what does not.** This course is unusually well documented by
its lecturer: a public English slide deck [S3], a public German prose script
[S4], last year's three exercise sheets [S5]–[S7] and two worked examples with
source [S8] [S9]. What does **not** exist: a past exam paper. The exam is an
oral interview about the course material and about how you obtained your
exercise results [S1] [S2]; there is nothing to mine, see
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md). **TUWEL was not
accessed**: it needs a login, and the 2026W TISS page shows no TUWEL link yet
[S1].

---

## Course-authoritative

### S1: TISS course page 185.190, 2026W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=185190&semester=2026W>
- Retrieved: 2026-09-27 (browser, logged in). Transcribed in
  [`../docs/tiss.md`](../docs/tiss.md); API record in
  `../docs/tiss-api.md`.
- Access: public (dates and text), login for registration status.
- Used for: VU, 2.0 h, 3.0 ECTS, blocked; the seven Monday lectures
  16:00–18:00 in EI 2 from 05.10 to 30.11.2026 with no lecture on 26.10 and
  02.11; the **InfLab bookings** "Test 1" Wed 04.11 10:00–14:00 and "Test" Fri
  20.11 / 04.12 / 18.12 09:00–13:00 (three labs each, unexplained, absent in
  2025W); registration 23.09–13.10.2026 23:59; examination modalities "The
  grade is based on the exercises and on an oral examination"; ECTS breakdown
  20 h lectures, 50 h exercises, 5 h exam; the Subject of course list that
  the deck follows; curricula (CSE: **elective**, not mandatory elective);
  the literature line "Lecture notes for this course are available. See Course
  Homepage".

### S2: Course homepage (A. Ertl, complang) ★

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/effiziente-programme.html>
- Retrieved: 2026-09-27, 6 845 bytes → `cite-only/S2-course-homepage.html`.
- Access: public. No licence stated.
- Used for: grading in the lecturer's words: exercises "where you have to
  deliver some results", and "The grade will be based on an oral exam that
  checks your knowledge of the course material, as well as whether you can
  explain how you achieved the exercise results"; accounts on
  `g0.complang.tuwien.ac.at` created in batches on Tuesdays; TUWEL
  auto-enrolment; German lecture videos 2020W/2021W; the PR rules: group of
  3–5, program of your choice, grade = presentation, the presentation must
  say which optimisation steps worked how well against expectations and why;
  algorithmic optimisation allowed and "usually expected", write it
  straightforwardly then apply measurable non-algorithmic steps; results
  directory `effizienz-abgaben/2025w/`; attendance at the presentations
  required; the link list (slides, TSP programs, matmul example, 2022W German
  notes and slides). Also the curriculum claim (CSE module "Computational
  Informatics", mandatory elective) that TISS [S1] contradicts.

### S3: Slides: *Efficient Programs*, English deck ★★ (primary source)

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/efficient.pdf>
- Retrieved: 2026-09-27. 871 478 bytes, 100 pages, pdfTeX 1.40.21, created
  2025-11-17 17:28 CET.
  `sha256 1350c909480e1273c322e7d85c8a342df5b6956b6358fe01f0ee25358349fa1c`
  → `cite-only/S3-efficient-slides.pdf`; `pdftotext -layout` →
  `cite-only/S3-efficient-slides.txt` (1 623 lines). **Caveat:** the PDF
  encodes the en-dash of number ranges as the control character `\025`,
  which the `.txt` drops: p.14 reads "28", "35c", "01c", "3090c" for
  2–8, 3–5 c, 0–1 c, 30–90 c, and prints "50–ns" (upper bound missing) for
  DRAM. Ligatures fi/ff are dropped too ("eciency"). Check numbers against
  the rendered PDF (`pdftoppm -f N -l N -png`).
- Access: public. No licence stated. Not vendored.
- Used for: **everything** in notes 01–10. The deck order is the note order,
  see [`lecture-notes-map.md`](lecture-notes-map.md). Specifically: the
  method loop (p.8); tools (p.9, 22, 23); compiler vs programmer and the
  stumbling blocks (p.10–13); the latency table (p.14) and the Rocket Lake
  recurrence measurements 1.52 / 5 / 3.73 / 1.27 / 0.3 / 0.16 c/iteration
  (p.16–18); the Skylake cache/TLB parameters (p.21); complexity (p.25);
  SIMD and the vectorisable-loop recipe (p.28–32); memmove/memcpy and
  Hyrum's law (p.33); Bentley's transformation catalogue (p.39–68); packing,
  factoring, energy and DVFS (p.69–74); TSP steps tsp1→tsp9 and tspi4
  (p.75–85); matmul mm1→mm7 with c/iteration and the ATLAS/OpenBLAS figures
  (p.86–96); I/O, system-call costs, io_uring (p.97–100).

### S4: Script: *Effiziente Programme*, 2022W, German prose ★

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/skriptum-effizienz.html>
- Retrieved: 2026-09-27, 29 274 bytes → `cite-only/S4-skriptum-effizienz-2022w.html`.
- Access: public. No licence stated.
- Used for: the literature list at its head (S11–S15, S20 below); the prose
  version of slides 1–25 (why efficiency, costs, "1–10 s waits cost about
  three times the time", Bentley's 1982 prices, Kernighan quotes, the method,
  what compilers can and cannot do, the 2001 latency table for comparison
  with p.14, Fenwick 2001 on KMP vs naive search, languages); the measured
  **cycle counts of the TSP steps** on a Celeron (57.5 M → 13.2 M) and the
  normalised comparison table against Bentley's PDP-KL10 and HP1000; the
  perf/gprof/gcov command lines with `:u` explained. Its transformation part
  says "this year only the slides".

### S5: Exercises 1, 2025W (deadline 2025-10-24)

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/efficient/25/exercises1.html>
- Retrieved: 2026-09-27 → `cite-only/S5-exercises1-2025w.html`. Public.
- Used for: the question types in note 00 and 11: Q1–Q6 five unknown binaries
  `q1a..q1e`, one `/bin/time` transcript, "fast enough?", CPU-bound, user vs
  system mode, most memory, most CPU time; Q7–Q11 `gcc -O magichex.c`,
  `./magichex 3 0`, gprof (most time, most calls, who calls `sethi`, callee of
  `lessthan`), gcov (most executed line in `solve`, delete `.gcda` first).
  Submission: `1/Exercises1.txt` in a git project, transcripts via `script -f`,
  "document how you arrived at the answers … useful for preparing yourself
  for the interview part of the exam".

### S6: Exercises 2, 2025W (deadline 2025-11-03)

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/efficient/25/exercises2.html>
- Retrieved: 2026-09-27 → `cite-only/S6-exercises2-2025w.html`. Public.
- Used for: the latency-vs-bandwidth exercise: `2.zip` with `e2work1.c`,
  `e2main1.c`, a Makefile measuring 100 000 000 iterations of `list1`,
  `array1`, `array2`, `list2`; Q1 add as many `instructions:u` to `list1()`
  as fit under 600 000 000 `cycles:u`; Q2 the same computation in `array1()`,
  cycles; Q3 add code to `array2()` that burns as many cycles as possible
  under 810 000 000 instructions; Q4 the same in `list2()`. Constraints: data
  structures, iteration count and `e2main1.c` unchanged, ≤ 20 cycles/
  instructions of setup, unused computations are optimised away.

### S7: Exercises 3, 2025W (deadline 2025-12-09) ★

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/efficient/25/exercises3.html>
- Retrieved: 2026-09-27 → `cite-only/S7-exercises3-2025w.html`. Public.
- Used for: the whole of note 04's measurement half and `src/c/pointer_chase.c`.
  `memory1 random|linear <elements> <stride>`: 100 M dependent accesses through
  a cyclic list; `LC_NUMERIC=prog perf stat -e cycles`; the event list
  (`L1-dcache-load-misses`, `l2_rqsts.demand_data_rd_miss`, `LLC-loads`,
  `LLC-load-misses`, `longest_lat_cache.miss`, `dtlb_load_misses.stlb_hit`,
  `dTLB-load-misses`, `dtlb_load_misses.walk_completed`); the worked example
  `random 5000 8` → 501 793 612 cycles, 35 203 L1 misses, 449 dTLB misses,
  i.e. 5 cycles per L1 hit; the advice to size for one way less than the
  cache has; the eleven questions (L1 size, line size, L2 size, L2 latency
  linear vs random, DRAM latency and ns, prefetched DRAM bandwidth against
  46.9 GB/s theoretical, conflict misses at stride 8192/4096/2048 →
  associativity, ways, sets; L1 TLB entries at stride 131136 …, TLB miss
  penalties, L2 TLB entries); the remark that the course machine is a
  **Rocket Lake** and that its clock drops when waiting on DRAM.

### S8: Matrix multiply worked example (German page + `main.c`, `mm1.c`–`mm5.c`, `Makefile`)

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/effizienz/matmul/>
  (index page; the files are linked from it)
- Retrieved: 2026-09-27 → `cite-only/S8-matmul-example.html`,
  `S8-matmul-main.c`, `S8-matmul-mm1.c` … `S8-matmul-mm5.c`,
  `S8-matmul-Makefile`. Public. No licence stated; **not copied** into `src/`.
- Used for: note 09. The machine (Core i3-3227U, 32 KB L1, 256 KB L2, 3 MB
  L3), `perf record`/`perf annotate` on `mm1 700` (99 % in `matmul`, the
  `addsd` recurrence of 4 cycles), the perf-stat tables for `mm1`, `mm2-O2`,
  `mm2 -O3 -mavx`, `mm3`, `mm4`, `mm5`, `limit1/2`, `mm6`, `mm7`, `atlas`,
  `openblas` (cycles, instructions, IPC, L1/LLC/dTLB misses); the TLB
  explanation of `mm1 700` (stride 5 600 B > 4 KB page, 512 L2-TLB entries);
  transparent huge pages; the `v4d` GNU vector extension; recursion as
  cache-oblivious blocking; the 2-/4-process contention experiment; OpenBLAS
  thread scaling. Its Makefile shows `-O3 -mavx2 -mfma` and the `perf` target.

### S9: Bentley's TSP programs in C (`tsp.html`, `tsp1.c`–`tsp9.c` without `tsp7.c`, `Makefile`)

- URL: <http://www.complang.tuwien.ac.at/anton/lvas/effizienz/tsp.html>
- Retrieved: 2026-09-27 → `cite-only/S9-tsp.html`, `S9-tsp1.c` … `S9-tsp9.c`
  (no tsp7: Bentley's step 7, integers instead of floats, was not
  transliterated), `S9-Makefile`. Public. No licence stated; **not copied**.
- Used for: note 08. What each step changes, read from the sources: CSE of
  `dist()` (tsp2), `DistSqrd` without `sqrt` (tsp3), `visited[]` replaced by
  swapping within `tour[]` (tsp4), inlining (tsp5), lazy y-distance (tsp6),
  `tour` becomes an array of points (tsp8), sentinel loop `for (j=ncities-1;;j--)`
  with `<=` and `if (j<i) break` (tsp9); `alloca`, `random()/(1U<<31)` input,
  EPS output checked with `diff tsp.eps tsp_ref.eps` (Makefile `check`).

### S10: TISS course page 185.190, 2025W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=185190&semester=2025W>
- Retrieved: 2026-09-27 (browser). Summarised in [`../docs/tiss.md`](../docs/tiss.md) § 2025W vs 2026W.
- Used for: the year-on-year diff. Same text, ECTS and modalities; seven
  Mondays 06.10–17.11.2025; registration 24.09–14.10.2025; TUWEL link shown;
  **no InfLab dates at all**. This is what makes the 2026W "Test" bookings
  new and unexplained.

## Literature named by the course (script [S4], slides [S3])

### S11: J. L. Bentley, *Writing Efficient Programs*, Prentice Hall 1982

- ISBN 0-13-970244-X. Out of print; library or second hand
  (<https://openlibrary.org/search?q=writing+efficient+programs+bentley>).
- Access: not free. Not vendored.
- Used for: the origin of the transformation catalogue (p.39–68) and of the
  TSP example (p.75). [S4] asks that chapter 2 not be read in advance. The
  normalised step table in [S4] compares the Celeron numbers with Bentley's
  PDP-KL10 (Pascal) and HP1000 (C) figures.

### S12: M. Abrash, *Graphics Programming Black Book*, Special Edition, Coriolis 1997

- URL: <https://www.jagregory.com/abrash-black-book/> (free HTML/epub edition,
  released by the author; source <https://github.com/jagregory/abrash-black-book>).
- Access: free. Not vendored.
- Used for: named in [S4]'s literature list; not cited for any specific claim.

### S13: A. Fog, optimisation manuals ★

- URL: <https://www.agner.org/optimize/>; manual 3
  <https://www.agner.org/optimize/microarchitecture.pdf>, manual 4
  <https://www.agner.org/optimize/instruction_tables.pdf>, manual 1
  <https://www.agner.org/optimize/optimizing_cpp.pdf>.
- Access: free download, copyright line only → not vendored; fetched by the
  script.
- Used for: [S4] names manuals 3 and 4 as the source for processor details.
  Checked in the fetched copies on 2026-09-28: manual 3, chapter 12 "Intel
  Ice Lake and Tiger Lake pipeline": five instructions per clock (Skylake
  four), 352-entry reorder buffer, two loads per clock, misprediction penalty
  16 to 20 c, L1d 48 kB 12-way 64 sets latency 4, L2 512 to 1 280 kB (table
  12.3); manual 4, Ice Lake table: `DIV r64` 15 c, `DIVSD` 13 to 14 c,
  `SQRTSD` 15 to 16 c. Rocket Lake is not named in either manual; that its
  Cypress Cove core is a Sunny Cove (Ice Lake) backport is general knowledge,
  so these figures are expectations for g0, not measurements of it.

### S14: Intel 64 and IA-32 Architectures Optimization Reference Manual (doc. 248966)

- URL: <https://www.intel.com/content/www/us/en/content-details/671488/intel-64-and-ia-32-architectures-optimization-reference-manual.html>
  ([S4]'s link `intel.com/design/processor/manuals/248966.pdf` is dead).
- Access: free. Not vendored.
- Used for: named in [S4]. Reference for the TopDown method behind
  `perf stat -M TopdownL1` (p.23); cited for general knowledge not in the
  course material (prefetchers not crossing 4 KB pages, counter numbers),
  which the notes flag as such. Not downloaded; not checked page by page.

### S15: T. Granlund, *Instruction latencies and throughput for AMD and Intel x86 processors*

- URL: <https://gmplib.org/~tege/x86-timing.pdf>
- Access: free. Not vendored; fetched by the script.
- Used for: named in [S4]; second source for instruction latencies.

## Tool documentation

### S16: Linux `perf`

- URL: <https://perf.wiki.kernel.org/>, man pages
  <https://man7.org/linux/man-pages/man1/perf-stat.1.html>,
  <https://man7.org/linux/man-pages/man1/perf-record.1.html>,
  <https://man7.org/linux/man-pages/man1/perf-annotate.1.html>.
- Used for: the semantics of `-e event:u`, `-M TopdownL1`, multiplexing (the
  percentage in parentheses, also explained in [S7]), `perf list`.

### S17: GNU `gprof` manual

- URL: <https://sourceware.org/binutils/docs/gprof/>
- Used for: flat profile vs call graph, `-pg`, `gmon.out`, sampling at 100 Hz
  (0.01 s) plus call counting by instrumentation.

### S18: GCC `gcov` documentation

- URL: <https://gcc.gnu.org/onlinedocs/gcc/Gcov.html>
- Used for: `--coverage`, `.gcno`/`.gcda`, accumulation across runs (why [S5]
  says delete `magichex.gcda`), the `.gcov` line format. Apple clang ships a
  compatible `gcov` (`/usr/bin/gcov`, llvm-cov), verified on the host [S19].

### S19: The host used for every measured number in the notes

- Apple M3 Pro (`sysctl -n machdep.cpu.brand_string`), 6 P + 6 E cores,
  36 GB; `hw.perflevel0.l1dcachesize` = 131 072 (P-core L1d 128 KB),
  `hw.perflevel0.l2cachesize` = 16 777 216 (P-cluster L2 16 MB),
  `hw.cachelinesize` = 128; macOS 26.7, Apple clang 21.0.0
  (`arm64-apple-darwin25.6.0`). Tools present: `cc`, `/usr/bin/time` (`-l`
  gives maxresident), `gcov`, `pdftotext`. **Absent: `perf`, `gprof`**
  (`-pg` is accepted but writes no `gmon.out`). Cycle counts in the notes are
  ns × 4.05 GHz, an assumed P-core clock: macOS exposes no cycle counter to
  user code and no frequency in `sysctl`, so they are estimates and labelled
  as such.

### S20: AMD software optimisation guides

- [S4] links three AMD guides (Family 10h, Athlon 64/Opteron, Athlon); all
  three URLs are dead. Current guides: <https://www.amd.com/en/search/documentation/hub.html>
  (e.g. *Software Optimization Guide for the AMD Zen 4 Microarchitecture*,
  pub. 57647). Not used for any claim.

### S21: Chips and Cheese articles reproduced on the slides

- p.15 out-of-order diagram: <https://chipsandcheese.com/p/sandy-bridge-setting-intels-modern-foundation>;
  p.73–74 power curves: <https://chipsandcheese.com/2022/01/28/alder-lakes-power-efficiency-a-complicated-picture/>.
  p.72 is a Zhihu graphic (<https://zhuanlan.zhihu.com/p/653961282>).
- Used for: attribution only.

### S22: Hyrum's law

- URL: <https://www.hyrumslaw.com/>. Quoted on p.33. Used in note 05.
