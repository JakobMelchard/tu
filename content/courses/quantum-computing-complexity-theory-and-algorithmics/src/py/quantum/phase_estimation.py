"""Quantum phase estimation (N&C 5.2, KLM 7.2).

Belongs to the Part C note on the QFT and phase estimation (C06).

U |u> = e^{2 pi i phi} |u>. t counting qubits 0..t-1 (qubit 0 = MSB of the
estimate), work qubits t..t+m-1 hold |u>. H on the counting register, then
controlled-U^{2^{t-1-j}} from counting qubit j (so qubit j carries phase
2 pi phi 2^{t-1-j}), inverse QFT, measure -> integer x, estimate phi ~ x / 2^t.
If phi = k/2^t the result is exact; otherwise the nearest x has probability
>= 4/pi^2 and |x/2^t - phi| <= 1/2^t with probability >= 8/pi^2.

Implements: phase_estimation_state, phase_estimation_distribution, phase_estimation.
"""
import numpy as np

from qft import qft
from sim import Register


def phase_estimation_state(U, eigenstate, t):
    """Register after inverse QFT, before measurement (counting qubits 0..t-1, work qubits after)."""
    U = np.asarray(U, dtype=complex)
    m = int(np.log2(U.shape[0]))
    reg = Register(t + m)
    reg.state = np.kron(Register(t).state, np.asarray(eigenstate, dtype=complex))
    counting = list(range(t))
    work = list(range(t, t + m))
    for q in counting:
        reg.h(q)
    for j in counting:                               # controlled U^{2^{t-1-j}} via small matrix powers
        Upow = np.linalg.matrix_power(U, 2 ** (t - 1 - j))
        reg.apply_controlled(Upow, [j], work)
    qft(reg, counting, inverse=True)
    return reg


def phase_estimation_distribution(U, eigenstate, t):
    """Exact probabilities P(x) of the 2^t outcomes of the counting register."""
    reg = phase_estimation_state(U, eigenstate, t)
    return np.real(np.diag(reg.partial_trace(list(range(t)))))


def phase_estimation(U, eigenstate, t, rng):
    """One run: returns (phase estimate x/2^t, integer x)."""
    reg = phase_estimation_state(U, eigenstate, t)
    bits = reg.measure(list(range(t)), rng)
    x = int("".join(map(str, bits)), 2)
    return x / 2 ** t, x


if __name__ == "__main__":
    from sim import phase
    rng = np.random.default_rng(0)
    t = 5
    for phi in (3 / 32, 0.3):
        U = phase(2 * np.pi * phi)
        est, x = phase_estimation(U, [0, 1], t, rng)
        P = phase_estimation_distribution(U, [0, 1], t)
        best = int(np.argmax(P))
        print(f"phi={phi:.5f}: sampled x={x} -> {est:.5f}; most likely x={best} (P={P[best]:.3f}), "
              f"P(|x/2^t - phi| <= 2^-t) = {P[np.abs(np.arange(32) / 32 - phi) <= 1 / 32 + 1e-12].sum():.3f}")
