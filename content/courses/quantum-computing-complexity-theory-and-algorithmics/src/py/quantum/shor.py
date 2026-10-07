"""Shor's factoring algorithm: reduction from factoring to order finding (N&C 5.3.2, KLM 7.3.3).

Belongs to the Part C note on order finding and Shor's algorithm (C07).

For odd composite N that is not a prime power: pick random a, if gcd(a, N) > 1 done;
find the order r of a mod N; if r is even and a^{r/2} != -1 mod N then
(a^{r/2} - 1)(a^{r/2} + 1) = 0 mod N gives nontrivial factors gcd(a^{r/2} +- 1, N).
A random a succeeds with probability >= 1/2 (N&C thm 5.3).

Implements: shor_trial, shor, shor_classical_order (same reduction with a classical order oracle).
"""
from math import gcd

import numpy as np

from order_finding import order_classical, order_finding


def shor_trial(N, a, order_fn):
    """One attempt with a fixed base a. order_fn(a, N) -> r or None. Returns (p, q) or None."""
    g = gcd(a, N)
    if g > 1:
        return tuple(sorted((g, N // g)))
    r = order_fn(a, N)
    if r is None or r % 2:
        return None
    y = pow(a, r // 2, N)
    if y == N - 1:
        return None
    p = gcd(y - 1, N)
    q = gcd(y + 1, N)
    for f in (p, q):
        if 1 < f < N:
            return tuple(sorted((f, N // f)))
    return None


def shor(N, rng, max_trials=10, order_fn=None, check_multiples=False):
    """Factor N with random bases; quantum order finding by default. Returns (p, q) or None."""
    if order_fn is None:
        def order_fn(a, N_):
            return order_finding(a, N_, rng, check_multiples=check_multiples)[0]
    for _ in range(max_trials):
        a = int(rng.integers(2, N - 1))
        result = shor_trial(N, a, order_fn)
        if result is not None:
            return result
    return None


def shor_classical_order(N, rng, max_trials=10):
    """Same reduction but with the brute-force classical order (for larger N in demos)."""
    return shor(N, rng, max_trials, order_fn=lambda a, N_: order_classical(a, N_))


if __name__ == "__main__":
    import time
    rng = np.random.default_rng(0)
    for N in (15, 21):
        t0 = time.time()
        print(f"quantum order finding: {N} = {shor(N, rng)}  ({time.time() - t0:.2f} s)")
    for N in (91, 221, 1001, 3599):
        print(f"classical order oracle: {N} = {shor_classical_order(N, rng)}")
