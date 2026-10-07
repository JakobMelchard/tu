"""Tests for the educational toy code in lattice_toy.py: Gauss reduction finds a shortest vector,
LLL output is reduced and within the 2^((n-1)/2) bound, Babai is exact for
small errors under a good basis and fails under a bad one."""
import random
from fractions import Fraction

import lattice_toy as T


def _random_basis(rng, n, lo=-20, hi=20):
    while True:
        B = [[rng.randint(lo, hi) for _ in range(n)] for _ in range(n)]
        Bs, _ = T.gram_schmidt(B)
        if all(T.norm2(v) != 0 for v in Bs):
            return B


def test_gram_schmidt_orthogonal():
    B = [[3, 1, 0], [1, 2, 2], [0, 1, 5]]
    Bs, _ = T.gram_schmidt(B)
    for i in range(3):
        for j in range(i):
            assert T.dot(Bs[i], Bs[j]) == 0


def test_gauss_reduction_is_exact_svp_2d():
    rng = random.Random(0)
    for _ in range(100):
        B = _random_basis(rng, 2)
        b1, b2 = T.gauss_reduce(*B)
        assert abs(T.det2([b1, b2])) == abs(T.det2(B))          # same lattice
        assert T.norm2(b1) <= T.norm2(b2)
        assert 2 * abs(T.dot(b1, b2)) <= T.norm2(b1)
        assert T.norm2(b1) == T.norm2(T.svp_bruteforce([b1, b2], R=3))


def test_lll_reduced_and_approximation_bound():
    rng = random.Random(1)
    for _ in range(15):
        B = _random_basis(rng, 3, -9, 9)
        L = T.lll(B)
        assert T.is_lll_reduced(L)
        lam1 = T.norm2(T.svp_bruteforce(L, R=4))
        assert T.norm2(L[0]) <= 2 ** (3 - 1) * lam1                 # |b1|^2 <= 2^(n-1) lambda1^2


def test_babai_matches_bruteforce_for_short_error():
    rng = random.Random(2)
    for _ in range(50):
        v = T.combo([rng.randrange(-5, 6), rng.randrange(-5, 6)], T.GOOD)
        t = [v[0] + rng.randint(-4, 4), v[1] + rng.randint(-4, 4)]
        assert T.babai_round(T.GOOD, t) == v == T.babai_nearest_plane(T.GOOD, t)
        assert T.cvp_bruteforce(T.GOOD, t, R=8) == v


def test_bad_basis_same_lattice_but_useless():
    assert abs(T.det2(T.GOOD)) == abs(T.det2(T.BAD))
    assert T.hadamard_ratio(T.GOOD) > 0.9 > 0.3 > T.hadamard_ratio(T.BAD)
    good, bad = T.trapdoor_experiment()
    assert good == 1.0 and bad < 0.5
    b1, b2 = T.gauss_reduce(*T.BAD)                   # reduction recovers a good basis
    assert T.norm2(b1) == T.norm2(T.svp_bruteforce(T.GOOD))


def test_nearest_plane_in_3d_vs_bruteforce():
    B = [[7, 0, 1], [1, 8, -1], [0, 2, 9]]
    rng = random.Random(3)
    for _ in range(30):
        v = T.combo([rng.randrange(-3, 4) for _ in range(3)], B)
        t = [x + rng.randint(-2, 2) for x in v]
        assert T.babai_nearest_plane(B, t) == v == T.cvp_bruteforce(B, t, R=5)
