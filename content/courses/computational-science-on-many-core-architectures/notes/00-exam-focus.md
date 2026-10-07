# 00 Exam focus: the practical part, the reports, the oral exam

What is **known** (with source), what is **inferred** (labelled), and what to
check when the 2027W TISS page appears.

## Status, as of 2026-09-28

- **Offered in winter semesters.** Mandatory course, CSE master (066 646), **3rd semester** [S1].
- **The 2027W TISS page is not published.** Everything below is the **2026W** offering, the latest one [S1].
- VU, 2.0 h, 3.0 ECTS, hybrid, English; mode of examination: oral; the page says **"Attendance Required!"** [S1].
- Lecturer: **Karl Rupp**, E360 Institute for Microelectronics [S1].
- 2026W pattern [S1]:
  - new material as **weekly videos** for self-study;
  - a one-hour interactive hybrid **feedback session, Fri 12:00-13:00, EI 4 Reithoffer HS, 09.10.2026-22.01.2027**;
  - **hands-on exercises** between sessions, **short reports** submitted by students, review and discussion of the submissions;
  - **virtual oral exam after a positive evaluation of the practical part; exam registration in TISS**;
  - course registration **21.09.2026 00:00 - 15.10.2026 23:59** (deregistration until the same time), "to participate in the hands-on exercises";
  - "Slides from the lecture will be made available for download."
- Previous knowledge: one programming language, e.g. C or Python [S1].
- **TUWEL**: TISS does not say where slides and exercises are distributed; if it is TUWEL, check access well before the registration window *(inference)*.

## How the grade is formed

Known [S1] [S2]: the practical part (exercises + reports) must be evaluated
**positively**; only then comes a **virtual oral exam**.

Not stated anywhere public [S1] [S2] [S8]: the weighting of reports vs oral
exam, the pass threshold of the practical part, the number of exercises, and
whether the oral grade alone is the course grade. **Unknown; ask in the first
feedback session.**

## What the exercise sheets ask

**No public exercise sheet for 360.252 was found** [S8]. The brief for this
folder assumed that the lecturer publishes slides and exercises on his site or
GitHub; that could not be verified: karlrupp.net and his 18 public GitHub
repositories contain no material for this course, the one student repository
found by search is gone, and the VoWi page is behind a bot wall [S8].

**Inference** from the teaching method ("hands-on exercises", "short
reports") [S1], the subject list [S2] and the lecturer's own tutorial, which
teaches modelling by example (vector add, CG, sparse transpose) [S4]. Likely
exercise shapes, with the code here that rehearses each:

| likely task *(inference)* | topic | rehearse with |
|---|---|---|
| time $x = y + z$ vs $N$ on CPU and GPU, fit $T = \alpha + 24N/\beta$, plot | 2, 3 | `cpp/stream_triad.cpp`, `cuda/vector_add.cu` |
| dot product / sum: shared-memory tree vs atomics vs warp shuffles | 4 | `cpp/reduction_scan.cpp`, `cuda/reduction.cu` |
| prefix sum; use it to build CSR row pointers | 4 | `cpp/reduction_scan.cpp`, `cuda/scan.cu` |
| SpMV and CG on a 2-D Laplacian, measured vs modelled | 3, 4 | `cpp/spmv_csr_ell.cpp`, `py/perf_models.py`, note 03 §4 |
| dense matmul with shared-memory tiles, GFLOP/s vs tile size | 4 | `cpp/matmul_tiling.cpp`, `cuda/tiled_matmul.cu` |
| stencil with halo; strong/weak scaling | 1, 4 | `cpp/stencil_halo.cpp`, `cuda/stencil.cu` |
| same kernel in OpenMP and CUDA, compare effort and speed | 5 | `cpp/*` vs `cuda/*` |
| histogram / atomics contention | 4 | `cpp/atomics_histogram.cpp` |

**Hardware.** CUDA exercises need an NVIDIA GPU. This Mac has none (Apple M3
Pro, no CUDA, no FP64 on its GPU [S36]). Whether the course provides GPU access
is **not stated** [S1]; ask. Every CUDA file here is untested and has a CPU
mirror that is tested (`src/README.md`).

## Report expectations

TISS says only "short reports" [S1]. Our template, built so that each report
already answers the oral-exam questions of notes 01-07:

1. **Machine**: model; peak FP64/FP32 and bandwidth from the data sheet [S29] [S30] [S31], **and** measured STREAM (note 02); ridge point.
2. **Method**: sizes (larger than the last cache for bandwidth), repetitions, best-of or median, timer (CUDA events, `omp_get_wtime`), byte-counting convention [S13].
3. **Result**: one table and one log-log plot ($T$ or GB/s vs $N$; GFLOP/s vs parameter), model curve on the same axes.
4. **Discussion** (3-5 sentences): which bound applies (roofline, $n_{1/2}$), how far from it, why; what one would change next.
5. **Correctness**: how the result was checked (against a serial reference, bitwise where possible, as every `--test` here does).

## The oral exam

Virtual, after the practical part [S1]. *Inference*: expect questions on your
own reports ("explain this plot", "why does the curve flatten here") plus the
seven topics. Each note ends with five questions with answers. The
derivations worth being able to do on a whiteboard:

- Amdahl and Gustafson, and why they are one law (note 01);
- peak FLOP/s from cores x clock x width x 2; arithmetic intensity of triad, dot, SpMV, stencil, tiled matmul (note 02);
- roofline of a given machine, $n_{1/2} = \alpha\beta$, Little's law, Rupp's CG model (note 03);
- occupancy from Table 27 limits, coalescing, bank conflicts ($\gcd(s,32)$), reduction kernels 1 vs 3, Hillis-Steele vs Blelloch work (note 04);
- CUDA vs OpenMP `target teams distribute parallel for` vs OpenACC vs OpenCL/SYCL/HIP names (note 05);
- II and pipeline time $D + (N-1)\mathrm{II}$ (note 06); energy per flop (note 07).

## What to verify when the 2027W page appears

Diff the new page against [`../docs/tiss.md`](../docs/tiss.md) and update it:

- [ ] feedback-session day, time, room, first and last date;
- [ ] registration window (2026W: 21.09-15.10) and whether a cap or priority appears;
- [ ] lecturer(s); teaching method text (videos + weekly session still?);
- [ ] examination modalities: still "virtual oral exam after positive evaluation of the practical part"? any weighting?
- [ ] what "Attendance Required!" means in practice for a video-based course;
- [ ] where slides and exercises are published (TISS download, TUWEL, a public URL);
- [ ] GPU access for the exercises;
- [ ] literature field (still slides only?); previous knowledge;
- [ ] exam dates and their TISS registration windows.

## How to prepare, in order

1. Read the lecturer's 2015 tutorial [S4] (`refs/fetch-sources.sh`, 61 slides).
2. Notes 01-07 with the code; run `make -C src/cpp test bench` and reproduce the numbers.
3. CUDA guide §5, §7, §8.3 [S15]; Harris [S16]; GPU Gems ch. 39 [S18].
4. Before 2027W: get access to an NVIDIA GPU (course-provided if it is; otherwise another machine; *unchecked*: whether the VSC training of 057.020 ASC-School I, same semester folder, includes GPU nodes) and run `make -C src/cuda test`, which has never run.

Sources: [S1]-[S4] [S8] [S13] [S15] [S16] [S18] [S29]-[S31] [S36].
