# 13 One-sided communication (RMA)

Block 3, **day 4, 09:00** [S13]. Lab `08_1sided` (`ring-1sided-win`,
`ring-1sided-put`, `ring-1sided-exa3`) [S11]. Code:
[`src/c/onesided.c`](../src/c/onesided.c). Semantics from MPI 5.0 §12 [S15].

## The idea

In point-to-point communication both sides participate: a send must meet a
receive. In **one-sided** communication — remote memory access, RMA — one
process does all the work. The other process exposes a region of its memory
once, and thereafter the **origin** reads from or writes to the **target**'s
memory without the target calling anything at all.

Why it exists:

- Hardware does this natively. InfiniBand-class networks perform RDMA: the NIC
  writes into remote memory with no involvement of the remote CPU. Two-sided
  MPI has to emulate the matching on top of that; one-sided maps onto it.
- Some algorithms have no natural receiver. Irregular, data-dependent access —
  a distributed hash table, an unstructured mesh whose neighbours change, a
  work-stealing queue — would otherwise need every process to poll for requests
  it cannot predict.
- It decouples synchronisation from data movement, so you can move many pieces
  and synchronise once.

The price is that "when is the data actually there?" becomes your problem, and
the rules are stricter than they look.

## Windows

A **window** is the memory a process exposes, plus a communicator. Creating one
is collective [S15]:

```c
/* (a) expose memory you already have */
MPI_Win_create(base, size_bytes, disp_unit, MPI_INFO_NULL, comm, &win);

/* (b) let MPI allocate it (may be faster: registered, aligned, symmetric) */
MPI_Win_allocate(size_bytes, disp_unit, MPI_INFO_NULL, comm, &baseptr, &win);

/* (c) shared memory - see note 14 */
MPI_Win_allocate_shared(size_bytes, disp_unit, MPI_INFO_NULL, comm, &baseptr, &win);

/* (d) attach and detach memory later */
MPI_Win_create_dynamic(MPI_INFO_NULL, comm, &win);   /* + MPI_Win_attach/_detach */

MPI_Win_free(&win);   /* collective; frees (b)/(c) memory too */
```

`disp_unit` is the unit in which displacements are counted — pass
`sizeof(double)` and you address the window in doubles rather than bytes. Every
process may expose a *different* size, including zero (a process that only reads
others' windows).

The **window memory is not your whole address space**: only what you exposed is
reachable, and each process's window is separate. `MPI_Win_create(&rcv_buf,
sizeof(int), sizeof(int), …)` — exposing a single `int` — is what the course's
ring lab does [S11].

## The three data-movement calls

```c
MPI_Put (origin_addr, origin_count, origin_type,
         target_rank, target_disp, target_count, target_type, win);   /* write  */
MPI_Get (origin_addr, origin_count, origin_type,
         target_rank, target_disp, target_count, target_type, win);   /* read   */
MPI_Accumulate(origin_addr, origin_count, origin_type,
         target_rank, target_disp, target_count, target_type, op, win); /* combine */
