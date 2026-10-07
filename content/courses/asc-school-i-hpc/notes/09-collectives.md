# 09 Collective communication

Block 3, **day 2, 10:45** [S13]. Lab `04_allreduce` (and `ring_scan`) [S11].
Code: [`src/c/collectives.c`](../src/c/collectives.c) (every collective below
with a check, Bcast vs P sends timing),
[`src/c/pi_reduce.c`](../src/c/pi_reduce.c) (`MPI_Reduce` for a sum),
[`src/exercises/2025w-mpi/ring_variants.c`](../src/exercises/2025w-mpi/ring_variants.c)
(the ring sum replaced by one `Allreduce`, and by `MPI_Scan`).
Semantics from MPI 5.0 §6 [S15]; the cost model from [S20].

Derived datatypes used to live at the end of this note; they now have their own,
because the course gives them a session of their own —
[12](12-derived-datatypes.md).

## Rules that hold for all collectives

- Called by **every** rank of the communicator, with matching parameters (same `count`, `type`, `root`, `op`); no tags.
- Blocking versions return when the *local* buffers may be reused; only `MPI_Barrier` guarantees that everyone has arrived.
- `count` is **per process**: `MPI_Scatter(..., sendcount=3, ...)` sends 3 elements to each of P ranks from a root buffer of 3P.
- `root` buffers matter only on the root; on other ranks pass `NULL` for the unused one.
- `MPI_IN_PLACE` as send buffer (`Reduce`/`Allreduce`/`Gather`/`Scatter` on root, `Allgather`, `Alltoall`) uses the receive buffer for input and avoids a copy.
- Every collective has a non-blocking `MPI_I...` variant returning a request (MPI-3); also neighbourhood collectives on Cartesian communicators.

## The catalogue

```
Bcast       root: [a b c]                ->  all: [a b c]
Scatter     root: [a0 a1 | b0 b1 | c0 c1] ->  rank0 [a0 a1], rank1 [b0 b1], rank2 [c0 c1]
Gather      rank0 [a0 a1], rank1 [b0 b1], rank2 [c0 c1]  ->  root: [a0 a1 b0 b1 c0 c1]
Allgather   = Gather then Bcast: everybody gets [a0 a1 b0 b1 c0 c1]
Alltoall    rank i sends block j to rank j: a transpose of the P x P block matrix
Reduce      root gets op(x_0, x_1, ..., x_{P-1}) elementwise
Allreduce   = Reduce then Bcast: everybody gets the result
Scan        rank i gets op(x_0, ..., x_i) (inclusive prefix); Exscan excludes x_i
Reduce_scatter  reduce, then scatter the result vector in blocks
Barrier     nobody leaves before everybody arrived
```

```c
MPI_Bcast(buf, n, MPI_DOUBLE, root, comm);
MPI_Scatter(sendbuf, n_each, MPI_INT, recvbuf, n_each, MPI_INT, root, comm);
MPI_Gather(sendbuf, n_each, MPI_INT, recvbuf, n_each, MPI_INT, root, comm);
MPI_Scatterv(sendbuf, counts, displs, MPI_DOUBLE, recvbuf, mycount, MPI_DOUBLE, root, comm);  /* uneven blocks */
MPI_Gatherv(sendbuf, mycount, MPI_DOUBLE, recvbuf, counts, displs, MPI_DOUBLE, root, comm);
MPI_Allgather(sendbuf, n_each, MPI_INT, recvbuf, n_each, MPI_INT, comm);
MPI_Alltoall(sendbuf, n_each, MPI_INT, recvbuf, n_each, MPI_INT, comm);
MPI_Reduce(&local, &global, 1, MPI_DOUBLE, MPI_SUM, root, comm);
MPI_Allreduce(&local, &global, 1, MPI_DOUBLE, MPI_MAX, comm);
MPI_Allreduce(MPI_IN_PLACE, vec, n, MPI_DOUBLE, MPI_SUM, comm);
MPI_Scan(&x, &prefix, 1, MPI_INT, MPI_SUM, comm);
MPI_Barrier(comm);
```

Reduction ops: `MPI_SUM MPI_PROD MPI_MAX MPI_MIN MPI_LAND MPI_LOR MPI_BAND MPI_BOR MPI_MAXLOC MPI_MINLOC` (the last two on pair types `MPI_DOUBLE_INT` etc. return the value *and* the rank/index), or your own with `MPI_Op_create` (must be associative; commutative if you say so). Reductions on arrays are elementwise.

