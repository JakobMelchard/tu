"""Linear and integer programming (KT 11.6, Papadimitriou ch. 1-2 style):
vertex cover LP/ILP, integrality gap, LP rounding, max-flow LP and its dual,
branch and bound, and a tableau simplex with Bland's rule.

Belongs to the algorithmics note on LP / ILP (A08).

Implements: vertex_cover_lp, vertex_cover_ilp, vertex_cover_lp_rounding,
integrality_gap, max_flow_lp, min_cut_dual_lp, branch_and_bound, simplex,
solve_ilp (pulp CBC if available, else scipy milp; see ILP_BACKEND).
"""
import math
import warnings

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

try:
    import pulp
    ILP_BACKEND = "pulp" if pulp.listSolvers(onlyAvailable=True) else "milp"
except ImportError:  # pragma: no cover
    pulp = None
    ILP_BACKEND = "milp"


# ---------------------------------------------------------------- generic ILP
def solve_ilp(c, A_ub, b_ub, bounds, integrality):
    """min c.x  s.t. A_ub x <= b_ub, bounds, x_i integer where integrality[i].

    Uses pulp's CBC when installed, otherwise scipy.optimize.milp (HiGHS).
    Returns (value, x as numpy array).
    """
    if ILP_BACKEND == "pulp":
        prob = pulp.LpProblem("ilp", pulp.LpMinimize)
        xs = [prob.add_variable(f"x{i}", lo, hi, cat=pulp.LpInteger if integrality[i] else pulp.LpContinuous)
              for i, (lo, hi) in enumerate(bounds)]
        prob += pulp.lpSum(ci * xi for ci, xi in zip(c, xs))
        for row, b in zip(A_ub, b_ub):
            prob += pulp.lpSum(a * xi for a, xi in zip(row, xs) if a) <= b
        with warnings.catch_warnings():  # bundled CBC is deprecated in pulp 3.x but the only one installed
            warnings.simplefilter("ignore", DeprecationWarning)
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
        x = np.array([v.value() for v in xs], dtype=float)
        return float(np.dot(c, x)), x
    lo = [b[0] for b in bounds]
    hi = [math.inf if b[1] is None else b[1] for b in bounds]
    cons = LinearConstraint(np.atleast_2d(A_ub), -np.inf, b_ub) if len(A_ub) else ()
    res = milp(c, constraints=cons, integrality=integrality, bounds=Bounds(lo, hi))
    return float(res.fun), res.x


# ------------------------------------------------------------- vertex cover
def _vc_matrices(nodes, edges):
    """min sum x_v  s.t.  x_u + x_v >= 1  (as -x_u - x_v <= -1),  0<=x<=1."""
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(edges), len(nodes)))
    for k, (u, v) in enumerate(edges):
        A[k, idx[u]] = A[k, idx[v]] = -1
    return np.ones(len(nodes)), A, -np.ones(len(edges))


def vertex_cover_lp(nodes, edges):
    """LP relaxation via HiGHS. Returns (value, dict node -> x_v)."""
    c, A, b = _vc_matrices(nodes, edges)
    res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, 1)] * len(nodes), method="highs")
    return float(res.fun), dict(zip(nodes, res.x))


def vertex_cover_ilp(nodes, edges):
    """Exact integer program. Returns (value, cover set)."""
    c, A, b = _vc_matrices(nodes, edges)
    val, x = solve_ilp(c, A, b, [(0, 1)] * len(nodes), [1] * len(nodes))
    return round(val), {v for v, xv in zip(nodes, x) if xv > 0.5}


def vertex_cover_lp_rounding(nodes, edges):
    """Round x_v >= 1/2 up. Every edge has x_u + x_v >= 1 so one endpoint is
    rounded up: a cover of size <= 2 * LP <= 2 * OPT (KT 11.6)."""
    lp, x = vertex_cover_lp(nodes, edges)
    return {v for v in nodes if x[v] >= 0.5 - 1e-9}, lp


def integrality_gap(nodes, edges):
    """(LP value, ILP value, ILP/LP). K_n: LP n/2 (all x=1/2), ILP n-1."""
    lp, _ = vertex_cover_lp(nodes, edges)
    ilp, _ = vertex_cover_ilp(nodes, edges)
    return lp, ilp, ilp / lp


# ----------------------------------------------------------------- max flow
def max_flow_lp(nodes, edges, s, t):
    """max net flow out of s; conservation at internal nodes; 0 <= f_e <= c_e.

    edges: list of (u, v, cap). Returns (value, {edge index -> flow}).
    """
    m = len(edges)
    c = np.zeros(m)
    for k, (u, v, _) in enumerate(edges):
        c[k] += -1 if u == s else 0  # linprog minimises: negate objective
        c[k] += 1 if v == s else 0
    internal = [v for v in nodes if v not in (s, t)]
    A_eq = np.zeros((len(internal), m))
    for i, w in enumerate(internal):
        for k, (u, v, _) in enumerate(edges):
            if v == w:
                A_eq[i, k] += 1
            if u == w:
                A_eq[i, k] -= 1
    res = linprog(c, A_eq=A_eq if internal else None, b_eq=np.zeros(len(internal)) if internal else None,
                  bounds=[(0, cap) for _, _, cap in edges], method="highs")
    return -float(res.fun), dict(enumerate(res.x))


