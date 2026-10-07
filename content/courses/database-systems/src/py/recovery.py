"""ARIES-style recovery in miniature (note 12), after [S20] and [S6] ch. 19.

One page = one integer item.  Buffer management is steal / no-force: any
dirty page may be written at any time, provided the write-ahead-log rule holds
(the log is forced up to the page's pageLSN first); commit forces the log up
to the commit record.  A crash loses the buffer and the unforced log tail.

Log records (dicts): update (txn, page, before, after, prev), commit, end,
clr (txn, page, after = the restored value, undo_next), ckpt (a fuzzy
checkpoint carrying copies of the transaction table and dirty-page table).

restart() runs the three passes of [S20]:
  analysis  from the last checkpoint: rebuild the transaction table (ATT:
            txn -> lastLSN, status) and the dirty-page table (DPT: page ->
            recLSN, the first LSN that may have dirtied it)
  redo      from min recLSN, "repeating history": reapply every update AND
            every CLR unless the page is not in the DPT, the LSN is below the
            page's recLSN, or pageLSN >= LSN (already on the page)
  undo      roll back the losers together, largest LSN first; each undone
            update writes a CLR whose undo_next = the update's prev, so a
            crash during undo never undoes anything twice
`max_clrs` stops the undo pass early to simulate a crash during recovery.
"""
import random


class AriesDB:
    def __init__(self, disk=None, log=None):
        self.disk = dict(disk or {})                 # page -> (value, pageLSN)
        self.log = list(log or [])
        self.flushed = len(self.log)                 # records 1..flushed are stable
        self.buffer = {}                             # page -> [value, pageLSN]
        self.att = {}                                # txn -> lastLSN (normal operation)
        self.dpt = {}                                # page -> recLSN (normal operation)

    # ---- log and buffer ---------------------------------------------------
    def append(self, **rec):
        rec["lsn"] = len(self.log) + 1
        self.log.append(rec)
        return rec["lsn"]

    def force(self, lsn):
        self.flushed = max(self.flushed, min(lsn, len(self.log)))

    def page(self, p):
        if p not in self.buffer:
            self.buffer[p] = list(self.disk.get(p, (0, 0)))
        return self.buffer[p]

    def write_page(self, p, value, lsn):
        pg = self.page(p)
        pg[0], pg[1] = value, lsn
        self.dpt.setdefault(p, lsn)

    def flush(self, p):
        if p in self.buffer:
            self.force(self.buffer[p][1])            # WAL rule
            self.disk[p] = tuple(self.buffer[p])
            self.dpt.pop(p, None)

    # ---- normal operation -------------------------------------------------
    def update(self, t, p, value):
        lsn = self.append(type="update", txn=t, page=p, before=self.page(p)[0], after=value,
                          prev=self.att.get(t))
        self.att[t] = lsn
        self.write_page(p, value, lsn)

    def commit(self, t):
        self.force(self.append(type="commit", txn=t, prev=self.att.get(t)))
        self.append(type="end", txn=t, prev=None)
        self.att.pop(t, None)

    def abort(self, t):
        self._undo({t: self.att.get(t)})
        self.att.pop(t, None)

    def checkpoint(self):
        self.append(type="ckpt", att={t: (l, "U") for t, l in self.att.items()}, dpt=dict(self.dpt))

    def crash(self, rng=None):
        """Optionally flush a random subset of pages first; return what survives."""
        rng = rng or random.Random(0)
        for p in list(self.buffer):
            if rng.random() < 0.5:
                self.flush(p)
        return dict(self.disk), self.log[:self.flushed]

    # ---- restart ----------------------------------------------------------
    def restart(self, max_clrs=None):
        att, dpt, start = {}, {}, 0
        for rec in self.log:                          # last complete checkpoint
            if rec["type"] == "ckpt":
                att, dpt, start = dict(rec["att"]), dict(rec["dpt"]), rec["lsn"]
        for rec in self.log[start:]:                  # analysis
            t = rec.get("txn")
            if rec["type"] in ("update", "clr"):
                att[t] = (rec["lsn"], "U")
                dpt.setdefault(rec["page"], rec["lsn"])
            elif rec["type"] == "commit":
                att[t] = (rec["lsn"], "C")
            elif rec["type"] == "end":
                att.pop(t, None)
        stats = {"redone": 0, "skipped": 0, "clrs": 0}
        redo_lsn = min(dpt.values(), default=len(self.log) + 1)
        for rec in self.log[redo_lsn - 1:]:           # redo: repeat history
            if rec["type"] not in ("update", "clr"):
                continue
            p = rec["page"]
            if p not in dpt or rec["lsn"] < dpt[p] or self.page(p)[1] >= rec["lsn"]:
                stats["skipped"] += 1
                continue
            self.write_page(p, rec["after"], rec["lsn"])
            stats["redone"] += 1
        for t, (_, status) in list(att.items()):
            if status == "C":                         # committed, end record lost
                self.append(type="end", txn=t, prev=None)
                del att[t]
        self.dpt = {p: l for p, l in dpt.items() if p in self.buffer}
        stats["clrs"] = self._undo({t: l for t, (l, _) in att.items()}, max_clrs)
        return stats

    def _undo(self, last, max_clrs=None):
        """Undo the given transactions (txn -> lastLSN) together, largest LSN first."""
        todo = {t: l for t, l in last.items() if l}
        for t in [t for t, l in last.items() if not l]:
            self.append(type="end", txn=t, prev=None)
        clrs = 0
        while todo:
            t = max(todo, key=todo.get)
            rec = self.log[todo[t] - 1]
            if rec["type"] == "update":
                if max_clrs is not None and clrs >= max_clrs:
                    return clrs
                lsn = self.append(type="clr", txn=t, page=rec["page"], after=rec["before"],
                                  undo_next=rec["prev"], prev=todo[t])
                self.write_page(rec["page"], rec["before"], lsn)
                clrs += 1
                nxt = rec["prev"]
            elif rec["type"] == "clr":
                nxt = rec["undo_next"]
            else:
                nxt = rec.get("prev")
            if nxt:
                todo[t] = nxt
            else:
                del todo[t]
                self.append(type="end", txn=t, prev=None)
        return clrs

    def values(self):
        pages = set(self.disk) | set(self.buffer)
        return {p: self.page(p)[0] for p in sorted(pages)}


