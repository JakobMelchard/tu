// common.hpp -- tiny helpers shared by the NSSC I reference programs.
#pragma once
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>

// Wall-clock timer (steady_clock is monotonic; never use system_clock for timing).
struct Timer {
    using clk = std::chrono::steady_clock;
    clk::time_point t0 = clk::now();
    double seconds() const { return std::chrono::duration<double>(clk::now() - t0).count(); }
    void reset() { t0 = clk::now(); }
};

// Assertion that survives -DNDEBUG and prints what failed.
#define CHECK(cond)                                                                   \
    do {                                                                              \
        if (!(cond)) {                                                                \
            std::fprintf(stderr, "CHECK failed: %s  (%s:%d)\n", #cond, __FILE__, __LINE__); \
            std::exit(1);                                                             \
        }                                                                             \
    } while (0)

inline bool close(double a, double b, double rtol = 1e-9, double atol = 1e-12) {
    return std::fabs(a - b) <= atol + rtol * std::fabs(b);
}

// Mode from argv: "" (demo), "test" or "bench".
inline std::string mode_of(int argc, char** argv) {
    if (argc < 2) return "";
    std::string s = argv[1];
    if (s == "--test") return "test";
    if (s == "--bench") return "bench";
    return "";
}
