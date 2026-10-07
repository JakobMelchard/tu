import networkx as nx

import mapreduce as mr
import spark_like as sp


def test_transformations_are_lazy_actions_run():
    ctx = sp.Context()
    rdd = ctx.parallelize(range(10)).map(lambda x: x * x).filter(lambda x: x % 2 == 0)
    assert ctx.computed == 0 and ctx.jobs == 0
    assert rdd.collect() == [0, 4, 16, 36, 64]
    assert ctx.jobs == 1 and ctx.computed == 3 * 2      # 3 RDDs x 2 partitions


def test_word_count_equals_mapreduce():
    ctx = sp.Context(3)
    counts = (ctx.parallelize(mr.TEXT).flatMap(mr.wc_map)
              .reduceByKey(lambda a, b: a + b))
    assert dict(counts.collect()) == mr.word_count(mr.TEXT)[0]


def test_reduce_by_key_combines_before_shuffle():
    pairs = [(w, 1) for w in "a a a b a b b a a c".split()]
    c1, c2 = sp.Context(2), sp.Context(2)
    r1 = dict(c1.parallelize(pairs).reduceByKey(lambda a, b: a + b).collect())
    r2 = {k: sum(v) for k, v in c2.parallelize(pairs).groupByKey().collect()}
    assert r1 == r2 == {"a": 6, "b": 3, "c": 1}
    assert c2.shuffled == len(pairs) and c1.shuffled == 5   # <= distinct keys per partition


def test_stages_split_at_wide_dependencies():
    ctx = sp.Context()
    base = ctx.parallelize([(i % 3, i) for i in range(9)])
    assert base.map(lambda kv: kv).filter(lambda kv: True).num_stages() == 1
    once = base.reduceByKey(max)
    twice = once.map(lambda kv: (kv[1] % 2, kv[0])).groupByKey()
    assert once.num_stages() == 2 and twice.num_stages() == 3
    assert "wide" in twice.lineage()


def test_join_narrow_when_co_partitioned():
    ctx = sp.Context()
    a = ctx.parallelize([(i, i) for i in range(10)]).partitionBy(2).cache()
    b = ctx.parallelize([(i, -i) for i in range(0, 10, 2)]).partitionBy(2).cache()
    a.count(), b.count()
    before = ctx.shuffled
    j = a.join(b)
    assert sorted(j.collect()) == [(i, (i, -i)) for i in range(0, 10, 2)]
    assert ctx.shuffled == before and j.name == "join(co-partitioned)"
    assert j.num_stages() == 2                          # only the partitionBy shuffles


def test_join_shuffles_otherwise():
    ctx = sp.Context()
    a = ctx.parallelize([(i, i) for i in range(6)])
    b = ctx.parallelize([(i, -i) for i in range(6)])
    j = a.join(b)
    assert len(j.collect()) == 6 and ctx.shuffled == 12


def test_cache_and_lineage_recovery():
    ctx = sp.Context()
    squares = ctx.parallelize(range(8)).map(lambda x: x * x).cache()
    assert squares.reduce(lambda a, b: a + b) == 140
    n = ctx.computed
    assert squares.count() == 8 and ctx.computed == n   # served from cache
    squares.lose_partition(1)
    assert squares.collect() == [x * x for x in range(8)]
    assert ctx.computed == n + 2                        # partition 1 of map + of parallelize


def test_union_distinct_take():
    ctx = sp.Context()
    u = ctx.parallelize([1, 2, 2]).union(ctx.parallelize([2, 3], 1))
    assert u.n == 3 and sorted(u.collect()) == [1, 2, 2, 2, 3]
    assert sorted(u.distinct().collect()) == [1, 2, 3]
    ctx2 = sp.Context(4)
    assert ctx2.parallelize(range(100), 4).take(3) == [0, 1, 2] and ctx2.computed == 1


def test_pagerank_matches_networkx():
    # every node has an in-link and an out-link; otherwise [S19]'s simplified
    # update (no teleport term for nodes nobody links to) differs from networkx
    links = {"a": ["b", "c"], "b": ["c", "d"], "c": ["a"], "d": ["a", "b"]}
    pr = sp.pagerank(sp.Context(), links, iters=80)
    G = nx.DiGraph([(s, d) for s, ds in links.items() for d in ds])
    ref = nx.pagerank(G, alpha=0.85, tol=1e-12)
    # ranks here are N times [S19]'s alpha/N + (1-alpha) sum, i.e. N x networkx
    assert set(pr) == set(ref)
    for node, v in pr.items():
        assert abs(v / len(links) - ref[node]) < 1e-6
