# 02 Serial optimisation

Before parallelising, make one core fast. The order of importance: algorithm (note 08), memory access pattern (note 01), then compiler flags, then micro-optimisation. All numbers below are from `src/cpp/matmul_opt.cpp` and `cache_bench.cpp` on the M3 Pro with Apple clang 21.0.0 [S34]; the flag semantics are from the clang manual [S37], the blocking structure from [S8] and [S31], the benchmarking discipline from [S35].

## Loop ordering

C/C++ and numpy default arrays are **row-major**: `a[i][j]` and `a[i][j+1]` are adjacent (Fortran, MATLAB, Eigen default and `numpy order='F'` are column-major). The innermost loop must run over the last index.

Matrix multiply $C = AB$, $c_{ij} = \sum_k a_{ik} b_{kj}$:

| variant | inner loop reads | n = 256 | GFLOP/s |
|---|---|---|---|
| `ijk` naive | `b[k][j]`: stride n | 13.3 ms | 2.5 |
| `ikj` | `b[k][j]`, `c[i][j]`: stride 1 | 2.3 ms | 14.5 |
| transposed $B^T$ | `a[i][k]`, `bt[j][k]`: stride 1 | 7.5 ms | 4.5 |
| blocked `ikj`, 64x64 tiles | stride 1, tile in cache | 2.4 ms | 14.2 |

(`./bin/matmul_opt`, best of 3 per variant, 2026-09-27.)

`ikj` is an axpy `c[i][:] += a[i][k] * b[k][:]` with no loop-carried dependency, so clang vectorises it. The transposed variant has contiguous access too but its inner loop is a dot-product reduction, which is not vectorised without `-ffast-math` (see note 01). Loop order alone gives 6x.

## Blocking (tiling)

Blocked matmul processes $b \times b$ tiles so that the three tiles ($3 b^2 \cdot 8$ B) stay in L1/L2 while $2 b^3$ flops are done on them. Arithmetic intensity rises from $O(1)$ to $O(b)$ flop/byte [S16]. Choose $b$ so that $3 \cdot 8 b^2 \le$ cache size: L1 = 128 KB on this machine [S34] gives $b \approx 70$; 64 is a common choice.

**What a real BLAS does** [S31] [S8]: two levels, not one. An outer level copies a block of $A$ sized for L2 - [S8] uses $96 \times 96$, about 72 KB - into contiguous scratch memory, so the inner loops see a packed array with no stride games; an inner **register micro-kernel** then computes a small tile of $C$ (4 x 12 in [S8], via `SIMD<double,4>`) entirely in registers, which is what turns the 2:1 memory-to-arithmetic ratio of a dot product into 1:1 (note 01). The copy costs $O(b^2)$ against $O(b^2 n)$ of work, so it is free. Our `matmul_blocked` does the outer level only; the gap to the ~90 % of peak that OpenBLAS reaches is the micro-kernel. The same idea applies to stencils (spatial and temporal blocking) and to sorting.

**On this machine one level of blocking does not pay, at any size measured.** `./bin/matmul_opt --bench`: at n = 1024 `ikj` reaches 14.4 GFLOP/s and `blocked 64` 10.2; at n = 2048 the block-size sweep gives 8.9 / 11.1 / 11.3 / 11.3 GFLOP/s for $b$ = 32 / 64 / 128 / 256 against 14.0 for `ikj`. The reason is a bandwidth estimate, not a cache-size one. For fixed $i$, `ikj` streams all of $B$ once and keeps the row `c[i][:]` (16 KB at n = 2048) in L1:
$$\frac{\text{bytes}}{\text{flop}} = \frac{8 n^2}{2 n^2} = 4 \;\Rightarrow\; 14\ \text{GFLOP/s} \times 4\ \text{B/flop} = 56\ \text{GB/s} < 110\ \text{GB/s (triad, note 01)}.$$
So `ikj` is not memory bound even when $B$ comes from DRAM, and tiling only adds loop overhead and shorter vectorised inner loops ($b = 32$ is worst). Tiling starts to pay when the kernel would need more than the memory delivers, i.e. above $110/4 \approx 27$ GFLOP/s: only after SIMD and a register micro-kernel, which is why [S31] and [S8] introduce both levels together.

## Aliasing

```cpp
void axpy(double* y, const double* x, double a, int n) {
    for (int i = 0; i < n; ++i) y[i] += a * x[i];
}
```
The compiler cannot know that `x` and `y` do not overlap (`axpy(v, v+1, ...)` is legal), so it must either not vectorise or emit a runtime overlap check plus two code paths. Fixes: `__restrict` (`double* __restrict y`), passing `std::vector` by reference with distinct objects, or `#pragma omp simd`. Fortran assumes no aliasing by default, one reason it historically vectorised better.

## Compiler flags (clang/gcc)

Semantics from the clang/LLVM user manual [S37]; gcc agrees except where noted.

| flag | effect |
|---|---|
| `-O0` | no optimisation, for debugging; 10-50x slower |
| `-O1` | basic; `-O2` inlining, vectorisation (clang), unrolling; `-O3` more aggressive unrolling and inlining |
| `-march=native` | use every instruction of this CPU (AVX2/AVX-512 on x86); binary is not portable. On Apple silicon `-mcpu=native` |
| `-ffast-math` | implies `-fno-honor-infinities -fno-honor-nans -fassociative-math -freciprocal-math -ffinite-math-only -fno-signed-zeros` and sets `FTZ/DAZ` [S37]; vectorises reductions but changes results; never for code that relies on IEEE semantics (Kahan summation, NaN checks) |
| `-funroll-loops` | more ILP, larger code |
| `-flto` | link-time optimisation: inlining across translation units |
| `-g` | debug info, no speed cost; `-fno-omit-frame-pointer` for profilers |
| `-DNDEBUG` | removes `assert` |

