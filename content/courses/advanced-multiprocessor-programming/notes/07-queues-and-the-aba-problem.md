# 07 Queues and the ABA problem

Book chapter 10 [S1]; Michael & Scott 1996 [S14]. FIFO pools: bounded and
unbounded, blocking and lock-free, and the bug that every CAS-on-pointers
design must defend against. Code: `src/cpp/ms_queue.cpp` (lock-free queue
with counted pointers and free list, plus the linearisability checker of
note 02).

## Definitions

- **Pool**: a collection with `put`/`get` and no order guarantee; a **queue** is a FIFO pool.
- **Bounded** (fixed capacity) vs **unbounded**. **Total** method: returns a result (EMPTY / FULL) instead of waiting; **partial**: waits until it can proceed (a `deq` on an empty queue blocks); **synchronous**: a `put` waits for a matching `get` (rendezvous) [S1 ch. 10].
- **Sentinel / dummy node**: a node whose value is ignored, so `head` and `tail` are never null and enqueuers and dequeuers touch different nodes.

## Lock-based queues

**Bounded partial queue** [S1 ch. 10]: two locks, `enqLock` and `deqLock`, so an enqueuer and a dequeuer run in parallel; an atomic `size` counter decides "full" and "empty"; condition variables `notFull`, `notEmpty` put waiters to sleep. The subtle part is the **lost wake-up**: a dequeuer that frees a slot must signal `notFull` while holding `enqLock`, otherwise a waiting enqueuer that has just tested `size` and is about to sleep misses the signal.

**Unbounded total queue**: the same two-lock idea without `size`; Michael & Scott also give it as their blocking algorithm [S14]. `enq` touches only `tail`, `deq` only `head` and the dummy.

## Michael-Scott lock-free queue [S14]

```
enq(v):  node = new(v, next = null)
         loop: last = Tail; next = last.next
               if last != Tail: continue                         // inconsistent snapshot
               if next == null:
                   if CAS(last.next, null, node): break          // LP of enq
               else CAS(Tail, last, next)                        // Tail lags: help it
         CAS(Tail, last, node)                                   // may fail: someone helped
deq():   loop: first = Head; last = Tail; next = first.next
               if first != Head: continue
               if first == last:
                   if next == null: return EMPTY                 // LP of empty deq
                   CAS(Tail, last, next)                          // help the lagging enq
               else: v = next.value                              // read BEFORE the CAS
                     if CAS(Head, first, next): free(first); return v   // LP of deq
```

- **Two-step enqueue.** Linking the node and swinging `Tail` cannot be one CAS. So `Tail` may lag by one node, and **any** thread that sees `Tail.next != null` advances it. This is **helping**: an enqueuer that stalls after linking does not block anyone. Lock-free.
- **The dummy.** `Head` always points at a dummy; the dequeued value lives in `Head.next`, which becomes the new dummy. Enqueuers and dequeuers conflict only when the queue is empty or has one element.
- **Read the value before the CAS**: after the CAS another thread may dequeue and free `next`.
- **Why `first == last` must help**: otherwise `Head` could pass `Tail`, and `Tail` would point at a freed node.

## The ABA problem

A CAS succeeds if the location **holds the expected bits**, not if it has **not changed**. Thread 1 reads `Head = A`, `next = B`, stalls. Thread 2 dequeues A and B; A is freed and recycled by a later enqueue, so `Head == A` again. Thread 1's `CAS(Head, A, B)` succeeds and installs B, a freed node [S14] [S1 ch. 10].

