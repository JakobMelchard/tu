// cache_bench.cpp -- memory hierarchy experiments (topic 01: computer architectures).
//
//   1. working-set sweep: chase random pointers inside W bytes (each load depends on
//      the previous one). Latency per load jumps at each cache level: L1 -> L2 -> DRAM.
//   2. stride sweep on a 32 MB array: stride s, s passes offset by 0..s-1, so every
//      element is loaded exactly once for every s. Cost per load rises until one
//      cache line (128 B on Apple silicon, 64 B on x86) is fetched per load.
//   3. loop order on a row-major 2D array: i-j (contiguous) vs j-i (stride n).
//   4. STREAM-like triad a = b + s*c  -> sustained memory bandwidth in GB/s.
//   5. compute-bound kernel with independent accumulators -> attainable FLOP/s.
//   4 and 5 are the two roofs of a roofline plot for this machine and compiler.
//
// Sources: latency vs throughput and the 8-accumulator argument [S8]; the triad
// kernel and byte-counting convention of STREAM [S17]; roofline [S16]; cache
// line and cache sizes read from sysctl on the host [S34].
//
// Usage: ./cache_bench [--test | --bench]
#include "common.hpp"
#include <cstdint>
#include <vector>

// Sum with stride s using s offset passes and 4 accumulators (breaks the add
// dependency chain so throughput, not latency, is measured).
static double strided_sum(const std::vector<double>& a, std::size_t s) {
    const std::size_t n = a.size();
    double a0 = 0, a1 = 0, a2 = 0, a3 = 0;
    for (std::size_t p = 0; p < s; ++p) {
        std::size_t k = p;
        for (; k + 3 * s < n; k += 4 * s) { a0 += a[k]; a1 += a[k + s]; a2 += a[k + 2 * s]; a3 += a[k + 3 * s]; }
        for (; k < n; k += s) a0 += a[k];
    }
    return (a0 + a1) + (a2 + a3);
}

// Pointer chasing through a random cyclic permutation of w/4 uint32 slots: each
// load depends on the previous one, so the time per step is the *latency* of the
// cache level that holds the working set (L1 ~1 ns, L2 ~4 ns, DRAM ~100 ns).
static double chase_ns(std::size_t w_bytes, std::size_t steps, std::uint32_t seed) {
    const std::uint32_t len = static_cast<std::uint32_t>(w_bytes / 4);
    std::vector<std::uint32_t> next(len);
    for (std::uint32_t i = 0; i < len; ++i) next[i] = i;
    std::uint64_t st = seed | 1;                       // xorshift64: cheap, good enough for shuffling
    for (std::uint32_t i = len - 1; i > 0; --i) {      // Sattolo: one cycle through all slots
        st ^= st << 13; st ^= st >> 7; st ^= st << 17;
        std::uint32_t j = static_cast<std::uint32_t>(st % i);
        std::swap(next[i], next[j]);
    }
    Timer t;
    std::uint32_t idx = 0;
    for (std::size_t k = 0; k < steps; ++k) idx = next[idx];
    double sec = t.seconds();
    if (idx == 0xFFFFFFFFu) std::puts("");           // keep idx alive
    return sec / static_cast<double>(steps) * 1e9;
}

static double sum_ij(const std::vector<double>& m, std::size_t n) {   // row-major, inner loop contiguous
    double s = 0.0;
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t j = 0; j < n; ++j) s += m[i * n + j];
    return s;
}
static double sum_ji(const std::vector<double>& m, std::size_t n) {   // inner loop jumps by n doubles
    double s = 0.0;
    for (std::size_t j = 0; j < n; ++j)
        for (std::size_t i = 0; i < n; ++i) s += m[i * n + j];
    return s;
}

// Triad: 2 flops per element, 3 doubles moved (24 bytes) -> AI = 1/12 flop/byte.
static double triad_gbs(std::vector<double>& a, const std::vector<double>& b,
                        const std::vector<double>& c, double s, int reps) {
    double best = 1e30;
    for (int r = 0; r < reps; ++r) {
        Timer t;
        for (std::size_t i = 0; i < a.size(); ++i) a[i] = b[i] + s * c[i];
        best = std::min(best, t.seconds());
    }
    return 3.0 * 8.0 * static_cast<double>(a.size()) / best / 1e9;
}