```

`MPI_Accumulate` applies a predefined reduction op (`MPI_SUM`, `MPI_REPLACE`,
…) at the target — the only way to have several origins update the same location
safely. MPI-3 added the "request-based" variants `MPI_Rput`, `MPI_Rget`,
`MPI_Raccumulate` (they return an `MPI_Request` you can `MPI_Wait` on
individually) and the read-modify-write primitives `MPI_Get_accumulate`,
`MPI_Fetch_and_op` and `MPI_Compare_and_swap`, which are what a distributed lock
or a work queue is built from [S15].

All of these are **non-blocking and unordered**. Nothing has happened until a
synchronisation call says so.

## Synchronisation: three models

This is where the difficulty lives. MPI defines an **epoch**: data movement is
only legal inside one, and is only complete when it closes [S15].

### 1. Fence — active target, collective, the simplest

```c
MPI_Win_fence(assert, win);     /* opens and/or closes an epoch; collective over the window */
MPI_Put(...);
MPI_Win_fence(assert, win);     /* after this returns, the Put is complete at the target */
```

Think "barrier for the window". It is the bulk-synchronous model: everyone
fences, everyone does their puts and gets, everyone fences again. This is what
the course uses [S11], and it is the right default.

The `assert` argument is a set of promises that let the implementation skip
work. Zero is always legal. The four that matter [S15]:

| assertion | promise |
|---|---|
| `MPI_MODE_NOSTORE` | the local window was not written by local stores since the last fence |
| `MPI_MODE_NOPUT` | the local window will not be updated by RMA until the next fence |
| `MPI_MODE_NOPRECEDE` | this fence does not **close** an epoch (no RMA precedes it) |
| `MPI_MODE_NOSUCCEED` | this fence does not **open** an epoch (no RMA follows it) |

The course's ring solution uses exactly
`MPI_Win_fence(MPI_MODE_NOSTORE | MPI_MODE_NOPRECEDE, win)` before the `Put` and
`MPI_Win_fence(MPI_MODE_NOSTORE | MPI_MODE_NOPUT | MPI_MODE_NOSUCCEED, win)`
after it [S11]. Read them as: "nothing to flush going in, and going out I
promise nobody is still writing." They are assertions, i.e. *your* promises —
get one wrong and the program is erroneous, with no diagnostic.

### 2. PSCW — active target, but only between the ranks that talk

```c
MPI_Win_post(group, assert, win);      /* target: my window is open to this group */
MPI_Win_start(group, assert, win);     /* origin: I am about to access this group */
   MPI_Put(...);
MPI_Win_complete(win);                 /* origin: my accesses are issued          */
MPI_Win_wait(win);                     /* target: all accesses to me are done     */
```

Same semantics as fence but scoped to the neighbour groups instead of the whole
communicator — the natural fit for a halo exchange, where each process only ever
talks to its 2*d* neighbours and a collective fence would over-synchronise
[S15].

### 3. Lock / unlock — passive target, the target does nothing at all

```c
MPI_Win_lock(MPI_LOCK_SHARED /* or _EXCLUSIVE */, target, assert, win);
MPI_Get(...);
MPI_Win_unlock(target, win);

MPI_Win_lock_all(assert, win);      /* lock every rank once, at start-up   */
   MPI_Put(...);  MPI_Win_flush(target, win);     /* complete, keep the lock */
