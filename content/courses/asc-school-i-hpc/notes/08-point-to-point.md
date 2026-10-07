# 08 Point-to-point communication

Block 3, **day 1 afternoon and day 2 morning**: *"Messages and point-to-point
communication"*, then *"Ping pong benchmark — solution and results"* and
*"Nonblocking communication"* [S13]. Labs `02_pingpong` and `03_ring` [S11].

Code: [`src/c/sendrecv.c`](../src/c/sendrecv.c) (Send/Recv, status, tags,
Sendrecv, Probe), [`src/c/deadlock.c`](../src/c/deadlock.c) (the deadlock and
four fixes, `--unsafe recv-first` shows the hang),
[`src/c/nonblocking.c`](../src/c/nonblocking.c) (Isend/Irecv/Wait/Test/Waitany,
overlap), [`src/c/pingpong.c`](../src/c/pingpong.c) (timing),
[`src/exercises/2025w-mpi/ring_variants.c`](../src/exercises/2025w-mpi/ring_variants.c)
(the course's ring, seven ways).

Every signature and semantic statement below is MPI 5.0 §3 [S15].

## Send and Recv

```c
int MPI_Send(const void *buf, int count, MPI_Datatype type, int dest,   int tag, MPI_Comm comm);
int MPI_Recv(void *buf,       int count, MPI_Datatype type, int source, int tag, MPI_Comm comm, MPI_Status *status);
```

`count` on the receive is the *capacity* of the buffer; the message may be shorter, never longer (`MPI_ERR_TRUNCATE`). `status.MPI_SOURCE`, `status.MPI_TAG` tell what matched (needed with wildcards), `MPI_Get_count(&status, type, &n)` how many elements arrived; pass `MPI_STATUS_IGNORE` if you do not care. Tags are non-negative ints up to at least 32767; use them to label message kinds, not to number messages. `MPI_PROC_NULL` as source/destination makes the call a no-op (boundary ranks in a stencil, `heat1d_halo.c`).

**Matching**: a receive matches the *earliest* posted message from the given source (or any) with the given tag (or any) in this communicator. Messages between one sender and one receiver are **non-overtaking**: if A sends m1 then m2 to B and both match the same receive, m1 is received first. Nothing is guaranteed about messages from different senders.

## Blocking semantics and buffering

**Blocking** means: when the call returns, the *buffer* may be reused. It does *not* mean the matching operation has happened. For `MPI_Recv` the two coincide (the data is in the buffer). For `MPI_Send` (standard mode) the implementation chooses:

- **eager** protocol for small messages (below the *eager limit*, ~4-64 KB depending on the transport): the data is copied into an internal buffer on the sender or pushed to the receiver's unexpected-message buffer, and `MPI_Send` returns *before* the receiver has called `MPI_Recv`;
- **rendezvous** for large messages: the sender waits until the receiver has posted a matching receive, then transfers directly; `MPI_Send` blocks until the receiver is there.

Consequence: a program that relies on `MPI_Send` returning early is correct only by luck for small messages and hangs once the message size crosses the eager limit (`deadlock.c --unsafe send-first -n 1` vs `-n 1000000`). The standard says: a correct program must not depend on buffering.

Explicit modes: `MPI_Ssend` (synchronous, returns only after the receive matched: use it in testing to expose buffering dependence), `MPI_Bsend` (buffered in a user-attached buffer, `MPI_Buffer_attach`), `MPI_Rsend` (ready: receive must already be posted; rare).

## Deadlock patterns

Ring exchange: every rank sends to the right and receives from the left.

1. `Recv; Send` on every rank: **always** deadlocks. Everyone waits in `Recv` for a message nobody has sent yet.
2. `Send; Recv` on every rank: deadlocks for messages above the eager limit (everyone is stuck in a rendezvous `Send`). Works "by accident" for small messages.
3. Two ranks that both `Send` a large array to each other, then `Recv`: same as 2.
4. A collective on some ranks while others are in a point-to-point that waits for them: mixed deadlock ([09](09-collectives.md)).

Fixes, in order of preference:

```c
/* a) MPI_Sendrecv: send and receive in one call, MPI orders them internally; never deadlocks */
MPI_Sendrecv(sbuf, n, MPI_INT, right, 0, rbuf, n, MPI_INT, left, 0, comm, MPI_STATUS_IGNORE);
MPI_Sendrecv_replace(buf, n, MPI_INT, right, 0, left, 0, comm, MPI_STATUS_IGNORE);   /* same buffer */

/* b) non-blocking: post the receive, post the send, do something else, wait for both */
MPI_Request req[2];
MPI_Irecv(rbuf, n, MPI_INT, left, 0, comm, &req[0]);
MPI_Isend(sbuf, n, MPI_INT, right, 0, comm, &req[1]);
MPI_Waitall(2, req, MPI_STATUSES_IGNORE);

/* c) break the symmetry: even ranks send first, odd ranks receive first (needs care with odd P) */
if (rank % 2 == 0) { MPI_Send(...); MPI_Recv(...); } else { MPI_Recv(...); MPI_Send(...); }

/* d) MPI_Bsend with an attached buffer: legal, but you manage the buffer size and pay a copy */
```

## Non-blocking communication

```c
int MPI_Isend(const void *buf, int count, MPI_Datatype t, int dest, int tag, MPI_Comm c, MPI_Request *req);
int MPI_Irecv(void *buf, int count, MPI_Datatype t, int src, int tag, MPI_Comm c, MPI_Request *req);
int MPI_Wait(MPI_Request *req, MPI_Status *st);                  /* block until complete */
int MPI_Test(MPI_Request *req, int *flag, MPI_Status *st);       /* poll */
int MPI_Waitall(int n, MPI_Request reqs[], MPI_Status sts[]);    /* also Waitany, Waitsome, Testall, Testany */
```

The `I` calls return immediately with a **request** handle; the operation proceeds "in the background" (in practice: whenever the MPI library gets CPU time, i.e. inside other MPI calls, or through hardware offload on real interconnects). Between the post and the completion the buffer belongs to MPI: do not write a send buffer, do not read a receive buffer. Every request must be completed by a `Wait`/`Test` (or `MPI_Request_free`), otherwise it leaks and `MPI_Finalize` may hang.

Three uses: (1) deadlock-free exchanges (post all receives first, then sends, then wait), (2) **overlap** of communication with computation: start the halo exchange, update the interior points that do not need the halo, wait, update the boundary points, (3) receiving from many sources in arrival order with `MPI_Waitany` (a master collecting results). `nonblocking.c` shows all three and measures the overlap gain.

Persistent requests (`MPI_Send_init`/`MPI_Recv_init` + `MPI_Start` + `MPI_Wait`) avoid re-creating the same request every time step; partitioned communication is the MPI-4 extension.

## Probe and unknown message sizes

`MPI_Probe(source, tag, comm, &status)` blocks until a matching message is *available*, without receiving it; `MPI_Get_count` on the status gives its length so you can `malloc` and then `MPI_Recv` it. `MPI_Iprobe` is the polling version (`flag`). With `MPI_ANY_SOURCE` and multiple threads use `MPI_Mprobe`/`MPI_Mrecv` so the probed message cannot be stolen by another receive.

## The ring: the exercise that runs through the whole block

Labs `03_ring`, `04_allreduce`, `06_virtual_cartesian_topologies`, `08_1sided`
and `09_1sided-shmem` are all the **same** program written five ways [S11].
Each rank starts with `snd_buf = rank`; it passes the value once around a ring
of $P$ processes, $P$ times, adding what arrives to a running `sum`. After $P$
rounds every rank has seen every rank number exactly once, so on **every** rank

$$\texttt{sum} \;=\; \sum_{r=0}^{P-1} r \;=\; \frac{P(P-1)}{2}.$$

For $P=4$ that is 6; for $P=8$, 28. The skeleton the course hands out is
deliberately the **wrong** version — `MPI_Send` then `MPI_Recv` into the same
buffer, which the comment in the file marks as *"WRONG program, it will deadlock
with a synchronous communication protocol"* [S11] — and the exercise is to make
it correct. The ASC/HLRS solution of choice is `MPI_Issend` + `MPI_Recv` +
`MPI_Wait`, i.e. the *synchronous* non-blocking send, precisely because it
cannot be rescued by buffering and therefore proves the fix [S11].

[`../src/exercises/2025w-mpi/ring_variants.c`](../src/exercises/2025w-mpi/ring_variants.c)
implements it seven ways (ordered Send/Recv, `Sendrecv`,
`Sendrecv_replace`, `Issend`+`Recv`+`Wait`, `Irecv`+`Issend`+`Waitall`,
`MPI_Allreduce`, `MPI_Scan`) and asserts $P(P-1)/2$ for each — which is exactly
why a fixed reference answer is worth having.

## Cost model

From `pingpong.c`: one-way time $t(n) \approx \alpha + n/B$ with latency
$\alpha$ and asymptotic bandwidth $B$; $n_{1/2} = \alpha B$ is the message size
at which the two terms are equal, i.e. the boundary between latency-bound and
bandwidth-bound. With $\alpha = 1.5\,\mu$s and $B = 12$ GB/s,
$n_{1/2} = \alpha B = 18\,000$ bytes (17.6 KiB) — and at that size the message
takes exactly $2\alpha$. Computed by
[`../src/py/mpi_cost.py`](../src/py/mpi_cost.py)`::n_half`, which also asserts
the identity. Many small messages are the classic performance bug; pack them, use
derived datatypes ([12](12-derived-datatypes.md)), or send fewer, larger ones
[S14].

**Published reference numbers.** The lecturer's own ping-pong measurements, on
VSC-3 (2 sockets of Intel Ivy Bridge, 8 cores each, 2 host channel adapters,
dual-rail Intel QDR-80 in a 3-level fat tree), one-way latency in µs [S14]:

| path | `MPI_Send`, Intel MPI | `MPI_Send`, Open MPI | `MPI_Ssend`, Intel MPI | `MPI_Ssend`, Open MPI |
|---|---|---|---|---|
| intra-socket | 0.3 | 0.3 | 1.2 | 1.3 |
| inter-socket | 0.7 | 0.6 | 1.7 | 2.0 |
| InfiniBand, 1 hop (edge) | 1.4–1.5 | 1.2 | 2.0 | **14.0** |
| InfiniBand, 2 hops (leaf) | 1.8–1.9 | 1.6 | 2.5 | **15.0** |
| InfiniBand, 3 hops (spine) | 2.3–2.4 | 2.1 | 3.0 | **18.0** |

Three things to take from it, all of which the slide states: latency grows with
each switch hop, so **where your ranks are placed matters**; bandwidth, by
contrast, is almost identical on all these paths once the message is large, so
the curves differ only at the left end; and a synchronous send can cost an order
of magnitude more than a standard send on some implementations — an argument for
using `MPI_Ssend` as a *correctness* tool and not in production [S14].

VSC-3 is retired, so treat the table as a shape, not as today's VSC-5 numbers.
On the reference laptop (Open MPI 5.0.11, shared memory, 4 oversubscribed ranks
[S24]) `pingpong.c` reproduces the shape: a flat latency floor of a few tenths
of a µs up to a few kB, then a bandwidth-limited straight line.

## Pitfalls

- Reusing a buffer after `MPI_Isend` before `MPI_Wait` (silent corruption); reading a receive buffer before `MPI_Wait` (stale data).
- Receive count smaller than the message: `MPI_ERR_TRUNCATE`, fatal by default.
- Mismatched types (`MPI_INT` sent, `MPI_DOUBLE` received): compiles, silently wrong or truncated.
- Mismatched tags or wrong destination: the receive waits forever; the program hangs at the end when `MPI_Finalize` cannot complete.
- Sending a `struct` or a non-contiguous slice as `MPI_BYTE` across heterogeneous nodes or with padding: use derived datatypes.
- `MPI_ANY_SOURCE` with results that depend on arrival order: non-deterministic output, non-reproducible floating-point sums.
- A hang that appears only for large N or large P: buffering dependence; test with `MPI_Ssend` in place of `MPI_Send` (a macro switch) to make it show up at any size.
- `MPI_Status` fields are unset when you passed `MPI_STATUS_IGNORE`; `MPI_Get_count` needs a real status.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1 and Q4 are the `03_ring` lab in words [S11].

1. **Why does the following program hang when P = 2 and N = 10^6 but work for N = 10?**
   `MPI_Send(buf, N, ..., other, ...); MPI_Recv(buf2, N, ..., other, ...);` on both ranks. For small N the sends are eager (buffered), return, and both ranks reach `Recv`. For large N both sends wait for a matching receive (rendezvous) that neither rank posts: deadlock. Fix with `MPI_Sendrecv` or `Irecv`+`Isend`+`Waitall`.
2. **What exactly does "blocking" guarantee for `MPI_Send`, and what does it not guarantee?**
   That the send buffer can be modified on return. Not that the receiver has received or even posted the receive; the message may sit in a system buffer.
3. **Rank 0 sends messages with tags 1 and 2 to rank 1 in that order; rank 1 receives tag 2 first. Legal? What if rank 1 receives with `MPI_ANY_TAG` twice?**
   Legal: non-matching messages wait in the unexpected queue. With `MPI_ANY_TAG` the non-overtaking rule applies and the tag-1 message arrives first.
4. **Sketch the halo update of a 1D stencil with non-blocking calls so that interior computation overlaps the communication.**
   `Irecv(left ghost); Irecv(right ghost); Isend(first point to left); Isend(last point to right); update points 2..n-1; Waitall; update points 1 and n`.
5. **What does `MPI_Probe` give you that `MPI_Recv` does not, and why can `MPI_Probe` + `MPI_Recv` with `MPI_ANY_SOURCE` be unsafe with threads?**
   The envelope and length of a message before allocating a buffer. Between the probe and the receive another thread may receive that message, and your receive then matches a different one; `MPI_Mprobe`/`MPI_Mrecv` bind the probed message to a handle.
