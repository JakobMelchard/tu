import numpy as np
import pytest

from errors import (machine_epsilon, ulp, naive_sum, kahan_sum, pairwise_sum,
                    quadratic_roots_naive, quadratic_roots_stable, cond_scalar,
                    cond, inverse, forward_backward_error, hilbert, norm_inf,
                    log1p_naive, log1p_series, cond_rel, rel_error, norm_1,
                    error_sources_fd)


def test_machine_epsilon_matches_finfo():
    assert machine_epsilon() == np.finfo(np.float64).eps == 2.0 ** -52
    assert machine_epsilon(np.float32) == np.finfo(np.float32).eps


def test_ulp_matches_numpy_spacing():
    for x in (1.0, 3.7, 1e10, 1e-5):
        assert ulp(x) == np.spacing(x)


def test_kahan_beats_naive_in_float32():
    x = np.full(10 ** 5, 0.1)
    err_naive = abs(float(naive_sum(x)) - 1e4)
    err_kahan = abs(float(kahan_sum(x)) - 1e4)
    err_pair = abs(float(pairwise_sum(x)) - 1e4)
    assert err_kahan < 1e-2 and err_pair < err_naive
    assert err_naive > 1.0


def test_stable_quadratic_roots():
    r_naive = quadratic_roots_naive(1.0, -1e8, 1.0)
    r_stab = quadratic_roots_stable(1.0, -1e8, 1.0)
    assert abs(r_stab[1] - 1e-8) / 1e-8 < 1e-12
    assert abs(r_naive[1] - 1e-8) / 1e-8 > 1e-3     # cancellation
    np.testing.assert_allclose(sorted(r_stab), sorted(np.roots([1, -1e8, 1])), rtol=1e-12)


def test_scalar_condition_number():
    # f = sqrt: kappa = 1/2 ; f = exp: kappa = |x|
    assert abs(cond_scalar(np.sqrt, 4.0) - 0.5) < 1e-6
    assert abs(cond_scalar(np.exp, 3.0) - 3.0) < 1e-5


def test_inverse_and_cond_against_numpy():
    rng = np.random.default_rng(3)
    A = rng.standard_normal((6, 6)) + 6 * np.eye(6)
    np.testing.assert_allclose(inverse(A), np.linalg.inv(A), atol=1e-12)
    assert abs(cond(A) - np.linalg.cond(A, np.inf)) / np.linalg.cond(A, np.inf) < 1e-10
    assert abs(cond(A, "1") - np.linalg.cond(A, 1)) / np.linalg.cond(A, 1) < 1e-10


def test_hilbert_condition_grows():
    c = [cond(hilbert(n)) for n in (3, 5, 8)]
    assert c[0] < c[1] < c[2] and c[2] > 1e10
    assert abs(c[0] - 748.0) < 1.0


def test_forward_error_within_bound():
    A = hilbert(5)
    x = np.arange(1.0, 6.0)
    b = A @ x
    x_hat = x + 1e-6 * np.array([1, -1, 1, -1, 1])
    r = forward_backward_error(A, b, x_hat)
    actual = norm_inf(x_hat - x) / norm_inf(x)
    assert actual <= r["forward_bound"] * (1 + 1e-12)
    assert r["backward_error"] < 1e-7


@pytest.mark.parametrize("n", [3, 4])
def test_singular_raises(n):
    with pytest.raises(ValueError):
        inverse(np.ones((n, n)))


# ================= [S4] sec. 3.2-3.3: the script's own examples ==============


def test_s4_example_3_5_log_one_plus_x():
    """[S4] Ex. 3.5, reproduced to the digit.

    MATLAB prints 1.234568003306966e-10 for the naive route and the true value
    is 1.234567890047248e-10 -- 6 correct digits out of 16.
    """
    x = 1.234567890123456e-10
    naive = float(log1p_naive(x))
    series = float(log1p_series(x, terms=2))
    assert naive == pytest.approx(1.234568003306966e-10, rel=1e-15)
    assert series == pytest.approx(1.234567890047248e-10, rel=1e-15)
    assert series == pytest.approx(np.log1p(x), rel=1e-15)
    assert abs(naive - np.log1p(x)) / abs(np.log1p(x)) > 1e-8      # ~10 digits lost
    assert abs(series - np.log1p(x)) / abs(np.log1p(x)) < 1e-15


