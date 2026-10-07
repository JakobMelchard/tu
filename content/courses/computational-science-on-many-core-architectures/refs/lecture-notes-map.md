# Topic map - what the course says it covers, and where we cover it

No lecture script is public ([S8]), so the structural index is the **TISS
"Subject of course" list** [S1] [S2]: seven items, one note each, in TISS
order. The lecturer's 2015 tutorial [S4] is the closest public text; the right
column says which of its slide files covers the topic.

| # | TISS topic [S2] | our note | primary sources | [S4] slide file | our code |
|---|---|---|---|---|---|
| 1 | Ahmdal's *(sic)* Law | [01](../notes/01-amdahl-and-scaling.md) | [S9] [S10] [S37] | `bottlenecks.tex` | `py/perf_models.py` (`amdahl`, `gustafson`, `karp_flatt`, `offload_speedup`) |
| 2 | FLOPs, Bandwidth, and Latency | [02](../notes/02-flops-bandwidth-latency.md) | [S13] [S5] [S6] [S7] [S29]-[S32] | `bottlenecks.tex`, `gpus.tex` | `cpp/stream_triad.cpp` |
| 3 | Performance Modeling | [03](../notes/03-performance-modelling.md) | [S11] [S12] [S14] [S4] | `modeling-examples.tex` | `py/roofline.py`, `py/perf_models.py`, `cpp/stream_triad.cpp` (alpha-beta), `cpp/spmv_csr_ell.cpp` |
| 4 | Graphics Processing Units (SIMT processing, thread block synchronization) | [04](../notes/04-gpu-architecture.md) | [S15] [S16]-[S21] [S38] | `gpus.tex`, `primitives.tex` | `cpp/reduction_scan.cpp`, `cpp/matmul_tiling.cpp`, `cpp/stencil_halo.cpp`, `cpp/spmv_csr_ell.cpp`, `cpp/atomics_histogram.cpp`; `cuda/*.cu` |
| 5 | Programming Models (Annotation-driven such as OpenMP, native such as CUDA) | [05](../notes/05-programming-models.md) | [S15] [S22]-[S26] | `cuda.tex`, `opencl.tex` | `cuda/vector_add.cu` (streams), every `cpp/*.cpp` (OpenMP) |
| 6 | Field Programmable Gate Arrays | [06](../notes/06-fpgas.md) | [S27] [S28] [S33] | none | - (no FPGA toolchain here) |
| 7 | Emerging Many-Core Architectures | [07](../notes/07-emerging-many-core.md) | [S29]-[S36] [S39] | `mics.tex` (Xeon Phi, the 2015 "emerging" architecture) | `py/perf_models.py` (`pj_per_flop`) |

Plus [00-exam-focus.md](../notes/00-exam-focus.md), about the practical part
and the oral exam.

## What the 2015 tutorial [S4] has that TISS does not name

- **Parallel primitives** (reduction, scan, sparse triangular solves by level
  scheduling) - folded into note 04, because they are the canonical
  "thread-block synchronisation" examples.
- **OpenCL** - folded into note 05's portability section.
- **Worked performance models of real kernels** (vector add, CG, pipelined CG,
  sparse transpose) - note 03 reproduces them with numbers.

## What TISS names that [S4] does not cover

- **FPGAs** (topic 6): no slide in [S4]. Note 06 rests on [S27] (CC BY 4.0
  textbook) and [S28] (AMD HLS guide).
- **Amdahl as a law** (topic 1): [S4] states only the time split
  $T = T_s + T_p/p$; note 01 adds Gustafson, Shi, Karp-Flatt, strong/weak scaling.

## Cross-links, not duplicates

The OpenMP basics (fork-join, data-sharing, `reduction`, `schedule`, races,
atomics vs critical, false sharing) are in NSSC I note 07 [S40]; the memory
hierarchy, pointer-chasing latency and a single-core roofline on this same Mac
are in NSSC I note 01; loop order and cache blocking in NSSC I note 02. Notes
here start where those stop: offload, many-core GPUs, performance models with
several machines.
