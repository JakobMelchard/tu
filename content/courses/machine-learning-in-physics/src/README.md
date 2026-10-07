# Reference implementations

Python only: the course's exercises are Python notebooks on JupyterHub [S1, S5].
Pure numpy/scipy first; scikit-learn and torch appear as cross-checks in tests, as
the tool itself where the course uses it (sklearn `MLPClassifier`, as in exercise
09 [S5]), and for the non-linear autoencoder. No network and no data files: every
module generates its data with a fixed seed (Ising configurations by Metropolis,
synthetic collision features). Notes 01-03 (optimisation, regularisation, SVD)
have no reference code here, because the course's graded weekly exercises
implement exactly those methods.

From the course folder, with the repo's Python environment:

```
python -m pytest src -q          # 43 tests, about 15 s
python src/py/ising.py           # any module: runs its demo
```

Every module docstring names its note and sources. Demo outputs are quoted in the
notes; rerunning reproduces them exactly (seeded).

| module | note | implements | demo shows | test anchors |
|---|---|---|---|---|
| `py/classification.py` | 04 | `sigmoid`, `bce`, `bce_grad`, `logistic_newton` (IRLS), `logistic_gd`, `softmax_fit`, `rbf_features`, `confusion` | Gaussian blobs vs Bayes boundary; XOR linear 0.54 vs RBF 0.98; 3-class softmax | `LogisticRegression(C=1/lam)` to $10^{-6}$; finite-difference gradients; separable-data divergence; 2-class softmax = logistic |
| `py/nn_numpy.py` | 05 | `MLP` (forward, backward), `numerical_grad`, `grad_check`, `train` (SGD/Adam, early stopping) | gradient check $<10^{-8}$; XOR; width 2/8/32 on $\sin2x+0.3x$ | backprop vs central differences for 3 activations x 2 losses; XOR needs a hidden layer; early stopping restores the best epoch |
| `py/clustering_pca.py` | 06, 07 | `kmeans` (Lloyd, k-means++), `gmm_em`, `pca`, `pca_eig`, `explained_variance_ratio`, `truncated_svd`, `subspace_distance` | inertia elbow; elongated clusters k-means 0.505 vs GMM 0.998; explained variance | `sklearn` `KMeans` (same init), `GaussianMixture.score`, `PCA`; monotone $J$ and log-likelihood; Eckart-Young |
| `py/autoencoder.py` | 08 | `linear_ae_numpy`, torch `AE`, `train_ae` (plain and denoising), `curve_data` | linear AE hits the Eckart-Young optimum, spans the PCA subspace; arc: AE $r=1$ 0.002 vs PCA $r=1$ 0.307; denoising 0.135 to 0.023 | principal angle $<10^{-3}$; AE $<0.1\times$ PCA; denoised $<0.4\times$ noisy |
| `py/qlearning.py` | 09 | `DoubleWell` MDP, `value_iteration`, `q_learning` ($\varepsilon$-greedy, $\eta=n^{-0.6}$), `greedy_policy`, `rollout` | $\gamma$ decides whether the agent leaves the metastable well; $\|Q-Q^*\|_\infty=0.027$ | Bellman residual $<10^{-9}$; stays for $\gamma\le0.85$, crosses at $0.95$; learned policy = optimal (also with slip) |
| `py/ising.py` | 07, 10 | checkerboard `metropolis`, `exact_small` ($2^{16}$ states), `binder`, `random_global_flip`, `dataset`, `pca_tc`, `supervised_tc`, `binder_crossing` | exact vs Metropolis at $L=4$; $\langle|m|\rangle(T)$; PC1 = magnetisation; three classifiers and their $T_c$; Binder crossing 2.24 | $T_c=2.269185$; exact $L=4$ within 0.02; PC1 uniform; raw logistic $<0.8$, symmetric features $>0.97$; $|T_c^\text{est}-T_c|<0.2$; Binder $<0.1$ |
| `py/collisions.py` | 10 | `make_events` (toy, not physics), `engineered`, `roc_curve`, `auc`, `auc_mann_whitney`, `tpr_at_fpr`, `fit_all` | AUC/accuracy/sensitivity/specificity for raw logistic, engineered logistic, MLP | AUC and ROC equal to `sklearn.metrics` to $10^{-12}$ (with ties); monotone invariance; useless features at AUC 0.5; model ranking |

## Runtime and determinism

Seeds are fixed everywhere (`numpy.random.default_rng`, `torch.manual_seed`,
`torch.set_num_threads(1)`). The slowest tests: Binder crossing (about 3 s),
Q-learning with slip (2 s), non-linear autoencoder (2 s). The Ising results were
checked for three further seeds: Binder crossing 2.27-2.30, classifier $T_c$
2.29-2.33, raw-logistic accuracy 0.63-0.65.

## Not implemented, and why

- **CartPole (exercise 12)**: needs `gymnasium`, not installed in the venv and
  not needed to learn tabular Q-learning; the double well replaces it.
- **The real SUSY and Ising data sets** [S17, S6 app. A]: downloads are excluded
  by the repo conventions; `collisions.make_events` and `ising.dataset` stand in.
- No `exercises/` directory: the course's own notebooks are public [S5] but carry
  no licence, so they are mapped in
  [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md), not copied.
