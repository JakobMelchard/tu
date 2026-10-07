import numpy as np
import pytest

from bpp_amplify import (chernoff_bound, empirical_error, exact_majority_error,
                         majority_vote, repetitions_needed, rp_amplify, rp_error)


@pytest.mark.parametrize("p", [0.6, 2 / 3, 0.75])
def test_exact_tail_below_chernoff(p):
    for k in range(1, 200, 2):
        assert exact_majority_error(k, p) <= chernoff_bound(k, p) + 1e-12


def test_empirical_error_below_bound_with_slack():
    rng = np.random.default_rng(1)
    p = 2 / 3
    for k in (3, 11, 21, 41):
        emp = empirical_error(p, k, 20000, rng)
        # exact tail +- 4 sigma of the binomial estimate must contain emp
        ex = exact_majority_error(k, p)
        assert emp <= ex + 4 * np.sqrt(ex * (1 - ex) / 20000) + 1e-3
        assert emp <= chernoff_bound(k, p) + 1e-2


def test_monotone_in_k_and_p():
    for p in (0.55, 2 / 3, 0.9):
        errs = [exact_majority_error(k, p) for k in range(1, 100, 2)]
        assert all(a >= b for a, b in zip(errs, errs[1:]))
    for k in (5, 21):
        errs = [exact_majority_error(k, p) for p in np.linspace(0.51, 0.99, 20)]
        assert all(a >= b for a, b in zip(errs, errs[1:]))


def test_repetitions_needed_meets_target():
    for s in (5, 10, 30):
        k = repetitions_needed(2 / 3, 2 ** -s)
        assert k % 2 == 1
        assert chernoff_bound(k, 2 / 3) <= 2 ** -s
        assert exact_majority_error(k, 2 / 3) <= 2 ** -s
        assert chernoff_bound(k - 2, 2 / 3) > 2 ** -s  # minimal


def test_majority_vote_and_rp_simulation():
    rng = np.random.default_rng(3)
    base = lambda r: r.random() < 2 / 3
    wrong = sum(not majority_vote(base, 31, rng) for _ in range(2000)) / 2000
    assert wrong <= chernoff_bound(31, 2 / 3) + 0.01
    yes_base = lambda r: r.random() < 0.5  # RP on a yes-instance
    misses = sum(not rp_amplify(yes_base, 10, rng) for _ in range(2000)) / 2000
    assert misses <= rp_error(10, 0.5) + 0.01
    no_base = lambda r: False  # never accepts a no-instance
    assert not rp_amplify(no_base, 10, rng)
