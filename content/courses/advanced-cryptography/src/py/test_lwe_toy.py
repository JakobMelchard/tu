"""Tests for the educational toy code in lwe_toy.py: Regev correctness and failure-rate estimate, the
noiseless-LWE break, FIPS 203 Compress/Decompress properties, negacyclic
multiplication against sympy, and the toy module-LWE KEM."""
import numpy as np
import pytest
import sympy

import lwe_toy as L


def test_regev_correct_small_noise():
    pk, s = L.regev_keygen(sigma=2.0)
    for b in [0, 1] * 100:
        assert L.regev_decrypt(s, L.regev_encrypt(pk, b)) == b


@pytest.mark.parametrize("sigma", [8.0, 12.0, 16.0])
def test_failure_rate_matches_gaussian_estimate(sigma):
    assert abs(L.failure_rate(sigma, trials=20000) - L.failure_estimate(sigma)) < 0.02


def test_noise_is_what_makes_lwe_hard_for_elimination():
    rng = np.random.default_rng(0)
    A = rng.integers(0, L.REGEV_Q, (L.REGEV_N + 8, L.REGEV_N))
    s = rng.integers(0, L.REGEV_Q, L.REGEV_N)
    assert np.array_equal(L.solve_mod_q(A, A @ s % L.REGEV_Q), s)
    noisy = (A @ s + L.gaussian_error(len(A), 2.0, rng)) % L.REGEV_Q
    assert not np.array_equal(L.solve_mod_q(A, noisy), s)


@pytest.mark.parametrize("d", range(1, 12))
def test_compress_decompress_fips203_properties(d):
    ys = np.arange(1 << d)
    assert np.array_equal(L.compress(L.decompress(ys, d), d), ys)   # [S16 sec. 4.2.1]
    xs = np.arange(L.Q)
    err = (L.decompress(L.compress(xs, d), d) - xs) % L.Q
    err = np.minimum(err, L.Q - err)
    assert err.max() <= round(L.Q / (1 << (d + 1)))                 # rounding error bound


def test_negacyclic_polymul_against_sympy():
    X = sympy.symbols("X")
    rng = np.random.default_rng(1)
    for _ in range(5):
        a, b = rng.integers(0, L.Q, L.N), rng.integers(0, L.Q, L.N)
        pa = sympy.Poly(list(reversed(a.tolist())), X, modulus=L.Q)
        pb = sympy.Poly(list(reversed(b.tolist())), X, modulus=L.Q)
        r = (pa * pb).rem(sympy.Poly(X**L.N + 1, X, modulus=L.Q))
        want = [int(c) % L.Q for c in reversed(r.all_coeffs())]
        want += [0] * (L.N - len(want))
        assert L.polymul(a, b).tolist() == want


def test_cbd_range_and_mean():
    x = L.cbd(b"seed", 3, 64)
    assert x.min() >= -3 and x.max() <= 3 and abs(x.mean()) < 0.2


def test_pke_roundtrip():
    ek, s = L.pke_keygen(b"\x01" * 32)
    rng = np.random.default_rng(2)
    for i in range(50):
        m = rng.integers(0, 2, L.N)
        c = L.pke_encrypt(ek, m, bytes([i]) * 32)
        assert np.array_equal(L.pke_decrypt(s, c), m)


def test_kem_agreement_and_implicit_rejection():
    ek, dk = L.kem_keygen()
    for _ in range(50):
        K, c = L.kem_encaps(ek)
        assert L.kem_decaps(dk, c) == K
    bad = (c[0], (c[1] + 1) % (1 << L.DV))
    k1, k2 = L.kem_decaps(dk, bad), L.kem_decaps(dk, bad)
    assert k1 != K and k1 == k2              # deterministic pseudorandom reject key


def test_kem_deterministic_given_m():
    ek, dk = L.kem_keygen()
    m = b"\x5a\xa5"
    assert L.kem_encaps(ek, m)[0] == L.kem_encaps(ek, m)[0]
