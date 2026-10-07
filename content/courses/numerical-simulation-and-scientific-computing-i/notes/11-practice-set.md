# 11 Practice set - substitute problems for the ten TISS topics

**Read this first.** *There is no past paper for 360.242.* TISS says *"No lecture
notes are available."* in every offering from 2019W to 2026W [S1] [S2] [S3], the
VoWi page is empty - 0 Materialien [S4], and no lecturer publishes sheets for
this course [S7] [S8] [S10]. Nothing below is a reconstruction of a real
question, and nothing below claims to be. See
[`00-exam-focus.md`](00-exam-focus.md), which this note does not contradict.

What this note is: a **bounded set of exam-shaped problems** for this course's
stated topic list [S1], assembled from three free, licence-clear outside sources
and from our own writing. Every problem carries its provenance on its first
line.

| tag | source | licence |
|---|---|---|
| **[S8]** | J. Schöberl, *Introduction to Scientific Computing*, TU Wien E101 - **a 2026W lecturer of this course** [S1] [S10] | LGPL-2.1 |
| **[S43]** | V. Eijkhout, *The Art of HPC* vol. 1, UT Austin / TACC | CC BY 4.0 |
| **[S44]** | D. Bindel, Cornell CS 5220 *Applications of Parallel Computers*, Fall 2015, HW3 | MIT |
| **ours** | written here, against a specification or a primary source | - |

"Adapted from [S43]" means the exercise is **restated in our words** and extended
with a number to check against; the original wording is not reproduced. Solutions
that run are in [`../src/exercises/`](../src/exercises/README.md); the registry
entries are S43 and S44 in [`../refs/SOURCES.md`](../refs/SOURCES.md).

**24 problems, one to four per TISS topic.** Answers follow each problem.

---

## Topic 1 - Computer Architectures

### P1 *(adapted from [S43], ch. Single-processor Computing, §Caches → Direct mapped caches)*

A 64 KB direct-mapped cache with 32-byte lines, 32-bit addresses, 8-byte
doubles. Run

```c
double A[3][8192];
for (int i = 0; i < 512; ++i)
  A[2][i] = (A[0][i] + A[1][i]) / 2.0;
```

(a) How many cache misses does the loop take? (b) How many would a
fully-associative cache of the same size take? (c) Eijkhout asks what happens if
the cache index is taken from the *most significant* address bits instead of the
least significant. Answer that, and say why it is a bad rule in general.
(d) Give a one-line source change that fixes the problem without touching the
cache.

**Answer.** (a) **1536** - every one of the 3 × 512 accesses misses. The rows are
$8192 \times 8 = 65536$ bytes apart, which is exactly the cache size, so
`A[0][i]`, `A[1][i]` and `A[2][i]` carry identical index bits and each access
evicts the line the previous one just brought in. Spatial locality within a line
is destroyed: the line is gone before `i+1` reaches it.
(b) **384** = 3 rows × 512/4 lines: the compulsory misses only, one per line,
since three lines coexist happily in a fully-associative cache.
(c) The conflicts vanish - the rows then differ in bit 16 and upwards, so they
land in **different** sets, and the measured count drops to the same **384**.
But it is useless in general: with the index taken from the top bits, an entire
contiguous array smaller than the cache has *identical* index bits and collapses
onto **one** set. Measured in
[`../src/exercises/utaustin-theartofhpc-2022/cache_sim.py`](../src/exercises/utaustin-theartofhpc-2022/cache_sim.py):
streaming a contiguous 64 KB leaves **2048** lines resident under low-bit
indexing and **1** under high-bit indexing.
(d) **Pad the row**: `double A[3][8192+4];`. The stride is no longer a multiple
of the cache size, so the three rows spread across sets. This is the standard
fix and the reason array leading dimensions in tuned code are odd multiples of a
line.

### P2 *(adapted from [S43], §Caches → Associative caches)*

$n$ addresses are thrown at random at a cache with $n$ entries.
(a) For a direct-mapped cache, what fraction of them is still resident at the
end? Derive it. (b) What is the answer for a fully-associative cache?
(c) Sketch the curve in between, and say what it tells you about why real L1
caches are 8-way rather than 64-way.

**Answer.** (a) A given slot is missed by all $n$ addresses with probability
$(1-1/n)^n$, so the expected number of occupied slots is
$n\bigl(1-(1-1/n)^n\bigr) \to n(1-1/e) \approx 0.632\,n$. For $n = 32$ that is
**20.41**; the simulation gives a mean of **20.44** over 100 trials.
(b) $n$ - nothing is ever evicted below capacity.
(c) Monotone and sharply concave: 20.4 → 23.7 → 26.1 → 28.2 → 29.8 → 32.0 for
$k = 1,2,4,8,16,32$. Most of the benefit is bought by the first few doublings,
and each doubling costs $k$ parallel tag comparisons on the critical path of an
L1 hit. That trade - nearly all the conflict benefit at a fraction of the
latency cost - is the whole argument for small associativity in L1 and larger in
L2.

