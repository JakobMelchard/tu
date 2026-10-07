// Edmonds-Karp maximum flow: Ford-Fulkerson with BFS augmenting paths (KT 7.1-7.2).
// Belongs to note A06. Adjacency list of residual arcs stored in pairs (e, e^1).
// O(n m^2). Also extracts the min cut as the residual-reachable set.
// Usage: ./edmonds_karp        -> demo
//        ./edmonds_karp --test -> self-check, exit 1 on failure
#include <cstdio>
#include <cstring>
#include <queue>
#include <vector>

struct FlowNetwork {
    struct Arc { int to; long long cap; };  // cap = remaining residual capacity
    int n;
    std::vector<Arc> arcs;                   // arc 2k is the edge, 2k+1 its reverse
    std::vector<std::vector<int>> adj;
    std::vector<long long> orig;             // original capacity of arc 2k
    explicit FlowNetwork(int n_) : n(n_), adj(n_) {}
    int add_edge(int u, int v, long long c) {
        adj[u].push_back((int)arcs.size()); arcs.push_back({v, c});
        adj[v].push_back((int)arcs.size()); arcs.push_back({u, 0});
        orig.push_back(c);
        return (int)orig.size() - 1;
    }
    long long flow_on(int k) const { return orig[k] - arcs[2 * k].cap; }

    long long max_flow(int s, int t) {
        long long total = 0;
        std::vector<int> pred(n);            // arc used to reach each node
        while (true) {
            std::fill(pred.begin(), pred.end(), -1);
            pred[s] = -2;
            std::queue<int> q; q.push(s);   // BFS: fewest-arc augmenting path
            while (!q.empty() && pred[t] == -1) {
                int u = q.front(); q.pop();
                for (int a : adj[u])
                    if (arcs[a].cap > 0 && pred[arcs[a].to] == -1) { pred[arcs[a].to] = a; q.push(arcs[a].to); }
            }
            if (pred[t] == -1) break;        // no augmenting path: flow is maximum
            long long b = -1;                // bottleneck
            for (int v = t; v != s; v = arcs[pred[v] ^ 1].to)
                b = (b < 0 || arcs[pred[v]].cap < b) ? arcs[pred[v]].cap : b;
            for (int v = t; v != s; v = arcs[pred[v] ^ 1].to) {
                arcs[pred[v]].cap -= b;      // push forward, open the reverse arc
                arcs[pred[v] ^ 1].cap += b;
            }
            total += b;
        }
        return total;
    }

    // After max_flow: nodes reachable from s in the residual graph form the source side of a min cut.
    std::vector<bool> min_cut_side(int s) const {
        std::vector<bool> in(n, false);
        std::vector<int> st = {s};
        in[s] = true;
        while (!st.empty()) {
            int u = st.back(); st.pop_back();
            for (int a : adj[u]) if (arcs[a].cap > 0 && !in[arcs[a].to]) { in[arcs[a].to] = true; st.push_back(arcs[a].to); }
        }
        return in;
    }
    long long cut_capacity(const std::vector<bool>& in) const {
        long long c = 0;
        for (size_t k = 0; k < orig.size(); ++k) {
            int u = arcs[2 * k + 1].to, v = arcs[2 * k].to;
            if (in[u] && !in[v]) c += orig[k];
        }
        return c;
    }
};

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("  CHECK failed: %s (line %d)\n", #cond, __LINE__); ++failures; } } while (0)

static FlowNetwork demo_network() {
    // s=0, a=1, b=2, c=3, t=4; same instance as the Python flow.py demo (max flow 14)
    FlowNetwork g(5);
    g.add_edge(0, 1, 10); g.add_edge(0, 2, 10); g.add_edge(1, 2, 2); g.add_edge(1, 4, 4);
    g.add_edge(1, 3, 8); g.add_edge(2, 3, 9); g.add_edge(3, 4, 10); g.add_edge(3, 2, 6);
    return g;
}

static int run_tests() {
    FlowNetwork g = demo_network();
    long long f = g.max_flow(0, 4);
    CHECK(f == 14);
    auto side = g.min_cut_side(0);
    CHECK(side[0] && !side[4]);
    CHECK(g.cut_capacity(side) == f);        // max-flow min-cut theorem
    for (size_t k = 0; k < g.orig.size(); ++k) CHECK(0 <= g.flow_on((int)k) && g.flow_on((int)k) <= g.orig[k]);
    // KT figure 7.6-style instance where the wrong path choice would need many augmentations
    FlowNetwork h(4);
    h.add_edge(0, 1, 100); h.add_edge(0, 2, 100); h.add_edge(1, 2, 1); h.add_edge(1, 3, 100); h.add_edge(2, 3, 100);
    CHECK(h.max_flow(0, 3) == 200);
    // bipartite matching 3x3 via unit capacities: L={1,2,3}, R={4,5,6}
    FlowNetwork m(8);
    for (int l = 1; l <= 3; ++l) m.add_edge(0, l, 1);
    for (int r = 4; r <= 6; ++r) m.add_edge(r, 7, 1);
    m.add_edge(1, 4, 1); m.add_edge(1, 5, 1); m.add_edge(2, 4, 1); m.add_edge(3, 6, 1);
    CHECK(m.max_flow(0, 7) == 3);
    FlowNetwork none(3);
    none.add_edge(0, 1, 5);
    CHECK(none.max_flow(0, 2) == 0);
    std::printf("edmonds_karp: %s (%d failures)\n", failures ? "FAIL" : "ok", failures);
    return failures ? 1 : 0;
}

int main(int argc, char** argv) {
    if (argc > 1 && std::strcmp(argv[1], "--test") == 0) return run_tests();
    FlowNetwork g = demo_network();
    long long f = g.max_flow(0, 4);
    auto side = g.min_cut_side(0);
    std::printf("Edmonds-Karp max flow s->t = %lld; min cut source side:", f);
    for (int v = 0; v < g.n; ++v) if (side[v]) std::printf(" %d", v);
    std::printf(" (capacity %lld)\nflow per edge:", g.cut_capacity(side));
    for (size_t k = 0; k < g.orig.size(); ++k)
        std::printf(" %d->%d:%lld/%lld", g.arcs[2 * k + 1].to, g.arcs[2 * k].to, g.flow_on((int)k), g.orig[k]);
    std::printf("\n");
    return 0;
}
