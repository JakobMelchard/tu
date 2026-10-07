"""Privacy amplification with Toeplitz hashing and the leftover hash lemma.

TOY CRYPTO: exact enumeration on at most ~16-bit strings, for checking the lemma numerically.
Note 04 (reconciliation and privacy amplification):
- Toeplitz family T_s : {0,1}^n -> {0,1}^l, seed s of n + l - 1 bits (`toeplitz`, `toeplitz_hash`).
  Two-universal: for x != x', Pr_s[T_s x = T_s x'] = 2^-l, checked exactly by enumerating all
  seeds (`collision_probability`) [S4 Def. 5.4.1].
- Leftover hash lemma, trace-distance form: with H = H_min(X|E),
      1/2 || rho_{F(X) F E} - U_l (x) rho_{F E} ||_1 <= 1/2 * 2^{-(H - l)/2}
  [S4 Cor. 5.6.1 with eps = 0, which states it for the unhalved L1 distance; S12] (`lhl_bound`).
- Key length with smoothing, error-correction leakage and verification hash
  l = floor(H_min^eps - leak_EC - t - 2 log2(1/(2 eps_PA))) (`key_length`) [S5 Eq. (58)].
- Exact distance from uniform for a flat source X uniform on S (|S| = 2^k), no side
  information (`distance_flat_source`), and for X uniform on n bits with Eve holding the first
  m bits (`distance_with_prefix_leak`, H_min(X|E) = n - m).

Run `python privacy_amplification.py`.
"""
from __future__ import annotations

import math

import numpy as np


def toeplitz(seed: np.ndarray, n: int, l: int) -> np.ndarray:
    """l x n binary Toeplitz matrix T[i, j] = seed[i - j + n - 1] (constant diagonals)."""
    i, j = np.indices((l, n))
    return seed[i - j + n - 1].astype(np.int64)


def toeplitz_hash(x: np.ndarray, seed: np.ndarray, l: int) -> np.ndarray:
    """Hash rows of x (shape (..., n)) to l bits: T x mod 2."""
    n = x.shape[-1]
    return (x.astype(np.int64) @ toeplitz(seed, n, l).T) % 2


def all_bitstrings(n: int) -> np.ndarray:
    return ((np.arange(2**n)[:, None] >> np.arange(n)[::-1]) & 1).astype(np.int8)


def bits_to_int(y: np.ndarray) -> np.ndarray:
    return (y * (1 << np.arange(y.shape[-1])[::-1])).sum(-1)


def collision_probability(n: int, l: int) -> float:
    """max over x != x' of Pr_seed[T x = T x'] by enumeration of all 2^(n+l-1) seeds.

    T x = T x' iff T z = 0 with z = x xor x' != 0, so it suffices to range over z.
    """
    zs = all_bitstrings(n)[1:]
    seeds = all_bitstrings(n + l - 1)
    zero = np.zeros(len(zs))
    for s in seeds:
        zero += ~toeplitz_hash(zs, s, l).any(axis=1)
    return float(zero.max() / len(seeds))


def lhl_bound(h_min: float, l: int) -> float:
    """Trace-distance bound 1/2 * 2^{-(H_min - l)/2}."""
    return 0.5 * 2.0 ** (-(h_min - l) / 2)


def key_length(h_min_smooth: float, leak_ec: float, t: int, eps_pa: float) -> int:
    """Largest l with 1/2 sqrt(2^{-(H - leak - t - l)}) <= eps_pa."""
    return max(0, math.floor(h_min_smooth - leak_ec - t - 2 * math.log2(1 / (2 * eps_pa))))


def _distance_given_support(xs: np.ndarray, weights: np.ndarray, seed: np.ndarray, l: int) -> float:
    """1/2 sum_k |P(T x = k) - 2^-l| for X distributed on xs with the given weights."""
    k = bits_to_int(toeplitz_hash(xs, seed, l))
    p = np.bincount(k, weights=weights, minlength=2**l)
    return 0.5 * float(np.abs(p - 2.0**-l).sum())


def distance_flat_source(n: int, k: int, l: int, rng: np.random.Generator,
                         n_seeds: int | None = None) -> tuple[float, float]:
    """X uniform on a random 2^k-subset of {0,1}^n. Returns (E_seed distance, LHL bound).

    Averaging over the seed is the distance of (F(X), F) from (U, F). All seeds if n_seeds is None.
    """
    xs = all_bitstrings(n)[rng.choice(2**n, size=2**k, replace=False)]
    w = np.full(len(xs), 2.0**-k)
    seeds = (all_bitstrings(n + l - 1) if n_seeds is None
             else rng.integers(0, 2, size=(n_seeds, n + l - 1)))
    d = np.mean([_distance_given_support(xs, w, s, l) for s in seeds])
    return float(d), lhl_bound(k, l)


def distance_with_prefix_leak(n: int, m: int, l: int, rng: np.random.Generator,
                              n_seeds: int = 200) -> tuple[float, float]:
    """X uniform on n bits, Eve holds E = first m bits. Distance of (F(X), F, E) from (U, F, E)."""
    xs = all_bitstrings(n)
    prefixes = bits_to_int(xs[:, :m]) if m else np.zeros(len(xs), dtype=int)
    tot = 0.0
    for _ in range(n_seeds):
        s = rng.integers(0, 2, n + l - 1)
        for e in range(2**m):               # sum_e P(e) * d(F(X) | E = e)
            sel = prefixes == e
            w = np.full(int(sel.sum()), 2.0 ** -(n - m))
            tot += 2.0**-m * _distance_given_support(xs[sel], w, s, l)
    return tot / n_seeds, lhl_bound(n - m, l)


def demo() -> None:
    rng = np.random.default_rng(5)
    for n, l in [(5, 2), (6, 3)]:
        print(f"Toeplitz n={n}, l={l}: max collision prob {collision_probability(n, l):.4f} "
              f"= 2^-l = {2**-l:.4f}")
    print(f"{'n':>3} {'k=Hmin':>7} {'l':>3} {'exact dist':>11} {'LHL bound':>10}")
    for n, k, l in [(12, 8, 2), (12, 8, 4), (12, 8, 6), (12, 8, 8), (12, 8, 10)]:
        d, b = distance_flat_source(n, k, l, rng, n_seeds=300)
        print(f"{n:3d} {k:7d} {l:3d} {d:11.5f} {b:10.5f}")
    print("l > H_min: output support 2^k < 2^l, so distance >= 1 - 2^(k-l) (key not secret)")
    d, b = distance_with_prefix_leak(10, 4, 3, rng)
    print(f"Eve knows 4 of 10 bits, l=3: distance {d:.5f} <= bound {b:.5f}")
    eps = 1e-10
    print("key length for H_min^eps=10^6, leak_EC=2.1e5, t=34, eps_PA=1e-10:",
          key_length(1e6, 2.1e5, 34, eps))


if __name__ == "__main__":
    demo()
