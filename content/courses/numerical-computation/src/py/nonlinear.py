"""Newton's method and fixed-point iteration (note 08).

Implements [S4 §6.1] scalar Newton, [S4 §6.2] fixed-point iteration and the
empirical order p (convergence_order), [S4 §6.3] Newton for systems (with
optional damping, see optimize.py for [S4 §6.5]), and [S4 §6.4] the
finite-difference Jacobian and simplified Newton.  Bisection and the secant
method are background comparisons, not in [S4 §6].
"""
import numpy as np


def bisection(f, a, b, tol=1e-12, maxiter=200):
    """Halve [a, b] while keeping a sign change.  Linear convergence with
    factor 1/2: after k steps the error is <= (b-a)/2^(k+1).
    Returns (root, iterations, history of midpoints)."""
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")
    hist = []
    for k in range(1, maxiter + 1):
        m = 0.5 * (a + b)
        fm = f(m)
        hist.append(m)
        if fm == 0 or 0.5 * (b - a) < tol:
            return m, k, np.array(hist)
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b), maxiter, np.array(hist)


def fixed_point(g, x0, tol=1e-12, maxiter=1000):
    """x_{k+1} = g(x_k).  Converges to the fixed point x* if |g'(x*)| < 1
    (Banach: g a contraction on a neighbourhood); linear with rate |g'(x*)|.
    Works for vectors too."""
    x = np.asarray(x0, float)
    hist = [x]
    for k in range(1, maxiter + 1):
        x_new = np.asarray(g(x), float)
        hist.append(x_new)
        if np.max(np.abs(x_new - x)) < tol:
            return x_new, k, np.array(hist)
        x = x_new
    return x, maxiter, np.array(hist)


def newton(f, df, x0, tol=1e-12, maxiter=100):
    """x_{k+1} = x_k - f(x_k)/f'(x_k).  Quadratic convergence for a simple
    root and x0 close enough; only linear (rate 1 - 1/m) for a root of
    multiplicity m."""
    x = float(x0)
    hist = [x]
    for k in range(1, maxiter + 1):
        dfx = df(x)
        if dfx == 0:
            raise ZeroDivisionError("f'(x) = 0 at x = %g" % x)
        step = f(x) / dfx
        x -= step
        hist.append(x)
        if abs(step) < tol * max(1.0, abs(x)):
            return x, k, np.array(hist)
    return x, maxiter, np.array(hist)


def secant(f, x0, x1, tol=1e-12, maxiter=100):
    """Newton with f' replaced by the secant slope (f(x1)-f(x0))/(x1-x0).
    Superlinear, order (1+sqrt5)/2 ~ 1.618; one f-evaluation per step."""
    f0, f1 = f(x0), f(x1)
    hist = [x0, x1]
    for k in range(1, maxiter + 1):
        if f1 == f0:
            break
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        hist.append(x2)
        x0, f0, x1, f1 = x1, f1, x2, f(x2)
        if abs(x1 - x0) < tol * max(1.0, abs(x1)):
            return x1, k, np.array(hist)
    return x1, maxiter, np.array(hist)


def jacobian_fd(F, x, h=1e-7):
    """Forward-difference Jacobian J_ij = dF_i/dx_j (n function evaluations)."""
    x = np.asarray(x, float)
    F0 = np.asarray(F(x), float)
    J = np.zeros((len(F0), len(x)))
    for j in range(len(x)):
        e = np.zeros(len(x))
        e[j] = h * max(1.0, abs(x[j]))
        J[:, j] = (np.asarray(F(x + e), float) - F0) / e[j]
    return J


def newton_system(F, J, x0, tol=1e-12, maxiter=100, damped=False, lam_min=1e-4):
    """Newton for F(x) = 0, x in R^n:  solve J(x_k) d = -F(x_k), x_{k+1} = x_k + d.
    With damped=True use x_{k+1} = x_k + lam d, halving lam until
    ||F(x_k + lam d)|| < ||F(x_k)|| (Armijo-type monotonicity test),
    which enlarges the basin of convergence.  J may be None -> finite differences.
    Returns (x, iterations, history of ||F||)."""
    from linsolve import solve
    x = np.array(x0, float)
    Jf = J if J is not None else (lambda v: jacobian_fd(F, v))
    Fx = np.asarray(F(x), float)
    hist = [np.max(np.abs(Fx))]
    for k in range(1, maxiter + 1):
        d = solve(Jf(x), -Fx)
        lam = 1.0
        while True:
            x_new = x + lam * d
            F_new = np.asarray(F(x_new), float)
            if not damped or np.max(np.abs(F_new)) < np.max(np.abs(Fx)) or lam < lam_min:
                break
            lam *= 0.5
        x, Fx = x_new, F_new
        hist.append(np.max(np.abs(Fx)))
        if np.max(np.abs(lam * d)) < tol * max(1.0, np.max(np.abs(x))):
            return x, k, np.array(hist)
    return x, maxiter, np.array(hist)