### P3 *(adapted from [S43], §Locality and data reuse → The roofline model; and [S16])*

"How would you determine whether a given program kernel is bandwidth or compute
bound?" Answer it as a procedure, then carry it out for (i) the STREAM triad
`a[i] = b[i] + s*c[i]`, (ii) a 2D 5-point stencil in double precision, (iii) a
CSR SpMV, on a machine with peak $P = 100$ GFLOP/s and bandwidth $B = 50$ GB/s.

**Answer.** Procedure: count the flops and the **DRAM bytes** the kernel must
move, form the arithmetic intensity $I = \text{flops}/\text{bytes}$, compare it
to the **ridge point** $P/B$, and quote the attainable rate
$\min(P,\, I\cdot B)$. Below the ridge the kernel is memory bound; a measured
rate well below $\min(P, I\cdot B)$ means neither roof is the limit and something
else (latency, no SIMD, no ILP) is.

Ridge point here: $P/B = 2$ flop/byte.
(i) Triad: 2 flops, 24 bytes (and 32 with write-allocate) [S17] →
$I = 1/12 \approx 0.083$; attainable $\approx 4.2$ GFLOP/s, i.e. **4 %** of peak.
Memory bound, decisively.
(ii) 5-point stencil: ~5 flops per point; with perfect caching only the new
point is read and one written, 16 bytes → $I \approx 0.31$; attainable
$\approx 16$ GFLOP/s. Still memory bound - and the "with perfect caching" is the
whole art, because a naive sweep re-reads the neighbour rows.
(iii) CSR SpMV: 2 flops per non-zero, ~12 bytes per non-zero (an 8-byte value
plus a 4-byte column index) plus the indexed access into $x$ →
$I \approx 0.17$; attainable $\approx 8.3$ GFLOP/s. Memory bound, and the
irregular access to $x$ usually puts it below even that.
All three sit left of the ridge; that is the structural fact about this course's
kernels. Code: `src/cpp/cache_bench.cpp`, note 01.

### P4 *(adapted from [S8], Performance → Pipelining)*

A fused multiply-add has latency 4 cycles and reciprocal throughput (CPI) 0.5.
A loop accumulates into a single variable. (a) What fraction of peak can it
reach? (b) How many independent accumulators remove the bottleneck? (c) Why does
the compiler not simply do this for you?

**Answer.** (a) Each FMA must wait for the previous one, so one result every 4
cycles instead of every 0.5: **CPI/latency = 0.5/4 = 1/8 of peak**.
(b) $\text{latency}/\text{CPI} = 8$ - Schöberl states that with eight
accumulators the latency bottleneck is overcome. `src/cpp/cache_bench.cpp` uses
eight for exactly this reason.
(c) Because reassociating a floating-point sum changes the result, and the
compiler may not do that without `-ffast-math` [S37]. This is the single most
common reason a hand-written reduction runs at an eighth of peak.

---

## Topic 2 - Serial Optimization

### P5 *(adapted from [S43], §Locality → Spatial locality)*

`nvectors` is small compared to the cache, `length` is large.

```c
for (int k = 0; k < nvectors; ++k)
  for (int i = 0; i < length; ++i)
    a[k][i] = b[i] * c[k];
```

Relate reuse, cache size and associativity to its performance, and say whether
exchanging the loops helps.

**Answer.** As written, the inner loop streams `b` of length `length` for each
`k`. `b` does not fit, so it is re-read from DRAM `nvectors` times: `b` traffic
is $\texttt{nvectors} \times \texttt{length}$ words where `length` would do. `c[k]`
is a scalar, loop-invariant, and lives in a register. Associativity bites if
`a[k]` rows are a power-of-two stride apart - then `a[k][i]` and `b[i]` can
conflict.

Exchanged, `b[i]` is loaded once and reused `nvectors` times while it is still
in a register, and the writes to `a[0..nvectors-1][i]` touch `nvectors` distinct
streams. That is better **if** `nvectors` streams fit in the cache and in the
prefetcher's stream budget; if `nvectors` is large it is worse, because you now
have `nvectors` open streams thrashing. The honest answer is "better for small
`nvectors`, and that is exactly the hypothesis of the question".

### P6 *(adapted from [S43], §Data reuse and arithmetic intensity → Example: matrix operations)*

The matrix-matrix product moves $3n^2$ data and does $2n^3$ flops, so its
arithmetic intensity is $O(n)$. Argue that a straightforward triple loop does
**not** realise that reuse, and state what decides whether it does.

**Answer.** $O(n)$ intensity is a property of the *mathematical operation*, not
of an implementation: it says the data *could* be reused $O(n)$ times. A triple
loop reuses a datum only if it is still in cache when it comes round again. In
the `ijk` order, the inner loop walks a column of $B$ with stride $n$ - one
useful word per line - and by the time `i` advances, the whole of $B$ has been
swept, so nothing survives. The realised intensity collapses to $O(1)$ once
$3n^2 \times 8$ bytes exceed the cache.

