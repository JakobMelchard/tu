// striped_hashset.cpp -- closed-addressing hash sets: coarse vs lock striping,
// and the split-ordering property behind the lock-free hash set
// (Herlihy-Shavit ch. 13 [S1]; Shalev & Shavit 2006 [S18]).
//
// Coarse   one mutex; resize under it.
// Striped  a FIXED array of L mutexes; key x is protected by lock x mod L,
//          bucket x mod N with N a multiple of L (so lock i guards buckets
//          i, i+L, i+2L, ...). Resize takes ALL L locks in index order (no
//          deadlock: a global lock order), rechecks that nobody resized in
//          between, and doubles N. Disjoint stripes proceed in parallel.
// Split-ordered (idea only): keep ALL items in ONE lock-free sorted list,
//          sorted by the bit-reversed key. Bucket b of a 2^i table is then a
//          contiguous segment, and doubling the table splits every segment in
//          two without moving any item (recursive split-ordering [S18]).
//          split_order_property() checks that claim exhaustively.
//
//   ./striped_hashset    demo    ./striped_hashset --test    ./striped_hashset --bench
#include <algorithm>
#include <climits>
#include <memory>
#include <mutex>
#include <set>

#include "common.hpp"

static size_t hsh(int x) { return size_t(uint32_t(x) * 2654435761u); }  // Knuth multiplicative

struct CoarseHashSet {
    std::mutex m;
    std::vector<std::vector<int>> b = std::vector<std::vector<int>>(16);
    size_t n = 0;
    bool add(int x) {
        std::lock_guard<std::mutex> g(m);
        auto& v = b[hsh(x) % b.size()];
        if (std::find(v.begin(), v.end(), x) != v.end()) return false;
        v.push_back(x);
        if (++n > 4 * b.size()) resize();
        return true;
    }
    bool remove(int x) {
        std::lock_guard<std::mutex> g(m);
        auto& v = b[hsh(x) % b.size()];
        auto it = std::find(v.begin(), v.end(), x);
        if (it == v.end()) return false;
        *it = v.back(); v.pop_back(); --n; return true;
    }
    bool contains(int x) {
        std::lock_guard<std::mutex> g(m);
        auto& v = b[hsh(x) % b.size()];
        return std::find(v.begin(), v.end(), x) != v.end();
    }
    void resize() {
        std::vector<std::vector<int>> nb(2 * b.size());
        for (auto& v : b) for (int x : v) nb[hsh(x) % nb.size()].push_back(x);
        b.swap(nb);
    }
    size_t buckets() { return b.size(); }
};

class StripedHashSet {
    static constexpr size_t L = 16;                       // number of locks, fixed
    struct alignas(128) Lock { std::mutex m; };
    Lock locks_[L];
    std::vector<std::vector<int>> b_ = std::vector<std::vector<int>>(L);
    std::atomic<size_t> n_{0};
    // b_.size() changes only while ALL locks are held, so reading it while
    // holding ANY one lock is race-free.
    std::mutex& lock_for(int x) { return locks_[hsh(x) % L].m; }
    void resize(size_t seen) {
        std::vector<std::unique_lock<std::mutex>> all;
        for (auto& l : locks_) all.emplace_back(l.m);     // global order: 0, 1, ..., L-1
        if (b_.size() != seen) return;                     // somebody else resized first
        std::vector<std::vector<int>> nb(2 * seen);
        for (auto& v : b_) for (int x : v) nb[hsh(x) % nb.size()].push_back(x);
        b_.swap(nb);
    }
  public:
    bool add(int x) {
        size_t cap;
        {
            std::lock_guard<std::mutex> g(lock_for(x));
            cap = b_.size();
            auto& v = b_[hsh(x) % cap];
            if (std::find(v.begin(), v.end(), x) != v.end()) return false;
            v.push_back(x);
        }
        if (n_.fetch_add(1) + 1 > 4 * cap) resize(cap);  // policy check outside the stripe lock
        return true;
    }
    bool remove(int x) {
        std::lock_guard<std::mutex> g(lock_for(x));
        auto& v = b_[hsh(x) % b_.size()];
        auto it = std::find(v.begin(), v.end(), x);
        if (it == v.end()) return false;
        *it = v.back(); v.pop_back(); n_.fetch_sub(1); return true;
    }
    bool contains(int x) {
        std::lock_guard<std::mutex> g(lock_for(x));
        auto& v = b_[hsh(x) % b_.size()];
        return std::find(v.begin(), v.end(), x) != v.end();
    }
    size_t buckets() { std::lock_guard<std::mutex> g(locks_[0].m); return b_.size(); }
    bool well_formed() {                                   // every item in its bucket (quiescent)
        for (size_t i = 0; i < b_.size(); ++i) for (int x : b_[i]) if (hsh(x) % b_.size() != i) return false;
        return true;
    }
};

