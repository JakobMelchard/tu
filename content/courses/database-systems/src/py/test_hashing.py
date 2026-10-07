import random

import pytest

from hashing import BitmapIndex, ExtendibleHash


@pytest.mark.parametrize("cap", [2, 3, 8])
@pytest.mark.parametrize("seed", range(4))
def test_extendible_matches_dict(cap, seed):
    rng = random.Random(seed)
    e, ref = ExtendibleHash(cap, h=lambda k: hash((k, 7)) & 0xFFFFFFFF), {}
    for _ in range(500):
        k = rng.randrange(10_000)
        e.insert(k, k * 2)
        ref[k] = k * 2
    assert e.check() == len(ref)
    assert all(e.get(k) == v for k, v in ref.items())
    assert e.get(-1) is None


def test_demo_trace():
    """Hand trace in note 08 (cap 2, h(k) = k, low-order bits)."""
    e = ExtendibleHash(cap=2)
    for k in [1, 4, 5]:
        e.insert(k)
    assert e.global_depth == 1 and e.doublings == 1          # {4} | {1, 5}
    e.insert(7)
    assert e.global_depth == 2 and e.doublings == 2          # 7 = ..11 needs bit 1
    e.insert(10)
    e.insert(12)                                             # splits {4, 10} (d = 1 < G): no doubling
    assert e.global_depth == 2 and e.splits == 3
    e.insert(13)                                             # {1, 5} has d = G = 2: double
    assert (e.global_depth, e.doublings, e.splits) == (3, 3, 4)
    assert e.dump().splitlines() == [
        "000 -> d=2 [4, 12]", "001 -> d=3 [1]", "010 -> d=2 [10]", "011 -> d=2 [7]",
        "100 -> d=2 [4, 12]", "101 -> d=3 [5, 13]", "110 -> d=2 [10]", "111 -> d=2 [7]"]
    e.check()


def test_bitmap_against_scan():
    rng = random.Random(0)
    a = [rng.choice("xyz") for _ in range(200)]
    b = [rng.randrange(4) for _ in range(200)]
    A, B = BitmapIndex(a), BitmapIndex(b)
    q = (A.eq("x") | A.eq("y")) & A.neg(B.eq(0))
    want = [i for i in range(200) if a[i] in "xy" and b[i] != 0]
    assert BitmapIndex.rows(q) == want and BitmapIndex.count(q) == len(want)
    assert A.eq("nope") == 0
    assert A.size_bits() == 3 * 200
