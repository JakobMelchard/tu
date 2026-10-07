// Shared helpers for the 360.252 CPU reference programs.
// Every program: `./prog` runs a small demo, `--test` asserts known results,
// `--bench` prints a timing table. Timing = minimum over repetitions of a
// monotonic wall clock (see notes/02-flops-bandwidth-latency.md, "Measuring").
#pragma once
#include <omp.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdlib.h>  // getloadavg
#include <string>
#include <vector>

namespace mc {

enum class Mode { demo, test, bench };

inline Mode parse_mode(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--test")) return Mode::test;
        if (!std::strcmp(argv[i], "--bench")) return Mode::bench;
    }
    return Mode::demo;
}

inline double now() {
    using clk = std::chrono::steady_clock;
    return std::chrono::duration<double>(clk::now().time_since_epoch()).count();
}

// Minimum wall time of f() over `reps` runs after one warm-up run.
template <class F>
double time_min(F&& f, int reps = 5) {
    f();
    double best = 1e300;
    for (int r = 0; r < reps; ++r) {
        double t0 = now();
        f();
        best = std::min(best, now() - t0);
    }
    return best;
}

inline int g_failures = 0;

inline void check(bool ok, const char* what) {
    std::printf("  [%s] %s\n", ok ? "ok" : "FAIL", what);
    if (!ok) ++g_failures;
}

inline int finish() {
    if (g_failures) {
        std::printf("%d check(s) FAILED\n", g_failures);
        return 1;
    }
    std::printf("all checks passed\n");
    return 0;
}

// Deterministic pseudo-random numbers (splitmix64): same input on every run
// and every machine, so tests are reproducible without <random> engine details.
struct Rng {
    unsigned long long s;
    explicit Rng(unsigned long long seed) : s(seed) {}
    unsigned long long next() {
        unsigned long long z = (s += 0x9E3779B97F4A7C15ULL);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
    }
    double uniform() { return (next() >> 11) * (1.0 / 9007199254740992.0); }
};

inline double max_abs_diff(const std::vector<double>& a, const std::vector<double>& b) {
    double m = 0;
    for (size_t i = 0; i < a.size(); ++i) m = std::max(m, std::fabs(a[i] - b[i]));
    return m;
}

// Benchmarks on a shared machine lie. Print the 1-minute load average next to
// every table so a reader can discard numbers taken under load.
inline void print_load() {
    double l[3] = {0, 0, 0};
    if (getloadavg(l, 3) > 0)
        std::printf("  (load average %.1f %.1f %.1f on %d logical CPUs)\n", l[0], l[1], l[2],
                    omp_get_num_procs());
}

// Thread counts to sweep: 1, 2, 4, 6 (all P-cores on an M3 Pro), max.
inline std::vector<int> thread_sweep() {
    int mx = omp_get_max_threads();
    std::vector<int> v;
    for (int p : {1, 2, 4, 6, 8, 12})
        if (p <= mx) v.push_back(p);
    if (v.back() != mx) v.push_back(mx);
    return v;
}

}  // namespace mc
