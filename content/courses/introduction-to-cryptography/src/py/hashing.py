"""Hash functions: a toy compression function, the Merkle-Damgard transform,
SHA-256 written out from FIPS 180-4, the length-extension attack on both,
and a birthday collision search against a truncated SHA-256.

Primitive: collision-resistant hash functions and the Merkle-Damgard
construction; the attacks are length extension and the birthday bound.
Note: notes/08-hash-functions.md (lecture 9); the MAC consequence is
notes/07-macs-and-ae.md.
Standard: `sha256` implements FIPS 180-4 [S28] sec. 4.1.2 (functions),
4.2.2 (constants), 5.1.1 (padding), 5.3.3 (initial value) and 6.2.2
(computation).  Its constants are *derived* from their sec. 4.2.2 / 5.3.3
definition (cube and square roots of the first primes) rather than copied,
and the output is checked against the RFC 6234 sec. 8.5 test patterns [S23]
and against `hashlib`.  The toy `merkle_damgard` uses the same padding rule
with an 8-byte block.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
The toy compression function is small and NOT collision resistant; it only
illustrates the Merkle-Damgard structure.  The pure SHA-256 is correct but
slow and exists to show *why* H(k || m) is not a MAC: its output is the
full internal state, so anyone can keep hashing from it.
"""
from __future__ import annotations

import hashlib
import math

import rng

# Merkle-Damgard parameters for the toy hash.
DIGEST = 4          # bytes of chaining value / output
BLOCK = 8           # bytes per message block


def compress(state: bytes, block: bytes) -> bytes:
    """Toy compression function h: {0,1}^32 x {0,1}^64 -> {0,1}^32.
    Built from SHA-256 truncated to 4 bytes. Collision resistance of the
    overall hash reduces to collision resistance of this function (that is
    the Merkle-Damgard theorem); this toy version is easy to break, which is
    the point of the birthday demo."""
    return hashlib.sha256(state + block).digest()[:DIGEST]


def _pad(msg_len: int, block: int = BLOCK) -> bytes:
    """The padding that follows a `msg_len`-byte message: 0x80, zeros, then
    the 64-bit big-endian bit length, up to a multiple of `block` bytes.
    FIPS 180-4 sec. 5.1.1 with block = 64 is SHA-256's rule.  Encoding the
    length is what makes Merkle-Damgard collision resistant given a
    collision-resistant compression function."""
    zeros = (block - (msg_len + 1 + 8) % block) % block
    return b"\x80" + b"\x00" * zeros + (8 * msg_len).to_bytes(8, "big")


def merkle_damgard(msg: bytes, iv: bytes = b"\x00" * DIGEST) -> bytes:
    """H(m): pad, then chain the compression function block by block."""
    state = iv
    padded = msg + _pad(len(msg))
    for i in range(0, len(padded), BLOCK):
        state = compress(state, padded[i:i + BLOCK])
    return state


def length_extension(hash_of_secret: bytes, orig_len: int, suffix: bytes) -> tuple[bytes, bytes]:
    """Given H(secret) and len(secret) but NOT the secret, forge
    H(secret || pad(secret) || suffix). The published digest is exactly the
    chaining state after absorbing secret||padding, so we resume the
    Merkle-Damgard iteration from it. This is why naive MAC = H(key || m) is
    broken and HMAC exists.

    Returns (forged_digest, glue_padding) where the attacker-known extended
    message is  original_padding_glue || suffix  appended to the secret."""
    glue = _pad(orig_len)
    prefix_len = orig_len + len(glue)
    ext = suffix + _pad(prefix_len + len(suffix))   # length field counts the prefix
    state = hash_of_secret
    for i in range(0, len(ext), BLOCK):
        state = compress(state, ext[i:i + BLOCK])
    return state, glue


# ------------------------------------------------------ SHA-256, FIPS 180-4
def _first_primes(n: int) -> list[int]:
    out, c = [], 2
    while len(out) < n:
        if all(c % p for p in out if p * p <= c):
            out.append(c)
        c += 1
    return out


