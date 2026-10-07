"""Concentration, PAC sample complexity and VC theory, verified against the books.

Covers notes 02-04: Hoeffding, the two finite-class sample complexities,
No-Free-Lunch, Sauer-Shelah, the VC dimensions of the standard classes, and
the fundamental theorem of statistical learning with its generalisation bound.

Part of the textbook-verification suite (see ../README.md). Each test hard-codes
the expression as the source states it and compares it against an independently
computed quantity, so a *misremembered constant* in the notes -- a wrong sign, a
stray factor of two, a log that should be a log-log, an exponent inside a square
root instead of outside -- fails here rather than being read past.

Locators refer to ../../refs/SOURCES.md:

    S9  = Shalev-Shwartz & Ben-David, Understanding Machine Learning (2014)
    S10 = Mohri, Rostamizadeh & Talwalkar, Foundations of ML, 2nd ed. (2018)
"""
import math

import numpy as np
import pytest

import concentration
import rademacher
import vc


# --- Concentration: S9 Lemma 4.5, S9 Cor. 2.3 / Cor. 4.6 ---------------------

def test_hoeffding_dominates_exact_binomial_tail():
    """S9 Lemma 4.5: P(|mean - mu| > eps) <= 2 exp(-2 n eps^2).

    Checked against the exact binomial tail, and against the worked numbers of
    note 02: for a fair coin with n=100, eps=0.1 the bound is 2e^-2 = 0.271
    while the exact two-sided probability is about 0.057.
    """
    from scipy.stats import binom

    for n in (50, 100, 500, 1000):
        for eps in (0.05, 0.1, 0.2):
            k = math.floor(n * (0.5 - eps))
            exact = 2 * binom.cdf(k, n, 0.5)
            assert exact <= concentration.hoeffding_bound(n, eps) + 1e-12

    assert concentration.hoeffding_bound(100, 0.1) == pytest.approx(0.2707, abs=5e-4)
    assert 2 * binom.cdf(40, 100, 0.5) == pytest.approx(0.0569, abs=5e-4)
    # Chebyshev at n=100 is comparable; by n=1000 Hoeffding is astronomically better.
    assert concentration.chebyshev_bound(0.25 / 100, 0.1) == pytest.approx(0.25, abs=1e-9)
    assert concentration.hoeffding_bound(1000, 0.1) < 1e-8
    assert concentration.chebyshev_bound(0.25 / 1000, 0.1) == pytest.approx(0.025, abs=1e-9)


def test_finite_class_sample_complexities_match_the_two_theorems():
    """S9 Cor. 4.6 (agnostic) and S9 Cor. 2.3 (realisable), worked in note 02.

    S9 Cor. 4.6:  m >= log(2|H|/delta) / (2 eps^2)
    S9 Cor. 2.3:  m >= log(|H|/delta)  / eps
    """
    size_H, eps, delta = 1000, 0.05, 0.05
    agnostic = concentration.sample_complexity_finite(size_H, eps, delta, realisable=False)
    realisable = concentration.sample_complexity_finite(size_H, eps, delta, realisable=True)

    assert agnostic == math.ceil(math.log(2 * size_H / delta) / (2 * eps**2)) == 2120
    assert realisable == math.ceil(math.log(size_H / delta) / eps) == 199

    # The exponents, not just the values: eps -> eps/2 costs 4x agnostic, 2x realisable.
    a2 = concentration.sample_complexity_finite(size_H, eps / 2, delta, realisable=False)
    r2 = concentration.sample_complexity_finite(size_H, eps / 2, delta, realisable=True)
    assert a2 / agnostic == pytest.approx(4.0, rel=0.01)
    assert r2 / realisable == pytest.approx(2.0, rel=0.01)

    # Dependence on |H| is logarithmic: doubling |H| adds log2/(2 eps^2) samples.
    bigger = concentration.sample_complexity_finite(2 * size_H, eps, delta, realisable=False)
    assert bigger - agnostic == pytest.approx(math.log(2) / (2 * eps**2), abs=1.0)


