# 04 GPU architecture: SIMT, thread-block synchronisation, memory hierarchy

TISS topic 4: "Graphics Processing Units (SIMT processing, thread block
synchronization)" [S2]. Normative source: the CUDA C++ Programming Guide,
release 13.4 [S15]; the lecturer's summary is [S4 `gpus.tex`,
`primitives.tex`]. Every algorithm below has a CPU mirror that is tested on
this Mac (`src/cpp`) and a CUDA version that is not (`src/cuda`, no GPU here).

## Execution model

- **Kernel**: a function run by many threads; launched over a **grid** of **thread blocks** [S15 §5.1-5.2]. Up to 1024 threads per block [S15 Table 27]. Built-ins `threadIdx`, `blockIdx`, `blockDim`, `gridDim` [S4 `cuda.tex`].
- **SM (streaming multiprocessor)**: a block runs on one SM from start to end; many blocks per SM if resources allow.
- **Warp**: 32 consecutive threads of a block, the unit of scheduling [S15 §7.1]. Blocks are split into $\lceil T/32 \rceil$ warps [S15 §7.2]. AMD CDNA: 64-thread wavefronts, RDNA: 32 [S26].
- **SIMT**: one instruction is issued for all *active* threads of a warp. Threads may branch differently; the warp then executes each path with the non-participating threads disabled: **divergence** costs the sum of the paths [S15 §7.1]. Since Volta each thread has its own program counter (independent thread scheduling), so "warp-synchronous" code without explicit sync is wrong [S15 §7.1].
- **SIMT vs SIMD**: same hardware idea (lock-step lanes, [S7]), different contract. SIMD exposes the vector width to the program; SIMT lets you write scalar per-thread code and pays for divergence at run time.
- **Latency hiding by multithreading**: every resident warp keeps its registers on chip, so switching warps costs nothing; each cycle the scheduler issues from any warp that is ready [S15 §7.2]. A stalled warp (waiting ~hundreds of ns for DRAM) is simply not picked.

## Occupancy

Resident warps per SM / maximum resident warps. The limits per SM (cc 9.0,
Hopper [S15 Table 27]): 64 warps (2048 threads), 32 blocks, 65 536 32-bit
registers, 228 KB shared memory; at most 255 registers per thread. Blocks per SM
$= \min$ over the four limits (`perf_models.py::occupancy`, simplified: no
allocation granularity):

| threads/block | regs/thread | smem/block | blocks/SM | occupancy | limiter |
|---|---|---|---|---|---|
| 256 | 32 | 0 | 8 | 100 % | warps |
| 256 | 64 | 0 | 4 | 50 % | registers: $65536/(64\cdot256)$ |
| 256 | 32 | 48 KB | 4 | 50 % | shared memory: $\lfloor 228/48 \rfloor$ |
| 1024 | 64 | 0 | 1 | 50 % | registers |
| 32 | 16 | 0 | 32 | 50 % | blocks |

