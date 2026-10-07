"""Boundary value problems by the shooting method (note 11).

Implements [S4 §9.4] (CSE), Alg. 30.  Turn
    y'' = f(t, y, y'),  y(0) = y0,  y(T) = yT
into an initial value problem with an unknown initial slope s0, and solve
    y(T; s0) = yT
for s0 by Newton.  The derivative d/ds0 y(T; s0) solves a *linear* variational
initial value problem, [S4] (9.14).
"""
import numpy as np

from ode import rk4


def _as_first_order(f):
    """y'' = f(t, y, u) as the system (y, u)' = (u, f(t, y, u)),  [S4] (9.13)."""
    def rhs(t, z):
        y, u = z[0], z[1]
        return np.array([u, float(f(t, y, u))])
    return rhs


def solve_ivp_shot(f, y0, s0, T, N=400, t0=0.0):
    """Solve [S4] (9.13) with initial slope s0; return (ts, y, u)."""
    h = (T - t0) / N
    ts, Z = rk4(_as_first_order(f), t0, np.array([float(y0), float(s0)]), h, N)
    Z = np.asarray(Z)
    return ts, Z[:, 0], Z[:, 1]


def variational_rhs(f_y, f_u, ysol, usol, ts):
    """The right-hand side of the variational problem [S4] (9.14).

        v'' = d_y f (t, y, y') v + d_{y'} f (t, y, y') v',   v(0)=0, v'(0)=1

    ysol/usol are callables giving y and y' along the current trajectory.
    """
    def rhs(t, w):
        v, vp = w[0], w[1]
        return np.array([vp,
                         float(f_y(t, ysol(t), usol(t))) * v
                         + float(f_u(t, ysol(t), usol(t))) * vp])
    return rhs


def shooting(f, y0, yT, T, s0=0.0, f_y=None, f_u=None, N=400, t0=0.0,
             tol=1e-10, iters=30, history=False):
    """[S4] Alg. 30.

    Each Newton step integrates (9.13) for the current s0 and (9.14) for the
    sensitivity, then updates
        s0 <- s0 - (d y(T; s0)/d s0)^{-1} (y(T; s0) - yT).
    If f_y / f_u are not supplied, the sensitivity is taken by a difference
    quotient in s0 instead -- same iteration, one extra trajectory per step.
    """
    s = float(s0)
    hist = [s]
    for _ in range(iters):
        ts, y, u = solve_ivp_shot(f, y0, s, T, N, t0)
        resid = y[-1] - yT
        if abs(resid) < tol:
            break
        if f_y is not None and f_u is not None:
            ysol = lambda t: np.interp(t, ts, y)
            usol = lambda t: np.interp(t, ts, u)
            _, W = rk4(variational_rhs(f_y, f_u, ysol, usol, ts),
                       t0, np.array([0.0, 1.0]), (T - t0) / N, N)
            dyds = np.asarray(W)[-1, 0]
        else:
            eps = 1e-6
            _, y2, _ = solve_ivp_shot(f, y0, s + eps, T, N, t0)
            dyds = (y2[-1] - y[-1]) / eps
        if dyds == 0.0:
            raise ZeroDivisionError("shooting: zero sensitivity, Newton cannot step")
        s = s - resid / dyds
        hist.append(s)
    ts, y, u = solve_ivp_shot(f, y0, s, T, N, t0)
    return (s, ts, y, np.array(hist)) if history else (s, ts, y)


def shooting_sensitivity(L, T):
    """The amplification bound of [S4] sec. 9.4:

        |y(T; s) - y(T; s + eps)| <= C e^{L T} eps

    For L = T = 10 this is e^100 ~ 2.7e43 -- the weakness of the method.
    """
    return float(np.exp(L * T))


if __name__ == "__main__":
    np.set_printoptions(precision=10, suppress=True)

    # [S4] Ex. 9.17: the same ODE, three sets of boundary conditions
    print("--- [S4] Ex. 9.17: solvability of a BVP is not automatic ---")
    f = lambda t, y, u: -y
    fy, fu = (lambda t, y, u: -1.0), (lambda t, y, u: 0.0)

    s, ts, y, hist = shooting(f, 0.0, 1.0, np.pi / 2, s0=0.0, f_y=fy, f_u=fu, history=True)
    print(f"  y(0)=0, y(pi/2)=1  -> unique, s0 = {s:.12f} (exact 1), "
          f"Newton path {hist}")
    print(f"     max |y - sin| = {np.abs(y - np.sin(ts)).max():.2e}")

    for c in (0.0, 2.5, -1.0):                    # y(0)=y(pi)=0: every c works
        _, _, yc = shooting(f, 0.0, 0.0, np.pi, s0=c, f_y=fy, f_u=fu, iters=1)
        print(f"  y(0)=y(pi)=0, started at s0={c:5.1f}: y(pi) = {yc[-1]:.2e} -> non-unique")

    try:
        s3, _, _ = shooting(f, 0.0, 1.0, np.pi, s0=0.5, f_y=fy, f_u=fu)
        print(f"  y(0)=0, y(pi)=1 -> Newton returned s0 = {s3:.3e} (no solution exists)")
    except ZeroDivisionError as e:
        print("  y(0)=0, y(pi)=1 ->", e, "(no solution exists)")

    print("\n--- [S4] Ex. 9.18: one Newton step is exact here ---")
    s, ts, y, hist = shooting(f, 0.0, 1.0, np.pi / 2, s0=0.0, f_y=fy, f_u=fu, history=True)
    print("  Newton iterates for s0:", hist, " (linear in s0 -> exact after one step)")

    print("\n--- a nonlinear BVP: y'' = 2 y^3, y(1)=1, y(2)=1/2, exact y = 1/t ---")
    g = lambda t, y, u: 2.0 * y ** 3
    gy, gu = (lambda t, y, u: 6.0 * y ** 2), (lambda t, y, u: 0.0)
    s, ts, y, hist = shooting(g, 1.0, 0.5, 2.0, s0=-0.9, f_y=gy, f_u=gu, t0=1.0,
                              history=True)
    print(f"  s0 = {s:.10f}  (exact y'(1) = -1)")
    print(f"  max |y - 1/t| = {np.abs(y - 1.0 / ts).max():.2e}   Newton steps: {len(hist) - 1}")

    print("\n--- sensitivity [S4 sec. 9.4] ---")
    for L, T in ((1.0, 1.0), (5.0, 2.0), (10.0, 10.0)):
        print(f"  L={L:4.1f}, T={T:4.1f}: amplification e^(LT) = {shooting_sensitivity(L, T):.3e}")
