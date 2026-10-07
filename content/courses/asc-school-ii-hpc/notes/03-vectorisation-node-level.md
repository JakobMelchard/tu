# 03 Vectorisation and node-level optimisation

Prepares for the vectorisation and affinity sessions of *Shared-Memory
Parallelization with OpenMP* [S8] and the node-level half of the hybrid course
[S5]. The memory hierarchy, serial optimisation and the roofline derivation are
in NSSC I notes 01-02; vectorisation, compiler reports and the matmul case in
Efficient Programs notes 04, 06, 09 [S11]. Here: only what changes on a
cluster node, plus one measured example.

## Definitions

- **SIMD lane / vector width $W$**: elements processed by one instruction.
  Doubles: NEON 128 bit, $W=2$; AVX2 256 bit, $W=4$; AVX-512, $W=8$.
- **FMA**: fused multiply-add $a \leftarrow a + b c$, one rounding, counted as
  2 flops.
- **Latency $L$ / throughput**: cycles until a result is usable vs
  instructions issued per cycle. A reduction $s \leftarrow s + x_i y_i$ is a
  dependency chain: one add per $L$ cycles. Hiding it needs $L \times
  (\text{pipes})$ independent accumulators, each $W$ wide.
- **Reassociation**: IEEE addition is not associative, so under strict
  semantics the compiler must keep the source order and cannot split a sum
  into lanes. `#pragma omp simd reduction(+:s)` or `-ffast-math`
  (`-fassociative-math`) grants the permission [S16] [S23].
- **Arithmetic intensity** $I$ = flops / bytes moved to or from memory.
- **Roofline** [S18]: attainable $P(I) = \min(P_\text{peak}, I\,B)$ with
  memory bandwidth $B$. Ridge point $I^* = P_\text{peak}/B$: left of it a
  kernel is memory-bound and SIMD barely helps.

## Worked example 1: four dot products, measured

[`../src/c/simd_dot.c`](../src/c/simd_dot.c), `cc -O2 -fopenmp-simd`, one
M3 Pro core, three runs of `./simd_dot` agreeing within ~5 % [S10]. `scalar`
has vectorisation switched off; `unroll4` uses 4 scalar accumulators;
`omp_simd` lets the compiler vectorise; `intrin` is NEON with 4 vector
accumulators.

| n (x and y) | scalar | unroll4 | omp_simd | intrin |
|---|---|---|---|---|
| 2048 (32 KiB, L1) | 1.08 ns, 1.9 GF/s | 0.25 ns, 8.0 GF/s | **0.128 ns, 15.6 GF/s** | 0.129 ns, 15.5 GF/s |
| $2^{24}$ (256 MiB, DRAM) | 1.12 ns, 1.8 GF/s, 14 GB/s | 0.285 ns, 7.0 GF/s, 56 GB/s | 0.161 ns, 12.4 GF/s, **99 GB/s** | 0.155 ns, 12.9 GF/s, 104 GB/s |

(ns per element; GFlop/s at 2 flops and GB/s at 16 bytes per element.)
Reading it:

1. In L1, `scalar` $\to$ `unroll4` is 4.3x with **no** SIMD at all: breaking
   the add chain (latency to throughput) is the first win.
2. `omp_simd` doubles that ($W=2$): 8.5x total. Hand-written NEON is not
   faster than the pragma.
3. From DRAM the dot product has $I = 2/16 = 1/8$ flop/byte. At the measured
   $B \approx 100$ GB/s of one core the roof is $I B \approx 12.5$ GFlop/s:
   the SIMD variants sit **on the memory roof**, the scalar one far below it
   (latency-bound, not bandwidth-bound). SIMD still pays here only because one
   core has the whole memory system to itself.
4. On a full cluster node all cores share $B$, so the per-core roof is
   $B/\text{cores}$, far below 100 GB/s; then even `unroll4` reaches it and
   SIMD gains vanish for this kernel.

A first measurement while another job loaded the laptop (load average ~18)
gave 2-7x worse numbers for every variant (e.g. `omp_simd` 7.3 GF/s in L1,
13.3 GB/s from DRAM). Measure on an idle, exclusive node.

`make vecreport` prints clang's remarks. A surprise worth knowing: the plain
loop *without* the pragma is also reported "vectorized (width 2, interleave
4)" on AArch64. The assembly shows why it is still exact: the 8 multiplies
per iteration are `fmul.2d`, the 8 adds are scalar `fadd d0, d0, ...` in
source order, an **in-order (strict) reduction** that keeps IEEE semantics and
so gains little (checked in the scratch assembly, [S10] [S23]).

## Worked example 2: flags vs intrinsics on the cluster

