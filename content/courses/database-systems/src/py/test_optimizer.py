import math
import random
import sqlite3

import pytest

import optimizer as opt


def random_query(rng, n, shape):
    names = "RSTUV"[:n]
    rels = {r: (rng.choice([10, 100, 1000, 10000]), {}) for r in names}
    if shape == "chain":
        pairs = list(zip(names, names[1:]))
    elif shape == "star":
        pairs = [(names[0], r) for r in names[1:]]
    else:                                            # cycle
        pairs = list(zip(names, names[1:])) + [(names[-1], names[0])]
    preds = []
    for i, (r, s) in enumerate(pairs):
        a = f"x{i}"
        rels[r][1][a] = rng.choice([5, 50, 500])
        rels[s][1][a] = rng.choice([5, 50, 500])
        preds.append((r, a, s, a))
    filters = {r: rng.choice([1.0, 0.1, 0.01]) for r in names}
    return opt.Query(rels, preds, filters)


@pytest.mark.parametrize("n", [3, 4, 5])
@pytest.mark.parametrize("shape", ["chain", "star", "cycle"])
@pytest.mark.parametrize("bushy", [False, True])
@pytest.mark.parametrize("cross", [False, True])
def test_dp_equals_brute_force(n, shape, bushy, cross):
    rng = random.Random(f"{n}{shape}{bushy}{cross}")
    for _ in range(5):
        q = random_query(rng, n, shape)
        dp_cost, dp_plan = opt.best_plan(q, bushy=bushy, cross=cross)
        bf_cost, _, _ = opt.brute_force(q, bushy=bushy, cross=cross)
        assert math.isclose(dp_cost, bf_cost)
        assert math.isclose(opt.plan_cost(q, dp_plan), dp_cost)


def test_bushy_never_worse_and_cross_never_worse():
    rng = random.Random(9)
    for _ in range(30):
        q = random_query(rng, 5, rng.choice(["chain", "star", "cycle"]))
        ld = opt.best_plan(q)[0]
        b = opt.best_plan(q, bushy=True)[0]
        bx = opt.best_plan(q, bushy=True, cross=True)[0]
        assert bx <= b + 1e-9 <= ld + 2e-9


@pytest.mark.parametrize("n", [2, 3, 4, 5])
def test_counts_by_enumeration(n):
    names = "RSTUV"[:n]
    assert sum(1 for _ in opt.all_trees(names, bushy=False)) == opt.count_left_deep(n)
    assert sum(1 for _ in opt.all_trees(names, bushy=True)) == opt.count_bushy(n)


def test_example_numbers():
    q = opt.example()
    assert opt.best_plan(q)[0] == 200
    assert opt.best_plan(q, bushy=True) == (150, (("R", "S"), ("T", "U")))
    assert opt.plan_cost(q, ((("R", "S"), "T"), "U")) == 250
    assert opt.best_plan(q, bushy=True, cross=True)[0] == 60       # R x U has 10 tuples


def test_selectivities():
    assert opt.sel_eq(50) == 0.02
    assert opt.sel_range(30, 0, 120) == 0.75 and opt.sel_range(200, 0, 120) == 0.0
    assert math.isclose(opt.sel_and(0.1, 0.5), 0.05)
    assert math.isclose(opt.sel_or(0.1, 0.5), 0.55)
    assert opt.sel_not(0.25) == 0.75
    assert opt.SELINGER_DEFAULTS == {"eq": 0.1, "range": 1 / 3, "between": 0.25}


def test_foreign_key_join_estimate_is_exact():
    """[S6] ch. 16: a foreign key s.A -> r.A gives |r join s| = |s| exactly, and the
    formula agrees because V(A, r) = |r| >= V(A, s)."""
    rng = random.Random(0)
    r = [(i,) for i in range(500)]
    s = [(rng.randrange(500), j) for j in range(3000)]
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE r (a PRIMARY KEY)")
    con.execute("CREATE TABLE s (a, b)")
    con.executemany("INSERT INTO r VALUES (?)", r)
    con.executemany("INSERT INTO s VALUES (?, ?)", s)
    actual = con.execute("SELECT COUNT(*) FROM r JOIN s USING (a)").fetchone()[0]
    Vs = con.execute("SELECT COUNT(DISTINCT a) FROM s").fetchone()[0]
    assert actual == 3000 == opt.join_size(500, 3000, 500, Vs)


def test_uniform_estimate_close_to_actual():
    rng = random.Random(1)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE r (a)")
    con.execute("CREATE TABLE s (a)")
    con.executemany("INSERT INTO r VALUES (?)", [(rng.randrange(100),) for _ in range(2000)])
    con.executemany("INSERT INTO s VALUES (?)", [(rng.randrange(100),) for _ in range(3000)])
    actual = con.execute("SELECT COUNT(*) FROM r JOIN s USING (a)").fetchone()[0]
    assert abs(actual - opt.join_size(2000, 3000, 100, 100)) / actual < 0.1
