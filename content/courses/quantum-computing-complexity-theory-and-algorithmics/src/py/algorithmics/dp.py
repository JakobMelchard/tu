"""Dynamic programming (KT ch. 6): weighted interval scheduling, subset sum,
0/1 knapsack, Bellman-Ford, Floyd-Warshall, sequence alignment, LCS.

Belongs to the algorithmics note on dynamic programming (A05).

Implements: weighted_interval_scheduling, subset_sum, knapsack_01, bellman_ford,
floyd_warshall, sequence_alignment, lcs.
"""
import bisect
import math


def weighted_interval_scheduling(jobs):
    """jobs = [(s, f, v)]. Max total value of compatible jobs (KT 6.1).

    Sort by finish; p(j) = last job finishing <= s_j via bisect on finish times.
    OPT(j) = max(v_j + OPT(p(j)), OPT(j-1)). Returns (value, chosen_indices).
    """
    order = sorted(range(len(jobs)), key=lambda i: jobs[i][1])
    finish = [jobs[i][1] for i in order]
    n = len(jobs)
    p = [bisect.bisect_right(finish, jobs[i][0]) for i in order]  # count of jobs with f <= s
    opt = [0] * (n + 1)
    for j in range(1, n + 1):
        s, f, v = jobs[order[j - 1]]
        opt[j] = max(v + opt[p[j - 1]], opt[j - 1])
    chosen = []
    j = n
    while j > 0:  # trace back the argmax decisions
        v = jobs[order[j - 1]][2]
        if v + opt[p[j - 1]] >= opt[j - 1]:
            chosen.append(order[j - 1])
            j = p[j - 1]
        else:
            j -= 1
    return opt[n], sorted(chosen)


def subset_sum(weights, W):
    """Boolean table M[i][w] = can items 1..i hit weight exactly w (KT 6.4).

    O(nW) pseudo-polynomial. Returns (reachable(W), table).
    """
    n = len(weights)
    M = [[False] * (W + 1) for _ in range(n + 1)]
    M[0][0] = True
    for i in range(1, n + 1):
        wi = weights[i - 1]
        for w in range(W + 1):
            M[i][w] = M[i - 1][w] or (w >= wi and M[i - 1][w - wi])
    return M[n][W], M


def knapsack_01(weights, values, W):
    """0/1 knapsack: OPT(i, w) = max(OPT(i-1, w), v_i + OPT(i-1, w - w_i)).

    O(nW). Returns (best_value, chosen_indices) by tracing the table back.
    """
    n = len(weights)
    opt = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wi, vi = weights[i - 1], values[i - 1]
        for w in range(W + 1):
            opt[i][w] = opt[i - 1][w]
            if w >= wi and opt[i - 1][w - wi] + vi > opt[i][w]:
                opt[i][w] = opt[i - 1][w - wi] + vi
    chosen = []
    w = W
    for i in range(n, 0, -1):
        if opt[i][w] != opt[i - 1][w]:  # item i was taken
            chosen.append(i - 1)
            w -= weights[i - 1]
    return opt[n][W], sorted(chosen)


def bellman_ford(nodes, edges, s):
    """Shortest paths with negative weights allowed (KT 6.8).

    n-1 rounds of relaxing every edge: after round i, dist is optimal over
    paths with <= i edges. A further improving relaxation means a negative
    cycle reachable from s. Returns (dist, parent, has_negative_cycle).
    """
    dist = {u: math.inf for u in nodes}
    parent = {u: None for u in nodes}
    dist[s] = 0
    for _ in range(len(nodes) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if not changed:
            break
    neg = any(dist[u] + w < dist[v] for u, v, w in edges)
    return dist, parent, neg


def floyd_warshall(nodes, edges):
    """All-pairs shortest paths: d_k(i,j) = min(d_{k-1}(i,j), d_{k-1}(i,k) + d_{k-1}(k,j)).

    O(n^3). Returns dict-of-dicts; a negative diagonal entry signals a negative cycle.
    """
    d = {u: {v: (0 if u == v else math.inf) for v in nodes} for u in nodes}
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in nodes:
        dk = d[k]
        for i in nodes:
            dik = d[i][k]
            if dik == math.inf:
                continue
            di = d[i]
            for j in nodes:
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d


def sequence_alignment(x, y, gap=1, mismatch=1):
    """Needleman-Wunsch minimum-cost alignment (KT 6.6).

    A(i,j) = min(cost(x_i,y_j) + A(i-1,j-1), gap + A(i-1,j), gap + A(i,j-1)).
    mismatch may be a number or a function (a, b) -> cost. Returns
    (cost, aligned_x, aligned_y) with '-' for gaps.
    """
    alpha = mismatch if callable(mismatch) else (lambda a, b: 0 if a == b else mismatch)
    m, n = len(x), len(y)
    A = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        A[i][0] = i * gap
    for j in range(1, n + 1):
        A[0][j] = j * gap
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            A[i][j] = min(alpha(x[i - 1], y[j - 1]) + A[i - 1][j - 1],
                          gap + A[i - 1][j], gap + A[i][j - 1])
    ax, ay = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and A[i][j] == alpha(x[i - 1], y[j - 1]) + A[i - 1][j - 1]:
            ax.append(x[i - 1]); ay.append(y[j - 1]); i -= 1; j -= 1
        elif i > 0 and A[i][j] == gap + A[i - 1][j]:
            ax.append(x[i - 1]); ay.append("-"); i -= 1
        else:
            ax.append("-"); ay.append(y[j - 1]); j -= 1
    return A[m][n], "".join(reversed(ax)), "".join(reversed(ay))


def lcs(x, y):
    """Longest common subsequence: L(i,j) = L(i-1,j-1)+1 if match else max(...).

    Returns (length, one LCS string).
    """
    m, n = len(x), len(y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    out = []
    i, j = m, n
    while i > 0 and j > 0:
        if x[i - 1] == y[j - 1]:
            out.append(x[i - 1]); i -= 1; j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return L[m][n], "".join(reversed(out))


if __name__ == "__main__":
    jobs = [(1, 4, 2), (3, 5, 4), (0, 6, 4), (4, 7, 7), (3, 8, 2), (5, 9, 1)]
    print("weighted interval scheduling:", weighted_interval_scheduling(jobs))
    print("subset sum {3,34,4,12,5,2} hits 9:", subset_sum([3, 34, 4, 12, 5, 2], 9)[0])
    print("knapsack W=11:", knapsack_01([1, 2, 5, 6, 7], [1, 6, 18, 22, 28], 11))
    nodes = ["s", "a", "b", "t"]
    edges = [("s", "a", 4), ("s", "b", 2), ("b", "a", -3), ("a", "t", 1), ("b", "t", 5)]
    d, p, neg = bellman_ford(nodes, edges, "s")
    print("Bellman-Ford:", d, "negative cycle:", neg)
    fw = floyd_warshall(nodes, edges)
    print("Floyd-Warshall s->t:", fw["s"]["t"])
    print("alignment:", sequence_alignment("ocurrance", "occurrence", gap=1, mismatch=1))
    print("lcs:", lcs("AGGTAB", "GXTXAYB"))
