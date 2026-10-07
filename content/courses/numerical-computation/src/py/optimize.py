"""Descent methods, globalised Newton, Gauss-Newton, Broyden (note 08).

Implements [S4 §6.5-6.8]: Armijo line search [S4 (6.13)] and globalised Newton
[S4 §6.5, Alg. 15], Gauss-Newton [S4 §6.6], Broyden with Sherman-Morrison
[S4 §6.7] (CSE) and the gradient method on a quadratic [S4 §6.8.1] (CSE).
The plain Newton methods live in nonlinear.py.
"""
import numpy as np


# ------------------------------------------------------------- Armijo rule
def armijo(g, grad_g, x, d, sigma=1e-4, q=0.5, kmax=60):
    """Largest step q^k with g(x + q^k d) < g(x) + sigma (grad g . d) q^k.

    [S4] (6.13).  d must be a descent direction, grad_g(x) . d < 0.
    Returns (lambda, number of trials).
    """
    g0 = g(x)
    slope = float(np.asarray(grad_g(x)) @ np.asarray(d))
    if slope >= 0:
        raise ValueError("not a descent direction")
    lam = 1.0
    for k in range(kmax):
        if g(x + lam * np.asarray(d)) < g0 + sigma * slope * lam:
            return lam, k + 1
        lam *= q
    return lam, kmax


def steepest_descent(g, grad_g, x0, iters=500, tol=1e-10, sigma=1e-4, q=0.5,
                     history=False):
    """Descent with d = -grad g and an Armijo step,  [S4] sec. 6.5.2."""
    x = np.array(x0, float)
    hist = [x.copy()]
    for _ in range(iters):
        d = -np.asarray(grad_g(x), float)
        if np.linalg.norm(d) < tol:
            break
        lam, _ = armijo(g, grad_g, x, d, sigma, q)
        x = x + lam * d
        hist.append(x.copy())
    return (x, np.array(hist)) if history else x


def gradient_descent_quadratic(Q, c, gamma, x0, iters=200, tol=1e-12, history=False):
    """Steepest descent on f(x) = gamma + c.x + x.Qx/2 with the exact line search.

    [S4] sec. 6.8.1: the minimising step is t = -(grad f . d)/(d^T Q d).
    [S4] Lem. 6.23: the method degrades when Q has widely differing eigenvalues
    -- which is the reason CG exists (note 10).
    """
    Q, c = np.asarray(Q, float), np.asarray(c, float)
    x = np.array(x0, float)
    hist = [x.copy()]
    for _ in range(iters):
        g = Q @ x + c
        d = -g
        nd = float(d @ (Q @ d))
        if nd <= 0 or np.linalg.norm(g) < tol:
            break
        t = -float(g @ d) / nd
        x = x + t * d
        hist.append(x.copy())
    return (x, np.array(hist)) if history else x


# ------------------------------------------------------ globalised Newton
def globalized_newton(f, jac, x0, mu=0.5, q=0.5, tol=1e-12, iters=100,
                      history=False):
    """[S4] Alg. 15 verbatim.

    Zeros of f are minima of g(x) = ||f(x)||_2^2, and the Newton direction
    d = -(f'(x))^{-1} f(x) is a descent direction for it ([S4] Lem. 6.15).
    The step is shrunk until the descent is at least mu * lambda * ||f(x)||^2,
    then lambda is allowed to grow again (line 11 of [S4] Alg. 15) so that full
    Newton steps -- and quadratic convergence -- are recovered near the root.
    """
    x = np.array(x0, float)
    lam = 1.0
    hist = [x.copy()]
    lams = []
    for _ in range(iters):
        fx = np.atleast_1d(np.asarray(f(x), float))
        g0 = float(fx @ fx)
        if np.sqrt(g0) < tol:
            break
        J = np.atleast_2d(np.asarray(jac(x), float))
        d = np.linalg.solve(J, -fx)
        inner = 0
        while inner < 60:
            fn = np.atleast_1d(np.asarray(f(x + lam * d), float))
            if g0 - float(fn @ fn) >= mu * lam * g0:
                break
            lam *= q
            inner += 1
        x = x + lam * d
        lams.append(lam)
        hist.append(x.copy())
        lam = min(1.0, lam / q)
    return (x, np.array(hist), np.array(lams)) if history else x


