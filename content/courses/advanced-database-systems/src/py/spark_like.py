"""An RDD-like lazy dataset with lineage, narrow vs wide dependencies,
partition-aware joins, caching and recomputation. Note 06; [S19], [S20].

NOT Spark. Real Spark is not installed in the repo venv (no pyspark; a stray
`spark-submit` wrapper exists on this machine but there is no Java runtime),
so this module imitates the *semantics* the exam asks about:
  - transformations are lazy: they only record lineage (parents + function);
  - actions (collect, count, reduce, take) run a job;
  - narrow dependency: each parent partition feeds at most one child partition
    (map, filter, flatMap, mapValues, union, join of co-partitioned inputs);
  - wide dependency: a child partition needs many parent partitions -> shuffle,
    stage boundary (groupByKey, reduceByKey, distinct, partitionBy, join of
    differently partitioned inputs) [S19 section 4];
  - a lost partition is recomputed from its lineage, not restored from a replica.

Run: python spark_like.py
"""
from __future__ import annotations

from collections import defaultdict
from functools import reduce as _reduce

from mapreduce import stable_hash


class HashPartitioner:
    def __init__(self, n: int):
        self.n = n

    def __call__(self, key) -> int:
        return stable_hash(key) % self.n

    def __eq__(self, other) -> bool:
        return isinstance(other, HashPartitioner) and other.n == self.n


