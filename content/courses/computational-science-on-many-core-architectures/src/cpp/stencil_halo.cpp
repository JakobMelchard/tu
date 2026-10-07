// 2-D Jacobi for the Laplace equation: naive sweep, a blocked sweep that stages
// each tile plus its one-cell halo in a local buffer (the GPU shared-memory
// pattern), and a strip decomposition with explicit halo exchange (the
// multi-GPU / MPI pattern). Mirrors src/cuda/stencil.cu. Notes 03 and 04.
//
// Grid: (n+2) x (n+2) doubles, row-major; row/column 0 and n+1 are the halo
// holding Dirichlet data. One sweep: u'_{ij} = (u_{i-1,j}+u_{i+1,j}+u_{i,j-1}+u_{i,j+1})/4.
// Model traffic per lattice-site update (LUP): 8 B read + 8 B write if the
// three rows i-1, i, i+1 stay in cache ("layer condition"), +8 B write-allocate.
#include "common.hpp"

using mc::Mode;

namespace {

struct Grid {
    int n;
    std::vector<double> v;
    explicit Grid(int n_) : n(n_), v(size_t(n_ + 2) * (n_ + 2), 0.0) {}
    double& at(int i, int j) { return v[size_t(i) * (n + 2) + j]; }
    double at(int i, int j) const { return v[size_t(i) * (n + 2) + j]; }
};

inline double upd(double n, double s, double w, double e) { return 0.25 * (((n + s) + w) + e); }

void sweep_naive(const Grid& u, Grid& w) {
    const int n = u.n;
#pragma omp parallel for schedule(static)
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= n; ++j)
            w.at(i, j) = upd(u.at(i - 1, j), u.at(i + 1, j), u.at(i, j - 1), u.at(i, j + 1));
}

template <int TB>
void sweep_blocked(const Grid& u, Grid& w) {
    const int n = u.n, nb = (n + TB - 1) / TB;
#pragma omp parallel for collapse(2) schedule(static)
    for (int bi = 0; bi < nb; ++bi)
        for (int bj = 0; bj < nb; ++bj) {
            double s[TB + 2][TB + 2];  // tile + halo: (TB+2)^2 loads for TB^2 updates
            int i0 = bi * TB, j0 = bj * TB;
            int hi = std::min(TB, n - i0), hj = std::min(TB, n - j0);
            for (int i = 0; i < hi + 2; ++i)
                for (int j = 0; j < hj + 2; ++j) s[i][j] = u.at(i0 + i, j0 + j);
            for (int i = 1; i <= hi; ++i)
                for (int j = 1; j <= hj; ++j)
                    w.at(i0 + i, j0 + j) = upd(s[i - 1][j], s[i + 1][j], s[i][j - 1], s[i][j + 1]);
        }
}

// P horizontal strips, each with its own array and one ghost row above/below.
// Per iteration: (1) exchange ghost rows with the neighbours, (2) local sweep.
struct Strips {
    int n, P;
    std::vector<int> lo, rows;              // global first interior row, row count
    std::vector<std::vector<double>> a, b;  // (rows+2) x (n+2) each
    Strips(const Grid& g, int P_) : n(g.n), P(P_), lo(P_), rows(P_), a(P_), b(P_) {
        for (int p = 0; p < P; ++p) {
            lo[p] = 1 + n * p / P;
            rows[p] = n * (p + 1) / P - n * p / P;
            a[p].assign(size_t(rows[p] + 2) * (n + 2), 0.0);
            for (int r = 0; r < rows[p] + 2; ++r)  // copy incl. ghost rows and side halo
                for (int j = 0; j < n + 2; ++j) a[p][size_t(r) * (n + 2) + j] = g.at(lo[p] - 1 + r, j);
            b[p] = a[p];
        }
    }
    void exchange() {
        const size_t W = n + 2;
        for (int p = 0; p + 1 < P; ++p) {  // my last interior row -> neighbour's top ghost, and back
            std::copy_n(&a[p][size_t(rows[p]) * W], W, &a[p + 1][0]);
            std::copy_n(&a[p + 1][W], W, &a[p][size_t(rows[p] + 1) * W]);
        }
    }
    void iterate() {
        exchange();
        const size_t W = n + 2;
#pragma omp parallel for schedule(static)
        for (int p = 0; p < P; ++p) {
            for (int r = 1; r <= rows[p]; ++r)
                for (int j = 1; j <= n; ++j)
                    b[p][r * W + j] = upd(a[p][(r - 1) * W + j], a[p][(r + 1) * W + j],
                                          a[p][r * W + j - 1], a[p][r * W + j + 1]);
            std::swap(a[p], b[p]);
        }
    }
    void gather(Grid& g) const {
        for (int p = 0; p < P; ++p)
            for (int r = 1; r <= rows[p]; ++r)
                for (int j = 1; j <= n; ++j) g.at(lo[p] - 1 + r, j) = a[p][size_t(r) * (n + 2) + j];
    }
};

