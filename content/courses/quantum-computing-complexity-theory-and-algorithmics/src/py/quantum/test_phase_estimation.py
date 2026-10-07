import numpy as np
from scipy.stats import unitary_group

from phase_estimation import phase_estimation, phase_estimation_distribution
from sim import phase


def test_exact_for_dyadic_phases_one_qubit():
    rng = np.random.default_rng(0)
    for t in (3, 4):
        for k in range(2 ** t):
            U = phase(2 * np.pi * k / 2 ** t)
            est, x = phase_estimation(U, [0, 1], t, rng)
            assert x == k and np.isclose(est, k / 2 ** t)
            P = phase_estimation_distribution(U, [0, 1], t)
            assert np.isclose(P[k], 1.0)


def test_non_dyadic_phase_within_one_bin_with_prob_at_least_8_over_pi2():
    rng = np.random.default_rng(1)
    t = 4
    phi = 0.3    # 0.3 * 16 = 4.8 -> nearest bins 5 (best) and 4
    U = phase(2 * np.pi * phi)
    P = phase_estimation_distribution(U, [0, 1], t)
    assert P[5] >= 4 / np.pi ** 2 and P[4] + P[5] >= 8 / np.pi ** 2
    hits = sum(abs(phase_estimation(U, [0, 1], t, rng)[0] - phi) <= 1 / 2 ** t for _ in range(200))
    assert hits / 200 >= 0.4


def test_two_qubit_unitary_random_eigenvector():
    rng = np.random.default_rng(2)
    t = 5
    # random 2-qubit unitary with a prescribed eigenphase 11/32 on one eigenvector
    V = unitary_group.rvs(4, random_state=rng)
    phis = [11 / 32, 0.1, 0.77, 0.5]
    U = V @ np.diag(np.exp(2j * np.pi * np.array(phis))) @ V.conj().T
    est, x = phase_estimation(U, V[:, 0], t, rng)
    assert x == 11
    P = phase_estimation_distribution(U, V[:, 3], t)      # phi = 0.5 = 16/32, exact too
    assert np.isclose(P[16], 1.0)
    P = phase_estimation_distribution(U, V[:, 1], t)      # phi = 0.1 -> 3.2, nearest bin 3
    assert np.argmax(P) == 3 and P[3] >= 4 / np.pi ** 2
    # a superposition of eigenvectors gives a mixture of the two eigenphase peaks
    v = (V[:, 0] + V[:, 3]) / np.sqrt(2)
    P = phase_estimation_distribution(U, v, t)
    assert np.isclose(P[11], 0.5) and np.isclose(P[16], 0.5)


def test_worked_numbers_in_note_c06():
    """The phase-estimation probabilities printed in notes/C06, recomputed.

    |alpha_m|^2 = sin^2(pi 2^t delta) / (4^t sin^2(pi delta)),  delta = phi - m/2^t.
    The trap the note used to fall into: pairing the numerator of one m with the
    denominator of another.  Both m are listed here so the pairing is explicit.
    """
    def amp2(phi, t, m):
        delta = phi - m / 2 ** t
        if abs(delta) < 1e-15:
            return 1.0
        return np.sin(np.pi * 2 ** t * delta) ** 2 / (4 ** t * np.sin(np.pi * delta) ** 2)

    # phi = 2/3, t = 3: 2^t phi = 5.333, so m = 5 is nearest
    assert abs(amp2(2 / 3, 3, 5) - 0.68784) < 1e-4
    assert abs(amp2(2 / 3, 3, 6) - 0.17494) < 1e-4
    assert amp2(2 / 3, 3, 5) + amp2(2 / 3, 3, 6) >= 8 / np.pi ** 2

    # phi = 0.3, t = 4: 2^t phi = 4.8, so m = 5 is nearest (NOT m = 4)
    assert abs(amp2(0.3, 4, 5) - 0.87559) < 1e-4
    assert abs(amp2(0.3, 4, 4) - 0.05515) < 1e-4
    assert amp2(0.3, 4, 5) + amp2(0.3, 4, 4) >= 8 / np.pi ** 2

    # the 4/pi^2 floor, swept over phi
    worst = min(amp2(phi, 5, round(phi * 32)) for phi in np.linspace(0.01, 0.99, 400))
    assert worst >= 4 / np.pi ** 2
