"""Entanglement: PPT criterion, negativity, witnesses, entropy of entanglement.

Note 10. Implements
- partial transpose on B, PPT test [S33]; for 2x2 and 2x3 PPT <=> separable [S34],
  cross-checked here against Wootters' concurrence (C > 0 <=> entangled) [S37],
- negativity N = (||rho^{T_B}||_1 - 1)/2 and log-negativity [S36],
- entropy of entanglement E(psi) = S(tr_B psi) for pure states,
- Werner state p|psi-><psi-| + (1-p) I/4: witness W = I/2 - |psi-><psi-|, with
  tr(W rho_p) = (1 - 3p)/4 < 0 iff p > 1/3, the same threshold as PPT,
- W >= 0 on product states: max_{a,b} <ab|psi-><psi-|ab> = 1/2 (largest Schmidt coeff^2),
- P. Horodecki's 3x3 PPT entangled state [S60], detected by realignment [S61].
Run `python entanglement.py`.
"""
from __future__ import annotations

import numpy as np

from entropies import mutual_information, von_neumann
from states import BELL, Y, dm, partial_trace, random_pure, random_state


def partial_transpose(rho: np.ndarray, da: int, db: int) -> np.ndarray:
    """(rho^{T_B})_{(i j),(k l)} = rho_{(i l),(k j)}."""
    return rho.reshape(da, db, da, db).transpose(0, 3, 2, 1).reshape(da * db, da * db)


def is_ppt(rho: np.ndarray, da: int, db: int, tol: float = 1e-10) -> bool:
    return bool(np.linalg.eigvalsh(partial_transpose(rho, da, db)).min() > -tol)


def negativity(rho: np.ndarray, da: int, db: int) -> float:
    w = np.linalg.eigvalsh(partial_transpose(rho, da, db))
    return float(max(0.0, -w[w < 0].sum()))


def log_negativity(rho: np.ndarray, da: int, db: int) -> float:
    return float(np.log2(2 * negativity(rho, da, db) + 1))


def entropy_of_entanglement(psi: np.ndarray, da: int, db: int) -> float:
    return von_neumann(partial_trace(dm(psi), [da, db], [0]))


def concurrence(rho: np.ndarray) -> float:
    """Wootters: C = max(0, l1 - l2 - l3 - l4), l_i = sqrt eig(rho (Y x Y) rho* (Y x Y)) decreasing."""
    YY = np.kron(Y, Y)
    R = rho @ YY @ rho.conj() @ YY
    l = np.sqrt(np.clip(np.sort(np.linalg.eigvals(R).real)[::-1], 0, None))
    return float(max(0.0, l[0] - l[1] - l[2] - l[3]))


def werner(p: float) -> np.ndarray:
    return p * dm(BELL["psi-"]) + (1 - p) * np.eye(4) / 4


WERNER_WITNESS = np.eye(4) / 2 - dm(BELL["psi-"])


def witness_value(W: np.ndarray, rho: np.ndarray) -> float:
    return float(np.real(np.trace(W @ rho)))


def random_separable(da: int, db: int, rng: np.random.Generator, terms: int = 5) -> np.ndarray:
    """Convex mixture of random product pure states."""
    w = rng.dirichlet(np.ones(terms))
    return sum(wi * np.kron(dm(random_pure(da, rng)), dm(random_pure(db, rng))) for wi in w)


def realignment(rho: np.ndarray, da: int, db: int) -> np.ndarray:
    """R(rho)_{(i k),(j l)} = rho_{(i j),(k l)}; ||R||_1 > 1 implies entangled."""
    return rho.reshape(da, db, da, db).transpose(0, 2, 1, 3).reshape(da * da, db * db)


def horodecki_3x3(a: float) -> np.ndarray:
    """P. Horodecki (1997) PPT entangled state of two qutrits, 0 < a < 1."""
    b, c = (1 + a) / 2, np.sqrt(1 - a * a) / 2
    M = a * np.eye(9)
    for i in (0, 4, 8):
        for j in (0, 4, 8):
            M[i, j] = a
    M[6, 6] = M[8, 8] = b
    M[6, 8] = M[8, 6] = c
    return M / (8 * a + 1)


def demo() -> None:
    rng = np.random.default_rng(8)
    for p in (0.2, 1 / 3, 0.34, 0.6, 1.0):
        r = werner(p)
        print(f"Werner p={p:.3f}: PPT={is_ppt(r, 2, 2)!s:5}  N={negativity(r, 2, 2):.4f}"
              f"  C={concurrence(r):.4f}  tr(W rho)={witness_value(WERNER_WITNESS, r):+.4f}"
              f"  I(A:B)={mutual_information(r, [2, 2]):.4f}")
    worst = min(witness_value(WERNER_WITNESS, np.kron(dm(random_pure(2, rng)), dm(random_pure(2, rng))))
                for _ in range(2000))
    print("min tr(W sigma) over 2000 random product states:", round(worst, 6), "(>= 0)")
    agree = sum(is_ppt(r, 2, 2) == (concurrence(r) < 1e-10)
                for r in (random_state(4, rng, rank=int(rng.integers(1, 5))) for _ in range(500)))
    print("2x2: PPT agrees with C = 0 on", agree, "of 500 random states")
    print("2x3 random separable mixtures all PPT:",
          all(is_ppt(random_separable(2, 3, rng), 2, 3) for _ in range(200)))
    psi = random_pure(4, rng)
    print("pure 2x2: E =", round(entropy_of_entanglement(psi, 2, 2), 6), " Bell: E =",
          round(entropy_of_entanglement(BELL["phi+"], 2, 2), 6))
    h = horodecki_3x3(0.5)
    print("Horodecki 3x3 (a=0.5): PPT =", is_ppt(h, 3, 3), " ||R||_1 =",
          round(float(np.linalg.svd(realignment(h, 3, 3), compute_uv=False).sum()), 6), "> 1")


if __name__ == "__main__":
    demo()
