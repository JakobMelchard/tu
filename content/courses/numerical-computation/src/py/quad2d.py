"""Quadrature on the unit square and the reference triangle (note 03).

Implements [S4 §2.6]: the reference square S = (0,1)^2 by tensor products, the
reference triangle T = {0<x<1, 0<y<1-x} by direct construction or by the Duffy
transformation of the square.
"""
import numpy as np

from quad import gauss_legendre


# ------------------------------------------------------------------ square
def tensor_square(f, n, rule="gauss"):
    """Q^2D(F) = sum_{i,j} w_i w_j F(x_i, x_j) on (0,1)^2,  [S4] (2.16).

    n-point 1-D rule per direction.  By [S4] Exercise 2.21, if the 1-D rule is
    exact on P_p then this is exact on span{x^i y^j : i, j <= p} -- the *tensor*
    space, not the bivariate polynomials of total degree p.
    """
    x, w = _rule_01(n, rule)
    X, Y = np.meshgrid(x, x, indexing="ij")
    W = np.outer(w, w)
    return float((W * f(X, Y)).sum())


def _rule_01(n, rule):
    """n-point rule on [0, 1]."""
    if rule == "gauss":
        xg, wg = gauss_legendre(n)                    # on [-1, 1]
        return 0.5 * (xg + 1.0), 0.5 * wg
    if rule == "midpoint":
        x = (np.arange(n) + 0.5) / n
        return x, np.full(n, 1.0 / n)
    if rule == "trapezoid":
        x = np.linspace(0.0, 1.0, n)
        w = np.full(n, 1.0 / (n - 1))
        w[0] = w[-1] = 0.5 / (n - 1)
        return x, w
    raise ValueError(rule)


# ---------------------------------------------------------------- triangle
def barycentre_triangle(f):
    """One-point rule at the barycentre of T with weight |T| = 1/2.

    [S4] Exercise 2.22: exact for degree 0 by construction, and in fact for
    degree 1, since int_T x = int_T y = 1/6 = (1/2)(1/3).
    """
    return 0.5 * float(f(1.0 / 3.0, 1.0 / 3.0))


def vertex_triangle(f):
    """Three-point rule at the vertices of T, weights 1/6 each.

    [S4] Exercise 2.22, second part: also exact on P_1.
    """
    pts = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    return sum(f(x, y) for x, y in pts) / 6.0


def duffy_triangle(f, n, rule="gauss"):
    """Map the square onto the triangle, [S4] Ex. 2.23.

        int_T F = int_0^1 int_0^1 F(x, (1-x) eta) (1-x) d eta dx

    so a square rule with points (x_i, y_i) and weights w_i becomes
        sum_i w_i (1 - x_i) F(x_i, (1 - x_i) y_i).
    The (1-x) Jacobian makes a polynomial integrand non-polynomial in the new
    variables, which is why dedicated triangle rules exist.
    """
    x, w = _rule_01(n, rule)
    X, Y = np.meshgrid(x, x, indexing="ij")
    W = np.outer(w, w)
    return float((W * (1.0 - X) * f(X, (1.0 - X) * Y)).sum())


# -------------------------------------------------------------- exactness
def monomial_integral_square(i, j):
    """int_{(0,1)^2} x^i y^j = 1/((i+1)(j+1))."""
    return 1.0 / ((i + 1) * (j + 1))


def monomial_integral_triangle(i, j):
    """int_T x^i y^j = i! j! / (i+j+2)!  on the unit triangle."""
    from math import factorial
    return factorial(i) * factorial(j) / factorial(i + j + 2)


def exactness_degree_2d(rule, domain="square", maxdeg=8, tol=1e-11):
    """Largest total degree d with rule(x^i y^j) exact for all i + j <= d."""
    exact = (monomial_integral_square if domain == "square"
             else monomial_integral_triangle)
    for d in range(maxdeg + 1):
        for i in range(d + 1):
            j = d - i
            got = rule(lambda x, y, i=i, j=j: x ** i * y ** j)
            if abs(got - exact(i, j)) > tol * max(1.0, abs(exact(i, j))):
                return d - 1
    return maxdeg


if __name__ == "__main__":
    print("--- square: tensor Gauss [S4 (2.16), Exercise 2.21] ---")
    for n in (1, 2, 3, 4):
        rule = lambda f, n=n: tensor_square(f, n)
        print(f"  n={n} per direction: total-degree exactness {exactness_degree_2d(rule)}"
              f"   (1-D exactness {2 * n - 1}, tensor x^{n and 2*n-1} y^{2*n-1})")
    val = tensor_square(lambda x, y: np.exp(x + y), 8)
    print("  int_S exp(x+y) =", val, " exact (e-1)^2 =", (np.e - 1) ** 2)

    print("\n--- triangle [S4 Exercise 2.22, Ex. 2.23] ---")
    print("  barycentre rule, exactness:", exactness_degree_2d(barycentre_triangle, "triangle"))
    print("  vertex rule,     exactness:", exactness_degree_2d(vertex_triangle, "triangle"))
    for n in (2, 4, 8):
        rule = lambda f, n=n: duffy_triangle(f, n)
        print(f"  Duffy with {n}x{n} Gauss, exactness: {exactness_degree_2d(rule, 'triangle')}")
    print("  int_T 1 =", barycentre_triangle(lambda x, y: 1.0 + 0 * x), "(area 1/2)")
    print("  int_T x =", barycentre_triangle(lambda x, y: x), "(exact 1/6)")
    ex = np.exp(1) - 2
    print("  int_T exp(x) via Duffy(16):", duffy_triangle(lambda x, y: np.exp(x), 16),
          " exact e - 2 =", ex)