# --- No-Free-Lunch: S9 Thm 5.1 ----------------------------------------------

def test_no_free_lunch_reverse_markov_constants():
    """S9 Thm 5.1 gives P(L_D(A(S)) >= 1/8) >= 1/7 from E[L_D(A(S))] >= 1/4.

    The step is reverse Markov: for Z in [0,1], P(Z >= a) >= (E Z - a) / (1 - a).
    Note 03 states exactly these constants; this pins them down.
    """
    def reverse_markov(mean, a):
        return (mean - a) / (1 - a)

    assert reverse_markov(0.25, 0.125) == pytest.approx(1 / 7)

    # And the inequality itself, on random [0,1] variables with mean >= 1/4.
    rng = np.random.default_rng(0)
    for _ in range(200):
        z = rng.random(5000)
        z = np.clip(z + 0.25 - z.mean(), 0.0, 1.0)
        a = 0.125
        assert (z >= a).mean() >= reverse_markov(z.mean(), a) - 1e-9


# --- Sauer-Shelah: S9 Lemma 6.10, S10 Thm 3.17, S10 Cor. 3.18 ---------------

def test_sauer_shelah_holds_and_is_tight_for_intervals():
    """S9 Lemma 6.10 / S10 Thm 3.17: tau_H(n) <= sum_{i<=d} C(n,i).

    For intervals (d=2) the bound is attained: tau(n) = C(n,2) + n + 1, which is
    the closed form note 04 tabulates for n = 1..6 as 2, 4, 7, 11, 16, 22.
    """
    rng = np.random.default_rng(0)
    expected = {1: 2, 2: 4, 3: 7, 4: 11, 5: 16, 6: 22}
    for n, tau in expected.items():
        assert math.comb(n, 2) + n + 1 == tau
        observed = vc.growth_function(vc.interval_labelings, vc.sample_line, n, 30, rng)
        assert observed == tau
        assert observed <= vc.sauer_bound(2, n)
        assert vc.sauer_bound(2, n) == tau          # tight for intervals

    # Thresholds (d=1): tau(n) = n+1, also tight.
    for n in range(1, 8):
        observed = vc.growth_function(vc.threshold_labelings, vc.sample_line, n, 30, rng)
        assert observed == n + 1 == vc.sauer_bound(1, n)

    # Rectangles (d=4) satisfy but do not attain the bound once n > d.
    for n in (5, 6):
        observed = vc.growth_function(vc.rectangle_labelings, vc.sample_plane, n, 60, rng)
        assert observed <= vc.sauer_bound(4, n)


def test_polynomial_form_of_sauer_valid_exactly_for_n_ge_d():
    """S10 Cor. 3.18: sum_{i<=d} C(n,i) <= (en/d)^d for all n >= d.

    Note 04 states the hypothesis as n >= d (S9 Lemma 6.10 says m > d+1, which is
    weaker). This checks n >= d really is enough, and that it fails below d --
    note 04's table flags (e*1/2)^2 = 1.85 < tau_int(1) = 2 for exactly this reason.
    """
    for d in range(1, 8):
        for n in range(d, 60):
            assert vc.sauer_bound(d, n) <= vc.sauer_upper_estimate(d, n) + 1e-9
        # At n = d the two sides are 2^d and e^d.
        assert vc.sauer_bound(d, d) == 2**d
        assert vc.sauer_upper_estimate(d, d) == pytest.approx(math.e**d)

    # Below n = d the polynomial form is simply false.
    assert vc.sauer_upper_estimate(2, 1) == pytest.approx(1.8473, abs=1e-4)
    assert vc.sauer_bound(2, 1) == 2 > vc.sauer_upper_estimate(2, 1)


