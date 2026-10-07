"""Givens rotations, Hessenberg QR, QR with column pivoting (note 06).

Implements [S4 §4.7.4-4.7.5] (CSE; Lem. 4.53, Ex. 4.54-4.55).  Givens
rotations zero one entry at a time; a dense QR this way costs more than
Householder, but for an upper Hessenberg matrix only n-1 rotations are needed,
so the factorisation is O(n^2) and R Q is Hessenberg again: the two facts that
make the QR *algorithm* affordable (note 09).
"""
import numpy as np


def givens_rotation(a, b):
    """(c, s) with [[c, s], [-s, c]]^T (a, b)^T = (r, 0)^T, i.e. c*b = s*a.

    [S4] Lem. 4.53(iv): choose c = 1, s = 0 when b = 0, else cot(theta) = a/b.
    """
    if b == 0.0:
        return 1.0, 0.0
    r = np.hypot(a, b)
    return a / r, b / r


def apply_givens_left(A, i, j, c, s):
    """G(i, j, theta)^T A: touches only rows i and j ([S4] Lem. 4.53(iii))."""
    A = np.array(A, float)
    ri, rj = A[i].copy(), A[j].copy()
    A[i] = c * ri + s * rj
    A[j] = -s * ri + c * rj
    return A


def apply_givens_right(A, i, j, c, s):
    """A G(i, j, theta): touches only columns i and j ([S4] Lem. 4.53(ii))."""
    A = np.array(A, float)
    ci, cj = A[:, i].copy(), A[:, j].copy()
    A[:, i] = c * ci - s * cj
    A[:, j] = s * ci + c * cj
    return A


def givens_qr(A, count_rotations=False):
    """QR by Givens rotations, annihilating below the diagonal column by column.

    O(n^2) rotations for a dense matrix, hence more expensive than Householder
    ([S4] sec. 4.7.5); included for the comparison and for hessenberg_qr below.
    """
    A = np.array(A, float)
    m, n = A.shape
    Q = np.eye(m)
    rot = 0
    for j in range(min(m, n)):
        for i in range(m - 1, j, -1):
            if A[i, j] == 0.0:
                continue
            c, s = givens_rotation(A[i - 1, j], A[i, j])
            A = apply_givens_left(A, i - 1, i, c, s)
            Q = apply_givens_right(Q, i - 1, i, c, -s)      # accumulate G^T
            rot += 1
    return (Q, A, rot) if count_rotations else (Q, A)


def hessenberg_qr(H, count_rotations=False):
    """QR of an upper Hessenberg matrix with n-1 Givens rotations, [S4] Ex. 4.55.

    Only the subdiagonal has to be annihilated, so this is O(n^2) -- O(n) for a
    tridiagonal (symmetric Hessenberg) matrix.
    """
    H = np.array(H, float)
    n = H.shape[0]
    Q = np.eye(n)
    rots = []
    for k in range(n - 1):
        if H[k + 1, k] == 0.0:
            rots.append((k, 1.0, 0.0))
            continue
        c, s = givens_rotation(H[k, k], H[k + 1, k])
        H = apply_givens_left(H, k, k + 1, c, s)
        Q = apply_givens_right(Q, k, k + 1, c, -s)          # accumulate G^T
        rots.append((k, c, s))
    return (Q, H, len(rots)) if count_rotations else (Q, H)


def rq_product(H):
    """One step of the QR algorithm on a Hessenberg H: return R Q.

    [S4] sec. 4.7.5 shows R Q is upper Hessenberg again -- each right
    multiplication by a G(k, k+1)^T puts back exactly one subdiagonal entry.
    """
    Q, R = hessenberg_qr(H)
    return R @ Q


def is_hessenberg(A, tol=1e-12):
    A = np.asarray(A, float)
    n = A.shape[0]
    return all(abs(A[i, j]) <= tol for i in range(n) for j in range(n) if i > j + 1)


