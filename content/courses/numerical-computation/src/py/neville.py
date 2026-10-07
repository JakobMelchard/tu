"""Neville scheme, extrapolation, Lebesgue constants, Hermite interpolation (note 01).

Implements [S4 §1.2, 1.4, 1.6, 1.7]:
  - Aitken-Neville evaluation of the interpolant, O(n^2)        [S4 §1.2, Alg. 1]
  - extrapolation of a difference quotient to h = 0             [S4 §1.4, Thm 1.17]
  - Chebyshev node polynomial and Lebesgue constants            [S4 §1.6, Thm 1.21, 1.24]
  - Hermite interpolation via divided differences on repeated knots [S4 §1.7]
"""
import numpy as np


# ------------------------------------------------------------ Neville scheme
def aitken_neville(xs, fs, t, count_ops=False):
    """p(t) for the polynomial interpolating (xs, fs), by [S4] Alg. 1.

    Overwrites a copy of the data vector column by column:
        f[j] <- ((t - x[j]) f[j+1] - (t - x[j+m]) f[j]) / (x[j+m] - x[j])
    Cost O(n^2) arithmetic operations -- the fact the exams keep asking about.
    With count_ops=True returns (value, number of multiplications/divisions).
    """
    x = np.asarray(xs, float)
    f = np.array(fs, float)
    n = len(x) - 1
    ops = 0
    for m in range(1, n + 1):
        for j in range(0, n - m + 1):
            f[j] = ((t - x[j]) * f[j + 1] - (t - x[j + m]) * f[j]) / (x[j + m] - x[j])
            ops += 3                                   # two products, one division
    return (f[0], ops) if count_ops else f[0]


def neville_tableau(xs, fs, t):
    """Full lower-triangular tableau P[j, m] = p_{j,m}(t), [S4] Thm 1.4.

    P[j, 0] = f_j and P[0, n] is the answer.  Column m holds the values of the
    polynomials of degree m through the knots x_j .. x_{j+m}.
    """
    x = np.asarray(xs, float)
    f = np.asarray(fs, float)
    n = len(x) - 1
    P = np.full((n + 1, n + 1), np.nan)
    P[:, 0] = f
    for m in range(1, n + 1):
        for j in range(0, n - m + 1):
            P[j, m] = ((t - x[j]) * P[j + 1, m - 1]
                       - (t - x[j + m]) * P[j, m - 1]) / (x[j + m] - x[j])
    return P


# ---------------------------------------------------------- extrapolation
def extrapolate_derivative(f, x0, hs, m=None):
    """Approximate f'(x0) by extrapolating D(h) = (f(x0+h) - f(x0))/h to h = 0.

    [S4] sec. 1.4: interpolate the pairs (h_j, D(h_j)) and evaluate at h = 0.
    Returns the full Neville tableau; entry [i, m] uses h_i .. h_{i+m}, and by
    [S4] Thm 1.17 its error is O(h_i^{m+1}) *when f is smooth*.  For
    u(x) = |x|^{3/2} (so D(h) = sqrt(h)) every column stalls at O(sqrt h)
    -- [S4] Ex. 1.18.
    """
    hs = np.asarray(hs, float)
    D = np.array([(f(x0 + h) - f(x0)) / h for h in hs])
    T = neville_tableau(hs, D, 0.0)
    if m is None:
        return T
    return T[:, m]


# ------------------------------------------------- node polynomial, Lebesgue
def omega(xs, t):
    """omega_{n+1}(t) = prod_i (t - x_i), the node polynomial of [S4] Thm 1.15."""
    x = np.asarray(xs, float)
    t = np.asarray(t, float)
    out = np.ones_like(t)
    for xi in x:
        out = out * (t - xi)
    return out


def omega_max(xs, a=-1.0, b=1.0, samples=20001):
    """max |omega_{n+1}| on [a, b], sampled.

    For Chebyshev nodes [S4] Thm 1.21 gives exactly 2*((b-a)/4)^{n+1}.
    """
    t = np.linspace(a, b, samples)
    return float(np.abs(omega(xs, t)).max())


