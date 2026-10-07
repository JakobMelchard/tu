"""Log-space flavoured reachability, Savitch's recursion, 2SAT in NL, and
Immerman-Szelepcsenyi inductive counting.

Belongs to the complexity notes B02 (Savitch) and B03 (L, NL, coNL).

Graphs are dicts  vertex -> list of out-neighbours  with vertices 0..n-1.

Implements: nl_reachable (nondeterministic "guess the next vertex" machine, state =
current vertex + step counter, exponential time, all branches explored),
savitch_reach (recursive reach(u, v, k) for paths of length <= 2^k, stack depth
O(log n) frames of O(log n) bits), two_sat (implication graph + Kosaraju SCC),
inductive_count / certify_unreachable (Immerman-Szelepcsenyi: count reachable
vertices layer by layer, then prove non-reachability with that count).
"""
import math
from itertools import product


# ------------------------------------------------ NL: guess the path step by step
def nl_reachable(g, s, t):
    """Nondeterministic log-space machine for PATH, run over ALL branches.

    A branch keeps only (current vertex, steps taken): O(log n) bits.  It guesses
    the next vertex, accepts if it reaches t within n-1 steps, rejects otherwise.
    Exploring every guess costs time up to n^n, but no branch stores a path.
    """
    n = len(g)

    def branch(cur, steps):
        if cur == t:
            return True
        if steps >= n - 1:  # a simple path has at most n-1 edges: reject
            return False
        return any(branch(nxt, steps + 1) for nxt in g[cur])  # exists-branch

    return branch(s, 0)


# ------------------------------------------------ Savitch: halve the path length
def savitch_reach(g, u, v, k, trace=None):
    """reach(u, v, k): is there a walk u -> v of length <= 2^k?

    reach(u, v, k) = exists w: reach(u, w, k-1) and reach(w, v, k-1).
    Recursion depth k = ceil(log2 n), each frame stores (u, v, w, k): O(log n) bits,
    so space O(log^2 n).  Time is n^{O(log n)}: Savitch trades time for space.
    trace (optional list) records the maximal recursion depth reached.
    """
    if trace is not None:
        trace[0] = max(trace[0], k)
    if u == v or v in g[u]:
        return True
    if k == 0:
        return False
    return any(savitch_reach(g, u, w, k - 1, trace) and savitch_reach(g, w, v, k - 1, trace)
               for w in g)


def reachable_savitch(g, s, t):
    k = max(1, math.ceil(math.log2(len(g)))) if len(g) > 1 else 1
    return savitch_reach(g, s, t, k)


# ------------------------------------------------ 2SAT via implication graph + SCC
def kosaraju_scc(g):
    """Returns dict vertex -> component id (ids are in reverse topological order)."""
    order, seen = [], set()

    def dfs1(u):
        seen.add(u)
        for w in g[u]:
            if w not in seen:
                dfs1(w)
        order.append(u)

    for u in g:
        if u not in seen:
            dfs1(u)
    rev = {u: [] for u in g}
    for u in g:
        for w in g[u]:
            rev[w].append(u)
    comp = {}

    def dfs2(u, c):
        comp[u] = c
        for w in rev[u]:
            if w not in comp:
                dfs2(w, c)

    c = 0
    for u in reversed(order):
        if u not in comp:
            dfs2(u, c)
            c += 1
    return comp


def implication_graph(cnf, n):
    """Literal l is vertex 2*(|l|-1) + (l < 0).  Clause (a v b) gives -a -> b, -b -> a."""
    idx = lambda l: 2 * (abs(l) - 1) + (1 if l < 0 else 0)
    g = {i: [] for i in range(2 * n)}
    for a, b in cnf:
        g[idx(-a)].append(idx(b))
        g[idx(-b)].append(idx(a))
    return g


def two_sat(cnf, n):
    """Satisfiable iff no variable x has x and -x in the same SCC.

    Assignment: x = True iff comp[x] comes later in topological order than
    comp[-x] (Kosaraju ids: smaller id = earlier).  Returns dict or None.
    """
    g = implication_graph(cnf, n)
    comp = kosaraju_scc(g)
    a = {}
    for x in range(1, n + 1):
        if comp[2 * (x - 1)] == comp[2 * (x - 1) + 1]:
            return None
        a[x] = comp[2 * (x - 1)] > comp[2 * (x - 1) + 1]
    return a


def two_sat_brute(cnf, n):
    for bits in product((False, True), repeat=n):
        a = {i + 1: b for i, b in enumerate(bits)}
        if all(a[abs(x)] == (x > 0) or a[abs(y)] == (y > 0) for x, y in cnf):
            return a
    return None


# ------------------------------------------------ Immerman-Szelepcsenyi
def nl_reachable_bounded(g, s, t, d):
    if s == t:
        return True
    if d == 0:
        return False
    return any(nl_reachable_bounded(g, w, t, d - 1) for w in g[s])


def inductive_count(g, s, trace=None):
    """Compute c_d = #{v : dist(s, v) <= d} for d = 0..n-1 knowing only c_{d-1}.

    For each candidate v we decide 'v in layer <= d' by enumerating ALL vertices u,
    verifying (by guessing a path) that exactly c_{d-1} of them are in layer <= d-1
    and checking whether some such u is v or has edge u -> v.  If the count of
    verified u's falls short of c_{d-1}, the branch rejects (a cheating guess was
    made).  State: d, c_{d-1}, running counters, v, u -- O(log n) bits.
    """
    n = len(g)
    c_prev = 1  # layer 0 = {s}
    counts = [1]
    for d in range(1, n):
        c_d = 0
        for v in g:
            in_layer = False
            verified = 0
            for u in g:
                if nl_reachable_bounded(g, s, u, d - 1):  # guess-and-check u in L_{d-1}
                    verified += 1
                    if u == v or v in g[u]:
                        in_layer = True
            assert verified == c_prev  # else this branch would reject
            c_d += in_layer
        counts.append(c_d)
        c_prev = c_d
    if trace is not None:
        trace.extend(counts)
    return c_prev


def certify_unreachable(g, s, t):
    """coNL side: with c = #reachable known, enumerate all u, verify c of them are
    reachable (by guessed paths) and that none equals t or has an edge to t.
    Returns True iff t is provably NOT reachable from s."""
    n = len(g)
    c = inductive_count(g, s)
    verified = 0
    for u in g:
        if nl_reachable_bounded(g, s, u, n - 1):
            verified += 1
            if u == t:
                return False
    return verified == c


if __name__ == "__main__":
    g = {0: [1, 2], 1: [3], 2: [3], 3: [4], 4: [], 5: [0]}
    print("graph:", g)
    for t in (4, 5):
        print(f"0 -> {t}: NL guess {nl_reachable(g, 0, t)}, Savitch {reachable_savitch(g, 0, t)},"
              f" certified unreachable {certify_unreachable(g, 0, t)}")
    tr = []
    inductive_count(g, 0, tr)
    print("inductive counts c_0..c_{n-1} =", tr)
    cnf = [(1, 2), (-1, 2), (-2, 3), (-3, -1)]
    print("2SAT", cnf, "->", two_sat(cnf, 3))
    print("2SAT unsat", [(1, 1), (-1, -1)], "->", two_sat([(1, 1), (-1, -1)], 1))
