# 11 Transactions and multi-user synchronisation

> **Sourcing.** [S6] ch. 17 (ACID, schedules, conflict and view
> serialisability, precedence graph, recoverable and cascadeless schedules) and
> ch. 18 (2PL, strict and rigorous 2PL, deadlock handling, timestamp ordering);
> [S19] (phenomena P0-P3, snapshot isolation, write skew); [S22] (isolation
> levels in PostgreSQL); strict schedules as in [S18] (not re-read); 2PL goes
> back to [S17] (not read). Results from `transactions.py` and `locking.py`.

## ACID and schedules

A **transaction** is a sequence of reads and writes ending in commit or abort.
ACID: **atomicity** (all or nothing, note 12), **consistency** (a correct
transaction run alone preserves the integrity constraints), **isolation**
(concurrent execution looks like some serial one), **durability** (committed
effects survive failures, note 12) [S6].

A **schedule** interleaves the operations of several transactions, keeping each
transaction's own order. Notation: `r1(A)`, `w2(B)`, `c1`, `a2`. **Serial**:
no interleaving.

Two operations **conflict** iff they belong to different transactions, access
the same item, and at least one is a write (rw, wr, ww).

| notion | definition | test |
|---|---|---|
| conflict equivalent | same operations, every conflicting pair in the same order | |
| conflict serialisable (CSR) | conflict equivalent to a serial schedule | **precedence graph** acyclic: edge $T_i \to T_j$ for each conflict with $T_i$ first; serial orders = topological sorts [S6] |
| view equivalent | same reads-from relation (who wrote the value each read sees, initial value included) and same final writer per item | |
| view serialisable (VSR) | view equivalent to a serial schedule; testing is NP-complete [S6] | brute force over serial orders |

$\mathrm{CSR} \subsetneq \mathrm{VSR}$; every VSR schedule that is not CSR has
**blind writes** (a write without a preceding read of the item) [S6].

### Recoverability

| class | condition (for every $T_j$ reading or overwriting what $T_i$ wrote) |
|---|---|
| recoverable | if $T_j$ reads from $T_i$ and commits, $T_i$ commits first [S6] |
| cascadeless (ACA) | $T_j$ reads only values of committed transactions [S6] |
| strict | $T_j$ neither reads nor overwrites an item until its last writer has committed or aborted [S18] |

strict $\subset$ cascadeless $\subset$ recoverable. Strictness is what makes
before-image undo correct: `w1(A) w2(A) c2` then a crash restores $A$ from
$T_1$'s before-image and erases $T_2$'s committed value
(`test_transactions.py::test_dirty_write_breaks_before_image_undo`); [S19] calls
this P0, dirty write.

### Anomalies and isolation levels

Phenomena in [S19]'s history notation (broad reading):
P0 dirty write `w1[x]..w2[x]`, P1 dirty read `w1[x]..r2[x]`, P2 fuzzy read
`r1[x]..w2[x]`, P3 phantom `r1[P]..w2[y in P]`; plus the **lost update**
`r1[x]..r2[x]..w1[x]..w2[x]`.

| level (SQL standard) | dirty read | non-repeatable read | phantom | serialisation anomaly |
|---|---|---|---|---|
| Read Uncommitted | possible (not in PostgreSQL) | possible | possible | possible |
| Read Committed | no | possible | possible | possible |
| Repeatable Read | no | no | possible (not in PostgreSQL) | possible |
| Serializable | no | no | no | no |

Table 13.1 of [S22]. PostgreSQL's default is Read Committed; its Read Uncommitted
behaves like Read Committed [S22].

## Locking

Lock modes S (shared, for reading) and X (exclusive, for writing); S is
compatible with S only.

**Two-phase locking** [S6]: each transaction first acquires locks (growing
phase), then releases them (shrinking phase); no lock after the first unlock.
Every 2PL schedule is conflict serialisable, in the order of the transactions'
**lock points** (their last acquisition). Proof sketch: an edge $T_i \to T_j$
means $T_j$ locked an item after $T_i$ released it, so $T_i$'s lock point
precedes $T_j$'s; a cycle would make a lock point precede itself.

| variant | rule | adds |
|---|---|---|
| basic 2PL | two phases | CSR |
| strict 2PL | X-locks held until commit/abort | strict schedules, no cascading aborts [S6] |
| rigorous 2PL | all locks held until commit/abort | serial order = commit order; what most systems implement [S6] |

2PL does not prevent **deadlocks**. Detection: the **waits-for graph** has an
edge $T_i \to T_j$ if $T_i$ waits for a lock $T_j$ holds; deadlock iff a cycle
[S6]; abort a victim. Prevention by timestamps (older = smaller TS) [S6]:

