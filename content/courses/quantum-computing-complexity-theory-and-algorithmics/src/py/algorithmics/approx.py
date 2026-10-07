"""Approximation algorithms (KT ch. 11): vertex cover via maximal matching,
list scheduling / LPT for load balancing, greedy set cover, knapsack FPTAS.

Belongs to the algorithmics note on approximation algorithms (A07).

Implements: vertex_cover_2approx, vertex_cover_exact, is_vertex_cover,
load_balancing_greedy, load_balancing_lpt, load_balancing_exact,
set_cover_greedy, set_cover_exact, harmonic, knapsack_fptas,
approximation_ratio. Graphs are (nodes, edges) with edges (u, v).
"""
import heapq
import itertools
import math


def is_vertex_cover(edges, cover):
    return all(u in cover or v in cover for u, v in edges)


def vertex_cover_2approx(edges):
    """Take both endpoints of every edge of a greedily built maximal matching.

    Any cover must contain one endpoint of each matching edge (they are
    disjoint), so |C| = 2|M| <= 2 OPT (KT 11.4 via pricing / LP; this is the
    matching argument). Returns (cover, matching).
    """
    cover, matching = set(), []
    for u, v in edges:
        if u not in cover and v not in cover:
            matching.append((u, v))
            cover.update((u, v))
    return cover, matching


def vertex_cover_exact(nodes, edges):
    """Brute force: smallest subset covering all edges. Exponential; n <= ~15."""
    nodes = list(nodes)
    for k in range(len(nodes) + 1):
        for S in itertools.combinations(nodes, k):
            if is_vertex_cover(edges, set(S)):
                return set(S)
    return set(nodes)


def load_balancing_greedy(jobs, m):
    """List scheduling: assign each job to the currently least loaded machine.

    Makespan <= 2 OPT (KT 11.1): the last job on the max machine started when
    every machine had load >= (sum t)/m <= OPT, and t_j <= OPT.
    Returns (makespan, assignment list machine index per job).
    """
    heap = [(0, i) for i in range(m)]
    assign = [None] * len(jobs)
    for j, t in enumerate(jobs):
        load, i = heapq.heappop(heap)
        assign[j] = i
        heapq.heappush(heap, (load + t, i))
    return max(load for load, _ in heap), assign


def load_balancing_lpt(jobs, m):
    """Sorted (longest processing time first) list scheduling: <= 3/2 OPT."""
    order = sorted(range(len(jobs)), key=lambda j: -jobs[j])
    mk, a = load_balancing_greedy([jobs[j] for j in order], m)
    assign = [None] * len(jobs)
    for pos, j in enumerate(order):
        assign[j] = a[pos]
    return mk, assign


def load_balancing_exact(jobs, m):
    """Brute-force optimal makespan (m^n assignments; tiny instances only)."""
    best = math.inf
    for a in itertools.product(range(m), repeat=len(jobs)):
        loads = [0] * m
        for j, i in enumerate(a):
            loads[i] += jobs[j]
        best = min(best, max(loads))
    return best


def set_cover_greedy(universe, sets, weights=None):
    """Repeatedly pick the set with smallest weight per newly covered element.

    Total weight <= H(d*) OPT where d* = largest set size (KT 11.3).
    Returns list of chosen set indices.
    """
    weights = [1] * len(sets) if weights is None else weights
    uncovered = set(universe)
    chosen = []
    while uncovered:
        best, best_ratio = None, math.inf
        for i, S in enumerate(sets):
            gain = len(uncovered & set(S))
            if gain and weights[i] / gain < best_ratio:
                best, best_ratio = i, weights[i] / gain
        if best is None:
            raise ValueError("universe not coverable")
        chosen.append(best)
        uncovered -= set(sets[best])
    return chosen


def set_cover_exact(universe, sets, weights=None):
    """Brute-force minimum-weight cover (2^k subsets of sets)."""
    weights = [1] * len(sets) if weights is None else weights
    universe = set(universe)
    best, best_w = None, math.inf
    for r in range(len(sets) + 1):
        for combo in itertools.combinations(range(len(sets)), r):
            w = sum(weights[i] for i in combo)
            if w < best_w and set().union(*(sets[i] for i in combo)) >= universe:
                best, best_w = list(combo), w
    return best, best_w


def harmonic(d):
    return sum(1 / i for i in range(1, d + 1))


def knapsack_fptas(weights, values, W, eps):
    """(1 - eps)-approximation in O(n^3 / eps) by scaling values (KT 11.8).

    Round v_i to ceil(v_i / b) with b = eps * v_max / (2n); solve exact DP over
    the (small) total rounded value: OPT_dp(v) = min weight achieving value v.
    Returns (value, chosen_indices).
    """
    n = len(values)
    vmax = max(values)
    b = eps * vmax / (2 * n)
    vt = [math.ceil(v / b) for v in values]
    V = sum(vt)
    INF = math.inf
    minw = [[INF] * (V + 1) for _ in range(n + 1)]  # minw[i][v]: min weight, items < i, value v
    minw[0][0] = 0
    for i in range(1, n + 1):
        for v in range(V + 1):
            minw[i][v] = minw[i - 1][v]
            if v >= vt[i - 1] and minw[i - 1][v - vt[i - 1]] + weights[i - 1] < minw[i][v]:
                minw[i][v] = minw[i - 1][v - vt[i - 1]] + weights[i - 1]
    v = max(v for v in range(V + 1) if minw[n][v] <= W)
    chosen = []
    for i in range(n, 0, -1):
        if minw[i][v] != minw[i - 1][v]:
            chosen.append(i - 1)
            v -= vt[i - 1]
    chosen.sort()
    return sum(values[i] for i in chosen), chosen


def approximation_ratio(approx_fn, exact_fn, instances):
    """Worst observed ratio approx/exact (>= 1 for minimisation) over instances."""
    return max(approx_fn(*inst) / exact_fn(*inst) for inst in instances)


if __name__ == "__main__":
    import random
    rng = random.Random(0)
    nodes = list(range(10))
    edges = [(u, v) for u in nodes for v in nodes if u < v and rng.random() < 0.3]
    c, m = vertex_cover_2approx(edges)
    print(f"vertex cover: 2-approx size {len(c)}, optimum {len(vertex_cover_exact(nodes, edges))}")
    jobs = [rng.randint(1, 10) for _ in range(8)]
    print("load balancing greedy/LPT/opt:", load_balancing_greedy(jobs, 3)[0],
          load_balancing_lpt(jobs, 3)[0], load_balancing_exact(jobs, 3))
    U = range(12)
    sets = [set(rng.sample(range(12), rng.randint(2, 5))) for _ in range(8)] + [set(range(12)) - {0}, {0}]
    g = set_cover_greedy(U, sets)
    print("set cover greedy:", len(g), "optimum:", set_cover_exact(U, sets)[1], "H(d*)=%.2f" % harmonic(11))
    w = [rng.randint(1, 20) for _ in range(10)]
    v = [rng.randint(1, 100) for _ in range(10)]
    print("knapsack FPTAS eps=0.2:", knapsack_fptas(w, v, 40, 0.2))
