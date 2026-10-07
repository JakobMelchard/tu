"""Message authentication codes: a PRF MAC, CBC-MAC and its variable-length
forgery, HMAC and HKDF built from scratch, and encrypt-then-MAC
authenticated encryption.

Primitive: MACs (EUF-CMA), the HMAC PRF, the HKDF key-derivation function,
and the encrypt-then-MAC composition.
Note: notes/07-macs-and-ae.md (lecture 8); HKDF is the TLS 1.3 key schedule
of notes/12-tls-and-pki.md; `prf_mac` meets length extension in
notes/08-hash-functions.md.
Standard: `hmac` is RFC 2104 sec. 2 [S19] = FIPS 198-1 [S29], checked
against the RFC 4231 test cases (test_standard_vectors.py); `hkdf` is
RFC 5869 sec. 2 [S34], checked against its appendix A test cases read from
the vendored RFC.  CBC-MAC and the PRF MAC are textbook (Katz-Lindell
sec. 4 [S10]); CBC-MAC over AES is cross-checked against the
`cryptography` package's AES-CBC.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
By default the block MAC uses the toy Feistel PRP and the PRF MAC the toy
SHA-256(k || m) PRF; HMAC and HKDF match the standards, but nothing here is
constant-time or meant for deployment.
"""
from __future__ import annotations

import hashlib
import hmac as std_hmac

import rng
from prg import toy_prf
from private_key import FeistelPRP, _blocks, xor


# ------------------------------------------------------------- PRF MAC
def prf_mac(key: bytes, msg: bytes) -> bytes:
    """Fixed-length MAC: t = F_k(m). A PRF is a secure MAC because forging a
    tag means predicting F_k on a fresh input, i.e. distinguishing F from
    random. Only sound for messages of one fixed length: with the toy PRF
    SHA-256(k || m) a variable-length m is broken by length extension
    (`hashing.sha256_length_extension`, note 08)."""
    return toy_prf(key, msg)


def prf_mac_verify(key: bytes, msg: bytes, tag: bytes) -> bool:
    return std_hmac.compare_digest(prf_mac(key, msg), tag)   # constant-time compare


# ------------------------------------------------------------- CBC-MAC
def cbc_mac(key: bytes, msg: bytes, cipher=None) -> bytes:
    """Basic CBC-MAC: run CBC with a zero IV, output the last block.
    Secure ONLY for fixed-length messages. No IV, no last-block encryption,
    so the length-extension forgery below applies.  `cipher` is any object
    with `block_size` and `encrypt_block` (default: FeistelPRP(key))."""
    cipher = cipher if cipher is not None else FeistelPRP(key)
    bs = cipher.block_size
    if len(msg) == 0 or len(msg) % bs:
        raise ValueError(f"message length must be a positive multiple of {bs}")
    tag = b"\x00" * bs
    for block in _blocks(msg, bs):
        tag = cipher.encrypt_block(xor(block, tag))
    return tag


def cbc_mac_forgery(key: bytes, cipher=None):
    """Demonstrate the classic variable-length forgery on raw CBC-MAC.
    Given t1 = MAC(m1) (one block) and t2 = MAC(m2) (one block), the
    two-block message  m1 || (m2 xor t1)  has tag t2:
        block1 -> E(m1 xor 0) = t1
        block2 -> E((m2 xor t1) xor t1) = E(m2) = t2.
    The attacker queries only m1 and m2, never the forged message."""
    bs = (cipher or FeistelPRP).block_size
    m1 = rng.token_bytes(bs)
    m2 = rng.token_bytes(bs)
    t1 = cbc_mac(key, m1, cipher)
    t2 = cbc_mac(key, m2, cipher)
    forged_msg = m1 + xor(m2, t1)
    forged_tag = t2
    return forged_msg, forged_tag, (m1, m2)


# --------------------------------------------------------------- HMAC
def hmac(key: bytes, msg: bytes, hash_fn=hashlib.sha256) -> bytes:
    """RFC 2104 sec. 2: H((K xor opad) || H((K xor ipad) || m)), with the key
    hashed first if longer than the block (64 bytes for SHA-1/-256, 128 for
    SHA-384/-512) and zero-padded otherwise.  A secure MAC (indeed a PRF)
    if the compression function is a PRF; the outer call is what stops the
    length extension that breaks H(k || m)."""
    block = hash_fn().block_size
    if len(key) > block:
        key = hash_fn(key).digest()
    key = key.ljust(block, b"\x00")
    inner = hash_fn(xor(key, b"\x36" * block) + msg).digest()
    return hash_fn(xor(key, b"\x5c" * block) + inner).digest()


