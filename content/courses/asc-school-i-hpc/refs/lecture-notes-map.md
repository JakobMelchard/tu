# Lecture → source → note → code

The course is three independent blocks, each a separate ASC training event with
its own registration [S1] [S4]. The tables below are the **published running
order** of the most recent instance of each block, not a guess: block 1 from the
agenda of event 206 [S6], block 2 from events 191 and 275 [S8], block 3 from
event 213 [S13]. The notes are now ordered to match.

Dates in the tables are the last time each block ran. As of 2026-09-28 the ASC calendar has no instance of any of
the three blocks up to its last listed event on 20.04.2027 [S25]. Re-read the
agendas when the next instances are published; see
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

---

## Block 1 — Linux Command Line (1 day, 09:00–16:00, online)

Agenda from the 08.10.2025 instance [S6]; the block last ran on 02.03.2026 [S5]. Lecturers on the
October 2025 instance: Luis Casillas Trujillo, Atul Singh [S6] — not the TISS
lecturer of record. TISS marks this block *"participation is required for Linux
newbies only"* [S2].

Four lecture / exercise / demonstration / break cycles, lunch 12:00–13:00, one
slide deck end to end [S6] [S7].

| deck section [S7] | sources | note | code |
|---|---|---|---|
| terminal & prompt, execution, history, completion, flags, order | S7 | [01](../notes/01-linux-command-line.md) | `src/sh/essentials_demo.sh` |
| filesystem, path, navigation, file operations, I/O redirection | S7 | 01 | `src/sh/essentials_demo.sh` |
| **exercise 1** (login, `man`, `echo`, completion, history search) | S7 | 01 | — |
| transfer: `scp`, `rsync`, FileZilla, WinSCP | S7, S19 | [03](../notes/03-environment.md) | `src/sh/sync_to_cluster.sh` |
| **exercise 2** (setup script, `mkdir`, `rm -r` via `man`, `scp` back) | S7 | 01 | `src/sh/essentials_demo.sh` |
| search: `find`, `grep`, wildcards; ownership & permissions; size & space | S7 | 01 | `src/sh/essentials_demo.sh` |
| pipes, `sed`, `awk`, escapes & quotes, variables, environment variables | S7 | 01, [02](../notes/02-shell-scripting.md), 03 | `src/sh/scripting_patterns.sh` |
| monitoring: `top`, per-core view | S7 | 01 | — |
| **exercise 3** | S7 | 01 | — |
| editors: nano, vim, emacs | S7 | 01 | — |
| scripting: shebang, loops, expansion, if/else, case, functions | S7 | 02 | `src/sh/scripting_patterns.sh` |
| **exercise 4** | S7 | 02 | — |
| documentation; bonus: alias, `.bashrc` | S7 | 03 | `src/sh/env_setup.sh` |
| *(pre-assignment, not a session)* SSH to `vsc5.vsc.ac.at`, jump host `vmos`, JupyterHub, SMS OTP | S6, S19 | 03 | `src/sh/ssh_config.example` |

---

## Block 2 — Introduction to Working on the ASC Clusters (1 day, 09:00–17:00)

Agenda from 15.10.2025 [S8]; last run 23.03.2026 [S5] [S8]. TISS lists it twice a
year, "either October or January" [S2] [S3].

| time [S8] | session | sources | note | code |
|---|---|---|---|---|
| 09:05 | ASC intro & login | S9 (`asc_intro+login.pdf`), S19, S22 | [04](../notes/04-cluster-anatomy.md), [03](../notes/03-environment.md) | `src/sh/ssh_config.example` |
| 10:00 | File storage options | S10 (`file_storage`), S19 | 04 | — |
| 10:15 | Modules | S10 (`modules`), S17, S19 | [05](../notes/05-module-environment.md) | `src/sh/modules_cheatsheet.md` |
| 10:35 | Spack | S9 (`spack.pdf`), S19 | 05 | — |
| 10:40 | EESSI | S9 (`eessi.pdf`), S19 | 05 | — |
| 11:00 | Conda | S9 (`conda.pdf`), S19 | 05 | — |
| 11:35 | **Slurm (basics)** | S9 (`slurm_basics.pdf`), S16, S19 | [06](../notes/06-slurm.md) | `src/sh/slurm/vsc4_serial.sbatch`, `vsc5_serial.sbatch`, `vsc5_mpi.sbatch` |
| 14:00 | **Slurm (advanced)** | S9 (`slurm_advanced.pdf`), S16, S19 | 06 | `src/sh/slurm/vsc5_array.sbatch`, `vsc5_single_node_many_jobs.sbatch`, `vsc5_hybrid.sbatch` |
| 15:00 | GPUs | S9 (`gpus.pdf`), S19, S22 | 04, 06 | `src/sh/slurm/vsc5_gpu.sbatch` |
| — | *Compiling*, *Singularity* — **marked OUTDATED by ASC** and dropped from the running order | S8, S10 | 05 (command shapes only) | — |

---

## Block 3 — Parallelization with MPI (4 mornings)

Last four-morning run 17.–20.11.2025, 09:00–13:30, hybrid (Getreidemarkt 9 or Zoom) [S2]
[S13]. Since 2025 ASC also runs the same material as two 2-day events,
*(Beginner)* and *(Intermediate – Advanced)*, in spring and summer [S5]; the
four-morning winter block is the one TISS schedules for 057.020.

