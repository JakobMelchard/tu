# 03 SciPy

Code: [`../src/py/scipy_tour.py`](../src/py/scipy_tour.py), tests in `test_scipy_tour.py`. Optimisation has its own note (07).

Sources: the SciPy 1.18 reference [S15]; Dormand & Prince 1980 for RK45 [S37];
cross-checked against the *SciPy* chapter of the *Scientific Python Lectures*
(CC BY 4.0) [S39]. **Verified against SciPy 1.18.1** [S40], last re-run 2026-09-27. That is the installed
version; the documentation build cited is 1.18.0, which is the latest SciPy
publishes.

SciPy is a collection of subpackages on top of NumPy wrapping decades-old Fortran/C libraries (QUADPACK, ODEPACK, MINPACK, LAPACK, ARPACK, SuperLU, FFTPACK/pocketfft, FITPACK). Import subpackages explicitly: `from scipy import integrate` (importing `scipy` alone does not load them). Most routines accept array-likes and return either arrays or a *result object* with named fields (`res.x`, `res.success`, `sol.t`, `sol.y`).

## integrate

- `quad(f, a, b)`: adaptive Gauss-Kronrod (21-point) with error estimate, `(value, abserr)`. Infinite limits are mapped to finite ones; `points=` marks singularities; `epsabs/epsrel` set tolerances; `args=` passes parameters. `dblquad`, `tplquad`, `nquad` for higher dimensions (cost grows exponentially: use Monte Carlo or `qmc` beyond 3-4 D). `quad_gaussian` gets $\int e^{-x^2} = \sqrt\pi$ to $10^{-8}$.
- `trapezoid`, `simpson` for *tabulated* data: errors $O(h^2)$ and $O(h^4)$ (`trapezoid_vs_simpson`). `cumulative_trapezoid` for running integrals.
- `solve_ivp(fun, (t0, t1), y0, method="RK45", rtol, atol, t_eval, dense_output, events)`: initial value problems $y' = f(t, y)$ as first-order systems (rewrite $x'' = -\omega^2 x$ as $y = (x, v)$) [S15]. `RK45` (Dormand-Prince, explicit, adaptive step from the embedded error estimate; SciPy's page names the 1980 paper [S37] as its reference) for non-stiff; `Radau`, `BDF`, `LSODA` for stiff problems (explicit methods would need tiny steps for stability). `dense_output=True` gives a continuous interpolant `sol.sol(t)`; events find zero crossings. `solve_ivp_oscillator` reaches $10^{-8}$ error with `rtol=1e-8`. Legacy `odeint` (LSODA) has the argument order `f(y, t)`.

## optimize (summary; details in note 07)

`minimize` (local, many methods), `minimize_scalar`, `least_squares`/`curve_fit`, `root`/`brentq`/`newton`, `linprog`, `milp`, global methods `differential_evolution`, `basinhopping`, `shgo`, `dual_annealing`. `root_transcendental`: `brentq` needs a sign-changing bracket and always converges (superlinear); `newton` needs a good start and derivative (quadratic) and can diverge. `curve_fit_decay`: nonlinear least squares returning parameters and covariance $\to$ standard errors $\sqrt{\mathrm{diag}\,\Sigma}$.

## interpolate

- `interp1d(x, y, kind="linear"|"cubic")` — **legacy**. SciPy's own page states: *"This class is considered legacy and will no longer receive updates. While we currently have no plans to remove it, we recommend that new code uses more modern alternatives instead"* [S15]. It still works in 1.18 and emits no warning, so old code and old slides are full of it; write `np.interp` for linear and `CubicSpline`/`make_interp_spline` for everything else.
- `CubicSpline(x, y, bc_type="not-a-knot"|"natural"|"periodic")` (piecewise cubic, $C^2$, has `.derivative()`, `.integrate()`, `.roots()`), `PchipInterpolator` (shape-preserving, no overshoot), `Akima1DInterpolator`, `make_interp_spline` (B-splines, `k` degree), `UnivariateSpline(s=...)` (smoothing, not interpolating) [S15].
- Multidimensional: `RegularGridInterpolator` (grid), `griddata` and `RBFInterpolator` (scattered).
- Interpolation vs fitting: an interpolant passes through the data; a fit minimises a residual. High-degree global polynomial interpolation on equispaced nodes oscillates (Runge), splines do not: `interpolation_demo` gives errors spline 0.02 < linear 0.07 < degree-10 polynomial 1.9 for $1/(1+25x^2)$.

