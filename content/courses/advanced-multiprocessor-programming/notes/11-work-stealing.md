# 11 Work stealing

Book chapter 16 [S1]; the scheduling theorem: Blumofe & Leiserson [S8]; the
deque: Chase & Lev [S9] with the C11 orderings proved by Lê et al. [S25].
TISS: "work-stealing" and the learning outcome "understand concepts and
implementations of work-stealing schedulers" [S2]. Code:
`src/cpp/work_stealing.cpp`. The OpenMP-task and hand-written task-manager
view of the same idea is in
[NSSC I 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md).

## The computation as a DAG

A fork-join program (`spawn f; g; sync`) unfolds into a directed acyclic graph: nodes are unit instructions, edges are dependencies (sequence, spawn, join).

- **Work** $T_1$: number of nodes = time on one processor.
- **Span** (critical path) $T_\infty$: length of the longest path = time on infinitely many processors.
- **Parallelism** $T_1 / T_\infty$: the maximum useful speedup.
- Lower bounds for any schedule on $P$ processors: $T_P \ge T_1 / P$ (work law) and $T_P \ge T_\infty$ (span law).

**Greedy scheduling** (never idle while a node is ready): $T_P \le T_1/P + T_\infty$ [S8]. Proof: each step either runs $P$ nodes (a complete step; at most $T_1/P$ of these) or runs every ready node (an incomplete step), which shortens the longest remaining path by one (at most $T_\infty$ of these). Since both lower bounds are within a factor 2 of this, greedy is 2-optimal; if $P \ll T_1/T_\infty$ the speedup is nearly linear.

## Work stealing [S8]

Each processor keeps a **deque** (double-ended queue) of ready tasks. It pushes spawned tasks and pops them at the **bottom** (LIFO: depth-first, like the serial program, good locality, bounded space). When its deque is empty it becomes a **thief**: picks a random victim and steals from the **top** (FIFO: the oldest task, near the root of the DAG, usually the biggest chunk of work).

**Theorem** [S8]: for fully strict computations, the expected time is $T_1/P + O(T_\infty)$; with probability $\ge 1 - \varepsilon$ it is $T_1/P + O(T_\infty + \lg P + \lg(1/\varepsilon))$; space $S_P \le S_1 P$; expected total communication $O(P\, T_\infty (1 + n_d) S_{\max})$. ($S_{\max}$: largest activation record; $n_d$: most syncs of any thread with its parent.) Intuition for the time bound: at every step each processor either works (at most $T_1$ processor-steps in total) or attempts a steal; the paper shows with a **delay-sequence** argument that the expected number of steal attempts is $O(P\, T_\infty)$ [S8]; dividing $T_1 + O(P\, T_\infty)$ processor-steps by $P$ gives the bound.

Consequence: steals are rare when parallelism is high, so the deque's owner path must be cheap and thieves may be slower.

## The Chase-Lev deque [S9] [S25]

Circular array `a`, indices `top` (thieves) and `bottom` (owner), $\text{size} = \text{bottom} - \text{top}$; `top` only ever increases.

```
push(x):  b = bottom; t = top; if b - t >= cap: grow (copy [t, b) to a 2x array)
          a[b] = x; fence(release); bottom = b + 1
take():   b = bottom - 1; bottom = b; fence(seq_cst); t = top
          if t > b: bottom = b + 1; return EMPTY
          x = a[b]; if t < b: return x                       // more than one: no conflict possible
          ok = CAS(top, t, t + 1); bottom = b + 1             // last element: race the thieves
          return ok ? x : EMPTY
steal():  t = top; fence(seq_cst); b = bottom
          if t >= b: return EMPTY
          x = a[t]; if !CAS(top, t, t + 1): return ABORT      // lost to another thief or the owner
          return x
```

(Orderings exactly as [S25, Fig. 1]; the code uses signed 64-bit indices so `bottom - 1` on an empty deque does not wrap.)

- **Owner fast path**: push and take use no RMW unless one element is left. That is the design goal given the theorem.
- **The two seq_cst fences.** `take` writes `bottom` then reads `top`; `steal` reads `top` then `bottom`. This is the SB pattern of note 03: without seq_cst both could miss the other's update, and owner and thief would both take the last element. With the fences, at least one of them sees the other, and the single remaining conflict (`t == b`) is settled by the CAS on `top`.
- **Growth**: only the owner grows the array; a thief may still read the old array, which is why old arrays are kept (the code frees them with the deque). Items live at the same logical index in both arrays, so a thief reading the old array still gets the right item.
- **No ABA**: `top` is monotonic, so a stale `CAS(top, t, t+1)` can never succeed after `top` moved on.
- The book's version is the same algorithm in Java: a bounded deque with a stamped `top` and an unbounded one on a circular array [S1 ch. 16].
- ThreadSanitizer does not model `atomic_thread_fence`: under `-fsanitize=thread` the code replaces the fences with seq_cst/release accesses (`AMP_TSAN` in `common.hpp`).

