"""Pseudorandom generators and functions: a linear congruential generator
as a *bad* PRG with an explicit distinguisher, PRG stretching, a toy PRF
from a keyed hash, the PRF-to-PRG construction, and ChaCha20 as the real
stream cipher that the pseudo-one-time pad becomes in practice.

Primitive: PRGs and PRFs (Katz-Lindell Def. 3.14, sec. 3.5.1 [S10]) and the
stream cipher Enc_k(m) = G(k) xor m (Thm 3.16).
Note: notes/05-pseudorandomness.md (lecture 5), with the LCG distinguisher
in notes/04-computational-security.md and the stream cipher as
construction 1 of notes/06-private-key-encryption.md.
Standard: `chacha20_block` / `chacha20_encrypt` implement RFC 8439 sec. 2.1-2.4
[S36] and reproduce its sec. 2.3.2 and 2.4.2 test vectors, read from the
vendored RFC, and the `cryptography` package's ChaCha20.  The LCG, the toy
PRF and `stretch` are textbook constructions with no standard.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
The "toy PRF" is SHA-256(key || x); we *assume* it behaves as a PRF for
teaching purposes, and for variable-length x it does not (length extension,
note 08).  ChaCha20 here is correct but slow, unauthenticated (no Poly1305)
and not constant-time.
"""
from __future__ import annotations

import hashlib

import rng


# ------------------------------------------------------------ LCG (bad PRG)
class LCG:
    """x_{i+1} = a*x_i + c mod m. Fine for Monte Carlo, useless as a PRG:
    the state is the output, so the next output is a public function of
    the previous ones."""

    def __init__(self, seed: int, a: int = 1103515245, c: int = 12345, m: int = 2 ** 31):
        self.x, self.a, self.c, self.m = seed % m, a, c, m

    def next(self) -> int:
        self.x = (self.a * self.x + self.c) % self.m
        return self.x

    def stream(self, n: int) -> list[int]:
        return [self.next() for _ in range(n)]


def lcg_distinguisher(outputs: list[int], m: int) -> bool:
    """Distinguisher D for the LCG with *unknown* a, c but known modulus m.
    From x0, x1, x2 solve a = (x2-x1)/(x1-x0), c = x1 - a*x0 (mod m) and
    predict x3. Returns True ("pseudorandom") iff the prediction is right.
    On a truly uniform stream the prediction succeeds with prob ~1/m,
    on LCG output with prob ~1 (when x1-x0 is invertible mod m)."""
    x0, x1, x2, x3 = outputs[:4]
    try:
        a = (x2 - x1) * pow(x1 - x0, -1, m) % m
    except ValueError:               # x1-x0 not invertible; fall back to guess
        return False
    c = (x1 - a * x0) % m
    return (a * x2 + c) % m == x3


def lcg_advantage(trials: int = 200, m: int = 2 ** 31 - 1) -> float:
    """Empirical advantage |Pr[D(G(s))=1] - Pr[D(r)=1]| over `trials` runs.
    m prime makes x1-x0 always invertible, so D is right with prob 1."""
    hits_prg = sum(lcg_distinguisher(LCG(rng.randbelow(m), a=16807, c=0, m=m).stream(4), m)
                   for _ in range(trials))
    hits_rand = sum(lcg_distinguisher([rng.randbelow(m) for _ in range(4)], m)
                    for _ in range(trials))
    return abs(hits_prg - hits_rand) / trials


# ----------------------------------------------------------- toy PRF / PRG
BLOCK = 32   # bytes: output length of the toy PRF


def toy_prf(key: bytes, x: bytes) -> bytes:
    """F_k(x) = SHA-256(k || x), 32-byte output. Keyed hash *modelled* as a
    PRF. (Real designs use HMAC or a block cipher; this is fine for demos.)"""
    return hashlib.sha256(key + x).digest()


