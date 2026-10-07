"""2D heat equation u_t = alpha Laplace(u) on the unit square (topic 04).

Explicit Euler (stable iff r = alpha dt / h^2 <= 1/4 in 2D) and implicit Euler
(unconditionally stable; sparse LU factorised once, then one solve per step).
Exact solution for u0 = sin(pi x) sin(pi y): exp(-2 alpha pi^2 t) u0.

Run `python3 heat2d.py` for the stable / unstable / implicit comparison.
C++ counterpart: ../cpp/heat2d.cpp (matrix-free CG for the implicit solve).

Sources: method of lines, explicit/implicit Euler and the von Neumann limit
[S23 ch. 9-10]; stability <=> convergence [S24]. Test: test_heat2d.py.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from fd_poisson import poisson2d_matrix


def initial(N):
    x = np.linspace(0, 1, N + 1)
    X, Y = np.meshgrid(x, x, indexing="ij")
    return X, Y, np.sin(np.pi * X) * np.sin(np.pi * Y)


def exact(X, Y, t, alpha=1.0):
    return np.exp(-2 * alpha * np.pi**2 * t) * np.sin(np.pi * X) * np.sin(np.pi * Y)


def laplacian(U, h):
    """5-point Laplacian on the interior; boundary rows stay 0 (Dirichlet)."""
    L = np.zeros_like(U)
    L[1:-1, 1:-1] = (U[:-2, 1:-1] + U[2:, 1:-1] + U[1:-1, :-2] + U[1:-1, 2:] - 4 * U[1:-1, 1:-1]) / h**2
    return L


def cfl_limit(h, alpha=1.0, dim=2):
    """Largest stable explicit-Euler step: h^2 / (2 dim alpha)."""
    return h**2 / (2 * dim * alpha)


def explicit_euler(N, r, T, alpha=1.0):
    """March with dt = r h^2 / alpha (rounded so that the last step lands on T)."""
    X, Y, U = initial(N)
    h = 1.0 / N
    steps = int(np.ceil(T * alpha / (r * h**2)))
    dt = T / steps
    for _ in range(steps):
        U = U + dt * alpha * laplacian(U, h)
    return X, Y, U, steps


def implicit_euler(N, dt, T, alpha=1.0):
    """(I - dt alpha L_h) U^{n+1} = U^n on the interior; factorise once with splu."""
    X, Y, U = initial(N)
    steps = int(np.ceil(T / dt))
    dt = T / steps
    A = sp.identity((N - 1) ** 2, format="csc") + dt * alpha * poisson2d_matrix(N).tocsc()  # -L_h is SPD
    lu = spla.splu(A)
    for _ in range(steps):
        U[1:-1, 1:-1] = lu.solve(U[1:-1, 1:-1].ravel()).reshape(N - 1, N - 1)
    return X, Y, U, steps


if __name__ == "__main__":
    N, T = 32, 0.05
    h = 1.0 / N
    print(f"N={N}, h={h:.4f}, explicit limit dt <= {cfl_limit(h):.3e}")
    for r in (0.24, 0.30):
        X, Y, U, steps = explicit_euler(N, r, T)
        err = np.max(np.abs(U - exact(X, Y, T)))
        print(f"explicit r={r:.2f}: {steps:5d} steps, max|u| = {np.max(np.abs(U)):.3e}, max err = {err:.3e}")
    for k in (1, 4, 16):
        dt = k * cfl_limit(h)
        X, Y, U, steps = implicit_euler(N, dt, T)
        err = np.max(np.abs(U - exact(X, Y, T)))
        print(f"implicit dt={k:2d} x limit: {steps:5d} steps, max err = {err:.3e}")
