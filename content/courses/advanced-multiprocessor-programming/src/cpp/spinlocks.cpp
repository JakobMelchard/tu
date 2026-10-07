// spinlocks.cpp -- TAS, TTAS, TTAS + exponential backoff, CLH, MCS
// (Herlihy-Shavit ch. 7 [S1]; Mellor-Crummey & Scott 1991 [S13]).
//
// TAS    spins on exchange(true): every spin iteration is a write, so the lock's
//        cache line bounces between all waiters (coherence traffic, note 05).
// TTAS   spins on a plain load (hits in the local cache) and only tries the
//        exchange when the lock looks free. On release all waiters miss at once.
// Backoff after a failed exchange, wait a random time in [0, limit), double
//        the limit up to a cap: fewer simultaneous attempts.
// CLH    implicit queue: each thread spins on its PREDECESSOR's node; unlock
//        clears its own node, which the successor is watching. FIFO. Needs a
//        node recycled from the predecessor (the "node swap").
// MCS    explicit queue: each thread spins on its OWN node; unlock hands the
//        lock to the successor through node->next. FIFO, local spinning even
//        without coherent caches, O(1) remote references per acquisition [S13].
//
// --test: 4 threads x N acquisitions per lock, occupancy invariant, exact
//         non-atomic counter, and FIFO hand-off for CLH/MCS (sequence check).
// --bench: ns per acquisition and fairness (min/max acquisitions per thread
//          in a fixed time window) for 1, 2, 4, 8 threads.
#include <mutex>

#include "common.hpp"

constexpr auto rlx = std::memory_order_relaxed, acq = std::memory_order_acquire,
               rel = std::memory_order_release, acq_rel = std::memory_order_acq_rel;

// Every lock takes a per-thread handle so CLH/MCS can keep their queue node.
struct TAS {
    struct Handle {};
    std::atomic<bool> held{false};
    void lock(Handle&) { while (held.exchange(true, acq)) cpu_relax(); }
    void unlock(Handle&) { held.store(false, rel); }
};

struct TTAS {
    struct Handle {};
    std::atomic<bool> held{false};
    void lock(Handle&) {
        for (;;) {
            while (held.load(rlx)) cpu_relax();          // local spinning
            if (!held.exchange(true, acq)) return;       // looked free: try
        }
    }
    void unlock(Handle&) { held.store(false, rel); }
};

struct Backoff {
    struct Handle { Rng rng{uint64_t(std::hash<std::thread::id>{}(std::this_thread::get_id()))}; };
    std::atomic<bool> held{false};
    static constexpr unsigned kMin = 4, kMax = 1024;
    void lock(Handle& h) {
        unsigned limit = kMin;
        for (;;) {
            while (held.load(rlx)) cpu_relax();
            if (!held.exchange(true, acq)) return;
            unsigned d = h.rng.below(limit);             // random delay in [0, limit)
            for (unsigned i = 0; i < d; ++i) cpu_relax();
            if (limit < kMax) limit *= 2;
        }
    }
    void unlock(Handle&) { held.store(false, rel); }
};

struct alignas(128) QNodeCLH { std::atomic<bool> locked{false}; };

struct CLH {
    struct Handle {
        QNodeCLH* mine = new QNodeCLH;
        QNodeCLH* pred = nullptr;
        ~Handle() { delete mine; }
    };
    std::atomic<QNodeCLH*> tail;
    QNodeCLH sentinel;  // initial tail, unlocked
    CLH() : tail(&sentinel) {}
    void lock(Handle& h) {
        h.mine->locked.store(true, rlx);
        h.pred = tail.exchange(h.mine, acq_rel);         // enqueue: linearisation point
        while (h.pred->locked.load(acq)) cpu_relax();    // spin on predecessor
    }
    void unlock(Handle& h) {
        QNodeCLH* me = h.mine;
        me->locked.store(false, rel);                    // successor sees this
        // Recycle the predecessor's node: nobody spins on it any more, while my
        // old node may still be watched by my successor.
        // The sentinel is a member of the lock, not heap: replace it by a fresh node.
        h.mine = (h.pred == &sentinel) ? new QNodeCLH : h.pred;
    }
    // Ownership: each Handle owns exactly its `mine`; the node at the tail after
    // the last unlock belongs to no handle and is freed here.
    ~CLH() {
        QNodeCLH* t = tail.load();
        if (t != &sentinel) delete t;   // the last released node is owned by nobody
    }
};

struct alignas(128) QNodeMCS {
    std::atomic<QNodeMCS*> next{nullptr};
    std::atomic<bool> locked{false};
};

