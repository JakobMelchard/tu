"""SAT, 3SAT and the chain of Karp reductions SAT -> 3SAT -> VERTEX COVER -> SUBSET SUM.

Belongs to the complexity note B01 (models and NP-completeness).

CNF format: a formula is a list of clauses, a clause a list of nonzero ints
(DIMACS style: literal k means variable k, -k its negation; variables are 1..n).

Implements: brute_force_sat, dpll (unit propagation + branching, cross-check),
sat_to_3sat (clause splitting with fresh variables), three_sat_to_vertex_cover
(triangle gadget + variable edges, also gives the INDEPENDENT SET instance),
vertex_cover_to_subset_sum (KT 8.8 base-4 digit encoding), and brute-force
vertex_cover_exists / independent_set_exists / subset_sum_exists for tiny
instances.  Every reduction is polynomial time and preserves yes/no answers.
"""
from itertools import combinations, product


# ---------------------------------------------------------------- SAT solvers
def num_vars(cnf):
    return max((abs(l) for c in cnf for l in c), default=0)


def evaluate(cnf, assignment):
    """assignment: dict var -> bool. A clause is true iff one literal is true."""
    return all(any(assignment[abs(l)] == (l > 0) for l in c) for c in cnf)


def brute_force_sat(cnf):
    """Try all 2^n assignments; return a satisfying dict or None."""
    n = num_vars(cnf)
    for bits in product((False, True), repeat=n):
        a = {i + 1: b for i, b in enumerate(bits)}
        if evaluate(cnf, a):
            return a
    return None


def dpll(cnf, assignment=None):
    """Davis-Putnam-Logemann-Loveland: simplify, unit-propagate, branch on a variable.

    Returns a satisfying assignment (possibly partial: unmentioned variables are
    free) or None.  Exponential worst case, but the standard practical algorithm.
    """
    assignment = dict(assignment or {})
    clauses = [list(c) for c in cnf]
    while True:
        # simplify under the current partial assignment
        new = []
        for c in clauses:
            if any(abs(l) in assignment and assignment[abs(l)] == (l > 0) for l in c):
                continue  # clause satisfied
            rest = [l for l in c if abs(l) not in assignment]
            if not rest:
                return None  # empty clause: conflict
            new.append(rest)
        clauses = new
        if not clauses:
            return assignment
        units = [c[0] for c in clauses if len(c) == 1]
        if not units:
            break
        for l in units:  # unit propagation: forced literal
            if abs(l) in assignment and assignment[abs(l)] != (l > 0):
                return None
            assignment[abs(l)] = l > 0
    v = abs(clauses[0][0])  # branch
    for val in (True, False):
        r = dpll(clauses, {**assignment, v: val})
        if r is not None:
            return r
    return None


# --------------------------------------------------------------- SAT -> 3SAT
def sat_to_3sat(cnf):
    """Clause splitting.  Each clause (l1 ... lk), k > 3, becomes the chain
    (l1 l2 y1)(-y1 l3 y2)...(-y_{k-3} l_{k-1} l_k) with fresh y's; k < 3 clauses are
    padded by repeating a literal.  Equisatisfiable, size O(|F|)."""
    fresh = num_vars(cnf)
    out = []
    for c in cnf:
        c = list(c)
        if len(c) <= 3:
            while len(c) < 3:
                c.append(c[0])
            out.append(c)
            continue
        fresh += 1
        out.append([c[0], c[1], fresh])
        for l in c[2:-2]:
            out.append([-fresh, l, fresh + 1])
            fresh += 1
        out.append([-fresh, c[-2], c[-1]])
    return out


