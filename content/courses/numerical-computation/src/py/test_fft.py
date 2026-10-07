import numpy as np
import pytest
import scipy.signal

from fft import (dft, fft_recursive, fft_iterative, bit_reverse_permutation, ifft,
                 convolve, fft_two_real, rfft, next_pow2, fft_dif, ifft_dif,
                 trig_interp_coeffs, trig_interp_eval, dft_matrix, solve_circulant,
                 circulant)


@pytest.mark.parametrize("N", [1, 2, 4, 8, 64, 256])
def test_fft_matches_numpy(N):
    x = np.random.default_rng(N).standard_normal(N) + 1j * np.random.default_rng(N + 1).standard_normal(N)
    ref = np.fft.fft(x)
    np.testing.assert_allclose(fft_iterative(x), ref, atol=1e-11)
    np.testing.assert_allclose(fft_recursive(x), ref, atol=1e-11)
    if N <= 64:
        np.testing.assert_allclose(dft(x), ref, atol=1e-10)


def test_bit_reversal():
    np.testing.assert_array_equal(bit_reverse_permutation(8), [0, 4, 2, 6, 1, 5, 3, 7])
    p = bit_reverse_permutation(64)
    assert np.array_equal(p[p], np.arange(64))                 # involution


def test_non_power_of_two_rejected():
    with pytest.raises(ValueError):
        fft_iterative(np.ones(12))
    with pytest.raises(ValueError):
        fft_recursive(np.ones(6))


def test_inverse_and_parseval():
    x = np.random.default_rng(7).standard_normal(32)
    X = fft_iterative(x)
    np.testing.assert_allclose(ifft(X), x, atol=1e-13)
    assert abs(np.sum(x ** 2) - np.sum(np.abs(X) ** 2) / 32) < 1e-10


def test_pure_tone_lands_in_one_bin():
    N, k = 128, 9
    x = np.cos(2 * np.pi * k * np.arange(N) / N)
    X = fft_iterative(x)
    assert abs(X[k] - N / 2) < 1e-10 and abs(X[N - k] - N / 2) < 1e-10
    X[[k, N - k]] = 0
    assert np.max(np.abs(X)) < 1e-10


def test_convolution_matches_numpy_and_scipy():
    rng = np.random.default_rng(8)
    a, b = rng.standard_normal(37), rng.standard_normal(52)
    c = convolve(a, b)
    assert len(c) == 88
    np.testing.assert_allclose(c, np.convolve(a, b), atol=1e-11)
    np.testing.assert_allclose(c, scipy.signal.fftconvolve(a, b), atol=1e-11)
    assert next_pow2(88) == 128 and next_pow2(64) == 64


def test_real_signal_tricks():
    rng = np.random.default_rng(9)
    x, y = rng.standard_normal(64), rng.standard_normal(64)
    X, Y = fft_two_real(x, y)
    np.testing.assert_allclose(X, np.fft.fft(x), atol=1e-12)
    np.testing.assert_allclose(Y, np.fft.fft(y), atol=1e-12)
    np.testing.assert_allclose(rfft(x), np.fft.rfft(x), atol=1e-12)


# ================= [S4] sec. 1.9: the course's own version ==================

_RNG = np.random.default_rng(31)


def test_dif_matches_dit_and_numpy():
    """[S4] Alg. 3 (decimation in frequency) against the usual DIT version."""
    for n in (1, 2, 4, 8, 16, 64):
        y = _RNG.standard_normal(n) + 1j * _RNG.standard_normal(n)
        np.testing.assert_allclose(fft_dif(y), np.fft.fft(y), atol=1e-10)
        np.testing.assert_allclose(fft_dif(y), fft_recursive(y), atol=1e-10)
        np.testing.assert_allclose(fft_dif(y), fft_iterative(y), atol=1e-10)


def test_dif_worked_example_from_the_note():
    """n = 4, y = (1,2,3,4): g = (4,6), h = (-2, 2i), output (10, -2+2i, -2, -2-2i)."""
    y = np.array([1.0, 2.0, 3.0, 4.0])
    np.testing.assert_allclose(fft_dif(y), [10, -2 + 2j, -2, -2 - 2j], atol=1e-12)
    m, w = 2, np.exp(-2j * np.pi / 4)
    np.testing.assert_allclose(y[:m] + y[m:], [4.0, 6.0])
    np.testing.assert_allclose((y[:m] - y[m:]) * w ** np.arange(m), [-2.0, 2j], atol=1e-12)


def test_ifft_dif_inverts():
    """[S4] Alg. 4: the same recursion with omega conjugated and a factor 1/2."""
    for n in (2, 8, 32):
        y = _RNG.standard_normal(n) + 1j * _RNG.standard_normal(n)
        np.testing.assert_allclose(ifft_dif(fft_dif(y)), y, atol=1e-10)
        np.testing.assert_allclose(ifft_dif(y), np.fft.ifft(y), atol=1e-10)


def test_dif_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        fft_dif(np.ones(6))


def test_dft_matrix_is_symmetric_and_unitary_after_scaling():
    """[S4] Thm 1.45(ii)."""
    for n in (3, 4, 8):
        V = dft_matrix(n)
        np.testing.assert_allclose(V, V.T, atol=1e-12)
        U = V / np.sqrt(n)
        np.testing.assert_allclose(U.conj().T @ U, np.eye(n), atol=1e-12)
        np.testing.assert_allclose(np.linalg.inv(U), U.conj(), atol=1e-12)


def test_trigonometric_interpolation_hits_the_data():
    """[S4] (1.36), Thm 1.43, Thm 1.45(i)."""
    for n in (4, 8, 16):
        y = _RNG.standard_normal(n)
        c = trig_interp_coeffs(y)
        xs = 2 * np.pi * np.arange(n) / n
        np.testing.assert_allclose(trig_interp_eval(c, xs).real, y, atol=1e-10)
        np.testing.assert_allclose(trig_interp_eval(c, xs).imag, 0.0, atol=1e-10)
        np.testing.assert_allclose(c, np.fft.fft(y) / n, atol=1e-12)   # c = V_n y / n


def test_trigonometric_interpolation_is_periodic():
    y = _RNG.standard_normal(8)
    c = trig_interp_coeffs(y)
    t = np.linspace(0, 2 * np.pi, 37)
    np.testing.assert_allclose(trig_interp_eval(c, t), trig_interp_eval(c, t + 2 * np.pi),
                               atol=1e-9)


def test_circulant_systems_via_the_dft():
    """[S4] Ex. 1.59: a circulant is diagonalised by the DFT."""
    for c in ([4.0, 1.0, 0.0, 1.0], [3.0, -1, 0, 0, 0, 0, 0, -1]):
        c = np.array(c)
        C = circulant(c)
        b = _RNG.standard_normal(len(c))
        np.testing.assert_allclose(solve_circulant(c, b), np.linalg.solve(C, b), atol=1e-9)
    # the eigenvalues of C really are the DFT of its first column
    c = np.array([4.0, 1.0, 0.0, 1.0])
    np.testing.assert_allclose(np.sort(np.linalg.eigvals(circulant(c)).real),
                               np.sort(np.fft.fft(c).real), atol=1e-10)


def test_convolution_theorem_example_from_s4():
    """[S4] Ex. 1.57: multiplying polynomials is convolving coefficients."""
    a, b = [1, 2, 3], [4, 5, 6, 7]
    np.testing.assert_allclose(np.round(convolve(a, b), 10), [4, 13, 28, 34, 32, 21])
    np.testing.assert_allclose(np.convolve(a, b), [4, 13, 28, 34, 32, 21])
