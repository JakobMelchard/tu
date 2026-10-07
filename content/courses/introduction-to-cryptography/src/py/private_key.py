"""Private-key encryption: a PRF-based CPA-secure scheme, a toy Feistel PRP,
AES via `cryptography`, ECB/CBC/CTR modes, the ECB leakage demo and the
CBC padding-oracle attack (a classic classroom illustration of why an
unauthenticated CCA adversary breaks CBC).

Primitive: EAV/CPA/CCA-secure private-key encryption; PRPs; modes of
operation; PKCS #7 padding and the padding-oracle CCA attack.
Note: notes/06-private-key-encryption.md (lectures 6 and 7); the Feistel
PRP is notes/05-pseudorandomness.md.
Standard: ECB, CBC and CTR are NIST SP 800-38A sec. 6.1, 6.2, 6.5 [S25]
(its appendix F vectors are replayed in test_standard_vectors.py, and
`ctr_keystream_from` is the sec. 6.5 / appendix B.1 counter); `AESBlock` is
FIPS 197 AES [S21] from the `cryptography` package, with `aes.PureAES` as
the from-scratch twin.  The PRF scheme is Katz-Lindell Constr. 3.28 [S10];
the padding oracle is Vaudenay's [S48]; PKCS #7 padding is RFC 5652
sec. 6.3 (not vendored).

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
The Feistel PRP has an 8-byte block and a SHA-256 round function; AES is
used only through the `cryptography` package as a real-world cross-check.
Nothing here is constant-time or hardened; it exists to make the security
definitions and their failures concrete.
"""
from __future__ import annotations

import hashlib
from typing import Callable

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import rng
from prg import BLOCK as PRF_LEN, toy_prf


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


# ---------------------------------------------- PRF-based CPA-secure scheme
def prf_encrypt(key: bytes, msg: bytes) -> tuple[bytes, bytes]:
    """Enc_k(m) = (r, F_k(r) xor m) with r uniform. Randomised, so encrypting
    the same m twice gives different ciphertexts (necessary for CPA)."""
    if len(msg) != PRF_LEN:
        raise ValueError(f"fixed-length scheme: message must be {PRF_LEN} bytes")
    r = rng.token_bytes(PRF_LEN)
    return r, xor(toy_prf(key, r), msg)


def prf_decrypt(key: bytes, ct: tuple[bytes, bytes]) -> bytes:
    r, c = ct
    return xor(toy_prf(key, r), c)


# ---------------------------------------------------------- block ciphers
class FeistelPRP:
    """4-round Feistel network on 8-byte blocks with round function
    f_i(x) = SHA-256(k || i || x)[:4]. Luby-Rackoff: 3 rounds give a PRP,
    4 rounds a strong PRP, *if* the round functions are PRFs."""
    block_size = 8
    rounds = 4

    def __init__(self, key: bytes):
        self.key = key

    def _f(self, i: int, half: bytes) -> bytes:
        return hashlib.sha256(self.key + bytes([i]) + half).digest()[:4]

    def encrypt_block(self, block: bytes) -> bytes:
        left, right = block[:4], block[4:]
        for i in range(self.rounds):            # (L, R) -> (R, L xor f_i(R))
            left, right = right, xor(left, self._f(i, right))
        return left + right

    def decrypt_block(self, block: bytes) -> bytes:
        left, right = block[:4], block[4:]
        for i in reversed(range(self.rounds)):  # undo one round at a time
            left, right = xor(right, self._f(i, left)), left
        return left + right


class AESBlock:
    """Raw AES block permutation (single-block ECB) from the cryptography
    package. Used to cross-check the modes against a real strong PRP."""
    block_size = 16

    def __init__(self, key: bytes):
        self._c = Cipher(algorithms.AES(key), modes.ECB())

    def encrypt_block(self, block: bytes) -> bytes:
        e = self._c.encryptor()
        return e.update(block) + e.finalize()

    def decrypt_block(self, block: bytes) -> bytes:
        d = self._c.decryptor()
        return d.update(block) + d.finalize()


# -------------------------------------------------------------- padding
def pad(msg: bytes, bs: int) -> bytes:
    """PKCS#7: append n bytes of value n, 1 <= n <= bs (always at least one)."""
    n = bs - len(msg) % bs
    return msg + bytes([n]) * n


def unpad(msg: bytes, bs: int) -> bytes:
    if not msg or len(msg) % bs:
        raise ValueError("bad padding")
    n = msg[-1]
    if not 1 <= n <= bs or msg[-n:] != bytes([n]) * n:
        raise ValueError("bad padding")
    return msg[:-n]


