import time
from fractions import Fraction

import pytest
import numpy as np

from order_finding import (continued_fraction, convergents, denominator_from_phase,
                           modmul_permutation, order_classical, order_finding,
                           order_finding_distribution, order_finding_success_probability)


def test_continued_fractions_and_convergents():
    assert continued_fraction(85, 256) == [0, 3, 85]           # 85/256 ~ 1/3
    assert convergents([0, 3, 85]) == [(0, 1), (1, 3), (85, 256)]
    assert continued_fraction(415, 93) == [4, 2, 6, 7]
    assert convergents([4, 2, 6, 7]) == [(4, 1), (9, 2), (58, 13), (415, 93)]
    rng = np.random.default_rng(0)
    for _ in range(50):
        p, q = int(rng.integers(0, 500)), int(rng.integers(1, 500))
        cf = convergents(continued_fraction(p, q))
        assert Fraction(*cf[-1]) == Fraction(p, q)
        assert all(Fraction(h, k) == Fraction(*c) for (h, k), c in zip(cf, cf))
    assert denominator_from_phase(85, 256, 15) == 3
    assert denominator_from_phase(192, 256, 15) == 4
    assert denominator_from_phase(0, 256, 15) == 1


def test_worked_examples_in_the_notes():
    """Every continued fraction printed in notes/C06 and notes/C07, recomputed.

    These four are the ones a hand calculation gets wrong: the expansion is easy,
    the *convergents* recursion p_k = a_k p_{k-1} + p_{k-2} is where a digit slips.
    """
    # C06 worked example: m = 1365, t = 11, s/r = 2/3
    assert continued_fraction(1365, 2048) == [0, 1, 1, 1, 682]
    assert convergents([0, 1, 1, 1, 682]) == [(0, 1), (1, 1), (1, 2), (2, 3), (1365, 2048)]
    assert abs(1365 / 2048 - 2 / 3) == pytest.approx(1.6276e-4, rel=1e-3)
    # C06 exam question 5: m = 427, t = 9, N = 21
    assert continued_fraction(427, 512) == [0, 1, 5, 42, 2]
    assert (5, 6) in convergents(continued_fraction(427, 512))
    assert denominator_from_phase(427, 512, 21) == 6
    # C07 worked example 2, N = 21, a = 2: the three representative outcomes
    assert continued_fraction(171, 1024) == [0, 5, 1, 84, 2]
    assert convergents([0, 5, 1, 84, 2]) == [(0, 1), (1, 5), (1, 6), (85, 509), (171, 1024)]
    assert abs(171 / 1024 - 1 / 6) == pytest.approx(3.2552e-4, rel=1e-3)
    assert continued_fraction(683, 1024) == [0, 1, 2, 341]
    assert (2, 3) in convergents(continued_fraction(683, 1024))
    # C07 worked example 1, N = 15: 192/256 = 3/4
    assert continued_fraction(192, 256) == [0, 1, 3]


def test_modmul_permutation_is_bijection():
    perm = modmul_permutation(7, 15, 4)
    assert sorted(perm.tolist()) == list(range(16)) and perm[1] == 7 and perm[15] == 15


def test_classical_orders():
    assert order_classical(7, 15) == 4 and order_classical(2, 15) == 4 and order_classical(11, 15) == 2
    assert order_classical(2, 21) == 6


def test_distribution_peaks_at_multiples_of_2t_over_r():
    for a, r in ((7, 4), (2, 4), (11, 2)):
        P, t = order_finding_distribution(a, 15)
        step = 2 ** t // r
        assert np.isclose(P.sum(), 1)
        for x in range(2 ** t):
            assert np.isclose(P[x], 1 / r if x % step == 0 else 0.0)


def test_success_rate_at_least_half():
    rng = np.random.default_rng(1)
    for a in (7, 2, 11):
        assert order_finding_success_probability(a, 15) >= 0.5 - 1e-12
        assert order_finding_success_probability(a, 15, check_multiples=True) > 0.99
        r_true = order_classical(a, 15)
        results = [order_finding(a, 15, rng)[0] for _ in range(30)]
        assert all(r in (None, r_true) for r in results)
        assert results.count(r_true) / 30 >= 0.4          # exact rate is 0.5; sampled with a seed


def test_n_21_runs_fast():
    t0 = time.time()
    p = order_finding_success_probability(2, 21)
    assert p > 0.3                                        # r=6 is not a power of two: 3/6 fractions with gcd 1
    assert time.time() - t0 < 5
