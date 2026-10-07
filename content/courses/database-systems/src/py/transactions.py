"""Schedules: serialisability, recoverability, 2PL legality, and log replay
(note 11 and the simple half of note 12).

Notation as in [S6] ch. 17-18 and [S19]: "r1(A) w2(A) c1 a2" with r/w =
read/write, c/a = commit/abort, digit = transaction.  Lock operations for
the 2PL check: "sl1(A)" shared lock, "xl1(A)" exclusive lock, "u1(A)" unlock.

  precedence_graph(s)       edge Ti -> Tj for every conflicting pair (same item,
                            different transactions, at least one write), Ti first
  conflict_serializable(s)  acyclic precedence graph ([S6] ch. 17); serial_orders
                            lists every equivalent serial order (topological sorts)
  view_serializable(s)      brute force over serial orders: same reads-from and
                            same final writes (NP-complete in general, [S6] ch. 17)
  recoverability(s)         recoverable / cascadeless (ACA) / strict
  check_2pl(s)              well-formed, compatible, two-phase, strict, rigorous
  recover(log, disk, mode)  undo/redo, undo-only, redo-only replay of a
                            physical log of (T, item, before, after) records
"""
import re
from itertools import permutations

import networkx as nx

OP = re.compile(r"(sl|xl|u|r|w)(\d+)\((\w+)\)|([ca])(\d+)")


def parse(s):
    out = []
    for m in OP.finditer(s):
        if m.group(1):
            out.append((m.group(1), int(m.group(2)), m.group(3)))
        else:
            out.append((m.group(4), int(m.group(5)), None))
    return out


def txns(s):
    return sorted({t for _, t, _ in s})


def aborted(s):
    return {t for k, t, _ in s if k == "a"}


def precedence_graph(s):
    ops = [(i, k, t, x) for i, (k, t, x) in enumerate(s) if k in "rw" and t not in aborted(s)]
    g = nx.DiGraph()
    g.add_nodes_from(t for t in txns(s) if t not in aborted(s))
    for i, k1, t1, x1 in ops:
        for j, k2, t2, x2 in ops:
            if i < j and x1 == x2 and t1 != t2 and "w" in (k1, k2):
                g.add_edge(t1, t2)
    return g


def conflict_serializable(s):
    return nx.is_directed_acyclic_graph(precedence_graph(s))


def serial_orders(s):
    g = precedence_graph(s)
    return [tuple(o) for o in nx.all_topological_sorts(g)] if nx.is_directed_acyclic_graph(g) else []


def _view(s):
    """(reads-from set, final writer per item); 0 = the initial database."""
    last, reads = {}, set()
    for n, (k, t, x) in enumerate(s):
        if k == "r":
            reads.add((t, x, last.get(x, 0), sum(1 for kk, tt, xx in s[:n] if (kk, tt, xx) == (k, t, x))))
        elif k == "w":
            last[x] = t
    return reads, last


def view_serializable(s):
    s = [op for op in s if op[0] in "rw" and op[1] not in aborted(s)]
    target = _view(s)
    for order in permutations(txns(s)):
        serial = [op for t in order for op in s if op[1] == t]
        if _view(serial) == target:
            return order
    return None


def recoverability(s):
    """Classify against [S6] ch. 17: recoverable, cascadeless, strict."""
    done = {}                              # t -> position of commit/abort
    for i, (k, t, _) in enumerate(s):
        if k in "ca":
            done[t] = i
    committed = {t for k, t, _ in s if k == "c"}
    rec = aca = strict = True
    for j, (k, t, x) in enumerate(s):
        if k not in "rw":
            continue
        for i in range(j - 1, -1, -1):     # most recent earlier write of x by someone else
            k2, t2, x2 = s[i]
            if k2 == "w" and x2 == x and t2 != t:
                open_ = done.get(t2, len(s)) > j
                if open_:
                    strict = False
                    if k == "r":
                        aca = False
                        if t in committed and not (t2 in committed and done[t2] < done[t]):
                            rec = False
                break
    return {"recoverable": rec, "cascadeless": aca and rec, "strict": strict and aca and rec}


def check_2pl(s):
    held = {}                              # (t, x) -> "s" | "x"
    unlocked, violations = set(), []
    committed_at = {t: i for i, (k, t, _) in enumerate(s) if k in "ca"}
    strict = rigorous = True
    for i, (k, t, x) in enumerate(s):
        if k in ("sl", "xl"):
            mode = k[0]
            if t in unlocked:
                violations.append(f"{i}: T{t} locks after unlocking (not two-phase)")
            for (t2, x2), m2 in held.items():
                if x2 == x and t2 != t and "x" in (mode, m2):
                    violations.append(f"{i}: T{t} {mode}-lock on {x} conflicts with T{t2}'s {m2}-lock")
            if held.get((t, x)) != "x":
                held[(t, x)] = mode
        elif k == "u":
            mode = held.pop((t, x), None)
            if mode is None:
                violations.append(f"{i}: T{t} unlocks {x} without holding it")
            unlocked.add(t)
            if i < committed_at.get(t, len(s)):
                rigorous = False
                if mode == "x":
                    strict = False
        elif k == "r" and (t, x) not in held:
            violations.append(f"{i}: T{t} reads {x} without a lock")
        elif k == "w" and held.get((t, x)) != "x":
            violations.append(f"{i}: T{t} writes {x} without an x-lock")
    legal = not violations
    return {"legal_2pl": legal, "strict": legal and strict, "rigorous": legal and rigorous,
            "violations": violations}


def recover(log, disk, mode="undo/redo"):
    """log: [("start", T) | ("update", T, x, before, after) | ("commit", T) | ("abort", T)].
    Returns the database after recovery.  Assumptions each mode relies on:
      undo/redo  steal + no-force: any update may or may not be on disk
      undo       steal + force: committed updates are on disk at commit
      redo       no-steal: uncommitted updates never reach disk
    """
    db = dict(disk)
    finished = {r[1] for r in log if r[0] in ("commit", "abort")}
    committed = {r[1] for r in log if r[0] == "commit"}
    if mode in ("undo/redo", "redo"):
        for r in log:                                   # redo forward, committed only
            if r[0] == "update" and r[1] in committed:
                db[r[2]] = r[4]
    if mode in ("undo/redo", "undo"):
        for r in reversed(log):                         # undo backward, losers only
            if r[0] == "update" and r[1] not in finished:
                db[r[2]] = r[3]
    return db


if __name__ == "__main__":
    for text in ["r1(A) r2(A) w1(A) w2(A) c1 c2",
                 "r1(A) w1(A) r2(A) w2(A) r1(B) w1(B) c1 c2",
                 "w1(A) w2(A) w2(B) w1(B) w3(B) c1 c2 c3"]:
        s = parse(text)
        print(text)
        print("   edges", sorted(precedence_graph(s).edges()), " CSR", conflict_serializable(s),
              " orders", serial_orders(s), " VSR", view_serializable(s))
        print("  ", recoverability(s))
    locked = parse("xl1(A) r1(A) w1(A) xl1(B) u1(A) sl2(A) r2(A) r1(B) w1(B) c1 u1(B) c2 u2(A)")
    print("2PL:", check_2pl(locked))
    log = [("start", 1), ("update", 1, "A", 10, 20), ("start", 2), ("update", 2, "B", 5, 6),
           ("commit", 1), ("update", 2, "A", 20, 30)]
    print("crash; disk {A: 30, B: 5} ->", recover(log, {"A": 30, "B": 5}))
