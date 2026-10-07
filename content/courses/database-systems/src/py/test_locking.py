import random

import networkx as nx
import pytest

import locking
import transactions as tx


def random_programs(rng, n=3, items="ABC", length=3):
    return {t: [(rng.choice("rw"), rng.choice(items)) for _ in range(length)] for t in range(1, n + 1)}


@pytest.mark.parametrize("seed", range(40))
def test_strict_2pl_output_is_serializable_and_strict(seed):
    rng = random.Random(seed)
    progs = random_programs(rng)
    order = [rng.choice(list(progs)) for _ in range(200)] + [t for _ in range(10) for t in progs]
    sched = locking.Strict2PL().run(progs, order)
    s = tx.parse(sched)
    finished = {t for k, t, _ in s if k in "ca"}
    assert finished == set(progs)                   # every transaction commits or is a victim
    assert tx.conflict_serializable(s)
    assert tx.recoverability(s)["strict"]


def test_deadlock_victim_is_youngest():
    s = locking.Strict2PL()
    out = s.run({1: [("r", "A"), ("w", "B")], 2: [("r", "B"), ("w", "A")]}, [1, 2, 1, 2, 1, 1])
    assert out == "r1(A) r2(B) a2 w1(B) c1" and s.deadlocks == [[1, 2]]


def test_upgrade_deadlock():
    """Both read A under S, both want X: the classic conversion deadlock."""
    s = locking.Strict2PL()
    out = s.run({1: [("r", "A"), ("w", "A")], 2: [("r", "A"), ("w", "A")]}, [1, 2, 1, 2, 1, 1])
    assert s.deadlocks == [[1, 2]] and out.endswith("a2 w1(A) c1")


def test_wait_die_and_wound_wait_never_cycle():
    rng = random.Random(0)
    for _ in range(300):
        edges_wd, edges_ww = [], []
        for _ in range(8):
            a, b = rng.sample(range(1, 7), 2)        # a requests, b holds
            if locking.wait_die(a, b) == "wait":
                edges_wd.append((a, b))
            if locking.wound_wait(a, b) == "wait":
                edges_ww.append((a, b))
        assert nx.is_directed_acyclic_graph(nx.DiGraph(edges_wd))   # only older -> younger
        assert nx.is_directed_acyclic_graph(nx.DiGraph(edges_ww))   # only younger -> older


def test_timestamp_ordering_accepts_only_ts_order():
    rng = random.Random(1)
    for _ in range(300):
        progs = random_programs(rng, length=2)
        s, pools = [], {t: [(k, t, x) for k, x in p] for t, p in progs.items()}
        while any(pools.values()):
            t = rng.choice([t for t in pools if pools[t]])
            s.append(pools[t].pop(0))
        ok, aborted = locking.timestamp_ordering(s)
        g = tx.precedence_graph(ok)
        assert all(a < b for a, b in g.edges())       # every conflict goes old -> young


def test_thomas_write_rule():
    s = tx.parse("r1(A) w2(A) w1(A)")
    assert locking.timestamp_ordering(s)[1] == {1}
    ok, aborted = locking.timestamp_ordering(s, thomas=True)
    assert aborted == set() and ok == [("r", 1, "A"), ("w", 2, "A")]


def test_snapshot_isolation():
    db = locking.SnapshotDB({"x": 10})
    db.begin(1)
    db.begin(2)
    db.write(1, "x", db.read(1, "x") + 1)
    db.write(2, "x", db.read(2, "x") + 1)
    assert db.commit(1) is True and db.commit(2) is False    # lost update prevented
    assert db.current() == {"x": 11}
    db.begin(3)
    db.begin(4)
    db.write(4, "x", 99)
    assert db.commit(4)
    assert db.read(3, "x") == 11                             # T3 still sees its snapshot


def test_write_skew_allowed_by_si():
    db = locking.SnapshotDB({"a": 1, "b": 1})
    db.begin(1)
    db.begin(2)
    if db.read(1, "a") + db.read(1, "b") >= 2:
        db.write(1, "a", 0)
    if db.read(2, "a") + db.read(2, "b") >= 2:
        db.write(2, "b", 0)
    assert db.commit(1) and db.commit(2)
    assert sum(db.current().values()) == 0                    # invariant a + b >= 1 broken
