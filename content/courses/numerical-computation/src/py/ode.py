"""Explicit and implicit Euler, RK4, stability functions, RK45 (note 11).

Implements [S4 §9.1] explicit Euler, [S4 §9.2] implicit Euler (Newton per
step), [S4 §9.3.1] Heun and classical RK4, and the stability function R(z) of
[S4 §9.3.4] (all CSE).  rk45 (Dormand-Prince 5(4), adaptive, FSAL) is from
[S19], beyond [S4].  All solvers take f(t, y) with y a numpy array and return
(ts, ys).
"""
import numpy as np


# ---------------------------------------------------------------- fixed step
def euler(f, t0, y0, h, n):
    """y_{k+1} = y_k + h f(t_k, y_k).  Local error O(h^2), global O(h)."""
    ts = t0 + h * np.arange(n + 1)
    ys = np.zeros((n + 1, np.size(y0)))
    ys[0] = y0
    for k in range(n):
        ys[k + 1] = ys[k] + h * f(ts[k], ys[k])
    return ts, ys


def implicit_euler(f, t0, y0, h, n, jac=None, newton_tol=1e-12):
    """y_{k+1} = y_k + h f(t_{k+1}, y_{k+1}), solved by Newton on
    G(y) = y - y_k - h f(t_{k+1}, y) with G' = I - h J.  A-stable (R(z) =
    1/(1-z)), order 1; usable on stiff problems with large h."""
    from nonlinear import newton_system, jacobian_fd
    ts = t0 + h * np.arange(n + 1)
    ys = np.zeros((n + 1, np.size(y0)))
    ys[0] = y0
    d = np.size(y0)
    for k in range(n):
        t1, yk = ts[k + 1], ys[k]
        G = lambda y: y - yk - h * f(t1, y)
        Jf = jac if jac is not None else (lambda t, y: jacobian_fd(lambda v: f(t, v), y))
        GJ = lambda y: np.eye(d) - h * Jf(t1, y)
        ys[k + 1] = newton_system(G, GJ, yk + h * f(ts[k], yk), tol=newton_tol)[0]
    return ts, ys


def heun(f, t0, y0, h, n):
    """Explicit trapezoid (RK2): k1 = f(t,y), k2 = f(t+h, y+h k1),
    y += h/2 (k1 + k2).  Order 2."""
    ts = t0 + h * np.arange(n + 1)
    ys = np.zeros((n + 1, np.size(y0)))
    ys[0] = y0
    for k in range(n):
        k1 = f(ts[k], ys[k])
        k2 = f(ts[k] + h, ys[k] + h * k1)
        ys[k + 1] = ys[k] + 0.5 * h * (k1 + k2)
    return ts, ys


