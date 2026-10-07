"""Compressed sparse row matrices and iterative solvers, pure numpy (topic 05).

CSR: values and column indices row by row, row_ptr[i]:row_ptr[i+1] is row i.
Solvers for SPD systems: Jacobi, Gauss-Seidel / SOR (Python loops, slow but
explicit), conjugate gradients (vectorised, only needs matvec).

Run `python3 csr.py` for iteration counts on the 2D Poisson system.
C++ counterpart: ../cpp/csr.cpp.

Sources: CSR [S22 §3.4]; Jacobi / Gauss-Seidel / SOR as splittings A = M - K
[S22 ch. 4]; conjugate gradients [S15]. Test: test_csr.py, against scipy.sparse.
"""
import numpy as np


class CSR:
    def __init__(self, n, row_ptr, col, val):
        self.n = n
        self.row_ptr = np.asarray(row_ptr, dtype=np.int64)
        self.col = np.asarray(col, dtype=np.int64)
        self.val = np.asarray(val, dtype=float)

    @classmethod
    def from_dense(cls, A):
        A = np.asarray(A)
        row_ptr, col, val = [0], [], []
        for i in range(A.shape[0]):
            nz = np.nonzero(A[i])[0]
            col.extend(nz)
            val.extend(A[i, nz])
            row_ptr.append(len(col))
        return cls(A.shape[0], row_ptr, col, val)

    @classmethod
    def poisson2d(cls, N):
        """5-point -Laplacian on (N-1)^2 interior unknowns, k = (i-1)(N-1) + (j-1)."""
        m = N - 1
        row_ptr, col, val = [0], [], []
        for i in range(m):
            for j in range(m):
                k = i * m + j
                for kk, v in ((k - m, -1), (k - 1, -1), (k, 4), (k + 1, -1), (k + m, -1)):
                    inside = 0 <= kk < m * m and not (kk == k - 1 and j == 0) and not (kk == k + 1 and j == m - 1)
                    if inside:
                        col.append(kk)
                        val.append(v * N**2)
                row_ptr.append(len(col))
        return cls(m * m, row_ptr, col, val)

    @property
    def nnz(self):
        return len(self.val)

    def matvec(self, x):
        y = np.zeros(self.n)
        for i in range(self.n):  # explicit loop version of what scipy does in C
            s, e = self.row_ptr[i], self.row_ptr[i + 1]
            y[i] = self.val[s:e] @ x[self.col[s:e]]
        return y

    def diag(self):
        d = np.zeros(self.n)
        for i in range(self.n):
            s, e = self.row_ptr[i], self.row_ptr[i + 1]
            hit = self.col[s:e] == i
            d[i] = self.val[s:e][hit].sum()
        return d

    def to_dense(self):
        A = np.zeros((self.n, self.n))
        for i in range(self.n):
            s, e = self.row_ptr[i], self.row_ptr[i + 1]
            A[i, self.col[s:e]] = self.val[s:e]
        return A


def _rel_res(A, b, x):
    return np.linalg.norm(b - A.matvec(x)) / np.linalg.norm(b)


def jacobi(A, b, tol=1e-8, maxit=10000):
    x = np.zeros(A.n)
    d = A.diag()
    for it in range(1, maxit + 1):
        x = x + (b - A.matvec(x)) / d  # x_new = D^{-1}(b - (A - D) x) = x + D^{-1} r
        if _rel_res(A, b, x) < tol:
            return x, it
    return x, maxit


def sor(A, b, omega=1.0, tol=1e-8, maxit=10000):
    """omega = 1 is Gauss-Seidel. Uses freshly updated x_j for j < i inside the sweep."""
    x = np.zeros(A.n)
    for it in range(1, maxit + 1):
        for i in range(A.n):
            s, e = A.row_ptr[i], A.row_ptr[i + 1]
            cols, vals = A.col[s:e], A.val[s:e]
            diag = vals[cols == i][0]
            off = vals[cols != i] @ x[cols[cols != i]]
            x[i] = (1 - omega) * x[i] + omega * (b[i] - off) / diag
        if _rel_res(A, b, x) < tol:
            return x, it
    return x, maxit


def cg(A, b, tol=1e-8, maxit=10000, precond=None):
    """(Preconditioned) conjugate gradients; precond is a function r -> M^{-1} r."""
    M = precond or (lambda r: r)
    x = np.zeros(A.n)
    r = b - A.matvec(x)
    z = M(r)
    p = z.copy()
    rz = r @ z
    bn = np.linalg.norm(b)
    for it in range(1, maxit + 1):
        Ap = A.matvec(p)
        alpha = rz / (p @ Ap)
        x += alpha * p
        r -= alpha * Ap
        if np.linalg.norm(r) / bn < tol:
            return x, it
        z = M(r)
        rz_new = r @ z
        p = z + (rz_new / rz) * p
        rz = rz_new
    return x, maxit


if __name__ == "__main__":
    N = 16
    A = CSR.poisson2d(N)
    x = np.linspace(0, 1, N + 1)
    X, Y = np.meshgrid(x[1:-1], x[1:-1], indexing="ij")
    u_ex = (X * (1 - X) * Y * (1 - Y) * np.exp(X * Y)).ravel()
    b = A.matvec(u_ex)  # consistent right-hand side: solvers must recover u_ex exactly
    print(f"2D Poisson N={N}: n={A.n}, nnz={A.nnz}")
    omega = 2 / (1 + np.sin(np.pi / N))
    for name, solver in [("Jacobi", jacobi), ("Gauss-Seidel", lambda A, b: sor(A, b, 1.0)),
                         (f"SOR w={omega:.3f}", lambda A, b: sor(A, b, omega)), ("CG", cg)]:
        u, it = solver(A, b)
        print(f"{name:14s} {it:6d} iterations, max err {np.max(np.abs(u - u_ex)):.2e}")
