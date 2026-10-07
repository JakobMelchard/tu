"""LWE in code: Regev's bit encryption with its decryption-failure rate
(measured vs. the Gaussian estimate), why the noise is needed (noiseless LWE
falls to Gaussian elimination), and a tiny module-LWE KEM in the shape of
ML-KEM / Kyber: K-PKE with Compress/Decompress, wrapped in the
Fujisaki-Okamoto transform with implicit rejection.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). Regev with
n = 32 is broken by lattice reduction in seconds; the KEM uses N = 16
coefficients instead of 256, schoolbook multiplication instead of the NTT and
none of the FIPS 203 byte encodings, so its outputs do NOT match ML-KEM.
Sources: [S15 sec. 5], [S6 sec. 4.2, 5.2.1], [S16 sec. 4.2.1, 5, 6, Alg. 17-18].
"""
from __future__ import annotations

import hashlib
import math
import secrets

import numpy as np

# --- Regev's cryptosystem [S15 sec. 5] ----------------------------------------

REGEV_N = 32
REGEV_Q = 1031  # prime in [n^2, 2 n^2] as in [S15 sec. 5]
REGEV_M = math.ceil(1.1 * (REGEV_N + 1) * math.log2(REGEV_Q))


def _rng():
    return np.random.default_rng(secrets.randbits(64))


def gaussian_error(size, sigma: float, rng) -> np.ndarray:
    """Rounded continuous Gaussian: the discretisation used in [S15]."""
    return np.rint(rng.normal(0.0, sigma, size)).astype(np.int64)


def regev_keygen(sigma: float, n=REGEV_N, q=REGEV_Q, m=REGEV_M, rng=None):
    rng = rng or _rng()
    s = rng.integers(0, q, n)
    A = rng.integers(0, q, (m, n))
    b = (A @ s + gaussian_error(m, sigma, rng)) % q
    return (A, b), s


