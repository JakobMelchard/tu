# 09 Matrix multiply worked example

Slides 86 to 96 [S3]; the lecturer's page with `perf` output for every
version and the sources `mm1.c` to `mm5.c` [S8]. The second running example:
where the TSP taught source-level steps, this one teaches the memory system
and the recurrence bound with `perf stat` and `perf annotate` as the
instruments. Our re-implementation is `src/c/matmul_steps.c`.

## The problem [S3 p.86 to 87]

$C = AB$, $c_{ij} = \sum_{k=1}^{n} a_{ik} b_{kj}$; $A$ is $n \times m$, $B$ is
$m \times p$, row-major flat arrays (`a[i*m+k]`). $nmp$ multiply-adds, i.e.
$2nmp$ flops; all sources use $n = m = p$ and report **cycles per inner
iteration** (c/It), so $\text{time} = \text{c/It} \cdot n^3 / f$. Two
textbook forms [S3 p.87]:

```c
for i: for j: { r = 0; for k: r += a[i*m+k]*b[k*p+j]; c[i*p+j] = r; }     /* mm1: 4.6 c/It, 4.1 with THP */
for i: for j: for k: c[i*p+j] += a[i*m+k]*b[k*p+j];                        /* accumulate in memory: 5.0 / 4.5 */
```

## What the profile says about mm1 [S8]

`perf record; perf report`: over 99 % in `matmul`, 0.06 % in `main`.
`perf annotate` (on `mm1 700`): 88.83 % of samples on the `add %r10,%rdx` after
`mulsd (%rdx),%xmm0` and 10.64 % on `jne`; the page itself calls this
attribution unlikely (the `add` is fast and waits for nothing, the `jne` is
well predicted) and turns to the counters instead [S8] (note 02, skid). `perf stat`, 700 × 700: 7.96 G cycles, 2.43 G
instructions, **IPC 0.31**, 65 % L1 miss rate, **48 % dTLB miss rate**; at
500 × 500: 0.57 G cycles, IPC 1.55, 44 % L1 misses, 1 % dTLB misses. Two
different bottlenecks at two sizes:

- At 500 the inner loop takes ≈4 c per iteration: the **`addsd` recurrence**,
  latency 4 c, each add waiting for the previous [S8]. The loads miss L1 (44 %)
  but their latency is off the critical path, hidden by out-of-order
  execution.
- At 700 the column walk through `b` has stride $8 \cdot 700 = 5\,600$ B >
  4 KB: **one page per element**, 700 pages per column > 512 L2 TLB entries
  → 48 % of all loads (practically every load of `b`) miss the dTLB, one
  miss per 24 cycles; at ~20 c each, the page says, that explains the
  difference. DRAM traffic does not (the `offcore … llc_miss_dram` counts of
  `mm1` and `mm4` at 700 differ little, since all versions read `b`
  completely). Per inner iteration: 23 c at 700 against 4.6 c at 500, a
  factor 5. Separately, later `mm1 700` runs were often 4× faster, with far
  fewer dTLB misses, which the page attributes to transparent huge pages;
  with THP disabled the slow result came every time [S8].

## Loop order: the six nestings [S3 p.88 to 90]

