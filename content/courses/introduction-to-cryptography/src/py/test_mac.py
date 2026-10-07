"""Tests for mac.py (note 07).  HMAC is checked against the stdlib and the
`cryptography` package here and against RFC 4231 in test_standard_vectors.py
[S22]; HKDF against all seven RFC 5869 appendix A cases read from the
vendored RFC [S34] and against `cryptography`'s HKDF; CBC-MAC over AES
against `cryptography`'s AES-CBC with a zero IV."""
import hashlib
import hmac as std_hmac

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as libhmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

import mac
import rfc_vectors
import rng
from private_key import AESBlock, xor

HASHES = {"SHA-1": hashlib.sha1, "SHA-256": hashlib.sha256}
RFC5869 = rfc_vectors.rfc5869_cases()


def test_prf_mac_verify_and_reject():
    key = rng.token_bytes(16)
    m = rng.token_bytes(32)
    t = mac.prf_mac(key, m)
    assert mac.prf_mac_verify(key, m, t)
    assert not mac.prf_mac_verify(key, m, xor(t, b"\x01" + b"\x00" * 31))
    assert not mac.prf_mac_verify(rng.token_bytes(16), m, t)


def test_cbc_mac_length_check():
    key = rng.token_bytes(16)
    with pytest.raises(ValueError):
        mac.cbc_mac(key, b"not a block multiple")
    assert len(mac.cbc_mac(key, b"12345678")) == 8


def test_cbc_mac_over_aes_is_the_last_cbc_block():
    """CBC-MAC(m) = last block of CBC-Enc with IV = 0, no padding."""
    key = rng.token_bytes(16)
    for nblocks in (1, 2, 5):
        msg = rng.token_bytes(16 * nblocks)
        enc = Cipher(algorithms.AES(key), modes.CBC(b"\x00" * 16)).encryptor()
        lib = enc.update(msg) + enc.finalize()
        assert mac.cbc_mac(key, msg, AESBlock(key)) == lib[-16:]


@pytest.mark.parametrize("cipher", ["feistel", "aes"])
def test_cbc_mac_variable_length_forgery(cipher):
    key = rng.token_bytes(16)
    c = AESBlock(key) if cipher == "aes" else None
    forged_msg, forged_tag, (m1, m2) = mac.cbc_mac_forgery(key, c)
    assert mac.cbc_mac(key, forged_msg, c) == forged_tag
    assert forged_msg not in (m1, m2)            # a genuinely new message


@pytest.mark.parametrize("hash_fn", [hashlib.sha1, hashlib.sha256, hashlib.sha512])
def test_hmac_matches_stdlib_and_cryptography(hash_fn):
    lib_hash = {"sha1": hashes.SHA1, "sha256": hashes.SHA256, "sha512": hashes.SHA512}[hash_fn().name]
    for _ in range(30):
        key = rng.token_bytes(rng.randbelow(200) + 1)       # shorter and longer than a block
        msg = rng.token_bytes(rng.randbelow(300))
        ours = mac.hmac(key, msg, hash_fn)
        assert ours == std_hmac.new(key, msg, hash_fn).digest()
        h = libhmac.HMAC(key, lib_hash())
        h.update(msg)
        assert ours == h.finalize()


@pytest.mark.parametrize("case", RFC5869, ids=[f"A.{i + 1}" for i in range(len(RFC5869))])
def test_hkdf_rfc5869_appendix_a(case):
    hash_fn = HASHES[case["hash"]]
    salt = case["salt"] or b""                    # None = "not provided"
    assert mac.hkdf_extract(salt, case["IKM"], hash_fn) == case["PRK"]
    assert mac.hkdf_expand(case["PRK"], case["info"], case["L"], hash_fn) == case["OKM"]


def test_rfc5869_parser_saw_all_seven_cases():
    assert len(RFC5869) == 7 and sum(c["hash"] == "SHA-256" for c in RFC5869) == 3


def test_hkdf_matches_cryptography():
    for length in (1, 32, 33, 100, 255 * 32):
        ikm, salt, info = rng.token_bytes(40), rng.token_bytes(16), rng.token_bytes(8)
        lib = HKDF(hashes.SHA256(), length, salt, info).derive(ikm)
        assert mac.hkdf(ikm, length, salt, info) == lib
    with pytest.raises(ValueError):
        mac.hkdf(b"x", 255 * 32 + 1)


def test_encrypt_then_mac_roundtrip_and_tamper():
    k_enc, k_mac = rng.token_bytes(16), rng.token_bytes(16)
    msg = b"authenticated encryption via encrypt-then-MAC"
    ct, tag = mac.encrypt_then_mac(k_enc, k_mac, msg)
    assert mac.etm_decrypt(k_enc, k_mac, ct, tag) == msg
    with pytest.raises(ValueError):
        mac.etm_decrypt(k_enc, k_mac, bytes([ct[0] ^ 1]) + ct[1:], tag)
    with pytest.raises(ValueError):
        mac.etm_decrypt(k_enc, k_mac, ct, xor(tag, b"\x01" + b"\x00" * 31))