class Context:
    def __init__(self, parallelism: int = 2):
        self.parallelism = parallelism
        self.computed = 0          # partition computations (lineage steps executed)
        self.shuffled = 0          # records written to shuffle files
        self.jobs = 0

    def parallelize(self, data, n: int | None = None) -> "RDD":
        n = n or self.parallelism
        data = list(data)
        size = -(-len(data) // n) if data else 1
        chunks = [data[i * size:(i + 1) * size] for i in range(n)]
        return RDD(self, [], n, lambda i: list(chunks[i]), "parallelize")


class RDD:
    def __init__(self, ctx, parents, n, compute, name, partitioner=None):
        self.ctx, self.parents, self.n = ctx, parents, n       # parents: [(rdd, 'narrow'|'wide')]
        self._compute, self.name, self.partitioner = compute, name, partitioner
        self._cache: dict[int, list] | None = None

    # -- evaluation ------------------------------------------------------
    def partition(self, i: int) -> list:
        if self._cache is not None and i in self._cache:
            return self._cache[i]
        self.ctx.computed += 1
        data = self._compute(i)
        if self._cache is not None:
            self._cache[i] = data
        return data

    def cache(self) -> "RDD":
        self._cache = {}
        return self

    def lose_partition(self, i: int) -> None:
        """Simulate an executor failure that loses one cached partition."""
        if self._cache is not None:
            self._cache.pop(i, None)

    # -- narrow transformations -----------------------------------------
    def _narrow(self, f, name, keep_partitioner=False):
        return RDD(self.ctx, [(self, "narrow")], self.n, lambda i: f(self.partition(i)),
                   name, self.partitioner if keep_partitioner else None)

    def map(self, f):
        return self._narrow(lambda p: [f(x) for x in p], "map")

    def flatMap(self, f):
        return self._narrow(lambda p: [y for x in p for y in f(x)], "flatMap")

    def filter(self, f):
        return self._narrow(lambda p: [x for x in p if f(x)], "filter", True)

    def mapValues(self, f):          # keys untouched -> partitioner survives
        return self._narrow(lambda p: [(k, f(v)) for k, v in p], "mapValues", True)

    def union(self, other):
        n = self.n
        return RDD(self.ctx, [(self, "narrow"), (other, "narrow")], n + other.n,
                   lambda i: self.partition(i) if i < n else other.partition(i - n), "union")

    # -- wide transformations -------------------------------------------
    def _shuffle(self, part: HashPartitioner, name: str, combine=None):
        """Map side: bucket every parent partition (optionally pre-combined per
        key) into shuffle files, once; reduce side: read bucket i."""
        files: list | None = None

        def compute(i):
            nonlocal files
            if files is None:
                files = [[] for _ in range(part.n)]
                for j in range(self.n):
                    recs = self.partition(j)
                    if combine is not None:
                        acc = {}
                        for k, v in recs:
                            acc[k] = combine(acc[k], v) if k in acc else v
                        recs = list(acc.items())
                    for k, v in recs:
                        files[part(k)].append((k, v))
                        self.ctx.shuffled += 1
            return files[i]
        return RDD(self.ctx, [(self, "wide")], part.n, compute, f"shuffle<{name}>", part)

    def partitionBy(self, n: int):
        return self._shuffle(HashPartitioner(n), "partitionBy")

    def groupByKey(self, n: int | None = None):
        sh = self._shuffle(HashPartitioner(n or self.n), "groupByKey")
        return sh._narrow(_group, "groupByKey", True)

    def reduceByKey(self, f, n: int | None = None):
        """Like groupByKey + reduce, but combines on the map side first."""
        sh = self._shuffle(HashPartitioner(n or self.n), "reduceByKey", combine=f)
        return sh._narrow(lambda p: [(k, _reduce(f, vs)) for k, vs in _group(p)],
                          "reduceByKey", True)

    def distinct(self):
        return self.map(lambda x: (x, None)).reduceByKey(lambda a, b: a).map(lambda kv: kv[0])

    def join(self, other, n: int | None = None):
        """Inner join on keys. If both sides already share a partitioner, partition
        i of the result needs only partition i of each side: a narrow join."""
        if self.partitioner is not None and self.partitioner == other.partitioner:
            left, right, name = self, other, "join(co-partitioned)"
        else:
            part = self.partitioner or other.partitioner or HashPartitioner(n or self.n)
            left = self if self.partitioner == part else self._shuffle(part, "shuffle")
            right = other if other.partitioner == part else other._shuffle(part, "shuffle")
            name = "join"

        def compute(i):
            table = defaultdict(list)
            for k, w in right.partition(i):
                table[k].append(w)
            return [(k, (v, w)) for k, v in left.partition(i) for w in table.get(k, [])]
        return RDD(self.ctx, [(left, "narrow"), (right, "narrow")], left.n, compute,
                   name, left.partitioner)

    # -- actions ---------------------------------------------------------
    def collect(self) -> list:
        self.ctx.jobs += 1
        return [x for i in range(self.n) for x in self.partition(i)]

    def count(self) -> int:
        return len(self.collect())

    def reduce(self, f):
        return _reduce(f, self.collect())

    def take(self, k: int) -> list:
        self.ctx.jobs += 1
        out = []
        for i in range(self.n):                      # stops early, like Spark
            out += self.partition(i)
            if len(out) >= k:
                break
        return out[:k]

    # -- introspection ---------------------------------------------------
    def lineage(self, depth: int = 0) -> str:
        pad = "  " * depth
        lines = [f"{pad}{self.name} [{self.n} partitions]{' cached' if self._cache is not None else ''}"]
        for p, dep in self.parents:
            lines.append(f"{pad}  +- {dep}")
            lines.append(p.lineage(depth + 2))
        return "\n".join(lines)

    def num_stages(self) -> int:
        """1 + number of shuffle boundaries on the longest path to a source."""
        return 1 + max((p.num_stages() - 1 + (dep == "wide") for p, dep in self.parents),
                       default=0)


def _group(p):
    g = defaultdict(list)
    for k, v in p:
        g[k].append(v)
    return list(g.items())


def pagerank(ctx: Context, links: dict, iters: int = 20, n: int = 2) -> dict:
    """The iterative example of [S19 3.2.2]: `links` is partitioned once and
    cached; each iteration joins it with `ranks` without reshuffling links.
    [S19] writes r <- a/N + (1-a) sum(c); this is the same update scaled by N
    (ranks start at 1.0, r <- 0.15 + 0.85 sum(c))."""
    L = ctx.parallelize(list(links.items()), n).partitionBy(n).cache()
    ranks = L.mapValues(lambda _: 1.0)
    for _ in range(iters):
        contribs = L.join(ranks).flatMap(
            lambda kv: [(d, kv[1][1] / len(kv[1][0])) for d in kv[1][0]])
        ranks = contribs.reduceByKey(lambda a, b: a + b, n).mapValues(lambda s: 0.15 + 0.85 * s)
        ranks = ctx.parallelize(ranks.collect(), 1).partitionBy(n)  # materialise the iterate
    return dict(ranks.collect())


def demo() -> None:
    ctx = Context()
    lines = ctx.parallelize(["to be or not", "to be", "that is the question"], 2)
    words = lines.flatMap(str.split).map(lambda w: (w, 1))
    counts = words.reduceByKey(lambda a, b: a + b)
    print(f"after 3 transformations: {ctx.computed} partitions computed (lazy)")
    print(counts.lineage())
    print("stages:", counts.num_stages(), "| result:", sorted(counts.collect()))
    print(f"reduceByKey shuffled {ctx.shuffled} records;", end=" ")
    ctx.shuffled = 0
    words.groupByKey().mapValues(sum).collect()
    print(f"groupByKey shuffled {ctx.shuffled}")
    a = ctx.parallelize([(i, i * i) for i in range(8)]).partitionBy(2).cache()
    b = ctx.parallelize([(i, -i) for i in range(8)]).partitionBy(2).cache()
    a.count(), b.count()
    ctx.shuffled = 0
    j = a.join(b)
    print(f"join of co-partitioned RDDs: {j.name}, extra shuffle {len(j.collect()) and ctx.shuffled}")
    a.lose_partition(0)
    before = ctx.computed
    j.collect()
    print(f"partition 0 of `a` lost -> recomputed via lineage ({ctx.computed - before} steps)")
    pr = pagerank(Context(), {"a": ["b", "c"], "b": ["c"], "c": ["a"]})
    print("pagerank:", {k: round(v, 4) for k, v in sorted(pr.items())})


if __name__ == "__main__":
    demo()
