"""Matplotlib and tabular data (note 04).

The figure/axes object model, publication-style figures, subplots, 3D,
images, and pandas basics.  Every plot function writes a PNG into `outdir`
and returns its path; the Agg backend is forced so this runs headless.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                       # before pyplot import: no display needed
import matplotlib.pyplot as plt             # noqa: E402
import numpy as np                           # noqa: E402
import pandas as pd                          # noqa: E402

PUB_STYLE = {
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8,
    "lines.linewidth": 1.2, "figure.dpi": 100, "savefig.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
}


def line_plot(outdir: Path) -> Path:
    """Object-oriented API: Figure holds Axes; Axes own the artists.  Avoid
    the stateful plt.plot(...) interface in scripts and functions."""
    x = np.linspace(0, 2 * np.pi, 400)
    with plt.rc_context(PUB_STYLE):
        fig, ax = plt.subplots(figsize=(3.4, 2.4), constrained_layout=True)   # single column
        for k in (1, 2, 3):
            ax.plot(x, np.sin(k * x) / k, label=rf"$\sin({k}x)/{k}$")
        ax.set(xlabel="$x$", ylabel="$y$", xlim=(0, 2 * np.pi), title="Harmonics")
        ax.legend(frameon=False)
        path = outdir / "line.png"
        fig.savefig(path)                    # png for screen, pdf/svg for papers
        plt.close(fig)                       # free memory in loops
    return path


def subplots_grid(outdir: Path) -> Path:
    """Shared axes, log scales, error bars, twin axis, annotation."""
    rng = np.random.default_rng(0)
    fig, axs = plt.subplots(2, 2, figsize=(7, 5), sharex="col", constrained_layout=True)
    x = np.linspace(0.1, 10, 50)
    axs[0, 0].plot(x, x**2); axs[0, 0].set_title("linear")
    axs[0, 1].loglog(x, x**2, "o-", ms=3); axs[0, 1].set_title("log-log: slope = exponent")
    y = np.exp(-x / 3) + 0.05 * rng.standard_normal(x.size)
    axs[1, 0].errorbar(x, y, yerr=0.05, fmt=".", capsize=2)
    axs[1, 0].annotate("noise floor", xy=(8, 0.05), xytext=(5, 0.5),
                       arrowprops=dict(arrowstyle="->"))
    ax2 = axs[1, 1].twinx()
    axs[1, 1].plot(x, np.sin(x), "C0"); ax2.plot(x, 100 * np.cos(x), "C1")
    axs[1, 1].set_ylabel("sin", color="C0"); ax2.set_ylabel("100 cos", color="C1")
    for ax in axs[1]:
        ax.set_xlabel("x")
    path = outdir / "grid.png"
    fig.savefig(path); plt.close(fig)
    return path


def image_plot(outdir: Path) -> Path:
    """imshow: origin upper-left by default, extent maps pixels to data
    coordinates; use a perceptually uniform colormap and a colorbar."""
    x, y = np.meshgrid(np.linspace(-2, 2, 200), np.linspace(-2, 2, 200))
    z = np.exp(-(x**2 + y**2)) * np.cos(3 * x)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7, 3), constrained_layout=True)
    im = a1.imshow(z, extent=(-2, 2, -2, 2), origin="lower", cmap="viridis")
    fig.colorbar(im, ax=a1, label="z")
    cs = a2.contourf(x, y, z, levels=15, cmap="RdBu_r", vmin=-1, vmax=1)   # diverging: centred
    a2.contour(x, y, z, levels=[0], colors="k", linewidths=0.6)
    fig.colorbar(cs, ax=a2)
    a1.set_title("imshow"); a2.set_title("contourf")
    path = outdir / "image.png"
    fig.savefig(path); plt.close(fig)
    return path


def surface_3d(outdir: Path) -> Path:
    """mplot3d: projection='3d' axes; plot_surface needs 2D X, Y, Z grids."""
    x, y = np.meshgrid(np.linspace(-3, 3, 60), np.linspace(-3, 3, 60))
    z = np.sin(np.hypot(x, y)) / (1 + np.hypot(x, y))
    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(x, y, z, cmap="viridis", linewidth=0)
    ax.view_init(elev=30, azim=-60)
    ax.set(xlabel="x", ylabel="y", zlabel="z")
    path = outdir / "surface.png"
    fig.savefig(path); plt.close(fig)
    return path


def histogram_and_fit(outdir: Path) -> Path:
    rng = np.random.default_rng(1)
    data = rng.normal(1.0, 0.3, 5000)
    fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
    counts, edges, _ = ax.hist(data, bins=40, density=True, alpha=0.6, label="samples")
    mids = 0.5 * (edges[1:] + edges[:-1])
    mu, sd = data.mean(), data.std()
    ax.plot(mids, np.exp(-0.5 * ((mids - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)),
            label=rf"$\mathcal{{N}}({mu:.2f}, {sd:.2f}^2)$")
    ax.legend()
    path = outdir / "hist.png"
    fig.savefig(path); plt.close(fig)
    return path


# ---------------------------------------------------------------- pandas
def make_measurements(n: int = 120, seed: int = 0) -> pd.DataFrame:
    """A DataFrame is a dict of column Series sharing an Index; columns are
    numpy arrays underneath (one dtype per column)."""
    rng = np.random.default_rng(seed)
    sample = rng.choice(["A", "B", "C"], size=n)
    temp = rng.choice([300, 350, 400], size=n)
    base = {"A": 1.0, "B": 2.0, "C": 3.0}
    y = np.array([base[s] for s in sample]) * (temp / 300) + 0.1 * rng.standard_normal(n)
    return pd.DataFrame({"sample": sample, "temp_K": temp, "conductivity": y})


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    """Split-apply-combine: groupby returns one row per key, agg names the
    statistics.  pivot_table reshapes long -> wide."""
    return df.groupby(["sample", "temp_K"])["conductivity"].agg(["mean", "std", "count"])


def wide_table(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot_table(index="sample", columns="temp_K", values="conductivity", aggfunc="mean")


def csv_roundtrip(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    df.to_csv(path, index=False)
    return pd.read_csv(path)


def plot_dataframe(df: pd.DataFrame, outdir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
    for name, g in df.groupby("sample"):
        s = g.groupby("temp_K")["conductivity"].agg(["mean", "std"])
        ax.errorbar(s.index, s["mean"], yerr=s["std"], marker="o", capsize=3, label=name)
    ax.set(xlabel="T [K]", ylabel="conductivity [a.u.]"); ax.legend(title="sample")
    path = outdir / "df.png"
    fig.savefig(path); plt.close(fig)
    return path


def all_plots(outdir: Path) -> list[Path]:
    df = make_measurements()
    return [line_plot(outdir), subplots_grid(outdir), image_plot(outdir),
            surface_3d(outdir), histogram_and_fit(outdir), plot_dataframe(df, outdir)]


if __name__ == "__main__":
    out = Path(tempfile.mkdtemp(prefix="plotting_"))
    for p in all_plots(out):
        print("wrote", p, p.stat().st_size, "bytes")
    df = make_measurements()
    print(df.head(), "\n", summarise(df).head(), "\n", wide_table(df))