// ---------------------------------------------------------------- split order
static uint32_t rev32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 32; ++i) r = (r << 1) | ((x >> i) & 1);
    return r;
}
// Along the list sorted by rev32(key), the bucket index of a 2^i table, read
// bit-reversed in i bits, never decreases: each bucket is one contiguous run,
// in bit-reversed order, for EVERY i simultaneously. Doubling 2^i -> 2^(i+1)
// cuts run b into runs b and b + 2^i, in that order, without moving items.
static bool split_order_property(int nbits_keys, int max_i) {
    std::vector<uint32_t> keys(size_t(1) << nbits_keys);
    for (uint32_t k = 0; k < keys.size(); ++k) keys[k] = k;
    std::sort(keys.begin(), keys.end(), [](uint32_t a, uint32_t b) { return rev32(a) < rev32(b); });
    for (int i = 1; i <= max_i; ++i) {
        uint32_t mask = (1u << i) - 1, prev = 0;
        for (uint32_t k : keys) {
            uint32_t bucket_rev = rev32(k & mask) >> (32 - i);  // i-bit reversal of the bucket index
            if (bucket_rev < prev) return false;
            prev = bucket_rev;
        }
    }
    return true;
}

template <class S>
static void test_set(const char* name) {
    const int T = 4; const long ops = 40000 / kScale;
    {
        S s; std::set<int> ref; Rng r(2);
        for (long i = 0; i < ops; ++i) {
            int k = int(r.below(5000)), op = int(r.below(3));
            if (op == 0) CHECK(s.add(k) == ref.insert(k).second);
            else if (op == 1) CHECK(s.remove(k) == (ref.erase(k) == 1));
            else CHECK(s.contains(k) == (ref.count(k) == 1));
        }
        CHECK(s.buckets() > 16);                            // resize was exercised
    }
    {   // contended: per-key balance, with enough keys to force resizes mid-run
        S s; const int keys = 4096;
        std::vector<std::atomic<long>> bal(keys);
        for (auto& b : bal) b = 0;
        run_threads(T, [&](int t) {
            Rng r(t + 50);
            for (long i = 0; i < ops; ++i) {
                int k = int(r.below(keys)), op = int(r.below(3));
                if (op < 2) { if (s.add(k)) bal[k].fetch_add(1); }   // add-heavy: the table grows
                else if (s.remove(k)) bal[k].fetch_sub(1);
            }
        });
        for (int k = 0; k < keys; ++k) { long b = bal[k].load(); CHECK(b == 0 || b == 1); CHECK(s.contains(k) == (b == 1)); }
        CHECK(s.buckets() > 16);
        if constexpr (std::is_same_v<S, StripedHashSet>) CHECK(s.well_formed());
    }
    std::printf("  %-8s spec + contended with concurrent resize: ok\n", name);
}

static void test() {
    std::printf("striped_hashset:\n");
    test_set<CoarseHashSet>("coarse");
    test_set<StripedHashSet>("striped");
    CHECK(rev32(1) == 0x80000000u && rev32(6) == 0x60000000u);
    CHECK(split_order_property(12, 10));
    std::printf("  split-order: 4096 keys, table sizes 2..1024: every bucket contiguous, splits in place\n");
}

template <class S>
static void bench_set(const char* name) {
    for (int T : {1, 2, 4, 8}) {
        S s; const long ops = 400000;
        for (int k = 0; k < 20000; k += 2) s.add(k);
        Timer tm;
        run_threads(T, [&](int t) {
            Rng r(t + 9);
            for (long i = 0; i < ops; ++i) {
                int k = int(r.below(20000)), op = int(r.below(10));
                if (op == 0) s.add(k); else if (op == 1) s.remove(k); else s.contains(k);
            }
        });
        std::printf("  %-8s T=%d  %6.2f Mops/s\n", name, T, double(T * ops) / tm.seconds() / 1e6);
    }
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "bench") { bench_set<CoarseHashSet>("coarse"); bench_set<StripedHashSet>("striped"); return 0; }
    test();
    return 0;
}
