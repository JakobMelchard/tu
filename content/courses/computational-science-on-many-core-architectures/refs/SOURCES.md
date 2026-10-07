# Sources - 360.252 Computational Science on Many-Core Architectures

Register of every source behind [`../notes`](../notes/README.md) and
[`../src`](../src/README.md). Notes cite `[S<n>]`. Retrieval date is the day the
page or file was fetched and checked (all 2026-09-28 unless stated). Licence
column decides vendoring: **vendor** = committed under `vendor/`,
**fetch** = downloaded by [`fetch-sources.sh`](fetch-sources.sh) into the
git-ignored `cite-only/`, **cite** = DOI or URL only.

**Headline finding (S8).** The brief for this folder assumed that the lecturer,
Karl Rupp, publishes the slides and exercises of *this* course publicly. That
could **not** be verified. His site and GitHub account carry no 360.252 or "GPU
Computing" course material; what they do carry is a 2015 VSC tutorial whose
outline is this course's syllabus almost item by item (S4), and two CC BY 4.0
hardware data sets (S5, S39). TISS promises the slides as a download for
registered students (S1). No TUWEL material was used: TUWEL needs a login.

---

## Course-authoritative

### S1 - TISS course page, 2026W (latest offering; 2027W not published)
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=360252&semester=2026W>
- Transcribed 2026-09-28 in a logged-in browser: [`../docs/tiss.md`](../docs/tiss.md). Offerings 2020W-2026W exist; **2027W is not published**.
- Used for: VU 2.0 h, 3.0 ECTS, hybrid, English, oral exam; "Attendance Required!"; mandatory CSE 3rd semester (066 646, only curriculum entry); the seven-item subject list that fixes the note order; teaching methods (weekly videos, one-hour interactive hybrid lecture, hands-on exercises, short reports, review and discussion); lecturer Rupp, E360; Fri 12:00-13:00 EI 4 Reithoffer HS, 09.10.2026-22.01.2027, "Lecture Feedback Session"; registration 21.09.2026 00:00-15.10.2026 23:59 (deregistration same end); "Virtual oral exam after positive evaluation of the practical part. Registration in TISS."; "Slides from the lecture will be made available for download."; previous knowledge: one programming language (C or Python).
- Licence: public page, facts only. **cite**

### S2 - TISS API record, 2026W
- `../docs/tiss-api.md`, rendered from `https://tiss.tuwien.ac.at/api/course/360252-2026W`.
- Used for: the learning outcome (use modern parallel processors efficiently, strengths and weaknesses; run larger problems in less time) and the subject list, which spells the first topic "Ahmdal's Law" *(sic)*. **cite**


## The lecturer's public material

### S4 - Rupp, *Modern Many-Core Architectures for Supercomputing*, VSC School Seminar, Vienna, 2015-12-11
- PDF (61 pages) and LaTeX sources: <https://github.com/karlrupp/slides/tree/master/VSC2015>; listed on <https://www.karlrupp.net/publications/tutorials/> as tutorial [8].
- Licence: the `slides` repository has **no licence file** (GitHub API: no licence detected) = all rights reserved. **fetch** (PDF + the seven `slides/*.tex`).
- Used for, with slide-source file: bottlenecks (`bottlenecks.tex`: AI "larger than 1-10" = FLOP-limited; latencies Ethernet ~20 us, InfiniBand ~5 us, PCIe/kernel launch ~10 us, barriers/locks ~1-10 us, memory ~100 ns; $T = T_\text{serial} + T_\text{parallel}/p$); GPU overview (`gpus.tex`: workgroups of 32-64 hardware threads, shared memory ~32-64 KB, 32/64/128-byte memory transactions, PCIe v2 8 GB/s, v3 16 GB/s, ~10 us latency, ">> 10-fold speedups (usually) not backed by hardware"); CUDA (`cuda.tex`: `threadIdx/blockDim/blockIdx/gridDim`, block size 256 or 512, "at least 10 000 logical threads", AoS vs SoA); reduction and scan kernels and the scan example 4 3 6 5 4 7 4 4 4 (`primitives.tex`); performance models for vector addition $T \approx 3 \cdot 8 N / B + \text{latency}$, CG $T(N) = 8\cdot10^{-6} + 2\cdot2\cdot10^{-6} + 20 \cdot 8 N / B$, pipelined CG, sparse transpose $T = 2 (4+8)\,\text{nnz}/B$ (`modeling-examples.tex`); Xeon Phi (`mics.tex`: KNC 320 GB/s ideal, 160 real, 1 TFLOP/s FP64).

