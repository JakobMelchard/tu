"""Tests for the educational toy code in rom_reductions.py: oracle consistency and programming, the BR93
scheme and its log-reading reduction, keyless Schnorr signing by programming,
and forking-lemma extraction against the bound of [S27]."""
import random

import pytest
import sympy

import rom_reductions as R
from groups import MEDIUM, TINY


def test_oracle_consistent_logged_programmable():
    H = R.RandomOracle(1000, random.Random(0))
    a = H("x")
    assert H("x") == a and H.log == ["x", "x"]
    H.program("y", 5)
    assert H("y") == 5
    with pytest.raises(R.ProgrammingFailure):
        H.program("x", 1)


def test_toy_rsa_is_a_permutation_with_trapdoor():
    assert sympy.isprime(R.TOY_RSA_P) and sympy.isprime(R.TOY_RSA_Q)
    for x in (2, 12345, R.TOY_RSA_N - 2):
        assert R.f_inv(R.f(x)) == x


def test_br93_correct_and_reduction_reads_log():
    Gro = R.RandomOracle(2**32)
    for m in (0, 1, 2**31 + 7):
        ct = R.br_encrypt(Gro, m)
        assert R.br_decrypt(Gro, ct) == m
    ct = R.br_encrypt(Gro, 99)
    Gro.log.clear()
    for _ in range(50):                      # adversary's unrelated queries
        Gro(random.randrange(R.TOY_RSA_N))
    assert R.ow_inverter_from_log(ct[0], Gro.log) is None   # never asked r*: G(r*) hidden
    Gro(R.f_inv(ct[0]))                                       # now it asks
    assert R.f(R.ow_inverter_from_log(ct[0], Gro.log)) == ct[0]


def test_keyless_signing_by_programming():
    G = MEDIUM
    x = G.rand_scalar()
    y = G.exp(G.g, x)
    H = R.RandomOracle(G.q)
    for i in range(20):
        m = f"m{i}"
        assert R.verify(G, H, y, m, R.simulated_sign(G, H, y, m))
        assert R.verify(G, H, y, m, R.sign(G, H, x, m))    # real and simulated coexist


def test_programming_failure_rate_matches_bound():
    """TINY (q = 11): after Qro queries on random t, programming a signature
    fails about Qro/q of the time, as the collision term in [S4 (19.5)]."""
    G = TINY
    y = G.exp(G.g, 3)
    fails, trials, Qro = 0, 3000, 4
    rng = random.Random(7)
    for _ in range(trials):
        H = R.RandomOracle(G.q, rng)
        for _ in range(Qro):
            H((y, G.exp(G.g, rng.randrange(G.q)), "m"))
        try:
            R.simulated_sign(G, H, y, "m")
        except R.ProgrammingFailure:
            fails += 1
    assert fails / trials <= Qro / G.q + 0.05


@pytest.mark.parametrize("acc,q", [(1.0, 1), (0.5, 4), (0.8, 16)])
def test_forking_extracts_and_beats_bound(acc, q):
    G = MEDIUM
    x = G.rand_scalar()
    y = G.exp(G.g, x)
    A = R.toy_forger(G, x, acc, q)
    rng = random.Random(3)
    trials, wins = 3000, 0
    for _ in range(trials):
        out = R.fork(A, y, q, G.q, rng)
        if out:
            wins += 1
            assert R.extract_from_fork(G, *out) == x
    assert wins / trials >= R.forking_bound(acc, q, G.q) - 0.03
