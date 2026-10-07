import numpy as np
import pytest

from channels import (amplitude_damping, apply_kraus, born, choi, dephasing, depolarising, is_cptp_choi,
                      is_povm, is_trace_preserving, kraus_from_choi, neumark_direct_sum,
                      neumark_isometry, stinespring, stinespring_apply, transpose_map, trine)
from states import bloch_vector, dm, from_bloch, partial_trace, random_state, random_unitary

CHANNELS = [depolarising(0.3), dephasing(0.2), amplitude_damping(0.4)]


@pytest.mark.parametrize("K", CHANNELS)
def test_kraus_channels_are_cptp(K):
    assert is_trace_preserving(K)
    assert is_cptp_choi(choi(lambda A: apply_kraus(K, A), 2), 2, 2) == (True, True)


def test_bloch_actions():
    r = np.array([0.3, -0.2, 0.5])
    rho = from_bloch(r)
    assert np.allclose(bloch_vector(apply_kraus(depolarising(0.3), rho)), 0.7 * r)
    assert np.allclose(bloch_vector(apply_kraus(dephasing(0.2), rho)), [0.6 * 0.3, 0.6 * -0.2, 0.5])
    g = 0.4
    assert np.allclose(bloch_vector(apply_kraus(amplitude_damping(g), rho)),
                       [np.sqrt(1 - g) * 0.3, np.sqrt(1 - g) * -0.2, g + (1 - g) * 0.5])


def test_transpose_is_positive_not_completely_positive():
    rho = random_state(2, np.random.default_rng(0))
    assert np.linalg.eigvalsh(transpose_map(rho)).min() > -1e-12
    J = choi(transpose_map, 2)
    assert np.allclose(J, np.eye(4)[[0, 2, 1, 3]])  # SWAP
    assert is_cptp_choi(J, 2, 2) == (False, True)


def test_kraus_from_choi_and_unitary_freedom():
    rng = np.random.default_rng(1)
    K = depolarising(0.5)
    rho = random_state(2, rng)
    K2 = kraus_from_choi(choi(lambda A: apply_kraus(K, A), 2), 2, 2)
    assert np.allclose(apply_kraus(K2, rho), apply_kraus(K, rho))
    U = random_unitary(4, rng)
    K3 = [sum(U[i, j] * K[j] for j in range(4)) for i in range(4)]
    assert np.allclose(apply_kraus(K3, rho), apply_kraus(K, rho))


@pytest.mark.parametrize("K", CHANNELS)
def test_stinespring(K):
    rho = random_state(2, np.random.default_rng(2))
    V = stinespring(K)
    assert np.allclose(V.conj().T @ V, np.eye(2))
    assert np.allclose(stinespring_apply(V, rho, 2, len(K)), apply_kraus(K, rho))
    comp = stinespring_apply(V, rho, 2, len(K), keep=1)
    assert np.trace(comp).real == pytest.approx(1) and np.linalg.eigvalsh(comp).min() > -1e-12


def test_amplitude_damping_complement_is_amplitude_damping():
    g = 0.3
    rho = random_state(2, np.random.default_rng(3))
    comp = stinespring_apply(stinespring(amplitude_damping(g)), rho, 2, 2, keep=1)
    assert np.allclose(comp, apply_kraus(amplitude_damping(1 - g), rho))


def test_trine_povm_and_neumark_dilations():
    rng = np.random.default_rng(4)
    E, kets = trine()
    assert is_povm(E) and not is_povm(E[:2])
    rho = random_state(2, rng)
    V = neumark_isometry(E)
    anc = np.real(np.diag(partial_trace(V @ rho @ V.conj().T, [2, 3], [1])))
    assert np.allclose(anc, born(E, rho))
    U = neumark_direct_sum([np.sqrt(2 / 3) * k for k in kets])
    assert np.allclose(U @ U.conj().T, np.eye(3))
    for k in kets:
        emb = np.concatenate([k, [0]])
        assert np.allclose(np.abs(U.conj().T @ emb) ** 2, born(E, dm(k)))