def test_log_one_plus_x_problem_is_well_conditioned():
    """[S4] Ex. 3.5: kappa_rel = |x| / ((1+x)|log(1+x)|) <= 2 near 0."""
    for x in (1e-12, 1e-8, 1e-4, 0.1):
        k = float(cond_rel(np.log1p, lambda t: 1.0 / (1.0 + t), x))
        assert k <= 2.0
    # but the intermediate step w -> log w has kappa ~ 1/x
    for x in (1e-4, 1e-8):
        w = 1.0 + x
        assert 1.0 / abs(np.log(w)) == pytest.approx(1.0 / x, rel=1e-3)


def test_s4_example_3_6_quadratic_roots():
    """[S4] Ex. 3.6: x^2 - 2 p x - q = 0 with p = 400000, q = 1.234567890123456.

    MATLAB prints -1.543201506137848e-06 for p - sqrt(p^2+q) and the exact root
    is -1.543209862651343e-06.
    """
    p, q = 400000.0, 1.234567890123456
    naive = p - np.sqrt(p * p + q)
    x1 = p + np.sqrt(p * p + q)
    stable = -q / x1
    assert naive == pytest.approx(-1.543201506137848e-06, rel=1e-14)
    assert stable == pytest.approx(-1.543209862651343e-06, rel=1e-14)
    assert abs(naive - stable) / abs(stable) > 1e-6
    # the stable root satisfies the equation to machine precision
    assert abs(stable ** 2 - 2 * p * stable - q) < 1e-15 * max(1.0, abs(q))


def test_s1a_exam_condition_number():
    """S1a 1.4, 2024W: phi(x) = sqrt(2x+1) - 1, kappa_rel = (1 + 1/sqrt(2x+1))/2 <= 1."""
    phi = lambda x: np.sqrt(2 * x + 1) - 1
    dphi = lambda x: 1.0 / np.sqrt(2 * x + 1)
    for x in (1e-6, 1e-3, 0.5, 10.0, 1000.0):
        k = float(cond_rel(phi, dphi, x))
        assert k == pytest.approx(0.5 * (1 + 1 / np.sqrt(2 * x + 1)), rel=1e-10)
        assert k <= 1.0
    # the formula cancels near 0; the rationalised one does not
    x = 1e-12
    naive = np.sqrt(2 * x + 1) - 1
    stable = 2 * x / (np.sqrt(2 * x + 1) + 1)
    assert abs(stable - x) / x < 1e-12                    # phi(x) ~ x for small x
    assert abs(naive - stable) / stable > 1e-5


def test_norm_1_and_rel_error_match_numpy():
    A = np.random.default_rng(5).standard_normal((6, 4))
    assert norm_1(A) == pytest.approx(np.linalg.norm(A, 1))
    assert norm_1(A[:, 0]) == pytest.approx(np.linalg.norm(A[:, 0], 1))
    assert rel_error(1.1, 1.0) == pytest.approx(0.1)


def test_error_sources_fd_total_error_is_v_shaped():
    """[S4 §3.1]: discretisation error ~ h, round-off ~ u/h, minimum near sqrt(u)."""
    hs = 10.0 ** -np.arange(1, 15)
    disc, roundoff, total = error_sources_fd(np.exp, np.exp, 1.0, hs)
    k = int(np.argmin(total))
    assert 1e-10 <= hs[k] <= 1e-6                     # sqrt(u) ~ 1e-8
    assert total[0] > 100 * total[k] and total[-1] > 100 * total[k]
    np.testing.assert_allclose(roundoff * hs, roundoff[0] * hs[0])   # ~ 1/h