The standard tracked is **MPI 5.0** [S13] [S15]. Labs run in C, Fortran or
Python (mpi4py) on the ASC JupyterHub [S11] [S13].

| day / time [S13] | session | lab [S11] | sources | note | code |
|---|---|---|---|---|---|
| 1 / 09:05 | MPI overview | — | S15 §1, S11 `01_hello` | [07](../notes/07-mpi-concepts.md) | `src/c/hello_mpi.c` |
| 1 / 10:45 | Process model and language bindings | `01_hello` | S15 §2, §11 | 07 | `src/c/hello_mpi.c` |
| 1 / 12:15 | Messages and point-to-point communication | `02_pingpong`, `03_ring` | S15 §3 | [08](../notes/08-point-to-point.md) | `src/c/sendrecv.c`, `deadlock.c` |
| 2 / 09:00 | Ping-pong benchmark — solution and results | `02_pingpong` | S14, S15 §3 | 08, [16](../notes/16-best-practice-and-debugging.md) | `src/c/pingpong.c` |
| 2 / 09:10 | Nonblocking communication | `03_ring` (Irecv/Issend) | S15 §3.7 | 08 | `src/c/nonblocking.c`, `src/exercises/2025w-mpi/ring_variants.c` |
| 2 / 10:45 | Collective communication | `04_allreduce` | S15 §6, S20 | [09](../notes/09-collectives.md) | `src/c/collectives.c`, `pi_reduce.c` |
| 2 / 12:15 | Optimizing MPI communication — a real world example | — | **S14** | 16 | — |
| 2 / 12:30 | Short tour: other MPI topics | — | S15 | 07 (§"what the standard also contains") | — |
| 2 / 13:00 | Fortran and MPI (Fortran participants only) | — | S15 §20 | 07 | — |
| 3 / 09:00 | Groups & communicators | `05_comm-split` | S15 §7 | [10](../notes/10-groups-and-communicators.md) | `src/c/comm_split.c` |
| 3 / 10:15 | Virtual topologies | `06_virtual_cartesian_topologies` | S15 §8 | [11](../notes/11-virtual-topologies.md) | `src/c/cart_topology.c` |
| 3 / 12:15 | Derived datatypes | `07_derived-datatypes` | S15 §5 | [12](../notes/12-derived-datatypes.md) | `src/c/derived_types.c` |
| 4 / 09:00 | One-sided communication | `08_1sided` | S15 §12 | [13](../notes/13-one-sided.md) | `src/c/onesided.c` |
| 4 / 10:45 | Shared memory one-sided communication | `09_1sided-shmem` | S15 §12.2.3, §7.4.2 | [14](../notes/14-shared-memory-one-sided.md) | `src/c/shmem_onesided.c` |
| 4 / 12:15 | Short tour: MPI I/O | — | S15 §14, S14 (`mpi_io_cb.pdf`) | [15](../notes/15-mpi-io.md) | `src/c/mpi_io.c` |
| 4 / 12:45 | Best practice, Summary, Q&A | — | **S14** (`mpi_bp_cb.pdf`) | 16 | `src/c/heat1d_halo.c`, `hybrid_omp_mpi.c` |

### The one exercise that runs through the whole block

Labs 03, 04, 06, 08 and 09 are all the **same ring sum**, re-implemented with
every mechanism the course has just introduced [S11]: each rank starts holding
its own rank number, passes it once around a ring of $P$ processes $P$ times,
and accumulates. The answer is always

$$\texttt{sum} = \sum_{r=0}^{P-1} r = \frac{P(P-1)}{2},$$

independent of the mechanism, which is exactly why it makes a good test.
[`../src/exercises/2025w-mpi/ring_variants.c`](../src/exercises/2025w-mpi/ring_variants.c)
implements it seven ways and checks all seven against that number.

---

## What the notes deliberately do **not** re-derive

Topics that belong to the sibling course 360.242 and are already written up
there with measured numbers [S23]:

| topic | where it is | why not here |
|---|---|---|
| memory hierarchy, cache lines, roofline, measuring GB/s | [NSSC I note 01](../../numerical-simulation-and-scientific-computing-i/notes/01-computer-architectures.md) | this course only sketches a node; its own slide [S9] gives the latency ladder and stops |
| loop order, blocking, compiler flags, benchmarking protocol | [NSSC I note 02](../../numerical-simulation-and-scientific-computing-i/notes/02-serial-optimisation.md) | out of scope for all three blocks |
| OpenMP from the specification, races, false sharing, scheduling | [NSSC I note 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md) | ASC teaches OpenMP as a **separate** training event, not part of 057.020 [S5] |
| Amdahl / Gustafson / Karp–Flatt derivations, strong vs weak scaling | [NSSC I note 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md) | note 16 states Amdahl in the lecturer's own form [S9] and links across |
| git, Make/CMake, sanitizers, lldb | [NSSC I note 10](../../numerical-simulation-and-scientific-computing-i/notes/10-software-engineering-for-scientific-computing.md) | note 16 covers only MPI-specific debugging |

Both courses need the same warning about conventions, so both state it: in the
Amdahl formula used here, **$f$ is the sequential fraction**, following the
lecturer's slide [S9].
