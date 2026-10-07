// treiber_stack.cpp -- lock-free stack, the ABA problem, elimination backoff
// (Treiber 1986 [S12]; Herlihy-Shavit ch. 10-11 [S1]; Hendler, Shavit &
// Yerushalmi 2004 [S17]).
//
// Nodes live in an array and are named by 32-bit indices; freed nodes go back
// to a free list, which is itself a Treiber stack (as in Michael-Scott [S14]).
// `top` is 64 bits: [tag:32 | index:32]. Every successful CAS increments the
// tag, so a top that went A -> B -> A reads as (A, t) -> (A, t+2) and a stale
// CAS fails. With tagging switched off the same code has the ABA bug, and
// aba_script() replays the interleaving that triggers it, deterministically.
//
// Elimination: a push and a pop that meet can cancel without touching `top`.
// After a failed CAS a thread visits a random slot of an exchanger array; if a
// push meets a pop there, both succeed (linearised push-then-pop at the
// moment of exchange).
//
//   ./treiber_stack           demo    ./treiber_stack --test    ./treiber_stack --bench
#include <memory>

#include "common.hpp"

constexpr auto rlx = std::memory_order_relaxed, acq = std::memory_order_acquire,
               rel = std::memory_order_release, acq_rel = std::memory_order_acq_rel;
constexpr uint32_t NIL = 0xFFFFFFFFu;

struct Node { long value = 0; std::atomic<uint32_t> next{NIL}; };

static uint64_t pack(uint32_t tag, uint32_t idx) { return (uint64_t(tag) << 32) | idx; }
static uint32_t idx_of(uint64_t v) { return uint32_t(v); }
static uint32_t tag_of(uint64_t v) { return uint32_t(v >> 32); }

struct IndexStack {  // Treiber stack of node indices
    std::atomic<uint64_t> top{pack(0, NIL)};
    Node* nodes;
    bool tagged;
    IndexStack(Node* n, bool t) : nodes(n), tagged(t) {}
    uint64_t bump(uint64_t old, uint32_t idx) const { return pack(tagged ? tag_of(old) + 1 : 0, idx); }
    bool try_push(uint32_t i) {
        uint64_t old = top.load(acq);
        nodes[i].next.store(idx_of(old), rlx);
        return top.compare_exchange_strong(old, bump(old, i), acq_rel, acq);  // linearisation point
    }
    void push(uint32_t i) { while (!try_push(i)) cpu_relax(); }
    // One attempt: returns false on CAS failure, true with *out (NIL if empty).
    bool try_pop(uint32_t* out) {
        uint64_t old = top.load(acq);
        uint32_t i = idx_of(old);
        if (i == NIL) { *out = NIL; return true; }            // empty: linearised at the load
        uint32_t nx = nodes[i].next.load(rlx);                // may be stale if i was recycled
        if (!top.compare_exchange_strong(old, bump(old, nx), acq_rel, acq)) return false;
        *out = i; return true;
    }
    uint32_t pop() { uint32_t r; while (!try_pop(&r)) cpu_relax(); return r; }
};

// Values stack + free list over one node array.
struct Stack {
    std::unique_ptr<Node[]> nodes;
    IndexStack s, free;
    Stack(uint32_t cap, bool tagged) : nodes(new Node[cap]), s(nodes.get(), tagged), free(nodes.get(), tagged) {
        for (uint32_t i = 0; i < cap; ++i) free.push(i);
    }
    uint32_t alloc(long v) { uint32_t i = free.pop(); CHECK(i != NIL); nodes[i].value = v; return i; }
    void push(long v) { s.push(alloc(v)); }
    bool pop(long* v) { uint32_t i = s.pop(); if (i == NIL) return false; *v = nodes[i].value; free.push(i); return true; }
};

// Exchanger slot: [state:2 | tag:30 | item:32] (book ch. 11, LockFreeExchanger [S1]).
enum : uint64_t { EMPTY = 0, WAITING = 1, BUSY = 2 };
static uint64_t slot(uint64_t st, uint64_t tag, uint32_t item) { return (st << 62) | ((tag & 0x3FFFFFFF) << 32) | item; }
static uint64_t st_of(uint64_t v) { return v >> 62; }
static uint64_t stag(uint64_t v) { return (v >> 32) & 0x3FFFFFFF; }

struct alignas(128) Exchanger {
    std::atomic<uint64_t> v{slot(EMPTY, 0, 0)};
    bool exchange(uint32_t mine, int spins, uint32_t* his) {
        for (int i = 0; i < spins; ++i) {
            uint64_t s = v.load(acq);
            if (st_of(s) == EMPTY) {
                uint64_t w = slot(WAITING, stag(s) + 1, mine);
                if (!v.compare_exchange_strong(s, w, acq_rel, acq)) continue;
                for (int j = 0; j < spins; ++j) {             // wait for a partner
                    uint64_t b = v.load(acq);
                    if (st_of(b) == BUSY) { *his = uint32_t(b); v.store(slot(EMPTY, stag(b) + 1, 0), rel); return true; }
                    cpu_relax();
                }
                if (v.compare_exchange_strong(w, slot(EMPTY, stag(w) + 1, 0), acq_rel, acq)) return false;  // withdrew
                uint64_t b = v.load(acq);                     // a partner arrived at the last moment
                *his = uint32_t(b); v.store(slot(EMPTY, stag(b) + 1, 0), rel); return true;
            }
            if (st_of(s) == WAITING) {
                if (v.compare_exchange_strong(s, slot(BUSY, stag(s) + 1, mine), acq_rel, acq)) { *his = uint32_t(s); return true; }
            }
            cpu_relax();                                      // BUSY: two others are pairing
        }
        return false;
    }
};

