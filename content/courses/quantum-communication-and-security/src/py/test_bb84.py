import numpy as np
import pytest

from bb84 import (estimate_qber, eve_information, qber, qber_analytic, sampling_deviation_mc,
                  serfling_tail, sift, simulate)


def test_no_eve_no_noise_is_error_free_and_sifting_keeps_half():
    rng = np.random.default_rng(0)
    s = sift(simulate(50_000, rng))
    assert qber(s) == 0.0
    assert len(s["a_bits"]) / 50_000 == pytest.approx(0.5, abs=0.01)


@pytest.mark.parametrize("p_ir,p_dep", [(1.0, 0.0), (0.5, 0.0), (0.0, 0.1), (0.3, 0.06)])
def test_qber_matches_analytic_within_five_sigma(p_ir, p_dep):
    rng = np.random.default_rng(1)
    s = sift(simulate(100_000, rng, p_ir, p_dep))
    e = qber_analytic(p_ir, p_dep)["total"]
    sigma = np.sqrt(e * (1 - e) / len(s["a_bits"]))
    assert abs(qber(s) - e) < 5 * sigma + 1e-12


def test_full_intercept_resend_gives_25_percent_and_eve_knows_half():
    rng = np.random.default_rng(2)
    s = sift(simulate(100_000, rng, 1.0, 0.0))
    assert qber(s) == pytest.approx(0.25, abs=0.01)
    assert eve_information(s) == pytest.approx(0.5, abs=0.01)     # I(A:E) = 2e


def test_biased_eve_shows_up_only_in_x_basis():
    rng = np.random.default_rng(3)
    s = sift(simulate(100_000, rng, 1.0, 0.0, eve_basis="Z"))
    a = qber_analytic(1.0, 0.0, "Z")
    assert qber(s, 0) == 0.0 and a["Z"] == 0.0
    assert qber(s, 1) == pytest.approx(a["X"], abs=0.01)


def test_sample_estimate_is_consistent_with_remainder():
    rng = np.random.default_rng(4)
    s = sift(simulate(40_000, rng, 0.2, 0.02))
    est, rest = estimate_qber(s, 4000, rng)
    assert abs(est - qber(rest)) < 0.015
    assert len(rest["a_bits"]) == len(s["a_bits"]) - 4000


def test_serfling_tail_bounds_monte_carlo():
    rng = np.random.default_rng(5)
    n, k, e, nu = 900, 100, 0.05, 0.05
    mc = sampling_deviation_mc(n, k, e, nu, 4000, rng)
    assert mc <= serfling_tail(n, k, nu)
