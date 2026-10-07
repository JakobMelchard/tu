import itertools
import random

import networkx as nx

from greedy import (UnionFind, interval_partitioning, interval_scheduling,
                    is_spanning_tree, kruskal, prim)


def disjoint(iv):
    iv = sorted(iv)
    return all(a[1] <= b[0] for a, b in zip(iv, iv[1:]))


def brute_max_disjoint(intervals):
    best = 0
    for r in range(len(intervals), 0, -1):
        for combo in itertools.combinations(intervals, r):
            if disjoint(combo):
                return r
    return best


def test_interval_scheduling_vs_brute_force():
    rng = random.Random(0)
    for _ in range(40):
        n = rng.randint(1, 9)
        iv = []
        for _ in range(n):
            s = rng.randint(0, 15)
            iv.append((s, s + rng.randint(1, 6)))
        ch = interval_scheduling(iv)
        assert disjoint([iv[i] for i in ch])
        assert len(ch) == brute_max_disjoint(iv)


def test_interval_partitioning_depth_and_validity():
    rng = random.Random(1)
    for _ in range(40):
        n = rng.randint(1, 30)
        iv = [(s, s + rng.randint(1, 8)) for s in (rng.randint(0, 40) for _ in range(n))]
        k, assign = interval_partitioning(iv)
        for r in range(k):  # each resource holds pairwise disjoint intervals
            assert disjoint([iv[i] for i in range(n) if assign[i] == r])
        depth = max(sum(1 for s, f in iv if s <= t < f) for t in range(0, 50))
        assert k == depth


def test_union_find_invariants():
    rng = random.Random(2)
    n = 60
    uf = UnionFind(range(n))
    ref = {i: {i} for i in range(n)}  # naive partition
    for _ in range(200):
        a, b = rng.randrange(n), rng.randrange(n)
        merged = uf.union(a, b)
        assert merged == (ref[a] is not ref[b])
        if merged:
            s = ref[a] | ref[b]
            for x in s:
                ref[x] = s
        for x, y in [(rng.randrange(n), rng.randrange(n)) for _ in range(5)]:
            assert (uf.find(x) == uf.find(y)) == (ref[x] is ref[y])
    assert uf.count == len({id(s) for s in ref.values()})
    # rank bound: a root of rank r has >= 2^r elements => rank <= log2 n
    assert max(uf.rank.values()) <= n.bit_length()


def random_weighted(n, p, rng):
    nodes = list(range(n))
    edges = []
    nxg = nx.Graph()
    nxg.add_nodes_from(nodes)
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                w = rng.randint(1, 30)
                edges.append((u, v, w))
                nxg.add_edge(u, v, weight=w)
    return nodes, edges, nxg


def test_mst_weight_matches_networkx():
    rng = random.Random(3)
    for _ in range(25):
        nodes, edges, nxg = random_weighted(20, 0.3, rng)
        if not nx.is_connected(nxg):
            continue
        ref = nx.minimum_spanning_tree(nxg).size(weight="weight")
        wk, tk = kruskal(nodes, edges)
        wp, tp = prim(nodes, edges)
        assert wk == ref == wp
        assert is_spanning_tree(nodes, tk) and is_spanning_tree(nodes, tp)
        assert sum(w for _, _, w in tk) == wk


def test_is_spanning_tree_rejects_cycles_and_forests():
    nodes = [0, 1, 2, 3]
    assert is_spanning_tree(nodes, [(0, 1, 1), (1, 2, 1), (2, 3, 1)])
    assert not is_spanning_tree(nodes, [(0, 1, 1), (1, 2, 1), (2, 0, 1)])
    assert not is_spanning_tree(nodes, [(0, 1, 1), (2, 3, 1)])
