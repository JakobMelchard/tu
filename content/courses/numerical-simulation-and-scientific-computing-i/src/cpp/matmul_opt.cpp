// matmul_opt.cpp -- serial optimisation of dense matrix multiply (topic 02).
//
//   naive (i,j,k): inner loop walks B down a column -> stride n, cache misses
//   ikj          : inner loop over j is contiguous in B and C -> vectorisable
//   transposed   : C[i][j] = dot(A[i,:], Bt[j,:]), both rows contiguous
//   blocked      : ikj inside cache-sized tiles so the A/B/C tiles stay in L1/L2
// All variants must give the same C; timing shows the payoff of memory-friendly
// loop order. FLOP count is 2 n^3 for every variant, so GFLOP/s compares fairly.
// Each variant is timed best-of-3 (the first call doubles as the warm-up), the
// protocol of note 02 [S35].
//
// --bench adds a block-size sweep at n = 2048 against ikj. Model for why blocking
// may NOT pay: ikj streams all of B once per row i, 8 bytes per 2 flops, i.e.
// 4 B/flop. At ~14 GFLOP/s that is ~57 GB/s, below the ~107 GB/s one core
// streams (cache_bench triad), so ikj is not bandwidth bound and one level of
// tiling only adds loop overhead. Tiling pays once SIMD and a register
// micro-kernel make the kernel fast enough to outrun memory [S31] [S8].
//
// Sources: loop orders and tiling [S8] (Performance / Caches), two-level GEMM
// [S31], arithmetic intensity [S16], benchmarking protocol [S35].
//
// Usage: ./matmul_opt [--test | --bench]
#include "common.hpp"
#include <algorithm>
#include <random>
#include <vector>

using Mat = std::vector<double>;   // row-major n x n

static void matmul_naive(const Mat& a, const Mat& b, Mat& c, std::size_t n) {
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t j = 0; j < n; ++j) {
            double s = 0;
            for (std::size_t k = 0; k < n; ++k) s += a[i * n + k] * b[k * n + j];
            c[i * n + j] = s;
        }
}

static void matmul_ikj(const Mat& a, const Mat& b, Mat& c, std::size_t n) {
    std::fill(c.begin(), c.end(), 0.0);
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t k = 0; k < n; ++k) {
            const double aik = a[i * n + k];
            const double* brow = &b[k * n];
            double* crow = &c[i * n];
            for (std::size_t j = 0; j < n; ++j) crow[j] += aik * brow[j];
        }
}

static void matmul_transposed(const Mat& a, const Mat& b, Mat& c, std::size_t n) {
    Mat bt(n * n);
    for (std::size_t k = 0; k < n; ++k)
        for (std::size_t j = 0; j < n; ++j) bt[j * n + k] = b[k * n + j];
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t j = 0; j < n; ++j) {
            double s = 0;
            const double* ar = &a[i * n];
            const double* br = &bt[j * n];
            for (std::size_t k = 0; k < n; ++k) s += ar[k] * br[k];
            c[i * n + j] = s;
        }
}

static void matmul_blocked(const Mat& a, const Mat& b, Mat& c, std::size_t n, std::size_t bs = 64) {
    std::fill(c.begin(), c.end(), 0.0);
    for (std::size_t i0 = 0; i0 < n; i0 += bs)
        for (std::size_t k0 = 0; k0 < n; k0 += bs)
            for (std::size_t j0 = 0; j0 < n; j0 += bs) {
                const std::size_t i1 = std::min(i0 + bs, n), k1 = std::min(k0 + bs, n), j1 = std::min(j0 + bs, n);
                for (std::size_t i = i0; i < i1; ++i)
                    for (std::size_t k = k0; k < k1; ++k) {
                        const double aik = a[i * n + k];
                        for (std::size_t j = j0; j < j1; ++j) c[i * n + j] += aik * b[k * n + j];
                    }
            }
}

