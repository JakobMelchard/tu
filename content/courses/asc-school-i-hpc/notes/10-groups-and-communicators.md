# 10 Groups and communicators

Block 3, **day 3, 09:00** [S13]. Lab `05_comm-split` [S11]. Code:
[`src/c/comm_split.c`](../src/c/comm_split.c). Semantics from MPI 5.0 §7 [S15].

Days 1 and 2 use exactly one communicator, `MPI_COMM_WORLD`. Day 3 is about
making your own, and it is the first thing in the course that changes how you
*structure* a parallel program rather than how you move bytes.

## Group, context, communicator

A **group** is an ordered set of processes; each has a rank $0 \dots n-1$ within
it. A **communicator** is a group **plus a communication context** [S15]. The
context is the part people forget and the part that matters: it is an opaque tag
that MPI adds to every message, so a message sent on one communicator can never
be received on another. That is what makes libraries safe — a solver that does
`MPI_Comm_dup(MPI_COMM_WORLD, &mycomm)` at start-up cannot have its messages
intercepted by the application, and vice versa, no matter what tags either side
uses.

Predefined: `MPI_COMM_WORLD` (all processes started by the launcher),
`MPI_COMM_SELF` (just me), `MPI_COMM_NULL` (the "no communicator" value).

**Ranks are per communicator.** A process has a different number in each
communicator it belongs to, and translating between them is the source of most
confusion. `MPI_Group_translate_ranks(g1, n, ranks1, g2, ranks2)` does it
explicitly; `MPI_UNDEFINED` comes back for processes not in `g2`.

## `MPI_Comm_split` — the workhorse

```c
int MPI_Comm_split(MPI_Comm comm, int color, int key, MPI_Comm *newcomm);
```

Collective over `comm`. Every process passes a `color`; all processes with the
same colour end up in one new communicator, ordered by `key` (ties broken by the
old rank). `color = MPI_UNDEFINED` opts out and yields `MPI_COMM_NULL` [S15].

```c
int world_rank, world_size;
MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
MPI_Comm_size(MPI_COMM_WORLD, &world_size);

int color = (world_rank < world_size / 2) ? 0 : 1;   /* two halves */
MPI_Comm sub;
MPI_Comm_split(MPI_COMM_WORLD, color, world_rank, &sub);

int sub_rank, sub_size;
MPI_Comm_rank(sub, &sub_rank);
MPI_Comm_size(sub, &sub_size);
/* ... collectives here act on half the processes ... */
MPI_Comm_free(&sub);
```

That is the `05_comm-split` lab in three lines. The exercise's point is made by
running the *same* `MPI_Allreduce(&world_rank, …, MPI_SUM, …)` on
`MPI_COMM_WORLD` and on `sub` and comparing: for $P = 4$ the world sum is
$0+1+2+3 = 6$ on every rank, while the sub-communicator sums are $0+1 = 1$ for
ranks 0–1 and $2+3 = 5$ for ranks 2–3 [S11]. Two numbers to check against, and
they generalise: for $P$ even, world $= P(P-1)/2$, lower half $= \frac{P}{2}
\cdot \frac{P/2-1}{2}$, upper half $= \frac{P}{2}\cdot\frac{3P/2-1}{2}$.

Three standard colourings:

| goal | colour | key |
|---|---|---|
| rows of a 2D process grid | `rank / ncols` | `rank % ncols` |
| columns of the same grid | `rank % ncols` | `rank / ncols` |
| one communicator per node | see `MPI_Comm_split_type` below | `0` |

## `MPI_Comm_split_type` — "everyone on my node"

```c
MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL, &comm_sm);
```

Splits by a property the implementation knows, not one you compute. With
`MPI_COMM_TYPE_SHARED` the new communicator contains exactly the processes that
*can share memory with you* — in practice, the ranks on your node [S15]. This is
the doorway to [14](14-shared-memory-one-sided.md), and it is how a hybrid code
finds out how many ranks it has per node without parsing hostnames. MPI 4.0
added `MPI_COMM_TYPE_HW_GUIDED` for finer hardware levels (socket, NUMA domain)
with an info key.

Useful test in a course lab: if `size(comm_sm) == size(MPI_COMM_WORLD)` you are
running inside a single shared-memory region; otherwise the job spans several
"islands" [S11].

## Building communicators from groups

The long way round, when a colour cannot express what you want:

