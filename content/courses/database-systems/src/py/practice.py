"""Multiple-choice practice items whose answers are computed, not asserted by
hand (note 13).  Each item is a stem and a list of statements; every
statement is a zero-argument function that returns True or False using the
reference implementations.  `python practice.py` prints the answer key;
test_practice.py pins it so a code change that flips an answer is noticed.

The format (several independent true/false statements per stem) is ours: the
public TISS text only says "written multiple choice exam" [S1]; how the 2027S
exam scores wrong ticks is unknown (see note 00).
"""
import random

import bplustree
import fd
import hashing
import joins
import locking
import optimizer
import recovery
import relalg as ra
import sql_lab
import storage
import transactions as tx
from fd import fs, parse


def _bounds_hold(check, trials=300):
    """Search random small instances for a counterexample to `check(R, S)`."""
    rng = random.Random(0)
    for _ in range(trials):
        R = ra.Relation(("a", "b"), {(rng.randrange(3), rng.randrange(3)) for _ in range(rng.randint(0, 6))})
        S = ra.Relation(("b",), {(rng.randrange(3),) for _ in range(rng.randint(1, 3))})
        T = ra.Relation(("a", "b"), {(rng.randrange(3), rng.randrange(3)) for _ in range(rng.randint(0, 6))})
        if not check(R, S, T):
            return False
    return True


R5, F5 = fs("ABCDE"), parse("A->B, B->C, CD->E, E->A")
R4, F4 = fs("ABCD"), parse("AB->C, C->D, D->A")


def _demo_tree():
    t = bplustree.BPlusTree(4)
    for k in [10, 20, 5, 6, 12, 30, 7, 17, 3, 25, 27, 8]:
        t.insert(k)
    return t


def _hash_demo():
    e = hashing.ExtendibleHash(2)
    for k in [1, 4, 5, 7, 10, 12, 13]:
        e.insert(k)
    return e


def _doubled_by_12():
    e = hashing.ExtendibleHash(2)
    for k in [1, 4, 5, 7, 10]:
        e.insert(k)
    before = e.doublings
    e.insert(12)
    return e.doublings > before


def _ex(ex_id):
    return next(sql for i, _, sql, _ in sql_lab.EXERCISES if i == ex_id)


def _sql(q):
    con = sql_lab.connect()
    return con.execute(q).fetchall()


def _aries():
    db = recovery.AriesDB()
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
    db2 = recovery.AriesDB(disk, log)
    return db2.restart(), db2


