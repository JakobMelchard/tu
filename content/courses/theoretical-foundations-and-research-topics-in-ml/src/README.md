# Reference implementations

Python only (the course uses Python for its coursework and project). Pure numpy/scipy implementations first; scikit-learn appears only inside tests as a cross-check. No datasets and no network: every module generates its own toy problem with a fixed seed. Each module runs as a script whose demo reproduces a bound numerically (empirical quantity over many resamples next to the theorem's value); `--png` on `concentration.py`, `regularisation.py`, `least_squares.py` and `deep_theory.py` additionally saves a figure into the current directory.

From the course folder, with the repo's Python environment:

```
python -m pytest src/py -q   # 105 tests, ~8 s
python src/py/vc.py          # any module
```

Every module docstring names the note and the theorems it implements.

| Module | Note | Implements | Demo reproduces | Test anchors |
|---|---|---|---|---|
| `py/framework.py` | 01 | `ThresholdProblem` (closed-form risk $\eta+(1-2\eta)\lvert t-\theta\rvert$, Prop. 1.5), losses, `empirical_risk`, `erm_finite`, vectorised `threshold_empirical_risks`, memoriser | Thm 1.3(b): $\mathbb E L_S(h_S)\le\min_H L_{\mathcal D}\le\mathbb E L_{\mathcal D}(h_S)$ over 200 resamples per $n$; Thm 1.4 | closed-form risk vs MC; memoriser $L_{\mathcal D}=P(y=+1)$ |
| `py/concentration.py` | 02 | `hoeffding_bound`, `binomial_tail_exact`, `union_bound_experiment`, `sample_complexity_finite`, `epsilon_from_n`, `uniform_deviation_finite` | Thm 2.4 (observed vs exact vs Hoeffding); Thm 2.6: 95 % quantile of $\sup_{H_k}\lvert L_S-L_{\mathcal D}\rvert$ vs $\varepsilon(n)$ | exact binomial tail $0.0569$; sample sizes 199 / 2120 |
| `py/pac.py` | 03 | sample complexities (finite, VC), consistent / ERM / largest-negative threshold learners, `estimate_failure_probability`, `threshold_failure_exact` | $P(\text{excess}>\varepsilon)\le\delta$ at the bound's $n$; MC vs exact $(1-\varepsilon)^n$ vs $e^{-\varepsilon n}$ | exact $(1-\varepsilon)^n$; ERM vs brute force |
| `py/vc.py` | 04 | labelings of thresholds, intervals, rectangles, halfspaces (LP), `is_shattered`, `growth_function`, `vc_dimension_estimate`, `sauer_bound`, `threshold_sup_deviation`, Thm 4.10 / 4.12 bounds | VCdim $1,2,4,3$, $\tau$ vs Sauer; exact $\sup_t$ gap over all thresholds vs Thm 4.10 (expectation, McDiarmid) and Thm 4.12 | $\tau_{\mathrm{int}}(n)=\binom n2+n+1$, $\tau_{\mathrm{thr}}(n)=n+1$; exact sup vs dense grid; 0.164 |
| `py/rademacher.py` | 05 | MC and exact ($2^n$ enumeration) $\mathfrak R_S$, $O(n)$ threshold $\mathfrak R_S$, linear class, Massart, VC bound, `rademacher_bound_experiment` | Thm 5.3 over 500 resamples; Thm 5.7 dimension-free $BR/\sqrt n$ | exact $3/4$; orthonormal points attain $B/\sqrt n$ |
| `py/srm.py` | 06 | **new.** Nested dyadic threshold classes, weights $6/(\pi^2k^2)$, `srm_threshold_select`, `srm_experiment` | Thms 6.1, 6.2 failure frequencies $\le\delta$; selected $k$ grows with $n$; SRM vs ERM | Basel tail; exact class on a dyadic target |
| `py/regularisation.py` | 06 | polynomial U-curve, heuristic `srm_select`, `validation_select`, `tikhonov`, `rlm_logistic` (Newton), `stability_experiment`, `validation_experiment` | Thm 6.7 replace-one change vs $2\rho^2/(\lambda n)$; Thm 6.6 identity; Thm 6.9(a) | sklearn `Ridge` ($\alpha=n\lambda$), `LogisticRegression` ($C=1/(2n\lambda)$) |
| `py/least_squares.py` | 07 | `ols`, `hat_matrix`, `ridge` primal/dual, `effective_dof`, `bias_variance_simulation`, `kernel_ridge`, fixed- and random-design risks, `ridge_risk_exact` / `_bound` / `_mc` | Thm 7.3(c) $\sigma^2d$; Gaussian design $\sigma^2d/(n-d-1)$; Thm 7.9(c) exact vs bound | sklearn `LinearRegression`, `Ridge`, `KernelRidge` |
| `py/kernels.py` | 08 | linear, polynomial, RBF, Laplacian, sigmoid (non-PSD), `is_psd`, explicit quadratic map, `representer_demo`, `kernel_rademacher_mc` / `_bound` | PSD checks; representer theorem; $\mathfrak R_S$ of the RKHS ball vs $B\sqrt{\mathrm{tr}K}/n$ | sklearn pairwise kernels; $K=cI$ closed form |
| `py/svm.py` | 09 | dual SVM (SLSQP), kernel `SVM`, `leave_one_out_error`, `perceptron`, `make_margin_data` | 4-point worked example; Thm 9.6 LOO vs $N_{SV}/(n+1)$; Thm 9.9 mistakes vs $(R/\gamma)^2$ | sklearn `SVC` (linear, RBF); two-point perceptron |
| `py/deep_theory.py` | 10 | `MLP` (hand-written backprop, Adam), `hat_network`, random ReLU features, `min_norm_least_squares`, `gd_least_squares`, `ridgeless_risk`, `min_norm_risk_simulation`, `double_descent_curve` | Thm 10.1 widths; Thm 10.8 MC vs formula on both branches; double descent | finite differences; sklearn `LinearRegression` min-norm; $\sigma^2p/(n-p-1)$ |

### Textbook verification: `py/test_textbook_*.py`

18 tests that exist for a different reason from the rest: not to check the
modules, but to catch a **misremembered constant in the notes**: a wrong sign, a
stray factor of two, a `log` that should be `log log`, an exponent inside a
square root instead of outside. Each hard-codes the expression as the source
states it and compares it with an independently computed quantity; each docstring
names its locator in [`../refs/SOURCES.md`](../refs/SOURCES.md).

Split along the notes' own seam, which is also where the errors fell: notes 01–09
came through source verification clean, and **every** factual error found was in
note 10, whose claims rest on research papers rather than the two textbooks.

| file | notes | tests |
|---|---|---|
| [`py/test_textbook_vc_theory.py`](py/test_textbook_vc_theory.py) | 02–04 | 8 |
| [`py/test_textbook_algorithm_bounds.py`](py/test_textbook_algorithm_bounds.py) | 05–09 | 8 |
| [`py/test_textbook_deep_theory.py`](py/test_textbook_deep_theory.py) | 10 | 2 |

**`test_textbook_vc_theory.py`**: concentration, PAC sample complexity, VC.

| test | source | what would be caught |
|---|---|---|
| `hoeffding_dominates_exact_binomial_tail` | S9 Lemma 4.5 | a wrong exponent in $2e^{-2n\varepsilon^2}$; compared against the exact binomial tail |
| `finite_class_sample_complexities_match_the_two_theorems` | S9 Cor. 4.6, Cor. 2.3 | swapping $2|\mathcal H|$ for $|\mathcal H|$, or $\varepsilon^{-2}$ for $\varepsilon^{-1}$ |
| `no_free_lunch_reverse_markov_constants` | S9 Thm 5.1 | the $1/4 \to 1/8, 1/7$ step |
| `sauer_shelah_holds_and_is_tight_for_intervals` | S9 Lemma 6.10 | the growth function, by brute-force enumeration; tightness for intervals and thresholds |
| `polynomial_form_of_sauer_valid_exactly_for_n_ge_d` | S10 Cor. 3.18 | the hypothesis $n\ge d$, and that it genuinely fails below $d$ |
| `vc_dimensions_of_the_standard_classes` | S9 §6.3, §9.1.3 | $1,2,4,k+1$ |
| `fundamental_theorem_realisable_upper_bound_carries_the_log_one_over_eps` | S9 Thm 6.8 | **the realisable/agnostic asymmetry**, the most misquoted part of the theorem |
| `vc_generalisation_bound_worked_numbers` | S10 Cor. 3.19 | note 04's numbers, in both the Vapnik-style and FoML forms |

**`test_textbook_algorithm_bounds.py`**: Rademacher complexity and what specific
algorithms guarantee.

| test | source | what would be caught |
|---|---|---|
| `massart_bound_dominates_exact_rademacher_complexity` | S10 Thm 3.7 | a factor of two, against $\mathfrak R_S$ computed by enumerating all $2^n$ sign vectors |
| `threshold_class_on_two_points_...three_quarters` | note 05 | the worked value $3/4$, exactly and by Monte Carlo |
| `linear_class_rademacher_exact_bound_and_jensen_gap` | S10 Thm 5.10 | $BR/\sqrt n$ vs $BR/n$; both limiting geometries |
| `rlm_stability_rate_and_its_optimal_lambda` | S9 Cor. 13.6, 13.9 | that $\sqrt{8\rho^2B^2/n}$ really is the minimum of $\lambda B^2+2\rho^2/(\lambda n)$ |
| `ridge_bias_bound_lambda_over_four` | note 07 Thm 7.9(c) | the constant $1/4$, and that it is **attained**, so $\lambda/2$ would fail |
| `ols_in_sample_excess_risk_is_sigma_squared_d` | note 07 Thm 7.3(c) | $\sigma^2d$, by simulation |
| `svm_worked_example_matches_the_hand_computation` | note 09 | $w^*=(\tfrac12,\tfrac12)$, $b=0$, $\gamma=\sqrt2$, $\alpha=\tfrac14$, strong duality |
| `leave_one_out_support_vector_bound_is_respected` | S10 Thm 5.4 | that every leave-one-out mistake is a support vector |

**`test_textbook_deep_theory.py`**: note 10.

| test | source | what would be caught |
|---|---|---|
| `ridgeless_risk_formula_and_where_its_global_minimum_lies` | S36 Thm 1 | both branches, **and that the global minimum is underparameterised at every SNR**; this is the error the pass found in note 10 |
| `min_norm_interpolator_risk_tracks_the_asymptotic_formula` | S36 Thm 1 | the $\gamma>1$ branch by simulation |

**No `exercises/` directory.** The conventions ask for one per past exercise
sheet. This course publishes none; assignments live in TUWEL, which needs a
login. Rather than invent exercises and label them with a term, the slot is taken
by the tests above, which reproduce *published* results. See
`../notes/CHANGELOG.md`.

### Module tests

`py/test_<module>.py`, 87 tests. Each module has at least one test against a closed form (risk of thresholds, $(1-\varepsilon)^n$, $\tau_{\mathrm{int}}(n)=\binom n2+n+1$, $\sigma^2d$, $\sigma^2d/(n-d-1)$, the 4-point SVM, the two-point Rademacher value $3/4$, the Basel sum) and, where a library implements the same thing, a scikit-learn cross-check (`Ridge`, `LinearRegression`, `KernelRidge`, `LogisticRegression`, `SVC`, pairwise kernels). Bounds are tested as "fails on at most a $\delta$ fraction of resamples".
