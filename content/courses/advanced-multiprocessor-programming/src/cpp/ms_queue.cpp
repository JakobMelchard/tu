// ms_queue.cpp -- Michael-Scott lock-free FIFO queue with a linearisability
// checker (Michael & Scott 1996 [S14]; Herlihy-Shavit ch. 10 [S1];
// linearisability Herlihy & Wing 1990 [S6]).
//
// The queue is a singly linked list with a dummy node; Head points at the
// dummy, Tail at the last or second-to-last node. As in the paper, pointers
// are "counted": 64-bit [count:32 | index:32], nodes come from an array and
// are recycled through a free list, and every CAS bumps the count so that a
// recycled node cannot fool a stale CAS (ABA, note 07).
//   enqueue: link node after the last node by CAS on last.next (linearisation
//            point), then swing Tail (anyone may help: a lagging Tail is fixed
//            by whoever notices it).
//   dequeue: read the value of Head.next, CAS Head forward (linearisation
//            point); the old dummy is freed and the dequeued node is the new dummy.
//
// Checker: threads record each operation's invocation and response time from
// one shared atomic clock. A history is linearisable iff some total order of
// the operations (a) respects real time (a.res < b.inv => a before b) and (b) is
// a legal sequential FIFO run. Search (Wing & Gong style): repeatedly pick a
// "minimal" pending operation, apply it to a sequential queue if legal,
// backtrack otherwise; memoise (set of done ops, queue contents).
//
//   ./ms_queue    demo    ./ms_queue --test    ./ms_queue --bench
#include <deque>
#include <memory>
#include <mutex>
#include <queue>
#include <set>

#include "common.hpp"

constexpr auto rlx = std::memory_order_relaxed, acq = std::memory_order_acquire, acq_rel = std::memory_order_acq_rel;
constexpr uint32_t NIL = 0xFFFFFFFFu;
constexpr long EMPTY = -1;
static uint64_t cp(uint32_t cnt, uint32_t idx) { return (uint64_t(cnt) << 32) | idx; }
static uint32_t ix(uint64_t v) { return uint32_t(v); }
static uint32_t ct(uint64_t v) { return uint32_t(v >> 32); }

class MSQueue {
    struct Node { std::atomic<long> value{0}; std::atomic<uint64_t> next{cp(0, NIL)}; std::atomic<uint32_t> fnext{NIL}; };
    std::unique_ptr<Node[]> n_;
    alignas(128) std::atomic<uint64_t> head_;
    alignas(128) std::atomic<uint64_t> tail_;
    alignas(128) std::atomic<uint64_t> free_{cp(0, NIL)};  // Treiber free list over fnext
    void release(uint32_t i) {
        uint64_t old = free_.load(acq);
        do n_[i].fnext.store(ix(old), rlx);
        while (!free_.compare_exchange_weak(old, cp(ct(old) + 1, i), acq_rel, acq));
    }
    uint32_t grab() {
        uint64_t old = free_.load(acq);
        for (;;) {
            CHECK(ix(old) != NIL);                              // pool exhausted
            uint32_t nx = n_[ix(old)].fnext.load(rlx);
            if (free_.compare_exchange_weak(old, cp(ct(old) + 1, nx), acq_rel, acq)) return ix(old);
        }
    }
  public:
    explicit MSQueue(uint32_t cap) : n_(new Node[cap + 1]) {
        for (uint32_t i = 1; i <= cap; ++i) release(i);
        head_ = tail_ = cp(0, 0);                              // node 0 is the first dummy
    }
    void enqueue(long v) {
        uint32_t node = grab();
        n_[node].value.store(v, rlx);
        uint64_t nn = n_[node].next.load(rlx);
        n_[node].next.store(cp(ct(nn) + 1, NIL), rlx);
        uint64_t tail;
        for (;;) {
            tail = tail_.load(acq);
            uint64_t next = n_[ix(tail)].next.load(acq);
            if (tail != tail_.load(acq)) continue;              // inconsistent snapshot
            if (ix(next) == NIL) {
                if (n_[ix(tail)].next.compare_exchange_strong(next, cp(ct(next) + 1, node), acq_rel, acq)) break;
            } else {
                tail_.compare_exchange_strong(tail, cp(ct(tail) + 1, ix(next)), acq_rel, acq);  // help
            }
        }
        tail_.compare_exchange_strong(tail, cp(ct(tail) + 1, node), acq_rel, acq);  // may fail: someone helped
    }
    long dequeue() {
        for (;;) {
            uint64_t head = head_.load(acq), tail = tail_.load(acq);
            uint64_t next = n_[ix(head)].next.load(acq);
            if (head != head_.load(acq)) continue;
            if (ix(head) == ix(tail)) {
                if (ix(next) == NIL) return EMPTY;              // linearised at the read of next
                tail_.compare_exchange_strong(tail, cp(ct(tail) + 1, ix(next)), acq_rel, acq);
            } else {
                long v = n_[ix(next)].value.load(rlx);          // read BEFORE the CAS: after it, next may be freed
                if (head_.compare_exchange_strong(head, cp(ct(head) + 1, ix(next)), acq_rel, acq)) {
                    release(ix(head));
                    return v;
                }
            }
        }
    }
};