static double max_diff(const Mat& x, const Mat& y) {
    double d = 0;
    for (std::size_t i = 0; i < x.size(); ++i) d = std::max(d, std::fabs(x[i] - y[i]));
    return d;
}

using Kernel = void (*)(const Mat&, const Mat&, Mat&, std::size_t);
static void blocked64(const Mat& a, const Mat& b, Mat& c, std::size_t n) { matmul_blocked(a, b, c, n, 64); }

// Best-of-reps wall time of f(); the first repetition pays cold caches and page faults.
template <class F>
static double best_seconds(F&& f, int reps) {
    double best = 1e30;
    for (int r = 0; r < reps; ++r) {
        Timer t;
        f();
        best = std::min(best, t.seconds());
    }
    return best;
}

static void random_fill(Mat& m, unsigned seed) {
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> U(-1, 1);
    for (auto& x : m) x = U(rng);
}

static void run(std::size_t n, bool test) {
    Mat a(n * n), b(n * n), c_ref(n * n), c(n * n);
    random_fill(a, 42);
    random_fill(b, 43);
    const int reps = n > 512 ? 2 : 3;   // naive at n = 1024 takes ~1.5 s per call

    const char* names[] = {"naive ijk", "ikj", "transposed", "blocked 64"};
    Kernel kernels[] = {matmul_naive, matmul_ikj, matmul_transposed, blocked64};
    std::printf("n = %zu\n%-12s %10s %10s %12s\n", n, "variant", "time [s]", "GFLOP/s", "max|diff|");
    for (int v = 0; v < 4; ++v) {
        const double sec = best_seconds([&] { kernels[v](a, b, v == 0 ? c_ref : c, n); }, reps);
        double diff = v == 0 ? 0.0 : max_diff(c, c_ref);
        std::printf("%-12s %10.4f %10.2f %12.2e\n", names[v], sec, 2.0 * n * n * n / sec / 1e9, diff);
        if (test) CHECK(diff < 1e-10 * n);
    }
}

// ikj against one-level tiling for several tile sizes b; 3 b^2 * 8 bytes must fit
// the targeted cache level (b = 64: 96 KB, L1 = 128 KB on the M3 P-cores [S34]).
static void block_sweep(std::size_t n) {
    Mat a(n * n), b(n * n), c_ref(n * n), c(n * n);
    random_fill(a, 42);
    random_fill(b, 43);
    const double flops = 2.0 * n * n * n;
    const double t_ikj = best_seconds([&] { matmul_ikj(a, b, c_ref, n); }, 3);
    std::printf("\nblock-size sweep, n = %zu (best of 3)\n%-12s %10s %10s\n", n, "variant", "GFLOP/s", "vs ikj");
    std::printf("%-12s %10.2f %10.2f\n", "ikj", flops / t_ikj / 1e9, 1.0);
    for (std::size_t bs : {32, 64, 128, 256}) {
        const double t = best_seconds([&] { matmul_blocked(a, b, c, n, bs); }, 3);
        std::printf("blocked %-4zu %10.2f %10.2f\n", bs, flops / t / 1e9, t_ikj / t);
    }
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    if (mode == "test") {
        run(97, true);   // odd size exercises the partial blocks
        run(256, true);
        // tile sizes that do not divide n, and one larger than n, must agree too
        Mat a(97 * 97), b(97 * 97), c_ref(97 * 97), c(97 * 97);
        random_fill(a, 1);
        random_fill(b, 2);
        matmul_naive(a, b, c_ref, 97);
        for (std::size_t bs : {1, 7, 32, 200}) {
            matmul_blocked(a, b, c, 97, bs);
            CHECK(max_diff(c, c_ref) < 1e-12);
        }
        std::puts("matmul_opt: ok");
    } else if (mode == "bench") {
        run(512, false);
        run(1024, false);
        block_sweep(2048);
    } else {
        run(256, false);
    }
    return 0;
}
