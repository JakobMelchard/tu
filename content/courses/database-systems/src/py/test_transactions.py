import random
from itertools import permutations

import pytest

import transactions as tx


def random_schedule(rng, n_tx=3, items="AB", ops=3):
    progs = {t: [(rng.choice("rw"), t, rng.choice(items)) for _ in range(ops)] + [("c", t, None)]
             for t in range(1, n_tx + 1)}
    out = []
    while any(progs.values()):
        t = rng.choice([t for t, p in progs.items() if p])
        out.append(progs[t].pop(0))
    return out


def conflict_pairs(s):
    rw = [(i, k, t, x) for i, (k, t, x) in enumerate(s) if k in "rw"]
    return {(t1, k1, x1, t2, k2) for i, k1, t1, x1 in rw for j, k2, t2, x2 in rw
            if i < j and x1 == x2 and t1 != t2 and "w" in (k1, k2)}


def brute_csr(s):
    """Conflict-equivalent to some serial schedule = same orientation of every conflicting pair."""
    target = conflict_pairs(s)
    for order in permutations(tx.txns(s)):
        serial = [op for t in order for op in s if op[1] == t]
        if conflict_pairs(serial) == target:
            return True
    return False


def test_csr_matches_brute_force_and_implies_vsr():
    rng = random.Random(0)
    for _ in range(400):
        s = random_schedule(rng)
        assert tx.conflict_serializable(s) == brute_csr(s)
        if tx.conflict_serializable(s):
            assert tx.view_serializable(s) is not None
            for order in tx.serial_orders(s):
                serial = [op for t in order for op in s if op[1] == t]
                assert conflict_pairs(serial) == conflict_pairs(s)


def test_blind_writes_vsr_not_csr():
    s = tx.parse("w1(A) w2(A) w2(B) w1(B) w3(B) c1 c2 c3")
    assert not tx.conflict_serializable(s) and tx.view_serializable(s) == (1, 2, 3)


def test_lost_update_not_serializable():
    s = tx.parse("r1(A) r2(A) w1(A) w2(A) c1 c2")
    assert sorted(tx.precedence_graph(s).edges()) == [(1, 2), (2, 1)]
    assert tx.view_serializable(s) is None


def test_recoverability_ladder():
    rng = random.Random(1)
    for _ in range(400):
        s = random_schedule(rng)
        r = tx.recoverability(s)
        assert (not r["strict"] or r["cascadeless"]) and (not r["cascadeless"] or r["recoverable"])
    assert tx.recoverability(tx.parse("w1(A) r2(A) c2 c1"))["recoverable"] is False
    assert tx.recoverability(tx.parse("w1(A) r2(A) c1 c2")) == {
        "recoverable": True, "cascadeless": False, "strict": False}
    assert tx.recoverability(tx.parse("w1(A) c1 r2(A) w2(A) c2"))["strict"] is True
    assert tx.recoverability(tx.parse("w1(A) w2(A) c1 c2")) == {
        "recoverable": True, "cascadeless": True, "strict": False}


def test_2pl_checks():
    ok = tx.check_2pl(tx.parse("sl1(A) r1(A) xl1(B) w1(B) c1 u1(A) u1(B)"))
    assert ok["legal_2pl"] and ok["strict"] and ok["rigorous"]
    not_2p = tx.check_2pl(tx.parse("xl1(A) w1(A) u1(A) xl1(B) w1(B) c1 u1(B)"))
    assert not not_2p["legal_2pl"] and "two-phase" in not_2p["violations"][0]
    clash = tx.check_2pl(tx.parse("sl1(A) r1(A) xl2(A) w2(A)"))
    assert "conflicts" in clash["violations"][0]
    strict_not_rigorous = tx.check_2pl(tx.parse("sl1(A) xl1(B) r1(A) w1(B) u1(A) c1 u1(B)"))
    assert strict_not_rigorous["strict"] and not strict_not_rigorous["rigorous"]
    unlocked_read = tx.check_2pl(tx.parse("r1(A)"))
    assert "without a lock" in unlocked_read["violations"][0]


def _run(rng, policy):
    """Random updates by 3 transactions under strict 2PL (x-locks until commit: without
    them a loser's before-image would overwrite a winner's committed value, P0 in
    [S19]), random flushes allowed by the policy, crash."""
    committed_state = {"A": 0, "B": 0, "C": 0}
    cache, disk, log, active = dict(committed_state), dict(committed_state), [], set()
    pending = {}
    for t in (1, 2, 3):
        log.append(("start", t))
        active.add(t)
    for _ in range(rng.randint(3, 12)):
        t = rng.choice(sorted(active)) if active else None
        if t is None:
            break
        if rng.random() < 0.2:
            log.append(("commit", t))
            active.discard(t)
            for x in pending.pop(t, set()):
                if policy in ("undo",):                  # force at commit
                    disk[x] = cache[x]
            continue
        free = [x for x in "ABC" if all(x not in pending.get(u, set()) for u in active if u != t)]
        if not free:
            continue
        x = rng.choice(free)
        new = rng.randrange(100)
        log.append(("update", t, x, cache[x], new))
        cache[x] = new
        pending.setdefault(t, set()).add(x)
        if policy != "redo" and rng.random() < 0.5:     # steal: flush an uncommitted page
            disk[x] = cache[x]
    committed = {r[1] for r in log if r[0] == "commit"}
    for r in log:                                       # the state recovery must produce
        if r[0] == "update" and r[1] in committed:
            committed_state[r[2]] = r[4]
    if policy == "undo/redo":                           # no-force: committed pages may be missing
        for x in "ABC":
            if rng.random() < 0.5:
                disk[x] = cache[x]
    elif policy == "redo":                              # no-steal: only committed values may be flushed
        for x in "ABC":
            if rng.random() < 0.5:
                disk[x] = committed_state[x]
    return log, disk, committed_state


@pytest.mark.parametrize("policy", ["undo/redo", "undo", "redo"])
def test_recover_restores_committed_state(policy):
    rng = random.Random(policy)
    for _ in range(300):
        log, disk, want = _run(rng, policy)
        assert tx.recover(log, disk, policy) == want
        assert tx.recover(log, tx.recover(log, disk, policy), policy) == want   # idempotent


def test_dirty_write_breaks_before_image_undo():
    """w1(A) w2(A) c2, crash: undoing loser T1 restores A = 0 and erases winner T2's 7."""
    log = [("start", 1), ("start", 2), ("update", 1, "A", 0, 5), ("update", 2, "A", 5, 7), ("commit", 2)]
    assert tx.recover(log, {"A": 7}) == {"A": 0}
    assert tx.recoverability(tx.parse("w1(A) w2(A) c2"))["strict"] is False
