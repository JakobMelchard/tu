# 06 Linked lists: the role of locking

Book chapter 9 [S1]; lazy list Heller et al. [S16]; lock-free list Harris
[S15]. One abstract object, an integer **set** with `add`, `remove`,
`contains`, implemented five ways with less and less locking. The chapter is
the course's catalogue of techniques; every later structure reuses them.
Code: `src/cpp/lists.cpp` (coarse, lazy, lock-free with one shared test).

## Representation

Sorted singly linked list with sentinels `head` ($-\infty$) and `tail` ($+\infty$). Two tools from the book [S1 ch. 9] make correctness arguments precise:

- **Representation invariant**: a property of the concrete list that every method preserves (sentinels present, keys strictly increasing, `tail` reachable from `head`, and for the lazy/lock-free lists: an unmarked node is reachable).
- **Abstraction map**: which set the list represents: $\{k : \text{a node with key } k \text{ is reachable from head and unmarked}\}$.

A method is correct if it preserves the invariant and, at its linearisation point, changes the abstract set as the sequential specification says.

## Five implementations

| variant | idea | `contains` | progress of add/remove |
|---|---|---|---|
| coarse | one lock for the whole list | locked | blocking, starvation-free with a fair lock |
| fine-grained | lock per node, **hand-over-hand**: lock `pred`, lock `curr`, release `pred`, move on | locked | blocking |
| optimistic | traverse without locks, lock `pred` and `curr`, **validate** by re-traversing from head that `pred` is reachable and `pred.next == curr` | locked, validates | blocking, not starvation-free |
| lazy [S16] | add a `marked` bit; remove marks first (**logical** delete), then unlinks (**physical**); validate locally: `!pred.marked && !curr.marked && pred.next == curr` | **wait-free**, no locks | blocking |
| lock-free [S15] | mark in the low bit of `next`; CAS on `(next, mark)` together | **wait-free** | **lock-free** |

**Why two locks (fine-grained)?** Remove `b` from `a → b → c` locks `a` and `b`. With only `b` locked, a concurrent `remove(a)` that sets `head.next = b` and our `a.next = c` both succeed and `b` stays reachable: a lost removal. Holding `pred`'s lock stops anyone from changing `pred.next` or unlinking `pred`.

## Lazy list, and why validation is local

`add(k)`: find `pred.key < k <= curr.key` without locks; lock `pred`, `curr`; validate; if `curr.key == k` return false; else `pred.next = new node(k, curr)`.
`remove(k)`: same, then `curr.marked = true` (**linearisation point**), `pred.next = curr.next`.
`contains(k)`: walk to the first key $\ge k$; return `key == k && !marked`.

**Validation is local** because of the invariant *every unmarked node is reachable*: marking happens before unlinking, both under the locks of the node and its predecessor. So `!pred.marked` implies `pred` is still reachable, and `pred.next == curr` then pins the window; no re-traversal (unlike optimistic).

**`contains` is linearisable without locks.** Successful: at the moment it reads `curr.marked == false`, `curr` is unmarked, hence reachable, hence in the set. Unsuccessful: either the key was not in the list when traversal passed its position, or it found a marked node; if a concurrent `add(k)` put a new unmarked `k` in, the linearisation point of `contains` is placed just **before** that add's point; this point can be a step of another thread [S1 ch. 9] [S16].

## Lock-free list: the Harris mark

Plain CAS on `pred.next` is not enough. List `a → b → c`, thread 1 removes `a` (`CAS(head.next: a → b)`), thread 2 adds `x` after `a` (`CAS(a.next: b → x)`). Both CASes succeed, and `x` hangs off an unlinked node: **lost insert**. The fix [S15]: store a **mark bit in `a.next` itself**. Remove first CASes `a.next` from `(b, 0)` to `(b, 1)` (logical delete, linearisation point); thread 2's `CAS(a.next: (b,0) → (x,0))` now fails and retries.

```
find(k):   from head, for each curr: if curr.next is marked, CAS pred.next (curr,0) -> (succ,0)  // snip
           (restart from head if that CAS fails); stop at first curr.key >= k
add(k):    loop { find; if curr.key == k return false;
                  node.next = (curr,0); if CAS(pred.next, (curr,0), (node,0)) return true }
remove(k): loop { find; if curr.key != k return false; succ = curr.next;
                  if !CAS(curr.next, (succ,0), (succ,1)) continue;       // mark
                  CAS(pred.next, (curr,0), (succ,0)); return true }      // try once to unlink
contains:  wait-free traversal ignoring marks; key == k && !marked(curr.next)
```

