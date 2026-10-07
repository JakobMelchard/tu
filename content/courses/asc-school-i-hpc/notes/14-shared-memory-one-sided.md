# 14 Shared-memory one-sided communication (MPI+MPI)

Block 3, **day 4, 10:45** [S13]. Lab `09_1sided-shmem`
(`ring-1sided-put-win-alloc-shared`, `ring-1sided-store-win-alloc-shared`)
[S11]. Code: [`src/c/shmem_onesided.c`](../src/c/shmem_onesided.c). Semantics
from MPI 5.0 §12.2.3 and §7.4.2 [S15].

## The point

A cluster is distributed memory *between* nodes and shared memory *inside* one
([04](04-cluster-anatomy.md)). The usual way to exploit that is hybrid
MPI+OpenMP: fewer ranks, threads inside ([07](07-mpi-concepts.md)). MPI-3 offers
a second way, usually called **MPI+MPI**: keep one rank per core, but let the
ranks on a node allocate a genuinely shared memory region and access it with
ordinary loads and stores.

What that buys you over MPI+OpenMP:

- **No second programming model.** No pragmas, no thread-safety level, no
  `MPI_THREAD_MULTIPLE` performance cliff. One rank per core throughout.
- **No replication.** A large read-only table — a lookup table, a mesh
  connectivity array, an interpolation grid — is stored **once per node**
  instead of once per rank. On a 128-core VSC-5 node that is a factor 128 in
  memory for that array [S19].
- **Zero-copy intra-node exchange.** The neighbour's halo is at an address you
  can dereference.

What it costs: you are back to shared-memory reasoning — races, false sharing,
and a synchronisation model that MPI expresses through window calls rather than
through anything a thread sanitiser understands.

## Two calls and a pointer

```c
/* 1. Who can share memory with me? */
MPI_Comm comm_sm;
MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL, &comm_sm);
MPI_Comm_rank(comm_sm, &rank_sm);
MPI_Comm_size(comm_sm, &size_sm);

/* 2. Allocate a window that is really shared */
int *ptr;
MPI_Win_allocate_shared((MPI_Aint) sizeof(int), sizeof(int),
                        MPI_INFO_NULL, comm_sm, &ptr, &win);

/* 3. Where is somebody else's piece? */
MPI_Aint sz; int disp_unit; int *other;
MPI_Win_shared_query(win, target_rank_sm, &sz, &disp_unit, &other);
```

`MPI_Win_allocate_shared` is collective over a communicator whose processes
*can* share memory — which is exactly what `MPI_Comm_split_type` with
`MPI_COMM_TYPE_SHARED` produced [S15]. Every process contributes a piece; the
pieces are, by default, **contiguous in the shared segment in rank order**, so
`ptr + (k - rank_sm) * count` addresses rank `k`'s piece. That is the trick the
course's solution uses:

```c
/* MPI_Put(&snd_buf, 1, MPI_INT, right, 0, 1, MPI_INT, win)  becomes */
*(rcv_buf_ptr + (right - my_rank_sm)) = snd_buf;      /* an ordinary store */
```

— a one-line replacement of a communication call by an assignment [S11].

Relying on contiguity is legal only because of the default;
`MPI_Info` key `alloc_shared_noncontig = "true"` asks for per-rank alignment
instead (usually better, because it puts each rank's piece on its own page and
NUMA domain), and then you **must** use `MPI_Win_shared_query` [S15]. Portable
code queries.

## Synchronisation

The window calls still apply, and they are what makes the stores visible:

```c
MPI_Win_fence(0, win);          /* everyone on the node arrives            */
*(ptr + (right - rank_sm)) = snd_buf;    /* plain store into a neighbour's piece */
MPI_Win_fence(0, win);          /* the store is now visible to everyone    */
sum += *ptr;
```

Two fences per exchange, as in [13](13-one-sided.md). The ASC solution passes
assertion `0` here with the comment *"workaround: no assertions"* [S11] — a
useful reminder that the fence assertions of note 13 describe RMA operations and
are easy to get wrong once ordinary stores are in the mix. The alternative to a
fence is `MPI_Win_lock_all` + `MPI_Win_sync` (a memory barrier for the window)
plus your own `MPI_Barrier(comm_sm)` [S15].

For a read-mostly table the pattern is simpler still: rank 0 of `comm_sm`
allocates the whole thing (others pass size 0), fills it, one fence, and
everyone reads it for the rest of the run.

## The result to check against

`09_1sided-shmem` is the ring one last time, on `comm_sm` instead of
`MPI_COMM_WORLD`, so the invariant becomes

