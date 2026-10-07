# 04 Matplotlib and data processing

Code: [`../src/py/plotting.py`](../src/py/plotting.py) (writes PNGs to a temp dir), tests in `test_plotting.py`. Notebook: [`../src/notebooks/tour.ipynb`](../src/notebooks/tour.ipynb).

Sources: the Matplotlib 3.11.2 documentation [S17] and the pandas 3.0
documentation and release notes [S16]. **Verified against Matplotlib 3.11.2 and
pandas 3.0.6** [S40], last re-run 2026-09-27. §7 changed substantially in pandas 3.0; if the course's
TUWEL environment pins pandas 2, read the boxed warning there. (Which pandas the course uses is unverified: TUWEL was not read.)

## 1. The object model

Matplotlib has three layers: the **backend** (renders to screen or file: `Agg` for PNG, `pdf`, `svg`, `MacOSX`/`QtAgg` for windows, `inline` in Jupyter), the **artist** layer (everything drawn is an `Artist`: `Figure`, `Axes`, `Axis`, `Line2D`, `Text`, `Patch`, `Image`), and the **scripting** layer `pyplot`, a stateful wrapper that tracks a "current figure/axes".

Hierarchy: a `Figure` (the canvas, with `figsize` in inches and `dpi`) contains one or more `Axes` (a plotting area with its own data coordinate system); each `Axes` has two `Axis` objects (ticks, labels, scale) and holds the artists produced by `ax.plot`, `ax.scatter`, `ax.imshow`, ... The recommended style is **object-oriented**, and Matplotlib's own *API interfaces* page says so [S17]: `fig, ax = plt.subplots()` then `ax.plot(...)`, `ax.set_xlabel(...)`, `fig.savefig(...)`. `plt.plot(...)` works on "whatever is current", which breaks inside functions and loops. `ax.set(xlabel=..., ylim=...)` sets several properties at once.

Every plot call returns the artists (`lines = ax.plot(...)` gives a list of `Line2D`), which you can restyle later (`line.set_color`). Colour cycle: `C0`, `C1`, ... index the current property cycle. Format strings: `"o-"`, `"k--"`. `ax.legend()` collects artists with a `label=`.

`fig.savefig("f.pdf")` chooses the format from the extension; vector formats (pdf, svg) for line plots in papers, raster (png with `dpi=200+`) for images and dense scatter. `bbox_inches="tight"` crops whitespace; `layout="constrained"` prevents overlapping labels — that is the current spelling, and it is what the layout guide uses [S17]; the older `constrained_layout=True` and `fig.tight_layout()` still work in 3.11.2 (both verified). `plt.close(fig)` releases memory; matplotlib warns after 20 open figures (`rcParams["figure.max_open_warning"]`, checked in the venv). Headless scripts and tests: `matplotlib.use("Agg")` *before* importing pyplot (`plotting.py`).

## 2. Publication figures

- Size the figure to the final column width (`figsize=(3.4, 2.4)` inches for a single column) so fonts come out at the size you set instead of being shrunk.
- Style through `rcParams` (`plt.rc_context(PUB_STYLE)` for a scoped change, `plt.style.use("seaborn-v0_8-paper")` or a `.mplstyle` file for a global one): font sizes, line widths, spines, `savefig.dpi`.
- Label axes with units, use $\LaTeX$ math in labels (`r"$\sigma^2$"`; `text.usetex=True` for real LaTeX), `ax.legend(frameon=False)`, consistent colours across panels, colour-blind safe palettes (`tab10` default, `viridis` sequential, `RdBu_r` diverging centred with `vmin=-v, vmax=v`).
- Error bars: `ax.errorbar(x, y, yerr, fmt=".", capsize=2)`; `ax.fill_between(x, lo, hi, alpha=0.3)` for bands.
- Log axes: `ax.set_xscale("log")` / `ax.loglog`; a power law $y = c x^p$ is a straight line of slope $p$ in log-log (`subplots_grid`).
- Annotation: `ax.annotate(text, xy=(point), xytext=(text pos), arrowprops=dict(arrowstyle="->"))`; `ax.axhline`, `ax.axvspan` for reference lines/regions.
- `ax.twinx()` shares x with a second y axis (colour the axis labels to match the lines).

