"""Classical and quantum entropies used in QKD security proofs.

Note 03 (theoretical tools):
- Shannon, binary, von Neumann, conditional and mutual entropies (`shannon`, `h2`,
  `von_neumann`, `conditional_entropy`, `mutual_information`), Holevo chi (`holevo_chi`).
- Min-/max-entropy of distributions, classical conditional min-entropy
  H_min(X|Y) = -log2 sum_y max_x P(x,y) (`cond_min_entropy_classical`) [S4 Def. 3.1.2].
- Smooth min-entropy of a distribution under sub-normalised trace-distance smoothing:
  cut the largest probabilities down to a water level lambda with total cut mass eps
  (`smooth_min_entropy_classical`).
- Conditional min-entropy of a binary cq state via Helstrom (`min_entropy_cq_binary`),
  of a pure bipartite state via Schmidt coefficients (`min_entropy_pure`).
- Entanglement-based BB84: Bell-diagonal states, purification, H(Z|E) (`h_z_given_e`).
- Entropic uncertainty relation with quantum memory, H(X|B) + H(Z|C) >= 1 for a qubit A
  [S20] (`uncertainty_sum`).

All logs are base 2. Run `python entropies.py`.
"""
from __future__ import annotations

import math

import numpy as np

LOG2 = math.log(2.0)


def h2(p):
    """Binary entropy h(p) = -p log p - (1-p) log(1-p), with h(0) = h(1) = 0."""
    p = np.clip(np.asarray(p, dtype=float), 0.0, 1.0)
    out = np.zeros_like(p)
    m = (p > 0) & (p < 1)
    q = p[m]
    out[m] = -(q * np.log2(q) + (1 - q) * np.log2(1 - q))
    return float(out) if out.ndim == 0 else out


def shannon(p) -> float:
    p = np.asarray(p, dtype=float).ravel()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def von_neumann(rho: np.ndarray) -> float:
    """S(rho) = -tr rho log rho from the eigenvalues."""
    return shannon(np.clip(np.linalg.eigvalsh((rho + rho.conj().T) / 2), 0, None))


def partial_trace(rho: np.ndarray, dims: list[int], keep: list[int]) -> np.ndarray:
    """Reduced state on the subsystems listed in `keep` (in order)."""
    n = len(dims)
    t = rho.reshape(dims + dims)
    # trace out systems not kept, highest index first so axis numbers stay valid
    for s in sorted(set(range(n)) - set(keep), reverse=True):
        m = t.ndim // 2
        t = np.trace(t, axis1=s, axis2=s + m)
    d = int(np.prod([dims[k] for k in sorted(keep)]))
    return t.reshape(d, d)


def conditional_entropy(rho: np.ndarray, dims: list[int], a: list[int], b: list[int]) -> float:
    """H(A|B) = S(AB) - S(B)."""
    return von_neumann(partial_trace(rho, dims, sorted(a + b))) - von_neumann(partial_trace(rho, dims, b))


def mutual_information(rho: np.ndarray, dims: list[int], a: list[int], b: list[int]) -> float:
    """I(A:B) = S(A) + S(B) - S(AB)."""
    return (von_neumann(partial_trace(rho, dims, a)) + von_neumann(partial_trace(rho, dims, b))
            - von_neumann(partial_trace(rho, dims, sorted(a + b))))


def holevo_chi(probs, states) -> float:
    """chi = S(sum p_x rho_x) - sum p_x S(rho_x): the most Eve learns about X per copy."""
    avg = sum(p * r for p, r in zip(probs, states))
    return von_neumann(avg) - sum(p * von_neumann(r) for p, r in zip(probs, states))


# ---------------------------------------------------------------- one-shot entropies
def min_entropy_classical(p) -> float:
    return -math.log2(float(np.max(p)))


def max_entropy_classical(p) -> float:
    """Renyi-1/2 form H_max = 2 log2 sum sqrt(p) (Renner's H_max is log of support size)."""
    p = np.asarray(p, dtype=float)
    return 2.0 * math.log2(float(np.sqrt(p[p > 0]).sum()))


def cond_min_entropy_classical(pxy: np.ndarray) -> float:
    """H_min(X|Y) = -log2 p_guess(X|Y), p_guess = sum_y max_x P(x,y). Rows x, columns y."""
    return -math.log2(float(np.max(pxy, axis=0).sum()))


def smooth_min_entropy_classical(p, eps: float) -> float:
    """max over sub-normalised q <= p with sum(p - q) <= eps of -log2 max q.

    Optimal q flattens the top of p at a water level lam with sum (p - lam)_+ = eps.
    """
    p = np.sort(np.asarray(p, dtype=float))[::-1]
    if eps <= 0:
        return min_entropy_classical(p)
    csum = np.cumsum(p)
    for k in range(1, len(p) + 1):
        lam = (csum[k - 1] - eps) / k          # level if the top k entries are cut
        nxt = p[k] if k < len(p) else 0.0
        if lam >= nxt:
            return -math.log2(max(lam, 1e-300))
    raise ValueError("eps too large")


def helstrom_guess(p0: float, rho0: np.ndarray, p1: float, rho1: np.ndarray) -> float:
    """Optimal probability of guessing x from rho_x: (1 + ||p0 rho0 - p1 rho1||_1) / 2."""
    ev = np.linalg.eigvalsh(p0 * rho0 - p1 * rho1)
    return 0.5 * (1.0 + float(np.abs(ev).sum()))


def min_entropy_cq_binary(p0, rho0, p1, rho1) -> float:
    """H_min(X|E) = -log2 p_guess for a binary classical X [S4 Def. 3.1.2, operational form]."""
    return -math.log2(helstrom_guess(p0, rho0, p1, rho1))


