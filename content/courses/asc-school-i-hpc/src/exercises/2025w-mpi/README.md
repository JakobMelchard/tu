# Block-3 hands-on labs — 17–20 November 2025 instance

The MPI block of 057.020 has nine hands-on labs, done during the four mornings
alone or in pairs, in C, Fortran **or** Python (mpi4py), on the ASC JupyterHub
[S11] [S13]. They are the "submitted program examples" that the examination
modalities refer to [S1], and they are the only assessed work in the course
([`../../../notes/00-exam-focus.md`](../../../notes/00-exam-focus.md)).

The official skeletons and solutions are public — `git clone
https://gitlab.tuwien.ac.at/vsc-public/training/MPI`, or run
[`../../../refs/fetch-sources.sh`](../../../refs/fetch-sources.sh), which puts
them in `refs/cite-only/mpi/`. They are **not** copied here: the repository
states CC BY-SA 4.0 for the notebooks but also that some exercise descriptions,
images and code snippets in it are HLRS-copyrighted and used with permission
granted to its author, which is not a licence we can rely on
([`../../../refs/README.md`](../../../refs/README.md)).

What follows is therefore **a description in our own words of what each lab
asks**, and our own independent solutions.

## What the nine labs ask

| lab | in one sentence | our version |
|---|---|---|
| `01_hello` | Compile and run a serial program, then a minimal MPI one; make every process print its rank and the size of `MPI_COMM_WORLD` and only rank 0 print "Hello world"; then explain why the output order is non-deterministic and how you would order it. | [`../../c/hello_mpi.c`](../../c/hello_mpi.c) |
| `02_pingpong` | Send a message back and forth between two ranks, time it over many repetitions, sweep the message size, and read latency and bandwidth off the curve. | [`../../c/pingpong.c`](../../c/pingpong.c) |
| `03_ring` | Fix a deliberately broken ring: the handed-out file does `MPI_Send` then `MPI_Recv` on every rank into the same buffer, which its own comment marks as wrong because it deadlocks under a synchronous protocol. Make it correct with non-blocking calls. | [`ring_variants.c`](ring_variants.c), variants 0–4 |
| `04_allreduce` | Replace that whole ring loop by a single `MPI_Allreduce`, and then do the prefix-sum version with `MPI_Scan`. | [`ring_variants.c`](ring_variants.c), variants 5–6 |
| `05_comm-split` | Split `MPI_COMM_WORLD` into sub-communicators with `MPI_Comm_split`, run the same reduction on both, and see that the answers differ. | [`../../c/comm_split.c`](../../c/comm_split.c) |
| `06_virtual_cartesian_topologies` | Build the ring as a 1D periodic Cartesian communicator; get the neighbours from `MPI_Cart_shift` instead of computing them; note that `reorder` may renumber the ranks. | [`../../c/cart_topology.c`](../../c/cart_topology.c) |
| `07_derived-datatypes` | Build a datatype for a C `struct` / Fortran derived type and send an array of them in one call. | [`../../c/derived_types.c`](../../c/derived_types.c) |
| `08_1sided` | Do the ring again with an RMA window and `MPI_Put`, bracketed by `MPI_Win_fence`. | [`../../c/onesided.c`](../../c/onesided.c) |
| `09_1sided-shmem` | Allocate a *shared* window with `MPI_Win_allocate_shared` on the shared-memory communicator and replace the `MPI_Put` by a plain assignment into the neighbour's piece. | [`../../c/shmem_onesided.c`](../../c/shmem_onesided.c) |

## The one number to check against

Labs 03, 04, 06, 08 and 09 are the same computation. Each rank starts holding
its own rank number and passes it around a ring of $P$ processes $P$ times,
accumulating. Every rank must end with

$$\texttt{sum} = \sum_{r=0}^{P-1} r = \frac{P(P-1)}{2}$$

— 1 for $P=2$, 6 for $P=4$, 28 for $P=8$. Lab 09 runs on the shared-memory
communicator, so its answer is $P_\text{sm}(P_\text{sm}-1)/2$ with
$P_\text{sm}$ the ranks on *your node* — identical on one node, different across
nodes, which is the point of that lab.

## `ring_variants.c`

Seven implementations of that ring in one file, each asserting the invariant:

| # | mechanism | what it demonstrates |
|---|---|---|
| 0 | ordered `Send`/`Recv` | one rank receives first; no buffering assumed |
| 1 | `Sendrecv` | MPI orders the pair internally |
| 2 | `Sendrecv_replace` | one buffer |
| 3 | `Issend` + `Recv` + `Wait` | the course's own answer: a **synchronous** non-blocking send, so a correct run proves correctness rather than luck |
| 4 | `Irecv` + `Issend` + `Waitall` | post the receive first |
| 5 | `Allreduce` | the whole loop in one collective (lab 04) |
| 6 | `Scan` + `Bcast` | inclusive prefix; rank $P-1$ holds the total |

The deliberately **wrong** version is not in this file. It is in
[`../../c/deadlock.c`](../../c/deadlock.c), which runs it under an `alarm()` so
that the hang is observable and turns into a non-zero exit code instead of
wedging the test suite:

```sh
mpirun --oversubscribe -np 4 ../../c/deadlock --unsafe recv-first -t 3   # always hangs
mpirun --oversubscribe -np 4 ../../c/deadlock --unsafe send-first        # hangs above the eager limit
```

### Why variant 0 is not "even ranks send first"

The textbook fix for a *pairwise* exchange — even ranks send first, odd ranks
receive first — is **wrong for a ring with an odd number of processes**: rank 0
and rank $P-1$ are then both even, both send first, and nothing in that cycle is
receiving. A ring needs exactly one rank to invert the order. Rank $P-1$'s send
matches rank 0's receive; rank $P-1$ then posts its own receive, which releases
rank $P-2$, and the release cascades backwards until rank 1's send releases rank
0's. No step depends on buffering, so it is correct at any message size and for
any $P \ge 2$. Run it with `-np 3` and `-np 7` to see that it matters.

## Build and run

```sh
mpicc -O2 -Wall -Wextra ring_variants.c -o ring_variants
mpirun --oversubscribe -np 4 ./ring_variants
mpirun --oversubscribe -np 7 ./ring_variants     # odd P
```

or, from `src/`, `make -C c test` builds and runs this together with everything
else. On a cluster, inside a job: `srun ./ring_variants`.

Sources for this page: [S11] (the lab list and the skeletons' own comments),
[S13] (the agenda that maps labs to sessions), [S1] (the examination
modalities). Full entries in
[`../../../refs/SOURCES.md`](../../../refs/SOURCES.md).
