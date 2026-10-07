// 0/1 knapsack by dynamic programming with reconstruction (KT 6.4). Belongs to note A05.
// OPT(i, w) = max(OPT(i-1, w), v_i + OPT(i-1, w - w_i)); O(nW) pseudo-polynomial.
// Usage: ./knapsack        -> demo
//        ./knapsack --test -> self-check, exit 1 on failure
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <vector>

// Returns best value; chosen receives item indices (ascending).
long long knapsack(const std::vector<int>& wt, const std::vector<long long>& val, int W,
                   std::vector<int>& chosen) {
    int n = (int)wt.size();
    std::vector<std::vector<long long>> opt(n + 1, std::vector<long long>(W + 1, 0));
    for (int i = 1; i <= n; ++i)
        for (int w = 0; w <= W; ++w) {
            opt[i][w] = opt[i - 1][w];                      // skip item i
            if (w >= wt[i - 1])                             // or take it if it fits
                opt[i][w] = std::max(opt[i][w], val[i - 1] + opt[i - 1][w - wt[i - 1]]);
        }
    chosen.clear();
    for (int i = n, w = W; i >= 1; --i)                     // trace back the decisions
        if (opt[i][w] != opt[i - 1][w]) { chosen.push_back(i - 1); w -= wt[i - 1]; }
    std::reverse(chosen.begin(), chosen.end());
    return opt[n][W];
}

// Brute force over all 2^n subsets, used only for cross-checking in --test.
static long long brute(const std::vector<int>& wt, const std::vector<long long>& val, int W) {
    int n = (int)wt.size();
    long long best = 0;
    for (unsigned mask = 0; mask < (1u << n); ++mask) {
        long long v = 0; int w = 0;
        for (int i = 0; i < n; ++i) if (mask >> i & 1) { v += val[i]; w += wt[i]; }
        if (w <= W) best = std::max(best, v);
    }
    return best;
}

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("  CHECK failed: %s (line %d)\n", #cond, __LINE__); ++failures; } } while (0)

static int run_tests() {
    std::vector<int> chosen;
    // textbook instance: W=11, items (w,v) = (1,1),(2,6),(5,18),(6,22),(7,28) -> 40 with items {2,3}
    CHECK(knapsack({1, 2, 5, 6, 7}, {1, 6, 18, 22, 28}, 11, chosen) == 40);
    CHECK((chosen == std::vector<int>{2, 3}));
    CHECK(knapsack({5, 6}, {10, 20}, 4, chosen) == 0 && chosen.empty());   // nothing fits
    CHECK(knapsack({}, {}, 10, chosen) == 0);                                // no items
    // deterministic pseudo-random instances vs brute force, and the chosen set is feasible
    unsigned seed = 12345;
    auto rnd = [&seed](int lo, int hi) { seed = seed * 1103515245u + 12345u; return lo + (int)((seed >> 16) % (unsigned)(hi - lo + 1)); };
    for (int trial = 0; trial < 50; ++trial) {
        int n = rnd(1, 10), W = rnd(1, 30);
        std::vector<int> wt(n); std::vector<long long> val(n);
        for (int i = 0; i < n; ++i) { wt[i] = rnd(1, 12); val[i] = rnd(1, 50); }
        long long got = knapsack(wt, val, W, chosen);
        CHECK(got == brute(wt, val, W));
        long long sv = 0; int sw = 0;
        for (int i : chosen) { sv += val[i]; sw += wt[i]; }
        CHECK(sv == got && sw <= W);
    }
    std::printf("knapsack: %s (%d failures)\n", failures ? "FAIL" : "ok", failures);
    return failures ? 1 : 0;
}

int main(int argc, char** argv) {
    if (argc > 1 && std::strcmp(argv[1], "--test") == 0) return run_tests();
    std::vector<int> wt = {1, 2, 5, 6, 7};
    std::vector<long long> val = {1, 6, 18, 22, 28};
    std::vector<int> chosen;
    long long best = knapsack(wt, val, 11, chosen);
    std::printf("knapsack W=11: best value %lld, items:", best);
    for (int i : chosen) std::printf(" %d(w=%d,v=%lld)", i, wt[i], val[i]);
    std::printf("\n");
    return 0;
}
