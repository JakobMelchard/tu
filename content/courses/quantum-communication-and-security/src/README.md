# Reference implementations

Python only (numpy, scipy). **Toy crypto:** every module is a teaching model of a QKD step, labelled as such in its docstring; none is a usable QKD or cryptographic implementation. No network and no data files: every module generates its own inputs with a fixed seed. Each module runs as a script whose demo prints the numbers quoted in the notes; each test checks against a closed form, an exact enumeration, or a number published in a cited paper. No plots (the notes' tables are the output); nothing needs `--png`.

From the course folder, with the repo's Python environment:

```
python -m pytest src -q        # 67 tests, ~1 s
python src/py/decoy.py         # any module's demo
```

Every module docstring names its note and the equations it implements, with `[S<n>]` locators into [`../refs/SOURCES.md`](../refs/SOURCES.md).

| Module | Note | Implements | Demo reproduces | Test anchors |
|---|---|---|---|---|
| `py/bb84.py` | 02 | `simulate` (Born-rule BB84 with intercept-resend in random or fixed basis and depolarising noise), `sift`, `qber`, `qber_analytic`, `eve_information`, `estimate_qber`, `serfling_tail`, `sampling_deviation_mc` | sift 0.5; QBER 0.25 / 0.10 / 0.05 / 0.14 vs analytic; $I(A{:}E)=2e$; biased Eve $e_Z=0$, $e_X=\tfrac12$ | analytic QBER within $5\sigma$; Serfling bound ≥ Monte Carlo |
| `py/entropies.py` | 03 | Shannon, $h$, von Neumann, partial trace, conditional/mutual, Holevo, $H_{\min}$/$H_{\max}$, classical conditional $H_{\min}$, smooth $H_{\min}$ (water level), Helstrom, $H_{\min}$ of pure states, Bell-diagonal states, purification, `h_z_given_e`, `uncertainty_sum` | $H(Z\mid E)$ vs $\lambda_{\Psi^-}$ with minimum $1-2h(e)$; uncertainty relation ≥ 1 on random states | closed form $1-H(\lambda)+h(\lambda_1+\lambda_2)$; $H_{\min}(A\mid B)_{\Phi^+}=-1$; chain rule on random distributions |
| `py/reconciliation.py` | 04 | `binary`, simplified `cascade` (with the cascade step), `hamming_reconcile`, `verify_hash`, `shannon_leak`, `efficiency` | Cascade $f=1.10$-$1.18$ for $e=1$-$8\%$, no residual errors; Hamming leaks 3/7 | all errors corrected; $1<f<1.4$; hash collisions $2^{-t}$ |
| `py/privacy_amplification.py` | 04 | `toeplitz`, `toeplitz_hash`, `collision_probability` (exhaustive), `lhl_bound`, `key_length`, `distance_flat_source`, `distance_with_prefix_leak` | exact distance from uniform vs $\frac12 2^{-(H_{\min}-\ell)/2}$; $\ell>H_{\min}$ fails | two-universality exactly $2^{-\ell}$; bound holds exactly; distance ≥ $1-2^{k-\ell}$ |
| `py/key_rates.py` | 05 | `shor_preskill`, `sp_threshold`, `devetak_winter_bell_diagonal`, `holevo_eve`, `devetak_winter_bb84_min`, `decoy_rate_curve`, `single_photon_rate`, `finite_key_length`, `finite_key_errors` | $e^*=11.0028\%$; DW minimum at $\lambda_4=e^2$ equals $1-2h(e)$; decoy rate vs $L$; $\ell/m$ table ($\varepsilon=10^{-10}$) | $\chi(Z{:}E)=h(e)$; finite key monotone, below $1-2.1h(\delta)$, $\varepsilon$-secure |
| `py/decoy.py` | 06 | `Channel` (GYS model), `vacuum_weak_bounds`, `two_decoy_bounds`, `rate_decoy`, `rate_gllp_no_decoy`, `best_mu`, `max_distance`, `mu_optimal_small_eta`, `relative_deviations`, `pns_attack_gains` | 142.01 km / 140.62 km (paper 142.05 / 140.55); $\beta$ 3.5 % / 16.8 %; no-decoy 40 km; PNS exposed | [S9] distances ±0.3 km, deviations ±0.2 pp, $\mu_{\rm opt}=0.48$; bounds bracket true $Y_1$, $e_1$ |
| `py/mdi_qkd.py` | 06 | `single_photon_bsm` (two-photon Fock model with loss, dark counts), `y11_e11`, `coherent_bsm`, `gain_qber` (phase-averaged WCPs), Ma-Razavi closed forms `mr_y11`, `mr_e11`, `mr_rect`, `mr_diag`, `key_rate`, `rate_curve` | ideal BSM table (Z: only unequal bits succeed; X: $\psi^+$ correlated, $\psi^-$ anticorrelated); rate vs $L$, cutoff 232 km | first-principles models = [S11] closed forms to $10^{-9}$; rate > 0 at 200 km; rate ∝ total transmittance |

Module dependencies: `reconciliation`, `key_rates`, `decoy`, `mdi_qkd` import `h2` from `entropies`; `key_rates` and `mdi_qkd` import `best_mu`, `max_distance` from `decoy`. Tests import modules by bare name (pytest's default `prepend` import mode puts `src/py` on the path).

**Name collision caveat.** If the sibling course `../../quantum-information-theory-i/src/py` also has a module `entropies.py` or a test file `test_entropies.py`, run the two suites separately (`pytest <course>/src`), not in one pytest invocation: identical basenames without packages collide.
