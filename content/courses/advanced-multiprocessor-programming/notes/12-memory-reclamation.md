# 12 Memory reclamation: hazard pointers and epochs

Michael's hazard pointers [S26]; Fraser's epoch-based reclamation [S27,
§5.2.3]. The revised first edition of the book [S1] is written for Java and
relies on the garbage collector; the 2020 second edition adds a chapter on
manual memory management (unverified: chapter number and content not checked,
see `refs/SOURCES.md` S1). In C/C++, which the project uses [S2], this is
where lock-free code most often breaks. Code: `src/cpp/hazard_pointers.cpp`.

## The problem

A lock-free `pop` reads `t = top` and then `t->next`. Between the two another thread may pop `t` and `delete` it: the read is a **use-after-free** (undefined behaviour; in practice garbage or a crash). If the memory is reused for a new node at the same address, the later `CAS(top, t, ...)` succeeds on a different node: **ABA** (note 07). A node that is unlinked must not be freed while any thread may still dereference it.

- **Retire**: hand an unlinked node to the reclamation scheme instead of freeing it.
- **Safe to free**: no thread holds (or can later obtain) a reference.
- **Reference counting** per node does not solve it cheaply: incrementing the count of `t` itself dereferences `t`, which may already be freed [S26].

## Hazard pointers [S26]

Each thread owns $K$ **hazard pointer** slots (single-writer, multi-reader). $H = NK$ slots in total for $N$ threads.

```
protect(src):  p = src.load()
               loop: hp[me] = p                 // publish (seq_cst store)
                     q = src.load()             // validate (seq_cst load)
                     if q == p: return p        // p was reachable after being published
                     p = q
retire(n):     rlist.push(n); if |rlist| >= R: scan()
scan():        read all H slots into a set; free every n in rlist not in the set; keep the rest
```

**Safety.** A node is freed only by `scan` after it was unlinked. If thread $T$ dereferences $p$, then $T$ published $p$ and afterwards saw $p$ still reachable from `src`, so the unlink happened after the publication; `scan` runs after the unlink and therefore reads $T$'s slot after the publication and keeps $p$. The argument is a store-then-load handshake (publish, then re-read `src`; unlink, then read slots): the SB pattern of note 03, so both sides need seq_cst.

**Bound.** Choose $R = H + \Omega(H)$ [S26]. A scan finds at most $H$ protected nodes, so it frees at least $R - H = \Omega(H)$ of the $R$ retired: $O(1)$ amortised time per retired node, and at most $N R$ retired-but-unfreed nodes in the system at any time. The code uses $K = 1$ (a Treiber stack pop needs one), $R = 2H$.

**Properties**: wait-free `scan` and `retire`; **bounded** garbage even if a thread stalls forever; cost: a seq_cst store and a re-read per **protected pointer** traversed (a list traversal needs a hand-over-hand of two or three slots).

## Epoch-based reclamation [S27, §5.2.3]

A global epoch $e$; each thread has `active` and `local_epoch`, and three limbo lists.

```
enter():  active = true; local_epoch = global; fence(seq_cst)       // once per operation
          (every so often) try_advance: if every ACTIVE thread has local_epoch == global: global++
leave():  active = false
retire(n): limbo[local_epoch mod 3].push(n)
on entering an epoch e for the first time: free limbo[e mod 3]       // holds nodes retired in epoch <= e - 3
```

**Safety.** A node retired in epoch $e$ was unlinked by a thread in epoch $e$. Any thread that can hold a reference to it was active in epoch $e$ or $e - 1$ when it read it. The global epoch reaches $e + 1$ only when every active thread has announced $e$, and $e + 2$ only when every active thread has announced $e + 1$; by then every thread that was active in epoch $\le e$ has left its operation. So a node retired in $e$ is safe once the epoch is $e + 2$ [S27]; the three rotating lists implement exactly that (the code frees one epoch later still, which is also safe).

**Properties**: per operation only two stores and a fence, no per-pointer work: cheaper traversals. But a thread **stalled inside an operation** stops the epoch from advancing: garbage grows **without bound**. Not suitable when threads can be descheduled for long inside operations; hazard pointers are.

## How the test makes a use-after-free observable

