# 05 Spin locks and contention

Book chapter 7 [S1]; Mellor-Crummey & Scott [S13]. Note 01 built locks from
reads and writes; here one read-modify-write instruction makes a lock of one
word, and the whole problem becomes **cache-coherence traffic**. Code:
`src/cpp/spinlocks.cpp`. Hardware background:
Efficient Programs 04, caches
and the false-sharing measurement in
[NSSC I 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md).

## Definitions

- **Read-modify-write (RMW)**: one atomic instruction that reads a location and writes a function of it: `exchange` (test-and-set), `fetch_add`, `compare_exchange` (CAS).
- **Spinning** (busy-waiting): re-testing a condition in a loop instead of sleeping. Good when the wait is shorter than a context switch (microseconds).
- **Cache coherence** (MESI-style): a line may be **shared** (read-only copies in many caches) or **modified/exclusive** in one. A write to a shared line **invalidates** all other copies; their next read **misses** and fetches the line across the interconnect (a queue-lock hand-off, which is essentially such transfers, costs 50-230 ns on this machine, measured below).
- **Local spinning**: a waiter spins on a line in its own cache, generating no traffic until the value changes.
- **Contention**: many threads trying to acquire at once.

## TAS, TTAS, backoff

```
TAS:   lock: while (held.exchange(true)) {}
TTAS:  lock: for (;;) { while (held.load()) {}  if (!held.exchange(true)) return; }
unlock (both): held.store(false)
```

**TAS**: every spin iteration is an `exchange`, i.e. a **write**: the line ping-pongs between all $n$ waiters; the lock holder's `unlock` competes for the same line. **TTAS**: waiters spin on a load, which hits their cached shared copy: no traffic while the lock is held. On release: one invalidation, $n$ misses, then $n$ `exchange` attempts of which one wins and $n - 1$ write anyway (invalidating each other). Cost per hand-off grows with $n$ (an "invalidation storm") [S1 ch. 7].

**Exponential backoff**: after a failed `exchange`, wait a random time in $[0, L)$, then double $L$ up to $L_{\max}$. Fewer simultaneous attempts; but $L_{\min}, L_{\max}$ are machine-specific and unfair: a thread that just released tends to re-acquire before sleeping waiters wake.

## Queue locks: CLH and MCS

Idea: waiters form a queue; each spins on a **different** location; release touches one waiter's location only. FIFO, hence starvation-free.

**CLH** (implicit queue). Each thread owns a node `{locked}`.
```
lock:   my.locked = true; pred = tail.exchange(&my);  while (pred->locked) {}
unlock: my.locked = false;  my_node = pred;           // recycle the predecessor's node
```
The successor spins on **my** node, so I cannot reuse it; I take my predecessor's, which nobody watches any more. Spinning is on a remote node: local on cache-coherent machines (the line is cached after the first miss), remote on NUMA-without-cache.

**MCS** [S13] (explicit queue). Each thread owns `{next, locked}`.
```
lock:   q.next = null; q.locked = true; pred = tail.exchange(&q);
        if (pred) { pred->next = &q; while (q.locked) {} }
unlock: if (!q.next) { if (tail.CAS(&q, null)) return;   // nobody queued
                       while (!q.next) {} }              // a waiter is between exchange and link
        q.next->locked = false;
```
Each thread spins on **its own** node, so spinning is local even without coherent caches: $O(1)$ remote references per acquisition [S13]. Cost: `unlock` may have to wait for a slow successor to link in, and the extra CAS.

**Correctness of MCS (the race in unlock).** Between a waiter's `tail.exchange` and its `pred->next = &q` the holder may see `next == null`. The CAS on `tail` distinguishes the cases: if `tail` is still me, nobody has exchanged, so setting it to null is safe; if the CAS fails, someone has exchanged and will link in, so wait for `next`.

**FIFO, checked**: `check_fifo()` holds the lock, starts threads one at a time, waits until each has visibly swapped itself into `tail`, releases, and asserts the service order equals the arrival order (for CLH and MCS; a TAS lock gives no such guarantee).

Also in chapter 7 [S1]: the Anderson array lock (a ring of flags, one per slot, padded to cache lines), timeout-capable queue locks, and hierarchical locks for NUMA.

## Measured

`./bin/spinlocks --bench`: each thread repeatedly locks, increments one shared counter, unlocks, for 200 ms. "ns/acq" = wall time / total acquisitions; fairness = fewest / most acquisitions of any thread. M3 Pro, 6 performance + 6 efficiency cores [S35], run of 2026-09-28:

