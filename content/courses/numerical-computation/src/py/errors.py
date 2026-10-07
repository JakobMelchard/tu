"""Conditioning, stability and floating point (note 04).

Implements [S4 §3.1-3.3]: the error sources (error_sources_fd), the relative
condition number kappa_rel = |phi'(x)| |x| / |phi(x)| (cond_scalar, cond_rel),
and the two stability examples, log(1+x) [S4 Ex. 3.5] and the quadratic
formula [S4 Ex. 3.6].  cond is the matrix condition number of [S4 §4.5].
Machine epsilon, Kahan/pairwise summation and backward error are background,
not in [S4] ([S12], [S13]).  Pure numpy; numpy.linalg only in the tests.
"""
import numpy as np


# ---------------------------------------------------------------- floating point
def machine_epsilon(dtype=np.float64):
    """Smallest eps with fl(1 + eps) > 1, found by halving.  Equals 2^-52 for
    float64 (numpy's finfo.eps); the unit round-off u = eps/2 bounds the
    relative rounding error |fl(x) - x| / |x| <= u."""
    one = dtype(1)
    eps = dtype(1)
    while one + eps / dtype(2) > one:
        eps = eps / dtype(2)
    return eps


def ulp(x, dtype=np.float64):
    """Spacing between x and the next representable number: 2^(e - p + 1)
    with e = floor(log2 |x|), p = 53 for double."""
    x = abs(dtype(x))
    if x == 0:
        return np.finfo(dtype).tiny * np.finfo(dtype).eps
    e = int(np.floor(np.log2(x)))
    return dtype(2.0) ** (e - np.finfo(dtype).nmant)


def rel_error(approx, exact):
    approx, exact = np.asarray(approx, float), np.asarray(exact, float)
    return np.abs(approx - exact) / np.abs(exact)


# ---------------------------------------------------------------- summation
def naive_sum(x, dtype=np.float32):
    """Recursive summation: error bound (n-1) u sum|x_i|."""
    s = dtype(0)
    for v in x:
        s = s + dtype(v)
    return s


def kahan_sum(x, dtype=np.float32):
    """Compensated summation: error bound 2u sum|x_i| + O(n u^2)."""
    s, c = dtype(0), dtype(0)
    for v in x:
        y = dtype(v) - c
        t = s + y
        c = (t - s) - y            # the low-order part lost in t
        s = t
    return s


def pairwise_sum(x, dtype=np.float32):
    """Divide-and-conquer summation: error bound O(log2 n) u sum|x_i|."""
    x = np.asarray(x, dtype=dtype)
    if len(x) <= 8:
        return naive_sum(x, dtype)
    m = len(x) // 2
    return dtype(pairwise_sum(x[:m], dtype) + pairwise_sum(x[m:], dtype))


# ---------------------------------------------------------------- cancellation
def quadratic_roots_naive(a, b, c):
    """x = (-b +- sqrt(b^2 - 4ac)) / 2a: cancellation when b^2 >> 4ac."""
    d = np.sqrt(b * b - 4 * a * c)
    return (-b + d) / (2 * a), (-b - d) / (2 * a)


def quadratic_roots_stable(a, b, c):
    """Compute the root with no cancellation, then the other from x1 x2 = c/a
    (Vieta).  Backward stable."""
    d = np.sqrt(b * b - 4 * a * c)
    q = -0.5 * (b + np.copysign(d, b))
    return q / a, c / q


# ---------------------------------------------------------------- conditioning
def cond_scalar(f, x, h=None):
    """Relative condition number kappa = |x f'(x) / f(x)| of a scalar map,
    f' from a central difference."""
    h = h or 1e-5 * max(1.0, abs(x))
    fp = (f(x + h) - f(x - h)) / (2 * h)
    return abs(x * fp / f(x))


def norm_inf(A):
    """Matrix inf-norm = max absolute row sum (vector: max |x_i|)."""
    A = np.asarray(A, float)
    return np.abs(A).max() if A.ndim == 1 else np.abs(A).sum(axis=1).max()


def norm_1(A):
    A = np.asarray(A, float)
    return np.abs(A).sum() if A.ndim == 1 else np.abs(A).sum(axis=0).max()


def inverse(A):
    """A^{-1} via our own pivoted LU (linsolve.lu_solve), column by column."""
    from linsolve import lu_decompose, lu_solve
    A = np.asarray(A, float)
    n = len(A)
    LU, piv = lu_decompose(A)
    return np.column_stack([lu_solve(LU, piv, e) for e in np.eye(n)])


def cond(A, norm="inf"):
    """kappa(A) = ||A|| ||A^{-1}|| in the 1- or inf-norm."""
    nrm = norm_inf if norm == "inf" else norm_1
    return nrm(A) * nrm(inverse(A))