# ---------------------------------------------------------- Gauss-Newton
def gauss_newton(F, JF, x0, iters=100, tol=1e-12, history=False):
    """Nonlinear least squares min ||F(x)||_2,  [S4] (6.18)-(6.19).

    Each step solves the *linear* least-squares problem
        min_dx || F'(x_n) dx + F(x_n) ||_2
    i.e. drops the (F'')^T F term of the exact Newton Hessian [S4] (6.17).
    By [S4] Thm 6.17 convergence is quadratic when F(x*) = 0 and F'(x*) has full
    rank, and only linear otherwise (a "large residual" problem).
    """
    x = np.array(x0, float)
    hist = [x.copy()]
    for _ in range(iters):
        Fx = np.atleast_1d(np.asarray(F(x), float))
        J = np.atleast_2d(np.asarray(JF(x), float))
        dx, *_ = np.linalg.lstsq(J, -Fx, rcond=None)     # the normal equations of (6.18)
        x = x + dx
        hist.append(x.copy())
        if np.linalg.norm(dx) < tol:
            break
    return (x, np.array(hist)) if history else x


# --------------------------------------------------------------- Broyden
def sherman_morrison(Ainv, u, v):
    """(A + u v^T)^{-1} = A^{-1} - A^{-1} u v^T A^{-1} / (1 + v^T A^{-1} u).

    [S4] (6.23).  Lets a rank-1 Broyden update be applied to the inverse in
    O(d^2) instead of refactorising.
    """
    Ainv = np.asarray(Ainv, float)
    u, v = np.asarray(u, float), np.asarray(v, float)
    Au = Ainv @ u
    vA = v @ Ainv
    denom = 1.0 + float(v @ Au)
    if denom == 0.0:
        raise np.linalg.LinAlgError("Sherman-Morrison denominator vanishes")
    return Ainv - np.outer(Au, vA) / denom


def broyden_update(H, s, y):
    """H_{n+1} = H_n + (y - H_n s) s^T / ||s||^2,  [S4] (6.22).

    The unique minimiser of ||A - H_n||_F subject to the secant condition
    A s = y  ([S4] Lem. 6.19, (6.20)).
    """
    H, s, y = np.asarray(H, float), np.asarray(s, float), np.asarray(y, float)
    return H + np.outer(y - H @ s, s) / float(s @ s)


def broyden(f, x0, H0=None, jac=None, iters=100, tol=1e-12, use_sm=True,
            history=False):
    """Broyden's method,  [S4] sec. 6.7.1.

    x_{n+1} = x_n - H_n^{-1} f(x_n) with H updated by (6.22).  With use_sm the
    inverse is carried along and updated by Sherman-Morrison, so no linear
    system is solved after the first step.  Locally superlinear.
    """
    x = np.array(x0, float)
    fx = np.atleast_1d(np.asarray(f(x), float))
    d = len(x)
    if H0 is not None:
        H = np.array(H0, float)
    elif jac is not None:
        H = np.atleast_2d(np.asarray(jac(x), float))
    else:
        H = np.eye(d)
    Hinv = np.linalg.inv(H) if use_sm else None
    hist = [x.copy()]
    for _ in range(iters):
        s = -(Hinv @ fx) if use_sm else -np.linalg.solve(H, fx)
        xn = x + s
        fn = np.atleast_1d(np.asarray(f(xn), float))
        y = fn - fx
        if use_sm:
            u = (y - H @ s) / float(s @ s)
            H = H + np.outer(u, s)
            Hinv = sherman_morrison(Hinv, u, s)
        else:
            H = broyden_update(H, s, y)
        x, fx = xn, fn
        hist.append(x.copy())
        if np.linalg.norm(s) < tol:
            break
    return (x, np.array(hist)) if history else x


