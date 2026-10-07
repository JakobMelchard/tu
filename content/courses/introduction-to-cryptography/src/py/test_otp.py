"""Tests for otp.py (note 02).  The pad is checked against RFC 8439
sec. 2.4.2 [S36] (a ChaCha20 keystream as the pad reproduces the RFC's
ciphertext, the pseudo-one-time pad of note 05) and against the exact
distribution the perfect-secrecy proof computes."""
from collections import Counter

import pytest

import otp
import prg
import rfc_vectors


def test_roundtrip():
    m = b"hello, world"
    k = otp.keygen(len(m))
    assert otp.decrypt(k, otp.encrypt(k, m)) == m


def test_length_mismatch_rejected():
    with pytest.raises(ValueError):
        otp.encrypt(b"\x00", b"ab")


def test_pseudo_one_time_pad_reproduces_rfc8439():
    """Enc_k(m) = G(k) xor m with G = ChaCha20: the RFC's ciphertext is the
    RFC's plaintext xor its keystream, and reusing that keystream on a second
    message leaks m1 xor m2 exactly as a reused pad does."""
    v = rfc_vectors.rfc8439_cipher_vector()
    pad = prg.chacha20_encrypt(v["key"], v["counter"], v["nonce"], bytes(len(v["plaintext"])))
    assert otp.encrypt(pad, v["plaintext"]) == v["ciphertext"]
    m2 = bytes(reversed(v["plaintext"]))
    leak = otp.two_time_pad_leak(v["ciphertext"], otp.encrypt(pad, m2))
    assert leak == otp.xor(v["plaintext"], m2)


def test_every_ciphertext_exactly_once_per_message():
    """Thm 2.10 by enumeration on one byte: for each m the 256 keys map to
    the 256 ciphertexts bijectively, so Pr[C = c | M = m] = 2^-8 exactly,
    independent of m."""
    for m in (b"\x00", b"\x42", b"\xff"):
        assert sorted(otp.encrypt(bytes([k]), m)[0] for k in range(256)) == list(range(256))


def test_ciphertext_uniform_for_fixed_message():
    """Perfect secrecy on 1 byte: Pr[C = c | M = m] = 2^-8 for every c.
    Empirically: 20000 samples spread over all 256 values roughly evenly."""
    m = b"\x42"
    counts = Counter(otp.encrypt(otp.keygen(1), m)[0] for _ in range(20000))
    assert len(counts) == 256
    assert max(counts.values()) < 2.0 * 20000 / 256


def test_two_time_pad_leak_is_message_xor():
    m1, m2 = b"attack at dawn!!", b"defend the wall!"
    k = otp.keygen(len(m1))
    assert otp.two_time_pad_leak(otp.encrypt(k, m1), otp.encrypt(k, m2)) == otp.xor(m1, m2)


def test_crib_drag_finds_true_position():
    m1 = b"attack the bridge at dawn"
    m2 = b"retreat to the forest now"
    k = otp.keygen(len(m1))
    leak = otp.two_time_pad_leak(otp.encrypt(k, m1), otp.encrypt(k, m2))
    hits = dict(otp.crib_drag(leak, b"bridge"))
    assert hits[11] == m2[11:17]          # 'bridge' is at offset 11 in m1


def test_malleability():
    m = b"pay 100"
    k = otp.keygen(len(m))
    c = otp.encrypt(k, m)
    delta = otp.xor(b"pay 100", b"pay 900")
    assert otp.decrypt(k, otp.malleability_demo(c, delta)) == b"pay 900"
