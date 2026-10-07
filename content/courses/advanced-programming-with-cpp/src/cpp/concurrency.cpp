// concurrency.cpp -- threads, jthread + stop_token, mutex, atomics, condition variables,
// futures, and the parallel algorithms (note 14). All checks are deterministic: every
// data race shown in the note is fixed here, none is executed.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <functional>
#include <future>
#include <latch>
#include <memory>
#include <mutex>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <stop_token>
#include <string>
#include <thread>
#include <vector>
#if defined(HAVE_EXECUTION)
#include <execution>
#endif
#include "check.hpp"

constexpr int kThreads = 4, kIncrements = 100'000;

// an unbounded producer/consumer queue: mutex + condition_variable, the canonical pattern
template <class T> class Channel {
    std::mutex m_;
    std::condition_variable cv_;
    std::queue<T> q_;
    bool closed_ = false;
public:
    void push(T v) {
        { std::lock_guard lock(m_); q_.push(std::move(v)); }
        cv_.notify_one();                          // notify after unlocking: the woken thread can proceed
    }
    void close() { { std::lock_guard lock(m_); closed_ = true; } cv_.notify_all(); }
    bool pop(T& out) {                             // false when closed and drained
        std::unique_lock lock(m_);
        cv_.wait(lock, [&] { return !q_.empty() || closed_; });   // predicate handles spurious wakeups
        if (q_.empty()) return false;
        out = std::move(q_.front());
        q_.pop();
        return true;
    }
};

#if defined(HAVE_EXECUTION)
// ./bin/concurrency --bench : seq vs par wall time, not part of the test
template <class F> double seconds(F&& f) {
    auto t0 = std::chrono::steady_clock::now();
    f();
    return std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
}
void bench() {
    std::vector<double> v(20'000'000);
    std::uint64_t x = 88172645463325252ull;                       // xorshift64: deterministic data
    for (double& d : v) { x ^= x << 13; x ^= x >> 7; x ^= x << 17; d = static_cast<double>(x >> 11) * 0x1p-53; }
    auto w = v;
    double r1 = 0, r2 = 0;
    std::printf("threads available: %u\n", std::thread::hardware_concurrency());
    std::printf("reduce 2e7 doubles  seq %.4f s  par_unseq %.4f s\n",
                seconds([&] { r1 = std::reduce(std::execution::seq, v.begin(), v.end()); }),
                seconds([&] { r2 = std::reduce(std::execution::par_unseq, v.begin(), v.end()); }));
    std::printf("  sums differ by %.3g (reassociation)\n", r1 - r2);
    std::printf("sort   2e7 doubles  seq %.3f s   par %.3f s\n",
                seconds([&] { std::sort(v.begin(), v.end()); }),
                seconds([&] { std::sort(std::execution::par, w.begin(), w.end()); }));
}
#endif