The `v` variants (`Scatterv`, `Gatherv`, `Allgatherv`, `Alltoallv`) take per-rank `counts[]` and `displs[]` (in elements, relative to the root buffer) and are what you need for N points on P ranks when P does not divide N: `counts[r] = N/P + (r < N%P)`, `displs[r] = r*(N/P) + min(r, N%P)`.

## Performance: the cost model, derived rather than remembered

> **This table was wrong before this pass and has been rebuilt from the primary
> source.** The previous version gave $2\alpha\log_2 P$ for a small-message
> `Allreduce` and "$\approx 2n\beta$, independent of $P$" for a large `Bcast`.
> The first is the cost of the *naive* Reduce-then-Bcast implementation, not of
> the recursive-doubling algorithm every MPI library has used since the early
> 2000s; the second drops a $\frac{P-1}{P}$ factor. Both are now taken from
> Thakur, Rabenseifner and Gropp [S20] — Rabenseifner being the author of the
> slide deck this block is taught from — and are implemented and unit-tested in
> [`../src/py/mpi_cost.py`](../src/py/mpi_cost.py).

**Conventions, stated explicitly** because everything below depends on them
[S20]: $\alpha$ is the per-message latency in seconds, $\beta$ the transfer time
per **byte** (so $\beta = 1/B$), $\gamma$ the local reduction cost per byte, $n$
the number of **bytes in one process's contribution**, $p$ the number of
processes, and $\lg \equiv \log_2$. A single message of $n$ bytes costs
$\alpha + n\beta$. The model assumes a single-ported, full-duplex network and
ignores distance — good enough to rank algorithms, not to predict a runtime.

| collective | algorithm | cost |
|---|---|---|
| `Bcast` (short) | binomial tree | $\lceil\lg p\rceil\,(\alpha + n\beta)$ |
| `Bcast` (long) | scatter + ring allgather (Van de Geijn) | $(\lg p + p - 1)\,\alpha + 2\frac{p-1}{p}n\beta$ |
| `Reduce` (short) | binomial tree | $\lceil\lg p\rceil\,(\alpha + n\beta + n\gamma)$ |
| `Reduce` (long, > 2 kB) | reduce-scatter + gather (Rabenseifner) | $2\lg p\,\alpha + 2\frac{p-1}{p}n\beta + \frac{p-1}{p}n\gamma$ |
| `Allreduce` (short) | recursive doubling | $\lg p\,\alpha + n\lg p\,\beta + n\lg p\,\gamma$ |
| `Allreduce` (long) | reduce-scatter + allgather (Rabenseifner) | $2\lg p\,\alpha + 2\frac{p-1}{p}n\beta + \frac{p-1}{p}n\gamma$ |
| `Allgather` (short) | recursive doubling / Bruck | $\lceil\lg p\rceil\,\alpha + \frac{p-1}{p}n_\text{tot}\beta$ |
| `Allgather` (long) | ring | $(p-1)\,\alpha + \frac{p-1}{p}n_\text{tot}\beta$ |
| `Alltoall` (short) | Bruck | $\lg p\,\alpha + \frac{n_\text{tot}}{2}\lg p\,\beta$ |
| `Alltoall` (long) | pairwise exchange | $(p-1)(\alpha + n\beta)$ |
| `Barrier` | dissemination | $\lceil\lg p\rceil\,\alpha$ |

Five consequences, and they are the things worth remembering:

1. **A collective beats the same pattern hand-written with sends.** A loop of
   $p-1$ sends costs $(p-1)\alpha$; a binomial tree costs $\lg p\,\alpha$. At
   $p = 1000$ that is a factor ~100 in the latency term. `collectives.c` times
   both; on 4 oversubscribed ranks in shared memory they tie (0.31 ms vs
   0.32 ms for 4 MB [S24]) because $\lg 4 = 2$ against $p-1 = 3$ — the point is
   the scaling, which you cannot see on a laptop.
2. **One `Allreduce` on 100 doubles costs about the same as one on a single
   double**, because below $n_{1/2}$ the $\alpha$ terms dominate. Batch your
   scalar reductions into one array. This is a $\lg p\,\alpha$ saving per
   reduction you remove, per time step.
3. **The long-message algorithms all converge on $2\frac{p-1}{p}n\beta$**, i.e.
   about twice the data each process contributes, and *not* $n\lg p\,\beta$.
   That factor $\lg p$ is exactly what Rabenseifner's and Van de Geijn's
   algorithms remove, which is why "collectives do not scale" is a statement
   about a 1990s MPI, not about yours.
