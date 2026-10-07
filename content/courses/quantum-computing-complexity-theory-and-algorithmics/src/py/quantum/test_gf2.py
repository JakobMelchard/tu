import itertools

import numpy as np

from gf2 import gf2_nullspace, gf2_rank, gf2_rref, gf2_solve


def brute_nullspace(A):
    A = np.array(A)
    return {tuple(x) for x in itertools.product((0, 1), repeat=A.shape[1]) if not ((A @ x) % 2).any()}


def span(rows, n):
    out = set()
    for coeffs in itertools.product((0, 1), repeat=len(rows)):
        v = np.zeros(n, dtype=int)
        for c, r in zip(coeffs, rows):
            if c:
                v ^= r
        out.add(tuple(v))
    return out


def test_rank_and_rref_small_cases():
    assert gf2_rank([[1, 0], [0, 1]]) == 2
    assert gf2_rank([[1, 1], [1, 1]]) == 1
    assert gf2_rank([[1, 1, 0], [0, 1, 1], [1, 0, 1]]) == 2   # rows sum to 0 mod 2
    assert gf2_rank(np.zeros((3, 4), dtype=int)) == 0
    R, piv = gf2_rref([[0, 1, 1], [1, 1, 0]])
    assert piv == [0, 1] and R.tolist() == [[1, 0, 1], [0, 1, 1]]


def test_nullspace_matches_brute_force_on_random_matrices():
    rng = np.random.default_rng(0)
    for _ in range(40):
        m, n = int(rng.integers(1, 6)), int(rng.integers(1, 7))
        A = rng.integers(0, 2, (m, n))
        N = gf2_nullspace(A)
        assert N.shape[0] == n - gf2_rank(A)
        assert not ((A @ N.T) % 2).any()
        assert span(list(N), n) == brute_nullspace(A)


def test_solve():
    rng = np.random.default_rng(1)
    for _ in range(40):
        m, n = int(rng.integers(1, 6)), int(rng.integers(1, 6))
        A = rng.integers(0, 2, (m, n))
        x_true = rng.integers(0, 2, n)
        b = (A @ x_true) % 2
        x = gf2_solve(A, b)
        assert x is not None and (((A @ x) % 2) == b).all()
    assert gf2_solve([[1, 1], [1, 1]], [1, 0]) is None
