"""Crout, banded LU and Cholesky, skyline matrices (note 05).

Implements [S4 §4.3.1-4.3.4]:
  - Crout's ordering of the LU equations                 [S4 §4.3.1, Alg. 9, 10]
  - banded LU with the O(npq) cost                       [S4 §4.3.2, Thm 4.12]
  - banded Cholesky, same bandwidth                      [S4 §4.3.3, Rem. 4.15]
  - skyline matrices, pattern inherited by the factors   [S4 §4.3.4, Thm 4.18]

The fill-in and ordering material of [S4 §4.6] (CSE) is in ordering.py.
"""
import numpy as np


# ------------------------------------------------------------------ Crout
def crout_lu(A):
    """LU factorisation in Crout's ordering, [S4] Alg. 9.

    Same factors as sweeping Gaussian elimination, computed entry by entry:
    row i of U first, then column i of L.  No pivoting -- [S4] Alg. 9 assumes A
    has an LU factorisation.  Returns (L, U) with L normalised.
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    L, U = np.eye(n), np.zeros((n, n))
    for i in range(n):
        for k in range(i, n):
            U[i, k] = A[i, k] - L[i, :i] @ U[:i, k]
        if U[i, i] == 0.0:
            raise ZeroDivisionError(f"zero pivot at {i}: A has no LU factorisation")
        for k in range(i + 1, n):
            L[k, i] = (A[k, i] - L[k, :i] @ U[:i, i]) / U[i, i]
    return L, U


def crout_lu_inplace(A):
    """[S4] Alg. 10: overwrite A, u_ij for j >= i and l_ij for j < i."""
    a = np.array(A, float)
    n = a.shape[0]
    for i in range(n):
        for k in range(i, n):
            a[i, k] -= a[i, :i] @ a[:i, k]
        for k in range(i + 1, n):
            a[k, i] = (a[k, i] - a[k, :i] @ a[:i, i]) / a[i, i]
    return a


# ----------------------------------------------------------------- banded
def bandwidths(A, tol=0.0):
    """(p, q): lower and upper bandwidth, a_ik = 0 for i > k+p or k > i+q."""
    A = np.asarray(A, float)
    n = A.shape[0]
    p = q = 0
    for i in range(n):
        for k in range(n):
            if abs(A[i, k]) > tol:
                p, q = max(p, i - k), max(q, k - i)
    return p, q


def banded_lu(A, p=None, q=None, count_ops=False):
    """LU of a banded matrix, touching only the band.  [S4] Thm 4.12.

    L gets lower bandwidth p and U upper bandwidth q, and the factorisation
    costs O(n p q) -- returned as an operation count when count_ops=True.
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    if p is None or q is None:
        p, q = bandwidths(A)
    a = A.copy()
    ops = 0
    for k in range(n - 1):
        if a[k, k] == 0.0:
            raise ZeroDivisionError(f"zero pivot at {k}")
        for i in range(k + 1, min(k + p + 1, n)):            # only p rows below
            a[i, k] /= a[k, k]
            ops += 1
            for j in range(k + 1, min(k + q + 1, n)):        # only q columns right
                a[i, j] -= a[i, k] * a[k, j]
                ops += 2
    L = np.tril(a, -1) + np.eye(n)
    U = np.triu(a)
    return (L, U, ops) if count_ops else (L, U)


def banded_solve(L, U, b, p=None, q=None):
    """Forward/back substitution restricted to the band, O(np) + O(nq)."""
    L, U, b = np.asarray(L, float), np.asarray(U, float), np.asarray(b, float)
    n = len(b)
    if p is None:
        p = bandwidths(L)[0]
    if q is None:
        q = bandwidths(U)[1]
    y = np.zeros(n)
    for i in range(n):
        lo = max(0, i - p)
        y[i] = b[i] - L[i, lo:i] @ y[lo:i]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        hi = min(n, i + q + 1)
        x[i] = (y[i] - U[i, i + 1:hi] @ x[i + 1:hi]) / U[i, i]
    return x


