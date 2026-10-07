"""States and operators: density matrices, Bloch vectors, tensor products, partial trace.

Notes 01 (states and operators) and 02 (composite systems).
- ket -> density matrix, validity check (Hermitian, PSD, unit trace), purity
  tr rho^2, linear entropy S_L = 1 - tr rho^2 (and the normalised d/(d-1) form).
- Qubit Bloch decomposition rho = (I + r.sigma)/2, |r| <= 1, purity (1+|r|^2)/2.
- Generalised Gell-Mann basis of su(d), normalised tr(l_i l_j) = 2 delta_ij, and
  the generalised Bloch decomposition rho = I/d + (1/2) sum_i b_i l_i.
- Two-qubit decomposition rho = (I + a.s x I + I x b.s + sum t_ij s_i x s_j)/4, and
  its d_A x d_B generalisation in Gell-Mann bases (`bipartite_bloch`).
- Tensor products and the partial trace over any subset of subsystems.

Ordering convention: subsystem 0 is the leftmost tensor factor (np.kron order),
as in the ws2026 quantum-computing notes C01. Run `python states.py`.
"""
from __future__ import annotations

from functools import reduce

import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = (X, Y, Z)


def ket(*amps) -> np.ndarray:
    v = np.asarray(amps, dtype=complex).ravel()
    return v / np.linalg.norm(v)


def basis(d: int, i: int) -> np.ndarray:
    v = np.zeros(d, dtype=complex)
    v[i] = 1
    return v


def dm(psi: np.ndarray) -> np.ndarray:
    """|psi><psi| for a normalised ket."""
    psi = np.asarray(psi, dtype=complex).ravel()
    return np.outer(psi, psi.conj())


def is_state(rho: np.ndarray, tol: float = 1e-9) -> bool:
    """Hermitian, positive semidefinite, unit trace."""
    if not np.allclose(rho, rho.conj().T, atol=tol):
        return False
    return abs(np.trace(rho) - 1) < tol and np.linalg.eigvalsh(rho).min() > -tol


def purity(rho: np.ndarray) -> float:
    return float(np.real(np.trace(rho @ rho)))


def linear_entropy(rho: np.ndarray, normalised: bool = False) -> float:
    """S_L = 1 - tr rho^2 in [0, 1 - 1/d]; normalised: d/(d-1) (1 - tr rho^2) in [0, 1]."""
    s = 1.0 - purity(rho)
    d = rho.shape[0]
    return s * d / (d - 1) if normalised else s


def expval(rho: np.ndarray, A: np.ndarray) -> float:
    return float(np.real(np.trace(rho @ A)))


def kron(*ops) -> np.ndarray:
    return reduce(np.kron, ops)


def bloch_vector(rho: np.ndarray) -> np.ndarray:
    """r_i = tr(rho sigma_i) for a qubit."""
    return np.array([expval(rho, s) for s in PAULI])


def from_bloch(r) -> np.ndarray:
    r = np.asarray(r, dtype=float)
    return 0.5 * (I2 + sum(ri * s for ri, s in zip(r, PAULI)))


def gell_mann(d: int) -> list[np.ndarray]:
    """d^2 - 1 generalised Gell-Mann matrices: symmetric, antisymmetric, diagonal.

    Hermitian, traceless, tr(l_i l_j) = 2 delta_ij. For d = 2 they are X, Y, Z
    (in the order symmetric, antisymmetric, diagonal).
    """
    out = []
    for j in range(d):
        for k in range(j + 1, d):
            s = np.zeros((d, d), dtype=complex)
            s[j, k] = s[k, j] = 1
            a = np.zeros((d, d), dtype=complex)
            a[j, k], a[k, j] = -1j, 1j
            out += [s, a]
    for l in range(1, d):
        diag = np.zeros(d)
        diag[:l] = 1
        diag[l] = -l
        out.append(np.diag(diag * np.sqrt(2 / (l * (l + 1)))).astype(complex))
    return out


def generalised_bloch(rho: np.ndarray) -> np.ndarray:
    """b_i = tr(rho l_i), so that rho = I/d + (1/2) sum_i b_i l_i."""
    return np.array([expval(rho, l) for l in gell_mann(rho.shape[0])])


def from_generalised_bloch(b, d: int) -> np.ndarray:
    return np.eye(d) / d + 0.5 * sum(bi * l for bi, l in zip(b, gell_mann(d)))


def two_qubit_decomposition(rho: np.ndarray):
    """(a, b, T) with a_i = <s_i x I>, b_j = <I x s_j>, T_ij = <s_i x s_j>."""
    a = np.array([expval(rho, np.kron(s, I2)) for s in PAULI])
    b = np.array([expval(rho, np.kron(I2, s)) for s in PAULI])
    T = np.array([[expval(rho, np.kron(s, t)) for t in PAULI] for s in PAULI])
    return a, b, T


