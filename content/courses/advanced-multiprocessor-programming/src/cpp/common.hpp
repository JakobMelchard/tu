// common.hpp -- helpers shared by the 191.022 AMP reference programs.
// Timer, CHECK (survives -DNDEBUG), mode parsing, a per-thread RNG, a spin
// barrier for litmus tests, and a scale factor that shrinks test sizes under
// ThreadSanitizer (TSan slows atomics 5-15x).
#pragma once
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <thread>
#include <vector>

#if defined(__has_feature)
#if __has_feature(thread_sanitizer)
#define AMP_TSAN 1
#endif
#endif
#ifndef AMP_TSAN
#define AMP_TSAN 0
#endif
// Test sizes are divided by this under TSan so `make tsan` stays in seconds.
constexpr int kScale = AMP_TSAN ? 8 : 1;

struct Timer {
    using clk = std::chrono::steady_clock;
    clk::time_point t0 = clk::now();
    double seconds() const { return std::chrono::duration<double>(clk::now() - t0).count(); }
};

#define CHECK(cond)                                                                        \
    do {                                                                                   \
        if (!(cond)) {                                                                     \
            std::fprintf(stderr, "CHECK failed: %s  (%s:%d)\n", #cond, __FILE__, __LINE__); \
            std::exit(1);                                                                  \
        }                                                                                  \
    } while (0)

inline std::string mode_of(int argc, char** argv) {
    if (argc < 2) return "";
    std::string s = argv[1];
    if (s == "--test") return "test";
    if (s == "--bench") return "bench";
    return "";
}

// xorshift64*: tiny, per-thread, good enough for choosing operations and keys.
struct Rng {
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed * 0x9E3779B97F4A7C15ull + 1) {}
    uint64_t next() {
        s ^= s >> 12; s ^= s << 25; s ^= s >> 27;
        return s * 0x2545F4914F6CDD1Dull;
    }
    uint32_t below(uint32_t n) { return uint32_t(next() >> 33) % n; }
};

// CPU hint inside spin loops (ARM `yield`, x86 `pause`).
inline void cpu_relax() {
#if defined(__aarch64__)
    asm volatile("yield" ::: "memory");
#elif defined(__x86_64__)
    asm volatile("pause" ::: "memory");
#endif
}

// Run f(tid) on n threads and join.
template <class F>
void run_threads(int n, F f) {
    std::vector<std::thread> ts;
    for (int i = 0; i < n; ++i) ts.emplace_back(f, i);
    for (auto& t : ts) t.join();
}

// Sense-reversing spin barrier (book ch. 17): cheap enough to separate
// ~10^5 litmus-test rounds per second.
class SpinBarrier {
    std::atomic<int> count_;
    std::atomic<bool> sense_{false};
    int n_;
  public:
    explicit SpinBarrier(int n) : count_(n), n_(n) {}
    void wait(bool& local_sense) {
        local_sense = !local_sense;
        if (count_.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            count_.store(n_, std::memory_order_relaxed);
            sense_.store(local_sense, std::memory_order_release);
        } else {
            while (sense_.load(std::memory_order_acquire) != local_sense) cpu_relax();
        }
    }
};

inline int max_threads() {
    int hc = int(std::thread::hardware_concurrency());
    return hc > 0 ? hc : 4;
}
