"""Block-cipher internals -- lecture 3 of the course (Andreeva).

Three things the lecture spends its time on and that the rest of the code
takes for granted:

  * what an S-box actually *is*.  `aes_sbox` derives the AES substitution
    table from its FIPS 197 sec. 5.1.1 definition (inverse in GF(2^8), then
    a fixed affine map) instead of hard-coding it, so the table in FIPS 197
    Table 4 becomes a test rather than a magic constant [S21].
  * confusion and diffusion (Shannon).  `avalanche` measures diffusion:
    flipping one input bit of AES should flip about half the output bits.
  * why key length is not the whole story.  `meet_in_the_middle` breaks
    double encryption in ~2 * 2^k work instead of 2^(2k), which is why 2DES
    was never adopted.  Three-key 3DES has 168 key bits and 112 bits of
    security; two-key 3DES has 112 key bits and NIST rates it at 80 -- and
    SP 800-57 has deprecated 3TDEA outright [S27].

Primitive: block ciphers as keyed permutations; SPN and Feistel structure;
multiple encryption.
Note: notes/03-block-ciphers.md (lecture 3).
Standard: GF(2^8) arithmetic and the S-box are FIPS 197 sec. 4 and 5.1.1
[S21], checked against its worked examples and all 256 bytes of Table 4;
the full cipher built on them is `aes.py`.  The 3DES and key-length figures
are SP 800-57 Part 1 [S27].  `ToyCipher` and the meet-in-the-middle attack
are textbook (Katz-Lindell sec. 7.2 [S10]) with no standard.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
`ToyCipher` has a deliberately tiny key so the attacks finish in a second;
that makes it a teaching object, not a cipher.
"""
from __future__ import annotations

import hashlib

from private_key import AESBlock, xor

AES_POLY = 0x11B          # m(x) = x^8 + x^4 + x^3 + x + 1, FIPS 197 sec. 4.1
AFFINE_C = 0x63           # the constant of FIPS 197 eq. (5.2)


# ------------------------------------------------- GF(2^8), FIPS 197 sec. 4
def xtime(a: int) -> int:
    """Multiplication by x, reducing mod m(x) (FIPS 197 sec. 4.2)."""
    a <<= 1
    return a ^ AES_POLY if a & 0x100 else a


def gmul(a: int, b: int) -> int:
    """Product in GF(2^8): shift-and-add with the carry-less add being XOR."""
    out = 0
    while b:
        if b & 1:
            out ^= a
        a = xtime(a)
        b >>= 1
    return out


def ginv(a: int) -> int:
    """Multiplicative inverse in GF(2^8); 0 is mapped to 0 by convention
    (FIPS 197 sec. 4.4).  The group of units has order 255, so by Lagrange
    a^254 = a^-1."""
    if a == 0:
        return 0
    out = 1
    for _ in range(254):
        out = gmul(out, a)
    return out


def _affine(b: int) -> int:
    """FIPS 197 eq. (5.2): b'_i = b_i ^ b_(i+4) ^ b_(i+5) ^ b_(i+6) ^ b_(i+7)
    ^ c_i, indices mod 8, c = 0x63.  Affine over GF(2), and it is there to
    stop the S-box from having a simple algebraic description."""
    out = 0
    for i in range(8):
        bit = ((b >> i) ^ (b >> ((i + 4) % 8)) ^ (b >> ((i + 5) % 8))
               ^ (b >> ((i + 6) % 8)) ^ (b >> ((i + 7) % 8))
               ^ (AFFINE_C >> i)) & 1
        out |= bit << i
    return out


def aes_sbox() -> list[int]:
    """The 256-entry AES S-box, derived rather than copied."""
    return [_affine(ginv(a)) for a in range(256)]


def aes_inv_sbox() -> list[int]:
    inv = [0] * 256
    for a, s in enumerate(aes_sbox()):
        inv[s] = a
    return inv


