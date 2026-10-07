# 01 Project playbook

The PR is the VU's method loop, slide 8 [S3 p.8], run once for real:
tests → measure → profile → transform → tests, repeated until the program is
fast enough or the semester is over, then presented. What is graded is the
presentation, and the presentation should say which steps worked how well,
compared with the expectation, and ideally why [S2]. So the
deliverable is not a fast program but **a log of predictions and
measurements**. Keep it from day one.

## What the lecturer asks for [S2]

- A group of **3–5** students optimises **a program of its choice**.
- The grade is based on the **presentation**. It "should point out which
  optimization steps worked how well, compare this to your expectations, and
  ideally also have an explanation of why an optimization step worked better
  or worse than expected".
- Algorithmic optimisations are "not the topic of this course" but "allowed
  (and, for the given exercise program, usually expected)". Recommended
  handling: write the algorithmically improved version **straightforwardly
  first**, then apply non-algorithmic steps you can measure one by one.
- Measurements on `g0.complang.tuwien.ac.at`; accounts are generated in
  batches on Tuesdays, so register early.
- Publishing the work (not graded) is welcome: Sourcehut/GitHub plus a short
  page in `/nfs/unsafe/httpd/ftp/pub/anton/lvas/effizienz-abgaben/2025w/`
  (the 2026w directory presumably appears in November). The 2025W directory
  holds one group [P1], so there is a precedent to look at from g0.
- Attendance at all presentation dates is required.

## Choosing the program

Criteria, derived from what the presentation has to show:

1. **CPU-bound and deterministic.** ex1's Q2 asks "Which of these programs
   are CPU-bound?" [S5]; an I/O- or network-bound program leaves nothing for
   the VU's techniques. Output must be checkable (`diff` against a reference
   run, as the TSP Makefile does [S9]).
2. **A run of 1–30 s on g0 at a size you can scale.** Long enough for
   `perf stat` to be stable (> 10^9 cycles), short enough to run 50 times a
   day. Scalable so you can move between L1, L2, L3 and DRAM regimes (note
   04).
3. **One or two hot spots that own > 80 % of the time** (slide 7's 80–20
   rule [S3 p.7]); check with `perf record` before committing to the program.
   If the profile is flat, every step will be a 3 % step and there is nothing
   to explain.
4. **Room for both kinds of step.** At least one algorithmic change (which
   you do first and exclude from the measured series) and five to ten
   source-level or hardware-oriented steps from notes 03, 04, 06, 07.
5. **Small enough to understand in a week, in C or C++** (or a language that
   compiles to native code: `perf annotate` needs machine code you can map
   back to source).
6. **Not already optimised.** Established libraries (BLAS, zlib, sort
   routines) leave you nothing; your own or a colleague's simulation, parser,
   solver, image filter, or a naive implementation of a known algorithm do.

Bad choices: anything dominated by `printf`, file I/O or `malloc`; Python
(profile shows the interpreter); GPU code (different course); a program
whose correct output is not fixed (randomised without a fixed seed).

## Team

Three to five people [S2]. Suggested split: one owns the harness (build,
reference output, `perf` scripts, results log), everyone owns steps. Rotate
who predicts and who measures so that "expected vs measured" is not the same
person's guess twice. Use one git repository with a `results/` directory; the
VU exercises already require a git project on g0 [S5].

## Milestones against the 2026W dates [P1] [S1]

| by | what | why then |
|---|---|---|
| **13.10.2026 23:59** | everybody registered for the PR (and the VU) in TISS; team formed | registration and deregistration close the same minute; g0 accounts follow in Tuesday batches [S2] |
| 19.10 (3rd lecture) | program chosen; builds on g0 with `-O2`; reference output and `diff` check; **baseline** measured with `/usr/bin/time` and `perf stat -e cycles:u -e instructions:u`; `perf record` profile saved | presumably slides 1–23 (method, tools, hardware) have been covered by then (our guess at the pace) |
| 26.10 (no lecture) | algorithmic version written straightforwardly, checked, measured: this is the **new baseline** for the step series | [S2]: do the algorithmic change first, separately |
| 09.11 – 30.11 | one measured step per person per week: predict → change → `diff` → `perf stat` → log. Cover at least: one memory-layout step (note 04, 09), one recurrence/latency step (note 03), one compiler-help step (note 06), two Bentley transformations (note 07) | presumably covered in lectures 4–7 (our guess at the pace) |
| 30.11 (last VU lecture) | freeze the step series; decide the presentation date | the four PR dates are then two to eight weeks away |
| 07.12 | slides drafted: one slide per step with the expected/measured pair | 7 h budget for the presentation [P1] |
| **14.12 / 11.01 / 18.01 / 25.01**, Mon 16:00–18:00, EI 2 | present; attend all four dates | attendance required [S2] |