struct MCS {
    struct Handle { QNodeMCS node; };
    std::atomic<QNodeMCS*> tail{nullptr};
    void lock(Handle& h) {
        QNodeMCS* q = &h.node;
        q->next.store(nullptr, rlx);
        q->locked.store(true, rlx);
        QNodeMCS* pred = tail.exchange(q, acq_rel);
        if (pred) {
            pred->next.store(q, rel);                    // make myself findable
            while (q->locked.load(acq)) cpu_relax();     // spin on my own node
        }
    }
    void unlock(Handle& h) {
        QNodeMCS* q = &h.node;
        QNodeMCS* succ = q->next.load(acq);
        if (!succ) {
            QNodeMCS* expected = q;
            if (tail.compare_exchange_strong(expected, nullptr, acq_rel, rlx)) return;  // no waiter
            while (!(succ = q->next.load(acq))) cpu_relax();  // waiter is linking in
        }
        succ->locked.store(false, rel);                  // hand over
    }
};

struct StdMutex {
    struct Handle {};
    std::mutex m;
    void lock(Handle&) { m.lock(); }
    void unlock(Handle&) { m.unlock(); }
};

// Mutual exclusion invariant + exact counter.
template <class L>
void check_lock(int n, long iters) {
    L lk;
    std::atomic<int> inside{0};
    long counter = 0;
    run_threads(n, [&](int) {
        typename L::Handle h;
        for (long i = 0; i < iters; ++i) {
            lk.lock(h);
            CHECK(inside.fetch_add(1, rlx) == 0);
            ++counter;
            inside.fetch_sub(1, rlx);
            lk.unlock(h);
        }
    });
    CHECK(counter == n * iters);
}

// FIFO: a thread whose tail.exchange precedes another's is served first. Hold
// the lock in the main thread, start threads one at a time and wait until each
// has visibly swapped itself into `tail`, release, record the service order.
template <class L>
void check_fifo(int n) {
    L lk;
    typename L::Handle mh;
    lk.lock(mh);
    std::vector<int> order;
    std::vector<std::thread> ts;
    for (int i = 0; i < n; ++i) {
        auto before = lk.tail.load();
        ts.emplace_back([&, i] {
            typename L::Handle h;
            lk.lock(h);
            order.push_back(i);  // protected by the lock
            lk.unlock(h);
        });
        while (lk.tail.load() == before) cpu_relax();  // thread i is enqueued
    }
    lk.unlock(mh);
    for (auto& t : ts) t.join();
    for (int i = 0; i < n; ++i) CHECK(order[i] == i);
}

static void test() {
    const long it = 50000 / kScale;
    check_lock<TAS>(4, it);
    check_lock<TTAS>(4, it);
    check_lock<Backoff>(4, it);
    check_lock<CLH>(4, it);
    check_lock<MCS>(4, it);
    check_fifo<CLH>(4);
    check_fifo<MCS>(4);
    std::printf("spinlocks: TAS/TTAS/Backoff/CLH/MCS exclusive and exact; CLH, MCS serve FIFO\n");
}

// Throughput and fairness over a fixed window with a short critical section.
template <class L>
void bench_one(const char* name, int n) {
    L lk;
    std::atomic<bool> stop{false}, go{false};
    std::vector<long> got(n);
    long shared = 0;
    std::vector<std::thread> ts;
    for (int t = 0; t < n; ++t)
        ts.emplace_back([&, t] {
            typename L::Handle h;
            long c = 0;
            while (!go.load(acq)) cpu_relax();
            while (!stop.load(rlx)) {
                lk.lock(h);
                shared += 1;                             // tiny critical section
                lk.unlock(h);
                ++c;
            }
            got[t] = c;
        });
    Timer tm;
    go.store(true, rel);
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    stop.store(true);
    for (auto& th : ts) th.join();
    double secs = tm.seconds();
    long tot = 0, mn = got[0], mx = got[0];
    for (long g : got) tot += g, mn = std::min(mn, g), mx = std::max(mx, g);
    CHECK(shared == tot);
    std::printf("  %-8s n=%d  %7.1f ns/acq   fairness min/max = %.2f\n", name, n,
                secs * 1e9 / double(tot), double(mn) / double(mx));
}

static void bench() {
    for (int n : {1, 2, 4, 8}) {
        bench_one<TAS>("TAS", n);
        bench_one<TTAS>("TTAS", n);
        bench_one<Backoff>("Backoff", n);
        bench_one<CLH>("CLH", n);
        bench_one<MCS>("MCS", n);
        bench_one<StdMutex>("mutex", n);
    }
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "test") { test(); return 0; }
    if (m == "bench") { bench(); return 0; }
    test();
    bench_one<TAS>("TAS", 4);
    bench_one<MCS>("MCS", 4);
    return 0;
}
