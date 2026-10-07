import itertools
import math
import random

import numpy as np

from divide_conquer import (closest_pair, count_inversions, master_theorem,
                            matmul_naive, merge_sort, strassen)


def test_merge_sort_matches_sorted():
    rng = random.Random(0)
    for _ in range(50):
        a = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
        assert merge_sort(a) == sorted(a)


def test_count_inversions_vs_brute_force():
    rng = random.Random(1)
    for _ in range(50):
        a = [rng.randint(0, 20) for _ in range(rng.randint(0, 40))]
        brute = sum(1 for i, j in itertools.combinations(range(len(a)), 2) if a[i] > a[j])
        c, s = count_inversions(a)
        assert c == brute and s == sorted(a)


def test_closest_pair_vs_brute_force():
    rng = random.Random(2)
    for _ in range(30):
        n = rng.randint(2, 80)
        pts = [(rng.randint(0, 50), rng.randint(0, 50)) for _ in range(n)]
        pts = list(set(pts))
        if len(pts) < 2:
            continue
        brute = min(math.dist(p, q) for p, q in itertools.combinations(pts, 2))
        d, (p, q) = closest_pair(pts)
        assert math.isclose(d, brute)
        assert math.isclose(math.dist(p, q), d) and p != q


def test_strassen_matches_numpy():
    rng = np.random.default_rng(3)
    for n in (1, 2, 4, 8, 16):
        A = rng.integers(-5, 5, size=(n, n))
        B = rng.integers(-5, 5, size=(n, n))
        C = np.array(strassen(A.tolist(), B.tolist()))
        assert np.array_equal(C, A @ B)
        assert np.array_equal(np.array(matmul_naive(A.tolist(), B.tolist())), A @ B)


def test_master_theorem_textbook_cases():
    assert master_theorem(2, 2, 1) == (2, "Theta(n^1 log n)")     # merge sort
    assert master_theorem(8, 2, 2) == (1, "Theta(n^3)")           # naive matmul
    assert master_theorem(7, 2, 2)[0] == 1                        # Strassen
    assert "log_2(7)" in master_theorem(7, 2, 2)[1]
    assert master_theorem(1, 2, 0) == (2, "Theta(n^0 log n)")     # binary search
    assert master_theorem(4, 2, 3) == (3, "Theta(n^3)")
    assert master_theorem(4, 2, 1) == (1, "Theta(n^2)")
