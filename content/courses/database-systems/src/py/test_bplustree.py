import bisect
import random

import pytest

from bplustree import BPlusTree, max_height


@pytest.mark.parametrize("n", [3, 4, 5, 6, 10])
@pytest.mark.parametrize("seed", range(5))
def test_random_inserts_keep_invariants(n, seed):
    rng = random.Random(seed)
    t, ref = BPlusTree(n), {}
    for _ in range(600):
        k = rng.randrange(2000)
        t.insert(k, -k)
        ref[k] = -k
        if rng.random() < 0.05:
            assert t.check() == len(ref)
    assert t.check() == len(ref)
    keys = sorted(ref)
    for k in rng.sample(range(2000), 200):
        assert t.search(k) == ref.get(k)
        assert t.accesses == t.height()                  # one node per level
    for _ in range(50):
        lo, hi = sorted(rng.sample(range(2000), 2))
        want = keys[bisect.bisect_left(keys, lo):bisect.bisect_right(keys, hi)]
        assert [k for k, _ in t.range(lo, hi)] == want
    assert t.height() <= max_height(len(ref), n)


def test_height_bound_sequential():
    for n in (3, 4, 8, 50):
        t = BPlusTree(n)
        for k in range(3000):
            t.insert(k)
        t.check()
        assert t.height() <= max_height(3000, n)


def test_demo_tree_shape():
    t = BPlusTree(4)
    for k in [10, 20, 5, 6, 12, 30, 7, 17, 3, 25, 27, 8]:
        t.insert(k)
    t.check()
    # traced by hand in note 08: four leaf splits, then the root [6 10 20 27] overflows
    assert t.dump().splitlines() == ["[20]", "[6 10]  [27]",
                                     "[3 5]  [6 7 8]  [10 12 17]  [20 25]  [27 30]"]
    assert t.splits == 5 and t.height() == 3


def test_first_split_n4():
    """n = 4: a leaf holds 3 keys; the 4th insert splits 2 | 2 and copies the right min up."""
    t = BPlusTree(4)
    for k in (1, 2, 3):
        t.insert(k)
    assert t.height() == 1
    t.insert(4)
    assert t.dump().splitlines() == ["[3]", "[1 2]  [3 4]"]


def test_duplicate_insert_overwrites():
    t = BPlusTree(3)
    t.insert(5, "a")
    t.insert(5, "b")
    assert t.search(5) == "b" and t.check() == 1


def test_range_counts_leaf_hops():
    t = BPlusTree(4)
    for k in range(1, 101):
        t.insert(k)
    t.range(1, 100)
    leaves = sum(1 for _ in t.leaves())
    assert t.accesses == t.height() + leaves - 1        # descend once, then follow the chain
