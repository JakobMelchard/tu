"""Polynomial interpolation, splines, discrete least squares (note 01).

Implements [S4 §1.1] Lagrange form (lagrange_basis, lagrange_eval, vandermonde),
[S4 §1.3] (CSE) Newton form by divided differences, [S4 §1.6] Chebyshev nodes
and the Runge function, [S4 §1.8] (CSE) cubic splines via the Thomas algorithm,
and polynomial least squares by [S4 §5.1] normal equations and [S4 §5.2] QR.
Barycentric evaluation and discrete orthogonal polynomials are background.
The Neville scheme [S4 §1.2] and Hermite [S4 §1.7] are in neville.py.
"""
import numpy as np


# ---------------------------------------------------------------- Lagrange
def lagrange_basis(xs, j, t):
    """l_j(t) = prod_{m != j} (t - x_m)/(x_j - x_m)."""
    xs = np.asarray(xs, float)
    t = np.asarray(t, float)
    out = np.ones_like(t)
    for m, xm in enumerate(xs):
        if m != j:
            out *= (t - xm) / (xs[j] - xm)
    return out


def lagrange_eval(xs, ys, t):
    """p(t) = sum_j y_j l_j(t).  O(n^2) per evaluation point."""
    return sum(y * lagrange_basis(xs, j, t) for j, y in enumerate(ys))


def barycentric_weights(xs):
    """w_j = 1 / prod_{m != j} (x_j - x_m); barycentric form
    p(t) = sum_j w_j y_j/(t-x_j) / sum_j w_j/(t-x_j) costs O(n) per point."""
    xs = np.asarray(xs, float)
    w = np.ones(len(xs))
    for j in range(len(xs)):
        for m in range(len(xs)):
            if m != j:
                w[j] /= xs[j] - xs[m]
    return w


def barycentric_eval(xs, ys, t):
    xs, ys, t = (np.asarray(v, float) for v in (xs, ys, t))
    w = barycentric_weights(xs)
    out = np.empty_like(t)
    for i, ti in enumerate(t.ravel()):
        hit = np.where(xs == ti)[0]
        if len(hit):
            out.flat[i] = ys[hit[0]]
        else:
            q = w / (ti - xs)
            out.flat[i] = (q @ ys) / q.sum()
    return out


# ---------------------------------------------------------------- Newton
def divided_differences(xs, ys):
    """Table column by column: f[x_i..x_{i+k}] = (f[x_{i+1}..] - f[x_i..]) / (x_{i+k} - x_i).
    Returns the coefficients c_k = f[x_0..x_k] of
    p(t) = c_0 + c_1 (t-x_0) + c_2 (t-x_0)(t-x_1) + ...  O(n^2)."""
    xs = np.asarray(xs, float)
    c = np.array(ys, float)
    n = len(xs)
    for k in range(1, n):
        c[k:] = (c[k:] - c[k - 1:-1]) / (xs[k:] - xs[:n - k])
    return c


def newton_eval(xs, coef, t):
    """Horner-like nested evaluation of the Newton form, O(n) per point."""
    t = np.asarray(t, float)
    p = np.full_like(t, coef[-1])
    for k in range(len(coef) - 2, -1, -1):
        p = p * (t - xs[k]) + coef[k]
    return p


def chebyshev_nodes(n, a=-1.0, b=1.0):
    """Roots of T_n mapped to [a, b]: x_k = cos((2k+1) pi/(2n)).  They minimise
    max |prod (t - x_k)| = 2^(1-n) on [-1, 1] (vs. exponential growth for
    equispaced nodes) and keep the Lebesgue constant at O(log n)."""
    k = np.arange(n)
    x = np.cos((2 * k + 1) * np.pi / (2 * n))
    return np.sort(0.5 * (b - a) * x + 0.5 * (a + b))


def runge(x):
    return 1.0 / (1.0 + 25.0 * x * x)