## sparse

Formats [S15]: **COO** (row, col, data triples; easy to build, duplicates summed on conversion), **CSR** (row pointer + column indices + data; fast row slicing, matvec, arithmetic), **CSC** (column version; what `spsolve`/SuperLU wants), **LIL/DOK** (incremental construction), `diags`/`spdiags` (banded), `kron`, `block_diag`. Build in COO/LIL, convert with `.tocsr()`; do *not* modify CSR structure in a loop. `A @ x`, `A.T`, `A.nnz`, `A.toarray()` (dense, only for small tests). Solvers in `scipy.sparse.linalg`: direct `spsolve` (SuperLU), `splu` (factor once, solve many), iterative `cg` (SPD), `gmres`, `bicgstab`, `minres`, with `LinearOperator` for matrix-free operators and preconditioners; eigenvalues `eigsh`/`eigs` (ARPACK, a few eigenpairs), `svds`. `poisson_solve` discretises $-u'' = f$ with the tridiagonal stencil ($3n - 2$ nonzeros) and checks `spsolve` against dense `solve`; the $O(h^2)$ discretisation error is visible in the test. Newer `csr_array` classes follow numpy semantics (`*` elementwise, `@` matmul) rather than the matrix-style `csr_matrix`.

## linalg

Superset of `numpy.linalg` with explicit decompositions: `lu`, `lu_factor`/`lu_solve`, `cholesky`, `cho_factor`/`cho_solve`, `qr`, `svd`, `schur`, `eig`/`eigh` with generalised problems `eigh(A, B)`, `solve(assume_a="pos"|"sym"|"her"|"gen")` picking the right LAPACK driver, `solve_triangular`, `solve_banded`, `solve_toeplitz`, matrix functions `expm`, `logm`, `sqrtm`, `funm`, `norm`, `null_space`, `orth`, `block_diag`, `circulant`, `hilbert`. `linalg_demo`: $PLU = A$, Cholesky solve, $\exp(\frac{\pi}{2} K)$ with $K$ the rotation generator gives a 90-degree rotation. Prefer factor-once/solve-many (`cho_factor` + `cho_solve`) inside loops; `expm` uses Pade approximation with scaling and squaring, not eigendecomposition.

## fft

`scipy.fft` (pocketfft; replaces `scipy.fftpack`): `fft`/`ifft`, `rfft`/`irfft` for real input (returns $n/2+1$ bins, half the work), `fft2`/`fftn`, `fftfreq`/`rfftfreq(n, d)` for the frequency axis, `fftshift`, `dct`/`dst`, `next_fast_len`, `workers=` for threads. Bin $k$ of an $n$-point transform with sample spacing $d$ is frequency $k/(n d)$; resolution is $f_s/n$, maximum $f_s/2$ (Nyquist). Definition [S15]: $X_k = \sum_j x_j e^{-2\pi i jk/n}$, unnormalised forward (`norm="backward"` default), so `ifft(fft(x)) == x`. `fft_peaks` recovers 50 and 120 Hz from a 1 kHz signal; `convolution_theorem` checks that linear convolution equals `irfft(rfft(a, m) * rfft(b, m))` with zero-padding to $m \ge 2n - 1$ (without padding you get *circular* convolution). Windowing (`scipy.signal.windows.hann`) reduces spectral leakage for non-periodic segments.

## stats

Distributions are objects (`norm`, `expon`, `poisson`, `binom`, `chi2`, `t`, `uniform`, ...) with `pdf/pmf`, `cdf`, `ppf` (inverse cdf, quantiles), `sf` (1 - cdf, accurate in tails), `rvs(size, random_state)`, `mean/var`, `fit` (MLE). Freezing: `stats.norm(loc=2, scale=0.5)` fixes parameters. Tests return `(statistic, pvalue)` objects: `ttest_ind`, `ttest_rel`, `ttest_1samp`, `kstest`, `shapiro`, `chisquare`, `pearsonr`, `spearmanr`, `mannwhitneyu`, `wilcoxon`. Descriptive: `describe`, `skew`, `kurtosis`, `sem`, `zscore`, `bootstrap`, `linregress`. `stats_demo` fits $\mathcal N(2, 0.5^2)$, rejects equal means for shifted samples ($p < 10^{-6}$), fails to reject normality with KS ($p > 0.01$), and shows `ppf(0.95) = 1.645`. Random state: pass a `Generator` as `random_state`.

