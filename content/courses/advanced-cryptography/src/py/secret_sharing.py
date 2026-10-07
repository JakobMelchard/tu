"""Shamir secret sharing and BGW-style honest-majority MPC over F_p:
local addition and scalar multiplication, multiplication with degree
reduction (two ways) or with a Beaver triple, and a full n-party evaluation
of an arithmetic circuit.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). Semi-honest
parties only, simulated in one process; 'channels' are Python lists.
Shamir: [S14], [S7 sec. 4.1], [S4 sec. 22.1]. Multiplication by double
sharing: [S7 sec. 4.2]. Resharing + Lagrange (the BGW/GRR variant): [S31].
Convention of [S7]: degree-t polynomial, any t+1 shares reconstruct, any t
reveal nothing; multiplication needs n >= 2t + 1.
"""
from __future__ import annotations

import random
import secrets

P = 2**13 - 1  # 8191, a Mersenne prime; any prime p > n works


def _rand(rng):
    return rng.randrange(P) if rng else secrets.randbelow(P)


def share(s: int, t: int, n: int, rng: random.Random | None = None, p: int = P):
    """f(X) = s + a_1 X + ... + a_t X^t; party i (1..n) gets f(i)."""
    if not n < p:
        raise ValueError("need p > n distinct nonzero evaluation points")
    coeffs = [s % p] + [(rng.randrange(p) if rng else secrets.randbelow(p)) for _ in range(t)]
    return [sum(c * pow(i, k, p) for k, c in enumerate(coeffs)) % p for i in range(1, n + 1)]


def lagrange_at_zero(xs, p: int = P):
    """lambda_i with f(0) = sum lambda_i f(x_i) for deg f < len(xs)."""
    lams = []
    for i, xi in enumerate(xs):
        num = den = 1
        for j, xj in enumerate(xs):
            if j != i:
                num = num * (-xj) % p
                den = den * (xi - xj) % p
        lams.append(num * pow(den, -1, p) % p)
    return lams


def reconstruct(points, p: int = P) -> int:
    """points = [(i, f(i)), ...]; interpolate at 0."""
    xs = [x for x, _ in points]
    return sum(l * y for l, (_, y) in zip(lagrange_at_zero(xs, p), points)) % p


def degree(shares, p: int = P) -> int:
    """Degree of the polynomial through (i, shares[i-1]) (Newton differences)."""
    xs = list(range(1, len(shares) + 1))
    coef = list(shares)
    for j in range(1, len(xs)):
        for i in range(len(xs) - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) * pow(xs[i] - xs[i - j], -1, p) % p
    d = len(coef) - 1
    while d > 0 and coef[d] == 0:
        d -= 1
    return d


# --- BGW gates on share vectors (index k = party k+1) --------------------------

def add(a, b):
    """Local: (f + g)(i) = f(i) + g(i). No communication."""
    return [(x + y) % P for x, y in zip(a, b)]


def scal(k, a):
    return [k * x % P for x in a]


def add_const(k, a):
    return [(x + k) % P for x in a]


def mul_local(a, b):
    """Local product: a valid sharing of ab, but of degree 2t."""
    return [x * y % P for x, y in zip(a, b)]


def mul_resharing(a, b, t: int, rng=None):
    """BGW/GRR degree reduction: party i reshares c(i) = a(i)b(i) with degree
    t; everyone outputs sum_i lambda_i * (subshare from i), lambda = Lagrange
    coefficients at 0 for the points 1..n. Correct because
    c(0) = sum lambda_i c(i) when deg c = 2t <= n - 1."""
    n = len(a)
    if n < 2 * t + 1:
        raise ValueError("degree reduction needs n >= 2t + 1 (honest majority)")
    c = mul_local(a, b)
    sub = [share(ci, t, n, rng) for ci in c]         # sub[i][j]: from i to j
    lam = lagrange_at_zero(list(range(1, n + 1)))
    return [sum(lam[i] * sub[i][j] for i in range(n)) % P for j in range(n)]


