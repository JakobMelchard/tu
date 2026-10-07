import numpy as np
import pytest
from scipy.stats import unitary_group

import sim
from sim import (CNOT, CZ, H, I, Register, SWAP, TOFFOLI, X, Y, Z, controlled,
                 fidelity, ket, kron, permutation_matrix, phase)


def dense_on(U, targets, n):
    """Independent 2^n x 2^n construction of U acting on `targets` by bit arithmetic."""
    k = len(targets)
    D = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for col in range(2 ** n):
        bits = [(col >> (n - 1 - q)) & 1 for q in range(n)]
        x = int("".join(str(bits[t]) for t in targets), 2)
        for y in range(2 ** k):
            if U[y, x] == 0:
                continue
            nb = list(bits)
            for j, t in enumerate(targets):
                nb[t] = (y >> (k - 1 - j)) & 1
            row = int("".join(map(str, nb)), 2)
            D[row, col] += U[y, x]
    return D


def random_state(n, rng):
    v = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
    return v / np.linalg.norm(v)


def test_convention_qubit0_is_msb():
    r = Register(3).x(0)
    assert np.argmax(r.probabilities()) == 0b100
    assert np.allclose(ket("011"), ket(3, 3))
    assert Register(2).x(1).amplitude("01") == 1


def test_single_qubit_gates_match_kronecker_products():
    rng = np.random.default_rng(0)
    for U in (X, Y, Z, H, sim.S, sim.T, sim.Rx(0.7), sim.Ry(1.1), sim.Rz(2.3), phase(0.4)):
        for q in range(3):
            psi = random_state(3, rng)
            mats = [I, I, I]
            mats[q] = U
            expect = kron(*mats) @ psi
            assert np.allclose(Register(3, psi).apply_gate(U, [q]).state, expect)


def test_two_qubit_gates_adjacent_vs_kron():
    rng = np.random.default_rng(1)
    psi = random_state(3, rng)
    assert np.allclose(Register(3, psi).apply_gate(CNOT, [0, 1]).state, kron(CNOT, I) @ psi)
    assert np.allclose(Register(3, psi).apply_gate(SWAP, [1, 2]).state, kron(I, SWAP) @ psi)
    assert np.allclose(Register(3, psi).cx(0, 1).state, kron(CNOT, I) @ psi)


def test_arbitrary_target_order_and_random_unitaries():
    rng = np.random.default_rng(2)
    for n in (3, 4):
        for k in (1, 2, 3):
            U = unitary_group.rvs(2 ** k, random_state=rng)
            targets = list(rng.permutation(n)[:k])
            psi = random_state(n, rng)
            got = Register(n, psi).apply_gate(U, targets).state
            assert np.allclose(got, dense_on(U, targets, n) @ psi)


def test_controlled_gates():
    rng = np.random.default_rng(3)
    psi = random_state(3, rng)
    assert np.allclose(Register(3, psi).apply_controlled(X, [0], [2]).state,
                       dense_on(CNOT, [0, 2], 3) @ psi)
    assert np.allclose(Register(3, psi).ccx(0, 1, 2).state, TOFFOLI @ psi)
    assert np.allclose(Register(3, psi).ccx(2, 0, 1).state, dense_on(TOFFOLI, [2, 0, 1], 3) @ psi)
    assert np.allclose(Register(3, psi).cz(1, 2).state, kron(I, CZ) @ psi)
    U = unitary_group.rvs(4, random_state=rng)
    psi = random_state(4, rng)
    got = Register(4, psi).apply_controlled(U, [3], [0, 2]).state
    assert np.allclose(got, dense_on(controlled(U), [3, 0, 2], 4) @ psi)
    # control on |1> only: |0..> untouched, |1..> rotated
    r = Register(2).h(0).apply_controlled(phase(0.9), [0], [1])
    assert np.allclose(r.state, [1 / np.sqrt(2), 0, 1 / np.sqrt(2), 0])


def test_ghz():
    r = Register(3).h(0).cx(0, 1).cx(1, 2)
    p = r.probabilities()
    assert np.isclose(p[0], 0.5) and np.isclose(p[7], 0.5) and np.isclose(p.sum(), 1)
    assert np.isclose(r.expectation("XXX"), 1) and np.isclose(r.expectation("ZZI"), 1)
    assert np.isclose(r.expectation("ZII"), 0)