MPI_Win_unlock_all(win);
```

The target never calls anything — this is the true one-sided model, and the one
that makes a distributed hash table possible. `MPI_Win_flush`,
`MPI_Win_flush_local` and `MPI_Win_flush_all` complete operations without
closing the epoch [S15]. "Lock" is a misnomer: `MPI_LOCK_SHARED` does not
exclude other origins, it only opens an access epoch.

## The course's example: the ring, again

`ring-1sided-put` replaces the message passing of [08](08-point-to-point.md) by
a window on a single `int` and a `Put` into the right neighbour's window [S11]:

```c
MPI_Win_create(&rcv_buf, sizeof(int), sizeof(int), MPI_INFO_NULL, MPI_COMM_WORLD, &win);
sum = 0; snd_buf = my_rank;
for (int i = 0; i < size; i++) {
    MPI_Win_fence(MPI_MODE_NOSTORE | MPI_MODE_NOPRECEDE, win);
    MPI_Put(&snd_buf, 1, MPI_INT, right, (MPI_Aint)0, 1, MPI_INT, win);
    MPI_Win_fence(MPI_MODE_NOSTORE | MPI_MODE_NOPUT | MPI_MODE_NOSUCCEED, win);
    snd_buf = rcv_buf;
    sum += rcv_buf;
}
```

and the answer is the same invariant as everywhere else in the block,
$\sum_{r=0}^{P-1} r = P(P-1)/2$ [S11]. Note what disappeared: no tags, no
`MPI_Status`, no deadlock question, and no receive. Note what appeared: two
fences per iteration, which is why this version is *not* automatically faster.
One-sided pays off when you can move many items per epoch, not one.

## Rules you can break without noticing

The RMA memory model is the strictest part of MPI [S15]. The ones that bite:

- **Do not access a window location with local loads/stores and with RMA in the
  same epoch.** Reading `rcv_buf` between the two fences in the loop above is
  erroneous; reading it *after* the closing fence is correct.
- **Concurrent conflicting accesses are erroneous**, even if they look benign.
  Two `MPI_Put`s to the same location in one epoch: undefined. Use
  `MPI_Accumulate` with `MPI_REPLACE`, which *is* defined for concurrent
  updates.
- MPI defines a *separate* and a *unified* memory model. On cache-coherent
  hardware the unified model applies and public and private copies are the same
  memory; portable code must not assume it. `MPI_Win_get_attr(win,
  MPI_WIN_MODEL, …)` tells you which you have.
- An assertion you got wrong is not diagnosed. `MPI_MODE_NOSTORE` when you did
  store, or `MPI_MODE_NOPRECEDE` when RMA did precede, silently corrupts.

## When one-sided is the right answer

- Irregular or data-dependent access patterns (hash tables, adaptive meshes,
  graph algorithms, work stealing) — the target cannot know what to receive.
- Hardware RDMA with very low latency and many small accesses, batched into one
  epoch.
- Shared memory within a node — [14](14-shared-memory-one-sided.md), where
  `MPI_Put` degenerates into an ordinary store and the win is real.

And when it is not: a regular halo exchange with a small, fixed neighbour set.
Two-sided `MPI_Sendrecv` or `Irecv`/`Isend` expresses it in one line, the
library already knows the pattern, and you do not have to reason about epochs.

## Pitfalls

- Two fences per single small transfer — as in the ring lab — and then
  concluding "one-sided is slow". It is the synchronisation, not the transfer.
  Batch.
- Reading the target buffer before the closing fence.
- Forgetting that `MPI_Win_create` and `MPI_Win_free` are collective.
- Passing a byte offset when `disp_unit` is `sizeof(double)` (or the reverse).
- Assuming `MPI_Win_lock(MPI_LOCK_EXCLUSIVE)` gives mutual exclusion against
  processes that are not locking. It does not; it is an epoch, not a mutex.
- Using `MPI_Put` for a value several origins update. `MPI_Accumulate`.
- Leaving a window allocated per time step: a resource leak like any other.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1, Q2 and Q5 are what the `08_1sided` lab asks you
to work through [S11].

1. **Rewrite the ring with `MPI_Put`. What replaces the receive, and what does
   the program print for $P = 4$?** Nothing replaces it — the neighbour writes
   directly into your window. Bracket the `Put` with two `MPI_Win_fence` calls
   and read your window afterwards; the sum is still $P(P-1)/2 = 6$ [S11].
2. **Why is reading `rcv_buf` *between* the two fences wrong, even though the
   `Put` targeting you has "obviously" arrived?** Because the epoch has not
   closed: mixing local loads with RMA on the same location in one epoch is
   erroneous by the standard, whatever the implementation happens to do [S15].
3. **What do `MPI_MODE_NOSTORE` and `MPI_MODE_NOPRECEDE` promise, and who is
   harmed if you are wrong?** That you did not write the local window with
   ordinary stores since the last fence, and that no RMA operation precedes this
   fence. They let MPI skip flushes; if they are false the data is silently
   wrong and nothing warns you [S15].
4. **Name a case where one-sided clearly beats two-sided, and one where it
   clearly does not.** Beats: a distributed hash table, where the target cannot
   know which key you will ask for. Does not: a 3D stencil halo exchange with a
   fixed neighbour set, where `MPI_Sendrecv` is shorter and the library already
   knows the pattern.
5. **Three origins want to add to the same counter on rank 0 in one epoch.
   Which call, and why not `MPI_Put`?** `MPI_Accumulate` with `MPI_SUM`.
   Concurrent conflicting `MPI_Put`s to one location are erroneous;
   accumulate is defined for exactly this [S15].
6. **Give the synchronisation model for each of: bulk-synchronous stencil;
   halo exchange with 6 neighbours; a work-stealing queue.** Fence; PSCW
   (`post`/`start`/`complete`/`wait`); passive-target `lock_all` + `flush` with
   `MPI_Fetch_and_op` or `MPI_Compare_and_swap` [S15].
