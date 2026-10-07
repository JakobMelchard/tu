// peterson_filter.cpp -- read/write mutual exclusion: Peterson, Filter, Bakery
// (Herlihy-Shavit ch. 2 [S1]; Peterson 1981 [S10]; Lamport 1974 [S11]).
//
// All three use only loads and stores, no read-modify-write. They are correct
// under sequential consistency, so every shared variable is a
// std::atomic with the default memory_order_seq_cst. The Peterson variant with
// relaxed / acquire-release orderings shows why: the store "flag[me] = true"
// may be delayed past the load of flag[other] (store buffer, note 03), and two
// threads enter together.
//
// Invariant checked in --test: an atomic occupancy counter incremented on
// entry must read 0 (nobody else inside), and a plain non-atomic counter
// incremented inside the critical section must end at n * iters (a lost update
// would mean two threads overlapped; TSan also flags it as a data race).
//
//   ./peterson_filter           demo
//   ./peterson_filter --test    invariants for Peterson (2), Filter, Bakery (2, 4)
//   ./peterson_filter --bench   ns per lock/unlock; overlaps of the weakened Peterson
#include <algorithm>
#include <memory>

#include "common.hpp"

using std::memory_order;
using std::memory_order_seq_cst;

// Peterson's lock for threads 0 and 1 [S1 §2.3]. Orderings are parameters so
// the demo can weaken them; the correct lock uses seq_cst for all four.
struct Peterson {
    std::atomic<bool> flag[2] = {{false}, {false}};
    std::atomic<int> victim{0};
    memory_order st = memory_order_seq_cst, ld = memory_order_seq_cst;
    void lock(int me) {
        int other = 1 - me;
        flag[me].store(true, st);  // I am interested
        victim.store(me, st);      // you go first
        while (flag[other].load(ld) && victim.load(ld) == me) cpu_relax();
    }
    void unlock(int me) { flag[me].store(false, memory_order_seq_cst); }
};

// Filter lock [S1 §2.4]: n-1 levels, each a generalised Peterson that lets at
// most n-L threads through level L. level[i] = highest level thread i wants.
struct Filter {
    int n;
    std::unique_ptr<std::atomic<int>[]> level, victim;
    explicit Filter(int n_) : n(n_), level(new std::atomic<int>[n_]), victim(new std::atomic<int>[n_]) {
        for (int i = 0; i < n; ++i) level[i] = 0, victim[i] = 0;
    }
    void lock(int me) {
        for (int L = 1; L < n; ++L) {
            level[me] = L;
            victim[L] = me;
            // spin while a conflicting thread is at my level or above and I am the victim
            for (;;) {
                bool conflict = false;
                for (int k = 0; k < n && !conflict; ++k)
                    if (k != me && level[k] >= L) conflict = true;
                if (!conflict || victim[L] != me) break;
                cpu_relax();
            }
        }
    }
    void unlock(int me) { level[me] = 0; }
};

// Lamport's bakery [S11] [S1 §2.6]: take a ticket one larger than every ticket
// seen, wait for all smaller (label, id) pairs. First-come-first-served after
// the doorway (the ticket-taking section). Labels are 64-bit: they grow without
// bound in theory (§2.7) but not within 2^63 acquisitions.
struct Bakery {
    int n;
    std::unique_ptr<std::atomic<bool>[]> flag;
    std::unique_ptr<std::atomic<uint64_t>[]> label;
    explicit Bakery(int n_) : n(n_), flag(new std::atomic<bool>[n_]), label(new std::atomic<uint64_t>[n_]) {
        for (int i = 0; i < n; ++i) flag[i] = false, label[i] = 0;
    }
    void lock(int me) {
        flag[me] = true;  // doorway begins
        uint64_t mx = 0;
        for (int k = 0; k < n; ++k) mx = std::max(mx, label[k].load());
        label[me] = mx + 1;  // doorway ends
        for (int k = 0; k < n; ++k) {
            if (k == me) continue;
            for (;;) {
                if (!flag[k]) break;
                uint64_t lk = label[k], lm = label[me];
                if (lk > lm || (lk == lm && k > me)) break;  // (lk,k) > (lm,me): I go first
                cpu_relax();
            }
        }
    }
    void unlock(int me) { flag[me] = false; }
};

