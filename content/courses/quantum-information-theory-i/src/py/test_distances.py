import numpy as np
import pytest

from distances import (bures_distance, check_fuchs_van_de_graaf, fidelity, root_fidelity,
                       trace_distance, trace_distance_by_projector, uhlmann_optimal_unitary,
                       uhlmann_overlap)
from states import dm, from_bloch, random_pure, random_state, random_unitary


def test_pure_state_fidelity_is_overlap_squared():
    rng = np.random.default_rng(0)
    a, b = random_pure(3, rng), random_pure(3, rng)
    assert fidelity(dm(a), dm(b)) == pytest.approx(abs(np.vdot(a, b)) ** 2)


def test_fidelity_symmetric_and_unitarily_invariant():
    rng = np.random.default_rng(1)
    r, s, U = random_state(3, rng), random_state(3, rng), random_unitary(3, rng)
    assert fidelity(r, s) == pytest.approx(fidelity(s, r))
    assert fidelity(U @ r @ U.conj().T, U @ s @ U.conj().T) == pytest.approx(fidelity(r, s))


def test_commuting_states_reduce_to_bhattacharyya():
    p, q = np.array([0.5, 0.3, 0.2]), np.array([0.1, 0.6, 0.3])
    assert root_fidelity(np.diag(p), np.diag(q)) == pytest.approx(np.sqrt(p * q).sum())
    assert trace_distance(np.diag(p), np.diag(q)) == pytest.approx(0.5 * np.abs(p - q).sum())


def test_uhlmann_maximum_attained_and_not_exceeded():
    rng = np.random.default_rng(2)
    r, s = random_state(3, rng), random_state(3, rng, rank=2)
    F = fidelity(r, s)
    assert uhlmann_overlap(r, s, uhlmann_optimal_unitary(r, s)) == pytest.approx(F)
    assert max(uhlmann_overlap(r, s, random_unitary(3, rng)) for _ in range(500)) <= F + 1e-12


def test_trace_distance_qubit_formula_and_projector():
    r, s = np.array([0.2, 0.1, -0.3]), np.array([0.0, -0.4, 0.5])
    R, S = from_bloch(r), from_bloch(s)
    assert trace_distance(R, S) == pytest.approx(np.linalg.norm(r - s) / 2)
    assert trace_distance_by_projector(R, S) == pytest.approx(trace_distance(R, S))


def test_bures_extremes():
    rho = random_state(2, np.random.default_rng(3))
    assert bures_distance(rho, rho) == pytest.approx(0, abs=1e-6)
    assert bures_distance(dm(np.array([1, 0])), dm(np.array([0, 1]))) == pytest.approx(np.sqrt(2))


def test_fuchs_van_de_graaf_and_pinsker():
    w = check_fuchs_van_de_graaf(np.random.default_rng(4), trials=200)
    assert w["lower"] > -1e-9 and w["upper"] > -1e-9 and w["pinsker"] > -1e-9
    assert w["pure_equality_gap"] < 1e-9


def test_qubit_fidelity_bloch_formula():
    rng = np.random.default_rng(5)
    for _ in range(20):
        r, s = [v * rng.uniform() / np.linalg.norm(v) for v in rng.normal(size=(2, 3))]
        expected = 0.5 * (1 + r @ s + np.sqrt((1 - r @ r) * (1 - s @ s)))
        assert fidelity(from_bloch(r), from_bloch(s)) == pytest.approx(expected)


def test_fidelity_and_trace_distance_monotone_under_partial_trace():
    rng = np.random.default_rng(6)
    from states import partial_trace
    for _ in range(20):
        r, s = random_state(6, rng), random_state(6, rng)
        ra, sa = partial_trace(r, [2, 3], [0]), partial_trace(s, [2, 3], [0])
        assert fidelity(ra, sa) >= fidelity(r, s) - 1e-10
        assert trace_distance(ra, sa) <= trace_distance(r, s) + 1e-10
