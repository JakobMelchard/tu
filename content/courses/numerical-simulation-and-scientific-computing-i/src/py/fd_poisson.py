"""Finite differences for the Poisson equation, 1D and 2D (topics 03/04/05).

1D: -u'' = f on (0,1), Dirichlet ends, second-order central stencil, solved by
    the Thomas algorithm (pure Python, O(N)) and cross-checked against scipy.
2D: -(u_xx + u_yy) = f on the unit square assembled as a scipy.sparse CSR
    matrix from the 5-point stencil and solved with a direct sparse solver.
Also: finite-difference derivative and quadrature helpers used by note 03.

Run `python3 fd_poisson.py` for a convergence table (order 2 in h).
C++ counterpart: ../cpp/fd_poisson1d.cpp (Thomas + matrix-free CG).

Sources: the 1D/2D Poisson discretisation and its O(h^2) error [S23 ch. 2-3];
the composite quadrature rules are classical. Test: test_fd_poisson.py, against
scipy.sparse.linalg.spsolve and scipy.integrate.quad.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


# ---------------------------------------------------------------- derivatives / quadrature
def fd_derivative(f, x, h, scheme="central"):
    """First derivative: forward O(h), backward O(h), central O(h^2)."""
    if scheme == "forward":
        return (f(x + h) - f(x)) / h
    if scheme == "backward":
        return (f(x) - f(x - h)) / h
    return (f(x + h) - f(x - h)) / (2 * h)


def fd_second_derivative(f, x, h):
    """Central second derivative, O(h^2)."""
    return (f(x + h) - 2 * f(x) + f(x - h)) / h**2


def quad_composite(f, a, b, n, rule="simpson"):
    """Composite midpoint O(h^2), trapezoid O(h^2), Simpson O(h^4) on n panels (Simpson: n even)."""
    x = np.linspace(a, b, n + 1)
    h = (b - a) / n
    if rule == "midpoint":
        return h * np.sum(f(x[:-1] + h / 2))
    if rule == "trapezoid":
        y = f(x)
        return h * (0.5 * y[0] + y[1:-1].sum() + 0.5 * y[-1])
    assert n % 2 == 0, "Simpson needs an even number of panels"
    y = f(x)
    return h / 3 * (y[0] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum() + y[-1])


# ---------------------------------------------------------------- 1D
def thomas(sub, diag, sup, rhs):
    """Solve a tridiagonal system in O(n). sub[0] and sup[-1] are ignored."""
    n = len(diag)
    c = np.array(diag, dtype=float)
    d = np.array(rhs, dtype=float)
    for i in range(1, n):  # forward elimination
        w = sub[i] / c[i - 1]
        c[i] -= w * sup[i - 1]
        d[i] -= w * d[i - 1]
    x = np.empty(n)
    x[-1] = d[-1] / c[-1]
    for i in range(n - 2, -1, -1):  # back substitution
        x[i] = (d[i] - sup[i] * x[i + 1]) / c[i]
    return x


def poisson1d(f, N, ua=0.0, ub=0.0):
    """Return grid x (N+1 points) and FD solution u of -u'' = f, u(0)=ua, u(1)=ub."""
    h = 1.0 / N
    x = np.linspace(0, 1, N + 1)
    m = N - 1
    rhs = f(x[1:-1])
    rhs[0] += ua / h**2  # boundary values move to the right-hand side
    rhs[-1] += ub / h**2
    u_int = thomas(np.full(m, -1 / h**2), np.full(m, 2 / h**2), np.full(m, -1 / h**2), rhs)
    return x, np.concatenate([[ua], u_int, [ub]])


def poisson1d_matrix(N):
    """The (N-1)x(N-1) matrix (1/h^2) tridiag(-1, 2, -1) as scipy CSR, for cross-checks."""
    h = 1.0 / N
    m = N - 1
    return sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(m, m), format="csr") / h**2


# ---------------------------------------------------------------- 2D
def poisson2d_matrix(N):
    """5-point Laplacian on the (N-1)^2 interior unknowns, row-major (i, j) -> (i-1)*(N-1)+(j-1)."""
    m = N - 1
    T = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(m, m))
    I = sp.identity(m)
    return (sp.kron(I, T) + sp.kron(T, I)).tocsr() * N**2  # Kronecker sum = 2D Laplacian


def poisson2d(f, N):
    """Solve -Laplace u = f with u = 0 on the boundary; returns X, Y, U on the full grid."""
    x = np.linspace(0, 1, N + 1)
    X, Y = np.meshgrid(x, x, indexing="ij")
    A = poisson2d_matrix(N)
    b = f(X[1:-1, 1:-1], Y[1:-1, 1:-1]).ravel()
    U = np.zeros((N + 1, N + 1))
    U[1:-1, 1:-1] = spla.spsolve(A, b).reshape(N - 1, N - 1)
    return X, Y, U


def convergence_order(errors):
    """Observed orders log2(e_k / e_{k+1}) for successive halvings of h."""
    e = np.asarray(errors)
    return np.log2(e[:-1] / e[1:])


if __name__ == "__main__":
    u_ex = lambda x: np.sin(np.pi * x) + x
    f = lambda x: np.pi**2 * np.sin(np.pi * x)
    print("1D: -u'' = pi^2 sin(pi x), u(0)=0, u(1)=1")
    print(f"{'N':>6} {'max err':>12} {'order':>8}")
    errs = []
    for N in [8, 16, 32, 64, 128, 256]:
        x, u = poisson1d(f, N, 0.0, 1.0)
        errs.append(np.max(np.abs(u - u_ex(x))))
    orders = convergence_order(errs)
    for k, N in enumerate([8, 16, 32, 64, 128, 256]):
        print(f"{N:6d} {errs[k]:12.3e} {orders[k-1] if k else 0:8.3f}")

    print("\n2D: -Laplace u = 2 pi^2 sin(pi x) sin(pi y)")
    f2 = lambda X, Y: 2 * np.pi**2 * np.sin(np.pi * X) * np.sin(np.pi * Y)
    errs = []
    for N in [8, 16, 32, 64]:
        X, Y, U = poisson2d(f2, N)
        errs.append(np.max(np.abs(U - np.sin(np.pi * X) * np.sin(np.pi * Y))))
        print(f"{N:6d} {errs[-1]:12.3e}")
    print("orders:", np.round(convergence_order(errs), 3))
