import random

import networkx as nx

from reachability import (certify_unreachable, inductive_count, kosaraju_scc,
                          nl_reachable, reachable_savitch, savitch_reach, two_sat,
                          two_sat_brute)


def random_digraph(rng, n, p):
    g = {u: [v for v in range(n) if u != v and rng.random() < p] for u in range(n)}
    nxg = nx.DiGraph()
    nxg.add_nodes_from(range(n))
    nxg.add_edges_from((u, v) for u in g for v in g[u])
    return g, nxg


def test_nl_and_savitch_match_networkx():
    rng = random.Random(2)
    for _ in range(40):
        g, nxg = random_digraph(rng, 7, 0.2)
        for s, t in [(0, 6), (3, 1), (5, 5)]:
            ref = nx.has_path(nxg, s, t)
            assert nl_reachable(g, s, t) == ref
            assert reachable_savitch(g, s, t) == ref


def test_savitch_recursion_depth_is_log():
    n = 16
    g = {u: [u + 1] if u + 1 < n else [] for u in range(n)}  # path 0 -> 15
    trace = [0]
    assert savitch_reach(g, 0, 15, 4, trace) and trace[0] == 4  # 2^4 >= 15
    assert not savitch_reach(g, 0, 15, 3)  # 2^3 = 8 < 15: too short


def test_2sat_matches_brute_force():
    rng = random.Random(4)
    for _ in range(80):
        n = rng.randint(1, 5)
        cnf = [tuple(rng.choice((1, -1)) * rng.randint(1, n) for _ in range(2))
               for _ in range(rng.randint(1, 8))]
        a = two_sat(cnf, n)
        assert (a is not None) == (two_sat_brute(cnf, n) is not None)
        if a is not None:
            assert all(a[abs(x)] == (x > 0) or a[abs(y)] == (y > 0) for x, y in cnf)


def test_scc_matches_networkx():
    rng = random.Random(9)
    for _ in range(20):
        g, nxg = random_digraph(rng, 8, 0.25)
        comp = kosaraju_scc(g)
        ref = {u: i for i, c in enumerate(nx.strongly_connected_components(nxg)) for u in c}
        for u in g:
            for v in g:
                assert (comp[u] == comp[v]) == (ref[u] == ref[v])


def test_inductive_counting_and_certificate():
    rng = random.Random(6)
    for _ in range(15):
        g, nxg = random_digraph(rng, 6, 0.25)
        reach = nx.descendants(nxg, 0) | {0}
        tr = []
        assert inductive_count(g, 0, tr) == len(reach)
        assert tr == sorted(tr) and tr[0] == 1  # counts are nondecreasing
        for t in range(6):
            assert certify_unreachable(g, 0, t) == (t not in reach)
