# 02 Concurrent objects, linearisability, progress

Book chapter 3 [S1]; Herlihy & Wing [S6]; Lamport's sequential consistency
[S28]. The question: what does it *mean* for a concurrent queue to be
correct? Answer: every concurrent run must look like some sequential run
that respects real time. Code: `src/cpp/ms_queue.cpp` (`linearisable`,
`record_round`).

## Definitions

- **Object**: data plus methods, specified **sequentially** by pre- and postconditions (e.g. FIFO queue: `deq()` on $[x_1, \dots, x_k]$ returns $x_1$ and leaves $[x_2, \dots]$; on $[\,]$ returns EMPTY or throws).
- **Method call** = **invocation** event $\langle A\ q.\text{enq}(x)\rangle$ + matching **response** event $\langle A\ q{:}\text{ok}\rangle$. Between them the call is **pending**.
- **History** $H$: a finite sequence of invocations and responses. $H|A$: the subsequence of thread $A$; $H|q$: of object $q$. $H$ is **sequential** if it starts with an invocation and each invocation is immediately followed by its response. $H$ is **well formed** if every $H|A$ is sequential.
- **Legal**: a sequential history that satisfies every object's sequential specification.
- **Equivalent** histories: $H|A = H'|A$ for every thread $A$.
- **Real-time order** $<_H$: $m_0 <_H m_1$ if the response of $m_0$ precedes the invocation of $m_1$ in $H$. Overlapping calls are unordered.
- **complete(H)**: $H$ with pending invocations removed.

## Three correctness conditions, weakest first

| condition | a history is correct iff | composable? |
|---|---|---|
| quiescent consistency | calls separated by a quiet period (no pending calls) take effect in real-time order | yes |
| sequential consistency [S28] | equivalent to a legal sequential history that preserves each thread's **program order** | **no** |
| linearisability [S6] | $H$ can be extended (append responses to some pending calls, drop the rest) to $H'$ with complete($H'$) equivalent to a legal sequential $S$ and $<_H \subseteq <_S$ | **yes** |

Linearisability = sequential consistency + real-time order across threads. Operationally: each call takes effect at one instant, its **linearisation point**, between invocation and response.

**Linearisability is local** [S6 §3.1]: $H$ is linearisable iff $H|x$ is linearisable for every object $x$. Proof sketch ($\Leftarrow$; the full proof [S6 §3.1] also handles pending calls): take the linearisation $<_x$ of each object; the union of all $<_x$ and $<_H$ is acyclic, because a cycle would have to alternate between objects via real-time edges, and real-time order between intervals is transitive and irreflexive; any topological sort is a legal $S$ for $H$.

