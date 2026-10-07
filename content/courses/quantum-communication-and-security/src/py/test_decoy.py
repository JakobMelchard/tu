import math

import pytest

from decoy import (GYS, best_mu, max_distance, mu_optimal_small_eta, pns_attack_gains, rate_decoy,
                   rate_gllp_no_decoy, relative_deviations, two_decoy_bounds, vacuum_weak_bounds)


def test_poisson_mixture_identities():
    L, mu = 30.0, 0.48
    q = sum(GYS.yield_i(i, L) * mu**i / math.factorial(i) * math.exp(-mu) for i in range(40))
    eq = sum(GYS.error_i(i, L) * GYS.yield_i(i, L) * mu**i / math.factorial(i) * math.exp(-mu)
             for i in range(40))
    # Eq. (10) drops the Y0*eta_i cross term, so agreement is to O(Y0 * eta)
    assert q == pytest.approx(GYS.gain(mu, L), rel=1e-4)
    assert eq / q == pytest.approx(GYS.qber(mu, L), rel=1e-3)


@pytest.mark.parametrize("L", [10, 60, 120])
def test_vacuum_weak_bounds_bracket_true_values(L):
    mu, nu = 0.48, 0.05
    y1l, e1u = vacuum_weak_bounds(GYS.gain(mu, L), GYS.gain(nu, L), GYS.qber(nu, L), GYS.y0, mu, nu)
    assert y1l <= GYS.yield_i(1, L)
    assert e1u >= GYS.error_i(1, L)
    assert y1l > 0.97 * GYS.yield_i(1, L)


def test_bounds_tighten_as_decoy_intensity_goes_to_zero():
    devs = [relative_deviations(40, 0.48, nu) for nu in (0.12, 0.05, 0.01, 0.001)]
    assert all(a[0] > b[0] and a[1] > b[1] for a, b in zip(devs, devs[1:]))
    assert devs[-1][0] < 1e-3 and devs[-1][1] < 1e-2


def test_ma_et_al_figure_1_deviations_at_quarter_intensity():
    by, be = relative_deviations(40, 0.48, 0.25 * 0.48)
    assert 100 * by == pytest.approx(3.5, abs=0.1)
    assert 100 * be == pytest.approx(16.8, abs=0.2)


def test_two_decoy_with_vacuum_reduces_to_vacuum_weak():
    L, mu, nu = 50, 0.48, 0.05
    args = (GYS.gain(mu, L), GYS.gain(nu, L), GYS.qber(nu, L), GYS.gain(0, L), GYS.qber(0, L), mu, nu, 0.0)
    y0, y1, e1 = two_decoy_bounds(*args)
    y1v, e1v = vacuum_weak_bounds(GYS.gain(mu, L), GYS.gain(nu, L), GYS.qber(nu, L), GYS.y0, mu, nu)
    assert y0 == pytest.approx(GYS.y0)
    assert y1 == pytest.approx(y1v) and e1 == pytest.approx(e1v)


def test_ma_et_al_maximal_distances_and_optimal_mu():
    assert mu_optimal_small_eta() == pytest.approx(0.48, abs=0.005)
    assert max_distance(lambda L: rate_decoy(L, 0.48)) == pytest.approx(142.05, abs=0.3)
    assert max_distance(lambda L: rate_decoy(L, 0.48, nu=0.05)) == pytest.approx(140.55, abs=0.3)


def test_without_decoys_the_distance_collapses():
    d = max_distance(lambda L: best_mu(lambda LL, m: rate_gllp_no_decoy(LL, m), L)[1])
    assert 20 < d < 60


def test_pns_attack_is_exposed_by_the_decoy():
    p = pns_attack_gains(40, 0.48, 0.05)
    assert p["q_nu_pns"] < 0.3 * p["q_nu_honest"]
    assert p["y1_lower"] <= 0