### S5 - Rupp, `cpu-gpu-mic-comparison` data repository
- <https://github.com/karlrupp/cpu-gpu-mic-comparison>, commit `af3575960820`; supplements S6.
- Licence: **CC BY 4.0** (`LICENSE.txt`). **vendor**: `vendor/rupp-cpu-gpu-mic-comparison/`, 7 files, 28 KB, unmodified.
- Used for: FP64 peak, bandwidth and TDP of Xeon Platinum 8180 (2017: 2240 GFLOP/s, 120 GB/s/socket, 205 W), Tesla V100 (7800 GFLOP/s, 900 GB/s, 300 W), Tesla K20 (1173, 208), the growth of machine balance over time; parsed by `src/py/roofline.py`.

### S6 - Rupp, *CPU, GPU and MIC Hardware Characteristics over Time* (blog, 2013-06, last updated 2016-08-18)
- <https://www.karlrupp.net/2013/06/cpu-gpu-and-mic-hardware-characteristics-over-time/>. **cite**
- Used for: GPU/MIC bandwidth ~10x one CPU socket; FLOP/byte ratios high on all architectures; his conclusion that the problem for future hardware "is memory, not FLOPs"; speedups of much more than an order of magnitude over a comparable CPU are not backed by hardware.

### S7 - Rupp, *FLOPs per Cycle for CPUs, GPUs and Xeon Phis* (blog, 2016-08-19)
- <https://www.karlrupp.net/2016/08/flops-per-cycle-for-cpus-gpus-and-xeon-phis/>. **cite**
- Used for: architectures converge; tens of FLOPs/cycle per CPU core vs hundreds per GPU multiprocessor, from lock-step execution of warps.

### S8 - Search record: what the lecturer does and does not publish (2026-09-28)
- karlrupp.net: Research, Publications (incl. Tutorials), Software, Blog; `/teaching/` and `/lectures/` return 404. GitHub `karlrupp`: 18 public repositories (API listing), none a course. Web searches for the course number with "Rupp", "slides", "exercise", "CUDA": only TISS pages and one student repository `tellocam/CSMCA` ("3ECTS VU TU Wien") that now returns 404. VoWi page "Computational Science on Many-Core Architectures VU (Weinbub)" exists (an earlier lecturer) but is behind a bot wall (Anubis) and was not read.
- Consequence: **no public exercise sheet or report template for 360.252 exists that we could find**; note 00 says so.

### S39 - Rupp, `microprocessor-trend-data`
- <https://github.com/karlrupp/microprocessor-trend-data>, CC BY 4.0 (`LICENSE.txt`). **cite** (clone if wanted).
- Used for: the frequency plateau since the mid-2000s and the rise of core counts (note 07).

## Performance models

| # | source | licence | used for |
|---|---|---|---|
| S9 | G. M. Amdahl, *Validity of the single processor approach to achieving large scale computing capabilities*, AFIPS SJCC 1967, doi:10.1145/1465482.1465560 | paywalled, **cite** | Amdahl's law (note 01) |
| S10 | J. L. Gustafson, *Reevaluating Amdahl's Law*, CACM 31(5), 1988, doi:10.1145/42411.42415; author copy <http://www.johngustafson.net/pubs/pub13/amdahl.pdf> | **fetch** | scaled speedup $N + (1-N)s'$; 1024-processor speedups 1021, 1020, 1016 at $s$ = 0.4-0.8 % (note 01) |
| S11 | S. Williams, A. Waterman, D. Patterson, *Roofline*, CACM 52(4):65-76, 2009, doi:10.1145/1498765.1498785; tech report UCB/EECS-2008-134 | CACM paywalled; TR **fetch** | roofline, ridge point, ceilings, AI per DRAM byte (note 03) |
| S12 | J. D. C. Little, *A proof for the queuing formula L = lambda W*, Oper. Res. 9(3):383-387, 1961, doi:10.1287/opre.9.3.383 | **cite** | Little's law (notes 02, 03) |
| S13 | J. D. McCalpin, STREAM benchmark, <https://www.cs.virginia.edu/stream/> (and *Memory bandwidth and machine balance*, IEEE TCCA Newsletter 1995) | **cite** | copy/scale/add/triad, byte-counting convention (note 02) |
| S14 | R. W. Hockney, *The communication challenge for MPP: Intel Paragon and Meiko CS-2*, Parallel Computing 20(3):389-398, 1994, doi:10.1016/S0167-8191(06)80021-9 | **cite** | $T = \alpha + n/\beta$, $n_{1/2} = \alpha\beta$ (note 03) |
| S37 | Y. Shi, *Reevaluating Amdahl's Law and Gustafson's Law*, Temple University, 1996 (copy at uni-bremen.de, see script) | **fetch** | the two laws are one law in two normalisations (note 01) |

