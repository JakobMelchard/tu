"""Concurrency-control mechanisms (note 11): strict 2PL with deadlock detection,
deadlock prevention by timestamps, timestamp ordering, snapshot isolation.

  Strict2PL.run(programs, order)
        programs: {t: [("r", x) | ("w", x), ...]}; order: the sequence of
        transaction ids that ask to take their next step.  S-lock for r,
        X-lock for w (upgrade if sole holder), all locks released at commit.
        A blocked request adds waits-for edges; a cycle is a deadlock and the
        youngest transaction on it (largest id) is aborted ([S6] ch. 18).
        Returns the executed schedule in transactions.parse notation.
  wait_die / wound_wait
        [S6] ch. 18: wait-die: older waits, younger dies (non-preemptive);
        wound-wait: older wounds (aborts) the younger holder, younger waits.
  timestamp_ordering(schedule, thomas=False)
        basic TO with R-ts/W-ts per item; Thomas' write rule ignores obsolete
        writes instead of aborting ([S6] ch. 18).
  SnapshotDB
        multiversion store: a transaction reads the last version committed
        before it started, buffers writes, and commits only if no concurrent
        transaction committed a write to the same item first (first committer
        wins).  Prevents lost updates, allows write skew ([S19] section 4.2).
"""
import networkx as nx


class Strict2PL:
    def run(self, programs, order):
        progs = {t: list(p) for t, p in programs.items()}
        locks = {}                                  # x -> {t: "s" | "x"}
        waiting = {}                                # t -> set of holders it waits for
        out, done, self.deadlocks = [], set(), []
        for t in order:
            if t in done:
                continue
            if t in waiting:
                k, x = progs[t][0]
                if self._conflicts(t, k, x, locks):
                    continue                        # still blocked: the request is repeated later
                del waiting[t]
            if not progs[t]:
                out.append(f"c{t}")
                self._release(t, locks, waiting)
                done.add(t)
                continue
            self._step(t, progs, locks, waiting, out, done)
        return " ".join(out)

    def _conflicts(self, t, k, x, locks):
        need = "s" if k == "r" else "x"
        return {u for u, m in locks.get(x, {}).items() if u != t and "x" in (need, m)}

    def _step(self, t, progs, locks, waiting, out, done):
        k, x = progs[t][0]
        blockers = self._conflicts(t, k, x, locks)
        if blockers:
            waiting[t] = blockers
            g = nx.DiGraph((a, b) for a, bs in waiting.items() for b in bs)
            try:
                cycle = nx.find_cycle(g, source=t)
            except nx.NetworkXNoCycle:
                return
            victim = max(a for a, _ in cycle)
            self.deadlocks.append(sorted(a for a, _ in cycle))
            out.append(f"a{victim}")
            self._release(victim, locks, waiting)
            waiting.pop(victim, None)
            done.add(victim)
            progs[victim] = []
            return
        held = locks.setdefault(x, {})
        held[t] = "x" if k == "w" or held.get(t) == "x" else "s"
        out.append(f"{k}{t}({x})")
        progs[t].pop(0)

    def _release(self, t, locks, waiting):
        for held in locks.values():
            held.pop(t, None)
        for u in list(waiting):
            waiting[u].discard(t)


def wait_die(ts_requester, ts_holder):
    return "wait" if ts_requester < ts_holder else "die"


def wound_wait(ts_requester, ts_holder):
    return "wound holder" if ts_requester < ts_holder else "wait"


def timestamp_ordering(s, thomas=False):
    """s in transactions.parse form; TS(Ti) = i.  Returns (accepted ops, aborted txns)."""
    rts, wts, aborted, ok = {}, {}, set(), []
    for k, t, x in s:
        if t in aborted or k not in "rw":
            continue
        if k == "r":
            if t < wts.get(x, 0):
                aborted.add(t)
                continue
            rts[x] = max(rts.get(x, 0), t)
        else:
            if t < rts.get(x, 0):
                aborted.add(t)
                continue
            if t < wts.get(x, 0):
                if thomas:
                    continue                        # obsolete write: skip it
                aborted.add(t)
                continue
            wts[x] = t
        ok.append((k, t, x))
    return ok, aborted


class SnapshotDB:
    def __init__(self, data):
        self.versions = {x: [(0, v)] for x, v in data.items()}
        self.clock = 0
        self.tx = {}

    def begin(self, t):
        self.tx[t] = {"start": self.clock, "writes": {}}

    def read(self, t, x):
        me = self.tx[t]
        if x in me["writes"]:
            return me["writes"][x]
        return max(v for v in self.versions[x] if v[0] <= me["start"])[1]

    def write(self, t, x, value):
        self.tx[t]["writes"][x] = value

    def commit(self, t):
        me = self.tx.pop(t)
        for x in me["writes"]:
            if self.versions[x][-1][0] > me["start"]:
                return False                        # first committer won: abort
        self.clock += 1
        for x, v in me["writes"].items():
            self.versions[x].append((self.clock, v))
        return True

    def current(self):
        return {x: vs[-1][1] for x, vs in self.versions.items()}


if __name__ == "__main__":
    progs = {1: [("r", "A"), ("w", "B")], 2: [("r", "B"), ("w", "A")]}
    s2 = Strict2PL()
    print("deadlock:", s2.run(progs, [1, 2, 1, 2, 1, 2, 1, 2]), " cycles", s2.deadlocks)
    s2 = Strict2PL()
    print("no deadlock:", s2.run(progs, [1, 1, 1, 2, 2, 2]))
    print("wait-die T1 asks, T3 holds:", wait_die(1, 3), "| T3 asks, T1 holds:", wait_die(3, 1))
    print("wound-wait T1 asks, T3 holds:", wound_wait(1, 3), "| T3 asks, T1 holds:", wound_wait(3, 1))
    from transactions import parse
    s = parse("r1(A) r2(A) w2(A) w1(A) c1 c2")
    print("TO:", timestamp_ordering(s), " Thomas:", timestamp_ordering(parse("r1(A) w2(A) w1(A)"), True))
    db = SnapshotDB({"alice_on_call": 1, "bob_on_call": 1})
    for t in (1, 2):
        db.begin(t)
    for t, me, other in ((1, "alice_on_call", "bob_on_call"), (2, "bob_on_call", "alice_on_call")):
        if db.read(t, me) + db.read(t, other) >= 2:  # "someone else is still on call"
            db.write(t, me, 0)
    print("write skew under SI: commits", db.commit(1), db.commit(2), "->", db.current())