ITEMS = [
    ("P1", "R(ABCDE), F = {A->B, B->C, CD->E, E->A}.", [
        ("AD is a candidate key", lambda: fs("AD") in fd.candidate_keys(R5, F5)),
        ("R has exactly three candidate keys", lambda: len(fd.candidate_keys(R5, F5)) == 3),
        ("R is in 3NF", lambda: fd.is_3nf(R5, F5)),
        ("R is in BCNF", lambda: fd.is_bcnf(R5, F5)),
    ]),
    ("P2", "R(ABCD), F = {AB->C, C->D, D->A}.", [
        ("BD is a candidate key", lambda: fs("BD") in fd.candidate_keys(R4, F4)),
        ("every attribute is prime", lambda: fd.prime_attributes(R4, F4) == R4),
        ("R is in BCNF", lambda: fd.is_bcnf(R4, F4)),
        ("{C}+ = {A, C, D}", lambda: fd.closure("C", F4) == fs("ACD")),
    ]),
    ("P3", "F = {A->BC, B->C, AB->C, A->B}.", [
        ("{A->B, B->C} is a minimal cover of F", lambda: set(fd.minimal_cover(parse("A->BC, B->C, AB->C, A->B")))
         == set(parse("A->B, B->C"))),
        ("AB->C has an extraneous attribute", lambda: fd.implies(parse("A->BC, B->C"), (fs("A"), fs("C")))),
        ("F implies C->A", lambda: fd.implies(parse("A->BC, B->C, AB->C, A->B"), (fs("C"), fs("A")))),
    ]),
    ("P4", "R(ABC), F = {A->B}.", [
        ("{AB, AC} is lossless", lambda: fd.is_lossless("ABC", [fs("AB"), fs("AC")], parse("A->B"))),
        ("{AB, BC} is lossless", lambda: fd.is_lossless("ABC", [fs("AB"), fs("BC")], parse("A->B"))),
        ("{AB, AC} preserves F", lambda: fd.preserves(parse("A->B"), [fs("AB"), fs("AC")])),
        ("R is in 2NF", lambda: fd.is_2nf("ABC", parse("A->B"))),
    ]),
    ("P5", "R(ABC), F = {AB->C, C->B}.", [
        ("the BCNF decomposition {AC, BC} loses AB->C", lambda: not fd.preserves(
            parse("AB->C, C->B"), fd.bcnf_decompose("ABC", parse("AB->C, C->B")))),
        ("R is in 3NF", lambda: fd.is_3nf("ABC", parse("AB->C, C->B"))),
    ]),
    ("P6", "Relations R(a, b), T(a, b) with |R| = m, |T| = k; S(b) non-empty with |S| = n.", [
        ("|R union T| <= m + k", lambda: _bounds_hold(lambda R, S, T: len(ra.union(R, T)) <= len(R) + len(T))),
        ("|R - T| >= m - k", lambda: _bounds_hold(lambda R, S, T: len(ra.difference(R, T)) >= len(R) - len(T))),
        ("|pi_a(R)| <= m", lambda: _bounds_hold(lambda R, S, T: len(ra.project(R, ("a",))) <= len(R))),
        ("|R / S| <= m / n", lambda: _bounds_hold(lambda R, S, T: len(ra.division(R, S)) <= len(R) / len(S))),
        ("|R join S| <= m", lambda: _bounds_hold(lambda R, S, T: len(ra.natural_join(R, S)) <= len(R))),
        ("pi_a(R - T) = pi_a(R) - pi_a(T) always", lambda: _bounds_hold(
            lambda R, S, T: ra.project(ra.difference(R, T), ("a",)) == ra.difference(
                ra.project(R, ("a",)), ra.project(T, ("a",))))),
    ]),
    ("P7", "In the sql_lab database (Dan's program is NULL, Dan is the only 6th-semester student).", [
        ("E7a (NOT IN) returns no row", lambda: _sql(_ex("E7a")) == []),
        ("E7b (NOT EXISTS) returns all six students", lambda: len(_sql(_ex("E7b"))) == 6),
        ("COUNT(*) = COUNT(grade) on exam", lambda: _sql("SELECT COUNT(*) = COUNT(grade) FROM exam") == [(1,)]),
        ("AVG(grade) = SUM(grade) / COUNT(*) on exam", lambda: _sql(
            "SELECT AVG(grade) = SUM(grade) * 1.0 / COUNT(*) FROM exam") == [(1,)]),
    ]),
    ("P8", "B+ tree, n = 4 (at most 4 pointers), keys 10 20 5 6 12 30 7 17 3 25 27 8 inserted.", [
        ("the tree has 3 levels", lambda: _demo_tree().height() == 3),
        ("the root holds the single key 20", lambda: _demo_tree().root.keys == [20]),
        ("there are 5 leaves", lambda: sum(1 for _ in _demo_tree().leaves()) == 5),
        ("a point search reads 3 nodes", lambda: (lambda t: (t.search(17), t.accesses)[1])(_demo_tree()) == 3),
    ]),
    ("P9", "B+ tree with n = 100, 10^6 keys.", [
        ("height <= 4 is guaranteed", lambda: bplustree.max_height(10**6, 100) == 4),
        ("height 3 is possible (3 levels hold at most 100 * 100 * 99 keys)", lambda: 100 * 100 * 99 >= 10**6),
    ]),
    ("P10", "Extendible hashing, bucket capacity 2, h(k) = k (low bits), keys 1 4 5 7 10 12 13.", [
        ("global depth ends at 3", lambda: _hash_demo().global_depth == 3),
        ("there are 5 distinct buckets", lambda: len(_hash_demo().buckets()) == 5),
        ("inserting 12 (after 1 4 5 7 10) doubled the directory", lambda: _doubled_by_12()),
    ]),
    ("P11", "b_r = 100, b_s = 400 pages, M = 12 buffer pages.", [
        ("block NL join with r outer reads 4100 pages", lambda: joins.cost_bnlj(100, 400, 12) == 4100),
        ("block NL join with s outer is cheaper", lambda: joins.cost_bnlj(400, 100, 12) < joins.cost_bnlj(100, 400, 12)),
        ("hash join (no recursive partitioning) costs 1500", lambda: joins.cost_hash(100, 400) == 1500),
        ("sort-merge on sorted inputs costs 500", lambda: joins.cost_merge(100, 400) == 500),
    ]),
    ("P12", "External merge sort of b = 1000 pages with M = 5 buffers.", [
        ("it needs 5 passes including run generation", lambda: storage.sort_passes(1000, 5) == 5),
        ("with M = 32 it needs 2 passes", lambda: storage.sort_passes(1000, 32) == 2),
    ]),
    ("P13", "Estimation: n_r = 1000, n_s = 5000, V(A, r) = 100, V(A, s) = 1000.", [
        ("|r join_A s| is estimated as 5000", lambda: optimizer.join_size(1000, 5000, 100, 1000) == 5000),
        ("System R guesses 1/3 for A > c without statistics", lambda: optimizer.SELINGER_DEFAULTS["range"] == 1 / 3),
        ("four relations have 24 left-deep join orders", lambda: optimizer.count_left_deep(4) == 24),
        ("four relations have 120 bushy join trees", lambda: optimizer.count_bushy(4) == 120),
    ]),
    ("P14", "Schedule r1(A) w2(A) r2(B) w1(B) c1 c2.", [
        ("it is conflict-serialisable", lambda: tx.conflict_serializable(tx.parse("r1(A) w2(A) r2(B) w1(B) c1 c2"))),
        ("it is view-serialisable", lambda: tx.view_serializable(tx.parse("r1(A) w2(A) r2(B) w1(B) c1 c2")) is not None),
        ("it is recoverable", lambda: tx.recoverability(tx.parse("r1(A) w2(A) r2(B) w1(B) c1 c2"))["recoverable"]),
    ]),
    ("P15", "Schedule w1(A) r2(A) c2 c1.", [
        ("it is conflict-serialisable", lambda: tx.conflict_serializable(tx.parse("w1(A) r2(A) c2 c1"))),
        ("it is recoverable", lambda: tx.recoverability(tx.parse("w1(A) r2(A) c2 c1"))["recoverable"]),
    ]),
    ("P16", "Deadlock handling with timestamps TS(T1) < TS(T3).", [
        ("wait-die: T3 requesting a lock T1 holds is rolled back", lambda: locking.wait_die(3, 1) == "die"),
        ("wound-wait: T1 requesting a lock T3 holds waits", lambda: locking.wound_wait(1, 3) == "wait"),
    ]),
    ("P17", "Snapshot isolation (first committer wins).", [
        ("two concurrent increments of x both commit", lambda: _si_increments() == (True, True)),
        ("write skew on a + b >= 1 is possible", lambda: _si_skew()),
    ]),
    ("P18", "ARIES restart of the recovery.py demo (crash after LSN 8).", [
        ("redo reapplies 3 records", lambda: _aries()[0]["redone"] == 3),
        ("undo writes 3 CLRs", lambda: _aries()[0]["clrs"] == 3),
        ("page A ends with value 10", lambda: _aries()[1].values()["A"] == 10),
    ]),
]


def _si_increments():
    db = locking.SnapshotDB({"x": 0})
    db.begin(1)
    db.begin(2)
    db.write(1, "x", db.read(1, "x") + 1)
    db.write(2, "x", db.read(2, "x") + 1)
    return db.commit(1), db.commit(2)


def _si_skew():
    db = locking.SnapshotDB({"a": 1, "b": 1})
    db.begin(1)
    db.begin(2)
    db.write(1, "a", 0)
    db.write(2, "b", 0)
    return db.commit(1) and db.commit(2) and sum(db.current().values()) == 0


def answers():
    return {iid: [bool(f()) for _, f in stmts] for iid, _, stmts in ITEMS}


if __name__ == "__main__":
    key = answers()
    for iid, stem, stmts in ITEMS:
        print(f"{iid}  {stem}")
        for (text, _), ans in zip(stmts, key[iid]):
            print(f"     [{'T' if ans else 'F'}] {text}")
    n = sum(len(v) for v in key.values())
    print(f"{len(ITEMS)} items, {n} statements, {sum(sum(v) for v in key.values())} true")
