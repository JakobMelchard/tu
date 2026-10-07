"""Variational quantum eigensolver on a 2-qubit H2 Hamiltonian (Peruzzo et al. 2014; N&C 4.7 for Pauli expectations).

Belongs to the Part C note on variational algorithms (C08).

Hamiltonian as a list of (coefficient, Pauli string). H2 at 0.735 A in the STO-3G
basis reduced to two qubits (O'Malley et al. 2016):
  H = -1.0523 II + 0.3979 ZI - 0.3979 IZ - 0.0113 ZZ + 0.1809 XX,  E0 ~ -1.857 Ha.
Hardware-efficient ansatz: layers of Ry on every qubit followed by a CNOT ladder,
closed by a final Ry layer; params has n*(layers+1) angles.
Parameter-shift rule for gates exp(-i theta P/2):  dE/dtheta = [E(theta+pi/2) - E(theta-pi/2)]/2.

Implements: H2_TERMS, pauli_matrix, hamiltonian_matrix, exact_ground_energy, ansatz,
energy, parameter_shift_gradient, finite_difference_gradient, vqe.
"""
import numpy as np
from scipy.optimize import minimize

from sim import I, Register, X, Y, Z, kron

H2_TERMS = [(-1.0523, "II"), (0.3979, "ZI"), (-0.3979, "IZ"), (-0.0113, "ZZ"), (0.1809, "XX")]
_P = {"I": I, "X": X, "Y": Y, "Z": Z}


def pauli_matrix(s):
    return kron(*[_P[c] for c in s])


def hamiltonian_matrix(terms):
    return sum(c * pauli_matrix(s) for c, s in terms)


def exact_ground_energy(terms):
    return float(np.linalg.eigvalsh(hamiltonian_matrix(terms))[0])


def ansatz(params, n, layers):
    """Ry layer, CNOT ladder, repeated `layers` times, then a final Ry layer."""
    params = np.asarray(params)
    assert params.size == n * (layers + 1)
    reg = Register(n)
    for layer in range(layers + 1):
        for q in range(n):
            reg.ry(params[layer * n + q], q)
        if layer < layers:
            for q in range(n - 1):
                reg.cx(q, q + 1)
    return reg


def energy(params, terms, n, layers):
    """<psi(params)| H |psi(params)> summed term by term from the statevector."""
    reg = ansatz(params, n, layers)
    return sum(c * reg.expectation(s) for c, s in terms)


def parameter_shift_gradient(params, terms, n, layers):
    params = np.asarray(params, dtype=float)
    grad = np.zeros_like(params)
    for i in range(params.size):
        e = np.zeros_like(params)
        e[i] = np.pi / 2
        grad[i] = (energy(params + e, terms, n, layers) - energy(params - e, terms, n, layers)) / 2
    return grad


def finite_difference_gradient(params, terms, n, layers, eps=1e-6):
    params = np.asarray(params, dtype=float)
    grad = np.zeros_like(params)
    for i in range(params.size):
        e = np.zeros_like(params)
        e[i] = eps
        grad[i] = (energy(params + e, terms, n, layers) - energy(params - e, terms, n, layers)) / (2 * eps)
    return grad


def vqe(terms, n, layers, rng, method="BFGS", restarts=3):
    """Minimise the energy from `restarts` random starts. Returns (energy, params, history of restarts)."""
    best = None
    history = []
    for _ in range(restarts):
        x0 = rng.uniform(0, 2 * np.pi, n * (layers + 1))
        if method == "BFGS":
            res = minimize(energy, x0, args=(terms, n, layers), method="BFGS",
                           jac=lambda p, *a: parameter_shift_gradient(p, *a), options={"gtol": 1e-8})
        else:
            res = minimize(energy, x0, args=(terms, n, layers), method="COBYLA", options={"maxiter": 2000, "tol": 1e-8})
        history.append(float(res.fun))
        if best is None or res.fun < best[0]:
            best = (float(res.fun), res.x)
    return best[0], best[1], history


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    E0 = exact_ground_energy(H2_TERMS)
    print(f"exact spectrum: {np.round(np.linalg.eigvalsh(hamiltonian_matrix(H2_TERMS)), 5)}  ground {E0:.5f}")
    for method in ("BFGS", "COBYLA"):
        E, p, hist = vqe(H2_TERMS, 2, 1, rng, method=method)
        print(f"VQE {method}: E={E:.6f} (error {E - E0:.2e}), restarts {np.round(hist, 5)}, params {np.round(p, 3)}")
    st = ansatz(p, 2, 1).state
    print("ground-state amplitudes (real):", np.round(st.real, 4), " -> dominated by |10>, |01>")
