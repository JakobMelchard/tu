import numpy as np
import pytest

from entropies import (check_inequalities, check_ssa, conditional_entropy, mutual_information,
                       relative_entropy, shannon, von_neumann)
from states import BELL, dm, kron, partial_trace, random_pure, random_state


def test_shannon_and_von_neumann_basics():
    assert shannon([0.5, 0.5]) == pytest.approx(1)
    assert shannon([1, 0]) == 0
    assert von_neumann(np.eye(4) / 4) == pytest.approx(2)
    assert von_neumann(dm(random_pure(3, np.random.default_rng(0)))) == pytest.approx(0, abs=1e-9)


def test_pure_bipartite_marginals_have_equal_entropy():
    rng = np.random.default_rng(1)
    psi = random_pure(6, rng)
    r = dm(psi)
    assert von_neumann(partial_trace(r, [2, 3], [0])) == pytest.approx(
        von_neumann(partial_trace(r, [2, 3], [1])))


def test_bell_state_conditional_entropy_negative():
    phi = dm(BELL["phi+"])
    assert conditional_entropy(phi, [2, 2]) == pytest.approx(-1)
    assert mutual_information(phi, [2, 2]) == pytest.approx(2)


def test_relative_entropy_properties():
    rng = np.random.default_rng(2)
    r, s = random_state(3, rng), random_state(3, rng)
    assert relative_entropy(r, r) == pytest.approx(0, abs=1e-9)
    assert relative_entropy(r, s) > 0
    assert relative_entropy(np.eye(2) / 2, np.diag([1.0, 0.0])) == np.inf
    # D(rho || I/d) = log d - S(rho)
    assert relative_entropy(r, np.eye(3) / 3) == pytest.approx(np.log2(3) - von_neumann(r))


def test_entropy_additive_on_products():
    rng = np.random.default_rng(3)
    a, b = random_state(2, rng), random_state(3, rng)
    assert von_neumann(np.kron(a, b)) == pytest.approx(von_neumann(a) + von_neumann(b))
    assert mutual_information(np.kron(a, b), [2, 3]) == pytest.approx(0, abs=1e-9)


def test_inequalities_hold_on_random_states():
    w = check_inequalities(np.random.default_rng(4), trials=150)
    for k in ("klein", "subadditivity", "araki_lieb", "concavity"):
        assert w[k] > -1e-9, k
    assert w["mi_equals_relative_entropy"] < 1e-8


def test_araki_lieb_saturated_by_pure_states():
    psi = dm(random_pure(6, np.random.default_rng(5)))
    Sa = von_neumann(partial_trace(psi, [2, 3], [0]))
    Sb = von_neumann(partial_trace(psi, [2, 3], [1]))
    assert von_neumann(psi) == pytest.approx(abs(Sa - Sb), abs=1e-9)


def test_strong_subadditivity_numerically():
    assert check_ssa(np.random.default_rng(6), trials=80) > -1e-9


def test_ssa_saturated_by_markov_chain_product():
    rng = np.random.default_rng(7)
    rho = kron(random_state(2, rng), random_state(2, rng), random_state(2, rng))
    from entropies import conditional_mutual_information
    assert conditional_mutual_information(rho, [2, 2, 2]) == pytest.approx(0, abs=1e-9)