$n = p = m = 1\,000$, c/It; THP = transparent huge pages on (the slide
names flags, not the compiler; `-O2`/`-O3` as gcc's):

| nesting | inner loop touches | `-O2` | `-O2` THP | `-O3` THP |
|---|---|---|---|---|
| i j **k** | `a` row (stride 1), `b` column (stride $p$), `c` fixed | 5.0 | 4.5 | 4.5 |
| i k **j** | `b` row, `c` row (stride 1), `a` fixed | 2.3 | 2.2 | **0.84** |
| j k **i** | `a` column, `c` column (stride $m$, $p$) | 17.5 | 5.3 | 5.3 |
| j i **k** | as ijk | 4.4 | 4.2 | 4.2 |
| k i **j** | as ikj | 2.5 | 2.3 | 0.99 |
| k j **i** | as jki | 17.9 | 5.1 | 5.0 |

Reasons [S3 p.90]:

1. **Spatial locality**: `j` innermost walks `b` and `c` along rows, stride
   1: one line per 8 doubles, one TLB entry per 512 doubles. `i` innermost
   walks two columns: a line *and* a page per element, hence 17.5 c, and
   5.3 c once THP makes the pages 2 MB (the TLB misses go, the cache misses
   stay).
2. **Recurrences**: `k` innermost accumulates into one value: the 4 c
   `addsd` chain. `j` innermost writes a different `c[i*p+j]` each
   iteration: no dependence between iterations.
3. **SIMD**: only the `j` loop is vectorisable (note 06), which `-O3`
   does: 2.2 → 0.84.
4. **Temporal locality**: with `k` in the middle, the row `c[i*p+…]` is
   reused $m$ times while it is hot.

## From mm2 to mm7 [S3 p.91 to 95] [S8]

| step | what changed | c/It [S3] | lecturer's counters at 500 [S8] |
|---|---|---|---|
| mm2 `-O2` | ikj, scalar | 2.3 | 392 M cycles, IPC 2.26, L1 misses 4 % (from 44 %) |
| mm2 `-O3 -mavx` | auto-vectorised, 4 doubles per `vmulpd`/`vaddpd`; the generated loop reloads addresses from the stack | 0.85 (p.91; p.88 has 0.84 for the same nesting) | 180 M cycles, 2.12× |
| mm3 | explicit GNU vector type: on the slide `v8d` (`vector_size (64)`, 8 doubles), `p = p/8`; in the page's `mm3.c` `v4d` (32 B, 4 doubles), `p = p/4`; clean 6-instruction loop | 0.72 | 171 M, 1.06× |
| mm4 | loop-invariant code motion by hand: `double aik = a[i*m+k]` (the page: the compiler apparently does not do it; our guess why: it cannot rule out that the stores to `c` change `a`) | 0.70 | 169 M, fewer instructions, same time: "possibly" already at a limit such as L2/L3 bandwidth |
| mm5 | `k` unrolled by 4 with the unrolling applied *inside* the `j` loop: 4 products summed in a register, one read-modify-write of `c` per 4 `k` | 0.66 | 120 M, 1.41×; `limit1` (same loop, data pinned in L1) shows IPC 2.16 vs 0.89: memory still costs a factor |
| mm6 | **recursion**: halve the `i` and `k` index ranges at each level (the slide's `matmul1` splits the `k` range while it is ≥ 8), keep the `j` loop full length (700 × 4 doubles = 22 400 B fits L1); reuse at every level, some levels match some cache | 0.28 | 80 M, 1.5× over mm5 |
| mm7 | `i` unrolled by 2 so each loaded `b` vector serves two rows of `a`: half the loads | 0.25 | 65 M; **8.8× over mm1 at 500, 44× at 700** |
| ATLAS | | 0.54 | 1.22× slower than mm7 |
| OpenBLAS, 1 thread | | 0.16 | 1.54× faster than mm7 |

Traffic arithmetic behind mm5 and mm6 [S8]: in mm5 at 700 every element of
`a` is loaded once, every element of `b` 700 times, every element of `c`
700/4 times (but row by row, so from cache). Multiplying $r$ elements of `a`
by $s$ elements of `b` that fit some cache level performs $rs$ products per
$r + s$ loads: **blocking** trades loads for reuse; the arithmetic intensity
rises from $O(1)$ to $O(b)$ flops per byte. Tuning $r, s$ to three cache
levels is tedious, so mm6 halves recursively and lets the levels fall where
they fall (cache-oblivious). Parallel check [S8]: two copies of mm5 700 run
concurrently take 2.1× longer each (bandwidth bound: no point in
threading), two copies of mm7 take 1.13× (compute bound: threading would
pay), and OpenBLAS gains 1.6× from a second core but *loses* from
hyperthreading (one thread already fills the core).

## Our five versions, measured [S19]

`src/c/matmul_steps.c`, M3 Pro (L1d 128 KB, L2 16 MB), clang `-O2`, integer
inputs so every version is checked bit-identical against `ijk`:

Ranges over four `make bench` runs on 2026-09-28 (the first-pass table was
measured with a test matrix $A \equiv 0$, a bug in `fill()` fixed on
2026-09-28; the numbers moved by 5 to 20 %):

| version | idea | n = 512: ns/It, GFLOP/s | n = 1024: ns/It, GFLOP/s |
|---|---|---|---|
| `ijk` | textbook, `r +=` chain, `b` column stride $8n$ | 0.95 to 1.01, 2.0 to 2.1 | 1.21 to 1.37, 1.5 to 1.7 |
| `ikj` | interchange: stride-1 axpy on rows of `c` and `b` | 0.137 to 0.140, 14.3 to 14.6 | 0.136 to 0.140, 14.3 to 14.7 |
| `dotT` | transpose `b` once, dot products with 4 accumulators | 0.184 to 0.188, 10.7 to 10.9 | 0.229 to 0.243, 8.2 to 8.7 |
| `blocked` | ikj on 64 × 64 tiles | 0.170 to 0.173, 11.6 to 11.7 | 0.190 to 0.200, 10.0 to 10.5 |
| `ikj4` | ikj with `k` unrolled by 4 (mm5's step) | **0.114 to 0.117, 17.1 to 17.6** | **0.111 to 0.122, 16.4 to 18.1** |

Expected vs measured:

- `ijk` → `ikj`: expected the slides' 2× at `-O2` plus vectorisation;
  got **7× at 512 and 9 to 10× at 1 024** (8.6 to 10.1) (clang vectorises at `-O2`,
  `-Rpass` shows width 2, interleave 4). At 1 024 the `ijk` stride is 8 KB: with 16 KB pages every second
  element is a new page, and the 128 B line serves one element: the 700-case
  of the lecturer's page in miniature.
- `dotT`: expected to match `ikj` (stride 1, 4 chains cut the ~3 c add
  latency to 0.75 c per iteration ≈ 0.19 ns at the assumed 4.05 GHz); got
  0.18 to 0.19 ns at 512 and 0.23 to 0.24 ns at 1 024: the latency bound of 4 scalar chains
  (plus, at 1 024, presumably the transpose and cache misses), while `ikj`'s vector axpy
  has no chain at all. Prediction correct, choice of step inferior.
- `blocked`: expected a gain at 1 024 (three 8 MB matrices, 24 MB > L2); got
  a **loss** against `ikj` (0.19 to 0.20 vs 0.14 ns). The 16 MB L2 holds `b`
  (8 MB) plus the working rows, so `ikj` already reuses from cache and the
  tiles only shorten the inner loop to 64 and add loop overhead. It still
  loses at `--n 2048` (three 32 MB matrices, 6× the L2): 0.173 vs 0.138 ns
  in one run on 2026-09-28, presumably because `ikj` streams rows of `b`
  that the prefetcher delivers at full speed and keeps the 16 KB row of `c`
  in L1. The lecturer's mm6 gained 1.5× with a 256 KB L2 [S8]; whether a
  larger $n$ or other tile sizes turn our result around is untested.
- `ikj4`: expected fewer `c` read-modify-writes to help as in mm5 (1.41×);
  got 1.1 to 1.25×. Same mechanism, smaller constant; at `--n 2048`
  it fell behind `ikj` (0.147 vs 0.138 ns, one run), not investigated.

## Worked example: predict mm1's two regimes with the formulas of notes 03 and 04

Recurrence: `r += …` with $L_{\text{add}} = 4$ c gives ≥ 4 c/It, and
$n^3 = 1.25 \cdot 10^8$ iterations at 500 → ≥ 5.0 · 10^8 cycles; measured
5.7 · 10^8 [S8]. Memory: column stride $8n$ bytes; for $n \ge 8$ every
`b` access is a new line (compulsory miss rate 1 per access on `b`, ≈ 44 %
of all loads: matches the counter), for $8n > 4\,096$ ($n > 512$) every
access is a new page; $n$ pages per column against 512 L2 TLB entries →
every `b` load misses for $n = 700$ (48 % of all loads, as measured), few for
$n = 500$ (1 %). Predicted: 500 bound by the add
chain (≈4 c), 700 bound by TLB walks (≈20 c per access): measured 4.6 and
7.96 G / 3.43 · 10^8 = 23 c per iteration [S8]. Both regimes were
predictable from the two formulas before running anything.

## Pitfalls

- Reporting GFLOP/s without the size: `ijk` is 2.0 GFLOP/s at 512 and 0.9 at
  2 048, and a cache-fit size makes anything look good.
- Blocking for a cache you did not measure (note 04's sweep first).
- Comparing versions whose results differ in the last bits and calling one
  wrong: with integer inputs they must be bit-identical, with real data
  agree to $O(n\varepsilon)$.
- `-O3` without `-mavx2`: SSE2 vectors, half the width [S8].
- Trusting `perf annotate`'s hottest instruction (skid) [S8].
- Threading a bandwidth-bound kernel: two copies of mm5 ran 2.1× slower each [S8].

## Exam-style questions

1. **Why is `ikj` faster than `ijk` for row-major matrices, in three separate reasons?** Spatial locality (`b` and `c` walked along rows, one line per 8 elements, one page per 512), no recurrence (each iteration updates a different `c` element, the `ijk` form chains `r +=` at 4 c), and vectorisability of the `j` loop [S3 p.90].
2. **Explain the factor 5 in cycles per iteration between `mm1 500` (4.6 c) and `mm1 700` (23 c) with counters.** dTLB miss rate 1 % vs 48 % of all loads: stride 5 600 B exceeds the 4 KB page, so a column of 700 needs 700 TLB entries, more than the 512-entry L2 TLB; every `b` load pays a page walk, ~20 c by the page's estimate. DRAM traffic barely differs between versions, so it is not bandwidth [S8].
3. **What did `mm6`'s recursion achieve and why recursion instead of explicit blocking?** Reuse of `a` and `b` sub-blocks at many granularities, some of which fit each cache level, without tuning block sizes to three levels; the `j` loop was kept full length because its 22 KB fits L1 and recursion overhead there would dominate. 0.66 → 0.28 c/It [S3 p.94] [S8].
4. **Two processes of mm5 take twice as long each, two of mm7 take 13 % longer. What does that tell you?** mm5 is bound by a shared resource (memory bandwidth), mm7 by the core; parallelising mm5 would not scale, mm7 would [S8].
5. **Your blocked version is slower than the unblocked one. Give the likely reason and the test.** The working set already fits a cache level (here 8 MB `b` in a 16 MB L2), so blocking adds loop overhead and shortens the vectorised inner loop without saving misses; test by scaling $n$ until the working set exceeds the cache, or by counting `L1-dcache-load-misses`/`LLC-loads` for both [S19] [S8].

Code: `src/c/matmul_steps.c` (`--bench`, `--n N`). Sources: [S3 p.86 to 96] [S8] [S19].
