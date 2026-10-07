import itertools
import random

import networkx as nx

from flow import (FlowNetwork, bipartite_matching, capacity_scaling,
                  edmonds_karp, ford_fulkerson, min_cut, project_selection)


def random_network(n, p, rng):
    g = FlowNetwork()
    nxg = nx.DiGraph()
    for u in range(n):
        g.add_node(u)
        nxg.add_node(u)
    for u in range(n):
        for v in range(n):
            if u != v and rng.random() < p:
                c = rng.randint(1, 20)
                g.add_edge(u, v, c)
                nxg.add_edge(u, v, capacity=c)
    return g, nxg


def check_flow_conservation(g, s, t, value):
    for u in g.orig:
        out = sum(g.flow_on(u, v) for v in g.orig[u])
        inc = sum(g.flow_on(w, u) for w in g.orig if u in g.orig[w])
        for v in g.orig[u]:
            assert 0 <= g.flow_on(u, v) <= g.orig[u][v]
        if u == s:
            assert out - inc == value
        elif u == t:
            assert inc - out == value
        else:
            assert out == inc


def test_max_flow_algorithms_match_networkx_and_min_cut():
    rng = random.Random(0)
    for _ in range(25):
        g, nxg = random_network(9, 0.35, rng)
        ref = nx.maximum_flow_value(nxg, 0, 8)
        for fn in (ford_fulkerson, edmonds_karp, capacity_scaling):
            h = g.copy()
            val = fn(h, 0, 8)
            assert val == ref
            check_flow_conservation(h, 0, 8, val)
            A, cut = min_cut(h, 0, 8)
            assert 0 in A and 8 not in A
            assert cut == val  # max-flow min-cut theorem
        assert cut == nx.minimum_cut_value(nxg, 0, 8)


def test_min_cut_is_minimum_by_brute_force():
    rng = random.Random(1)
    for _ in range(10):
        g, nxg = random_network(7, 0.4, rng)
        h = g.copy()
        val = edmonds_karp(h, 0, 6)
        _, cut = min_cut(h, 0, 6)
        inner = list(range(1, 6))
        best = min(sum(c for u in {0, *S} for v, c in g.orig[u].items() if v not in {0, *S})
                   for r in range(len(inner) + 1) for S in itertools.combinations(inner, r))
        assert cut == best == val


def test_bipartite_matching_size_matches_networkx():
    rng = random.Random(2)
    for _ in range(25):
        nl, nr = rng.randint(1, 8), rng.randint(1, 8)
        edges = [(l, r) for l in range(nl) for r in range(nr) if rng.random() < 0.3]
        m = bipartite_matching(range(nl), range(nr), edges)
        assert len({l for l, _ in m}) == len(m) == len({r for _, r in m})
        assert set(m) <= set(edges)
        nxg = nx.Graph()
        nxg.add_nodes_from((("L", l) for l in range(nl)), bipartite=0)
        nxg.add_nodes_from((("R", r) for r in range(nr)), bipartite=1)
        nxg.add_edges_from((("L", l), ("R", r)) for l, r in edges)
        ref = nx.bipartite.maximum_matching(nxg, top_nodes=[("L", l) for l in range(nl)])
        assert len(m) == len(ref) // 2


def test_project_selection_vs_brute_force():
    rng = random.Random(3)
    for _ in range(30):
        n = rng.randint(1, 8)
        names = list(range(n))
        profit = {p: rng.randint(-10, 10) for p in names}
        prereq = [(p, q) for p in names for q in names if p != q and rng.random() < 0.2]
        best = max(sum(profit[p] for p in S)
                   for r in range(n + 1) for S in map(set, itertools.combinations(names, r))
                   if all(q in S for p, q in prereq if p in S))
        val, sel = project_selection(profit, prereq)
        assert val == best
        assert all(q in sel for p, q in prereq if p in sel)  # closed under prereqs
        assert sum(profit[p] for p in sel) == val
