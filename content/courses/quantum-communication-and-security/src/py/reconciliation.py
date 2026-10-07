"""Information reconciliation toys: BINARY, simplified Cascade, Hamming(7,4) syndromes,
verification hashing, and leakage accounting.

TOY CRYPTO: parity protocols for teaching; not constant-time, not production error correction.
Note 04 (reconciliation and privacy amplification):
- Leakage lower bound n h(e) (Slepian-Wolf, one-way) and efficiency f = leak / (n h(e))
  (`shannon_leak`, `efficiency`) [S3 Sec. III.B, S9 Eq. (1)].
- BINARY: bisect a block with a parity mismatch, one parity bit per halving (`binary`).
- Cascade (Brassard-Salvail idea [S22]): passes of block parities with block size
  k_1 ~ 0.73/e doubling each pass, random permutations, and the cascade step: a bit flipped
  in pass p makes the block containing it in every earlier pass odd again (`cascade`).
  Sub-block parities are not reused, so the leak is a slight over-count.
- Hamming(7,4) syndrome reconciliation: 3 bits leaked per 7, one error per block corrected
  (`hamming_reconcile`).
- Verification: random linear hash with t output bits, collision probability 2^-t [S5 Thm 2]
  (`verify_hash`).

Run `python reconciliation.py`.
"""
from __future__ import annotations

from collections import deque

import numpy as np

from entropies import h2


def shannon_leak(n: int, e: float) -> float:
    return n * float(h2(e))


def efficiency(leak: int, n: int, e: float) -> float:
    return leak / shannon_leak(n, e)


def parity(x: np.ndarray, idx: np.ndarray) -> int:
    return int(x[idx].sum() & 1)


def binary(a: np.ndarray, b: np.ndarray, idx: np.ndarray) -> tuple[int, int]:
    """Locate one error in a block of odd parity difference. Returns (position, parities leaked)."""
    leak = 0
    while len(idx) > 1:
        half = idx[: len(idx) // 2]
        leak += 1                                   # Alice announces the parity of the first half
        idx = half if parity(a, half) != parity(b, half) else idx[len(idx) // 2:]
    return int(idx[0]), leak


def cascade(a: np.ndarray, b: np.ndarray, e_est: float, rng: np.random.Generator,
            passes: int = 4, k1: int | None = None) -> tuple[np.ndarray, int]:
    """Simplified Cascade. Returns Bob's corrected string and the number of leaked parity bits."""
    n = len(a)
    b = b.copy()
    k1 = k1 or max(4, int(0.73 / max(e_est, 1e-6)))
    perms, invs, sizes = [], [], []
    leak = 0

    def block(q: int, j: int) -> np.ndarray:
        """Positions of the block that contains bit j in pass q."""
        start = (invs[q][j] // sizes[q]) * sizes[q]
        return perms[q][start: start + sizes[q]]

    def correct_and_cascade(p: int, blk: np.ndarray) -> None:
        nonlocal leak
        todo = deque([blk])
        while todo:
            blk = todo.popleft()
            if parity(a, blk) == parity(b, blk):    # Alice's parity is public already: free check
                continue
            j, l = binary(a, b, blk)
            leak += l
            b[j] ^= 1
            for q in range(p + 1):                  # every earlier pass sees a new odd block
                todo.append(block(q, j))

    for p in range(passes):
        perm = np.arange(n) if p == 0 else rng.permutation(n)
        inv = np.empty(n, dtype=int)
        inv[perm] = np.arange(n)
        perms.append(perm), invs.append(inv), sizes.append(min(n, k1 * 2**p))
        k = sizes[p]
        for start in range(0, n, k):
            blk = perm[start: start + k]
            leak += 1                               # top-level block parity
            if parity(a, blk) != parity(b, blk):
                correct_and_cascade(p, blk)
    return b, leak


# ------------------------------------------------------------------ Hamming(7,4) syndromes
H74 = np.array([[(c >> r) & 1 for c in range(1, 8)] for r in range(3)], dtype=np.int8)


def hamming_reconcile(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, int]:
    """Alice sends the 3-bit syndrome of every 7-bit block; Bob flips the indicated bit."""
    n = len(a) // 7 * 7
    b = b.copy()
    A, B = a[:n].reshape(-1, 7), b[:n].reshape(-1, 7)
    s = (A @ H74.T + B @ H74.T) % 2                 # syndrome of the error pattern a xor b
    pos = s @ np.array([1, 2, 4]) - 1               # column index of H74 equal to the syndrome
    rows = np.nonzero(pos >= 0)[0]
    B[rows, pos[rows]] ^= 1
    b[:n] = B.ravel()
    return b, 3 * (n // 7)


# ------------------------------------------------------------------ verification
def verify_hash(a: np.ndarray, b: np.ndarray, t: int, rng: np.random.Generator) -> bool:
    """Compare t-bit random linear hashes. For a != b, Pr[equal] = 2^-t exactly."""
    m = rng.integers(0, 2, size=(t, len(a)), dtype=np.int8)
    return bool(np.array_equal(m @ a % 2, m @ b % 2))


def bsc(a: np.ndarray, e: float, rng: np.random.Generator) -> np.ndarray:
    """Bob's raw key: Alice's string through a binary symmetric channel with flip rate e."""
    return (a ^ (rng.random(len(a)) < e)).astype(np.int8)


def demo() -> None:
    rng = np.random.default_rng(3)
    n = 20_000
    print(f"{'e':>5} {'errors':>7} {'left':>5} {'leak':>6} {'n h(e)':>8} {'f':>6}")
    for e in (0.01, 0.02, 0.05, 0.08):
        a = rng.integers(0, 2, n, dtype=np.int8)
        b = bsc(a, e, rng)
        bc, leak = cascade(a, b, e, rng)
        print(f"{e:5.2f} {int((a != b).sum()):7d} {int((a != bc).sum()):5d} {leak:6d} "
              f"{shannon_leak(n, e):8.0f} {efficiency(leak, n, e):6.3f}")
    a = rng.integers(0, 2, 7000, dtype=np.int8)
    b = bsc(a, 0.01, rng)
    bh, leak = hamming_reconcile(a, b)
    print(f"Hamming(7,4) at e=1%: {int((a != b).sum())} -> {int((a != bh).sum())} errors, "
          f"leak {leak} = 3/7 n vs n h(e) = {shannon_leak(7000, 0.01):.0f}")
    b2 = a.copy(); b2[5] ^= 1
    coll = np.mean([verify_hash(a, b2, 4, rng) for _ in range(20_000)])
    print(f"verification hash t=4 on unequal strings: collision {coll:.4f} vs 2^-4 = {2**-4:.4f}")


if __name__ == "__main__":
    demo()
