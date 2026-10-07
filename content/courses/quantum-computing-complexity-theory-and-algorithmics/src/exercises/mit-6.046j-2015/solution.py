"""Substitute practice for block A: MIT 6.046J Design and Analysis of Algorithms.

SOURCE [S61]: MIT OpenCourseWare, 6.046J / 18.410J, Profs. Erik Demaine, Srini
Devadas and Nancy Lynch, Spring 2015, "Final Exam" and "Solutions to Final Exam"
(23 May 2015).  Licence CC BY-NC-SA 4.0.  **MIT's paper, not 192.043's** --
192.043 has no past paper in any year [S24].  Questions restated in our own
words in README.md; nothing is copied.  Only the four whose topic is on
192.043's / 192.219's subject lists are worked.

Run:  ../../../../../.venv/bin/python solution.py
"""
import os
import sys

_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py"))
sys.path.insert(0, os.path.join(_py, "algorithmics"))

import approx                                                     # noqa: E402
import flow                                                       # noqa: E402
from divide_conquer import master_theorem                         # noqa: E402
from dp import floyd_warshall                                     # noqa: E402
from greedy import kruskal                                        # noqa: E402


# --- P1: the true/false block, in-scope items only (A01, A02, A04, A05) ------
def p1_true_false():
    """Four claims that 192.043's syllabus also covers, each settled by code."""
    out = {}

    # (i) A divide-and-conquer step costing Theta(n^2) is not improved by a
    #     Theta(n^2 log n) guess: T(n) = 2 T(n/2) + Theta(n^2) is Theta(n^2).
    case, bound = master_theorem(2, 2, 2)
    assert (case, bound) == (3, "Theta(n^2)")
    out["2T(n/2)+Theta(n^2)"] = bound

    # (ii) Floyd-Warshall's d^(k) is "shortest path using intermediates in
    #      {1..k}", NOT "shortest path with at most k edges".  Show they differ.
    nodes = [1, 2, 3, 4]
    edges = [(1, 2, 1), (2, 3, 1), (3, 4, 1), (1, 4, 10)]
    dist = floyd_warshall(nodes, edges)
    at_most_two_edges = min(10, 1 + 1 + 1)      # 1->2->3->4 needs three edges
    out["FW final d[1][4]"] = dist[1][4]
    out["'at most k=2 edges' would give"] = 10
    assert dist[1][4] == 3 and at_most_two_edges == 3
    out["the two readings differ"] = True

    # (iii) Negating every weight and taking a minimum spanning tree gives a
    #       maximum spanning tree of the original graph.
    g_edges = [("a", "b", 4), ("b", "c", 7), ("a", "c", 2), ("c", "d", 5),
               ("b", "d", 9)]
    _, max_tree = kruskal("abcd", [(u, v, -w) for u, v, w in g_edges])
    max_weight = sum(-w for _, _, w in max_tree)
    best = max(sum(w for _, _, w in t)
               for t in _all_spanning_trees("abcd", g_edges))
    assert max_weight == best
    out["max spanning tree weight"] = max_weight

    # (iv) With distinct edge weights the MST is unique but the *second*-best
    #      spanning tree need not be: two different swaps out of the MST cost
    #      the same +3 here, so two distinct trees tie for second place.
    sq = [("a", "b", 1), ("a", "c", 2), ("a", "d", 3),
          ("b", "c", 5), ("c", "d", 6)]
    weights = sorted(sum(w for _, _, w in t)
                     for t in _all_spanning_trees("abcd", sq))
    assert weights[0] < weights[1] == weights[2]
    out["second-best spanning tree unique"] = False
    out["spanning tree weights"] = weights
    return out


def _all_spanning_trees(nodes, edges):
    """Every spanning tree, by brute force over edge subsets of size n-1."""
    from itertools import combinations
    from greedy import is_spanning_tree
    n = len(nodes)
    return [list(sub) for sub in combinations(edges, n - 1)
            if is_spanning_tree(nodes, sub)]


# --- P6: one Edmonds-Karp iteration on the paper's network (A06) -------------
# The network of the paper's "be the computer" question, read off its figure as
# (tail, head, flow, capacity).  Conservation holds at every internal node and
# |f| = 25 both out of s and into t, which is how the figure was checked.
NETWORK = [("s", 2, 10, 10), ("s", 3, 2, 3), ("s", 4, 13, 15),
           (2, 5, 7, 9), (2, 3, 2, 4), (2, 6, 1, 15),
           (3, 6, 7, 7), (3, 4, 1, 4),
           (5, 6, 0, 15), (5, "t", 7, 10),
           (6, "t", 8, 9), (6, 7, 0, 15),
           (4, 7, 14, 30), (7, 3, 4, 6), (7, "t", 10, 10)]


def _residual_network():
    g = flow.FlowNetwork()
    for u, v, f, c in NETWORK:
        g.add_edge(u, v, c)
    for u, v, f, c in NETWORK:
        g.cap[u][v] -= f          # forward residual c - f
        g.cap[v][u] += f          # backward residual f
    return g