Occupancy is a means (Little's law, note 03), not the goal: Volkov gets higher
bandwidth at lower occupancy with more independent loads per thread [S38].

## Thread-block synchronisation

- `__syncthreads()`: barrier for all threads of **one block**, and makes their shared/global writes visible to each other [S15 §10.6]. There is no barrier across blocks inside a kernel (blocks may not even be co-resident); a grid-wide sync is a **kernel boundary** (or cooperative groups).
- Every thread of the block must reach the same `__syncthreads()`. A barrier inside a divergent branch, or an early `return` before it, is undefined behaviour (hang or garbage). `src/cuda/tiled_matmul.cu` and `stencil.cu` therefore guard the *work*, not the barrier.
- Warp-level: `__shfl_down_sync(mask, v, off)` exchanges registers inside a warp without shared memory [S15 §10.22] (`reduction.cu::reduce_shfl_atomic`).
- CPU analogue: one OpenMP `barrier` per tree level (`reduce_thread_tree`), 1-10 us each [S4], against a hardware barrier inside one SM for `__syncthreads` *(unsourced: tens of cycles)*.

## Memory hierarchy

| level | scope | size (cc 9.0 [S15 Table 27]) | notes |
|---|---|---|---|
| registers | thread | 64 K x 32 bit per SM, $\le 255$/thread | spill to "local memory" (in DRAM) when exceeded |
| shared memory | block | $\le 228$ KB per SM, $\le 227$ KB per block | software-managed, 32 banks [S15] |
| L1 / texture | SM | shares the array with shared memory | |
| L2 | device | (unsourced: ~50 MB on H100) | all SMs, atomics resolve here |
| global (HBM) | device + host copies | 80 GB, 3.35 TB/s (H100 [S29]) | 32/64/128-B transactions [S15 §8.3.2] |
| constant | device, read-only | 64 KB, 8 KB cache per SM | broadcast when all threads read one address |

### Coalescing

A warp's loads are combined into naturally aligned 32-, 64- or 128-byte
transactions [S15 §8.3.2]. 32 threads x 8 B consecutive = 256 B = 2 x 128 B:
100 % efficiency. The guide's worst case: one 32-byte transaction per thread
for a 4-byte word, "throughput is divided by 8" [S15 §8.3.2]. Rules: thread $i$
touches element $i$; structure of arrays, not array of structures [S4
`cuda.tex`]; pad 2-D rows to a multiple of the warp size [S15 §8.3.2].
The same layout that coalesces on a GPU can be pathological on a CPU (ELL,
note 03, 12x).

### Bank conflicts

Shared memory: 32 banks, successive 32-bit words in successive banks, 32 bits
per bank per cycle [S15]. Word address $w$ lives in bank $w \bmod 32$. If a
warp's 32 threads read words $w_t = s\,t$ (stride $s$), the number of threads
hitting one bank is $\gcd(s, 32)$: stride 1 is conflict-free, stride 2 is 2-way,
stride 32 is 32-way (fully serialised). Same address = broadcast, no conflict.
Fixes: pad `s[T][T+1]` so a column walk has stride $T+1$, odd
(`tiled_matmul.cu::Bs`); in the Blelloch scan, index $i \mapsto i + \lfloor i/32 \rfloor$
[S18] (`scan.cu::PAD`). Harris's reduction kernel 3 reads `s[t + stride]`:
consecutive threads, consecutive words, no conflict [S16].

### Atomics

An atomic RMW by several threads of a warp to one address is serialised, order
undefined [S15 §7.1]. `atomicAdd(double*)` exists from cc 6.0 [S15 §10.14].
Pattern: **privatise, then merge** (per-block histogram in shared memory, one
global atomic per bin). CPU mirror, `atomics_histogram --bench`, $2^{25}$
values, 12 threads (2026-09-28):

| bins, data | shared bins + `omp atomic` | private + atomic merge | serial |
|---|---|---|---|
| 1 | 23.8 ns/value | 0.23 | 1.54 |
| 16, uniform | 33.6 | 0.07 | 0.44 |
| 256, 90 % in bin 0 | 32.5 | 0.21 | 1.89 |
| 65 536, uniform | 3.1 | 0.15 | 0.74 |

100-500x. Contention is the cost: more bins, fewer collisions, cheaper atomics.

## Reductions [S16] [S4 `primitives.tex`]

Tree in shared memory, $\log_2 B$ levels, a barrier between levels; then a
second launch over the block sums (kernel boundary = global sync).

- Kernel 1 (interleaved): `if (t % (2*stride) == 0)`; active threads are scattered over all warps: divergence in every warp at every level.
- Kernel 3 (sequential addressing): `if (t < stride) s[t] += s[t+stride]`; whole warps drop out, no divergence until stride < 32, no bank conflicts [S16].
- Shuffle + one `atomicAdd` per warp: no shared memory at all.

Work $n - 1$ adds, depth $\log_2 n$. Measured (`reduction_scan --bench`,
$2^{25}$ doubles, second run): serial loop 10.4 GB/s (latency-bound chain),
OpenMP `reduction` 88.9 GB/s, thread tree with barriers 83.8, block tree
(kernel 3 mirror, 2 passes) 91.3 GB/s: all near STREAM, as a memory-bound
kernel should be.

**Accuracy bonus.** Summing $2^{24}$ copies of `0.1f`: running sum 1 935 089,
exact 1 677 721.6, block tree 1 677 721.6 (`--test`). A tree's rounding error
grows like $\log_2 n$, a running sum's like $n$.

## Scans (prefix sums)

Exclusive: $y_i = \sum_{k<i} x_k$. Rupp's example: 4 3 6 5 4 7 4 4 4 gives
inclusive 4 7 13 18 22 29 33 37 41 [S4]; used for sparse-matrix setup (row
pointers, $T = 2(4+8)\,\text{nnz}/B$ transpose) and stream compaction.

| algorithm | adds | depth | notes |
|---|---|---|---|
| serial | $n-1$ | $n$ | |
| Hillis-Steele [S19] | $n\log_2 n - (n-1)$ | $\log_2 n$ | Rupp's slide kernel; double buffer |
| Blelloch [S17] [S18] | $2(n-1)$ | $2\log_2 n$ | up-sweep = reduction tree, down-sweep pushes prefixes; work-efficient |
| three-phase (chunk, scan sums, add) | $\approx 2n$ | $n/p + p$ | how multi-block scans are built |

`--test` asserts 45 057 and 8 190 adds at $n = 4096$. Measured ($2^{24}$
int64): `std::inclusive_scan` 4.76 ms, three-phase 6.63, Blelloch 27.1,
Hillis-Steele 64.4 ms. On a CPU with 12 threads the serial scan wins: it is
memory-bound and each parallel variant moves the data between 2 and $\log_2 n$ times. On a GPU
the serial option does not exist; the block-level Blelloch plus recursive block
sums (`scan.cu::scan_device`) is the standard answer.

## Tiling (dense matmul)

Naive: one thread per $C_{ij}$, $2n$ loads per $2n$ flops, $I = 1/8$ without
caches. Tiled: each block stages $T\times T$ tiles of $A$ and $B$ in shared
memory, `__syncthreads()`, $T$ FMAs per staged value, `__syncthreads()`;
global traffic $2n^3/T$ doubles, $I = T/8$ (note 02). CPU mirror,
`matmul_tiling --bench`, $n = 1536$: naive 6.55, $T = 8$: 88.6, 16: 118.8,
**32: 160.9**, 64: 116.4 GFLOP/s (24x). $T = 64$ loses, probably because $3 \cdot 32$ KB
of tile buffers crowd the 128 KB L1d *(our reading, not measured with counters)*.

## Stencils and halos

Staging a $T_B\times T_B$ tile needs $(T_B+2)^2$ loads: overhead 1.13 at
$T_B = 32$, 1.27 at $T_B = 16$. On the CPU the explicit staging is *slower*
(`stencil_halo --bench`, $n = 4094$: naive 6446 MLUP/s, staged $T_B = 32$ 3674):
three 32 KB rows already fit L1, the hardware cache does the staging for free.
On a GPU the shared-memory tile is what turns 5 global loads per point into
~1.3. Strip decomposition with an explicit halo exchange: 6574 MLUP/s, bitwise
equal to the global sweep (`--test`).

## Pitfalls

- `__syncthreads()` in divergent code or after an early `return`.
- Assuming warp-synchronous execution without `__syncwarp`/shuffles (Volta+ [S15 §7.1]).
- Array of structures in global memory; row-major access with `threadIdx.x` walking the slow index.
- Stride-32 shared-memory access (32-way conflict).
- Chasing 100 % occupancy while the kernel is limited by something else [S38].
- Float atomics: result order undefined, so not bitwise reproducible.

## Oral-exam questions

1. **What is SIMT, and what does a branch cost?** One instruction for all active threads of a 32-thread warp; divergent paths execute one after another with lanes masked; cost = sum of both paths [S15 §7.1].
2. **Why is `__syncthreads()` limited to a block, and how do you synchronise the whole grid?** Blocks run independently and need not be co-resident; grid-wide sync = end the kernel and launch the next (or cooperative launch).
3. **Compute the occupancy of a 256-thread block using 64 registers per thread on cc 9.0.** $65536/(64\cdot256) = 4$ blocks = 32 warps of 64 = 50 %.
4. **Explain coalescing and bank conflicts; give one fix for each.** Coalescing: a warp's global accesses merge into 32/64/128-B transactions; fix: SoA, thread $i \to$ element $i$. Bank conflicts: 32 banks x 4 B; stride $s$ gives $\gcd(s,32)$-way; fix: pad to odd stride.
5. **Why is Hillis-Steele used at all when Blelloch is work-efficient?** Half the depth and one sweep; inside a warp or a small block the extra work is free and the fewer barriers win; for large $n$ Blelloch (or three-phase) wins.

Code: `src/cpp/reduction_scan.cpp`, `matmul_tiling.cpp`, `stencil_halo.cpp`, `spmv_csr_ell.cpp`, `atomics_histogram.cpp` (tested); `src/cuda/reduction.cu`, `scan.cu`, `tiled_matmul.cu`, `stencil.cu` (untested here); `src/py/perf_models.py::occupancy`. Sources: [S4] [S7] [S15]-[S20] [S26] [S29] [S38].