def banded_cholesky(A, p=None):
    """Cholesky A = C C^T of a banded SPD matrix; C has the same bandwidth p.

    [S4] (4.10) and Rem. 4.15.  Costs about half of banded_lu ([S4] Rem. 4.16).
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    if p is None:
        p = bandwidths(A)[0]
    C = np.zeros((n, n))
    for j in range(n):
        lo = max(0, j - p)
        s = A[j, j] - C[j, lo:j] @ C[j, lo:j]
        if s <= 0:
            raise np.linalg.LinAlgError("matrix is not positive definite")
        C[j, j] = np.sqrt(s)
        for i in range(j + 1, min(j + p + 1, n)):
            lo2 = max(0, i - p, j - p)
            C[i, j] = (A[i, j] - C[i, lo2:j] @ C[j, lo2:j]) / C[j, j]
    return C


# ---------------------------------------------------------------- skyline
def skyline_profile(A, tol=0.0):
    """(p_i, q_j) of [S4] (4.11): a_ij = 0 for j < i - p_i or i < j - q_j."""
    A = np.asarray(A, float)
    n = A.shape[0]
    p = np.zeros(n, int)
    q = np.zeros(n, int)
    for i in range(n):
        cols = np.flatnonzero(np.abs(A[i, :i + 1]) > tol)
        p[i] = i - cols[0] if len(cols) else 0
    for j in range(n):
        rows = np.flatnonzero(np.abs(A[:j + 1, j]) > tol)
        q[j] = j - rows[0] if len(rows) else 0
    return p, q


def is_skyline_preserved(A, tol=1e-12):
    """[S4] Thm 4.18: do the LU factors have the same skyline profile as A?"""
    L, U = crout_lu(A)
    p, q = skyline_profile(A, tol)
    pl, _ = skyline_profile(L, tol)
    _, qu = skyline_profile(U, tol)
    return bool(np.all(pl <= p) and np.all(qu <= q))



if __name__ == "__main__":
    rng = np.random.default_rng(0)

    A = np.array([[2.0, 1, 1], [4, -6, 0], [-2, 7, 2]])
    L, U = crout_lu(A)
    print("Crout LU, ||A - LU|| =", np.abs(A - L @ U).max())
    print("in-place form agrees:", np.abs(crout_lu_inplace(A) - (np.tril(L, -1) + U)).max())

    print("\n--- banded: cost O(n p q) [S4 Thm 4.12] ---")
    for n in (40, 80, 160, 320):
        B = np.diag(4.0 * np.ones(n)) + np.diag(-np.ones(n - 1), 1) + np.diag(-np.ones(n - 1), -1)
        _, _, ops = banded_lu(B, 1, 1, count_ops=True)
        print(f"  tridiagonal n={n:4d}: ops={ops:6d}  ops/n = {ops / n:.1f}   (O(n) since p=q=1)")
    for p in (1, 2, 4, 8):
        n = 200
        B = sum(np.diag(rng.standard_normal(n - abs(k)), k) for k in range(-p, p + 1))
        B += np.diag(20.0 * np.ones(n))
        _, _, ops = banded_lu(B, p, p, count_ops=True)
        print(f"  n=200, p=q={p}: ops={ops:7d}  ops/(n p q) = {ops / (n * p * p):.2f}")

    print("\n--- banded Cholesky keeps the bandwidth [S4 Rem. 4.15] ---")
    n, p = 60, 3
    M = rng.standard_normal((n, n))
    S = np.triu(np.tril(M @ M.T, p), -p) + np.diag(30.0 * np.ones(n))
    C = banded_cholesky(S, p)
    print("  ||S - C C^T|| =", np.abs(S - C @ C.T).max(), " bandwidth of C:", bandwidths(C)[0])

    print("\n--- skyline: the pattern is inherited [S4 Thm 4.18, Fig. 4.5] ---")
    Lk = np.array([[1., 0, 0, 0, 0, 0, 0],
                   [0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0, 0, 0],
                   [1, 2, 3, 1, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0],
                   [1, 2, 3, 4, 5, 6, 1]])
    Sk = Lk @ Lk.T                       # the SPD matrix of [S4] Fig. 4.5
    Ls = banded_cholesky(Sk, p=6)
    print("  A nnz =", int((Sk != 0).sum()), " Cholesky factor nnz =", int((np.abs(Ls) > 1e-12).sum()))
    print("  factor equals the one printed in [S4] Fig. 4.5:", np.abs(Ls - Lk).max() < 1e-12)
    print("  profile preserved:", is_skyline_preserved(Sk))
    rev = Sk[::-1, ::-1]                 # relabel backwards -> arrowhead, full fill-in
    print("  reversed ordering, Cholesky nnz =",
          int((np.abs(banded_cholesky(rev, p=6)) > 1e-12).sum()), "(fill-in)")
