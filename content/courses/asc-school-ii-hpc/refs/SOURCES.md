# Sources: 057.021 ASC-School II Courses in High Performance Computing

Register of every source behind `../notes` and `../src`, cited as `[S<n>]`.
All retrieved 2026-09-28 unless stated. Nothing was logged into: no ASC
account, no cluster, no job, **no TUWEL** (the course has no TUWEL presence). Nothing is
vendored; see [README.md](README.md) for licences and
[fetch-sources.sh](fetch-sources.sh) for the personal-copy download.

**Domain note.** TISS and older event pages link `vsc.ac.at/training`. The apex
`vsc.ac.at` has MX records only and **does not resolve** (checked with `host`
and `curl`, 2026-09-28); `events.vsc.ac.at` and `docs.vsc.ac.at` still redirect.
Use <https://asc.ac.at/training>. The mail address on current pages is
`training@asc.ac.at`; TISS and the 2025 pages say `training@vsc.ac.at`.

## Course-authoritative

**S1** TISS 057.021, 2026S (2028S not published).
[`../docs/tiss.md`](../docs/tiss.md), transcribed 2026-09-28. VU 2.0 h, 1.5
ECTS, blocked, hybrid, immanent, "Attendance Required!"; lecturers Störi,
Blaas-Schenner (E057-09); no TISS registration, write to training@vsc.ac.at
and register per event; grade on request, **at least 3 full training days**;
curriculum entry ALG "for all students" (free elective).

**S2** TISS API record 2026S, `../docs/tiss-api.md`.
Registration type `EXTERNAL`, course URL `https://vsc.ac.at/training`, learning
outcomes, "reviewing the submitted program examples".

**S3** ASC training portal, <https://asc.ac.at/training/>. For 057.021 (still
called "VSC-School II"): students pick training events **except MPI** (that is
School I); **"participation in at least 18 hours"** for the ECTS; contacts Störi
and Blaas-Schenner; register via training@asc.ac.at; students of other Austrian
universities need a TU Wien co-registration. The two thresholds (S1: 3 full
days; S3: 18 h) differ; see `../notes/00-exam-focus.md`.

**S4** ASC/EuroCC Indico, category *Trainings*,
<https://events.asc.ac.at/category/4/>, machine export
`https://events.asc.ac.at/export/categ/4.json?limit=400&from=2020-01-01&to=2027-12-31`
(two calls). The whole catalogue 2023-09 to 2027-04 with dates, entry level,
prerequisites, format, registration text and lecturers. Summarised below.

### S4 catalogue: HPC events eligible for ASC-School II

Days = calendar days of the event; *h* = teaching hours from the published
times (breaks included). Event ids in brackets: `https://events.asc.ac.at/event/<id>/`.

