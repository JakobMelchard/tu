import random

import pytest

from recovery import AriesDB, committed_state

PAGES = "ABCD"


def workload(rng, steps=40):
    """Random strict-2PL workload: a page written by an active transaction is
    off limits to the others until it commits or aborts."""
    db, active, owner, next_t = AriesDB(), set(), {}, 1
    for _ in range(steps):
        x = rng.random()
        if x < 0.15 or not active:
            active.add(next_t)
            next_t += 1
        elif x < 0.55:
            t = rng.choice(sorted(active))
            free = [p for p in PAGES if owner.get(p) in (None, t)]
            if free:
                p = rng.choice(free)
                owner[p] = t
                db.update(t, p, rng.randrange(1, 100))
        elif x < 0.70:
            t = rng.choice(sorted(active))
            db.commit(t)
            active.discard(t)
            owner = {p: o for p, o in owner.items() if o != t}
        elif x < 0.78:
            t = rng.choice(sorted(active))
            db.abort(t)
            active.discard(t)
            owner = {p: o for p, o in owner.items() if o != t}
        elif x < 0.85:
            db.checkpoint()
        elif x < 0.95:
            db.flush(rng.choice(PAGES))
        else:
            db.force(rng.randint(db.flushed, len(db.log)))
    return db


def check_wal(disk, log):
    assert all(lsn <= len(log) for _, lsn in disk.values())


@pytest.mark.parametrize("seed", range(150))
def test_restart_restores_committed_state(seed):
    rng = random.Random(seed)
    disk, log = workload(rng).crash(rng)
    check_wal(disk, log)
    want = committed_state(log, PAGES)
    db = AriesDB(disk, log)
    db.restart()
    assert {p: db.page(p)[0] for p in PAGES} == want
    losers_updates = sum(1 for r in log if r["type"] == "update") - sum(
        1 for r in log if r["type"] == "update" and r["txn"] in
        {c["txn"] for c in log if c["type"] == "commit"})
    assert sum(1 for r in db.log if r["type"] == "clr") <= losers_updates   # nothing undone twice


@pytest.mark.parametrize("seed", range(100))
def test_crash_during_undo_then_restart_again(seed):
    rng = random.Random(1000 + seed)
    disk, log = workload(rng).crash(rng)
    want = committed_state(log, PAGES)
    db = AriesDB(disk, log)
    db.restart(max_clrs=rng.randint(0, 3))           # crash in the middle of the undo pass
    db.force(rng.randint(db.flushed, len(db.log)))
    disk2, log2 = db.crash(rng)
    check_wal(disk2, log2)
    db2 = AriesDB(disk2, log2)
    db2.restart()
    assert {p: db2.page(p)[0] for p in PAGES} == want
    undone = [(r["txn"], r["prev"]) for r in db2.log if r["type"] == "clr"]
    assert len(undone) == len(set(undone))           # each update compensated at most once


def test_demo_numbers():
    db = AriesDB()
    db.update(1, "A", 10)
    db.update(2, "B", 20)
    db.update(1, "C", 30)
    db.commit(1)
    db.checkpoint()
    db.update(2, "A", 40)
    db.flush("A")
    db.update(3, "C", 50)
    db.force(len(db.log))
    disk, log = db.crash(random.Random(1))
    db2 = AriesDB(disk, log)
    assert db2.restart() == {"redone": 3, "skipped": 2, "clrs": 3}
    assert db2.values() == {"A": 10, "B": 0, "C": 30}
    assert [r["type"] for r in db2.log[len(log):]] == ["clr", "end", "clr", "clr", "end"]


def test_lost_commit_means_loser():
    db = AriesDB()
    db.update(1, "A", 5)
    db.flush("A")                                     # WAL forces LSN 1 first
    db.log.append({"type": "commit", "txn": 1, "prev": 1, "lsn": 2})   # appended, never forced
    disk, log = db.crash(random.Random(0))
    assert len(log) == 1
    db2 = AriesDB(disk, log)
    db2.restart()
    assert db2.values() == {"A": 0}
