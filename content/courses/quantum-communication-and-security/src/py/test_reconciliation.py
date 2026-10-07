import numpy as np
import pytest

from reconciliation import (H74, binary, bsc, cascade, efficiency, hamming_reconcile,
                            verify_hash)


def test_binary_finds_the_single_error_with_log_parities():
    rng = np.random.default_rng(0)
    a = rng.integers(0, 2, 64, dtype=np.int8)
    for j in (0, 17, 63):
        b = a.copy(); b[j] ^= 1
        pos, leak = binary(a, b, np.arange(64))
        assert pos == j and leak == 6


@pytest.mark.parametrize("e", [0.01, 0.03, 0.06])
def test_cascade_corrects_and_leaks_slightly_above_shannon(e):
    rng = np.random.default_rng(1)
    n = 10_000
    effs = []
    for _ in range(3):
        a = rng.integers(0, 2, n, dtype=np.int8)
        b = bsc(a, e, rng)
        bc, leak = cascade(a, b, e, rng)
        assert np.array_equal(a, bc)
        effs.append(efficiency(leak, n, e))
    assert 1.0 < np.mean(effs) < 1.4


def test_hamming_corrects_every_single_error_pattern():
    for c in range(1, 8):                                  # every column is a distinct syndrome
        assert list(H74[:, c - 1]) == [(c >> r) & 1 for r in range(3)]
    a = np.zeros(7, dtype=np.int8)
    for j in range(7):
        b = a.copy(); b[j] = 1
        bc, leak = hamming_reconcile(a, b)
        assert np.array_equal(a, bc) and leak == 3


def test_hamming_fails_on_two_errors_in_a_block():
    a = np.zeros(7, dtype=np.int8)
    b = a.copy(); b[[0, 1]] = 1
    bc, _ = hamming_reconcile(a, b)
    assert not np.array_equal(a, bc)


def test_verification_hash_collision_rate():
    rng = np.random.default_rng(2)
    a = rng.integers(0, 2, 50, dtype=np.int8)
    b = a.copy(); b[3] ^= 1
    assert verify_hash(a, a, 8, rng)
    coll = np.mean([verify_hash(a, b, 3, rng) for _ in range(20_000)])
    assert coll == pytest.approx(1 / 8, abs=0.01)
