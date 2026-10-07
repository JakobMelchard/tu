"""Linear algebra over GF(2): row reduction, rank, null space, solving (used by Simon's algorithm).

Belongs to the Part C note on Simon's algorithm (C04).

Matrices are int numpy arrays with entries 0/1; arithmetic is mod 2 (XOR).
Implements: gf2_rref, gf2_rank, gf2_nullspace, gf2_solve.
"""
import numpy as np


def gf2_rref(A):
    """Reduced row echelon form mod 2. Returns (R, pivot_columns)."""
    R = np.array(A, dtype=int) % 2
    rows, cols = R.shape
    pivots = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        nz = np.nonzero(R[r:, c])[0]
        if len(nz) == 0:
            continue
        p = r + nz[0]
        R[[r, p]] = R[[p, r]]                     # bring a pivot row up
        for i in range(rows):                     # XOR the pivot row into all others
            if i != r and R[i, c]:
                R[i] ^= R[r]
        pivots.append(c)
        r += 1
    return R, pivots


def gf2_rank(A):
    return len(gf2_rref(A)[1])


def gf2_nullspace(A):
    """Basis of {x : A x = 0 mod 2} as rows of an int array (shape (cols - rank, cols))."""
    R, pivots = gf2_rref(A)
    cols = R.shape[1]
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for f in free:                                # one basis vector per free column
        x = np.zeros(cols, dtype=int)
        x[f] = 1
        for i, p in enumerate(pivots):            # pivot var = sum of free vars in its row
            x[p] = R[i, f]
        basis.append(x)
    return np.array(basis, dtype=int).reshape(len(basis), cols)


def gf2_solve(A, b):
    """One solution x of A x = b mod 2, or None if inconsistent."""
    A = np.array(A, dtype=int) % 2
    aug = np.hstack([A, np.array(b, dtype=int).reshape(-1, 1) % 2])
    R, pivots = gf2_rref(aug)
    cols = A.shape[1]
    if cols in pivots:                            # pivot in the augmented column: 0 = 1
        return None
    x = np.zeros(cols, dtype=int)
    for i, p in enumerate(pivots):
        x[p] = R[i, cols]
    return x


if __name__ == "__main__":
    A = np.array([[1, 1, 0, 1], [0, 1, 1, 1], [1, 0, 1, 0]])
    R, piv = gf2_rref(A)
    print("A =\n", A, "\nrref =\n", R, "\npivots", piv, "rank", gf2_rank(A))
    N = gf2_nullspace(A)
    print("nullspace basis rows:", N.tolist(), " A N^T mod 2 =", ((A @ N.T) % 2).tolist())
    print("solve A x = [1,0,1]:", gf2_solve(A, [1, 0, 1]))
