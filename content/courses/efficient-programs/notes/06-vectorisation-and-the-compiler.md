# 06 Vectorisation and the compiler

Slides 28 to 32 (SIMD), 10 to 13 (stumbling blocks), 35 (aliasing) [S3];
the matmul page's `mm2`/`mm3` [S8]; the Makefile flags of [S8]. The topic:
the microoptimisations that consist of *letting the compiler do it*: making
loops vectorisable, removing aliasing, choosing flags, and knowing where the
compiler stops.

## SIMD [S3 p.28]

One instruction, several data lanes in one register: SSE `xmm` 128 bit (2
doubles), AVX `ymm` 256 bit (4 doubles, `vmulpd %ymm2,%ymm3,%ymm1`), AVX-512
`zmm` 512 bit (8 doubles); NEON on ARM 128 bit (2 doubles). Requirements:
the data are adjacent, also in memory (a vector load is one contiguous
block), and the operations are mostly the same across lanes. Pays off for
some problems with a large factor; useless for a pointer chase.

## Vectorisation: who does it [S3 p.29]

- **Auto-vectorisation** works for simple loops and is hit-and-miss
  otherwise. gcc needed `-O3` in the lecturer's examples [S3 p.90] [S8];
  clang vectorises at `-O2` (verified: `-Rpass=loop-vectorize` on our code
  [S19]).
- **Programmer help**: arrange the data (structure of arrays instead of
  array of structures, alignment, padding), arrange the computation (loop
  interchange so the stride-1 loop is innermost, split the reduction).
- **Manual vectorisation**: little language support. GNU C vector types
  (`typedef double v4d __attribute__((vector_size(32)))` in the lecturer's
  `mm3.c` for AVX [S8]; the slides' version uses `v8d`, `vector_size (64)`,
  8 doubles [S3 p.91]) are portable across gcc/clang and let the compiler
  pick instructions; intrinsics (`_mm256_*`, used in `tspi4` [S3 p.85]) are
  ISA-specific; assembly is last.

## The vectorisable-loop recipe [S3 p.30 to 31]

The slide's example loop and the rules it illustrates:

```c
for (i=1; i<n-1; i++) {
    c[i] = r0; r0 += inc;                  /* generation: recurrence on a loop-invariant step, associative */
    d[i] = a[i] + b[i];                    /* data-parallel */
    if (a[i] > a[i-1]) r1 += a[i];         /* reduction, associative, conditional on array elements */
    if (a[i] < r2) r2 = a[i];              /* reduction: min is associative */
    if (d[i] > c[i]) e[i] = a[i-1]+a[i]+a[i+1];  /* stencil, conditional store */
}
```

with `c, d, e` declared `restrict`. Rules:

1. Stride 1 or −1.
2. Every recurrence is computed with an **associative** operation (sum,
   min, max, `r0 += inc`), so lanes can hold partial results.
3. Array accesses are `[i + const]`.
4. **One write per array per iteration**, through `restrict` pointers.
5. Loop-body forms: *generation* (`c[i] = r0`), *data-parallel*
   (`d[i] = a[i]+b[i]`), *stencil* (`e[i] = a[i-1]+a[i]+a[i+1]`), *reduction*
   (`r1 += a[i]`).
6. **Not vectorisable**: using the reduction result to compute an array
   element in the same loop (the value is not known until the loop ends).
7. Conditions may depend on array elements, constants and constant-step
   recurrences (they become masks).

Applied to the course's two examples: matmul's `ikj` inner loop `c[i][j] +=
aik * b[k][j]` is data-parallel, stride 1, one write per array: vectorised
(`mm2 -O3`, 2.12× on the lecturer's machine [S8]; our `ikj` 0.136 to 0.140 ns
per iteration [S19]). The TSP inner loop is an **argmin**, a reduction on the
tuple (distance, index), which the slide calls "not associative"; it "still
does not fit the vectorizable loop recipe" but can be vectorised by hand by treating the search as "loop until a
closer city is found" (`tspi4`) or as a tuple reduction (`tspj`, `tspk`)
[S3 p.85].

## Reductions and associativity [S3 p.18, 47]

Integer addition is associative (modulo $2^{64}$), so compilers vectorise
`r += a[i]` over `long` without being asked: our `isum1` runs at about 0.28 c
per element against 2.7 to 3.05 c for the double version (cycles at the
assumed 4.05 GHz, note 03) [S19]. Floating-point addition
is not ($a + (b + c) \ne (a + b) + c$ in general), so without `-ffast-math`
(or `-fassociative-math`) the compiler keeps one chain: the slide's 3.73
c/iteration, which the flag turns into 0.3 [S3 p.18]. The programmer's
alternative that keeps the flags honest: write the $k$ accumulators
explicitly and accept the changed rounding for this loop only (note 03,
`sum4`/`sum8`).

