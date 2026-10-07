// Dijkstra's shortest paths with a binary heap (KT 4.4). Belongs to note A03.
// Adjacency list, lazy-deletion priority queue: O((n + m) log n).
// Usage: ./dijkstra        -> demo on a small graph
//        ./dijkstra --test -> self-check against hard-coded answers, exit 1 on failure
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <queue>
#include <vector>

using Weight = long long;
const Weight INF = std::numeric_limits<Weight>::max() / 4;

struct Edge { int to; Weight w; };

struct Graph {
    int n;
    std::vector<std::vector<Edge>> adj;
    explicit Graph(int n_) : n(n_), adj(n_) {}
    void add_edge(int u, int v, Weight w, bool directed = true) {
        adj[u].push_back({v, w});
        if (!directed) adj[v].push_back({u, w});
    }
};

// Returns dist (INF if unreachable) and parent (-1 for source/unreachable).
void dijkstra(const Graph& g, int s, std::vector<Weight>& dist, std::vector<int>& parent) {
    dist.assign(g.n, INF);
    parent.assign(g.n, -1);
    using Item = std::pair<Weight, int>;  // (tentative distance, node)
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    dist[s] = 0;
    pq.push({0, s});
    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;  // stale entry: a shorter path was found later
        for (const Edge& e : g.adj[u]) {
            Weight nd = d + e.w;
            if (nd < dist[e.to]) {  // relax
                dist[e.to] = nd;
                parent[e.to] = u;
                pq.push({nd, e.to});
            }
        }
    }
}

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("  CHECK failed: %s (line %d)\n", #cond, __LINE__); ++failures; } } while (0)

static Graph demo_graph() {
    // KT-style example: s=0, a=1, b=2, c=3, t=4
    Graph g(5);
    g.add_edge(0, 1, 4); g.add_edge(0, 2, 1); g.add_edge(2, 1, 2);
    g.add_edge(1, 3, 1); g.add_edge(2, 3, 5); g.add_edge(3, 4, 3); g.add_edge(1, 4, 6);
    return g;
}

static int run_tests() {
    std::vector<Weight> dist; std::vector<int> parent;
    Graph g = demo_graph();
    dijkstra(g, 0, dist, parent);
    CHECK((dist == std::vector<Weight>{0, 3, 1, 4, 7}));
    CHECK(parent[4] == 3 && parent[3] == 1 && parent[1] == 2 && parent[2] == 0);
    // unreachable node and zero-weight edges
    Graph h(4);
    h.add_edge(0, 1, 0); h.add_edge(1, 2, 0);
    dijkstra(h, 0, dist, parent);
    CHECK(dist[2] == 0 && dist[3] == INF && parent[3] == -1);
    // undirected triangle with a long direct edge: shortest path goes around
    Graph t(3);
    t.add_edge(0, 1, 1, false); t.add_edge(1, 2, 1, false); t.add_edge(0, 2, 10, false);
    dijkstra(t, 0, dist, parent);
    CHECK(dist[2] == 2 && parent[2] == 1);
    std::printf("dijkstra: %s (%d failures)\n", failures ? "FAIL" : "ok", failures);
    return failures ? 1 : 0;
}

int main(int argc, char** argv) {
    if (argc > 1 && std::strcmp(argv[1], "--test") == 0) return run_tests();
    Graph g = demo_graph();
    std::vector<Weight> dist; std::vector<int> parent;
    dijkstra(g, 0, dist, parent);
    std::printf("Dijkstra from node 0:\n");
    for (int v = 0; v < g.n; ++v) {
        std::printf("  node %d: dist %lld, path:", v, dist[v]);
        std::vector<int> path;
        for (int x = v; x != -1; x = parent[x]) path.push_back(x);
        for (auto it = path.rbegin(); it != path.rend(); ++it) std::printf(" %d", *it);
        std::printf("\n");
    }
    return 0;
}
