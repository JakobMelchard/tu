// work_stealing.cpp -- Chase-Lev work-stealing deque + a fork-join scheduler
// (Chase & Lev 2005 [S9]; C11 orderings from Le, Pop, Cohen & Zappa Nardelli
// 2013, Fig. 1 [S25]; Blumofe & Leiserson 1999 [S8]; Herlihy-Shavit ch. 16 [S1]).
//
// Deque: the OWNER pushes and takes at the bottom (LIFO, no CAS except when
// one element is left); THIEVES steal at the top (FIFO) with one CAS on
// `top`. The circular array grows when full; old arrays are kept until the
// deque dies, because a thief may still be reading one.
// The two seq_cst fences are the whole difficulty: take() must publish its
// decrement of `bottom` before reading `top`, and steal() must read `top`
// before `bottom` -- a store-load order that only seq_cst provides (note 03).
// ThreadSanitizer does not model standalone fences, so under -fsanitize=thread
// the fences are replaced by seq_cst/release accesses (equally correct, slower).
//
// Scheduler: one deque per worker. spawn(t) pushes t on my deque; sync(t)
// runs my own tasks or steals until t is done (the parent waits by helping).
// A worker with an empty deque steals from a random victim.
//
//   ./work_stealing    demo    ./work_stealing --test    ./work_stealing --bench
#include <algorithm>
#include <functional>
#include <memory>

#include "common.hpp"

constexpr auto rlx = std::memory_order_relaxed, acq = std::memory_order_acquire,
               rel = std::memory_order_release, sc = std::memory_order_seq_cst;
constexpr auto kBotPub = AMP_TSAN ? sc : rlx;   // store of bottom after the fence
constexpr auto kLd = AMP_TSAN ? sc : rlx;
static inline void fence_sc() { if (!AMP_TSAN) std::atomic_thread_fence(sc); }
static inline void fence_rel() { if (!AMP_TSAN) std::atomic_thread_fence(rel); }

enum class R { OK, EMPTY, ABORT };

template <class T>
class ChaseLev {
    struct Array {
        int64_t cap; std::unique_ptr<std::atomic<T>[]> buf;
        explicit Array(int64_t c) : cap(c), buf(new std::atomic<T>[size_t(c)]) {}
        T get(int64_t i) const { return buf[size_t(i & (cap - 1))].load(rlx); }
        void put(int64_t i, T x) { buf[size_t(i & (cap - 1))].store(x, rlx); }
    };
    alignas(128) std::atomic<int64_t> top_{0};
    alignas(128) std::atomic<int64_t> bottom_{0};
    std::atomic<Array*> array_;
    std::vector<std::unique_ptr<Array>> all_;             // owner-only: every array ever used
  public:
    explicit ChaseLev(int64_t cap = 64) { all_.emplace_back(new Array(cap)); array_ = all_.back().get(); }
    void push(T x) {                                      // owner
        int64_t b = bottom_.load(rlx), t = top_.load(acq);
        Array* a = array_.load(rlx);
        if (b - t > a->cap - 1) {                         // full: grow, copy live range [t, b)
            all_.emplace_back(new Array(2 * a->cap));
            Array* na = all_.back().get();
            for (int64_t i = t; i < b; ++i) na->put(i, a->get(i));
            array_.store(na, rel);
            a = na;
        }
        a->put(b, x);
        fence_rel();
        bottom_.store(b + 1, AMP_TSAN ? rel : rlx);       // publish
    }
    R take(T& out) {                                      // owner
        int64_t b = bottom_.load(rlx) - 1;
        Array* a = array_.load(rlx);
        bottom_.store(b, kBotPub);                        // reserve the bottom element ...
        fence_sc();                                       // ... BEFORE looking at top
        int64_t t = top_.load(kLd);
        if (t > b) { bottom_.store(b + 1, rlx); return R::EMPTY; }
        out = a->get(b);
        if (t < b) return R::OK;                          // more than one left: no race possible
        // exactly one element: race the thieves for it with the same CAS they use
        bool won = top_.compare_exchange_strong(t, t + 1, sc, rlx);
        bottom_.store(b + 1, rlx);
        return won ? R::OK : R::EMPTY;
    }
    R steal(T& out) {                                     // any thread
        int64_t t = top_.load(AMP_TSAN ? sc : acq);
        fence_sc();                                       // read top BEFORE bottom
        int64_t b = bottom_.load(AMP_TSAN ? sc : acq);
        if (t >= b) return R::EMPTY;
        Array* a = array_.load(acq);
        T x = a->get(t);
        if (!top_.compare_exchange_strong(t, t + 1, sc, rlx)) return R::ABORT;  // lost to a thief or the owner
        out = x; return R::OK;
    }
    int64_t capacity() const { return array_.load()->cap; }
};

// ---------------------------------------------------------------- scheduler
struct Task { std::function<void()> f; std::atomic<bool> done{false}; };