def chebyshev_omega_max(n, a=-1.0, b=1.0):
    """The closed form of [S4] Thm 1.21 for n+1 Chebyshev nodes."""
    return 2.0 * ((b - a) / 4.0) ** (n + 1)


def lebesgue_function(xs, t):
    """sum_i |l_i(t)| -- the function whose maximum is the Lebesgue constant."""
    x = np.asarray(xs, float)
    t = np.asarray(t, float)
    out = np.zeros_like(t)
    for i in range(len(x)):
        li = np.ones_like(t)
        for j in range(len(x)):
            if j != i:
                li = li * (t - x[j]) / (x[i] - x[j])
        out = out + np.abs(li)
    return out


def lebesgue_constant(xs, a=-1.0, b=1.0, samples=20001):
    """Lambda_n = max_x sum_i |l_i(x)|, [S4] (1.21).

    Bounds of [S4] Thm 1.24(ii):
        uniform nodes    Lambda_n ~ 2^n / (e n ln n)      (exponential!)
        Chebyshev nodes  Lambda_n <= (2/pi) ln(n+1) + 1   (logarithmic)
    """
    t = np.linspace(a, b, samples)
    return float(lebesgue_function(xs, t).max())


def chebyshev_lebesgue_bound(n):
    """(2/pi) ln(n+1) + 1, the Chebyshev bound of [S4] Thm 1.24(ii)."""
    return 2.0 / np.pi * np.log(n + 1) + 1.0


# --------------------------------------------------- Hermite interpolation
def _factorial(k):
    out = 1.0
    for i in range(2, k + 1):
        out *= i
    return out


def hermite_divided_differences(xs, derivs):
    """Divided differences for Hermite interpolation, [S4] sec. 1.7.

    xs      distinct knots x_0 .. x_n
    derivs  derivs[i] = [f(x_i), f'(x_i), ..., f^{(d_i)}(x_i)]

    Returns (zs, coeffs): the knot list with x_i repeated d_i+1 times, and the
    Newton coefficients, so that the interpolant is
        p(t) = sum_k coeffs[k] * prod_{j<k} (t - zs[j]),
    of degree n + sum_i d_i.  The interpolation problem [S4] (1.22) is uniquely
    solvable; coincident knots use the limit of [S4] Rem. 1.12,
        f[x_i, ..., x_i]  (k+1 arguments)  =  f^{(k)}(x_i) / k!.
    """
    zs, owner = [], []                       # owner[k] = index into derivs
    for i, (xi, ds) in enumerate(zip(xs, derivs)):
        zs.extend([float(xi)] * len(ds))
        owner.extend([i] * len(ds))
    N = len(zs)
    Q = np.zeros((N, N))
    Q[:, 0] = [derivs[owner[k]][0] for k in range(N)]
    for col in range(1, N):
        for row in range(N - col):
            if zs[row + col] == zs[row]:     # confluent block: use the derivative
                Q[row, col] = derivs[owner[row]][col] / _factorial(col)
            else:
                Q[row, col] = ((Q[row + 1, col - 1] - Q[row, col - 1])
                               / (zs[row + col] - zs[row]))
    return np.array(zs), Q[0, :].copy()


def hermite_eval(zs, coeffs, t):
    """Horner evaluation of the Newton form on the (possibly repeated) knots zs."""
    zs = np.asarray(zs, float)
    t = np.asarray(t, float)
    y = np.full_like(t, coeffs[-1])
    for k in range(len(coeffs) - 2, -1, -1):
        y = coeffs[k] + (t - zs[k]) * y
    return y


def hermite(xs, derivs, t):
    """Convenience wrapper: build and evaluate the Hermite interpolant."""
    zs, c = hermite_divided_differences(xs, derivs)
    return hermite_eval(zs, c, t)