What decides it: **whether the working set of the innermost loops fits**. Fix it
by blocking so that three tiles of size $b \times b$ are resident, which gives
reuse $O(b)$ instead of $O(n)$ - the two-level structure of a real BLAS, a cache
block copied into contiguous scratch plus a register micro-kernel [S31] [S8].
Code: `src/cpp/matmul_opt.cpp`.

### P7 *(adapted from [S44] task 3, and [S8], Performance → Caches)*

You are tiling a matrix product for a cache of $C$ bytes, doubles.
(a) Why must **three** tiles fit and not two? (b) Give the largest power-of-two
tile for an L1 of 128 KB and for an L2 of 16 MB. (c) The kernel is not a sum but
a $\min$ over $k$ (the $(\min,+)$ semiring of P19). Does the blocking argument
still hold?

**Answer.** (a) The innermost triple loop over a tile touches a tile of $A$, a
tile of $B$ **and** the accumulating tile of $C$; if $C$'s tile is evicted, the
partial results have to be re-read and re-combined, which is the traffic the
blocking was meant to remove. So the residency condition is
$3b^2 \times 8 \le C$.
(b) $b \le \sqrt{C/24}$, rounded down to a power of two: 128 KB → $b = 64$
(96 KB resident); 16 MB → $b = 512$ (6 MB resident). Computed by
`largest_block_for_cache` in
[`../src/exercises/cornell-cs5220-2015/minplus_path.py`](../src/exercises/cornell-cs5220-2015/minplus_path.py).
(c) Yes, and the reason is algebraic, not empirical: $\min$ is associative and
commutative and $+$ distributes over it, so partial results over disjoint
$k$-blocks combine exactly as partial sums do. Verified for four block sizes and
a non-divisible matrix size in `test_minplus_path.py`.

---

## Topic 3 - Numerical Derivatives and Integrals

### P8 *(adapted from [S43], ch. Numerical treatment of differential equations)*

Analyse $u_{i+1} = u_i + h\bigl(f(x_i) + f(x_{i+1})\bigr)/2$ for $u' = f(x)$:
accuracy, and computational cost relative to explicit and implicit Euler.

**Answer.** It is the average of explicit and implicit Euler, i.e. the
trapezoidal rule. Taylor expansion gives a local truncation error
$-\tfrac{h^3}{12}u'''(\xi)$ and hence a **global order 2**, against order 1 for
either Euler. Because $f$ here depends on $x$ only and not on $u$, the "implicit"
half costs nothing: no equation has to be solved, and the scheme is as cheap as
explicit Euler per step - two $f$ evaluations, one of which is reused from the
previous step, so one new evaluation per step in practice. The lesson to carry:
implicitness is only expensive when the right-hand side depends on the unknown.
(For $u' = f(x,u)$ the same scheme is Crank–Nicolson and does need a solve; see
note 04.)

### P9 *(ours, against [S25])*

For the central difference $D_h u = (u(x+h) - u(x-h))/2h$ in double precision,
derive the $h$ that minimises the total error and the error attained there. Why
does halving $h$ eventually make the answer worse?

**Answer.** Truncation $\approx \tfrac{h^2}{6}|u'''|$; round-off
$\approx \varepsilon |u| / h$ with $\varepsilon \approx 2.2\times10^{-16}$.
Minimising $\tfrac{h^2}{6}C_t + \varepsilon C_r/h$ gives
$h_\ast \sim (3\varepsilon C_r/C_t)^{1/3} \approx \varepsilon^{1/3} \approx
6\times10^{-6}$, with total error $\sim \varepsilon^{2/3} \approx 4\times10^{-11}$.
Below $h_\ast$ the cancellation in the numerator dominates: the two values agree
to more and more digits and their difference is pure noise, amplified by $1/2h$.
This is the one plot in numerical differentiation that has a V in it, and it is
worth being able to sketch with the two slopes ($+2$ and $-1$ on a log-log
plot) labelled. Code: `src/py/fd_poisson.py`, `src/py/fdstencil.py`.

---

## Topic 4 - Finite Difference Discretisation

### P10 *(adapted from [S43], ch. Numerical treatment of DEs, §boundary conditions)*

A Neumann condition $u'(0) = u'_0$ is imposed as $(u_0 - u_1)/h = u'_0$.
(a) What order is that, and what does it do to the global order of an otherwise
second-order scheme? (b) Give a second-order alternative and say what it costs.

