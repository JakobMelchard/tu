"""Tests for the educational toy code in secret_sharing.py: reconstruction from any t+1 shares, perfect
privacy of any t shares (exhaustively over a small field), degree bookkeeping
of the BGW gates, and end-to-end MPC."""
import itertools
import random
from collections import Counter

import pytest

import secret_sharing as S


def test_any_t_plus_1_reconstruct():
    t, n = 2, 6
    sh = S.share(4321, t, n)
    for subset in itertools.combinations(range(1, n + 1), t + 1):
        assert S.reconstruct([(i, sh[i - 1]) for i in subset]) == 4321


def test_t_shares_perfectly_private_exact():
    """p = 11, t = 2, n = 4: for every secret, the joint distribution of the
    shares of parties {1, 3} (over all t random coefficients) is uniform."""
    p, t, n = 11, 2, 4
    dists = []
    for s in range(p):
        cnt = Counter()
        for a1 in range(p):
            for a2 in range(p):
                f = lambda x: (s + a1 * x + a2 * x * x) % p
                cnt[(f(1), f(3))] += 1
        dists.append(cnt)
    assert all(d == dists[0] for d in dists)
    assert len(dists[0]) == p * p and set(dists[0].values()) == {1}


def test_share_matches_polynomial_degree():
    rng = random.Random(0)
    for t in range(4):
        sh = S.share(rng.randrange(S.P), t, 9, rng)
        assert S.degree(sh) <= t


def test_add_is_local_and_degree_t():
    a, b = S.share(10, 2, 5), S.share(20, 2, 5)
    c = S.add(a, b)
    assert S.degree(c) <= 2 and S.reconstruct(list(enumerate(c, 1))) == 30
    assert S.reconstruct(list(enumerate(S.scal(7, a), 1))) == 70


@pytest.mark.parametrize("mul", [S.mul_resharing, S.mul_double_sharing])
def test_multiplication_degree_reduction(mul):
    rng = random.Random(1)
    t, n = 2, 5
    for _ in range(20):
        x, y = rng.randrange(S.P), rng.randrange(S.P)
        a, b = S.share(x, t, n, rng), S.share(y, t, n, rng)
        local = S.mul_local(a, b)
        assert S.degree(local) <= 2 * t
        assert S.reconstruct(list(enumerate(local, 1))) == x * y % S.P   # needs all 2t+1
        out = mul(a, b, t, rng)
        c = out[0] if isinstance(out, tuple) else out
        assert S.degree(c) <= t
        assert S.reconstruct([(i, c[i - 1]) for i in (2, 4, 5)]) == x * y % S.P


def test_honest_majority_needed():
    a, b = S.share(2, 2, 4), S.share(3, 2, 4)         # n = 4 < 2t + 1 = 5
    with pytest.raises(ValueError):
        S.mul_resharing(a, b, 2)
    with pytest.raises(ValueError):
        S.mul_double_sharing(a, b, 2)


def test_opened_mask_is_uniform():
    """d(0) = ab - r in [S7]'s protocol is independent of ab (small check)."""
    rng = random.Random(3)
    seen = Counter()
    for _ in range(4000):
        a, b = S.share(5, 1, 3, rng), S.share(6, 1, 3, rng)
        _, d0 = S.mul_double_sharing(a, b, 1, rng)
        seen[d0 * 8 // S.P] += 1                      # 8 buckets
    assert min(seen.values()) > 350


@pytest.mark.parametrize("mul", [S.mul_resharing, S.mul_double_sharing])
def test_mpc_circuit(mul):
    rng = random.Random(5)
    for _ in range(10):
        xs = [rng.randrange(S.P) for _ in range(5)]
        want = ((xs[0] + xs[1]) * xs[2] + 3 * xs[3] * xs[4]) % S.P
        assert S.mpc_eval(xs, 2, S.EXAMPLE, mul, rng) == want


def test_beaver_multiplication_keeps_degree_t():
    rng = random.Random(9)
    t, n = 2, 5
    for _ in range(20):
        x, y = rng.randrange(S.P), rng.randrange(S.P)
        c = S.mul_beaver(S.share(x, t, n, rng), S.share(y, t, n, rng), S.beaver_triple(t, n, rng))
        assert S.degree(c) <= t and S.reconstruct(list(enumerate(c, 1))) == x * y % S.P
