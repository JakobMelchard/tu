# Notes: 057.021 ASC-School II Courses in High Performance Computing

**Course facts** (2026S transcription; 2028S not published) [S1] [S3]:
VU 2.0 h, 1.5 ECTS, blocked, online or hybrid, English, "Attendance
Required!". Lecturers Herbert Störi, Claudia Blaas-Schenner (E057-09, ASC
Research Center). **No TISS registration**: register per event at
<https://asc.ac.at/training> (TISS still links `vsc.ac.at/training`, which no
longer resolves) and mail `training@asc.ac.at`. Grade on request after **at
least 3 full training days** (ASC portal: 18 hours) and review of the submitted
program examples. Curriculum: ALG "for all students", i.e. a free elective.

## How ASC-School I and II split the catalogue

Both courses are credit wrappers around the same ASC/EuroCC training calendar
[S4]. School I (057.020, [`asc-school-i-hpc`](../../asc-school-i-hpc/notes/README.md))
is a fixed set: Linux command line, introduction to the ASC clusters,
Parallelization with MPI. School II is **free choice from everything else**,
MPI events excluded [S3]: hybrid programming, OpenMP, GPU courses, Python for
HPC, profiling and debugging tools, C++ and deep-learning courses, application
workshops. This folder is the smaller "advanced modules" half: it prepares the
HPC events School I does not touch and links School I for Linux, Slurm and MPI.

| # | note | one line |
|---|---|---|
| 00 | [How the grade is formed; which three days](00-exam-focus.md) | no exam; 3 full days / 18 h; Plan A *Python for HPC*, Plan B *Hybrid* + *Multi-GPU*; what to verify in early 2028 |
| 01 | [Hybrid MPI + OpenMP](01-hybrid-mpi-openmp.md) | thread levels, mapping and binding, one rank per NUMA domain on MUSICA, Open MPI's binding defaults, overlap |
| 02 | [Performance analysis and profiling](02-performance-analysis.md) | sampling vs instrumentation, counters, POP efficiencies, perf / Forge / Score-P / Scalasca / Vampir / LIKWID / PAPI |
| 03 | [Vectorisation and node-level optimisation](03-vectorisation-node-level.md) | measured: chain-breaking 4.3x, SIMD 8.5x in L1, the memory roof from DRAM; `-march`, cache blocking, node roofline |
| 04 | [GPU programming on the ASC systems](04-gpu-on-vsc.md) | CUDA vs OpenACC vs OpenMP offload, A100/A40/H100 partitions, `--gres`, one rank per GPU |
| 05 | [Python for HPC](05-python-for-hpc.md) | measured: numpy 30x over the loop; Numba, mpi4py buffer vs pickle, Dask; environments and BLAS threads |
| 06 | [Parallel I/O](06-parallel-io.md) | ASC storage tiers (GPFS, WekaIO, no Lustre), collective MPI-IO verified, hints ignored by Open MPI, HDF5, striping |
| 07 | [Job efficiency, scaling, energy](07-job-efficiency-and-energy.md) | `sacct` fields, CPU efficiency, Karp-Flatt, energy $\propto 1/E(p)$, array jobs |

Every claim carries `[S<n>]` into [`../refs/SOURCES.md`](../refs/SOURCES.md);
what could not be sourced says "unsourced". Timings are from the laptop [S10]
and show shapes, not cluster magnitudes. Changes: CHANGELOG.md.
Map from catalogue events to notes and code:
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

Not here on purpose: Linux, modules, Slurm basics and all of MPI (School I
notes 01-16), OpenMP and the roofline derivation (NSSC I notes 01, 02, 07),
serial profiling and vectorisation basics (Efficient Programs notes 02, 04,
06), CUDA in depth (Many-Core Architectures).
