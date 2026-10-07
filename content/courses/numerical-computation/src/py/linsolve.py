"""Direct and stationary/Krylov solvers for Ax = b (notes 05, 10).

Implements [S4 §4.1] forward/back substitution, [S4 §4.2] Gaussian
elimination as LU, [S4 §4.4] LU with partial pivoting, [S4 §4.3.3] Cholesky
A = C C^T; and for note 10 Jacobi and Gauss-Seidel from the [S4 §8]
introduction and the conjugate gradient method [S4 §8.1, Alg. 27] (CSE).  SOR
and its optimal omega are background, not in [S4].  Pure numpy (no
numpy.linalg inside the algorithms).
"""
import numpy as np


# ---------------------------------------------------------------- triangular
def forward_substitution(L, b, unit_diag=False):
    """Solve L y = b, L lower triangular.  O(n^2)."""
    n = len(b)
    y = np.zeros(n)
    for i in range(n):
        s = b[i] - L[i, :i] @ y[:i]
        y[i] = s if unit_diag else s / L[i, i]
    return y


def back_substitution(U, y):
    """Solve U x = y, U upper triangular.  O(n^2)."""
    n = len(y)
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - U[i, i + 1:] @ x[i + 1:]) / U[i, i]
    return x


# ---------------------------------------------------------------- direct
def gauss_elim(A, b):
    """Gaussian elimination with partial pivoting on the augmented matrix,
    then back substitution.  ~ n^3/3 flops for the elimination."""
    Ab = np.column_stack([np.asarray(A, float), np.asarray(b, float)])
    n = len(Ab)
    for k in range(n - 1):
        p = k + np.argmax(np.abs(Ab[k:, k]))          # partial pivot
        if Ab[p, k] == 0:
            raise ValueError("singular matrix")
        Ab[[k, p]] = Ab[[p, k]]
        for i in range(k + 1, n):
            m = Ab[i, k] / Ab[k, k]
            Ab[i, k:] -= m * Ab[k, k:]
    if Ab[n - 1, n - 1] == 0:
        raise ValueError("singular matrix")
    return back_substitution(Ab[:, :n], Ab[:, n])


def lu_decompose(A):
    """P A = L U with partial pivoting.  Returns packed LU (L unit lower in the
    strict lower part, U in the upper part) and the permutation vector piv
    such that A[piv] = L U."""
    LU = np.array(A, float)
    n = len(LU)
    piv = np.arange(n)
    for k in range(n - 1):
        p = k + np.argmax(np.abs(LU[k:, k]))
        if LU[p, k] == 0:
            raise ValueError("singular matrix")
        if p != k:
            LU[[k, p]] = LU[[p, k]]
            piv[[k, p]] = piv[[p, k]]
        LU[k + 1:, k] /= LU[k, k]                                   # multipliers
        LU[k + 1:, k + 1:] -= np.outer(LU[k + 1:, k], LU[k, k + 1:])  # rank-1 update
    if LU[n - 1, n - 1] == 0:
        raise ValueError("singular matrix")
    return LU, piv


def lu_unpack(LU, piv):
    n = len(LU)
    L = np.tril(LU, -1) + np.eye(n)
    U = np.triu(LU)
    P = np.eye(n)[piv]
    return P, L, U


def lu_solve(LU, piv, b):
    """Solve A x = b given P A = L U:  L y = P b,  U x = y.  O(n^2) per rhs."""
    b = np.asarray(b, float)[piv]
    y = forward_substitution(LU, b, unit_diag=True)
    return back_substitution(LU, y)


def solve(A, b):
    LU, piv = lu_decompose(A)
    return lu_solve(LU, piv, b)


def determinant(A):
    LU, piv = lu_decompose(A)
    sign = 1
    # parity of the permutation from cycle count
    visited = np.zeros(len(piv), bool)
    for i in range(len(piv)):
        if not visited[i]:
            j, length = i, 0
            while not visited[j]:
                visited[j] = True
                j = piv[j]
                length += 1
            if length % 2 == 0:
                sign = -sign
    return sign * np.prod(np.diag(LU))


def cholesky(A):
    """A = L L^T for symmetric positive definite A.  ~ n^3/3 flops (half of
    LU), no pivoting needed.  Raises if a pivot is <= 0 (A not SPD)."""
    A = np.asarray(A, float)
    n = len(A)
    L = np.zeros((n, n))
    for j in range(n):
        d = A[j, j] - L[j, :j] @ L[j, :j]
        if d <= 0:
            raise ValueError("matrix not positive definite")
        L[j, j] = np.sqrt(d)
        L[j + 1:, j] = (A[j + 1:, j] - L[j + 1:, :j] @ L[j, :j]) / L[j, j]
    return L


def cholesky_solve(L, b):
    y = forward_substitution(L, np.asarray(b, float))
    return back_substitution(L.T, y)


# ---------------------------------------------------------------- iterative
def jacobi(A, b, x0=None, tol=1e-10, maxiter=10_000):
    """x^{k+1} = D^{-1} (b - (L+U) x^k).  Converges if A strictly diagonally
    dominant (rho(D^{-1}(L+U)) < 1).  Returns (x, iterations, residual history)."""
    A, b = np.asarray(A, float), np.asarray(b, float)
    x = np.zeros_like(b) if x0 is None else np.array(x0, float)
    D = np.diag(A)
    R = A - np.diag(D)
    hist = []
    for k in range(1, maxiter + 1):
        x = (b - R @ x) / D
        r = np.max(np.abs(b - A @ x))
        hist.append(r)
        if r < tol:
            break
    return x, k, np.array(hist)


