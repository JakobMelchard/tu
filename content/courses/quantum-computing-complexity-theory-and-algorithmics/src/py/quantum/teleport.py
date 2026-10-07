"""Quantum teleportation and superdense coding (N&C 1.3.7, 2.3; KLM 5.2).

Belongs to the Part C note on entanglement protocols (C03).

Teleportation: qubit 0 carries the unknown |psi>, qubits 1,2 share a Bell pair.
Alice measures 0,1 in the Bell basis (CNOT, H, then Z-measure), sends two
classical bits, Bob applies X^b1 Z^b0 to qubit 2. Superdense coding: Alice
encodes two bits into her half of a Bell pair with X^b1 Z^b0, Bob decodes by
CNOT, H and a measurement.

Implements: random_qubit_state, bell_pair, teleport, superdense_coding.
"""
import numpy as np

from sim import Register, fidelity


def random_qubit_state(rng):
    v = rng.normal(size=2) + 1j * rng.normal(size=2)
    return v / np.linalg.norm(v)


def bell_pair(reg, a, b):
    """(|00> + |11>)/sqrt2 on qubits a, b."""
    return reg.h(a).cx(a, b)


def teleport(psi, rng):
    """Teleport the 1-qubit state psi from qubit 0 to qubit 2. Returns (fidelity, (b0, b1))."""
    reg = Register(3, np.kron(psi, [1, 0, 0, 0]))
    bell_pair(reg, 1, 2)
    reg.cx(0, 1).h(0)                     # Bell measurement of qubits 0,1 in the computational basis
    b0, b1 = reg.measure([0, 1], rng)
    if b1:                                # classical corrections on Bob's qubit
        reg.x(2)
    if b0:
        reg.z(2)
    rho_bob = reg.partial_trace([2])
    return fidelity(psi, rho_bob), (b0, b1)


def superdense_coding(b0, b1, rng):
    """Send two classical bits with one qubit. Returns the decoded (b0, b1)."""
    reg = bell_pair(Register(2), 0, 1)    # shared beforehand, qubit 0 = Alice, 1 = Bob
    if b1:
        reg.x(0)
    if b0:
        reg.z(0)
    reg.cx(0, 1).h(0)                     # Bob has both qubits now: decode the Bell state
    d0, d1 = reg.measure([0, 1], rng)
    return d0, d1


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    psi = random_qubit_state(rng)
    F, bits = teleport(psi, rng)
    print(f"teleport psi={np.round(psi, 3)}: Alice sent bits {bits}, Bob's fidelity = {F:.12f}")
    for b in ((0, 0), (0, 1), (1, 0), (1, 1)):
        print(f"superdense coding {b} -> decoded {superdense_coding(*b, rng)}")
