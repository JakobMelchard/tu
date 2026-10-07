"""Finite-difference weights on arbitrary grids (topic 03).

Note 03 says "choose stencil points, write the Taylor series of each, solve the
linear system for weights that cancel all terms up to the desired order
(Fornberg's algorithm does this for arbitrary stencils)". This module is that
sentence, executed, so the table of stencils in the note can be regenerated
instead of trusted.

Two routes to the same answer:

* `weights_vandermonde` solves the order conditions directly. For offsets
  s_0..s_n and derivative order d, the weights w satisfy
  sum_j w_j s_j^k / k! = delta_{k,d} / h^d for k = 0..n -- i.e. a Vandermonde
  system. Clear, and O(n^3).
* `weights_fornberg` is Fornberg's recurrence [S25], which builds the weights
  for every derivative order 0..d and every prefix of the node set in O(n^2 d),
  and is what real codes use.

The leading error term of a stencil is obtained from the first order condition
it fails to satisfy: if the weights annihilate x^k/k! for k = 0..m-1 but leave
C = sum_j w_j s_j^m / m! for k = m, the truncation error is
C h^(m-d) f^(m)(x). `leading_error_term` returns (m, C).

Run `python3 fdstencil.py` to print the table in note 03. Tests: test_fdstencil.py.
"""
import math
from fractions import Fraction

import numpy as np


def weights_vandermonde(offsets, deriv):
    """Exact rational weights (in units of 1/h**deriv) for d^deriv/dx^deriv.

    offsets: integer or Fraction node offsets s_j, so the nodes are x + s_j h.
    Solves sum_j w_j s_j^k = deriv! * delta_{k,deriv}, k = 0..n, in Fractions,
    so the result is the textbook fraction and not a float.
    """
    s = [Fraction(o) for o in offsets]
    n = len(s)
    if deriv >= n:
        raise ValueError("need more than `deriv` nodes")
    # Gaussian elimination on the transposed Vandermonde system, in Fractions.
    a = [[s[j] ** k for j in range(n)] for k in range(n)]
    b = [Fraction(math.factorial(deriv)) if k == deriv else Fraction(0) for k in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if a[r][col] != 0)
        a[col], a[piv] = a[piv], a[col]
        b[col], b[piv] = b[piv], b[col]
        inv = Fraction(1) / a[col][col]
        a[col] = [v * inv for v in a[col]]
        b[col] *= inv
        for r in range(n):
            if r != col and a[r][col] != 0:
                f = a[r][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
                b[r] -= f * b[col]
    return b


def weights_fornberg(offsets, deriv, x0=0):
    """Fornberg's recurrence [S25]: weights for derivatives 0..deriv at x0.

    Returns an array c[k, j]: the weight of node j in the order-k derivative,
    for k = 0..deriv, using nodes 0..j. c[deriv, :] over all nodes is the
    stencil. Mirrors Fornberg (1988), Math. Comp. 51, eq. (6)-(9).
    """
    z = np.asarray(offsets, dtype=float)
    n = len(z) - 1
    c = np.zeros((deriv + 1, n + 1))
    c1, c4 = 1.0, z[0] - x0
    c[0, 0] = 1.0
    for i in range(1, n + 1):
        mn = min(i, deriv)
        c2, c5 = 1.0, c4
        c4 = z[i] - x0
        for j in range(i):
            c3 = z[i] - z[j]
            c2 *= c3
            if j == i - 1:
                for k in range(mn, 0, -1):
                    c[k, i] = c1 * (k * c[k - 1, i - 1] - c5 * c[k, i - 1]) / c2
                c[0, i] = -c1 * c5 * c[0, i - 1] / c2
            for k in range(mn, 0, -1):
                c[k, j] = (c4 * c[k, j] - k * c[k - 1, j]) / c3
            c[0, j] = c4 * c[0, j] / c3
        c1 = c2
    return c


def leading_error_term(offsets, deriv, weights=None, max_order=14):
    """(m, C) with truncation error C h^(m-deriv) f^(m)(x).

    m is the lowest Taylor order the stencil fails to reproduce; C is the
    residual coefficient sum_j w_j s_j^m / m!.
    """
    w = weights if weights is not None else weights_vandermonde(offsets, deriv)
    s = [Fraction(o) for o in offsets]
    for m in range(len(s), max_order):
        c = sum(wj * sj ** m for wj, sj in zip(w, s)) / math.factorial(m)
        if c != 0:
            return m, c
    return None, Fraction(0)


STENCILS = [
    ("forward   D+", (0, 1), 1),
    ("backward  D-", (-1, 0), 1),
    ("central   D0", (-1, 1), 1),
    ("2nd deriv", (-1, 0, 1), 2),
    ("4th-order central", (-2, -1, 1, 2), 1),
    ("one-sided 2nd order", (0, 1, 2), 1),
    ("4th-order 2nd deriv", (-2, -1, 0, 1, 2), 2),
]


def table():
    """Regenerate the stencil table of note 03 from first principles."""
    rows = []
    for name, off, d in STENCILS:
        w = weights_vandermonde(off, d)
        m, c = leading_error_term(off, d, w)
        rows.append((name, off, d, w, m, c, m - d))
    return rows


def _main():
    print("Finite-difference weights (units of 1/h^d), Fornberg [S25]")
    print(f"{'stencil':<22}{'offsets':<18}{'d':>2}  weights x 1/h^d"
          f"{'':<14}leading error")
    for name, off, d, w, m, c, order in table():
        ws = ' '.join(str(x) for x in w)
        print(f"{name:<22}{str(tuple(off)):<18}{d:>2}  {ws:<30}"
              f"{c} h^{order} f^({m})   order {order}")
    print("\nVandermonde vs Fornberg agree to machine precision:")
    for name, off, d in STENCILS:
        a = np.array([float(x) for x in weights_vandermonde(off, d)])
        b = weights_fornberg(off, d)[d]
        print(f"  {name:<22} max|diff| = {np.max(np.abs(a - b)):.2e}")


if __name__ == "__main__":
    _main()
