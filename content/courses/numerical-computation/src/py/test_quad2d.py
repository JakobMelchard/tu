"""Tests for quad2d.py, against [S4] sec. 2.6."""
import numpy as np
import pytest

from quad2d import (tensor_square, barycentre_triangle, vertex_triangle, duffy_triangle,
                    monomial_integral_square, monomial_integral_triangle,
                    exactness_degree_2d)


def test_monomial_integrals():
    assert monomial_integral_square(0, 0) == 1.0
    assert monomial_integral_square(2, 1) == pytest.approx(1 / 6)
    assert monomial_integral_triangle(0, 0) == pytest.approx(0.5)      # |T| = 1/2
    assert monomial_integral_triangle(1, 0) == pytest.approx(1 / 6)
    assert monomial_integral_triangle(0, 1) == pytest.approx(1 / 6)
    assert monomial_integral_triangle(1, 1) == pytest.approx(1 / 24)


# ------------------------------------------------------------------ square
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_tensor_gauss_is_exact_on_the_tensor_space(n):
    """[S4] Exercise 2.21: exact on span{x^i y^j : i, j <= 2n-1}."""
    p = 2 * n - 1
    rule = lambda f: tensor_square(f, n)
    for i in range(p + 1):
        for j in range(p + 1):
            got = rule(lambda x, y, i=i, j=j: x ** i * y ** j)
            assert got == pytest.approx(monomial_integral_square(i, j), abs=1e-12)
    # but not on x^{p+1}
    bad = rule(lambda x, y: x ** (p + 1))
    assert abs(bad - monomial_integral_square(p + 1, 0)) > 1e-12


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_tensor_total_degree_exactness(n):
    assert exactness_degree_2d(lambda f: tensor_square(f, n)) == 2 * n - 1


def test_tensor_square_on_a_smooth_function():
    val = tensor_square(lambda x, y: np.exp(x + y), 10)
    assert val == pytest.approx((np.e - 1) ** 2, rel=1e-13)


def test_composite_midpoint_and_trapezoid_on_the_square():
    for rule in ("midpoint", "trapezoid"):
        val = tensor_square(lambda x, y: x * y, 40, rule=rule)
        assert val == pytest.approx(0.25, abs=1e-3)


# ---------------------------------------------------------------- triangle
def test_barycentre_rule_is_exact_on_degree_one():
    """[S4] Exercise 2.22: weight |T| = 1/2 at (1/3, 1/3), exact on P_1."""
    assert barycentre_triangle(lambda x, y: 1.0 + 0 * x) == pytest.approx(0.5)
    assert barycentre_triangle(lambda x, y: x) == pytest.approx(1 / 6)
    assert barycentre_triangle(lambda x, y: y) == pytest.approx(1 / 6)
    for a, b, c in [(1.0, 2.0, -3.0), (0.0, 1.0, 1.0)]:
        f = lambda x, y: a + b * x + c * y
        assert barycentre_triangle(f) == pytest.approx(a / 2 + b / 6 + c / 6)
    assert exactness_degree_2d(barycentre_triangle, "triangle") == 1


def test_vertex_rule_is_exact_on_degree_one():
    """[S4] Exercise 2.22, second part: the three vertices with weights 1/6."""
    assert vertex_triangle(lambda x, y: 1.0 + 0 * x) == pytest.approx(0.5)
    assert vertex_triangle(lambda x, y: x) == pytest.approx(1 / 6)
    assert exactness_degree_2d(vertex_triangle, "triangle") == 1
    # not exact on x^2: int = 1/12, rule = (0 + 1 + 0)/6 = 1/6
    assert vertex_triangle(lambda x, y: x ** 2) == pytest.approx(1 / 6)
    assert monomial_integral_triangle(2, 0) == pytest.approx(1 / 12)


@pytest.mark.parametrize("n", [4, 8, 12])
def test_duffy_converges_on_the_triangle(n):
    """[S4] Ex. 2.23.  int_T exp(x) dy dx = e - 2."""
    got = duffy_triangle(lambda x, y: np.exp(x), n)
    assert got == pytest.approx(np.e - 2, abs=10.0 ** (-n // 2))


def test_duffy_exact_on_low_degree():
    for n in (6, 10):
        rule = lambda f: duffy_triangle(f, n)
        for (i, j) in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2)]:
            assert rule(lambda x, y, i=i, j=j: x ** i * y ** j) == pytest.approx(
                monomial_integral_triangle(i, j), abs=1e-12)


def test_duffy_jacobian_costs_accuracy():
    """The (1-x) factor makes a polynomial integrand non-polynomial, so the
    Duffy rule needs more points than the underlying tensor rule suggests."""
    square = exactness_degree_2d(lambda f: tensor_square(f, 3))
    triangle = exactness_degree_2d(lambda f: duffy_triangle(f, 3), "triangle")
    assert triangle <= square
