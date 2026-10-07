// threads_cpp.cpp -- shared-memory parallelism without OpenMP (topic 07).
//
// TISS calls the topic "Shared Memory Parallel Computing", not "OpenMP", and
// one of the 2026W lecturers teaches it with a hand-written C++ task manager
// rather than with directives [S8]. This file is the omp_examples.cpp material
// done in plain C++17: std::thread, std::atomic, std::mutex, and a small
// persistent worker pool with a RunParallel(n, f) entry point modelled on the
// StartWorkers / RunParallel / StopWorkers pattern of ASC-HPC [S9].
//
// The point is the comparison. Everything OpenMP gives you -- a thread pool
// that outlives one loop, a reduction, a barrier -- has to be written out here,
// and writing it out is what makes the cost of each visible.
//
//   ./threads_cpp           demo
//   ./threads_cpp --test    assertions
//   ./threads_cpp --bench   timings
#include <atomic>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <numeric>
#include <thread>
#include <vector>

#include "common.hpp"

// ---------------------------------------------------------------------------
// A persistent worker pool. Creating a std::thread costs ~10-50 us, so a pool
// that is started once is the difference between OpenMP-like cost and none.
// ---------------------------------------------------------------------------
class TaskManager {
  public:
    explicit TaskManager(int extra_threads) {
        stop_ = false;
        for (int i = 0; i < extra_threads; ++i) workers_.emplace_back([this] { loop(); });
    }
    ~TaskManager() {
        {
            std::unique_lock<std::mutex> lk(m_);
            stop_ = true;
        }
        cv_.notify_all();
        for (auto& t : workers_) t.join();
    }
    int size() const { return static_cast<int>(workers_.size()) + 1; }

    // Run f(i, n) for i = 0..n-1 across the pool plus the calling thread, and
    // return when every task is finished. This is `#pragma omp parallel for`.
    void run_parallel(int n, const std::function<void(int, int)>& f) {
        {
            std::unique_lock<std::mutex> lk(m_);
            fn_ = &f;
            total_ = n;
            next_ = 0;
            done_ = 0;
            ++epoch_;
        }
        cv_.notify_all();
        work();  // the caller is a worker too
        std::unique_lock<std::mutex> lk(m_);
        cv_done_.wait(lk, [this] { return done_ == total_; });
        fn_ = nullptr;
    }

  private:
    void loop() {
        std::size_t seen = 0;
        for (;;) {
            {
                std::unique_lock<std::mutex> lk(m_);
                cv_.wait(lk, [&] { return stop_ || epoch_ != seen; });
                if (stop_) return;
                seen = epoch_;
            }
            work();
        }
    }
    // Pull tasks off a shared counter: this is schedule(dynamic, 1).
    void work() {
        for (;;) {
            int i = next_.fetch_add(1, std::memory_order_relaxed);
            if (i >= total_) break;
            (*fn_)(i, total_);
            if (done_.fetch_add(1, std::memory_order_acq_rel) + 1 == total_) cv_done_.notify_all();
        }
    }

    std::vector<std::thread> workers_;
    std::mutex m_;
    std::condition_variable cv_, cv_done_;
    const std::function<void(int, int)>* fn_ = nullptr;
    std::atomic<int> next_{0}, done_{0};
    int total_ = 0;
    bool stop_ = false;
    std::size_t epoch_ = 0;
};

// ---------------------------------------------------------------------------
// The four ways to accumulate across threads, and what each costs.
// ---------------------------------------------------------------------------
struct CounterResult {
    long racy, atomic_, locked, reduced;
    double ns_racy, ns_atomic, ns_locked, ns_reduced;
};

