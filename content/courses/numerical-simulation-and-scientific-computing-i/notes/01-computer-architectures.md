# 01 Computer architectures

What the hardware does with your loop: where the data lives, how long a load takes, how many flops per second a core can retire, and how to tell which of the two limits your code. Everything in this note is measured by `src/cpp/cache_bench.cpp` on the machine the notes were written on (Apple M3 Pro, `Mac15,7`, Apple clang 21.0.0, `-O2`), with the hardware parameters read from `sysctl` on that machine [S34]. The framing - latency vs throughput, caches, the dependency chain - follows [S8], the online book of one of the 2026W lecturers, and [S35].

**Read every number here with the machine beside it.** Nothing in this note is a fact about computing; it is a fact about one laptop. The method is the transferable part.

## Memory hierarchy

A core cannot compute on DRAM directly. Data moves through a hierarchy of caches; each level is larger, slower and cheaper per byte than the one above.

| level | size on this machine [S34] | latency, measured | typical x86 [S18] |
|---|---|---|---|
| registers | 31 x 64 bit general purpose + 32 x 128 bit NEON | 0 | 16 x 64 bit + 16/32 SIMD |
| L1 data | **128 KB** P-core (`hw.perflevel0.l1dcachesize`), **64 KB** E-core (`hw.perflevel1.l1dcachesize`) | 1.0-1.1 ns | 32-48 KB, ~1 ns |
| L2 | **16 MB** shared by the 6 P-cores (`hw.perflevel0.l2cachesize`), **4 MB** by the 6 E-cores (`hw.perflevel1.l2cachesize`) | 3.8-14 ns | 1-2 MB per core, ~4 ns |
| L3 | **none reported** - `sysctl hw.l3cachesize` is absent on this chip; the system-level cache sits in the memory controller and is not exposed | - | 16-64 MB, 10-20 ns |
| DRAM | **36 GiB** unified (`hw.memsize = 38654705664`) | 85-89 ns at 64 MB, 109 ns at 256 MB | 60-100 ns |

Cores: `hw.ncpu = 12`, six performance (`hw.perflevel0.physicalcpu`) and six efficiency (`hw.perflevel1.physicalcpu`) [S34].

**Read your machine, do not look it up.** Even [S8] falls back on "From Wikipedia, Apple Silicon M1 has …" [S42] for its cache table - a reasonable shortcut, and exactly the one this table avoids: every figure above is a `sysctl` key, and the key name is printed so you can check it. On Linux the equivalent is `lscpu` and `/sys/devices/system/cpu/cpu0/cache/`. That asymmetry shows up again in the scaling table of note 07.

Measured with pointer chasing (each load depends on the previous one, so nothing overlaps): `./bin/cache_bench` prints (2026-09-27)

```
        size        ns/load
       16 KB           1.12      L1
       64 KB           1.12
      256 KB           4.35      L2
     1024 KB           6.51
     4096 KB           8.52
    16384 KB          14.14      L2/SLC boundary
    65536 KB          87.08      DRAM
```

The 16 MB row sits exactly on the P-cluster L2 capacity and is the least reproducible: 10.9, 11.4 and 14.1 ns in three runs the same day, and one disturbed run read 18 ns at 4 MB and 104 ns at 16 MB. Repeat before you believe a boundary point.

Definitions:

- **Cache line**: the unit of transfer between levels. `hw.cachelinesize = 128` on this machine [S34]; 64 B on x86 [S18]. A load of one `double` brings 8 or 16 doubles into cache. Reading the neighbours afterwards is free.
- **Spatial locality**: after `a[i]` you touch `a[i+1]`. **Temporal locality**: you touch `a[i]` again soon. Caches only help if your access pattern has one of the two.
- **Hit / miss**; **miss penalty** = latency of the next level. A DRAM miss costs ~90 ns = ~350 cycles; in that time the core could have done ~1000 flops.
- **Associativity**: a line can only live in a small set of slots determined by its address bits. Power-of-two strides map many lines to the same set (conflict misses).
- **Prefetcher**: hardware detects sequential and constant-stride streams and fetches lines ahead of time. Stride-1 loops rarely see DRAM latency; random access always does.
- **TLB and pages**: virtual-to-physical translation is cached too (page size 16 KB on macOS/arm64, 4 KB on Linux/x86). Strides larger than a page add a TLB miss per load.
- **Bandwidth vs latency**: bandwidth (GB/s) is how much a stream can pull when many loads are in flight; latency (ns) is how long one dependent load takes. A single core on this machine streams at 103-110 GB/s (triad, three runs) but a dependent DRAM load still costs ~90 ns. [S8] states the same distinction as *latency* $t_{lat}$ vs *reciprocal throughput* $t_{rtp}$, with the ski-lift picture: to keep a pipeline full you need $t_{lat}/t_{rtp}$ independent items in flight.

