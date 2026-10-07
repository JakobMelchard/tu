# 12 Error handling and recovery

> **Sourcing.** [S6] ch. 19 (failure classes, log records, steal/no-force,
> checkpoints, ARIES data structures and passes); ARIES itself [S20] (WAL,
> pageLSN, CLRs with UndoNxtLSN, repeating history, bounded logging during
> repeated restarts); [S21] atomiccommit.html and isolation.html (how sqlite
> does it). The traces are output of `transactions.recover` and `recovery.py`.

## Failures and what must survive

| failure | lost | handled by |
|---|---|---|
| transaction failure (logic error, deadlock victim) | nothing on disk | rollback from the log |
| system crash | main memory: buffer pool, unforced log tail | restart recovery (redo + undo) |
| media failure | disk contents | archive copy + log replay |

Atomicity requires undoing uncommitted effects that reached disk; durability
requires redoing committed effects that did not.

### Buffer policies decide what recovery must do

| | **force** (write pages at commit) | **no-force** |
|---|---|---|
| **no-steal** (no uncommitted page on disk) | nothing to undo or redo (impractical) | redo only |
| **steal** (uncommitted pages may be written) | undo only | **undo and redo** (what real systems do, [S6], [S20]) |

**Write-ahead logging (WAL)** [S20], [S6]: (1) before a dirty page is written,
all log records up to its last change (its pageLSN) are on stable storage
(so undo is possible); (2) at commit, the log is forced up to the commit
record (so redo is possible). Committing then costs one sequential log write
instead of random page writes.

### Log records and simple restart

An update record $\langle T, X, v_{\text{before}}, v_{\text{after}}\rangle$
serves both directions: undo writes $v_{\text{before}}$, redo writes
$v_{\text{after}}$. Restart after a crash:

1. **Redo** forward: reapply the after-image of every update of a **committed**
   transaction (a commit record is in the stable log).
2. **Undo** backward: restore the before-image of every update of a transaction
   with neither commit nor abort (a **loser**).

Both are idempotent (running recovery twice gives the same state), which is
what makes a crash during recovery harmless. Under steal + force only step 2
is needed, under no-steal + no-force only step 1 (`transactions.recover` with
`mode="undo"` / `"redo"`; each mode is tested on 300 random runs whose disk
state obeys that policy). All of this assumes **strict** schedules (note 11):
with a dirty write, undoing the loser clobbers the winner.

**Checkpoints** bound how far back restart must read. A quiescent checkpoint
stops the system and flushes everything; a **fuzzy** checkpoint only logs the
active transactions and the dirty pages and lets work continue [S6], [S20].

## ARIES

Data structures [S6], [S20]:

| item | meaning |
|---|---|
| LSN | log sequence number, increasing |
| prevLSN | the transaction's previous log record (a per-transaction backward chain) |
| pageLSN | on each page: the LSN of the last record applied to it |
| transaction table (ATT) | active transactions, their lastLSN and status |
| dirty-page table (DPT) | dirty pages and their **recLSN**, the first LSN that may have dirtied them |
| CLR | compensation log record written when an update is undone; **redo-only**, carries **UndoNxtLSN** = the undone record's prevLSN |

Three passes after a crash:

1. **Analysis** from the last checkpoint forward: rebuild ATT and DPT; the redo
   start point is $\min$ recLSN over the DPT.
2. **Redo** from there, **repeating history**: reapply every update and every
   CLR, of winners **and losers**, unless the page is not in the DPT, the LSN is
   below the page's recLSN, or $\text{pageLSN} \ge \text{LSN}$ (already applied).
3. **Undo** all losers together, largest LSN first; each undone update writes a
   CLR; a CLR met during undo is skipped by jumping to its UndoNxtLSN.

Because CLRs are never undone and point past what they compensate, a crash
during undo followed by another restart undoes nothing twice: the logging
during repeated restarts is bounded [S20].

### Worked example (`python src/py/recovery.py`)

Stable log at the crash:

| LSN | record |
|---|---|
| 1 | $T_1$ update A: 0 → 10 |
| 2 | $T_2$ update B: 0 → 20 |
| 3 | $T_1$ update C: 0 → 30, prev 1 |
| 4 | $T_1$ commit |
| 5 | $T_1$ end |
| 6 | checkpoint: ATT = $\{T_2: 2\}$, DPT = $\{A: 1, B: 2, C: 3\}$ |
| 7 | $T_2$ update A: 10 → 40, prev 2 |
| 8 | $T_3$ update C: 30 → 50 |

Disk: page A = (40, pageLSN 7) because it was flushed (steal: $T_2$'s
uncommitted 40 is on disk); B and C were never written (value 0).

- **Analysis** from LSN 6: ATT becomes $T_2$ (lastLSN 7), $T_3$ (8), both
  losers; DPT unchanged (A, B, C already in it); redo starts at $\min = 1$.
- **Redo**: LSN 1 on A skipped (pageLSN 7 ≥ 1); LSN 2 on B redone (B = 20);
  LSN 3 on C redone (C = 30); LSN 7 on A skipped (pageLSN 7); LSN 8 on C
  redone (C = 50, a loser's update: history is repeated). **3 redone, 2 skipped.**
- **Undo** losers, largest LSN first: LSN 8 → CLR 9 (C := 30, UndoNxt none),
  end 10 for $T_3$; LSN 7 → CLR 11 (A := 10, UndoNxt 2); LSN 2 → CLR 12
  (B := 0, UndoNxt none), end 13 for $T_2$. **3 CLRs.**
- Result A = 10, B = 0, C = 30: exactly $T_1$'s committed writes.

`test_recovery.py` runs 150 random workloads (updates under strict locking,
commits, aborts, checkpoints, flushes, partial log forces), crashes them,
restarts, and compares with the committed state; 100 more crash again in the
middle of the undo pass and restart a second time.

### sqlite, for comparison

sqlite achieves atomic commit either with a **rollback journal** (original
page contents are saved before the database file is changed) or in **WAL
mode** (changes are appended to a separate write-ahead log and later copied
back in a checkpoint); WAL mode lets readers and a writer proceed concurrently
[S21].

## Pitfalls

- WAL means "log before data", not "write the log and never the data".
- Redo in ARIES includes losers' updates; they are undone afterwards.
- CLRs are redone but never undone.
- The redo start point is the minimum recLSN, not the checkpoint LSN.
- A transaction whose commit record was not forced is a loser, even if the
  application saw "commit" being requested (`test_lost_commit_means_loser`).
- No-force needs redo; steal needs undo. Easy to swap under pressure.

## Exam-style questions

1. *Steal and no-force: which recovery actions are needed?* **Undo and redo.**
2. *True or false: during ARIES redo, only committed transactions' updates are reapplied.* **False** (repeating history).
3. *A page has pageLSN 120; the log record being redone has LSN 110. Redo it?* **No.**
4. *True or false: a CLR can itself be undone later.* **False**: CLRs are redo-only [S20].
5. *In the worked example, how many CLRs does undo write?* **3** (for LSNs 8, 7, 2).

## Code

`src/py/transactions.py`: `transactions.recover` (undo/redo, undo-only,
redo-only). `src/py/recovery.py`: `recovery.AriesDB` (`update`, `commit`,
`abort`, `checkpoint`, `flush`, `force`, `crash`, `restart` with `max_clrs` for
a crash during undo), `recovery.committed_state`, `recovery.fmt`.
