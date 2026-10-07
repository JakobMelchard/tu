import numpy as np

from qaoa import (barren_plateau_variances, cut_values, expected_cut, maxcut_bruteforce,
                  most_likely_cut, qaoa, qaoa_state, random_graph, ring_graph)
from sim import Register, kron, Z, I


def test_cut_values_and_bruteforce():
    n, edges = 4, [(0, 1), (1, 2), (2, 3)]
    c = cut_values(n, edges)
    assert c[0b0101] == 3 and c[0b0000] == 0 and c[0b1000] == 1
    assert maxcut_bruteforce(5, ring_graph(5))[0] == 4


def test_cost_unitary_is_zz_phase_and_expectation_from_paulis():
    n, edges = 3, [(0, 2), (1, 2)]
    reg = qaoa_state([0.7], [0.3], n, edges)
    # <C> = sum_edges (1 - <Z_i Z_j>)/2
    ref = sum((1 - reg.expectation("".join("Z" if q in (i, j) else "I" for q in range(n)))) / 2 for i, j in edges)
    assert np.isclose(expected_cut(reg, n, edges), ref)
    # cost unitary equals exp(-i gamma C) with C the diagonal cut operator (global phase aside)
    C = np.diag(cut_values(n, edges).astype(complex))
    psi = np.ones(8) / np.sqrt(8)
    from qaoa import apply_cost_unitary
    got = apply_cost_unitary(Register(n, psi), 0.7, edges).state
    exp = np.diag(np.exp(-0.7j * np.diag(C))) @ psi
    assert np.allclose(got, exp)


def test_p2_reaches_85_percent_of_maxcut_on_ring_and_random_graph():
    rng = np.random.default_rng(0)
    n, edges = 5, ring_graph(5)
    cmax = maxcut_bruteforce(n, edges)[0]
    val1 = qaoa(n, edges, 1, rng, restarts=3)[0]
    val, g, b = qaoa(n, edges, 2, rng, restarts=4)
    assert val >= 0.85 * cmax and val >= val1 - 1e-6
    reg = qaoa_state(g, b, n, edges)
    assert cut_values(n, edges)[most_likely_cut(reg)] == cmax
    n6, e6 = 6, random_graph(6, 0.6, np.random.default_rng(5))
    val = qaoa(n6, e6, 2, rng, restarts=4)[0]
    assert val >= 0.85 * maxcut_bruteforce(n6, e6)[0]


def test_barren_plateau_variance_decreases():
    rng = np.random.default_rng(1)
    var = barren_plateau_variances(range(2, 9), 30, rng)
    assert list(var) == list(range(2, 9))
    assert all(v > 0 for v in var.values())
    assert var[8] < 0.25 * var[2] and var[8] < var[4]      # exponential decay, noisy in between