Stride experiment (every element loaded once per stride, 4 accumulators):

```
  stride    ns/load
       1      0.28      streaming, prefetched, bandwidth bound
       8      0.74
      16      3.46      one 128-byte line per load: cost = a line fetch
      64      1.27
    1024      2.63      + TLB misses
```

(The stride-16 row read 1.70 ns in another run; the jump at 16 doubles = 128 B is reproducible, its height is not.)

Once the stride reaches the line size, every load pays for a full line. That is why the row-major loop order `for i: for j: a[i][j]` beats `for j: for i:` by 3.7x in the loop-order test (0.0030 s vs 0.0110 s for 2048x2048; 4.7x at 4096x4096 with `--bench`).

## SIMD and the dependency chain

Single Instruction, Multiple Data: one instruction operates on a vector register. NEON (arm64): 128 bit = 2 doubles or 4 floats. AVX2: 256 bit = 4 doubles. AVX-512: 8 doubles. The compiler auto-vectorises a loop when

1. iterations are independent (no loop-carried dependency: `a[i] = a[i-1] + 1` is not vectorisable),
2. it can prove pointers do not alias (see note 02),
3. floating-point reductions are allowed to be reassociated (`-ffast-math` or `#pragma omp simd reduction`), otherwise `s += a[i]*b[i]` stays scalar because IEEE addition is not associative.

Check with `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize` (clang) [S37].

**Latency vs throughput of one instruction.** [S8] works the canonical example: an x86 `_mm256_fmadd_pd` has latency 4 cycles and reciprocal throughput 0.5, so two can be *started* per cycle but a result is only available four cycles later. A dot product

```cpp
double sum = 0;
for (size_t i = 0; i < n; i++) sum += x[i] * y[i];
```

cannot start the next addition until the previous one lands, so it uses $t_{rtp}/t_{lat} = 1/8$ of the arithmetic peak. Unrolling into independent accumulators fixes it - "with eight accumulators the full latency bottleneck could be overcome" [S8]. That is why `cache_bench`'s FLOP/s kernel uses 8 chains, and why the daxpy-shaped loop `x[i] += alpha*y[i]` does *not* need the trick: its iterations are independent.

A second consequence, also from [S8]: an inner product moves 2 values per fma, a ratio of 2:1, so it can never reach peak no matter how it is unrolled. Computing several inner products at once (two rows of $A$ against two columns of $B$) brings the ratio to 1:1. That is the seed of blocked matmul in note 02 and of [S31].

## Peak performance and the roofline model

$$P_{\text{peak}} = \text{cores} \times f_{\text{clock}} \times \text{FMA units} \times \text{vector width} \times 2 \;\text{flop/FMA}.$$

One M3 P-core at 4 GHz with 4 NEON FMA pipes of 2 doubles: $4 \cdot 10^9 \cdot 4 \cdot 2 \cdot 2 \approx 64$ GFLOP/s. The scalar dependency-chain kernel in `cache_bench` reaches only 15 GFLOP/s (14.2-15.0 in three runs) because it uses no SIMD and has 8 chains for a latency-4 FMA on 4 pipes.

*(Unsourced: the clock and the pipe count. Apple publishes neither a clock ceiling nor an execution-port diagram for the M3, and `sysctl` does not report them. 4 GHz and 4 FMA pipes are the widely-repeated reverse-engineered figures; treat the 64 GFLOP/s as an order of magnitude. The 15 GFLOP/s is measured [S34]. On an Intel or AMD part the same quantities are in [S18] manual 3, which is where [S8] sends you.)*

**Arithmetic intensity** of a kernel: $\text{AI} = \dfrac{\text{flops}}{\text{bytes moved from DRAM}}$ [flop/byte].

**Roofline** [S16]: attainable performance is
$$P = \min\big(P_{\text{peak}},\; \text{AI} \cdot B\big), \qquad B = \text{memory bandwidth}.$$
On log-log axes (AI horizontal, P vertical) this is a sloped line of slope 1 meeting a horizontal roof at the **ridge point** $\text{AI}^* = P_{\text{peak}} / B$. Kernels left of the ridge are memory bound, right of it compute bound. [S16] defines AI as flops per byte of **DRAM** traffic specifically (not per byte of any traffic), and adds *ceilings* below each roof for the optimisations you have not done - no SIMD lowers the compute roof, no unit-stride access lowers the bandwidth roof - so the gap between your measurement and a ceiling names the next thing to fix.

Worked example (numbers from this machine, single core, `./bin/cache_bench` on 2026-09-27): $B = 110$ GB/s (triad), $P_{\text{peak}} = 15$ GFLOP/s scalar. Ridge point $\text{AI}^* = 15/110 = 0.14$ flop/byte.