def _blocks(data: bytes, bs: int) -> list[bytes]:
    return [data[i:i + bs] for i in range(0, len(data), bs)]


# ----------------------------------------------------------------- modes
def ecb_encrypt(cipher, msg: bytes) -> bytes:
    """Deterministic, stateless: equal plaintext blocks give equal ciphertext
    blocks, so ECB is not even EAV-secure."""
    bs = cipher.block_size
    return b"".join(cipher.encrypt_block(b) for b in _blocks(pad(msg, bs), bs))


def ecb_decrypt(cipher, ct: bytes) -> bytes:
    bs = cipher.block_size
    return unpad(b"".join(cipher.decrypt_block(b) for b in _blocks(ct, bs)), bs)


def cbc_encrypt(cipher, msg: bytes, iv: bytes | None = None) -> bytes:
    """c_i = E_k(m_i xor c_{i-1}), c_0 = IV uniform. CPA-secure with random IV."""
    bs = cipher.block_size
    prev = iv if iv is not None else rng.token_bytes(bs)
    out = [prev]
    for block in _blocks(pad(msg, bs), bs):
        prev = cipher.encrypt_block(xor(block, prev))
        out.append(prev)
    return b"".join(out)


def cbc_decrypt_raw(cipher, ct: bytes) -> bytes:
    """m_i = D_k(c_i) xor c_{i-1}; returns the still-padded plaintext."""
    bs = cipher.block_size
    blocks = _blocks(ct, bs)
    return b"".join(xor(cipher.decrypt_block(c), p) for p, c in zip(blocks, blocks[1:]))


def cbc_decrypt(cipher, ct: bytes) -> bytes:
    return unpad(cbc_decrypt_raw(cipher, ct), cipher.block_size)


def ctr_keystream(cipher, nonce: bytes, nblocks: int) -> bytes:
    """Keystream block i = E_k(nonce || counter). Only the forward direction
    of the cipher is used, so CTR turns any PRF into an encryption scheme and
    needs no padding."""
    bs = cipher.block_size
    ctr_len = bs - len(nonce)
    return b"".join(cipher.encrypt_block(nonce + i.to_bytes(ctr_len, "big")) for i in range(nblocks))


def ctr_keystream_from(cipher, counter_block: bytes, nblocks: int) -> bytes:
    """CTR keystream in the form NIST SP 800-38A sec. 6.5 specifies it [S25]:
    the counter is the *whole* block, incremented mod 2^(block bits) by the
    standard incrementing function of appendix B.1. `ctr_keystream` above
    uses the commoner nonce||counter split, in which the nonce prefix is
    never touched by the carry; the two agree only while the counter does
    not overflow into the nonce."""
    bs = cipher.block_size
    ctr = int.from_bytes(counter_block, "big")
    mod = 1 << (8 * bs)
    return b"".join(cipher.encrypt_block(((ctr + i) % mod).to_bytes(bs, "big"))
                    for i in range(nblocks))