def min_cut_dual_lp(nodes, edges, s, t):
    """Dual of max_flow_lp: min sum c_e d_e  s.t.  d_e >= p_u - p_v, p_s = 1,
    p_t = 0, d >= 0. An integral optimum is the indicator of a min cut.
    Returns (value, cut side A = {v : p_v >= 1/2})."""
    m, n = len(edges), len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    c = np.concatenate([[cap for _, _, cap in edges], np.zeros(n)])
    A = np.zeros((m, m + n))  # -d_e + p_u - p_v <= 0
    for k, (u, v, _) in enumerate(edges):
        A[k, k] = -1
        A[k, m + idx[u]] += 1
        A[k, m + idx[v]] -= 1
    bounds = [(0, None)] * m + [(0, 1)] * n
    bounds[m + idx[s]] = (1, 1)
    bounds[m + idx[t]] = (0, 0)
    res = linprog(c, A_ub=A, b_ub=np.zeros(m), bounds=bounds, method="highs")
    p = res.x[m:]
    return float(res.fun), {v for v in nodes if p[idx[v]] >= 0.5}


# --------------------------------------------------------- branch and bound
def branch_and_bound(c, A_ub, b_ub, bounds, integrality, tol=1e-6):
    """min c.x, A_ub x <= b_ub, with x_i integer where integrality[i].

    DFS over LP relaxations (linprog/HiGHS). Prune when the relaxation is
    infeasible or its bound is no better than the incumbent; otherwise branch
    on the most fractional integer variable: x_i <= floor or x_i >= ceil.
    Returns (value, x) or (inf, None) if infeasible.
    """
    best_val, best_x = math.inf, None
    stack = [list(bounds)]
    nodes_visited = 0
    while stack:
        bnd = stack.pop()
        nodes_visited += 1
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bnd, method="highs")
        if res.status != 0 or res.fun >= best_val - tol:
            continue
        frac = [(abs(x - round(x)), i) for i, x in enumerate(res.x) if integrality[i]]
        gap, i = max(frac, default=(0, None))
        if gap <= tol:  # integral: new incumbent
            best_val = res.fun
            best_x = np.where(np.array(integrality, bool), np.round(res.x), res.x) + 0.0
            continue
        lo, hi = bnd[i]
        left, right = list(bnd), list(bnd)
        left[i] = (lo, math.floor(res.x[i]))
        right[i] = (math.ceil(res.x[i]), hi)
        stack.extend([right, left])  # explore the floor branch first
    return best_val, best_x


# ------------------------------------------------------------------ simplex
def simplex(c, A, b, max_iter=1000):
    """max c.x  s.t.  A x <= b, x >= 0, with b >= 0 (origin feasible).

    Tableau with slack columns; Bland's rule (smallest-index entering and
    leaving) guarantees termination. Returns (value, x). Raises on unbounded.
    """
    A, b, c = np.asarray(A, float), np.asarray(b, float), np.asarray(c, float)
    m, n = A.shape
    assert np.all(b >= 0), "need b >= 0 for the slack basis to be feasible"
    T = np.zeros((m + 1, n + m + 1))
    T[:m, :n] = A
    T[:m, n:n + m] = np.eye(m)
    T[:m, -1] = b
    T[m, :n] = -c  # reduced costs; negative means improving
    basis = list(range(n, n + m))
    for _ in range(max_iter):
        entering = next((j for j in range(n + m) if T[m, j] < -1e-9), None)
        if entering is None:
            break
        rows = [i for i in range(m) if T[i, entering] > 1e-9]
        if not rows:
            raise ValueError("LP is unbounded")
        ratios = [(T[i, -1] / T[i, entering], basis[i], i) for i in rows]
        _, _, leaving = min(ratios)  # min ratio, ties by smallest basic index
        T[leaving] /= T[leaving, entering]
        for i in range(m + 1):
            if i != leaving:
                T[i] -= T[i, entering] * T[leaving]
        basis[leaving] = entering
    x = np.zeros(n + m)
    for i, j in enumerate(basis):
        x[j] = T[i, -1]
    return float(T[m, -1]), x[:n]


if __name__ == "__main__":
    print("ILP backend:", ILP_BACKEND)
    n = 5
    Kn = [(i, j) for i in range(n) for j in range(i + 1, n)]
    C5 = [(i, (i + 1) % n) for i in range(n)]
    print("K5 integrality gap (LP, ILP, ratio):", integrality_gap(list(range(n)), Kn))
    print("C5 integrality gap (LP, ILP, ratio):", integrality_gap(list(range(n)), C5))
    cover, lp = vertex_cover_lp_rounding(list(range(n)), C5)
    print("C5 LP rounding cover:", sorted(cover), "LP =", lp)
    nodes = ["s", "a", "b", "t"]
    edges = [("s", "a", 3), ("s", "b", 2), ("a", "b", 1), ("a", "t", 2), ("b", "t", 3)]
    fv, f = max_flow_lp(nodes, edges, "s", "t")
    cv, A = min_cut_dual_lp(nodes, edges, "s", "t")
    print("max-flow LP:", fv, "min-cut dual LP:", cv, "cut side:", sorted(A))
    c = [-5, -4]; Aub = [[6, 4], [1, 2], [-1, 1]]; bub = [24, 6, 1]
    print("simplex max 5x+4y:", simplex([5, 4], Aub, bub))
    print("B&B integer version:", branch_and_bound(c, Aub, bub, [(0, None)] * 2, [1, 1]))
