// Kruskal's minimum spanning tree with union-find (KT 4.5-4.6). Belongs to note A03.
// Sort edges by weight, add an edge iff it joins two different components.
// Usage: ./kruskal        -> demo
//        ./kruskal --test -> self-check, exit 1 on failure
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <numeric>
#include <vector>

struct Edge { int u, v; long long w; };

// Disjoint sets with path compression and union by rank: near-constant amortised ops.
struct UnionFind {
    std::vector<int> parent, rank;
    int count;
    explicit UnionFind(int n) : parent(n), rank(n, 0), count(n) { std::iota(parent.begin(), parent.end(), 0); }
    int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }  // path halving
        return x;
    }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (rank[a] < rank[b]) std::swap(a, b);
        parent[b] = a;
        if (rank[a] == rank[b]) ++rank[a];
        --count;
        return true;
    }
};

// Returns total weight; tree receives the chosen edges (a forest if disconnected).
long long kruskal(int n, std::vector<Edge> edges, std::vector<Edge>& tree) {
    std::sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) { return a.w < b.w; });
    UnionFind uf(n);
    tree.clear();
    long long total = 0;
    for (const Edge& e : edges) {
        if (uf.unite(e.u, e.v)) {  // cut property: cheapest edge across the cut is safe
            tree.push_back(e);
            total += e.w;
        }
    }
    return total;
}

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("  CHECK failed: %s (line %d)\n", #cond, __LINE__); ++failures; } } while (0)

static std::vector<Edge> demo_edges() {
    // nodes a..f = 0..5, same instance as the Python greedy.py demo (MST weight 13)
    return {{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}, {3, 5, 6}, {4, 5, 3}};
}

static int run_tests() {
    std::vector<Edge> tree;
    CHECK(kruskal(6, demo_edges(), tree) == 13);
    CHECK(tree.size() == 5);
    // tree edges must be acyclic and span all nodes
    UnionFind uf(6);
    bool acyclic = true;
    for (const Edge& e : tree) acyclic = acyclic && uf.unite(e.u, e.v);
    CHECK(acyclic && uf.count == 1);
    // disconnected graph -> forest with two trees
    std::vector<Edge> two = {{0, 1, 1}, {1, 2, 2}, {0, 2, 3}, {3, 4, 7}};
    CHECK(kruskal(5, two, tree) == 10 && tree.size() == 3);
    // equal weights: any MST has the same total
    std::vector<Edge> eq = {{0, 1, 1}, {1, 2, 1}, {2, 0, 1}, {2, 3, 1}};
    CHECK(kruskal(4, eq, tree) == 3);
    std::printf("kruskal: %s (%d failures)\n", failures ? "FAIL" : "ok", failures);
    return failures ? 1 : 0;
}

int main(int argc, char** argv) {
    if (argc > 1 && std::strcmp(argv[1], "--test") == 0) return run_tests();
    std::vector<Edge> tree;
    long long w = kruskal(6, demo_edges(), tree);
    std::printf("Kruskal MST weight %lld, edges:", w);
    for (const Edge& e : tree) std::printf(" (%c,%c,%lld)", 'a' + e.u, 'a' + e.v, e.w);
    std::printf("\n");
    return 0;
}