def forward_backward_error(A, b, x_hat):
    """For an approximate solution x_hat of A x = b:
    residual r = b - A x_hat,
    normwise backward error eta = ||r|| / (||A|| ||x_hat||)  (Rigal-Gaches),
    forward error bound ||x - x_hat|| / ||x|| <= kappa(A) eta  (inf-norm)."""
    A, b, x_hat = (np.asarray(v, float) for v in (A, b, x_hat))
    r = b - A @ x_hat
    eta = norm_inf(r) / (norm_inf(A) * norm_inf(x_hat))
    kappa = cond(A)
    return {"residual": r, "backward_error": eta, "cond": kappa,
            "forward_bound": kappa * eta}


def hilbert(n):
    i = np.arange(1, n + 1)
    return 1.0 / (i[:, None] + i[None, :] - 1)


# ---------------------------------------------------------------- error sources
def error_sources_fd(f, df, x, hs):
    """Total error of the forward difference D_h f = (f(x+h) - f(x)) / h.
    Returns arrays (discretisation estimate ~ h |f''|/2 modelled by the exact
    difference in high precision, round-off ~ 2u|f|/h, and measured total)."""
    u = machine_epsilon() / 2
    hs = np.asarray(hs, float)
    total = np.array([abs((f(x + h) - f(x)) / h - df(x)) for h in hs])
    roundoff = 2 * u * abs(f(x)) / hs
    disc = np.abs(total - roundoff)
    return disc, roundoff, total



# ------------------------------------------ [S4] sec. 3.3: stability examples
def log1p_naive(x):
    """The unstable realisation of [S4] Ex. 3.5: x -> w := 1 + x -> log w.

    The problem is well conditioned (kappa_rel <= 2 near 0) but the second step
    has kappa_rel(w) = 1/|log w| ~ 1/x, so about log10(1/x) digits are lost.
    """
    return np.log(1.0 + np.asarray(x, float))


def log1p_series(x, terms=4):
    """The stable realisation of [S4] Ex. 3.5: the Taylor series of log(1+x).

        log(1+x) = x - x^2/2 + x^3/3 - ...

    For x = 1.234567890123456e-10, [S4] reports the naive route gives 6 correct
    digits and x - x^2/2 gives all 16.
    """
    x = np.asarray(x, float)
    out = np.zeros_like(x)
    for k in range(terms, 0, -1):
        out = out + (-1.0) ** (k + 1) * x ** k / k
    return out


def cond_rel(f, fprime, x):
    """kappa_rel(x) = |f'(x)| |x| / |f(x)|,  [S4] Def. 3.1."""
    x = np.asarray(x, float)
    return np.abs(fprime(x)) * np.abs(x) / np.abs(f(x))


if __name__ == "__main__":
    eps = machine_epsilon()
    print(f"machine eps (float64) = {eps:.3e}  = 2^{int(np.log2(eps))}")
    print(f"machine eps (float32) = {machine_epsilon(np.float32):.3e}")
    print(f"ulp(1.0) = {ulp(1.0):.3e}, ulp(1e10) = {ulp(1e10):.3e}")

    x = np.full(10 ** 6, 0.1)
    print("\nsum of 1e6 * 0.1 in float32:")
    for name, fn in (("naive", naive_sum), ("kahan", kahan_sum),
                     ("pairwise", pairwise_sum)):
        s = fn(x)
        print(f"  {name:9s} {s:.6f}  rel err {rel_error(float(s), 1e5):.2e}")

    print("\nquadratic x^2 - 1e8 x + 1 = 0 (roots ~ 1e8 and 1e-8):")
    print("  naive :", quadratic_roots_naive(1.0, -1e8, 1.0))
    print("  stable:", quadratic_roots_stable(1.0, -1e8, 1.0))

    print("\ncondition of f(x) = 1 - cos(x) near 0:")
    for xv in (1.0, 1e-2, 1e-4):
        print(f"  x={xv:g}: kappa = {cond_scalar(lambda t: 1 - np.cos(t), xv):.3f}"
              f"  (analytic x sin x /(1-cos x) -> 2)")

    print("\nHilbert matrices, kappa_inf:")
    for n in (3, 5, 8):
        print(f"  n={n}: {cond(hilbert(n)):.3e}")

    A = hilbert(6)
    x_true = np.ones(6)
    b = A @ x_true
    x_hat = inverse(A) @ b
    r = forward_backward_error(A, b, x_hat)
    print(f"\nHilbert(6) solve: backward err {r['backward_error']:.1e}, "
          f"actual fwd err {norm_inf(x_hat - x_true):.1e}, "
          f"bound {r['forward_bound']:.1e}")

    print("\nforward difference of sin at 1, total error vs h:")
    hs = 10.0 ** -np.arange(1, 17)
    disc, ro, tot = error_sources_fd(np.sin, np.cos, 1.0, hs)
    for h, t in zip(hs, tot):
        print(f"  h=1e{int(np.log10(h)):3d}  err={t:.2e}")
    print(f"  optimal h ~ sqrt(u) = {np.sqrt(eps / 2):.1e}")