## signal

Filter design and application: `butter`, `cheby1`, `ellip`, `bessel` with `output="sos"` (second-order sections: numerically robust; `(b, a)` transfer-function form is ill-conditioned above order ~8), `firwin` (FIR), `sosfilt` (causal), `sosfiltfilt`/`filtfilt` (zero-phase, forward-backward, doubles the order), `lfilter`. Analysis: `find_peaks(x, height, distance, prominence)`, `periodogram`, `welch` (averaged PSD), `spectrogram`, `stft`, `correlate`/`convolve`/`fftconvolve`, `resample`, `decimate`, `detrend`, `savgol_filter` (polynomial smoothing that also gives derivatives), `hilbert` (analytic signal, envelope), windows. `lowpass_demo`: 6th-order Butterworth at 40 Hz, `sosfiltfilt`, removes a 300 Hz component from a 20 Hz signal to $10^{-4}$ RMS; `find_peaks` counts the 20 peaks per second.

## Pitfalls

- Forgetting to pass `args=` and closing over globals instead; wrong argument order for `odeint` vs `solve_ivp`.
- Using explicit RK on stiff systems (extremely slow or unstable) and not noticing; `atol` too large for small-magnitude components.
- `quad` on discontinuous or oscillatory integrands without `points`/`limit`; integrating tabulated data with `quad` (use `trapezoid`).
- `interp1d` raises outside the data range unless `fill_value="extrapolate"`; extrapolating splines is meaningless. Reaching for `interp1d` at all, now that it is legacy [S15].
- Converting sparse matrices to dense (`toarray`) inside algorithms; solving sparse systems with `np.linalg.solve`.
- FFT without zero-padding when linear convolution is meant; interpreting bins beyond Nyquist; forgetting `rfftfreq`.
- `(b, a)` filter coefficients at high order; using `sosfilt` when zero phase is needed for offline analysis.
- p-values as "probability the hypothesis is true"; running `fit` on tiny samples; `std` with `ddof=0` (numpy) vs `ddof=1` (scipy.stats.sem, pandas).

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md). Numeric
answers re-computed in the venv against SciPy 1.18.1.

1. `solve_ivp` requires the ODE to be
   (a) linear (b) a first-order system $y' = f(t, y)$ (c) scalar (d) autonomous
   **b.** Higher-order equations are rewritten with auxiliary variables ($v = x'$).

2. Which sparse format should you convert to before repeated matrix-vector products and slicing rows?
   (a) COO (b) LIL (c) CSR (d) DOK
   **c.** COO/LIL/DOK are for construction; CSR stores row pointers for fast row access and matvec.

3. `rfft` of a real signal of length 1000 sampled at 500 Hz returns how many bins and up to which frequency?
   (a) 1000 bins, 500 Hz (b) 501 bins, 250 Hz (c) 500 bins, 250 Hz (d) 501 bins, 500 Hz
   **b.** Real input: $n/2 + 1$ bins, spacing $f_s/n = 0.5$ Hz, up to Nyquist $f_s/2$.

4. Which statement about `brentq` vs `newton` is correct?
   (a) Both need a bracket with a sign change. (b) `brentq` needs a bracket and is guaranteed to converge; `newton` needs a start point and may diverge. (c) `newton` cannot use a derivative. (d) `brentq` converges quadratically.
   **b.** Brent combines bisection with secant/inverse quadratic steps (superlinear, safe); Newton is quadratic but local.

5. `scipy.stats.norm(2, 0.5).ppf(0.975)` returns
   (a) the probability of 0.975 (b) about 2.98, the 97.5 % quantile (c) 1.96 (d) the density at 0.975
   **b.** `ppf` is the inverse CDF: $2 + 1.96 \cdot 0.5 = 2.98$; (c) would be the standard normal.