// ---------------------------------------------------------------- checker
struct Op { bool enq; long val; uint64_t inv, res; };  // val: argument of enq, result of deq

static bool linearisable(const std::vector<Op>& h) {
    const int n = int(h.size());
    CHECK(n <= 30);
    std::set<std::pair<uint32_t, std::vector<long>>> dead;  // states known to fail
    std::deque<long> q;
    auto dfs = [&](auto& self, uint32_t done) -> bool {
        if (done == (1u << n) - 1) return true;
        std::vector<long> key(q.begin(), q.end());
        if (dead.count({done, key})) return false;
        uint64_t min_res = ~0ull;                          // earliest response among pending ops
        for (int i = 0; i < n; ++i) if (!(done >> i & 1)) min_res = std::min(min_res, h[i].res);
        for (int i = 0; i < n; ++i) {
            if ((done >> i & 1) || h[i].inv > min_res) continue;  // not minimal in real-time order
            const Op& o = h[i];
            if (o.enq) {
                q.push_back(o.val);
                if (self(self, done | 1u << i)) return true;
                q.pop_back();
            } else if (o.val == EMPTY) {
                if (q.empty() && self(self, done | 1u << i)) return true;
            } else if (!q.empty() && q.front() == o.val) {
                q.pop_front();
                if (self(self, done | 1u << i)) return true;
                q.push_front(o.val);
            }
        }
        dead.insert({done, key});
        return false;
    };
    return dfs(dfs, 0);
}

static void checker_selftest() {
    // enq(1) then enq(2) strictly before a deq that returns 2: FIFO says 1.
    CHECK(!linearisable({{true, 1, 0, 1}, {true, 2, 2, 3}, {false, 2, 4, 5}}));
    // Overlapping enqueues may take effect in either order.
    CHECK(linearisable({{true, 1, 0, 5}, {true, 2, 1, 6}, {false, 2, 7, 8}, {false, 1, 9, 10}}));
    // An "empty" answer after a completed enq with nothing dequeued is illegal ...
    CHECK(!linearisable({{true, 1, 0, 1}, {false, EMPTY, 2, 3}}));
    // ... but legal if the dequeue overlaps the enqueue.
    CHECK(linearisable({{true, 1, 0, 3}, {false, EMPTY, 1, 2}}));
    // A value dequeued twice is never legal.
    CHECK(!linearisable({{true, 7, 0, 1}, {false, 7, 2, 3}, {false, 7, 4, 5}}));
}

struct LifoByMistake {  // a stack posing as a queue: the checker must reject it
    std::mutex m; std::vector<long> v;
    explicit LifoByMistake(uint32_t) {}
    void enqueue(long x) { std::lock_guard<std::mutex> g(m); v.push_back(x); }
    long dequeue() { std::lock_guard<std::mutex> g(m); if (v.empty()) return EMPTY; long x = v.back(); v.pop_back(); return x; }
};

static bool has_overlap(const std::vector<Op>& h) {  // two ops whose intervals intersect
    for (size_t i = 0; i < h.size(); ++i)
        for (size_t j = i + 1; j < h.size(); ++j)
            if (h[i].inv < h[j].res && h[j].inv < h[i].res) return true;
    return false;
}

