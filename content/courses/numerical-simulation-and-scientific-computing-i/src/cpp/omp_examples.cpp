// omp_examples.cpp -- shared-memory parallelism with OpenMP (topic 07).
//
//   parallel for + reduction, race condition and its three fixes (atomic, critical,
//   reduction), false sharing (adjacent per-thread counters vs padded), scheduling
//   of unbalanced loops (static / dynamic / guided), strong scaling vs thread count
//   compared with Amdahl's law.
//
// Sources: every directive and clause as specified in OpenMP 5.2 [S11] (vendored
// in refs/vendor/): reduction §5.5.8, schedule §11.5.3, atomic §15.8.4, critical
// §15.2. Amdahl's bound [S19]; reading the table with Karp-Flatt is py/scaling.py.
//
// Build: clang++ -std=c++17 -O2 -Xpreprocessor -fopenmp -I$(brew --prefix libomp)/include
//        omp_examples.cpp -L$(brew --prefix libomp)/lib -lomp
// Usage: ./omp_examples [--test | --bench]
#include "common.hpp"
#include <omp.h>
#include <utility>
#include <vector>

// Compute-heavy kernel: sum_i f(x_i) with f expensive enough that threads pay off.
static double heavy_sum(const std::vector<double>& x) {
    double s = 0;
#pragma omp parallel for reduction(+ : s) schedule(static)
    for (std::size_t i = 0; i < x.size(); ++i) s += std::sqrt(x[i]) * std::sin(x[i]);
    return s;
}

// Returns {counter, expected}. fix: 0 none (data race), 1 atomic, 2 critical, 3 reduction.
static std::pair<long, long> race_counter(long n, int fix) {
    long counter = 0;
    if (fix == 0) {
        long per = 0;
#pragma omp parallel
        {
            per = n / omp_get_num_threads();
            for (long i = 0; i < n / omp_get_num_threads(); ++i) {
                long t = counter;                   // load
                asm volatile("" ::: "memory");      // compiler barrier: keep load, add, store separate
                counter = t + 1;                    // store -- another thread may have stored meanwhile
            }
        }
        return {counter, per * omp_get_max_threads()};
    } else if (fix == 1) {
#pragma omp parallel for
        for (long i = 0; i < n; ++i) {
#pragma omp atomic
            counter++;
        }
    } else if (fix == 2) {
#pragma omp parallel for
        for (long i = 0; i < n; ++i) {
#pragma omp critical
            counter++;
        }
    } else {
#pragma omp parallel for reduction(+ : counter)
        for (long i = 0; i < n; ++i) counter++;
    }
    return {counter, n};
}

// False sharing: each thread bumps its own counter, but all counters share one
// cache line -> the line ping-pongs between cores. Padding to 128 bytes fixes it.
struct Padded { alignas(128) long v; };
static double false_sharing(long per_thread, bool padded, long* total) {
    int nt = omp_get_max_threads();
    std::vector<long> plain(nt, 0);
    std::vector<Padded> pad(nt);
    for (auto& p : pad) p.v = 0;
    Timer t;
#pragma omp parallel
    {
        int tid = omp_get_thread_num();
        // `volatile` forces a real load-modify-store per increment. Without it
        // the compiler may keep the counter in a register for the whole loop
        // (a data race is UB, so it assumes nobody else writes), and the line
        // never bounces -- which hides false sharing entirely. [S11] [S37]
        volatile long* slot = padded ? &pad[tid].v : &plain[tid];
        for (long k = 0; k < per_thread; ++k) (*slot)++;
    }
    double sec = t.seconds();
    *total = 0;
    for (int i = 0; i < nt; ++i) *total += padded ? pad[i].v : plain[i];
    return sec;
}

