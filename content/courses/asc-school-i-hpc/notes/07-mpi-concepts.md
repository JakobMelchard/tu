# 07 MPI concepts, process model and language bindings

Block 3, **day 1**: *"MPI overview"* (09:05) and *"Process model and language
bindings"* (10:45) [S13]. Lab `01_hello` [S11]. Code: [`src/c/hello_mpi.c`](../src/c/hello_mpi.c) (skeleton, ranks, ordered output), [`src/c/hybrid_omp_mpi.c`](../src/c/hybrid_omp_mpi.c) (MPI + OpenMP). Build and run everything with `make -C src/c test`.

## What MPI is

The **Message Passing Interface** is a *standard* — a document, not a library —
for an API that lets independent processes exchange data and synchronise. The
current version is **MPI 5.0, 5 June 2025** [S15], and that is the version the
ASC course links as its "standard document" [S13]. The lineage, from the
standard's own front matter [S15]: MPI-1.0 (1994), 1.1 (1995), 1.2 and 2.0
(1997), 1.3 and 2.1 (2008), 2.2 (2009), 3.0 (2012), 3.1 (2015), 4.0 (2021),
4.1 (2023), 5.0 (2025). The HLRS deck the block is taught from is still the
MPI-3.1 edition [S12] [S13], so expect the lecture to say "MPI-3.1" and the
linked document to say 5.0; nothing in this course changed between them.

**Standard ≠ implementation** — the lecturer makes this a slide of its own
[S14]. Implementations: Open MPI, MPICH and its derivatives (Intel MPI, Cray
MPICH, MVAPICH/MVAPICH2). The standard fixes semantics; the implementation fixes
performance, the launcher (`mpirun`, `srun`) and which algorithms the collectives
use ([09](09-collectives.md)). On the ASC systems all of these are available as
modules ([05](05-module-environment.md)) [S10].

**Language bindings.** The standard defines bindings for **C and Fortran** only
[S15]. C++ had a binding in MPI-2, which was deprecated in MPI-2.2 and removed
in MPI-3.0 — C++ programs call the C API. Python is served by `mpi4py`, which is
not part of the standard but is a first-class option in this course: the labs
ship in C, Fortran **and** Python, and `mpi4py.readthedocs.io` is one of the four
links on the course-material page [S11] [S13]. Fortran gets its own session on
day 2, for Fortran participants only [S13]; its modern binding is `use mpi_f08`,
and the reason it needs a session is that non-blocking calls on Fortran arrays
need `ASYNCHRONOUS` attributes to stop the compiler moving the buffer — a trap
the lecturer's best-practice deck shows in a production code [S14].

Model: **SPMD**, single program multiple data. `mpirun -np 4 ./prog` (or `srun` inside a Slurm job) starts 4 *processes* of the same executable, possibly on different nodes. Each has its own address space (no shared variables, ever), its own copy of every array, and a number, the **rank**, 0..P-1. The only way for data to move between them is a message. Branching on the rank (`if (rank == 0) ...`) is how the one program does different things on different processes.

```c
#include <mpi.h>
int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);                   /* every MPI program: first MPI call */
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);     /* my number */
    MPI_Comm_size(MPI_COMM_WORLD, &size);     /* how many of us */
    /* ... work, communicate ... */
    MPI_Finalize();                           /* last MPI call; all ranks must reach it */
    return 0;
}
```

Compile with the wrapper `mpicc` (adds include and library paths), run with the launcher. `MPI_Wtime()` gives a wall-clock double for timing; `MPI_Abort(comm, code)` kills everything; `MPI_Get_processor_name` tells the node.

## Communicators, groups, ranks

A **communicator** is a group of processes plus a private communication context. `MPI_COMM_WORLD` contains all processes; the rank is *relative to a communicator*. Every communication names its communicator, so a library can create its own (`MPI_Comm_dup`) and never collide with the application's messages. `MPI_Comm_split(comm, color, key, &newcomm)` partitions processes (e.g. one communicator per node, or per row of a 2D process grid); `MPI_Cart_create` builds a Cartesian topology with `MPI_Cart_shift` giving the neighbour ranks. `MPI_COMM_SELF` contains only me.

## A message

Data: `(buffer, count, datatype)`; the datatype (`MPI_INT`, `MPI_DOUBLE`, `MPI_CHAR`, `MPI_BYTE`, `MPI_LONG`, `MPI_FLOAT`, `MPI_C_BOOL`, `MPI_DOUBLE_COMPLEX`, or a *derived* type for non-contiguous data, [09](09-collectives.md)) lets MPI convert between heterogeneous nodes and describe layouts. Envelope: source, destination, **tag** (an integer you choose to distinguish message kinds), communicator. A receive matches a message when source, tag and communicator match (wildcards `MPI_ANY_SOURCE`, `MPI_ANY_TAG` on the receive side only); the datatype and count must be *compatible* (receive buffer at least as large).

Two families: **point-to-point** (one sender, one receiver, [08](08-point-to-point.md)) and **collective** (all ranks of a communicator, [09](09-collectives.md)). Plus **one-sided communication** ([13](13-one-sided.md),
[14](14-shared-memory-one-sided.md)) and **parallel I/O**
([15](15-mpi-io.md)), both of which this course *does* cover, on day 4 [S13].

## Implicit synchronisation