CounterResult counters(TaskManager& tm, int per_task) {
    const int n = tm.size();
    const long expected = static_cast<long>(n) * per_task;
    CounterResult r{};
    Timer t;

    long racy = 0;  // UB in C++: a data race. Shown because it is the bug.
    t.reset();
    tm.run_parallel(n, [&](int, int) {
        for (int k = 0; k < per_task; ++k) *const_cast<volatile long*>(&racy) += 1;
    });
    r.racy = racy;
    r.ns_racy = t.seconds() * 1e9 / expected;

    std::atomic<long> at{0};
    t.reset();
    tm.run_parallel(n, [&](int, int) {
        for (int k = 0; k < per_task; ++k) at.fetch_add(1, std::memory_order_relaxed);
    });
    r.atomic_ = at.load();
    r.ns_atomic = t.seconds() * 1e9 / expected;

    std::mutex mu;
    long locked = 0;
    const int locked_iters = per_task / 50 + 1;  // a mutex per increment is far slower
    t.reset();
    tm.run_parallel(n, [&](int, int) {
        for (int k = 0; k < locked_iters; ++k) {
            std::lock_guard<std::mutex> g(mu);
            ++locked;
        }
    });
    r.locked = locked;
    r.ns_locked = t.seconds() * 1e9 / (static_cast<long>(n) * locked_iters);

    // The reduction: a private accumulator per task, combined once. This is
    // what `reduction(+:s)` does, and it is as fast as serial code. The
    // accumulator reads a shared array so the loop is not constant-folded away.
    std::vector<long> ones(per_task, 1);
    std::vector<long> partial(n, 0);
    t.reset();
    tm.run_parallel(n, [&](int i, int) {
        long local = 0;
        for (int k = 0; k < per_task; ++k) local += ones[k];
        partial[i] = local;
    });
    r.reduced = std::accumulate(partial.begin(), partial.end(), 0L);
    r.ns_reduced = t.seconds() * 1e9 / expected;
    return r;
}

// False sharing: per-thread accumulators packed into one cache line.
// hw.cachelinesize is 128 on Apple silicon, 64 on x86 [S34], so 16 `long`
// counters share one line and every write invalidates the other 15 copies.
//
// The counters must be std::atomic (relaxed is enough): with a plain `long`
// the compiler is entitled to assume no other thread touches it -- a data race
// is undefined behaviour -- and will keep it in a register for the whole loop,
// which hides the effect entirely. That is itself worth knowing.
struct alignas(128) PaddedCounter {
    std::atomic<long> v{0};
};

double false_sharing_ns(TaskManager& tm, int iters, bool padded) {
    const int n = tm.size();
    std::vector<std::atomic<long>> packed(n);
    std::vector<PaddedCounter> spread(n);
    for (int i = 0; i < n; ++i) packed[i].store(0);
    Timer t;
    tm.run_parallel(n, [&](int i, int) {
        auto& c = padded ? spread[i].v : packed[i];
        for (int k = 0; k < iters; ++k) c.fetch_add(1, std::memory_order_relaxed);
    });
    return t.seconds() * 1e9 / (static_cast<double>(n) * iters);
}

// A compute-bound kernel for the strong-scaling table.
double heavy_sum(TaskManager& tm, int chunks, long per_chunk) {
    std::vector<double> partial(chunks, 0.0);
    tm.run_parallel(chunks, [&](int i, int) {
        double s = 0.0;
        for (long k = 0; k < per_chunk; ++k) s += 1.0 / (1.0 + static_cast<double>(k + i));
        partial[i] = s;
    });
    return std::accumulate(partial.begin(), partial.end(), 0.0);
}