4. **`Alltoall` is the expensive one**: $(p-1)\alpha$ messages in the long case,
   all of them crossing the network at once. It is what limits FFT-based codes.
5. **`Barrier` costs $\lceil\lg p\rceil\alpha$ plus the idle time of the slowest
   rank, and is almost never needed for correctness** — message passing
   synchronises through data dependencies. The lecturer's own real-world example
   measures the price: removing three barriers from a production code took an
   8×8 case from 21 000 s to 3 500 s [S14]. Her slide says it in capitals:
   *"NEVER use MPI_BARRIER in production code!!!!!"* See
   [16](16-best-practice-and-debugging.md).

The crossover point between the "short" and "long" algorithm of a pair is where
the two expressions cross; MPICH simply hard-codes 2 kB for reduce [S20].
`mpi_cost.py` computes it for given $\alpha,\beta,\gamma$.

Floating-point reductions are not bitwise reproducible across P or even across runs (tree shape may change with message size); `pi_reduce.c` shows the parallel and serial sums differing in the last digits. If you need reproducibility, gather and sum in a fixed order.

## Pitfalls

- Not every rank calls the collective (an `if (rank == 0) MPI_Bcast(...)`): the others never match; hangs, or mismatches with a *later* collective and produces garbage.
- Collectives called in different order on different ranks (rank 0: Bcast then Reduce, rank 1: Reduce then Bcast): they match by order, not by name or argument: chaos.
- `recvcount` in `Gather` given as the total instead of per-rank; root buffer allocated too small.
- Passing the same pointer for send and receive buffer (aliasing) without `MPI_IN_PLACE`: erroneous.
- Mixing collectives and point-to-point so that a rank waits in `MPI_Recv` for a message that will only be sent after a collective the sender is stuck in.
- `MPI_Reduce` result read on a non-root rank: undefined (use `Allreduce`).
- Deadlock through two communicators: a collective on `comm_row` waiting for ranks that are inside a collective on `comm_col`.
- Non-blocking collective without `MPI_Wait`; or reading the buffer before it.
- Assuming the cost table above applies to *your* library: it is MPICH's algorithm selection [S20]. Open MPI and Intel MPI choose differently and by different thresholds. The table tells you what is *achievable* and what to expect asymptotically; a measurement on the target cluster tells you what happens — which is precisely the block-3 learning outcome about comparing methods "on this particular cluster" [S1].

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q2 and Q4 are what the `04_allreduce` lab makes you
discover [S11].

1. **Rank 0 has 1000 particle positions, P = 8 does not divide 1000. Which call distributes them, and what are `counts` and `displs`?**
   `MPI_Scatterv`; `counts = {125,125,125,125,125,125,125,125}` here it does divide; for N = 1001: `counts[0] = 126`, others 125, `displs = {0,126,251,...}` computed with the formula above.
2. **Why is `MPI_Allreduce` on one double "as expensive" as on 1000 doubles, and what should you do about it in a time loop with three scalar norms?**
   Below $n_{1/2}$ the time is dominated by $2 \alpha \log_2 P$, not by data; put the three norms into one array and do one `Allreduce`.
3. **What is wrong with `if (rank == 0) MPI_Bcast(data, n, MPI_INT, 0, comm);`?**
   Collectives must be called by all ranks; the other ranks never participate, rank 0 hangs (or matches a later collective of the others).
4. **Parallel and serial sum of the same numbers differ in the 14th digit. Bug?**
   No: floating-point addition is not associative; the reduction tree changes the summation order. Differences of a few ulp times the number of terms are expected. A large difference would be a bug.
5. **You replace a loop of $p-1$ `MPI_Send`s from the root by one `MPI_Bcast`. By what factor does the latency term improve at $p = 1024$, and why do you see nothing on 4 ranks?**
   From $(p-1)\alpha = 1023\alpha$ to $\lceil\lg p\rceil\alpha = 10\alpha$, a factor ~100 [S20]. At $p = 4$ it is $3\alpha$ against $2\alpha$ — within the noise, which is exactly what `collectives.c` measures on the laptop [S24].
6. **Your time loop does three `MPI_Allreduce` calls on one double each. What do you change, and what does it save?**
   One `Allreduce` on an array of three doubles. Saves $2\lg p\,\alpha$ per step; at $p=1024$, $\alpha = 1.5\,\mu$s that is 30 µs per step, which for $10^5$ steps is 50 minutes [S20].
