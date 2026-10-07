# Notes: 057.020 ASC-School I HPC

One file per session of the three blocks, **in the published running order of
each block** — block 1 from the Indico agenda of the 08.10.2025 instance [S6],
block 2 from the 23.03.2026 instance [S8], block 3 from the 17.–20.11.2025
instance [S13]. Each note gives definitions and commands or code, a worked
example, pitfalls, self-check questions with answers, and pointers into
[`../src`](../src/README.md).

Every claim carries an `[S<n>]` citation into
[`../refs/SOURCES.md`](../refs/SOURCES.md); claims that could not be sourced are
marked `(unsourced: …)` in place. Changes are recorded in
`CHANGELOG.md`. The session-by-session map from lecture to
source to note to code is [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

**Read [00](00-exam-focus.md) first.** There is no exam: the assessment is
attendance plus submitted program examples [S1], so the questions in these notes
are ours, not reconstructions of past papers — there are none.

**Literature.** TISS names none and states *"No lecture notes are available."*
[S1]. What exists instead is public and specific: the lecturers' own slide
sources on GitLab under CC BY-SA ([S7], [S10] — vendored in
`../refs/vendor/`), the ASC slide PDFs on Indico [S9] [S14],
the ASC user documentation [S19], the course's own MPI hands-on repository
[S11], and the **MPI 5.0 standard** [S15], which the course links as its
reference document and which is vendored here. The block-3 lectures are given
from Rabenseifner's HLRS deck [S12], which may not be redistributed, so nothing
here is written from it; the MPI semantics come from the standard instead.

| # | note | one line |
|---|---|---|
| 00 | [What is assessed](00-exam-focus.md) | no exam, no past papers; how registration works; offered in winter semesters, and what ASC has on its calendar as of 2026-09-28 |

**Block 1 — Linux command line** (1 day, online) [S6]

| # | note | one line |
|---|---|---|
| 01 | [Linux command line](01-linux-command-line.md) | the primer's running order: filesystem, the core commands, pipes and redirection, permissions, find/grep/sed/awk, editors, archives |
| 02 | [Shell scripting](02-shell-scripting.md) | shebang, loops, expansion, if/else, case, functions — then strict mode, arrays, traps, `getopts` for the scripts around a job |
| 03 | [Environment](03-environment.md) | logging in to ASC (2FA, IP ranges, login-node limits), environment variables, PATH, dotfiles, SSH, `scp`/`rsync`, tmux |

**Block 2 — Introduction to working on the ASC clusters** (1 day) [S8]

| # | note | one line |
|---|---|---|
| 04 | [Cluster anatomy](04-cluster-anatomy.md) | VSC-4/VSC-5/MUSICA by the numbers, login vs compute nodes, NUMA, the latency ladder, storage tiers and quotas, GPUs, fair share |
| 05 | [The module environment](05-module-environment.md) | **Environment Modules, not Lmod**; Spack-generated names; compilers and MPI wrappers on ASC; Spack, EESSI, conda |
| 06 | [Slurm](06-slurm.md) | `--qos` **and** `--partition`; the ASC job templates; arrays, dependencies, pinning; backfill and the 72 h limit; checking that a job succeeded |

**Block 3 — Parallelization with MPI** (4 mornings) [S13]

| # | note | day | one line |
|---|---|---|---|
| 07 | [MPI concepts, process model, bindings](07-mpi-concepts.md) | 1 | standard vs implementation, MPI 5.0, SPMD, ranks, communicators, C/Fortran/mpi4py, MPI vs OpenMP vs hybrid |
| 08 | [Point-to-point](08-point-to-point.md) | 1–2 | Send/Recv, blocking semantics and buffering, deadlocks and fixes, non-blocking and overlap, ping-pong, the ring |
| 09 | [Collectives](09-collectives.md) | 2 | the catalogue, `v` variants, `MPI_IN_PLACE`, and a cost model rebuilt from the primary source |
| 10 | [Groups and communicators](10-groups-and-communicators.md) | 3 | contexts, `MPI_Comm_split`, `split_type(SHARED)`, groups, inter-communicators |
| 11 | [Virtual topologies](11-virtual-topologies.md) | 3 | `Cart_create`/`shift`/`sub`, `MPI_PROC_NULL` at boundaries, graph topologies, neighbourhood collectives |
| 12 | [Derived datatypes](12-derived-datatypes.md) | 3 | size vs extent, vector/indexed/subarray/struct, `create_resized`, when to pack instead |
| 13 | [One-sided communication](13-one-sided.md) | 4 | windows, Put/Get/Accumulate, fence / PSCW / lock, the memory model |
| 14 | [Shared-memory one-sided](14-shared-memory-one-sided.md) | 4 | `Win_allocate_shared`, MPI+MPI, one copy of a table per node |
| 15 | [MPI I/O](15-mpi-io.md) | 4 | file views, the 18-cell access table, collective two-phase I/O, the non-fatal error default |
| 16 | [Patterns, performance, best practice, debugging](16-best-practice-and-debugging.md) | 2 + 4 | domain decomposition, scaling with the convention stated, the lecturer's measured 22× optimisation, debugging MPI |

## The one number that ties block 3 together

Labs `03_ring`, `04_allreduce`, `06_virtual_cartesian_topologies`, `08_1sided`
and `09_1sided-shmem` are the same ring sum written with five different
mechanisms [S11]. Whatever the mechanism, every rank must end with

$$\sum_{r=0}^{P-1} r = \frac{P(P-1)}{2}$$

(6 for $P=4$, 28 for $P=8$). Seven implementations, all asserting it, are in
[`../src/exercises/2025w-mpi/ring_variants.c`](../src/exercises/2025w-mpi/ring_variants.c).

## Not here, on purpose

The memory hierarchy and roofline, serial optimisation, OpenMP from the
specification, the Amdahl/Gustafson/Karp–Flatt derivations and the
git/CMake/sanitizer toolchain are written up with measured numbers in the
sibling course 360.242 [S23] and are linked rather than repeated; see the table
at the end of [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).
