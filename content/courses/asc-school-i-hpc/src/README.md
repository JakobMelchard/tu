# Reference implementations: ASC-School I HPC

Four directories: `sh/` for blocks 1–2 (shell, environment, ASC job templates),
`c/` for block 3 (MPI in C), `py/` for the cost models the notes quote, and
`exercises/` for the course's own hands-on labs.

## Run everything

```bash
make -C c test                       # builds every MPI program (and the exercise)
                                     # and runs each with mpirun --oversubscribe -np 4
python -m pytest py -q                    # the cost models (run from src/, repo venv)
for f in sh/*.sh sh/slurm/*.sbatch; do bash -n "$f"; done    # syntax-check every script
bash sh/essentials_demo.sh           # block 1 commands in a temp dir
bash sh/scripting_patterns.sh -v -n you -r 2 /etc/hosts      # bash constructs, getopts, traps
bash sh/env_setup.sh                 # prints a .bashrc block, modifies nothing
bash sh/sync_to_cluster.sh           # rsync dry run; without a configured `vsc5` ssh alias it prints the command and exits 0
```

Requirements: Open MPI (`mpicc`, `mpirun`; Homebrew on macOS, `module load
openmpi/<full-spack-name>` on the cluster), a C compiler, and for
`hybrid_omp_mpi` OpenMP (Homebrew `libomp` on macOS; the Makefile picks the
flags by `uname`). Without MPI `make -C c test` prints SKIP and builds nothing;
without libomp it skips only `hybrid_omp_mpi`. Python: the repo venv (root `pyproject.toml`). bash 3.2 is enough for the demos;
bash 4 features are guarded.

On a cluster, inside a Slurm job: `make test MPIRUN=srun MPIRUN_FLAGS=`.

## c/ — block 3, MPI

`make` builds, `make test` runs each program with `mpirun --oversubscribe -np 4`,
`make clean` removes binaries. **Every program checks its own result against a
closed form and exits non-zero on failure** — no program prints numbers you have
to eyeball.

| Program | What | Note |
|---|---|---|
| `hello_mpi.c` | init/finalize, rank/size, processor name, ordered output via a token | [07](../notes/07-mpi-concepts.md) |
| `sendrecv.c` | Send/Recv, status and `MPI_Get_count`, wildcards, tag matching order, `Sendrecv(_replace)` ring, `Probe` for unknown length | [08](../notes/08-point-to-point.md) |
| `deadlock.c` | ring exchange: `--unsafe recv-first` (always hangs), `--unsafe send-first` (hangs above the eager limit), and the fixes ordered / `Sendrecv` / non-blocking / `Bsend`, timed; an `alarm()` turns the hang into exit code 3 | [08](../notes/08-point-to-point.md) |
| `pingpong.c` | one-way latency and bandwidth vs message size, $n_{1/2}$ | [08](../notes/08-point-to-point.md), [16](../notes/16-best-practice-and-debugging.md) |
| `nonblocking.c` | `Irecv/Isend/Waitall` both-ways ring, overlap of a 32 MB exchange with computation (timed vs blocking), `Test` polling, `Waitany` in arrival order | [08](../notes/08-point-to-point.md) |
| `collectives.c` | Bcast, Scatter/Gather, Scatterv/Gatherv, Allgather, Reduce/Allreduce/Scan, MAXLOC, Alltoall, `MPI_Type_vector` column, Bcast vs P−1 sends timing | [09](../notes/09-collectives.md) |
| **`comm_split.c`** | `MPI_Comm_split` into halves with both reductions checked in closed form, `Comm_group`/`Group_incl`/`Comm_create`, `Group_translate_ranks`, `Comm_split_type(SHARED)` | [10](../notes/10-groups-and-communicators.md) |
| **`cart_topology.c`** | `Dims_create` (product and ordering asserted), the ring on a 1D periodic Cartesian communicator, `Cart_shift` source/destination order, `MPI_PROC_NULL` at a non-periodic edge, `Cart_coords`/`Cart_rank` round trip, `Cart_sub` row communicators | [11](../notes/11-virtual-topologies.md) |
| **`derived_types.c`** | **measures** `MPI_Type_size` (32 B) and the extent (104 B) of a matrix column and asserts both against the hand derivation; `create_resized` so `count>1` works; a `struct` built with `MPI_Get_address`; a halo face with `create_subarray` | [12](../notes/12-derived-datatypes.md) |
| **`onesided.c`** | the ring with `MPI_Put` + `Win_fence` (and the real fence assertions), `MPI_Get` of the whole distributed vector, `MPI_Accumulate` for concurrent updates, passive target `Win_lock` + `Fetch_and_op` as a distributed ticket counter | [13](../notes/13-one-sided.md) |
| **`shmem_onesided.c`** | `Comm_split_type(SHARED)`, `Win_allocate_shared`, the ring with a **plain store** instead of `MPI_Put`, `Win_shared_query` rather than assuming contiguity, one read-only table per node, and the node-leader communicator | [14](../notes/14-shared-memory-one-sided.md) |
| **`mpi_io.c`** | collective `write_at_all`/`read_at_all` into one shared file, the same layout via a file **view**, an interleaved view built from a derived type, and a demonstration that file errors are **non-fatal** by default | [15](../notes/15-mpi-io.md) |
| `pi_reduce.c` | midpoint rule for $\int_0^1 4/(1+x^2)$, block decomposition, `MPI_Reduce`, speedup vs serial on rank 0 | [09](../notes/09-collectives.md) |
| `heat1d_halo.c` | 1D heat equation (FTCS), block decomposition, halo exchange with `Sendrecv` and `MPI_PROC_NULL`, `Gatherv`, bitwise check against the serial solver and error vs the exact solution; `-N`, `-T` | [16](../notes/16-best-practice-and-debugging.md) |
| `hybrid_omp_mpi.c` | `MPI_Init_thread(FUNNELED)`, OpenMP reduction inside each rank, `Allreduce` across ranks; `OMP_NUM_THREADS=2 mpirun -np 4` | [07](../notes/07-mpi-concepts.md) |