`delete` followed by a read is undefined behaviour, so a test cannot "check" it. In test mode the disposer **poisons** instead: `alive = 0`, memory kept in a graveyard freed at the end. `pop` checks `alive` of the node it protected, after an adjustable delay `window` that widens the race. Measured (4 threads, 2026-09-28) [S35]:

| scheme | window | violations | freed during run / retired |
|---|---|---|---|
| hazard pointers | 0 | 0 | 399984 / 400000 |
| epochs | 0 | 0 | 313631 / 400000 |
| hazard pointers | 64 | 0 | 99984 / 100000 |
| epochs | 64 | 0 | 73974 / 100000 |
| unsafe (free at once) | 0 | 0 at 2, 4, 8 threads | all |
| unsafe (free at once) | 64 | 0 / 18 / 815 at 2 / 4 / 8 threads | all |

Every retired node is freed exactly once after a final `quiesce()` (asserted). Note the unsafe line with window 0: **the bug exists and the test does not see it**. Only widening the window exposes it; and HP and epochs stay at zero with the wide window, which is the real evidence. A direct check of the HP bound: thread 1 protects one node, thread 0 retires 64: its list stays below $2H = 8$ and the protected node survives (`test`).

Real `delete`, push+pop pairs [S35]:

| threads | hazard pointers | epochs |
|---|---|---|
| 1 | 48.8 ns/pair | 27.4 |
| 2 | 301 | 149 |
| 4 | 465 | 484 |
| 8 | 2655 | 3046 |

Uncontended, epochs are 1.8x cheaper (no per-pointer publication). From 4 threads on the single `top` word (and `malloc`) dominate both.

## Worked example: a hazard pointer saves a pop

Stack `A → B`. Threads P, Q both pop. Slots `hp[P]`, `hp[Q]`.

| step | P | Q | effect |
|---|---|---|---|
| 1 | p = top = A; hp[P] = A; re-read top = A: protected | | |
| 2 | | protects A, CAS(top, A, B) ok, retire(A) | A unlinked |
| 3 | | scan: hazards {A} (P's slot): A kept | not freed |
| 4 | reads A->next (safe), CAS(top, A, B) fails (top is B) | | retry |
| 5 | hp[P] = B ... | | |
| 6 | | a later scan: A no longer hazardous: freed | |

Without step 1's validation P could have published A **after** Q's scan read the slots: then A is freed while P uses it.

## Pitfalls

- Publishing the hazard pointer without re-reading the source: the node may have been unlinked and scanned before the publication.
- Release/acquire instead of seq_cst on publish and scan: the SB pattern; both sides can miss each other.
- Retiring a node that is still reachable (retire only after the unlinking CAS succeeded).
- Epochs in a system with long-running or preempted operations: unbounded memory.
- "It passed the stress test": use-after-free windows are nanoseconds wide; poison and widen, or run under a sanitizer.

## Exam-style questions

1. **Why can a lock-free stack not just `delete` a popped node in C++?** Another thread may have read the pointer and be about to dereference it or CAS with it: use-after-free and ABA [S26].
2. **Describe hazard pointers and argue safety.** Publish, validate, retire list, scan with threshold $R$; a validated hazard is published before the unlink, so any scan after the unlink sees it [S26].
3. **Give the bound on unreclaimed nodes and amortised cost of hazard pointers.** $R = H + \Omega(H)$: each scan frees $\Omega(H)$ nodes, $O(1)$ amortised per retire; at most $N R$ unreclaimed [S26].
4. **Explain epoch-based reclamation and its failure mode.** Announce epoch on entry; advance when all active threads announced; free after two advances; a stalled active thread blocks advancement, garbage unbounded [S27].
5. **Does a garbage collector solve ABA?** Mostly: a node referenced by a stalled thread is never freed, so its address cannot be reused; ABA on values (not addresses) remains possible, and GC does not help structures that recycle nodes themselves (free lists) [S26].

Code: `src/cpp/hazard_pointers.cpp` (`HazardPointers::protect`/`retire`/`scan`, `Epochs::enter`/`try_advance`, `Unsafe`, `Disposer`, `Stack::pop`). Sources: [S1] [S2] [S26] [S27] [S35].
