import numpy as np
import pytest

from protocols import (bb84, teleport_with_resource, dense_coding, e91_exact, e91_sampled, entanglement_swapping,
                       intercept_resend_z, teleport)
from states import BELL, dm, random_pure


def test_teleportation_all_outcomes_exact():
    rng = np.random.default_rng(0)
    for _ in range(10):
        psi = random_pure(2, rng)
        for p, bob in teleport(psi).values():
            assert p == pytest.approx(0.25)
            assert np.allclose(bob, np.outer(psi, psi.conj()))


def test_teleportation_bob_before_correction_is_maximally_mixed():
    psi = random_pure(2, np.random.default_rng(1))
    avg = sum(p * bob for p, bob in teleport(psi).values())  # average of corrected states = psi
    assert np.allclose(avg, np.outer(psi, psi.conj()))


def test_entanglement_swapping():
    for p, overlap in entanglement_swapping().values():
        assert p == pytest.approx(0.25) and overlap == pytest.approx(1)


def test_dense_coding_decodes_two_bits():
    for m, row in dense_coding().items():
        assert row[m] == pytest.approx(1)
        assert sum(row.values()) == pytest.approx(1)


def test_bb84_statistics():
    rng = np.random.default_rng(2)
    sift, q = bb84(20000, rng)
    assert abs(sift - 0.5) < 0.02 and q == 0
    sift, q = bb84(20000, rng, eve=True)
    assert abs(q - 0.25) < 0.02


def test_e91_exact_and_sampled():
    s = dm(BELL["psi-"])
    S, key = e91_exact(s)
    assert S == pytest.approx(-2 * np.sqrt(2)) and np.allclose(key, -1)
    assert abs(e91_exact(intercept_resend_z(s))[0]) <= 2
    S_hat, err, n = e91_sampled(s, 4000, np.random.default_rng(3))
    assert abs(S_hat + 2 * np.sqrt(2)) < 0.25 and err == 0 and n > 500


@pytest.mark.parametrize("p", [0.0, 1 / 3, 0.5, 1.0])
def test_teleportation_with_noisy_resource(p):
    rng = np.random.default_rng(4)
    res = p * dm(BELL["phi+"]) + (1 - p) * np.eye(4) / 4
    for _ in range(5):
        assert teleport_with_resource(random_pure(2, rng), res) == pytest.approx((1 + p) / 2)