**Sequential consistency is not local** (the book's two-queue example [S1 ch. 3]). $A$: `p.enq(x); q.enq(x); p.deq() -> y`. $B$: `q.enq(y); p.enq(y); q.deq() -> x`. $H|p$ is SC (put `p.enq(y)` first); $H|q$ is SC (put `q.enq(x)` first). Together, program order and the two FIFO requirements give
$$p.\text{enq}(y) \to p.\text{enq}(x) \to q.\text{enq}(x) \to q.\text{enq}(y) \to p.\text{enq}(y),$$
a cycle. So "each object is correct" does not imply "the program is correct" under SC. This is why linearisability, not SC, is the correctness condition for concurrent **objects**; SC remains the model for **memory** (note 03).

## Linearisation points in practice

| implementation | linearisation point |
|---|---|
| any object under one lock | somewhere inside the critical section |
| Treiber stack push/pop (note 08) | the successful CAS on `top`; empty pop: the load that saw `null` |
| Michael-Scott enqueue (note 07) | the CAS that links the node after the last one, not the later Tail swing |
| Michael-Scott dequeue | the CAS on Head; empty: the read of `head.next == null` |
| lazy list remove (note 06) | the write `marked = true` |
| lazy list unsuccessful contains | can be **outside** the method's own steps: the instant the key was absent, argued via other threads' steps [S1 ch. 9] |

## Progress conditions

- **Blocking**: a delayed thread can stop others (locks). **Deadlock-free**: some thread makes progress; **starvation-free**: every thread does (both assume the scheduler eventually runs every thread).
- **Non-blocking** (no thread's delay can stop the others):
  - **wait-free**: every call finishes in a finite number of its **own** steps (bounded wait-free: a fixed bound);
  - **lock-free**: in every infinite run, infinitely many calls finish (some thread always progresses; individual ones may starve);
  - **obstruction-free**: a call finishes if it runs **alone** for long enough.
- Implications: wait-free ⇒ lock-free ⇒ obstruction-free; starvation-free ⇒ deadlock-free. Wait-free and starvation-free both guarantee progress for **everyone**; lock-free and deadlock-free only for **someone** [S1 ch. 3].
- Linearisability is **non-blocking** as a property [S6]: a pending call of a total method never needs to wait for another pending call to be linearised.

## Checking a history

The checker in `ms_queue.cpp` records `inv` and `res` from one shared `fetch_add` counter, so "$a$.res < $b$.inv" really means $a$ finished before $b$ started. It then searches (Wing & Gong style):

1. The **minimal** pending calls are those whose invocation precedes the earliest response among undecided calls: any of them may be linearised next without violating $<_H$.
2. Try each: apply it to a sequential `std::deque`; if legal, recurse; else backtrack.
3. Memoise (set of linearised calls, queue contents) states known to fail.

Worst case exponential; on 18-call histories it takes 0.04 ms including recording [S35]. On the test run 400 of 400 recorded 15-call histories contained overlapping calls, all linearisable; a stack posing as a queue is rejected (5 of 10 single-thread seeds) [S35].

## Worked example: find a linearisation

Times from the shared clock; `q` initially empty.

| call | thread | inv | res |
|---|---|---|---|
| $e_1$: enq(1) | A | 0 | 5 |
| $e_2$: enq(2) | B | 1 | 6 |
| $d_1$: deq → 2 | C | 7 | 8 |
| $d_2$: deq → 1 | A | 9 | 10 |

$e_1, e_2$ overlap, so either order is allowed by $<_H$; $d_1$ returns 2 first, so FIFO forces $e_2$ before $e_1$: $S = e_2, e_1, d_1, d_2$, legal, $<_H \subseteq <_S$. **Linearisable.** Change $e_1$ to [0, 0.5] (finished before $e_2$ started): now $e_1 <_H e_2$ is forced, and $d_1 \to 2$ violates FIFO: **not linearisable**, though still sequentially consistent (reorder threads freely). Both cases are in `checker_selftest()`.

## Pitfalls

- Linearisable **methods** do not make a **sequence** of calls atomic: `if (!s.contains(x)) s.add(x);` is a race (check-then-act).
- A linearisation point may be a step of **another** thread (helping, note 07) or depend on the future (lazy contains). Say which event, and argue it lies inside the call's interval.
- Sequential consistency of memory (note 03) and linearisability of objects are different things with confusingly similar names.
- "Lock-free" is a progress condition, not "uses no mutex": a CAS retry loop in which one thread can block everyone (e.g. by holding a flag) is not lock-free.

## Exam-style questions

1. **Define linearisability precisely and contrast it with sequential consistency.** Extension $H'$, complete($H'$) equivalent to legal sequential $S$ with $<_H \subseteq <_S$ [S6]. SC keeps only per-thread program order, not real-time order between threads; SC is not composable, linearisability is.
2. **Give a history that is SC but not linearisable.** $A$: enq(1) [0,1]; $B$: enq(2) [2,3]; $C$: deq → 2 [4,5]. SC: order $B, A, C$ respects each thread; not linearisable because enq(1) precedes enq(2) in real time.
3. **Prove or sketch: linearisability is a local property.** Union of per-object linearisations and real-time order is acyclic; topological sort gives $S$ [S6 §3.1].
4. **Where is the linearisation point of an unsuccessful dequeue in the Michael-Scott queue?** The read of `head.next` returning null while Head equals Tail: at that instant the queue is empty [S14].
5. **Classify: (a) a CAS retry loop on a counter, (b) a TTAS lock, (c) the lazy list's `contains`.** (a) lock-free (some CAS succeeds each round), not wait-free (one thread can fail forever); (b) blocking, deadlock-free, not starvation-free; (c) wait-free (bounded by list length, no retries) [S1 ch. 3, 9].

Code: `src/cpp/ms_queue.cpp` (`Op`, `linearisable`, `checker_selftest`, `record_round`, `has_overlap`, `LifoByMistake`). Sources: [S1] [S6] [S14] [S28] [S35].