def test_vc_dimensions_of_the_standard_classes():
    """S9 ch. 6.3 and 9.1.3: thresholds 1, intervals 2, rectangles 4, halfspaces k+1.

    A random search certifies lower bounds only, so this asserts the shattered
    sets are found and, separately, that no set of size d+1 in the search is
    shattered -- the direction note 04 warns is the hard one.
    """
    rng = np.random.default_rng(1)
    assert vc.vc_dimension_estimate(vc.threshold_labelings, vc.sample_line, 4, 80, rng) == 1
    assert vc.vc_dimension_estimate(vc.interval_labelings, vc.sample_line, 5, 80, rng) == 2
    assert vc.vc_dimension_estimate(vc.rectangle_labelings, vc.sample_plane, 6, 200, rng) == 4
    # Non-homogeneous halfspaces in R^2 have VCdim 3 = k+1.
    assert vc.vc_dimension_estimate(vc.halfspace_labelings, vc.sample_plane, 5, 200, rng) == 3


# --- The fundamental theorem: S9 Thm 6.8 ------------------------------------

def test_fundamental_theorem_realisable_upper_bound_carries_the_log_one_over_eps():
    """S9 Thm 6.8 is ASYMMETRIC in the realisable case:

        C1 (d + log(1/delta)) / eps  <=  m_H  <=  C2 (d log(1/eps) + log(1/delta)) / eps

    The log(1/eps) appears in the UPPER bound only. This is the single most
    commonly misquoted part of the theorem, so the test pins the shape down:
    the realisable upper bound must grow faster than 1/eps as eps -> 0, while
    the lower bound is exactly proportional to 1/eps.
    """
    import pac

    d, delta = 5, 0.05
    for eps in (0.1, 0.01, 0.001):
        upper = pac.sample_complexity_vc(d, eps, delta, realisable=True)
        lower = (d + math.log(1 / delta)) / eps
        assert upper > lower                       # the log(1/eps) really is extra

    # eps -> eps/10 multiplies the lower bound by exactly 10 but the upper by more.
    u1 = pac.sample_complexity_vc(d, 0.01, delta, realisable=True)
    u2 = pac.sample_complexity_vc(d, 0.001, delta, realisable=True)
    assert u2 / u1 > 10.0

    # The agnostic case is symmetric: both bounds are (d + log(1/delta)) / eps^2.
    a1 = pac.sample_complexity_vc(d, 0.01, delta, realisable=False)
    a2 = pac.sample_complexity_vc(d, 0.001, delta, realisable=False)
    assert a2 / a1 == pytest.approx(100.0, rel=0.01)


def test_vc_generalisation_bound_worked_numbers():
    """The two forms note 04 quotes, at d=3, n=1e4, delta=0.05.

    Vapnik-style:  sqrt((8 d log(2en/d) + 8 log(4/delta)) / n)  ~ 0.164
    S10 Cor. 3.19: sqrt(2 d log(en/d) / n) + sqrt(log(1/delta) / (2n)) ~ 0.085

    They differ by a factor ~2, which is exactly why note 04 insists you say
    which form you are quoting.
    """
    d, n, delta = 3, 10**4, 0.05

    vapnik = math.sqrt((8 * d * math.log(2 * math.e * n / d)
                        + 8 * math.log(4 / delta)) / n)
    assert 8 * d * math.log(2 * math.e * n / d) == pytest.approx(235.3, abs=0.2)
    assert 8 * math.log(4 / delta) == pytest.approx(35.06, abs=0.05)
    assert vapnik == pytest.approx(0.1644, abs=5e-4)

    foml = (math.sqrt(2 * d * math.log(math.e * n / d) / n)
            + math.sqrt(math.log(1 / delta) / (2 * n)))
    assert foml == pytest.approx(0.0862, abs=5e-4)
    assert rademacher.rademacher_vc_bound(d, n) == pytest.approx(0.0739, abs=5e-4)

    # Both scale as sqrt(d log n / n): 100x the data cuts the bound ~ 10x.
    big = math.sqrt((8 * d * math.log(2 * math.e * 10**6 / d)
                     + 8 * math.log(4 / delta)) / 10**6)
    assert big == pytest.approx(0.0195, abs=5e-4)
    assert vapnik / big == pytest.approx(8.4, rel=0.05)
