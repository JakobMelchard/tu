// csr.cpp -- compressed sparse row storage and iterative solvers (topic 05).
//
//   CSR: val[] and col[] hold the nnz entries row by row, row_ptr[i]..row_ptr[i+1]
//   delimits row i. SpMV costs O(nnz) and 16 bytes per nonzero instead of 8 n^2.
//   Solvers on the 2D Poisson system A u = f (5-point stencil, (N-1)^2 unknowns):
//     Jacobi, Gauss-Seidel, SOR (omega_opt = 2/(1+sin(pi h))), CG, Jacobi-PCG.
//   Iteration counts: Jacobi ~ N^2, GS ~ N^2/2, SOR ~ N, CG ~ N.
//   The test uses the manufactured solution u = x(1-x)y(1-y)e^{xy}, which is not
//   an eigenvector of A (sin(pi x) sin(pi y) would let CG finish in one step).
//
// Sources: CSR storage [S22 §3.4]; splittings and rho(Jacobi) = cos(pi h),
// omega_opt [S22 ch. 4]; CG [S15], its kappa bound [S22 §6.11].
//
// Usage: ./csr [--test | --bench]
#include "common.hpp"
#include <random>
#include <vector>

struct CSR {
    std::size_t n = 0;
    std::vector<std::size_t> row_ptr, col;
    std::vector<double> val;

    void spmv(const std::vector<double>& x, std::vector<double>& y) const {
        for (std::size_t i = 0; i < n; ++i) {
            double s = 0;
            for (std::size_t k = row_ptr[i]; k < row_ptr[i + 1]; ++k) s += val[k] * x[col[k]];
            y[i] = s;
        }
    }
    double diag(std::size_t i) const {
        for (std::size_t k = row_ptr[i]; k < row_ptr[i + 1]; ++k) if (col[k] == i) return val[k];
        return 0.0;
    }
    std::size_t nnz() const { return val.size(); }
};

// 2D Poisson, -Laplace, interior unknown (i,j) -> k = (i-1)*(N-1) + (j-1), rows sorted by column.
static CSR poisson2d(std::size_t N) {
    const std::size_t m = N - 1;
    const double ih2 = static_cast<double>(N) * N;
    CSR A; A.n = m * m; A.row_ptr.push_back(0);
    for (std::size_t i = 1; i <= m; ++i)
        for (std::size_t j = 1; j <= m; ++j) {
            auto push = [&](std::size_t ii, std::size_t jj, double v) {
                A.col.push_back((ii - 1) * m + (jj - 1)); A.val.push_back(v * ih2);
            };
            if (i > 1) push(i - 1, j, -1);
            if (j > 1) push(i, j - 1, -1);
            push(i, j, 4);
            if (j < m) push(i, j + 1, -1);
            if (i < m) push(i + 1, j, -1);
            A.row_ptr.push_back(A.col.size());
        }
    return A;
}

static double norm2(const std::vector<double>& v) { double s = 0; for (double x : v) s += x * x; return std::sqrt(s); }
static double dot(const std::vector<double>& a, const std::vector<double>& b) { double s = 0; for (std::size_t i = 0; i < a.size(); ++i) s += a[i] * b[i]; return s; }
static double rel_residual(const CSR& A, const std::vector<double>& b, const std::vector<double>& x) {
    std::vector<double> r(A.n); A.spmv(x, r);
    for (std::size_t i = 0; i < A.n; ++i) r[i] = b[i] - r[i];
    return norm2(r) / norm2(b);
}

static int jacobi(const CSR& A, const std::vector<double>& b, std::vector<double>& x, double tol, int maxit) {
    std::vector<double> xn(A.n);
    for (int it = 1; it <= maxit; ++it) {
        for (std::size_t i = 0; i < A.n; ++i) {
            double s = b[i], d = 0;
            for (std::size_t k = A.row_ptr[i]; k < A.row_ptr[i + 1]; ++k)
                if (A.col[k] == i) d = A.val[k]; else s -= A.val[k] * x[A.col[k]];
            xn[i] = s / d;
        }
        x.swap(xn);
        if (rel_residual(A, b, x) < tol) return it;
    }
    return maxit;
}

