"""Implicit Runge-Kutta, the theta-scheme, A-stability, the stiff example (note 11).

Implements [S4 §9.3.2-9.3.4] (CSE; Def. 9.9, 9.14, Ex. 9.11-9.12).  Explicit
methods live in ode.py; this module adds the Butcher tableaux, implicit RK by
Newton on the coupled stages, the stability function as a rational map, the
A-stability test, and the stiff system of [S4] Ex. 9.12.
"""
import numpy as np


# --------------------------------------------------------- Butcher tableaux
def butcher_explicit_euler():
    """[S4] Exercise 9.5."""
    return np.array([[0.0]]), np.array([1.0]), np.array([0.0])


def butcher_heun():
    """The order-2 method of [S4] (9.8),  [S4] Exercise 9.5."""
    A = np.array([[0.0, 0.0], [1.0, 0.0]])
    return A, np.array([0.5, 0.5]), np.array([0.0, 1.0])


def butcher_rk4():
    """[S4] Ex. 9.6."""
    A = np.array([[0.0, 0, 0, 0], [0.5, 0, 0, 0], [0, 0.5, 0, 0], [0, 0, 1.0, 0]])
    return A, np.array([1, 2, 2, 1]) / 6.0, np.array([0.0, 0.5, 0.5, 1.0])


def butcher_implicit_euler():
    """[S4] Exercise 9.10: the 1-stage implicit tableau 1 | 1 ; 1."""
    return np.array([[1.0]]), np.array([1.0]), np.array([1.0])


def butcher_theta(theta):
    """[S4] Ex. 9.11: theta | theta ; 1.

    theta = 0 explicit Euler, theta = 1 implicit Euler, theta = 1/2 the implicit
    midpoint rule.  Order 1 for theta != 1/2 and order 2 for theta = 1/2.
    """
    return np.array([[float(theta)]]), np.array([1.0]), np.array([float(theta)])


# ---------------------------------------------------------- the integrators
def theta_scheme(f, y0, t0, T, N, theta=0.5, fprime=None, newton_tol=1e-12):
    """y1 = y0 + h f(t0 + theta h, theta y1 + (1-theta) y0),  [S4] Ex. 9.11.

    The eliminated form [S4] gives after removing the stage variable k1.
    Solved by Newton at each step (note 08); fprime is d f / d y.
    """
    y = np.atleast_1d(np.array(y0, float))
    h = (T - t0) / N
    ts = t0 + h * np.arange(N + 1)
    out = np.empty((N + 1, len(y)))
    out[0] = y
    d = len(y)
    for i in range(N):
        t = ts[i]
        yi = out[i]
        z = yi.copy()                                  # initial guess for y_{i+1}
        for _ in range(60):
            arg = theta * z + (1 - theta) * yi
            G = z - yi - h * np.atleast_1d(np.asarray(f(t + theta * h, arg), float))
            if np.linalg.norm(G) < newton_tol:
                break
            if fprime is None:
                J = np.eye(d)
                eps = 1e-7
                for j in range(d):
                    e = np.zeros(d)
                    e[j] = eps
                    J[:, j] = (np.atleast_1d(np.asarray(f(t + theta * h, arg + theta * e), float))
                               - np.atleast_1d(np.asarray(f(t + theta * h, arg), float))) / eps
                JG = np.eye(d) - h * theta * J
            else:
                JG = np.eye(d) - h * theta * np.atleast_2d(np.asarray(fprime(t + theta * h, arg), float))
            z = z - np.linalg.solve(JG, G)
        out[i + 1] = z
    return ts, out if out.shape[1] > 1 else out.ravel()


def implicit_rk(f, y0, t0, T, N, A, b, c, fprime=None, newton_tol=1e-12):
    """A general implicit Runge-Kutta step,  [S4] Def. 9.9.

    The s stages solve the coupled system
        k_i = f(t0 + c_i h, y0 + h sum_j a_ij k_j),   i = 1..s
    by Newton on the stacked unknown (k_1, ..., k_s).
    """
    A, b, c = np.asarray(A, float), np.asarray(b, float), np.asarray(c, float)
    s = len(b)
    y = np.atleast_1d(np.array(y0, float))
    d = len(y)
    h = (T - t0) / N
    ts = t0 + h * np.arange(N + 1)
    out = np.empty((N + 1, d))
    out[0] = y

    def F(K, t, yi):
        K = K.reshape(s, d)
        R = np.empty_like(K)
        for i in range(s):
            arg = yi + h * (A[i] @ K)
            R[i] = K[i] - np.atleast_1d(np.asarray(f(t + c[i] * h, arg), float))
        return R.ravel()

    for n in range(N):
        t, yi = ts[n], out[n]
        K = np.tile(np.atleast_1d(np.asarray(f(t, yi), float)), s).astype(float)
        for _ in range(60):
            R = F(K, t, yi)
            if np.linalg.norm(R) < newton_tol:
                break
            J = np.empty((s * d, s * d))               # finite-difference Jacobian
            eps = 1e-7
            for j in range(s * d):
                e = np.zeros(s * d)
                e[j] = eps
                J[:, j] = (F(K + e, t, yi) - R) / eps
            K = K - np.linalg.solve(J, R)
        out[n + 1] = yi + h * (b @ K.reshape(s, d))
    return ts, out if d > 1 else out.ravel()


