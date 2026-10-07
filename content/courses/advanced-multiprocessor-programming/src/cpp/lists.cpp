// lists.cpp -- list-based integer sets: coarse-grained, lazy, lock-free
// (Herlihy-Shavit ch. 9 [S1]; lazy list Heller et al. 2005 [S16]; lock-free
// list Harris 2001 [S15]). All three implement add/remove/contains over a
// sorted singly linked list with sentinels head = -inf, tail = +inf.
//
// Coarse   one mutex around every call. Linearisation point: inside the lock.
// Lazy     per-node mutex + `marked` bit. remove marks (logical delete, the
//          linearisation point) then unlinks (physical delete). add/remove
//          lock pred and curr and VALIDATE: !pred.marked && !curr.marked &&
//          pred.next == curr. contains takes no lock and is wait-free.
// LockFree the mark lives in the low bit of `next` so that "curr is deleted"
//          and "curr.next changed" are one CAS target (Harris). find() snips
//          marked nodes; add CASes pred.next; remove CASes the mark on, then
//          tries once to unlink. contains is wait-free.
// Memory: nodes come from a per-set arena and are freed with the set, so no
// node is reused while a traversal may hold it (note 12 does reclamation).
//
// Same test for all three: (1) random sequential ops against std::set;
// (2) disjoint-key concurrent phase, final contents known exactly;
// (3) contended phase on 64 shared keys: for every key,
//     #successful adds - #successful removes == contains(key) in {0, 1},
//     and the final list is strictly sorted.
//
//   ./lists           demo   ./lists --test   ./lists --bench
#include <climits>
#include <memory>
#include <mutex>
#include <set>

#include "common.hpp"

constexpr auto acq = std::memory_order_acquire, rel = std::memory_order_release;

// Bump allocator of nodes: enough for every add of a run, freed at the end.
template <class N>
struct Arena {
    std::unique_ptr<N[]> pool;
    std::atomic<size_t> used{0};
    size_t cap;
    explicit Arena(size_t c) : pool(new N[c]), cap(c) {}
    N* make(int key) { size_t i = used.fetch_add(1); CHECK(i < cap); pool[i].key = key; return &pool[i]; }
};

struct CoarseList {
    struct Node { int key = 0; Node* next = nullptr; };
    Arena<Node> ar; Node *head, *tail; std::mutex m;
    explicit CoarseList(size_t cap) : ar(cap + 2) { head = ar.make(INT_MIN); tail = ar.make(INT_MAX); head->next = tail; }
    bool add(int k) {
        std::lock_guard<std::mutex> g(m);
        Node* p = head; while (p->next->key < k) p = p->next;
        if (p->next->key == k) return false;
        Node* n = ar.make(k); n->next = p->next; p->next = n; return true;
    }
    bool remove(int k) {
        std::lock_guard<std::mutex> g(m);
        Node* p = head; while (p->next->key < k) p = p->next;
        if (p->next->key != k) return false;
        p->next = p->next->next; return true;
    }
    bool contains(int k) {
        std::lock_guard<std::mutex> g(m);
        Node* p = head->next; while (p->key < k) p = p->next;
        return p->key == k;
    }
    template <class F> void each(F f) { for (Node* p = head->next; p != tail; p = p->next) f(p->key, false); }
};

