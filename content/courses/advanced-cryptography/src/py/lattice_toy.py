"""Lattices in 2 and 3 dimensions: Gram-Schmidt, Lagrange-Gauss reduction
(exact SVP in dimension 2), LLL, Babai rounding and nearest plane for CVP,
brute-force SVP/CVP for checking, and the good-basis/bad-basis experiment
that is the intuition behind lattice trapdoors (GGH).

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). Exact
rational arithmetic (fractions) in tiny dimension; nothing here says anything
about the hardness of SVP in dimension 500. Sources: Lagrange-Gauss
[S37 Alg. 23, sec. 17.1], LLL [S37 sec. 17.4], Babai [S37 sec. 18.1-18.2],
definitions [S6 sec. 2.2].
"""
from __future__ import annotations

import itertools
import random
from fractions import Fraction


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def sub(u, v, k=1):
    return [a - k * b for a, b in zip(u, v)]


def norm2(u):
    return dot(u, u)


def combo(coeffs, B):
    return [sum(c * b[i] for c, b in zip(coeffs, B)) for i in range(len(B[0]))]


def gram_schmidt(B):
    """B* and mu with b_i = b_i* + sum_{j<i} mu_ij b_j*."""
    Bs, mu = [], [[Fraction(0)] * len(B) for _ in B]
    for i, b in enumerate(B):
        v = [Fraction(x) for x in b]
        for j in range(i):
            mu[i][j] = Fraction(dot(b, Bs[j])) / norm2(Bs[j])
            v = sub(v, Bs[j], mu[i][j])
        Bs.append(v)
    return Bs, mu


def det2(B) -> int:
    return B[0][0] * B[1][1] - B[0][1] * B[1][0]


def gauss_reduce(b1, b2):
    """Lagrange-Gauss: the 2-D Euclid. Output (b1, b2) with |b1| <= |b2| and
    |<b1,b2>| <= |b1|^2 / 2, whence b1 is a shortest nonzero vector."""
    b1, b2 = list(b1), list(b2)
    if norm2(b2) < norm2(b1):
        b1, b2 = b2, b1
    while True:
        mu = round(Fraction(dot(b1, b2), norm2(b1)))
        b2 = sub(b2, b1, mu)
        if norm2(b2) >= norm2(b1):
            return b1, b2
        b1, b2 = b2, b1


def lll(B, delta=Fraction(3, 4)):
    """Textbook LLL (size reduction + Lovasz swap), exact arithmetic."""
    B = [list(b) for b in B]
    k = 1
    while k < len(B):
        for j in range(k - 1, -1, -1):
            _, mu = gram_schmidt(B)
            q = round(mu[k][j])
            if q:
                B[k] = sub(B[k], B[j], q)
        Bs, mu = gram_schmidt(B)
        if norm2(Bs[k]) >= (delta - mu[k][k - 1] ** 2) * norm2(Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)
    return B


def is_lll_reduced(B, delta=Fraction(3, 4)) -> bool:
    Bs, mu = gram_schmidt(B)
    size = all(abs(mu[i][j]) <= Fraction(1, 2) for i in range(len(B)) for j in range(i))
    lovasz = all(norm2(Bs[k]) >= (delta - mu[k][k - 1] ** 2) * norm2(Bs[k - 1])
                 for k in range(1, len(B)))
    return size and lovasz


def svp_bruteforce(B, R: int = 6):
    """Shortest nonzero vector with coefficients in [-R, R]^n."""
    best = None
    for c in itertools.product(range(-R, R + 1), repeat=len(B)):
        if any(c):
            v = combo(c, B)
            if best is None or norm2(v) < norm2(best):
                best = v
    return best


def cvp_bruteforce(B, t, R: int = 8):
    best = None
    for c in itertools.product(range(-R, R + 1), repeat=len(B)):
        v = combo(c, B)
        if best is None or norm2(sub(v, t)) < norm2(sub(best, t)):
            best = v
    return best


def _solve(B, t):
    """Coordinates x with x B = t (rows of B are the basis), via Cramer / GS."""
    n = len(B)
    M = [[Fraction(B[j][i]) for j in range(n)] + [Fraction(t[i])] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        M[c] = [x / M[c][c] for x in M[c]]
        for r in range(n):
            if r != c:
                M[r] = sub(M[r], M[c], M[r][c])
    return [M[i][n] for i in range(n)]


def babai_round(B, t):
    """Write t in the basis, round each coordinate: lattice point in the
    translated fundamental parallelepiped around t [S37 sec. 18.2]."""
    return combo([round(x) for x in _solve(B, t)], B)


def babai_nearest_plane(B, t):
    """Project onto hyperplanes spanned by b_1..b_{i-1}, from the last
    Gram-Schmidt direction down [S37 sec. 18.1]."""
    Bs, _ = gram_schmidt(B)
    b = [Fraction(x) for x in t]
    for i in range(len(B) - 1, -1, -1):
        c = round(dot(b, Bs[i]) / norm2(Bs[i]))
        b = sub(b, B[i], c)
    return [int(ti - bi) for ti, bi in zip(t, b)]


def hadamard_ratio(B) -> float:
    """(|det B| / prod |b_i|)^(1/n) in (0, 1]; 1 = orthogonal (a 'good' basis)."""
    Bs, _ = gram_schmidt(B)
    vol = 1.0
    for v in Bs:
        vol *= float(norm2(v)) ** 0.5
    prod = 1.0
    for b in B:
        prod *= norm2(b) ** 0.5
    return (vol / prod) ** (1 / len(B))


GOOD = [[17, 1], [-2, 19]]           # nearly orthogonal
U = [[5, 8], [3, 5]]                 # unimodular: det = 1
BAD = [combo(row, GOOD) for row in U]


def trapdoor_experiment(trials=300, noise=6, seed=0):
    """Encode a lattice point + small error; decode with Babai rounding under
    the good and the bad basis. Returns success rates."""
    rng = random.Random(seed)
    ok_good = ok_bad = 0
    for _ in range(trials):
        v = combo([rng.randrange(-50, 50), rng.randrange(-50, 50)], GOOD)
        t = [v[0] + rng.randint(-noise, noise), v[1] + rng.randint(-noise, noise)]
        ok_good += babai_round(GOOD, t) == v
        ok_bad += babai_round(BAD, t) == v
    return ok_good / trials, ok_bad / trials


if __name__ == "__main__":
    print("good basis", GOOD, f"Hadamard ratio {hadamard_ratio(GOOD):.3f}")
    print("bad basis ", BAD, f"Hadamard ratio {hadamard_ratio(BAD):.3f}",
          "| same lattice: |det| =", abs(det2(GOOD)), abs(det2(BAD)))
    r = gauss_reduce(*BAD)
    print("Lagrange-Gauss on the bad basis:", r, " shortest (brute force):", svp_bruteforce(GOOD))
    g, b = trapdoor_experiment()
    print(f"Babai rounding decodes point+noise: good basis {g:.0%}, bad basis {b:.0%}")
    B3 = [[1, 1, 1], [-1, 0, 2], [3, 5, 6]]
    L3 = lll(B3)
    print("LLL in 3-D:", B3, "->", L3, " reduced:", is_lll_reduced(L3))