struct EliminationStack {
    Stack st;
    std::vector<Exchanger> arena;
    std::atomic<long> eliminated{0};
    EliminationStack(uint32_t cap, int width) : st(cap, true), arena(width) {}
    void push(long v, Rng& r) {
        uint32_t i = st.alloc(v);
        for (;;) {
            if (st.s.try_push(i)) return;
            uint32_t his;                                     // offer my node; a pop offers NIL
            if (arena[r.below(uint32_t(arena.size()))].exchange(i, 64, &his) && his == NIL) { eliminated.fetch_add(1, rlx); return; }
        }
    }
    bool pop(long* v, Rng& r) {
        for (;;) {
            uint32_t i;
            if (st.s.try_pop(&i)) {
                if (i == NIL) return false;
                *v = st.nodes[i].value; st.free.push(i); return true;
            }
            uint32_t his;
            if (arena[r.below(uint32_t(arena.size()))].exchange(NIL, 64, &his) && his != NIL) {
                *v = st.nodes[his].value; st.free.push(his); return true;
            }
        }
    }
};

// Replays the textbook interleaving on bare indices: T1 reads top = A and
// next = B, then stalls; T2 pops A, pops B (and still holds B), pushes A back;
// T1's CAS(top: A -> B) succeeds without tags, making B the top although T2
// owns it, and A is lost. With tags the CAS sees (A, t) != (A, t+3) and fails.
static bool aba_script(bool tagged) {
    Node nodes[3];
    IndexStack s(nodes, tagged);
    s.push(2); s.push(1); s.push(0);                          // top: A=0 -> B=1 -> C=2
    uint64_t old = s.top.load();                              // T1: snapshot
    uint32_t A = idx_of(old), B = nodes[A].next.load();
    uint32_t a = s.pop(), b = s.pop();                        // T2 pops A, pops B
    CHECK(a == A && b == B);
    s.push(a);                                                // T2 pushes A back: A -> C
    bool won = s.top.compare_exchange_strong(old, s.bump(old, B));  // T1 resumes
    if (won) CHECK(idx_of(s.top.load()) == B);                // B is "in" the stack and owned by T2
    return won;
}

static void test() {
    CHECK(aba_script(false) == true);                         // untagged: the stale CAS succeeds (bug)
    CHECK(aba_script(true) == false);                         // tagged: it fails
    const int T = 4; const long per = 50000 / kScale;
    for (int variant = 0; variant < 2; ++variant) {
        Stack plain(uint32_t(T * per + 8), true);
        EliminationStack elim(uint32_t(T * per + 8), 2);
        std::vector<char> seen(size_t(T * per), 0);
        std::atomic<long> dup{0};
        auto note = [&](long v) { if (seen[size_t(v)]++) dup.fetch_add(1); };
        std::vector<std::vector<long>> got(T);
        run_threads(T, [&](int t) {
            Rng r(t + 3);
            long next = 0, v;
            while (next < per) {
                if (r.below(2)) {                            // push a fresh value, unique per thread
                    long val = t * per + next++;
                    if (variant) elim.push(val, r); else plain.push(val);
                } else if (variant ? elim.pop(&v, r) : plain.pop(&v)) got[t].push_back(v);
            }
        });
        long v;
        for (auto& g : got) for (long x : g) note(x);
        while (variant ? elim.st.pop(&v) : plain.pop(&v)) note(v);
        CHECK(dup.load() == 0);
        for (char c : seen) CHECK(c == 1);                   // every pushed value popped exactly once
        if (variant) std::printf("  elimination: %ld pairs eliminated in the test run\n", elim.eliminated.load());
    }
    std::printf("treiber_stack: ABA replay (bug without tags, none with), no loss/duplication (plain + elimination)\n");
}

static void bench() {
    for (int T : {1, 2, 4, 8}) {
        const long per = 400000;
        for (int variant = 0; variant < 2; ++variant) {
            Stack plain(uint32_t(T * per + 8), true);
            EliminationStack elim(uint32_t(T * per + 8), T > 1 ? T / 2 : 1);
            Timer tm;
            run_threads(T, [&](int t) {
                Rng r(t + 11); long v;
                for (long i = 0; i < per; ++i) {
                    if (i % 2 == 0) { if (variant) elim.push(i, r); else plain.push(i); }
                    else if (variant) elim.pop(&v, r); else plain.pop(&v);
                }
            });
            std::printf("  %-12s T=%d  %6.2f Mops/s%s\n", variant ? "elimination" : "treiber", T,
                        double(T * per) / tm.seconds() / 1e6,
                        variant ? (" (" + std::to_string(100.0 * 2 * elim.eliminated.load() / double(T * per)).substr(0, 4) + "% of ops eliminated)").c_str() : "");
        }
    }
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "bench") { bench(); return 0; }
    test();
    return 0;
}