// Compute-bound: 8 independent chains of x = x*c + d (2 flops each) so the CPU
// can overlap them (instruction-level parallelism); no memory traffic in the loop.
static double compute_gflops(std::size_t iters, double* sink) {
    double x[8];
    for (int j = 0; j < 8; ++j) x[j] = 0.1 * (j + 1);
    const double c = 0.999999, d = 1e-7;
    Timer t;
    for (std::size_t k = 0; k < iters; ++k)
        for (int j = 0; j < 8; ++j) x[j] = x[j] * c + d;
    double sec = t.seconds();
    double acc = 0;
    for (int j = 0; j < 8; ++j) acc += x[j];
    *sink = acc;
    return 2.0 * 8.0 * static_cast<double>(iters) / sec / 1e9;
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    const bool test = mode == "test", bench = mode == "bench";

    // 1. working set sweep (latency)
    const std::size_t steps = bench ? (1u << 25) : (1u << 23);
    std::printf("working set sweep: pointer chasing, %zu dependent loads, single core\n%12s %14s\n", steps, "size", "ns/load");
    for (std::size_t kb : {16u, 64u, 256u, 1024u, 4096u, 16384u, 65536u, 262144u}) {
        if (!bench && kb > 65536) break;
        std::printf("%9zu KB %14.2f\n", kb, chase_ns(kb * 1024, steps, 12345));
    }

    // 2. stride sweep
    const std::size_t n = bench ? (1u << 25) : (1u << 22);
    std::vector<double> a(n, 1.0);
    std::printf("\nstride sweep on %.0f MB (every element loaded once per stride)\n%8s %10s\n", n * 8.0 / 1e6, "stride", "ns/load");
    for (std::size_t stride : {1u, 2u, 4u, 8u, 16u, 32u, 64u, 256u, 1024u}) {
        Timer t;
        double s = strided_sum(a, stride);
        std::printf("%8zu %10.3f\n", stride, t.seconds() / static_cast<double>(n) * 1e9);
        if (test) CHECK(close(s, static_cast<double>(n)));
    }

    // 3. loop order on an n2 x n2 row-major matrix, m[i][j] = i + j
    const std::size_t n2 = bench ? 4096 : 2048;
    std::vector<double> m(n2 * n2);
    for (std::size_t i = 0; i < n2; ++i)
        for (std::size_t j = 0; j < n2; ++j) m[i * n2 + j] = static_cast<double>(i + j);
    Timer t1; double s_ij = sum_ij(m, n2); double t_ij = t1.seconds();
    Timer t2; double s_ji = sum_ji(m, n2); double t_ji = t2.seconds();
    std::printf("\nloop order, %zux%zu row-major: i-j %.4f s, j-i %.4f s, ratio %.1fx\n",
                n2, n2, t_ij, t_ji, t_ji / t_ij);
    const double expect = static_cast<double>(n2) * n2 * (n2 - 1);      // sum of (i+j)
    if (test) { CHECK(close(s_ij, expect)); CHECK(close(s_ji, expect)); }

    // 4./5. bandwidth and compute roofs
    std::vector<double> b(n, 1.0), c(n, 2.0);
    double gbs = triad_gbs(a, b, c, 3.0, bench ? 5 : 3);
    double sink = 0;
    double gflops = compute_gflops(bench ? 200000000 : 50000000, &sink);
    const double ai_triad = 2.0 / 24.0;
    std::printf("\ntriad bandwidth   : %.1f GB/s  (single core)\n", gbs);
    std::printf("compute peak      : %.1f GFLOP/s (single core, scalar chains, no SIMD)\n", gflops);
    std::printf("roofline for triad: AI = %.3f flop/byte -> bandwidth roof %.2f GFLOP/s < compute roof %.1f -> memory bound\n",
                ai_triad, gbs * ai_triad, gflops);
    if (test) {
        CHECK(close(a[n / 2], 7.0));                // 1 + 3*2
        CHECK(gbs > 0.1 && gflops > 0.1 && std::isfinite(sink));
        std::puts("cache_bench: ok");
    }
    return 0;
}