Always compile the timed version with `-O2` or `-O3`; comparing `-O0` timings is meaningless.

## Inlining and function call overhead

A call costs ~5-10 cycles plus lost optimisation across the boundary. The compiler inlines small functions it can see (same translation unit, or headers). `inline` in C++ is about the one-definition rule, not a command; `static` or anonymous-namespace functions and templates are inlined most readily. Virtual functions and function pointers in an inner loop block inlining and vectorisation; lambdas passed as template parameters do not.

## Branch prediction

The CPU guesses the outcome of `if` inside loops and speculatively executes; a misprediction costs 15-20 cycles on a typical modern core ([S18] manual 3 gives the figure per microarchitecture; it is not published for Apple silicon). Predictable patterns (loop bounds, monotone conditions) are free; data-dependent random branches are expensive (the classic "why is sorting the array first faster" effect). Remedies: branchless code (`s += (x > 0) * x`, `std::max`), lookup tables, sorting, hoisting the branch out of the loop (loop unswitching), `[[likely]]`.

## Benchmarking methodology

The protocol below follows [S35] ch. 2 and the measurement discipline of [S8] ("we measure how many GB per second we can load, depending on the vector lengths").

1. Fix the question: throughput of a kernel, or end-to-end wall time?
2. Compile with the flags you will ship. Same flags for every variant.
3. Warm up once; run $k$ repetitions; report min or median and the spread.
4. Check the result of every variant against a reference (`max|diff|` column in `matmul_opt`); a fast wrong kernel is worth nothing.
5. Prevent dead-code elimination: consume the result.
6. Compare to a bound: roofline (note 01), or $2n^3 / P_{\text{peak}}$.
7. Profile before optimising: `perf record` / `perf report` (Linux), Instruments Time Profiler or `xctrace` (macOS), `gprof` with `-pg`, `valgrind --tool=cachegrind` for cache-miss counts, Python `cProfile`. Optimise the hot 10%.
8. Change one thing at a time and keep the numbers (a table in the README, or a benchmark script such as `src/sh/build_and_bench.sh`).

## Worked example

Estimate what blocked matmul at n = 1024 should achieve. Working set $3 \cdot 8 \cdot 64^2 = 96$ KiB fits the 128 KB L1 [S34]; compute bound; scalar peak measured 15 GFLOP/s. `--bench` shows 14.4 GFLOP/s for `ikj` and 10.2 for `blocked 64`: `ikj` is at the scalar roof, and the blocked version loses 30 % to loop overhead because there was no bandwidth problem to solve (previous section). The next step would be SIMD (vectorised the inner `j` loop already gives it 2 doubles per instruction; the remaining gap to the 64 GFLOP/s SIMD peak is the dependency on `c[i][j]` loads/stores) and register blocking (compute a 4x4 block of $C$ in registers), which is what BLAS libraries do to reach 90% of peak.

## Pitfalls

- Optimising without measuring; the hot spot is rarely where you think.
- `-O3 -ffast-math` silently changing a convergence test that compares against `NaN`.
- Benchmarking with `n` that fits in cache and extrapolating to production sizes.
- Timing with `clock()`: it measures CPU time summed over threads.
- Micro-optimising a kernel whose algorithm is $O(n^2)$ where $O(n \log n)$ exists.
- `std::vector<std::vector<double>>` for a matrix: each row is a separate heap allocation, rows are not contiguous, blocking cannot work. Use one flat vector with `i*n + j`.

## Exam-style questions

1. **Why is `ikj` faster than `ijk` for row-major matmul, although both do $2n^3$ flops?** In `ijk` the inner loop over `k` reads `b[k][j]` with stride `n`: one cache line per element, no vectorisation. In `ikj` the inner loop over `j` reads `b[k][j]` and `c[i][j]` contiguously, one line per 8-16 elements, and the update is a vectorisable axpy.
2. **What does blocking change in the roofline picture?** It raises the arithmetic intensity from constant to $O(b)$ by reusing each loaded tile $b$ times, moving the kernel from the bandwidth-limited slope to the compute roof.
3. **What is pointer aliasing and how does it affect vectorisation? Name two remedies.** Two pointers may refer to overlapping memory, so a store through one may change what the other reads; the compiler must preserve sequential semantics and either serialises or adds runtime checks. Remedies: `__restrict`, distinct container objects, `#pragma omp simd` / `ivdep`.
4. **Give a benchmarking protocol for comparing two implementations of the same kernel.** Same compiler flags, verify equal results, warm-up run, repeat $\ge 5$ times over a total of $> 0.1$ s, report min and spread, use a realistic problem size (larger than cache if the production case is), keep the result alive, quote the roofline bound.
5. **When may `-ffast-math` change results, and when is it harmless?** It permits reassociation ($ (a+b)+c \to a+(b+c) $), reciprocal approximations, and assumes no NaN/inf. Harmless for a dot product with well-scaled data (error still $O(n \epsilon)$); dangerous for compensated summation, for code testing `x != x`, and for reproducibility across compilers.

Code: `src/cpp/matmul_opt.cpp` (`matmul_naive`, `matmul_ikj`, `matmul_transposed`, `matmul_blocked`), `src/cpp/cache_bench.cpp` (`sum_ij` vs `sum_ji`). Sources: [S8] [S16] [S18] [S31] [S34] [S35] [S37].
