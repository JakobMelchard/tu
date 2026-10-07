"""Underdetermined systems, minimum-norm solutions, Moore-Penrose (note 07).

Implements [S4 §5.3]: the reduced SVD and numerical rank [S4 §5.3.1, Rem. 5.16],
the minimum-norm solution of an underdetermined system [S4 §5.3.2], least
squares via the SVD [S4 §5.3.3], and the pseudoinverse A^+ [S4 §5.3.5] (CSE).
Our own SVD is qr_svd.jacobi_svd; numpy's is used only as a cross-check in
the tests.
"""
import numpy as np

from qr_svd import jacobi_svd


def reduced_svd(A, tol=None, use_jacobi=True):
    """A = Ut St Vt^T with r = rank A columns kept, [S4] sec. 5.3.1.

    Returns (Ut, s, Vt, r) where s holds the r positive singular values and
    Ut, Vt have orthonormal columns.
    """
    A = np.asarray(A, float)
    if use_jacobi and A.shape[0] >= A.shape[1]:
        U, s, V = jacobi_svd(A)            # note: jacobi_svd returns V, not V^T
    else:
        U, s, Vh = np.linalg.svd(A, full_matrices=False)
        V = Vh.T
    if tol is None:
        tol = max(A.shape) * np.finfo(float).eps * (s[0] if len(s) else 0.0)
    r = int((s > tol).sum())
    return U[:, :r], s[:r], V[:, :r], r


def numerical_rank(A, tol=None):
    """#{sigma_i >= tol}, [S4] Rem. 5.16.

    In floating point every computed sigma_i is non-zero, so a cut-off a little
    above machine precision has to be chosen.
    """
    return reduced_svd(A, tol)[3]


def pinv(A, tol=None):
    """Moore-Penrose pseudoinverse A^+ = Vt St^{-1} Ut^T,  [S4] (5.6)."""
    Ut, s, Vt, r = reduced_svd(A, tol)
    return Vt @ np.diag(1.0 / s) @ Ut.T


def lstsq_svd(A, b, tol=None):
    """Minimum-norm least-squares solution x* = A^+ b,  [S4] Thm 5.17.

    Works for any shape and any rank: it minimises ||Ax - b||_2 and, among the
    minimisers, ||x||_2.
    """
    return pinv(A, tol) @ np.asarray(b, float)


def min_norm_solution(A, b, tol=None):
    """min ||x||_2 subject to Ax = b, for an underdetermined full-rank A.

    [S4] sec. 5.3.2: x* = Vt St^{-1} U^T b.  Every solution is x* + V0 y with
    x* orthogonal to ker A, so ||x||^2 = ||x*||^2 + ||V0 y||^2.
    """
    return lstsq_svd(A, b, tol)


def project_range(A, x, tol=None):
    """Orthogonal projection onto range A, Ut Ut^T x  ([S4] Exercise 5.12)."""
    Ut = reduced_svd(A, tol)[0]
    return Ut @ (Ut.T @ np.asarray(x, float))


def project_kernel(A, x, tol=None):
    """Orthogonal projection onto ker A, V0 V0^T x = x - Vt Vt^T x."""
    _, _, Vt, _ = reduced_svd(A, tol)
    x = np.asarray(x, float)
    return x - Vt @ (Vt.T @ x)


def svd_via_symmetric(A):
    """Singular values from the symmetric embedding of [S4] sec. 5.3.6.

        [[0, A^T], [A, 0]]  has eigenvalues +- sigma_i (and zeros)

    The point of the detour is that forming A^T A squares the condition number
    and destroys the small singular values.
    """
    A = np.asarray(A, float)
    m, n = A.shape
    S = np.zeros((m + n, m + n))
    S[:n, n:] = A.T
    S[n:, :n] = A
    ev = np.linalg.eigvalsh(S)            # +- sigma_i, plus |m - n| zeros
    return np.sort(ev)[::-1][:min(m, n)]


def normal_equations_solve(A, b):
    """The A^T A x = A^T b route of [S4] (5.3) -- the one that squares kappa.

    Solved by Cholesky, since A^T A is SPD when A has full column rank
    ([S4] Thm 5.5).  That is what MATLAB's backslash does too, and it is what
    makes the digit loss of [S4] Ex. 5.6 visible: a general LU solve happens to
    exploit the symmetry of that particular right-hand side and returns the
    exact answer.
    """
    from linsolve import cholesky, cholesky_solve
    A, b = np.asarray(A, float), np.asarray(b, float)
    return cholesky_solve(cholesky(A.T @ A), A.T @ b)


def s4_example_5_6(eps=1e-7):
    """The matrix of [S4] Ex. 5.6, whose exact least-squares solution is (1,1)."""
    A = np.array([[1.0, 1.0], [eps, 0.0], [0.0, eps]])
    b = np.array([2.0, eps, eps])
    return A, b, np.array([1.0, 1.0])


if __name__ == "__main__":
    np.set_printoptions(precision=15, suppress=False)

    print("--- [S4] Ex. 5.6: normal equations vs QR ---")
    A, b, x = s4_example_5_6(1e-7)
    from qr_svd import qr_solve
    print("  kappa(A^T A) = 2/eps^2 + 1 =", np.linalg.cond(A.T @ A))
    print("  normal equations:", normal_equations_solve(A, b))
    print("  via QR          :", qr_solve(A, b))
    print("  via SVD (A^+ b) :", lstsq_svd(A, b))
    print("  exact           :", x)

    print("\n--- underdetermined system, minimum-norm solution [S4 sec. 5.3.2] ---")
    rng = np.random.default_rng(0)
    Au = rng.standard_normal((3, 6))
    bu = rng.standard_normal(3)
    xs = min_norm_solution(Au, bu)
    print("  ||A x - b|| =", np.linalg.norm(Au @ xs - bu))
    print("  ||x*||      =", np.linalg.norm(xs))
    for _ in range(3):
        y = rng.standard_normal(6)
        other = xs + project_kernel(Au, y)           # another solution
        print(f"    another solution: residual {np.linalg.norm(Au @ other - bu):.2e},"
              f" norm {np.linalg.norm(other):.6f}  >= {np.linalg.norm(xs):.6f}")

    print("\n--- pseudoinverse identities [S4 sec. 5.3.6] ---")
    M = rng.standard_normal((6, 4))
    M[:, 3] = M[:, 0] + 2 * M[:, 1]                  # rank 3
    P = pinv(M)
    print("  rank =", numerical_rank(M), " (numpy:", np.linalg.matrix_rank(M), ")")
    print("  ||A A^+ A - A|| =", np.abs(M @ P @ M - M).max())
    print("  ||A^+ A A^+ - A^+|| =", np.abs(P @ M @ P - P).max())
    print("  ||A^+ - numpy.pinv|| =", np.abs(P - np.linalg.pinv(M)).max())
    s = np.linalg.svd(M, compute_uv=False)
    print("  ||A^+||_2 =", np.linalg.norm(P, 2), " 1/sigma_r =", 1 / s[2])

    print("\n--- singular values from the symmetric embedding [S4 sec. 5.3.6] ---")
    print("  ours :", svd_via_symmetric(M))
    print("  numpy:", np.linalg.svd(M, compute_uv=False))
