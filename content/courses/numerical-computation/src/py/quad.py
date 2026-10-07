"""Newton-Cotes, Romberg, adaptive and Gaussian quadrature (note 03).

Implements [S4 §2.1] Newton-Cotes weights and the composite midpoint,
trapezoidal and Simpson rules (error [S4 Thm 2.8]), [S4 §2.2] Romberg,
[S4 §2.3] graded meshes and the adaptive trapezoidal rule (Alg. 5),
[S4 §2.4] Gauss-Legendre with nodes by Newton on the three-term recurrence, and
[S4 §2.7] (CSE) weighted Gauss rules (Chebyshev, Jacobi via Golub-Welsch).
Adaptive Simpson is background.
"""
import numpy as np


# ---------------------------------------------------------------- Newton-Cotes
def newton_cotes_weights(n):
    """Closed Newton-Cotes weights on n+1 equispaced nodes of [0, 1]:
    integrate the Lagrange basis exactly by solving the moment equations
    sum_j w_j x_j^k = 1/(k+1), k = 0..n.  n=1 trapezoid, 2 Simpson, 3 3/8 rule.
    Negative weights appear from n = 8 -> not convergent for large n."""
    from linsolve import solve
    x = np.linspace(0, 1, n + 1)
    V = np.array([x ** k for k in range(n + 1)])
    return solve(V, 1.0 / np.arange(1, n + 2))


def newton_cotes(f, a, b, n):
    w = newton_cotes_weights(n)
    x = np.linspace(a, b, n + 1)
    return (b - a) * (w @ f(x))


# ---------------------------------------------------------------- composite
def midpoint(f, a, b, n):
    """Composite midpoint, error (b-a) h^2 f''/24."""
    h = (b - a) / n
    x = a + h * (np.arange(n) + 0.5)
    return h * np.sum(f(x))


def trapezoid(f, a, b, n):
    """Composite trapezoid, error -(b-a) h^2 f''/12.  Spectrally accurate
    for periodic smooth integrands (Euler-Maclaurin)."""
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    fx = f(x)
    return h * (0.5 * fx[0] + fx[1:-1].sum() + 0.5 * fx[-1])


def simpson(f, a, b, n):
    """Composite Simpson (n even), error -(b-a) h^4 f''''/180."""
    if n % 2:
        raise ValueError("n must be even")
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    fx = f(x)
    return h / 3 * (fx[0] + 4 * fx[1:-1:2].sum() + 2 * fx[2:-1:2].sum() + fx[-1])


# ---------------------------------------------------------------- Gauss
def legendre(n, x):
    """P_n(x) and P_n'(x) by the three-term recurrence
    (k+1) P_{k+1} = (2k+1) x P_k - k P_{k-1}."""
    p0, p1 = np.ones_like(x), x
    if n == 0:
        return p0, np.zeros_like(x)
    for k in range(1, n):
        p0, p1 = p1, ((2 * k + 1) * x * p1 - k * p0) / (k + 1)
    dp = n * (x * p1 - p0) / (x * x - 1)
    return p1, dp


def gauss_legendre(n):
    """Nodes = roots of P_n (Newton from the Chebyshev-like initial guess
    cos(pi (i - 1/4)/(n + 1/2))), weights w_i = 2 / ((1 - x_i^2) P_n'(x_i)^2).
    Exact for polynomials of degree 2n-1."""
    x = np.cos(np.pi * (np.arange(1, n + 1) - 0.25) / (n + 0.5))
    for _ in range(100):
        p, dp = legendre(n, x)
        dx = p / dp
        x -= dx
        if np.max(np.abs(dx)) < 1e-15:
            break
    _, dp = legendre(n, x)
    w = 2.0 / ((1 - x * x) * dp * dp)
    order = np.argsort(x)
    return x[order], w[order]


def gauss_quad(f, a, b, n):
    x, w = gauss_legendre(n)
    t = 0.5 * (b - a) * x + 0.5 * (b + a)
    return 0.5 * (b - a) * (w @ f(t))


