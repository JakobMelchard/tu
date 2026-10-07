# 02 Measurement and profiling

Slides 9, 22 and 23 [S3]; the script's *Messwerkzeuge* section [S4]; the
tool manuals [S16] [S17] [S18]. The exercise sheets [S5] [S6] [S7] use these
tools. On this Mac only `time` and `gcov`
could be run; `gprof` and `perf` are described from the sources and their
manuals and must be practised on g0 [S19].

## `time` and `/bin/time` [S3 p.9] [S5]

```
/bin/time ./prog >/dev/null            # GNU time (g0): "0.87user 0.02system 0:00.90elapsed 99%CPU ... 3424maxresident"
/usr/bin/time -l ./prog                # macOS: real/user/sys, then "maximum resident set size" in bytes
/bin/time -v ./prog                    # GNU: one field per line
```

Three times: **user** (CPU time executing your code), **system** (CPU time
the kernel spent on your behalf: system calls, page faults, copying), **elapsed**
(wall clock). Derived facts:

- **CPU-bound** iff $\text{user} + \text{system} \approx \text{elapsed}$ (the
  `%CPU` field near 100 %). Otherwise the process waited: I/O, sleep,
  another process.
- Mostly **user** time: computation. Mostly **system** time: system calls,
  memory management (page faults on a large `malloc`, `mmap`), I/O through
  the kernel; note 10.
- **Memory**: `maxresident` (kB on GNU, bytes on macOS) is the peak resident
  set. It does not count memory that was allocated but never touched.
- **Fast enough**: compare elapsed against the budgets of note 01 (300 ms
  for a command).
- **Most CPU time**: user + system, not elapsed.

Our run: `/usr/bin/time -l ./profile_demo --bench` gives `0.07 real 0.07 user
0.00 sys` to `0.08 real 0.08 user 0.00 sys`, 3 424 256 bytes maximum resident
set size [S19]: CPU-bound, user mode, 3.3 MB.

## `gprof`: function-level profile [S3 p.9] [S17] [S5]

```
gcc -pg -O tsp1.c -lm -o tsp1      # -pg: call counting instrumentation (mcount at every function entry)
./tsp1 10000 >/dev/null            # writes gmon.out
gprof tsp1                         # flat profile, then call graph
```

Mechanism [S17]: two data sources. **Call counts** come from the `mcount`
call the compiler inserts at every function entry, so they are exact.
**Time** comes from sampling the program counter at 100 Hz (every 0.01 s),
so it is statistical: with $N$ samples in a function the relative standard
error is about $1/\sqrt{N}$; a function with 4 samples (0.04 s) is known to
±50 %. Two tables:

- *Flat profile*: `% time`, `cumulative seconds`, `self seconds`, `calls`,
  `self ms/call`, `total ms/call`, `name`. Time spent in a function is `self
  seconds`; how often it was called is `calls`.
- *Call graph*: for each function, its parents with the number of calls from
  each, and its children. Who calls whom, and how often, is read here.

Caveats: inlined functions disappear (compile with `-O`, not `-O3`; or `-fno-inline` to see them, which changes the program); time in
library functions without `-pg` (libc, libm) is attributed to the caller;
`gmon.out` is overwritten per run. Not available on macOS: `-pg` compiles and
links but no `gmon.out` appears [S19]; `sample`/Instruments are the
substitutes.

## `gcov`: line-level execution counts [S3 p.9] [S18] [S5]

```
gcc -O --coverage tsp1.c -lm -o tsp1   # .gcno (graph) at compile time
rm -f tsp1.gcda; ./tsp1 10000 >/dev/null   # .gcda (counts) at run time, ACCUMULATES over runs
gcov tsp1.c; cat tsp1.c.gcov
```