def random_double_sharing(t: int, n: int, rng=None):
    """[r]_t and [r]_2t of the same unknown r = sum of every party's r_j [S7]."""
    R_t, R_2t = [0] * n, [0] * n
    for _ in range(n):
        rj = _rand(rng)
        R_t = add(R_t, share(rj, t, n, rng))
        R_2t = add(R_2t, share(rj, 2 * t, n, rng))
    return R_t, R_2t


def mul_double_sharing(a, b, t: int, rng=None):
    """[S7 sec. 4.2]: d = c - R_2t is opened (it is ab - r, uniform), then
    c'(i) = R_t(i) + d(0) is a degree-t sharing of ab."""
    n = len(a)
    if n < 2 * t + 1:
        raise ValueError("opening a degree-2t sharing needs n >= 2t + 1")
    R_t, R_2t = random_double_sharing(t, n, rng)
    d = [(ci - ri) % P for ci, ri in zip(mul_local(a, b), R_2t)]
    d0 = reconstruct(list(enumerate(d, 1)))           # public opening
    return add_const(d0, R_t), d0


def beaver_triple(t: int, n: int, rng=None):
    """Dealer-generated sharing of (a, b, ab) with a, b uniform: the
    preprocessing of Beaver's protocol [S4 sec. 23.2.2]."""
    a, b = _rand(rng), _rand(rng)
    return share(a, t, n, rng), share(b, t, n, rng), share(a * b, t, n, rng)


def mul_beaver(x, y, triple):
    """Open d = x - a and e = y - b (uniform, reveal nothing); then
    xy = c + d b + e a + d e is LINEAR in the shares: no degree growth."""
    A, B, C = triple
    d = reconstruct(list(enumerate([(xi - ai) % P for xi, ai in zip(x, A)], 1)))
    e = reconstruct(list(enumerate([(yi - bi) % P for yi, bi in zip(y, B)], 1)))
    return add_const(d * e, add(C, add(scal(d, B), scal(e, A))))


# --- an n-party computation ----------------------------------------------------

def mpc_eval(inputs: list[int], t: int, circuit, mul=mul_resharing, rng=None) -> int:
    """Each party j shares input j; the circuit is a list of
    (op, in1, in2) over wire names 'x0'.. and gate indices 'g0'..; the
    result is the last gate's value, opened to everyone."""
    n = len(inputs)
    wires = {f"x{j}": share(v, t, n, rng) for j, v in enumerate(inputs)}
    for k, (op, a, b) in enumerate(circuit):
        if op == "add":
            wires[f"g{k}"] = add(wires[a], wires[b])
        elif op == "mul":
            out = mul(wires[a], wires[b], t, rng)
            wires[f"g{k}"] = out[0] if isinstance(out, tuple) else out
        elif op == "cmul":
            wires[f"g{k}"] = scal(b, wires[a])
        else:
            raise ValueError(op)
    final = wires[f"g{len(circuit) - 1}"]
    return reconstruct(list(enumerate(final, 1)))


# (x0 + x1) * x2 + 3 * x3 * x4
EXAMPLE = [("add", "x0", "x1"), ("mul", "g0", "x2"), ("mul", "x3", "x4"),
           ("cmul", "g2", 3), ("add", "g1", "g3")]


if __name__ == "__main__":
    t, n, s = 2, 5, 1234
    sh = share(s, t, n)
    print(f"({t}+1)-of-{n} Shamir shares of {s}:", sh)
    print("any 3 reconstruct:", reconstruct([(1, sh[0]), (3, sh[2]), (5, sh[4])]),
          "| 2 shares fit a line, its value at 0 is unrelated:", reconstruct([(1, sh[0]), (2, sh[1])]))
    a, b = share(20, t, n), share(30, t, n)
    print("deg a =", degree(a), " deg a*b local =", degree(mul_local(a, b)),
          " after resharing =", degree(mul_resharing(a, b, t)))
    c, d0 = mul_double_sharing(a, b, t)
    print("double-sharing product opens to", reconstruct(list(enumerate(c, 1))),
          f"(publicly opened mask d(0) = {d0})")
    xs = [3, 4, 5, 6, 7]
    print("MPC (x0+x1)*x2 + 3*x3*x4 =", mpc_eval(xs, t, EXAMPLE),
          "expected", ((3 + 4) * 5 + 3 * 6 * 7) % P)
