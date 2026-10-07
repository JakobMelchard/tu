# 09 Hash sets: striping and split ordering

Book chapter 13 [S1]; split-ordered lists: Shalev & Shavit [S18]. Unlike a
stack, a hash set has **natural parallelism**: operations on different
buckets do not conflict. The difficulty is **resizing**, which touches
everything. Code: `src/cpp/striped_hashset.cpp`.

## Definitions

- **Closed addressing**: bucket $i$ holds a list of all keys with $h(k) \bmod N = i$. **Open addressing**: one key per slot, probe a sequence of slots (linear probing, cuckoo hashing) [S1 ch. 13].
- **Load factor** $\alpha = n / N$ (items per bucket). Expected cost of an operation with a good hash: $O(1 + \alpha)$. Keep $\alpha$ bounded by **resizing**: double $N$ when $\alpha$ exceeds a threshold (the code uses 4), rehashing every item.
- **Lock striping**: $L$ locks for $N \ge L$ buckets, lock $i$ guards all buckets $b$ with $b \bmod L = i$.

## Three lock-based designs [S1 ch. 13]

| design | locks | resize |
|---|---|---|
| coarse | 1 | under the lock |
| striped | fixed array of $L$; key $k$ uses lock $h(k) \bmod L$; $N$ always a multiple of $L$ | acquire **all** $L$ locks in index order, re-check $N$, double |
| refinable | the lock array itself grows with the table | a thread marks "resizing" with an atomic flag, waits for quiescence of each lock, replaces locks and table |

**Why striping is correct across a resize.** Key $k$'s lock is $h(k) \bmod L$ before and after doubling (the lock array does not change), and its bucket changes from $h(k) \bmod N$ to $h(k) \bmod 2N$, both $\equiv h(k) \bmod L$ because $L \mid N$. A thread holding lock $i$ therefore excludes a resize (which needs all locks) and every other operation on its bucket. `N` changes only while all locks are held, so reading it while holding any one lock is race-free.

**Why the global lock order.** Two resizers each holding some locks and waiting for the others would deadlock; taking locks $0, 1, \dots, L-1$ in order makes a cycle in the wait-for graph impossible. After acquiring all, re-check that $N$ still equals the size that triggered the resize, or two threads double twice.

**Resize policy outside the stripe lock**: `add` increments an atomic count and calls `resize(seen_N)` after releasing its stripe lock (resizing needs all locks, including the one it holds).

## Lock-free: split-ordered lists [S18]

Keep **all** items in **one** lock-free sorted list (note 06) and let the bucket array hold **shortcuts** into it. The problem: after doubling, items of bucket $b$ must be split between $b$ and $b + N$; moving nodes lock-free between lists is hard. The trick: sort the list so that no node ever moves.

**Recursive split ordering.** Sort by the bit-reversed key $\text{rev}(k)$. Derivation: the leading $i$ bits of $\text{rev}(k)$ are the trailing $i$ bits of $k$ reversed, i.e. $\text{rev}_i(k \bmod 2^i)$. Sorting by $\text{rev}(k)$ therefore sorts first by $\text{rev}_i(k \bmod 2^i)$, so for **every** table size $2^i$:

1. each bucket $b = k \bmod 2^i$ is one **contiguous** run of the list;
2. runs appear in the order of $\text{rev}_i(b)$;
3. doubling to $2^{i+1}$ looks at one more bit: run $b$ splits into run $b$ (bit $i$ of $k$ is 0) followed by run $b + 2^i$ (bit $i$ is 1). **Split in place**: the new bucket just needs a pointer to where its run starts.

Example with 3-bit keys: sorted by reversed bits, the order is 0, 4, 2, 6, 1, 5, 3, 7. With $N = 2$: bucket 0 = {0, 4, 2, 6}, bucket 1 = {1, 5, 3, 7}. With $N = 4$: bucket 0 = {0, 4}, 2 = {2, 6}, 1 = {1, 5}, 3 = {3, 7}: each old run cut in two.

