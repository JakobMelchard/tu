// fd_poisson1d.cpp -- finite differences for -u'' = f on (0,1) (topics 03/04/05).
//
//   grid x_i = i h, h = 1/N, unknowns u_1..u_{N-1}; second-order central stencil
//     (-u_{i-1} + 2 u_i - u_{i+1}) / h^2 = f_i,
//   Dirichlet values u_0, u_N move to the right-hand side of rows 1 and N-1.
//   The tridiagonal SPD system is solved (a) with the Thomas algorithm, O(N),
//   and (b) matrix-free with conjugate gradients. The convergence table shows
//   max-norm error ~ h^2 (order 2) and CG iterations ~ N (kappa ~ N^2).
//
// Sources: discretisation, eigenvalues and the O(h^2) error bound [S23 §2.9-2.10];
// Thomas = LU without pivoting for a tridiagonal SPD matrix; CG [S15].
//
// Usage: ./fd_poisson1d [--test | --bench]
#include "common.hpp"
#include <vector>

const double PI = 3.14159265358979323846;
static double u_exact(double x) { return std::sin(PI * x) + x; }     // u(0)=0, u(1)=1
static double f_rhs(double x) { return PI * PI * std::sin(PI * x); }  // -u''

// Thomas algorithm for a tridiagonal system (sub, diag, sup, rhs), overwrites rhs with solution.
static void thomas(std::vector<double> sub, std::vector<double> diag, std::vector<double> sup,
                   std::vector<double>& rhs) {
    const std::size_t m = diag.size();
    for (std::size_t i = 1; i < m; ++i) {           // forward elimination
        double w = sub[i] / diag[i - 1];
        diag[i] -= w * sup[i - 1];
        rhs[i] -= w * rhs[i - 1];
    }
    rhs[m - 1] /= diag[m - 1];                        // back substitution
    for (std::size_t i = m - 1; i-- > 0;) rhs[i] = (rhs[i] - sup[i] * rhs[i + 1]) / diag[i];
}

// y = A x for the (N-1)x(N-1) matrix (1/h^2) tridiag(-1, 2, -1).
static void apply_A(const std::vector<double>& x, std::vector<double>& y, double h) {
    const std::size_t m = x.size();
    for (std::size_t i = 0; i < m; ++i) {
        double s = 2 * x[i];
        if (i > 0) s -= x[i - 1];
        if (i + 1 < m) s -= x[i + 1];
        y[i] = s / (h * h);
    }
}

static double dot(const std::vector<double>& a, const std::vector<double>& b) {
    double s = 0;
    for (std::size_t i = 0; i < a.size(); ++i) s += a[i] * b[i];
    return s;
}

// Conjugate gradients, matrix-free; returns iterations used.
static int cg(const std::vector<double>& b, std::vector<double>& x, double h, double tol, int maxit) {
    const std::size_t m = b.size();
    std::vector<double> r(m), p(m), Ap(m);
    apply_A(x, Ap, h);
    for (std::size_t i = 0; i < m; ++i) r[i] = b[i] - Ap[i];
    p = r;
    double rr = dot(r, r);
    const double stop = tol * tol * dot(b, b);
    int it = 0;
    for (; it < maxit && rr > stop; ++it) {
        apply_A(p, Ap, h);
        double alpha = rr / dot(p, Ap);
        for (std::size_t i = 0; i < m; ++i) { x[i] += alpha * p[i]; r[i] -= alpha * Ap[i]; }
        double rr_new = dot(r, r);
        double beta = rr_new / rr;
        rr = rr_new;
        for (std::size_t i = 0; i < m; ++i) p[i] = r[i] + beta * p[i];
    }
    return it;
}

struct Result { double err_thomas, err_cg; int cg_iters; };

static Result solve(std::size_t N) {
    const double h = 1.0 / N;
    const std::size_t m = N - 1;
    std::vector<double> rhs(m);
    for (std::size_t i = 0; i < m; ++i) rhs[i] = f_rhs((i + 1) * h);
    rhs[0] += u_exact(0.0) / (h * h);      // Dirichlet data enters the rhs
    rhs[m - 1] += u_exact(1.0) / (h * h);

    std::vector<double> sub(m, -1 / (h * h)), diag(m, 2 / (h * h)), sup(m, -1 / (h * h));
    std::vector<double> u_t = rhs;
    thomas(sub, diag, sup, u_t);

    std::vector<double> u_c(m, 0.0);
    int iters = cg(rhs, u_c, h, 1e-12, 10 * static_cast<int>(N) + 100);

    double e_t = 0, e_c = 0;
    for (std::size_t i = 0; i < m; ++i) {
        double ue = u_exact((i + 1) * h);
        e_t = std::max(e_t, std::fabs(u_t[i] - ue));
        e_c = std::max(e_c, std::fabs(u_c[i] - ue));
    }
    return {e_t, e_c, iters};
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    std::printf("%6s %12s %8s %12s %8s\n", "N", "err Thomas", "order", "err CG", "CG its");
    double prev = 0;
    std::vector<double> orders;
    for (std::size_t N : {8u, 16u, 32u, 64u, 128u, 256u, 512u}) {
        Result r = solve(N);
        double order = prev > 0 ? std::log2(prev / r.err_thomas) : 0.0;
        if (prev > 0) orders.push_back(order);
        std::printf("%6zu %12.3e %8.3f %12.3e %8d\n", N, r.err_thomas, order, r.err_cg, r.cg_iters);
        if (mode == "test") CHECK(std::fabs(r.err_thomas - r.err_cg) < 1e-7);   // same discrete solution
        prev = r.err_thomas;
    }
    if (mode == "test") {
        for (double o : orders) CHECK(o > 1.9 && o < 2.1);
        std::puts("fd_poisson1d: ok");
    }
    return 0;
}