# ------------------------------------------------- confusion and diffusion
def avalanche(encrypt, block: bytes, trials: int | None = None) -> float:
    """Average fraction of output bits that change when one input bit is
    flipped.  Shannon's diffusion requirement says this should sit at 1/2:
    a single-bit change must spread over the whole block.  Compare a
    one-round Feistel network, where the left half of the output is a
    verbatim copy of the right half of the input (final exam 2 Feb 2021,
    question 1a [S15])."""
    base = encrypt(block)
    nbits = 8 * len(block)
    positions = range(nbits if trials is None else trials)
    total = 0
    for i in positions:
        flipped = bytearray(block)
        flipped[i // 8] ^= 1 << (i % 8)
        diff = xor(base, encrypt(bytes(flipped)))
        total += sum(bin(byte).count("1") for byte in diff)
    n = len(list(positions))
    return total / (n * 8 * len(base))


# --------------------------------------------------- a tiny keyed cipher
class ToyCipher:
    """Four-round Feistel on 8-byte blocks with a `key_bits`-bit key, so the
    key space can be searched exhaustively in a test.  Same shape as DES
    (Feistel, 64-bit block) with the key shortened from 56 bits to something
    a laptop can enumerate."""
    block_size = 8
    rounds = 4

    def __init__(self, key: int, key_bits: int = 16):
        self.key = key
        self.key_bits = key_bits
        self._kb = key.to_bytes((key_bits + 7) // 8, "big")

    def _f(self, i: int, half: bytes) -> bytes:
        return hashlib.sha256(self._kb + bytes([i]) + half).digest()[:4]

    def encrypt_block(self, block: bytes) -> bytes:
        left, right = block[:4], block[4:]
        for i in range(self.rounds):
            left, right = right, xor(left, self._f(i, right))
        return left + right

    def decrypt_block(self, block: bytes) -> bytes:
        left, right = block[:4], block[4:]
        for i in reversed(range(self.rounds)):
            left, right = xor(right, self._f(i, left)), left
        return left + right


def double_encrypt(k1: int, k2: int, block: bytes, key_bits: int = 16) -> bytes:
    """E'_(k1,k2)(x) = E_k2(E_k1(x)) -- the "obvious" way to double the key
    length.  It does not double the security."""
    return ToyCipher(k2, key_bits).encrypt_block(
        ToyCipher(k1, key_bits).encrypt_block(block))


def triple_encrypt_ede(k1: int, k2: int, k3: int, block: bytes,
                       key_bits: int = 16) -> bytes:
    """E-D-E, as in 3DES.  With k1 = k2 = k3 this degenerates to single
    encryption, which is how 3DES stayed backwards compatible with DES.
    Meet-in-the-middle still applies, so three-key 3DES buys 112 bits of
    security out of 168 key bits, and NIST rates the two-key variant at 80
    and deprecates both [S27]."""
    c = ToyCipher(k1, key_bits).encrypt_block(block)
    c = ToyCipher(k2, key_bits).decrypt_block(c)
    return ToyCipher(k3, key_bits).encrypt_block(c)


def brute_force(plain: bytes, ct: bytes, key_bits: int = 16) -> tuple[int, int]:
    """Exhaustive key search against single encryption.  Returns (key, work)
    where work counts cipher evaluations: 2^k in the worst case."""
    for k in range(1 << key_bits):
        if ToyCipher(k, key_bits).encrypt_block(plain) == ct:
            return k, k + 1
    raise ValueError("no key found")


def meet_in_the_middle(plain: bytes, ct: bytes,
                       key_bits: int = 16) -> tuple[list[tuple[int, int]], int]:
    """Break double encryption with ~2 * 2^k evaluations instead of 2^(2k).

    E_k2(E_k1(p)) = c  <=>  E_k1(p) = D_k2(c), so tabulate the left side for
    every k1 (2^k evaluations, 2^k memory) and scan the right side for every
    k2 (2^k more), looking each value up in the table.  A single plaintext/
    ciphertext pair leaves some false positives -- the table has 2^k entries
    in a space of 2^64 blocks -- so a second pair is used to filter.

    Returns (candidate key pairs, work).  This is midterm 3 Dec 2025
    question 1f [S13]: the attack costs roughly the square root of the
    2^(2k) brute force on the double cipher.
    """
    table: dict[bytes, list[int]] = {}
    work = 0
    for k1 in range(1 << key_bits):
        table.setdefault(ToyCipher(k1, key_bits).encrypt_block(plain), []).append(k1)
        work += 1
    found = []
    for k2 in range(1 << key_bits):
        mid = ToyCipher(k2, key_bits).decrypt_block(ct)
        work += 1
        for k1 in table.get(mid, ()):
            found.append((k1, k2))
    return found, work


if __name__ == "__main__":
    sbox = aes_sbox()
    print("AES S-box derived from GF(2^8) inverse + affine map:")
    print("  S(00) =", f"{sbox[0]:02x}", "(FIPS 197 Table 4: 63)")
    print("  S(53) =", f"{sbox[0x53]:02x}", "(FIPS 197 sec. 5.1.1 worked example: ed)")
    print("  bijective:", sorted(sbox) == list(range(256)))

    aes = AESBlock(bytes(range(16)))
    print(f"AES avalanche: {avalanche(aes.encrypt_block, bytes(16)):.3f} "
          f"(Shannon diffusion wants 0.5)")
    one_round = ToyCipher(1234)
    one_round.rounds = 1
    print(f"1-round Feistel avalanche: "
          f"{avalanche(one_round.encrypt_block, bytes(8)):.3f} "
          f"(half the output is a copy of the input)")

    KEY_BITS = 12
    plain, plain2 = b"plaintxt", b"2ndpair!"
    k1, k2 = 0x0ab, 0x7c3
    ct = double_encrypt(k1, k2, plain, KEY_BITS)
    ct2 = double_encrypt(k1, k2, plain2, KEY_BITS)

    cands, work = meet_in_the_middle(plain, ct, KEY_BITS)
    cands = [(a, b) for a, b in cands
             if double_encrypt(a, b, plain2, KEY_BITS) == ct2]
    print(f"double encryption with 2 x {KEY_BITS}-bit keys: "
          f"meet-in-the-middle used {work} evaluations "
          f"(brute force would need 2^{2 * KEY_BITS} = {1 << (2 * KEY_BITS)})")
    print("  recovered:", [(hex(a), hex(b)) for a, b in cands],
          "| true:", (hex(k1), hex(k2)))