class Pool {
    int P_;
    std::vector<std::unique_ptr<ChaseLev<Task*>>> dq_;
    std::vector<std::thread> th_;
    std::atomic<bool> stop_{false};
    static thread_local int me_;
    bool try_run_one(Rng& r) {
        Task* t;
        if (dq_[size_t(me_)]->take(t) == R::OK) { run(t); return true; }
        int v = int(r.below(uint32_t(P_)));
        if (v != me_ && dq_[size_t(v)]->steal(t) == R::OK) { steals.fetch_add(1, rlx); run(t); return true; }
        return false;
    }
    static void run(Task* t) { t->f(); t->done.store(true, rel); }
  public:
    std::atomic<long> steals{0};
    explicit Pool(int P) : P_(P) {
        for (int i = 0; i < P; ++i) dq_.emplace_back(new ChaseLev<Task*>(16));
        for (int i = 1; i < P; ++i)
            th_.emplace_back([this, i] {
                me_ = i; Rng r(uint64_t(i) * 7919);
                while (!stop_.load(acq)) if (!try_run_one(r)) cpu_relax();
            });
    }
    ~Pool() { stop_.store(true, rel); for (auto& t : th_) t.join(); }
    template <class F> void root(F f) { me_ = 0; f(); }   // the calling thread is worker 0
    void spawn(Task* t) { dq_[size_t(me_)]->push(t); }
    void sync(Task* t) {                                  // help until t is done
        Rng r(uint64_t(me_) + 1);
        while (!t->done.load(acq)) if (!try_run_one(r)) cpu_relax();
    }
};
thread_local int Pool::me_ = 0;

static long fib_seq(int n) { return n < 2 ? n : fib_seq(n - 1) + fib_seq(n - 2); }
static long fib(Pool& p, int n) {
    if (n < 16) return fib_seq(n);                        // cutoff: tasks must be worth a steal
    long x = 0;
    Task t; t.f = [&] { x = fib(p, n - 1); };
    p.spawn(&t);                                          // child may be stolen ...
    long y = fib(p, n - 2);                               // ... while the parent continues
    p.sync(&t);
    return x + y;
}
static void qsort_par(Pool& p, int* a, long n) {
    if (n < 2048) { std::sort(a, a + n); return; }
    int piv = a[n / 2];
    int* mid1 = std::partition(a, a + n, [piv](int v) { return v < piv; });
    int* mid2 = std::partition(mid1, a + n, [piv](int v) { return v == piv; });
    Task t; t.f = [&] { qsort_par(p, a, mid1 - a); };
    p.spawn(&t);
    qsort_par(p, mid2, a + n - mid2);
    p.sync(&t);
}

static void test() {
    {   // sequential semantics: owner LIFO, thief FIFO, growth from capacity 4
        ChaseLev<int64_t> d(4); int64_t x;
        for (int64_t i = 1; i <= 100; ++i) d.push(i);
        CHECK(d.capacity() >= 128);
        CHECK(d.take(x) == R::OK && x == 100);
        CHECK(d.steal(x) == R::OK && x == 1);
        int64_t cnt = 2; while (d.take(x) == R::OK) ++cnt;
        CHECK(cnt == 100 && d.steal(x) == R::EMPTY && d.take(x) == R::EMPTY);
    }
    {   // concurrent: owner pushes/takes, 3 thieves steal; every item exactly once
        const int64_t N = 200000 / kScale;
        ChaseLev<int64_t> d(8);
        std::vector<std::atomic<int>> seen(static_cast<size_t>(N));
        for (auto& s : seen) s = 0;
        std::atomic<bool> fin{false};
        std::atomic<long> stolen{0};
        run_threads(4, [&](int t) {
            int64_t x;
            if (t == 0) {
                Rng r(1);
                for (int64_t i = 0; i < N; ++i) {
                    d.push(i);
                    if (r.below(3) == 0 && d.take(x) == R::OK) seen[size_t(x)].fetch_add(1);
                }
                while (d.take(x) == R::OK) seen[size_t(x)].fetch_add(1);
                fin = true;
            } else {
                while (!fin.load()) if (d.steal(x) == R::OK) { seen[size_t(x)].fetch_add(1); stolen.fetch_add(1); }
            }
        });
        for (auto& s : seen) CHECK(s.load() == 1);
        std::printf("  deque: %lld items, %ld stolen, each obtained exactly once\n", (long long)N, stolen.load());
    }
    {
        Pool p(4); long r = 0;
        p.root([&] { r = fib(p, 24); });
        CHECK(r == 46368);
        std::vector<int> v(200000 / size_t(kScale)); Rng g(3);
        for (auto& x : v) x = int(g.below(1000000));
        std::vector<int> ref = v; std::sort(ref.begin(), ref.end());
        p.root([&] { qsort_par(p, v.data(), long(v.size())); });
        CHECK(v == ref);
        std::printf("  scheduler: fib(24) = 46368, parallel quicksort == std::sort (%ld steals)\n", p.steals.load());
    }
    std::printf("work_stealing: ok\n");
}

static void bench() {
    const int n = 40;
    Timer t0; long ref = fib_seq(n); double ts = t0.seconds();
    std::printf("  fib(%d) serial %.3f s\n", n, ts);
    for (int P : {1, 2, 4, 8}) {
        Pool p(P); long r = 0; Timer t;
        p.root([&] { r = fib(p, n); });
        double tp = t.seconds();
        CHECK(r == ref);
        std::printf("  fib(%d) P=%d  %.3f s  speedup vs serial %.2f  steals %ld\n", n, P, tp, ts / tp, p.steals.load());
    }
    std::vector<int> base(4000000); Rng g(5);
    for (auto& x : base) x = int(g.below(1u << 30));
    std::vector<int> v = base; Timer ts2; std::sort(v.begin(), v.end()); double tss = ts2.seconds();
    for (int P : {1, 2, 4, 8}) {
        Pool p(P); v = base; Timer t;
        p.root([&] { qsort_par(p, v.data(), long(v.size())); });
        std::printf("  quicksort 4e6 P=%d  %.3f s  (std::sort %.3f s)\n", P, t.seconds(), tss);
    }
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "bench") { bench(); return 0; }
    test();
    return 0;
}
