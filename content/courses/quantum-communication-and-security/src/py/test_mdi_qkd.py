import itertools

import pytest

from mdi_qkd import (LCQ, POL, gain_qber, key_rate, mr_diag, mr_e11, mr_rect, mr_y11, rate_curve,
                     single_photon_bsm, y11_e11)
from decoy import max_distance


def test_ideal_bsm_success_half_and_bell_state_table():
    for basis in ("Z", "X"):
        y, e = y11_e11(basis, 1.0, 1.0)
        assert y == pytest.approx(0.5) and e == pytest.approx(0.0, abs=1e-12)
    # equal Z bits never succeed (HOM bunching / same polarisation)
    r = single_photon_bsm(POL[("Z", 0)], POL[("Z", 0)], 1, 1)
    assert r["psi_minus"] + r["psi_plus"] == pytest.approx(0.0, abs=1e-12)
    # equal X bits: only Psi+; different X bits: only Psi-
    r = single_photon_bsm(POL[("X", 0)], POL[("X", 0)], 1, 1)
    assert r["psi_minus"] == pytest.approx(0, abs=1e-12) and r["psi_plus"] == pytest.approx(0.5)
    r = single_photon_bsm(POL[("X", 0)], POL[("X", 1)], 1, 1)
    assert r["psi_plus"] == pytest.approx(0, abs=1e-12) and r["psi_minus"] == pytest.approx(0.5)


def test_fock_model_probabilities_normalised():
    for (ba, xa), (bb, xb) in itertools.product(POL, repeat=2):
        assert single_photon_bsm(POL[(ba, xa)], POL[(bb, xb)], 0.3, 0.7)["norm"] == pytest.approx(1.0)


@pytest.mark.parametrize("eta_a,eta_b,pd", [(0.01, 0.01, 1e-4), (0.2, 0.05, 1e-3), (1e-3, 2e-3, 3e-6)])
def test_fock_model_matches_ma_razavi_single_photon_forms(eta_a, eta_b, pd):
    for basis in ("Z", "X"):
        y, _ = y11_e11(basis, eta_a, eta_b, pd)
        assert y == pytest.approx(mr_y11(eta_a, eta_b, pd), rel=1e-9)
    _, ex = y11_e11("X", eta_a, eta_b, pd)
    assert ex == pytest.approx(mr_e11(eta_a, eta_b, pd, 0.0), rel=1e-9)


@pytest.mark.parametrize("ma,mb,pd", [(0.05, 0.05, 1e-4), (0.3, 0.1, 1e-5), (0.01, 0.02, 3e-6)])
def test_coherent_model_matches_ma_razavi_gains(ma, mb, pd):
    qz, ez = gain_qber("Z", ma, mb, pd)
    qx, ex = gain_qber("X", ma, mb, pd)
    rz, rx = mr_rect(ma, mb, pd, 0.0), mr_diag(ma, mb, pd, 0.0)
    assert qz == pytest.approx(rz[0], rel=1e-9) and ez == pytest.approx(rz[1], rel=1e-9)
    assert qx == pytest.approx(rx[0], rel=1e-9) and ex == pytest.approx(rx[1], rel=1e-9)


def test_rate_curve_reaches_beyond_200_km_and_scales_with_total_transmittance():
    curve = rate_curve([0, 100, 200])
    assert all(r > 0 for _, _, r in curve)
    assert curve[0][2] / curve[1][2] == pytest.approx(10 ** (0.2 * 100 / 10), rel=0.25)
    d = max_distance(lambda L: rate_curve([L])[0][2], hi=500)
    assert 200 < d < 260


def test_misalignment_reduces_rate():
    from dataclasses import replace
    worse = replace(LCQ, ed=0.03)
    assert key_rate(50, 0.5, worse) < key_rate(50, 0.5, LCQ)
