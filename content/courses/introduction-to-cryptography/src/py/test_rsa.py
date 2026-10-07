"""Tests for rsa.py (note 10).  Every generated key must be accepted by the
`cryptography` package (which validates n = pq, e d = 1 mod lambda(n) and
the CRT exponents), its CRT values must equal the library's, and the
textbook primitive must invert on the published 2048-bit Wycheproof key
[S24] that test_oaep.py uses; RSAEP / RSADP are RFC 8017 sec. 5.1 [S20]."""
import json
import math

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa as librsa

import rfc_vectors
import rsa
from numtheory import crt, egcd, euler_phi, gen_prime


def _lib_key(k: dict):
    pub = librsa.RSAPublicNumbers(k["e"], k["n"])
    return librsa.RSAPrivateNumbers(k["p"], k["q"], k["d"], k["dp"], k["dq"], k["qinv"], pub).private_key()


def test_keys_are_valid_for_the_library_and_crt_values_agree():
    for bits, e in ((512, 65537), (512, 3), (1024, 65537)):
        k = rsa.keygen(bits, e)
        lib = _lib_key(k).private_numbers()                 # raises if inconsistent
        assert (lib.dmp1, lib.dmq1, lib.iqmp) == (
            librsa.rsa_crt_dmp1(k["d"], k["p"]), librsa.rsa_crt_dmq1(k["d"], k["q"]),
            librsa.rsa_crt_iqmp(k["p"], k["q"]))
        assert (k["dp"], k["dq"], k["qinv"]) == (lib.dmp1, lib.dmq1, lib.iqmp)
        assert set(librsa.rsa_recover_prime_factors(k["n"], k["e"], k["d"])) == {k["p"], k["q"]}


def test_textbook_primitive_on_the_wycheproof_key():
    data = json.loads((rfc_vectors.REFS / "vectors" /
                       "rsa_oaep_2048_sha256_mgf1sha256_test.json").read_text())
    pk = data["testGroups"][0]["privateKey"]
    key = {"n": int(pk["modulus"], 16), "e": int(pk["publicExponent"], 16),
           "d": int(pk["privateExponent"], 16), "p": int(pk["prime1"], 16),
           "q": int(pk["prime2"], 16), "dp": int(pk["exponent1"], 16),
           "dq": int(pk["exponent2"], 16), "qinv": int(pk["coefficient"], 16)}
    for m in (0, 1, 2, 123456789, key["n"] - 1):
        c = rsa.encrypt(key, m)
        assert rsa.decrypt(key, c) == m == rsa.decrypt_crt(key, c)


def test_garner_crt_equals_general_crt():
    k = rsa.keygen(512)
    c = 987654321
    mp, mq = pow(c, k["dp"], k["p"]), pow(c, k["dq"], k["q"])
    assert rsa.decrypt_crt(k, c) == crt([mp, mq], [k["p"], k["q"]]) == rsa.decrypt(k, c)


def test_keygen_and_roundtrip():
    key = rsa.keygen(512)
    assert key["e"] * key["d"] % ((key["p"] - 1) * (key["q"] - 1)) == 1
    m = 987654321
    c = rsa.encrypt(key, m)
    assert rsa.decrypt(key, c) == m
    assert rsa.decrypt_crt(key, c) == m


def test_deterministic():
    key = rsa.keygen(512)
    assert rsa.encrypt(key, 5) == rsa.encrypt(key, 5)


def test_malleability():
    key = rsa.keygen(512)
    c = rsa.encrypt(key, 6)
    assert rsa.decrypt(key, rsa.malleability_demo(key, c, 7)) == 42


def test_small_message_cube_root():
    key = rsa.keygen(512, e=3)
    m = 424242
    assert rsa.small_message_attack(key, rsa.encrypt(key, m), 3) == m


def test_hastad_broadcast():
    msg = 123456789
    keys = [rsa.keygen(512, e=3) for _ in range(3)]
    cts = [rsa.encrypt(k, msg) for k in keys]
    assert rsa.small_e_attack(cts, [k["n"] for k in keys], 3) == msg


def test_common_modulus():
    from numtheory import modexp
    p, q = gen_prime(256), gen_prime(256)
    n, m = p * q, 31337
    e1, e2 = 3, 65537
    rec = rsa.common_modulus_attack(n, e1, e2, modexp(m, e1, n), modexp(m, e2, n))
    assert rec == m


def test_shared_prime_attack():
    """Final exam, 26 January 2024, question 4b [S12]: two RSA public keys
    whose moduli share a prime factor.  gcd recovers it and both secret
    keys follow."""
    shared = gen_prime(256)
    k1 = rsa._priv_from_factors(shared, gen_prime(256), 65537)
    k2 = rsa._priv_from_factors(shared, gen_prime(256), 65537)
    r1, r2 = rsa.shared_prime_attack(k1["n"], k2["n"], 65537, 65537)
    assert r1["d"] == k1["d"] and r2["d"] == k2["d"]
    m = 4711
    assert rsa.decrypt(r1, rsa.encrypt(k1, m)) == m


def test_independent_moduli_share_nothing():
    """The attack only bites on a faulty RNG: fresh keys are coprime."""
    a, b = rsa.keygen(512), rsa.keygen(512)
    assert math.gcd(a["n"], b["n"]) == 1


def test_rsa_is_a_permutation_of_the_unit_group():
    """Final exam, 26 January 2024, question 1j [S12]: for gcd(e, phi(N)) = 1
    the map x -> x^e mod N is a bijection on Z_N^*."""
    n, e = 3 * 5, 3                       # phi(15) = 8, gcd(3, 8) = 1
    assert egcd(e, euler_phi(n))[0] == 1
    units = [x for x in range(1, n) if egcd(x, n)[0] == 1]
    assert sorted(pow(x, e, n) for x in units) == units


def test_common_modulus_needs_coprime_exponents():
    with pytest.raises(ValueError):
        rsa.common_modulus_attack(3 * 11, 3, 9, 1, 1)