def rk4_step(f, t, y, h):
    k1 = f(t, y)
    k2 = f(t + 0.5 * h, y + 0.5 * h * k1)
    k3 = f(t + 0.5 * h, y + 0.5 * h * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4(f, t0, y0, h, n):
    """Classical Runge-Kutta, 4 stages, order 4: local O(h^5), global O(h^4)."""
    ts = t0 + h * np.arange(n + 1)
    ys = np.zeros((n + 1, np.size(y0)))
    ys[0] = y0
    for k in range(n):
        ys[k + 1] = rk4_step(f, ts[k], ys[k], h)
    return ts, ys


# ---------------------------------------------------------------- stability
def stability_function(method, z):
    """R(z) for y' = lambda y, z = h lambda: y_{k+1} = R(z) y_k.  The method is
    stable at z iff |R(z)| <= 1.  Explicit RK of order p: truncated exp."""
    z = np.asarray(z, complex)
    if method == "euler":
        return 1 + z
    if method == "implicit_euler":
        return 1 / (1 - z)
    if method == "heun":
        return 1 + z + z ** 2 / 2
    if method == "rk4":
        return 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24
    if method == "trapezoid":
        return (1 + z / 2) / (1 - z / 2)
    raise ValueError(method)


def real_stability_interval(method, zmax=-6.0, npts=60001):
    """Leftmost real z with |R(z)| <= 1 (Euler -2, Heun -2, RK4 ~ -2.785)."""
    z = np.linspace(zmax, 0, npts)
    ok = np.abs(stability_function(method, z)) <= 1
    idx = np.argmax(ok)                   # first True from the left
    return z[idx]


# ---------------------------------------------------------------- adaptive
# Dormand-Prince 5(4) tableau
_DP_C = np.array([0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1])
_DP_A = [
    [],
    [1 / 5],
    [3 / 40, 9 / 40],
    [44 / 45, -56 / 15, 32 / 9],
    [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
    [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
    [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84],
]
_DP_B5 = np.array([35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0])
_DP_B4 = np.array([5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40])


def rk45(f, t0, y0, t_end, rtol=1e-6, atol=1e-9, h0=None, h_min=1e-12, h_max=None):
    """Adaptive Dormand-Prince RK5(4) with FSAL.  Error estimate
    err = ||(y5 - y4) / (atol + rtol max(|y|, |y_new|))||_inf;  accept if err <= 1,
    new step h <- h min(5, max(0.2, 0.9 err^(-1/5)))  (order 5 -> exponent 1/5).
    Returns (ts, ys, n_rejected)."""
    y = np.array(y0, float, ndmin=1)
    t = t0
    h_max = h_max or (t_end - t0)
    h = h0 or min(h_max, 0.01 * (t_end - t0))
    ts, ys, rejected = [t], [y.copy()], 0
    k = [f(t, y)]
    while t < t_end:
        h = min(h, t_end - t)
        ks = [k[0]]
        for i in range(1, 7):
            yi = y + h * sum(a * kk for a, kk in zip(_DP_A[i], ks))
            ks.append(f(t + _DP_C[i] * h, yi))
        y5 = y + h * sum(b * kk for b, kk in zip(_DP_B5, ks))
        y4 = y + h * sum(b * kk for b, kk in zip(_DP_B4, ks))
        scale = atol + rtol * np.maximum(np.abs(y), np.abs(y5))
        err = np.max(np.abs(y5 - y4) / scale)
        if err <= 1.0:
            t, y = t + h, y5
            ts.append(t)
            ys.append(y.copy())
            k = [ks[6]]                     # FSAL: last stage = first stage of next step
        else:
            rejected += 1
        fac = 0.9 * (err ** -0.2 if err > 0 else 5.0)
        h = h * min(5.0, max(0.2, fac))
        h = min(h, h_max)
        if h < h_min:
            raise RuntimeError("step size underflow at t = %g" % t)
    return np.array(ts), np.array(ys), rejected


if __name__ == "__main__":
    f = lambda t, y: -2 * t * y            # y = exp(-t^2)
    exact = lambda t: np.exp(-t * t)
    T = 2.0
    print("global error at t = 2 for y' = -2ty, y(0)=1:")
    print("   n     euler      heun       rk4      impl.euler")
    for n in (10, 20, 40, 80):
        h = T / n
        row = []
        for m in (euler, heun, rk4, implicit_euler):
            _, ys = m(f, 0.0, np.array([1.0]), h, n)
            row.append(abs(ys[-1, 0] - exact(T)))
        print(f"  {n:3d}  " + "  ".join(f"{e:.2e}" for e in row))
    print("(each halving of h: Euler /2, Heun /4, RK4 /16)")

    print("\nreal stability intervals:", {m: round(real_stability_interval(m), 3)
                                          for m in ("euler", "heun", "rk4")})

    lam = -50.0
    print(f"\nstiff y' = {lam} y, h = 0.1 (z = {lam * 0.1}):")
    for m in (euler, rk4, implicit_euler):
        _, ys = m(lambda t, y: lam * y, 0.0, np.array([1.0]), 0.1, 10)
        print(f"  {m.__name__:14s} y(1) = {ys[-1, 0]: .3e}   (exact {np.exp(lam):.1e})")

    # Van der Pol, mu = 5, and adaptive RK45
    mu = 5.0
    vdp = lambda t, y: np.array([y[1], mu * (1 - y[0] ** 2) * y[1] - y[0]])
    ts, ys, rej = rk45(vdp, 0.0, [2.0, 0.0], 20.0, rtol=1e-8, atol=1e-10)
    hs = np.diff(ts)
    print(f"\nVan der Pol mu=5, RK45: {len(ts) - 1} steps, {rej} rejected, "
          f"h in [{hs.min():.1e}, {hs.max():.1e}], y(20) = {ys[-1]}")
    ts, ys, rej = rk45(f, 0.0, [1.0], T, rtol=1e-10, atol=1e-12)
    print(f"RK45 on y' = -2ty: {len(ts) - 1} steps, error {abs(ys[-1, 0] - exact(T)):.1e}")