**Answer.** (a) A one-sided difference is **first order**: its truncation error
is $\tfrac{h}{2}u''(0) + O(h^2)$. A first-order boundary condition in a
second-order scheme for a *boundary value problem* pollutes the whole solution -
the error propagates through $A^{-1}$ - so the global order drops to 1. This is
the classic silent order loss, and the way you catch it is a convergence table
that shows 1.0 where you expected 2.0.
(b) A **ghost point**: introduce $u_{-1}$, impose the centred condition
$(u_1 - u_{-1})/2h = u'_0$, and eliminate $u_{-1}$ from the interior stencil at
$i=0$. The cost is one extra unknown per Neumann boundary (or none, if
eliminated symbolically) and a modified first row of $A$; the alternative, a
one-sided *second-order* three-point formula, keeps the matrix size but widens
the bandwidth of the first row. Code: `src/py/fd_poisson.py`, note 04.

### P11 *(adapted from [S43], ch. Numerical treatment of DEs, §2D BVP)*

Central differences on a square give a block-tridiagonal matrix with equal
blocks. Sketch the structure on a **triangular** domain. For $n = 4$ you should
get a $10 \times 10$ matrix - say what the block sizes are and what changes.

**Answer.** Order the unknowns row by row. On a triangle with $n = 4$ the rows
hold 4, 3, 2 and 1 interior points, total 10. The matrix is still block
tridiagonal, because the 5-point stencil couples a point only to its own row and
the two neighbouring rows, but the diagonal blocks are now $4\times4$, $3\times3$,
$2\times2$, $1\times1$ and the **off-diagonal blocks are rectangular**
($3\times4$, $2\times3$, $1\times2$) - a row's points couple to a *subset* of the
next row's.

What this changes in practice: the regular structure that lets you write the 2D
Poisson operator as a Kronecker sum $A = I \otimes T + T \otimes I$ is gone, so
fast direct solvers built on that factorisation no longer apply, and the
bandwidth is no longer constant. This is the step at which a structured-grid code
has to become an unstructured one - which is topic 9's whole justification.

---

## Topic 5 - Numerical Linear Algebra

### P12 *(adapted from [S43], ch. Numerical treatment of DEs, §tridiagonal systems)*

(a) Show the LU factors of a tridiagonal matrix are bidiagonal. (b) Give the
operation count of the solve and of a matrix-vector product with the same
matrix. (c) Eijkhout remarks that this relation "is not typical" - what is
atypical, and what does the typical case look like?

**Answer.** (a) Eliminating $a_{i+1,i}$ with row $i$ touches only columns $i$ and
$i+1$, because row $i$ has no entries beyond column $i+1$. So no fill-in is
created: $L$ is unit lower bidiagonal, $U$ upper bidiagonal.
(b) Factorisation $\approx 3n$ flops, forward/back substitution $\approx 5n$;
the matvec is $\approx 5n$. Both are $O(n)$, i.e. **solving costs the same order
as multiplying**.
(c) That is the atypical part. Normally a matvec is $O(\text{nnz})$ while a
direct solve is far worse because of **fill-in**: for the 2D Poisson matrix a
banded solve is $O(N^2)$ for $N^2$ unknowns with bandwidth $N$, and in 3D a
sparse Cholesky needs $O(N^4)$ storage and $O(N^6)$ work for $N^3$ unknowns.
That gap is the entire reason iterative methods exist - each iteration is a
matvec, so the cost is $O(\text{nnz})\times$ iteration count [S22]. Code:
`src/py/csr.py`, `src/cpp/csr.cpp`.

### P13 *(ours, against [S22] and [S23])*

For the 2D Poisson system on an $N\times N$ grid: (a) how does $\kappa(A)$ grow,
(b) how many CG iterations to a fixed tolerance, (c) at what $N$ does CG beat a
banded direct solve, and (d) what does a Jacobi preconditioner do to the answer?

**Answer.** (a) The eigenvalues are $\lambda_{k} = \tfrac{4}{h^2}\sin^2(k\pi h/2)$,
so $\kappa \approx 4/(\pi h)^2 = O(N^2)$ [S23].
(b) The CG energy-norm bound gives
$k \sim \tfrac12\sqrt{\kappa}\,\log(2/\varepsilon) = O(N)$ [S22]. Total work
$O(N) \times O(N^2) = O(N^3)$ for $N^2$ unknowns.
(c) The banded solve is $O(N^4)$ with $O(N^3)$ storage, so CG wins
asymptotically and, on the measured runs in `src/cpp/fd_poisson1d.cpp` and
`src/cpp/csr.cpp`, from a few hundred unknowns per direction - but the crossover
is machine-dependent and the honest exam answer states the exponents and says
*measure it*.
(d) **Nothing useful.** Jacobi rescales by the diagonal, and the diagonal of the
Poisson matrix is constant, so $\kappa$ is unchanged and the iteration count is
unchanged (up to the boundary rows). That is a good question to be able to answer
cold, because the instinct is to say "preconditioning helps". IC(0) or a
multigrid V-cycle is what actually moves $\kappa$.

---

## Topic 6 - Random Number Generation and Monte Carlo

*No substitute source was used here; see "Where no substitute exists" below.
Both problems are ours, written against the original papers.*

