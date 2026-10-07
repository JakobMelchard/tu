// Householder QR and least squares; notes 06 and 07, [S4 §4.7.3] (CSE) and
// [S4 §5.2].
// A (m x n, m >= n) is overwritten by R (upper part) and the Householder
// vectors (below the diagonal); Q is applied implicitly to the right-hand side.
// Build: make; run: ./qr
#include <cmath>
#include <cstdio>
#include <vector>

#include "check.hpp"

using Mat = std::vector<double>;  // row-major m x n
using Vec = std::vector<double>;

// For k = 0..n-1: v = A[k:, k] - alpha e_1, alpha = -sign(a_kk) ||A[k:, k]||,
// H = I - 2 v v^T / (v^T v); apply H to the trailing block A[k:, k:].
// Stores v (scaled so v_0 = 1) below the diagonal, and beta_k = 2/(v^T v).
// Cost 2 m n^2 - 2 n^3 / 3 flops.
void householder_qr(Mat& A, int m, int n, Vec& beta) {
    beta.assign(n, 0.0);
    Vec v(m);
    for (int k = 0; k < n; ++k) {
        double norm2 = 0.0;
        for (int i = k; i < m; ++i) norm2 += A[i * n + k] * A[i * n + k];
        const double norm = std::sqrt(norm2);
        if (norm == 0.0) continue;
        const double alpha = A[k * n + k] >= 0 ? -norm : norm;   // avoid cancellation
        for (int i = k; i < m; ++i) v[i] = A[i * n + k];
        v[k] -= alpha;
        double vv = 0.0;
        for (int i = k; i < m; ++i) vv += v[i] * v[i];
        // apply H to columns k..n-1
        for (int j = k; j < n; ++j) {
            double s = 0.0;
            for (int i = k; i < m; ++i) s += v[i] * A[i * n + j];
            s *= 2.0 / vv;
            for (int i = k; i < m; ++i) A[i * n + j] -= s * v[i];
        }
        // store v scaled by v_k below the diagonal; R_kk = alpha already there
        for (int i = k + 1; i < m; ++i) A[i * n + k] = v[i] / v[k];
        beta[k] = 2.0 / vv * v[k] * v[k];   // 2 / (v'^T v') with v' = v / v_k
    }
}

// b <- Q^T b by applying H_0, ..., H_{n-1} in order.
void apply_qt(const Mat& A, int m, int n, const Vec& beta, Vec& b) {
    for (int k = 0; k < n; ++k) {
        if (beta[k] == 0.0) continue;
        double s = b[k];                              // v'_k = 1
        for (int i = k + 1; i < m; ++i) s += A[i * n + k] * b[i];
        s *= beta[k];
        b[k] -= s;
        for (int i = k + 1; i < m; ++i) b[i] -= s * A[i * n + k];
    }
}

// Least squares: min ||A x - b||_2  ->  R x = (Q^T b)[0:n], residual = ||(Q^T b)[n:]||.
Vec lstsq(Mat A, int m, int n, Vec b, double* resid = nullptr) {
    Vec beta;
    householder_qr(A, m, n, beta);
    apply_qt(A, m, n, beta, b);
    Vec x(n);
    for (int i = n - 1; i >= 0; --i) {
        double s = b[i];
        for (int j = i + 1; j < n; ++j) s -= A[i * n + j] * x[j];
        x[i] = s / A[i * n + i];
    }
    if (resid) {
        double r = 0.0;
        for (int i = n; i < m; ++i) r += b[i] * b[i];
        *resid = std::sqrt(r);
    }
    return x;
}

int main() {
    // 1. QR of a small matrix: |R_kk| equal the known values, Q^T A = R
    {
        const int m = 3, n = 3;
        Mat A = {12, -51, 4, 6, 167, -68, -4, 24, -41};   // classic example: R = diag(14, 175, -35) up to signs
        Mat R = A;
        Vec beta;
        householder_qr(R, m, n, beta);
        std::printf("R diagonal: %.6f %.6f %.6f (|.| expect 14, 175, 35)\n", R[0], R[4], R[8]);
        CHECK_NEAR(std::fabs(R[0]), 14.0, 1e-12);
        CHECK_NEAR(std::fabs(R[4]), 175.0, 1e-12);
        CHECK_NEAR(std::fabs(R[8]), 35.0, 1e-12);
        // Q^T applied to each column of A must reproduce R's upper part
        double err = 0.0;
        for (int j = 0; j < n; ++j) {
            Vec col(m);
            for (int i = 0; i < m; ++i) col[i] = A[i * n + j];
            apply_qt(R, m, n, beta, col);
            for (int i = 0; i < m; ++i)
                err = std::max(err, std::fabs(col[i] - (i <= j ? R[i * n + j] : 0.0)));
        }
        CHECK_LESS(err, 1e-12);
    }
    // 2. least squares: fit y = 2 + 3 x - x^2 exactly (zero residual), then with a
    //    known perturbation whose residual is computable by hand
    {
        const int m = 7, n = 3;
        Mat A(m * n);
        Vec y(m);
        for (int i = 0; i < m; ++i) {
            const double x = i;
            A[i * n + 0] = 1; A[i * n + 1] = x; A[i * n + 2] = x * x;
            y[i] = 2 + 3 * x - x * x;
        }
        double resid;
        Vec c = lstsq(A, m, n, y, &resid);
        std::printf("exact quadratic fit: c = (%.12g, %.12g, %.12g), residual %.2e\n", c[0], c[1], c[2], resid);
        CHECK_NEAR(c[0], 2.0, 1e-12);
        CHECK_NEAR(c[1], 3.0, 1e-12);
        CHECK_NEAR(c[2], -1.0, 1e-12);
        CHECK_LESS(resid, 1e-12);
        // linear fit to y = (1, 2, 4) at x = (0, 1, 2): normal equations give c = (5/6, 3/2), residual sqrt(1/6)
        Mat B = {1, 0, 1, 1, 1, 2};
        Vec d = lstsq(B, 3, 2, {1, 2, 4}, &resid);
        std::printf("line through (0,1),(1,2),(2,4): c = (%.10f, %.10f), residual %.10f\n", d[0], d[1], resid);
        CHECK_NEAR(d[0], 5.0 / 6.0, 1e-14);
        CHECK_NEAR(d[1], 1.5, 1e-14);
        CHECK_NEAR(resid, std::sqrt(1.0 / 6.0), 1e-14);
    }
    // 3. ill-conditioned Vandermonde (degree 12 on 60 points): QR still gives a
    //    small residual where the normal equations would lose ~kappa^2 u
    {
        const int m = 60, n = 13;
        Mat A(m * n);
        Vec y(m);
        for (int i = 0; i < m; ++i) {
            const double x = i / (m - 1.0);
            double p = 1.0;
            for (int j = 0; j < n; ++j) { A[i * n + j] = p; p *= x; }
            y[i] = std::exp(x);
        }
        double resid;
        Vec c = lstsq(A, m, n, y, &resid);
        double maxres = 0.0;
        for (int i = 0; i < m; ++i) {
            double s = 0.0, p = 1.0;
            const double x = i / (m - 1.0);
            for (int j = 0; j < n; ++j) { s += c[j] * p; p *= x; }
            maxres = std::max(maxres, std::fabs(s - y[i]));
        }
        std::printf("degree-12 fit of exp on [0,1]: max residual %.2e, c0 = %.12f (exp(0) = 1)\n", maxres, c[0]);
        CHECK_LESS(maxres, 1e-10);
        CHECK_NEAR(c[0], 1.0, 1e-9);
    }
    return check::summary("qr");
}
