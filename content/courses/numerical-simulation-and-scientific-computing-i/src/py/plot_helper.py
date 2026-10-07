"""Plot helpers for the notes: log-log convergence and a 2D field (notes 04, 09).

`plot_convergence` draws max-error against h on log-log axes with a reference
line h^order through the first point; a second-order scheme [S23 ch. 2] must lie
parallel to it. `plot_field` draws a 2D grid function with x horizontal.

Uses the Agg backend so it also works headless (tests). Figures go to
../../notes/img/ (module variable OUT; test_plot_helper.py points it elsewhere).
Run `python3 plot_helper.py` to regenerate fd_poisson_convergence.png and
poisson2d.png.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "notes" / "img"


def plot_convergence(hs, errors, order, label, fname):
    """Error vs h on log-log axes with a reference line of the given order."""
    hs, errors = np.asarray(hs, float), np.asarray(errors, float)
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    ax.loglog(hs, errors, "o-", label=label)
    ax.loglog(hs, errors[0] * (hs / hs[0]) ** order, "k--", label=f"$h^{order}$")
    ax.set_xlabel("h")
    ax.set_ylabel("max error")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    return _save(fig, fname)


def plot_field(U, fname, title=""):
    fig, ax = plt.subplots(figsize=(4.5, 4))
    im = ax.imshow(U.T, origin="lower", extent=(0, 1, 0, 1), cmap="viridis")
    fig.colorbar(im, ax=ax)
    ax.set_title(title)
    return _save(fig, fname)


def _save(fig, fname):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / fname
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


if __name__ == "__main__":
    from fd_poisson import poisson1d, poisson2d

    f = lambda x: np.pi**2 * np.sin(np.pi * x)
    Ns = [8, 16, 32, 64, 128]
    errs = [np.max(np.abs(poisson1d(f, N)[1] - np.sin(np.pi * np.linspace(0, 1, N + 1)))) for N in Ns]
    print(plot_convergence([1 / N for N in Ns], errs, 2, "FD Poisson 1D", "fd_poisson_convergence.png"))
    X, Y, U = poisson2d(lambda X, Y: 2 * np.pi**2 * np.sin(np.pi * X) * np.sin(np.pi * Y), 64)
    print(plot_field(U, "poisson2d.png", "-Laplace u = f, N = 64"))