struct LazyList {
    struct Node { int key = 0; std::atomic<Node*> next{nullptr}; std::atomic<bool> marked{false}; std::mutex m; };
    Arena<Node> ar; Node *head, *tail;
    explicit LazyList(size_t cap) : ar(cap + 2) { head = ar.make(INT_MIN); tail = ar.make(INT_MAX); head->next = tail; }
    static bool validate(Node* p, Node* c) { return !p->marked.load(acq) && !c->marked.load(acq) && p->next.load(acq) == c; }
    void locate(int k, Node*& p, Node*& c) {
        p = head; c = p->next.load(acq);
        while (c->key < k) { p = c; c = c->next.load(acq); }
    }
    bool add(int k) {
        for (;;) {
            Node *p, *c; locate(k, p, c);
            std::scoped_lock g(p->m, c->m);
            if (!validate(p, c)) continue;               // something changed: retry
            if (c->key == k) return false;
            Node* n = ar.make(k); n->next.store(c, std::memory_order_relaxed);
            p->next.store(n, rel);                       // linearisation point of a successful add
            return true;
        }
    }
    bool remove(int k) {
        for (;;) {
            Node *p, *c; locate(k, p, c);
            std::scoped_lock g(p->m, c->m);
            if (!validate(p, c)) continue;
            if (c->key != k) return false;
            c->marked.store(true, rel);                  // logical delete = linearisation point
            p->next.store(c->next.load(acq), rel);       // physical delete
            return true;
        }
    }
    bool contains(int k) {                               // wait-free: no locks, no retries
        Node* c = head;
        while (c->key < k) c = c->next.load(acq);
        return c->key == k && !c->marked.load(acq);
    }
    template <class F> void each(F f) { for (Node* p = head->next; p != tail; p = p->next) f(p->key, p->marked.load()); }
};

struct LockFreeList {
    struct Node { int key = 0; std::atomic<uintptr_t> next{0}; };  // low bit = "this node is deleted"
    static Node* ptr(uintptr_t v) { return reinterpret_cast<Node*>(v & ~uintptr_t(1)); }
    static bool mark(uintptr_t v) { return v & 1; }
    static uintptr_t pack(Node* p, bool m) { return reinterpret_cast<uintptr_t>(p) | uintptr_t(m); }
    Arena<Node> ar; Node *head, *tail;
    explicit LockFreeList(size_t cap) : ar(cap + 2) { head = ar.make(INT_MIN); tail = ar.make(INT_MAX); head->next = pack(tail, false); }
    // Returns pred, curr with pred.key < k <= curr.key, both unmarked when seen,
    // physically removing every marked node met on the way [S1 ch. 9].
    void find(int k, Node*& pred, Node*& curr) {
    retry:
        pred = head; curr = ptr(pred->next.load(acq));
        for (;;) {
            uintptr_t succ = curr->next.load(acq);
            while (mark(succ)) {                         // curr is logically deleted: snip it
                uintptr_t exp = pack(curr, false);
                if (!pred->next.compare_exchange_strong(exp, pack(ptr(succ), false), std::memory_order_acq_rel)) goto retry;
                curr = ptr(succ); succ = curr->next.load(acq);
            }
            if (curr->key >= k) return;
            pred = curr; curr = ptr(succ);
        }
    }
    bool add(int k) {
        for (;;) {
            Node *p, *c; find(k, p, c);
            if (c->key == k) return false;
            Node* n = ar.make(k); n->next.store(pack(c, false), std::memory_order_relaxed);
            uintptr_t exp = pack(c, false);
            if (p->next.compare_exchange_strong(exp, pack(n, false), std::memory_order_acq_rel)) return true;
            // lost the race: the arena node is simply abandoned (freed with the set)
        }
    }
    bool remove(int k) {
        for (;;) {
            Node *p, *c; find(k, p, c);
            if (c->key != k) return false;
            uintptr_t succ = c->next.load(acq);
            if (mark(succ)) continue;
            uintptr_t exp = succ;
            if (!c->next.compare_exchange_strong(exp, succ | 1, std::memory_order_acq_rel)) continue;  // mark = linearisation point
            exp = pack(c, false);
            p->next.compare_exchange_strong(exp, pack(ptr(succ), false), std::memory_order_acq_rel);  // one try; find() finishes it
            return true;
        }
    }
    bool contains(int k) {
        Node* c = head;
        while (c->key < k) c = ptr(c->next.load(acq));
        return c->key == k && !mark(c->next.load(acq));
    }
    template <class F> void each(F f) { for (Node* p = ptr(head->next.load()); p != tail; p = ptr(p->next.load())) f(p->key, mark(p->next.load())); }
};