## GPU architecture and algorithms

| # | source | licence | used for |
|---|---|---|---|
| S15 | NVIDIA, *CUDA C++ Programming Guide*, Release 13.4, 2026-09-15, 598 pp., <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> | NVIDIA documentation, **fetch** | §5.1-5.3 kernels, thread and memory hierarchy; §6.2.8 streams; §7.1 SIMT (warp = 32, divergence, independent thread scheduling since Volta, serialised atomics); §7.2 hardware multithreading (zero-cost warp switch, registers and shared memory partitioned, warps per block $\lceil T/32 \rceil$); §8.3.2 device memory accesses (32/64/128-B aligned transactions, "throughput is divided by 8" example); shared memory 32 banks of 32-bit words; §10.6 synchronisation, §10.14 atomics, §10.22 warp shuffles; Table 27 (cc 7.5-12.0: 1024 threads/block, 64 K registers/SM, 255 registers/thread, 16-32 resident blocks, 32-64 resident warps, 64-228 KB shared memory per SM) |
| S16 | M. Harris, *Optimizing Parallel Reduction in CUDA*, NVIDIA, 2007 | **fetch** | interleaved vs sequential addressing, divergence, bank conflicts (note 04) |
| S17 | G. E. Blelloch, *Prefix Sums and Their Applications*, CMU-CS-90-190, 1990 (author copy) | **fetch** | work-efficient up-sweep/down-sweep scan, $2(n-1)$ adds (note 04) |
| S18 | M. Harris, S. Sengupta, J. D. Owens, *Parallel Prefix Sum (Scan) with CUDA*, GPU Gems 3, ch. 39, 2007 | free online, **fetch** | block scan, bank-conflict padding `n >> LOG_NUM_BANKS`, multi-block scan (note 04) |
| S19 | W. D. Hillis, G. L. Steele, *Data parallel algorithms*, CACM 29(12):1170-1183, 1986, doi:10.1145/7902.7903 | **cite** | step-efficient scan, $n\log_2 n$ work (note 04) |
| S20 | M. Kreutzer, G. Hager, G. Wellein, H. Fehske, A. R. Bishop, *A unified sparse matrix data format for efficient general sparse matrix-vector multiplication on modern processors with wide SIMD units*, SIAM J. Sci. Comput. 36(5):C401-C423, 2014, doi:10.1137/130930352; arXiv:1307.6209 | arXiv non-exclusive licence, **fetch** | SELL-C-$\sigma$, fill efficiency $\beta$ (note 04) |
| S21 | N. Bell, M. Garland, *Implementing sparse matrix-vector multiplication on throughput-oriented processors*, SC09, doi:10.1145/1654059.1654078 | **cite** | ELL, HYB, CSR-vector on GPUs (note 04) |
| S38 | V. Volkov, *Better Performance at Lower Occupancy*, GTC 2010 | **fetch** | ILP instead of occupancy; occupancy is not the goal (note 04) |

## Programming models

| # | source | licence | used for |
|---|---|---|---|
| S22 | OpenMP ARB, *OpenMP API Specification 5.2*, 2021 | ARB copy permission; **vendored once**, in [`../../../ws2026/numerical-simulation-and-scientific-computing-i/refs/vendor/`](../../numerical-simulation-and-scientific-computing-i/refs/vendor/openmp-api-specification-5.2.pdf) | `target`, `teams`, `distribute`, `map`, `declare target` (note 05); basics are in NSSC I note 07 |
| S23 | OpenACC-Standard.org, *The OpenACC API*, v3.3, Nov 2022 | "no part of this document may be reproduced ... without the express written permission"; **fetch** | `parallel`, `kernels`, `loop gang/worker/vector`, data clauses (note 05) |
| S24 | Khronos, *The OpenCL Specification*, 3.0 unified | Khronos grants use and reproduction of the unmodified spec, no distribution grant; **fetch** | platform/context/queue/kernel model, work-items and work-groups (note 05) |
| S25 | Khronos, *SYCL 2020 Specification*, revision 12 | as S24; **fetch** | queues, buffers/accessors vs USM, `nd_range`, single-source C++ (note 05) |
| S26 | AMD, *HIP documentation*, <https://rocm.docs.amd.com/projects/HIP/en/latest/>, page *Hardware implementation* (`understand/hardware_implementation.html`) | live docs, **cite** | CUDA-like API, `hipify`; "warps, each containing 32 (RDNA) or 64 (CDNA) threads"; LDS of 32 banks x 4 B on CDNA 1-3 (notes 04, 05) |