if __name__ == "__main__":
    # --- Neville, [S4] Ex. 1.3 / the F1 2022 exam item -------------------
    xs, fs = [0.0, 1.0, 2.0, 4.0], [1.0, 3.0, 2.0, 5.0]
    val, ops = aitken_neville(xs, fs, 3.0, count_ops=True)
    print(f"Neville p(3) = {val}  (expect 1.5)   ops = {ops}  ~ O(n^2)")
    print("tableau at t=3:\n", np.round(neville_tableau(xs, fs, 3.0), 6))

    print("\n--- cost growth: O(n^2) [S4 Rem. 1.6] ---")
    for n in (4, 8, 16, 32):
        x = np.linspace(0, 1, n + 1)
        _, o = aitken_neville(x, np.sin(x), 0.5, count_ops=True)
        print(f"  n={n:3d}  ops={o:6d}   ops/n^2 = {o / n ** 2:.2f}")

    # --- extrapolation, [S4] Exercise 1.14 and Ex. 1.18 -----------------
    hs = 2.0 ** -np.arange(8)
    T = extrapolate_derivative(np.exp, 0.0, hs)
    print("\nextrapolating D(h) for f = exp at 0 (exact f'(0) = 1), errors:")
    for i in range(5):
        print("  " + "  ".join(f"{abs(T[i, m] - 1):8.2e}" for m in range(i + 1)))
    T2 = extrapolate_derivative(lambda x: abs(x) ** 1.5, 0.0, hs)
    print("same for u = |x|^{3/2} ([S4] Ex. 1.18) -- columns stall at sqrt(h):")
    for i in range(5):
        print("  " + "  ".join(f"{abs(T2[i, m]):8.2e}" for m in range(i + 1)))

    # --- Lebesgue constants, [S4] Thm 1.24 ------------------------------
    print("\nLebesgue constants on [-1,1]:")
    print("   n   uniform      Chebyshev   (2/pi)ln(n+1)+1")
    for n in (5, 10, 15, 20):
        u = lebesgue_constant(np.linspace(-1, 1, n + 1))
        c = lebesgue_constant(np.cos((2 * np.arange(n + 1) + 1) * np.pi / (2 * n + 2)))
        print(f"  {n:3d}  {u:11.3f}  {c:9.3f}  {chebyshev_lebesgue_bound(n):9.3f}")

    # --- node polynomial, [S4] Thm 1.21 ---------------------------------
    print("\n||omega_{n+1}||_inf for Chebyshev nodes vs the closed form 2((b-a)/4)^{n+1}:")
    for n in (3, 6, 9):
        xc = np.cos((2 * np.arange(n + 1) + 1) * np.pi / (2 * n + 2))
        print(f"  n={n}: {omega_max(xc):.8e}  vs  {chebyshev_omega_max(n):.8e}")

    # --- Hermite, the F3 2022 re-test item ------------------------------
    print("\nHermite: value + first derivative at 0 and 1 -> cubic, exact on cubics")
    g = lambda x: 2 * x ** 3 - x + 1
    gp = lambda x: 6 * x ** 2 - 1
    zs, c = hermite_divided_differences([0.0, 1.0],
                                        [[g(0.0), gp(0.0)], [g(1.0), gp(1.0)]])
    tt = np.array([0.0, 0.25, 0.5, 1.0])
    print("  p:", np.round(hermite_eval(zs, c, tt), 12))
    print("  g:", np.round(g(tt), 12), " (identical: 4 conditions fix the cubic)")

    print("\n  Taylor as the degenerate case [S4] Rem. 1.29: one knot, N derivatives")
    zs, c = hermite_divided_differences([0.0], [[1.0, 1.0, 1.0, 1.0]])   # exp at 0
    print("  p(0.3) =", hermite_eval(zs, c, np.array([0.3]))[0],
          " Taylor_3(0.3) =", sum(0.3 ** k / _factorial(k) for k in range(4)))
