"""RSAES-OAEP exactly as specified in RFC 8017 (PKCS #1 v2.2) [S20].

Primitive: IND-CCA RSA encryption (in the ROM), i.e. padded RSA.
Note: notes/10-key-exchange-pke.md (lecture 12), section on RSA-OAEP.
Standard: RFC 8017 [S20], replayed against 37 Project Wycheproof vectors
[S24] and the `cryptography` package in both directions (test_oaep.py).

Section map, so every line here is traceable:

  I2OSP / OS2IP          RFC 8017 sec. 4.1 / 4.2
  RSAEP / RSADP          RFC 8017 sec. 5.1.1 / 5.1.2
  MGF1                   RFC 8017 appendix B.2.1
  RSAES-OAEP-ENCRYPT     RFC 8017 sec. 7.1.1
  RSAES-OAEP-DECRYPT     RFC 8017 sec. 7.1.2

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
The *encoding* here is faithful to the RFC and is checked against published
test vectors in `test_oaep.py`.  The surrounding code is not: `rsadp` uses a
plain big-int `pow`, there is no blinding, and `eme_oaep_decode` raises a
Python exception whose traceback timing is not constant.  A real
implementation must make every decryption failure indistinguishable --
RFC 8017 sec. 7.1.2 step 3(g) says so explicitly, because a decoder that
leaks *which* check failed is broken by Manger's attack (CRYPTO 2001).
Never use this to protect anything.

Lecture 12 of the course ("PKCS #1 v2.0") draws OAEP as two rounds of a
Feistel network over (seed, m || padding); this file is the same object
written out as the standard specifies it, including the label hash and the
0x01 separator that the classroom picture leaves out.
"""
from __future__ import annotations

import hashlib

import rng


class OAEPError(Exception):
    """RFC 8017 sec. 7.1.2: 'decryption error'.  The RFC requires that the
    *same* error be returned for every failure mode, with no timing
    difference -- see the module docstring."""


# ------------------------------------------------- sec. 4: data conversion
def i2osp(x: int, x_len: int) -> bytes:
    """Integer-to-Octet-String, RFC 8017 sec. 4.1.  Big-endian, fixed width."""
    if x < 0 or x >= 256 ** x_len:
        raise ValueError("integer too large")
    return x.to_bytes(x_len, "big")


def os2ip(octets: bytes) -> int:
    """Octet-String-to-Integer, RFC 8017 sec. 4.2."""
    return int.from_bytes(octets, "big")


# --------------------------------------------- sec. 5.1: RSA primitives
def rsaep(pub: dict, m: int) -> int:
    """RSAEP, RFC 8017 sec. 5.1.1.  Requires 0 <= m <= n-1."""
    n = pub["n"]
    if not 0 <= m <= n - 1:
        raise ValueError("message representative out of range")
    return pow(m, pub["e"], n)


def rsadp(priv: dict, c: int) -> int:
    """RSADP, RFC 8017 sec. 5.1.2.  Requires 0 <= c <= n-1."""
    n = priv["n"]
    if not 0 <= c <= n - 1:
        raise ValueError("ciphertext representative out of range")
    return pow(c, priv["d"], n)


# ------------------------------------------ appendix B.2.1: MGF1
def mgf1(mgf_seed: bytes, mask_len: int, hash_fn=hashlib.sha256) -> bytes:
    """MGF1, RFC 8017 appendix B.2.1.

    T = Hash(mgfSeed || I2OSP(0,4)) || Hash(mgfSeed || I2OSP(1,4)) || ...
    truncated to mask_len octets.  The counter is four octets, big-endian.
    """
    h_len = hash_fn().digest_size
    if mask_len > (1 << 32) * h_len:
        raise ValueError("mask too long")
    out = bytearray()
    counter = 0
    while len(out) < mask_len:
        out += hash_fn(mgf_seed + i2osp(counter, 4)).digest()
        counter += 1
    return bytes(out[:mask_len])


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


# ------------------------------------------- sec. 7.1.1: EME-OAEP encoding
def eme_oaep_encode(msg: bytes, k: int, label: bytes = b"",
                    hash_fn=hashlib.sha256, seed: bytes | None = None) -> bytes:
    """EME-OAEP encoding, RFC 8017 sec. 7.1.1 step 2.

    Produces the k-octet encoded message

        EM = 0x00 || maskedSeed || maskedDB

    where DB = lHash || PS || 0x01 || M.  `seed` is for reproducing test
    vectors only; leave it None so a fresh seed is drawn.
    """
    h_len = hash_fn().digest_size
    m_len = len(msg)
    if m_len > k - 2 * h_len - 2:
        raise ValueError("message too long")

    l_hash = hash_fn(label).digest()                       # (a)
    ps = b"\x00" * (k - m_len - 2 * h_len - 2)             # (b)
    db = l_hash + ps + b"\x01" + msg                       # (c)  len k-hLen-1
    if seed is None:                                       # (d)
        seed = rng.token_bytes(h_len)
    if len(seed) != h_len:
        raise ValueError("seed must be hLen octets")

    db_mask = mgf1(seed, k - h_len - 1, hash_fn)           # (e)
    masked_db = _xor(db, db_mask)                          # (f)
    seed_mask = mgf1(masked_db, h_len, hash_fn)            # (g)
    masked_seed = _xor(seed, seed_mask)                    # (h)
    return b"\x00" + masked_seed + masked_db               # (i)


