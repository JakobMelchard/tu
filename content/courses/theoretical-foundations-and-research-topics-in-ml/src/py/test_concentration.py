import math

import numpy as np

from concentration import (binomial_tail_exact, epsilon_from_n, hoeffding_bound,
                           hoeffding_empirical, sample_complexity_finite,
                           uniform_deviation_finite, union_bound_experiment)
from framework import ThresholdProblem


def test_hoeffding_bound_holds_empirically():
    rng = np.random.default_rng(0)
    for n in (20, 100, 400):
        for p in (0.2, 0.5):
            obs = hoeffding_empirical(p, n, 0.1, 50_000, rng)
            assert obs <= hoeffding_bound(n, 0.1) + 0.01


def test_simulation_matches_exact_binomial_tail():
    # Note 02 worked example: n=100, eps=0.1, exact 2 P(Bin(100,1/2) <= 40) = 0.0569,
    # Hoeffding 2e^{-2} = 0.271. The boundary k=40, 60 must count (>= eps, not > eps).
    from scipy.stats import binom
    exact = binomial_tail_exact(0.5, 100, 0.1)
    assert abs(exact - 2 * binom.cdf(40, 100, 0.5)) < 1e-15
    assert abs(exact - 0.0569) < 5e-4 and abs(hoeffding_bound(100, 0.1) - 2 * math.exp(-2)) < 1e-15
    rng = np.random.default_rng(1)
    obs = hoeffding_empirical(0.5, 100, 0.1, 200_000, rng)
    assert abs(obs - exact) < 4 * math.sqrt(exact * (1 - exact) / 200_000)


def test_union_bound_holds_and_is_loose():
    rng = np.random.default_rng(2)
    obs, ub, single = union_bound_experiment(50, 100, 0.1, 5000, rng)
    assert obs <= ub + 0.02
    assert obs >= single  # more hypotheses -> more chance of some bad one


def test_sample_complexity_formulas():
    assert sample_complexity_finite(1000, 0.05, 0.05, realisable=True) == math.ceil(math.log(20000) / 0.05)
    assert sample_complexity_finite(1000, 0.05, 0.05) == math.ceil(math.log(40000) / (2 * 0.0025))
    n = sample_complexity_finite(1000, 0.05, 0.05)
    assert epsilon_from_n(n, 1000, 0.05) <= 0.05 + 1e-9
    assert sample_complexity_finite(1000, 0.05, 0.05, True) < sample_complexity_finite(1000, 0.05, 0.05)


def test_realisable_guarantee_empirically():
    # Consistent learner over finite thresholds on noiseless data: P(L_D > eps) <= |H| e^{-eps n}.
    rng = np.random.default_rng(3)
    hyps = (np.arange(50) + 0.5) / 50
    theta, eps, n = 0.51, 0.1, sample_complexity_finite(50, 0.1, 0.05, True)  # theta in H
    fails = 0
    for _ in range(300):
        X = rng.uniform(size=n)
        y = np.where(X > theta, 1, -1)
        consistent = [h for h in hyps if np.all(np.where(X > h, 1, -1) == y)]
        h = consistent[0]
        fails += abs(h - theta) > eps
    assert fails / 300 <= 0.05


def test_finite_class_uniform_convergence_theorem_2_6():
    # P(sup_{h in H} |L_S(h) - L_D(h)| > sqrt(log(2|H|/delta)/(2n))) <= delta, exact L_D.
    rng = np.random.default_rng(4)
    delta, k = 0.1, 20
    for n in (30, 300):
        gaps = uniform_deviation_finite(ThresholdProblem(0.3, 0.1), k, n, 800, rng)
        assert np.mean(gaps > epsilon_from_n(n, k, delta)) <= delta
        assert np.quantile(gaps, 1 - delta) <= epsilon_from_n(n, k, delta)
