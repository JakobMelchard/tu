# Map: catalogue event -> note -> code

ASC-School II has no fixed syllabus: you choose events from the ASC catalogue
[S3] [S4]. This table maps each eligible event family to the note that prepares
for it and the code that goes with it. "Covered elsewhere" points to courses in
this repository that cover the topic already, so the note only adds the cluster
angle.

| event family [S4] | typical slot | note | code | covered elsewhere |
|---|---|---|---|---|
| Hybrid Programming in HPC: MPI+X [S5] | Jan/Feb, HLRS + online | [01 hybrid](../notes/01-hybrid-mpi-openmp.md) | `src/c/hybrid_pi.c`, `src/c/affinity_report.c`, `src/sh/slurm_templates/hybrid.sbatch` | MPI: ASC-School I notes 07-16; OpenMP: NSSC I note 07 |
| Linaro Forge; Extrae/Paraver; POP/VI-HPS tuning workshop; Profiling AI bootcamp | irregular | [02 profiling](../notes/02-performance-analysis.md) | `src/c/simd_dot.c` as a target | Efficient Programs note 02 (perf, measurement) |
| Shared-Memory Parallelization with OpenMP (vectorisation, affinity parts) [S8] | Nov or Jul | [03 vectorisation](../notes/03-vectorisation-node-level.md) | `src/c/simd_dot.c` | NSSC I notes 01-02, 07; Efficient Programs notes 04, 06 |
| CUDA 4 Dummies; N-Ways GPU; Multi-GPU; SYCL/OpenMP offload | Oct; Apr or Sep; May-Sep | [04 GPU](../notes/04-gpu-on-vsc.md) | `src/sh/slurm_templates/gpu.sbatch` | Many-Core Architectures |
| Python for HPC [S6] [S7]; MPI for Python | May or Dec; Sep 2024 | [05 Python](../notes/05-python-for-hpc.md) | `src/py/README.md` (mpi4py not installed) | Scientific Programming with Python notes 07-10 |
| MPI-IO tour (School I, day 4); no separate I/O event in 2023-2027 | - | [06 parallel I/O](../notes/06-parallel-io.md) | `src/c/mpi_io_write_read.c` | ASC-School I note 15 |
| Slurm (advanced) in the ASC intro; no separate efficiency event | - | [07 job efficiency](../notes/07-job-efficiency-and-energy.md) | `src/sh/slurm_templates/array.sbatch`, `src/sh/test_slurm_templates.sh` | ASC-School I note 06 |
| Modern C++ Software Design; Introduction to Deep Learning | Mar/Oct; several a year | not written up: eligible, but language/ML courses, see [00](../notes/00-exam-focus.md) | - | Advanced Programming with C++; Applied/Deep Learning courses |

## What ASC-School I already covers (link, do not repeat)

[`../../../ws2027/asc-school-i-hpc/notes/README.md`](../../asc-school-i-hpc/notes/README.md):
Linux command line (01-03), cluster anatomy, modules, Slurm (04-06), MPI from
concepts to one-sided, shared-memory windows and MPI I/O (07-16). Its
`src/c/hybrid_omp_mpi.c` is the minimal hybrid program; `src/c/hybrid_pi.c`
here adds the thread-level check, decomposition invariance and the timing split.