def committed_state(log, pages, init=0):
    """What recovery must produce: last committed write per page."""
    done = {r["txn"] for r in log if r["type"] == "commit"}
    state = {p: init for p in pages}
    for r in log:
        if r["type"] == "update" and r["txn"] in done:
            state[r["page"]] = r["after"]
    return state


def fmt(rec):
    keys = [k for k in ("txn", "page", "before", "after", "prev", "undo_next") if k in rec]
    return f"{rec['lsn']:3} {rec['type']:6} " + " ".join(f"{k}={rec[k]}" for k in keys)


if __name__ == "__main__":
    db = AriesDB()
    db.update(1, "A", 10)
    db.update(2, "B", 20)
    db.update(1, "C", 30)
    db.commit(1)
    db.checkpoint()
    db.update(2, "A", 40)
    db.flush("A")                                     # steal: T2's uncommitted A reaches disk
    db.update(3, "C", 50)
    db.force(len(db.log))
    disk, log = db.crash(random.Random(1))
    print("stable log at crash:")
    for r in log:
        print("   ", fmt(r) if r["type"] != "ckpt" else f"{r['lsn']:3} ckpt   att={r['att']} dpt={r['dpt']}")
    print("disk at crash:", disk)
    db2 = AriesDB(disk, log)
    print("restart:", db2.restart(), "->", db2.values())
    print("expected committed state:", committed_state(log, "ABC"))
    print("log written by recovery:")
    for r in db2.log[len(log):]:
        print("   ", fmt(r))