## FPGAs

| # | source | licence | used for |
|---|---|---|---|
| S27 | R. Kastner, J. Matai, S. Neuendorffer, *Parallel Programming for FPGAs*, 2018, arXiv:1805.03648, <https://github.com/KastnerRG/pp4fpgas> | **CC BY 4.0** (repo and arXiv); redistributable, fetched (8 MB) not committed | LUTs, FFs, DSPs, BRAM; HLS; pipelining, II, unrolling, array partitioning (note 06) |
| S28 | AMD, *Vitis High-Level Synthesis User Guide* (UG1399), live at <https://docs.amd.com/r/en-US/ug1399-vitis-hls>; PDF v2022.2 (2022-10-19) at <https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_2/ug1399-vitis-hls.pdf>, read for the pragma syntax | vendor docs, **cite** | `#pragma HLS pipeline II=1`, `#pragma HLS unroll`, `#pragma HLS array_partition variable=... type=block\|cyclic factor=...` (note 06) |

## Hardware data and other

| # | source | licence | used for |
|---|---|---|---|
| S29 | NVIDIA, H100 product page, specifications table, <https://www.nvidia.com/en-us/data-center/h100/> | **cite** | H100 SXM: FP64 34 TFLOP/s, FP64 tensor 67, FP32 67, FP16 tensor 1979 (with sparsity), 80 GB, 3.35 TB/s, up to 700 W |
| S30 | AMD, *Instinct MI300X* data sheet (PDF) | **fetch** | 304 CUs; FP64 vector 81.7, FP64 matrix 163.4, FP32 vector 163.4 TFLOP/s; 192 GB HBM3, 5.3 TB/s; 256 MB Infinity Cache; 750 W TBP; PCIe Gen 5 x16 128 GB/s |
| S31 | Apple, *MacBook Pro (16-inch, Nov 2023) - Tech Specs*, <https://support.apple.com/en-us/117737> | **cite** | M3 Pro: 12-core CPU (6P + 6E), 18-core GPU, 16-core Neural Engine, **150 GB/s** memory bandwidth |
| S32 | The host machine, measured | - | `Mac15,7`, Apple M3 Pro, 36 GB, `hw.ncpu = 12` (6 + 6), `hw.cachelinesize = 128`, L1d 128 KB and L2 16 MB per P-cluster (`sysctl`); 18 GPU cores (`system_profiler`); Apple clang 21.0.0, Homebrew libomp; all measured numbers in the notes come from `src/cpp --bench` on 2026-09-28 (see `../notes/CHANGELOG.md` for the load average at the time) |
| S33 | J. L. Hennessy, D. A. Patterson, *Computer Architecture: A Quantitative Approach*, 6th ed., Morgan Kaufmann, 2017 | commercial, **cite** | ch. 4 (vector, SIMD, GPU), ch. 7 (domain-specific architectures, TPU) |
| S34 | M. Horowitz, *Computing's energy problem (and what we can do about it)*, ISSCC 2014, pp. 10-14, doi:10.1109/ISSCC.2014.6757323 | **cite** | energy of an operation vs of moving its operands (note 07) |
| S35 | Cerebras, *Chip* page (WSE-3), <https://www.cerebras.ai/chip> | **cite** | 900 000 cores, 4 trillion transistors, 46 225 mm$^2$, "250 petaflops" (AI precision) |
| S36 | Apple, *Metal Shading Language Specification*, version 4.1 | **fetch** | "Metal does not support the double ... data types": no FP64 on the Apple GPU through Metal (note 07) |
| S40 | This repo, NSSC I study folder, [`../../../ws2026/numerical-simulation-and-scientific-computing-i/notes/`](../../numerical-simulation-and-scientific-computing-i/notes/README.md) | ours | cross-links: note 01 (memory hierarchy, pointer-chase latency 87-109 ns on this Mac), 02 (serial optimisation, blocking), 07 (OpenMP basics, races, false sharing, Amdahl/Gustafson/Karp-Flatt) |


## Unsourced statements

Marked `(unsourced: ...)` in place. The main ones: Apple's CPU clock and FP64
pipe count (so no official FP64 peak for the M3 Pro CPU), Apple GPU FP32 peak,
GPU DRAM latency (~400-800 ns order of magnitude), SM counts of specific GPUs,
FPGA clock ranges and energy figures.
