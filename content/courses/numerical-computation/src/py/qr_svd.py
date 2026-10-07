"""Gram-Schmidt, Householder QR, power method, QR algorithm, SVD (notes 06, 07, 09).

Implements [S4 §4.7.2] classical and modified Gram-Schmidt, [S4 §4.7.3] (CSE)
Householder QR with implicit Q, [S4 §5.2] least squares via QR (qr_solve),
[S4 §7.1] the power method (Alg. 17), [S4 §7.5] (CSE) the unshifted QR
algorithm (Alg. 23), and [S4 §5.3.4] low-rank approximation (Eckart-Young,
Thm 5.15).  The one-sided Jacobi SVD is background, not in [S4].
"""
import numpy as np


# ---------------------------------------------------------------- Gram-Schmidt
def gram_schmidt_classical(A):
    """q_j = a_j - sum_{i<j} (q_i^T a_j) q_i, normalised.  All projections use
    the ORIGINAL a_j, so rounding errors are not removed: loss of
    orthogonality ~ kappa(A)^2 u."""
    A = np.asarray(A, float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    for j in range(n):
        v = A[:, j].copy()
        for i in range(j):
            R[i, j] = Q[:, i] @ A[:, j]
            v -= R[i, j] * Q[:, i]
        R[j, j] = np.sqrt(v @ v)
        Q[:, j] = v / R[j, j]
    return Q, R


def gram_schmidt_modified(A):
    """Same arithmetic count, but each projection uses the already-updated
    v: loss of orthogonality ~ kappa(A) u."""
    A = np.asarray(A, float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    for j in range(n):
        v = A[:, j].copy()
        for i in range(j):
            R[i, j] = Q[:, i] @ v
            v -= R[i, j] * Q[:, i]
        R[j, j] = np.sqrt(v @ v)
        Q[:, j] = v / R[j, j]
    return Q, R


# ---------------------------------------------------------------- Householder
def householder_vector(x):
    """v such that H = I - 2 v v^T / (v^T v) maps x to -sign(x_0) ||x|| e_1.
    The sign choice avoids cancellation in v_0 = x_0 + sign(x_0)||x||."""
    x = np.asarray(x, float)
    alpha = -np.copysign(np.sqrt(x @ x), x[0] if x[0] != 0 else 1.0)
    v = x.copy()
    v[0] -= alpha
    return v, alpha


def householder_qr(A):
    """A = Q R with Q orthogonal (m x m), R upper triangular (m x n).
    Cost 2 m n^2 - 2 n^3/3 flops; backward stable: computed Q R = A + dA,
    ||dA|| = O(u ||A||), and Q orthogonal to working precision."""
    R = np.array(A, float)
    m, n = R.shape
    Q = np.eye(m)
    for k in range(min(m - 1, n)):
        v, alpha = householder_vector(R[k:, k])
        vv = v @ v
        if vv == 0:
            continue
        R[k:, k:] -= 2 * np.outer(v, v @ R[k:, k:]) / vv     # H applied from the left
        R[k + 1:, k] = 0.0
        R[k, k] = alpha
        Q[:, k:] -= 2 * np.outer(Q[:, k:] @ v, v) / vv       # Q <- Q H
    return Q, R


def qr_solve(A, b):
    """Least squares min ||A x - b||: R_1 x = (Q^T b)_{1:n}.  Residual norm is
    ||(Q^T b)_{n+1:m}||.  Avoids forming A^T A (kappa instead of kappa^2)."""
    from linsolve import back_substitution
    A, b = np.asarray(A, float), np.asarray(b, float)
    n = A.shape[1]
    Q, R = householder_qr(A)
    return back_substitution(R[:n, :n], (Q.T @ b)[:n])


# ---------------------------------------------------------------- eigenvalues
def power_method(A, iters=1000, tol=1e-12):
    """Dominant eigenpair; converges like |lambda_2/lambda_1|^k."""
    A = np.asarray(A, float)
    x = np.ones(len(A)) / np.sqrt(len(A))
    lam = 0.0
    for _ in range(iters):
        y = A @ x
        x_new = y / np.sqrt(y @ y)
        lam_new = x_new @ A @ x_new                 # Rayleigh quotient
        converged = np.max(np.abs(x_new - x)) < tol or np.max(np.abs(x_new + x)) < tol
        x, lam = x_new, lam_new
        if converged:
            break
    return lam, x


def qr_algorithm(A, iters=500, tol=1e-12):
    """Unshifted QR iteration A_{k+1} = R_k Q_k (= Q_k^T A_k Q_k, similar to A).
    For symmetric A with distinct |eigenvalues| it converges to diag(lambda),
    rate |lambda_{i+1}/lambda_i|.  Returns eigenvalues sorted descending."""
    Ak = np.array(A, float)
    for _ in range(iters):
        Q, R = householder_qr(Ak)
        Ak = R @ Q
        if np.max(np.abs(np.tril(Ak, -1))) < tol:
            break
    return np.sort(np.diag(Ak))[::-1]


# ---------------------------------------------------------------- SVD
def jacobi_svd(A, tol=1e-15, sweeps=60):
    """One-sided Jacobi (Hestenes): rotate column pairs (i, j) of A from the
    right until all columns are mutually orthogonal, U Sigma = A V.
    For each pair: alpha = ||a_i||^2, beta = ||a_j||^2, gamma = a_i . a_j,
    zeta = (beta - alpha)/(2 gamma), t = sign(zeta)/(|zeta| + sqrt(1 + zeta^2)),
    c = 1/sqrt(1+t^2), s = c t.  Returns U (m x n), sigma (desc), V (n x n).
    Quadratic convergence; accurate to high relative precision."""
    U = np.array(A, float)
    m, n = U.shape
    V = np.eye(n)
    for _ in range(sweeps):
        off = 0.0
        for i in range(n - 1):
            for j in range(i + 1, n):
                alpha, beta, gamma = U[:, i] @ U[:, i], U[:, j] @ U[:, j], U[:, i] @ U[:, j]
                if abs(gamma) <= tol * np.sqrt(alpha * beta):
                    continue
                off = max(off, abs(gamma) / np.sqrt(alpha * beta))
                zeta = (beta - alpha) / (2 * gamma)
                t = np.sign(zeta) / (abs(zeta) + np.sqrt(1 + zeta * zeta)) if zeta != 0 else 1.0
                c = 1 / np.sqrt(1 + t * t)
                s = c * t
                ui, uj = U[:, i].copy(), U[:, j].copy()
                U[:, i], U[:, j] = c * ui - s * uj, s * ui + c * uj
                vi, vj = V[:, i].copy(), V[:, j].copy()
                V[:, i], V[:, j] = c * vi - s * vj, s * vi + c * vj
        if off < tol:
            break
    sigma = np.sqrt(np.sum(U * U, axis=0))
    order = np.argsort(sigma)[::-1]
    sigma, U, V = sigma[order], U[:, order], V[:, order]
    nz = sigma > 0
    U[:, nz] /= sigma[nz]
    return U, sigma, V


def low_rank(A, k):
    """Best rank-k approximation A_k = sum_{i<k} sigma_i u_i v_i^T
    (Eckart-Young: ||A - A_k||_2 = sigma_{k+1}, ||.||_F = sqrt(sum_{i>k} sigma_i^2))."""
    U, s, V = jacobi_svd(A)
    return (U[:, :k] * s[:k]) @ V[:, :k].T, s


def cond2(A):
    s = jacobi_svd(A)[1]
    return s[0] / s[-1]


if __name__ == "__main__":
    # ill-conditioned columns: Gram-Schmidt loses orthogonality, Householder does not
    rng = np.random.default_rng(0)
    m, n = 60, 12
    U0, _ = householder_qr(rng.standard_normal((m, m)))
    V0, _ = householder_qr(rng.standard_normal((n, n)))
    S = np.logspace(0, -9, n)
    A = U0[:, :n] * S @ V0.T                       # kappa = 1e9
    print(f"A is {m}x{n} with kappa_2 = {cond2(A):.1e}; ||Q^T Q - I||:")
    for name, fn in (("classical GS", gram_schmidt_classical),
                     ("modified GS", gram_schmidt_modified),
                     ("Householder", householder_qr)):
        Q, R = fn(A)
        Qn = Q[:, :n]
        print(f"  {name:13s} {np.abs(Qn.T @ Qn - np.eye(n)).max():.1e}   "
              f"||A - QR|| = {np.abs(A - Q @ R).max():.1e}")

    x = np.linspace(0, 1, 30)
    y = 2 + 3 * x - x ** 2 + 0.05 * rng.standard_normal(30)
    Av = np.column_stack([x ** k for k in range(3)])
    print("least squares via QR:", qr_solve(Av, y), "(true 2, 3, -1 + noise)")

    S3 = np.array([[4., 1., 0.], [1., 3., 1.], [0., 1., 2.]])
    print("eigenvalues (QR algorithm):", qr_algorithm(S3))
    print("dominant (power method)   :", power_method(S3)[0])

    B = rng.standard_normal((8, 5))
    Ub, sb, Vb = jacobi_svd(B)
    print("Jacobi SVD sigma:", sb)
    print("  ||U S V^T - B|| =", np.abs((Ub * sb) @ Vb.T - B).max(),
          " ||V^T V - I|| =", np.abs(Vb.T @ Vb - np.eye(5)).max())
    Bk, s = low_rank(B, 2)
    print(f"  rank-2 error (2-norm) = {jacobi_svd(B - Bk)[1][0]:.6f}, sigma_3 = {s[2]:.6f}")
