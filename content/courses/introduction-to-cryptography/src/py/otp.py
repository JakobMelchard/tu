"""One-time pad: perfectly secret encryption, and what breaks when a pad is
reused (the "two-time pad" and crib dragging).

Primitive: the one-time pad (Vernam over bits), Katz-Lindell Thm 2.10
[S10].
Note: notes/02-perfect-secrecy.md (lecture 2); its Z_26 twin is
`classical.vernam_encrypt` (note 01), its computational version the stream
cipher of note 06 (`prg.chacha20_encrypt`).
Standard: none; the OTP is a definition, not a standardised algorithm.  The
tests check it against RFC 8439 sec. 2.4.2 [S36], where a ChaCha20
keystream used as the pad must turn the RFC's plaintext into its
ciphertext, and against the exact 2^-8 distribution of Pr[C = c | M = m].

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
The OTP itself is information-theoretically secure, but this module's key
handling (keys as Python bytes, reuse demos) is deliberately unsafe.
"""
from __future__ import annotations

import string

import rng


def xor(a: bytes, b: bytes) -> bytes:
    """Bytewise XOR of equal-length strings (the whole OTP algorithm)."""
    if len(a) != len(b):
        raise ValueError("xor needs equal lengths")
    return bytes(x ^ y for x, y in zip(a, b))


def keygen(n: int) -> bytes:
    """Key = uniform n bytes. Must be as long as the message."""
    return rng.token_bytes(n)


def encrypt(key: bytes, msg: bytes) -> bytes:
    return xor(key, msg)


decrypt = encrypt          # Dec_k(c) = c xor k = m; the pad is an involution


# ---------------------------------------------------------- two-time pad
def two_time_pad_leak(c1: bytes, c2: bytes) -> bytes:
    """If c1 = m1 xor k and c2 = m2 xor k, then c1 xor c2 = m1 xor m2:
    the key cancels and the attacker gets the XOR of the two plaintexts."""
    return xor(c1, c2)


PRINTABLE = set(bytes(string.ascii_letters + string.digits + " .,;:!?'-\"()", "ascii"))


def crib_drag(m1_xor_m2: bytes, crib: bytes) -> list[tuple[int, bytes]]:
    """Slide a guessed plaintext fragment (`crib`) along m1 xor m2. Where the
    crib really occurs in one message, XORing it out reveals the other
    message's bytes at that position; we keep offsets where the result is
    all printable text."""
    hits = []
    for i in range(len(m1_xor_m2) - len(crib) + 1):
        window = m1_xor_m2[i:i + len(crib)]
        other = xor(window, crib)
        if all(b in PRINTABLE for b in other):
            hits.append((i, other))
    return hits


def malleability_demo(c: bytes, delta: bytes) -> bytes:
    """OTP is perfectly secret but not non-malleable: flipping bits of c
    flips the same bits of m. Returns Enc_k(m xor delta) without k."""
    return xor(c, delta)


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    m1 = b"attack the bridge at dawn"
    m2 = b"retreat to the forest now"
    k = keygen(len(m1))
    c1, c2 = encrypt(k, m1), encrypt(k, m2)
    print("c1 =", c1.hex())
    print("dec(c1) =", decrypt(k, c1))
    leak = two_time_pad_leak(c1, c2)
    print("c1 xor c2 = m1 xor m2 =", leak.hex())
    for crib in (b" the ", b"attack"):
        print(f"crib {crib!r} -> candidate positions:")
        for pos, other in crib_drag(leak, crib):
            print(f"  offset {pos:2d}: other message reads {other!r}")
    print("bit-flip: dec(c1 xor delta) =", decrypt(k, malleability_demo(c1, b"\x00" * 7 + xor(b"the", b"our") + b"\x00" * 15)))