def eme_oaep_decode(em: bytes, k: int, label: bytes = b"",
                    hash_fn=hashlib.sha256) -> bytes:
    """EME-OAEP decoding, RFC 8017 sec. 7.1.2 step 3.

    Undoes the two masking rounds, then checks three things at once:
    Y == 0x00, lHash' == lHash, and that DB contains a 0x01 separator after
    the padding string.  The RFC requires a single indistinguishable error.
    """
    h_len = hash_fn().digest_size
    if k < 2 * h_len + 2 or len(em) != k:
        raise OAEPError("decryption error")

    l_hash = hash_fn(label).digest()                       # (a)
    y, masked_seed, masked_db = em[0:1], em[1:1 + h_len], em[1 + h_len:]   # (b)
    seed_mask = mgf1(masked_db, h_len, hash_fn)            # (c)
    seed = _xor(masked_seed, seed_mask)                    # (d)
    db_mask = mgf1(seed, k - h_len - 1, hash_fn)           # (e)
    db = _xor(masked_db, db_mask)                          # (f)

    l_hash_prime, rest = db[:h_len], db[h_len:]            # (g)
    # Walk the padding string; the first non-zero octet must be 0x01.
    i = 0
    while i < len(rest) and rest[i] == 0x00:
        i += 1
    bad = (y != b"\x00") or (l_hash_prime != l_hash) \
        or (i == len(rest)) or (rest[i] != 0x01)
    if bad:
        raise OAEPError("decryption error")
    return rest[i + 1:]


# ------------------------------------------------- sec. 7.1: the schemes
def _modulus_len(n: int) -> int:
    """k = length in octets of the modulus (RFC 8017 sec. 7.1 notation)."""
    return (n.bit_length() + 7) // 8


def encrypt(pub: dict, msg: bytes, label: bytes = b"",
            hash_fn=hashlib.sha256, seed: bytes | None = None) -> bytes:
    """RSAES-OAEP-ENCRYPT, RFC 8017 sec. 7.1.1.  pub = {'n':..., 'e':...}."""
    k = _modulus_len(pub["n"])
    em = eme_oaep_encode(msg, k, label, hash_fn, seed)
    return i2osp(rsaep(pub, os2ip(em)), k)


def decrypt(priv: dict, ct: bytes, label: bytes = b"",
            hash_fn=hashlib.sha256) -> bytes:
    """RSAES-OAEP-DECRYPT, RFC 8017 sec. 7.1.2.  priv = {'n':..., 'd':...}."""
    k = _modulus_len(priv["n"])
    h_len = hash_fn().digest_size
    if len(ct) != k or k < 2 * h_len + 2:                  # step 1
        raise OAEPError("decryption error")
    try:
        m = rsadp(priv, os2ip(ct))                         # step 2
        em = i2osp(m, k)
    except ValueError as exc:
        raise OAEPError("decryption error") from exc
    return eme_oaep_decode(em, k, label, hash_fn)          # step 3


def max_message_len(n: int, hash_fn=hashlib.sha256) -> int:
    """k - 2*hLen - 2 (RFC 8017 sec. 7.1.1 step 1b).  For a 2048-bit modulus
    and SHA-256 that is 256 - 64 - 2 = 190 octets -- which is why real
    systems use OAEP only to wrap a symmetric key (hybrid encryption)."""
    return _modulus_len(n) - 2 * hash_fn().digest_size - 2


if __name__ == "__main__":
    from rsa import keygen

    rng.seed(2027)                               # reproducible output; see rng.py
    key = keygen(2048)
    pub = {"n": key["n"], "e": key["e"]}
    msg = b"attack at dawn"

    print(f"modulus  k = {_modulus_len(key['n'])} octets, "
          f"max message = {max_message_len(key['n'])} octets")

    c1 = encrypt(pub, msg)
    c2 = encrypt(pub, msg)
    print("randomised (same m, different c):", c1 != c2)
    print("round-trip:", decrypt(key, c1) == msg and decrypt(key, c2) == msg)

    # The label is authenticated but not encrypted (RFC 8017 sec. 7.1):
    # decrypting under the wrong label fails.
    c3 = encrypt(pub, msg, label=b"session-42")
    print("right label:", decrypt(key, c3, label=b"session-42") == msg)
    try:
        decrypt(key, c3, label=b"session-43")
        print("wrong label: NOT rejected (bug)")
    except OAEPError:
        print("wrong label: rejected")

    # The point of OAEP: textbook RSA is multiplicatively malleable, so
    # c * 2^e decrypts to 2*m.  With OAEP the mauled ciphertext decodes to
    # garbage and the format check rejects it.
    mauled = os2ip(c1) * pow(2, key["e"], key["n"]) % key["n"]
    try:
        decrypt(key, i2osp(mauled, _modulus_len(key["n"])))
        print("mauled ciphertext: NOT rejected (bug)")
    except OAEPError:
        print("mauled ciphertext: rejected (textbook RSA would return 2m)")

    # One flipped bit in maskedDB scrambles the seed, hence the whole DB.
    flipped = bytearray(c1)
    flipped[-1] ^= 0x01
    try:
        decrypt(key, bytes(flipped))
        print("flipped bit: NOT rejected (bug)")
    except OAEPError:
        print("flipped bit: rejected (all-or-nothing transform)")