$$\texttt{sum} = \frac{P_\text{sm}(P_\text{sm}-1)}{2}$$

with $P_\text{sm}$ the number of ranks **on your node** [S11]. The lab prints
whether `MPI_COMM_WORLD` is one shared-memory region or several "islands",
which is the second thing it teaches: on a laptop or a single-node job the two
communicators coincide and the sum equals the world sum; on a multi-node job
they do not, and a program that assumed they did is now wrong.

That is the honest limitation of MPI+MPI: **it only works inside a node.** A
complete code needs a second level — the usual shape is shared memory within a
node, and two-sided MPI between the node leaders, using a communicator built
with `MPI_Comm_split(MPI_COMM_WORLD, rank_sm == 0 ? 0 : MPI_UNDEFINED, …)`
([10](10-groups-and-communicators.md)).

## MPI+MPI versus MPI+OpenMP

| | MPI+MPI (shared windows) | MPI+OpenMP |
|---|---|---|
| unit | one process per core | one process per node/socket, threads inside |
| second model to learn | none (MPI only) | OpenMP |
| replicated data | one copy per **node** | one copy per **process** |
| thread level needed | `MPI_THREAD_SINGLE` | at least `FUNNELED`, often more |
| load balance inside a node | manual | `schedule(dynamic)` for free |
| what goes wrong | races and window synchronisation | races, false sharing, NUMA first touch |
| cost of a call into MPI | unchanged | `MULTIPLE` can be expensive |

Neither dominates. The memory row is the one that decides it in practice: if a
big read-only structure is what forces you to use fewer ranks, shared windows
solve exactly that problem without touching the rest of the code. OpenMP itself
is a separate ASC training event, not part of 057.020 [S5]; the write-up is in
the sibling course [S23].

## Pitfalls

- **Assuming `comm_sm` is `MPI_COMM_WORLD`.** True on one node, false on two,
  and the bug appears only when you scale up. The lab prints the distinction on
  purpose [S11].
- Assuming contiguity without setting/checking it. Use
  `MPI_Win_shared_query`, or accept the default explicitly and say so in a
  comment [S15].
- Writing another rank's piece without any window synchronisation and expecting
  it to be seen. Compilers and hardware reorder; `MPI_Win_fence` or
  `MPI_Win_sync` is what makes it visible.
- Two ranks on a node writing adjacent `int`s in the same cache line, in a loop:
  **false sharing**, and the shared window makes it easy to write by accident.
- Forgetting that `MPI_Win_free` frees the memory `MPI_Win_allocate_shared`
  gave you — the pointer dangles afterwards.
- Allocating the big table on every rank "just to be safe", which throws away
  the entire point.
- Using shared windows to communicate *between* nodes. There is no such thing;
  that is what [13](13-one-sided.md) and the rest of MPI are for.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1, Q2 and Q4 are the `09_1sided-shmem` lab in words
[S11].

1. **Replace the `MPI_Put` of the ring by a plain store. What is the expression,
   and what has to hold for it to be legal?**
   `*(ptr + (right - rank_sm)) = snd_buf;`. It is legal because
   `MPI_Win_allocate_shared` lays the per-rank pieces out contiguously in rank
   order by default; with `alloc_shared_noncontig` you must get the address from
   `MPI_Win_shared_query` instead [S11] [S15].
2. **Why is the sum $P_\text{sm}(P_\text{sm}-1)/2$ and not $P(P-1)/2$?**
   The ring runs on `comm_sm`, the processes sharing memory with you, not on
   `MPI_COMM_WORLD`. On a single node they coincide; across nodes they do not
   [S11].
3. **How do you find `comm_sm` without parsing hostnames?**
   `MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL,
   &comm_sm)` [S15].
4. **You still need two `MPI_Win_fence` calls around a plain assignment. Why is
   the assignment not enough?** The fence is what makes the store visible to the
   other processes' view of the window and what orders it against their reads;
   without it you have a data race with no synchronisation point [S15].
5. **A 4 GB read-only table, 128 ranks on a VSC-5 node with 512 GB. What happens
   with plain MPI, and what with a shared window?** Plain MPI: $128\times4$ GB =
   512 GB, i.e. the node's entire memory, so it does not run. Shared window: one
   copy per node, 4 GB, and 508 GB left for the actual work [S19].
6. **Name one thing MPI+OpenMP gives you that MPI+MPI does not, and one the
   other way round.** OpenMP: dynamic load balancing inside the node for free.
   MPI+MPI: no second programming model and no MPI thread-level requirement
   above `MPI_THREAD_SINGLE`.