Budget: 60 h of project work **per person** (of the 75 h that 3 ECTS
mean) [P1], i.e. a 4-person team has 240 h. Ten measured steps at 10 h each plus 40 h harness and
baseline plus the algorithmic rewrite is a realistic fill.

## The loop, per step

1. **Predict** in writing before touching code: which bottleneck (latency
   chain, cache misses, TLB, branch mispredictions, instruction count), what
   counter should move, by how much. E.g. "inner loop is a 4-cycle FP add
   recurrence over 10^9 iterations → 4×10^9 cycles; four accumulators should
   give ≈ 1.1×10^9 cycles" (note 03).
2. **Change one thing.** Commit it alone.
3. **Test**: `diff` against the reference output. If the change may alter
   floating-point rounding (reassociation), decide beforehand what tolerance
   is acceptable and check against that, not against bitwise equality.
4. **Measure**: `perf stat -r 5 -e cycles:u -e instructions:u -e <the counter
   you predicted>`; keep the minimum, note the spread. Same input, same
   compiler flags every time.
5. **Log**: expected, measured, the counter evidence, a one-line explanation
   or an honest "unexplained".
6. **Keep or revert.** A step that made things slower stays in the log; it is
   presentation material ("worked worse than expected, because …").

## What the presentation must contain [S2]

- The program, what it does, the input, how correctness was checked.
- The machine (g0, Rocket Lake, flags) and the baseline numbers.
- The algorithmic change, kept separate, with its effect.
- **Per step: what was changed, what was expected and why, what was measured
  (cycles, the relevant counter), and why they differ if they differ.** This
  is what the lecturer says the presentation should show [S2].
- A cumulative chart (cycles vs step) and the total speedup.
- What you would do next and what you could not explain.

Timing: not published. If about four groups share a two-hour slot (our
assumption), plan on 15–20 minutes plus questions; ask on 05.10.

## Results-log template

One row per step, in `results/log.md`, filled in the order predict → measure:

```
| # | step | expected (why) | measured cycles:u | key counter before → after | verdict / explanation |
|---|------|----------------|-------------------|----------------------------|-----------------------|
| 0 | baseline -O2 | - | 8.21e9 | IPC 0.61 | memory bound? L1 miss 38 % |
| A | algorithmic: sort once instead of n searches | O(n log n) vs O(n^2): ~100x | 8.9e7 | - | new baseline |
| 1 | ikj loop order in kernel f | stride-1 on b: L1 misses /8, ~3x | 3.1e7 (2.9x) | L1-dcache-load-misses 2.1e8 → 2.7e7 | as expected |
| 2 | 4 accumulators in g | 4c add recurrence → ~1c: 3x on g's 40 % | 2.4e7 (1.3x) | instructions unchanged | g was only 40 %; Amdahl: max 1/(0.6+0.4/3)=1.36x, ok |
| 3 | restrict on pointers | vectorisation: 2-4x on f | 2.4e7 (1.0x) | - | worse than expected: gcc already versioned the loop (checked -fopt-info-vec) |
```

Keep the raw `perf stat` output per step under `results/NN-step/` (the
`script -f` transcript habit from the VU exercises [S5]).

## Pitfalls

- Optimising before the reference output and `diff` exist.
- Measuring wall time on a shared g0 while another group runs a DRAM-bound
  job: use `cycles:u` and `-r`, and repeat at a quiet hour (ex3 says L3 and
  DRAM numbers vary between groups for exactly this reason [S7]).
- Changing the compiler flags between steps, or measuring `-O0`.
- Reporting only speedups. The grade is for expected-vs-measured [S2].
- Counting the PR towards the CSE degree as a module course: it is not
  listed for 066 646 [P1]; check what a free elective is worth to you before
  the 60 h.

## Exam-style questions

1. **What must a PR presentation show to be graded well?** Which optimisation steps worked how well, compared with your expectations, and ideally why a step worked better or worse than expected [S2]; hence one expected/measured pair per step, with the counter that explains the difference.
2. **Algorithmic optimisation is "not the topic of this course". May you do it, and how do you present it?** Yes, it is allowed and for the given exercise program usually expected; write the algorithmically improved version straightforwardly, then apply non-algorithmic steps you can evaluate and present [S2]. It becomes the new baseline of the step series.
3. **Why is a program with a flat profile a poor PR choice?** By the 80–20 observation [S3 p.7] and Amdahl, a step on a part with fraction $f$ of the time gives at most $1/(1-f)$; with no part above 10 % every step is below 1.11×, inside the noise, and nothing can be explained.
4. **Does the PR count towards the CSE master?** Not as a module course: TISS lists it only for 066 937 Software Engineering [P1], so for 066 646 it is at most a free elective.
5. **A step made the program slower. Drop it?** No: keep it in the log and in the presentation with the expected and measured numbers and your explanation; a step that "worked worse than expected" is exactly what the presentation is asked to discuss [S2].
