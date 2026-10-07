import numpy as np

from vqe import (H2_TERMS, ansatz, energy, exact_ground_energy, finite_difference_gradient,
                 hamiltonian_matrix, parameter_shift_gradient, vqe)


def test_exact_ground_energy_by_diagonalisation():
    """Reference result: O'Malley et al., Phys. Rev. X 6, 031007 (2016) [S50].

    The two-qubit reduced H2 Hamiltonian at 0.735 A in STO-3G has ground energy
    -1.8572 Ha.  With the five coefficients as published to four decimals the
    diagonalisation gives -1.85710; the 1e-4 gap is their rounding.  The whole
    spectrum is checked too, because the note C08 quotes all four levels.
    """
    E0 = exact_ground_energy(H2_TERMS)
    assert abs(E0 - (-1.85710)) < 1e-5
    assert abs(E0 - (-1.8572)) < 2e-4          # the published value
    spectrum = np.linalg.eigvalsh(hamiltonian_matrix(H2_TERMS))
    assert np.allclose(spectrum, [-1.85710, -1.24450, -0.88270, -0.22490], atol=1e-4)
    Hm = hamiltonian_matrix(H2_TERMS)
    assert np.allclose(Hm, Hm.conj().T)
    # C08's diagonal entries, which are what a hand calculation produces first
    assert np.allclose(np.diag(Hm).real, [-1.0636, -0.2452, -1.8368, -1.0636], atol=1e-4)


def test_energy_from_statevector_matches_matrix():
    rng = np.random.default_rng(0)
    Hm = hamiltonian_matrix(H2_TERMS)
    for _ in range(5):
        p = rng.uniform(0, 2 * np.pi, 4)
        psi = ansatz(p, 2, 1).state
        assert np.isclose(energy(p, H2_TERMS, 2, 1), np.real(np.vdot(psi, Hm @ psi)))


def test_parameter_shift_matches_finite_differences():
    rng = np.random.default_rng(1)
    for layers in (1, 2):
        p = rng.uniform(0, 2 * np.pi, 2 * (layers + 1))
        g_ps = parameter_shift_gradient(p, H2_TERMS, 2, layers)
        g_fd = finite_difference_gradient(p, H2_TERMS, 2, layers)
        assert np.allclose(g_ps, g_fd, atol=1e-6)
        assert np.linalg.norm(g_ps) > 1e-3


def test_vqe_converges_to_ground_energy():
    rng = np.random.default_rng(2)
    E0 = exact_ground_energy(H2_TERMS)
    E, p, _ = vqe(H2_TERMS, 2, 1, rng, method="BFGS")
    assert abs(E - E0) < 1e-3
    assert E >= E0 - 1e-9                              # variational principle
    E, p, _ = vqe(H2_TERMS, 2, 1, rng, method="COBYLA", restarts=4)
    assert abs(E - E0) < 1e-3