# ---------------------------------------------------------------- Romberg
def romberg(f, a, b, levels=6):
    """Richardson extrapolation of the trapezoid rule (error expansion in h^2
    by Euler-Maclaurin):  T[i,j] = T[i,j-1] + (T[i,j-1] - T[i-1,j-1]) / (4^j - 1).
    T[1,1] is Simpson, T[2,2] Boole.  Returns the tableau."""
    T = np.zeros((levels, levels))
    n = 1
    T[0, 0] = trapezoid(f, a, b, 1)
    for i in range(1, levels):
        n *= 2
        h = (b - a) / n
        # reuse: T_{2n} = T_n / 2 + h * sum of new midpoints
        new = a + h * np.arange(1, n, 2)
        T[i, 0] = 0.5 * T[i - 1, 0] + h * np.sum(f(new))
        for j in range(1, i + 1):
            T[i, j] = T[i, j - 1] + (T[i, j - 1] - T[i - 1, j - 1]) / (4 ** j - 1)
    return T


# ---------------------------------------------------------------- adaptive
def adaptive_simpson(f, a, b, tol=1e-10, maxdepth=50):
    """Recursive Simpson: accept S(a,m) + S(m,b) when
    |S_left + S_right - S_whole| < 15 tol (the 1/15 comes from the h^4 error
    expansion), else subdivide with tol/2 per half.  Returns (I, evaluations)."""
    counter = [0]

    def S(fa, fm, fb, a, b):
        return (b - a) / 6 * (fa + 4 * fm + fb)

    def rec(a, b, fa, fm, fb, whole, tol, depth):
        m = 0.5 * (a + b)
        lm, rm = 0.5 * (a + m), 0.5 * (m + b)
        flm, frm = f(lm), f(rm)
        counter[0] += 2
        left, right = S(fa, flm, fm, a, m), S(fm, frm, fb, m, b)
        if depth >= maxdepth or abs(left + right - whole) <= 15 * tol:
            return left + right + (left + right - whole) / 15      # Richardson
        return (rec(a, m, fa, flm, fm, left, tol / 2, depth + 1)
                + rec(m, b, fm, frm, fb, right, tol / 2, depth + 1))

    fa, fm, fb = f(a), f(0.5 * (a + b)), f(b)
    counter[0] += 3
    return rec(a, b, fa, fm, fb, S(fa, fm, fb, a, b), tol, 0), counter[0]



# ------------------------------------------- [S4] sec. 2.3 and 2.7 additions
def adaptive_trapezoid(f, a, b, tau, rho=0.5, hmin=1e-10):
    """[S4] Alg. 5 verbatim: estimate the trapezoidal error with Simpson.

    Returns (value, number of function evaluations).  Unlike the usual adaptive
    Simpson, this compares T([a,b]) against S([a,b]) on the *same* interval and
    bisects when they disagree by more than rho * tau.
    """
    count = [0]

    def ev(x):
        count[0] += 1
        return f(x)

    def rec(a, b, tau):
        m = 0.5 * (a + b)
        fa, fm, fb = ev(a), ev(m), ev(b)
        T = (b - a) * 0.5 * (fa + fb)
        S = (b - a) / 6.0 * (fa + 4 * fm + fb)
        if (b - a) <= hmin:
            return S                                  # forced termination
        if abs(S - T) <= rho * tau:
            return S
        return rec(a, m, tau / 2) + rec(m, b, tau / 2)

    return rec(a, b, tau), count[0]


def graded_mesh(N, beta=2.0, a=0.0, b=1.0):
    """x_i = a + (b-a)(i/N)^beta,  the mesh of [S4] Ex. 2.12.

    Refined towards a.  For int_0^1 x^0.1 the uniform mesh gives O(N^{-1.1});
    beta = 2 restores O(N^{-2}).
    """
    return a + (b - a) * (np.arange(N + 1) / N) ** beta


def composite_trapezoid_mesh(f, xs):
    """Composite trapezoidal rule on an arbitrary mesh, [S4] Thm 2.8 notation."""
    xs = np.asarray(xs, float)
    fx = np.array([f(x) for x in xs])
    return float(np.sum(0.5 * np.diff(xs) * (fx[:-1] + fx[1:])))


def gauss_chebyshev(n):
    """n-point Gauss rule for the weight (1-x^2)^{-1/2} on (-1, 1).

    The Jacobi case alpha = beta = -1/2 of [S4] sec. 2.7.1, where everything is
    explicit: x_i = cos((2i+1) pi / (2n)), w_i = pi/n.  Exact on P_{2n-1} for
    the weighted integral int_{-1}^{1} f(x) / sqrt(1-x^2) dx.
    """
    i = np.arange(n)
    x = np.cos((2 * i + 1) * np.pi / (2 * n))
    return np.sort(x), np.full(n, np.pi / n)


