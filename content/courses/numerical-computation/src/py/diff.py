"""Numerical differentiation: difference quotients, stencils, Richardson (note 12).

[S4] has no differentiation chapter.  It treats difference quotients only as
the prime application of Neville extrapolation to h = 0, [S4 §1.4] (Thm 1.17,
Ex. 1.18); that part is neville.extrapolate_derivative.  This module is the
background around it: one-sided and central quotients, stencil weights for any
derivative by a Vandermonde solve (Fornberg), the truncation/round-off optimum
h ~ u^(1/(p+1)), and a Richardson tableau.
"""
import numpy as np


def forward_diff(f, x, h):
    """(f(x+h) - f(x))/h = f'(x) + h/2 f''(xi).  Order 1."""
    return (f(x + h) - f(x)) / h


def backward_diff(f, x, h):
    return (f(x) - f(x - h)) / h


def central_diff(f, x, h):
    """(f(x+h) - f(x-h))/(2h) = f'(x) + h^2/6 f'''(xi).  Order 2."""
    return (f(x + h) - f(x - h)) / (2 * h)


def second_diff(f, x, h):
    """(f(x+h) - 2f(x) + f(x-h))/h^2 = f''(x) + h^2/12 f''''(xi).  Order 2.
    Round-off ~ 4u|f|/h^2, so h_opt ~ u^(1/4)."""
    return (f(x + h) - 2 * f(x) + f(x - h)) / h ** 2


def fd_weights(offsets, m):
    """Weights w_j such that sum_j w_j f(x + s_j h) = h^m f^(m)(x) + O(h^(n-m)).
    Solve the Vandermonde system  sum_j w_j s_j^k / k! = delta_{k,m}, k = 0..n-1
    (Taylor expansion matching).  offsets s_j are stencil points in units of h."""
    from linsolve import solve
    s = np.asarray(offsets, float)
    n = len(s)
    fact = np.array([_fact(k) for k in range(n)], float)
    V = np.array([s ** k / fact[k] for k in range(n)])
    rhs = np.zeros(n)
    rhs[m] = 1.0
    return solve(V, rhs)


def _fact(k):
    r = 1
    for i in range(2, k + 1):
        r *= i
    return r


def optimal_h(order, f_scale=1.0, u=np.finfo(float).eps / 2):
    """Balance truncation C h^p against round-off u|f|/h: h_opt ~ u^(1/(p+1)).
    order 1 -> sqrt(u) ~ 1e-8, order 2 -> u^(1/3) ~ 6e-6."""
    return (u * f_scale) ** (1.0 / (order + 1))


def richardson(D, h, p=2, levels=4, ratio=2.0):
    """Richardson extrapolation for an approximation D(h) = L + c1 h^p + c2 h^(2p) + ...
    (even expansion, as for central differences).  Tableau
        T[i,0] = D(h / r^i),
        T[i,j] = T[i,j-1] + (T[i,j-1] - T[i-1,j-1]) / (r^(j p) - 1).
    Returns the tableau; T[-1,-1] is the best estimate, order p (levels)."""
    T = np.zeros((levels, levels))
    for i in range(levels):
        T[i, 0] = D(h / ratio ** i)
        for j in range(1, i + 1):
            T[i, j] = T[i, j - 1] + (T[i, j - 1] - T[i - 1, j - 1]) / (ratio ** (j * p) - 1)
    return T


def gradient_fd(f, x, h=None):
    """Central-difference gradient of a scalar field f: R^n -> R."""
    x = np.asarray(x, float)
    h = optimal_h(2) if h is None else h
    g = np.zeros_like(x)
    for i in range(len(x)):
        e = np.zeros_like(x)
        e[i] = h * max(1.0, abs(x[i]))
        g[i] = (f(x + e) - f(x - e)) / (2 * e[i])
    return g


if __name__ == "__main__":
    f, df, x = np.exp, np.exp, 1.0
    print(" h        forward      central      second-deriv")
    for h in 10.0 ** -np.arange(1, 11):
        e1 = abs(forward_diff(f, x, h) - df(x))
        e2 = abs(central_diff(f, x, h) - df(x))
        e3 = abs(second_diff(f, x, h) - df(x))
        print(f"{h:.0e}  {e1:.2e}    {e2:.2e}    {e3:.2e}")
    print(f"optimal h: order 1 -> {optimal_h(1):.1e}, order 2 -> {optimal_h(2):.1e}, "
          f"2nd derivative -> {np.finfo(float).eps ** 0.25:.1e}")

    print("\nRichardson on the central difference of exp at 1, h = 0.5:")
    T = richardson(lambda h: central_diff(np.exp, 1.0, h), 0.5, p=2, levels=5)
    for i in range(5):
        print("  " + "  ".join(f"{T[i, j] - np.e:+.2e}" for j in range(i + 1)))

    print("\nFD weights, 5-point central first derivative:", fd_weights([-2, -1, 0, 1, 2], 1) * 12)
    print("FD weights, one-sided 2nd order f'         :", fd_weights([0, 1, 2], 1) * 2)
    print("FD weights, 3-point second derivative       :", fd_weights([-1, 0, 1], 2))
