import math

import numpy as np

from framework import ThresholdProblem
from srm import (dyadic_class, srm_experiment, srm_penalties, srm_threshold_select,
                 srm_weight, uc_epsilon)


def test_weights_sum_to_one_basel():
    # sum_{k>=1} 6/(pi^2 k^2) = 1; the tail beyond K is between 6/(pi^2 (K+1)) and 6/(pi^2 K).
    K = 2000
    partial = sum(srm_weight(k) for k in range(1, K + 1))
    tail = 1 - partial
    assert 6 / (math.pi**2 * (K + 1)) < tail < 6 / (math.pi**2 * K)


def test_classes_are_nested_and_penalty_increases():
    for k in range(1, 8):
        assert set(dyadic_class(k)) <= set(dyadic_class(k + 1))
        assert len(dyadic_class(k)) == 2**k + 1
    pen = srm_penalties(100, 10, 0.05)
    assert np.all(np.diff(pen) > 0)
    assert pen[0] == uc_epsilon(3, 100, 0.05 * 6 / math.pi**2)


def test_theorems_6_1_and_6_2_hold_over_resamples():
    rng = np.random.default_rng(0)
    delta = 0.1
    for n in (50, 500):
        r = srm_experiment(ThresholdProblem(0.3, 0.1), n, 10, delta, 150, rng)
        assert r["viol_61"] <= delta and r["viol_62"] <= delta


def test_srm_picks_finer_classes_as_n_grows_and_approaches_bayes():
    rng = np.random.default_rng(1)
    prob = ThresholdProblem(0.3, 0.1)
    small = srm_experiment(prob, 30, 10, 0.05, 100, rng)
    large = srm_experiment(prob, 5000, 10, 0.05, 30, rng)
    assert large["k_mean"] > small["k_mean"] + 2
    assert large["LD_srm"] - prob.bayes_risk < 0.01


def test_srm_on_noiseless_dyadic_target_selects_exact_class():
    # theta = 3/8 lies in H_3; with n large SRM returns it exactly.
    rng = np.random.default_rng(2)
    X, y = ThresholdProblem(0.375, 0.0).sample(4000, rng)
    k, t = srm_threshold_select(X, y, 10, 0.05)
    assert k == 3 and t == 0.375
