import numpy as np

from qft import qft, qft_matrix
from sim import Register


def random_state(n, rng):
    v = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
    return v / np.linalg.norm(v)


def test_matches_dft_matrix_and_numpy_ifft():
    rng = np.random.default_rng(0)
    for n in range(1, 6):
        psi = random_state(n, rng)
        got = qft(Register(n, psi), range(n)).state
        assert np.allclose(got, qft_matrix(n) @ psi)
        assert np.allclose(got, np.fft.ifft(psi) * np.sqrt(2 ** n))   # numpy's sign convention is e^{-2 pi i}


def test_inverse_and_unitarity():
    rng = np.random.default_rng(1)
    for n in range(1, 6):
        psi = random_state(n, rng)
        back = qft(qft(Register(n, psi), range(n)), range(n), inverse=True).state
        assert np.allclose(back, psi)
        inv = qft(Register(n, psi), range(n), inverse=True).state
        assert np.allclose(inv, qft_matrix(n).conj().T @ psi)
    F = qft_matrix(4)
    assert np.allclose(F @ F.conj().T, np.eye(16))


def test_on_a_sub_register_and_without_swaps():
    rng = np.random.default_rng(2)
    psi = random_state(5, rng)
    got = qft(Register(5, psi), [1, 3, 4]).state
    # reference: dense F on qubits (1,3,4) using the simulator's generic gate application
    ref = Register(5, psi).apply_gate(qft_matrix(3), [1, 3, 4]).state
    assert np.allclose(got, ref)
    # do_swaps=False yields the bit-reversed output
    got = qft(Register(3, psi[:8] / np.linalg.norm(psi[:8])), [0, 1, 2], do_swaps=False).state
    ref = qft(Register(3, psi[:8] / np.linalg.norm(psi[:8])), [0, 1, 2]).state
    rev = [int(f"{i:03b}"[::-1], 2) for i in range(8)]
    assert np.allclose(got[rev], ref)
