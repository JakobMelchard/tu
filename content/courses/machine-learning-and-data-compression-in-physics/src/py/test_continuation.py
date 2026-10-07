import numpy as np
import pytest

from continuation import (LearnedLinearInverse, WarmMaxent, chi2, condition, discrepancy_alpha,
                          grids, kernel_matrix, l1_error, maxent, noise_band, peak_positions,
                          random_spectra, synthetic_data, tikhonov, two_peak)

BETA = 10.0


@pytest.fixture(scope="module")
def setup():
    tau, w, dw = grids(BETA)
    Kd = kernel_matrix(tau, w, dw, BETA)
    m = np.full_like(w, 1.0 / (2 * w[-1]))
    return tau, w, dw, Kd, m, two_peak(w)


def test_problem_is_ill_posed(setup):
    *_, Kd, m, A = setup
    assert condition(Kd) > 1e15
    # sum rule: G(0) + G(beta) = -int A
    G = Kd @ A
    assert G[0] + G[-1] == pytest.approx(-1.0, abs=1e-6)


def test_tikhonov_matches_normal_equations(setup):
    tau, w, dw, Kd, m, A = setup
    G = synthetic_data(A, Kd, 1e-3, np.random.default_rng(0))
    alpha, sigma = 3.0, 1e-3
    Ks = Kd / sigma
    direct = m + np.linalg.solve(Ks.T @ Ks + alpha * np.eye(len(w)), Ks.T @ ((G - Kd @ m) / sigma))
    assert np.allclose(tikhonov(Kd, G, sigma, alpha, m), direct, atol=1e-8)


def test_maxent_stationarity_and_positivity(setup):
    tau, w, dw, Kd, m, A = setup
    sigma, alpha = 1e-4, 50.0
    G = synthetic_data(A, Kd, sigma, np.random.default_rng(1))
    Am, c = maxent(Kd, G, sigma, alpha, m, dw)
    assert np.all(Am > 0)
    grad = (Kd / sigma).T @ ((Kd @ Am - G) / sigma) + alpha * dw * np.log(Am / m)
    assert np.max(np.abs(grad)) < 1e-6 * np.max(np.abs((Kd / sigma).T @ (G / sigma)))


@pytest.mark.parametrize("sigma", [1e-3, 1e-4, 1e-5])
def test_discrepancy_principle_hits_chi2_equal_n(setup, sigma):
    tau, w, dw, Kd, m, A = setup
    G = synthetic_data(A, Kd, sigma, np.random.default_rng(2))
    for solve in (lambda a: tikhonov(Kd, G, sigma, a, m), WarmMaxent(Kd, G, sigma, m, dw)):
        _, Ar = discrepancy_alpha(solve, Kd, G, sigma)
        assert 0.98 <= chi2(Ar, Kd, G, sigma) / len(G) <= 1.2


def test_maxent_recovers_two_peaks_and_improves_with_less_noise(setup):
    tau, w, dw, Kd, m, A = setup
    errs = []
    for k, sigma in enumerate((1e-3, 1e-5)):
        G = synthetic_data(A, Kd, sigma, np.random.default_rng(10 + k))
        _, Am = discrepancy_alpha(WarmMaxent(Kd, G, sigma, m, dw), Kd, G, sigma)
        errs.append(l1_error(Am, A, dw))
        assert Am.sum() * dw == pytest.approx(1.0, abs=0.01)
    assert errs[1] < errs[0] and errs[1] < 0.15
    p = peak_positions(Am, w)
    assert abs(p[0] + 1.5) < 0.2 and abs(p[1] - 2.5) < 0.2


def test_tikhonov_violates_positivity_maxent_does_not(setup):
    tau, w, dw, Kd, m, A = setup
    sigma = 1e-4
    G = synthetic_data(A, Kd, sigma, np.random.default_rng(3))
    _, At = discrepancy_alpha(lambda a: tikhonov(Kd, G, sigma, a, m), Kd, G, sigma)
    _, Am = discrepancy_alpha(WarmMaxent(Kd, G, sigma, m, dw), Kd, G, sigma)
    assert At.min() < 0 < Am.min()
    assert l1_error(Am, A, dw) < l1_error(At, A, dw)


def test_learned_linear_inverse_beats_flat_tikhonov_in_distribution(setup):
    tau, w, dw, Kd, m, _ = setup
    sigma = 1e-4
    train = random_spectra(w, 1500, np.random.default_rng(4))
    test = random_spectra(w, 60, np.random.default_rng(5))
    inv = LearnedLinearInverse(Kd, sigma, train)
    Gt = test @ Kd.T + sigma * np.random.default_rng(6).standard_normal((len(test), len(tau)))
    e_learn = np.mean([l1_error(a, t, dw) for a, t in zip(inv(Gt), test)])
    e_tik = np.mean([l1_error(tikhonov(Kd, g, sigma, 150.0, m), t, dw) for g, t in zip(Gt, test)])
    assert e_learn < e_tik
    # batch and single-vector calls agree
    assert np.allclose(inv(Gt)[0], inv(Gt[0]))


def test_noise_band_shrinks_with_alpha_while_bias_grows(setup):
    tau, w, dw, Kd, m, A = setup
    sigma, rng = 1e-4, np.random.default_rng(7)
    lo = noise_band(lambda g: tikhonov(Kd, g, sigma, 1.0, m), A, Kd, sigma, 20, rng)
    hi = noise_band(lambda g: tikhonov(Kd, g, sigma, 150.0, m), A, Kd, sigma, 20, rng)
    assert hi[1].max() < lo[1].max()
    assert np.abs(hi[0] - A).max() > np.abs(lo[0] - A).max()
