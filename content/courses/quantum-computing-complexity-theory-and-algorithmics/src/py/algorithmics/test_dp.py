import itertools
import math
import random

import networkx as nx

from dp import (bellman_ford, floyd_warshall, knapsack_01, lcs,
                sequence_alignment, subset_sum, weighted_interval_scheduling)


def compatible(iv):
    iv = sorted(iv)
    return all(a[1] <= b[0] for a, b in zip(iv, iv[1:]))


def test_weighted_interval_scheduling_vs_brute_force():
    rng = random.Random(0)
    for _ in range(40):
        n = rng.randint(1, 9)
        jobs = []
        for _ in range(n):
            s = rng.randint(0, 12)
            jobs.append((s, s + rng.randint(1, 5), rng.randint(1, 10)))
        best = 0
        for r in range(n + 1):
            for combo in itertools.combinations(range(n), r):
                if compatible([jobs[i][:2] for i in combo]):
                    best = max(best, sum(jobs[i][2] for i in combo))
        val, chosen = weighted_interval_scheduling(jobs)
        assert val == best
        assert compatible([jobs[i][:2] for i in chosen])
        assert sum(jobs[i][2] for i in chosen) == val


def test_subset_sum_and_knapsack_vs_brute_force():
    rng = random.Random(1)
    for _ in range(40):
        n = rng.randint(1, 8)
        w = [rng.randint(1, 10) for _ in range(n)]
        v = [rng.randint(1, 20) for _ in range(n)]
        W = rng.randint(1, 25)
        reach = {sum(w[i] for i in c) for r in range(n + 1) for c in itertools.combinations(range(n), r)}
        assert subset_sum(w, W)[0] == (W in reach)
        best = max(sum(v[i] for i in c) for r in range(n + 1)
                   for c in itertools.combinations(range(n), r) if sum(w[i] for i in c) <= W)
        val, chosen = knapsack_01(w, v, W)
        assert val == best
        assert sum(w[i] for i in chosen) <= W and sum(v[i] for i in chosen) == val


def random_digraph(n, p, rng, lo, hi):
    nodes = list(range(n))
    edges = []
    for u in range(n):
        for v in range(n):
            if u != v and rng.random() < p:
                edges.append((u, v, rng.randint(lo, hi)))
    nxg = nx.DiGraph()
    nxg.add_nodes_from(nodes)
    nxg.add_weighted_edges_from(edges)
    return nodes, edges, nxg


def test_bellman_ford_and_floyd_warshall_vs_networkx():
    rng = random.Random(2)
    checked_neg = 0
    for _ in range(30):
        nodes, edges, nxg = random_digraph(9, 0.3, rng, -3, 10)
        dist, parent, neg = bellman_ford(nodes, edges, 0)
        fw = floyd_warshall(nodes, edges)
        fw_neg = any(fw[u][u] < 0 for u in nodes)  # negative cycle anywhere
        assert fw_neg == nx.negative_edge_cycle(nxg)
        if neg:  # Bellman-Ford only sees cycles reachable from the source
            checked_neg += 1
            assert fw_neg
            continue
        if fw_neg:
            continue
        ref = nx.single_source_bellman_ford_path_length(nxg, 0)
        for u in nodes:
            assert dist[u] == ref.get(u, math.inf)
            assert fw[0][u] == ref.get(u, math.inf)
        refall = dict(nx.all_pairs_bellman_ford_path_length(nxg))
        for u in nodes:
            for v in nodes:
                assert fw[u][v] == refall[u].get(v, math.inf)
    assert checked_neg > 0


def test_sequence_alignment_vs_brute_force_and_symmetry():
    rng = random.Random(3)
    for _ in range(30):
        x = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        y = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        gap, mis = rng.randint(1, 3), rng.randint(1, 3)
        cost, ax, ay = sequence_alignment(x, y, gap, mis)
        assert ax.replace("-", "") == x and ay.replace("-", "") == y and len(ax) == len(ay)
        recomputed = sum(gap if "-" in (a, b) else (0 if a == b else mis) for a, b in zip(ax, ay))
        assert recomputed == cost
        assert cost == sequence_alignment(y, x, gap, mis)[0]
        # brute force: enumerate all monotone matchings of positions
        best = min(brute_align(x, y, gap, mis))
        assert cost == best


def brute_align(x, y, gap, mis):
    m, n = len(x), len(y)
    for k in range(min(m, n) + 1):
        for ix in itertools.combinations(range(m), k):
            for iy in itertools.combinations(range(n), k):
                c = sum(0 if x[i] == y[j] else mis for i, j in zip(ix, iy))
                yield c + gap * (m - k + n - k)


def test_lcs_vs_brute_force():
    rng = random.Random(4)
    for _ in range(30):
        x = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        y = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        subs = {"".join(x[i] for i in c) for r in range(len(x) + 1) for c in itertools.combinations(range(len(x)), r)}
        best = max((len(s) for s in subs if is_subseq(s, y)), default=0)
        L, s = lcs(x, y)
        assert L == best == len(s) and is_subseq(s, x) and is_subseq(s, y)


def is_subseq(s, t):
    it = iter(t)
    return all(ch in it for ch in s)