// omega = 1 gives Gauss-Seidel; in-place sweep uses already updated x_j for j < i.
static int sor(const CSR& A, const std::vector<double>& b, std::vector<double>& x, double omega, double tol, int maxit) {
    for (int it = 1; it <= maxit; ++it) {
        for (std::size_t i = 0; i < A.n; ++i) {
            double s = b[i], d = 0;
            for (std::size_t k = A.row_ptr[i]; k < A.row_ptr[i + 1]; ++k)
                if (A.col[k] == i) d = A.val[k]; else s -= A.val[k] * x[A.col[k]];
            x[i] = (1 - omega) * x[i] + omega * s / d;
        }
        if (rel_residual(A, b, x) < tol) return it;
    }
    return maxit;
}

// Preconditioned CG with M = diag(A) if precond, else plain CG.
static int cg(const CSR& A, const std::vector<double>& b, std::vector<double>& x, double tol, int maxit, bool precond) {
    const std::size_t n = A.n;
    std::vector<double> r(n), z(n), p(n), Ap(n), invd(n, 1.0);
    if (precond) for (std::size_t i = 0; i < n; ++i) invd[i] = 1.0 / A.diag(i);
    A.spmv(x, Ap);
    for (std::size_t i = 0; i < n; ++i) { r[i] = b[i] - Ap[i]; z[i] = invd[i] * r[i]; }
    p = z;
    double rz = dot(r, z), bn = norm2(b);
    for (int it = 1; it <= maxit; ++it) {
        A.spmv(p, Ap);
        double alpha = rz / dot(p, Ap);
        for (std::size_t i = 0; i < n; ++i) { x[i] += alpha * p[i]; r[i] -= alpha * Ap[i]; }
        if (norm2(r) / bn < tol) return it;
        for (std::size_t i = 0; i < n; ++i) z[i] = invd[i] * r[i];
        double rz_new = dot(r, z);
        for (std::size_t i = 0; i < n; ++i) p[i] = z[i] + (rz_new / rz) * p[i];
        rz = rz_new;
    }
    return maxit;
}

const double PI = 3.14159265358979323846;

// Manufactured solution u = x(1-x) y(1-y) e^{xy}: vanishes on the boundary and is
// not an eigenfunction of the Laplacian (an eigenfunction would make CG converge
// in one step and hide the real iteration counts).
static double u_exact(double x, double y) { return x * (1 - x) * y * (1 - y) * std::exp(x * y); }
static double f_rhs(double x, double y) {
    const double g = std::exp(x * y), p = x * (1 - x) * y * (1 - y);
    const double px = (1 - 2 * x) * y * (1 - y), py = (1 - 2 * y) * x * (1 - x);
    const double uxx = g * (-2 * y * (1 - y) + 2 * px * y + p * y * y);
    const double uyy = g * (-2 * x * (1 - x) + 2 * py * x + p * x * x);
    return -(uxx + uyy);
}