# ---------------------------------------------------------------- splines
def thomas(lower, diag, upper, rhs):
    """Tridiagonal solve in O(n) (no pivoting; fine for diagonally dominant)."""
    n = len(diag)
    c, d = np.array(upper, float), np.array(rhs, float)
    b = np.array(diag, float)
    for i in range(1, n):
        m = lower[i - 1] / b[i - 1]
        b[i] -= m * c[i - 1]
        d[i] -= m * d[i - 1]
    x = np.zeros(n)
    x[-1] = d[-1] / b[-1]
    for i in range(n - 2, -1, -1):
        x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
    return x


def cubic_spline(xs, ys, bc="natural", dy0=0.0, dyn=0.0):
    """Cubic spline s with s in C^2, s(x_i) = y_i.  Unknowns are the second
    derivatives M_i; continuity of s' gives the tridiagonal system
        h_{i-1} M_{i-1} + 2(h_{i-1}+h_i) M_i + h_i M_{i+1} = 6 (d_i - d_{i-1}),
    d_i = (y_{i+1}-y_i)/h_i.  natural: M_0 = M_n = 0; clamped: s'(a)=dy0, s'(b)=dyn.
    Returns (xs, ys, M).  Error O(h^4) for clamped/smooth f."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    n = len(xs) - 1
    h = np.diff(xs)
    d = np.diff(ys) / h
    lower = h[:-1].copy()
    diag = 2 * (h[:-1] + h[1:])
    upper = h[1:].copy()
    rhs = 6 * np.diff(d)
    if bc == "natural":
        M = np.zeros(n + 1)
        M[1:n] = thomas(lower, diag, upper, rhs)
    elif bc == "clamped":
        # extra rows: 2 h_0 M_0 + h_0 M_1 = 6 (d_0 - dy0),  h_{n-1} M_{n-1} + 2 h_{n-1} M_n = 6 (dyn - d_{n-1})
        diag = np.concatenate([[2 * h[0]], diag, [2 * h[-1]]])
        rhs = np.concatenate([[6 * (d[0] - dy0)], rhs, [6 * (dyn - d[-1])]])
        M = thomas(h, diag, h, rhs)
    else:
        raise ValueError(bc)
    return xs, ys, M


def spline_eval(spl, t):
    """s(t) on [x_i, x_{i+1}] from M_i, M_{i+1} (standard form)."""
    xs, ys, M = spl
    t = np.asarray(t, float)
    i = np.clip(np.searchsorted(xs, t) - 1, 0, len(xs) - 2)
    h = xs[i + 1] - xs[i]
    a, b = xs[i + 1] - t, t - xs[i]
    return (M[i] * a ** 3 + M[i + 1] * b ** 3) / (6 * h) \
        + (ys[i] / h - M[i] * h / 6) * a + (ys[i + 1] / h - M[i + 1] * h / 6) * b


# ---------------------------------------------------------------- least squares
def vandermonde(xs, deg):
    xs = np.asarray(xs, float)
    return np.array([xs ** k for k in range(deg + 1)]).T


def lstsq_normal(A, b):
    """Minimise ||A x - b||_2 via A^T A x = A^T b (Cholesky).  Squares the
    condition number: kappa(A^T A) = kappa(A)^2."""
    from linsolve import cholesky, cholesky_solve
    A, b = np.asarray(A, float), np.asarray(b, float)
    return cholesky_solve(cholesky(A.T @ A), A.T @ b)


def lstsq_qr(A, b):
    """Minimise ||A x - b||_2 via Householder QR: R x = Q^T b (backward stable)."""
    from qr_svd import qr_solve
    return qr_solve(A, b)


def polyfit(xs, ys, deg, method="qr"):
    A = vandermonde(xs, deg)
    return lstsq_qr(A, ys) if method == "qr" else lstsq_normal(A, ys)


def polyval(c, t):
    """Horner for c_0 + c_1 t + ... ."""
    t = np.asarray(t, float)
    p = np.zeros_like(t)
    for ck in c[::-1]:
        p = p * t + ck
    return p


def orthogonal_polys(xs, deg, w=None):
    """Discrete orthogonal polynomials for the inner product <f,g> = sum w_i f(x_i) g(x_i),
    built by the Stieltjes three-term recurrence
        p_{k+1}(x) = (x - a_k) p_k(x) - b_k p_{k-1}(x),
        a_k = <x p_k, p_k>/<p_k, p_k>,  b_k = <p_k,p_k>/<p_{k-1},p_{k-1}>.
    Returns matrix P[i, k] = p_k(x_i), and (a, b).  The least-squares fit in
    this basis needs no linear solve: c_k = <f, p_k>/<p_k, p_k>."""
    xs = np.asarray(xs, float)
    w = np.ones_like(xs) if w is None else np.asarray(w, float)
    P = np.zeros((len(xs), deg + 1))
    P[:, 0] = 1.0
    a, b = np.zeros(deg + 1), np.zeros(deg + 1)
    for k in range(deg):
        pk = P[:, k]
        nk = w @ (pk * pk)
        a[k] = (w @ (xs * pk * pk)) / nk
        if k > 0:
            b[k] = nk / (w @ (P[:, k - 1] ** 2))
        P[:, k + 1] = (xs - a[k]) * pk - (b[k] * P[:, k - 1] if k > 0 else 0)
    return P, (a, b)


def orthogonal_lstsq(xs, ys, deg, w=None):
    """Least-squares polynomial of degree `deg` in the orthogonal basis.
    Returns fitted values at xs and the coefficients."""
    P, _ = orthogonal_polys(xs, deg, w)
    w = np.ones(len(xs)) if w is None else np.asarray(w, float)
    c = np.array([(w * ys) @ P[:, k] / (w @ P[:, k] ** 2) for k in range(deg + 1)])
    return P @ c, c


if __name__ == "__main__":
    xs = np.array([0.0, 1.0, 2.0, 4.0])
    ys = np.array([1.0, 3.0, 2.0, 5.0])
    c = divided_differences(xs, ys)
    t = np.linspace(0, 4, 5)
    print("divided differences:", c)
    print("Newton form  :", newton_eval(xs, c, t))
    print("Lagrange form:", lagrange_eval(xs, ys, t))
    print("barycentric  :", barycentric_eval(xs, ys, t))

    tt = np.linspace(-1, 1, 2001)
    print("\nRunge function 1/(1+25x^2), max interpolation error:")
    print("  n   equispaced   Chebyshev    spline(equi)")
    for n in (5, 9, 13, 17, 21):
        xe = np.linspace(-1, 1, n)
        xc = chebyshev_nodes(n)
        ee = np.max(np.abs(barycentric_eval(xe, runge(xe), tt) - runge(tt)))
        ec = np.max(np.abs(barycentric_eval(xc, runge(xc), tt) - runge(tt)))
        es = np.max(np.abs(spline_eval(cubic_spline(xe, runge(xe)), tt) - runge(tt)))
        print(f"  {n:2d}  {ee:.2e}     {ec:.2e}     {es:.2e}")

    rng = np.random.default_rng(1)
    x = np.linspace(0, 1, 50)
    y = 1 + 2 * x - 3 * x ** 2 + 0.01 * rng.standard_normal(50)
    print("\nleast squares fit deg 2 (true 1, 2, -3):")
    print("  QR     :", polyfit(x, y, 2, "qr"))
    print("  normal :", polyfit(x, y, 2, "normal"))
    fit, coef = orthogonal_lstsq(x, y, 2)
    print("  orthogonal basis, same fitted values?", np.allclose(fit, polyval(polyfit(x, y, 2), x)))
    from qr_svd import jacobi_svd
    sv = jacobi_svd(vandermonde(x, 12))[1]
    print(f"  kappa_2(V_12) = {sv[0] / sv[-1]:.1e}, kappa_2(V^T V) = {(sv[0] / sv[-1]) ** 2:.1e}")
