"""Inverse iteration, Rayleigh quotient iteration, orthogonal iteration, shifted QR (note 09).

Implements [S4 §7.2-7.6] (Alg. 18-21, 24; Thm 7.10).  The power method
[S4 §7.1] is qr_svd.power_method and the unshifted QR algorithm [S4 §7.5] is
qr_svd.qr_algorithm.  §7.4 onwards is CSE-only ([S4] writes "END OF LECTURE
FOR VISUAL COMPUTING" at the end of §7.3).
"""
import numpy as np
import scipy.linalg

from givens import hessenberg_qr, is_hessenberg


def rayleigh_quotient(A, x):
    """lambda = x^T A x / ||x||_2^2,  [S4] sec. 7."""
    x = np.asarray(x, float)
    return float(x @ (np.asarray(A, float) @ x) / (x @ x))


def subspace_angle(x, y):
    """d(span x, span y) = |sin phi|,  [S4] Def. 7.3.

    0 when the lines coincide, 1 when they are orthogonal.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    c = abs(x @ y) / (np.linalg.norm(x) * np.linalg.norm(y))
    return float(np.sqrt(max(0.0, 1.0 - min(1.0, c) ** 2)))


# ------------------------------------------------------- inverse iteration
def inverse_iteration(A, x0=None, iters=50, tol=1e-14, history=False):
    """Power iteration on A^{-1}: converges to the smallest |lambda|.

    [S4] Alg. 18 and Rem. 7.6: rate |lambda_n / lambda_{n-1}|.  The LU
    factorisation is computed once and reused, so each step costs O(n^2).
    """
    return inverse_iteration_shift(A, 0.0, x0, iters, tol, history)


def inverse_iteration_shift(A, mu, x0=None, iters=50, tol=1e-14, history=False):
    """Inverse iteration with a fixed shift,  [S4] Alg. 19.

    Converges to the eigenvalue closest to mu, at the rate
    |lambda_n - mu| / |lambda_{n-1} - mu|  ([S4] Thm 7.7).
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    x = np.ones(n) if x0 is None else np.array(x0, float)
    x /= np.linalg.norm(x)
    lu = scipy.linalg.lu_factor(A - mu * np.eye(n))      # factor once
    lams, xs = [], []
    lam = rayleigh_quotient(A, x)
    for _ in range(iters):
        xt = scipy.linalg.lu_solve(lu, x)
        x = xt / np.linalg.norm(xt)
        new = rayleigh_quotient(A, x)
        lams.append(new)
        xs.append(x.copy())
        if abs(new - lam) < tol * max(1.0, abs(new)):
            lam = new
            break
        lam = new
    return (lam, x, np.array(lams), xs) if history else (lam, x)


