# 01 Mutual exclusion from reads and writes

Book chapter 2 [S1 §2.1-2.8]; Peterson [S10], Lamport's bakery [S11]. The
question: can threads that only **read and write** shared variables (no
read-modify-write instruction) take turns in a critical section? Yes, and the
proofs are the template for every correctness argument in the course.
Code: `src/cpp/peterson_filter.cpp`.

## Definitions

- **Thread**: a sequential program running concurrently with others on shared memory. Its run is a sequence of **events** (a read, a write, a method call starting or returning).
- **Interval** $I_A^j$: the time between two events of thread $A$. $I \to J$ ("$I$ precedes $J$") if $I$ ends before $J$ starts. $\to$ is a partial order on intervals: two intervals may overlap, then neither precedes [S1 §2.1].
- **Critical section (CS)**: code that at most one thread may execute at a time. A **lock** has `lock()` before and `unlock()` after the CS.
- **Register**: a shared variable with atomic `read` and `write` (in C++: a `std::atomic<T>` used with `load`/`store`, note 03).
- **Mutual exclusion**: $CS_A^j$ and $CS_B^k$ never overlap: $CS_A^j \to CS_B^k$ or $CS_B^k \to CS_A^j$.
- **Deadlock-freedom**: if some thread calls `lock()` and never returns, other threads still complete infinitely many CS.
- **Starvation-freedom** (lockout-freedom): every call to `lock()` eventually returns. Starvation-free implies deadlock-free.
- **Doorway**: a prefix of `lock()` that finishes in a bounded number of own steps; the rest is the **waiting section**. **$r$-bounded waiting**: if $D_A^j \to D_B^k$ then $CS_A^j \to CS_B^{k+r}$; **first-come-first-served (FCFS)** is $r = 0$ [S1 §2.5].

All algorithms here assume **sequential consistency** (every read returns the most recent write in one global order, note 03). In C++ that means `memory_order_seq_cst` atomics, the default.

## Two failed attempts and Peterson

`LockOne`: `flag[me] = true; while (flag[other]) {}`. Mutually exclusive, deadlocks if both set the flag before either reads. `LockTwo`: `victim = me; while (victim == me) {}`. Mutually exclusive, deadlocks when one thread runs alone. **Peterson** [S10] [S1 §2.3] combines them:

```
lock(me):   flag[me] = true; victim = me;
            while (flag[other] && victim == me) {}   // wait while the other wants in and I yielded last
unlock(me): flag[me] = false;
```

**Mutual exclusion, proof.** Suppose $A$ and $B$ are both in the CS. Let $A$ be the last to write `victim` (the other case is symmetric). Then
$$ w_B(\text{flag}[B]{=}1) \to w_B(\text{victim}{=}B) \to w_A(\text{victim}{=}A) \to r_A(\text{flag}[B]) \to r_A(\text{victim}).$$
$A$ entered, so it read `flag[B] == false` or `victim == B`. Nobody writes `victim` after $A$, so it read `victim == A`; hence it read `flag[B] == false`. But `flag[B] = true` was written before and $B$ is in the CS, so it was not reset. Contradiction.

**Starvation-freedom, proof.** Suppose $A$ spins forever. Then `flag[B] && victim == A` stays true. Either $B$ is outside for good (then `flag[B]` is false: contradiction), or $B$ re-enters `lock()`, which sets `victim = B` and releases $A$, or $B$ also spins forever, which needs `victim == B` too: contradiction. So $A$ waits for at most one CS of $B$.

## Filter: Peterson for $n$ threads [S1 §2.4]

$n-1$ levels. `level[i]` is the highest level thread $i$ tries to pass; `victim[L]` is one per level.

```
for L = 1 .. n-1:  level[me] = L; victim[L] = me;
                   while (exists k != me: level[k] >= L) && victim[L] == me {}
unlock:            level[me] = 0
```

**Invariant**: for $0 \le j \le n-1$, at most $n - j$ threads have reached level $j$. So level $n-1$ holds one thread: the CS. **Proof by induction.** True for $j = 0$. Assume for $j-1$ and suppose $n-j+1$ threads at level $j$. Let $A$ be the last of them to write `victim[j]`. Any other such $B$ has $w_B(\text{level}[B]{=}j) \to w_B(\text{victim}[j]) \to w_A(\text{victim}[j]) \to r_A(\text{level}[B])$, so $A$ saw `level[B]` $\ge j$ and `victim[j] == A`: $A$ cannot have passed. Contradiction.

Filter is starvation-free but **not fair**: a thread can be overtaken arbitrarily often while it climbs [S1 §2.5]. Measured cost grows fast: 164 ns (n = 2), 247 ns (n = 4), 1887 ns (n = 8) per lock+unlock [S35].

## Bakery: FCFS [S11] [S1 §2.6]

```
lock(me):  flag[me] = true; label[me] = 1 + max(label[0..n-1]);        // doorway
           while (exists k != me: flag[k] && (label[k], k) < (label[me], me)) {}
unlock:    flag[me] = false
```

$(\ell, k) < (\ell', k')$ is lexicographic: smaller label first, ties broken by id.

