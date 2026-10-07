# 08 TSP worked example

Slides 75 to 85 [S3]; the C sources tsp1 to tsp9 [S9]; the script's
measured cycle counts and its comparison with Bentley's own [S4] [S11]. The
running example of the course: one $O(n^2)$ loop taken through eight
source-level steps, each with a number. Our re-implementation with different
steps is `src/c/tsp_greedy.c`.

## The problem and the algorithm [S3 p.75 to 76]

Visit every city once, minimise the distance. Optimal is NP-complete;
Bentley's greedy heuristic starts at a city and always goes to the nearest
unvisited one: $O(n^2)$, tours about 25 % longer than optimal. The hot loop
(tsp1, our paraphrase of the structure, not the code):

```
for each position i in the tour:
    best = +inf
    for each city j:
        if not visited[j] and dist(current, j) < best:   # dist computed again inside
            best = dist(current, j); closest = j
    append closest; mark visited; current = closest
```

Data: `cities[]` of `(x, y)` doubles, `visited[]` bytes, `tour[]` indices
[S3 p.76]. Correctness check across all versions: `diff tsp.eps tsp_ref.eps`
after a 1 000-city run (the Makefile's `check` target [S9]).

## The steps and their measured effect [S3 p.77 to 84] [S4]

Cycles for 1 000 cities, gcc on a Celeron, from the script [S4]; Bentley's
own ratios (PDP-KL10 Pascal, HP1000 C) normalised to step 6 in the last two
columns [S4] [S11].

| version | change | catalogue (note 07) | cycles [S4] | ratio to step 6: Celeron / KL10 / HP1000 |
|---|---|---|---|---|
| tsp1 `-O` | as written | | 57.5 M | 4.01 / 5.73 / 4.39 |
| tsp1 `-O3` | compiler only | | 49.5 M | 2.87 / – / – |
| tsp2 | `ThisDist = dist(…)` computed once | CSE | 49.0 M | 2.84 / 5.56 / 4.27 |
| tsp3 | `DistSqrd` without `sqrt`; `dist` kept for `main` | algebraic identity, specialisation | 20.9 M | 1.35 / 2.95 / 2.78 |
| tsp4 | no `visited[]`: unvisited cities are `tour[i..n-1]`, chosen one swapped to `tour[i]`, inner loop `j = i..n-1` | data structure change | 13.9 M | 1.05 / 2.59 / 2.63 |
| tsp5 | `DistSqrd` inlined, `ThisX`/`ThisY` hoisted | inlining, code motion | 13.9 M | 1.01 / 1.71 / 1.72 |
| tsp6 | `ThisDist = sqr(dx)`; only `if (ThisDist < CloseDist)` add `sqr(dy)` and test again | short-circuit on a monotone bound | 14.1 M | 1 / 1 / 1 |
| (7) | integers instead of floats: skipped, changes results, no gain expected on modern FP units [S3 p.82] [S4] | | – | – / 0.91 / 0.86 |
| tsp8 | `tour` is an array of `point`s, reordered directly; `tsp()`'s interface changes | data layout, remove indirection | 13.2 M | 0.94 / 0.84 / 0.84 |
| tsp9 | sentinel: `for (j = ncities-1; ; j--)` with `<=` and `if (j < i) break;` inside the rare branch; the current city at `tour[i-1]` is its own sentinel | sentinel | 13.4 M | 0.98 / 0.83 / – |

Readings the sources give:

- **tsp2 gained 1 %** because the second `dist` call was inside the `if`,
  executed only when a new minimum was found: $H_n \approx \ln n$ times per
  pass, not $n$ [S4] (note 07).
- **tsp3 gained 2.3×**: `sqrt` was in every candidate evaluation; it is
  monotone and only the order matters [S3 p.78].
- **tsp4 gained 1.5×**, of which about half is better branch prediction:
  `if (!visited[j])` is unpredictable; the other half is halving the
  iterations (the inner loop now runs over the unvisited only, $n(n-1)/2$
  candidates in total) [S4]. Slide 23's TopDown of tsp1 shows 35.6 % bad
  speculation [S3 p.23], which this step should largely remove (our
  inference; the slide shows only tsp1).
- **tsp5, tsp6, tsp8, tsp9 are within noise of each other on the Celeron**
  while Bentley's KL10 figures show 1.5× from inlining and 1.7× from the lazy
  y-distance [S4]. Our explanation, not the script's: gcc presumably inlines `DistSqrd`
  by itself at `-O3`, and a 1982 machine without caches, branch prediction
  or out-of-order execution paid for every instruction, while the script's
  general remark is that relative operation costs have shifted since
  Bentley's book [S4].
- **tsp9 is slower than tsp8**, "not investigated" [S4]: the honest
  entry every PR log should be willing to contain.
- Compiler vs programmer [S4]: `-O3` alone gave 1.16× (57.5 M → 49.5 M), the
  steps 3.7× on top (to tsp8's 13.2 M); slide 11 shows the same comparison
  for seven compiler configurations [S3 p.11] (note 01).

## tspi4 and the vectorised argmin [S3 p.85]

Separate `tourx[]` and `toury[]` (structure of arrays), no lazy computation
of the y-distance (our reason: SIMD wants uniform work), AVX intrinsics
[S3 p.85]. The inner loop still does not fit the recipe of note 06 (an argmin
works on the tuple (distance, index), which the slide calls not
associative), but it can be vectorised
either as "loop until a closer city is found" (tspi4) or as a proper tuple
reduction (tspj, tspk).

## Our version: four steps, measured [S19]

`src/c/tsp_greedy.c` is written from scratch (city struct with an id,
xorshift input, start at city 0), with steps chosen from the same catalogue.
Every version must produce the identical tour (checked for 6 sizes × 3
seeds), and the baseline tour is verified against the greedy property
independently. $n = 10\,000$, M3 Pro, clang `-O2`, ranges over four
`make bench` runs on 2026-09-28 (the machine's clock varies by up to 10 %
between runs; the speedups vary less):

| version | change | ms | ns per candidate ($n(n-1)/2$) | speedup |
|---|---|---|---|---|
| v1 | `visited[]`, `sqrt` in a function called twice as in tsp1 (clang merges the calls: one `fsqrt` per candidate) | 61.4 to 64.5 | 1.23 to 1.29 | 1.00 |
| v2 | squared distance, current coordinates hoisted | 46.8 to 48.7 | 0.94 to 0.97 | 1.31 to 1.37 |
| v3 | compaction instead of `visited[]` (tsp4's step) | 51.5 to 56.3 | 1.03 to 1.13 | 1.13 to 1.19 |
| v4 | lazy y-distance on top of v3 (tsp6's step) | 28.5 to 30.9 | 0.57 to 0.62 | 2.06 to 2.17 |

Expected vs measured, the way the PR wants it [S2]:

- **v2**: expected a gain from removing `sqrt` (15 to 16 c latency on an Ice
  Lake-class core [S13]; Apple publishes no figure) from the candidate path;
  got 1.31 to 1.37×. Less than tsp3's 2.3× presumably because clang had
  already inlined `dist` and merged its two calls, and because the loop was
  not bound by the `sqrt` alone (our reading).
- **v3**: expected ~2× (half the candidates, no unpredictable branch);
  **got 1.13 to 1.19×, slower per candidate than v2**. The assembly explains
  it:
  clang compiled both v2's and v3's update as `fcmp` + `fcsel`/`csel`
  (branchless select), so `best` is a **recurrence**: compare → select →
  compare, 4.2 to 4.6 c per candidate at the assumed 4.05 GHz, and the loop
  is latency bound at
  that chain regardless of how many candidates it skips. v2's `visited[]`
  test compiled to a real branch (`ldrb; cbnz`) and clang unrolled the
  skip-scan, so visited candidates cost less than a chain step; v3 pays the
  full chain for every candidate. Removing the test did not remove the
  bottleneck, because the bottleneck was not the test. The 0.2 to 0.8 c per
  candidate by which v2 beats v3 per unvisited candidate is not explained;
  it belongs in the log as such.
- **v4**: expected the saving of the y-part on most candidates; **got 2.06
  to 2.17× over v1 and 1.8 to 1.9× over v3**, more than the arithmetic
  saved. The assembly
  again: the first test `if (dx*dx < best)` is a **branch** (`fcmp; b.pl`),
  rarely taken (a new candidate for the minimum is rare, $\approx H_n$ per
  pass plus the x-only false positives), and a predicted branch does not
  wait for its operand: the next iteration proceeds speculatively while the
  compare resolves, so the `best` recurrence no longer bounds the loop. It
  runs near the throughput bound, 2.3 to 2.5 c per candidate (assumed
  clock). The lazy y-test was
  worth having for the branch it introduced, not for the multiply it saved.

So on this core the order of Bentley's steps matters differently: tsp6's
transformation is the one that breaks the chain, tsp4's is neutral until
then. On the Celeron [S4] and on Bentley's machines [S11] the constants
were different again. Same source-level steps, three different rankings:
the point of the course is to predict, measure and explain the ranking, not
to memorise one.

## Worked example: predict the cost of a candidate

Per candidate in v3: 2 loads (x, y), 2 subtracts, 1 multiply and 1 fused
multiply-add, 1 compare, 2 selects, loop overhead (read from `cc -O2 -S`).
Apple publishes no latencies or port counts, so the following are
**assumptions**: 4 FP pipes, `fcmp` 2 c, `fcsel` 2 c. Throughput bound:
about 2 c. Latency bound: `best` → `fcmp` → `fcsel` → `best`: 4 c.
Predicted $\max(2, 4) = 4$ c; measured 4.2 to 4.6 c (at the assumed clock).
For v4 the chain is cut by the branch: predicted 2 c, measured 2.3 to 2.5 c.
For v1 add an unpredictable `visited` branch at ~0.25 mispredictions per
candidate ($\int_0^1 \min(p, 1-p)\,dp$ over the run) × 17 to 19 c ≈ 4 to
5 c, plus `sqrt`: measured 5.0 to 5.2 c per unvisited candidate.

## Pitfalls

- Comparing tour *lengths* between versions and calling them equal: compare
  the tours; two different tours can have the same length to six digits.
- Ties: compaction changes the scan order, so with duplicate distances the
  tie-break differs. Random doubles have none; integer coordinates would.
- Judging a step by the instruction count it saves; judge it by the chain
  it shortens or the branch it makes predictable.
- Starting from a different city than the reference run (Bentley's starts at
  `ncities-1`, ours at 0): different tour, both correct.

## Exam-style questions

1. **Why did dropping `sqrt` give 2.3× but computing `dist` only once gave 1 %?** `sqrt` executed for every candidate ($n^2/2$ times); the second `dist` call was inside the `if` and executed only when the minimum improved, $H_n \approx \ln n$ times per pass [S3 p.77 to 78] [S4].
2. **Explain tsp4's data-structure change and its two sources of speedup.** Keep the unvisited cities contiguous in `tour[i..n-1]` and swap the chosen one to position `i`; the inner loop then iterates over exactly the unvisited cities. Speedup from half the iterations ($n(n-1)/2$ candidates) and from removing the unpredictable `if (!visited[j])`, about half each [S3 p.79] [S4].
3. **What does the lazy y-distance rely on, and what did it do on our machine that the slides do not mention?** $\Delta x^2 \le \Delta x^2 + \Delta y^2$, so if the x-part already exceeds the best, the candidate loses. On the M3 the added test compiled to a rarely taken branch that decoupled the compare from the `best` chain; the loop went from latency bound (≈4 c) to near the throughput bound (2.3 to 2.5 c, assumed 4.05 GHz) [S3 p.81] [S19].
4. **Why was step 7 (integers) skipped, and when would it still pay?** It changes results (rounding of coordinates) and modern cores do FP add/multiply at the same latency as integer multiply, so no gain for this code. It pays where integer ops allow the compiler to reassociate/vectorise a reduction, or where memory size matters [S3 p.82] [S3 p.14] [S4].
5. **tsp9 was slower than tsp8 on the Celeron. Give two plausible reasons and say how you would test them.** The sentinel adds a data-dependent `if (j < i)` inside the update path and changes the scan direction; the loop may have been bound by a recurrence, so removing a predictable compare saved nothing. Test: `perf stat -e branch-misses:u -e cycles:u -e instructions:u` on both (instructions down, cycles not), then `perf annotate` for the chain [S4] [S3 p.84].

Code: `src/c/tsp_greedy.c` (`--test`, `--bench`; `cc -O2 -S` to see the `fcsel` vs `b.pl` difference). Sources: [S2] [S3 p.11, 23, 75 to 85] [S4] [S9] [S11] [S13] [S19].
