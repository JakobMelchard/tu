"""Quantum channels, Choi matrices, Stinespring dilations, POVMs and Neumark dilation.

Notes 11 (channels) and 12 (generalised measurements). Implements
- Kraus operators of the depolarising, dephasing and amplitude-damping channels,
- apply_kraus, Choi matrix J = sum_ij |i><j| x Phi(|i><j|) (input x output),
  CP <=> J >= 0, TP <=> tr_out J = I (Choi's theorem [S45]); Kraus from Choi,
- the transpose map: positive, not completely positive (J = SWAP, eigenvalue -1),
- Stinespring isometry V = sum_k K_k x |k>_E, Phi(rho) = tr_E V rho V^dag [S44],
  and the complementary channel tr_B V rho V^dag,
- POVMs: validity, Born probabilities, the trine POVM; Neumark dilation both as
  an ancilla isometry (V|psi> = sum_k sqrt(E_k)|psi>|k>) and, for rank-1 POVMs,
  as a projective measurement in a direct-sum space (rows completed to a unitary).
Run `python channels.py`.
"""
from __future__ import annotations

import numpy as np

from states import I2, X, Y, Z, bloch_vector, dm, from_bloch, partial_trace, random_state


def depolarising(p: float):
    """rho -> (1 - p) rho + p I/2, Bloch vector shrinks by (1 - p)."""
    return [np.sqrt(1 - 3 * p / 4) * I2, np.sqrt(p / 4) * X, np.sqrt(p / 4) * Y, np.sqrt(p / 4) * Z]


def dephasing(p: float):
    """rho -> (1 - p) rho + p Z rho Z: x, y shrink by (1 - 2p), z fixed."""
    return [np.sqrt(1 - p) * I2, np.sqrt(p) * Z]


def amplitude_damping(g: float):
    """|1> -> |0> with probability g: (x, y, z) -> (sqrt(1-g) x, sqrt(1-g) y, g + (1-g) z)."""
    return [np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=complex),
            np.array([[0, np.sqrt(g)], [0, 0]], dtype=complex)]


def apply_kraus(kraus, rho: np.ndarray) -> np.ndarray:
    return sum(K @ rho @ K.conj().T for K in kraus)


def is_trace_preserving(kraus, tol: float = 1e-10) -> bool:
    d = kraus[0].shape[1]
    return np.allclose(sum(K.conj().T @ K for K in kraus), np.eye(d), atol=tol)


def choi(channel, d_in: int) -> np.ndarray:
    """J = sum_ij |i><j| x Phi(|i><j|) for a linear map given as a function."""
    blocks = []
    for i in range(d_in):
        for j in range(d_in):
            E = np.zeros((d_in, d_in), dtype=complex)
            E[i, j] = 1
            blocks.append(np.kron(E, channel(E)))
    return sum(blocks)


def is_cptp_choi(J: np.ndarray, d_in: int, d_out: int, tol: float = 1e-10) -> tuple[bool, bool]:
    cp = np.linalg.eigvalsh(J).min() > -tol
    tp = np.allclose(partial_trace(J, [d_in, d_out], [0]), np.eye(d_in), atol=tol)
    return bool(cp), bool(tp)


def kraus_from_choi(J: np.ndarray, d_in: int, d_out: int, tol: float = 1e-12):
    """Eigenvectors sqrt(l) |v> of J, reshaped (d_in x d_out) and transposed, are Kraus operators."""
    w, V = np.linalg.eigh(J)
    return [np.sqrt(l) * V[:, k].reshape(d_in, d_out).T for k, l in enumerate(w) if l > tol]


def transpose_map(rho: np.ndarray) -> np.ndarray:
    return rho.T


def stinespring(kraus) -> np.ndarray:
    """Isometry V: C^d_in -> C^d_out x C^r, V = sum_k K_k x |k>."""
    r = len(kraus)
    return sum(np.kron(K, np.eye(r)[:, [k]]) for k, K in enumerate(kraus))


def stinespring_apply(V: np.ndarray, rho: np.ndarray, d_out: int, r: int, keep: int = 0) -> np.ndarray:
    """keep=0: channel output (trace out E); keep=1: complementary channel (trace out B)."""
    return partial_trace(V @ rho @ V.conj().T, [d_out, r], [keep])


def is_povm(effects, tol: float = 1e-10) -> bool:
    d = effects[0].shape[0]
    pos = all(np.linalg.eigvalsh(E).min() > -tol for E in effects)
    return pos and np.allclose(sum(effects), np.eye(d), atol=tol)


