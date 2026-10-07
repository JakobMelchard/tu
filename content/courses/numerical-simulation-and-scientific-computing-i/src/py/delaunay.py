"""Bowyer-Watson Delaunay triangulation (topic 09).

Note 09 defines the Delaunay property and describes the incremental
construction; this is that construction, so the property can be tested instead
of asserted. Following Shewchuk [S32] for the definitions and the quality
measures.

The algorithm, one point at a time:

1. start from a super-triangle that contains every input point;
2. insert p: find every triangle whose **circumcircle** contains p (the "bad"
   triangles), delete them, which leaves a star-shaped cavity;
3. retriangulate the cavity by joining p to each boundary edge of the cavity;
4. at the end, drop every triangle touching a super-triangle vertex.

Expected O(n log n) with a good insertion order, O(n^2) worst case; this
implementation scans all triangles per insertion, so it is O(n^2) and is meant
for reading and for meshes of a few thousand points.

The InCircle and orientation predicates are evaluated in floating point with a
relative tolerance, so exactly cocircular input (a square grid) is resolved
arbitrarily rather than robustly -- the pitfall note 09 lists. Production codes
use Shewchuk's exact adaptive predicates instead [S32].

Run `python3 delaunay.py` for the demo. Tests: test_delaunay.py.
"""
import numpy as np


def circumcircle(a, b, c):
    """(centre, radius^2) of the circle through three non-collinear points."""
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if d == 0.0:
        raise ValueError("degenerate triangle")
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return (ux, uy), (ax - ux) ** 2 + (ay - uy) ** 2


def in_circumcircle(p, a, b, c, eps=1e-12):
    """Is p strictly inside the circumcircle of (a, b, c)?

    Equivalent to the sign of the InCircle determinant, but computed from the
    explicit circumcentre so the tolerance is a relative one on the radius.
    """
    (ux, uy), r2 = circumcircle(a, b, c)
    return (p[0] - ux) ** 2 + (p[1] - uy) ** 2 < r2 * (1.0 - eps)


def signed_area2(a, b, c):
    """Twice the signed area; > 0 iff (a, b, c) is counter-clockwise."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def triangulate(points):
    """Delaunay triangulation of a 2D point set.

    points: (n, 2) array. Returns an (m, 3) int array of vertex indices, every
    triangle counter-clockwise. Duplicate points are rejected.
    """
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError("points must be (n, 2)")
    n = len(pts)
    if n < 3:
        raise ValueError("need at least 3 points")
    if len(np.unique(pts, axis=0)) != n:
        raise ValueError("duplicate points")

    # Super-triangle, large enough that no input point is inside its circumcircle.
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    c, d = (lo + hi) / 2, np.max(hi - lo)
    d = max(d, 1.0) * 100.0
    sup = np.array([[c[0] - d, c[1] - d], [c[0] + d, c[1] - d], [c[0], c[1] + d]])
    work = np.vstack([pts, sup])
    tris = [(n, n + 1, n + 2)]

    for i in range(n):
        p = work[i]
        bad = [t for t in tris if in_circumcircle(p, work[t[0]], work[t[1]], work[t[2]])]
        # Boundary of the cavity: edges belonging to exactly one bad triangle.
        count = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                key = (min(e), max(e))
                count[key] = count.get(key, 0) + 1
        hull = [e for e, k in count.items() if k == 1]
        badset = set(bad)
        tris = [t for t in tris if t not in badset]
        for (u, v) in hull:
            t = (u, v, i) if signed_area2(work[u], work[v], p) > 0 else (v, u, i)
            tris.append(t)

    return np.array([t for t in tris if max(t) < n], dtype=int) if tris else np.empty((0, 3), int)


def is_delaunay(points, tris, eps=1e-9):
    """True iff no vertex lies strictly inside any triangle's circumcircle."""
    pts = np.asarray(points, float)
    for t in tris:
        a, b, c = pts[t[0]], pts[t[1]], pts[t[2]]
        (ux, uy), r2 = circumcircle(a, b, c)
        for k, p in enumerate(pts):
            if k in t:
                continue
            if (p[0] - ux) ** 2 + (p[1] - uy) ** 2 < r2 * (1.0 - eps):
                return False
    return True


def min_angle_degrees(points, tris):
    """The smallest angle in the mesh, the quality measure Delaunay maximises [S32]."""
    pts = np.asarray(points, float)
    best = 180.0
    for t in tris:
        p = pts[list(t)]
        for k in range(3):
            u = p[(k + 1) % 3] - p[k]
            v = p[(k + 2) % 3] - p[k]
            cosa = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
            best = min(best, np.degrees(np.arccos(np.clip(cosa, -1, 1))))
    return best


def _main():
    from scipy.spatial import ConvexHull

    rng = np.random.default_rng(7)
    print("Euler: a triangulation of n points with h of them on the convex hull")
    print("has exactly 2n - 2 - h triangles.")
    for n in (8, 50, 200):
        pts = rng.random((n, 2))
        tris = triangulate(pts)
        h = len(ConvexHull(pts).vertices)
        print(f"n = {n:>4}  triangles = {len(tris):>4}  2n-2-h = {2 * n - 2 - h:>4}  "
              f"Delaunay = {is_delaunay(pts, tris)}  min angle = {min_angle_degrees(pts, tris):5.1f} deg")

    print("\nA square grid is the cocircular case note 09 warns about:")
    g = np.array([[i, j] for i in range(4) for j in range(4)], float)
    t = triangulate(g)
    print(f"  4x4 grid -> {len(t)} triangles, Delaunay = {is_delaunay(g, t)}, "
          f"min angle = {min_angle_degrees(g, t):.1f} deg (the diagonal choice is arbitrary)")


if __name__ == "__main__":
    _main()