- **FCFS.** If $D_A \to D_B$ then $A$'s write of `label[A]` precedes $B$'s reads in its doorway, so $\text{label}_B \ge \text{label}_A + 1$. $B$ then waits while `flag[A]` is true.
- **Mutual exclusion.** Suppose $A, B$ in the CS with $(\text{label}_A, A) < (\text{label}_B, B)$. $B$'s wait for $k = A$ ended, so $B$ read `flag[A] == false` or a pair for $A$ larger than its own. A thread's labels only increase (each new one exceeds its old one), so every label of $A$ that $B$ can have read is $\le \text{label}_A$: the second case is impossible. Hence $B$ read `flag[A] == false` before $A$'s current doorway:
  $$w_B(\text{label}[B]) \to r_B(\text{flag}[A]) \to w_A(\text{flag}[A]) \to r_A(\text{label}[B]) \to w_A(\text{label}[A]),$$
  so $\text{label}_A \ge \text{label}_B + 1$. Contradiction.
- **Labels grow without bound.** With 64-bit labels this never matters in practice; §2.7 of [S1] shows bounded timestamps exist but are complicated.

Measured: 90 ns (n = 2) to 361 ns (n = 8) [S35]: cheaper than Filter at 8 threads because a waiter scans once per competitor rather than once per level.

## The lower bound [S1 §2.8]

Any deadlock-free mutual exclusion for $n$ threads from read/write registers must use at least $n$ distinct locations: Burns & Lynch [S36]; the book proves it with a **covering argument**. Idea: a thread must write before entering (otherwise others cannot know it is inside). A thread **covers** a location if its next step is a write there. Build a run where $k$ threads cover $k$ distinct locations and the lock looks free; let a new thread enter; the $k$ covering writes then erase every trace of it, and another thread enters too. This is why real locks use read-modify-write instructions (note 05): with `exchange` one word suffices.

## Worked example: a Peterson history

Threads $A$ (id 0) and $B$ (id 1) arrive together. `f` = flag, `v` = victim.

| step | event | f[0] | f[1] | v | comment |
|---|---|---|---|---|---|
| 1 | $A$: f[0] = 1 | 1 | 0 | 0 | |
| 2 | $B$: f[1] = 1 | 1 | 1 | 0 | |
| 3 | $B$: v = 1 | 1 | 1 | 1 | |
| 4 | $A$: v = 0 | 1 | 1 | 0 | $A$ is the last writer of `victim` |
| 5 | $B$: reads f[0] = 1, v = 0 | | | | $v \ne 1$: $B$ enters |
| 6 | $A$: reads f[1] = 1, v = 0 | | | | $v = 0$: $A$ spins |
| 7 | $B$: f[1] = 0 | 1 | 0 | 0 | unlock |
| 8 | $A$: reads f[1] = 0 | | | | $A$ enters |

Whoever writes `victim` last waits. Under a weak memory model step 1 can still sit in $A$'s store buffer at step 5, $B$ reads f[0] = 0 and enters, and $A$ enters too: see note 03.

## Measured: why seq_cst is not optional

`./bin/peterson_filter --bench` aligns both threads with a spin barrier every round and counts rounds in which both were inside. Three runs on the M3 Pro (Apple clang 21, `-O2`) [S35]:

| orderings of the four accesses | overlaps per $10^6$ aligned rounds |
|---|---|
| relaxed stores, relaxed loads | 1, 3, 87, 1497 |
| release stores, acquire loads | 0, 32, 167, 11918 |
| seq_cst (the correct lock) | 0 in every run |

In an unaligned tight loop the same weakened lock showed 0 overlaps in $2 \cdot 10^6$ entries: the waiter has long published its flag. **A test that does not provoke the race proves nothing.**

## Pitfalls

- Plain `bool flag[2]`: a data race, undefined behaviour; the compiler may hoist the load out of `while` and spin forever [S32].
- Release/acquire looks enough ("I publish my flag") but the proof needs the order *store then load*, which only seq_cst gives (note 03).
- Filter is starvation-free, not FCFS. Bakery is FCFS only after the doorway.
- `max(label[])` is not atomic: two threads may pick the same label. The id tie-break handles it; forgetting it breaks mutual exclusion.
- These locks are for proofs. Real locks use `exchange`/CAS and are two orders of magnitude cheaper uncontended (note 05).

## Exam-style questions

1. **Prove Peterson's lock mutually exclusive.** The last writer of `victim`, say $A$, must have read `flag[B] == false`, but $B$ set it before writing `victim` and has not reset it; contradiction (full chain above) [S1 §2.3].
2. **Is Peterson's lock starvation-free? Bound the waiting.** Yes: a waiting $A$ is released as soon as $B$ unlocks or re-enters (`victim = B`); $A$ waits for at most one CS of $B$ (1-bounded).
3. **Why does the Filter lock admit at most $n - j$ threads to level $j$?** Induction; the last writer of `victim[j]` among $n - j + 1$ threads sees another at level $\ge j$ and itself as victim, so it cannot have passed [S1 §2.4].
4. **Show the bakery lock is FCFS and explain the tie-break.** $D_A \to D_B$ implies $\text{label}_B > \text{label}_A$, and $B$ waits for $A$. Equal labels arise when doorways overlap; comparing $(\text{label}, \text{id})$ makes the order total [S11].
5. **Why do practical locks not use read/write-only algorithms?** They need $n$ locations and $O(n)$ reads per acquisition [S1 §2.8] [S36], and they require sequential consistency, which costs full fences on every modern CPU (note 03). One `exchange` on one word does the job (note 05).

Code: `src/cpp/peterson_filter.cpp` (`Peterson`, `Filter`, `Bakery`, `hammer`, `aligned_overlaps`). Sources: [S1] [S10] [S11] [S32] [S35] [S36].
