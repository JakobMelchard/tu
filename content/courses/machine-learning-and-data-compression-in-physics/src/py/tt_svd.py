"""TT-SVD: tensor-train / matrix-product-state compression of a physics tensor.

Note 05 (tensor-network compression).
- TT-SVD (Oseledets [S26] Alg. 1): sweep left to right, reshape, truncated SVD,
  keep U as a left-orthogonal core, push S V^T to the right (`tt_svd`).
- Error: ||T - TT||_F^2 = sum_k eps_k^2 (the per-cut discarded weights; the
  pieces are mutually orthogonal because the cores are left-orthogonal), hence
  the bound sqrt(d-1) * delta of [S26 Thm 2.2] with per-cut tolerance delta.
- Physics tensors: transverse-field Ising ground state psi_{s1...sn} (area law,
  small bond dimension [S24, S25]), GHZ (rank 2), random state (volume law).
- Quantics [S16, S32]: f(x) on 2^R points as a (2,)*R tensor; exp -> rank 1,
  sin -> rank 2, degree-p polynomial -> rank <= p+1.

Run `python tt_svd.py`.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh


def tt_svd(T: np.ndarray, max_rank: int | None = None, rel_eps: float | None = None):
    """Return (cores, discarded) with cores[k].shape = (r_{k-1}, n_k, r_k).

    rel_eps: per-cut tolerance delta = rel_eps ||T||_F / sqrt(d-1), which guarantees
    ||T - TT||_F <= rel_eps ||T||_F. max_rank caps every bond dimension.
    discarded[k] = Frobenius norm of what cut k threw away.
    """
    dims = T.shape
    d = len(dims)
    delta = 0.0 if rel_eps is None else rel_eps * np.linalg.norm(T) / np.sqrt(max(d - 1, 1))
    cores, discarded = [], []
    C = T.reshape(1, -1)
    r_prev = 1
    for k in range(d - 1):
        C = C.reshape(r_prev * dims[k], -1)
        U, s, Vt = np.linalg.svd(C, full_matrices=False)
        tail = np.sqrt(np.append(np.cumsum((s ** 2)[::-1])[::-1], 0.0))   # tail[r] = ||s[r:]||
        r = int(np.argmax(tail <= delta)) if delta > 0 else int(np.sum(s > 0))
        r = max(1, min(r, max_rank or r, len(s)))
        discarded.append(float(tail[r]))
        cores.append(U[:, :r].reshape(r_prev, dims[k], r))
        C = s[:r, None] * Vt[:r]
        r_prev = r
    cores.append(C.reshape(r_prev, dims[-1], 1))
    return cores, np.array(discarded)


def tt_to_full(cores) -> np.ndarray:
    out = cores[0]
    for G in cores[1:]:
        out = np.tensordot(out, G, axes=([-1], [0]))
    return out.reshape([G.shape[1] for G in cores])


def tt_ranks(cores) -> list[int]:
    return [G.shape[2] for G in cores[:-1]]


def tt_num_params(cores) -> int:
    return int(sum(G.size for G in cores))


def schmidt_values(psi: np.ndarray, cut: int) -> np.ndarray:
    """Singular values of psi reshaped (prod dims[:cut], rest)."""
    return np.linalg.svd(psi.reshape(int(np.prod(psi.shape[:cut])), -1), compute_uv=False)


def entanglement_entropy(psi: np.ndarray, cut: int) -> float:
    lam2 = schmidt_values(psi, cut) ** 2
    lam2 = lam2[lam2 > 1e-300] / lam2.sum()
    return float(-np.sum(lam2 * np.log(lam2)))


def tfim_ground_state(n: int, g: float, J: float = 1.0) -> np.ndarray:
    """Ground state of H = -J sum Z_i Z_{i+1} - g sum X_i, open chain, as (2,)*n.

    Site 0 is the most significant bit / first tensor index.
    """
    X = sp.csr_matrix(np.array([[0.0, 1.0], [1.0, 0.0]]))
    Z = sp.csr_matrix(np.diag([1.0, -1.0]))
    I = sp.identity(2, format="csr")

    def op(o, i):
        mats = [I] * n
        mats[i] = o
        out = mats[0]
        for m in mats[1:]:
            out = sp.kron(out, m, format="csr")
        return out

    H = sp.csr_matrix((2 ** n, 2 ** n))
    for i in range(n - 1):
        H = H - J * op(Z, i) @ op(Z, i + 1)
    for i in range(n):
        H = H - g * op(X, i)
    _, v = eigsh(H, k=1, which="SA", v0=np.ones(2 ** n))
    psi = v[:, 0]
    return (psi * np.sign(psi[np.argmax(np.abs(psi))])).reshape((2,) * n)


def ghz(n: int) -> np.ndarray:
    psi = np.zeros(2 ** n)
    psi[0] = psi[-1] = 1 / np.sqrt(2)
    return psi.reshape((2,) * n)


def random_state(n: int, rng: np.random.Generator) -> np.ndarray:
    psi = rng.standard_normal(2 ** n)
    return (psi / np.linalg.norm(psi)).reshape((2,) * n)


def quantics(f, R: int) -> np.ndarray:
    """f(x_j), x_j = j / 2^R, j = sum_k b_k 2^{R-1-k}, as a (2,)*R tensor (b_0 first)."""
    x = np.arange(2 ** R) / 2 ** R
    return f(x).reshape((2,) * R)


def error_vs_bond_dimension(T: np.ndarray, chis) -> list[tuple[int, float, int]]:
    """(chi, relative error, parameters) for each max bond dimension chi."""
    nrm = np.linalg.norm(T)
    out = []
    for chi in chis:
        cores, _ = tt_svd(T, max_rank=chi)
        out.append((chi, float(np.linalg.norm(tt_to_full(cores) - T) / nrm), tt_num_params(cores)))
    return out


def demo() -> None:
    n = 12
    rng = np.random.default_rng(0)
    states = {"TFIM g=0.5": tfim_ground_state(n, 0.5), "TFIM g=1 (critical)": tfim_ground_state(n, 1.0),
              "random": random_state(n, rng)}
    chis = [1, 2, 4, 8, 16, 32, 64]
    print(f"n = {n} qubits, full tensor 2^{n} = {2 ** n} amplitudes")
    print(f"{'chi':>4} " + " ".join(f"{k:>20}" for k in states) + f" {'params(random)':>15}")
    rows = {k: error_vs_bond_dimension(v, chis) for k, v in states.items()}
    for i, chi in enumerate(chis):
        print(f"{chi:4d} " + " ".join(f"{rows[k][i][1]:20.2e}" for k in states)
              + f" {rows['random'][i][2]:15d}")
    print("half-chain entropy S:", ", ".join(f"{k} {entanglement_entropy(v, n // 2):.3f}"
                                             for k, v in states.items()))
    print(f"(Page value for a random state ~ {n / 2 * np.log(2) - 0.5:.3f})")
    R = 16
    for name, f in [("exp(-3x)", lambda x: np.exp(-3 * x)), ("sin(2 pi 5x)", lambda x: np.sin(10 * np.pi * x)),
                    ("x^3 - x", lambda x: x ** 3 - x), ("Gaussian bump", lambda x: np.exp(-((x - .4) / .01) ** 2))]:
        cores, _ = tt_svd(quantics(f, R), rel_eps=1e-10)
        print(f"quantics R={R} ({2 ** R} points) {name:>14}: ranks {tt_ranks(cores)}, "
              f"params {tt_num_params(cores)}")


if __name__ == "__main__":
    demo()