## The scheduler in `work_stealing.cpp`

One deque per worker; the calling thread is worker 0. `spawn(t)` pushes `t` on the own deque; `sync(t)` loops "take own, else steal from a random victim, run it" until `t.done`. The parent **helps** while waiting instead of blocking: the task it waits for is either still at the bottom of its own deque (then it runs it itself) or stolen (then it runs other work). Tasks live on the spawning function's stack frame, which outlives them because the frame waits in `sync`. A cutoff (`n < 16` for fib, 2048 elements for quicksort) keeps tasks worth a steal.

## Measured

M3 Pro, 6 performance + 6 efficiency cores [S35]:

| P | fib(40) time | speedup vs serial 0.282 s | steals | quicksort $4\cdot10^6$ |
|---|---|---|---|---|
| 1 | 0.290 s | 0.97 | 0 | 0.168 s |
| 2 | 0.148 | 1.91 | 16 | 0.088 |
| 4 | 0.077 | 3.67 | 114 | 0.054 |
| 8 | 0.047 | 5.99 | 158 | 0.037 |

- **fib**: $T_1 = \Theta(\varphi^n)$, $T_\infty = \Theta(n)$: parallelism is astronomical; 158 steals for 196417 spawned tasks (calls with $n \ge 16$), as the theorem predicts. 6.0x on 8 threads rather than 8x because two of the eight threads run on efficiency cores.
- **Quicksort**: the top-level partition is serial, so $T_\infty = \Theta(n)$ and parallelism is only $\Theta(\log n)$; speedup 4.5x over $P = 1$ at 8 threads. It is also 2.2x slower than `std::sort` at $P = 1$ (two `std::partition` passes): speedup must be quoted against the best serial code, which it beats only from $P = 2$.
- Tests: 200000 items through one deque with 3 thieves, every item obtained exactly once (about half stolen); fib(24) and a parallel quicksort equal to `std::sort`; clean under ThreadSanitizer [S35].

## Worked example: the last element

Deque holds one task at index 5: `top = 5`, `bottom = 6`. Owner takes, thief steals.

| step | owner (take) | thief (steal) |
|---|---|---|
| 1 | b = 5; bottom = 5; fence | |
| 2 | | t = 5; fence; b = bottom |
| 3 | t = top = 5; t == b: last element | reads b = 5 (sees the decrement): t >= b: EMPTY |

Alternative order, thief first: step 2' thief reads t = 5, fence, b = 6 (before the owner's store): proceeds, reads a[5], CAS(top, 5, 6) succeeds. Owner then reads t = 6 > b = 5: EMPTY, restores bottom = 6. In the remaining interleaving both see "one element" and both CAS `top` from 5: exactly one wins.

## Pitfalls

- Relaxed or acquire/release in place of the seq_cst fences: owner and thief both take the last task (SB, note 03).
- Unsigned indices: `bottom - 1` wraps on an empty deque and `t <= b` becomes true.
- Freeing the old array on growth while a thief reads it.
- Parent blocks in `sync` instead of helping: with $P$ workers and deep recursion all workers can end up blocked.
- No cutoff: task overhead dominates; the steal count explodes.

## Exam-style questions

1. **State and prove the greedy scheduling bound.** $T_P \le T_1/P + T_\infty$; complete steps at most $T_1/P$, incomplete steps each shorten the critical path [S8].
2. **State the Blumofe-Leiserson work-stealing bound and what it implies for the deque design.** Expected $T_1/P + O(T_\infty)$, $O(P T_\infty)$ steal attempts; the owner's operations dominate, so push/take must avoid RMW; steals may be expensive [S8].
3. **Why does the owner take LIFO and the thief steal FIFO?** LIFO follows the serial depth-first order (locality, space $S_1$ per worker); FIFO steals the oldest, largest subcomputation, which minimises the number of steals.
4. **Where exactly do owner and thief conflict in Chase-Lev, and how is it resolved?** Only on the last element ($t = b$ after the owner's decrement); both CAS `top`; the fences guarantee they cannot both miss each other [S9] [S25].
5. **fib scales almost linearly, quicksort does not. Explain with work and span.** fib's span is $\Theta(n)$ against exponential work; quicksort's first partition is $\Theta(n)$ serial work on the critical path, parallelism $\Theta(\log n)$.

Code: `src/cpp/work_stealing.cpp` (`ChaseLev::push`/`take`/`steal`, `Pool::spawn`/`sync`, `fib`, `qsort_par`). Sources: [S1] [S2] [S8] [S9] [S25] [S35].
