"""Basic iterative methods, Arnoldi and GMRES (note 10).

Implements [S4 §8] (all CSE): Richardson and the gradient method of the §8
introduction, and GMRES with Arnoldi [S4 §8.2, Alg. 28-29].  GMRES minimises
the 2-norm of the residual over x0 + K_l, which by [S4] Exercise 8.9 is the
same as making the residual orthogonal to A K_l: a least-squares method
(note 07).  The internal least-squares problem is Hessenberg, so it is solved
by one new Givens rotation per iteration (note 06).  cg_polynomial_bound is
the CG bound of [S4 Thm 8.7].  Jacobi, Gauss-Seidel, SOR and CG are in
linsolve.py.
"""
import numpy as np

from givens import givens_rotation


def arnoldi(A, v1, m, tol=1e-14, modified=True):
    """Orthonormal basis of K_m(A, v1) by Gram-Schmidt,  [S4] Alg. 28.

    Returns (V, H, k) with V of shape (n, k+1), H of shape (k+1, k) upper
    Hessenberg, and A V[:, :k] = V H.  k < m signals a *lucky* breakdown:
    h[j+1, j] = 0 means K_j is A-invariant and the exact solution already lies
    in it ([S4] Rem. 8.12).

    [S4] Alg. 28 is titled "standard Gram-Schmidt variant"; modified=False
    reproduces it, and modified=True (the default, and what every practical
    implementation does) subtracts the projections one at a time.  The
    difference is the loss of orthogonality of note 06: O(kappa^2 u) against
    O(kappa u), and here kappa is the conditioning of the Krylov basis, which
    degrades fast.
    """
    matvec = A if callable(A) else (lambda x: np.asarray(A, float) @ x)
    v1 = np.asarray(v1, float)
    n = len(v1)
    V = np.zeros((n, m + 1))
    H = np.zeros((m + 1, m))
    V[:, 0] = v1 / np.linalg.norm(v1)
    for j in range(m):
        w = matvec(V[:, j])
        if modified:
            for i in range(j + 1):
                H[i, j] = V[:, i] @ w
                w = w - H[i, j] * V[:, i]
        else:                                        # [S4] Alg. 28 as written
            w0 = w.copy()
            for i in range(j + 1):
                H[i, j] = V[:, i] @ w0
            w = w0 - V[:, :j + 1] @ H[:j + 1, j]
        H[j + 1, j] = np.linalg.norm(w)
        if H[j + 1, j] <= tol:
            return V[:, :j + 2], H[:j + 2, :j + 1], j + 1
        V[:, j + 1] = w / H[j + 1, j]
    return V, H, m


def gmres(A, b, x0=None, m=None, tol=1e-12, history=False):
    """GMRES,  [S4] (8.7) and Alg. 29.

    Builds the Arnoldi basis and minimises || ||r0|| e1 - Hbar y ||_2 with a QR
    factorisation kept up to date by one Givens rotation per step, from which
    the residual norm is read off for free ([S4] Rem. 8.13).
    Returns (x, residual norms) when history=True.
    """
    matvec = A if callable(A) else (lambda v: np.asarray(A, float) @ v)
    b = np.asarray(b, float)
    n = len(b)
    x0 = np.zeros(n) if x0 is None else np.asarray(x0, float)
    m = n if m is None else min(m, n)
    r0 = b - matvec(x0)
    beta = np.linalg.norm(r0)
    if beta <= tol:
        return (x0, np.array([beta])) if history else x0

    V = np.zeros((n, m + 1))
    H = np.zeros((m + 1, m))
    V[:, 0] = r0 / beta
    cs, sn = np.zeros(m), np.zeros(m)
    g = np.zeros(m + 1)
    g[0] = beta
    res = [beta]
    k = 0
    for j in range(m):
        w = matvec(V[:, j])
        for i in range(j + 1):
            H[i, j] = V[:, i] @ w
            w = w - H[i, j] * V[:, i]
        H[j + 1, j] = np.linalg.norm(w)
        # apply the previous rotations to the new column
        for i in range(j):
            t = cs[i] * H[i, j] + sn[i] * H[i + 1, j]
            H[i + 1, j] = -sn[i] * H[i, j] + cs[i] * H[i + 1, j]
            H[i, j] = t
        cs[j], sn[j] = givens_rotation(H[j, j], H[j + 1, j])
        H[j, j] = cs[j] * H[j, j] + sn[j] * H[j + 1, j]
        H[j + 1, j] = 0.0
        g[j + 1] = -sn[j] * g[j]
        g[j] = cs[j] * g[j]
        k = j + 1
        res.append(abs(g[j + 1]))
        if H[j + 1, j] == 0.0 and abs(g[j + 1]) <= tol:  # lucky breakdown
            break
        if abs(g[j + 1]) <= tol * max(1.0, beta):
            break
        if np.linalg.norm(w) > 1e-300:
            V[:, j + 1] = w / np.linalg.norm(w)

    y = np.linalg.solve(np.triu(H[:k, :k]), g[:k])
    x = x0 + V[:, :k] @ y
    return (x, np.array(res)) if history else x


