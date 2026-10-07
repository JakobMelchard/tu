"""Tests for signatures.py (note 11).  RSASSA-PKCS1-v1_5 (RFC 8017 sec. 8.2,
9.2 [S20]) is cross-checked against the `cryptography` package in both
directions on a library-generated 2048-bit key; Schnorr runs over RFC 3526
group 14 [S26] and is checked by its algebra, including the two exam
questions on special soundness and nonce reuse [S16, S15]."""
import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa as librsa

import dh
import rng
import rsa
import signatures as sig

G14 = sig.SchnorrParams.from_values(dh.MODP2048, 2)


def _lib_keypair():
    lib = librsa.generate_private_key(public_exponent=65537, key_size=2048)
    n = lib.private_numbers()
    ours = {"n": n.public_numbers.n, "e": n.public_numbers.e, "d": n.d, "p": n.p, "q": n.q,
            "dp": n.dmp1, "dq": n.dmq1, "qinv": n.iqmp}
    return lib, ours


def test_pkcs1_v15_signatures_interoperate_with_the_library():
    lib, key = _lib_keypair()
    msg = b"certificate to be signed"
    ours = sig.rsassa_pkcs1_v15_sign(key, msg)
    lib.public_key().verify(ours, msg, padding.PKCS1v15(), hashes.SHA256())   # raises if wrong
    theirs = lib.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    assert theirs == ours                        # the scheme is deterministic
    assert sig.rsassa_pkcs1_v15_verify(key, msg, theirs)
    assert not sig.rsassa_pkcs1_v15_verify(key, msg + b"!", theirs)
    with pytest.raises(InvalidSignature):
        lib.public_key().verify(ours, msg + b"!", padding.PKCS1v15(), hashes.SHA256())


def test_pkcs1_v15_encoding_layout():
    """RFC 8017 sec. 9.2 step 5: 00 01 ff..ff 00 || DigestInfo || H(m)."""
    em = sig.emsa_pkcs1_v15_encode(b"abc", 256)
    assert em[:2] == b"\x00\x01" and em[2:-52] == b"\xff" * 202 and em[-52] == 0
    assert em[-51:-32] == sig.SHA256_DIGEST_INFO
    with pytest.raises(ValueError):
        sig.emsa_pkcs1_v15_encode(b"abc", 61)


def test_textbook_forgery_verifies_and_fdh_resists_it():
    key = rsa.keygen(512)
    m, s = sig.textbook_forgery(key)
    assert sig.rsa_verify_textbook(key, m, s)            # forgery works on textbook RSA
    m_bytes = m.to_bytes((key["n"].bit_length() + 7) // 8, "big")
    assert not sig.fdh_verify(key, m_bytes, s)           # sigma^e is not H(m)


def test_textbook_homomorphic_forgery():
    key = rsa.keygen(512)
    s1, s2 = sig.rsa_sign_textbook(key, 111), sig.rsa_sign_textbook(key, 222)
    fm, fs = sig.rsa_homomorphic_forgery(key, 111, s1, 222, s2)
    assert fm == 111 * 222 and sig.rsa_verify_textbook(key, fm, fs)


def test_fdh_sign_verify():
    key = rsa.keygen(512)
    s = sig.fdh_sign(key, b"hello")
    assert sig.fdh_verify(key, b"hello", s)
    assert not sig.fdh_verify(key, b"hell0", s)


def test_schnorr_identification():
    x, y = sig.schnorr_keygen(G14)
    assert sig.schnorr_identify(G14, x, lambda t: 1 + rng.randbelow(G14.q - 1))
    t, c, s = sig.schnorr_transcript(G14, x, lambda t: 12345)
    assert sig.schnorr_check(G14, y, t, c, s) and not sig.schnorr_check(G14, y, t, c + 1, s)


def test_special_soundness_extracts_the_witness():
    """Two accepting answers to one commitment reveal x (note 11)."""
    x, y = sig.schnorr_keygen(G14)
    r = 1 + rng.randbelow(G14.q - 1)
    tr1 = sig.schnorr_transcript(G14, x, lambda t: 7, r)
    tr2 = sig.schnorr_transcript(G14, x, lambda t: 11, r)
    assert sig.schnorr_check(G14, y, *tr1) and sig.schnorr_check(G14, y, *tr2)
    assert sig.schnorr_extract(G14, tr1, tr2) == x


def test_schnorr_signature():
    x, y = sig.schnorr_keygen(G14)
    s = sig.schnorr_sign(G14, x, b"approve")
    assert sig.schnorr_verify(G14, y, b"approve", s)
    assert not sig.schnorr_verify(G14, y, b"reject", s)
    x2, y2 = sig.schnorr_keygen(G14)                      # wrong key fails
    assert not sig.schnorr_verify(G14, y2, b"approve", s)


def test_schnorr_nonce_reuse_recovers_the_key():
    """Final exam 31 January 2025, question 5b, and 2 February 2021,
    question 6b [S16, S15]: two signatures, one nonce, and x falls out."""
    x, y = sig.schnorr_keygen(G14)
    r = 1 + rng.randbelow(G14.q - 1)
    s1 = sig.schnorr_sign(G14, x, b"m1", r)
    s2 = sig.schnorr_sign(G14, x, b"m2", r)
    assert sig.schnorr_verify(G14, y, b"m1", s1) and sig.schnorr_verify(G14, y, b"m2", s2)
    assert sig.schnorr_nonce_reuse_attack(G14, s1, s2) == x