void set_harmonic_boundary(Grid& g) {  // u = x^2 - y^2 on [0,1]^2 (discrete-harmonic)
    const int n = g.n;
    const double h = 1.0 / (n + 1);
    for (int i = 0; i <= n + 1; ++i)
        for (int j = 0; j <= n + 1; ++j)
            if (i == 0 || j == 0 || i == n + 1 || j == n + 1) g.at(i, j) = (i * h) * (i * h) - (j * h) * (j * h);
}

template <class Sweep>
Grid iterate(Grid u, int iters, Sweep sweep) {
    Grid w = u;
    for (int k = 0; k < iters; ++k) { sweep(u, w); std::swap(u, w); }
    return u;
}

int run_test() {
    std::printf("stencil_halo --test\n");
    const int n = 67;  // not a multiple of the tile size
    Grid u0(n);
    mc::Rng r(11);
    for (auto& x : u0.v) x = r.uniform();
    Grid a = iterate(u0, 50, sweep_naive);
    Grid b = iterate(u0, 50, sweep_blocked<16>);
    Strips s(u0, 5);
    for (int k = 0; k < 50; ++k) s.iterate();
    Grid c = u0;
    s.gather(c);
    mc::check(a.v == b.v, "blocked(16) == naive after 50 sweeps, bitwise (n = 67)");
    mc::check(a.v == c.v, "5 strips with halo exchange == global sweep after 50 sweeps, bitwise");

    Grid h(16);
    set_harmonic_boundary(h);
    const double hh = 1.0 / 17;
    Grid exact = h;
    for (int i = 1; i <= 16; ++i)
        for (int j = 1; j <= 16; ++j) exact.at(i, j) = (i * hh) * (i * hh) - (j * hh) * (j * hh);
    Grid one = iterate(exact, 1, sweep_naive);
    mc::check(mc::max_abs_diff(one.v, exact.v) < 1e-14,
              "x^2 - y^2 is a fixed point of the sweep (5-point Laplacian exact for quadratics)");
    // Jacobi error contracts by rho = cos(pi h) per sweep: 1500 sweeps -> rho^1500 ~ 1e-11
    Grid conv = iterate(h, 1500, sweep_blocked<8>);
    double err = mc::max_abs_diff(conv.v, exact.v);
    std::printf("  n = 16 from zero interior: max error after 1500 sweeps = %.2e (rho = %.4f)\n", err,
                std::cos(M_PI / 17));
    mc::check(err < 1e-9, "Jacobi converges to the discrete-harmonic solution (< 1e-9)");
    return mc::finish();
}

void run(bool bench) {
    const int n = bench ? 4094 : 2046, iters = bench ? 20 : 10;
    Grid u(n), w(n);
    mc::Rng r(1);
    for (auto& x : u.v) x = r.uniform();
    w = u;
    const double lups = double(n) * n;
    std::printf("Jacobi sweep, n = %d (%.0f MB per grid), %d threads, best of %d\n", n,
                8e-6 * u.v.size(), omp_get_max_threads(), iters);
    mc::print_load();
    auto row = [&](const char* name, double t) {
        std::printf("  %-18s %9.3f ms %9.0f MLUP/s %8.1f GB/s (16 B/LUP) %8.1f GB/s (24 B/LUP)\n", name,
                    t * 1e3, lups / t * 1e-6, 16 * lups / t * 1e-9, 24 * lups / t * 1e-9);
    };
    row("naive", mc::time_min([&] { sweep_naive(u, w); }, iters));
    row("blocked TB=32", mc::time_min([&] { sweep_blocked<32>(u, w); }, iters));
    row("blocked TB=128", mc::time_min([&] { sweep_blocked<128>(u, w); }, iters));
    Strips s(u, omp_get_max_threads());
    row("strips + exchange", mc::time_min([&] { s.iterate(); }, iters));
    std::printf("  halo overhead of staging: (TB+2)^2/TB^2 = %.3f (TB=32), %.3f (TB=16 on a GPU)\n",
                34.0 * 34 / (32 * 32), 18.0 * 18 / (16 * 16));
}

}  // namespace

int main(int argc, char** argv) {
    Mode m = mc::parse_mode(argc, argv);
    if (m == Mode::test) return run_test();
    run(m == Mode::bench);
    return 0;
}