def test_partial_trace_of_bell_is_maximally_mixed():
    r = Register(2).h(0).cx(0, 1)
    assert np.allclose(r.partial_trace([0]), np.eye(2) / 2)
    assert np.allclose(r.partial_trace([1]), np.eye(2) / 2)
    rho = r.partial_trace([0, 1])
    assert np.allclose(rho, np.outer(r.state, r.state.conj()))
    assert np.isclose(r.expectation("XX"), 1) and np.isclose(r.expectation("YY"), -1)


def test_measurement_statistics_and_collapse():
    rng = np.random.default_rng(4)
    theta = 1.0
    shots = 4000
    ones = sum(Register(1).ry(theta, 0).measure([0], rng)[0] for _ in range(shots))
    assert abs(ones / shots - np.sin(theta / 2) ** 2) < 0.03
    # collapse of one qubit of a GHZ state fixes the others
    for _ in range(5):
        r = Register(3).h(0).cx(0, 1).cx(1, 2)
        b = r.measure([1], rng)[0]
        assert np.isclose(np.linalg.norm(r.state), 1)
        assert r.measure_all(rng) == [b, b, b]
    # sampling without collapse reproduces probabilities
    r = Register(2).h(0).cx(0, 1)
    counts = np.bincount(r.sample(rng, 2000), minlength=4) / 2000
    assert abs(counts[0] - 0.5) < 0.05 and counts[1] == 0 and counts[2] == 0


def test_permutation_vs_dense_unitary():
    rng = np.random.default_rng(5)
    for n, k in ((3, 2), (4, 3), (4, 4)):
        perm = rng.permutation(2 ** k)
        qubits = list(rng.permutation(n)[:k])
        psi = random_state(n, rng)
        got = Register(n, psi).apply_permutation(perm, qubits).state
        assert np.allclose(got, dense_on(permutation_matrix(perm), qubits, n) @ psi)
    # controlled permutation == dense controlled permutation matrix
    perm = rng.permutation(4)
    psi = random_state(4, rng)
    got = Register(4, psi).apply_controlled_permutation(perm, [1], [3, 0]).state
    assert np.allclose(got, dense_on(controlled(permutation_matrix(perm)), [1, 3, 0], 4) @ psi)
    # apply_function == apply_permutation with the same table
    a = Register(3, psi[:8] / np.linalg.norm(psi[:8])).apply_function(lambda v: (v * 3) % 8, [0, 1, 2])
    b = Register(3, psi[:8] / np.linalg.norm(psi[:8])).apply_permutation([(v * 3) % 8 for v in range(8)], [0, 1, 2])
    assert np.allclose(a.state, b.state)


def test_diagonal_vs_dense():
    rng = np.random.default_rng(6)
    d = np.exp(1j * rng.uniform(0, 2 * np.pi, 4))
    psi = random_state(3, rng)
    got = Register(3, psi).apply_diagonal(d, [2, 0]).state
    assert np.allclose(got, dense_on(np.diag(d), [2, 0], 3) @ psi)
    got = Register(3, psi).apply_diagonal(d, [2, 0], controls=[1]).state
    assert np.allclose(got, dense_on(controlled(np.diag(d)), [1, 2, 0], 3) @ psi)


def test_unitarity_preserved():
    rng = np.random.default_rng(7)
    r = Register(5, random_state(5, rng))
    for _ in range(30):
        q = int(rng.integers(5))
        r.h(q).rz(rng.uniform(0, 7), q).cx(q, (q + 1) % 5).cp(0.3, (q + 2) % 5, q)
    assert np.isclose(np.linalg.norm(r.state), 1)
    r.apply_permutation(rng.permutation(8), [4, 1, 2])
    assert np.isclose(np.linalg.norm(r.state), 1)


def test_fidelity_helper():
    a, b = ket("0", 1), ket("1", 1)
    assert fidelity(a, a) == 1 and fidelity(a, b) == 0
    plus = (a + b) / np.sqrt(2)
    assert np.isclose(fidelity(plus, a), 0.5)
    assert np.isclose(fidelity(plus, np.eye(2) / 2), 0.5)
    with pytest.raises(AssertionError):
        Register(2).expectation("XXX")
