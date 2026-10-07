"""Tests for aes.py (note 03): the pure FIPS 197 AES against the numbers
FIPS 197 [S21] and SP 800-38A [S25] print (transcribed from the vendored
PDFs, section by section), and against the `cryptography` package."""
import pytest

import aes
import rng
from private_key import AESBlock, cbc_decrypt, cbc_encrypt, ctr_decrypt, ctr_encrypt

h = bytes.fromhex

# FIPS 197 appendix A: key and the last four expanded words for each size.
KEY_EXPANSION = [
    ("A.1", "2b7e151628aed2a6abf7158809cf4f3c", 44,
     "d014f9a8c9ee2589e13f0cc8b6630ca6"),
    ("A.2", "8e73b0f7da0e6452c810f32b809079e562f8ead2522c6b7b", 52,
     "e98ba06f448c773c8ecc720401002202"),
    ("A.3", "603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4", 60,
     "fe4890d1e6188d0b046df344706c631e"),
]

# SP 800-38A appendix F.1.1 / F.1.3 / F.1.5: ECB with the appendix-A keys.
F1_PLAIN = ["6bc1bee22e409f96e93d7e117393172a", "ae2d8a571e03ac9c9eb76fac45af8e51",
            "30c81c46a35ce411e5fbc1191a0a52ef", "f69f2445df4f9b17ad2b417be66c3710"]
F1_ECB = [
    ("F.1.1", KEY_EXPANSION[0][1], ["3ad77bb40d7a3660a89ecaf32466ef97", "f5d3d58503b9699de785895a96fdbaaf",
                                    "43b1cd7f598ece23881b00e3ed030688", "7b0c785e27e8ad3f8223207104725dd4"]),
    ("F.1.3", KEY_EXPANSION[1][1], ["bd334f1d6e45f25ff712a214571fa5cc", "974104846d0ad3ad7734ecb3ecee4eef",
                                    "ef7afd2270e2e60adce0ba2face6444e", "9a4b41ba738d6c72fb16691603c18e0e"]),
    ("F.1.5", KEY_EXPANSION[2][1], ["f3eed1bdb5d2a03c064b5a7e3db181f8", "591ccb10d410ed26dc5ba74a31362870",
                                    "b6ed21b99ca6f4f9f153e7b1beafed1d", "23304b7a39f9f3ff067d8d8f9e24ecc7"]),
]


@pytest.mark.parametrize("sec,key,nwords,last4", KEY_EXPANSION, ids=[k[0] for k in KEY_EXPANSION])
def test_key_expansion_fips197_appendix_a(sec, key, nwords, last4):
    w = aes.key_expansion(h(key))
    assert len(w) == nwords
    assert b"".join(w[:len(h(key)) // 4]) == h(key)          # w0.. is the key itself
    assert b"".join(w[-4:]).hex() == last4


def test_cipher_example_fips197_appendix_b():
    """Input 3243f6a8..., key 2b7e1516...; the appendix prints the state at
    the start of every round.  Round 1 starts at input xor key; round 10's
    start is read column by column off the appendix B table."""
    trace = []
    w = aes.key_expansion(h("2b7e151628aed2a6abf7158809cf4f3c"))
    ct = aes.encrypt_block(h("3243f6a8885a308d313198a2e0370734"), w, trace)
    assert trace[0].hex() == "193de3bea0f4e22b9ac68d2ae9f84808"
    assert trace[9].hex() == "eb40f21e592e38848ba113e71bc342d2"
    assert ct.hex() == "3925841d02dc09fbdc118597196a0b32"
    assert aes.decrypt_block(ct, w).hex() == "3243f6a8885a308d313198a2e0370734"


@pytest.mark.parametrize("sec,key,expected", F1_ECB, ids=[f[0] for f in F1_ECB])
def test_sp800_38a_ecb_all_key_sizes(sec, key, expected):
    cipher = aes.PureAES(h(key))
    for p, c in zip(F1_PLAIN, expected):
        assert cipher.encrypt_block(h(p)).hex() == c
        assert cipher.decrypt_block(h(c)).hex() == p


@pytest.mark.parametrize("klen", [16, 24, 32])
def test_matches_the_library_on_random_blocks(klen):
    for _ in range(20):
        key, block = rng.token_bytes(klen), rng.token_bytes(16)
        ours, lib = aes.PureAES(key), AESBlock(key)
        assert ours.encrypt_block(block) == lib.encrypt_block(block)
        assert ours.decrypt_block(block) == lib.decrypt_block(block)


def test_modes_run_on_the_pure_cipher():
    """`PureAES` is a drop-in for the library block, so CBC and CTR built in
    private_key.py give byte-identical ciphertexts on either."""
    key, iv, nonce = rng.token_bytes(16), rng.token_bytes(16), rng.token_bytes(8)
    msg = b"the same modes, now over AES written from FIPS 197"
    pure, lib = aes.PureAES(key), AESBlock(key)
    assert cbc_encrypt(pure, msg, iv) == cbc_encrypt(lib, msg, iv)
    assert ctr_encrypt(pure, msg, nonce) == ctr_encrypt(lib, msg, nonce)
    assert cbc_decrypt(pure, cbc_encrypt(lib, msg, iv)) == msg
    assert ctr_decrypt(pure, ctr_encrypt(lib, msg, nonce)) == msg


def test_bad_key_length_rejected():
    with pytest.raises(ValueError):
        aes.key_expansion(b"\x00" * 20)