// One round: T threads x k random ops on a fresh queue, history recorded.
template <class Q = MSQueue>
static std::vector<Op> record_round(int T, int k, uint64_t seed) {
    Q q(uint32_t(T * k + 2));
    std::atomic<uint64_t> clock{0};
    std::vector<std::vector<Op>> per(T);
    SpinBarrier bar(T);
    run_threads(T, [&](int t) {
        Rng r(seed * 131 + t);
        bool sense = false;
        bar.wait(sense);                                      // start together: maximise overlap
        for (int i = 0; i < k; ++i) {
            Op o;
            o.enq = r.below(2);
            o.inv = clock.fetch_add(1);
            if (o.enq) { o.val = long(t) * 100 + i; q.enqueue(o.val); }
            else o.val = q.dequeue();
            o.res = clock.fetch_add(1);
            per[t].push_back(o);
        }
    });
    std::vector<Op> h;
    for (auto& p : per) h.insert(h.end(), p.begin(), p.end());
    return h;
}

static void test() {
    checker_selftest();
    { MSQueue q(8); CHECK(q.dequeue() == EMPTY); q.enqueue(1); q.enqueue(2); CHECK(q.dequeue() == 1); CHECK(q.dequeue() == 2); CHECK(q.dequeue() == EMPTY); }
    // A single-threaded LIFO run is deterministic; some seed must expose it.
    int caught = 0;
    for (int r = 0; r < 10; ++r) caught += !linearisable(record_round<LifoByMistake>(1, 8, uint64_t(r)));
    CHECK(caught > 0);
    const int rounds = 400 / kScale;
    int overlapping = 0;
    for (int r = 0; r < rounds; ++r) {
        auto h = record_round(3, 5, uint64_t(r));
        overlapping += has_overlap(h);
        CHECK(linearisable(h));
    }
    // Stress: P producers, C consumers; exactly-once delivery, and every consumer
    // sees each producer's values in increasing order (implied by linearisability).
    const int P = 4, C = 4; const long N = 100000 / kScale;
    MSQueue q(uint32_t(P * N + 2));
    std::vector<std::atomic<char>> seen(size_t(P * N));
    for (auto& s : seen) s = 0;
    std::atomic<long> taken{0};
    run_threads(P + C, [&](int t) {
        if (t < P) { for (long i = 0; i < N; ++i) q.enqueue(t * N + i); return; }
        std::vector<long> last(P, -1);
        while (taken.load(rlx) < P * N) {
            long v = q.dequeue();
            if (v == EMPTY) { cpu_relax(); continue; }
            taken.fetch_add(1, rlx);
            CHECK(seen[size_t(v)].fetch_add(1) == 0);
            long p = v / N, i = v % N;
            CHECK(i > last[size_t(p)]); last[size_t(p)] = i;
        }
    });
    for (auto& s : seen) CHECK(s.load() == 1);
    std::printf("ms_queue: checker self-test (LIFO caught in %d/10 seeds); %d/%d recorded histories had\n"
                "  overlapping ops, all linearisable; %ld items exactly once in per-producer order\n",
                caught, overlapping, rounds, P * N);
}

struct LockedQueue {  // baseline: std::queue under one mutex
    std::mutex m; std::queue<long> q;
    void enqueue(long v) { std::lock_guard<std::mutex> g(m); q.push(v); }
    long dequeue() { std::lock_guard<std::mutex> g(m); if (q.empty()) return EMPTY; long v = q.front(); q.pop(); return v; }
};

template <class Q>
static double pairs_mops(Q& q, int T, long per) {
    Timer tm;
    run_threads(T, [&](int t) { for (long i = 0; i < per; ++i) { q.enqueue(t * per + i); q.dequeue(); } });
    return double(2 * T * per) / tm.seconds() / 1e6;
}

static void bench() {
    for (int T : {1, 2, 4, 8}) {
        const long per = 300000;
        MSQueue ms(uint32_t(T * per + 2)); LockedQueue lq;
        std::printf("  T=%d  michael-scott %6.2f Mops/s   mutex+std::queue %6.2f Mops/s\n", T,
                    pairs_mops(ms, T, per), pairs_mops(lq, T, per));
    }
    Timer tm; int rounds = 2000;
    for (int r = 0; r < rounds; ++r) CHECK(linearisable(record_round(3, 6, uint64_t(r) + 99)));
    std::printf("  checker: %d histories of 18 ops each, %.2f ms per history (record + search)\n", rounds, tm.seconds() * 1e3 / rounds);
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "bench") { bench(); return 0; }
    test();
    return 0;
}