MPI has no shared clock and no shared memory, so *synchronisation only happens through messages*. A blocking receive cannot return before the message has arrived; therefore whoever sent it was at least at the send call. Collective operations imply synchronisation to the degree their data flow requires: an `MPI_Barrier` synchronises everyone, an `MPI_Bcast` guarantees only that every rank leaves after the root entered. Do not infer more ordering than the data dependency gives you: after `MPI_Bcast` rank 3 may still be inside it while rank 0 is far ahead.

## Shared, distributed, hybrid

| | Distributed memory: MPI | Shared memory: OpenMP | Hybrid MPI+OpenMP |
|---|---|---|---|
| unit | process (own memory) | thread (shares memory) | one process per node/socket, threads inside |
| scope | whole cluster, also within a node | one node | whole cluster |
| effort | restructure data into local pieces, explicit messages | pragmas on loops, incremental | both |
| errors | deadlocks, mismatched messages, wrong counts | data races, false sharing | both, plus thread-safety level of MPI |
| memory | every rank holds its part plus halos; replicated data costs P times | one copy | less replication than pure MPI, fewer ranks |
| performance | explicit locality, scales far; messages cost ~1 us + size/bandwidth | limited by memory bandwidth and NUMA; no message cost | fewer, larger messages; threads share halos; harder to balance |
| typical | domain decomposition, particle codes, linear algebra at scale | multi-threaded loops, libraries (BLAS), pre/post-processing | large stencil/particle codes on many-core nodes |

**When to use what.** Fits on one node and the parallel loops are obvious: OpenMP (hours of work). Needs more memory or cores than one node, or must scale: MPI, always usable inside a node too (messages go through shared memory at ~0.3 us). Very many cores per node, memory-bound with big halos, or an MPI code that stalls because of per-rank memory: hybrid, with one rank per NUMA domain and `OMP_NUM_THREADS` = cores per domain. GPUs: a separate decision layered on top (CUDA/OpenACC inside each rank). Embarrassingly parallel (independent runs): no MPI, a Slurm job array.

Hybrid needs `MPI_Init_thread(&argc, &argv, required, &provided)` with a thread level: `MPI_THREAD_SINGLE` (no threads), `FUNNELED` (only the main thread calls MPI: the usual choice, see `hybrid_omp_mpi.c`), `SERIALIZED` (any thread, one at a time), `MULTIPLE` (any thread, concurrently; costs performance in the library). Check `provided >= required`.

## What the standard also contains ("short tour: other MPI topics")

Day 2 ends with a survey of what you are *not* being taught [S13]. From the
standard's own table of contents [S15]: process creation and management
(`MPI_Comm_spawn`), the tool interfaces (`MPI_T`, PMPI), error handling beyond
the fatal default, info objects, generalized requests, persistent and
partitioned communication (MPI-4), sessions (MPI-4, an alternative to
`MPI_Init`), and neighbourhood collectives on topology communicators
([11](11-virtual-topologies.md)). The useful reflex is: if a communication
pattern feels awkward, look for it in the standard's contents before writing it
by hand.

## Pitfalls

- Thinking a variable set on rank 0 is visible on rank 1. Each rank has its own copy of everything, including `argv` and file handles.
- Reading input on every rank at once (P processes opening the same file) instead of rank 0 reading and `MPI_Bcast`.
- Every rank writing to stdout: interleaved garbage; print from rank 0 or prefix with the rank and sort later.
- `mpirun -np 4` on a 2-core laptop without `--oversubscribe`: Open MPI refuses; on the cluster `srun` handles placement.
- Calling MPI before `MPI_Init` or after `MPI_Finalize`; a rank returning from `main` without `MPI_Finalize` (or `exit()` on one rank) aborts the job.
- Running the executable directly (`./prog`) instead of through the launcher: one lonely rank, `size == 1`, which often "works" and hides bugs.
- Assuming the standard fixes performance: `MPI_Bcast` of 1 MB may be fast on one implementation and mediocre on another; measure on the target machine ([16](16-best-practice-and-debugging.md)).

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1 and Q2 are what the `01_hello` lab asks you to
work out for yourself [S11].

1. **What does SPMD mean, and how does one executable end up doing different things on different processes?**
   Single program, multiple data: all processes run the same binary on their own data; behaviour branches on the rank returned by `MPI_Comm_rank` (and on the data each rank owns).
2. **Give two reasons why a communicator is more than "the list of processes".**
   It carries a context that isolates its messages from those of other communicators (libraries cannot intercept application messages), and it defines the rank numbering and the set of participants for collectives; subsets (`MPI_Comm_split`) let you do collectives on rows/columns/nodes.
3. **A colleague says "after `MPI_Bcast` all ranks are synchronised". Correct?**
   Only in the weak sense that no rank leaves before the root has entered. Non-root ranks may leave at different times; it is not a barrier.
4. **You have a 10 GB dataset and a 512 GB node. Pure MPI with 128 ranks or hybrid 8 ranks x 16 threads: which uses less memory and why?**
   Hybrid: pure MPI replicates any global tables per rank (128 copies) and stores 128 halo regions; with 8 ranks there are 8 copies and larger interior blocks per halo, so lower surface-to-volume overhead.
5. **What does `MPI_THREAD_FUNNELED` promise, and what happens if an OpenMP worker thread calls `MPI_Send` in such a program?**
   Only the thread that called `MPI_Init_thread` will make MPI calls. A worker calling MPI is undefined behaviour: it may work by luck, corrupt internal state, or crash. Use `SERIALIZED`/`MULTIPLE` if workers must communicate.
