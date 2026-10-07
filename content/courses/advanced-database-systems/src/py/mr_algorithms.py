"""Relational algebra and matrix multiplication as MapReduce jobs, note 05.

Follows [S17] 2.3.3-2.3.10 and 2.6.7, using mapreduce.run_job. Relations are
lists of tuples (bags); set semantics is restored where the operator needs it.

Operator      map emits                       reduce                     r
selection     (t, t) if C(t)                  none (map-only)            <=1
projection    (t[L], t[L])                    emit key once (dedup)      1
union         (t, t) from R and S             emit key once              1
intersection  (t, 'R') / (t, 'S')             emit t if both tags        1
difference    (t, 'R') / (t, 'S')             emit t if only 'R'         1
group-by      (a, b)                          (a, agg(bs))               1

Matrix product P = M N (n x n):
one round   M[i,j] -> ((i,k), ('M', j, m)) for all k; N[j,k] -> ((i,k), ('N', j, n))
            for all i. r = n, q = 2n; with g x g blocks r = g, q = 2n^2/g and the
            lower bound r >= 2n^2/q is met [S17 2.6.7].
two rounds  job 1 joins on j and emits ((i,k), m*n); job 2 sums per (i,k).

Run: python mr_algorithms.py
"""
from __future__ import annotations

from mapreduce import run_job, split


def selection(R, cond, n_maps=2):
    return run_job(split(R, n_maps), lambda t: [(t, t)] if cond(t) else [], None)


def projection(R, cols, n_maps=2):
    def m(t):
        p = tuple(t[c] for c in cols)
        yield p, p
    return run_job(split(R, n_maps), m, lambda k, vs: [k])


def union(R, S, n_maps=2):
    return run_job(split(R + S, n_maps), lambda t: [(t, t)], lambda k, vs: [k])


def _tagged(R, S):
    return [(t, "R") for t in R] + [(t, "S") for t in S]


def intersection(R, S, n_maps=2):
    return run_job(split(_tagged(R, S), n_maps), lambda rec: [rec],
                   lambda k, tags: [k] if {"R", "S"} <= set(tags) else [])


def difference(R, S, n_maps=2):
    return run_job(split(_tagged(R, S), n_maps), lambda rec: [rec],
                   lambda k, tags: [k] if set(tags) == {"R"} else [])


def group_by(R, key, val, agg=sum, n_maps=2, combine=True):
    """gamma_{key, agg(val)}(R). The combiner is valid only for associative and
    commutative agg (sum, min, max, count-as-sum), not for avg."""
    comb = (lambda k, vs: [(k, agg(vs))]) if combine else None
    return run_job(split(R, n_maps), lambda t: [(t[key], t[val])],
                   lambda k, vs: [(k, agg(vs))], comb)


def _entries(M):
    return [(i, j, x) for i, row in enumerate(M) for j, x in enumerate(row) if x]


def matmul_one_round(M, N, n_maps=2):
    """Sparse matrices given as nested lists; returns (dict (i,k) -> value, stats)."""
    I, J, K = len(M), len(N), len(N[0])
    recs = [("M",) + e for e in _entries(M)] + [("N",) + e for e in _entries(N)]

    def m(rec):
        tag, a, b, x = rec
        if tag == "M":                               # M[i=a, j=b] is needed by every (i, k)
            for k in range(K):
                yield (a, k), ("M", b, x)
        else:                                        # N[j=a, k=b] is needed by every (i, k)
            for i in range(I):
                yield (i, b), ("N", a, x)

    def r(ik, vals):
        mj = {j: x for tag, j, x in vals if tag == "M"}
        s = sum(x * mj[j] for tag, j, x in vals if tag == "N" and j in mj)
        if s:
            yield ik, s
    out, st = run_job(split(recs, n_maps), m, r)
    assert J == len(M[0])
    return dict(out), st


def matmul_two_rounds(M, N, n_maps=2):
    recs = [("M",) + e for e in _entries(M)] + [("N",) + e for e in _entries(N)]

    def m1(rec):
        tag, a, b, x = rec
        yield (b, ("M", a, x)) if tag == "M" else (a, ("N", b, x))

    def r1(j, vals):                                 # natural join on j
        for tm, i, x in vals:
            for tn, k, y in vals:
                if tm == "M" and tn == "N":
                    yield (i, k), x * y
    products, st1 = run_job(split(recs, n_maps), m1, r1)
    out, st2 = run_job(split(products, n_maps), lambda p: [p],
                       lambda ik, vs: [(ik, sum(vs))], lambda ik, vs: [(ik, sum(vs))])
    return {k: v for k, v in out if v}, (st1, st2)


def demo() -> None:
    R = [(1, "a", 10), (2, "b", 20), (3, "a", 30), (2, "b", 20)]
    S = [(2, "b", 20), (4, "c", 40)]
    print("sigma_{x>1}(R):", sorted(selection(R, lambda t: t[0] > 1)[0]))
    print("pi_{1}(R):     ", sorted(projection(R, [1])[0]))
    print("R u S:         ", sorted(union(R, S)[0]))
    print("R n S:         ", sorted(intersection(R, S)[0]))
    print("R - S:         ", sorted(difference(R, S)[0]))
    print("gamma sum:     ", sorted(group_by(R, 1, 2)[0]))
    M = [[1, 2, 0], [0, 1, 3], [4, 0, 1]]
    N = [[1, 0, 2], [0, 3, 0], [1, 1, 1]]
    p1, st = matmul_one_round(M, N)
    p2, (s1, s2) = matmul_two_rounds(M, N)
    print(f"MN one round  : {dict(sorted(p1.items()))}")
    print(f"   nonzeros in={st.input_records} map out={st.map_output} r={st.replication_rate:.1f} "
          f"q={st.max_reducer_size}")
    print(f"MN two rounds : same={p1 == p2}; communication {s1.shuffled} + {s2.shuffled} "
          f"(after combiner)")


if __name__ == "__main__":
    demo()
