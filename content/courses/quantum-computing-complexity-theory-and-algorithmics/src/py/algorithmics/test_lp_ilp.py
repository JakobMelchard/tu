import random

import numpy as np
import pytest
from scipy.optimize import linprog

from approx import is_vertex_cover
from flow import FlowNetwork, edmonds_karp
from lp_ilp import (ILP_BACKEND, branch_and_bound, integrality_gap, max_flow_lp,
                    min_cut_dual_lp, simplex, solve_ilp, vertex_cover_ilp,
                    vertex_cover_lp, vertex_cover_lp_rounding)


def random_graph(n, p, rng):
    nodes = list(range(n))
    edges = [(u, v) for u in nodes for v in nodes if u < v and rng.random() < p]
    return nodes, edges


def test_lp_relaxation_below_ilp_and_rounding_is_2approx():
    rng = random.Random(0)
    for _ in range(6):
        nodes, edges = random_graph(9, 0.4, rng)
        lp, x = vertex_cover_lp(nodes, edges)
        ilp, cover = vertex_cover_ilp(nodes, edges)
        assert is_vertex_cover(edges, cover) and len(cover) == ilp
        assert lp <= ilp + 1e-9
        assert all(x[u] + x[v] >= 1 - 1e-9 for u, v in edges)
        rounded, lp2 = vertex_cover_lp_rounding(nodes, edges)
        assert is_vertex_cover(edges, rounded)
        assert len(rounded) <= 2 * lp2 + 1e-9 and len(rounded) <= 2 * ilp


def test_integrality_gap_complete_graph_and_odd_cycle():
    for n in (3, 5, 7):
        nodes = list(range(n))
        Kn = [(i, j) for i in nodes for j in nodes if i < j]
        lp, ilp, ratio = integrality_gap(nodes, Kn)
        assert abs(lp - n / 2) < 1e-6 and ilp == n - 1
        assert abs(ratio - 2 * (n - 1) / n) < 1e-6  # -> 2 as n grows
        Cn = [(i, (i + 1) % n) for i in nodes]
        lp, ilp, _ = integrality_gap(nodes, Cn)
        assert abs(lp - n / 2) < 1e-6 and ilp == (n + 1) // 2


def test_max_flow_lp_equals_dual_and_combinatorial_flow():
    rng = random.Random(1)
    for _ in range(8):
        n = 7
        nodes = list(range(n))
        edges = [(u, v, rng.randint(1, 9)) for u in nodes for v in nodes if u != v and rng.random() < 0.3]
        g = FlowNetwork()
        for u in nodes:
            g.add_node(u)
        for u, v, c in edges:
            g.add_edge(u, v, c)
        ref = edmonds_karp(g, 0, n - 1)
        fv, f = max_flow_lp(nodes, edges, 0, n - 1)
        cv, A = min_cut_dual_lp(nodes, edges, 0, n - 1)
        assert abs(fv - ref) < 1e-6 and abs(cv - ref) < 1e-6  # strong duality
        assert 0 in A and n - 1 not in A
        assert all(-1e-9 <= f[k] <= edges[k][2] + 1e-9 for k in f)


SMALL_LPS = [  # (c, A, b) for max c.x, A x <= b, x >= 0
    ([5, 4], [[6, 4], [1, 2], [-1, 1]], [24, 6, 1]),
    ([3, 2, 4], [[1, 1, 2], [2, 0, 3], [2, 1, 3]], [4, 5, 7]),
    ([1, 1], [[1, 0], [0, 1], [1, 1]], [2, 3, 4]),
]


@pytest.mark.parametrize("c,A,b", SMALL_LPS)
def test_simplex_matches_linprog(c, A, b):
    val, x = simplex(c, A, b)
    ref = linprog(-np.array(c), A_ub=A, b_ub=b, bounds=[(0, None)] * len(c), method="highs")
    assert abs(val + ref.fun) < 1e-9
    assert np.all(np.asarray(A) @ x <= np.asarray(b) + 1e-9) and np.all(x >= -1e-9)
    assert abs(np.dot(c, x) - val) < 1e-9


def test_simplex_detects_unbounded():
    with pytest.raises(ValueError):
        simplex([1, 1], [[1, -1]], [1])


def test_branch_and_bound_matches_milp_and_pulp():
    rng = random.Random(2)
    for _ in range(8):  # random small knapsack-with-side-constraints ILPs
        n = rng.randint(2, 5)
        c = [-rng.randint(1, 10) for _ in range(n)]
        A = [[rng.randint(0, 6) for _ in range(n)] for _ in range(2)]
        b = [rng.randint(5, 15) for _ in range(2)]
        bounds = [(0, 3)] * n
        val, x = branch_and_bound(c, A, b, bounds, [1] * n)
        ref, _ = solve_ilp(c, A, b, bounds, [1] * n)
        assert abs(val - ref) < 1e-6
        assert np.allclose(x, np.round(x)) and np.all(np.asarray(A) @ x <= np.asarray(b) + 1e-9)
    # vertex cover on K5 via B&B vs ILP backend
    nodes = list(range(5))
    Kn = [(i, j) for i in nodes for j in nodes if i < j]
    Amat = np.zeros((len(Kn), 5))
    for k, (u, v) in enumerate(Kn):
        Amat[k, u] = Amat[k, v] = -1
    val, _ = branch_and_bound(np.ones(5), Amat, -np.ones(len(Kn)), [(0, 1)] * 5, [1] * 5)
    assert round(val) == 4 == vertex_cover_ilp(nodes, Kn)[0]
    assert ILP_BACKEND in ("pulp", "milp")
