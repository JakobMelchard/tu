# 04 Consensus numbers and universality

Book chapters 4 to 6 [S1]; Herlihy 1991 [S7]; the impossibility technique
comes from Fischer, Lynch & Paterson [S29]. TISS: "consensus, impossibility
and universality results" [S2]. The question: which synchronisation
instructions are strong enough to build **every** wait-free object? Answer: a
hierarchy, with compare-and-swap at the top. No dedicated program; every
CAS-based structure in `src/cpp` is the constructive side of this note.

## Definitions

- **Consensus object**: each of $n$ threads calls `decide(v)` at most once; every call returns the same value (**consistent**) and that value was some thread's input (**valid**); the implementation is **wait-free** [S1 ch. 5].
- **Consensus number** of a class of objects $X$: the largest $n$ for which $X$ objects plus atomic read/write registers implement wait-free $n$-thread consensus; $\infty$ if there is no largest [S7 Def. 1].
- **Protocol state**: the state of all threads and objects. A state is **bivalent** if both decisions 0 and 1 are still reachable, **$x$-valent** (univalent) if only $x$ is. A **critical state** is bivalent, and every thread's next move makes it univalent.
- **Lemma (existence)**: a wait-free 2-valued protocol has a bivalent initial state (validity: inputs (0,1) with A alone decide 0, B alone decide 1) and therefore a critical state (otherwise extend a bivalent run forever, contradicting wait-freedom) [S1 ch. 5].

**Theorem [S7]**: if $X$ has consensus number $n$ and $Y$ has $m < n$, there is no wait-free implementation of $X$ from $Y$ for more than $m$ threads (it would solve $n$-consensus with $Y$).

## Registers: consensus number 1

Two threads $A, B$ in a critical state $s$; $A$'s move leads to 0-valent, $B$'s to 1-valent. Case analysis on the moves:

1. **One reads** (say $A$). Compare $s \cdot A \cdot B^{\text{solo}}$ with $s \cdot B^{\text{solo}}$. $A$'s read changed only $A$'s local state, so $B$ running alone cannot tell the two apart and decides the same value in both. But the first is 0-valent, the second 1-valent. Contradiction.
2. **Both write different registers.** $s \cdot A \cdot B$ and $s \cdot B \cdot A$ are the same state: one is 0-valent, the other 1-valent. Contradiction.
3. **Both write the same register.** $s \cdot A \cdot B$ and $s \cdot B$ differ only in $A$'s local state ($B$ overwrote $A$'s write); $B$ running alone cannot distinguish. Contradiction.

So registers cannot solve 2-consensus: consensus number 1 [S7]. Consequence: **no wait-free queue, stack or set from reads and writes**.

## FIFO queues: consensus number exactly 2

**At least 2.** Queue initialised to [WIN, LOSE]; array `proposed[2]`.

```
decide(v): proposed[me] = v;
           if (q.deq() == WIN) return v;          // I dequeued first
           else return proposed[other];            // the other one did, and wrote first
```

Wait-free, consistent (exactly one gets WIN), valid (the winner wrote its proposal before dequeuing).

**At most 2** [S7 §3.3] [S1 ch. 5]. Three threads $A, B, C$, critical state $s$; $A$ leads to 0-valent, $B$ to 1-valent. Both moves must be queue operations on the same queue (registers are covered above, different objects commute).

- **Both deq**: $s \cdot A \cdot B$ and $s \cdot B \cdot A$ differ only in which of $A, B$ holds which item; $C$ running alone sees the same queue. Contradiction.
- **$A$ enq($a$), $B$ deq**: if the queue is non-empty the two operations commute ($B$ takes the old head either way), so $C$ cannot observe the order. If it is empty, the 1-valent state $s \cdot B \cdot A$ ($B$ gets EMPTY, then $a$ is enqueued) is indistinguishable to $C$ from the 0-valent state $s \cdot A$ ($A$ alone enqueues). Contradiction.
- **Both enq ($a$, $b$)**: execution 1: $A$ then $B$ enqueue (queue ends $a\,b$); run $A$ alone until it dequeues (it gets $a$), then $B$ alone until it dequeues ($b$). Execution 2: $B$ then $A$ enqueue; $A$ runs until it dequeues ($b$), then $B$ ($a$). Up to those dequeues neither $A$ nor $B$ can have observed the order (the queue is only observable through `deq`), and afterwards the queue and all shared objects are the same: $C$ cannot distinguish a 0-valent from a 1-valent state. Contradiction [S7 Thm. 7].

