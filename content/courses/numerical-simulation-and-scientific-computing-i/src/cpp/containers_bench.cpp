// containers_bench.cpp -- STL containers and their real cost (topic 08).
//
//   push_back / traversal / middle insertion: vector vs list vs deque
//   lookup: std::map (red-black tree, O(log n)), std::unordered_map (hash, O(1) avg),
//           sorted vector + binary search (O(log n), but contiguous -> cache friendly)
//   Big-O says list insertion is O(1); the timings show why vector still wins for
//   small elements: pointer chasing misses the cache on every node.
//
// Sources: the complexity column is the container requirements of ISO C++ [S14]
// (push_back amortised constant, map O(log n), unordered_map O(1) average);
// the timings are measurements on the host [S34].
//
// Usage: ./containers_bench [--test | --bench]
#include "common.hpp"
#include <algorithm>
#include <deque>
#include <list>
#include <map>
#include <numeric>
#include <random>
#include <unordered_map>
#include <vector>

template <class F> static double timed(F&& f) { Timer t; f(); return t.seconds(); }

static void run(std::size_t n, bool test) {
    std::mt19937 rng(7);
    std::vector<int> keys(n);
    std::iota(keys.begin(), keys.end(), 0);
    std::shuffle(keys.begin(), keys.end(), rng);

    std::vector<int> vec; std::list<int> lst; std::deque<int> deq;
    std::printf("n = %zu\n%-32s %10s %10s %10s\n", n, "operation", "vector", "list", "deque");
    double tv = timed([&] { for (int k : keys) vec.push_back(k); });
    double tl = timed([&] { for (int k : keys) lst.push_back(k); });
    double td = timed([&] { for (int k : keys) deq.push_back(k); });
    std::printf("%-32s %10.4f %10.4f %10.4f\n", "push_back n [s]", tv, tl, td);

    long long sv = 0, sl = 0, sd = 0;
    tv = timed([&] { for (int k : vec) sv += k; });
    tl = timed([&] { for (int k : lst) sl += k; });
    td = timed([&] { for (int k : deq) sd += k; });
    std::printf("%-32s %10.4f %10.4f %10.4f\n", "traverse and sum [s]", tv, tl, td);
    if (test) CHECK(sv == sl && sl == sd && sv == static_cast<long long>(n) * (n - 1) / 2);

    const std::size_t m = std::min<std::size_t>(n / 100, 5000);   // middle insertions
    std::vector<int> v2(vec); std::list<int> l2(lst);
    tv = timed([&] { for (std::size_t k = 0; k < m; ++k) v2.insert(v2.begin() + v2.size() / 2, 1); });
    auto mid = l2.begin(); std::advance(mid, l2.size() / 2);
    tl = timed([&] { for (std::size_t k = 0; k < m; ++k) l2.insert(mid, 1); });
    std::printf("%-32s %10.4f %10.4f %10s   (%zu inserts, list iterator already at position)\n", "insert in the middle [s]", tv, tl, "-", m);
    // list wins only if you already hold the iterator; finding the middle costs O(n) walking
    tl = timed([&] { for (std::size_t k = 0; k < m; ++k) { auto it = l2.begin(); std::advance(it, l2.size() / 2); l2.insert(it, 1); } });
    std::printf("%-32s %10s %10.4f %10s   (list: walk to middle each time)\n", "insert in the middle, find first", "-", tl, "-");

    // lookups
    std::map<int, int> mp; std::unordered_map<int, int> um; std::vector<std::pair<int, int>> sv2;
    double t_mp = timed([&] { for (int k : keys) mp[k] = k * 2; });
    double t_um = timed([&] { um.reserve(n); for (int k : keys) um[k] = k * 2; });
    double t_sv = timed([&] { for (int k : keys) sv2.push_back({k, k * 2}); std::sort(sv2.begin(), sv2.end()); });
    std::vector<int> probes(n);
    for (auto& p : probes) p = static_cast<int>(rng() % (2 * n));    // half the probes miss
    long long h_mp = 0, h_um = 0, h_sv = 0;
    double q_mp = timed([&] { for (int p : probes) { auto it = mp.find(p); if (it != mp.end()) h_mp += it->second; } });
    double q_um = timed([&] { for (int p : probes) { auto it = um.find(p); if (it != um.end()) h_um += it->second; } });
    double q_sv = timed([&] { for (int p : probes) {
        auto it = std::lower_bound(sv2.begin(), sv2.end(), std::make_pair(p, 0));
        if (it != sv2.end() && it->first == p) h_sv += it->second; } });
    std::printf("\n%-32s %10s %13s %14s\n", "", "map", "unordered_map", "sorted vector");
    std::printf("%-32s %10.4f %13.4f %14.4f\n", "build n entries [s]", t_mp, t_um, t_sv);
    std::printf("%-32s %10.4f %13.4f %14.4f\n", "n lookups (50% miss) [s]", q_mp, q_um, q_sv);
    if (test) CHECK(h_mp == h_um && h_um == h_sv);
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    if (mode == "test") { run(100000, true); std::puts("containers_bench: ok"); }
    else if (mode == "bench") { run(1000000, false); run(10000000, false); }
    else run(1000000, false);
    return 0;
}