### P14 *(ours, against [S27] and [S29])*

(a) State the Hull–Dobell condition for an LCG $x \leftarrow (ax + c) \bmod m$ to
have full period $m$. (b) RANDU is $a = 65539$, $c = 0$, $m = 2^{31}$. Show that
consecutive triples satisfy an exact linear relation and say how many planes they
lie on. (c) What does Marsaglia's bound say in general?

**Answer.** (a) Full period for every seed iff $\gcd(c,m) = 1$, $a \equiv 1 \pmod p$
for every prime $p \mid m$, and $a \equiv 1 \pmod 4$ if $4 \mid m$. Note $c \ne 0$
is required, so RANDU (with $c = 0$) is not covered - a multiplicative generator
has period at most $m-1$ and only for a primitive root.
(b) $a = 65539 = 2^{16}+3$, so $a^2 = 2^{32} + 6\cdot2^{16} + 9 \equiv 6a - 9
\pmod{2^{31}}$, giving $x_{k+2} = 6x_{k+1} - 9x_k \pmod{2^{31}}$ **exactly**.
Every triple therefore lies on one of **15** parallel planes. Tested in
`src/py/test_lattice.py`.
(c) $k$-tuples from any LCG lie on at most $(k!\,m)^{1/k}$ hyperplanes - for
$k=3$, $m=2^{31}$ that is about 2344, so RANDU's 15 is catastrophically worse
than the bound allows, not merely an instance of it.

### P15 *(ours)*

You estimate $\int_0^1 f$ by Monte Carlo and by the composite trapezoidal rule.
(a) Give the error of each against the number of samples $N$ in $d$ dimensions.
(b) At what $d$ does Monte Carlo win? (c) Name two variance-reduction techniques
and say what each needs to know about $f$.

**Answer.** (a) MC: $\sigma/\sqrt N$, **independent of $d$**. Trapezoid on a
tensor grid: $O(h^2) = O(N^{-2/d})$.
(b) $N^{-2/d} > N^{-1/2}$ once $d > 4$; at $d = 4$ they tie. That is the whole
argument for Monte Carlo, and it is worth stating as "MC's error does not know
what $d$ is".
(c) **Antithetic variates** - needs $f$ to be monotone in the uniform variate for
the induced correlation to be negative. **Control variates** - needs a function
$g$ with a known integral and high correlation with $f$. Both are implemented and
measured in `src/py/montecarlo.py` and `src/cpp/rng_mc.cpp`; both reduce the
constant, neither changes the $N^{-1/2}$ rate.

---

## Topic 7 - Shared Memory Parallel Computing

### P16 *(adapted from [S8], Performance → Parallelization, "Exercises")*

Implement a mutual-exclusion lock using only
`std::atomic<T>::compare_exchange_strong`. What is the bug that catches almost
everyone, and why does it not show up in a single-threaded test?

**Answer.**

```cpp
void lock() {
  bool expected = false;
  while (!flag_.compare_exchange_strong(expected, true)) expected = false;
}
void unlock() { flag_.store(false); }
```

The bug is the missing `expected = false`. On failure, CAS **overwrites its
`expected` argument with the value it observed** - here `true` - so every
subsequent attempt compares against `true`, and the loop either spins forever or,
worse, succeeds spuriously when the lock is taken. It never shows up
single-threaded because the first CAS always succeeds and the retry path is never
entered; it needs contention. Tested in
`../src/exercises/tuwien-introsc-2025/taskmanager_matmul.cpp`
by four threads doing 20 000 **non-atomic** increments each under the lock and
requiring the exact total.

### P17 *(adapted from [S8], same exercise list)*

Parallelise $C = AB$ with a task-based runtime (`RunParallel(ntasks, f)`, no
OpenMP). (a) Where, if anywhere, is a lock needed? (b) How many tasks per thread,
and why not one? (c) The measured speedup flattens at 4 threads on a 6+6-core
machine. Name three candidate causes and how you would tell them apart.

**Answer.** (a) **Nowhere**, if the tasks are row bands of $C$: bands are
disjoint, each element of $C$ is written by exactly one task, and $A$ and $B$ are
read-only. A lock would be needed for a *shared accumulator* - e.g. if you split
over $k$ instead of $i$, where several tasks add into the same $C$ tile.
(b) Several (4 is a good default). One task per thread makes the schedule static,
so one slow task - an E-core, a page fault, an OS steal - leaves everyone waiting.
More tasks let the atomic counter balance dynamically; too many and the
per-task overhead dominates.
(c) **(i) Memory bandwidth saturated** - check by computing the arithmetic
intensity (P3): if the kernel is left of the ridge, cores cannot help. Test:
re-run at a matrix size that fits in L2 and see if the scaling returns.
**(ii) Heterogeneous cores** - 6 performance + 6 efficiency cores [S34] do not
contribute equally; test by pinning or by comparing 6 threads with 12.
**(iii) A serial section or overhead** - fit Karp–Flatt: a serial fraction that
*rises* with thread count means overhead or a shared limit, not a serial section.
On this machine $e$ stays at 0.02 for 2 and 4 threads and jumps to 0.11 at 8, when two threads land on E-cores (`src/py/scaling.py`, re-measured 2026-09-27).