Trivial variations give consensus number 2 for sets, stacks, double-ended queues and priority queues [S7]. Same for `test_and_set`, `exchange` (swap) and `fetch_add`: their two moves commute or overwrite for a third thread.

## The hierarchy [S7 Fig. 1]

| consensus number | objects / instructions |
|---|---|
| 1 | atomic read/write registers |
| 2 | test&set, swap, fetch&add, queue, stack |
| $2n - 2$ | $n$-register assignment |
| $\infty$ | compare&swap, fetch&cons, memory-to-memory move and swap, augmented queue (with `peek`), sticky byte |

**CAS solves $n$-consensus for every $n$**: `r` initially EMPTY; `decide(v)`: `CAS(r, EMPTY, v)`; return `r`. The first CAS wins, everyone reads the winner. LL/SC (load-linked/store-conditional, the ARM and POWER primitive) is also universal.

## Universality [S1 ch. 6] [S7]

**Theorem**: $n$-thread consensus objects plus registers implement **any** sequentially specified object wait-free for $n$ threads.

**Lock-free universal construction.** The object's state is the sequential object applied to a **log** of invocations, kept as a linked list from a sentinel. To apply invocation $x$: create node $x$; repeat: at the current head, run the consensus object stored **in the head node** (`head.decideNext(x)`), append the winner, advance the head; stop when the winner is $x$. Then replay the log from the start on a private copy to compute the response. Every round appends someone's node, so some call finishes: lock-free, not wait-free (a thread can lose every round).

**Wait-free construction.** Add `announce[n]`: a thread first announces its node. Each thread, at log position $k$, proposes not its own node but `announce[k mod n]` if that is still unappended (**helping**). Within $n$ rounds after announcing, the position with $k \bmod n = i$ comes up and every thread proposes thread $i$'s node, so it is appended: every call finishes in $O(n)$ rounds. Consensus objects are one-shot, which is why each log node carries its own.

**Consequence**: CAS alone (with registers) suffices to build wait-free versions of everything in this course. The constructions are slow ($O(\text{log length})$ replay); the rest of the course is about **efficient** lock-free structures.

## Asynchronous messages: FLP [S29]

The same valence technique proves that consensus is impossible in an asynchronous message-passing system if even one process may crash: there is always a bivalent successor state. Shared memory with CAS escapes it; message passing needs timing assumptions or randomisation.

## Worked example: queue consensus trace

$A$ proposes 7, $B$ proposes 9. Queue [WIN, LOSE].

| step | event | proposed | queue |
|---|---|---|---|
| 1 | $B$: proposed[1] = 9 | [ -, 9 ] | [WIN, LOSE] |
| 2 | $A$: proposed[0] = 7 | [7, 9] | |
| 3 | $A$: deq → WIN | | [LOSE] |
| 4 | $B$: deq → LOSE, return proposed[0] = 7 | | [ ] |
| 5 | $A$: return 7 | | |

Why must the proposal be written **before** the deq? If $A$ wrote after, $B$ could read `proposed[0]` before step 2 and return garbage.

## Pitfalls

- Consensus numbers are about **wait-free** implementations. With a lock anything is implementable, but not wait-free.
- `fetch_add` is "powerful" in practice (counters, tickets) and still only consensus number 2; CAS is not faster, it is **stronger**.
- The critical-state proofs need every case, including the one where the operations are on different objects (they commute).
- Consensus number 2 for queues does not contradict the lock-free Michael-Scott queue: it is built from CAS (consensus number $\infty$), not from queues.

## Exam-style questions

1. **Prove that atomic registers cannot solve 2-thread wait-free consensus.** Critical state; cases read/any, write/write different, write/write same; each yields two states one thread cannot tell apart but of different valence [S7].
2. **Give a 2-thread consensus protocol from a queue and argue it is correct.** Above; the WIN dequeuer decides its own value; the other reads the winner's proposal, written before the deq.
3. **Why can a queue not solve 3-thread consensus?** Cases deq/deq, enq/deq, enq/enq; in each the third thread cannot distinguish the two orders [S7 §3.3].
4. **Show CAS has consensus number $\infty$ and state what follows for implementations.** `CAS(r, EMPTY, v)`, return `r`; consequently no wait-free CAS from queues, stacks, `fetch_add` or registers for 3 or more threads [S7].
5. **Outline the wait-free universal construction. Where does helping enter and why is it needed?** Log of invocations agreed by per-node consensus; `announce[]` plus proposing `announce[k mod n]` guarantees each announced call is appended within $n$ rounds; without helping, the construction is only lock-free [S1 ch. 6].

Sources: [S1] [S2] [S7] [S29].