def gmres_restarted(A, b, x0=None, m=20, maxit=200, tol=1e-12, history=False):
    """GMRES(m): restart every m steps to bound storage,  [S4] Ex. 8.14."""
    matvec = A if callable(A) else (lambda v: np.asarray(A, float) @ v)
    b = np.asarray(b, float)
    x = np.zeros(len(b)) if x0 is None else np.asarray(x0, float).copy()
    res = [np.linalg.norm(b - matvec(x))]
    for _ in range(maxit):
        x, r = gmres(A, b, x, m=m, tol=tol, history=True)
        res.extend(r[1:])
        if res[-1] <= tol * max(1.0, res[0]):
            break
    return (x, np.array(res)) if history else x


def cg_polynomial_bound(kappa, ell):
    """2 ((sqrt k - 1)/(sqrt k + 1))^l,  the CG estimate of [S4] Thm 8.7."""
    r = (np.sqrt(kappa) - 1.0) / (np.sqrt(kappa) + 1.0)
    return 2.0 * r ** ell


# ------------------------------- [S4] sec. 8: the other basic iterative methods
def richardson(A, b, x0=None, omega=1.0, tol=1e-10, maxiter=10000, matvec=None):
    """x_{k+1} = x_k + omega (b - A x_k),  [S4] sec. 8.

    The simplest of the basic iterative methods; converges only when the
    spectrum of I - omega A lies inside the unit disc, which is why [S4] notes
    that these methods "do not always converge".
    """
    b = np.asarray(b, float)
    Av = matvec if matvec is not None else (lambda v: np.asarray(A, float) @ v)
    x = np.zeros(len(b)) if x0 is None else np.array(x0, float)
    for k in range(maxiter):
        r = b - Av(x)
        if np.linalg.norm(r) <= tol * max(1.0, np.linalg.norm(b)):
            return x, k
        x = x + omega * r
    return x, maxiter


def steepest_descent_linear(A, b, x0=None, tol=1e-10, maxiter=20000, matvec=None):
    """The gradient method for phi(x) = (Ax, x)/2 - (b, x),  [S4] sec. 8.

    Search direction d_k = -grad phi = r_k, optimal step
    alpha_k = (r_k, r_k)_2 / (r_k, r_k)_A ([S4] sec. 6.8.1).  Consecutive
    directions are Euclidean-orthogonal, which is the zig-zag CG removes.
    Needs A SPD.  Returns (x, iterations).
    """
    b = np.asarray(b, float)
    Av = matvec if matvec is not None else (lambda v: np.asarray(A, float) @ v)
    x = np.zeros(len(b)) if x0 is None else np.array(x0, float)
    for k in range(maxiter):
        r = b - Av(x)
        nr = float(r @ r)
        if np.sqrt(nr) <= tol * max(1.0, np.linalg.norm(b)):
            return x, k
        Ar = Av(r)
        x = x + (nr / float(r @ Ar)) * r
    return x, maxiter


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)
    rng = np.random.default_rng(0)

    n = 40
    A = np.eye(n) * 4 + np.diag(-np.ones(n - 1), 1) + np.diag(-2.0 * np.ones(n - 1), -1)
    b = rng.standard_normal(n)

    print("--- Arnoldi [S4 Alg. 28] ---")
    V, H, k = arnoldi(A, b, 10)
    print("  V^T V - I:", np.abs(V.T @ V - np.eye(V.shape[1])).max())
    print("  ||A V_k - V_{k+1} Hbar||:", np.abs(A @ V[:, :k] - V @ H).max())
    print("  H upper Hessenberg:", np.abs(np.tril(H, -2)).max() == 0.0)

    print("\n--- GMRES [S4 (8.7), Alg. 29] ---")
    x, res = gmres(A, b, history=True)
    print("  residual norms:", res[:8], "...", res[-1])
    print("  monotone:", bool(np.all(np.diff(res) <= 1e-14)))
    print("  ||Ax - b|| =", np.linalg.norm(A @ x - b))
    print("  vs numpy.linalg.solve:", np.abs(x - np.linalg.solve(A, b)).max())

    print("\n--- lucky breakdown [S4 Rem. 8.12] ---")
    D = np.diag([1.0, 2.0, 3.0, 4.0])
    bb = np.array([1.0, 1.0, 0.0, 0.0])              # Krylov space is 2-dimensional
    Vb, Hb, kb = arnoldi(D, bb, 4)
    print(f"  Arnoldi stops after k = {kb} of 4 (A-invariant subspace)")
    xb, rb = gmres(D, bb, history=True)
    print("  GMRES residuals:", rb, " exact:", np.abs(xb - np.linalg.solve(D, bb)).max())

    print("\n--- GMRES handles a non-symmetric matrix that breaks CG ---")
    N = np.array([[0.0, 1.0], [-1.0, 0.0]])          # skew: CG has no inner product
    rhs = np.array([1.0, 2.0])
    print("  GMRES:", gmres(N, rhs), " exact:", np.linalg.solve(N, rhs))

    print("\n--- restarted GMRES(10) ---")
    xr, rr = gmres_restarted(A, b, m=10, history=True)
    print(f"  {len(rr) - 1} total steps, final residual {rr[-1]:.2e},"
          f" error {np.abs(xr - np.linalg.solve(A, b)).max():.2e}")

    print("\n--- CG bound [S4 Thm 8.7] ---")
    for kappa in (10, 100, 1000):
        need = next(l for l in range(1, 100000) if cg_polynomial_bound(kappa, l) < 1e-6)
        print(f"  kappa={kappa:5d}: {need:5d} iterations for 1e-6  (~ sqrt(kappa) = {np.sqrt(kappa):.0f})")
