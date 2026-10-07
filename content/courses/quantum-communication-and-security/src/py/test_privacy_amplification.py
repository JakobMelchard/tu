import math

import numpy as np
import pytest

from privacy_amplification import (collision_probability, distance_flat_source,
                                   distance_with_prefix_leak, key_length, lhl_bound, toeplitz)


def test_toeplitz_structure():
    seed = np.arange(6)                      # n=4, l=3 -> 6 seed entries
    t = toeplitz(seed, 4, 3)
    assert t.shape == (3, 4)
    for i in range(2):
        for j in range(3):
            assert t[i, j] == t[i + 1, j + 1]


@pytest.mark.parametrize("n,l", [(4, 2), (5, 2), (6, 3)])
def test_toeplitz_family_is_exactly_two_universal(n, l):
    assert collision_probability(n, l) == pytest.approx(2.0**-l)


@pytest.mark.parametrize("k,l", [(8, 2), (8, 5), (8, 8)])
def test_leftover_hash_lemma_bound_holds_exactly(k, l):
    rng = np.random.default_rng(k + l)
    d, b = distance_flat_source(11, k, l, rng, n_seeds=None if 11 + l - 1 <= 14 else 400)
    assert d <= b


def test_extracting_more_than_hmin_is_insecure():
    rng = np.random.default_rng(0)
    d, _ = distance_flat_source(10, 6, 9, rng, n_seeds=50)
    assert d >= 1 - 2.0 ** (6 - 9)


def test_side_information_reduces_extractable_key():
    rng = np.random.default_rng(1)
    d, b = distance_with_prefix_leak(10, 4, 3, rng, n_seeds=100)
    assert d <= b == pytest.approx(lhl_bound(6, 3))
    d_all, _ = distance_with_prefix_leak(8, 8, 1, rng, n_seeds=20)   # Eve knows everything
    assert d_all == pytest.approx(0.5)


def test_key_length_formula_inverts_the_bound():
    l = key_length(1000, 200, 30, 1e-6)
    assert l == math.floor(1000 - 200 - 30 - 2 * math.log2(1 / 2e-6))
    assert 0.5 * math.sqrt(2.0 ** (-(1000 - 200 - 30 - l))) <= 1e-6
    assert key_length(10, 5, 5, 1e-6) == 0
