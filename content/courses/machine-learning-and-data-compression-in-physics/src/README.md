# Reference implementations

Python only (the course's tools are Python: sparse-ir [S14], the 138.128 notebooks [S6]).
numpy/scipy first, torch for the neural models, scikit-learn only inside tests as a
cross-check. No datasets and no network: every module generates its data with a
fixed seed (Ising snapshots by Metropolis, Green's functions from closed forms,
spectra from Gaussians). Every module runs as a script whose demo produces the
numbers quoted in the notes.

From the course folder, with the repo's Python environment:

```sh
python -m pytest src -q   # 67 passed, 1 skipped, ~10 s
cd src/py
python ir_toy.py          # any module; all demos together ~20 s
```

The skipped test compares `ir_toy` against sparse-ir and runs only if
`sparse_ir` is installed (`uv pip install sparse-ir`; not a repo dependency).

| module | note | implements | demo shows | test anchors |
|---|---|---|---|---|
| `py/lowrank.py` | 02 | truncated SVD, Eckart-Young error, `rank_for_tolerance`, `noise_threshold_rank`, PCA, `range_finder`, `randomized_svd` | error vs rank for an analytic kernel, clean and noisy; denoising optimum at the noise edge | sklearn `PCA`; Eckart-Young equalities; HMT Thm 10.5 [S18] over 200 draws |
| `py/ir_toy.py` | 03 | logistic kernel, graded Gauss-Legendre SVE, `IRBasis` (`u`, `v`, `uhat`, sampling points by roots or extrema, `fit`, `project`), `single_pole` | $L(\Lambda)$; single pole from 26 $\tau$ / 28 Matsubara samples to $10^{-8}$; IR vs uniform grid | closed-form single pole in $\tau$ and $i\nu$; orthonormality; parity; $\hat u$ = FT of $u$; sparse-ir (optional) |
| `py/autoencoder_compression.py` | 04 | `LinearAE`, `MLPAE`, `VAE`, `train`, `quantise`, `compare`, `compare_poles` | AE vs PCA on Ising (PCA wins) and on single-pole $G$ (AE wins 100x); rate via quantisation; VAE $\beta$ sweep | linear AE = PCA; PC1 = magnetisation; quantiser $\Delta^2/12$ |
| `py/tt_svd.py` | 05 | `tt_svd` (max rank / rel. tolerance), `tt_to_full`, Schmidt values, entropy, `tfim_ground_state`, `ghz`, `quantics` | error vs bond dimension: TFIM ($g=0.5,1$) vs random state; quantics ranks of exp, sin, polynomial, Gaussian | error = RSS of discarded weights; per-cut Eckart-Young lower bound; ED energy; ranks 1, 2, $\le p+1$ |
| `py/continuation.py` | 06 | kernel matrix, `tikhonov`, `maxent` (Newton on the convex dual), `discrepancy_alpha`, `LearnedLinearInverse`, `noise_band` | Tikhonov vs MaxEnt at three noise levels; learned linear inverse; bias vs variance of the noise band | normal equations; MaxEnt stationarity; $\chi^2/N\approx1$; positivity; peaks within 0.2 |
| `py/observables.py` | 07 | `ridge`, `kernel_ridge` (poly-2), `logistic_newton`, `MLPClassifier`, `estimate_tc` | test $R^2$ of $e$, $m^2$ by feature choice; phase accuracy; $T_c$ from the crossing | sklearn `Ridge`, `KernelRidge`; symmetry obstruction; $\lvert T^*-T_c\rvert<0.25$ |
| `py/ising_snapshots.py` | 04, 07 | checkerboard Metropolis, energy, magnetisation, bond features, Onsager/Yang | MC vs exact $\langle\lvert m\rvert\rangle$, $\langle e\rangle$ | $u(T_c)=-\sqrt2$; MC within 0.02-0.03 of exact |
| `py/error_bars.py` | 08 | `mean_sem`, `binning_error`, `binning_curve`, `ar1`, `tau_int_ar1`, `bootstrap` | binning plateau of an AR(1) series at $\sqrt{2\tau_{\rm int}}\times$ the naive error | exact AR(1) $\tau_{\rm int}$; bootstrap = SEM |

Every module docstring names its note and the source it implements. Sources:
[`../refs/SOURCES.md`](../refs/SOURCES.md).
