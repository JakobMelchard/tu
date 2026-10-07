import random

from sat import (assignment_to_independent_set, brute_force_sat, dpll, evaluate,
                 independent_set_exists, num_vars, sat_to_3sat, subset_sum_exists,
                 three_sat_to_vertex_cover, vertex_cover_exists,
                 vertex_cover_to_subset_sum)


def random_cnf(rng, n, m, kmax):
    return [[rng.choice((1, -1)) * v for v in rng.sample(range(1, n + 1), rng.randint(1, kmax))]
            for _ in range(m)]


def test_dpll_agrees_with_brute_force():
    rng = random.Random(7)
    for _ in range(60):
        F = random_cnf(rng, n=5, m=rng.randint(1, 8), kmax=4)
        a = dpll(F)
        assert (a is not None) == (brute_force_sat(F) is not None)
        if a is not None:
            full = {v: a.get(v, False) for v in range(1, num_vars(F) + 1)}
            assert evaluate(F, full)


def test_3sat_is_equisatisfiable_and_has_3_literals():
    rng = random.Random(3)
    for _ in range(40):
        F = random_cnf(rng, n=4, m=rng.randint(1, 4), kmax=4)
        G = sat_to_3sat(F)
        assert all(len(c) == 3 for c in G)
        assert (brute_force_sat(F) is None) == (brute_force_sat(G) is None)


def test_reduction_chain_preserves_answer():
    """satisfiable(F) == 3SAT == IS == VC == SUBSET SUM on ~30 tiny instances."""
    rng = random.Random(11)
    for _ in range(30):
        F = random_cnf(rng, n=3, m=rng.randint(1, 3), kmax=3)
        G = sat_to_3sat(F)
        V, E, k_is, k_vc = three_sat_to_vertex_cover(G)
        sat = brute_force_sat(F) is not None
        assert (independent_set_exists(V, E, k_is) is not None) == sat
        assert (vertex_cover_exists(V, E, k_vc) is not None) == sat
        nums, W = vertex_cover_to_subset_sum(V, E, k_vc)
        assert (subset_sum_exists(nums, W) is not None) == sat


def test_satisfying_assignment_maps_to_cover():
    rng = random.Random(5)
    found = 0
    while found < 10:
        F = sat_to_3sat(random_cnf(rng, n=3, m=3, kmax=3))
        a = brute_force_sat(F)
        if a is None:
            continue
        found += 1
        V, E, k_is, k_vc = three_sat_to_vertex_cover(F)
        S = set(assignment_to_independent_set(F, a))
        assert len(S) == k_is and not any(u in S and v in S for u, v in E)
        C = set(V) - S  # complement of an independent set is a vertex cover
        assert len(C) == k_vc and all(u in C or v in C for u, v in E)
        nums, W = vertex_cover_to_subset_sum(V, E, k_vc)
        # the cover plus one b_i for every edge covered once sums to the target
        cover_sum = sum(nums[V.index(v)] for v in C)
        for i, (u, v) in enumerate(E):
            if (u in C) + (v in C) == 1:
                cover_sum += 4 ** i
        assert cover_sum == W


def test_worked_example_from_note():
    F = [[1, 2, 3], [-1, -2, 3], [-3, 1, 2]]
    V, E, k_is, k_vc = three_sat_to_vertex_cover(F)
    assert len(V) == 9 and k_is == 3 and k_vc == 6
    assert vertex_cover_exists(V, E, k_vc) is not None
    assert vertex_cover_exists(V, E, k_vc - 1) is None  # 3 disjoint triangles need 6