```bash
# portable build that uses the node's full vector ISA
mpicc -O3 -march=native -fopenmp prog.c          # compile ON the node type you run on
mpicc -O3 -march=znver4 ...                      # or name it (MUSICA Zen4) [S13]
# what got vectorised
clang -O3 -Rpass=loop-vectorize -Rpass-missed=loop-vectorize -c prog.c
gcc   -O3 -fopt-info-vec-optimized -fopt-info-vec-missed -c prog.c
```

`-march=native` on a login node of a different CPU generation produces a
binary that faults with "illegal instruction" on the compute nodes. VSC-5 mixes
Zen2 (A40 GPU nodes) and Zen3; MUSICA has Zen4 CPU and GPU nodes and Zen5
B200 nodes [S13] (the sibling course documents the VSC-5 case). Intrinsics tie
code to one ISA (`simd_dot.c` needs two versions and a fallback); prefer
`omp simd` and let `-march` choose the width.

## Worked example 3: cache blocking

Transpose-like access $B_{ji} = A_{ij}$ of $n \times n$ doubles walks one of
the two arrays with stride $8n$ bytes: every access a new cache line, 8x the
traffic. Tiling with blocks of $b \times b$:

```c
for (int ii = 0; ii < n; ii += b)
  for (int jj = 0; jj < n; jj += b)
    for (int i = ii; i < min(ii + b, n); i++)
      for (int j = jj; j < min(jj + b, n); j++)
        B[j * n + i] = A[i * n + j];
```

keeps $b$ lines of $B$ in cache while each is filled. Condition: $2 b^2
\cdot 8\,\text{B} \lesssim$ cache size (both tiles), e.g. $b = 32$ for a
32 KiB L1, $b \approx 256$ for 1 MiB L2. For matmul the tile count is three
and the gain is larger; derivation and measurements in Efficient Programs
note 09 [S11].

## Node-level roofline in practice

Measure, do not look up: $B$ with a STREAM-type triad over all cores of the
node, $P_\text{peak}$ from clock x cores x $2W$ x FMA pipes, or both from
`likwid-bench` [S19]. Then place each hot loop by its measured $I$ (flops and
bytes from `likwid-perfctr -g MEM_DP`). Two caveats on a many-core node:

- **Bandwidth saturates before the cores do**: a memory-bound loop stops
  scaling after a few cores per NUMA domain, so more threads buy nothing.
- **Per-domain bandwidth**: with 8 NUMA domains [S14], a single-threaded
  initialisation puts all pages in one domain and caps $B$ at one eighth.

## Pitfalls

- Pointer aliasing: without `restrict` (or `omp simd`) the compiler must
  assume `x` and `y` overlap and may not vectorise.
- Non-unit stride and indirect access (`x[idx[i]]`) need gathers: slow even
  when "vectorised".
- `-ffast-math` also assumes no NaN/Inf and flushes denormals: it silently
  breaks `isnan` checks and compensated (Kahan) summation. Prefer the
  per-loop `omp simd reduction`.
- Timing a 2048-element loop once: below timer resolution. `simd_dot` repeats
  until a sample lasts $\ge 20$ ms and takes the best of 5.
- Speed-ups measured with one core do not transfer to a full node: the
  memory roof per core drops by the number of cores sharing the bandwidth.

## Questions (ours)

1. *Why is `unroll4` 4.3x faster than `scalar` in L1 without SIMD?* The FP add
   latency (several cycles) serialises a single accumulator; four chains keep
   the adder busy.
2. *Why does the compiler not vectorise `s += x[i]*y[i]` at `-O2`?* Vectorising
   reorders the additions, which changes the rounded result; strict IEEE mode
   forbids it. `omp simd reduction(+:s)` permits exactly this reordering.
3. *Dot product on a node with $B$ = 400 GB/s: upper bound?* $I B = 400/8 = 50$
   GFlop/s, independent of core count and vector width.
4. *A binary built with `-march=native` on the login node dies with SIGILL on
   a GPU node. Why?* Different CPU generation; the binary uses instructions the
   compute node lacks. Build on the target node type or name the target.
5. *Block size for a tiled transpose to fit two tiles in a 48 KiB L1?*
   $2 b^2 \cdot 8 \le 49152 \Rightarrow b \le 55$; take $b = 48$ or 32
   (multiple of the line size of 8 doubles).

## Code

- [`../src/c/simd_dot.c`](../src/c/simd_dot.c): `dot_scalar`, `dot_unroll4`,
  `dot_omp_simd`, `dot_intrin` (NEON / AVX2+FMA), exactness and rounding
  checks, `time_fn`. `make -C ../src/c vecreport`.
