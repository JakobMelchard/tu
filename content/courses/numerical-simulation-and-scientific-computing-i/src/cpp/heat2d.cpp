// heat2d.cpp -- 2D heat equation u_t = alpha (u_xx + u_yy) on the unit square (topic 04).
//
//   Dirichlet u = 0 on the boundary, u(x,y,0) = sin(pi x) sin(pi y), exact solution
//   u = exp(-2 alpha pi^2 t) sin(pi x) sin(pi y). Five-point Laplacian, h = 1/N.
//   explicit Euler : u^{n+1} = u^n + dt alpha L_h u^n,  stable iff r = alpha dt/h^2 <= 1/4
//   implicit Euler : (I - dt alpha L_h) u^{n+1} = u^n,  unconditionally stable, solved by CG
//   The demo runs explicit at r = 0.24 (fine), r = 0.30 (blows up) and implicit at a
//   dt that would be far beyond the explicit limit.
//
// Sources: method of lines and von Neumann analysis [S23 ch. 9-10]; the
// stability/convergence link is the Lax equivalence theorem [S24]; CG [S15].
//
// Usage: ./heat2d [--test | --bench]
#include "common.hpp"
#include <vector>

const double PI = 3.14159265358979323846;
using Field = std::vector<double>;   // (N+1)*(N+1) values incl. boundary, row-major idx = i*(N+1)+j

struct Grid { std::size_t N; double h; std::size_t idx(std::size_t i, std::size_t j) const { return i * (N + 1) + j; } };

static void laplacian(const Grid& g, const Field& u, Field& Lu) {
    const double ih2 = 1.0 / (g.h * g.h);
    std::fill(Lu.begin(), Lu.end(), 0.0);
    for (std::size_t i = 1; i < g.N; ++i)
        for (std::size_t j = 1; j < g.N; ++j)
            Lu[g.idx(i, j)] = ih2 * (u[g.idx(i - 1, j)] + u[g.idx(i + 1, j)] + u[g.idx(i, j - 1)] +
                                     u[g.idx(i, j + 1)] - 4 * u[g.idx(i, j)]);
}

static double dot(const Field& a, const Field& b) {
    double s = 0;
    for (std::size_t i = 0; i < a.size(); ++i) s += a[i] * b[i];
    return s;
}

// CG for (I - c L_h) x = b on the interior (boundary entries stay 0). Returns iterations.
static int cg_implicit(const Grid& g, double c, const Field& b, Field& x, double tol = 1e-10) {
    Field r(b.size()), p(b.size()), Ap(b.size()), Lp(b.size());
    auto apply = [&](const Field& v, Field& out) {
        laplacian(g, v, Lp);
        for (std::size_t k = 0; k < v.size(); ++k) out[k] = v[k] - c * Lp[k];
        for (std::size_t i = 0; i <= g.N; ++i)   // keep boundary rows as identity with zero data
            out[g.idx(i, 0)] = out[g.idx(i, g.N)] = out[g.idx(0, i)] = out[g.idx(g.N, i)] = 0.0;
    };
    apply(x, Ap);
    for (std::size_t k = 0; k < b.size(); ++k) r[k] = b[k] - Ap[k];
    p = r;
    double rr = dot(r, r), stop = tol * tol * dot(b, b);
    int it = 0;
    for (; it < 10000 && rr > stop; ++it) {
        apply(p, Ap);
        double alpha = rr / dot(p, Ap);
        for (std::size_t k = 0; k < b.size(); ++k) { x[k] += alpha * p[k]; r[k] -= alpha * Ap[k]; }
        double rr_new = dot(r, r);
        for (std::size_t k = 0; k < b.size(); ++k) p[k] = r[k] + (rr_new / rr) * p[k];
        rr = rr_new;
    }
    return it;
}

static Field initial(const Grid& g) {
    Field u((g.N + 1) * (g.N + 1), 0.0);
    for (std::size_t i = 1; i < g.N; ++i)
        for (std::size_t j = 1; j < g.N; ++j) u[g.idx(i, j)] = std::sin(PI * i * g.h) * std::sin(PI * j * g.h);
    return u;
}