OpenMP flags on macOS (Apple clang): `-Xpreprocessor -fopenmp
-I/opt/homebrew/opt/libomp/include` and `-L/opt/homebrew/opt/libomp/lib -lomp`;
on Linux/GCC `-fopenmp`. The Makefile switches on `uname -s`.

## exercises/ — the course's own labs

[`exercises/2025w-mpi/`](exercises/2025w-mpi/README.md) describes, in our own
words, what each of the nine block-3 hands-on labs asks, and points at our
solution for each. Nothing from the official repository is copied here; see
[`../refs/README.md`](../refs/README.md) for why.

| File | What |
|---|---|
| `2025w-mpi/README.md` | the nine labs, what each asks, and the one invariant they all share |
| `2025w-mpi/ring_variants.c` | the course's ring sum in **seven** mechanisms, each asserting $P(P-1)/2$; run it with an odd `-np` too |

## py/ — the cost models

Run with the repo venv from `src/`: `python -m pytest py -q`.

| File | What |
|---|---|
| `mpi_cost.py` | the point-to-point model $\alpha + n\beta$ and $n_{1/2}$; the eleven collective algorithms of Thakur, Rabenseifner & Gropp (2005) with a bisection `crossover()`; Amdahl in the lecturer's **sequential-fraction** convention. `python3 mpi_cost.py` prints the tables the notes quote. |
| `test_mpi_cost.py` | 28 tests. They check each formula against its closed form, reproduce the published VSC-3 ping-pong latency ladder as a monotonicity statement, and pin the correction this module exists for: a short-message `Allreduce` costs $\lg p\,\alpha$, not $2\lg p\,\alpha$. |

## sh/ — blocks 1 and 2

| File | What | Note |
|---|---|---|
| `essentials_demo.sh` | creates a temp dir and exercises the ~25 core commands, pipes, redirection, permissions, find/grep/sed/awk, tar/gzip, processes | [01](../notes/01-linux-command-line.md) |
| `scripting_patterns.sh` | strict mode, quoting, arithmetic, conditionals, loops, arrays, functions, exit codes, EXIT/ERR traps, here-docs, `getopts` | [02](../notes/02-shell-scripting.md) |
| `env_setup.sh` | prints safe `.bashrc` additions (PATH, history, prompt, Slurm aliases, functions); never edits a file | [03](../notes/03-environment.md) |
| `ssh_config.example` | `~/.ssh/config` template: alias, key, keep-alive, connection multiplexing, ProxyJump | [03](../notes/03-environment.md) |
| `sync_to_cluster.sh` | rsync template, dry run unless `--go`, `--down` to pull results, `--delete` to mirror | [03](../notes/03-environment.md) |
| `modules_cheatsheet.md` | **Environment Modules** (not Lmod): the commands, the Spack names, the compiler and MPI-wrapper tables | [05](../notes/05-module-environment.md) |

### sh/slurm/ — job templates

These follow ASC's own `examples/05_submitting_batch_jobs/` scripts in shape and
naming, and they all give **both** `--qos` and `--partition`, which ASC requires.
They pass `bash -n`; they cannot be run here, and the `module load` lines are
deliberately left as placeholders because ASC module names carry a Spack hash
that has no default and changes per architecture.

| File | What |
|---|---|
| `vsc4_serial.sbatch` / `vsc5_serial.sbatch` | one core on a **shared** node, hence `--mem`; 2 G on VSC-4, 4 G on VSC-5 |
| `vsc5_devel.sbatch` | the development QoS: 5 nodes, 10 minutes, priority 5 000 000 — where debugging belongs |
| `vsc4_mpi.sbatch` / `vsc5_mpi.sbatch` | 2 × 48 = 96 ranks (Skylake) and 2 × 128 = 256 ranks (Zen3), with the pinning recipes |
| `vsc5_hybrid.sbatch` | 2 nodes × 2 ranks × 64 threads: one rank per ccNUMA domain |
| `vsc5_array.sbatch` | `--array=1-20:5%2`, i.e. ASC's own array exercise |
| `vsc5_single_node_many_jobs.sbatch` | fill one node with 128 background tasks — `&` and `wait` are the point |
| `vsc5_gpu.sbatch` | `--gres=gpu:2` on the A100 partition, with the FP32/FP64 argument for choosing A40 instead |
| `slurm_cheatsheet.md` | commands, the partition/QoS table, ASC-local commands (`sqos`, `lastjobs`, `interactivejobs`), reason codes, reading results |

Every `[S<n>]` in these files resolves to
[`../refs/SOURCES.md`](../refs/SOURCES.md).
