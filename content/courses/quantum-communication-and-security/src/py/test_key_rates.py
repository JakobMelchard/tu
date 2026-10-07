import numpy as np
import pytest

from entropies import bb84_lams, h2
from key_rates import (decoy_rate_curve, devetak_winter_bb84_min, devetak_winter_bell_diagonal,
                       finite_key_errors, finite_key_length, holevo_eve, shor_preskill,
                       single_photon_rate, sp_threshold)


def test_shor_preskill_threshold_is_eleven_percent():
    assert sp_threshold() == pytest.approx(0.110028, abs=1e-6)
    assert shor_preskill(0.05) == pytest.approx(1 - 2 * h2(0.05))


@pytest.mark.parametrize("e", [0.01, 0.04, 0.08, 0.11])
def test_devetak_winter_minimum_equals_shor_preskill(e):
    rate, arg = devetak_winter_bb84_min(e)
    assert rate == pytest.approx(shor_preskill(e), abs=1e-9)
    assert arg == pytest.approx(e * e, abs=e / 200)


def test_eve_holevo_is_h_of_e_in_worst_case_and_rate_is_ia_b_minus_chi():
    e = 0.06
    lams = bb84_lams(e, e)
    assert holevo_eve(lams) == pytest.approx(h2(e), abs=1e-9)
    i_ab = 1 - h2(e)
    assert devetak_winter_bell_diagonal(lams) == pytest.approx(i_ab - holevo_eve(lams), abs=1e-9)


def test_devetak_winter_depends_on_unobserved_weight():
    e = 0.05
    assert devetak_winter_bell_diagonal(bb84_lams(e, e, 0.0)) > shor_preskill(e)


def test_decoy_curve_decreases_and_single_photon_source_is_better():
    curve = decoy_rate_curve([0, 50, 100])
    rates = [r for _, _, r in curve]
    assert rates[0] > rates[1] > rates[2] > 0
    for L, _, r in curve:
        assert single_photon_rate(L) > r
    # rate ~ eta: 50 km of 0.21 dB/km is 10.5 dB -> factor ~ 11
    assert rates[0] / rates[1] == pytest.approx(10 ** 1.05, rel=0.15)


def test_finite_key_approaches_asymptotic_and_is_eps_secure():
    ms = [10**4, 10**5, 10**6, 10**7]
    rates = [finite_key_length(m, 0.02)[0] / m for m in ms]
    assert all(np.diff(rates) > 0)
    assert rates[-1] < 1 - 2.1 * h2(0.02)
    assert rates[-1] > 0.85 * (1 - 2.1 * h2(0.02))
    l, p = finite_key_length(10**6, 0.02)
    errs = finite_key_errors(10**6, p["k"], 0.02, p["nu"], p["r"], p["t"], l)
    assert errs["total"] <= 1e-10
    assert finite_key_errors(10**6, p["k"], 0.02, p["nu"], p["r"], p["t"], l + 200)["total"] > 1e-10


def test_finite_key_vanishes_for_tiny_blocks():
    assert finite_key_length(1000, 0.05)[0] == 0