# --------------------------------------------------- 3SAT -> IS / VERTEX COVER
def three_sat_to_vertex_cover(cnf):
    """KT 8.4 / 8.2: one triangle per clause (vertices = literal occurrences),
    plus an edge between every pair of complementary occurrences.

    Returns (vertices, edges, k_is, k_vc): the graph has an independent set of
    size k_is = #clauses iff F is satisfiable iff it has a vertex cover of size
    k_vc = 3 * #clauses - #clauses = 2 * #clauses.  Vertices are (clause, pos).
    """
    m = len(cnf)
    vertices = [(i, j) for i in range(m) for j in range(3)]
    edges = set()
    for i in range(m):
        for j1, j2 in combinations(range(3), 2):
            edges.add(((i, j1), (i, j2)))
    for (i1, j1), (i2, j2) in combinations(vertices, 2):
        if cnf[i1][j1] == -cnf[i2][j2]:
            edges.add(((i1, j1), (i2, j2)))
    return vertices, sorted(edges), m, 3 * m - m


def assignment_to_independent_set(cnf, assignment):
    """Pick one true literal per clause: independent by construction."""
    return [(i, next(j for j, l in enumerate(c) if assignment[abs(l)] == (l > 0)))
            for i, c in enumerate(cnf)]


def independent_set_exists(vertices, edges, k):
    for S in combinations(vertices, k):
        s = set(S)
        if not any(u in s and v in s for u, v in edges):
            return S
    return None


def vertex_cover_exists(vertices, edges, k):
    """Brute force over subsets of size k (complement of an independent set)."""
    for C in combinations(vertices, k):
        c = set(C)
        if all(u in c or v in c for u, v in edges):
            return C
    return None


# -------------------------------------------------- VERTEX COVER -> SUBSET SUM
def vertex_cover_to_subset_sum(vertices, edges, k):
    """KT 8.8: base-4 digits, one digit per edge plus a leading digit.

    Vertex v  -> a_v = 4^m + sum_{edges i incident to v} 4^i.
    Edge i    -> b_i = 4^i.
    Target    -> W = k * 4^m + 2 * sum_i 4^i.
    No column can carry (each column sums to at most 3), so a subset summing
    to W picks exactly k vertices and makes every edge digit equal 2, i.e.
    every edge is covered (1 or 2 endpoints, filled up with b_i).
    Returns (numbers, target).
    """
    m = len(edges)
    idx = {e: i for i, e in enumerate(edges)}
    nums = []
    for v in vertices:
        a = 4 ** m
        for e in edges:
            if v in e:
                a += 4 ** idx[e]
        nums.append(a)
    nums.extend(4 ** i for i in range(m))
    target = k * 4 ** m + sum(2 * 4 ** i for i in range(m))
    return nums, target


def subset_sum_exists(nums, target):
    """Exact exponential search: numbers in descending order, prune a branch when
    the partial sum overshoots or cannot reach the target even with all remaining
    numbers.  Returns the chosen indices or None.  Still 2^n in the worst case."""
    order = sorted(range(len(nums)), key=lambda i: -nums[i])
    suffix = [0] * (len(nums) + 1)  # suffix[j] = sum of nums[order[j:]]
    for j in range(len(nums) - 1, -1, -1):
        suffix[j] = suffix[j + 1] + nums[order[j]]

    def go(j, partial, chosen):
        if partial == target:
            return tuple(sorted(chosen))
        if j == len(nums) or partial > target or partial + suffix[j] < target:
            return None
        return (go(j + 1, partial + nums[order[j]], chosen + [order[j]])
                or go(j + 1, partial, chosen))

    return go(0, 0, [])


if __name__ == "__main__":
    F = [[1, 2, -3, 4], [-1, 2], [3, -4], [-2, -3]]
    print("F =", F, "n =", num_vars(F))
    print("brute force:", brute_force_sat(F))
    print("dpll:       ", dpll(F))
    G = sat_to_3sat(F)
    print("3SAT(F) =", G, "(", num_vars(G), "vars )")
    V, E, k_is, k_vc = three_sat_to_vertex_cover(G)
    print(f"graph: {len(V)} vertices, {len(E)} edges, k_IS={k_is}, k_VC={k_vc}")
    print("vertex cover:", vertex_cover_exists(V, E, k_vc))
    nums, W = vertex_cover_to_subset_sum(V, E, k_vc)
    print(f"subset sum: {len(nums)} numbers (largest {max(nums)}), target {W}")
    print("subset found:", subset_sum_exists(nums, W) is not None)
