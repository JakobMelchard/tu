"""Quantum order finding: the period r of a mod N via phase estimation of U_a|y> = |a y mod N> (N&C 5.3.1, KLM 7.3).

Belongs to the Part C note on order finding and Shor's algorithm (C07).

Register layout: t = 2 ceil(log2 N) counting qubits (0..t-1), then n = ceil(log2 N)
work qubits holding y (initialised to |1>). Controlled-U_a^{2^j} is NOT a dense
matrix: a^{2^j} mod N is computed classically and the map y -> a^{2^j} y mod N is
applied as a permutation of the amplitude array (identity on y >= N). The
eigenphases of U_a are s/r, so |1> = sum_s |u_s>/sqrt(r) makes phase estimation
return x ~ 2^t s/r; continued fractions of x/2^t recover r when gcd(s, r) = 1.

Implements: modmul_permutation, order_finding_state, order_finding_distribution,
continued_fraction, convergents, denominator_from_phase, order_from_measurement,
order_finding, order_finding_success_probability, order_classical.
"""
from math import ceil, gcd, log2

import numpy as np

from qft import qft
from sim import Register


def modmul_permutation(a, N, n_work):
    """perm[y] = a*y mod N for y < N (bijective iff gcd(a,N)=1), identity for y >= N."""
    perm = np.arange(2 ** n_work)
    perm[:N] = (a * np.arange(N)) % N
    return perm


def order_finding_state(a, N, t=None):
    """Register after the inverse QFT (counting qubits first, work register after)."""
    assert gcd(a, N) == 1
    n = ceil(log2(N))
    t = 2 * n if t is None else t
    reg = Register(t + n)
    reg.state[0], reg.state[1] = 0, 1                 # work register |1>, counting |0...0>
    counting, work = list(range(t)), list(range(t, t + n))
    for q in counting:
        reg.h(q)
    for j in counting:                                # counting qubit j controls U_a^{2^{t-1-j}}
        a_pow = pow(a, 2 ** (t - 1 - j), N)
        reg.apply_permutation(modmul_permutation(a_pow, N, n), work, controls=[j])
    qft(reg, counting, inverse=True)
    return reg, t


def order_finding_distribution(a, N, t=None):
    """Exact P(x) over the 2^t counting outcomes."""
    reg, t = order_finding_state(a, N, t)
    return reg.probabilities().reshape(2 ** t, -1).sum(axis=1), t


def continued_fraction(p, q):
    """Partial quotients [a0; a1, ...] of p/q (finite, p,q >= 0, q > 0)."""
    cf = []
    while q:
        cf.append(p // q)
        p, q = q, p % q
    return cf


def convergents(cf):
    """(numerator, denominator) of every convergent of a partial-quotient list."""
    out = []
    h_prev, h = 1, cf[0]
    k_prev, k = 0, 1
    out.append((h, k))
    for a in cf[1:]:
        h, h_prev = a * h + h_prev, h
        k, k_prev = a * k + k_prev, k
        out.append((h, k))
    return out


def denominator_from_phase(x, M, N):
    """Largest convergent denominator of x/M that is <= N (the candidate for r)."""
    best = 1
    for _, q in convergents(continued_fraction(x, M)):
        if q <= N:
            best = q
    return best


def order_from_measurement(x, t, a, N, check_multiples=False):
    """Candidate r from counting outcome x; verified with a^r = 1 mod N, else None."""
    r = denominator_from_phase(x, 2 ** t, N)
    if pow(a, r, N) == 1:
        return r
    if check_multiples:                               # classical post-processing: try small multiples
        for k in range(2, N // r + 1):
            if pow(a, k * r, N) == 1:
                return k * r
    return None


def order_finding(a, N, rng, t=None, check_multiples=False):
    """One quantum run. Returns (r or None, measured x)."""
    reg, t = order_finding_state(a, N, t)
    bits = reg.measure(list(range(t)), rng)
    x = int("".join(map(str, bits)), 2)
    return order_from_measurement(x, t, a, N, check_multiples), x


def order_finding_success_probability(a, N, t=None, check_multiples=False):
    """Exact P(one run returns the correct r), summing P(x) over the good outcomes."""
    P, t = order_finding_distribution(a, N, t)
    r_true = order_classical(a, N)
    return float(sum(p for x, p in enumerate(P)
                     if order_from_measurement(x, t, a, N, check_multiples) == r_true))


def order_classical(a, N):
    """Smallest r >= 1 with a^r = 1 mod N by repeated multiplication (gcd(a,N)=1)."""
    assert gcd(a, N) == 1
    r, y = 1, a % N
    while y != 1:
        y = (y * a) % N
        r += 1
    return r


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    for a, N in ((7, 15), (2, 15), (11, 15), (2, 21)):
        P, t = order_finding_distribution(a, N)
        peaks = [(int(x), round(float(P[x]), 3)) for x in np.argsort(P)[::-1][:6] if P[x] > 1e-3]
        r, x = order_finding(a, N, rng)
        print(f"a={a} N={N}: t={t}, true r={order_classical(a, N)}, peaks (x,P)={peaks},"
              f" P(success)={order_finding_success_probability(a, N):.3f}, one run: x={x} -> r={r}")
    print("continued fraction of 85/256:", continued_fraction(85, 256), "convergents", convergents(continued_fraction(85, 256)))