# ------------------------------------------------------------- A-stability
def stability_function_rational(A, b, z):
    """R(z) = 1 + z b^T (I - z A)^{-1} 1,  the stability function of any RK method.

    Polynomial for an explicit (strictly lower triangular) A, rational otherwise
    -- [S4] Exercise 9.13 and the remark after it.
    """
    A, b = np.asarray(A, float), np.asarray(b, float)
    s = len(b)
    one = np.ones(s)
    M = np.eye(s) - z * A
    return 1.0 + z * (b @ np.linalg.solve(M, one))


def is_a_stable(A, b, radius=200.0, samples=400, tol=1e-9):
    """|R(z)| <= 1 for all Re z <= 0,  [S4] Def. 9.14.

    Sampled on a half-disc plus the imaginary axis.  An explicit method has a
    polynomial R, so it fails as soon as |z| is large ([S4] Exercise 9.15).
    """
    rng = np.random.default_rng(0)
    pts = [1j * t for t in np.linspace(-radius, radius, samples)]
    r = radius * rng.random(samples)
    th = np.pi / 2 + np.pi * rng.random(samples)
    pts += list(r * np.exp(1j * th))
    pts += [-x for x in np.logspace(-3, np.log10(radius), 60)]
    for z in pts:
        if abs(stability_function_rational(A, b, z)) > 1.0 + tol:
            return False
    return True


# ------------------------------------------------------ the stiff example
def lambert_system():
    """The stiff initial value problem of [S4] Ex. 9.12.

    Returns (A, y0, exact) with eigenvalues -2 and -40(1 +- i).  The exact
    solution printed in [S4]:
        y1 = e^{-2t}/2 + e^{-40t}(cos 40t + sin 40t)/2
        y2 = e^{-2t}/2 - e^{-40t}(cos 40t + sin 40t)/2
        y3 = -e^{-40t}(cos 40t - sin 40t)
    """
    A = np.array([[-21.0, 19.0, -20.0],
                  [19.0, -21.0, 20.0],
                  [40.0, -40.0, -40.0]])
    y0 = np.array([1.0, 0.0, -1.0])

    def exact(t):
        t = np.atleast_1d(np.asarray(t, float))
        e2, e40 = np.exp(-2 * t), np.exp(-40 * t)
        cs, sn = np.cos(40 * t), np.sin(40 * t)
        return np.column_stack([0.5 * e2 + 0.5 * e40 * (cs + sn),
                                0.5 * e2 - 0.5 * e40 * (cs + sn),
                                -e40 * (cs - sn)])
    return A, y0, exact


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    print("--- stability functions [S4 Exercise 9.13] ---")
    for name, (A, b, c) in [("explicit Euler", butcher_explicit_euler()),
                            ("Heun", butcher_heun()),
                            ("RK4", butcher_rk4()),
                            ("implicit Euler", butcher_implicit_euler()),
                            ("theta = 1/2", butcher_theta(0.5))]:
        z = -0.7 + 0.3j
        R = stability_function_rational(A, b, z)
        print(f"  {name:16s} R({z}) = {R:.8f}")
    z = -0.7 + 0.3j
    print("  checks: 1+z =", 1 + z, "  1/(1-z) =", 1 / (1 - z),
          "  (1+z/2)/(1-z/2) =", (1 + z / 2) / (1 - z / 2))
    from math import factorial
    print("  RK4 Taylor:", sum(z ** k / factorial(k) for k in range(5)))

    print("\n--- A-stability [S4 Def. 9.14, Exercise 9.15] ---")
    for name, (A, b, c) in [("explicit Euler", butcher_explicit_euler()),
                            ("Heun", butcher_heun()),
                            ("RK4", butcher_rk4()),
                            ("implicit Euler", butcher_implicit_euler()),
                            ("theta = 1/2 (midpoint)", butcher_theta(0.5)),
                            ("theta = 0.75", butcher_theta(0.75))]:
        print(f"  {name:24s} A-stable: {is_a_stable(A, b)}")

    print("\n--- theta-scheme order [S4 Ex. 9.11] ---")
    f = lambda t, y: -2 * t * y
    ex = lambda t: np.exp(-t ** 2)
    for theta in (0.0, 0.5, 1.0, 0.75):
        errs = []
        for N in (20, 40, 80, 160):
            ts, ys = theta_scheme(f, [1.0], 0.0, 2.0, N, theta,
                                  fprime=lambda t, y: np.array([[-2 * t]]))
            errs.append(abs(ys[-1] - ex(2.0)))
        rate = np.log2(np.array(errs[:-1]) / np.array(errs[1:])).mean()
        print(f"  theta={theta:4.2f}: errors {['%.2e' % e for e in errs]}  order ~ {rate:.2f}")

    print("\n--- the stiff system of [S4] Ex. 9.12 ---")
    A, y0, exact = lambert_system()
    print("  eigenvalues:", np.linalg.eigvals(A))
    f = lambda t, y: A @ y
    fp = lambda t, y: A
    for h, N in ((0.05, 20), (0.02, 50)):
        _, ye = theta_scheme(f, y0, 0.0, 1.0, int(1 / h), 0.0, fprime=fp)
        _, yi = theta_scheme(f, y0, 0.0, 1.0, int(1 / h), 1.0, fprime=fp)
        ref = exact(1.0)[0]
        print(f"  h={h}: explicit Euler |y| = {np.abs(ye[-1]).max():.3e},"
              f"  implicit Euler error = {np.abs(yi[-1] - ref).max():.3e}")
    print("  stability limit for explicit Euler: h <= 2/|lambda| = 2/(40 sqrt2) ="
          f" {2 / abs(-40 * (1 + 1j)):.4f}")
