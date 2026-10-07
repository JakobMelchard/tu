// rng_mc.cpp -- random numbers and Monte Carlo (topic 06).
//
//   LCG x_{k+1} = (a x_k + c) mod m  (minstd: a=16807, c=0, m=2^31-1) vs std::mt19937.
//   Uniform -> other distributions: inverse transform (exponential), Box-Muller (normal).
//   MC integration: pi from the quarter circle, I = int_0^1 e^x dx = e-1, with the
//   1/sqrt(N) error law measured over repeated runs, and two variance-reduction
//   tricks (antithetic variates, control variate) on the same integral.
//
// Sources: minstd parameters [S28]; the required 10000th values of minstd_rand0
// and mt19937 [S14, rand.predef]; MT19937 [S26]; Box-Muller [S30].
//
// Usage: ./rng_mc [--test | --bench]
#include "common.hpp"
#include <array>
#include <cstdint>
#include <random>
#include <vector>

const double PI_ = 3.14159265358979323846;
struct LCG {                       // 64-bit state so a*x never overflows for m < 2^32
    std::uint64_t a, c, m, state;
    LCG(std::uint64_t a_, std::uint64_t c_, std::uint64_t m_, std::uint64_t seed) : a(a_), c(c_), m(m_), state(seed) {}
    std::uint64_t next() { state = (a * state + c) % m; return state; }
    double uniform() { return static_cast<double>(next()) / static_cast<double>(m); }   // in [0,1)
};

// Exponential with rate lambda by inverting F(x) = 1 - e^{-lambda x}.
template <class U> double exponential(U& u01, double lambda) { return -std::log(1.0 - u01()) / lambda; }

// Box-Muller: two uniforms -> two independent standard normals.
template <class U> std::pair<double, double> box_muller(U& u01) {
    double u1 = u01(), u2 = u01();
    while (u1 <= 0.0) u1 = u01();               // avoid log(0)
    double r = std::sqrt(-2.0 * std::log(u1)), th = 2.0 * 3.14159265358979323846 * u2;
    return {r * std::cos(th), r * std::sin(th)};
}

struct Stats { double mean, var; };
static Stats mean_var(const std::vector<double>& v) {
    double m = 0; for (double x : v) m += x; m /= v.size();
    double s = 0; for (double x : v) s += (x - m) * (x - m);
    return {m, s / (v.size() - 1)};
}

// MC estimate of pi: fraction of points in the quarter disc times 4.
template <class U> double mc_pi(U& u01, std::size_t n) {
    std::size_t hits = 0;
    for (std::size_t k = 0; k < n; ++k) { double x = u01(), y = u01(); hits += (x * x + y * y < 1.0); }
    return 4.0 * hits / n;
}