| lock | 1 thread | 2 | 4 | 8 | fairness at 8 |
|---|---|---|---|---|---|
| TAS | 2.1 ns | 17.0 | 92.2 | 626.7 | 0.71 |
| TTAS | 1.9 | 9.7 | 27.8 | 195.4 | 0.41 |
| TTAS + backoff | 3.4 | 3.7 | 11.2 | 232.6 | 0.40 |
| CLH | 1.4 | 48.6 | 144.5 | 128.3 | **1.00** |
| MCS | 3.4 | 153.3 | 225.2 | 226.2 | **1.00** |
| `std::mutex` | 4.9 | 9.3 | 29.1 | 16.6 | 0.94 |

Reading it:

- **TAS vs TTAS** at 8 threads: 627 vs 195 ns, the price of spinning with writes.
- **Queue locks are fair and slow per acquisition here.** Every hand-off moves the counter's and the node's lines to *another* core: a cross-core transfer each time, 50-230 ns. The unfair locks let the releasing thread re-acquire while the line is still in its cache (TTAS fairness 0.41 means one thread got less than half of another's share). Throughput and fairness trade off; the book's queue-lock advantage appears at high contention on machines where the TAS storm dominates.
- `std::mutex` at 8 threads (17 ns, fairness 0.94) beats every spin lock here. How the macOS implementation achieves that (parking waiters, not handing off in FIFO order) is not examined in this note (unsourced); the measurement is the point: measure before choosing a spin lock.
- Numbers vary by 2x between runs; the ordering TAS > TTAS at $n \ge 4$ and queue-lock fairness 1.00 were the same in both runs of 2026-09-28.

## Worked example: coherence messages per hand-off

$n$ threads waiting, one holder releases. Count line transfers of the lock word.

| lock | on release | to settle |
|---|---|---|
| TAS | holder's store must get the line back from a spinning writer: 1 transfer | waiters' `exchange`es keep bouncing it: $\Theta(n)$ per hand-off, plus continuous traffic while held |
| TTAS | 1 invalidation of $n$ shared copies | $n$ read misses + up to $n$ `exchange`s: $\Theta(n)$ per hand-off, no traffic while held |
| MCS | 1 write to the successor's node (one remote line) | successor's spin load misses once: $O(1)$ |

## Pitfalls

- Spinning on `exchange` (TAS): burns the interconnect even while the lock is held.
- Queue nodes without padding: two nodes in one 128-byte line (this machine's line size [S35]) make "local" spinning false-shared. The code uses `alignas(128)`.
- Reusing a CLH node you still own: the successor spins on it. Reuse the predecessor's.
- MCS unlock that sets `tail = null` unconditionally: loses a waiter that is between `exchange` and linking.
- Spin locks with more threads than cores: a preempted holder makes everybody spin for a whole time slice; a preempted queue waiter blocks everyone behind it.

## Exam-style questions

1. **Why is TTAS faster than TAS, and why does it still degrade with $n$?** Waiters spin on cached shared copies (no traffic while held); on release all $n$ miss and race with `exchange`, $\Theta(n)$ transfers per hand-off [S1 ch. 7].
2. **Write the MCS lock and explain the `while (!q.next)` in unlock.** Code above; a successor has done `tail.exchange` but not yet `pred->next = &q`; the failed CAS on `tail` proves it exists [S13].
3. **CLH vs MCS: where does each thread spin, and when does it matter?** CLH on the predecessor's node, MCS on its own. On cache-less NUMA machines only MCS spins locally; with coherent caches both do after one miss [S13].
4. **Prove CLH is FIFO.** The `tail.exchange` totally orders arrivals; each thread waits exactly for its predecessor in that order to clear `locked`, which happens only in that predecessor's unlock.
5. **Our benchmark shows `std::mutex` beating MCS at 8 threads. Does that contradict the book?** No: the benchmark measures throughput with a tiny critical section, where an unfair lock that lets the same core re-acquire avoids cross-core transfers; MCS pays one transfer per hand-off by design but guarantees FIFO and bounded traffic under contention. State the metric before claiming a winner.

Code: `src/cpp/spinlocks.cpp` (`TAS`, `TTAS`, `Backoff`, `CLH`, `MCS`, `check_lock`, `check_fifo`, `bench_one`). Sources: [S1] [S13] [S35].
