import numpy as np

from framework import (ThresholdProblem, empirical_risk, erm_finite,
                       finite_threshold_class, generalisation_gap_experiment,
                       memoriser_experiment, memoriser_risk,
                       threshold_empirical_risks, threshold_predict, zero_one_loss)


def test_closed_form_risk_matches_monte_carlo():
    rng = np.random.default_rng(1)
    prob = ThresholdProblem(theta=0.3, eta=0.1)
    for t in (0.1, 0.3, 0.7):
        assert abs(prob.risk(t) - prob.risk_mc(t, rng, n=400_000)) < 5e-3


def test_bayes_predictor_is_optimal_in_class():
    prob = ThresholdProblem(theta=0.3, eta=0.1)
    ts = np.linspace(0, 1, 101)
    assert min(prob.risk(t) for t in ts) == prob.bayes_risk


def test_empirical_risk_of_fixed_h_is_unbiased():
    rng = np.random.default_rng(2)
    prob = ThresholdProblem(theta=0.3, eta=0.1)
    ls = [empirical_risk(threshold_predict(0.5, X), y)
          for X, y in (prob.sample(50, rng) for _ in range(2000))]
    assert abs(np.mean(ls) - prob.risk(0.5)) < 5e-3


def test_erm_picks_min_empirical_risk():
    rng = np.random.default_rng(3)
    X, y = ThresholdProblem().sample(200, rng)
    hyps = finite_threshold_class(20)
    h, ls = erm_finite(hyps, X, y)
    risks = [empirical_risk(threshold_predict(t, X), y) for t in hyps]
    assert ls == min(risks) and prob_close(h, hyps[int(np.argmin(risks))])


def prob_close(a, b):
    return abs(a - b) < 1e-12


def test_training_error_is_optimistic_and_gap_shrinks():
    rng = np.random.default_rng(4)
    prob = ThresholdProblem()
    tr10, te10, best = generalisation_gap_experiment(prob, 50, 10, 300, rng)
    tr1000, te1000, _ = generalisation_gap_experiment(prob, 50, 1000, 100, rng)
    assert tr10 <= best <= te10          # E L_S(h_S) <= min_H L_D <= E L_D(h_S)
    assert te1000 - tr1000 < te10 - tr10  # gap shrinks with n


def test_zero_one_loss():
    assert zero_one_loss(np.array([1, -1, 1]), np.array([1, 1, -1])).tolist() == [0, 1, 1]


def test_vectorised_threshold_risks_match_brute_force():
    rng = np.random.default_rng(5)
    X, y = ThresholdProblem(0.4, 0.2).sample(137, rng)
    ts = np.concatenate([[-0.5, 0.0, 1.0, 1.5], X[:10], rng.uniform(size=50)])
    brute = [empirical_risk(threshold_predict(t, X), y) for t in ts]
    assert np.allclose(threshold_empirical_risks(X, y, ts), brute)


def test_memoriser_matches_closed_form():
    # Theorem 1.4: L_S = 0 and L_D = P(y = +1) = (1-theta)(1-eta) + theta*eta.
    rng = np.random.default_rng(6)
    prob = ThresholdProblem(theta=0.3, eta=0.1)
    ls, ld = memoriser_experiment(prob, 200, 200_000, rng)
    assert ls == 0.0
    assert abs(ld - memoriser_risk(prob)[1]) < 5e-3
    assert memoriser_risk(prob)[1] == 0.7 * 0.9 + 0.3 * 0.1