def min_entropy_pure(psi: np.ndarray, da: int, db: int) -> float:
    """H_min(A|B) of a pure state = -2 log2 sum_i sqrt(lambda_i) (Schmidt coefficients)."""
    s = np.linalg.svd(psi.reshape(da, db), compute_uv=False)   # s_i = sqrt(lambda_i)
    return -2.0 * math.log2(float(s.sum()))


# ---------------------------------------------------------------- BB84 as an EB protocol
PHI_P = np.array([1, 0, 0, 1]) / math.sqrt(2)
PHI_M = np.array([1, 0, 0, -1]) / math.sqrt(2)
PSI_P = np.array([0, 1, 1, 0]) / math.sqrt(2)
PSI_M = np.array([0, 1, -1, 0]) / math.sqrt(2)
BELL = [PHI_P, PHI_M, PSI_P, PSI_M]


def bell_diagonal(lams) -> np.ndarray:
    """rho_AB = sum_i lam_i |B_i><B_i| in the order Phi+, Phi-, Psi+, Psi-."""
    return sum(l * np.outer(b, b) for l, b in zip(lams, BELL))


def bell_diagonal_qbers(lams) -> tuple[float, float]:
    """(e_Z, e_X): Z errors come from Psi+-, X errors from Phi- and Psi-."""
    l1, l2, l3, l4 = lams
    return l3 + l4, l2 + l4


def bb84_lams(e_z: float, e_x: float, l4: float | None = None):
    """Bell-diagonal weights with given QBERs; default l4 = e_z e_x (the worst case for Alice-Bob)."""
    if l4 is None:
        l4 = e_z * e_x
    return np.array([1 - e_z - e_x + l4, e_x - l4, e_z - l4, l4])


def purify(rho: np.ndarray) -> np.ndarray:
    """|psi>_{RE} = sum_i sqrt(p_i) |i>_R |i>_E with E a copy of the eigenbasis: Eve's best system."""
    p, v = np.linalg.eigh(rho)
    d = len(p)
    psi = np.zeros(d * d, dtype=complex)
    for i in range(d):
        if p[i] > 1e-14:
            psi += math.sqrt(p[i]) * np.kron(v[:, i], np.eye(d)[i])
    return psi


def h_z_given_e(lams) -> float:
    """H(Z_A|E) with E purifying the Bell-diagonal rho_AB, computed from the full 4-party state."""
    psi = purify(bell_diagonal(lams))                 # systems A, B, E (dims 2, 2, 4)
    rho = np.outer(psi, psi.conj())
    rho_ae = partial_trace(rho, [2, 2, 4], [0, 2])
    # measure A in Z: rho_ZE = sum_z |z><z| (x) <z|rho_AE|z>
    blocks = [rho_ae.reshape(2, 4, 2, 4)[z, :, z, :] for z in range(2)]
    s_ze = sum(shannon(np.clip(np.linalg.eigvalsh(b), 0, None)) for b in blocks)
    # rho_ZE is block-diagonal, so S(ZE) is the sum over the unnormalised blocks
    return s_ze - von_neumann(blocks[0] + blocks[1])


def uncertainty_sum(psi: np.ndarray, db: int, dc: int) -> float:
    """H(X_A|B) + H(Z_A|C) for pure |psi>_{ABC}, A a qubit; Berta et al. [S20]: >= 1 + H(A|B)."""
    rho = np.outer(psi, psi.conj())
    dims = [2, db, dc]
    hadamard = np.array([[1, 1], [1, -1]]) / math.sqrt(2)

    def h_meas(u: np.ndarray, side: int) -> float:
        big = np.kron(np.kron(u.conj().T, np.eye(db)), np.eye(dc))
        r = big @ rho @ big.conj().T
        r2 = partial_trace(r, dims, [0, side])
        d = dims[side]
        blocks = [r2.reshape(2, d, 2, d)[k, :, k, :] for k in range(2)]
        s_joint = sum(shannon(np.clip(np.linalg.eigvalsh(b), 0, None)) for b in blocks)
        return s_joint - von_neumann(blocks[0] + blocks[1])

    return h_meas(hadamard, 1) + h_meas(np.eye(2), 2)


def random_pure(d: int, rng: np.random.Generator) -> np.ndarray:
    v = rng.normal(size=d) + 1j * rng.normal(size=d)
    return v / np.linalg.norm(v)


def demo() -> None:
    print("h(0.11) =", round(h2(0.11), 4), " 1-2h(0.11) =", round(1 - 2 * h2(0.11), 4))
    e = 0.05
    for l4 in (0.0, e * e, e / 2):
        lams = bb84_lams(e, e, l4)
        hze = h_z_given_e(lams)
        print(f"e=5%, lambda_Psi-={l4:.4f}: H(Z|E)={hze:.4f}  rate H(Z|E)-h(e)={hze - h2(e):.4f}")
    print("worst case is lambda_Psi- = e^2, rate 1-2h(e) =", round(1 - 2 * h2(e), 4))
    p = np.full(8, 1 / 8)
    print("uniform 3 bits: H_min =", min_entropy_classical(p), " H =", shannon(p))
    q = np.array([0.5] + [0.5 / 7] * 7)
    for eps in (0.0, 0.1, 0.3):
        print(f"skewed: H_min^eps({eps}) = {smooth_min_entropy_classical(q, eps):.4f}")
    phi = PHI_P
    print("H_min(A|B) of Phi+ =", min_entropy_pure(phi, 2, 2), "(= -log2 d)")
    rng = np.random.default_rng(0)
    sums = [uncertainty_sum(random_pure(2 * 2 * 2, rng), 2, 2) for _ in range(200)]
    print("min over 200 random ABC states of H(X|B)+H(Z|C):", round(min(sums), 4), ">= 1")


if __name__ == "__main__":
    demo()