// Unbalanced work: iteration i costs ~ i, so static chunks give the last thread
// most of the work; dynamic/guided rebalance at the cost of scheduling overhead.
static double unbalanced(int n, int sched, double* out) {
    double s = 0;
    Timer t;
    if (sched == 0) {
#pragma omp parallel for reduction(+ : s) schedule(static)
        for (int i = 0; i < n; ++i) { double a = 0; for (int k = 0; k < i; ++k) a += std::sqrt(k + 1.0); s += a; }
    } else if (sched == 1) {
#pragma omp parallel for reduction(+ : s) schedule(dynamic, 16)
        for (int i = 0; i < n; ++i) { double a = 0; for (int k = 0; k < i; ++k) a += std::sqrt(k + 1.0); s += a; }
    } else {
#pragma omp parallel for reduction(+ : s) schedule(guided)
        for (int i = 0; i < n; ++i) { double a = 0; for (int k = 0; k < i; ++k) a += std::sqrt(k + 1.0); s += a; }
    }
    *out = s;
    return t.seconds();
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    const bool test = mode == "test", bench = mode == "bench";
    const int max_threads = omp_get_max_threads();
    std::printf("omp_get_max_threads() = %d\n", max_threads);

    // race condition
    const char* fixes[] = {"none (race)", "atomic", "critical", "reduction"};
    for (int f = 0; f < 4; ++f) {
        const long n_race = f == 2 ? 20000 : 1000000;   // critical is ~1000x slower than atomic
        Timer t; auto [c, expected] = race_counter(n_race, f);
        std::printf("counter with %-12s = %8ld (expected %8ld)  %8.1f ns/increment\n", fixes[f], c, expected,
                    t.seconds() / n_race * 1e9);
        if (test && f > 0) CHECK(c == expected);
    }

    // false sharing
    long tot1, tot2;
    const long per = bench ? 50000000 : 10000000;
    double t_plain = false_sharing(per, false, &tot1), t_pad = false_sharing(per, true, &tot2);
    const double upd = double(per) * max_threads;   // total increments per variant
    std::printf("\nfalse sharing: adjacent counters %.4f s, padded %.4f s (%.1fx); %.3f vs %.3f ns/update\n", t_plain,
                t_pad, t_plain / t_pad, t_plain / upd * 1e9, t_pad / upd * 1e9);
    if (test) { CHECK(tot1 == per * max_threads); CHECK(tot2 == per * max_threads); }

    // scheduling
    const int nu = bench ? 20000 : 6000;
    double r0, r1, r2;
    double ts = unbalanced(nu, 0, &r0), td = unbalanced(nu, 1, &r1), tg = unbalanced(nu, 2, &r2);
    std::printf("unbalanced loop: static %.4f s, dynamic,16 %.4f s, guided %.4f s\n", ts, td, tg);
    if (test) { CHECK(close(r0, r1, 1e-9)); CHECK(close(r0, r2, 1e-9)); }

    // strong scaling vs Amdahl
    const std::size_t nx = bench ? 40000000 : 8000000;
    std::vector<double> x(nx);
    for (std::size_t i = 0; i < nx; ++i) x[i] = 1e-3 * (i % 1000);
    std::printf("\n%8s %10s %8s %10s\n", "threads", "time[ms]", "speedup", "efficiency");
    double t1 = 0, s1 = 0;
    for (int p = 1; p <= max_threads; p *= 2) {
        omp_set_num_threads(p);
        double best = 1e30, s = 0;
        for (int r = 0; r < 3; ++r) { Timer t; s = heavy_sum(x); best = std::min(best, t.seconds()); }
        if (p == 1) { t1 = best; s1 = s; }
        std::printf("%8d %10.2f %8.2f %10.2f\n", p, best * 1e3, t1 / best, t1 / best / p);
        if (test) CHECK(close(s, s1, 1e-9));
    }
    omp_set_num_threads(max_threads);
    std::printf("Amdahl: with serial fraction f the speedup is bounded by 1/f; for f = 0.05 and p = %d: %.2f\n",
                max_threads, 1.0 / (0.05 + 0.95 / max_threads));
    if (test) {
        if (max_threads > 1) { omp_set_num_threads(2); int seen = 0;
#pragma omp parallel reduction(+ : seen)
            seen = 1;
            CHECK(seen == 2); }
        std::puts("omp_examples: ok");
    }
    return 0;
}