| scheme | older requests, younger holds | younger requests, older holds |
|---|---|---|
| wait-die (non-preemptive) | older **waits** | younger **dies** (rolled back, keeps its TS) |
| wound-wait (preemptive) | older **wounds** the younger (rollback) | younger **waits** |

Waits then only go one way in age, so no cycle can form
(`test_locking.py::test_wait_die_and_wound_wait_never_cycle`).

**Timestamp ordering** [S6]: keep $R$-$TS(Q)$, $W$-$TS(Q)$. $T$ reading $Q$
with $TS(T) < W$-$TS(Q)$ aborts; $T$ writing $Q$ with $TS(T) < R$-$TS(Q)$ or
$< W$-$TS(Q)$ aborts; **Thomas' write rule** ignores the obsolete write in the
last case instead. Conflicts then always go from older to younger.

**Multiversion / snapshot isolation (SI)** [S19]: a transaction reads the
last version committed before it started; at commit, if a concurrent
transaction already committed a write to an item it also wrote, it aborts
(**first committer wins**). SI prevents dirty reads, fuzzy reads and lost
updates, but allows **write skew**: two doctors on call, each checks "the other
is still on call" and goes off; both commit; nobody is on call.

## Worked examples

**Schedules** (`python src/py/transactions.py`):

| schedule | precedence edges | CSR | VSR | recoverability |
|---|---|---|---|---|
| `r1(A) r2(A) w1(A) w2(A) c1 c2` (lost update) | 1→2, 2→1 | no | no | cascadeless, not strict |
| `r1(A) w1(A) r2(A) w2(A) r1(B) w1(B) c1 c2` | 1→2 | yes, order 1, 2 | yes | recoverable, not cascadeless |
| `w1(A) w2(A) w2(B) w1(B) w3(B) c1 c2 c3` | 1→2, 2→1, 1→3, 2→3 | no | **yes**, 1, 2, 3 (blind writes) | cascadeless, not strict |

**Deadlock under strict 2PL** (`locking.Strict2PL`): $T_1$: `r(A) w(B)`,
$T_2$: `r(B) w(A)`, alternating requests. $T_1$ takes S(A), $T_2$ takes S(B);
$T_1$ asks X(B), waits for $T_2$; $T_2$ asks X(A), waits for $T_1$: cycle
$\{1, 2\}$, the younger $T_2$ is aborted; executed schedule
`r1(A) r2(B) a2 w1(B) c1`. Two transactions reading then upgrading the same item
deadlock the same way (conversion deadlock, `test_upgrade_deadlock`). Over 40
random workloads, every schedule the scheduler emits is conflict serialisable
and strict.

**Lock legality** (`transactions.check_2pl`):
`xl1(A) r1(A) w1(A) xl1(B) u1(A) sl2(A) r2(A) r1(B) w1(B) c1 u1(B) c2 u2(A)`
is legal 2PL (no lock after `u1(A)`) but **not strict**: $T_1$ releases the
X-lock on $A$ before committing and $T_2$ reads the uncommitted $A$.

## Pitfalls

- A conflict needs **different** transactions and at least one write; two reads never conflict.
- The precedence graph ignores aborted transactions.
- 2PL guarantees CSR, not freedom from deadlock or from cascading aborts (strict 2PL does the latter).
- Wait-die: the **younger** requester dies; wound-wait: the **older** requester wounds.
- SI is not serialisable (write skew); PostgreSQL's Repeatable Read is SI-based and prevents phantoms [S22].

## Exam-style questions

1. *`r1(A) w2(A) r2(B) w1(B) c1 c2`: conflict serialisable?* **No** (1→2 on $A$, 2→1 on $B$).
2. *`w1(A) r2(A) c2 c1`: recoverable?* **No**: $T_2$ commits after reading from uncommitted $T_1$.
3. *True or false: every schedule produced by strict 2PL is cascadeless.* **True**.
4. *Wound-wait, $TS(T_1) < TS(T_3)$, $T_1$ requests a lock $T_3$ holds. What happens?* **$T_3$ is rolled back** (wounded).
5. *Under SI, two transactions concurrently increment the same counter. Both commit?* **No**: first committer wins, the second aborts (lost update prevented).

## Code

`src/py/transactions.py`: `transactions.parse`, `transactions.precedence_graph`,
`transactions.conflict_serializable`, `transactions.serial_orders`,
`transactions.view_serializable`, `transactions.recoverability`,
`transactions.check_2pl`. `src/py/locking.py`: `locking.Strict2PL`,
`locking.wait_die`, `locking.wound_wait`, `locking.timestamp_ordering`,
`locking.SnapshotDB`. The CSR test is checked against a brute-force
conflict-equivalence search on 400 random schedules.
