"""Tests for numtheory.py (note 09).  Every function is cross-checked against
`sympy` or Python's built-in `pow`; the RFC 3526 safe prime is checked in
test_standard_vectors.py.  Random inputs come from a fixed-seed generator."""
import math
import random

import sympy

import numtheory as nt

R = random.Random(9)


def test_egcd_bezout():
    for _ in range(100):
        a, b = R.randint(1, 10**9), R.randint(1, 10**9)
        g, x, y = nt.egcd(a, b)
        assert g == math.gcd(a, b) and a * x + b * y == g


def test_modinv_and_modexp_match_python():
    for _ in range(100):
        n = R.randint(3, 10**6)
        a = R.randint(1, n - 1)
        if math.gcd(a, n) == 1:
            assert nt.modinv(a, n) == pow(a, -1, n)
        assert nt.modexp(a, 12345, n) == pow(a, 12345, n)
        assert nt.modexp(3, -5, 1000003) == pow(3, -5, 1000003)


def test_crt():
    x = nt.crt([2, 3, 2], [3, 5, 7])
    assert x == 23 and x % 3 == 2 and x % 5 == 3 and x % 7 == 2


def test_miller_rabin_vs_sympy():
    for n in list(range(2, 2000)) + [561, 1105, 1729, 2 ** 61 - 1, 2 ** 61 + 1]:
        assert nt.miller_rabin(n) == sympy.isprime(n), n


def test_gen_prime_and_safe_prime():
    p = nt.gen_prime(128)
    assert p.bit_length() == 128 and sympy.isprime(p)
    sp = nt.gen_safe_prime(48)
    assert sympy.isprime(sp) and sympy.isprime((sp - 1) // 2)


def test_euler_phi_and_factorize():
    for n in range(1, 500):
        assert nt.euler_phi(n) == sympy.totient(n)
    assert nt.factorize(2 * 2 * 3 * 7 * 7 * 101) == {2: 2, 3: 1, 7: 2, 101: 1}


def test_order_generator():
    p = 23
    g = nt.find_generator(p)
    assert g == 5 and nt.order(g, p) == 22
    assert nt.order(2, p) == 11 and not nt.is_generator(2, p)
    assert sympy.primitive_root(p) == g


def test_subgroup_generator_has_order_q():
    p = nt.gen_safe_prime(32)
    q = (p - 1) // 2
    g = nt.subgroup_generator(p, q)
    assert nt.modexp(g, q, p) == 1 and g != 1


def test_bsgs():
    p = 1000003
    g = nt.find_generator(p)
    for x in (0, 1, 2, 999, 123456, p - 2):
        assert nt.bsgs(g, nt.modexp(g, x, p), p) == x


def test_order_mod_matches_sympy_and_the_exam_items():
    """Note 00: F24 1k, [3^1000000 mod 22] = 1 because ord(3) = 5 divides
    10^6 (phi(22) = 10 is the trap), and F23 4a, [2^63 mod 11] = 8 because
    ord(2) = 10 and 63 = 3 mod 10 [S16, S12]."""
    assert nt.order_mod(3, 22) == sympy.n_order(3, 22) == 5
    assert nt.modexp(3, 10 ** 6, 22) == pow(3, 10 ** 6, 22) == 1
    assert nt.order_mod(2, 11) == 10 and nt.modexp(2, 63, 11) == 8
    for n in range(2, 200):
        for a in range(1, n):
            if math.gcd(a, n) == 1:
                assert nt.order_mod(a, n) == sympy.n_order(a, n)


def test_modexp_edge_cases_match_pow():
    for b, e, n in ((5, 0, 1), (5, 3, 1), (0, 0, 7), (0, 5, 7), (7, 0, 7)):
        assert nt.modexp(b, e, n) == pow(b, e, n)