## 3. Subplots and layout

`fig, axs = plt.subplots(nrows, ncols, sharex=..., sharey=..., figsize=..., layout="constrained")` returns a 2D array of `Axes` (`squeeze=False` to always get 2D). `sharex="col"` links limits and hides inner tick labels. Uneven grids: `fig.add_gridspec(2, 3)` with slicing `ax = fig.add_subplot(gs[0, :])`, or `plt.subplot_mosaic([["a", "a"], ["b", "c"]])` returning a dict. Insets: `ax.inset_axes([x, y, w, h])`. Loop over `axs.flat`.

## 4. Images, contours and colour maps

`ax.imshow(Z, extent=(x0, x1, y0, y1), origin="lower", cmap, vmin, vmax, interpolation="nearest", aspect)`: without `extent` axes are pixel indices with row 0 at the *top* (`origin="upper"`, image convention). `fig.colorbar(im, ax=ax, label=...)` needs the mappable returned by `imshow`/`contourf`/`scatter(c=...)`. `ax.contour` (lines, `levels=`, `ax.clabel`) and `ax.contourf` (filled) take 2D `X, Y, Z` from `np.meshgrid`. `ax.pcolormesh(x, y, Z)` for non-uniform grids. Normalisation: `norm=LogNorm()`, `SymLogNorm`, `TwoSlopeNorm(vcenter=0)`. Use perceptually uniform sequential maps (`viridis` — the default `image.cmap` since 2.0 — `magma`, `cividis`), never `jet`; diverging maps only when zero is meaningful (`image_plot`). Matplotlib's *Choosing colormaps* page is the source for the perceptual-uniformity argument [S17].

## 5. 3D

`ax = fig.add_subplot(projection="3d")` (mplot3d): `plot_surface(X, Y, Z, cmap=...)`, `plot_wireframe`, `contour3D`, `scatter(x, y, z)`, `plot(x, y, z)`. `ax.view_init(elev, azim)` sets the camera; `ax.set_box_aspect` the aspect. It is a software renderer with painter's-algorithm depth sorting per artist, so intersecting surfaces render wrongly; for serious 3D use pyvista/mayavi/plotly. Often a heat map or contour plot communicates better than a surface (`surface_3d`).

## 6. Other plot types

`hist(data, bins, density=True)` (returns counts, edges), `hist2d`/`hexbin`, `bar`/`barh`, `boxplot`/`violinplot`, `scatter(x, y, c=values, s=sizes)`, `step`, `stem`, `quiver`/`streamplot` for vector fields, `polar` projection, `matshow`. Animation: `matplotlib.animation.FuncAnimation`. Interactive exploration: `%matplotlib widget` in Jupyter, plotly/bokeh for web output.

## 7. pandas basics for tabular data

A **DataFrame** is a dict-like collection of **Series** (1D, labelled, one dtype each, numpy or extension arrays underneath) sharing an **Index** [S16]. Rows are labelled by the index, columns by name; alignment on labels is automatic in arithmetic (a source of NaNs when indices differ).

> **pandas 3.0 changed three things you will read the old version of everywhere.** Verified in the venv against pandas 3.0.6 [S40]; all three are in the 3.0.0 release notes [S16].
>
> 1. **Copy-on-Write is permanent.** Any subset or returned object *always behaves as a copy*, while pandas uses views internally where it can. The `mode.copy_on_write` option still exists but does nothing and warns that it will be removed in 4.0.
> 2. **`SettingWithCopyWarning` is gone** — the class is no longer in `pandas.errors` at all. Chained assignment does not silently half-work any more; it simply does nothing to the original and raises a `ChainedAssignmentError` warning instead. All those defensive `.copy()` calls people wrote to silence the old warning are unnecessary.
> 3. **String columns default to a dedicated `str` dtype**, not `object` (PDEP-14): `pd.Series(["a", "b"]).dtype` is `str`, backed by PyArrow when it is installed and by numpy `object` otherwise. Unlike `object`, that dtype can hold only strings and missing values.