def ctr_encrypt(cipher, msg: bytes, nonce: bytes | None = None) -> bytes:
    """Ciphertext = nonce || m xor keystream.  The nonce is half a block,
    which is where `ctr_decrypt` splits it off."""
    bs = cipher.block_size
    nonce = nonce if nonce is not None else rng.token_bytes(bs // 2)
    if len(nonce) != bs // 2:
        raise ValueError(f"nonce must be {bs // 2} bytes")
    ks = ctr_keystream(cipher, nonce, (len(msg) + bs - 1) // bs)
    return nonce + xor(msg, ks[:len(msg)])


def ctr_decrypt(cipher, ct: bytes) -> bytes:
    half = cipher.block_size // 2
    nonce, body = ct[:half], ct[half:]
    ks = ctr_keystream(cipher, nonce, (len(body) + cipher.block_size - 1) // cipher.block_size)
    return xor(body, ks[:len(body)])           # XOR keystream is its own inverse


# ----------------------------------------------------------- ECB leakage
def structured_image(width: int = 16, height: int = 12, bs: int = 16) -> bytes:
    """A 'bitmap': each pixel is one block, background is 0x00-blocks, a
    filled rectangle is 0xff-blocks. Under ECB the shape survives encryption
    (the 'ECB penguin')."""
    out = []
    for y in range(height):
        for x in range(width):
            inside = 3 <= x < width - 3 and 3 <= y < height - 3
            out.append((b"\xff" if inside else b"\x00") * bs)
    return b"".join(out)


def block_pattern(ct: bytes, bs: int, width: int) -> list[str]:
    """Label each ciphertext block by first occurrence ('a', 'b', ...) and
    render as rows: identical blocks share a letter, so a deterministic mode
    reveals the plaintext structure while a randomised one does not."""
    ids: dict[bytes, str] = {}
    labels = [ids.setdefault(b, chr(ord("a") + len(ids)) if len(ids) < 26 else ".") for b in _blocks(ct, bs)]
    return ["".join(labels[i:i + width]) for i in range(0, len(labels), width)]


# ------------------------------------------------------ padding oracle
def make_padding_oracle(cipher) -> Callable[[bytes], bool]:
    """Models a server that decrypts a CBC ciphertext and only reveals whether
    the PKCS#7 padding was valid. That single leaked bit is the whole
    vulnerability the attack below exploits."""
    def oracle(ct: bytes) -> bool:
        try:
            unpad(cbc_decrypt_raw(cipher, ct), cipher.block_size)
            return True
        except ValueError:
            return False
    return oracle


def padding_oracle_attack(oracle: Callable[[bytes], bool], ct: bytes, bs: int) -> bytes:
    """Recover the plaintext from CBC ciphertext using only the padding
    oracle. For target block c_i we tamper with the preceding block c_{i-1}:
    since m_i = D_k(c_i) xor c_{i-1}, adjusting c_{i-1} byte j to force valid
    padding of value p reveals D_k(c_i)[j] = c'_{i-1}[j] xor p, hence the
    real plaintext byte m_i[j] = D_k(c_i)[j] xor c_{i-1}[j]."""
    blocks = _blocks(ct, bs)
    recovered = bytearray()
    for b in range(1, len(blocks)):                 # decrypt block b using block b-1
        prev, target = blocks[b - 1], blocks[b]
        inter = bytearray(bs)                        # inter[j] = D_k(target)[j]
        for pad_val in range(1, bs + 1):
            forged = bytearray(rng.token_bytes(bs))
            j = bs - pad_val
            for k in range(j + 1, bs):               # set already-known tail to pad_val
                forged[k] = inter[k] ^ pad_val
            for guess in range(256):
                forged[j] = guess
                if oracle(bytes(forged) + target):
                    # guard against the false positive at the very first byte
                    if pad_val == 1:
                        forged[j - 1] ^= 1 if j > 0 else 0
                        if j > 0 and not oracle(bytes(forged) + target):
                            continue
                    inter[j] = guess ^ pad_val
                    break
            else:
                raise RuntimeError("oracle gave no valid padding; attack failed")
        recovered += xor(bytes(inter), prev)
    return unpad(bytes(recovered), bs)


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    key = rng.token_bytes(16)

    # PRF-based CPA scheme: same message, two different ciphertexts
    m = b"32-byte block for the toy PRF!!!"
    print("PRF scheme roundtrip:", prf_decrypt(key, prf_encrypt(key, m)) == m)
    print("randomised?", prf_encrypt(key, m) != prf_encrypt(key, m))

    # Feistel PRP is a permutation
    f = FeistelPRP(key)
    blk = b"12345678"
    print("Feistel roundtrip:", f.decrypt_block(f.encrypt_block(blk)) == blk)

    # AES cross-checks all modes
    aes = AESBlock(key)
    msg = b"the modes of operation matter a lot for security"
    for enc, dec, name in [(ecb_encrypt, ecb_decrypt, "ECB"),
                           (cbc_encrypt, cbc_decrypt, "CBC"),
                           (ctr_encrypt, ctr_decrypt, "CTR")]:
        print(f"AES-{name} roundtrip:", dec(aes, enc(aes, msg)) == msg)

    # ECB leakage: structure survives; CBC hides it
    img = structured_image()
    print("\nECB ciphertext block map (structure leaks):")
    print("\n".join(block_pattern(ecb_encrypt(aes, img), 16, 16)))
    print("\nCBC ciphertext block map (no structure):")
    print("\n".join(block_pattern(cbc_encrypt(aes, img)[16:], 16, 16)))

    # Padding oracle attack recovers the plaintext from the oracle alone
    secret = b"attack at dawn, bring the manuals"
    ct = cbc_encrypt(aes, secret)
    recovered = padding_oracle_attack(make_padding_oracle(aes), ct, 16)
    print("\npadding oracle recovered:", recovered)
    print("matches plaintext:", recovered == secret)