## Aliasing and `restrict` [S3 p.13, 35]

```c
void f(double a[], double b[], double c[], long n) { for (long i=0; i<n; i++) c[i] = a[i]+b[i]; }
```

C must allow `c == a+1`, in which case iteration $i$'s store changes
iteration $i+1$'s load and vector execution would be wrong. Compilers
respond by not vectorising, or by **versioning**: a run-time overlap check
that selects a vector or a scalar loop (code size, and a branch). Fortran
forbids the overlap by rule [S3 p.35]. Fixes in C: `restrict` on the pointer
parameters (a promise, unchecked, that the object is accessed only through
this pointer), local copies of loop-invariant values (`double aik = a[i*m+k]`
in `mm4` [S8], which also works around the compiler's inability to hoist a
load past stores to `c`), or `#pragma omp simd` / `#pragma GCC ivdep`.

## Compiler flags (gcc and clang, as used in the sources)

| flag | effect | where used |
|---|---|---|
| `-O` / `-O1` | basic optimisation; the exercise sheets' level for gprof/gcov [S5] | tsp Makefile `CFLAGS=-O` [S9] |
| `-O2` | standard; inlining; vectorisation in clang, and in gcc ≥ 12 with its "very cheap" cost model (general knowledge, not from the sources) | our Makefile |
| `-O3` | aggressive unrolling/inlining; vectorisation in older gcc [S3 p.90] [S8]; can be slower (code size) | matmul Makefile [S8] |
| `-march=rocketlake`, `-mavx2 -mfma`, `-march=native` | allow the ISA extensions: without them x86 code is SSE2 only, no `ymm` | [S3 p.18] [S8] |
| `-mtune=znver5` | scheduling model without changing the ISA | [S3 p.18] |
| `-ffast-math` | reassociation, no NaN/inf/signed-zero guarantees, reciprocal approximations; changes results | [S3 p.18] |
| `-pg`, `--coverage` | gprof / gcov instrumentation | [S3 p.9] |
| `-g` | debug info, no speed cost; needed for `perf annotate` with source | |
| `-fopt-info-vec` (gcc), `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize` (clang) | which loops vectorised and why not | this note |
| `-fno-tree-vectorize` (gcc), `-fno-vectorize` (clang) | for A/B measurement | |

Apple Silicon has no AVX; `-mavx2` fails there, which is why `src/c` uses
plain C that clang vectorises for NEON and gcc for AVX2 with `-march=native`
on g0.

## What `-O3` does and does not do