def hmac_sha256(key: bytes, msg: bytes) -> bytes:
    return hmac(key, msg, hashlib.sha256)


# --------------------------------------------------------------- HKDF
def hkdf_extract(salt: bytes, ikm: bytes, hash_fn=hashlib.sha256) -> bytes:
    """RFC 5869 sec. 2.2: PRK = HMAC-Hash(salt, IKM); an absent salt is
    HashLen zero bytes.  Concentrates the entropy of, say, a DH shared value
    into a uniform-looking key."""
    return hmac(salt or b"\x00" * hash_fn().digest_size, ikm, hash_fn)


def hkdf_expand(prk: bytes, info: bytes, length: int, hash_fn=hashlib.sha256) -> bytes:
    """RFC 5869 sec. 2.3: T(i) = HMAC(PRK, T(i-1) || info || i), i = 1, 2, ...
    The counter octet caps the output at 255 * HashLen bytes."""
    if length > 255 * hash_fn().digest_size:
        raise ValueError("HKDF output too long")
    out, t, i = b"", b"", 1
    while len(out) < length:
        t = hmac(prk, t + info + bytes([i]), hash_fn)
        out, i = out + t, i + 1
    return out[:length]


def hkdf(ikm: bytes, length: int, salt: bytes = b"", info: bytes = b"",
         hash_fn=hashlib.sha256) -> bytes:
    return hkdf_expand(hkdf_extract(salt, ikm, hash_fn), info, length, hash_fn)


# ---------------------------------------------------- encrypt-then-MAC
def encrypt_then_mac(k_enc: bytes, k_mac: bytes, msg: bytes) -> tuple[bytes, bytes]:
    """The composition with a security proof: encrypt, then MAC the
    ciphertext. Ciphertext integrity implies CCA security. Keys MUST be
    independent."""
    from private_key import AESBlock, ctr_encrypt
    ct = ctr_encrypt(AESBlock(k_enc), msg)
    return ct, hmac_sha256(k_mac, ct)


def etm_decrypt(k_enc: bytes, k_mac: bytes, ct: bytes, tag: bytes) -> bytes:
    """Verify the tag BEFORE decrypting. A wrong tag aborts, so the
    decryption routine never processes attacker-chosen ciphertexts and a
    padding oracle cannot arise."""
    from private_key import AESBlock, ctr_decrypt
    if not std_hmac.compare_digest(hmac_sha256(k_mac, ct), tag):
        raise ValueError("authentication failed")
    return ctr_decrypt(AESBlock(k_enc), ct)


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    key = rng.token_bytes(16)

    # PRF MAC on one block
    m = b"32-byte message for the PRF MAC!"
    t = prf_mac(key, m)
    print("PRF MAC verifies:", prf_mac_verify(key, m, t))
    print("tampered rejected:", not prf_mac_verify(key, m, xor(t, b"\x01" + b"\x00" * 31)))

    # CBC-MAC variable-length forgery
    forged_msg, forged_tag, (m1, m2) = cbc_mac_forgery(key)
    print("\nCBC-MAC forgery valid without querying the forged message:",
          cbc_mac(key, forged_msg) == forged_tag)

    # HMAC matches the standard library; HKDF reproduces RFC 5869 test case 1
    hk, hm = rng.token_bytes(20), b"hash-based MAC"
    print("\nHMAC matches stdlib:", hmac_sha256(hk, hm) == std_hmac.new(hk, hm, hashlib.sha256).digest())
    okm = hkdf(b"\x0b" * 22, 42, bytes(range(13)), bytes(range(0xf0, 0xfa)))
    print("HKDF, RFC 5869 A.1 inputs, OKM starts:", okm[:8].hex(), "(RFC: 3cb25f25faacd57a)")

    # Encrypt-then-MAC authenticated encryption
    k_enc, k_mac = rng.token_bytes(16), rng.token_bytes(16)
    ct, tag = encrypt_then_mac(k_enc, k_mac, b"authenticated and confidential")
    print("\nEtM roundtrip:", etm_decrypt(k_enc, k_mac, ct, tag))
    try:
        etm_decrypt(k_enc, k_mac, ct, xor(tag, b"\x01" + b"\x00" * 31))
    except ValueError as e:
        print("EtM rejects tampered ciphertext:", e)