static void demo() {
    const unsigned hw = std::thread::hardware_concurrency();
    std::printf("std::thread::hardware_concurrency() = %u\n\n", hw);

    TaskManager tm(static_cast<int>(hw) - 1);
    std::printf("task manager: %d threads (pool of %u + the caller)\n\n", tm.size(), hw - 1);

    auto c = counters(tm, 1'000'00);
    const long expect = static_cast<long>(tm.size()) * 100000;
    std::printf("accumulating %ld increments across %d threads\n", expect, tm.size());
    std::printf("  %-26s = %8ld  %9.2f ns/increment %s\n", "racy (data race, UB)", c.racy,
                c.ns_racy, c.racy == expect ? "" : "<- updates lost");
    std::printf("  %-26s = %8ld  %9.2f ns/increment\n", "std::atomic relaxed", c.atomic_,
                c.ns_atomic);
    std::printf("  %-26s = %8ld  %9.2f ns/lock\n", "std::mutex", c.locked, c.ns_locked);
    std::printf("  %-26s = %8ld  %9.2f ns/increment\n", "private + combine", c.reduced,
                c.ns_reduced);

    std::printf("\nfalse sharing (128-byte lines on this machine [S34])\n");
    std::printf("  adjacent long per thread   %6.2f ns/update\n", false_sharing_ns(tm, 400000, false));
    std::printf("  alignas(128) per thread    %6.2f ns/update\n", false_sharing_ns(tm, 400000, true));
}

static void bench() {
    const unsigned hw = std::thread::hardware_concurrency();
    std::printf("strong scaling of a compute-bound sum (std::thread pool)\n");
    std::printf("%8s%10s%10s%12s\n", "threads", "time[s]", "speedup", "efficiency");
    double t1 = 0;
    for (unsigned p = 1; p <= hw; p *= 2) {
        TaskManager tm(static_cast<int>(p) - 1);
        Timer t;
        volatile double s = heavy_sum(tm, static_cast<int>(p) * 8, 2'000'000 / p);
        (void)s;
        double dt = t.seconds();
        if (p == 1) t1 = dt;
        std::printf("%8u%10.4f%10.2f%12.2f\n", p, dt, t1 / dt, t1 / dt / p);
    }
    std::printf("\npool startup cost\n");
    for (unsigned p : {2u, 4u, 8u}) {
        Timer t;
        for (int r = 0; r < 20; ++r) TaskManager tm(static_cast<int>(p) - 1);
        std::printf("  create+join a %u-thread pool: %7.1f us\n", p, t.seconds() * 1e6 / 20);
    }
}

static void test() {
    TaskManager tm(3);
    CHECK(tm.size() == 4);

    // every task index is visited exactly once
    std::vector<int> hits(1000, 0);
    tm.run_parallel(1000, [&](int i, int n) {
        CHECK(n == 1000);
        hits[i] += 1;
    });
    for (int h : hits) CHECK(h == 1);

    // nested calls still terminate (the pool is not re-entered)
    std::atomic<int> total{0};
    tm.run_parallel(8, [&](int, int) { total.fetch_add(1); });
    CHECK(total.load() == 8);

    auto c = counters(tm, 50000);
    const long expect = static_cast<long>(tm.size()) * 50000;
    CHECK(c.atomic_ == expect);   // atomic is correct
    CHECK(c.reduced == expect);   // private accumulation is correct
    CHECK(c.locked == static_cast<long>(tm.size()) * (50000 / 50 + 1));
    // the racy counter is undefined behaviour; we only assert it cannot exceed
    // the true count, never that it is wrong (on a fast enough machine it may
    // happen to be right).
    CHECK(c.racy <= expect);
    // a private accumulator is at least as fast as an atomic one
    CHECK(c.ns_reduced <= c.ns_atomic);

    // the reduction reproduces the serial sum exactly (integers, so it must)
    std::vector<long> v(10000);
    for (std::size_t i = 0; i < v.size(); ++i) v[i] = static_cast<long>(i);
    std::vector<long> part(4, 0);
    tm.run_parallel(4, [&](int i, int n) {
        long s = 0;
        for (std::size_t k = i; k < v.size(); k += n) s += v[k];
        part[i] = s;
    });
    CHECK(std::accumulate(part.begin(), part.end(), 0L) ==
          std::accumulate(v.begin(), v.end(), 0L));

    std::printf("threads_cpp: all tests passed (%d threads)\n", tm.size());
}

int main(int argc, char** argv) {
    const std::string m = mode_of(argc, argv);
    if (m == "test") {
        test();
    } else if (m == "bench") {
        bench();
    } else {
        demo();
    }
    return 0;
}
