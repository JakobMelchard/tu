from itertools import product
import math

import numpy as np
import pytest

from query_complexity import (AND, OR, PARITY, acceptance_polynomial_degree,
                              decision_tree_depth, deutsch_jozsa, deutsch_pair_parity,
                              grover_iterations, grover_or, multilinear_coefficients,
                              parity_via_pairs, random_query_algorithm)


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_decision_tree_depth_of_or_parity_and(n):
    assert decision_tree_depth(OR, n) == n
    assert decision_tree_depth(PARITY, n) == n
    assert decision_tree_depth(AND, n) == n


def test_decision_tree_depth_nontrivial():
    # f = x0 or (x1 and x2): query x0 first, then at most two more -> 3; but
    # g = x0 ? x1 : x2 (index function) has depth 2 < 3.
    g = lambda x: x[1] if x[0] else x[2]
    assert decision_tree_depth(g, 3) == 2
    assert decision_tree_depth(lambda x: 0, 3) == 0


@pytest.mark.parametrize("n", [2, 3, 4])
def test_parity_via_pairs_is_correct_with_half_the_queries(n):
    for x in product((0, 1), repeat=n):
        val, q = parity_via_pairs(x)
        assert val == sum(x) % 2
        assert q == math.ceil(n / 2)
        for i in range(n):
            for j in range(i + 1, n):
                assert deutsch_pair_parity(x, i, j) == x[i] ^ x[j]


def test_deutsch_jozsa_one_query():
    for m in (1, 2, 3):
        N = 2 ** m
        assert deutsch_jozsa((0,) * N) == "constant"
        assert deutsch_jozsa((1,) * N) == "constant"
        rng = np.random.default_rng(m)
        for _ in range(5):
            tt = [1] * (N // 2) + [0] * (N // 2)
            rng.shuffle(tt)
            assert deutsch_jozsa(tuple(tt)) == "balanced"


def test_grover_iteration_count_and_success():
    for N in (4, 16, 64, 256):
        x = [0] * N
        x[N // 2] = 1
        r, p = grover_or(x)
        assert r == grover_iterations(N)
        assert abs(r - math.pi / 4 * math.sqrt(N)) <= 1.0
        assert p >= 0.9
        assert p == pytest.approx(math.sin((2 * r + 1) * math.asin(1 / math.sqrt(N))) ** 2)
    assert grover_or([0] * 8) == (0, 0.0)


def test_polynomial_method_degree_bound():
    # exact 1-query Deutsch algorithm: acceptance = x0 + x1 - 2 x0 x1, degree 2
    P = lambda x: deutsch_pair_parity(x, 0, 1)
    c = multilinear_coefficients([P(((m >> 0) & 1, (m >> 1) & 1)) for m in range(4)])
    assert np.allclose(c, [0, 1, 1, -2])
    assert acceptance_polynomial_degree(P, 2) == 2
    # generic t-query algorithms on n=5 bits: degree <= 2t (Beals et al.)
    rng = np.random.default_rng(42)
    for t in (1, 2):
        for _ in range(3):
            alg = random_query_algorithm(5, t, rng)
            assert acceptance_polynomial_degree(alg, 5) <= 2 * t
    # a 3-query algorithm can and generically does reach full degree 5
    assert acceptance_polynomial_degree(random_query_algorithm(5, 3, rng), 5) == 5
    # multilinear fit is exact: reconstruct values from coefficients
    alg = random_query_algorithm(4, 2, rng)
    vals = [alg(tuple((m >> i) & 1 for i in range(4))) for m in range(16)]
    c = multilinear_coefficients(vals)
    for m in range(16):
        rec = sum(c[s] for s in range(16) if s & ~m == 0)
        assert rec == pytest.approx(vals[m])