Mechanism [S18]: the compiler adds counters on arcs of the control-flow graph
(enough of them that every basic block's count can be derived); counts are
exact, not sampled, and are execution counts, not time.
Format of `tsp1.c.gcov`: `count: line: source`, `#####` for a line with code
that never ran, `-` for a line without code. Because the `.gcda` accumulates,
delete it before the measured run; a forgotten delete adds the earlier runs'
counts (two identical runs double every count).

Verified here (`make -C src/c gcov`, Apple clang's `gcov` is llvm-cov in
disguise [S19]); the top of the sorted output for one default run of
`profile_demo` (limit 200 000, what `make gcov` runs):

```
  3629199:   34:    for (long d = 3; d * d <= n; d += 2)
  3529200:   35:        if (n % d == 0) return 0;
   416270:   55:        for (long m = n * n; m < limit; m += n) comp[m] = 1;
   200001:   42:    for (long n = 0; n < limit; n++)
```

The trial-division loop body runs 3.5 million times for 200 000 calls, the
sieve's inner line 0.4 million: a count ratio of 8.5×, while note 01 measures
a time ratio of about 19× (at limit 2 000 000, where the counts diverge
further). Coverage tools answer "how often", profilers answer "how long":
line 35 is an integer division (`n % d`, 30 to 90 c on the slide's machine
[S3 p.14]), the sieve line a byte store. Use both.

## `perf stat`: hardware performance counters [S3 p.22] [S4] [S16]

```
perf list                                                   # events this CPU and kernel know
perf stat -e cycles:u -e instructions:u -e L1-dcache-load-misses:u -e dTLB-load-misses:u ./tsp1 10000 >/dev/null
perf stat -r 5 -e cycles:u ./prog                           # 5 runs, mean and spread
LC_NUMERIC=prog perf stat -e cycles ./memory1 random 5000 8 # digit grouping with _ as in the ex3 sheet [S7]
```

- **Events**: `cycles`, `instructions`, `branches`, `branch-misses`,
  `L1-dcache-loads`, `L1-dcache-load-misses`, `LLC-loads`, `LLC-load-misses`,
  `dTLB-loads`, `dTLB-load-misses`, plus raw per-microarchitecture events
  such as `l2_rqsts.demand_data_rd_miss`, `dtlb_load_misses.stlb_hit`,
  `longest_lat_cache.miss` (ex3's list [S7]). Names and meanings are in
  `perf list` and Intel's manual [S14]; the sheet itself notes that
  `LLC-load-misses` and `longest_lat_cache.miss` disagree a lot, probably
  because one excludes prefetches [S7].
- **`:u`** counts user mode only: less variance and what your code did, but
  it hides kernel work your code caused, e.g. copy-on-write after a write to
  a page that was so far only read [S4]. Exercise 2 counts `cycles:u` and
  `instructions:u` [S6]; exercise 3's example uses plain `-e cycles` and
  asks for "ns (user time)" [S7].
- **Derived quantities**: $\text{IPC} = \text{instructions}/\text{cycles}$
  (perf prints it as "insns per cycle"); **cycles per iteration** =
  cycles / iteration count, the unit the slides use throughout (`c/It`);
  miss rate = misses / accesses. Time = cycles / clock, but the clock varies:
  ex3 warns that g0's core clocks down while waiting on DRAM, so report ns as
  well as cycles [S7].
- **Multiplexing**: a core has a handful of programmable counters (on recent
  Intel cores 4 per hardware thread with hyperthreading on, 8 with it off,
  plus a few fixed ones [S14]; general knowledge, not from the course). Ask for more events than counters and perf
  time-slices them; the percentage in parentheses after an event is the
  fraction of the run during which it was actually counted, and the reported
  value is scaled up. Fewer events per run avoids it [S7] [S16].

Reading the ex3 example [S7]: `random 5000 8` gives 501 793 612 cycles for
100 M dependent accesses with 35 203 L1 misses and 449 dTLB misses. Cycles
per access $= 5.0$, misses per access $\approx 3.5 \cdot 10^{-4}$: every load
hits L1, so 5 cycles is the L1 load-to-use latency on that machine
(the slides' 3 to 5 c [S3 p.14]).

## TopDown [S3 p.23] [S14]

```
perf stat -M TopdownL1 tsp1 10000 >/dev/null
perf stat -M tma_bad_speculation_group tsp1 10000 >/dev/null      # drill down one level
```

The pipeline's issue slots (as many per cycle as the machine is wide: 4 on
Skylake, 5 on Ice Lake, whose core Rocket Lake shares [S13]; the slide does
not name its machine) are each classified as one of four: **retiring** (useful work), **bad speculation**
(work thrown away after a mispredicted branch), **frontend bound** (no
instruction available: fetch/decode), **backend bound** (instruction
available, no execution resource: waiting for loads, full buffers). They
sum to 100 %. The slide's tsp1 result: retiring 40.2 %, backend 5.9 %,
frontend 18.3 %, **bad speculation 35.6 %** [S3 p.23]: a third of the
machine's capacity is wasted on mispredicted branches. Our reading (the
slide gives none): the suspect is the unpredictable `if (!visited[j])` in
tsp1's inner loop, consistent with the script's remark that about half of
tsp4's gain came from better branch prediction [S4] (note 08); the
`if (dist < CloseDist)` is rarely taken and therefore well predicted.
Drill-down groups give the cause within a bucket. The method and the `tma_*` metric names are Intel's [S14].

## `perf record`, `perf report`, `perf annotate` [S3 p.22] [S4] [S8]

```
perf record -e cycles:u ./tsp1 10000 >/dev/null     # samples into perf.data
perf report                                         # % of samples per function (the profile)
perf annotate -s tsp                                # per instruction, with source interleaved if -g
```

Sampling on an event: every $N$ events the PC is recorded, so the profile is
by *event*, not only by time (`-e L1-dcache-load-misses:u` gives a cache-miss
profile). Attribution to instructions is imprecise (**skid**, general
knowledge [S16]): the sample lands on an instruction near, usually after, the
one that caused the event. The matmul page shows it [S8]: 88.83 % of the
`mm1 700` samples sit on `add %r10,%rdx`, right after `mulsd (%rdx),%xmm0`,
and 10.64 % on `jne`; the page calls this attribution unlikely, since the
`add` is fast and waits for nothing and the `jne` is very predictable. The
cycles belong to the loop's real bottlenecks (the `addsd` recurrence and, at
n = 700, the TLB-missing loads of `b`, note 09). Read the annotated loop as a
whole and guess which nearby instruction caused the event [S4] [S8].

