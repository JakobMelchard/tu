"""Tests for hashing.py (note 08).

The pure SHA-256 is checked three ways: its derived constants against the
table FIPS 180-4 sec. 4.2.2 prints [S28], its digests against the RFC 6234
sec. 8.5 test patterns [S23] (in test_standard_vectors.py) and against
`hashlib` across every padding boundary, and its length extension against
`hashlib` on the extended message.  The toy Merkle-Damgard hash has no
standard; its padding is checked against SHA-256's."""
import hashlib

import hashing as h
import mac
import rng

# FIPS 180-4 sec. 4.2.2, "In hex, these constant words are" [S28].
FIPS180_K = bytes.fromhex(
    "428a2f9871374491b5c0fbcfe9b5dba53956c25b59f111f1923f82a4ab1c5ed5"
    "d807aa9812835b01243185be550c7dc372be5d7480deb1fe9bdc06a7c19bf174"
    "e49b69c1efbe47860fc19dc6240ca1cc2de92c6f4a7484aa5cb0a9dc76f988da"
    "983e5152a831c66db00327c8bf597fc7c6e00bf3d5a7914706ca635114292967"
    "27b70a852e1b21384d2c6dfc53380d13650a7354766a0abb81c2c92e92722c85"
    "a2bfe8a1a81a664bc24b8b70c76c51a3d192e819d6990624f40e3585106aa070"
    "19a4c1161e376c082748774c34b0bcb5391c0cb34ed8aa4a5b9cca4f682e6ff3"
    "748f82ee78a5636f84c878148cc7020890befffaa4506cebbef9a3f7c67178f2")
# FIPS 180-4 sec. 5.3.3, H(0) for SHA-256.
FIPS180_H0 = bytes.fromhex("6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19")


def test_constants_derived_from_their_definition_match_fips180_4():
    assert b"".join(k.to_bytes(4, "big") for k in h.SHA256_K) == FIPS180_K
    assert b"".join(x.to_bytes(4, "big") for x in h.SHA256_H0) == FIPS180_H0


def test_padding_is_fips180_4_section_5_1_1():
    """'abc' pads to one 512-bit block ending in the 64-bit length 24."""
    padded = b"abc" + h._pad(3, 64)
    assert len(padded) == 64 and padded[3] == 0x80 and padded[-8:] == (24).to_bytes(8, "big")
    for n in range(0, 200):                       # every residue of both block sizes
        assert (n + len(h._pad(n, 64))) % 64 == 0 and (n + len(h._pad(n))) % h.BLOCK == 0


def test_sha256_matches_hashlib_across_block_boundaries():
    for n in list(range(0, 130)) + [447, 448, 1000]:
        msg = rng.token_bytes(n)
        assert h.sha256(msg) == hashlib.sha256(msg).digest(), n


def test_sha256_length_extension_forges_a_secret_prefix_mac():
    """MAC_k(m) = SHA-256(k || m) is forgeable: the published tag is the
    chaining state, so the attacker keeps hashing (note 07, note 08)."""
    for klen in (1, 16, 55, 56, 64, 100):
        key = rng.token_bytes(klen)
        tag = hashlib.sha256(key + b"amount=10").digest()
        forged, msg = h.sha256_length_extension(tag, klen, b"amount=10", b"&amount=10000")
        assert msg.startswith(b"amount=10") and msg.endswith(b"&amount=10000")
        assert forged == hashlib.sha256(key + msg).digest()


def test_prf_mac_on_variable_length_messages_is_forgeable_but_hmac_is_not():
    """`mac.prf_mac` uses the toy PRF SHA-256(k || m), so it is only a MAC
    for one fixed message length.  The forged message was never queried."""
    key = rng.token_bytes(16)
    tag = mac.prf_mac(key, b"pay 10")
    forged, msg = h.sha256_length_extension(tag, 16, b"pay 10", b" and 1000000")
    assert msg != b"pay 10" and mac.prf_mac_verify(key, msg, forged)
    hmac_tag = mac.hmac_sha256(key, b"pay 10")
    forged2, msg2 = h.sha256_length_extension(hmac_tag, 16, b"pay 10", b" and 1000000")
    assert mac.hmac_sha256(key, msg2) != forged2


def test_merkle_damgard_deterministic_and_length():
    assert h.merkle_damgard(b"hello") == h.merkle_damgard(b"hello")
    assert len(h.merkle_damgard(b"anything at all")) == h.DIGEST
    assert h.merkle_damgard(b"a") != h.merkle_damgard(b"b")


def test_padding_is_injective_across_block_boundary():
    # messages differing only by length must not collide via padding
    assert h.merkle_damgard(b"\x00" * 7) != h.merkle_damgard(b"\x00" * 8)


def test_toy_length_extension_forges_valid_digest():
    for slen in (1, 5, 8, 9, 12, 16, 23):
        secret = rng.token_bytes(slen)
        forged, glue = h.length_extension(h.merkle_damgard(secret), slen, b"&role=admin")
        assert forged == h.merkle_damgard(secret + glue + b"&role=admin")


def test_birthday_attack_finds_collision_cheaply():
    a, b, tries = h.birthday_attack(24)
    assert a != b
    trunc = lambda x: hashlib.sha256(x).digest()[:3]
    assert trunc(a) == trunc(b)
    # birthday bound: expect ~ sqrt(pi/2 * 2^24) = 5134; allow generous slack
    assert tries < 40_000