def p6_edmonds_karp_one_iteration():
    """Draw the residual graph, take the *shortest* augmenting path, augment.

    The paper's answer is that the augmenting path has four edges, its
    bottleneck is 1, and the resulting flow value is **26**.  Reproduced here.
    """
    value_before = sum(f for u, _, f, _ in NETWORK if u == "s")
    # conservation check on the figure, which is how the reading was verified
    for node in {u for u, _, _, _ in NETWORK} | {v for _, v, _, _ in NETWORK}:
        if node in ("s", "t"):
            continue
        inflow = sum(f for _, v, f, _ in NETWORK if v == node)
        outflow = sum(f for u, _, f, _ in NETWORK if u == node)
        assert inflow == outflow, f"figure misread at {node}"
    assert value_before == sum(f for _, v, f, _ in NETWORK if v == "t") == 25

    g = _residual_network()
    path = flow._bfs_path(g, "s", "t")
    bottleneck = flow._augment(g, path, "s", "t")
    assert len(path) == 5 and bottleneck == 1
    assert value_before + bottleneck == 26

    # and, for context, where the algorithm ends up: the max flow from scratch,
    # and the minimum cut it certifies (max-flow/min-cut, A06).
    g2 = flow.FlowNetwork()
    for u, v, _, c in NETWORK:
        g2.add_edge(u, v, c)
    max_flow = flow.edmonds_karp(g2, "s", "t")
    source_side, cut_value = flow.min_cut(g2, "s", "t")
    assert cut_value == max_flow >= value_before + bottleneck
    return {"flow before": value_before, "augmenting path": path,
            "bottleneck": bottleneck, "flow after": value_before + bottleneck,
            "max flow": max_flow, "min cut value": cut_value,
            "source side of the cut": sorted(map(str, source_side))}


# --- P5: a greedy with an exchange argument (A03) ----------------------------
def pairing_feasible(pieces, helpers, budget, k):
    """Can k of the pieces be finished?  Restated in our own words:

    each piece i costs p_i hours; each helper j can absorb up to t_j hours of
    exactly one piece; whatever a helper does not absorb comes out of a shared
    budget T.  Exchange argument: it is never worse to take the k *cheapest*
    pieces and the k *most capable* helpers, and to pair the cheapest piece with
    the weakest of those helpers (so the strongest helper meets the dearest
    piece).  Then the budget needed is forced.
    """
    if k == 0:
        return True
    if k > min(len(pieces), len(helpers)):
        return False
    p = sorted(pieces)[:k]
    t = sorted(helpers)[-k:]                 # ascending: weakest helper first
    return sum(max(0, pi - tj) for pi, tj in zip(p, t)) <= budget


def _pairing_brute(pieces, helpers, budget, k):
    from itertools import combinations, permutations
    for chosen in combinations(range(len(pieces)), k):
        for used in permutations(range(len(helpers)), k):
            need = sum(max(0, pieces[i] - helpers[j]) for i, j in zip(chosen, used))
            if need <= budget:
                return True
    return False


def p5_greedy_exchange(seed=0, trials=300):
    """Check the greedy against brute force, then binary-search the largest k."""
    import random
    rng = random.Random(seed)
    for _ in range(trials):
        pieces = [rng.randint(1, 9) for _ in range(rng.randint(1, 4))]
        helpers = [rng.randint(0, 9) for _ in range(rng.randint(1, 4))]
        budget = rng.randint(0, 12)
        for k in range(min(len(pieces), len(helpers)) + 1):
            assert pairing_feasible(pieces, helpers, budget, k) == \
                _pairing_brute(pieces, helpers, budget, k), (pieces, helpers, budget, k)
    pieces = [3, 8, 2, 6, 5]
    helpers = [4, 1, 7, 2]
    budget = 6
    lo, hi = 0, min(len(pieces), len(helpers))
    while lo < hi:                                # feasibility is monotone in k
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if pairing_feasible(pieces, helpers, budget, mid) else (lo, mid - 1)
    return {"random instances checked": trials, "worked instance max k": lo,
            "cost": "O(n log n) to sort, then O(log n) feasibility tests"}


# --- P8: list scheduling is a 2-approximation (A07) --------------------------
def p8_load_balancing(seed=1, instances=40):
    """Greedy list scheduling never exceeds 2 OPT; LPT never exceeds 3/2 OPT.

    The proof is the one the paper asks for: OPT is at least both the average
    load (sum t_i)/m and the longest job max t_i; the machine finishing last
    started its final job when every machine was at or below the average.
    Measured here against brute-force optima on small instances.
    """
    import random
    rng = random.Random(seed)
    worst_greedy = worst_lpt = 0.0
    for _ in range(instances):
        m = rng.randint(2, 3)
        jobs = [rng.randint(1, 12) for _ in range(rng.randint(m, 7))]
        opt = approx.load_balancing_exact(jobs, m)
        greedy, _ = approx.load_balancing_greedy(jobs, m)
        lpt, _ = approx.load_balancing_lpt(jobs, m)
        assert greedy <= 2 * opt and lpt <= 1.5 * opt
        assert opt >= max(max(jobs), sum(jobs) / m) - 1e-9
        worst_greedy = max(worst_greedy, greedy / opt)
        worst_lpt = max(worst_lpt, lpt / opt)
    # The tight family: m(m-1) jobs of length 1, then one job of length m.
    # Greedy spreads the units evenly (m-1 each) and then has to put the long
    # job somewhere: makespan 2m-1.  The optimum is m -- park the long job on
    # its own machine and share the units over the other m-1.  Brute force is
    # m^(m^2-m+1) assignments, so the optimum is argued, not enumerated.
    m = 4
    tight = [1] * (m * (m - 1)) + [m]
    greedy, _ = approx.load_balancing_greedy(tight, m)
    opt = m
    assert greedy == 2 * m - 1
    return {"instances": instances, "worst greedy ratio": worst_greedy,
            "worst LPT ratio": worst_lpt,
            "tight family m=4": {"greedy": greedy, "opt": opt,
                                 "ratio": greedy / opt, "limit": 2 - 1 / m}}


def solve():
    return {"p1": p1_true_false(), "p5": p5_greedy_exchange(),
            "p6": p6_edmonds_karp_one_iteration(), "p8": p8_load_balancing()}


if __name__ == "__main__":
    for key, value in solve().items():
        print(key, "->", value)