def born(effects, rho: np.ndarray) -> np.ndarray:
    return np.array([np.real(np.trace(E @ rho)) for E in effects])


def trine():
    """E_k = (2/3)|psi_k><psi_k|, psi_k at Bloch angles 0, 120, 240 deg in the xz-plane."""
    kets = [np.array([np.cos(t / 2), np.sin(t / 2)], dtype=complex)
            for t in (0, 2 * np.pi / 3, 4 * np.pi / 3)]
    return [2 / 3 * dm(k) for k in kets], kets


def psd_sqrt(A: np.ndarray) -> np.ndarray:
    w, V = np.linalg.eigh(A)
    return (V * np.sqrt(np.clip(w, 0, None))) @ V.conj().T


def neumark_isometry(effects) -> np.ndarray:
    """V = sum_k sqrt(E_k) x |k>: V^dag V = sum E_k = I; measuring |k><k| on the ancilla gives tr E_k rho."""
    n = len(effects)
    return sum(np.kron(psd_sqrt(E), np.eye(n)[:, [k]]) for k, E in enumerate(effects))


def neumark_direct_sum(vectors) -> np.ndarray:
    """Neumark in the direct-sum form for a rank-1 POVM E_k = |v_k><v_k| on C^d, n outcomes.

    M = [v_1 ... v_n] (d x n) has orthonormal rows since M M^dag = sum_k E_k = I.
    Append n - d rows orthonormal to them to get a unitary U (n x n). Its columns
    u_k form an orthonormal basis of C^n = C^d + C^(n-d) whose first d entries are
    v_k, so for the embedded state |psi, 0>:  |<u_k|psi, 0>|^2 = |<v_k|psi>|^2 = tr E_k psi.
    """
    M = np.column_stack(vectors)
    d, n = M.shape
    Q, _ = np.linalg.qr(np.vstack([M, np.random.default_rng(0).normal(size=(n - d, n))]).conj().T)
    comp = Q[:, d:].conj().T  # rows orthogonal to the rows of M
    return np.vstack([M, comp])


def demo() -> None:
    rng = np.random.default_rng(9)
    r = np.array([0.3, -0.2, 0.5])
    rho = from_bloch(r)
    for name, K in (("depolarising p=0.3", depolarising(0.3)), ("dephasing p=0.2", dephasing(0.2)),
                    ("amplitude damping g=0.4", amplitude_damping(0.4))):
        J = choi(lambda A: apply_kraus(K, A), 2)
        print(f"{name:24s} TP={is_trace_preserving(K)} (CP,TP)_Choi={is_cptp_choi(J, 2, 2)}"
              f" r -> {bloch_vector(apply_kraus(K, rho)).round(4)}")
    Jt = choi(transpose_map, 2)
    print("transpose map: Choi eigenvalues", np.linalg.eigvalsh(Jt).round(6), "-> positive but not CP")
    K = amplitude_damping(0.4)
    K2 = kraus_from_choi(choi(lambda A: apply_kraus(K, A), 2), 2, 2)
    s = random_state(2, rng)
    print("Kraus from Choi reproduces the channel:", np.allclose(apply_kraus(K2, s), apply_kraus(K, s)))
    V = stinespring(K)
    print("Stinespring V^dag V = I:", np.allclose(V.conj().T @ V, np.eye(2)),
          " tr_E V s V^dag = Phi(s):", np.allclose(stinespring_apply(V, s, 2, 2), apply_kraus(K, s)))
    E, kets = trine()
    print("trine is a POVM:", is_povm(E), " p(k|psi_0) =", born(E, dm(kets[0])).round(6))
    Vn = neumark_isometry(E)
    anc = [partial_trace(Vn @ s @ Vn.conj().T, [2, 3], [1])[k, k].real for k in range(3)]
    print("Neumark (ancilla): isometry", np.allclose(Vn.conj().T @ Vn, np.eye(2)),
          " probabilities match:", np.allclose(anc, born(E, s)))
    U = neumark_direct_sum([np.sqrt(2 / 3) * k for k in kets])
    psi = kets[1]
    emb = np.concatenate([psi, [0]])
    probs = np.abs(U.conj().T @ emb) ** 2  # outcome k: projector onto column u_k of U
    print("Neumark (direct sum): U unitary", np.allclose(U @ U.conj().T, np.eye(3)),
          " probabilities", probs.round(6), "vs POVM", born(E, dm(psi)).round(6))


if __name__ == "__main__":
    demo()
