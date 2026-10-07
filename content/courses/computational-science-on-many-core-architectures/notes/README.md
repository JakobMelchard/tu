# 360.252 Computational Science on Many-Core Architectures - notes

Preparation material for a course **offered in winter semesters** (mandatory, CSE 3rd
semester). The 2027W TISS page is **not published**; all course facts are from
the 2026W offering [S1]. One note per TISS topic, in the order of the TISS
subject list [S2]. Each note: definitions and formulas, a worked example with
real numbers (data sheets [S5] [S29] [S30] [S31], or measured on this Mac
[S32]), pitfalls, five oral-exam questions with answers, pointers into
[`../src`](../src/README.md). Reader: physics master's level; no calculus or
linear-algebra refreshers, computer-science terms defined.

**Course logistics, 2026W pattern** (details in [00](00-exam-focus.md)):
weekly videos + Fri 12:00-13:00 feedback session, EI 4 Reithoffer HS,
09.10.2026-22.01.2027; hands-on exercises with short reports; virtual oral exam
after a positive practical part, exam registration in TISS; course registration
21.09-15.10.2026; "Attendance Required!"; slides downloadable; lecturer Karl
Rupp (E360) [S1].

**Sources.** Every claim carries `[S<n>]` into
[`../refs/SOURCES.md`](../refs/SOURCES.md); what could not be sourced is marked
*(unsourced: ...)* in place. The lecturer publishes **no** course material
that we could find [S8]; his 2015 VSC tutorial [S4] covers the syllabus and is
used throughout. The OpenMP basics are not repeated here: see NSSC I notes 01,
02, 07 in [`../../../ws2026/numerical-simulation-and-scientific-computing-i/notes/`](../../numerical-simulation-and-scientific-computing-i/notes/README.md)
[S40].

| # | note | one line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | status, what is known about the practical part and the oral exam, likely exercise shapes (inferred), report template, what to verify for 2027W |
| 01 | [Amdahl and scaling](01-amdahl-and-scaling.md) | Amdahl, offload form, Gustafson (1988 numbers reproduced), Shi's equivalence, Karp-Flatt on a bandwidth-bound measurement, strong vs weak scaling |
| 02 | [FLOPs, bandwidth, latency](02-flops-bandwidth-latency.md) | peak FP64 of Xeon 8180, V100, H100, MI300X and this Mac; STREAM measured (121 GB/s of 150); latencies; memory- vs compute-bound |
| 03 | [Performance modelling](03-performance-modelling.md) | roofline of five machines, alpha-beta and $n_{1/2}$ (measured), Little's law, Rupp's CG model worked, SpMV formats where the model fails 12x |
| 04 | [GPU architecture](04-gpu-architecture.md) | SIMT, warps, divergence, occupancy from Table 27, `__syncthreads`, memory hierarchy, coalescing, bank conflicts, atomics, reductions, scans, tiling |
| 05 | [Programming models](05-programming-models.md) | $x = y + z$ in CUDA, OpenMP `target`, OpenACC, OpenCL, SYCL, HIP; concept map; streams; choosing |
| 06 | [FPGAs](06-fpgas.md) | LUTs, FFs, DSPs, BRAM; pipelining and II; HLS pragmas; the accumulation dependency; when FPGAs win |
| 07 | [Emerging many-core](07-emerging-many-core.md) | frequency plateau, Xeon Phi lesson, unified-memory SoCs, matrix engines, wafer-scale dataflow, energy per flop |

Figure: [`img/roofline.png`](img/roofline.png), from `src/py/roofline.py --png`.

Changes: `CHANGELOG.md`.
