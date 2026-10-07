import numpy as np
import pytest

from error_bars import ar1, binning_curve, binning_error, bootstrap, mean_sem, tau_int_ar1


def test_mean_sem_of_independent_normals():
    rng = np.random.default_rng(0)
    sems = [mean_sem(rng.standard_normal(100))[1] for _ in range(200)]
    assert np.mean(sems) == pytest.approx(0.1, rel=0.05)


def test_ar1_has_unit_variance_and_exact_tau():
    assert tau_int_ar1(0.0) == 0.5
    assert tau_int_ar1(0.9) == pytest.approx(9.5)
    x = ar1(2 ** 16, 0.9, np.random.default_rng(1))
    assert x.var() == pytest.approx(1.0, rel=0.1)


def test_binning_plateau_reaches_exact_error():
    rho, n = 0.9, 2 ** 17
    x = ar1(n, rho, np.random.default_rng(2))
    exact = np.sqrt(2 * tau_int_ar1(rho) / n)
    assert binning_error(x, 1) < 0.3 * exact                 # naive error far too small
    assert binning_error(x, 512) == pytest.approx(exact, rel=0.2)
    errs = [e for _, e in binning_curve(x)]
    assert np.all(np.diff(errs[:5]) > 0)                    # rises before the plateau


def test_bootstrap_of_mean_matches_sem():
    rng = np.random.default_rng(3)
    d = rng.standard_normal((400, 1))
    v, e = bootstrap(lambda z: float(z.mean()), d, n_boot=2000, rng=rng)
    assert e == pytest.approx(mean_sem(d[:, 0])[1], rel=0.1)
