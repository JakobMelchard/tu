"""Bowyer-Watson, checked against the defining property and against scipy.

The Delaunay property and the max-min-angle optimality are Shewchuk's
definitions [S32]; `scipy.spatial.Delaunay` (Qhull) is the independent
implementation the results are compared with.
"""
import numpy as np
import pytest
from scipy.spatial import ConvexHull
from scipy.spatial import Delaunay as ScipyDelaunay

from delaunay import circumcircle, is_delaunay, min_angle_degrees, signed_area2, triangulate


def _sorted_triangles(tris):
    return sorted(tuple(sorted(t)) for t in np.asarray(tris))


def test_circumcircle_of_the_unit_right_triangle():
    (cx, cy), r2 = circumcircle((0, 0), (1, 0), (0, 1))
    assert abs(cx - 0.5) < 1e-15 and abs(cy - 0.5) < 1e-15
    assert abs(r2 - 0.5) < 1e-15                     # radius = sqrt(2)/2


def test_four_points_pick_the_shorter_diagonal():
    """The textbook two-triangle case: a thin quadrilateral has one Delaunay
    triangulation and it is not the one with the long diagonal."""
    pts = np.array([[0, 0], [4, 0], [5, 1], [1, 1]], float)
    tris = triangulate(pts)
    assert len(tris) == 2
    assert is_delaunay(pts, tris)
    assert _sorted_triangles(tris) == _sorted_triangles(ScipyDelaunay(pts).simplices)


@pytest.mark.parametrize("n, seed", [(12, 0), (60, 1), (150, 2)])
def test_random_point_sets_are_delaunay_and_match_scipy(n, seed):
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2))
    tris = triangulate(pts)
    assert is_delaunay(pts, tris)
    assert _sorted_triangles(tris) == _sorted_triangles(ScipyDelaunay(pts).simplices)


@pytest.mark.parametrize("n, seed", [(12, 0), (60, 1), (150, 2)])
def test_euler_triangle_count(n, seed):
    """A triangulation of n points with h on the convex hull has 2n - 2 - h
    triangles -- an exact identity, so it catches a lost or duplicated cell."""
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2))
    h = len(ConvexHull(pts).vertices)
    assert len(triangulate(pts)) == 2 * n - 2 - h


def test_every_triangle_is_counter_clockwise():
    """The orientation convention note 09 states for 2D meshes."""
    rng = np.random.default_rng(5)
    pts = rng.random((40, 2))
    for t in triangulate(pts):
        assert signed_area2(pts[t[0]], pts[t[1]], pts[t[2]]) > 0


def test_delaunay_maximises_the_minimum_angle():
    """[S32]: among all triangulations of a point set, Delaunay maximises the
    smallest angle. Checked against every alternative on a 5-point set by
    flipping the one interior edge."""
    pts = np.array([[0, 0], [1, 0], [1.6, 0.9], [0.5, 1.4], [-0.4, 0.7]], float)
    d = triangulate(pts)
    assert is_delaunay(pts, d)
    best = min_angle_degrees(pts, d)
    # the other fan triangulations of this convex polygon
    for apex in range(5):
        fan = [(apex, (apex + k) % 5, (apex + k + 1) % 5) for k in range(1, 4)]
        fan = [t for t in fan if abs(signed_area2(*pts[list(t)])) > 1e-12]
        fan = [t if signed_area2(*pts[list(t)]) > 0 else (t[0], t[2], t[1]) for t in fan]
        assert min_angle_degrees(pts, fan) <= best + 1e-9


def test_cocircular_grid_is_still_a_valid_triangulation():
    """The pitfall in note 09: on a square grid four points are cocircular, so
    the triangulation is not unique. It must still be a valid, Delaunay,
    complete triangulation -- only the diagonal choice is arbitrary."""
    g = np.array([[i, j] for i in range(5) for j in range(5)], float)
    tris = triangulate(g)
    assert is_delaunay(g, tris)
    # h counts points ON the hull boundary, not just the corners: a 5x5 grid has
    # 16, not the 4 that ConvexHull.vertices reports for a square.
    h = 16
    assert len(tris) == 2 * len(g) - 2 - h == 32
    assert abs(sum(signed_area2(*g[list(t)]) for t in tris) / 2 - 16.0) < 1e-9  # total area


def test_bad_input_is_rejected():
    with pytest.raises(ValueError):
        triangulate(np.array([[0.0, 0.0], [1.0, 1.0]]))
    with pytest.raises(ValueError):
        triangulate(np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 0.0], [0.0, 1.0]]))
