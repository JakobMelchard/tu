import random
from itertools import combinations

import pytest

import nosql as ns

KEYS = [f"k{i}" for i in range(3000)]


def test_ring_moves_few_keys_on_join():
    before = ns.ConsistentHashRing("ABCD", vnodes=64)
    after = ns.ConsistentHashRing("ABCDE", vnodes=64)
    moved = ns.moved_fraction(KEYS, before.owner, after.owner)
    assert 0.1 < moved < 0.3                                  # ~1/5
    assert all(after.owner(k) == "E" for k in KEYS if before.owner(k) != after.owner(k))
    mod = ns.moved_fraction(KEYS, lambda k: ns.h32(k) % 4, lambda k: ns.h32(k) % 5)
    assert mod > 0.7                                          # ~4/5


def test_ring_remove_only_moves_that_nodes_keys():
    ring = ns.ConsistentHashRing("ABCDE", vnodes=32)
    owners = {k: ring.owner(k) for k in KEYS}
    ring.remove("C")
    assert all(ring.owner(k) == o for k, o in owners.items() if o != "C")


def test_preference_list_distinct_physical_nodes():
    ring = ns.ConsistentHashRing("ABCDE", vnodes=16)
    for k in KEYS[:200]:
        pl = ring.preference_list(k, 3)
        assert len(set(pl)) == 3 and pl[0] == ring.owner(k)


@pytest.mark.parametrize("N", [1, 2, 3, 4, 5])
def test_quorum_intersection_iff_r_plus_w_gt_n(N):
    for R in range(1, N + 1):
        for W in range(1, N + 1):
            assert ns.quorums_always_intersect(N, R, W) == (R + W > N)


def test_strict_quorum_reads_latest_from_any_read_set():
    s = ns.QuorumStore("ABCDE", N=3, R=2, W=2)
    s.put("x", "old")
    s.put("x", "new")
    for read_set in combinations(s.replicas("x"), 2):
        assert s.get("x", read_from=list(read_set)) == "new"


def test_weak_quorum_can_read_stale_and_read_repair_fixes_it():
    s = ns.QuorumStore("ABCDE", N=3, R=1, W=1)
    reps = s.replicas("x")
    s.put("x", "v1")                        # lands on reps[0] only
    s.down = {reps[0]}
    s.put("x", "v2")                        # lands on reps[1] only
    s.down = set()
    assert s.get("x", read_from=[reps[0]]) == "v1"   # stale
    s2 = ns.QuorumStore("ABCDE", N=3, R=3, W=1)
    s2.put("y", "v1")
    s2.get("y", repair=True)
    assert all(s2.data[n]["y"][1] == "v1" for n in s2.replicas("y"))


def test_put_fails_without_w_live_replicas():
    s = ns.QuorumStore("ABCDE", N=3, R=2, W=2)
    s.down = set(s.replicas("z")[:2])
    with pytest.raises(RuntimeError):
        s.put("z", 1)


def test_dynamo_vector_clock_example():
    D = ns.dynamo_example()
    assert D["D1"].compare(D["D2"]) == "before"
    assert D["D3"].compare(D["D4"]) == "concurrent"
    assert D["D5"].compare(D["D3"]) == "after" and D["D5"].compare(D["D4"]) == "after"
    assert D["D5"].c == {"Sx": 3, "Sy": 1, "Sz": 1}


def test_lsm_behaves_like_a_dict():
    rng = random.Random(7)
    t, ref = ns.LSMTree(limit=5, max_runs=3), {}
    for _ in range(2000):
        k = f"k{rng.randrange(60)}"
        if rng.random() < 0.2:
            t.delete(k)
            ref.pop(k, None)
        else:
            v = rng.randrange(1000)
            t.put(k, v)
            ref[k] = v
        if rng.random() < 0.05:
            q = f"k{rng.randrange(60)}"
            assert t.get(q) == ref.get(q)
    assert t.items() == ref
    assert all(t.get(k) == ref.get(k) for k in (f"k{i}" for i in range(60)))


def test_compaction_drops_tombstones_and_shadowed_versions():
    t = ns.LSMTree(limit=2, max_runs=10)
    for k, v in [("a", 1), ("b", 1), ("a", 2), ("c", 1), ("b", 2), ("d", 1)]:
        t.put(k, v)
    t.delete("c")
    t.flush()
    assert len(t.runs) == 4
    t.compact()
    assert t.runs[0][0] == [("a", 2), ("b", 2), ("d", 1)]


def test_bloom_filter_has_no_false_negatives():
    keys = [f"x{i}" for i in range(50)]
    b = ns.Bloom(keys, m=256, k=3)
    assert all(k in b for k in keys)
    fp = sum(f"y{i}" in b for i in range(1000)) / 1000
    assert fp < 0.2                          # (1 - e^{-kn/m})^k ~ 0.09 here


def test_column_encodings_roundtrip():
    col = list("aaabbbbccaaa")
    assert [x for x, n in ns.rle(col) for _ in range(n)] == col
    values, codes = ns.dictionary_encode(col)
    assert [values[c] for c in codes] == col
    bm = ns.bitmap_encode(col)
    assert all(sum(int(bits[i]) for bits in bm.values()) == 1 for i in range(len(col)))