```python
df = pd.read_csv("m.csv")                 # to_csv, read_parquet, read_excel, read_hdf
df.head(); df.dtypes; df.describe(); df.shape
df["conductivity"]                        # Series (a view-ish column)
df[["sample", "temp_K"]]                  # DataFrame (copy)
df.loc[df.temp_K > 300, "conductivity"]   # label-based; .iloc is positional
df.query("sample == 'A' and temp_K >= 350")
df.assign(sigma=lambda d: 1 / d.conductivity)
df.groupby(["sample", "temp_K"])["conductivity"].agg(["mean", "std", "count"])
df.pivot_table(index="sample", columns="temp_K", values="conductivity", aggfunc="mean")
df.melt(...)                              # wide -> long (tidy) ; pivot for long -> wide
df.merge(other, on="key", how="left")     # SQL join; pd.concat stacks
df.sort_values("temp_K"); df.dropna(); df.fillna(0); df.astype({"temp_K": "float32"})
df.to_numpy()                             # -> ndarray (object dtype if mixed)
```

Split-apply-combine (`groupby` -> `agg`/`transform`/`apply`) is the core idiom (`summarise`). `transform` returns a result aligned to the original rows (for group-wise normalisation). Time series: `pd.to_datetime`, a `DatetimeIndex`, `resample("1h").mean()`, `rolling(20).mean()`. Plotting: `df.plot(x=..., y=..., kind=...)` returns an `Axes`; for control, pass `ax=` or extract arrays and plot with matplotlib (`plot_dataframe`).

Pitfalls: chained assignment `df[mask]["col"] = v` writes to a temporary and leaves `df` unchanged — use `df.loc[mask, "col"] = v`. In pandas 3 this raises a **`ChainedAssignmentError`** warning; in pandas ≤ 2 it raised `SettingWithCopyWarning`, which no longer exists [S16]. Further: integer columns become float when NaNs appear (use nullable `Int64`); `axis=0` means "down the rows" (per column); `df.values`/`to_numpy()` may be object dtype for mixed frames; iterating rows (`iterrows`) is slow — vectorise on columns; `inplace=True` is discouraged and under CoW buys nothing. `std()` in pandas uses `ddof=1`, numpy `ddof=0` (checked: `pd.Series([1.,2.,3.]).std() == 1.0` vs `np.std(...) == 0.8165`). `read_csv` guesses dtypes: pass `dtype=` for large files, `parse_dates=`.

Where pandas is the wrong tool: homogeneous numeric arrays (use numpy), data larger than memory (polars, dask, duckdb, chunked reads).

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md).

1. In the matplotlib object model, which statement is correct?
   (a) A Figure has exactly one Axes. (b) An Axes has two Axis objects and holds the plotted artists. (c) `Axis` and `Axes` are synonyms. (d) `plt.plot` returns a Figure.
   **b.** Figure > Axes (plotting areas) > Axis (x and y); `plt.plot` returns a list of `Line2D`.

2. `ax.imshow(Z)` with no arguments places row 0 of `Z`
   (a) at the bottom (b) at the top (c) at the centre (d) depends on the colormap
   **b.** Image convention `origin="upper"`; use `origin="lower"` with `extent` for data grids.

3. `fig.savefig("plot.svg")` produces
   (a) a raster image at `savefig.dpi` (b) a vector image where lines stay sharp when zoomed (c) an error, only png is supported (d) an interactive HTML file
   **b.** Format follows the extension; pdf/svg are vector.

4. `df.groupby("sample")["y"].transform("mean")` returns
   (a) one value per group (b) a Series aligned with the original rows holding each row's group mean (c) a DataFrame with one column per group (d) the global mean
   **b.** `agg` reduces to one row per group; `transform` broadcasts back to the original index.

5. Why does `df[df.x > 0]["y"] = 1` not modify `df` in pandas 3?
   (a) Boolean indexing is not allowed in pandas. (b) The first indexing returns an object that behaves as a copy under Copy-on-Write; the assignment writes to that temporary and pandas raises a `ChainedAssignmentError` warning. (c) `y` is read-only. (d) It does modify `df`, but only the first matching row.
   **b.** Use `df.loc[df.x > 0, "y"] = 1`. In pandas ≤ 2 the same mistake raised `SettingWithCopyWarning`, a class that no longer exists [S16].
