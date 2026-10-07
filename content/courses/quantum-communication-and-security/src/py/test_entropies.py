import math

import numpy as np
import pytest

from entropies import (PHI_P, bb84_lams, bell_diagonal, bell_diagonal_qbers, cond_min_entropy_classical,
                       conditional_entropy, h2, h_z_given_e, helstrom_guess, holevo_chi,
                       max_entropy_classical, min_entropy_classical, min_entropy_cq_binary,
                       min_entropy_pure, mutual_information, partial_trace, random_pure, shannon,
                       smooth_min_entropy_classical, uncertainty_sum, von_neumann)


def test_binary_entropy_closed_forms():
    assert h2(0.5) == pytest.approx(1.0)
    assert h2(0.0) == 0.0 and h2(1.0) == 0.0
    assert h2(0.11) == pytest.approx(0.4999, abs=1e-4)
    assert shannon([0.5, 0.25, 0.25]) == pytest.approx(1.5)


def test_von_neumann_of_bell_state_and_marginal():
    rho = np.outer(PHI_P, PHI_P)
    assert von_neumann(rho) == pytest.approx(0.0, abs=1e-12)
    assert von_neumann(partial_trace(rho, [2, 2], [0])) == pytest.approx(1.0)
    # H(A|B) = -1 for a maximally entangled qubit pair; I(A:B) = 2
    assert conditional_entropy(rho, [2, 2], [0], [1]) == pytest.approx(-1.0)
    assert mutual_information(rho, [2, 2], [0], [1]) == pytest.approx(2.0)


def test_partial_trace_matches_einsum():
    rng = np.random.default_rng(0)
    psi = random_pure(2 * 3 * 2, rng)
    rho = np.outer(psi, psi.conj())
    t = rho.reshape(2, 3, 2, 2, 3, 2)
    ref = np.einsum("abcdbf->acdf", t).reshape(4, 4)
    assert np.allclose(partial_trace(rho, [2, 3, 2], [0, 2]), ref)


def test_holevo_of_bb84_z_states_is_one_and_of_identical_states_zero():
    k0, k1 = np.diag([1.0, 0.0]), np.diag([0.0, 1.0])
    assert holevo_chi([0.5, 0.5], [k0, k1]) == pytest.approx(1.0)
    assert holevo_chi([0.5, 0.5], [k0, k0]) == pytest.approx(0.0, abs=1e-12)


def test_min_max_entropy_ordering_and_uniform_equality():
    rng = np.random.default_rng(1)
    for _ in range(50):
        p = rng.dirichlet(np.ones(6))
        assert min_entropy_classical(p) <= shannon(p) + 1e-12 <= max_entropy_classical(p) + 2e-12
    u = np.full(16, 1 / 16)
    assert min_entropy_classical(u) == pytest.approx(4) == max_entropy_classical(u)


def test_conditional_min_entropy_classical_and_chain_rule():
    # X uniform on 2 bits, Y = first bit: H_min(X|Y) = 1
    pxy = np.zeros((4, 2))
    for x in range(4):
        pxy[x, x >> 1] = 0.25
    assert cond_min_entropy_classical(pxy) == pytest.approx(1.0)
    # chain rule H_min(X|YC) >= H_min(X|Y) - log|C| on random distributions
    rng = np.random.default_rng(2)
    for _ in range(100):
        p = rng.dirichlet(np.ones(4 * 3 * 2)).reshape(4, 3, 2)     # x, y, c
        h_y = cond_min_entropy_classical(p.sum(axis=2))
        h_yc = cond_min_entropy_classical(p.reshape(4, 6))
        assert h_yc >= h_y - 1.0 - 1e-12


def test_smooth_min_entropy_water_level():
    q = np.array([0.5] + [0.5 / 7] * 7)
    assert smooth_min_entropy_classical(q, 0.0) == pytest.approx(1.0)
    assert smooth_min_entropy_classical(q, 0.1) == pytest.approx(-math.log2(0.4))
    # cutting 0.3: level lam with 0.5-lam + 7*(0.5/7 - lam)_+ = 0.3 -> lam = 0.2
    assert smooth_min_entropy_classical(q, 0.3) == pytest.approx(-math.log2(0.2))
    # monotone in eps and i.i.d. rate approaches Shannon entropy (AEP) from H_min
    p = np.array([0.8, 0.2])
    n = 14
    joint = np.array([p[0] ** (n - k) * p[1] ** k for k in range(n + 1) for _ in range(math.comb(n, k))])
    rates = [smooth_min_entropy_classical(joint, e) / n for e in (0.0, 0.01, 0.1)]
    assert rates[0] < rates[1] < rates[2] < h2(0.2) + 0.2
    assert rates[0] == pytest.approx(-math.log2(0.8))


def test_helstrom_and_cq_min_entropy():
    k0 = np.diag([1.0, 0.0])
    plus = np.full((2, 2), 0.5)
    # guessing a BB84 bit when Eve holds |0> vs |+>: (1 + 1/sqrt2)/2
    assert helstrom_guess(0.5, k0, 0.5, plus) == pytest.approx((1 + 1 / math.sqrt(2)) / 2)
    assert min_entropy_cq_binary(0.5, k0, 0.5, k0) == pytest.approx(1.0)       # no information


def test_min_entropy_pure_states():
    assert min_entropy_pure(PHI_P, 2, 2) == pytest.approx(-1.0)                   # -log d
    prod = np.kron([1, 0], [0, 1]).astype(float)
    assert min_entropy_pure(prod, 2, 2) == pytest.approx(0.0, abs=1e-12)
    rng = np.random.default_rng(3)
    psi = random_pure(9, rng)
    rho = np.outer(psi, psi.conj())
    # H_min(A|B) <= H(A|B) = -S(A)
    assert min_entropy_pure(psi, 3, 3) <= conditional_entropy(rho, [3, 3], [0], [1]) + 1e-9


def test_bell_diagonal_qbers_and_h_z_given_e_closed_form():
    for lams in ([0.9, 0.05, 0.03, 0.02], bb84_lams(0.05, 0.05)):
        rho = bell_diagonal(lams)
        assert np.trace(rho) == pytest.approx(1.0)
        ez, ex = bell_diagonal_qbers(lams)
        # closed form H(Z|E) = 1 - H(lambda) + h(lambda_1 + lambda_2)
        ref = 1 - shannon(lams) + h2(lams[0] + lams[1])
        assert h_z_given_e(lams) == pytest.approx(ref, abs=1e-9)
        assert ez == pytest.approx(lams[2] + lams[3])


def test_entropic_uncertainty_relation_with_quantum_memory():
    rng = np.random.default_rng(4)
    for _ in range(100):
        psi = random_pure(2 * 2 * 3, rng)
        assert uncertainty_sum(psi, 2, 3) >= 1.0 - 1e-9
    # tight for |0>_A (x) |junk>: H(X|B) = 1, H(Z|C) = 0
    psi = np.kron(np.kron([1, 0], [1, 0]), [1, 0]).astype(complex)
    assert uncertainty_sum(psi, 2, 2) == pytest.approx(1.0)
