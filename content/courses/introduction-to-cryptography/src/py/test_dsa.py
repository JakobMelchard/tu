"""Tests for dsa.py (note 11).  All twenty DSA signatures of RFC 6979
appendix A.2.1 (1024-bit p, 160-bit q, so SHA-256 and longer are truncated)
and A.2.2 (2048/256) [S32] are read from the vendored RFC and reproduced
exactly, nonce included; the 2048-bit ones are also verified by the
`cryptography` package's DSA (OpenSSL)."""
import hashlib
import warnings

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa as libdsa
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

import dsa
import rfc_vectors
import rng

HASH = {"SHA-1": hashlib.sha1, "SHA-224": hashlib.sha224, "SHA-256": hashlib.sha256,
        "SHA-384": hashlib.sha384, "SHA-512": hashlib.sha512}
LIBHASH = {"SHA-1": hashes.SHA1, "SHA-224": hashes.SHA224, "SHA-256": hashes.SHA256,
           "SHA-384": hashes.SHA384, "SHA-512": hashes.SHA512}
KEYS = {bits: rfc_vectors.rfc6979_dsa(bits) for bits in (1024, 2048)}
CASES = [(bits, v) for bits, (_, sigs) in KEYS.items() for v in sigs]


def test_parser_found_every_vector():
    for bits, (key, sigs) in KEYS.items():
        assert key["p"].bit_length() == bits and len(sigs) == 10
        assert pow(key["g"], key["x"], key["p"]) == key["y"]        # the key is consistent


@pytest.mark.parametrize("bits,v", CASES,
                         ids=[f"{b}-{v['hash']}-{v['msg'].decode()}" for b, v in CASES])
def test_rfc6979_appendix_a2(bits, v):
    key, _ = KEYS[bits]
    hash_fn = HASH[v["hash"]]
    assert dsa.rfc6979_k(key["x"], key["q"], hash_fn(v["msg"]).digest(), hash_fn) == v["k"]
    assert dsa.sign(key, v["msg"], hash_fn) == (v["r"], v["s"])
    assert dsa.verify(key, v["msg"], (v["r"], v["s"]), hash_fn)
    assert not dsa.verify(key, v["msg"] + b"!", (v["r"], v["s"]), hash_fn)


def test_library_verifies_our_signatures():
    key, sigs = KEYS[2048]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")                  # DSA is deprecated in the library
        params = libdsa.DSAParameterNumbers(key["p"], key["q"], key["g"])
        pub = libdsa.DSAPublicNumbers(key["y"], params).public_key()
        for v in sigs:
            sig = dsa.sign(key, v["msg"], HASH[v["hash"]])
            pub.verify(encode_dss_signature(*sig), v["msg"], LIBHASH[v["hash"]]())


def test_nonce_reuse_recovers_the_private_key():
    """A repeated k gives a repeated r, and two linear equations in (k, x)."""
    key, _ = KEYS[2048]
    q = key["q"]
    k = 1 + rng.randbelow(q - 1)
    m1, m2 = b"first", b"second"
    s1, s2 = dsa.sign(key, m1, k=k), dsa.sign(key, m2, k=k)
    assert s1[0] == s2[0]                                # the tell-tale equal r
    z = lambda m: dsa.bits2int(hashlib.sha256(m).digest(), q.bit_length())
    assert dsa.nonce_reuse_attack(q, z(m1), s1, z(m2), s2) == (k, key["x"])


def test_deterministic_nonces_differ_per_message():
    key, _ = KEYS[2048]
    r1, _ = dsa.sign(key, b"first")
    r2, _ = dsa.sign(key, b"second")
    assert r1 != r2 and dsa.sign(key, b"first") == dsa.sign(key, b"first")


def test_out_of_range_signature_rejected():
    key, sigs = KEYS[1024]
    for bad in ((0, 1), (1, 0), (key["q"], 1)):
        assert not dsa.verify(key, b"sample", bad)


def test_rfc6979_a1_conversions_and_retry_loop():
    """RFC 6979 A.1 (K-163, qlen = 163, SHA-256, "sample"): int2octets and
    bits2octets on a qlen that is not a multiple of 8, and a k that is only
    accepted on the third try of step h (typed in from the RFC).  The A.2
    vectors above never take the retry branch."""
    q = 0x4000000000000000000020108A2E0CC0D99F8A5EF
    x = 0x09A4D6792295A7F730FC3F2B49CBC0F62E862272F
    h1 = hashlib.sha256(b"sample").digest()
    assert dsa.int2octets(x, q).hex() == "009a4d6792295a7f730fc3f2b49cbc0f62e862272f"
    assert dsa.bits2octets(h1, q).hex() == "01795edf0d54db760f156d0dac04c0322b3a204224"
    assert dsa.rfc6979_k(x, q, h1) == 0x23AF4074C90A02B3FE61D286D5C87F425E6BDD81B
