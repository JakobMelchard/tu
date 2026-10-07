import math
import sqlite3

import pytest

import joins


@pytest.mark.parametrize("seed", range(6))
def test_all_algorithms_agree_with_sqlite(seed):
    r, s = joins.sample(n_r=40 + seed * 7, n_s=55, keys=5 + seed * 3, seed=seed)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE r (a, k)")
    con.execute("CREATE TABLE s (k, b)")
    con.executemany("INSERT INTO r VALUES (?, ?)", r)
    con.executemany("INSERT INTO s VALUES (?, ?)", s)
    want = sorted(con.execute("SELECT r.a, r.k, s.k, s.b FROM r JOIN s ON r.k = s.k").fetchall())
    outs = [joins.nested_loop(r, s, 1, 0)[0],
            joins.block_nested_loop(r, s, 1, 0, cap=7, M=5)[0],
            joins.index_nested_loop(r, s, 1, 0)[0],
            joins.sort_merge(r, s, 1, 0)[0],
            joins.hash_join(r, s, 1, 0, k=3)[0]]
    for out in outs:
        assert sorted(out) == want                   # bags, duplicates included


@pytest.mark.parametrize("n_r,n_s,cap,M", [(60, 90, 10, 3), (60, 90, 10, 4), (61, 5, 10, 8), (100, 100, 7, 5)])
def test_bnlj_pages_match_formula(n_r, n_s, cap, M):
    r, s = joins.sample(n_r, n_s)
    _, c = joins.block_nested_loop(r, s, 1, 0, cap, M)
    br, bs = math.ceil(n_r / cap), math.ceil(n_s / cap)
    assert c["pages_read"] == joins.cost_bnlj(br, bs, M)
    assert c["comparisons"] == n_r * n_s


def test_counts():
    r, s = joins.sample()
    assert joins.nested_loop(r, s, 1, 0)[1]["comparisons"] == len(r) * len(s)
    assert joins.index_nested_loop(r, s, 1, 0)[1]["probes"] == len(r)
    _, c = joins.sort_merge(r, s, 1, 0)
    assert c["comparisons"] <= len(r) + len(s)       # the merge is linear once sorted
    _, c = joins.hash_join(r, s, 1, 0)
    assert c["probes"] == len(r) and c["build_tuples"] == len(s)


def test_silberschatz_numbers():
    """[S6] ch. 15 running example: n_student 5000, b 100; n_takes 10000, b 400."""
    assert joins.cost_nlj(5000, 100, 400) == 2_000_100
    assert joins.cost_nlj(10000, 400, 100) == 1_000_400
    assert joins.cost_merge(100, 400) == 500
    assert joins.cost_hash(100, 400) == 1500
    assert joins.cost_bnlj(100, 400, 3) == 100 * 400 + 100   # M = 3: one outer page at a time
    assert joins.cost_bnlj(100, 400, 102) == 500             # outer fits: b_r + b_s


def test_theta_join_needs_nested_loop():
    r, s = joins.sample(20, 20)
    out, _ = joins.nested_loop(r, s, 1, 0, pred=lambda x, y: x[1] < y[0])
    assert len(out) == sum(1 for x in r for y in s if x[1] < y[0])


def test_note09_numbers():
    assert joins.cost_bnlj(50, 200, 52) == 250                  # exam question 1: outer fits
    assert joins.cost_bnlj(100, 400, 12) == 4100 and joins.cost_bnlj(400, 100, 12) == 4400
    r, s = joins.sample()
    assert len(joins.nested_loop(r, s, 1, 0)[0]) == 289
    assert joins.block_nested_loop(r, s, 1, 0, cap=10, M=4)[1]["pages_read"] == 33
    assert joins.sort_merge(r, s, 1, 0)[1]["comparisons"] == 22
