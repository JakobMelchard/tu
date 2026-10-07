"""QAOA for MaxCut (Farhi, Goldstone, Gutmann 2014) and a barren-plateau demo (McClean et al. 2018).

Belongs to the Part C note on variational algorithms (C08).

MaxCut cost C(x) = sum_{(i,j) in E} [x_i != x_j].  QAOA_p state
  |gamma, beta> = prod_{l=1..p} e^{-i beta_l B} e^{-i gamma_l C} H^n |0>,   B = sum_i X_i.
e^{-i gamma C} factorises over edges into 2-qubit diagonals diag(1, e^{-i gamma}, e^{-i gamma}, 1)
(a ZZ phase up to a global phase); e^{-i beta B} = prod Rx(2 beta). Expectation of the
cut is read off the probabilities; angles are optimised classically.

Implements: ring_graph, random_graph, cut_values, maxcut_bruteforce, apply_cost_unitary,
apply_mixer, qaoa_state, expected_cut, qaoa, most_likely_cut, barren_plateau_variances.
"""
import numpy as np
from scipy.optimize import minimize

from sim import Register, Rx, Ry, Rz


def ring_graph(n):
    return [(i, (i + 1) % n) for i in range(n)]


def random_graph(n, p, rng):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]


def cut_values(n, edges):
    """Array over all 2^n bit strings x (big-endian) of the number of cut edges."""
    x = np.arange(2 ** n)
    bit = lambda q: (x >> (n - 1 - q)) & 1
    return sum(bit(i) ^ bit(j) for i, j in edges) if edges else np.zeros(2 ** n, dtype=int)


def maxcut_bruteforce(n, edges):
    c = cut_values(n, edges)
    return int(c.max()), [int(i) for i in np.flatnonzero(c == c.max())]


def apply_cost_unitary(reg, gamma, edges):
    d = np.array([1, np.exp(-1j * gamma), np.exp(-1j * gamma), 1])
    for i, j in edges:
        reg.apply_diagonal(d, [i, j])
    return reg


def apply_mixer(reg, beta, n):
    for q in range(n):
        reg.rx(2 * beta, q)
    return reg


def qaoa_state(gammas, betas, n, edges):
    reg = Register(n)
    for q in range(n):
        reg.h(q)
    for g, b in zip(gammas, betas):
        apply_cost_unitary(reg, g, edges)
        apply_mixer(reg, b, n)
    return reg


def expected_cut(reg, n, edges):
    return float(reg.probabilities() @ cut_values(n, edges))


def qaoa(n, edges, p, rng, restarts=5, method="COBYLA"):
    """Maximise <C> over 2p angles from random starts. Returns (best <C>, gammas, betas)."""
    def neg_cut(x):
        return -expected_cut(qaoa_state(x[:p], x[p:], n, edges), n, edges)

    best = None
    for _ in range(restarts):
        x0 = np.concatenate([rng.uniform(0, 2 * np.pi, p), rng.uniform(0, np.pi, p)])
        res = minimize(neg_cut, x0, method=method, options={"maxiter": 1000})
        if best is None or res.fun < best[0]:
            best = (res.fun, res.x)
    return -best[0], best[1][:p], best[1][p:]


def most_likely_cut(reg):
    return int(np.argmax(reg.probabilities()))


def barren_plateau_variances(ns, samples, rng, layers=32):
    """Var over random circuits of d<Z0 Z1>/d theta_0 (parameter shift) for a random-rotation + CZ ansatz.

    Fixed depth (32 layers by default, deep enough to approach a 2-design for n <= 8); each
    rotation has a random Pauli axis and a uniform angle. Returns {n: variance}.
    McClean et al.: for deep enough circuits the variance shrinks exponentially with n.
    """
    rots = (Rx, Ry, Rz)
    out = {}
    for n in ns:
        L = layers
        grads = []
        for _ in range(samples):
            axes = rng.integers(0, 3, (L, n))
            angles = rng.uniform(0, 2 * np.pi, (L, n))

            def expval(shift):
                reg = Register(n)
                for q in range(n):
                    reg.ry(np.pi / 2, q)                 # start from |+>^n like a hardware-efficient ansatz
                for l in range(L):
                    for q in range(n):
                        th = angles[l, q] + (shift if (l, q) == (0, 0) else 0)
                        reg.apply_gate(rots[axes[l, q]](th), [q])
                    for q in range(n - 1):
                        reg.cz(q, q + 1)
                return reg.expectation("ZZ" + "I" * (n - 2))

            grads.append((expval(np.pi / 2) - expval(-np.pi / 2)) / 2)
        out[n] = float(np.var(grads))
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n = 5
    edges = ring_graph(n)
    cmax, argmax = maxcut_bruteforce(n, edges)
    print(f"5-ring: max cut {cmax}, achieved by {[f'{x:0{n}b}' for x in argmax]}")
    for p in (1, 2):
        val, g, b = qaoa(n, edges, p, rng)
        reg = qaoa_state(g, b, n, edges)
        ml = most_likely_cut(reg)
        print(f"  p={p}: <C>={val:.4f} ({val / cmax:.3f} of max), most likely string {ml:0{n}b} "
              f"(cut {cut_values(n, edges)[ml]}, P={reg.probabilities()[ml]:.3f})")
    n6, e6 = 6, random_graph(6, 0.6, rng)
    val, g, b = qaoa(n6, e6, 2, rng)
    print(f"random 6-vertex graph {e6}: max cut {maxcut_bruteforce(n6, e6)[0]}, QAOA p=2 <C>={val:.4f}")
    print("barren plateau: Var[dE/dtheta_0] vs n:",
          {k: f"{v:.2e}" for k, v in barren_plateau_variances(range(2, 9), 40, rng).items()})
