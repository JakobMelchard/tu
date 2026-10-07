// Histogram of N integers into `bins` bins: shared bins updated with atomics vs
// privatised per-thread bins merged once. Mirrors the CUDA pattern "per-block
// histogram in shared memory, then one atomicAdd per bin to global memory"
// [S15] ("Atomic Functions"). Note 04, section "Atomics".
//
// Contention model: with p threads hammering b bins, a bin's cache line is
// written by several cores at once when b is small; every atomic then pays a
// coherence round trip. Privatisation replaces N contended atomics by
// p * b uncontended merges.
#include "common.hpp"

using mc::Mode;

namespace {

using Hist = std::vector<long>;

Hist hist_serial(const std::vector<int>& d, int bins) {
    Hist h(bins, 0);
    for (int v : d) ++h[v];
    return h;
}

Hist hist_atomic(const std::vector<int>& d, int bins) {
    Hist h(bins, 0);
    long* hp = h.data();
#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < d.size(); ++i) {
#pragma omp atomic
        ++hp[d[i]];
    }
    return h;
}

// Per-thread private copy, merged with one atomic per (thread, bin): the
// shared-memory-then-global CUDA pattern.
Hist hist_private_atomic_merge(const std::vector<int>& d, int bins) {
    Hist h(bins, 0);
    long* hp = h.data();
#pragma omp parallel
    {
        Hist local(bins, 0);
#pragma omp for schedule(static) nowait
        for (size_t i = 0; i < d.size(); ++i) ++local[d[i]];
        for (int b = 0; b < bins; ++b)
            if (local[b]) {
#pragma omp atomic
                hp[b] += local[b];
            }
    }
    return h;
}

// Same idea expressed as an OpenMP array-section reduction (OpenMP >= 4.5).
Hist hist_reduction(const std::vector<int>& d, int bins) {
    Hist h(bins, 0);
    long* hp = h.data();
#pragma omp parallel for reduction(+ : hp[:bins]) schedule(static)
    for (size_t i = 0; i < d.size(); ++i) ++hp[d[i]];
    return h;
}

std::vector<int> data_uniform(size_t n, int bins, unsigned seed) {
    mc::Rng r(seed);
    std::vector<int> d(n);
    for (auto& v : d) v = int(r.next() % unsigned(bins));
    return d;
}

std::vector<int> data_skewed(size_t n, int bins, unsigned seed) {  // 90 % in bin 0
    mc::Rng r(seed);
    std::vector<int> d(n);
    for (auto& v : d) v = r.uniform() < 0.9 ? 0 : int(r.next() % unsigned(bins));
    return d;
}

int run_test() {
    std::printf("atomics_histogram --test\n");
    for (int bins : {1, 7, 256, 65536}) {
        for (int skew = 0; skew < 2; ++skew) {
            auto d = skew ? data_skewed(200003, bins, bins) : data_uniform(200003, bins, bins);
            Hist ref = hist_serial(d, bins);
            long tot = 0;
            for (long c : ref) tot += c;
            bool ok = tot == 200003 && hist_atomic(d, bins) == ref &&
                      hist_private_atomic_merge(d, bins) == ref && hist_reduction(d, bins) == ref;
            std::printf("  bins = %5d, %s: ", bins, skew ? "skewed " : "uniform");
            mc::check(ok, "atomic, private+merge and array reduction equal the serial histogram");
        }
    }
    return mc::finish();
}

void run(bool bench) {
    size_t n = bench ? (size_t(1) << 25) : (size_t(1) << 23);
    std::printf("histogram, N = %zu, %d threads, best of 5, ns per element\n", n, omp_get_max_threads());
    mc::print_load();
    std::printf("  %6s %-8s %10s %10s %14s %12s\n", "bins", "data", "serial", "atomic", "private+merge",
                "reduction");
    for (int bins : {1, 16, 256, 4096, 65536}) {
        for (int skew = 0; skew < 2; ++skew) {
            if (bins == 1 && skew) continue;
            auto d = skew ? data_skewed(n, bins, 1) : data_uniform(n, bins, 1);
            auto ns = [&](Hist (*f)(const std::vector<int>&, int)) {
                return mc::time_min([&] { volatile long x = f(d, bins)[0]; (void)x; }) / double(n) * 1e9;
            };
            std::printf("  %6d %-8s %10.3f %10.3f %14.3f %12.3f\n", bins, skew ? "skewed" : "uniform",
                        ns(hist_serial), ns(hist_atomic), ns(hist_private_atomic_merge), ns(hist_reduction));
        }
    }
}

}  // namespace

int main(int argc, char** argv) {
    Mode m = mc::parse_mode(argc, argv);
    if (m == Mode::test) return run_test();
    run(m == Mode::bench);
    return 0;
}
