# 02 FLOPs, bandwidth and latency

TISS topic 2 [S2]. Three numbers describe a processor for scientific codes:
how fast it computes, how fast it moves data, and how long one access takes.
Rupp's thesis, stated on the data he maintains: "FLOPs ... are for free"; the
problem is memory [S6]. The single-core version on this Mac (cache levels,
pointer chasing, one-core roofline) is NSSC I note 01 [S40]; this note compares
machines. Code: `src/cpp/stream_triad.cpp`.

## Definitions

- **FLOP**: one floating-point add or multiply; an FMA counts 2. **FLOP/s**: rate.
- **Peak** $P = n_\text{cores}\cdot f\cdot(\text{flop/cycle/core})$, flop/cycle $= n_\text{FMA units}\cdot w_\text{SIMD}\cdot 2$.
- **Bandwidth** $B$ [B/s]: sustained transfer rate between two levels (here DRAM/HBM to chip).
- **Latency** $\lambda$ [s]: time from issuing one request to its completion.
- **Throughput** vs latency: bandwidth needs many requests in flight; latency is paid once per *dependent* request (Little's law, note 03).
- **Arithmetic intensity** $I = W/Q$: flops per byte of DRAM traffic [S11].
- **Machine balance** $I^* = P/B$: the intensity at which both limits are equal.

A kernel with work $W$ and traffic $Q$ needs at least
$$T \;\ge\; \max\!\left(\frac{W}{P},\; \frac{Q}{B}\right) \quad\Longrightarrow\quad \text{memory-bound iff } I < I^*.$$

## Peak numbers (FP64)

| machine | $P$ [GFLOP/s] | $B$ [GB/s] | $I^*$ [flop/B] | TDP [W] | source |
|---|---|---|---|---|---|
| Xeon Platinum 8180 (2017, 28 cores, 2.5 GHz) | 2 240 | 120 | 18.7 | 205 | [S5] |
| Tesla V100 (2017, 80 SMs) | 7 800 | 900 | 8.7 | 300 | [S5] |
| H100 SXM, vector / tensor | 34 000 / 67 000 | 3 350 | 10.1 / 20.0 | 700 | [S29] |
| MI300X, vector / matrix | 81 700 / 163 400 | 5 300 | 15.4 / 30.8 | 750 | [S30] |
| **this Mac**, M3 Pro CPU (6P + 6E) | $\ge$ 161 measured | 150 spec, **121 measured** | $\approx$ 1.3 measured | - | [S31] [S32] |
| this Mac, M3 Pro GPU (18 cores) | no FP64 | shares the 150 | - | - | [S36] |

Derivations and remarks:

- Xeon 8180: $2240/(28 \cdot 2.5) = 32$ flop/cycle/core = 2 FMA units x 8 doubles (512-bit) x 2. That is Rupp's "tens of FLOPs per cycle" per CPU core, against hundreds per GPU multiprocessor [S7].
- V100: $7800/80 \approx 98$ GFLOP/s per SM, i.e. $\approx 67$ flop/cycle/SM at the listed 1455 MHz [S5].
- The Mac: Apple publishes no FP64 peak; 161 GFLOP/s is our best tiled matmul (`matmul_tiling --bench`, $T = 32$, 12 threads), a **lower bound**. *(unsourced: 4 FP64 FMA pipes x 2 lanes at ~4 GHz per P-core would give ~64 GFLOP/s per P-core, ~390 for the P-cluster.)* The GPU cannot do FP64 through Metal at all: "Metal does not support the double ... data types" [S36].
- Balance grows over time: V100 $I^* = 8.7$ vs K20 (2012) $1173/208 = 5.6$ [S5] (`test_machine_balance_grew_over_time`). Every generation, more kernels fall left of the ridge.

## Bandwidth, measured

`./bin/stream_triad --bench`, $N = 2^{25}$ doubles (268 MB per array), best of 10,
STREAM byte convention [S13] (2026-09-28, load average 6-10 [S32]):

| threads | copy | scale | add | triad [GB/s] |
|---|---|---|---|---|
| 1 | 91.4 | 92.0 | 106.1 | 104.9 |
| 2 | 121.5 | 123.5 | 117.1 | 117.7 |
| 6 | 122.1 | 122.8 | 119.0 | **121.4** |
| 12 | 120.4 | 120.4 | 119.4 | 118.0 |

- 121 GB/s = 81 % of the 150 GB/s spec [S31]. A later run at load 3-5 gave 109.8 GB/s on 1 thread and 123.6 GB/s best (82 %); treat the numbers as $\pm 5$ %. One thread already reaches 86 %: an M3 P-core keeps enough misses in flight to nearly saturate the memory system, unlike a server socket where one core gets a small fraction.
- **No write-allocate penalty visible.** STREAM counts 24 B per triad element; a write-allocate cache would move 32 B. At 32 B the triad would be 162 GB/s, above the 150 GB/s spec. Same for Jacobi: 103 GB/s at 16 B/LUP matches triad, 155 GB/s at 24 B/LUP would exceed spec (`stencil_halo --bench`). So full-line streaming stores on this chip are not read first. *(Inference from our numbers; Apple documents nothing here.)*
- Caches: $x = y + z$ with 6.3 MB of traffic ($N = 2^{18}$, fits the 16 MB L2) runs at 221-444 GB/s depending on OpenMP wait policy, 2-4x DRAM.

## Latency, stated and measured

| event | latency | source |
|---|---|---|
| DRAM load (dependent) | ~100 ns; measured 87-109 ns on this Mac | [S4] [S40] |
| barrier, lock | ~1-10 us | [S4] |
| OpenMP empty `parallel for`, 12 threads | **19 us** default (`OMP_WAIT_POLICY=PASSIVE` in this libomp), **1.4 us** with `OMP_WAIT_POLICY=active` | [S32] |
| CUDA kernel launch, PCIe transfer | ~10 us | [S4] |
| InfiniBand / Ethernet message | ~5 / ~20 us | [S4] |

Scale: at ~4 GHz *(unsourced clock)*, 100 ns is 400 cycles, time for
$400 \times 32 = 12\,800$ flops on one Xeon-8180-class core. A latency is a
bandwidth-shaped hole: 10 us of launch latency at 3.35 TB/s is 33.5 MB not
moved (note 03, $n_{1/2}$).

## Memory-bound vs compute-bound, worked

Kernel intensities (compulsory DRAM traffic, FP64):

| kernel | flops | bytes | $I$ | bound on every machine above? |
|---|---|---|---|---|
| triad $a = b + s c$ | 2 | 24 | 0.083 | memory |
| dot product $x\cdot y$ | 2 | 16 | 0.125 | memory |
| SpMV CSR (val + col) | 2/nnz | 12/nnz | 0.17 | memory |
| 5-point Jacobi | 4/LUP | 16/LUP | 0.25 | memory |
| tiled matmul, tile $T$ | $2n^3$ | $16n^3/T$ | $T/8$ | needs $T > 8I^*$: compute-bound on this Mac at $T = 32$ ($4 > 1.3$), memory-bound on every GPU and the Xeon ($T = 32$ gives 4, V100 needs $T > 70$); hence register tiling on top of shared-memory tiling |
| DGEMM $n = 4096$, $3n^2$ moved | $2n^3$ | $24n^2$ | 341 | compute |

Triad on H100: $I \cdot B = 0.083 \times 3350 = 279$ GFLOP/s, **0.8 %** of the
FP64 vector peak. On this Mac: 10.1 GFLOP/s measured, the same 0.083 x 121.
The speedup of a memory-bound kernel from Mac CPU to H100 is the bandwidth
ratio, $3350/121 = 28$, not the FLOP ratio.

## Measuring correctly

- Count flops and compulsory bytes analytically; state the convention (STREAM counts requested bytes [S13]).
- Arrays $\ge$ 4x the last cache level [S13]; here 268 MB against 16 MB L2.
- First-touch initialisation with the same `schedule(static)` as the kernel.
- Best of $k$ repetitions, after a warm-up; monotonic clock (`common.hpp::time_min`); on a GPU, CUDA events (`src/cuda/common.cuh::time_ms`).
- Print the load average (`mc::print_load`): numbers here were taken with other jobs running.

## Pitfalls

- Comparing peak FLOP/s across machines for a memory-bound code.
- Tensor-core or matrix peaks quoted for FP64 vector code (H100: 67 vs 34 TFLOP/s [S29]); low-precision tensor numbers "with sparsity" [S29].
- Mixing up GB (10^9) and GiB (2^30).
- Timing an OpenMP region that is shorter than its own fork/join cost (19 us here).
- Believing a data-sheet bandwidth is attainable: 81 % here; GPUs reach a similar fraction *(unsourced)*.

## Oral-exam questions

1. **Define arithmetic intensity and machine balance. Is a dot product on a V100 memory- or compute-bound?**
   $I = 2/16 = 0.125 < I^* = 8.7$: memory-bound, at most $0.125 \times 900 = 113$ GFLOP/s.
2. **Compute the FP64 peak of a 28-core CPU at 2.5 GHz with two 512-bit FMA units per core.**
   $28 \times 2.5\,\text{GHz} \times 2 \times 8 \times 2 = 2240$ GFLOP/s [S5].
3. **What is the difference between latency and bandwidth, and why do GPUs trade one for the other?**
   Latency = time per dependent access; bandwidth = rate with many accesses in flight. GPUs accept long latency and hide it with thousands of resident threads (note 04).
4. **Your SpMV reaches 100 GB/s on a machine with 120 GB/s STREAM. Is it worth optimising the arithmetic?**
   No: $I \approx 0.17$, 83 % of STREAM; only reducing bytes (index compression, mixed precision, blocking for $x$ reuse) helps.
5. **Why can a memory-bound kernel get only ~10x faster on a GPU than on a CPU socket?**
   Speedup = bandwidth ratio, which Rupp's data put at ~10x per socket [S6]; H100 vs this Mac 28x, vs a DDR5 server socket less.

Code: `src/cpp/stream_triad.cpp` (`copy`, `scale`, `add`, `triad`, `empty_region_s`), `src/cuda/vector_add.cu`, `src/py/roofline.py` (`machines`, `KERNELS`). Sources: [S4]-[S7] [S11] [S13] [S29]-[S32] [S36] [S40].
