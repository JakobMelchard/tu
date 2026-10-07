// STREAM-style bandwidth measurement, a roofline point, and an alpha-beta
// (latency-bandwidth) fit of T(N) for the vector addition x = y + z.
// Mirrors src/cuda/vector_add.cu on the CPU. Notes 02 and 03.
//
// Byte counting follows STREAM [S13]: bytes the program asks for (copy/scale 16,
// add/triad 24 per element). Write-allocate traffic (one extra read of the
// destination line) is NOT counted; with it the triad moves 32 B/element.
#include "common.hpp"

using mc::Mode;

namespace {

struct Arrays {
    std::vector<double> a, b, c;
    explicit Arrays(size_t n) : a(n), b(n), c(n) {
        // first touch in the same static pattern the kernels use
#pragma omp parallel for schedule(static)
        for (size_t i = 0; i < n; ++i) { a[i] = 0.0; b[i] = 2.0; c[i] = 1.0; }
    }
};

// The four STREAM kernels. schedule(static) so every thread touches the same
// pages in every kernel.
void copy(Arrays& x, size_t n) {
#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) x.a[i] = x.b[i];
}
void scale(Arrays& x, size_t n, double s) {
#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) x.a[i] = s * x.b[i];
}
void add(Arrays& x, size_t n) {
#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) x.a[i] = x.b[i] + x.c[i];
}
void triad(Arrays& x, size_t n, double s) {
#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) x.a[i] = x.b[i] + s * x.c[i];
}

// GB/s of one kernel at the current thread count.
template <class F>
double gbs(F&& f, double bytes, int reps = 10) {
    return bytes / mc::time_min(f, reps) * 1e-9;
}

// Least-squares fit of T = alpha + bytes/beta, i.e. linear in bytes.
struct AlphaBeta { double alpha, beta; };
AlphaBeta fit(const std::vector<double>& bytes, const std::vector<double>& t) {
    double n = bytes.size(), sx = 0, sy = 0, sxx = 0, sxy = 0;
    for (size_t i = 0; i < bytes.size(); ++i) {
        sx += bytes[i]; sy += t[i]; sxx += bytes[i] * bytes[i]; sxy += bytes[i] * t[i];
    }
    double slope = (n * sxy - sx * sy) / (n * sxx - sx * sx);
    return {(sy - slope * sx) / n, 1.0 / slope};
}

// Time an empty parallel-for: the fork/join latency of one "kernel launch".
double empty_region_s() {
    volatile double sink = 0;
    return mc::time_min([&] {
#pragma omp parallel for schedule(static)
        for (int i = 0; i < 64; ++i) sink = sink + 0.0;
    }, 200);
}

// T(N) for x = y + z over N = 2^10 .. 2^maxlog, printed as a table.
// alpha := T at the smallest N (pure overhead: fork/join + barrier);
// beta  := 1/slope of a least-squares line through the DRAM-sized points
// (>= 64 MB of traffic). A free intercept from two noisy DRAM points is
// meaningless (it can come out negative), so it is not used for alpha.
AlphaBeta size_sweep(int maxlog, bool print) {
    size_t nmax = size_t(1) << maxlog;
    Arrays x(nmax);
    std::vector<double> by, tt;
    double alpha = 0;
    if (print) std::printf("  %10s %12s %10s\n", "N", "time [us]", "GB/s");
    for (int lg = 10; lg <= maxlog; lg += (lg < 20 ? 2 : 1)) {
        size_t n = size_t(1) << lg;
        double t = mc::time_min([&] { add(x, n); }, lg < 20 ? 200 : 10);
        double bytes = 24.0 * n;
        if (lg == 10) alpha = t;
        if (print) std::printf("  %10zu %12.2f %10.1f\n", n, t * 1e6, bytes / t * 1e-9);
        if (bytes >= 64e6) { by.push_back(bytes); tt.push_back(t); }
    }
    double beta = by.size() >= 2 ? fit(by, tt).beta : 0;
    return {alpha, beta};
}

int run_test() {
    std::printf("stream_triad --test\n");
    const size_t n = 1 << 20;
    Arrays x(n);
    triad(x, n, 3.0);
    bool ok = true;
    for (size_t i = 0; i < n; ++i) ok &= (x.a[i] == 5.0);
    mc::check(ok, "triad a = b + 3c with b=2, c=1 gives 5 everywhere");
    add(x, n);
    ok = true;
    for (size_t i = 0; i < n; ++i) ok &= (x.a[i] == 3.0);
    mc::check(ok, "add a = b + c gives 3 everywhere");
    double g = gbs([&] { triad(x, n, 3.0); }, 24.0 * n);
    mc::check(g > 1.0 && g < 5000.0, "triad bandwidth in a plausible range (1..5000 GB/s)");
    AlphaBeta ab = fit({1e6, 2e6, 3e6}, {11e-6, 21e-6, 31e-6});
    mc::check(std::fabs(ab.alpha - 1e-6) < 1e-12 && std::fabs(ab.beta - 1e11) < 1e3,
              "alpha-beta fit recovers alpha = 1 us, beta = 100 GB/s from exact data");
    double lat = empty_region_s();
    mc::check(lat > 0 && lat < 1e-3, "empty parallel region costs between 0 and 1 ms");
    return mc::finish();
}

void run(bool bench) {
    const int maxlog = bench ? 25 : 24;
    const size_t n = size_t(1) << maxlog;
    std::printf("STREAM kernels, N = %zu doubles (%.0f MB per array), best of 10\n", n,
                8.0 * n / 1e6);
    Arrays x(n);
    mc::print_load();
    std::printf("  %7s %9s %9s %9s %9s %12s\n", "threads", "copy", "scale", "add", "triad",
                "triad GF/s");
    double best_triad = 0, one_triad = 0;
    for (int p : mc::thread_sweep()) {
        omp_set_num_threads(p);
        double c = gbs([&] { copy(x, n); }, 16.0 * n);
        double s = gbs([&] { scale(x, n, 3.0); }, 16.0 * n);
        double a = gbs([&] { add(x, n); }, 24.0 * n);
        double t = gbs([&] { triad(x, n, 3.0); }, 24.0 * n);
        std::printf("  %7d %9.1f %9.1f %9.1f %9.1f %12.2f\n", p, c, s, a, t, t * 2.0 / 24.0);
        best_triad = std::max(best_triad, t);
        if (p == 1) one_triad = t;
    }
    omp_set_num_threads(omp_get_num_procs());
    std::printf("  (GB/s, STREAM convention; x 32/24 for triad traffic incl. write-allocate)\n");
    std::printf("roofline point, triad: AI = 2/24 = %.4f flop/B -> %.2f GFLOP/s at %.1f GB/s\n",
                2.0 / 24.0, best_triad * 2.0 / 24.0, best_triad);
    std::printf("single-thread triad %.1f GB/s = %.0f %% of the best multi-thread value\n",
                one_triad, 100.0 * one_triad / best_triad);

    double lat = empty_region_s();
    std::printf("\nempty parallel region (%d threads): %.2f us  (the CPU analogue of a kernel launch)\n",
                omp_get_max_threads(), lat * 1e6);
    std::printf("\nalpha-beta model for x = y + z, T(N) = alpha + 24 N / beta:\n");
    AlphaBeta ab = size_sweep(maxlog, true);
    std::printf("  alpha = T(N=1024) = %.2f us, beta = 1/slope on the DRAM points = %.1f GB/s\n",
                ab.alpha * 1e6, ab.beta * 1e-9);
    // Hockney's half-performance length: traffic at which T = 2 alpha
    double half = ab.alpha * ab.beta;
    std::printf("  n_1/2 = alpha * beta = %.0f KB of traffic = %.0f elements per array\n", half / 1e3,
                half / 24.0);
}

}  // namespace

int main(int argc, char** argv) {
    Mode m = mc::parse_mode(argc, argv);
    if (m == Mode::test) return run_test();
    run(m == Mode::bench);
    return 0;
}