Does: inlining and specialisation of small functions [S3 p.55], constant
folding, strength reduction of induction variables [S3 p.63], common
subexpression elimination when no call or store intervenes [S3 p.64],
loop-invariant code motion when it can prove no aliasing and no trap
[S3 p.39, 13], unrolling [S3 p.41], vectorisation within the recipe,
if-conversion of small branches into selects (note 03's caveat), dead-code
elimination of unused results [S6].

Does not: change the algorithm or the data structure (`visited[]` →
compaction, note 08); change data layout (AoS → SoA); reassociate FP;
interchange loops whose bodies may alias; drop `sqrt` from a comparison;
remove a redundant test whose redundancy depends on the input; use
knowledge of value ranges or of the common case [S3 p.57]; choose block
sizes for the cache (`mm6` [S8]); exploit don't-care results. The
lecturer's chart [S3 p.11], read off the plot: the source-level steps
tsp1 → tsp9 give about 3× (gcc `-O3`) to 10× (clang `-O3`), the compiler's
`-O0` → `-O3` about 1.4× to 6×; comparable factors, and they multiply (note
01).

## Integers vs floating point [S3 p.14, 82] [S4]

Bentley's step 7 replaced floats by integers; the course skips it because it
changes results and because on modern cores FP add/multiply have the same
4 c latency as integer multiply [S3 p.14], so there is nothing to gain for
multiplicative code [S4]. Where integers still win: the compiler may
reassociate them (vectorised reductions), comparisons are cheaper to
if-convert, and they pack denser (note 10).

## Manual SIMD without SIMD instructions: SWAR [S3 p.32]

Population count of a 64-bit word by treating it as 32 two-bit lanes, then
16 four-bit lanes, and so on:

```c
x = (x & 0x5555555555555555L) + ((x >> 1) & 0x5555555555555555L);   /* 2-bit sums */
x = (x & 0x3333333333333333L) + ((x >> 2) & 0x3333333333333333L);   /* 4-bit sums */
x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0fL;                            /* 8-bit sums */
x = (x + (x >> 8)); x = (x + (x >> 16)); x = (x + (x >> 32)) & 0x7f; /* fold; masks may be dropped: sums fit */
```

Six steps instead of up to 64 iterations of `count += x & 1; x >>= 1`: the
lanes are the parallelism, the word is the register. After the third step
each byte holds at most 8; the unmasked folds then leave every byte at most
16, 32 and finally 64, all below 256, so no carry ever crosses a byte
boundary, and the masks would only clear bytes that the final `& 0x7f`
discards anyway.

## Worked example: matmul's inner loop through the recipe

`mm1`'s `r += a[i*m+k]*b[k*p+j]` over `k`: stride $p$ on `b` (rule 1 fails),
a reduction chain (rule 2 holds but it is the only work), so neither
vectorisable nor fast: 4.6 c/iteration at $n = 1000$, about the `addsd`
latency [S3 p.87] [S8]. Interchange to `j` innermost:
`c[i*p+j] += a[i*m+k]*b[k*p+j]`, stride 1, no recurrence between iterations,
one store per array: 2.3 c at `-O2`, 0.84 c at `-O3` with transparent huge
pages [S3 p.88]. Our clang `-O2` on the same shape at $n = 1024$: 1.21 to
1.37 → 0.136 to 0.140 ns per iteration, and `-Rpass` confirms width 2,
interleave 4 [S19].
The rest of the matmul story is note 09.

## Pitfalls

- Expecting `-O3` alone to use AVX: it needs `-march`/`-mavx2` too.
- `-ffast-math` on code with NaN checks, Kahan summation or reproducibility requirements.
- Aliasing you did not think of: the output array is also an input.
- A `restrict` that is false: silent wrong results.
- Reading "vectorized" as fast (note 03: the FP sum was "vectorized" and ran at the add latency).
- An argmin or any tuple reduction: not in the recipe; needs the tspi4-style rewrite.
- Intrinsics tied to one ISA in code that must also build on ARM.

## Exam-style questions

1. **State the vectorisable-loop recipe in five points and give one loop that violates each.** Stride ±1 (column walk fails); recurrences only via associative ops (an argmin fails); accesses `[i+const]` (`a[idx[i]]` fails); one write per array per iteration through `restrict` (`c[i]` and `c[i+1]` both written fails); no use of the reduction result inside the loop (`b[i] = sum` fails) [S3 p.31].
2. **Why does the compiler vectorise `long` sums (clang at `-O2`, gcc at `-O3`, or at `-O2` from gcc 12) but not `double` sums, and how do you change that?** Integer addition is associative; FP addition is not, and reassociation changes results, so it needs `-ffast-math`/`-fassociative-math`, or explicit multiple accumulators in the source [S3 p.18, 47].
3. **What does aliasing prevent in `c[i] = a[i] + b[i]` and what are three fixes?** The compiler cannot prove the store to `c[i]` does not change a later `a[j]`, so it cannot reorder loads across stores or vectorise without a run-time check. Fixes: `restrict` parameters, versioning by the compiler (accept the check), Fortran-style separate arrays guaranteed by the caller, or `#pragma omp simd` [S3 p.13, 35].
4. **Name three things `-O3` will never do for the TSP program.** Drop `sqrt` from the comparison (it does not know monotonicity is all that matters), replace `visited[]` by compaction (data structure), compute the y-distance lazily (algorithmic reordering under a monotone bound) [S3 p.77 to 81].
5. **Explain the SWAR popcount in two sentences and say why the last masks can be dropped.** Treat the word as lanes of 2, 4, 8, … bits and add neighbouring lanes with shifts and masks, doubling lane width each step. After the 8-bit step each byte holds at most 8, and the later folds keep every byte at most 64 < 256, so no carry crosses a byte and only the final `& 0x7f` is needed [S3 p.32].

Code: `src/c/matmul_steps.c` (`ikj`, `ikj4`), `src/c/recurrence.c` (`isum1` vs `sum1`); `cc -O2 -Rpass=loop-vectorize -c src/c/matmul_steps.c`. Sources: [S3 p.10 to 13, 18, 28 to 32, 35, 47, 82, 85, 87 to 91] [S4] [S5] [S6] [S8] [S9] [S19].