def rayleigh_quotient_iteration(A, x0=None, iters=30, tol=1e-14, history=False):
    """Inverse iteration whose shift is the current Rayleigh quotient.

    [S4] Alg. 20.  Cubic convergence for symmetric A ([S4] Thm 7.8), quadratic
    in general ([S4] Rem. 7.9) -- but the shift changes every step, so each one
    costs a fresh O(n^3) factorisation.
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    x = np.ones(n) if x0 is None else np.array(x0, float)
    x /= np.linalg.norm(x)
    lams, xs = [], []
    for _ in range(iters):
        lam = rayleigh_quotient(A, x)
        lams.append(lam)
        xs.append(x.copy())
        try:
            xt = np.linalg.solve(A - lam * np.eye(n), x)
        except np.linalg.LinAlgError:
            break                                        # exactly singular: converged
        nx = np.linalg.norm(xt)
        if not np.isfinite(nx) or nx == 0.0:
            break
        xn = xt / nx
        if np.linalg.norm(xn - x) < tol or np.linalg.norm(xn + x) < tol:
            x = xn
            break
        x = xn
    lam = rayleigh_quotient(A, x)
    return (lam, x, np.array(lams), xs) if history else (lam, x)


def eigen_residual_bound(A, x, lam=None, symmetric=None):
    """The three bounds of [S4] Thm 7.10 for r = A x - lam x, ||x|| = 1.

    Returns a dict with the residual norm, the true distance to the spectrum,
    and the applicable bounds:
        general    cond_2(T) ||r||      (T the eigenvector matrix)
        symmetric  ||r||
        rayleigh   C ||r||^2            (symmetric A, lam the Rayleigh quotient)
    """
    A = np.asarray(A, float)
    x = np.asarray(x, float)
    x = x / np.linalg.norm(x)
    if symmetric is None:
        symmetric = np.allclose(A, A.T, atol=1e-12)
    if lam is None:
        lam = rayleigh_quotient(A, x)
    r = np.linalg.norm(A @ x - lam * x)
    ev = np.linalg.eigvalsh(A) if symmetric else np.linalg.eigvals(A)
    dist = float(np.min(np.abs(ev - lam)))
    out = {"residual": r, "distance": dist, "lambda": lam}
    if symmetric:
        out["bound_symmetric"] = r
        out["bound_rayleigh"] = r ** 2
        out["cond_T"] = 1.0
    else:
        w, T = np.linalg.eig(A)
        out["cond_T"] = float(np.linalg.cond(T))
        out["bound_general"] = out["cond_T"] * r
    return out


# ---------------------------------------------------- orthogonal iteration
def orthogonal_iteration(A, k=None, iters=200, X0=None, history=False):
    """Power iteration on a k-dimensional subspace,  [S4] Alg. 21.

    The columns of Q_l span A^l S^0; by [S4] Thm 7.12 the subspace converges to
    the invariant subspace of the k dominant eigenvectors, so the off-diagonal
    block of Q_l^T A Q_l tends to zero ([S4] Rem. 7.13).
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    k = n if k is None else k
    X = np.eye(n, k) if X0 is None else np.array(X0, float)
    Q, _ = np.linalg.qr(X)
    offs = []
    for _ in range(iters):
        Q, _ = np.linalg.qr(A @ Q)
        if history:
            B = Q.T @ A @ Q
            offs.append(float(np.abs(np.tril(B, -1)).max()) if k == n else 0.0)
    return (Q, np.array(offs)) if history else Q


# ------------------------------------------------- Hessenberg, shifted QR
def hessenberg(A, return_q=False):
    """Orthogonal similarity reduction to upper Hessenberg form, O(n^3).

    [S4] sec. 7.6.1: H = Q^T A Q has the same eigenvalues as A, and every QR
    step on H then costs O(n^2) instead of O(n^3) ([S4] Ex. 4.55).
    Householder reflections acting on the trailing block.
    """
    A = np.array(A, float)
    n = A.shape[0]
    Q = np.eye(n)
    for k in range(n - 2):
        x = A[k + 1:, k]
        nx = np.linalg.norm(x)
        if nx == 0.0:
            continue
        lam = np.sign(x[0]) * nx if x[0] != 0 else nx    # [S4] Lem. 4.49 sign
        v = x.copy()
        v[0] += lam
        nv = np.linalg.norm(v)
        if nv == 0.0:
            continue
        v = v / nv
        A[k + 1:, :] -= 2.0 * np.outer(v, v @ A[k + 1:, :])
        A[:, k + 1:] -= 2.0 * np.outer(A[:, k + 1:] @ v, v)
        Q[:, k + 1:] -= 2.0 * np.outer(Q[:, k + 1:] @ v, v)
    A[np.tril_indices(n, -2)] = 0.0
    return (A, Q) if return_q else A


def wilkinson_shift(H):
    """Eigenvalue of the trailing 2x2 block closest to H[-1,-1]."""
    a, b, c, d = H[-2, -2], H[-2, -1], H[-1, -2], H[-1, -1]
    tr, det = a + d, a * d - b * c
    disc = tr * tr / 4 - det
    if disc >= 0:
        r = np.sqrt(disc)
        cands = [tr / 2 + r, tr / 2 - r]
        return min(cands, key=lambda z: abs(z - d))
    return d                                             # complex pair: no real shift