def s4_example_6_20():
    """The system of [S4] Ex. 6.20, with zero x* = (0, 1)^T."""
    def F(x):
        return np.array([(x[0] + 3) * (x[1] ** 3 - 7) + 18,
                         np.sin(x[1] * np.exp(x[0]) - 1)])

    def J(x):
        e = np.exp(x[0])
        c = np.cos(x[1] * e - 1)
        return np.array([[x[1] ** 3 - 7, 3 * (x[0] + 3) * x[1] ** 2],
                         [x[1] * e * c, e * c]])
    return F, J, np.array([-0.5, 1.4]), np.array([0.0, 1.0])


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    print("--- Armijo [S4 (6.13)] ---")
    g = lambda x: float(x @ x) + 3.0
    gg = lambda x: 2.0 * x
    x = np.array([1.0, 2.0])
    print("  lambda, trials:", armijo(g, gg, x, -gg(x)))

    print("\n--- steepest descent on a quadratic [S4 sec. 6.8.1, Lem. 6.23] ---")
    print("  error contraction per step vs the theoretical (kappa-1)/(kappa+1)")
    rng = np.random.default_rng(0)
    for kappa in (2.0, 10.0, 100.0, 1000.0):
        Q = np.diag(np.linspace(1.0, kappa, 6))
        V = np.linalg.qr(rng.standard_normal((6, 6)))[0]
        Q = V @ Q @ V.T                              # same spectrum, no axis alignment
        x0 = rng.standard_normal(6)
        _, hist = gradient_descent_quadratic(Q, np.zeros(6), 0.0, x0,
                                             iters=4000, history=True)
        err = np.linalg.norm(hist, axis=1)
        err = err[err > 1e-9]
        rate = (err[-1] / err[len(err) // 2]) ** (1.0 / (len(err) - 1 - len(err) // 2))
        print(f"  kappa={kappa:7.0f}: {len(hist) - 1:5d} steps, observed rate {rate:.4f}, "
              f"theory {(kappa - 1) / (kappa + 1):.4f}")

    print("\n--- globalised Newton [S4 Alg. 15] ---")
    f1 = lambda x: np.arctan(x)
    j1 = lambda x: np.array([[1.0 / (1.0 + float(x[0]) ** 2)]])
    xg, hist, lams = globalized_newton(f1, j1, [3.0], history=True)
    print(f"  arctan from x0 = 3: root {xg[0]:.3e} in {len(hist) - 1} steps")
    print("  damping factors:", lams)
    xn = np.array([3.0])
    for _ in range(6):
        xn = xn - np.arctan(xn) * (1.0 + xn ** 2)
    print("  plain Newton after 6 steps:", xn, "(diverges)")

    print("\n--- Gauss-Newton [S4 (6.19), Thm 6.17] ---")
    t = np.linspace(0, 2, 11)
    model = lambda p: p[0] * np.exp(p[1] * t)
    Jm = lambda p: np.column_stack([np.exp(p[1] * t), p[0] * t * np.exp(p[1] * t)])
    data = model([2.0, -1.0])
    Fz = lambda p: model(p) - data                       # zero residual
    x, h = gauss_newton(Fz, Jm, [1.0, -0.5], history=True)
    err = np.linalg.norm(h - np.array([2.0, -1.0]), axis=1)
    print("  zero residual: errors", err[:6], " -> quadratic")
    Fl = lambda p: model(p) - (data + 0.4 * np.sin(5 * t))   # large residual
    x2, h2 = gauss_newton(Fl, Jm, [1.0, -0.5], history=True)
    err2 = np.linalg.norm(h2[1:] - x2, axis=1)
    print("  large residual: ratios", np.round(err2[1:6] / err2[:5], 3), " -> linear")

    print("\n--- Broyden [S4 Ex. 6.20] ---")
    F, J, x0, xstar = s4_example_6_20()
    _, hb = broyden(F, x0, H0=J(x0), history=True)
    from nonlinear import newton_system
    en = []
    xx = x0.copy()
    for _ in range(8):
        xx = xx - np.linalg.solve(J(xx), F(xx))
        en.append(np.linalg.norm(xx - xstar))
    eb = np.linalg.norm(hb - xstar, axis=1)
    _, hs = steepest_descent(lambda p: float(F(p) @ F(p)),
                             lambda p: 2.0 * J(p).T @ F(p), x0, iters=8, history=True)
    es = np.linalg.norm(hs - xstar, axis=1)
    print("  iter   Newton        Broyden       steepest descent")
    for i in range(1, 9):
        print(f"   {i}   {en[i-1]:.3e}   {eb[min(i, len(eb)-1)]:.3e}   {es[min(i, len(es)-1)]:.3e}")
