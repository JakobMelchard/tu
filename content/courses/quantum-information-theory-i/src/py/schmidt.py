"""Schmidt decomposition and purification.

Note 04. A bipartite ket |psi> = sum_{ij} C_ij |i>|j> has coefficient matrix C
(d_A x d_B). The singular value decomposition C = U diag(s) V^dag gives
C = sum_k s_k a_k b_k^T with a_k = U[:, k] and b_k = (row k of V^dag), i.e.
|psi> = sum_k s_k |a_k>|b_k>. The Schmidt rank is the number of
nonzero s_k and rho_A = C C^dag, rho_B = C^T C^* share the spectrum {s_k^2}.

Purification: rho = sum_k p_k |k><k|  ->  |Psi> = sum_k sqrt(p_k) |k>|k>_R, and
the canonical purification (sqrt(rho) x I) |Omega>, |Omega> = sum_i |i>|i>.
Any two purifications on the same reference differ by a unitary on R
(`purification_unitary` finds it from the two Schmidt decompositions).
Run `python schmidt.py`.
"""
from __future__ import annotations

import numpy as np

from states import dm, partial_trace


def schmidt(psi: np.ndarray, da: int, db: int, tol: float = 1e-12):
    """Return (coeffs, A, B) with psi = sum_k coeffs[k] A[:, k] (x) B[:, k]."""
    C = np.asarray(psi, dtype=complex).reshape(da, db)
    U, s, Vh = np.linalg.svd(C)
    r = int((s > tol).sum())
    return s[:r], U[:, :r], Vh[:r, :].T


def schmidt_rank(psi: np.ndarray, da: int, db: int, tol: float = 1e-10) -> int:
    return len(schmidt(psi, da, db, tol)[0])


def reconstruct(coeffs, A, B) -> np.ndarray:
    return sum(c * np.kron(A[:, k], B[:, k]) for k, c in enumerate(coeffs))


def purify(rho: np.ndarray) -> np.ndarray:
    """Spectral purification sum_k sqrt(p_k) |e_k>|k>_R on C^d x C^d."""
    p, V = np.linalg.eigh(rho)
    p = np.clip(p, 0, None)
    d = rho.shape[0]
    return sum(np.sqrt(p[k]) * np.kron(V[:, k], np.eye(d)[k]) for k in range(d))


def canonical_purification(rho: np.ndarray) -> np.ndarray:
    """(sqrt(rho) x I) |Omega> with |Omega> = sum_i |ii> (unnormalised)."""
    d = rho.shape[0]
    p, V = np.linalg.eigh(rho)
    sq = (V * np.sqrt(np.clip(p, 0, None))) @ V.conj().T
    return np.kron(sq, np.eye(d)) @ np.eye(d).reshape(d * d)


def purification_unitary(psi1: np.ndarray, psi2: np.ndarray, d: int, dr: int) -> np.ndarray:
    """Unitary U_R with (I x U_R)|psi1> = |psi2>, both purifying the same rho_A.

    In matrix form psi_i = C_i (d x dr) and C_2 = C_1 U^T. With rho = C C^dag equal,
    polar decompositions C_i = sqrt(rho) W_i give U^T = W_1^dag W_2 on the support;
    we get W_i from the SVDs and complete to a unitary on the kernel.
    """
    C1, C2 = psi1.reshape(d, dr), psi2.reshape(d, dr)
    M = C1.conj().T @ C2  # = W1^dag rho W2 ; its polar unitary is W1^dag W2 on supp
    U, _, Vh = np.linalg.svd(M)
    Ut = U @ Vh
    return Ut.T


def demo() -> None:
    rng = np.random.default_rng(4)
    from states import random_pure, random_state
    psi = random_pure(6, rng)
    c, A, B = schmidt(psi, 2, 3)
    print("random 2x3 ket: Schmidt coefficients", c.round(4), " sum c^2 =", round(float(c @ c), 12))
    print("reconstruction error", np.abs(reconstruct(c, A, B) - psi).max())
    ra = partial_trace(dm(psi), [2, 3], [0])
    print("eigenvalues of rho_A", np.sort(np.linalg.eigvalsh(ra))[::-1].round(4))
    prod = np.kron([1, 0], [0, 1, 0])
    print("product ket Schmidt rank", schmidt_rank(prod, 2, 3))
    rho = random_state(3, rng, rank=2)
    P = purify(rho)
    print("purification of a rank-2 qutrit state: tr_R error",
          np.abs(partial_trace(dm(P), [3, 3], [0]) - rho).max())
    Q = canonical_purification(rho)
    U = purification_unitary(P, Q, 3, 3)
    print("two purifications related by U_R: error",
          np.abs(np.kron(np.eye(3), U) @ P - Q).max(), " unitary:",
          np.allclose(U @ U.conj().T, np.eye(3)))


if __name__ == "__main__":
    demo()