def prf_to_prg(seed: bytes, out_len: int) -> bytes:
    """G(s) = F_s(0) || F_s(1) || F_s(2) || ...  truncated to out_len bytes.
    If F is a PRF, G is a PRG: a distinguisher for G is one for F on the
    fixed inputs 0, 1, 2, ..."""
    out = b"".join(toy_prf(seed, i.to_bytes(8, "big")) for i in range((out_len + BLOCK - 1) // BLOCK))
    return out[:out_len]


def prg_one_bit(seed: bytes) -> bytes:
    """A minimal PRG G: {0,1}^n -> {0,1}^{n+1} (expansion by one byte, to
    keep the demo byte-aligned). Used only as the base case of stretching.
    The toy PRF yields BLOCK bytes, so the seed must be shorter than that."""
    if len(seed) >= BLOCK:
        raise ValueError(f"seed must be shorter than {BLOCK} bytes")
    return toy_prf(seed, b"one-bit")[:len(seed) + 1]


def stretch(seed: bytes, out_len: int) -> bytes:
    """From G with 1-bit expansion build any expansion (Katz-Lindell sec. 8,
    background: lecture 13a lists it as not covered [S8]).
      s_0 = s;  (s_i, b_i) = G(s_{i-1});  output b_1 b_2 ... b_l.
    Security by a hybrid argument: hybrid H_j replaces the first j outputs
    with true randomness; H_j and H_{j+1} differ by one application of G."""
    n = len(seed)
    s, out = seed, bytearray()
    for _ in range(out_len):
        block = prg_one_bit(s)
        s, b = block[:n], block[n:]      # new seed and one output symbol
        out += b
    return bytes(out)


def prg_distinguisher_test(prg_output: bytes, sample_fn, trials: int = 500) -> float:
    """Generic sanity harness: a *statistical* test (byte-mean) has ~0
    advantage against a good PRG. `sample_fn()` draws a fresh PRG output of
    len(prg_output) bytes. Returns |mean(prg) - mean(random)|/255."""
    mean_prg = sum(sum(sample_fn()) / len(prg_output) for _ in range(trials)) / trials
    mean_rnd = sum(sum(rng.token_bytes(len(prg_output))) / len(prg_output) for _ in range(trials)) / trials
    return abs(mean_prg - mean_rnd) / 255


# ------------------------------------------------------ ChaCha20, RFC 8439
_M32 = 0xFFFFFFFF


def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & _M32


def _quarter_round(st: list[int], a: int, b: int, c: int, d: int) -> None:
    """RFC 8439 sec. 2.1: add, xor, rotate by 16, 12, 8, 7."""
    for x, y, z, r in ((a, b, d, 16), (c, d, b, 12), (a, b, d, 8), (c, d, b, 7)):
        st[x] = (st[x] + st[y]) & _M32
        st[z] = _rotl(st[z] ^ st[x], r)


def chacha20_block(key: bytes, counter: int, nonce: bytes) -> bytes:
    """RFC 8439 sec. 2.3: a 4x4 state of 32-bit words (constants, 256-bit
    key, 32-bit counter, 96-bit nonce), 20 rounds alternating column and
    diagonal quarter rounds, then the input state is added back so the
    block function cannot be run backwards.  A PRF in (counter, nonce)."""
    words = lambda b: [int.from_bytes(b[i:i + 4], "little") for i in range(0, len(b), 4)]
    init = words(b"expand 32-byte k") + words(key) + [counter & _M32] + words(nonce)
    st = list(init)
    for _ in range(10):
        for q in ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                  (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)):
            _quarter_round(st, *q)
    return b"".join(((x + y) & _M32).to_bytes(4, "little") for x, y in zip(st, init))


def chacha20_encrypt(key: bytes, counter: int, nonce: bytes, msg: bytes) -> bytes:
    """RFC 8439 sec. 2.4: XOR with the keystream block(counter),
    block(counter+1), ...  This is note 06's construction 1 with the PRG
    built as a PRF in counter mode; reusing (key, nonce) is the two-time pad
    of note 02.  Decryption is the same call.  The counter is 32 bits
    (sec. 2.3), so a message that would wrap it is refused: wrapping
    would reuse keystream blocks."""
    if counter + (len(msg) + 63) // 64 > 1 << 32:
        raise ValueError("message too long for the 32-bit block counter")
    stream = b"".join(chacha20_block(key, counter + i, nonce)
                      for i in range((len(msg) + 63) // 64))
    return bytes(m ^ k for m, k in zip(msg, stream))


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    g = LCG(42)
    print("LCG stream:", g.stream(5))
    print(f"LCG distinguisher advantage (prime modulus): {lcg_advantage():.3f}")
    k20, n20 = bytes(range(32)), bytes.fromhex("000000090000004a00000000")
    print("ChaCha20 block, RFC 8439 sec. 2.3.2 inputs:", chacha20_block(k20, 1, n20)[:8].hex(),
          "(RFC: 10f1e7e4d13b5915)")
    seed = rng.token_bytes(16)
    print("PRF-to-PRG 40 bytes:", prf_to_prg(seed, 40).hex())
    print("stretched 1-byte PRG to 20 bytes:", stretch(seed, 20).hex())
    print("byte-mean statistical advantage vs stretch():",
          f"{prg_distinguisher_test(stretch(seed, 64), lambda: stretch(rng.token_bytes(16), 64), 200):.4f}")
