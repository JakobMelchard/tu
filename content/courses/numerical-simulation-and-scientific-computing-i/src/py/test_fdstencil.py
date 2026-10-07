"""The stencil table of note 03, regenerated and checked.

Fornberg (1988) [S25] is the reference for the recurrence; the weights
themselves are classical and are checked here in exact rational arithmetic, so
a wrong entry in the note cannot pass.
"""
from fractions import Fraction as F

import numpy as np

from fdstencil import leading_error_term, weights_fornberg, weights_vandermonde


def test_classical_weights_are_exact():
    assert weights_vandermonde((0, 1), 1) == [F(-1), F(1)]
    assert weights_vandermonde((-1, 0), 1) == [F(-1), F(1)]
    assert weights_vandermonde((-1, 1), 1) == [F(-1, 2), F(1, 2)]
    assert weights_vandermonde((-1, 0, 1), 2) == [F(1), F(-2), F(1)]
    assert weights_vandermonde((0, 1, 2), 1) == [F(-3, 2), F(2), F(-1, 2)]
    assert weights_vandermonde((-2, -1, 1, 2), 1) == [F(1, 12), F(-2, 3), F(2, 3), F(-1, 12)]
    assert weights_vandermonde((-2, -1, 0, 1, 2), 2) == [F(-1, 12), F(4, 3), F(-5, 2),
                                                         F(4, 3), F(-1, 12)]


def test_leading_error_terms_match_note_03():
    """(derivative order m, coefficient C) with error C h^(m-d) f^(m)."""
    assert leading_error_term((0, 1), 1) == (2, F(1, 2))
    assert leading_error_term((-1, 0), 1) == (2, F(-1, 2))
    assert leading_error_term((-1, 1), 1) == (3, F(1, 6))
    assert leading_error_term((-1, 0, 1), 2) == (4, F(1, 12))
    # the two the note had with the wrong sign:
    assert leading_error_term((-2, -1, 1, 2), 1) == (5, F(-1, 30))
    assert leading_error_term((0, 1, 2), 1) == (3, F(-1, 3))


def test_fornberg_agrees_with_the_order_conditions():
    for off, d in [((0, 1), 1), ((-1, 1), 1), ((-1, 0, 1), 2), ((-2, -1, 1, 2), 1),
                   ((-2, -1, 0, 1, 2), 2), ((0, 1, 2, 3, 4), 3)]:
        exact = np.array([float(x) for x in weights_vandermonde(off, d)])
        assert np.allclose(weights_fornberg(off, d)[d], exact, atol=1e-13)


def test_fornberg_on_a_nonuniform_stencil():
    """Fornberg's point [S25]: the nodes need not be equally spaced."""
    off = (-1, 0, 2, 5)
    w = weights_fornberg(off, 1)[1]
    s = np.array(off, float)
    # the order conditions: annihilate 1 and x^2..x^3, reproduce x
    assert abs(w.sum()) < 1e-12
    assert abs((w * s).sum() - 1) < 1e-12
    assert abs((w * s**2).sum()) < 1e-12
    assert abs((w * s**3).sum()) < 1e-12


def test_measured_order_matches_the_predicted_one():
    """Apply each stencil to exp and read the observed order off a refinement."""
    f = np.exp
    x = 0.7
    for off, d, want in [((0, 1), 1, 1), ((-1, 1), 1, 2), ((-1, 0, 1), 2, 2),
                         ((-2, -1, 1, 2), 1, 4)]:
        w = np.array([float(v) for v in weights_vandermonde(off, d)])
        s = np.array(off, float)
        errs = []
        for h in (1e-1, 5e-2, 2.5e-2):
            errs.append(abs((w * f(x + s * h)).sum() / h**d - f(x)))
        p = np.log2(errs[0] / errs[1]), np.log2(errs[1] / errs[2])
        assert all(abs(q - want) < 0.15 for q in p), (off, d, p)
