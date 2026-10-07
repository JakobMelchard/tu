import numpy as np
import pytest

from entanglement import (WERNER_WITNESS, concurrence, entropy_of_entanglement, horodecki_3x3,
                          is_ppt, log_negativity, negativity, partial_transpose, random_separable,
                          realignment, werner, witness_value)
from states import BELL, dm, random_pure, random_state


def test_partial_transpose_of_bell_is_swap_over_two():
    swap = np.eye(4)[[0, 2, 1, 3]]
    assert np.allclose(partial_transpose(dm(BELL["phi+"]), 2, 2), swap / 2)
    assert negativity(dm(BELL["phi+"]), 2, 2) == pytest.approx(0.5)
    assert log_negativity(dm(BELL["phi+"]), 2, 2) == pytest.approx(1)


@pytest.mark.parametrize("p,entangled", [(0.2, False), (1 / 3, False), (0.34, True), (0.9, True)])
def test_werner_threshold_one_third(p, entangled):
    r = werner(p)
    assert (not is_ppt(r, 2, 2)) == entangled
    assert (witness_value(WERNER_WITNESS, r) < -1e-12) == entangled
    assert witness_value(WERNER_WITNESS, r) == pytest.approx((1 - 3 * p) / 4)
    assert negativity(r, 2, 2) == pytest.approx(max(0, (3 * p - 1) / 4), abs=1e-9)


def test_witness_nonnegative_on_separable_states():
    rng = np.random.default_rng(0)
    assert min(witness_value(WERNER_WITNESS, random_separable(2, 2, rng)) for _ in range(300)) >= -1e-12


def test_ppt_equals_zero_concurrence_for_two_qubits():
    rng = np.random.default_rng(1)
    seen = set()
    for _ in range(300):
        r = random_state(4, rng, rank=int(rng.integers(1, 5)))
        sep = concurrence(r) < 1e-9
        assert is_ppt(r, 2, 2) == sep
        seen.add(sep)
    assert seen == {True, False}


def test_separable_2x3_states_are_ppt():
    rng = np.random.default_rng(2)
    assert all(is_ppt(random_separable(2, 3, rng), 2, 3) for _ in range(100))


def test_entropy_of_entanglement():
    assert entropy_of_entanglement(BELL["psi-"], 2, 2) == pytest.approx(1)
    t = 0.3
    psi = np.array([np.cos(t), 0, 0, np.sin(t)])
    p = np.cos(t) ** 2
    assert entropy_of_entanglement(psi, 2, 2) == pytest.approx(-p * np.log2(p) - (1 - p) * np.log2(1 - p))


def test_pure_state_concurrence():
    t = 0.3
    psi = np.array([np.cos(t), 0, 0, np.sin(t)])
    assert concurrence(dm(psi)) == pytest.approx(np.sin(2 * t))


@pytest.mark.parametrize("a", [0.1, 0.5, 0.9])
def test_horodecki_bound_entangled_state_is_ppt_but_realignment_detects(a):
    h = horodecki_3x3(a)
    assert np.trace(h) == pytest.approx(1) and np.linalg.eigvalsh(h).min() > -1e-12
    assert is_ppt(h, 3, 3)
    assert np.linalg.svd(realignment(h, 3, 3), compute_uv=False).sum() > 1 + 1e-4


def test_realignment_norm_at_most_one_for_separable():
    rng = np.random.default_rng(3)
    assert max(np.linalg.svd(realignment(random_separable(3, 3, rng), 3, 3), compute_uv=False).sum()
               for _ in range(50)) <= 1 + 1e-9
