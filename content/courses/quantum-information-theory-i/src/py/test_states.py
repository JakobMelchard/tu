import numpy as np
import pytest

from states import (BELL, bipartite_bloch, from_bipartite_bloch, PAULI, bloch_vector, dm, from_bloch, from_generalised_bloch,
                    from_two_qubit_decomposition, gell_mann, generalised_bloch, is_state, ket,
                    kron, linear_entropy, partial_trace, purity, random_pure, random_state,
                    random_unitary, two_qubit_decomposition)


def test_pure_qubit_bloch_vector_is_unit_and_purity_formula():
    rng = np.random.default_rng(0)
    for _ in range(20):
        r = bloch_vector(dm(random_pure(2, rng)))
        assert np.linalg.norm(r) == pytest.approx(1)
    r = np.array([0.1, -0.5, 0.3])
    rho = from_bloch(r)
    assert is_state(rho)
    assert purity(rho) == pytest.approx((1 + r @ r) / 2)
    assert np.allclose(bloch_vector(rho), r)


def test_bloch_ball_boundary():
    assert not is_state(from_bloch([0.8, 0.8, 0.0]))  # |r| > 1 gives a negative eigenvalue


@pytest.mark.parametrize("d", [2, 3, 4])
def test_gell_mann_basis_properties(d):
    L = gell_mann(d)
    assert len(L) == d * d - 1
    G = np.array([[np.trace(a @ b) for b in L] for a in L])
    assert np.allclose(G, 2 * np.eye(d * d - 1))
    assert all(abs(np.trace(l)) < 1e-12 and np.allclose(l, l.conj().T) for l in L)


def test_gell_mann_d2_are_paulis():
    L = gell_mann(2)
    assert all(np.allclose(a, b) for a, b in zip(L, PAULI))


@pytest.mark.parametrize("d", [2, 3, 5])
def test_generalised_bloch_roundtrip_and_purity(d):
    rng = np.random.default_rng(d)
    rho = random_state(d, rng)
    b = generalised_bloch(rho)
    assert np.allclose(from_generalised_bloch(b, d), rho)
    assert b @ b == pytest.approx(2 * (purity(rho) - 1 / d))


def test_two_qubit_decomposition_singlet_and_roundtrip():
    a, b, T = two_qubit_decomposition(dm(BELL["psi-"]))
    assert np.allclose(a, 0) and np.allclose(b, 0) and np.allclose(T, -np.eye(3))
    rho = random_state(4, np.random.default_rng(1))
    assert np.allclose(from_two_qubit_decomposition(*two_qubit_decomposition(rho)), rho)


def test_partial_trace_of_product_and_three_parties():
    rng = np.random.default_rng(2)
    A, B, C = random_state(2, rng), random_state(3, rng), random_state(2, rng)
    rho = kron(A, B, C)
    assert np.allclose(partial_trace(rho, [2, 3, 2], [0]), A)
    assert np.allclose(partial_trace(rho, [2, 3, 2], [1]), B)
    assert np.allclose(partial_trace(rho, [2, 3, 2], [0, 2]), np.kron(A, C))
    assert partial_trace(rho, [2, 3, 2], []).item() == pytest.approx(1)


def test_partial_trace_matches_explicit_sum():
    rng = np.random.default_rng(3)
    rho = random_state(6, rng)
    explicit = sum(np.kron(np.eye(2), ket(*np.eye(3)[j]).conj()) @ rho
                   @ np.kron(np.eye(2), ket(*np.eye(3)[j]).reshape(3, 1)) for j in range(3))
    assert np.allclose(partial_trace(rho, [2, 3], [0]), explicit)


def test_partial_trace_invariant_under_local_unitary_on_traced_part():
    rng = np.random.default_rng(4)
    rho = random_state(6, rng)
    U = np.kron(np.eye(2), random_unitary(3, rng))
    assert np.allclose(partial_trace(U @ rho @ U.conj().T, [2, 3], [0]), partial_trace(rho, [2, 3], [0]))


def test_linear_entropy_range():
    assert linear_entropy(np.eye(4) / 4) == pytest.approx(3 / 4)
    assert linear_entropy(np.eye(4) / 4, normalised=True) == pytest.approx(1)
    assert linear_entropy(dm(ket(1, 0))) == pytest.approx(0)


def test_bipartite_bloch_roundtrip_reduced_state_and_purity():
    rng = np.random.default_rng(5)
    da, db = 2, 3
    rho = random_state(da * db, rng)
    a, b, T = bipartite_bloch(rho, da, db)
    assert np.allclose(from_bipartite_bloch(a, b, T, da, db), rho)
    assert np.allclose(from_generalised_bloch(a, da), partial_trace(rho, [da, db], [0]))
    assert np.allclose(from_generalised_bloch(b, db), partial_trace(rho, [da, db], [1]))
    pur = (1 + da / 2 * a @ a + db / 2 * b @ b + da * db / 4 * (T * T).sum()) / (da * db)
    assert purity(rho) == pytest.approx(pur)


def test_product_state_has_factorised_correlation_tensor():
    rng = np.random.default_rng(6)
    A, B = random_state(3, rng), random_state(2, rng)
    a, b, T = bipartite_bloch(np.kron(A, B), 3, 2)
    assert np.allclose(T, np.outer(a, b))
