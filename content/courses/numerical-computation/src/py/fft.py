"""Trigonometric interpolation and the FFT (note 02).

Implements [S4 §1.9] (CSE): the DFT and its matrix (Thm 1.45), the FFT by
decimation in frequency [S4 Alg. 3-4] (fft_dif / ifft_dif), trigonometric
interpolation [S4 (1.36)], fast convolution [S4 Ex. 1.57] and circulant
systems [S4 Ex. 1.59].  Decimation in time (fft_recursive, fft_iterative) and
the real-signal tricks (fft_two_real, rfft) are background.
Convention: X_k = sum_n x_n exp(-2 pi i k n / N), inverse has 1/N.
"""
import numpy as np


def dft(x):
    """O(N^2): multiply by the Fourier matrix F_kn = w^(kn), w = exp(-2 pi i/N)."""
    x = np.asarray(x, complex)
    N = len(x)
    k = np.arange(N)
    F = np.exp(-2j * np.pi * np.outer(k, k) / N)
    return F @ x


def fft_recursive(x):
    """Cooley-Tukey radix-2 decimation in time:
    X_k = E_k + w^k O_k,  X_{k+N/2} = E_k - w^k O_k  (butterfly),
    E, O = FFTs of the even/odd samples.  T(N) = 2 T(N/2) + O(N) = O(N log N)."""
    x = np.asarray(x, complex)
    N = len(x)
    if N == 1:
        return x
    if N % 2:
        raise ValueError("length must be a power of two")
    E = fft_recursive(x[0::2])
    O = fft_recursive(x[1::2])
    w = np.exp(-2j * np.pi * np.arange(N // 2) / N)
    return np.concatenate([E + w * O, E - w * O])


def bit_reverse_permutation(N):
    """Index j -> reverse of its log2(N)-bit representation."""
    bits = N.bit_length() - 1
    idx = np.arange(N)
    rev = np.zeros(N, int)
    for b in range(bits):
        rev |= ((idx >> b) & 1) << (bits - 1 - b)
    return rev


def fft_iterative(x):
    """In-place radix-2 FFT: bit-reverse the input, then log2 N stages of
    butterflies with span s = 2, 4, ..., N.  Same arithmetic as the recursive
    version without the recursion/copies; this is what fft.cpp implements."""
    x = np.asarray(x, complex)
    N = len(x)
    if N & (N - 1):
        raise ValueError("length must be a power of two")
    X = x[bit_reverse_permutation(N)].copy()
    s = 2
    while s <= N:
        half = s // 2
        w = np.exp(-2j * np.pi * np.arange(half) / s)          # twiddles for this stage
        for start in range(0, N, s):
            a = X[start:start + half]
            b = w * X[start + half:start + s]
            X[start:start + half], X[start + half:start + s] = a + b, a - b
        s *= 2
    return X


def ifft(X):
    """x = conj(FFT(conj(X))) / N."""
    X = np.asarray(X, complex)
    return np.conj(fft_iterative(np.conj(X))) / len(X)


def next_pow2(n):
    return 1 << (n - 1).bit_length()


def convolve(a, b):
    """Linear convolution c_k = sum_j a_j b_{k-j} of length len(a)+len(b)-1,
    computed as ifft(fft(a) fft(b)) after zero-padding to a power of two
    (circular convolution theorem).  O(N log N) instead of O(N^2)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = len(a) + len(b) - 1
    N = next_pow2(L)
    A = fft_iterative(np.concatenate([a, np.zeros(N - len(a))]))
    B = fft_iterative(np.concatenate([b, np.zeros(N - len(b))]))
    return ifft(A * B)[:L].real


def fft_two_real(x, y):
    """Two real signals with one complex FFT: z = x + i y, Z = FFT(z), then
    X_k = (Z_k + conj(Z_{N-k}))/2,  Y_k = (Z_k - conj(Z_{N-k}))/(2i)
    using the Hermitian symmetry of real-signal spectra."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    N = len(x)
    Z = fft_iterative(x + 1j * y)
    Zr = np.conj(np.roll(Z[::-1], 1))       # conj(Z_{N-k})
    return 0.5 * (Z + Zr), (Z - Zr) / (2j)


def rfft(x):
    """Real FFT of length N (even) via a complex FFT of length N/2:
    z_n = x_{2n} + i x_{2n+1}, Z = FFT_{N/2}(z), split into the FFTs of the
    even and odd samples as in fft_two_real, then one butterfly stage.
    Returns X_0..X_{N/2} (the rest is the conjugate mirror)."""
    x = np.asarray(x, float)
    N = len(x)
    M = N // 2
    Z = fft_iterative(x[0::2] + 1j * x[1::2])
    Zr = np.conj(np.roll(Z[::-1], 1))
    E, O = 0.5 * (Z + Zr), (Z - Zr) / (2j)
    w = np.exp(-2j * np.pi * np.arange(M) / N)
    X = np.empty(M + 1, complex)
    X[:M] = E + w * O
    X[M] = E[0] - O[0]
    return X



# ---------------------------------------- [S4] sec. 1.9: the course's version
def fft_dif(y):
    """FFT by decimation in frequency -- [S4] Alg. 3, the form the course teaches.

    With n = 2m and omega = exp(-2 pi i / n), [S4] Lem. 1.48 splits the OUTPUT
    index by parity:
        alpha_{2l}   = DFT_m(g)_l   with g_j = y_j + y_{j+m}
        alpha_{2l+1} = DFT_m(h)_l   with h_j = (y_j - y_{j+m}) omega^j
    The input is untouched and the output comes out in bit-reversed order, the
    mirror image of the decimation-in-time version in fft_recursive.
    """
    y = np.asarray(y, complex)
    n = len(y)
    if n == 1:
        return y.copy()
    if n % 2:
        raise ValueError("length must be a power of two")
    m = n // 2
    w = np.exp(-2j * np.pi / n)
    g = y[:m] + y[m:]
    h = (y[:m] - y[m:]) * w ** np.arange(m)
    out = np.empty(n, complex)
    out[0::2] = fft_dif(g)
    out[1::2] = fft_dif(h)
    return out


def ifft_dif(y):
    """Inverse FFT by decimation in frequency -- [S4] Alg. 4.

    The same recursion with omega = exp(+2 pi i / n) and a factor 1/2 on both
    g and h; the n halvings supply the 1/n of [S4] Rem. 1.47.
    """
    y = np.asarray(y, complex)
    n = len(y)
    if n == 1:
        return y.copy()
    if n % 2:
        raise ValueError("length must be a power of two")
    m = n // 2
    w = np.exp(2j * np.pi / n)
    g = 0.5 * (y[:m] + y[m:])
    h = 0.5 * (y[:m] - y[m:]) * w ** np.arange(m)
    out = np.empty(n, complex)
    out[0::2] = ifft_dif(g)
    out[1::2] = ifft_dif(h)
    return out


def trig_interp_coeffs(y):
    """Coefficients c_k of the modified trigonometric interpolant, [S4] (1.36).

    For the uniform knots x_j = 2 pi j / n, [S4] Thm 1.45(i) gives
        c = (1/n) V_n y,   c_k = (1/n) sum_j omega_n^{jk} y_j,
    with omega_n = exp(-2 pi i / n) -- so c is the DFT divided by n.  Then
    p(x) = sum_k c_k exp(i k x) interpolates y at the knots, because
    sum_k omega_n^{(l-j)k} = n delta_{lj}.
    """
    y = np.asarray(y, complex)
    n = len(y)
    j = np.arange(n)
    return (np.exp(-2j * np.pi * np.outer(j, j) / n) @ y) / n


def trig_interp_eval(c, x):
    """p(x) = sum_{k=0}^{n-1} c_k exp(i k x),  [S4] Def. 1.40."""
    c = np.asarray(c, complex)
    x = np.atleast_1d(np.asarray(x, float))
    k = np.arange(len(c))
    return np.exp(1j * np.outer(x, k)) @ c


def dft_matrix(n):
    """V_n = (omega_n^{jk}),  [S4] Def. 1.44.  V_n/sqrt(n) is symmetric unitary."""
    j = np.arange(n)
    return np.exp(-2j * np.pi * np.outer(j, j) / n)


def solve_circulant(c, b):
    """Solve C x = b for the circulant C with first column c, in O(n log n).

    [S4] Ex. 1.59: a circulant is diagonalised by the DFT, so
        C x = b   <=>   chat * xhat = bhat   (componentwise)
    """
    c, b = np.asarray(c, complex), np.asarray(b, complex)
    ch = fft_iterative(c) if len(c) & (len(c) - 1) == 0 else dft(c)
    bh = fft_iterative(b) if len(b) & (len(b) - 1) == 0 else dft(b)
    if np.any(np.abs(ch) < 1e-300):
        raise np.linalg.LinAlgError("singular circulant matrix")
    xh = bh / ch
    n = len(b)
    x = np.conj(dft(np.conj(xh))) / n
    return x.real if np.allclose(x.imag, 0.0, atol=1e-10) else x


def circulant(c):
    """The circulant matrix with first column c (for tests and demos)."""
    c = np.asarray(c)
    n = len(c)
    return np.array([[c[(i - j) % n] for j in range(n)] for i in range(n)])


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    x = rng.standard_normal(16)
    X = fft_iterative(x)
    print("iterative vs recursive vs naive DFT, max diff:",
          np.abs(X - fft_recursive(x)).max(), np.abs(X - dft(x)).max())
    print("ifft(fft(x)) - x:", np.abs(ifft(X) - x).max())
    print("Parseval sum|x|^2 = sum|X|^2/N:", np.sum(x * x), np.sum(np.abs(X) ** 2) / 16)

    t = np.arange(64) / 64
    sig = np.sin(2 * np.pi * 5 * t) + 0.5 * np.cos(2 * np.pi * 12 * t)
    S = fft_iterative(sig)
    print("peaks at bins:", np.flatnonzero(np.abs(S) > 1)[:4], "(expect 5, 12, 52, 59)")

    a, b = [1, 2, 3], [4, 5, 6, 7]
    print("convolution via FFT:", np.round(convolve(a, b), 10), " direct:", np.convolve(a, b))

    y = rng.standard_normal(16)
    Xa, Ya = fft_two_real(x, y)
    print("two-for-one real trick error:", np.abs(Xa - X).max(), np.abs(Ya - fft_iterative(y)).max())
    print("rfft error:", np.abs(rfft(x) - X[:9]).max())

    print("\ncomplexity: operations naive N^2 vs N log2 N")
    for N in (2 ** 6, 2 ** 10, 2 ** 20):
        print(f"  N={N:8d}: {N * N:14d}  vs {N * int(np.log2(N)):10d}  (ratio {N / np.log2(N):.0f})")
