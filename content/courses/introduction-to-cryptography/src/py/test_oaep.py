"""Tests for the RFC 8017 sec. 7.1 OAEP implementation.

The important ones are `test_wycheproof_*`: they replay 37 published
RSAES-OAEP decryption vectors (SHA-256 / MGF1-SHA-256, 2048-bit modulus)
from Project Wycheproof [S24], vendored at
`../../refs/vectors/rsa_oaep_2048_sha256_mgf1sha256_test.json` under
Apache-2.0.  Eighteen are valid ciphertexts whose plaintext we must recover
exactly; nineteen are malformed in ways the RFC's format check is supposed
to catch (wrong lHash, corrupted PS, missing 0x01 separator, non-zero Y,
unreduced ciphertext).  RFC 8017 itself prints no test vectors, so this is
the closest available thing to the specification's own numbers.
"""
from __future__ import annotations

import json
import pathlib

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

import oaep

VECTORS = (pathlib.Path(__file__).resolve().parents[2]
           / "refs" / "vectors" / "rsa_oaep_2048_sha256_mgf1sha256_test.json")


def _load():
    data = json.loads(VECTORS.read_text())
    group = data["testGroups"][0]
    pk = group["privateKey"]
    priv = {"n": int(pk["modulus"], 16), "d": int(pk["privateExponent"], 16)}
    pub = {"n": priv["n"], "e": int(pk["publicExponent"], 16)}
    return priv, pub, group


PRIV, PUB, GROUP = _load()
CASES = GROUP["tests"]


def _ids(cases):
    return [f"tc{c['tcId']}-{c['result']}" for c in cases]


@pytest.mark.parametrize("case", CASES, ids=_ids(CASES))
def test_wycheproof_oaep_decrypt(case):
    """Replay one published RSAES-OAEP decryption vector [S24]."""
    ct = bytes.fromhex(case["ct"])
    label = bytes.fromhex(case["label"])
    if case["result"] == "valid":
        assert oaep.decrypt(PRIV, ct, label) == bytes.fromhex(case["msg"])
    else:
        with pytest.raises(oaep.OAEPError):
            oaep.decrypt(PRIV, ct, label)


def test_wycheproof_group_parameters():
    """Guard against silently swapping the vector file for a different one."""
    assert (GROUP["sha"], GROUP["mgf"], GROUP["mgfSha"], GROUP["keySize"]) == \
        ("SHA-256", "MGF1", "SHA-256", 2048)
    assert len(CASES) == 37
    assert sum(c["result"] == "valid" for c in CASES) == 18


def test_seeded_encrypt_reproduces_vector_ciphertext():
    """Encoding is deterministic given the seed, so re-encrypting a vector's
    plaintext with the seed recovered from its ciphertext must give the
    ciphertext back.  This pins RFC 8017 sec. 7.1.1 steps (e)-(i), which the
    decrypt-only vectors above exercise only in reverse."""
    case = next(c for c in CASES if c["result"] == "valid" and c["msg"])
    ct = bytes.fromhex(case["ct"])
    k = 256
    em = oaep.i2osp(oaep.rsadp(PRIV, oaep.os2ip(ct)), k)
    masked_seed, masked_db = em[1:33], em[33:]
    seed = bytes(a ^ b for a, b in zip(masked_seed, oaep.mgf1(masked_db, 32)))
    assert oaep.encrypt(PUB, bytes.fromhex(case["msg"]), seed=seed) == ct


# ------------------------------------------------------------ MGF1, sec. B.2.1
def test_mgf1_is_a_prefix_family():
    """T is built by concatenating Hash(seed || counter), so a shorter mask
    is a prefix of a longer one (RFC 8017 appendix B.2.1 step 4)."""
    long = oaep.mgf1(b"seed", 100)
    assert oaep.mgf1(b"seed", 40) == long[:40]
    assert len(oaep.mgf1(b"seed", 1)) == 1


def test_mgf1_first_block_is_the_bare_hash():
    import hashlib
    assert oaep.mgf1(b"x", 32) == hashlib.sha256(b"x" + b"\x00\x00\x00\x00").digest()


def test_i2osp_os2ip_roundtrip():
    assert oaep.i2osp(1, 4) == b"\x00\x00\x00\x01"
    assert oaep.os2ip(b"\x01\x00") == 256
    with pytest.raises(ValueError):
        oaep.i2osp(256, 1)


# ------------------------------------------------------ encoding-level checks
def test_encoded_message_layout():
    """EM = 0x00 || maskedSeed || maskedDB, length exactly k."""
    em = oaep.eme_oaep_encode(b"hi", 256, seed=b"\x00" * 32)
    assert len(em) == 256 and em[0] == 0x00
    assert oaep.eme_oaep_decode(em, 256) == b"hi"


def test_message_too_long_is_rejected():
    assert oaep.max_message_len(PUB["n"]) == 256 - 64 - 2
    with pytest.raises(ValueError):
        oaep.eme_oaep_encode(b"x" * 191, 256)


def test_longest_message_fits_exactly():
    msg = b"z" * oaep.max_message_len(PUB["n"])
    assert oaep.decrypt(PRIV, oaep.encrypt(PUB, msg)) == msg


def test_label_is_authenticated():
    ct = oaep.encrypt(PUB, b"secret", label=b"ctx-A")
    assert oaep.decrypt(PRIV, ct, label=b"ctx-A") == b"secret"
    with pytest.raises(oaep.OAEPError):
        oaep.decrypt(PRIV, ct, label=b"ctx-B")


def test_randomised_and_all_or_nothing():
    """Two properties the notes claim: a fresh seed per encryption, and that
    a single flipped ciphertext bit destroys the whole decoded block."""
    a, b = oaep.encrypt(PUB, b"m"), oaep.encrypt(PUB, b"m")
    assert a != b
    bad = bytearray(a)
    bad[-1] ^= 0x01
    with pytest.raises(oaep.OAEPError):
        oaep.decrypt(PRIV, bytes(bad))


def test_oaep_is_not_multiplicatively_malleable():
    """Textbook RSA: c * s^e decrypts to s*m.  With OAEP the mauled
    ciphertext fails the format check (notes 10/11)."""
    ct = oaep.encrypt(PUB, b"bid: 100")
    mauled = oaep.os2ip(ct) * pow(2, PUB["e"], PUB["n"]) % PUB["n"]
    with pytest.raises(oaep.OAEPError):
        oaep.decrypt(PRIV, oaep.i2osp(mauled, 256))


# ------------------------------------------------------ cross-check vs library
def _library_key():
    pem = GROUP["privateKeyPem"].encode()
    return serialization.load_pem_private_key(pem, password=None)


_OAEP = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None)


def test_library_decrypts_our_ciphertext():
    key = _library_key()
    ct = oaep.encrypt(PUB, b"interop")
    assert key.decrypt(ct, _OAEP) == b"interop"


def test_we_decrypt_library_ciphertext():
    key = _library_key()
    ct = key.public_key().encrypt(b"interop", _OAEP)
    assert oaep.decrypt(PRIV, ct) == b"interop"


def test_rsa_primitives_reject_out_of_range_representatives():
    """RFC 8017 sec. 5.1.1 / 5.1.2 step 1: 0 <= m, c <= n - 1."""
    m = 0x1234
    assert oaep.rsadp(PRIV, oaep.rsaep(PUB, m)) == m
    for bad in (-1, PUB["n"]):
        with pytest.raises(ValueError):
            oaep.rsaep(PUB, bad)
        with pytest.raises(ValueError):
            oaep.rsadp(PRIV, bad)
