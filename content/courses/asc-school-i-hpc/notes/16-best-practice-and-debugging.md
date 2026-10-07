# 16 Patterns, performance, best practice, debugging

Block 3, **day 2, 12:15** (*"Optimizing MPI communication — a real world
example"*) and **day 4, 12:45** (*"Best practice, Summary, Q&A"*) [S13].
Sources: the lecturer's own best-practice deck [S14], plus MPI 5.0 [S15] and
[S20] for the cost models. Amdahl is stated in the lecturer's form [S9]; the
derivations of Amdahl, Gustafson and Karp–Flatt, with measurements, are in the
sibling course's note 07 [S23] and are not repeated here.

Code: [`src/c/heat1d_halo.c`](../src/c/heat1d_halo.c) (domain decomposition + halo exchange, checked bitwise against the serial solver), [`src/c/pingpong.c`](../src/c/pingpong.c) (latency, bandwidth, $n_{1/2}$), [`src/c/pi_reduce.c`](../src/c/pi_reduce.c) (speedup measurement), [`src/c/nonblocking.c`](../src/c/nonblocking.c) (overlap).

## Parallelising a serial program

1. **Find the work and the data**: which loops dominate (profile: `gprof`, `perf`, or `MPI_Wtime` around sections), which arrays they touch.
2. **Choose a decomposition**: split the *data* (domain decomposition: each rank owns a block of the grid/particles/matrix and computes on it) or the *tasks* (master-worker/task pool: independent work items handed out on demand). Data decomposition scales; task pools balance.
3. **Identify dependencies**: which values does a rank need that another rank owns? Those become messages (halos), reductions (global sums, norms, time-step control) or redistributions (`Alltoall` in an FFT).
4. **Write it so that P = 1 reproduces the serial result**, then check P = 2, 3, 4 against P = 1 (`heat1d_halo.c` compares bitwise). Only then measure.

## Domain decomposition and halo exchange

For a stencil update $u_i^{n+1} = f(u_{i-1}^n, u_i^n, u_{i+1}^n)$ each rank stores its $n_\text{loc}$ points plus **ghost (halo) cells** holding copies of the neighbours' boundary points. Per time step: exchange halos, then update. In 1D:

```
rank r-1:  [.. x x x g]              g = ghost, receives neighbour's boundary point
rank r  :      [g x x x x g]         send u[1] left, u[n] right; receive into u[0], u[n+1]
rank r+1:              [g x x x ..]
```

`MPI_Sendrecv` once per direction (or `Irecv/Isend/Waitall`) with `MPI_PROC_NULL` at the physical boundary. In 2D/3D with a Cartesian communicator (`MPI_Cart_create`, `MPI_Cart_shift`) the faces are non-contiguous: `MPI_Type_create_subarray` or `MPI_Type_vector` describes them; a halo of width $w$ lets you exchange every $w$ steps at the price of redundant computation.

**Surface-to-volume**: computation per rank $\propto$ volume $(N/P)^{d}$ of the local block in $d$ dimensions, communication $\propto$ surface $(N/P)^{d-1}$. The ratio communication/computation shrinks as the local block grows: bigger blocks per rank, fewer nodes per problem size, or 2D/3D decomposition instead of slabs (a slab decomposition of a 3D grid has surface $N^2$ per rank regardless of P; a cubic block has $6 (N/P^{1/3})^2$). `heat1d_halo.c` with the default 400 points on 4 ranks is *slower* than serial: 100 points per rank means 400 flops per two messages of ~1 us; with `-N 20000` it scales.

## Load balancing

Static: give every rank the same amount of *work*, which is not always the same number of points (adaptive grids, particles clustering). Dynamic: a master hands out chunks to workers as they finish (`MPI_ANY_SOURCE` receive, `Waitany`), or work stealing. Imbalance shows up as time in `MPI_Wait`/`Allreduce`/`Barrier`: measure `t_compute` per rank, `max/mean` is the imbalance factor; efficiency cannot exceed mean/max.

## Measuring

```c
MPI_Barrier(comm); double t = MPI_Wtime();   /* barrier only to start together */
... work ...
t = MPI_Wtime() - t;
MPI_Reduce(&t, &tmax, 1, MPI_DOUBLE, MPI_MAX, 0, comm);   /* the slowest rank defines the runtime */
```

Report the maximum over ranks, repeat 3-5 times, take the minimum or median, note node count and placement (ranks on one node vs spread, `--ntasks-per-node`), and write the module list and Slurm parameters next to the numbers. Compare *methods* (blocking vs non-blocking halo exchange, `Sendrecv` vs `Isend` with overlap, one collective vs many sends) on the *target* cluster: the best method is an empirical question per machine; that is exactly what the block-3 exercises ask for.

Point-to-point model from `pingpong.c`: $t(n) = \alpha + n/B$, $n_{1/2} = \alpha B$. Compare intra-node (shared memory: $\alpha \sim 0.3\,\mu s$) and inter-node (InfiniBand: $\alpha \sim 1$-$2\,\mu s$, $B \sim 10$-$25$ GB/s) by placing the two ranks accordingly.

## Scaling and Amdahl

With serial time $T_1$ and parallel time $T_p$: speedup $S(p) = T_1/T_p$,
efficiency $E(p) = S/p$.

> **Convention, stated because it is the usual source of sign confusion.**
> Throughout this note, and on the lecturer's own slide [S9], **$f$ is the
> *sequential* fraction of the code** — the part that does *not* parallelise.
> Many textbooks use the same letter for the *parallel* fraction, in which case
> every formula below has $f$ and $1-f$ swapped. The lecturer writes it as
> $$T_{\text{parallel},p} = f\,T_{\text{serial}} + (1-f)\,\frac{T_{\text{serial}}}{p},
>   \qquad
>   S_p = \frac{T_{\text{serial}}}{T_{\text{parallel},p}} = \frac{1}{f + (1-f)/p} < \frac 1 f,$$
> neglecting communication time and load imbalance [S9]. The sibling course's
> note 07 uses the same convention [S23], so the two agree.

Checks, recomputed rather than recalled (`../src/py/mpi_cost.py::amdahl`
asserts them): $f = 0.05$ gives $S_\infty = 20$ and $S_{64} = 1/(0.05 +
0.95/64) = 15.42$, $E = 24.1\%$. $f = 0.02$ gives $S_\infty = 50$ and
$S_{100} = 1/(0.02 + 0.98/100) = 33.6$, $E = 33.6\%$. And the slide's own
caption, which is the thing to remember: **speedup is a ratio, not an absolute
performance** — a code with a terrible serial baseline scales beautifully [S9].

Communication adds to the "serial" part *and grows with $p$*, so real curves
bend down and there is an optimal $p$ for every problem size.

**Weak scaling**: problem size grows with P (constant work per rank, e.g. $N/P$ = const in `heat1d_halo.c`). Gustafson: $S(P) = s + (1-s) P$, the serial fraction is measured at the *parallel* size. Weak-scaling efficiency $T_1/T_P$ (should stay ~1) tells you whether the communication pattern is scalable; halo exchange is (constant per rank), a global `Allgather` of everything is not ($\propto P$).

Superlinear speedup (E > 1) is real: the local data fits into cache once the problem is split enough. A speedup plot without the problem size, the machine and the baseline (serial code or P = 1 MPI?) is meaningless.

## The lecturer's real-world example

Day 2 spends fifteen minutes on one production code, and it is the most useful
fifteen minutes of the block because the numbers are real [S14]. A Fortran
solver did, per iteration: a loop of `MPI_ISEND` to every other rank, an
`MPI_BARRIER`, a loop of `MPI_RECV`, another `MPI_BARRIER`, some work that does
not touch the send buffer, and a third `MPI_BARRIER`. Measured runtimes, for one
subroutine call and for the whole run, at two problem sizes:

| version | 6×6, one call | 6×6, total | 8×8, one call | 8×8, total |
|---|---|---|---|---|
| original | 1500 s | 14 h | 21 000 s | 90 h |
| barriers removed | 960 s | 12 h | 3 500 s | 32 h |
| correct non-blocking (`ISEND` … `RECV` … `WAIT`) | **425 s** | 10 h | **960 s** | 18 h |
| send loop replaced by `MPI_BCAST` | 420 s | 10 h | 1 025 s | 20 h |

Four readings, all of them transferable:

1. **Deleting three barriers was worth a factor 6 at the larger size**
   (21 000 → 3 500 s). The slide's conclusion is in capitals: *"NEVER use
   MPI_BARRIER in production code!!!!!"* [S14]. Barriers do not make message
   passing correct — data dependencies already do — and they convert every load
   imbalance into everyone's idle time.
2. **The non-blocking version then halved it again** (3 500 → 960 s), a total
   factor 22 on the 8×8 case. What was missing was the `MPI_WAIT`: the original
   used `MPI_ISEND` and then relied on a barrier instead of completing the
   request.
3. **`MPI_Bcast` was not automatically better.** It won at 6×6 (420 vs 425 s)
   and *lost* at 8×8 (1025 vs 960 s). This is the block-3 learning outcome about
   comparing communication methods "on this particular cluster" [S1] in one
   line: the right method is an empirical question, and the answer changes with
   problem size.
4. **The scaling of the bug was worse than the code.** Going from 6×6 to 8×8 —
   about twice the work — cost 14× in the original version and 2.3× in the fixed
   one. A communication defect does not cost a constant factor; it costs a worse
   exponent.

The Fortran detail the slide adds is worth knowing even if you write C: the
corrected version declares the send buffer `ASYNCHRONOUS` and checks
`MPI_ASYNC_PROTECTS_NONBLOCKING`, because otherwise a Fortran compiler is free
to copy the buffer around a non-blocking call [S14] [S15].

## Overlap and other tricks

- Post `Irecv` before `Isend`; compute the interior while halos travel ([08](08-point-to-point.md)); on a laptop the gain is small, with RDMA interconnects it hides most of the exchange.
- Fewer, larger messages: pack, derived datatypes, exchange every $w$ steps with wider halos.
- Batch reductions: one `Allreduce` on an array instead of many scalars.
- Avoid `Barrier` in production; avoid rank 0 doing serial work while the others wait (parallel I/O with `MPI_File_*` or HDF5, or at least rank 0 reading + `Bcast` once).
- Hybrid: one rank per NUMA domain with threads inside cuts messages and halo memory ([07](07-mpi-concepts.md)).
- Placement: `--ntasks-per-node` and binding (`srun --cpu-bind=cores`, `OMP_PROC_BIND`) change results by tens of percent.

## Debugging MPI programs

1. Build with `-g -Wall -Wextra -O0` first; run with P = 1, 2, 3 (odd P finds symmetry assumptions), small N.
2. `printf("[%d] ...\n", rank); fflush(stdout);` with rank prefix; `mpirun --output-filename out` (Open MPI) or `srun --output=out.%t` write one file per rank; sort by rank afterwards.
3. Hang: attach to a rank (`gdb -p PID` on the node, `bt` shows where it waits), or `mpirun -np 2 xterm -e gdb ./prog` on a machine with X; a hang in `MPI_Finalize` means one rank has an outstanding message/request.
4. Deadlock exposure: replace `MPI_Send` by `MPI_Ssend` (`#define MPI_Send MPI_Ssend` in a test build): buffering-dependent code then hangs at any size.
5. Wrong results: check counts and types at each pair, tags, `MPI_Get_count`; run under `valgrind` or `-fsanitize=address` (with `--oversubscribe` on a laptop) for buffer overruns into halos.
6. Correctness tools: MUST (runtime checker for MPI usage errors, deadlocks, type mismatches), Intel Trace Analyzer, `mpiP`/Score-P/Vampir/TAU for time in each MPI call (where does my run wait?).
7. Errors are fatal by default; `MPI_Comm_set_errhandler(comm, MPI_ERRORS_RETURN)` plus checking return codes and `MPI_Error_string` gives readable messages in library code.
8. The launcher's exit message names the rank that failed (`Process name: [...,3] Exit code: 3` in the `deadlock.c` demo); Slurm's `.out` shows `srun: error: n0123: task 7: Segmentation fault`.

## Pitfalls

- Measuring speedup against a slow serial baseline (unoptimised, `-O0`): the speedup looks great, the science is not faster.
- Timing one run, one size, on one node pair.
- Comparing P ranks on one node with P ranks across nodes and blaming MPI: the memory bandwidth per rank changed too.
- Halo exchange every step with a 1-cell halo when the stencil allows batching.
- Rank 0 as I/O bottleneck: gathering the whole field every step for a picture.
- Global `Allgather` "to be safe": $O(N)$ memory per rank, $O(P)$ traffic; weak scaling collapses.
- Declaring a hang "an MPI bug": in this course it is your tags/counts/order; use `Ssend` and P = 3.

## Best practice, in the lecturer's own order

The closing session distils to six rules [S14], all of which have appeared above:

1. **Know the hardware, know your code, know the system environment — then take
   control.** The latency/bandwidth ladder of [04](04-cluster-anatomy.md) is the
   whole argument: *avoiding slow data paths is the key to most performance
   optimizations.*
2. **Design the communication with the algorithm**, not afterwards (Foster's
   methodology): decide whether the pattern is local-neighbour or long-range,
   regular or unstructured, before writing a single `MPI_Send`.
3. **Communicate as little as possible, but as much as necessary.**
4. **Aggregate into longer messages**, because small ones are latency-bound
   ([08](08-point-to-point.md)).
5. **Look for an easy overlap**: split the code into the part that can run
   before the halo arrives and the part that needs it.
6. **Never `MPI_Barrier` in production.**

And one engineering rule from the same deck: **compile from a single source**.
Guard the MPI-specific and OpenMP-specific parts with `#ifdef USE_MPI` (set by
`-DUSE_MPI`) and `#ifdef _OPENMP` (set by the compiler with `-fopenmp` /
`-qopenmp`), with `rank = 0; size = 1;` in the serial branch [S14]. One file
that builds serial, OpenMP, MPI and hybrid keeps the serial baseline honest —
which matters, because the first pitfall below is measuring speedup against a
baseline nobody maintains.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q6 and Q7 are the real-world example above [S14].

1. **A 3D grid $N^3$ on P ranks: compare the communication volume per rank for slab (1D) and cubic (3D) decomposition, and the ratio to computation.**
   Slab: 2 faces of $N^2$ points, computation $N^3/P$, ratio $2P/N$. Cubic: 6 faces of $(N/P^{1/3})^2$, ratio $6 P^{1/3}/N$. For $N = 512$, $P = 512$: slab ratio 2, cubic ratio 0.09.
2. **Serial fraction 2%. Maximum speedup? Speedup and efficiency on 100 cores? What changes if communication costs $0.1\%$ per rank added to the serial fraction?**
   $S_\max = 50$; $S(100) = 1/(0.02 + 0.98/100) = 33.6$, $E = 34\%$. With $s(P) = 0.02 + 0.001 P$: at $P = 100$, $s = 0.12$, $S = 7.8$; there is now a maximum around $P \approx 30$.
3. **Weak-scaling efficiency drops from 0.98 at P = 8 to 0.6 at P = 512 for a halo-exchange code. Name two likely causes and how you would distinguish them.**
   A global operation whose cost grows with P (an `Allgather`/`Alltoall`, rank-0 I/O) or a network effect (placement across switches, contention). Time each MPI call per rank (mpiP/Score-P) and see whether the extra time is in a collective, in `Wait` (imbalance/contention) or in I/O; rerun with the collective removed or with `--ntasks-per-node` changed.
4. **Your parallel result differs from the serial one by $10^{-3}$ relative. Rounding?**
   No; reduction-order effects are $\sim 10^{-14}$ per term. A $10^{-3}$ difference is a bug: a halo not updated before use, an off-by-one in the block decomposition, or a boundary rank using a stale ghost cell. Compare fields pointwise for P = 2 and small N.
5. **How do you measure latency and bandwidth of the interconnect with your own code, and what is the point of $n_{1/2}$?**
   Ping-pong between two ranks on different nodes: send $n$ bytes and receive them back, time many repetitions, one-way time $t(n) = $ round trip / 2; $\alpha = t(0)$, $B = n/t(n)$ for large $n$; $n_{1/2} = \alpha B$ separates latency-bound from bandwidth-bound message sizes and tells you how much to aggregate.
6. **A production code does a loop of `MPI_Isend`, then `MPI_Barrier`, then a
   loop of `MPI_Recv`, then two more barriers. Name the two defects and the
   order to fix them in.** The barriers (remove them — worth a factor 6 at the
   larger size in the measured example) and the missing `MPI_Wait` on the
   non-blocking sends (add it — worth another factor 3.6). Together: 21 000 s →
   960 s [S14].
7. **In that same code, replacing the send loop by `MPI_Bcast` helped at one
   problem size and hurt at another. What is the lesson, and which learning
   outcome of this course is it?** That the best communication method is
   measured, not deduced — which is exactly the stated outcome about comparing
   methods "with regard to the runtime of the parallel program on a specific
   cluster" and determining "the best method of MPI communication on this
   particular cluster" [S1] [S14].
8. **You are asked for a speedup plot. Name three things it is meaningless
   without.** The problem size, the machine and placement (ranks per node), and
   what the baseline is — an optimised serial code, or the MPI code at $p = 1$.
   And say whether $f$ in any quoted Amdahl fit is the sequential or the
   parallel fraction [S9].
