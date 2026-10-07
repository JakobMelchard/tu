// Conjugate gradient on the 2-D Poisson matrix (5-point stencil, Dirichlet);
// note 10, [S4 §8.1] Alg. 27 (CSE), iteration count O(sqrt(kappa)) by [S4 Thm 8.7].
// The matrix is never stored: matvec applies the stencil directly.
// Build: make; run: ./cg
#include <cmath>
#include <cstdio>
#include <vector>

#include "check.hpp"

using Vec = std::vector<double>;

// A = (1/h^2) * 5-point Laplacian on an m x m interior grid of (0,1)^2, SPD.
struct Poisson2D {
    int m;
    double h;
    explicit Poisson2D(int m_) : m(m_), h(1.0 / (m_ + 1)) {}
    int n() const { return m * m; }
    Vec apply(const Vec& u) const {
        Vec v(n());
        const double s = 1.0 / (h * h);
        for (int i = 0; i < m; ++i)
            for (int j = 0; j < m; ++j) {
                const int k = i * m + j;
                double t = 4.0 * u[k];
                if (i > 0) t -= u[k - m];
                if (i < m - 1) t -= u[k + m];
                if (j > 0) t -= u[k - 1];
                if (j < m - 1) t -= u[k + 1];
                v[k] = s * t;
            }
        return v;
    }
    // eigenvalues 4/h^2 (sin^2(p pi h/2) + sin^2(q pi h/2)), p,q = 1..m
    double lambda_min() const { return 8.0 / (h * h) * std::pow(std::sin(0.5 * M_PI * h), 2); }
    double lambda_max() const { return 8.0 / (h * h) * std::pow(std::sin(0.5 * M_PI * m * h), 2); }
};

double dot(const Vec& a, const Vec& b) {
    double s = 0.0;
    for (size_t i = 0; i < a.size(); ++i) s += a[i] * b[i];
    return s;
}

// Unpreconditioned CG: x_{k+1} = x_k + alpha p_k, r_{k+1} = r_k - alpha A p_k,
// p_{k+1} = r_{k+1} + beta p_k with alpha = r.r/(p.Ap), beta = r'.r'/(r.r).
// One matvec, two dot products, three axpys per iteration.
template <class Op>
int cg(const Op& A, const Vec& b, Vec& x, double tol, int maxiter, std::vector<double>* hist = nullptr) {
    Vec r = A.apply(x);
    for (size_t i = 0; i < r.size(); ++i) r[i] = b[i] - r[i];
    Vec p = r;
    double rr = dot(r, r);
    const double stop = tol * tol * dot(b, b);
    int k = 0;
    for (; k < maxiter && rr > stop; ++k) {
        Vec Ap = A.apply(p);
        const double alpha = rr / dot(p, Ap);
        for (size_t i = 0; i < x.size(); ++i) { x[i] += alpha * p[i]; r[i] -= alpha * Ap[i]; }
        const double rr_new = dot(r, r);
        const double beta = rr_new / rr;
        for (size_t i = 0; i < p.size(); ++i) p[i] = r[i] + beta * p[i];
        rr = rr_new;
        if (hist) hist->push_back(std::sqrt(rr));
    }
    return k;
}

int main() {
    // manufactured solution u = x(1-x) y(1-y): -Laplace u = 2 (x(1-x) + y(1-y)).
    // The 5-point stencil is exact for this bicubic-free polynomial, so the only
    // error is CG's.  (sin(pi x) sin(pi y) would be a bad choice: it is an
    // eigenvector of A and CG converges in one step.)
    const int m = 63;
    Poisson2D A(m);
    const int n = A.n();
    Vec u_exact(n), b(n);
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < m; ++j) {
            const double x = (i + 1) * A.h, y = (j + 1) * A.h;
            u_exact[i * m + j] = x * (1 - x) * y * (1 - y);
            b[i * m + j] = 2.0 * (x * (1 - x) + y * (1 - y));
        }
    Vec x(n, 0.0);
    std::vector<double> hist;
    const int iters = cg(A, b, x, 1e-10, 5000, &hist);

    double res = 0.0, disc_err = 0.0;
    Vec Ax = A.apply(x);
    for (int k = 0; k < n; ++k) {
        res = std::max(res, std::fabs(Ax[k] - b[k]));
        disc_err = std::max(disc_err, std::fabs(x[k] - u_exact[k]));
    }
    const double kappa = A.lambda_max() / A.lambda_min();
    std::printf("2-D Poisson, %dx%d grid (n = %d): CG converged in %d iterations\n", m, m, n, iters);
    std::printf("  kappa(A) = %.1f (~ 4/(pi^2 h^2) = %.1f), sqrt(kappa) = %.1f\n", kappa,
                4.0 / (M_PI * M_PI * A.h * A.h), std::sqrt(kappa));
    std::printf("  max residual %.2e, max error vs exact u = %.2e (stencil is exact for this u)\n", res, disc_err);
    std::printf("  u at centre = %.12f (exact 1/16 = 0.0625)\n", x[(m / 2) * m + m / 2]);

    CHECK_LESS(res, 1e-6);
    CHECK_LESS(disc_err, 1e-9);
    CHECK_LESS(static_cast<double>(iters), 3.0 * std::sqrt(kappa) + 20);  // O(sqrt kappa) iterations
    CHECK_LESS(10.0, static_cast<double>(iters));                         // and not trivially few
    CHECK_NEAR(kappa, 4.0 / (M_PI * M_PI * A.h * A.h), 60.0);
    CHECK_NEAR(x[(m / 2) * m + m / 2], 1.0 / 16.0, 1e-9);
    // monotone decrease of the A-norm error is guaranteed; the residual isn't,
    // but the last residual must be far below the first
    CHECK_LESS(hist.back() / hist.front(), 1e-9);
    return check::summary("cg");
}
