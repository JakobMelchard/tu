"""plot_helper.py writes valid figures, and the data it plots for note 04 has order 2.

The convergence figure is only worth drawing if the plotted errors really follow
h^2 [S23 ch. 2]; the slope is checked here with numpy.polyfit, and the PNGs are
written to a temporary directory so the committed notes/img/ files stay untouched.
"""
import numpy as np
import pytest

import plot_helper
from fd_poisson import poisson1d, poisson2d

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def out(tmp_path, monkeypatch):
    monkeypatch.setattr(plot_helper, "OUT", tmp_path)
    return tmp_path


def test_convergence_figure_and_its_slope(out):
    f = lambda x: np.pi**2 * np.sin(np.pi * x)
    Ns = np.array([8, 16, 32, 64])
    errs = [np.max(np.abs(poisson1d(f, N)[1] - np.sin(np.pi * np.linspace(0, 1, N + 1)))) for N in Ns]
    slope = np.polyfit(np.log(1.0 / Ns), np.log(errs), 1)[0]
    assert abs(slope - 2.0) < 0.02
    path = plot_helper.plot_convergence(1.0 / Ns, errs, 2, "FD Poisson 1D", "conv.png")
    assert path.parent == out and path.read_bytes()[:8] == PNG_MAGIC


def test_field_figure(out):
    X, Y, U = poisson2d(lambda X, Y: 2 * np.pi**2 * np.sin(np.pi * X) * np.sin(np.pi * Y), 16)
    assert np.max(np.abs(U - np.sin(np.pi * X) * np.sin(np.pi * Y))) < 1e-2
    path = plot_helper.plot_field(U, "field.png", "test")
    assert path.stat().st_size > 1000 and path.read_bytes()[:8] == PNG_MAGIC
