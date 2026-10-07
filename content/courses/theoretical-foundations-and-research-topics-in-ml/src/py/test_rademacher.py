import math

import numpy as np

from framework import ThresholdProblem
from rademacher import (empirical_rademacher_exact, empirical_rademacher_finite,
                        massart_bound, rademacher_bound_experiment,
                        rademacher_linear_bound, rademacher_linear_exact,
                        rademacher_threshold, rademacher_vc_bound,
                        threshold_predictions)


def test_two_point_threshold_exact_value():
    # n=2 sorted points: thresholds realise (-,-), (-,+), (+,+). Enumerate sigma:
    # (+,+)->2, (-,-)->2, (-,+)->2, (+,-)->0, so R_S = (1/2)*(6/4) = 3/4.
    rng = np.random.default_rng(0)
    X = np.array([0.2, 0.8])
    r = rademacher_threshold(X, 20000, rng)
    assert abs(r - 0.75) < 0.02


def test_threshold_rademacher_decays_like_one_over_sqrt_n():
    rng = np.random.default_rng(1)
    r10 = rademacher_threshold(rng.uniform(size=10), 3000, rng)
    r1000 = rademacher_threshold(rng.uniform(size=1000), 500, rng)
    assert r1000 < r10 / 5
    assert r1000 <= rademacher_vc_bound(1, 1000)


def test_massart_bound_holds():
    rng = np.random.default_rng(2)
    F = rng.choice([-1.0, 1.0], size=(30, 50))
    r = empirical_rademacher_finite(F, 4000, rng)
    assert r <= massart_bound(30, 50) + 0.01


def test_linear_exact_below_bound_and_dimension_free():
    rng = np.random.default_rng(3)
    for d in (3, 300):
        X = rng.normal(size=(200, d))
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        r = rademacher_linear_exact(X, 2.0, 2000, rng)
        b = rademacher_linear_bound(X, 2.0)
        assert r <= b + 1e-9
        assert abs(b - 2.0 / math.sqrt(200)) < 1e-12
        assert r > 0.5 * b  # Jensen gap is small: bound is nearly tight


def test_finite_class_single_function_has_zero_complexity():
    rng = np.random.default_rng(4)
    F = np.ones((1, 40))
    assert abs(empirical_rademacher_finite(F, 4000, rng)) < 0.05


def test_exact_enumeration_gives_three_quarters_and_matches_prefix_sum_method():
    assert empirical_rademacher_exact(threshold_predictions(np.array([0.2, 0.8]))) == 0.75
    rng = np.random.default_rng(5)
    X = rng.uniform(size=12)
    exact = empirical_rademacher_exact(threshold_predictions(X))
    assert abs(rademacher_threshold(X, 200_000, rng) - exact) < 3e-3
    assert abs(empirical_rademacher_finite(threshold_predictions(X), 50_000, rng) - exact) < 5e-3


def test_linear_class_on_orthonormal_points_attains_the_bound():
    # ||sum sigma_i e_i|| = sqrt(n) for every sigma, so R_S = B/sqrt(n) = BR/sqrt(n) exactly.
    rng = np.random.default_rng(6)
    n, B = 16, 3.0
    X = np.eye(n)
    assert abs(rademacher_linear_exact(X, B, 50, rng) - B / math.sqrt(n)) < 1e-12
    assert abs(rademacher_linear_bound(X, B) - B / math.sqrt(n)) < 1e-12


def test_rademacher_generalisation_bound_theorem_5_3():
    rng = np.random.default_rng(7)
    delta = 0.1
    for n in (40, 200):
        gaps, slacks = rademacher_bound_experiment(ThresholdProblem(0.3, 0.1), n, delta, 300, 200, rng)
        assert np.mean(gaps > slacks) <= delta