def regev_encrypt(pk, bit: int, q=REGEV_Q, rng=None):
    """Sum a random subset S of the public samples; add bit * floor(q/2)."""
    A, b = pk
    rng = rng or _rng()
    S = rng.integers(0, 2, A.shape[0])
    return (S @ A) % q, (S @ b + bit * (q // 2)) % q


def regev_decrypt(s, ct, q=REGEV_Q) -> int:
    """b - <a, s> = sum_{i in S} e_i + bit q/2: closer to 0 or to q/2?"""
    a, c = ct
    d = (c - a @ s) % q
    return int(min(d, q - d) > q // 4)


def failure_rate(sigma: float, trials: int = 4000, n=REGEV_N, q=REGEV_Q, m=REGEV_M, seed=0):
    """Empirical: fraction of wrong decryptions. The accumulated error
    sum_{i in S} e_i has variance ~ (m/2) sigma^2; decryption fails iff it
    leaves (-q/4, q/4). Vectorised over many key pairs."""
    rng = np.random.default_rng(seed)
    errs = gaussian_error((trials, m), sigma, rng)
    S = rng.integers(0, 2, (trials, m))
    tot = (S * errs).sum(axis=1)
    return float(np.mean(np.abs(tot) > q // 4))


def failure_estimate(sigma: float, q=REGEV_Q, m=REGEV_M) -> float:
    """2 Phi(-(q/4) / (sigma sqrt(m/2)))."""
    z = (q / 4) / (sigma * math.sqrt(m / 2))
    return math.erfc(z / math.sqrt(2))


def solve_mod_q(A, b, q=REGEV_Q):
    """Gaussian elimination over Z_q (q prime): recovers s from EXACT
    equations A s = b. With noise the same procedure returns garbage."""
    A = [list(map(int, row)) + [int(bi)] for row, bi in zip(A, b)]
    n = len(A[0]) - 1
    r = 0
    for col in range(n):
        piv = next((i for i in range(r, len(A)) if A[i][col] % q), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][col], -1, q)
        A[r] = [x * inv % q for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][col]:
                f = A[i][col]
                A[i] = [(x - f * y) % q for x, y in zip(A[i], A[r])]
        r += 1
    return np.array([A[i][n] for i in range(n)])


# --- a toy Kyber-shaped module-LWE KEM [S16] ----------------------------------

Q, N, K_DIM, ETA1, ETA2, DU, DV = 3329, 16, 2, 3, 2, 10, 4   # ML-KEM-512 minus N


def compress(x, d):
    """Compress_d(x) = round((2^d / q) x) mod 2^d, rounding half up [S16 (4.7)]."""
    return ((np.asarray(x) * (1 << (d + 1)) + Q) // (2 * Q)) % (1 << d)


def decompress(y, d):
    """Decompress_d(y) = round((q / 2^d) y) [S16 (4.8)]."""
    return (np.asarray(y) * 2 * Q + (1 << d)) // (1 << (d + 1))


def polymul(a, b):
    """Product in Z_q[X]/(X^N + 1): negacyclic convolution."""
    full = np.convolve(a, b)
    out = full[:N].copy()
    out[: len(full) - N] -= full[N:]
    return out % Q


def matvec(M, v):   # M: k x k polys, v: k polys
    return np.array([sum(polymul(M[i][j], v[j]) for j in range(len(v))) % Q for i in range(len(M))])


def dotp(u, v):
    return sum(polymul(a, b) for a, b in zip(u, v)) % Q


def _xof(seed: bytes, n_bytes: int) -> bytes:
    return hashlib.shake_256(seed).digest(n_bytes)


def cbd(seed: bytes, eta: int, count: int):
    """Centred binomial: sum of eta bits minus sum of eta bits, per coefficient."""
    bits = np.unpackbits(np.frombuffer(_xof(seed, count * N * 2 * eta // 8 + 1), np.uint8))
    bits = bits[: count * N * 2 * eta].reshape(count, N, 2, eta).sum(axis=3)
    return (bits[:, :, 0] - bits[:, :, 1]).astype(np.int64)


def gen_matrix(rho: bytes):
    raw = np.frombuffer(_xof(b"A" + rho, K_DIM * K_DIM * N * 4), np.uint32)
    return (raw.astype(np.int64) % Q).reshape(K_DIM, K_DIM, N)   # slight bias: toy


def pke_keygen(d: bytes):
    rho, sigma = _xof(b"G" + d, 64)[:32], _xof(b"G" + d, 64)[32:]
    A = gen_matrix(rho)
    s = cbd(sigma + b"s", ETA1, K_DIM)
    e = cbd(sigma + b"e", ETA1, K_DIM)
    t = (matvec(A, s) + e) % Q                        # t = A s + e
    return (t, rho), s


def pke_encrypt(ek, m_bits, coins: bytes):
    t, rho = ek
    A = gen_matrix(rho)
    r = cbd(coins + b"r", ETA1, K_DIM)
    e1 = cbd(coins + b"1", ETA2, K_DIM)
    e2 = cbd(coins + b"2", ETA2, 1)[0]
    u = (matvec(np.transpose(A, (1, 0, 2)), r) + e1) % Q       # A^T r + e1
    v = (dotp(t, r) + e2 + decompress(m_bits, 1)) % Q          # t^T r + e2 + round(q/2) m
    return compress(u, DU), compress(v, DV)


def pke_decrypt(s, c):
    u, v = decompress(c[0], DU), decompress(c[1], DV)
    w = (v - dotp(s, u)) % Q            # = e^T r - s^T e1 + e2 + round(q/2) m + comp. noise
    return compress(w, 1)


def _enc_bytes(c) -> bytes:
    return c[0].astype(np.int64).tobytes() + c[1].astype(np.int64).tobytes()


def kem_keygen():
    d, z = secrets.token_bytes(32), secrets.token_bytes(32)
    ek, s = pke_keygen(d)
    h = hashlib.sha3_256(ek[0].tobytes() + ek[1]).digest()
    return ek, (s, ek, h, z)


def kem_encaps(ek, m: bytes | None = None):
    """(K, r) = G(m || H(ek)); c = Enc(ek, m; r)  [S16 Alg. 17]."""
    m = secrets.token_bytes(N // 8) if m is None else m
    h = hashlib.sha3_256(ek[0].tobytes() + ek[1]).digest()
    g = hashlib.sha3_512(m + h).digest()
    bits = np.unpackbits(np.frombuffer(m, np.uint8)).astype(np.int64)
    return g[:32], pke_encrypt(ek, bits, g[32:])


def kem_decaps(dk, c):
    """Decrypt, re-encrypt with the derived coins, compare; on mismatch return
    J(z || c), a pseudorandom key (implicit rejection) [S16 Alg. 18]."""
    s, ek, h, z = dk
    m2 = np.packbits(pke_decrypt(s, c).astype(np.uint8)).tobytes()
    g = hashlib.sha3_512(m2 + h).digest()
    k_bar = hashlib.shake_256(z + _enc_bytes(c)).digest(32)
    c2 = pke_encrypt(ek, np.unpackbits(np.frombuffer(m2, np.uint8)).astype(np.int64), g[32:])
    same = all(np.array_equal(x, y) for x, y in zip(c, c2))
    return g[:32] if same else k_bar


if __name__ == "__main__":
    print(f"Regev n={REGEV_N}, q={REGEV_Q}, m={REGEV_M}")
    pk, s = regev_keygen(sigma=2.0)
    ok = all(regev_decrypt(s, regev_encrypt(pk, b)) == b for b in [0, 1] * 50)
    print("100 encryptions decrypt correctly:", ok)
    for sigma in (2.0, 8.0, 12.0, 16.0):
        print(f"  sigma={sigma:5.1f}: failure {failure_rate(sigma):.4f}, Gaussian estimate "
              f"{failure_estimate(sigma):.4f}")
    rng = np.random.default_rng(1)
    A = rng.integers(0, REGEV_Q, (REGEV_N + 8, REGEV_N))
    s0 = rng.integers(0, REGEV_Q, REGEV_N)
    print("noiseless LWE: elimination recovers s:",
          np.array_equal(solve_mod_q(A, A @ s0 % REGEV_Q), s0), "| with noise:",
          np.array_equal(solve_mod_q(A, (A @ s0 + gaussian_error(len(A), 2.0, rng)) % REGEV_Q), s0))
    ek, dk = kem_keygen()
    K, c = kem_encaps(ek)
    print(f"toy MLWE KEM (N={N}, k={K_DIM}, q={Q}): keys agree:", kem_decaps(dk, c) == K)
    bad = (c[0], (c[1] + 1) % (1 << DV))
    print("tampered ciphertext -> implicit rejection (different key):", kem_decaps(dk, bad) != K)