def gauss_jacobi(n, alpha=0.0, beta=0.0):
    """n-point Gauss rule for the weight (1-x)^alpha (1+x)^beta on (-1, 1).

    [S4] Thm 2.26 and sec. 2.7.1.  alpha = beta = 0 is Legendre and
    alpha = beta = -1/2 is Chebyshev (use gauss_chebyshev for that one, where a
    closed form exists).  Computed with Golub-Welsch: the nodes are the
    eigenvalues of the symmetric tridiagonal Jacobi matrix built from the
    three-term recurrence of [S4] Lem. 2.24-2.25, and the weights come from the
    first components of its eigenvectors.
    """
    from scipy.special import gammaln
    if abs(alpha + 0.5) < 1e-14 and abs(beta + 0.5) < 1e-14:
        return gauss_chebyshev(n)
    ab = alpha + beta
    if ab <= -1.0 + 1e-12:
        raise ValueError("gauss_jacobi needs alpha + beta > -1 "
                         "(use gauss_chebyshev for alpha = beta = -1/2)")
    k = np.arange(n, dtype=float)
    a = np.empty(n)
    a[0] = (beta - alpha) / (ab + 2.0)
    kk = k[1:]
    a[1:] = (beta ** 2 - alpha ** 2) / ((2 * kk + ab) * (2 * kk + ab + 2.0))
    num = 4.0 * kk * (kk + alpha) * (kk + beta) * (kk + ab)
    den = (2 * kk + ab) ** 2 * (2 * kk + ab + 1.0) * (2 * kk + ab - 1.0)
    J = np.diag(a) + np.diag(np.sqrt(num / den), 1) + np.diag(np.sqrt(num / den), -1)
    x, V = np.linalg.eigh(J)
    mu0 = np.exp((ab + 1.0) * np.log(2.0) + gammaln(alpha + 1.0) + gammaln(beta + 1.0)
                 - gammaln(ab + 2.0))
    w = mu0 * V[0, :] ** 2
    order = np.argsort(x)
    return x[order], w[order]


if __name__ == "__main__":
    f, a, b, exact = np.exp, 0.0, 1.0, np.e - 1
    print("int_0^1 e^x dx = e - 1: errors")
    print("  n   midpoint    trapezoid   simpson     gauss")
    for n in (2, 4, 8, 16):
        print(f"  {n:2d}  {abs(midpoint(f, a, b, n) - exact):.2e}   "
              f"{abs(trapezoid(f, a, b, n) - exact):.2e}   "
              f"{abs(simpson(f, a, b, n) - exact):.2e}   "
              f"{abs(gauss_quad(f, a, b, n) - exact):.2e}")
    print("Newton-Cotes weights n=2 (Simpson) * 6:", newton_cotes_weights(2) * 6)
    print("Newton-Cotes weights n=8, min:", newton_cotes_weights(8).min(), "(negative!)")
    x, w = gauss_legendre(3)
    print("Gauss-Legendre n=3 nodes:", x, "weights:", w)
    print("  sum w =", w.sum(), " exact for x^4?", abs(w @ x ** 4 - 0.4) < 1e-14,
          " x^6?", abs(w @ x ** 6 - 2 / 7) < 1e-14)

    T = romberg(f, a, b, 5)
    print("Romberg diagonal errors:", [f"{abs(T[i, i] - exact):.1e}" for i in range(5)])

    g = lambda x: np.sqrt(np.abs(x))  # cusp at 0
    I, nev = adaptive_simpson(g, -1, 2, tol=1e-9)
    print(f"adaptive Simpson int_-1^2 sqrt|x| = {I:.12f}, exact {2/3 + 2/3*2**1.5:.12f}, evals {nev}")
    print(f"composite Simpson with {nev} evals: err "
          f"{abs(simpson(g, -1, 2, nev - nev % 2) - (2/3 + 2/3*2**1.5)):.1e} "
          f"vs adaptive err {abs(I - (2/3 + 2/3*2**1.5)):.1e}")
    per = lambda x: np.exp(np.cos(x))
    print(f"periodic integrand, trapezoid n=8: err {abs(trapezoid(per, 0, 2*np.pi, 8) - 7.954926521012846):.1e}")