def sor(A, b, omega=1.0, x0=None, tol=1e-10, maxiter=10_000):
    """Successive over-relaxation; omega = 1 is Gauss-Seidel.
    x_i <- (1-w) x_i + w/a_ii (b_i - sum_{j<i} a_ij x_j^{new} - sum_{j>i} a_ij x_j^{old}).
    Converges for SPD A and 0 < omega < 2 (Ostrowski-Reich)."""
    A, b = np.asarray(A, float), np.asarray(b, float)
    n = len(b)
    x = np.zeros(n) if x0 is None else np.array(x0, float)
    hist = []
    for k in range(1, maxiter + 1):
        for i in range(n):
            s = A[i, :i] @ x[:i] + A[i, i + 1:] @ x[i + 1:]
            x[i] = (1 - omega) * x[i] + omega * (b[i] - s) / A[i, i]
        r = np.max(np.abs(b - A @ x))
        hist.append(r)
        if r < tol:
            break
    return x, k, np.array(hist)


def gauss_seidel(A, b, **kw):
    return sor(A, b, omega=1.0, **kw)


def sor_optimal_omega(rho_jacobi):
    """For consistently ordered matrices (e.g. Poisson): w_opt = 2/(1+sqrt(1-rho_J^2))."""
    return 2.0 / (1.0 + np.sqrt(1.0 - rho_jacobi ** 2))


def conjugate_gradient(A, b, x0=None, tol=1e-10, maxiter=None, matvec=None):
    """CG for SPD A.  Minimises the A-norm of the error over the Krylov space;
    exact in <= n steps in exact arithmetic, in practice
    ||e_k||_A <= 2 ((sqrt(kappa)-1)/(sqrt(kappa)+1))^k ||e_0||_A.
    `matvec` allows a matrix-free operator.  Returns (x, iterations, residual norms)."""
    b = np.asarray(b, float)
    Av = matvec if matvec is not None else (lambda v: np.asarray(A, float) @ v)
    n = len(b)
    maxiter = maxiter or 2 * n
    x = np.zeros(n) if x0 is None else np.array(x0, float)
    r = b - Av(x)
    p = r.copy()
    rr = r @ r
    hist = [np.sqrt(rr)]
    for k in range(1, maxiter + 1):
        Ap = Av(p)
        alpha = rr / (p @ Ap)
        x += alpha * p
        r -= alpha * Ap
        rr_new = r @ r
        hist.append(np.sqrt(rr_new))
        if np.sqrt(rr_new) < tol:
            break
        p = r + (rr_new / rr) * p          # A-conjugate search direction
        rr = rr_new
    return x, k, np.array(hist)


def power_iteration(B, iters=2000, tol=1e-12, seed=0):
    """Dominant |eigenvalue| of B (spectral radius of an iteration matrix).
    Uses the 2-norm growth ||B x|| / ||x||, which also converges when the
    dominant eigenvalues come in a +-rho pair (Jacobi on Poisson)."""
    x = np.random.default_rng(seed).standard_normal(len(B))
    x /= np.sqrt(x @ x)
    lam = 0.0
    for _ in range(iters):
        y = B @ x
        lam_new = np.sqrt(y @ y)
        if lam_new == 0:
            return 0.0
        x = y / lam_new
        if abs(lam_new - lam) < tol * lam_new:
            break
        lam = lam_new
    return lam_new


def iteration_matrix(A, method="jacobi", omega=1.0):
    """M = I - P^{-1} A with P = D (Jacobi), D+L (GS), D/omega + L (SOR)."""
    A = np.asarray(A, float)
    D, L = np.diag(np.diag(A)), np.tril(A, -1)
    if method == "jacobi":
        P = D
    elif method == "gauss_seidel":
        P = D + L
    else:
        P = D / omega + L
    n = len(A)
    Pinv_A = np.column_stack([forward_substitution(P, A[:, j]) for j in range(n)])
    return np.eye(n) - Pinv_A


def poisson_1d(n):
    """Tridiagonal (2, -1) matrix, h^2 times the 1-D Dirichlet Laplacian.
    Eigenvalues 2 - 2 cos(k pi/(n+1)), kappa ~ 4 n^2 / pi^2."""
    return 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)

if __name__ == "__main__":
    A = np.array([[2., 1., 1.], [4., -6., 0.], [-2., 7., 2.]])
    b = np.array([5., -2., 9.])
    print("Gaussian elimination :", gauss_elim(A, b))
    LU, piv = lu_decompose(A)
    P, L, U = lu_unpack(LU, piv)
    print("piv", piv, " |PA - LU| =", np.abs(P @ A - L @ U).max())
    print("LU solve             :", lu_solve(LU, piv, b), " det =", determinant(A))

    S = np.array([[4., 12., -16.], [12., 37., -43.], [-16., -43., 98.]])
    Lc = cholesky(S)
    print("Cholesky L =\n", Lc)

    n = 20
    Ap = poisson_1d(n)
    bp = np.ones(n)
    x_ref = solve(Ap, bp)
    for name, fn in (("Jacobi", jacobi), ("Gauss-Seidel", gauss_seidel)):
        x, k, _ = fn(Ap, bp, tol=1e-8)
        print(f"{name:13s}: {k:5d} iterations, err {np.abs(x - x_ref).max():.1e}")
    rho_j = power_iteration(iteration_matrix(Ap, "jacobi"))
    w = sor_optimal_omega(rho_j)
    x, k, _ = sor(Ap, bp, omega=w, tol=1e-8)
    print(f"SOR w={w:.3f}    : {k:5d} iterations, err {np.abs(x - x_ref).max():.1e}")
    x, k, hist = conjugate_gradient(Ap, bp, tol=1e-8)
    print(f"CG           : {k:5d} iterations, err {np.abs(x - x_ref).max():.1e}")
    print("spectral radii J/GS:", rho_j, power_iteration(iteration_matrix(Ap, "gauss_seidel")))