| event | instances (id) | days, h | level | prerequisites | registration |
|---|---|---|---|---|---|
| Hybrid Programming in HPC: MPI+X | 23.-25.01.2024 (117), 21.-23.01.2025 (172), **10.-12.02.2026 (276)** | 2.5 d (2026 times: day 1 from 10:45, day 3 to 13:00); "14 h" content | Advanced | basic MPI and OpenMP "as presented in our ASC or HLRS courses", Linux CLI, Slurm, C/C++ or Fortran | **via the HLRS course page**, not Indico; in person at HLRS Stuttgart or Zoom; labs on the HLRS training cluster |
| Python for HPC | 27.11.-11.12.2023 (109), 13.-17.05.2024 (133), 09.-13.12.2024 (162), **12.+14.+15.05.2025 (185)** | 3 d, 09:00-16:30, a day off between course days | Basic | Python, Linux CLI | Indico form, official e-mail, pre-assignment, temporary VSC account + JupyterHub |
| MPI for Python | 09.-11.09.2024 (146) | 3 x 4 h | Basic | Python, numpy | Indico. MPI: likely School I, see S3 |
| Shared-Memory Parallelization with OpenMP | 04.-05.12.2023 (110), 29.-30.04.2024 (135), 16.-18.09.2024 (150), 03.-04.11.2025 (219), **06.-07.07.2026 (315)** | 2 d (2025/26), 09:30-17:00 | Basic | C/C++ or Fortran, Linux CLI | Indico; Gschwandtner, Blaas-Schenner, Vialov |
| CUDA 4 Dummies | 24.-25.10.2023 (106), 29.-30.10.2024 (154), **22.-23.10.2025 (208)** | 2 d, 09:00-17:00 | Basic | C/C++, Linux CLI | Indico; Höfinger; VSC-5 account |
| N-Ways to GPU Programming Bootcamp | 03.-05.04.2024 (127), 08.-09.04.2025 (179), **14.-15.09.2026 (352)** | 1.5 d | Basic | C/C++ or Fortran | 2026: ASC Indico. CUDA, OpenACC, OpenMP offload, standard-language parallelism, Nsight Systems |
| Multi-GPU Programming Bootcamp | 06.-07.05.2024 (129), 17.-18.06.2025 (187), **29.-30.09.2026 (358)** | 1.5 d | Intermediate | C/C++, CUDA, MPI | 2025: Cyfronet (application, acceptance); 2026: ASC Indico; A100 cluster |
| SYCL and OpenMP Offloading | 12.-13.12.2023 (111) | 2 d | Basic | C/C++ or Fortran | Indico |
| GPU Optimization with Kernel Tuner | 12.-13.09.2024 (143) | 2 x 3 h | Intermediate | Python, GPU programming | Indico |
| Debugging and Optimizing Parallel Codes with Linaro Forge | **30.10.2025 (218)** | 1 d, 10:00-15:00 | Intermediate | Slurm, MPI, one of C/C++/Fortran/Python | Indico; VSC-5 account |
| Extrae and Paraver (BSC) | 27.01.2025 (149) | 1 d | Intermediate | MPI and OpenMP basics | Indico |
| POP3 Profiling and Optimization Tools, 46th VI-HPS Tuning Workshop | 04.-06.09.2024 (145) | 3 d | Intermediate/advanced | MPI/OpenMP, ideally a GPU model | IT4I Ostrava + online; Extrae/Paraver, Score-P/Scalasca/CUBE |
| Profiling AI Software Bootcamp | 10.07.2025 (188) | 5 h | Intermediate | Python, PyTorch distributed | openhackathons.org |
| Modern C++ Software Design (Advanced) | 08.-11.04.2024 (119), 24.-27.03.2025 (166), **02.-05.03.2026 (261)** | 4 d, 09:00-15:30 | Advanced | >= 1 year C++ | Indico; Iglberger |
| Modern C++ Software Design (Intermediate) | 16.-19.10.2023 (104), 07.-10.10.2024 (118), 13.-16.10.2025 (214), **12.-15.10.2026 (273)** | 4 d | Intermediate | >= 1 year C++ | Indico; Iglberger |
| Introduction to Deep Learning | 9 instances 12.2023-11.2026, latest **03.-04.03.2026 (253)**, **23.-24.11.2026 (330)** | 2 d, 09:00-16:00 | Basic | Python, Linux CLI | Indico; Harrison |
| Large Language Models on Supercomputers | 25.-26.09.2024 (136), 04.-05.11.2024 (159) | 2 d | - | - | Indico |

Excluded as School I content [S3]: *Linux Command Line*, *Introduction to
Working on the ASC Clusters*, *Parallelization with MPI* (4 d, or Beginner +
Intermediate-Advanced 2 d each). Also listed, not HPC programming: the many
"Foundations of LLM Mastery", Trustworthy-AI, AI-Act, n8n and management
events, and application workshops (GROMACS, OpenFOAM, NWChem, QUANTUM
ESPRESSO, molecular modelling).