It needs **reuse** of addresses: with a garbage collector (Java, the book's language) a node cannot be recycled while thread 1 holds a reference, so the book's Java queue has no ABA; with manual reuse (C, C++, free lists) it does [S26].

**Fixes**:

1. **Counted (tagged) pointers** [S14]: store `(pointer, count)` in one CAS-able word and increment `count` on every successful CAS. The stale CAS expects `(A, c)`, finds `(A, c + k)` with $k \ge 2$, and fails. Needs a double-width CAS, or indices instead of pointers: `ms_queue.cpp` uses `[count:32 | index:32]` in one 64-bit word, the paper's design (counted pointers, a free list) with array indices in place of pointers. Wrap-around after $2^{32}$ operations **during one stall** is the residual risk.
2. **Safe memory reclamation** (note 12): hazard pointers or epochs guarantee A is not freed (hence not reused) while thread 1 may still use it.
3. **LL/SC** (ARM, POWER): the store-conditional fails if the location was **written**, whatever the value. (On ARMv8.1+ compilers emit `casal` instead, which is a value comparison again, see note 03.)

## Measured

Each thread does enqueue+dequeue pairs, $3 \cdot 10^5$ per thread, M3 Pro [S35]:

| threads | Michael-Scott | `std::mutex` + `std::queue` |
|---|---|---|
| 1 | 183 Mops/s | 208 |
| 2 | 22.7 | 131 |
| 4 | 16.5 | 55.8 |
| 8 | 4.7 | 67.0 |

The lock-free queue loses on this benchmark: every operation CASes one of two hot words (`Head`, `Tail`) plus the free list, and each failed CAS costs a cross-core transfer; the mutex version lets one core run long batches with the lines in its cache. Lock-freedom buys **progress guarantees** (no thread can block the others by being descheduled inside a critical section), not throughput under a benchmark with no preemption. The tests (2026-09-28): 400 recorded 15-call histories, 400 with overlapping calls, all linearisable; 4 producers and 4 consumers, $4 \cdot 10^5$ items delivered exactly once and in per-producer order [S35].

## Worked example: helping in action

Queue: `Head = Tail = D` (dummy), empty. Thread A enqueues `x`, thread B dequeues.

| step | A (enq x) | B (deq) | state |
|---|---|---|---|
| 1 | last = D, next = null | | |
| 2 | CAS(D.next, null, x) ok (**LP**) | | D → x, Tail = D |
| 3 | stalls before swinging Tail | | |
| 4 | | first = D, last = D, next = x | |
| 5 | | first == last and next != null: CAS(Tail, D, x) (help) | Tail = x |
| 6 | | retry: first = D, last = x, next = x; v = x.value; CAS(Head, D, x) ok (**LP**) | Head = x (new dummy) |
| 7 | CAS(Tail, D, x) fails: already done | | |

B could not return EMPTY at step 4 (x is linked, the enqueue has taken effect) and did not wait for A: it finished A's work.

## Pitfalls

- Reading `next.value` after the Head CAS (use-after-free).
- Forgetting the consistency re-check `last == Tail` / `first == Head`: the snapshot may mix two states.
- Believing a GC-free language can reuse nodes without tags or reclamation.
- Counting the tag in a field that is not part of the CAS word.
- Benchmarking a lock-free structure against a mutex on a machine with idle cores and concluding "lock-free is slower, hence useless": state what is measured.

## Exam-style questions

1. **Where are the linearisation points of MS enqueue and dequeue?** Enq: the CAS on `last.next`. Deq: the CAS on `Head`; empty deq: reading `next == null` with `first == last` [S14].
2. **Why can `Tail` lag, and why is that harmless?** Linking and advancing are two CASes; any thread that observes `Tail.next != null` advances `Tail` first, so the lag is at most one node and nobody waits for the stalled enqueuer.
3. **Describe the ABA problem with a concrete interleaving on the queue and two fixes.** Above; counted pointers [S14], hazard pointers [S26].
4. **Why does the book's Java queue not need tags?** Garbage collection: a node referenced by a stalled thread is never freed, so its address cannot come back; ABA needs reuse [S1 ch. 10] [S26].
5. **In a bounded two-lock queue, what is the lost wake-up and how is it avoided?** An enqueuer finds the queue full and is about to wait; the dequeuer frees a slot and signals before the enqueuer waits; the signal is lost. Signal while holding the lock the waiter holds when testing the condition (and re-test in a loop) [S1 ch. 10].

Code: `src/cpp/ms_queue.cpp` (`MSQueue::enqueue`, `MSQueue::dequeue`, `grab`/`release` free list, stress test in `test`). Sources: [S1] [S14] [S26] [S35].