### P18 *(adapted from [S43], ch. Parallel Computing; and [S19] [S20] [S21])*

A code is measured at $T_1 = 100$ s, $T_4 = 32$ s, $T_8 = 20$ s.
(a) Fit Amdahl's serial fraction from $T_4$. (b) Predict $T_8$ from it and
compare. (c) Compute Karp–Flatt at 4 and 8 and say what the trend means.
(d) Someone claims Gustafson's law "breaks" Amdahl's limit. Rebut it.

**Answer.** (a) $S_4 = 3.125$; $S(p) = 1/(f + (1-f)/p)$ gives $f = 0.0933$.
(b) $S_8 = 1/(0.0933 + 0.9067/8) = 4.84$, so $T_8 = 20.7$ s against **20 s**
measured - the model slightly *over*-predicts the time, i.e. the code scales a
shade better than Amdahl allows for. That is the boring case, and boring is the
answer you want.
(c) Karp–Flatt $e = (1/S_p - 1/p)/(1 - 1/p)$: $e_4 = 0.0933$, $e_8 = 0.0857$.
Flat to slightly falling, so the model holds and the loss really is a serial
section. Had $e$ *risen* with $p$ you would be looking at overhead, communication
or a saturated shared resource instead - a rising $e$ is the diagnostic, and it
is the one thing a bare Amdahl fit cannot tell you.
(d) It does not. Amdahl's $f$ is measured against the **1-processor** time and is
independent of $p$; Gustafson's $s$ is measured against the **$p$-processor**
time and depends on $p$. Substituting $f = s/(s + (1-s)p)$ turns one formula into
the other exactly [S21]. The two laws are one law in two normalisations;
Gustafson's contribution is the observation that problem size grows with machine
size, not a different speedup law. Implemented and tested in
`src/py/scaling.py`, which reproduces Gustafson's own 1024-processor numbers.

---

## Topic 8 - Algorithmic Complexity and Data Structures

### P19 *(adapted from [S44], HW3)*

All-pairs shortest paths. Floyd–Warshall is $O(n^3)$; the assignment's reference
instead squares the distance matrix in the $(\min,+)$ semiring until it stops
changing. (a) Why does that terminate, and after how many squarings?
(b) What is the total cost? (c) Why would anyone choose the **slower** algorithm?

**Answer.** (a) After $s$ squarings the entries are the shortest **walks using at
most $2^s$ edges**. A shortest path in a graph with no negative cycles uses at
most $n-1$ edges, so the matrix is final after
$\lceil \log_2(n-1) \rceil$ squarings and one more detects it.
(b) $n^3$ semiring operations per squaring, so
$O(n^3 \log n)$ - a factor $\lceil\log_2(n-1)\rceil + 1$ more than
Floyd–Warshall (7 at $n = 64$, 11 at $n = 1024$).
(c) Because the kernel is a **plain matrix product**: it blocks like GEMM (P7),
vectorises, and parallelises over independent output tiles with no
loop-carried dependence. Floyd–Warshall's $k$ loop is sequential - iteration $k$
reads what iteration $k-1$ wrote - so it parallelises only within a $k$ step.
Trading a $\log n$ factor of arithmetic for a dependence-free kernel is the
canonical parallel-computing bargain, and being able to say *why* is the point
of the question. Code:
[`../src/exercises/cornell-cs5220-2015/minplus_path.py`](../src/exercises/cornell-cs5220-2015/minplus_path.py).

### P20 *(adapted from [S44], HW3, and ours)*

The squaring loop stops when the matrix no longer changes. Written as
`if (nxt == d) break;` with exact floating-point equality, it runs far past the
$\log n$ bound. Why, and what is the fix?

**Answer.** $\min_k(d_{ik} + d_{kj})$ re-adds the two halves of an
already-optimal path. In floating point $(a+b)+c$ and $a+(b+c)$ differ by an
ulp, so the recomputed value can land **one ulp below** the stored one; `min`
takes it, the matrix "changes", and the loop chases last bits. Measured: **8**
squarings instead of 4 at $n = 32$. The fix is a tolerance,
$\max|{\text{nxt}-d}| \le \texttt{tol}$, with $\infty$ compared structurally
rather than arithmetically ($\infty - \infty$ is NaN). The general lesson, which
is fair game for any of topics 3–5: a convergence test written for the
*algorithm* can be wrong for *numerical* reasons.

### P21 *(ours, against [S14])*

