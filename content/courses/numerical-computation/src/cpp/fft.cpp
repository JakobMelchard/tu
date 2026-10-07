// Iterative radix-2 Cooley-Tukey FFT (decimation in time); note 02, [S4 §1.9]
// (CSE).  [S4] teaches decimation in frequency (Alg. 3-4, src/py/fft.py fft_dif);
// both give the same X_k = sum_n x_n exp(-2 pi i k n / N).
// In-place, bit-reversal permutation followed by log2(N) butterfly stages.
// Build: make; run: ./fft
#include <cmath>
#include <complex>
#include <cstdio>
#include <vector>

#include "check.hpp"

using cd = std::complex<double>;
using CVec = std::vector<cd>;

// X_k = sum_n x_n exp(-2 pi i k n / N) (inverse = true: +sign and 1/N).
void fft(CVec& a, bool inverse = false) {
    const size_t N = a.size();
    if (N & (N - 1)) throw std::invalid_argument("length must be a power of two");
    // bit-reversal permutation: j is the bit-reversed counterpart of i
    for (size_t i = 1, j = 0; i < N; ++i) {
        size_t bit = N >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) std::swap(a[i], a[j]);
    }
    // butterflies: span len = 2, 4, ..., N; twiddle w = exp(-+2 pi i / len)
    for (size_t len = 2; len <= N; len <<= 1) {
        const double ang = 2 * M_PI / static_cast<double>(len) * (inverse ? 1 : -1);
        const cd wlen(std::cos(ang), std::sin(ang));
        for (size_t start = 0; start < N; start += len) {
            cd w(1);
            for (size_t k = 0; k < len / 2; ++k) {
                const cd u = a[start + k], v = a[start + k + len / 2] * w;
                a[start + k] = u + v;
                a[start + k + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
    if (inverse)
        for (auto& x : a) x /= static_cast<double>(N);
}

// O(N^2) reference for the tests.
CVec dft(const CVec& x) {
    const size_t N = x.size();
    CVec X(N);
    for (size_t k = 0; k < N; ++k)
        for (size_t n = 0; n < N; ++n)
            X[k] += x[n] * std::polar(1.0, -2 * M_PI * static_cast<double>(k * n) / static_cast<double>(N));
    return X;
}

// Linear convolution via zero-padded FFTs.
std::vector<double> convolve(const std::vector<double>& a, const std::vector<double>& b) {
    size_t L = a.size() + b.size() - 1, N = 1;
    while (N < L) N <<= 1;
    CVec A(N), B(N);
    for (size_t i = 0; i < a.size(); ++i) A[i] = a[i];
    for (size_t i = 0; i < b.size(); ++i) B[i] = b[i];
    fft(A); fft(B);
    for (size_t i = 0; i < N; ++i) A[i] *= B[i];
    fft(A, true);
    std::vector<double> c(L);
    for (size_t i = 0; i < L; ++i) c[i] = A[i].real();
    return c;
}

int main() {
    // 1. pure tone: x_n = cos(2 pi 5 n / 64) -> X_5 = X_59 = 32, everything else 0
    {
        const size_t N = 64;
        CVec x(N);
        for (size_t n = 0; n < N; ++n) x[n] = std::cos(2 * M_PI * 5.0 * static_cast<double>(n) / static_cast<double>(N));
        CVec X = x;
        fft(X);
        double other = 0.0;
        for (size_t k = 0; k < N; ++k)
            if (k != 5 && k != 59) other = std::max(other, std::abs(X[k]));
        std::printf("cos(2 pi 5 n/64): X_5 = %.12f, X_59 = %.12f, max other |X_k| = %.1e\n",
                    X[5].real(), X[59].real(), other);
        CHECK_NEAR(X[5].real(), 32.0, 1e-12);
        CHECK_NEAR(X[59].real(), 32.0, 1e-12);
        CHECK_LESS(std::fabs(X[5].imag()), 1e-12);
        CHECK_LESS(other, 1e-12);
        // inverse restores the signal
        fft(X, true);
        double err = 0.0;
        for (size_t n = 0; n < N; ++n) err = std::max(err, std::abs(X[n] - x[n]));
        CHECK_LESS(err, 1e-14);
    }
    // 2. random data vs the O(N^2) DFT, plus Parseval
    {
        const size_t N = 256;
        CVec x(N);
        unsigned s = 7;
        for (auto& v : x) {
            s = 1664525u * s + 1013904223u; const double re = (s >> 8) / 16777216.0 - 0.5;
            s = 1664525u * s + 1013904223u; const double im = (s >> 8) / 16777216.0 - 0.5;
            v = cd(re, im);
        }
        CVec X = x;
        fft(X);
        CVec R = dft(x);
        double err = 0.0, ex = 0.0, eX = 0.0;
        for (size_t k = 0; k < N; ++k) {
            err = std::max(err, std::abs(X[k] - R[k]));
            ex += std::norm(x[k]);
            eX += std::norm(X[k]);
        }
        std::printf("N=%zu: max |FFT - DFT| = %.2e, Parseval sum|x|^2 = %.12f, sum|X|^2/N = %.12f\n",
                    N, err, ex, eX / static_cast<double>(N));
        CHECK_LESS(err, 1e-11);
        CHECK_NEAR(eX / static_cast<double>(N), ex, 1e-12);
    }
    // 3. convolution: (1,2,3) * (4,5,6,7) = (4,13,28,34,32,21)
    {
        auto c = convolve({1, 2, 3}, {4, 5, 6, 7});
        const double expect[] = {4, 13, 28, 34, 32, 21};
        std::printf("conv: ");
        double err = 0.0;
        for (size_t i = 0; i < c.size(); ++i) { std::printf("%.10g ", c[i]); err = std::max(err, std::fabs(c[i] - expect[i])); }
        std::printf("\n");
        CHECK_LESS(err, 1e-12);
    }
    // 4. bad length is rejected
    {
        CVec bad(12);
        bool threw = false;
        try { fft(bad); } catch (const std::invalid_argument&) { threw = true; }
        CHECK_NEAR(threw ? 1.0 : 0.0, 1.0, 0.0);
    }
    return check::summary("fft");
}