int main(int argc, char** argv) {
#if defined(HAVE_EXECUTION)
    if (argc > 1 && std::string(argv[1]) == "--bench") { bench(); return 0; }
#else
    (void)argc; (void)argv;
#endif
    // 1. mutex: the increment becomes a critical section
    long counter = 0;
    std::mutex m;
    {
        std::vector<std::jthread> ts;               // jthread joins in its destructor
        for (int t = 0; t < kThreads; ++t)
            ts.emplace_back([&] { for (int i = 0; i < kIncrements; ++i) { std::lock_guard lock(m); ++counter; } });
    }
    CHECK(counter == long{kThreads} * kIncrements);

    // 2. atomic: a single read-modify-write, no lock; relaxed is enough for a pure counter
    std::atomic<long> acount{0};
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < kThreads; ++t)
            ts.emplace_back([&] { for (int i = 0; i < kIncrements; ++i) acount.fetch_add(1, std::memory_order_relaxed); });
    }
    CHECK(acount.load() == long{kThreads} * kIncrements);

    // 3. best: no sharing at all; each thread owns a partial result, combine once
    std::vector<long> partial(kThreads);
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < kThreads; ++t)
            ts.emplace_back([&partial, t] { long s = 0; for (int i = 0; i < kIncrements; ++i) ++s; partial[static_cast<std::size_t>(t)] = s; });
    }
    CHECK(std::accumulate(partial.begin(), partial.end(), 0L) == long{kThreads} * kIncrements);

    // 4. release/acquire: publish data through a flag
    int payload = 0;
    std::atomic<bool> ready{false};
    std::jthread producer([&] { payload = 42; ready.store(true, std::memory_order_release); });
    while (!ready.load(std::memory_order_acquire)) std::this_thread::yield();
    CHECK(payload == 42);                           // happens-before via the release/acquire pair
    producer.join();

    // 5. jthread + stop_token: cooperative cancellation
    std::atomic<int> ticks{0};
    {
        std::jthread worker([&](std::stop_token st) { while (!st.stop_requested()) { ++ticks; std::this_thread::yield(); } });
        while (ticks.load() < 10) std::this_thread::yield();
    }                                               // destructor: request_stop(), then join()
    CHECK(ticks.load() >= 10);

    // 6. condition variable channel: 2 producers, 1 consumer
    Channel<int> ch;
    long received = 0;
    {
        std::jthread consumer([&] { int v; while (ch.pop(v)) received += v; });
        {
            std::jthread p1([&] { for (int i = 1; i <= 100; ++i) ch.push(i); });
            std::jthread p2([&] { for (int i = 1; i <= 100; ++i) ch.push(i); });
        }                                           // producers joined
        ch.close();
    }
    CHECK(received == 2 * 5050);

    // 7. futures: a value (or exception) from another thread
    std::promise<double> pr;
    std::future<double> fu = pr.get_future();
    std::jthread setter([p = std::move(pr)]() mutable { p.set_value(2.5); });
    CHECK(fu.get() == 2.5);
    auto af = std::async(std::launch::async, [] { return std::string("from async"); });
    CHECK(af.get() == "from async");
    auto bad = std::async(std::launch::async, []() -> int { throw std::runtime_error("boom"); });
    bool caught = false;
    try { bad.get(); } catch (const std::runtime_error&) { caught = true; }
    CHECK(caught);                                  // the exception crosses the thread boundary

    // 8. latch: wait until N events have happened (C++20)
    std::latch done(kThreads);
    std::atomic<int> started{0};
    std::vector<std::jthread> ws;
    for (int t = 0; t < kThreads; ++t) ws.emplace_back([&] { ++started; done.count_down(); });
    done.wait();
    CHECK(started.load() == kThreads);

    // 9. shared_ptr: the reference count is thread-safe, the pointee is not
    auto sp = std::make_shared<int>(7);
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < kThreads; ++t)
            ts.emplace_back([sp] { for (int i = 0; i < 1000; ++i) { auto copy = sp; (void)copy; } });
    }
    CHECK(sp.use_count() == 1);

    // 10. parallel algorithms (libc++: -fexperimental-library, libdispatch backend on macOS)
    std::vector<long> big(2'000'000);
    std::iota(big.begin(), big.end(), 1L);
    long seq = std::reduce(big.begin(), big.end(), 0L);
#if defined(HAVE_EXECUTION)
    long par = std::reduce(std::execution::par, big.begin(), big.end(), 0L);
    CHECK(par == seq);                              // integers: associative, so identical
    std::vector<long> rev(big.rbegin(), big.rend());
    std::sort(std::execution::par_unseq, rev.begin(), rev.end());
    CHECK(rev == big);
#else
    chk::skip("std::execution policies", "parallel algorithms unavailable (libc++ needs -fexperimental-library)");
#endif
    CHECK(seq == 2'000'000L * 2'000'001L / 2);
    return chk::report("concurrency");
}
