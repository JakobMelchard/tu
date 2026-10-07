// hazard_pointers.cpp -- safe memory reclamation for lock-free structures:
// hazard pointers (Michael 2004 [S26]) and epoch-based reclamation (Fraser
// 2004, §5.2.3 [S27]), both applied to a Treiber stack (note 08).
//
// The problem: pop() reads top = t and then t->next. If another thread pops t
// and frees it in between, that read is a use-after-free (and a recycled t is
// the ABA problem). Reclamation must delay free(t) until no thread can still
// hold t.
// Hazard pointers: before dereferencing t, publish it in a per-thread slot
//   and re-check that t is still reachable. retire(t) puts t on a private
//   list; when the list reaches R = 2H entries (H = number of slots), scan all
//   slots and free every retired node no slot names. At most H nodes per
//   thread stay unfreed; amortised O(1) per retire [S26].
// Epochs: a thread announces the global epoch e on entering an operation.
//   A node retired in epoch e is freed once the global epoch reaches e + 2;
//   the epoch advances only when every ACTIVE thread has announced the current
//   one. Cheaper per access than HP, but one stalled thread blocks all
//   reclamation (unbounded garbage).
//
// Test mode does not free: it POISONS (alive = 0, memory kept), so a late
// access is counted instead of being undefined behaviour. The "unsafe"
// reclaimer poisons at once and shows the violations the other two prevent.
//
//   ./hazard_pointers    demo    ./hazard_pointers --test    ./hazard_pointers --bench
#include <array>
#include <mutex>

#include "common.hpp"

constexpr auto rlx = std::memory_order_relaxed, acq = std::memory_order_acquire,
               rel = std::memory_order_release, sc = std::memory_order_seq_cst;
constexpr int kMaxThreads = 16;

struct Node { long value = 0; std::atomic<Node*> next{nullptr}; std::atomic<int> alive{1}; };

// Shared by all reclaimers: poison-or-delete, counters, graveyard.
struct Disposer {
    bool poison;
    std::atomic<long> retired{0}, freed{0};
    std::mutex gm; std::vector<Node*> graveyard;
    explicit Disposer(bool p) : poison(p) {}
    void dispose(Node* n) {
        freed.fetch_add(1, rlx);
        if (!poison) { delete n; return; }
        n->alive.store(0, rel);
        std::lock_guard<std::mutex> g(gm); graveyard.push_back(n);
    }
    ~Disposer() { for (Node* n : graveyard) delete n; }
};

struct alignas(128) Slot { std::atomic<Node*> p{nullptr}; std::vector<Node*> rlist; };

struct HazardPointers : Disposer {
    std::array<Slot, kMaxThreads> s;
    int nthreads;
    HazardPointers(int n, bool poison) : Disposer(poison), nthreads(n) {}
    void enter(int) {}
    void leave(int t) { s[size_t(t)].p.store(nullptr, rel); }
    Node* protect(int t, std::atomic<Node*>& src) {
        Node* p = src.load(acq);
        for (;;) {
            s[size_t(t)].p.store(p, sc);                    // publish ...
            Node* q = src.load(sc);                         // ... then validate (store-load order: seq_cst)
            if (q == p) return p;                           // p was reachable after it became hazardous
            p = q;
        }
    }
    void retire(int t, Node* n) {
        retired.fetch_add(1, rlx);
        auto& rl = s[size_t(t)].rlist;
        rl.push_back(n);
        if (rl.size() >= size_t(2 * nthreads)) scan(t);     // R = 2H with H = nthreads x 1 slot
    }
    void scan(int t) {
        std::vector<Node*> hazards;
        for (int i = 0; i < nthreads; ++i) if (Node* h = s[size_t(i)].p.load(sc)) hazards.push_back(h);
        auto& rl = s[size_t(t)].rlist;
        std::vector<Node*> keep;
        for (Node* n : rl) {
            bool hz = false;
            for (Node* h : hazards) hz |= (h == n);
            if (hz) keep.push_back(n); else dispose(n);
        }
        rl.swap(keep);
    }
    void quiesce() { for (int t = 0; t < nthreads; ++t) scan(t); }  // all slots clear: frees everything
};

struct Epochs : Disposer {
    struct alignas(128) Local { std::atomic<unsigned> epoch{0}; std::atomic<bool> active{false}; unsigned seen = 0; std::array<std::vector<Node*>, 3> limbo; long ops = 0; };
    std::atomic<unsigned> global{0};
    std::array<Local, kMaxThreads> l;
    int nthreads;
    Epochs(int n, bool poison) : Disposer(poison), nthreads(n) {}
    void try_advance() {
        unsigned e = global.load(sc);
        for (int i = 0; i < nthreads; ++i)
            if (l[size_t(i)].active.load(sc) && l[size_t(i)].epoch.load(sc) != e) return;  // someone lags
        global.compare_exchange_strong(e, e + 1, sc);
    }
    void enter(int t) {
        Local& me = l[size_t(t)];
        if (++me.ops % 32 == 0) try_advance();
        me.active.store(true, sc);
        unsigned e = global.load(sc);
        me.epoch.store(e, sc);
        std::atomic_thread_fence(sc);                       // announcement before any shared read
        if (e != me.seen) {                                 // new epoch: limbo[e%3] holds epoch <= e-3
            me.seen = e;
            for (Node* n : me.limbo[e % 3]) dispose(n);
            me.limbo[e % 3].clear();
        }
    }
    void leave(int t) { l[size_t(t)].active.store(false, rel); }
    Node* protect(int, std::atomic<Node*>& src) { return src.load(acq); }
    void retire(int t, Node* n) { retired.fetch_add(1, rlx); l[size_t(t)].limbo[l[size_t(t)].seen % 3].push_back(n); }
    void quiesce() { for (int t = 0; t < nthreads; ++t) for (auto& v : l[size_t(t)].limbo) { for (Node* n : v) dispose(n); v.clear(); } }
};