**Common registration procedure** (text of 185, 213, 315, 352): Indico form
from the event's left menu; institutional e-mail to prove affiliation;
automatic "[Indico] Registration" mail; details about a week before; form may
close early when full, waiting list by mail; mobile number for the SMS second
factor of the training account; **registration is binding, no-shows are
blacklisted**; free for academia in EU/EuroHPC countries (EuroCC funding).

**S5** Indico 276, agenda `page/734-agenda-content`. Day 1: MPI + MPI-3.0
shared memory, MPI+OpenMP "how to compile and start", "how to do pinning";
day 2: 2-D stencil case study, overlapping communication and computation,
taskloops; days 2-3: MPI + accelerators. Lecturers Blaas-Schenner (ASC),
Haas (HLRS), Hager (NHR@FAU). Content level 10 % intermediate, 90 % advanced.

**S6** Indico 185 (Python for HPC 2025): description, lecturers Muck,
Harrison, Blaas-Schenner. **S7** its material,
<https://gitlab.tuwien.ac.at/vsc-public/training/python4hpc>, **CC BY-SA 4.0**
(`LICENSE`, README), last activity 2025-05-12. Notebook order: HPC/VSC intro,
modules and Spack, venv, conda, Apptainer, Slurm and Python, debugging,
benchmarking and profiling; built-in and other profilers, single-node
performance, native code, Cython, Numba CPU, Dask; multi-node, mpi4py, Slurm
and MPI, Dask distributed, Numba GPU, cuDF and CuPy.

**S8** Indico 315 agenda (OpenMP, July 2026): hardware, execution model,
worksharing, correctness, Intel Inspector, heat equation, vectorisation with
OpenMP, thread affinity, taskloop.

## ASC user documentation (<https://docs.asc.ac.at/>, no licence file: cited only)

**S12** VSC-4/VSC-5 pages: `running_jobs/gpus.html` (A40/A100 nodes, partition
= QoS, `--gres=gpu:1|2`, more than one node only with both GPUs),
`running_jobs/profiling.html` (Linaro/Arm `perf-report`, `map --profile`,
licences up to 512 tasks), `running_jobs/job_accounting.html` (`sacct`
formats, core-h on service.vsc.ac.at), `running_jobs/monitoring_jobs.html`
(reason codes, `lastjobs`, `ssh` to the node + `htop`),
`storage/where_store_data.html` (GPFS `$HOME`/`$DATA`, `/local`, `/tmp`).

**S13** MUSICA pages: `musica/musica_queues.html` (partitions `zen4_0768`
72 nodes, `zen4_0768_h100x4` 112 nodes with 4x H100, `zen5_2304_b200x8` 28
private nodes; QoS = partition name, 72 h; devel QoS `dev_zen4_0768`,
`dev_zen4_0768_h100x4`, 2 nodes, 10 min), `musica/example_job_scripts.html`
(`--gres=gpu:1..4`, `#ASC --vanilla`, `--threads-per-core=1`, `srun` pins to
the GPU's NUMA domain, `--gpu-bind=none`), `musica/storage.html` (**WekaIO**
all-flash `$SCRATCH`, GPFS `$HOME`/`$DATA`, quotas).

**S14** `musica/node_config.html`: 8 NUMA domains of 24 cores per node; 4
logical cores reserved for WEKA (CPU nodes: on NUMA 7 only, 190 physical cores
for Slurm; GPU nodes: 4 per domain, 176); `nvidia-smi topo -m` shows the H100s
on NUMA 2, 3, 4, 6.

## Specifications and tool documentation (cited, not vendored)

**S9** Slurm, <https://slurm.schedmd.com/>: `sbatch.html`, `srun.html`
(`-c` semantics and the `--threads-per-core` warning), `sacct.html`
(`ConsumedEnergy` "only in the case of an exclusive job allocation"),
`job_array.html`, `gres.html`, `cpu_management.html`, `acct_gather.conf.html`.

