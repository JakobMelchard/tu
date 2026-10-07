"""Tests for private_key.py (note 06).  The modes are cross-checked against
the `cryptography` package's AES-CBC and AES-CTR here and against the
SP 800-38A appendix F vectors [S25] in test_standard_vectors.py; PKCS #7
padding against the library's padder; the padding-oracle attack must
recover the plaintext from the oracle bit alone."""
import pytest
from cryptography.hazmat.primitives import padding as libpadding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import private_key as pk
import rng


def test_prf_scheme_roundtrip_and_randomised():
    key = rng.token_bytes(16)
    m = rng.token_bytes(pk.PRF_LEN)
    assert pk.prf_decrypt(key, pk.prf_encrypt(key, m)) == m
    assert pk.prf_encrypt(key, m) != pk.prf_encrypt(key, m)   # fresh r each time


def test_prf_scheme_rejects_wrong_length():
    with pytest.raises(ValueError):
        pk.prf_encrypt(rng.token_bytes(16), b"too short")


def test_feistel_is_a_permutation():
    f = pk.FeistelPRP(rng.token_bytes(16))
    seen = set()
    for _ in range(500):
        blk = rng.token_bytes(8)
        ct = f.encrypt_block(blk)
        assert f.decrypt_block(ct) == blk
        seen.add(ct)
    assert len(seen) == 500          # no collisions observed


def test_pkcs7_roundtrip_matches_library_and_rejects_bad():
    for n in range(0, 40):
        m = rng.token_bytes(n)
        padder = libpadding.PKCS7(128).padder()
        assert pk.pad(m, 16) == padder.update(m) + padder.finalize()
        assert pk.unpad(pk.pad(m, 16), 16) == m
    with pytest.raises(ValueError):
        pk.unpad(b"\x00" * 15 + b"\x05", 16)


@pytest.mark.parametrize("cipher_factory", [
    lambda: pk.FeistelPRP(rng.token_bytes(16)),
    lambda: pk.AESBlock(rng.token_bytes(16)),
])
@pytest.mark.parametrize("enc,dec", [
    (pk.ecb_encrypt, pk.ecb_decrypt),
    (pk.cbc_encrypt, pk.cbc_decrypt),
    (pk.ctr_encrypt, pk.ctr_decrypt),
])
def test_modes_roundtrip(cipher_factory, enc, dec):
    cipher = cipher_factory()
    for n in (1, 15, 16, 17, 100):
        m = rng.token_bytes(n)
        assert dec(cipher, enc(cipher, m)) == m


def test_cbc_matches_reference_aes_cbc():
    key, iv = rng.token_bytes(16), rng.token_bytes(16)
    msg = b"cross-check CBC against the library implementation!!"
    ours = pk.cbc_encrypt(pk.AESBlock(key), msg, iv=iv)
    ref = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    lib = iv + ref.update(pk.pad(msg, 16)) + ref.finalize()
    assert ours == lib


def test_ctr_matches_reference_aes_ctr():
    key, nonce = rng.token_bytes(16), rng.token_bytes(8)
    msg = b"cross-check CTR keystream too"
    ours = pk.ctr_encrypt(pk.AESBlock(key), msg, nonce=nonce)[8:]
    ref = Cipher(algorithms.AES(key), modes.CTR(nonce + b"\x00" * 8)).encryptor()
    lib = ref.update(msg) + ref.finalize()
    assert ours == lib


def test_ecb_leaks_structure_cbc_does_not():
    aes = pk.AESBlock(rng.token_bytes(16))
    img = pk.structured_image()
    ecb_rows = pk.block_pattern(pk.ecb_encrypt(aes, img), 16, 16)
    # ECB: exactly three block labels (background, rectangle, padding block)
    assert len(set("".join(ecb_rows))) == 3
    cbc_rows = pk.block_pattern(pk.cbc_encrypt(aes, img)[16:], 16, 16)
    # CBC: essentially every block distinct
    assert len(set("".join(cbc_rows))) > 20


def test_padding_oracle_recovers_plaintext():
    aes = pk.AESBlock(rng.token_bytes(16))
    secret = b"attack at dawn, bring the manuals and the maps"
    ct = pk.cbc_encrypt(aes, secret)
    oracle = pk.make_padding_oracle(aes)
    assert pk.padding_oracle_attack(oracle, ct, 16) == secret


def test_ctr_keystream_agrees_with_the_sp800_38a_counter():
    """nonce || counter is the SP 800-38A sec. 6.5 counter block as long as the
    counter half does not overflow into the nonce."""
    aes, nonce = pk.AESBlock(rng.token_bytes(16)), rng.token_bytes(8)
    assert pk.ctr_keystream(aes, nonce, 5) == pk.ctr_keystream_from(aes, nonce + bytes(8), 5)


def test_ctr_rejects_a_nonce_decrypt_cannot_split_off():
    with pytest.raises(ValueError):
        pk.ctr_encrypt(pk.AESBlock(rng.token_bytes(16)), b"msg", nonce=bytes(4))