You must store an unstructured mesh's element→node connectivity and answer
"which elements touch node $j$?". Compare `std::vector<std::vector<int>>`,
`std::map<int, std::vector<int>>`, `std::unordered_map`, and a CSR-style pair of
flat arrays. Give the standard-mandated complexity, the memory, and the
cache behaviour, and pick one.

**Answer.**

| structure | lookup | memory | cache |
|---|---|---|---|
| `vector<vector<int>>` | $O(1)$ index | one heap block per node, 24 B header each | one indirection per node; blocks scattered |
| `map` | $O(\log n)$ (red-black tree) | node per entry, ~48 B overhead | pointer chase, worst of the four |
| `unordered_map` | $O(1)$ average, $O(n)$ worst | bucket array + node per entry | one hash + one chase |
| **CSR** (`offsets[n+1]`, `indices[nnz]`) | $O(1)$ index, $O(\deg)$ scan | $4(n+1) + 4\,\text{nnz}$ bytes, contiguous | **sequential**; prefetcher-friendly |

Pick **CSR**. The complexities of the first three are what the C++ standard
requires of the containers [S14], but on a static mesh the deciding factor is not
the exponent - it is that CSR's two flat arrays are contiguous, so a sweep over
all elements of all nodes is a single stream, and the same layout is already what
the sparse matrix wants (topic 5). The price is that CSR is immutable: inserting
one incidence means rebuilding. If the mesh is being refined, build with
`vector<vector<int>>` and compress once. Code: `src/cpp/containers_bench.cpp`,
`src/py/csr.py`.

---

## Topic 9 - Mesh Generation and Visualisation

*No substitute source covers this topic (see below). Both problems are ours,
written against the normative documents, which is what makes them checkable.*

### P22 *(ours, against [S12] and [S13])*

Here is a legacy VTK file for a $4\times3$ scalar field on a unit-spaced grid.
Find every error.

```
# vtk DataFile Version 3.0
scalar field
ASCII
DATASET STRUCTURED_POINTS
DIMENSIONS 3 2 0
ORIGIN 0 0 0
SPACING 1 1 1
POINT_DATA 12
SCALARS temperature float
0 1 2 3 4 5 6 7 8 9 10 11
```

**Answer.** Four errors.
1. **`DIMENSIONS 3 2 0`** - `DIMENSIONS` counts **points**, not cells, and every
   component must be $\ge 1$. A $4\times3$ point grid in 2D is `DIMENSIONS 4 3 1`.
   A 0 is illegal, not "flat".
2. **`POINT_DATA 12`** is right only by accident: it must equal
   $n_x n_y n_z = 4\cdot3\cdot1 = 12$. With the declared dimensions it would have
   to be 0.
3. **The `LOOKUP_TABLE` line is missing.** `SCALARS name type [numComp]` must be
   followed by `LOOKUP_TABLE default` (or a named table) before the values.
4. Not an error but a trap: the values must be in **x-fastest** order - *"Data
   with implicit topology … are ordered with x increasing fastest, then y, then
   z"* [S12]. A row-major dump of a `field[y][x]` array is already correct; a
   dump of `field[x][y]` is not.

Also worth knowing and *not* an error here: the version on line 1 is
`# vtk DataFile Version x.x` - it is **not** fixed at 3.0, and VTK's own example
files use 2.0. The header on line 2 is limited to 256 characters. Validator:
`src/py/vtk_check.py`, which rejects each of these.

### P23 *(ours, against [S32])*

(a) State the defining property of a Delaunay triangulation and the optimality
property that follows. (b) A triangulation of $n$ points with $h$ on the convex
hull has how many triangles? (c) Why does Delaunay refinement *terminate* with a
minimum-angle guarantee, and what is the guaranteed angle?

**Answer.** (a) **Empty circumcircle**: no vertex of the triangulation lies
inside the circumcircle of any triangle. It follows that among all
triangulations of the point set, the Delaunay one **maximises the minimum
angle** - which is why it is the mesh you want for a finite-element or
finite-difference discretisation, where thin triangles wreck the conditioning.
(b) $2n - 2 - h$ triangles (and $3n - 3 - h$ edges), by Euler's formula. Useful
as a cheap self-check on any mesh generator, and tested in
`src/py/test_delaunay.py`.
(c) Ruppert-style refinement inserts the circumcentre of any triangle whose
minimum angle is below a threshold. Each insertion is at least as far from every
existing vertex as the local feature size, so the vertex set stays
well-separated and the algorithm cannot insert infinitely many points in a
bounded region - that is the termination argument, and it is what the angle
threshold buys. Shewchuk's variant **guarantees 20.7°** with a proof and reaches
about 33° in practice [S32]. The guarantee is a statement about termination, not
about quality.

---

## Topic 10 - Software Engineering Principles for Scientific Computing

*No substitute source covers this topic either; the problem is ours.*

### P24 *(ours, against [S36] [S37] [S38])*

