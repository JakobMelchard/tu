# 08 Stacks and elimination

Book chapter 11 [S1]; Treiber 1986 [S12]; elimination backoff: Hendler,
Shavit & Yerushalmi 2004 [S17]. The stack has one hot spot, `top`, and so
cannot scale by partitioning; elimination turns contention itself into
parallelism. Code: `src/cpp/treiber_stack.cpp` (tagged Treiber stack,
deterministic ABA replay, elimination backoff stack).

## Treiber stack [S12]

```
push(n): loop { old = top; n.next = old; if CAS(top, old, n) return }          // LP: the CAS
pop():   loop { old = top; if old == null return EMPTY                           // LP: that load
                nx = old.next; if CAS(top, old, nx) return old }                 // LP: the CAS
```

Lock-free (a failed CAS means another succeeded), not wait-free. Every operation serialises on `top`: under contention most CASes fail and each failure costs a cache-line transfer. The book's first remedy is **exponential backoff** after a failed CAS, as for TTAS locks (note 05) [S1 ch. 11].

**ABA** (note 07) hits the stack in its purest form. `treiber_stack.cpp::aba_script` replays it deterministically on bare node indices:

| step | thread | action | stack (top first) |
|---|---|---|---|
| 0 | | initial | A → B → C |
| 1 | T1 | `old = top` (A), `nx = A.next` (B); stalls | |
| 2 | T2 | pop A, pop B (T2 now owns both) | C |
| 3 | T2 | push A back | A → C |
| 4 | T1 | `CAS(top, A, B)`: **succeeds** untagged | B → ? |

After step 4 `top` names B, which T2 owns and may reuse, and A (a live element) is lost. With `top = [tag:32 | index:32]` and the tag bumped on every CAS, T1 snapshotted `(A, 3)` (three pushes so far) and finds `(A, 6)` after T2's three CASes: the CAS fails. The test asserts both outcomes.

## Elimination [S17] [S1 ch. 11]

Observation: a `push(x)` and a `pop()` that overlap in time may **cancel**: the pop returns x, the stack is untouched. Linearise the pair as push immediately followed by pop, at the instant of the exchange. Any number of such pairs can happen in parallel at different places.

**Elimination backoff stack**: try the Treiber CAS once; on failure, instead of sleeping, visit a random slot of an **elimination array** (a few **exchangers**) for a short time. If a push meets a pop there, both return; if not (timeout, or push met push), retry on `top`. Under low load it behaves like Treiber with backoff; under high load more collisions happen, so it scales with contention.

**Lock-free exchanger** [S1 ch. 11]: one word per slot holding `(state, item)`, state in {EMPTY, WAITING, BUSY}.

1. EMPTY: CAS to (WAITING, my item). Spin until the state becomes BUSY: take the partner's item, reset to EMPTY. On timeout, CAS (WAITING, mine) back to EMPTY; if that fails, a partner arrived at the last moment: take its item.
2. WAITING (someone waits): CAS to (BUSY, my item) and return the waiter's item.
3. BUSY: two others are pairing; retry.

The code adds a 30-bit tag to the slot word so a waiter's withdraw CAS cannot confuse its own old entry with a new one. Push offers its node index, pop offers NIL; a push succeeds if it got NIL back, a pop if it got a node.

**Width**: few slots means more collisions but also more interference; the paper adapts the range to the load [S17]. The code uses $T/2$ slots.

## Measured

Alternating push/pop, $4 \cdot 10^5$ operations per thread, M3 Pro [S35]:

| threads | Treiber | elimination backoff | eliminated |
|---|---|---|---|
| 1 | 176 Mops/s | 175 | 0 % |
| 2 | 11.8 | 18.2 | 0 % |
| 4 | 7.4 | 9.4 | 3.5 % |
| 8 | 3.4 | 4.3 | 10.4 % |

At 2 threads nothing is eliminated and it is still 1.5x faster: the exchanger visit is a **backoff** that takes the thread off `top` for a while. At 8 threads a tenth of the operations never touch `top`. Absolute numbers collapse from 176 to 3-4 Mops/s: $1 / (3.4\ \text{Mops/s}) \approx 300$ ns per operation system-wide at 8 threads, the order of the cross-core hand-off cost measured for locks in note 05.

The test: 4 threads, random push/pop with values unique per thread, then drain; every pushed value popped **exactly once**, for both stacks (and under ThreadSanitizer) [S35].

## Worked example: an elimination

Slot `s` EMPTY. P pushes node 5, Q pops, both failed their CAS on `top` and picked slot `s`.

| step | P (push 5) | Q (pop) | slot |
|---|---|---|---|
| 1 | CAS EMPTY → (WAITING, 5) | | (W, 5) |
| 2 | spins | reads (W, 5) | |
| 3 | | CAS (W, 5) → (BUSY, NIL); returns node 5 | (B, NIL) |
| 4 | sees BUSY, partner item NIL: push done; resets EMPTY | | (E) |

Linearisation: P's push then Q's pop, both at step 3, inside both intervals.

## Pitfalls

- Pop reads `old.next` after `old` may have been popped and freed: use-after-free without reclamation (note 12) or a node pool as in the code.
- Eliminating two pushes (or two pops) with each other: both must fail and retry.
- Exchanger withdraw without CAS (plain store EMPTY): a partner that arrived just before is lost, its item vanishes.
- Tags only in the stack word but not in the free list: the free list is a Treiber stack too and has the same ABA.
- Measuring elimination with too few threads and concluding it "does nothing": its benefit grows with contention.

## Exam-style questions

1. **Give the Treiber stack and its linearisation points; is it wait-free?** Code above; successful CAS, or the load that saw null for an empty pop; lock-free, not wait-free [S12].
2. **Construct the ABA interleaving for the Treiber stack and show how a tag prevents it.** Table above; the stale CAS expects `(A, t)` but finds `(A, t+3)`.
3. **Why is an eliminated push/pop pair linearisable?** Both are pending at the exchange; placing push then pop at that instant yields a legal sequential history (the stack is unchanged by the pair) and respects real time.
4. **Why does elimination help even when no pair is eliminated?** Visiting the array delays retries on `top` (backoff), lowering contention [S17].
5. **How would you choose the elimination array width?** Adaptively: shrink on timeouts (too few partners), grow on collisions with busy slots (too many) [S17] [S1 ch. 11].

Code: `src/cpp/treiber_stack.cpp` (`IndexStack`, `aba_script`, `Exchanger::exchange`, `EliminationStack`). Sources: [S1] [S12] [S17] [S35].
