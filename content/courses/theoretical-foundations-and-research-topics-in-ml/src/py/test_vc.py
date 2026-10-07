import math

import numpy as np

from framework import ThresholdProblem, threshold_empirical_risks
from vc import (growth_function, halfspace_labelings, interval_labelings,
                is_shattered, rectangle_labelings, sample_line, sample_plane,
                sample_plane_circle, sauer_bound, sauer_upper_estimate,
                threshold_labelings, threshold_sup_deviation, uc_bound_expectation,
                uc_bound_mcdiarmid, vc_bound_experiment, vc_bound_vapnik,
                vc_dimension_estimate, verify_sauer)


def test_threshold_vc_dim_is_1():
    rng = np.random.default_rng(0)
    assert is_shattered(threshold_labelings, np.array([0.3]))
    assert not is_shattered(threshold_labelings, np.array([0.3, 0.7]))
    assert vc_dimension_estimate(threshold_labelings, sample_line, 4, 20, rng) == 1


def test_interval_vc_dim_is_2_and_exact_growth():
    rng = np.random.default_rng(1)
    assert is_shattered(interval_labelings, np.array([0.2, 0.8]))
    assert not is_shattered(interval_labelings, np.array([0.2, 0.5, 0.8]))
    assert vc_dimension_estimate(interval_labelings, sample_line, 5, 20, rng) == 2
    for n in range(1, 8):  # tau(n) = C(n,2) + n + 1 exactly
        assert growth_function(interval_labelings, sample_line, n, 5, rng) == math.comb(n, 2) + n + 1
        assert math.comb(n, 2) + n + 1 == sauer_bound(2, n)


def test_rectangle_vc_dim_is_4():
    rng = np.random.default_rng(2)
    diamond = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]], float)
    assert is_shattered(rectangle_labelings, diamond)
    five = np.array([[0, 1], [1, 0], [0, -1], [-1, 0], [0.1, 0.1]], float)
    assert not is_shattered(rectangle_labelings, five)
    assert vc_dimension_estimate(rectangle_labelings, sample_plane, 6, 100, rng) == 4


def test_halfspace_vc_dim_is_3_in_plane():
    rng = np.random.default_rng(3)
    assert is_shattered(halfspace_labelings, np.array([[0, 0], [1, 0], [0, 1]], float))
    assert not is_shattered(halfspace_labelings, sample_plane_circle(4, rng))  # convex position: XOR fails
    assert vc_dimension_estimate(halfspace_labelings, sample_plane, 5, 15, rng) == 3


def test_homogeneous_halfspaces_vc_dim_is_d():
    pts = np.eye(2)
    assert is_shattered(lambda P: halfspace_labelings(P, homogeneous=True), pts)
    three = np.array([[1, 0], [0, 1], [-1, -1]], float)
    assert not is_shattered(lambda P: halfspace_labelings(P, homogeneous=True), three)


def test_sauer_lemma():
    rng = np.random.default_rng(4)
    assert verify_sauer(interval_labelings, sample_line, 2, 8, 10, rng)
    assert verify_sauer(halfspace_labelings, sample_plane, 3, 6, 5, rng)
    for d in (1, 2, 3):
        for n in range(d, 20):
            assert sauer_bound(d, n) <= sauer_upper_estimate(d, n)
    assert sauer_bound(3, 3) == 8 and sauer_bound(2, 5) == 16


def test_threshold_growth_function_is_n_plus_one():
    rng = np.random.default_rng(5)
    for n in range(1, 10):
        assert growth_function(threshold_labelings, sample_line, n, 3, rng) == n + 1 == sauer_bound(1, n)


def test_exact_sup_deviation_matches_dense_grid():
    # The endpoint argument must agree with brute force over a fine grid of thresholds
    # (grid value <= exact sup, and close to it once the grid contains the sample points).
    rng = np.random.default_rng(6)
    prob = ThresholdProblem(0.3, 0.1)
    for _ in range(5):
        X, y = prob.sample(40, rng)
        two, one = threshold_sup_deviation(prob, X, y)
        grid = np.concatenate([np.linspace(0, 1, 20001), X, X - 1e-12, [prob.theta]])
        D = prob.risk(grid) - threshold_empirical_risks(X, y, grid)
        assert np.max(np.abs(D)) <= two + 1e-12 and two - np.max(np.abs(D)) < 1e-9
        assert np.max(D) <= one + 1e-12 and one - np.max(D) < 1e-9


def test_vc_bounds_hold_over_resamples():
    # Theorem 4.10 in expectation and with McDiarmid; Theorem 4.12. Thresholds: d=1, tau(2n)=2n+1.
    rng = np.random.default_rng(7)
    delta = 0.05
    for n in (30, 300):
        gaps = vc_bound_experiment(ThresholdProblem(0.3, 0.1), n, 400, rng)
        assert gaps.mean() <= uc_bound_expectation(2 * n + 1, n)
        assert np.mean(gaps > uc_bound_mcdiarmid(2 * n + 1, n, delta)) <= delta
        assert np.mean(gaps > vc_bound_vapnik(1, n, delta)) <= delta
    # note 04 worked number: d=3, n=1e4, delta=0.05 gives 0.164
    assert abs(vc_bound_vapnik(3, 10**4, 0.05) - 0.164) < 1e-3
