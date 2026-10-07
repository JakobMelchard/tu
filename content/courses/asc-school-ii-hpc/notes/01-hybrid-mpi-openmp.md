# 01 Hybrid MPI + OpenMP: placement, pinning, overlap

Prepares for *Hybrid Programming in HPC: MPI+X* (ASC/HLRS/NHR@FAU, 2.5 days,
Advanced) [S4] [S5]. Assumes MPI from ASC-School I notes 07-16 and OpenMP from
NSSC I note 07 [S11].

## Definitions

- **Hybrid program**: MPI between processes (distributed memory, explicit
  messages), threads inside each process (shared memory). "MPI+X" with X =
  OpenMP, MPI-3 shared-memory windows, or an accelerator model [S5].
- **Thread support level**, requested with `MPI_Init_thread` [S15]:
  `SINGLE` (no threads), `FUNNELED` (only the thread that initialised MPI calls
  it), `SERIALIZED` (any thread, never two at once), `MULTIPLE` (any thread,
  concurrently). The library returns `provided`; a program must check it.
- **Masteronly style**: MPI calls only outside parallel regions. Needs
  `FUNNELED`. Simple, but all other threads idle while the master communicates.
- **Mapping**: which node and which package/NUMA domain a rank is placed on.
  **Binding**: the set of CPUs a rank (or thread) may run on. **Pinning**: a
  binding to a fixed CPU set so the OS cannot migrate it.
- **OpenMP places** [S16]: `OMP_PLACES=cores|threads|sockets|{...}` defines
  the CPU sets; `OMP_PROC_BIND=close|spread|master` how threads are assigned
  to places. Without `OMP_PROC_BIND` threads float.
- **ccNUMA domain**: cores with the same local memory controller. A MUSICA
  node has **8 domains of 24 cores**, 2 x EPYC 9654 [S14].
- **First touch**: a page is placed in the NUMA domain of the thread that
  first writes it. Initialise data with the same thread schedule that later
  uses it.

## Why bother: the trade

For $P$ ranks per node with $T$ threads each and $PT = C$ cores:

| quantity | pure MPI ($T=1$) | hybrid ($P$ small) |
|---|---|---|
| replicated data, halo cells | $\propto C$ copies | $\propto P$ copies |
| messages per halo exchange per node | $\propto C$ | $\propto P$, each longer |
| ranks in a collective | $C N_\text{nodes}$, latency $\propto \lg(C N)$ | $\lg(P N)$ |
| idle cores during communication (masteronly) | none | $T-1$ per rank |
| NUMA risk | none (each rank local) | a rank spanning domains needs first touch |

The standard compromise is **one rank per NUMA domain** (or per socket), with
threads filling that domain [S5]. On a MUSICA CPU node that is 8 ranks x up
to 24 threads, but NUMA 7 has 4 logical cores reserved for WEKA, so Slurm
offers 190 physical cores and **22 per rank is the largest layout that fits
all 8 domains** [S14]. Nothing here is measured on ASC; the course measures it.

## Worked example 1: launching and checking the layout

On the cluster (Slurm launches, see
[`../src/sh/slurm_templates/hybrid.sbatch`](../src/sh/slurm_templates/hybrid.sbatch)):

```bash
#SBATCH --nodes=2 --ntasks-per-node=8 --cpus-per-task=22 --threads-per-core=1
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK OMP_PLACES=cores OMP_PROC_BIND=close
srun --cpus-per-task=$SLURM_CPUS_PER_TASK --cpu-bind=cores ./affinity_report
```

With `mpirun` (Open MPI 5, no Slurm) the same layout is [S17]:

```bash
mpirun -np 16 --map-by ppr:8:node:PE=22 --bind-to core --report-bindings \
       -x OMP_NUM_THREADS=22 -x OMP_PLACES=cores -x OMP_PROC_BIND=close ./hybrid_pi
```

`affinity_report` prints one line per (rank, thread) with the CPU it runs on,
its allowed-CPU mask and its OpenMP place. What to look for: each rank's mask
is a block of 22 cores inside one NUMA domain; threads 0..21 of a rank sit on
distinct CPUs of that block. On the laptop [S10] every CPU column reads -1 and
`omp_get_num_places()` returns 0: **macOS exposes no binding at all**, and
`mpirun --bind-to core` aborts with "processor binding support is not
available". Placement can only be practised on Linux.

## Worked example 2: the P x T sweep

`hybrid_pi` integrates $\int_0^1 4/(1+x^2)\,dx$ with the midpoint rule,
$N = 4\cdot10^8$, on the M3 Pro (6 performance + 6 efficiency cores, `sysctl
hw.perflevel*`) [S10], median of 3 runs, with some background load from other
processes (load average 6-9):

| P x T | 1x1 | 1x2 | 2x1 | 1x4 | 2x2 | 4x1 | 2x4 | 4x2 | 8x1 | 4x3 | 12x1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| time [s] | 0.351 | 0.177 | 0.158 | 0.086 | 0.083 | 0.087 | 0.048 | 0.050 | 0.055 | 0.050 | 0.155 |