struct Outcome { double max_abs, max_err; int steps; double seconds; int cg_iters_total; };

static Outcome max_err(const Grid& g, const Field& u, double alpha, double T) {
    double ma = 0, me = 0, decay = std::exp(-2 * alpha * PI * PI * T);
    for (std::size_t i = 0; i <= g.N; ++i)
        for (std::size_t j = 0; j <= g.N; ++j) {
            double ue = decay * std::sin(PI * i * g.h) * std::sin(PI * j * g.h);
            ma = std::max(ma, std::fabs(u[g.idx(i, j)]));
            me = std::max(me, std::fabs(u[g.idx(i, j)] - ue));
        }
    return {ma, me, 0, 0, 0};
}

static Outcome run_explicit(std::size_t N, double alpha, double r, double T) {
    Grid g{N, 1.0 / N};
    double dt = r * g.h * g.h / alpha;
    int steps = static_cast<int>(std::ceil(T / dt));
    dt = T / steps;                                  // land exactly on T
    Field u = initial(g), Lu(u.size());
    Timer t;
    for (int s = 0; s < steps; ++s) {
        laplacian(g, u, Lu);
        for (std::size_t k = 0; k < u.size(); ++k) u[k] += dt * alpha * Lu[k];
    }
    Outcome o = max_err(g, u, alpha, T);
    o.steps = steps; o.seconds = t.seconds();
    return o;
}

static Outcome run_implicit(std::size_t N, double alpha, double dt, double T) {
    Grid g{N, 1.0 / N};
    int steps = static_cast<int>(std::ceil(T / dt));
    dt = T / steps;
    Field u = initial(g), rhs(u.size());
    int its = 0;
    Timer t;
    for (int s = 0; s < steps; ++s) {
        rhs = u;
        its += cg_implicit(g, dt * alpha, rhs, u);   // warm start from u^n
    }
    Outcome o = max_err(g, u, alpha, T);
    o.steps = steps; o.seconds = t.seconds(); o.cg_iters_total = its;
    return o;
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    const std::size_t N = mode == "bench" ? 128 : 32;
    const double alpha = 1.0, T = 0.05;
    const double h = 1.0 / N, dt_max = h * h / (4 * alpha);
    std::printf("N = %zu, h = %.4f, alpha = %g, T = %g, explicit limit dt <= h^2/(4 alpha) = %.3e\n",
                N, h, alpha, T, dt_max);
    std::printf("%-22s %8s %10s %12s %12s %8s\n", "scheme", "r", "steps", "max|u|", "max err", "time[s]");

    Outcome e1 = run_explicit(N, alpha, 0.24, T);
    std::printf("%-22s %8.2f %10d %12.4e %12.4e %8.3f\n", "explicit (stable)", 0.24, e1.steps, e1.max_abs, e1.max_err, e1.seconds);
    Outcome e2 = run_explicit(N, alpha, 0.30, T);
    std::printf("%-22s %8.2f %10d %12.4e %12.4e %8.3f\n", "explicit (unstable)", 0.30, e2.steps, e2.max_abs, e2.max_err, e2.seconds);
    for (double dt : {dt_max, 4 * dt_max, 16 * dt_max}) {
        Outcome im = run_implicit(N, alpha, dt, T);
        std::printf("%-22s %8.2f %10d %12.4e %12.4e %8.3f   (CG its/step %.1f)\n", "implicit Euler",
                    alpha * dt / (h * h), im.steps, im.max_abs, im.max_err, im.seconds,
                    static_cast<double>(im.cg_iters_total) / im.steps);
        if (mode == "test") CHECK(im.max_err < 2e-2);
    }
    if (mode == "test") {
        CHECK(e1.max_err < 2e-3);
        CHECK(!std::isfinite(e2.max_abs) || e2.max_abs > 1e3);
        std::puts("heat2d: ok");
    }
    return 0;
}
