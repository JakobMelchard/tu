"""Join algorithms on the same inputs, with comparison and page-I/O counts (note 09).

Relations are lists of tuples; `key` is the column index of the equi-join
attribute.  Every algorithm returns the list of concatenated tuples (as a bag)
and a Counter of what it did, so the note can compare them:

  nested_loop          |r| * |s| comparisons, any predicate
  block_nested_loop    pages read = b_r + ceil(b_r / (M-2)) * b_s  (simulated)
  index_nested_loop    one index probe per outer tuple (dict = hash index)
  sort_merge           sort both, merge; duplicate groups joined pairwise
  hash_join            partition both on h1 into k buckets, build on the smaller
                       side's bucket with a dict, probe with the other (Grace)

Page-I/O formulas of [S6] ch. 15 (block transfers only, output not counted):
  cost_nlj(nr, br, bs)       = nr * bs + br          (worst case, 1 buffer each)
  cost_bnlj(br, bs, M)       = ceil(br/(M-2)) * bs + br
  cost_merge(br, bs)         = br + bs               (inputs already sorted)
  cost_hash(br, bs)          = 3 (br + bs)           (no recursive partitioning,
                                                      partial blocks ignored)
"""
import math
from collections import Counter, defaultdict


def paginate(rel, cap):
    return [rel[i:i + cap] for i in range(0, len(rel), cap)]


def nested_loop(r, s, kr, ks, pred=None):
    c, out = Counter(), []
    pred = pred or (lambda x, y: x[kr] == y[ks])
    for x in r:
        for y in s:
            c["comparisons"] += 1
            if pred(x, y):
                out.append(x + y)
    return out, c


def block_nested_loop(r, s, kr, ks, cap, M):
    """Outer chunk of M-2 pages in memory, one input page for s, one output page."""
    c, out = Counter(), []
    rp, sp = paginate(r, cap), paginate(s, cap)
    for i in range(0, len(rp), M - 2):
        chunk = rp[i:i + M - 2]
        c["pages_read"] += len(chunk)
        for page in sp:
            c["pages_read"] += 1
            for x in (t for p in chunk for t in p):
                for y in page:
                    c["comparisons"] += 1
                    if x[kr] == y[ks]:
                        out.append(x + y)
    return out, c


def index_nested_loop(r, s, kr, ks):
    c, out, index = Counter(), [], defaultdict(list)
    for y in s:
        index[y[ks]].append(y)
    for x in r:
        c["probes"] += 1
        for y in index.get(x[kr], ()):
            out.append(x + y)
    return out, c


def sort_merge(r, s, kr, ks):
    c = Counter()
    r = sorted(r, key=lambda t: t[kr])
    s = sorted(s, key=lambda t: t[ks])
    out, i, j = [], 0, 0
    while i < len(r) and j < len(s):
        c["comparisons"] += 1
        a, b = r[i][kr], s[j][ks]
        if a < b:
            i += 1
        elif a > b:
            j += 1
        else:                                       # equal: join the two duplicate groups
            i2 = i
            while i2 < len(r) and r[i2][kr] == a:
                i2 += 1
            j2 = j
            while j2 < len(s) and s[j2][ks] == a:
                j2 += 1
            out.extend(x + y for x in r[i:i2] for y in s[j:j2])
            i, j = i2, j2
    return out, c


def hash_join(r, s, kr, ks, k=4, h1=hash):
    c = Counter()
    rp, sp = defaultdict(list), defaultdict(list)
    for x in r:
        rp[h1(x[kr]) % k].append(x)
    for y in s:
        sp[h1(y[ks]) % k].append(y)
    out = []
    for i in range(k):
        build = defaultdict(list)
        for y in sp[i]:                              # build side: s (choose the smaller)
            build[y[ks]].append(y)
        c["build_tuples"] += len(sp[i])
        for x in rp[i]:
            c["probes"] += 1
            out.extend(x + y for y in build.get(x[kr], ()))
    return out, c


def cost_nlj(nr, br, bs):
    return nr * bs + br


def cost_bnlj(br, bs, M):
    return math.ceil(br / (M - 2)) * bs + br


def cost_merge(br, bs):
    return br + bs


def cost_hash(br, bs):
    return 3 * (br + bs)


def sample(n_r=60, n_s=90, keys=20, seed=0):
    import random
    rng = random.Random(seed)
    r = [(i, rng.randrange(keys)) for i in range(n_r)]
    s = [(rng.randrange(keys), f"s{j}") for j in range(n_s)]
    return r, s


if __name__ == "__main__":
    r, s = sample()
    results = {
        "nested loop": nested_loop(r, s, 1, 0),
        "block NL (cap 10, M 4)": block_nested_loop(r, s, 1, 0, cap=10, M=4),
        "index NL": index_nested_loop(r, s, 1, 0),
        "sort-merge": sort_merge(r, s, 1, 0),
        "hash (k = 4)": hash_join(r, s, 1, 0),
    }
    ref = sorted(results["nested loop"][0])
    for name, (out, cnt) in results.items():
        print(f"{name:24} {len(out):4} rows  same={sorted(out) == ref}  {dict(cnt)}")
    print("block NL formula:", cost_bnlj(6, 9, 4), "pages (b_r = 6, b_s = 9, M = 4)")
    print("[S6] ch. 15 student (n 5000, b 100) join takes (n 10000, b 400):")
    print("  NLJ student outer:", cost_nlj(5000, 100, 400), " takes outer:", cost_nlj(10000, 400, 100))
    print("  BNLJ M = 3 student outer:", cost_bnlj(100, 400, 3), " merge (sorted):", cost_merge(100, 400),
          " hash:", cost_hash(100, 400))