// int_0^1 e^x dx three ways; returns {plain, antithetic, control variate} estimates.
template <class U> std::array<double, 3> mc_exp_integral(U& u01, std::size_t n) {
    double plain = 0, anti = 0, ctrl = 0;
    for (std::size_t k = 0; k < n; ++k) {
        double u = u01(), fu = std::exp(u);
        plain += fu;
        anti += 0.5 * (fu + std::exp(1.0 - u));        // f(u) and f(1-u) are negatively correlated
        ctrl += fu - (1.0 + u) + 1.5;                   // g(u)=1+u has known integral 3/2, corr(f,g) ~ 1
    }
    return {plain / n, anti / n, ctrl / n};
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    const bool test = mode == "test", bench = mode == "bench";

    // 1. generators
    LCG minstd(16807, 0, 2147483647ULL, 1);
    std::minstd_rand0 ref(1);
    std::printf("minstd LCG first values:");
    for (int i = 0; i < 4; ++i) std::printf(" %llu", static_cast<unsigned long long>(minstd.next()));
    std::printf("\n");
    for (int i = 4; i < 9999; ++i) minstd.next();   // 9999 calls so far, next() is the 10000th
    ref.discard(9999);
    std::uint64_t v10000 = minstd.next(), r10000 = ref();
    std::printf("10000th value: LCG %llu, std::minstd_rand0 %llu (standard says 1043618065)\n",
                static_cast<unsigned long long>(v10000), static_cast<unsigned long long>(r10000));
    LCG tiny(5, 1, 16, 0);                         // period-16 toy: shows how short a bad LCG cycles
    std::printf("LCG a=5,c=1,m=16 from 0:");
    for (int i = 0; i < 18; ++i) std::printf(" %llu", static_cast<unsigned long long>(tiny.next()));
    std::printf("  <- repeats after 16\n");
    std::mt19937 mt;                                // default seed 5489
    mt.discard(9999);
    std::uint32_t m10000 = mt();
    std::printf("mt19937 10000th value: %u (standard says 4123659995)\n", m10000);
    if (test) { CHECK(v10000 == 1043618065ULL); CHECK(r10000 == 1043618065ULL); CHECK(m10000 == 4123659995u); }

    // 2. distributions
    std::mt19937_64 gen(2026);
    std::uniform_real_distribution<double> U(0.0, 1.0);
    auto u01 = [&] { return U(gen); };
    const std::size_t ns = bench ? 2000000 : 200000;
    std::vector<double> ex(ns), nz(ns);
    for (std::size_t k = 0; k < ns; ++k) ex[k] = exponential(u01, 2.0);
    for (std::size_t k = 0; k < ns; k += 2) { auto z = box_muller(u01); nz[k] = z.first; if (k + 1 < ns) nz[k + 1] = z.second; }
    Stats se = mean_var(ex), sn = mean_var(nz);
    std::printf("\nexponential(lambda=2): mean %.4f (1/2), var %.4f (1/4)\n", se.mean, se.var);
    std::printf("Box-Muller normal    : mean %.4f (0), var %.4f (1)\n", sn.mean, sn.var);
    if (test) { CHECK(std::fabs(se.mean - 0.5) < 0.01); CHECK(std::fabs(se.var - 0.25) < 0.01);
                CHECK(std::fabs(sn.mean) < 0.01); CHECK(std::fabs(sn.var - 1.0) < 0.02); }

    // 3. Monte Carlo pi and the 1/sqrt(N) law (RMS error over reps independent runs)
    const int reps = 20;
    std::printf("\n%10s %12s %12s %10s\n", "N", "rms err pi", "4*sqrt(p(1-p)/N)", "ratio");
    std::vector<double> logN, logE;
    for (std::size_t n : {100u, 1000u, 10000u, 100000u, 1000000u}) {
        double se2 = 0;
        for (int r = 0; r < reps; ++r) { double p = mc_pi(u01, n); se2 += (p - PI_) * (p - PI_); }
        double rms = std::sqrt(se2 / reps), theory = 4 * std::sqrt(PI_ / 4 * (1 - PI_ / 4) / n);
        std::printf("%10zu %12.2e %12.2e %10.2f\n", n, rms, theory, rms / theory);
        logN.push_back(std::log(static_cast<double>(n))); logE.push_back(std::log(rms));
    }
    // least-squares slope of log(err) vs log(N)
    double mx = 0, my = 0; for (std::size_t i = 0; i < logN.size(); ++i) { mx += logN[i]; my += logE[i]; }
    mx /= logN.size(); my /= logN.size();
    double sxy = 0, sxx = 0; for (std::size_t i = 0; i < logN.size(); ++i) { sxy += (logN[i] - mx) * (logE[i] - my); sxx += (logN[i] - mx) * (logN[i] - mx); }
    double slope = sxy / sxx;
    std::printf("fitted slope of log(err) vs log(N): %.3f (theory -0.5)\n", slope);
    if (test) CHECK(slope > -0.7 && slope < -0.3);

    // 4. variance reduction on int_0^1 e^x dx = e - 1
    const std::size_t nI = bench ? 1000000 : 100000;
    const double exact = std::exp(1.0) - 1.0;
    double s2[3] = {0, 0, 0};
    for (int r = 0; r < reps; ++r) { auto e = mc_exp_integral(u01, nI); for (int j = 0; j < 3; ++j) s2[j] += (e[j] - exact) * (e[j] - exact); }
    const char* names[3] = {"plain", "antithetic", "control variate"};
    std::printf("\nint_0^1 e^x dx, N = %zu, rms error over %d runs:\n", nI, reps);
    for (int j = 0; j < 3; ++j) std::printf("  %-16s %.2e   variance reduction x%.1f\n", names[j], std::sqrt(s2[j] / reps), s2[0] / s2[j]);
    if (test) { CHECK(s2[1] < s2[0]); CHECK(s2[2] < s2[0]); std::puts("rng_mc: ok"); }
    return 0;
}