// Runs n threads x iters acquisitions; returns the number of observed overlaps.
// When `plain` is true a non-atomic counter is also incremented and checked
// (only for locks that are supposed to be correct: a race on it is UB).
template <class Lock>
long hammer(Lock& lk, int n, long iters, bool plain, double* ns_per_op = nullptr) {
    std::atomic<int> inside{0};
    std::atomic<long> overlaps{0};
    long counter = 0;  // protected by lk, deliberately not atomic
    Timer t;
    run_threads(n, [&](int me) {
        for (long i = 0; i < iters; ++i) {
            lk.lock(me);
            if (inside.fetch_add(1) != 0) overlaps.fetch_add(1);
            if (plain) ++counter;
            inside.fetch_sub(1);
            lk.unlock(me);
        }
    });
    if (ns_per_op) *ns_per_op = t.seconds() * 1e9 / double(n * iters);
    if (plain) CHECK(counter == n * iters);
    return overlaps.load();
}

// Both threads call lock() at the same instant, round after round (spin
// barrier + jitter, as in memory_model.cpp). In a tight lock loop the waiter
// has long published its flag, so the store-buffer window is almost never hit;
// aligned arrivals are what expose it.
static long aligned_overlaps(Peterson& p, long rounds) {
    SpinBarrier bar(2);
    std::atomic<int> inside{0};
    std::atomic<long> overlaps{0};
    run_threads(2, [&](int me) {
        Rng rng(me + 5);
        bool sense = false;
        for (long i = 0; i < rounds; ++i) {
            bar.wait(sense);
            for (volatile unsigned k = 0, n = rng.below(32); k < n; ++k) {}
            p.lock(me);
            if (inside.fetch_add(1, std::memory_order_relaxed) != 0) overlaps.fetch_add(1);
            for (volatile int k = 0; k < 20; ++k) {}  // stay inside a little
            inside.fetch_sub(1, std::memory_order_relaxed);
            p.unlock(me);
        }
    });
    return overlaps.load();
}

static void test() {
    const long it = 20000 / kScale;
    { Peterson p; CHECK(hammer(p, 2, it, true) == 0); }
    { Peterson p; CHECK(aligned_overlaps(p, it) == 0); }  // seq_cst: never, even aligned
    for (int n : {2, 3, 4}) {
        Filter f(n); CHECK(hammer(f, n, it / n, true) == 0);
        Bakery b(n); CHECK(hammer(b, n, it / n, true) == 0);
    }
    // Filter with one thread has no levels: lock() must return at once.
    { Filter f(1); f.lock(0); f.unlock(0); }
    // Bakery doorway: a thread that finished its doorway before another started
    // gets a smaller label (the FCFS property of [S1 §2.6]), checked sequentially.
    {
        Bakery b(3);
        b.lock(0); uint64_t l0 = b.label[0]; b.unlock(0);
        b.lock(2); uint64_t l2 = b.label[2]; b.unlock(2);
        CHECK(l2 > l0);
    }
    std::printf("peterson_filter: Peterson(2), Filter(2..4), Bakery(2..4): no overlap, counters exact\n");
}

static void weakened(long rounds) {
    struct V { const char* name; memory_order st, ld; };
    V vs[] = {{"relaxed store / relaxed load", std::memory_order_relaxed, std::memory_order_relaxed},
              {"release store / acquire load", std::memory_order_release, std::memory_order_acquire},
              {"seq_cst (correct)           ", memory_order_seq_cst, memory_order_seq_cst}};
    for (auto& v : vs) {
        Peterson p; p.st = v.st; p.ld = v.ld;
        long ov = aligned_overlaps(p, rounds);
        std::printf("  Peterson %s : %7ld overlaps in %ld aligned rounds\n", v.name, ov, rounds);
    }
}

static void bench() {
    const long it = 200000;
    double ns;
    { Peterson p; hammer(p, 2, it, true, &ns); std::printf("Peterson   n=2 : %7.1f ns per lock+unlock\n", ns); }
    for (int n : {2, 4, 8}) {
        Filter f(n); hammer(f, n, it / n, true, &ns);
        std::printf("Filter     n=%d : %7.1f ns\n", n, ns);
        Bakery b(n); hammer(b, n, it / n, true, &ns);
        std::printf("Bakery     n=%d : %7.1f ns\n", n, ns);
    }
    std::printf("weakened Peterson (overlaps = mutual exclusion violated):\n");
    weakened(1000000);
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "test") { test(); return 0; }
    if (m == "bench") { bench(); return 0; }
    test();
    weakened(100000);
    return 0;
}