def _icbrt(x: int) -> int:
    """floor(x^(1/3)) exactly, by bisection."""
    lo, hi = 0, 1 << (x.bit_length() // 3 + 1)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if mid ** 3 <= x else (lo, mid - 1)
    return lo


# sec. 4.2.2: first 32 bits of the fractional parts of the cube roots of the
# first 64 primes; sec. 5.3.3: the same for square roots of the first 8.
# frac(p^(1/3)) * 2^32 = frac of cbrt(p * 2^96), so integer roots are exact.
SHA256_K = [_icbrt(p << 96) & 0xFFFFFFFF for p in _first_primes(64)]
SHA256_H0 = [math.isqrt(p << 64) & 0xFFFFFFFF for p in _first_primes(8)]
_M32 = 0xFFFFFFFF


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & _M32


def sha256_compress(state: list[int], block: bytes) -> list[int]:
    """One application of the compression function, FIPS 180-4 sec. 6.2.2."""
    w = [int.from_bytes(block[4 * t:4 * t + 4], "big") for t in range(16)]
    for t in range(16, 64):                       # message schedule
        s0 = _rotr(w[t - 15], 7) ^ _rotr(w[t - 15], 18) ^ (w[t - 15] >> 3)
        s1 = _rotr(w[t - 2], 17) ^ _rotr(w[t - 2], 19) ^ (w[t - 2] >> 10)
        w.append((w[t - 16] + s0 + w[t - 7] + s1) & _M32)
    a, b, c, d, e, f, g, h = state
    for t in range(64):
        t1 = (h + (_rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25))
              + ((e & f) ^ (~e & g)) + SHA256_K[t] + w[t]) & _M32   # Sigma1, Ch
        t2 = ((_rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22))
              + ((a & b) ^ (a & c) ^ (b & c))) & _M32               # Sigma0, Maj
        a, b, c, d, e, f, g, h = (t1 + t2) & _M32, a, b, c, (d + t1) & _M32, e, f, g
    return [(x + y) & _M32 for x, y in zip(state, (a, b, c, d, e, f, g, h))]


def sha256(msg: bytes, state: list[int] | None = None, prefix_len: int = 0) -> bytes:
    """SHA-256(msg).  With `state` and `prefix_len` it instead *resumes* from
    a chaining value after `prefix_len` already-absorbed bytes, which is all
    a length-extension attacker needs."""
    state = list(SHA256_H0 if state is None else state)
    padded = msg + _pad(prefix_len + len(msg), 64)
    for i in range(0, len(padded), 64):
        state = sha256_compress(state, padded[i:i + 64])
    return b"".join(x.to_bytes(4, "big") for x in state)


def sha256_length_extension(digest: bytes, secret_len: int,
                            known: bytes, suffix: bytes) -> tuple[bytes, bytes]:
    """Forge SHA-256(secret || known || glue || suffix) from the published
    SHA-256(secret || known), knowing only len(secret).  Returns
    (forged digest, known || glue || suffix): the message the forged tag is
    valid for, without the secret prefix."""
    total = secret_len + len(known)
    glue = _pad(total, 64)
    state = [int.from_bytes(digest[4 * i:4 * i + 4], "big") for i in range(8)]
    return sha256(suffix, state, total + len(glue)), known + glue + suffix


# ------------------------------------------------------------ birthday bound
def birthday_attack(bits: int) -> tuple[bytes, bytes, int]:
    """Find two distinct inputs with the same `bits`-bit truncated SHA-256.
    Expected work ~ 2^{bits/2} by the birthday bound, vastly less than the
    2^{bits} of a brute-force preimage search."""
    nbytes = (bits + 7) // 8
    mask = (1 << bits) - 1

    def trunc(x: bytes) -> int:
        return int.from_bytes(hashlib.sha256(x).digest()[:nbytes], "big") & mask

    seen: dict[int, bytes] = {}
    tries = 0
    while True:
        tries += 1
        x = rng.token_bytes(16)
        d = trunc(x)
        if d in seen and seen[d] != x:
            return seen[d], x, tries
        seen[d] = x


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    print("toy hash of b'hello':", merkle_damgard(b"hello").hex())

    # Length extension against the toy H(secret)
    secret = b"topsecretkey"
    forged, glue = length_extension(merkle_damgard(secret), len(secret), b"&admin=true")
    print("toy length extension forges the real digest:",
          forged == merkle_damgard(secret + glue + b"&admin=true"))

    # SHA-256 from FIPS 180-4, and the same attack on the real thing
    print("\nSHA-256('abc') =", sha256(b"abc").hex())
    print("matches hashlib:", sha256(b"abc") == hashlib.sha256(b"abc").digest())
    tag = hashlib.sha256(secret + b"user=alice").digest()      # MAC = H(k || m)
    forged, msg = sha256_length_extension(tag, len(secret), b"user=alice", b"&admin=true")
    print("SHA-256 length extension: forged tag valid for", msg[-11:], "->",
          forged == hashlib.sha256(secret + msg).digest())

    # Birthday attack on 32-bit truncated SHA-256
    a, b, tries = birthday_attack(32)
    dig = lambda x: hashlib.sha256(x).digest()[:4]
    print(f"\nbirthday collision on 32 bits after {tries} tries (~2^16 = {2**16} expected):")
    print(f"  H({a.hex()}) = {dig(a).hex()}")
    print(f"  H({b.hex()}) = {dig(b).hex()}")
    print("  collide:", dig(a) == dig(b), "| distinct inputs:", a != b)