template <class S>
void test_set(const char* name) {
    const int T = 4, keys = 64;
    const long ops = 20000 / kScale;
    {   // (1) sequential spec
        S s(size_t(ops) + 10); std::set<int> ref; Rng r(1);
        for (long i = 0; i < ops; ++i) {
            int k = int(r.below(100)), op = int(r.below(3));
            if (op == 0) CHECK(s.add(k) == ref.insert(k).second);
            else if (op == 1) CHECK(s.remove(k) == (ref.erase(k) == 1));
            else CHECK(s.contains(k) == (ref.count(k) == 1));
        }
    }
    {   // (2) disjoint keys: thread t owns keys = t (mod T); final contents known
        S s(size_t(T * ops) + 10);
        std::vector<std::set<int>> mine(T);
        run_threads(T, [&](int t) {
            Rng r(t + 100);
            for (long i = 0; i < ops; ++i) {
                int k = int(r.below(256)) * T + t;
                if (r.below(2)) { CHECK(s.add(k) == mine[t].insert(k).second); }
                else { CHECK(s.remove(k) == (mine[t].erase(k) == 1)); }
                s.contains(int(r.below(1024)));          // concurrent readers of others' keys
            }
        });
        std::set<int> all; for (auto& m : mine) all.insert(m.begin(), m.end());
        std::vector<int> seen; s.each([&](int k, bool marked) { if (!marked) seen.push_back(k); });
        CHECK(std::vector<int>(all.begin(), all.end()) == seen);
    }
    {   // (3) contended keys: per-key balance
        S s(size_t(T * ops) + 10);
        std::vector<std::atomic<long>> bal(keys);
        for (auto& b : bal) b = 0;
        run_threads(T, [&](int t) {
            Rng r(t + 1000);
            for (long i = 0; i < ops; ++i) {
                int k = int(r.below(keys)), op = int(r.below(3));
                if (op == 0) { if (s.add(k)) bal[k].fetch_add(1); }
                else if (op == 1) { if (s.remove(k)) bal[k].fetch_sub(1); }
                else s.contains(k);
            }
        });
        int prev = INT_MIN;
        // Strictly sorted over ALL reachable nodes. A marked node may still be
        // reachable in the lock-free list (its unlink CAS failed; the next find
        // snips it), never in the lazy list (it unlinks under both locks).
        s.each([&](int k, bool) { CHECK(k > prev); prev = k; });
        for (int k = 0; k < keys; ++k) { long b = bal[k].load(); CHECK(b == 0 || b == 1); CHECK(s.contains(k) == (b == 1)); }
    }
    std::printf("  %-12s spec, disjoint, contended: ok\n", name);
}

template <class S>
void bench_set(const char* name) {
    for (int T : {1, 2, 4, 8}) {
        const long ops = 200000;
        S s(size_t(T * ops) + 600);
        for (int k = 0; k < 512; k += 2) s.add(k);       // half full, range 512
        Timer tm;
        run_threads(T, [&](int t) {
            Rng r(t + 7);
            for (long i = 0; i < ops; ++i) {
                int k = int(r.below(512)), op = int(r.below(10));
                if (op == 0) s.add(k); else if (op == 1) s.remove(k); else s.contains(k);  // 80% contains
            }
        });
        std::printf("  %-12s T=%d  %6.2f Mops/s\n", name, T, double(T * ops) / tm.seconds() / 1e6);
    }
}

int main(int argc, char** argv) {
    std::string m = mode_of(argc, argv);
    if (m == "bench") { bench_set<CoarseList>("coarse"); bench_set<LazyList>("lazy"); bench_set<LockFreeList>("lock-free"); return 0; }
    std::printf("lists:\n");
    test_set<CoarseList>("coarse"); test_set<LazyList>("lazy"); test_set<LockFreeList>("lock-free");
    return 0;
}