```c
MPI_Group world_grp, sub_grp;
MPI_Comm_group(MPI_COMM_WORLD, &world_grp);              /* extract the group */
int ranks[3] = {0, 3, 7};
MPI_Group_incl(world_grp, 3, ranks, &sub_grp);           /* or _excl, _range_incl */
MPI_Comm_create(MPI_COMM_WORLD, sub_grp, &sub);          /* collective over the OLD comm */
MPI_Group_free(&world_grp); MPI_Group_free(&sub_grp);
```

Also `MPI_Group_union`, `_intersection`, `_difference`, `MPI_Group_rank`,
`_size`, `_compare` [S15]. `MPI_Comm_create` is collective over the parent and
gives `MPI_COMM_NULL` to processes not in the group;
`MPI_Comm_create_group` is collective only over the group, which is much cheaper
when you build many small communicators.

Other constructors worth knowing: `MPI_Comm_dup` (same group, fresh context —
what libraries do), `MPI_Comm_compare` (`MPI_IDENT`, `MPI_CONGRUENT`,
`MPI_SIMILAR`, `MPI_UNEQUAL`), and **inter-communicators**
(`MPI_Intercomm_create`, `MPI_Intercomm_merge`), which connect two disjoint
groups and are what the client–server and coupled-model patterns use [S15].

## Why you would bother

1. **Collectives on a subset.** A 2D matrix algorithm wants a sum along each row
   of the process grid, not over everybody. Row communicators turn that into one
   `MPI_Allreduce` per row, running in parallel.
2. **Two-level algorithms.** Reduce inside each node on `comm_sm`, then across
   nodes on a communicator of the node leaders. Turns $P$ participants into
   $P/c + c$ and is how most "hierarchical collective" tuning works.
3. **Library isolation.** `MPI_Comm_dup` once, use it forever.
4. **Different work on different groups.** I/O ranks, worker ranks, a coupled
   ocean and atmosphere in one `mpirun`.
5. **Topologies.** `MPI_Cart_create` is itself a communicator constructor —
   [11](11-virtual-topologies.md).

## Pitfalls

- **`MPI_Comm_split` is collective over the *old* communicator.** Every process
  in `comm` must call it, including the ones that pass `MPI_UNDEFINED`. An
  `if (rank < n) MPI_Comm_split(...)` hangs.
- Using a world rank where a sub-communicator rank is wanted. `MPI_Send(...,
  dest=3, ..., sub)` sends to rank 3 *of `sub`*, which is some other process
  entirely. Recompute with `MPI_Comm_rank(sub, …)` after every split.
- Forgetting `MPI_Comm_free` / `MPI_Group_free` in a loop: communicators are a
  finite resource and you will run out after a few thousand.
- Assuming the sub-communicator preserves the old rank order — it does, but only
  because you passed the old rank as `key`. Pass `0` for everyone and the order
  is unspecified-but-consistent, which is rarely what you want.
- Two communicators, two collectives, different order on different ranks: a
  deadlock that no single-communicator reasoning will find
  ([09](09-collectives.md)).
- Treating a context like a tag. Tags do not isolate; only communicators do.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1 and Q2 are the `05_comm-split` lab in words [S11].

1. **Split `MPI_COMM_WORLD` into two halves and `Allreduce` the world rank in
   each. For $P = 4$, what does each rank print for the world sum and for the
   sub sum?** World sum 6 everywhere; sub sum 1 on ranks 0 and 1, 5 on ranks 2
   and 3 [S11].
2. **In that program, why must every rank call `MPI_Comm_split`, even the ones
   whose colour you do not care about?** It is collective over
   `MPI_COMM_WORLD`; a rank that skips it leaves the others waiting forever
   [S15].
3. **Give the colour and key that build (a) row communicators and (b) column
   communicators of a $r \times c$ process grid laid out row-major.**
   (a) `color = rank / c`, `key = rank % c`; (b) `color = rank % c`,
   `key = rank / c`.
4. **What does a communication context buy you that a reserved tag range does
   not?** Isolation that the application cannot break. A library that dups a
   communicator is safe against *any* tag the application chooses, including
   `MPI_ANY_TAG` receives [S15].
5. **How do you find out, portably, how many of your ranks are on the same node,
   without looking at hostnames?**
   `MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL,
   &c)` then `MPI_Comm_size(c, &n)` [S15].
6. **You build one communicator per time step inside the main loop and the run
   dies after an hour with an MPI resource error. Why?** Communicators are
   objects the library allocates; without `MPI_Comm_free` they accumulate. Build
   it once outside the loop.