For a compute-bound kernel with one reduction at the end, **only $PT$ matters**
up to 8 workers: the split is within noise. Hybrid pays off where the table
above bites (memory per rank, message count, collective depth), which this
kernel does not have. At 12 workers every core is busy, so any background
process delays one worker and, since the runtime is the maximum over ranks,
the whole job: 12x1 scattered between 0.08 and 0.17 s. (An earlier single-run
sweep under different load gave 0.044 s for 12x1: same code, different
neighbours.) The program also checks that the result changes only by
summation order across decompositions (observed relative difference
$\le 5\cdot10^{-14}$).

## Worked example 3: overlapping communication and computation

Masteronly wastes $T-1$ threads during a halo exchange. Two standard fixes
[S5]:

```c
#pragma omp parallel
{
    #pragma omp masked                   /* 'master' before OpenMP 5.1 */
    {
        exchange_halos_start(&req);      /* MPI_Irecv/Isend: FUNNELED is enough */
        MPI_Waitall(4, req, MPI_STATUSES_IGNORE);
    }
    #pragma omp for schedule(static) nowait
    for (int i = 2; i < n - 2; i++) update_row(i);   /* interior: needs no halo */
    #pragma omp barrier                  /* halo has arrived */
    #pragma omp for
    for (int k = 0; k < 4; k++) update_row(k < 2 ? k : n - 4 + k); /* rows 0,1,n-2,n-1 */
}
```

The master thread communicates while the others start the interior; the
master joins the interior work late, so `schedule(dynamic)` or `taskloop`
balances better (taskloops are the hands-on of day 2 [S5]). Whether a
non-blocking transfer advances while no thread is inside an MPI call is up to
the implementation's progress engine [S15]; calling `MPI_Test` from the master
between chunks is the portable way to push it.

## Pitfalls

- **`OMP_NUM_THREADS` unset**: every rank starts one thread per visible core,
  so $P$ ranks oversubscribe the node $P$-fold. Slurm reserves cores with
  `--cpus-per-task` but does not set the variable.
- **Open MPI's defaults**: bind to *core* when $n_p \le 2$, to *package* when
  $n_p > 2$, none when oversubscribed [S17]. Two ranks with 64 threads each
  then run all 64 threads on one core. Always state `--bind-to` (or run under
  `srun --cpu-bind=`).
- **Hyper-threads counted as cores**: MUSICA has SMT on; `--cpus-per-task=22`
  without `--threads-per-core=1` can yield 11 cores x 2 threads [S13] [S9].
- **Initialising on the master thread**: all pages land in one NUMA domain,
  and the other domains' threads read remotely at lower bandwidth.
- **MPI calls from inside `omp for`** with only `FUNNELED`: undefined; request
  `MULTIPLE` and check `provided`.
- **Timing with `omp_get_wtime` on one rank**: the runtime is the maximum over
  ranks (`hybrid_pi` reduces with `MPI_MAX`).

## Questions (ours; there is no exam)

1. *A code runs 128 ranks per VSC-5 node. Why can 2 x 64 be faster, and why
   can it be slower?* Faster: 64x fewer halo copies and messages, shorter
   collectives, less memory per node. Slower: 63 idle threads during
   masteronly communication, a rank spanning several NUMA domains without
   first touch, OpenMP overheads in short loops.
2. *What does `provided = MPI_THREAD_FUNNELED` forbid?* Any MPI call from a
   thread other than the one that called `MPI_Init_thread`, including from
   inside `omp single` (which may run on any thread; use `masked`).
3. *`mpirun -np 2 ./a.out` with `OMP_NUM_THREADS=8` runs no faster than one
   thread. Why?* Open MPI binds each rank to one core for $n_p \le 2$; all 8
   threads share it. Fix: `--map-by ppr:1:package:PE=8 --bind-to core` or
   `--bind-to none`.
4. *Where do the pages of `a` land after `double *a = malloc(n*8); memset(a,0,n*8);`
   on the master thread?* All in the master's NUMA domain (first touch). Fix:
   initialise in an `omp for schedule(static)` loop with the same schedule as
   the compute loops.
5. *Why does `hybrid_pi` show almost no difference between 2x4, 4x2 and 8x1?* It is
   compute-bound with one 8-byte reduction; none of the hybrid trade-offs
   (memory, messages, collective depth) is exercised, only the product $PT$.

## Code

- [`../src/c/hybrid_pi.c`](../src/c/hybrid_pi.c): `MPI_Init_thread`, block
  distribution `block_range`, OpenMP reduction, three self-checks.
- [`../src/c/affinity_report.c`](../src/c/affinity_report.c): `sched_getcpu`,
  `sched_getaffinity`, `omp_get_place_num`, gathered to rank 0.
- [`../src/sh/slurm_templates/hybrid.sbatch`](../src/sh/slurm_templates/hybrid.sbatch).
- Minimal version in the sibling course:
  [`asc-school-i-hpc/src/c/hybrid_omp_mpi.c`](../../asc-school-i-hpc/src/c/hybrid_omp_mpi.c).