## Instrumentation

Timers in the program: `clock_gettime(CLOCK_MONOTONIC)` (our `util.h`),
`rdtsc` on x86 (cycles of the *reference* clock, not core cycles). Two
traps: the compiler hoists or deletes work whose result is unused, and it
may inline the kernel and move it across the timer calls. `recurrence.c`
and `branch_predict.c` call their kernels through a `volatile` function
pointer, `pointer_chase.c` stores the chase's end pointer in a `volatile`,
and every program checks or prints what it computed; the ex2 sheet makes the
same point ("computations … that are not
used … will not result in instructions") [S6].

## Pitfalls

- Timing an `-O0` build, or different flags per variant.
- `.gcda` accumulation across runs [S5].
- `perf stat` without `:u` on a program that does I/O: kernel cycles in.
- Trusting the hottest *line* of `perf annotate` (skid) [S8].
- Cycles across frequency changes: report ns and cycles [S7].
- Sampling too short a run: 100 Hz `gprof` needs seconds; `perf record` at
  its default 4 kHz needs at least a second for a stable percent split.
- Measuring on a shared machine while others run DRAM-bound jobs: L3 and
  DRAM numbers move; L1/L2 numbers do not [S7].
- Init time inside the measurement: `memory1` builds the list inside the
  `perf stat` window; the sheet says it is small except for large lists [S7].
  `pointer_chase` prints init and chase separately.

## Exam-style questions

1. **You ran `/bin/time` on a program: `2.1user 3.9system 0:06.1elapsed 98%CPU`. Classify it.** CPU-bound (6.0 of 6.1 s on CPU) but mostly in system mode: system calls, page faults or kernel copying dominate; profile with `perf record` including kernel samples, or `strace -c` to count calls, before touching the user code.
2. **`gprof` says function `f` uses 0.02 s and function `g` 1.90 s; `gcov` says `f`'s loop body executed 10^8 times and `g`'s 10^6 times. Reconcile.** gprof samples time, gcov counts executions. `f`'s line costs about 0.2 ns per execution (a cheap, vectorisable or predicted operation); `g`'s costs 1.9 µs each: an expensive body (calls, misses, divisions). Optimise `g`. Also check that `f` was not inlined into `g` under `-O`, which would move its time to `g`.
3. **What does the percentage in parentheses after a `perf stat` event mean and how do you get rid of it?** Multiplexing: more events requested than hardware counters, so the event was counted only that fraction of the time and scaled up; ask for fewer events per run, or use `-r` and compare runs [S7] [S16].
4. **A run shows 5.0 × 10^8 cycles and 3.5 × 10^4 L1 misses for 10^8 dependent loads. What did you learn about the machine?** Practically no misses, so every access is an L1 hit, and 5 cycles per access is the L1 load-to-use latency. If the accesses were independent the number would say nothing about latency, only about throughput [S7] [S3 p.16 to 17].
5. **TopDown reports bad speculation 35 %. What is that, what causes it and what would you look at next?** 35 % of issue slots were spent on instructions later discarded because a branch was mispredicted (or a machine clear). Cause: data-dependent, unpredictable branches. Next: `perf stat -e branch-misses:u`, `perf annotate` to find the branch, then a branchless form or a data-structure change that removes the test (tsp4's removal of `visited[]`, note 08) [S3 p.23].

Code: `src/c/profile_demo.c` (header lists every command line), `make -C src/c gcov`, `make -C src/c perf` and `gprof` on g0. Sources: [S3 p.9, 22, 23] [S4] [S5] [S6] [S7] [S8] [S13] [S14] [S16] [S17] [S18] [S19].