(a) `set(CMAKE_CXX_STANDARD 17)` is in your `CMakeLists.txt` and the build
silently uses C++14. Why, and what is the one-line fix? (b) `find_package(OpenMP
REQUIRED)` fails on macOS with AppleClang. Why, and how do you fix it without
changing the compiler? (c) Your code passes its tests at `-O2` and crashes at
`-O3`. Name the three sanitizers you would run, in order, and one bug class each
finds that the others do not.

**Answer.** (a) Without `CMAKE_CXX_STANDARD_REQUIRED`, CMake documents that the
standard "may decay to a previous standard if the requested is not available" -
a silent downgrade, not an error. Fix:
`set(CMAKE_CXX_STANDARD_REQUIRED ON)` (and `set(CMAKE_CXX_EXTENSIONS OFF)` if you
want `-std=c++17` rather than `-std=gnu++17`).
(b) Xcode's clang ships **no `libomp`**, and `FindOpenMP` does not search a
Homebrew keg, so it reports `Could NOT find OpenMP_CXX (missing:
OpenMP_CXX_FLAGS OpenMP_CXX_LIB_NAMES)`. Fix with the package-root rule:
`-DOpenMP_ROOT=$(brew --prefix libomp)`. Both defects were found by *running* the
snippet, not by reading it; see `src/cpp/CMakeLists.txt` and the changelog.
(c) **UBSan** first - it is nearly free and catches signed overflow and invalid
shifts, which `-O3` is entitled to assume cannot happen (and which therefore
*change behaviour* between `-O2` and `-O3`). **ASan** second - heap and stack
overflow and use-after-free, at ~2× slowdown and ~2–3× memory [S38]; it finds
nothing about threads. **TSan** third and **separately**, because it is
incompatible with ASan in the same binary - data races, which neither of the
others sees. None of them finds an uninitialised read on clang; that needs
MSan and a fully instrumented dependency chain. Scripts: `src/sh/sanitizers.sh`.

---

## Where no substitute exists

Stated plainly, because padding this note would be worse than a gap in it.

| TISS topic [S1] | substitute practice material found | what was done instead |
|---|---|---|
| 1 Computer Architectures | **plenty** - [S43] ch. 1, [S8] Performance | P1–P4, plus a runnable simulator |
| 2 Serial Optimization | **plenty** - [S43], [S8], [S44] | P5–P7 |
| 3 Numerical Derivatives and Integrals | **thin** - [S43]'s chapter is about DEs, not quadrature; one usable exercise | P8 from [S43], P9 ours |
| 4 Finite Difference Discretization | **adequate** - [S43] ch. 4 | P10, P11 |
| 5 Numerical Linear Algebra | **adequate** - [S43] ch. 5; [S22] is a free book but sets no exercises | P12 from [S43], P13 ours |
| 6 Random Numbers and Monte Carlo | **none.** [S43] has a Monte Carlo chapter with **no exercises**; [S8] has no RNG content; [S44] none | P14, P15 ours, written against [S27] [S29] - both have a single provable answer |
| 7 Shared Memory Parallel Computing | **plenty** - [S8]'s own exercises, [S43] ch. 2 | P16–P18 |
| 8 Algorithmic Complexity and Data Structures | **adequate** - [S44] HW3; [S43] on sparse storage | P19, P20 from [S44]; P21 ours |
| 9 Mesh Generation and Visualisation | **none.** Grepping [S43] for "mesh generation", "unstructured grid" and "visualization" returns nothing; [S8] goes to finite elements without a mesh-generation chapter; [S44] has none. No free licence-clear *exercise set* on Delaunay meshing or file formats was found at all | P22, P23 ours, against the **normative** documents [S12] [S13] [S32] - which is arguably better, because the answer is fixed by a specification rather than by an instructor |
| 10 Software Engineering Principles | **none** in the three sources. [S43] vol. 1 has none; the series' tutorials volume is out of scope; [S8]'s is a CMake/GitHub walkthrough, not exercises | P24 ours, against [S36] [S37] [S38], built from defects found by executing the examples |

Two things follow. First, the outside sources are strong exactly where this
course's *machine-facing* topics are (1, 2, 7, 8) and silent where its
*domain-facing* ones are (6, 9, 10) - so if you are budgeting time against
available practice, those three are where you have to write your own. Second,
topics 6, 9 and 10 are the ones where a **specification** fixes the answer
([S14], [S12] [S13], [S36] [S37]), so a self-written question there is still
objectively markable. That is the compensation, and it is why those problems were
written the way they were.

## How to use this

Three hours is the length of the real paper [S1]. A defensible mock: **P3, P7,
P10, P13, P17, P19, P22, P24** - one per cluster, all of them "choose, compute,
justify", none of them a long hand computation. That matches the shape argued for
in [`00-exam-focus.md`](00-exam-focus.md) and takes about the right time.

Then run the code: the three solution modules under
[`../src/exercises/`](../src/exercises/README.md) are what turns P1, P2, P5, P7,
P16, P17, P19 and P20 from claims into measurements.
