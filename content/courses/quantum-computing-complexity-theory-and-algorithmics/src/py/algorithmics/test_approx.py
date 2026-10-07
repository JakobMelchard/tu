import random

from approx import (approximation_ratio, harmonic, is_vertex_cover,
                    knapsack_fptas, load_balancing_exact, load_balancing_greedy,
                    load_balancing_lpt, set_cover_exact, set_cover_greedy,
                    vertex_cover_2approx, vertex_cover_exact)
from dp import knapsack_01


def test_vertex_cover_2approx_bound():
    rng = random.Random(0)
    worst = 1.0
    for _ in range(40):
        n = rng.randint(2, 11)
        nodes = list(range(n))
        edges = [(u, v) for u in nodes for v in nodes if u < v and rng.random() < 0.35]
        if not edges:
            continue
        cover, matching = vertex_cover_2approx(edges)
        assert is_vertex_cover(edges, cover)
        assert len(cover) == 2 * len(matching)
        assert len({x for e in matching for x in e}) == 2 * len(matching)  # disjoint
        opt = vertex_cover_exact(nodes, edges)
        assert is_vertex_cover(edges, opt)
        assert len(cover) <= 2 * len(opt)
        worst = max(worst, len(cover) / len(opt))
    assert 1.0 <= worst <= 2.0


def test_load_balancing_bounds():
    rng = random.Random(1)
    for _ in range(40):
        m = rng.randint(2, 3)
        jobs = [rng.randint(1, 15) for _ in range(rng.randint(m, 7))]
        opt = load_balancing_exact(jobs, m)
        mk, a = load_balancing_greedy(jobs, m)
        loads = [0] * m
        for j, i in enumerate(a):
            loads[i] += jobs[j]
        assert max(loads) == mk
        assert opt <= mk <= 2 * opt
        mk2, a2 = load_balancing_lpt(jobs, m)
        assert opt <= mk2 <= 1.5 * opt
        assert sorted(a2) == sorted(a2) and len(a2) == len(jobs)


def test_set_cover_greedy_within_harmonic_factor():
    rng = random.Random(2)
    for _ in range(40):
        U = set(range(rng.randint(3, 9)))
        k = rng.randint(2, 7)
        sets = [set(rng.sample(sorted(U), rng.randint(1, len(U)))) for _ in range(k)]
        sets.append(U - sets[0] if U - sets[0] else {0})  # ensure coverable
        w = [rng.randint(1, 5) for _ in sets]
        chosen = set_cover_greedy(U, sets, w)
        assert set().union(*(sets[i] for i in chosen)) >= U
        _, opt = set_cover_exact(U, sets, w)
        d = max(len(S) for S in sets)
        assert sum(w[i] for i in chosen) <= harmonic(d) * opt + 1e-9


def test_knapsack_fptas_within_eps():
    rng = random.Random(3)
    for eps in (0.5, 0.2, 0.05):
        for _ in range(15):
            n = rng.randint(2, 8)
            w = [rng.randint(1, 15) for _ in range(n)]
            v = [rng.randint(1, 500) for _ in range(n)]
            W = rng.randint(5, 30)
            opt, _ = knapsack_01(w, v, W)
            val, chosen = knapsack_fptas(w, v, W, eps)
            assert sum(w[i] for i in chosen) <= W
            assert sum(v[i] for i in chosen) == val <= opt
            assert val >= (1 - eps) * opt


def test_approximation_ratio_helper():
    rng = random.Random(4)
    insts = []
    for _ in range(10):
        n = rng.randint(2, 8)
        nodes = list(range(n))
        edges = [(u, v) for u in nodes for v in nodes if u < v and rng.random() < 0.5]
        if edges:
            insts.append((nodes, edges))
    r = approximation_ratio(lambda nodes, e: len(vertex_cover_2approx(e)[0]),
                            lambda nodes, e: len(vertex_cover_exact(nodes, e)), insts)
    assert 1.0 <= r <= 2.0
