"""DSA with deterministic nonces, and the key recovery a repeated nonce
allows.

Primitive: the Digital Signature Algorithm over a prime-order subgroup of
Z_p^*: r = (g^k mod p) mod q, s = k^-1 (H(m) + x r) mod q.
Note: notes/11-digital-signatures.md (lecture 13), section "DSA / ECDSA
overview" and the nonce-reuse pitfall.
Standard: DSA as FIPS 186 specifies it (FIPS 186-5 [S30] keeps it for
verification only); the per-message secret k is derived as in RFC 6979
sec. 3.2 [S32], with bits2int / int2octets / bits2octets of sec. 2.3 and
HMAC_DRBG built on `mac.hmac`.  Checked against all twenty DSA signatures
of RFC 6979 appendix A.2.1 and A.2.2, read from the vendored RFC, and
against the `cryptography` package's DSA verification.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
FIPS 186-5 withdrew DSA for signing; this exists to show the (EC)DSA
equations and why RFC 6979 was written.  Not constant-time.
"""
from __future__ import annotations

import hashlib

import rng
from mac import hmac
from numtheory import modexp, modinv


def bits2int(b: bytes, qlen: int) -> int:
    """RFC 6979 sec. 2.3.2: the leftmost qlen bits of b as an integer.  This
    is also how FIPS 186 truncates a hash longer than q."""
    x = int.from_bytes(b, "big")
    blen = 8 * len(b)
    return x >> (blen - qlen) if blen > qlen else x


def int2octets(x: int, q: int) -> bytes:
    """Sec. 2.3.3: x as rlen = 8 * ceil(qlen / 8) bits."""
    return x.to_bytes((q.bit_length() + 7) // 8, "big")


def bits2octets(b: bytes, q: int) -> bytes:
    """Sec. 2.3.4: bits2int, reduced once mod q, then int2octets."""
    z = bits2int(b, q.bit_length())
    return int2octets(z - q if z >= q else z, q)


def rfc6979_k(x: int, q: int, h1: bytes, hash_fn=hashlib.sha256) -> int:
    """Sec. 3.2: k from an HMAC_DRBG keyed with the private key and seeded
    with the message hash.  Deterministic, so no RNG failure can repeat a
    nonce, and a PRF output, so k is as unpredictable as a random one."""
    qlen, hlen = q.bit_length(), hash_fn().digest_size
    v, key = b"\x01" * hlen, b"\x00" * hlen                        # steps b, c
    seed = int2octets(x, q) + bits2octets(h1, q)
    key = hmac(key, v + b"\x00" + seed, hash_fn)                    # step d
    v = hmac(key, v, hash_fn)                                       # step e
    key = hmac(key, v + b"\x01" + seed, hash_fn)                    # step f
    v = hmac(key, v, hash_fn)                                       # step g
    while True:                                                     # step h
        t = b""
        while 8 * len(t) < qlen:
            v = hmac(key, v, hash_fn)
            t += v
        k = bits2int(t, qlen)
        if 1 <= k < q:
            return k
        key = hmac(key, v + b"\x00", hash_fn)
        v = hmac(key, v, hash_fn)


def sign(key: dict, msg: bytes, hash_fn=hashlib.sha256, k: int | None = None) -> tuple[int, int]:
    """(r, s) with r = (g^k mod p) mod q, s = k^-1 (z + x r) mod q, where z is
    the truncated hash.  k defaults to RFC 6979; pass one only to replay a
    nonce-reuse accident."""
    p, q, g, x = key["p"], key["q"], key["g"], key["x"]
    h1 = hash_fn(msg).digest()
    k = k if k is not None else rfc6979_k(x, q, h1, hash_fn)
    r = modexp(g, k, p) % q
    s = modinv(k, q) * (bits2int(h1, q.bit_length()) + x * r) % q
    if r == 0 or s == 0:
        raise ValueError("degenerate signature; pick another k")
    return r, s


def verify(key: dict, msg: bytes, sig: tuple[int, int], hash_fn=hashlib.sha256) -> bool:
    """w = s^-1; u1 = z w, u2 = r w; accept iff (g^u1 y^u2 mod p) mod q = r."""
    p, q, g, y = key["p"], key["q"], key["g"], key["y"]
    r, s = sig
    if not (0 < r < q and 0 < s < q):
        return False
    w = modinv(s, q)
    z = bits2int(hash_fn(msg).digest(), q.bit_length())
    return modexp(g, z * w % q, p) * modexp(y, r * w % q, p) % p % q == r


def nonce_reuse_attack(q: int, z1: int, sig1, z2: int, sig2) -> tuple[int, int]:
    """Two signatures with the same k share r.  From s_i k = z_i + x r:
    k = (z1 - z2) / (s1 - s2), then x = (s1 k - z1) / r, all mod q.
    Returns (k, x).  The (EC)DSA twin of the Schnorr exam question."""
    (r, s1), (r2, s2) = sig1, sig2
    if r != r2:
        raise ValueError("different r: the nonces differ")
    k = (z1 - z2) * modinv(s1 - s2, q) % q
    return k, (s1 * k - z1) * modinv(r, q) % q


if __name__ == "__main__":
    import rfc_vectors                           # the RFC 6979 A.2.2 key, from refs/
    rng.seed(2027)                               # reproducible output; see rng.py
    key, sigs = rfc_vectors.rfc6979_dsa(2048)
    want = next(v for v in sigs if v["hash"] == "SHA-256" and v["msg"] == b"sample")
    k = rfc6979_k(key["x"], key["q"], hashlib.sha256(b"sample").digest())
    print("RFC 6979 A.2.2, SHA-256, 'sample': k matches:", k == want["k"],
          "| (r, s) match:", sign(key, b"sample") == (want["r"], want["s"]))
    print("verifies:", verify(key, b"sample", (want["r"], want["s"])))

    bad_k = 1 + rng.randbelow(key["q"] - 1)      # a broken RNG repeats this k
    m1, m2 = b"pay Alice 10", b"pay Bob 20"
    s1, s2 = sign(key, m1, k=bad_k), sign(key, m2, k=bad_k)
    z = lambda m: bits2int(hashlib.sha256(m).digest(), key["q"].bit_length())
    print("nonce reused -> private key recovered:",
          nonce_reuse_attack(key["q"], z(m1), s1, z(m2), s2)[1] == key["x"])