static void poisson_table(std::size_t N, bool test) {
    CSR A = poisson2d(N);
    const double h = 1.0 / N;
    std::vector<double> b(A.n), ue(A.n);
    for (std::size_t i = 1; i < N; ++i)
        for (std::size_t j = 1; j < N; ++j) {
            std::size_t k = (i - 1) * (N - 1) + (j - 1);
            ue[k] = u_exact(i * h, j * h);
            b[k] = f_rhs(i * h, j * h);
        }
    std::printf("2D Poisson N=%zu: n = %zu unknowns, nnz = %zu; CSR %.2f MB vs dense %.2f MB\n", N, A.n, A.nnz(),
                (A.nnz() * 16.0 + (A.n + 1) * 8.0) / 1e6, A.n * A.n * 8.0 / 1e6);
    const double tol = 1e-8;
    const int maxit = 100000;
    const double omega = 2.0 / (1.0 + std::sin(PI * h));
    struct Row { const char* name; int its; double sec; double err; };
    std::vector<Row> rows;
    auto record = [&](const char* name, auto&& solver) {
        std::vector<double> x(A.n, 0.0);
        Timer t; int its = solver(x); double sec = t.seconds();
        double err = 0; for (std::size_t k = 0; k < A.n; ++k) err = std::max(err, std::fabs(x[k] - ue[k]));
        rows.push_back({name, its, sec, err});
        if (test) { CHECK(rel_residual(A, b, x) < tol); CHECK(err < 1e-3); }
    };
    record("Jacobi",       [&](auto& x) { return jacobi(A, b, x, tol, maxit); });
    record("Gauss-Seidel", [&](auto& x) { return sor(A, b, x, 1.0, tol, maxit); });
    record("SOR w_opt",    [&](auto& x) { return sor(A, b, x, omega, tol, maxit); });
    record("CG",           [&](auto& x) { return cg(A, b, x, tol, maxit, false); });
    std::printf("%-14s %8s %10s %12s\n", "solver", "iters", "time[s]", "max|u-u_ex|");
    for (auto& r : rows) std::printf("%-14s %8d %10.4f %12.3e\n", r.name, r.its, r.sec, r.err);
    if (test) { CHECK(rows[0].its > rows[1].its); CHECK(rows[1].its > rows[2].its); CHECK(rows[3].its < rows[1].its); }
}

// Preconditioning demo: B = D A D with a wildly varying diagonal D is still SPD but
// badly conditioned; Jacobi-PCG undoes the scaling and recovers the CG count of A.
static void precond_demo(std::size_t N, bool test) {
    CSR A = poisson2d(N);
    std::vector<double> d(A.n);
    for (std::size_t i = 0; i < A.n; ++i) d[i] = std::pow(10.0, 3.0 * (i % 7) / 6.0);   // 1 .. 1000
    for (std::size_t i = 0; i < A.n; ++i)
        for (std::size_t k = A.row_ptr[i]; k < A.row_ptr[i + 1]; ++k) A.val[k] *= d[i] * d[A.col[k]];
    std::vector<double> b(A.n, 1.0), x1(A.n, 0.0), x2(A.n, 0.0);
    int it_cg = cg(A, b, x1, 1e-8, 100000, false);
    int it_pcg = cg(A, b, x2, 1e-8, 100000, true);
    std::printf("scaled system D A D: CG %d iterations, Jacobi-PCG %d iterations\n", it_cg, it_pcg);
    if (test) { CHECK(it_pcg < it_cg); double dd = 0; for (std::size_t i = 0; i < A.n; ++i) dd = std::max(dd, std::fabs(x1[i] - x2[i])); CHECK(dd < 1e-5); }
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    if (mode == "test") {
        // SpMV against a dense reference on a small random sparse matrix
        std::mt19937 rng(1); std::uniform_real_distribution<double> U(-1, 1);
        const std::size_t n = 30; std::vector<double> dense(n * n, 0.0); CSR S; S.n = n; S.row_ptr.push_back(0);
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = 0; j < n; ++j) if (rng() % 4 == 0 || i == j) { dense[i * n + j] = U(rng); S.col.push_back(j); S.val.push_back(dense[i * n + j]); }
            S.row_ptr.push_back(S.col.size());
        }
        std::vector<double> x(n), y(n), yd(n, 0.0); for (auto& v : x) v = U(rng);
        S.spmv(x, y);
        for (std::size_t i = 0; i < n; ++i) for (std::size_t j = 0; j < n; ++j) yd[i] += dense[i * n + j] * x[j];
        for (std::size_t i = 0; i < n; ++i) CHECK(close(y[i], yd[i], 1e-12, 1e-12));
        poisson_table(16, true);
        precond_demo(16, true);
        std::puts("csr: ok");
    } else if (mode == "bench") {
        poisson_table(64, false);
        poisson_table(128, false);
        precond_demo(64, false);
    } else {
        poisson_table(32, false);
        precond_demo(32, false);
    }
    return 0;
}
