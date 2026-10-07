"""Tests for prg.py (notes 04, 05, 06).

ChaCha20 reproduces RFC 8439 sec. 2.3.2 (the block function) and sec. 2.4.2
(the cipher) [S36], both read from the vendored RFC, and agrees with the
`cryptography` package's ChaCha20.  The toy PRF and PRF-to-PRG are
cross-checked against `hashlib`; the LCG and stretching have no standard and
are checked for the properties the notes claim."""
import hashlib

import pytest
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

import prg
import rfc_vectors
import rng


def test_chacha20_block_rfc8439_2_3_2():
    v = rfc_vectors.rfc8439_block_vector()
    assert len(v["block"]) == 64
    assert prg.chacha20_block(v["key"], v["counter"], v["nonce"]) == v["block"]


def test_chacha20_cipher_rfc8439_2_4_2():
    v = rfc_vectors.rfc8439_cipher_vector()
    ct = prg.chacha20_encrypt(v["key"], v["counter"], v["nonce"], v["plaintext"])
    assert ct == v["ciphertext"]
    assert prg.chacha20_encrypt(v["key"], v["counter"], v["nonce"], ct) == v["plaintext"]


def test_chacha20_matches_the_library():
    """`cryptography` takes a 16-byte nonce: 32-bit little-endian counter,
    then the 96-bit RFC 8439 nonce."""
    for n in (0, 1, 63, 64, 65, 300):
        key, nonce, msg = rng.token_bytes(32), rng.token_bytes(12), rng.token_bytes(n)
        counter = rng.randbelow(1000)
        lib = Cipher(algorithms.ChaCha20(key, counter.to_bytes(4, "little") + nonce),
                     mode=None).encryptor().update(msg)
        assert prg.chacha20_encrypt(key, counter, nonce, msg) == lib


def test_lcg_is_deterministic():
    assert prg.LCG(7).stream(3) == prg.LCG(7).stream(3)


def test_lcg_distinguisher_wins():
    m = 2 ** 31 - 1
    for _ in range(50):
        out = prg.LCG(rng.randbelow(m), a=16807, c=0, m=m).stream(4)
        assert prg.lcg_distinguisher(out, m)
    # on random input the distinguisher almost never says "pseudorandom"
    false_pos = sum(prg.lcg_distinguisher([rng.randbelow(m) for _ in range(4)], m) for _ in range(300))
    assert false_pos <= 2
    assert prg.lcg_advantage(100) > 0.95


def test_toy_prf_is_sha256_of_key_and_input():
    k = rng.token_bytes(16)
    assert prg.toy_prf(k, b"x") == hashlib.sha256(k + b"x").digest()
    assert prg.toy_prf(k, b"x") != prg.toy_prf(k, b"y")
    assert prg.toy_prf(k, b"x") != prg.toy_prf(rng.token_bytes(16), b"x")
    assert len(prg.toy_prf(k, b"")) == prg.BLOCK


def test_prf_to_prg_lengths_prefix_and_definition():
    s = rng.token_bytes(16)
    for n in (1, 31, 32, 33, 100):
        assert len(prg.prf_to_prg(s, n)) == n
    assert prg.prf_to_prg(s, 100)[:40] == prg.prf_to_prg(s, 40)
    ref = b"".join(hashlib.sha256(s + i.to_bytes(8, "big")).digest() for i in range(4))
    assert prg.prf_to_prg(s, 100) == ref[:100]


def test_stretch_expands_and_depends_on_seed():
    s = rng.token_bytes(16)
    out = prg.stretch(s, 50)
    assert len(out) == 50 and out == prg.stretch(s, 50)
    assert out != prg.stretch(rng.token_bytes(16), 50)


def test_statistical_test_has_no_advantage():
    adv = prg.prg_distinguisher_test(b"\x00" * 64, lambda: prg.stretch(rng.token_bytes(16), 64), 100)
    assert adv < 0.05


def test_quarter_round_rfc8439_2_1_1():
    """Sec. 2.1.1's quarter-round test vector (four words, typed in)."""
    st = [0x11111111, 0x01020304, 0x9b8d6f43, 0x01234567]
    prg._quarter_round(st, 0, 1, 2, 3)
    assert st == [0xea2a92f4, 0xcb1cf8ce, 0x4581472e, 0x5881c4bb]


def test_chacha20_refuses_to_wrap_the_counter():
    """A wrapped 32-bit counter would replay keystream block 0: the two-time pad."""
    key, nonce = bytes(32), bytes(12)
    assert len(prg.chacha20_encrypt(key, 2 ** 32 - 1, nonce, bytes(64))) == 64
    with pytest.raises(ValueError):
        prg.chacha20_encrypt(key, 2 ** 32 - 1, nonce, bytes(65))


def test_prg_one_bit_expands_by_one_byte():
    for n in (1, 16, prg.BLOCK - 1):
        assert len(prg.prg_one_bit(bytes(n))) == n + 1
    with pytest.raises(ValueError):                      # would silently stretch to nothing
        prg.stretch(bytes(prg.BLOCK), 5)