struct Unsafe : Disposer {                                  // frees at once: the bug being prevented
    Unsafe(int, bool poison) : Disposer(poison) {}
    void enter(int) {}
    void leave(int) {}
    Node* protect(int, std::atomic<Node*>& src) { return src.load(acq); }
    void retire(int, Node* n) { retired.fetch_add(1, rlx); dispose(n); }
    void quiesce() {}
};

template <class Rec>
struct Stack {
    std::atomic<Node*> top{nullptr};
    Rec& rec;
    std::atomic<long> violations{0};
    int window = 0;  // spins between obtaining p and touching it: widens the race
    explicit Stack(Rec& r) : rec(r) {}
    void push(int t, long v) {
        Node* n = new Node; n->value = v;
        rec.enter(t);
        Node* old = top.load(acq);
        do n->next.store(old, rlx); while (!top.compare_exchange_weak(old, n, rel, acq));
        rec.leave(t);
    }
    bool pop(int t, long* v) {
        rec.enter(t);
        for (;;) {
            Node* p = rec.protect(t, top);
            if (!p) { rec.leave(t); return false; }
            for (int i = 0; i < window; ++i) cpu_relax();
            if (p->alive.load(acq) == 0) violations.fetch_add(1, rlx);  // touching freed memory
            Node* nx = p->next.load(acq);
            if (top.compare_exchange_strong(p, nx, acq, rlx)) {
                *v = p->value;
                rec.leave(t);
                rec.retire(t, p);
                return true;
            }
        }
    }
    ~Stack() { Node* p = top.load(); while (p) { Node* n = p->next.load(); delete p; p = n; } }
};

template <class Rec>
static long run(const char* name, int T, long per, bool poison, bool print, double* secs = nullptr, int window = 0) {
    Rec rec(T, poison);
    long viol;
    {
        Stack<Rec> st(rec);
        st.window = window;
        for (long i = 0; i < 64; ++i) st.push(0, i);
        Timer tm;
        run_threads(T, [&](int t) {
            long v;
            for (long i = 0; i < per; ++i) { st.push(t, i); st.pop(t, &v); }
        });
        if (secs) *secs = tm.seconds();
        long before = rec.freed.load();
        rec.quiesce();
        viol = st.violations.load();
        if (print) std::printf("  %-6s w=%-3d T=%d  retired %8ld  freed during run %8ld  after quiesce %8ld  violations %ld\n",
                               name, window, T, rec.retired.load(), before, rec.freed.load(), viol);
        CHECK(rec.freed.load() == rec.retired.load());      // nothing leaked, nothing freed twice
        if (!std::is_same_v<Rec, Unsafe>) CHECK(before > 0);  // reclamation happened DURING the run
    }
    return viol;
}

static void test() {
    const long per = 100000 / kScale;
    std::printf("hazard_pointers:\n");
    for (int w : {0, 64}) {                                 // w = 64: a wide window, still no violation
        CHECK(run<HazardPointers>("HP", 4, per / (w ? 4 : 1), true, true, nullptr, w) == 0);
        CHECK(run<Epochs>("epochs", 4, per / (w ? 4 : 1), true, true, nullptr, w) == 0);
    }
    // HP bound: after a scan at most H hazards survive, so a thread's list stays below 2H.
    {
        HazardPointers hp(4, true); Node* ns[64];
        for (auto& n : ns) n = new Node;
        hp.s[1].p.store(ns[0]);                             // thread 1 protects ns[0]
        for (auto* n : ns) hp.retire(0, n);
        CHECK(hp.s[0].rlist.size() < 8);
        bool kept = false; for (Node* n : hp.s[0].rlist) kept |= (n == ns[0]);
        CHECK(kept && ns[0]->alive.load() == 1);            // the protected node was not freed
        hp.s[1].p.store(nullptr); hp.quiesce();
        CHECK(hp.freed.load() == 64);
    }
    std::printf("  no use-after-free with HP or epochs; every retired node freed exactly once\n");
}

static void bench() {
    std::printf("unsafe immediate free (poisoned, counted):\n");
    for (int w : {0, 64}) for (int T : {2, 4, 8}) run<Unsafe>("unsafe", T, 100000, true, true, nullptr, w);
    std::printf("real delete, push+pop pairs:\n");
    for (int T : {1, 2, 4, 8}) {
        const long per = 300000; double a, b;
        run<HazardPointers>("hp", T, per, false, false, &a);
        run<Epochs>("ebr", T, per, false, false, &b);
        std::printf("  T=%d  hazard pointers %6.1f ns/pair   epochs %6.1f ns/pair\n", T, a * 1e9 / double(per), b * 1e9 / double(per));
    }
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "bench") { bench(); return 0; }
    test();
    if (m.empty()) run<Unsafe>("unsafe", 4, 100000, true, true, nullptr, 64);
    return 0;
}
