import math

import numpy as np

from framework import ThresholdProblem
from pac import (consistent_threshold_learner, erm_threshold_learner,
                 estimate_failure_probability, max_negative_threshold_learner,
                 sample_complexity_finite, sample_complexity_vc,
                 threshold_failure_exact)


def test_sample_complexity_monotone():
    assert sample_complexity_finite(100, 0.1, 0.1) < sample_complexity_finite(1000, 0.1, 0.1)
    assert sample_complexity_vc(1, 0.1, 0.05) < sample_complexity_vc(5, 0.1, 0.05)
    assert sample_complexity_vc(3, 0.05, 0.05) < sample_complexity_vc(3, 0.05, 0.05, realisable=False)


def test_consistent_learner_is_consistent():
    rng = np.random.default_rng(0)
    X, y = ThresholdProblem(0.4, 0.0).sample(100, rng)
    t = consistent_threshold_learner(X, y)
    assert np.all(np.where(X > t, 1, -1) == y)


def test_erm_threshold_learner_matches_brute_force():
    rng = np.random.default_rng(1)
    X, y = ThresholdProblem(0.4, 0.2).sample(60, rng)
    t = erm_threshold_learner(X, y)
    err = np.mean(np.where(X > t, 1, -1) != y)
    cands = np.concatenate([[-1.0], np.sort(X) + 1e-9])
    brute = min(np.mean(np.where(X > c, 1, -1) != y) for c in cands)
    assert abs(err - brute) < 1e-12


def test_pac_guarantee_realisable():
    rng = np.random.default_rng(2)
    n = sample_complexity_vc(1, 0.1, 0.05)
    fr = estimate_failure_probability(ThresholdProblem(0.3, 0.0), consistent_threshold_learner,
                                      n, 0.1, 400, rng)
    assert fr <= 0.05


def test_pac_guarantee_agnostic():
    rng = np.random.default_rng(3)
    n = sample_complexity_vc(1, 0.1, 0.05, realisable=False)
    fa = estimate_failure_probability(ThresholdProblem(0.3, 0.1), erm_threshold_learner,
                                      n, 0.1, 300, rng)
    assert fa <= 0.05


def test_realisable_threshold_failure_matches_closed_form():
    # P(L_D(h_S) > eps) = (1-eps)^n exactly for the largest-negative learner; <= e^{-eps n}.
    rng = np.random.default_rng(4)
    eps, theta, trials = 0.05, 0.3, 20_000
    for n in (10, 40):
        exact = threshold_failure_exact(eps, n, theta)
        assert exact == (1 - eps) ** n <= math.exp(-eps * n)
        mc = estimate_failure_probability(ThresholdProblem(theta, 0.0), max_negative_threshold_learner,
                                          n, eps, trials, rng)
        assert abs(mc - exact) < 4 * math.sqrt(exact * (1 - exact) / trials)


def test_max_negative_learner_is_consistent():
    rng = np.random.default_rng(5)
    X, y = ThresholdProblem(0.6, 0.0).sample(50, rng)
    t = max_negative_threshold_learner(X, y)
    assert np.all(np.where(X > t, 1, -1) == y)


def test_finite_sample_complexity_closed_form():
    # Theorem 3.1 with |H| = 1000, eps = delta = 0.05: 199 realisable, 2120 agnostic (note 02).
    assert sample_complexity_finite(1000, 0.05, 0.05) == 199
    assert sample_complexity_finite(1000, 0.05, 0.05, realisable=False) == 2120