def shifted_qr(A, tol=1e-12, max_iter=500, count=False):
    """QR algorithm with Hessenberg reduction, shifts and deflation.

    [S4] Alg. 24 and sec. 7.6:
        H_l - mu I =: Q R,   H_{l+1} := R Q + mu I     (similar to H_l)
    with a Wilkinson shift, deflating whenever the last subdiagonal entry of the
    active block is negligible.  Returns the eigenvalues (real matrices with
    complex pairs fall back to the 2x2 blocks).
    """
    H = hessenberg(A)
    n = H.shape[0]
    evs = []
    hi = n
    iters = 0
    while hi > 0 and iters < max_iter:
        if hi == 1:
            evs.append(H[0, 0])
            break
        # deflate from the bottom
        deflated = True
        while deflated and hi > 1:
            deflated = False
            if abs(H[hi - 1, hi - 2]) <= tol * (abs(H[hi - 1, hi - 1]) + abs(H[hi - 2, hi - 2]) + tol):
                evs.append(H[hi - 1, hi - 1])
                hi -= 1
                H = H[:hi, :hi].copy()
                deflated = True
        if hi == 1:
            evs.append(H[0, 0])
            break
        if hi == 0:
            break
        mu = wilkinson_shift(H)
        Q, R = hessenberg_qr(H - mu * np.eye(hi))
        H = R @ Q + mu * np.eye(hi)
        iters += 1
    evs = np.array(sorted(evs))
    return (evs, iters) if count else evs


if __name__ == "__main__":
    np.set_printoptions(precision=8, suppress=True)
    A = np.array([[4.0, 1, 0], [1, 3, 1], [0, 1, 2]])
    exact = np.sort(np.linalg.eigvalsh(A))
    print("A =", A.tolist(), "\neigenvalues 3 +- sqrt3, 3 :", exact)

    print("\n--- inverse iteration [S4 Alg. 18, Rem. 7.6] ---")
    lam, x = inverse_iteration(A)
    print(f"  smallest |lambda| = {lam:.12f}  (expect {3 - np.sqrt(3):.12f})")

    print("\n--- inverse iteration with shift [S4 Alg. 19, Thm 7.7] ---")
    for mu in (1.0, 2.9, 4.5):
        lam, _ = inverse_iteration_shift(A, mu)
        print(f"  shift {mu:4.1f} -> {lam:.12f}   (closest eigenvalue "
              f"{exact[np.argmin(np.abs(exact - mu))]:.12f})")

    print("\n--- Rayleigh quotient iteration is cubic [S4 Thm 7.8] ---")
    lam, x, hist, _ = rayleigh_quotient_iteration(A, x0=[1.0, 0.4, 0.1], history=True)
    target = exact[np.argmin(np.abs(exact - lam))]
    err = np.abs(hist - target)
    err = err[err > 0]
    print("  errors:", err)
    if len(err) >= 3:
        print("  log-log slopes (expect ~3):",
              [round(np.log(err[i + 1]) / np.log(err[i]), 2) for i in range(len(err) - 1)
               if err[i] < 0.5])

    print("\n--- stopping criteria [S4 Thm 7.10] ---")
    for xx in ([1.0, 0.7, 0.2], [1.0, 0.0, 0.0]):
        d = eigen_residual_bound(A, xx)
        print(f"  ||r|| = {d['residual']:.3e}  dist = {d['distance']:.3e}  "
              f"<= ||r|| ({d['bound_symmetric']:.3e}), <= C||r||^2 ({d['bound_rayleigh']:.3e})")

    print("\n--- orthogonal iteration [S4 Alg. 21, Thm 7.12] ---")
    Q, offs = orthogonal_iteration(A, iters=40, history=True)
    print("  max |below diagonal| of Q^T A Q over the iteration:", offs[::10])
    print("  diag(Q^T A Q):", np.diag(Q.T @ A @ Q))

    print("\n--- shifted QR with deflation [S4 Alg. 24, sec. 7.6] ---")
    ev, it = shifted_qr(A, count=True)
    print(f"  eigenvalues {ev}  in {it} QR steps (n = 3)")
    rng = np.random.default_rng(0)
    for n in (5, 10, 20):
        M = rng.standard_normal((n, n))
        S = M + M.T
        ev, it = shifted_qr(S, count=True)
        err = np.abs(ev - np.sort(np.linalg.eigvalsh(S))).max()
        print(f"  symmetric n={n:3d}: max error {err:.2e} in {it:3d} QR steps"
              f"  ({it / n:.1f} per eigenvalue)")
