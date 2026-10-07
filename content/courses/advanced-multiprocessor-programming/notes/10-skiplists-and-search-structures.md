# 10 Skiplists and concurrent search structures

Book chapter 14 [S1]; skip lists: Pugh 1990 [S30]. TISS: "search structures"
[S2]. A balanced search tree rebalances by rotations that touch many nodes at
once, which is hard to make concurrent; a skiplist balances **by probability**
and every change is local, so the list techniques of note 06 carry over.
No separate program: the per-level logic is the lazy and lock-free list of
`src/cpp/lists.cpp`; a lazy skiplist is a good project-sized extension of it.

## The sequential skiplist [S30]

A sorted linked list at level 0 plus express lanes: each node gets a random **height** $h \ge 1$ with $P(h \ge j+1 \mid h \ge j) = p$ (usually $p = 1/2$ or $1/4$), and is linked into levels $0 \dots h-1$. Sentinels `head`/`tail` have maximal height. Search: start at the top level of `head`, move right while the next key is smaller, else drop one level; at level 0 the next node is the candidate.

**Expected height.** Nodes at level $\ge j$: $n p^j$. Top level with an expected constant number of nodes: $L(n) = \log_{1/p} n$.

**Expected search cost** (Pugh's backward analysis [S30]). Walk the search path backwards from the found node. At a node of height at least the current level, the path came from the left with probability $1-p$ (node not taller) or from above with probability $p$. Let $C(k)$ be the expected cost to climb $k$ levels in an infinite list:
$$C(k) = (1-p)\,(1 + C(k)) + p\,(1 + C(k-1)) \;\Rightarrow\; C(k) = \frac{1}{p} + C(k-1) = \frac{k}{p}.$$
Climbing to level $L(n)$ costs $L(n)/p$; above it, at most the number of nodes of height $> L(n)$, expected $\le 1/(1-p)$. Total expected cost
$$\le \frac{L(n)}{p} + \frac{1}{1-p} = O(\log n) \quad [S30].$$
$p = 1/2$: $2\log_2 n + 2$ comparisons; $p = 1/4$: $2\log_2 n + 4/3$, fewer pointers per node ($1/(1-p) = 4/3$ vs 2).

## Lazy skiplist [S1 ch. 14]

Each node: key, `next[0..h-1]`, a lock, `marked`, and **`fullyLinked`**.

- **Abstraction map**: $k$ is in the set iff a node with key $k$ is **unmarked and fullyLinked**. Level 0 decides membership; upper levels are hints.
- `find(k)` fills `preds[j]`, `succs[j]` for every level without locks.
- `add(k)`: if found and unmarked, wait until it is fullyLinked and return false (someone else is adding it). Else lock `preds[0..h-1]` bottom-up, validate for each level `!preds[j].marked && !succs[j].marked && preds[j].next[j] == succs[j]`, link the new node at all levels, then set `fullyLinked = true` (**linearisation point** of a successful add).
- `remove(k)`: the victim must be fullyLinked, unmarked, and found at its top level. Lock the victim, set `marked` (**linearisation point**), lock the preds, validate, unlink top-down.
- `contains(k)`: wait-free: `find`, return `found && fullyLinked && !marked`.

Locks are taken bottom-up in key order at each level, so no deadlock; validation is local for the same reason as in the lazy list (marked before unlinked).

## Lock-free skiplist [S1 ch. 14]

Built from the lock-free list (note 06): every `next[j]` carries a mark bit. Remove marks the victim's `next` pointers top-down, then marks level 0 (**linearisation point**, bottom level is the set); `find` snips marked nodes at each level as in Harris's list [S15]. Add links level 0 first (**linearisation point**), then the higher levels one by one, retrying `find` if a CAS fails. Consequence: the upper levels are **not** a consistent skiplist at every instant, only a set of shortcuts; the structure is a set of lists whose level-0 list is the abstraction. `contains` is wait-free and never snips.

## Other search structures

Chapter 14 approaches balanced search through skiplists. Concurrent trees in practice (lock-based B-trees with lock coupling, lock-free BSTs) use the same tools: hand-over-hand locking, optimistic validation, marks on edges. Priority queues (book ch. 15) reuse the skiplist: `removeMin` marks the first unmarked node at level 0 [S1 ch. 15].

## Worked example: a search path

Keys 3, 7, 9, 12, 20 with heights 1, 3, 1, 2, 1. Levels (top first):

```
L2: head ------------> 7 --------------------------> tail
L1: head ------------> 7 ---------> 12 ------------> tail
L0: head -> 3 -------> 7 -> 9 ----> 12 -> 20 ------> tail
```

`contains(12)`: L2: head → 7 (7 < 12), next is tail: drop. L1: 7 → next 12, not < 12: drop. L0: 7 → 9 (9 < 12) → next 12: stop, found. 5 comparisons for 5 keys; the gain appears only for large $n$ ($L(n)/p$ grows like $\log n$).

`remove(7)` in the lazy skiplist: find sets `preds = [head, head, 3]` for levels 2, 1, 0 and `succs = [7, 7, 7]`; lock 7, mark it (LP), lock 3 then head, validate, unlink at levels 2, 1, 0.

## Pitfalls

- Treating a node found at level $j > 0$ as "in the set": membership is decided at level 0 (lazy: fullyLinked and unmarked).
- Setting `fullyLinked` before all levels are linked: a concurrent remove could find it at its top level before it is linked there.
- Random heights from a shared RNG: a hot spot; use a thread-local generator.
- Unbounded heights: cap at $\lceil \log_{1/p} n_{\max} \rceil$.

## Exam-style questions

1. **Derive the expected search cost of a skiplist.** Backward analysis: $C(k) = k/p$; total $\le L(n)/p + 1/(1-p)$ with $L(n) = \log_{1/p} n$ [S30].
2. **In the lazy skiplist, what is `fullyLinked` for, and where do add and remove linearise?** Hides a node until it is linked at every level; add at setting `fullyLinked`, remove at setting `marked` [S1 ch. 14].
3. **Why are skiplists preferred over balanced trees for concurrency?** Insert and delete change only the predecessors of one node per level; no rotations that touch a subtree [S30] [S1 ch. 14].
4. **In the lock-free skiplist, the upper levels may be inconsistent. Why is that acceptable?** The abstraction is the level-0 list; upper levels are only shortcuts; `find` repairs them by snipping marked nodes.
5. **How would you test a concurrent skiplist?** The same way as the lists in `lists.cpp`: a sequential run against `std::set`, a disjoint-key concurrent run with known final contents, the per-key add/remove balance under contention, plus a structural check that every level is sorted and each level is a sublist of the one below.

Sources: [S1] [S2] [S15] [S30].
