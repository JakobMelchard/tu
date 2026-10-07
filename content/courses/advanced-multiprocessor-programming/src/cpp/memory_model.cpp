// memory_model.cpp -- litmus tests for the C++ memory model on this machine
// (note 03; cppreference [S20]; Boehm & Adve [S19]; x86-TSO [S23]; ARMv8 [S24];
// Preshing [S21]).
//
// A litmus test is a tiny two-thread program plus a question: "can this final
// outcome happen?". The C++ model answers per memory_order; the hardware may
// or may not actually produce an allowed outcome. Each round is separated by a
// spin barrier and a random delay, so both threads run the test body at almost
// the same instant; we count how often each outcome occurs.
//
//   MP (message passing)   T0: data=1; flag=1        T1: r1=flag; r2=data
//        forbidden with release/acquire: r1==1 && r2==0
//   SB (store buffering)   T0: x=1; r1=y             T1: y=1; r2=x
//        forbidden only with seq_cst: r1==0 && r2==0 (x86 and ARM both allow it
//        for release/acquire, because a store may sit in the store buffer)
//   LB (load buffering)    T0: r1=x; y=1             T1: r2=y; x=1
//        allowed with relaxed: r1==1 && r2==1 (ARM hardware may; x86 never)
//
// --test asserts only what the C++ model FORBIDS never occurs; how often an
// ALLOWED weak outcome occurs is a property of the hardware, reported in --bench.
//
//   ./memory_model           demo (short run of all three)
//   ./memory_model --test    forbidden outcomes never observed
//   ./memory_model --bench   outcome statistics, 10^6 rounds each
#include "common.hpp"

using mo = std::memory_order;
constexpr mo rlx = std::memory_order_relaxed, acq = std::memory_order_acquire,
             rel = std::memory_order_release, sc = std::memory_order_seq_cst;

// Busy-wait a random number of iterations (0..63) to jitter thread alignment.
static inline void jitter(Rng& r) {
    unsigned n = r.below(64);
    for (volatile unsigned i = 0; i < n; ++i) {}
}

struct Counts { long both_weak = 0, rounds = 0; };

// Runs `rounds` rounds of a two-thread litmus body; body0/body1 return their
// register values; weak(r1, r2) says whether the pair is the weak outcome.
template <class Reset, class B0, class B1, class Weak>
Counts litmus(long rounds, Reset reset, B0 body0, B1 body1, Weak weak) {
    SpinBarrier bar(2);
    std::vector<int> r1(rounds), r2(rounds);
    auto worker = [&](int me) {
        Rng rng(me + 17);
        bool sense = false;
        for (long i = 0; i < rounds; ++i) {
            if (me == 0) reset();
            bar.wait(sense);  // reset visible to both
            jitter(rng);
            if (me == 0) r1[i] = body0(); else r2[i] = body1();
            bar.wait(sense);  // both done before the next reset
        }
    };
    run_threads(2, worker);
    Counts c;
    c.rounds = rounds;
    for (long i = 0; i < rounds; ++i) c.both_weak += weak(r1[i], r2[i]);
    return c;
}

std::atomic<int> X, Y, DATA, FLAG;

Counts mp(long n, mo st, mo ld) {
    return litmus(n, [] { DATA.store(0, rlx); FLAG.store(0, rlx); },
        [&] { DATA.store(1, rlx); FLAG.store(1, st); return 0; },
        [&] { int f = FLAG.load(ld); int d = DATA.load(rlx); return f * 2 + d; },
        [](int, int r) { return r == 2; });  // flag seen, data not
}
Counts sb(long n, mo st, mo ld) {
    return litmus(n, [] { X.store(0, rlx); Y.store(0, rlx); },
        [&] { X.store(1, st); return Y.load(ld); },
        [&] { Y.store(1, st); return X.load(ld); },
        [](int a, int b) { return a == 0 && b == 0; });
}
Counts sb_fence(long n) {  // relaxed accesses + seq_cst fences between them
    return litmus(n, [] { X.store(0, rlx); Y.store(0, rlx); },
        [&] { X.store(1, rlx); std::atomic_thread_fence(sc); return Y.load(rlx); },
        [&] { Y.store(1, rlx); std::atomic_thread_fence(sc); return X.load(rlx); },
        [](int a, int b) { return a == 0 && b == 0; });
}
Counts lb(long n, mo ld, mo st) {
    return litmus(n, [] { X.store(0, rlx); Y.store(0, rlx); },
        [&] { int r = X.load(ld); Y.store(1, st); return r; },
        [&] { int r = Y.load(ld); X.store(1, st); return r; },
        [](int a, int b) { return a == 1 && b == 1; });
}

static void report(const char* name, Counts c, bool allowed) {
    std::printf("  %-44s weak outcome %7ld / %ld  (%s by C++)\n", name, c.both_weak, c.rounds,
                allowed ? "allowed" : "FORBIDDEN");
}

static void test() {
    const long n = 100000 / kScale;
    CHECK(mp(n, rel, acq).both_weak == 0);
    CHECK(mp(n, sc, sc).both_weak == 0);
    CHECK(sb(n, sc, sc).both_weak == 0);
    CHECK(sb_fence(n).both_weak == 0);
    CHECK(lb(n, acq, rel).both_weak == 0);  // acquire load then release store: no LB
    // Coherence: a single atomic variable has one modification order that every
    // thread respects, even when relaxed. Two readers of increments by one
    // writer never see the value go backwards.
    std::atomic<int> v{0};
    std::atomic<bool> bad{false};
    run_threads(3, [&](int me) {
        if (me == 0) { for (int i = 1; i <= 200000 / kScale; ++i) v.store(i, rlx); return; }
        int last = 0;
        for (int i = 0; i < 200000 / kScale; ++i) {
            int x = v.load(rlx);
            if (x < last) bad = true;
            last = x;
        }
    });
    CHECK(!bad);
    std::printf("memory_model: forbidden MP/SB/LB outcomes never observed; coherence holds\n");
}

static void stats(long n) {
    std::printf("litmus statistics on this machine (%ld rounds each):\n", n);
    report("MP  relaxed flag", mp(n, rlx, rlx), true);
    report("MP  release/acquire flag", mp(n, rel, acq), false);
    report("SB  relaxed", sb(n, rlx, rlx), true);
    report("SB  release/acquire", sb(n, rel, acq), true);
    report("SB  seq_cst", sb(n, sc, sc), false);
    report("SB  relaxed + seq_cst fences", sb_fence(n), false);
    report("LB  relaxed", lb(n, rlx, rlx), true);
    report("LB  acquire/release", lb(n, acq, rel), false);
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "test") { test(); return 0; }
    if (m == "bench") { stats(1000000); return 0; }
    test();
    stats(100000);
    return 0;
}