def from_two_qubit_decomposition(a, b, T) -> np.ndarray:
    rho = np.kron(I2, I2).astype(complex)
    for i in range(3):
        rho += a[i] * np.kron(PAULI[i], I2) + b[i] * np.kron(I2, PAULI[i])
        for j in range(3):
            rho += T[i, j] * np.kron(PAULI[i], PAULI[j])
    return rho / 4


def bipartite_bloch(rho: np.ndarray, da: int, db: int):
    """(a, b, T): a_i = <l_i x I>, b_j = <I x l_j>, T_ij = <l_i x l_j> (Gell-Mann bases)."""
    LA, LB = gell_mann(da), gell_mann(db)
    a = np.array([expval(rho, np.kron(l, np.eye(db))) for l in LA])
    b = np.array([expval(rho, np.kron(np.eye(da), l)) for l in LB])
    T = np.array([[expval(rho, np.kron(k, l)) for l in LB] for k in LA])
    return a, b, T


def from_bipartite_bloch(a, b, T, da: int, db: int) -> np.ndarray:
    """rho = (I + (da/2) a.l x I + (db/2) I x b.l + (da db/4) sum T_ij l_i x l_j) / (da db)."""
    LA, LB = gell_mann(da), gell_mann(db)
    rho = np.eye(da * db, dtype=complex)
    rho += da / 2 * sum(ai * np.kron(l, np.eye(db)) for ai, l in zip(a, LA))
    rho += db / 2 * sum(bj * np.kron(np.eye(da), l) for bj, l in zip(b, LB))
    rho += da * db / 4 * sum(T[i, j] * np.kron(LA[i], LB[j])
                             for i in range(len(LA)) for j in range(len(LB)))
    return rho / (da * db)


def partial_trace(rho: np.ndarray, dims, keep) -> np.ndarray:
    """Trace out every subsystem not in `keep`; the kept ones stay in their order.

    rho is reshaped into a 2n-index tensor (i_0..i_{n-1}, j_0..j_{n-1}) and the
    traced indices are contracted pairwise: (tr_B rho)_{ik} = sum_j rho_{ij,kj}.
    """
    dims = list(dims)
    n = len(dims)
    keep = sorted(keep)
    t = rho.reshape(dims + dims)
    letters = "abcdefghijklmnopqrstuvwxyz"
    row = [letters[i] for i in range(n)]
    col = [letters[n + i] if i in keep else letters[i] for i in range(n)]
    out = [row[i] for i in keep] + [col[i] for i in keep]
    t = np.einsum("".join(row) + "".join(col) + "->" + "".join(out), t)
    dk = int(np.prod([dims[i] for i in keep])) if keep else 1
    return t.reshape(dk, dk)


def random_pure(d: int, rng: np.random.Generator) -> np.ndarray:
    """Haar-random ket: normalised complex Gaussian vector."""
    v = rng.normal(size=d) + 1j * rng.normal(size=d)
    return v / np.linalg.norm(v)


def random_state(d: int, rng: np.random.Generator, rank: int | None = None) -> np.ndarray:
    """Random density matrix G G^dag / tr (Hilbert-Schmidt measure for rank = d)."""
    rank = d if rank is None else rank
    G = rng.normal(size=(d, rank)) + 1j * rng.normal(size=(d, rank))
    rho = G @ G.conj().T
    return rho / np.trace(rho)


def random_unitary(d: int, rng: np.random.Generator) -> np.ndarray:
    """Haar unitary via QR of a Ginibre matrix with the phase fix."""
    G = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    Q, R = np.linalg.qr(G)
    return Q * (np.diag(R) / np.abs(np.diag(R)))


BELL = {
    "phi+": ket(1, 0, 0, 1), "phi-": ket(1, 0, 0, -1),
    "psi+": ket(0, 1, 1, 0), "psi-": ket(0, 1, -1, 0),
}


def demo() -> None:
    rng = np.random.default_rng(1)
    plus = ket(1, 1)
    print("|+><+| Bloch vector", bloch_vector(dm(plus)).round(6), "purity", purity(dm(plus)))
    mixed = from_bloch([0.3, 0.0, 0.4])
    print("r=(0.3,0,0.4): purity", round(purity(mixed), 6), "= (1+|r|^2)/2 =", (1 + 0.25) / 2)
    rho = dm(BELL["psi-"])
    print("singlet: tr_B =", partial_trace(rho, [2, 2], [0]).real.round(6).tolist())
    a, b, T = two_qubit_decomposition(rho)
    print("singlet: a =", a.round(6), "b =", b.round(6), "T = diag", np.diag(T).round(6))
    r3 = random_state(3, rng)
    bvec = generalised_bloch(r3)
    print("qutrit: |b|^2 =", round(float(bvec @ bvec), 6), "= 2(tr rho^2 - 1/3) =",
          round(2 * (purity(r3) - 1 / 3), 6))
    print("normalised linear entropy of I/3:", linear_entropy(np.eye(3) / 3, normalised=True))


if __name__ == "__main__":
    demo()