**S15** MPI 5.0 standard, vendored in the sibling course:
[`../../../ws2027/asc-school-i-hpc/refs/vendor/mpi-5.0-standard.pdf`](../../asc-school-i-hpc/refs/vendor/mpi-5.0-standard.pdf).
Thread levels (`MPI_Init_thread`), `MPI_File_*`, `MPI_Info` hints.

**S16** OpenMP 5.2, <https://www.openmp.org/spec-html/5.2/openmp.html>:
`OMP_PLACES`, `OMP_PROC_BIND`, `omp_get_place_num`, `simd`, `target`.

**S17** Open MPI 5.0 `mpirun(1)`,
<https://docs.open-mpi.org/en/v5.0.x/man-openmpi/man1/mpirun.1.html>:
`--map-by`, `--bind-to`, `--report-bindings`; hwloc,
<https://hwloc.readthedocs.io/>.

**S18** S. Williams, A. Waterman, D. Patterson, "Roofline: an insightful visual
performance model for multicore architectures", *CACM* 52(4), 65-76, 2009,
DOI 10.1145/1498765.1498785 (ACM blocks scripted fetches: cited by DOI).

**S19** Profiling tools: Linux `perf` wiki <https://perfwiki.github.io/main/>;
Score-P <https://www.vi-hps.org/projects/score-p/>; Scalasca
<https://www.scalasca.org/>; Vampir <https://vampir.eu/>; POP learning
material <https://pop-coe.eu/further-information/learning-material>; LIKWID
<https://github.com/RRZE-HPC/likwid> (GPL-3.0); PAPI <https://icl.utk.edu/papi/>;
Linaro Forge <https://docs.linaroforge.com/latest/html/forge/index.html>.

**S20** GPU: CUDA programming guide
<https://docs.nvidia.com/cuda/cuda-programming-guide/> and best-practices guide
<https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>; OpenACC
<https://www.openacc.org/specification>.

**S21** Python: mpi4py <https://mpi4py.readthedocs.io/en/stable/>, Numba
<https://numba.readthedocs.io/en/stable/>, Dask <https://docs.dask.org/en/stable/>.

**S22** Parallel I/O: HDF5 parallel intro
<https://support.hdfgroup.org/documentation/hdf5/latest/_intro_par_h_d_f5.html>;
Lustre manual <https://doc.lustre.org/lustre_manual.xhtml> (`lfs setstripe`);
NERSC striping guide <https://docs.nersc.gov/performance/io/lustre/>.
**No ASC system runs Lustre** (S12, S13: GPFS and WekaIO); Lustre matters at
other sites (which EuroHPC machine runs what was not checked: unsourced).

**S23** LLVM auto-vectoriser, <https://llvm.org/docs/Vectorizers.html>.

## Local

**S10** The host (measured, not read): Apple M3 Pro, 12 cores, macOS (Darwin
25.6), Apple clang 21.0.0, Open MPI 5.0.11, Homebrew libomp. Every timing in
the notes. Laptop numbers show shapes, not VSC magnitudes.

**S11** This repository: sibling courses
[`asc-school-i-hpc`](../../asc-school-i-hpc/refs/SOURCES.md)
(Linux, Slurm, MPI; its S9 are the ASC-Intro decks, `gpus.pdf`,
`slurm_advanced.pdf`), `numerical-simulation-and-scientific-computing-i`
(roofline, OpenMP), `efficient-programs` (profiling, vectorisation),
`scientific-programming-with-python`,
`computational-science-on-many-core-architectures` and
`advanced-multiprocessor-programming`.

## Not used

TUWEL (none exists for this course). VoWi: the sibling
register records no page for 057.020 or 057.021 (searched 2026-09-22); not
repeated. HLRS hybrid-course slides: HLRS allows personal download only, so
nothing here is written from them. The ASC Indico slide PDFs carry no licence:
cited through the sibling register, fetched only by `fetch-sources.sh`.
