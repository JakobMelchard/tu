// LU decomposition with partial pivoting (P A = L U) and solve; note 05,
// [S4 §4.2, §4.4].
// Dense row-major matrices as std::vector<double>.  Build: make; run: ./lu
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <stdexcept>
#include <vector>

#include "check.hpp"

using Mat = std::vector<double>;  // n x n row-major
using Vec = std::vector<double>;

// In-place: A becomes packed LU (unit L strictly below the diagonal, U on and
// above), piv[k] = row swapped into position k.  ~ 2n^3/3 flops.
void lu_decompose(Mat& A, std::vector<int>& piv, int n) {
    piv.resize(n);
    for (int k = 0; k < n; ++k) {
        // partial pivoting: largest |a_ik| in column k below the diagonal
        int p = k;
        for (int i = k + 1; i < n; ++i)
            if (std::fabs(A[i * n + k]) > std::fabs(A[p * n + k])) p = i;
        piv[k] = p;
        if (A[p * n + k] == 0.0) throw std::runtime_error("singular matrix");
        if (p != k)
            for (int j = 0; j < n; ++j) std::swap(A[k * n + j], A[p * n + j]);
        // eliminate below the pivot, store multipliers in L
        for (int i = k + 1; i < n; ++i) {
            const double m = A[i * n + k] / A[k * n + k];
            A[i * n + k] = m;
            for (int j = k + 1; j < n; ++j) A[i * n + j] -= m * A[k * n + j];
        }
    }
}

// Solve A x = b given the packed LU: apply the row swaps to b, then
// forward substitution (L y = P b) and back substitution (U x = y).  O(n^2).
Vec lu_solve(const Mat& LU, const std::vector<int>& piv, Vec b, int n) {
    for (int k = 0; k < n; ++k) std::swap(b[k], b[piv[k]]);
    for (int i = 1; i < n; ++i)
        for (int j = 0; j < i; ++j) b[i] -= LU[i * n + j] * b[j];
    for (int i = n - 1; i >= 0; --i) {
        for (int j = i + 1; j < n; ++j) b[i] -= LU[i * n + j] * b[j];
        b[i] /= LU[i * n + i];
    }
    return b;
}

double lu_det(const Mat& LU, const std::vector<int>& piv, int n) {
    double d = 1.0;
    for (int k = 0; k < n; ++k) d *= LU[k * n + k] * (piv[k] != k ? -1.0 : 1.0);
    return d;
}

Vec matvec(const Mat& A, const Vec& x, int n) {
    Vec y(n, 0.0);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j) y[i] += A[i * n + j] * x[j];
    return y;
}

double max_abs_diff(const Vec& a, const Vec& b) {
    double m = 0.0;
    for (size_t i = 0; i < a.size(); ++i) m = std::max(m, std::fabs(a[i] - b[i]));
    return m;
}

int main() {
    // 1. small hand-checkable system: x = (1, 1, 2), det = -16
    {
        const int n = 3;
        Mat A = {2, 1, 1, 4, -6, 0, -2, 7, 2};
        Vec b = {5, -2, 9};
        Mat LU = A;
        std::vector<int> piv;
        lu_decompose(LU, piv, n);
        Vec x = lu_solve(LU, piv, b, n);
        std::printf("3x3 system: x = (%.10g, %.10g, %.10g), det = %.10g\n", x[0], x[1], x[2], lu_det(LU, piv, n));
        CHECK_NEAR(x[0], 1.0, 1e-12);
        CHECK_NEAR(x[1], 1.0, 1e-12);
        CHECK_NEAR(x[2], 2.0, 1e-12);
        CHECK_NEAR(lu_det(LU, piv, n), -16.0, 1e-12);
    }
    // 2. a matrix that needs pivoting (zero leading entry)
    {
        Mat A = {0, 1, 1, 0};
        std::vector<int> piv;
        lu_decompose(A, piv, 2);
        Vec x = lu_solve(A, piv, {2, 3}, 2);
        CHECK_NEAR(x[0], 3.0, 1e-15);
        CHECK_NEAR(x[1], 2.0, 1e-15);
    }
    // 3. n = 200 random-ish matrix with known solution: residual and error
    {
        const int n = 200;
        Mat A(n * n);
        unsigned s = 12345;
        auto rnd = [&s]() { s = 1664525u * s + 1013904223u; return (s >> 8) / 16777216.0 - 0.5; };
        for (auto& a : A) a = rnd();
        for (int i = 0; i < n; ++i) A[i * n + i] += 4.0;  // diagonally dominant-ish
        Vec x_true(n);
        for (int i = 0; i < n; ++i) x_true[i] = std::sin(0.1 * i);
        Vec b = matvec(A, x_true, n);
        Mat LU = A;
        std::vector<int> piv;
        lu_decompose(LU, piv, n);
        Vec x = lu_solve(LU, piv, b, n);
        const double err = max_abs_diff(x, x_true);
        const double res = max_abs_diff(matvec(A, x, n), b);
        std::printf("n=%d: max error %.2e, max residual %.2e\n", n, err, res);
        CHECK_LESS(err, 1e-10);          // forward error ~ kappa * backward error
        CHECK_LESS(res, 1e-12);          // backward error ~ u
        // growth factor stays modest for partial pivoting on random matrices
        double umax = 0.0, amax = 0.0;
        for (int i = 0; i < n; ++i)
            for (int j = i; j < n; ++j) umax = std::max(umax, std::fabs(LU[i * n + j]));
        for (double a : A) amax = std::max(amax, std::fabs(a));
        std::printf("growth factor max|u_ij|/max|a_ij| = %.3f\n", umax / amax);
        CHECK_LESS(umax / amax, 50.0);
    }
    // 4. singular matrix is detected
    {
        Mat A = {1, 2, 2, 4};
        std::vector<int> piv;
        bool threw = false;
        try { lu_decompose(A, piv, 2); } catch (const std::runtime_error&) { threw = true; }
        CHECK_NEAR(threw ? 1.0 : 0.0, 1.0, 0.0);
    }
    return check::summary("lu");
}
