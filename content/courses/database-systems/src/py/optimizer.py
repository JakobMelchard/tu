"""Cardinality estimation, a simple cost model and join ordering by dynamic
programming (note 10).

Estimates ([S6] ch. 16, [S14] Table 1):
  sel_eq(V)                  1 / V(A, r)             (uniform distribution)
  sel_range(v, lo, hi)       (hi - v) / (hi - lo)    for A > v, linear interpolation
  SELINGER_DEFAULTS          1/10 (=), 1/3 (open range), 1/4 (BETWEEN) without statistics
  sel_and / sel_or / sel_not independence: prod s_i;  1 - prod (1 - s_i);  1 - s
  join_size(nr, ns, Vr, Vs)  nr * ns / max(V(A, r), V(A, s))

Cost model: C_out = sum of the estimated sizes of all intermediate results
(the final result is the same for every plan, so it is not counted).  It
ignores access paths and join algorithms on purpose: the note uses it to show
what join ORDER does, which is the part plan enumeration decides.

  best_plan(q, bushy=False, cross=False)   DP over subsets (System R style [S14]):
      best[S] = min over splits S = L u R of best[L] + best[R] + size(S)
      left-deep: R restricted to one relation.  cross=False skips splits with
      no join predicate between L and R (the [S14] heuristic).
  brute_force(q, bushy)      enumerate every tree; the tests check DP == brute force
  count_left_deep(n) = n!,  count_bushy(n) = (2(n-1))! / (n-1)!   ([S6] ch. 16)
"""
import math
from functools import lru_cache
from itertools import combinations, permutations

SELINGER_DEFAULTS = {"eq": 1 / 10, "range": 1 / 3, "between": 1 / 4}


def sel_eq(V):
    return 1 / V


def sel_range(v, lo, hi):
    """Selectivity of A > v with min lo and max hi; clipped to [0, 1]."""
    return min(1.0, max(0.0, (hi - v) / (hi - lo)))


def sel_and(*s):
    return math.prod(s)


def sel_or(*s):
    return 1 - math.prod(1 - x for x in s)


def sel_not(s):
    return 1 - s


def join_size(nr, ns, Vr, Vs):
    return nr * ns / max(Vr, Vs)


class Query:
    """rels: name -> (cardinality, {attr: distinct values}); preds: [(r, a, s, b)]
    meaning r.a = s.b; filters: name -> selectivity applied to the base relation."""

    def __init__(self, rels, preds, filters=None):
        self.rels, self.preds = rels, preds
        self.filters = filters or {}
        self.names = tuple(sorted(rels))

    def base(self, r):
        return self.rels[r][0] * self.filters.get(r, 1.0)

    def size(self, S):
        """Estimated |join of S| = prod |r| * prod over predicates inside S of 1/max(V)."""
        S = frozenset(S)
        est = math.prod(self.base(r) for r in S)
        for r, a, s, b in self.preds:
            if r in S and s in S:
                est /= max(self.rels[r][1][a], self.rels[s][1][b])
        return est

    def connected(self, L, R):
        return any((r in L and s in R) or (r in R and s in L) for r, _, s, _ in self.preds)


def best_plan(q, bushy=False, cross=False):
    """Returns (C_out, plan) where plan is a nested tuple of relation names."""
    best = {frozenset([r]): (0.0, r) for r in q.names}
    for k in range(2, len(q.names) + 1):
        for S in map(frozenset, combinations(q.names, k)):
            cands = []
            for L in _splits(S, bushy):
                R = S - L
                if L not in best or R not in best:
                    continue
                if not cross and not q.connected(L, R):
                    continue
                cost = best[L][0] + best[R][0] + (q.size(S) if len(S) < len(q.names) else 0)
                cands.append((cost, repr((best[L][1], best[R][1])), (best[L][1], best[R][1])))
            if cands:
                c, _, plan = min(cands)
                best[S] = (c, plan)
    return best.get(frozenset(q.names))


def _splits(S, bushy):
    if bushy:
        items = sorted(S)
        for k in range(1, len(items)):
            for L in combinations(items, k):
                yield frozenset(L)
    else:
        for r in sorted(S):                          # right input is a single base relation
            yield S - {r}


def plan_cost(q, plan):
    """C_out of an explicit plan tree."""
    def walk(p):
        if isinstance(p, str):
            return frozenset([p]), 0.0
        (L, cl), (R, cr) = walk(p[0]), walk(p[1])
        S = L | R
        return S, cl + cr + (q.size(S) if len(S) < len(q.names) else 0)
    return walk(plan)[1]


def all_trees(names, bushy):
    names = tuple(names)
    if len(names) == 1:
        yield names[0]
        return
    if not bushy:
        for perm in permutations(names):
            plan = perm[0]
            for r in perm[1:]:
                plan = (plan, r)
            yield plan
        return
    for k in range(1, len(names)):
        for L in combinations(names, k):
            R = tuple(n for n in names if n not in L)
            for lp in all_trees(L, True):
                for rp in all_trees(R, True):
                    yield (lp, rp)


def brute_force(q, bushy=False, cross=False):
    def ok(p):
        if isinstance(p, str):
            return True
        leaves = lambda t: {t} if isinstance(t, str) else leaves(t[0]) | leaves(t[1])
        return ok(p[0]) and ok(p[1]) and (cross or q.connected(leaves(p[0]), leaves(p[1])))
    return min((plan_cost(q, p), repr(p), p) for p in all_trees(q.names, bushy) if ok(p))


def count_left_deep(n):
    return math.factorial(n)


@lru_cache(maxsize=None)
def count_bushy(n):
    return math.factorial(2 * (n - 1)) // math.factorial(n - 1)


def example():
    """Chain R - S - T - U with selective filters on both ends (note 10 worked example)."""
    rels = {"R": (1000, {"a": 100}), "S": (5000, {"a": 1000, "b": 50}),
            "T": (20000, {"b": 5000, "c": 200}), "U": (100, {"c": 100})}
    preds = [("R", "a", "S", "a"), ("S", "b", "T", "b"), ("T", "c", "U", "c")]
    return Query(rels, preds, filters={"R": 0.01, "U": 0.01})


if __name__ == "__main__":
    q = example()
    print("sizes: |R S| =", q.size("RS"), " |S T| =", q.size("ST"), " |T U| =", q.size("TU"),
          " |R S T U| =", q.size("RSTU"))
    for bushy in (False, True):
        c, plan = best_plan(q, bushy=bushy)
        print(f"{'bushy' if bushy else 'left-deep'} DP optimum: C_out = {c:g}  plan {plan}")
    print("naive (((R S) T) U):", plan_cost(q, ((("R", "S"), "T"), "U")))
    print("with cross products allowed:", best_plan(q, bushy=True, cross=True))
    print("orders for n = 2..6: left-deep", [count_left_deep(n) for n in range(2, 7)],
          " bushy", [count_bushy(n) for n in range(2, 7)])
    print("Selinger defaults:", SELINGER_DEFAULTS, " A > 30 on [0, 120]:", sel_range(30, 0, 120))
