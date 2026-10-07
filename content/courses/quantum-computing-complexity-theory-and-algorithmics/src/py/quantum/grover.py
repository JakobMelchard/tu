"""Grover search and amplitude amplification (N&C 6.1-6.2, KLM 8.1-8.3).

Belongs to the Part C note on Grover / amplitude amplification (C05).

Marked set M of size m among N = 2^n items. One Grover iteration G = D O with
O = phase oracle (-1)^[x in M] and D = 2|s><s| - I = H^n (2|0><0| - I) H^n the
"inversion about the mean". In the 2-d span of |good>, |bad> each G rotates by
2 theta, sin theta = sqrt(m/N), so after k iterations
P(success) = sin^2((2k+1) theta) and k_opt = round(pi/(4 theta) - 1/2) ~ pi/4 sqrt(N/m).

Implements: apply_oracle, apply_diffusion, optimal_iterations, success_probability,
grover, amplitude_amplification.
"""
import numpy as np

from sim import Register


def apply_oracle(reg, marked, qubits):
    """Phase oracle: flip the sign of every basis state whose bits on `qubits` are in `marked`."""
    d = np.ones(2 ** len(qubits))
    d[list(marked)] = -1
    return reg.apply_diagonal(d, qubits)


def apply_diffusion(reg, qubits):
    """D = H^n (2|0><0| - I) H^n, up to global sign (we apply -(2|0><0|-I) = I - 2|0><0|)."""
    for q in qubits:
        reg.h(q)
    d = np.ones(2 ** len(qubits))
    d[0] = -1
    reg.apply_diagonal(d, qubits)
    for q in qubits:
        reg.h(q)
    return reg


def optimal_iterations(n, m):
    theta = np.arcsin(np.sqrt(m / 2 ** n))
    return max(0, int(round(np.pi / (4 * theta) - 0.5)))


def success_probability(n, marked, k):
    """Analytic P(measure a marked item after k iterations) = sin^2((2k+1) theta)."""
    theta = np.arcsin(np.sqrt(len(marked) / 2 ** n))
    return float(np.sin((2 * k + 1) * theta) ** 2)


def grover(n, marked, iterations=None, rng=None):
    """Run Grover on n qubits. Returns (P(marked) from the state, measured index or None, register)."""
    marked = sorted(set(marked))
    k = optimal_iterations(n, len(marked)) if iterations is None else iterations
    qubits = list(range(n))
    reg = Register(n)
    for q in qubits:
        reg.h(q)
    for _ in range(k):
        apply_oracle(reg, marked, qubits)
        apply_diffusion(reg, qubits)
    p_marked = float(reg.probabilities()[marked].sum())
    outcome = None
    if rng is not None:
        bits = reg.copy().measure_all(rng)
        outcome = int("".join(map(str, bits)), 2)
    return p_marked, outcome, reg


def amplitude_amplification(n, prepare, unprepare, apply_good_oracle, iterations):
    """General Q = -A S_0 A^-1 S_f applied `iterations` times to A|0>.

    prepare(reg) applies A, unprepare(reg) applies A^-1, apply_good_oracle(reg) flips
    the sign of the good states. With A = H^n this is exactly Grover.
    """
    qubits = list(range(n))
    reg = Register(n)
    prepare(reg)
    d = np.ones(2 ** n)
    d[0] = -1
    for _ in range(iterations):
        apply_good_oracle(reg)
        unprepare(reg)
        reg.apply_diagonal(d, qubits)   # I - 2|0><0|  (= -S_0)
        prepare(reg)
    return reg


if __name__ == "__main__":
    n, marked = 6, [5, 42]
    N, m = 2 ** n, len(marked)
    k = optimal_iterations(n, m)
    print(f"n={n}, N={N}, marked={marked}, optimal iterations k={k} (pi/4 sqrt(N/m) = {np.pi / 4 * np.sqrt(N / m):.2f})")
    rng = np.random.default_rng(0)
    for it in range(k + 3):
        p, out, _ = grover(n, marked, it, rng)
        print(f"  k={it}: P(marked) simulated={p:.6f} analytic={success_probability(n, marked, it):.6f} sample={out}")
