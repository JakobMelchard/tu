"""Random numbers and Monte Carlo: known LCG values, KS tests, the N^(-1/2) law.

The 10000th minstd_rand0 value is required by ISO C++ [S14]; distributions are
checked with scipy.stats.kstest.
"""
import numpy as np
import scipy.stats as st

from montecarlo import (LCG, box_muller, error_scaling, exponential_inverse, mc_antithetic,
                        mc_control_variate, mc_integral, mc_pi)


def test_lcg_minstd_known_values():
    g = LCG(1)
    assert [g.next() for _ in range(3)] == [16807, 282475249, 1622650073]
    g = LCG(1)
    for _ in range(9999):
        g.next()
    assert g.next() == 1043618065  # C++ standard: 10000th minstd_rand0 output


def test_exponential_and_normal_against_scipy():
    rng = np.random.default_rng(1)
    e = exponential_inverse(rng.random(50_000), 2.0)
    assert st.kstest(e, st.expon(scale=0.5).cdf).pvalue > 0.01
    z0, z1 = box_muller(rng.random(50_000), rng.random(50_000))
    assert st.kstest(z0, st.norm.cdf).pvalue > 0.01
    assert abs(np.corrcoef(z0, z1)[0, 1]) < 0.02


def test_mc_pi_within_error_bar():
    rng = np.random.default_rng(3)
    n = 200_000
    assert abs(mc_pi(rng, n) - np.pi) < 4 * 4 * np.sqrt(np.pi / 4 * (1 - np.pi / 4) / n)


def test_error_scaling_slope():
    _, slope = error_scaling(mc_pi, np.pi, [100, 1000, 10_000, 100_000], reps=20)
    assert -0.7 < slope < -0.3


def test_variance_reduction():
    exact = np.e - 1
    n = 20_000
    plain = error_scaling(lambda r, n: mc_integral(np.exp, r, n)[0], exact, [n], 20)[0][0]
    anti = error_scaling(lambda r, n: mc_antithetic(np.exp, r, n), exact, [n], 20)[0][0]
    ctrl = error_scaling(lambda r, n: mc_control_variate(np.exp, lambda x: 1 + x, 1.5, r, n), exact, [n], 20)[0][0]
    assert anti < plain and ctrl < plain