def convergence_order(hist, root=None):
    """Estimate p from consecutive errors e_k = |x_k - x*|:
    p ~ log(e_{k+1}/e_k) / log(e_k/e_{k-1}).  Uses the last iterate as x*
    if the root is unknown.  Returns the estimates for the usable steps."""
    hist = np.asarray(hist, float)
    r = hist[-1] if root is None else root
    e = np.abs(hist[:-1] - r) if root is None else np.abs(hist - r)
    e = e[e > 0]
    if len(e) < 3:
        return np.array([])
    return np.log(e[2:] / e[1:-1]) / np.log(e[1:-1] / e[:-2])



def simplified_newton(f, fprime, x0, tol=1e-12, maxiter=200, history=False):
    """x_{n+1} = x_n - (f'(x_0))^{-1} f(x_n),  [S4] sec. 6.4.

    The derivative is frozen at the starting point, so no Jacobian is
    re-evaluated and (for systems) one factorisation is reused.  The price is
    that convergence drops from quadratic to LINEAR.
    """
    x = np.asarray(x0, float) if np.ndim(x0) else float(x0)
    scalar = np.ndim(x) == 0
    J0 = fprime(x)
    hist = [x if scalar else x.copy()]
    for _ in range(maxiter):
        fx = f(x)
        step = fx / J0 if scalar else np.linalg.solve(np.atleast_2d(J0), np.atleast_1d(fx))
        x = x - (step if scalar else step)
        hist.append(x if scalar else x.copy())
        if np.linalg.norm(np.atleast_1d(step)) < tol:
            break
    return (x, np.array(hist)) if history else x


if __name__ == "__main__":
    f = lambda x: x ** 3 - 2 * x - 5          # Wallis' example, root 2.0945514815...
    df = lambda x: 3 * x ** 2 - 2
    root = 2.0945514815423265
    for name, res in (
        ("bisection", bisection(f, 2, 3)),
        ("newton", newton(f, df, 2.0)),
        ("secant", secant(f, 2.0, 3.0)),
        ("fixed point g=(2x+5)^(1/3)", fixed_point(lambda x: (2 * x + 5) ** (1 / 3), 2.0)),
    ):
        x, k, h = res
        p = convergence_order(h, root)
        print(f"{name:28s} x = {x:.15f}  iters = {k:3d}  "
              f"order ~ {p[-2] if len(p) > 1 else float('nan'):.2f}")

    print("\nNewton on (x-1)^2 (double root): linear, rate 1/2")
    x, k, h = newton(lambda x: (x - 1) ** 2, lambda x: 2 * (x - 1), 2.0, tol=1e-8)
    print(f"  iters = {k}, error ratios: {np.abs(h[1:4] - 1) / np.abs(h[:3] - 1)}")

    print("\nNewton for the system x^2 + y^2 = 4, e^x + y = 1:")
    F = lambda v: np.array([v[0] ** 2 + v[1] ** 2 - 4, np.exp(v[0]) + v[1] - 1])
    J = lambda v: np.array([[2 * v[0], 2 * v[1]], [np.exp(v[0]), 1.0]])
    x, k, h = newton_system(F, J, [1.0, 1.0])
    print(f"  x = {x}, iters = {k}, |F| history = {h}")
    x, k, h = newton_system(F, None, [-1.0, -1.0], damped=True)
    print(f"  damped, FD Jacobian, from (-1,-1): x = {x}, iters = {k}")

    print("\nDamping rescues Newton on arctan(x) from x0 = 3:")
    try:
        with np.errstate(over="ignore"):
            newton(np.arctan, lambda x: 1 / (1 + x * x), 3.0, maxiter=20)
        print("  plain Newton: finished")
    except (ZeroDivisionError, OverflowError) as e:
        print("  plain Newton failed:", e)
    x, k, _ = newton_system(lambda v: np.arctan(v), lambda v: np.array([[1 / (1 + v[0] ** 2)]]),
                            [3.0], damped=True)
    print(f"  damped Newton: x = {x}, iters = {k}")