| kernel | flops | bytes | AI | bound | attainable |
|---|---|---|---|---|---|
| triad `a = b + s*c` [S17] | 2 | 24 | 0.083 | memory | 9.2 GFLOP/s |
| 2D 5-point stencil (perfect cache reuse) | 6 | 16 | 0.375 | compute | 15 GFLOP/s |
| dense matmul $n^3$ blocked | $2n^3$ | $\sim 24 n^2 \cdot n/b$ | $\sim b/12$ | compute for $b \ge 2$ | 15 GFLOP/s |
| SpMV (CSR, double + int32 index) | 2 per nnz | 12 per nnz | 0.17 | compute, barely: $0.17 > 0.14$ | $\min(15, 0.17 \cdot 110 = 18) = 15$ GFLOP/s |

The SpMV row is right of the ridge only because the scalar roof is so low; against the SIMD roof below it is memory bound at 18 GFLOP/s, and the gather `x[col[k]]` (not counted in the 12 bytes) makes even that optimistic.

With SIMD the compute roof rises to ~64 GFLOP/s and the ridge moves right to 0.6; then even the stencil becomes memory bound, which is why stencil codes are optimised by reducing traffic (blocking in time, fusing loops), not by counting flops.

## Measuring FLOP/s and bandwidth

- Count flops analytically ($2n^3$ for matmul, $2\,\text{nnz}$ for SpMV); never trust "number of operations in the source".
- Count bytes as *compulsory traffic*: each array read or written once, 8 B per double. Write-allocate adds a read for every store unless streaming stores are used. [S17] counts the bytes the *program asked for* - the STREAM convention - which is why two papers can report different GB/s for the same kernel.
- The **Triad** kernel `a[i] = b[i] + s*c[i]` is [S17]'s, with 2 flops and 24 bytes per iteration and arrays at least 4x the last-level cache. `cache_bench::triad_gbs` is that kernel.
- Time with a monotonic wall clock (`std::chrono::steady_clock`, `omp_get_wtime`, `time.perf_counter`), repeat, report the minimum (least disturbed) or median, never the mean of noisy runs.
- Warm up: the first pass pays page faults and cold caches.
- Keep the result alive (print it, or write it to a `volatile`) or the compiler deletes the loop.
- Use problem sizes larger than the last cache level when you want DRAM bandwidth, smaller than L1 when you want compute peak.
- Hardware counters (`perf stat`, Instruments on macOS) give cache-miss rates directly.

## Pitfalls

- Timing one run of a kernel that takes microseconds: timer resolution and turbo transitions dominate. Repeat until the total is > 0.1 s.
- Comparing GB/s numbers that counted bytes differently (with or without write-allocate, with or without the index array of a sparse matrix).
- Thinking latency and bandwidth are the same thing: random gather (`x[col[k]]` in SpMV) is latency bound and runs at a small fraction of the streaming bandwidth.
- Power-of-two array dimensions (1024 x 1024) can produce cache-set conflicts for column access; pad to 1025.
- Measuring on a laptop under thermal throttling or with other threads running.

## Exam-style questions

1. **A loop touches 1 double every 128 bytes of a 1 GB array. How long does it take, roughly, on a machine with 100 GB/s bandwidth?** Every load brings a whole 128 B line, so the full 1 GB is transferred: about 10 ms, the same as touching every element. Stride-1 would do 128x more useful work in that time.
2. **Define arithmetic intensity and use it to decide whether `y[i] = a*x[i] + y[i]` (daxpy) is memory or compute bound on a machine with 50 GFLOP/s and 50 GB/s.** AI = 2 flop / 24 B (read x, read y, write y) = 0.083; ridge point is 1 flop/byte, so daxpy is memory bound at 50 x 0.083 = 4.2 GFLOP/s, 8% of peak.
3. **Why does the pointer-chasing test measure latency while the triad measures bandwidth?** Each chase load depends on the result of the previous one, so only one request is outstanding: time = latency. In the triad all loads are independent, the core keeps ~10-20 requests in flight and the prefetcher streams ahead: time = bytes / bandwidth.
4. **What is a cache line, and why does `for j: for i: a[i][j]` on a row-major array run several times slower than the opposite order?** The line is the transfer unit (64/128 B). Column traversal loads a full line for one element, then evicts it before the neighbours are used once the working set exceeds cache; row traversal uses all 8-16 elements per line.
5. **Give two reasons a compiler refuses to vectorise `for i: s += a[i]*b[i]`.** (a) The reduction on `s` is a loop-carried dependency and reordering the additions changes IEEE results, so it needs `-ffast-math` or an explicit reduction pragma; (b) if `a`, `b` are pointers it must also assume they may alias (irrelevant for a pure reduction but decisive for `c[i] = a[i] + b[i]`).

Code: `src/cpp/cache_bench.cpp` (`chase_ns`, `strided_sum`, `triad_gbs`, `compute_gflops`), `src/sh/build_and_bench.sh` summary table. Sources: [S8] [S16] [S17] [S18] [S34] [S35] [S37].