def qr_column_pivoting(A, tol=1e-12):
    """Rank-revealing QR: A P = Q R with |r_00| >= |r_11| >= ...  [S4] sec. 4.7.4.

    Householder steps, moving the column of largest remaining norm to the front.
    Returns (Q, R, piv, rank) with piv the permutation as an index vector, so
    A[:, piv] = Q @ R.
    """
    A = np.array(A, float)
    m, n = A.shape
    R = A.copy()
    Q = np.eye(m)
    piv = np.arange(n)
    colnorm = (R ** 2).sum(axis=0)
    rank = 0
    for k in range(min(m, n)):
        j = k + int(np.argmax(colnorm[k:]))
        if colnorm[j] <= tol * max(1.0, colnorm.max()):
            break
        if j != k:
            R[:, [k, j]] = R[:, [j, k]]
            piv[[k, j]] = piv[[j, k]]
            colnorm[[k, j]] = colnorm[[j, k]]
        x = R[k:, k]
        nx = np.linalg.norm(x)
        if nx > tol:
            lam = np.sign(x[0]) * nx if x[0] != 0 else nx     # [S4] Lem. 4.49
            v = x.copy()
            v[0] += lam
            nv = np.linalg.norm(v)
            if nv > tol:
                v = v / nv
                R[k:, :] -= 2.0 * np.outer(v, v @ R[k:, :])
                Q[:, k:] -= 2.0 * np.outer(Q[:, k:] @ v, v)
        rank = k + 1
        colnorm[k + 1:] = (R[k + 1:, k + 1:] ** 2).sum(axis=0)
    R = np.triu(R)
    return Q, R, piv, rank


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    # [S4] Ex. 4.54, worked in the note
    A = np.array([[1.0, 1, 1], [1, 0, 1], [0, 1, 1]])
    Q, R, rot = hessenberg_qr(A, count_rotations=True)
    print("[S4] Ex. 4.54, Hessenberg QR with", rot, "Givens rotations")
    print("R =\n", R)
    print("|R| diag:", np.abs(np.diag(R)), " expect sqrt2, sqrt(3/2), 1/sqrt3 =",
          [np.sqrt(2), np.sqrt(1.5), 1 / np.sqrt(3)])
    print("||A - QR|| =", np.abs(A - Q @ R).max(), "  Q orthogonal:",
          np.abs(Q.T @ Q - np.eye(3)).max())

    print("\nR Q is Hessenberg again [S4 sec. 4.7.5]:")
    H = A.copy()
    for step in range(4):
        H = rq_product(H)
        print(f"  step {step + 1}: Hessenberg = {is_hessenberg(H)}   diag = {np.diag(H)}")
    print("  eigenvalues of A:", np.sort(np.linalg.eigvals(A).real))

    print("\nrotation count: n-1 for Hessenberg, O(n^2) for dense [S4 Ex. 4.55]")
    rng = np.random.default_rng(0)
    for n in (5, 10, 20, 40):
        Hn = np.triu(rng.standard_normal((n, n)), -1)
        D = rng.standard_normal((n, n))
        _, _, rh = hessenberg_qr(Hn, count_rotations=True)
        _, _, rd = givens_qr(D, count_rotations=True)
        print(f"  n={n:3d}:  Hessenberg {rh:4d} (= n-1)   dense {rd:5d} (= n(n-1)/2)")

    print("\nQR with column pivoting reveals the rank [S4 sec. 4.7.4]")
    B = rng.standard_normal((8, 3))
    B = np.column_stack([B, B[:, 0] + 2 * B[:, 1]])      # rank 3, 4 columns
    Qp, Rp, piv, rank = qr_column_pivoting(B)
    print("  |diag R| =", np.abs(np.diag(Rp)), " numerical rank =", rank,
          " (numpy:", np.linalg.matrix_rank(B), ")")
    print("  ||A[:,piv] - QR|| =", np.abs(B[:, piv] - Qp @ Rp).max())