Lock-free, not wait-free: a CAS fails only because another thread's CAS succeeded, so some operation always progresses; one thread can retry forever. In the code a marked node may still be reachable after `remove` returns (its one unlink CAS failed); the next `find` passing by snips it. The C++ version packs the mark into bit 0 of a `uintptr_t` (nodes are at least 8-byte aligned); the book's Java uses `AtomicMarkableReference` [S1 ch. 9].

## The shared test

`test_set<S>()` runs the same three checks on all three variants:

1. 20000 random sequential operations against `std::set`.
2. Four threads, **disjoint** keys (thread $t$ owns keys $\equiv t \bmod 4$) plus random `contains` on all keys: the final contents are known exactly.
3. Four threads on 64 **shared** keys: for every key, (successful adds) - (successful removes) must be 0 or 1 and equal `contains(k)` at the end; all reachable keys strictly increasing. This is a consequence of linearisability that needs no history recording.

All pass, also under ThreadSanitizer (`make tsan`) [S35].

## Measured

80 % `contains`, 10 % `add`, 10 % `remove`, keys in [0, 512), half full, $2 \cdot 10^5$ operations per thread, M3 Pro [S35]:

| threads | coarse | lazy | lock-free |
|---|---|---|---|
| 1 | 24.5 Mops/s | 5.0 | 4.4 |
| 2 | 16.1 | 6.3 | 8.5 |
| 4 | 7.1 | 8.0 | 16.0 |
| 8 | 7.0 | 9.1 | 22.9 |

Single-threaded the coarse list wins by 5x: compact nodes, no atomics, no marks (the lazy node also carries a `std::mutex`, which makes it several cache lines). Under concurrency the coarse list serialises and falls; the lock-free list scales 5x from 1 to 8 threads because `contains`, 80 % of the load, never writes shared memory.

## Worked example: a lazy-list interleaving

List `h → 3 → 7 → t`. Thread A: `remove(3)`; thread B: `add(5)`.

| step | A | B | list |
|---|---|---|---|
| 1 | finds pred = h, curr = 3 | | |
| 2 | | finds pred = 3, curr = 7 | |
| 3 | locks h, 3; validates ok | | |
| 4 | | tries to lock 3: blocks | |
| 5 | 3.marked = true (**LP**), h.next = 7, unlocks | | h → 7 → t |
| 6 | | locks 3, 7; validate: `3.marked` → **fail**, retry | |
| 7 | | finds pred = h, curr = 7; locks; validates; h.next = 5 (**LP**) | h → 5 → 7 → t |

Without validation step 6 would set `3.next = 5` on an unlinked node: lost insert.

## Pitfalls

- Validating only `pred.next == curr` in the lazy list: `pred` may be marked and unlinked with its `next` unchanged.
- Freeing a removed node while a wait-free `contains` may still be walking through it: needs note 12. The code allocates from an arena freed with the set.
- Lock order: always `pred` then `curr` (list order), or two threads deadlock; `std::scoped_lock` in the code avoids the issue with a deadlock-avoidance algorithm.
- Marked nodes can remain reachable in the lock-free list; tests must not assert "no marked node reachable" there.

## Exam-style questions

1. **Why does hand-over-hand locking need two locks for remove?** See the lost-removal example: a single lock does not stop `pred` from being unlinked concurrently [S1 ch. 9].
2. **State the lazy list's validation and the invariant that makes it sufficient.** `!pred.marked && !curr.marked && pred.next == curr`; unmarked nodes are reachable because marking precedes unlinking under both locks [S16].
3. **Where are the linearisation points of lazy `add`, `remove`, `contains`?** Successful add: the write of `pred.next`; remove: the write of `marked`; contains: reading `marked` (success) or just before a concurrent add's point (failure) [S16].
4. **Show why a lock-free list with plain pointer CAS loses inserts and how Harris's mark fixes it.** Concurrent remove of `a` and insert after `a` both succeed; putting the mark in `a.next` makes the insert's CAS fail [S15].
5. **Is the lock-free list wait-free? Is its `contains`?** add/remove: lock-free only (a thread's CAS can fail forever). contains: wait-free (bounded by the number of nodes, no retries).

Code: `src/cpp/lists.cpp` (`CoarseList`, `LazyList::validate`, `LockFreeList::find`, `test_set`, `bench_set`). Sources: [S1] [S15] [S16] [S35].
