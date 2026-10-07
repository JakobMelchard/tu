"""Divide and conquer (KT ch. 5): merge sort, inversion counting, closest pair,
Strassen matrix multiplication, and the master theorem.

Belongs to the algorithmics note on divide and conquer / recurrences (A04).

Implements: merge_sort, count_inversions, closest_pair, matmul_naive, strassen,
master_theorem.
"""
import math


def merge_sort(a):
    """T(n) = 2T(n/2) + O(n) => O(n log n). Returns a new sorted list."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    return _merge(merge_sort(a[:mid]), merge_sort(a[mid:]))


def _merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def count_inversions(a):
    """Number of pairs i<j with a[i]>a[j], by merge-and-count (KT 5.3).

    When an element of the right half is emitted, every remaining element of
    the left half is larger and precedes it: add len(left) - i.
    Returns (count, sorted_list).
    """
    if len(a) <= 1:
        return 0, list(a)
    mid = len(a) // 2
    cl, left = count_inversions(a[:mid])
    cr, right = count_inversions(a[mid:])
    out = []
    i = j = 0
    cross = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
            cross += len(left) - i
    out.extend(left[i:])
    out.extend(right[j:])
    return cl + cr + cross, out


def closest_pair(points):
    """Closest pair of 2D points in O(n log n) (KT 5.4).

    Split by x-median; recurse; then only points within delta of the split line
    matter, and in y-sorted order each needs comparing to <= 7 successors
    (packing argument: a delta x 2delta strip box holds <= 8 points).
    Points must be distinct. Returns (distance, (p, q)).
    """
    px = sorted(points)
    py = sorted(points, key=lambda p: (p[1], p[0]))
    return _closest(px, py)


def _dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def _closest(px, py):
    n = len(px)
    if n <= 3:
        best = (math.inf, None)
        for i in range(n):
            for j in range(i + 1, n):
                d = _dist(px[i], px[j])
                if d < best[0]:
                    best = (d, (px[i], px[j]))
        return best
    mid = n // 2
    xline = px[mid][0]
    left_set = set(px[:mid])
    ly = [p for p in py if p in left_set]
    ry = [p for p in py if p not in left_set]
    dl = _closest(px[:mid], ly)
    dr = _closest(px[mid:], ry)
    best = min(dl, dr, key=lambda t: t[0])
    delta = best[0]
    strip = [p for p in py if abs(p[0] - xline) < delta]
    for i, p in enumerate(strip):
        for q in strip[i + 1 : i + 8]:  # at most 7 successors
            if q[1] - p[1] >= delta:
                break
            d = _dist(p, q)
            if d < best[0]:
                best = (d, (p, q))
    return best


def matmul_naive(A, B):
    """Cubic triple loop on lists of lists."""
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]


def _add(A, B, sign=1):
    return [[a + sign * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def strassen(A, B, cutoff=2):
    """Strassen's algorithm for n x n with n a power of two (KT 5.5).

    Seven half-size products instead of eight: T(n) = 7T(n/2) + O(n^2),
    so O(n^{log2 7}) = O(n^2.81). Falls back to naive below the cutoff.
    """
    n = len(A)
    assert n == len(B) and n & (n - 1) == 0, "need power-of-two size"
    if n <= cutoff:
        return matmul_naive(A, B)
    h = n // 2
    a11 = [r[:h] for r in A[:h]]; a12 = [r[h:] for r in A[:h]]
    a21 = [r[:h] for r in A[h:]]; a22 = [r[h:] for r in A[h:]]
    b11 = [r[:h] for r in B[:h]]; b12 = [r[h:] for r in B[:h]]
    b21 = [r[:h] for r in B[h:]]; b22 = [r[h:] for r in B[h:]]
    m1 = strassen(_add(a11, a22), _add(b11, b22), cutoff)
    m2 = strassen(_add(a21, a22), b11, cutoff)
    m3 = strassen(a11, _add(b12, b22, -1), cutoff)
    m4 = strassen(a22, _add(b21, b11, -1), cutoff)
    m5 = strassen(_add(a11, a12), b22, cutoff)
    m6 = strassen(_add(a21, a11, -1), _add(b11, b12), cutoff)
    m7 = strassen(_add(a12, a22, -1), _add(b21, b22), cutoff)
    c11 = _add(_add(_add(m1, m4), m5, -1), m7)
    c12 = _add(m3, m5)
    c21 = _add(m2, m4)
    c22 = _add(_add(_add(m1, m3), m2, -1), m6)
    return [r1 + r2 for r1, r2 in zip(c11, c12)] + [r1 + r2 for r1, r2 in zip(c21, c22)]


def master_theorem(a, b, k):
    """Solve T(n) = a T(n/b) + Theta(n^k). Returns (case, bound string).

    Compare k with log_b a: k < log_b a -> leaves dominate (case 1);
    k = log_b a -> every level equal (case 2, extra log); k > log_b a -> root
    dominates (case 3).
    """
    c = math.log(a, b)
    if abs(k - c) < 1e-9:
        return 2, f"Theta(n^{k:g} log n)"
    if k < c:
        exp = f"{c:g}" if abs(c - round(c)) < 1e-9 else f"log_{b}({a})"
        return 1, f"Theta(n^{exp})"
    return 3, f"Theta(n^{k:g})"


if __name__ == "__main__":
    import random
    rng = random.Random(0)
    a = [rng.randint(0, 99) for _ in range(12)]
    print("input:", a)
    print("merge_sort:", merge_sort(a))
    print("inversions:", count_inversions(a)[0])
    pts = [(rng.random(), rng.random()) for _ in range(200)]
    d, (p, q) = closest_pair(pts)
    print(f"closest pair distance {d:.4f} between {p} and {q}")
    A = [[rng.randint(-3, 3) for _ in range(4)] for _ in range(4)]
    B = [[rng.randint(-3, 3) for _ in range(4)] for _ in range(4)]
    print("strassen == naive:", strassen(A, B) == matmul_naive(A, B))
    for a_, b_, k_ in [(2, 2, 1), (8, 2, 2), (7, 2, 2), (1, 2, 0), (4, 2, 3)]:
        print(f"T(n) = {a_} T(n/{b_}) + n^{k_}:", master_theorem(a_, b_, k_))
