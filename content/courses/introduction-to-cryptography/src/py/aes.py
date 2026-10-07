"""AES written out from FIPS 197: key expansion, the round function
(SubBytes, ShiftRows, MixColumns, AddRoundKey) and its inverse.

Primitive: the AES block cipher, a substitution-permutation network and the
strong PRP that every mode of operation in the course is instantiated with.
Note: notes/03-block-ciphers.md (lecture 3); the modes are
notes/06-private-key-encryption.md, the PRP definition notes/05.
Standard: FIPS 197 [S21] sec. 5.1 (Cipher), 5.2 (KeyExpansion), 5.3
(InvCipher), for 128-, 192- and 256-bit keys.  Checked against the key
expansions of appendix A.1-A.3, the appendix B worked example (including the
state at the start of round 10), the SP 800-38A appendix F.1 ECB vectors for
all three key sizes [S25], and the `cryptography` package's AES.  The S-box
comes from `block_ciphers.aes_sbox`, which derives it from sec. 5.1.1.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
Correct but slow, and table lookups indexed by secret bytes are exactly the
cache-timing leak that real implementations avoid (hardware AES-NI, or
bitsliced code).  `PureAES` has the same interface as `private_key.AESBlock`
so the modes can run on either.
"""
from __future__ import annotations

from block_ciphers import aes_inv_sbox, aes_sbox, gmul, xtime

SBOX, INV_SBOX = aes_sbox(), aes_inv_sbox()


def key_expansion(key: bytes) -> list[bytes]:
    """FIPS 197 sec. 5.2: Nk = 4, 6, 8 key words give Nr = 10, 12, 14 rounds
    and 4 (Nr + 1) round-key words.  Every Nk-th word is RotWord, SubWord and
    xor Rcon; AES-256 adds a SubWord halfway through each Nk-word cycle."""
    nk = len(key) // 4
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 16, 24 or 32 bytes")
    nr = nk + 6
    w = [key[4 * i:4 * i + 4] for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        temp = w[i - 1]
        if i % nk == 0:
            temp = bytes(SBOX[b] for b in temp[1:] + temp[:1])       # SubWord(RotWord)
            temp = bytes([temp[0] ^ rcon]) + temp[1:]
            rcon = xtime(rcon)                                      # Rcon = x^(i/Nk - 1)
        elif nk > 6 and i % nk == 4:
            temp = bytes(SBOX[b] for b in temp)
        w.append(bytes(a ^ b for a, b in zip(w[i - nk], temp)))
    return w


# The state is 16 bytes in column-major order, s[r + 4c] (FIPS 197 sec. 3.4).
def _add_round_key(s: list[int], w: list[bytes], rnd: int) -> list[int]:
    rk = b"".join(w[4 * rnd:4 * rnd + 4])
    return [a ^ b for a, b in zip(s, rk)]


def _shift_rows(s: list[int], sign: int = 1) -> list[int]:
    """Row r rotates left by r (right by r for the inverse)."""
    return [s[r + 4 * ((c + sign * r) % 4)] for c in range(4) for r in range(4)]


def _mix_columns(s: list[int], coeffs=(2, 3, 1, 1)) -> list[int]:
    """Each column times a fixed polynomial over GF(2^8): the circulant
    matrix (2 3 1 1), or (14 11 13 9) for InvMixColumns."""
    out = []
    for c in range(4):
        col = s[4 * c:4 * c + 4]
        for r in range(4):
            v = 0
            for j in range(4):
                v ^= gmul(coeffs[(j - r) % 4], col[j])
            out.append(v)
    return out


def encrypt_block(block: bytes, w: list[bytes], trace: list | None = None) -> bytes:
    """FIPS 197 sec. 5.1, Cipher(): initial AddRoundKey, Nr - 1 full rounds,
    a final round without MixColumns.  `trace` collects the state at the
    start of each round, as appendix B prints it."""
    nr = len(w) // 4 - 1
    s = _add_round_key(list(block), w, 0)
    for rnd in range(1, nr + 1):
        if trace is not None:
            trace.append(bytes(s))
        s = _shift_rows([SBOX[b] for b in s])
        if rnd != nr:
            s = _mix_columns(s)
        s = _add_round_key(s, w, rnd)
    return bytes(s)


def decrypt_block(block: bytes, w: list[bytes]) -> bytes:
    """FIPS 197 sec. 5.3, InvCipher(): the rounds in reverse, each step
    replaced by its inverse."""
    nr = len(w) // 4 - 1
    s = _add_round_key(list(block), w, nr)
    for rnd in range(nr - 1, -1, -1):
        s = [INV_SBOX[b] for b in _shift_rows(s, -1)]
        s = _add_round_key(s, w, rnd)
        if rnd != 0:
            s = _mix_columns(s, (14, 11, 13, 9))
    return bytes(s)


class PureAES:
    """Drop-in for `private_key.AESBlock`, with no library underneath."""
    block_size = 16

    def __init__(self, key: bytes):
        self._w = key_expansion(key)

    def encrypt_block(self, block: bytes) -> bytes:
        return encrypt_block(block, self._w)

    def decrypt_block(self, block: bytes) -> bytes:
        return decrypt_block(block, self._w)


if __name__ == "__main__":
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    plain = bytes.fromhex("3243f6a8885a308d313198a2e0370734")
    w = key_expansion(key)
    print("FIPS 197 A.1, round key 10 (w40..w43):", b"".join(w[40:44]).hex())
    trace: list[bytes] = []
    ct = encrypt_block(plain, w, trace)
    print("FIPS 197 B, start of round 1: ", trace[0].hex())
    print("FIPS 197 B, start of round 10:", trace[9].hex())
    print("FIPS 197 B, output:           ", ct.hex(), "(3925841d02dc09fbdc118597196a0b32)")
    print("decrypts back:", decrypt_block(ct, w) == plain)