**Dummy nodes.** Each bucket $b$ gets a sentinel node with key $\text{rev}(b)$ that marks the start of its run; regular keys have their most significant bit set **before** reversal, so their reversed key ends in 1 and sorts after the dummy of their bucket, whose reversed key ends in 0 [S18]. Dummies are never deleted. A bucket is initialised **lazily**: on first access, recursively make sure its parent bucket (the bucket with the top set bit of $b$ cleared) exists and insert the dummy from there. Resizing is then one atomic increment of the size; no item moves.

`split_order_property()` checks claims 1-3 exhaustively for $2^{12}$ keys and all table sizes $2^1 \dots 2^{10}$: along the list sorted by `rev32(k)`, $\text{rev}_i(k \bmod 2^i)$ never decreases.

## Measured

80 % `contains`, 10 % `add`, 10 % `remove`, keys in [0, 20000), half full, 16 locks, M3 Pro [S35]:

| threads | coarse | striped |
|---|---|---|
| 1 | 39.7 Mops/s | 42.9 |
| 2 | 21.5 | 38.3 |
| 4 | 14.2 | 41.5 |
| 8 | 13.1 | 23.7 |

Striping holds throughput to 4 threads, then drops at 8 (more threads than performance cores; 16 stripes and `std::mutex` hand-offs). The coarse table halves at 2 threads and does not recover.

## Worked example: concurrent add during a resize

$L = 2$, $N = 2$, threshold $\alpha > 4$. Thread A inserts the 9th key and triggers `resize(2)`; thread B is inside `add(k)` holding lock 1.

| step | A | B |
|---|---|---|
| 1 | acquires lock 0 | holds lock 1, inserts into bucket $h(k) \bmod 2$ |
| 2 | waits for lock 1 | releases lock 1; its count increment also sees $\alpha > 4$ and calls `resize(2)` |
| 3 | acquires lock 1; $N == 2$: doubles to 4, rehashes | waits for lock 0 |
| 4 | releases all | acquires 0, 1; sees $N = 4 \ne 2$: returns without doubling |

Without the re-check the table would double twice.

## Pitfalls

- Taking stripe locks in data-dependent order during resize: deadlock.
- Reading `N` without holding any lock, then indexing the table: the table may be replaced in between.
- A striped table whose $N$ is not a multiple of $L$: a key's bucket may move to a bucket guarded by a different lock.
- Split order without the MSB trick: a regular key equal to a dummy's reversed key sorts ambiguously.
- Resize triggers under the stripe lock: `resize` then waits for a lock the caller holds.

## Exam-style questions

1. **Why does lock striping stay correct when the table doubles but the lock array does not?** $L \mid N$ keeps a key's lock index fixed; resize holds all locks [S1 ch. 13].
2. **Derive why bit-reversed order makes every bucket contiguous for every power-of-two table size.** The first $i$ bits of $\text{rev}(k)$ are $\text{rev}_i(k \bmod 2^i)$; sorting by $\text{rev}(k)$ groups by them [S18].
3. **What are the dummy nodes in a split-ordered list for, and how are regular keys kept after them?** Start-of-bucket markers the bucket array points to; regular keys set the MSB before reversal so their reversed key is odd and larger than the dummy's [S18].
4. **How does the lock-free hash set resize, and what is the cost?** Atomically double the bucket count; new buckets are initialised lazily by inserting a dummy, found through the parent bucket; no item moves; expected $O(1)$ per operation [S18].
5. **Coarse vs striped: predict the scaling of each for a 90 % read workload and justify.** Coarse serialises everything including reads; striped admits up to $L$ concurrent operations on distinct stripes; measured 13 vs 24-41 Mops/s at 4-8 threads.

Code: `src/cpp/striped_hashset.cpp` (`CoarseHashSet`, `StripedHashSet::resize`, `rev32`, `split_order_property`). Sources: [S1] [S18] [S35].
