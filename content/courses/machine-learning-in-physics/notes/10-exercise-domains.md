# 10 The three exercise domains named on TISS

TISS: "In the exercises, you will then apply these methods to problems from
physics, e.g. temperature deblurring of spectral functions, classification of
proton collisions in the LHC, recognizing magnetic phases in the Ising model"
[S2]. The public 2021S notebooks [S5] show what each looked like then: Ex07
(deblurring), Ex08-09 (SUSY collisions), Ex10-11 (Ising). The 2027S notebooks
live on JupyterHub and are unseen. Our versions generate all data in code.

## A. Magnetic phases of the 2D Ising model

**Physics.** $H=-J\sum_{\langle ij\rangle}\sigma_i\sigma_j$, $J=1$, periodic $L\times L$.
Onsager: $T_c=2/\ln(1+\sqrt2)=2.2692$ [S18]. Order parameter $m=\frac1{L^2}\sum_i\sigma_i$;
$\mathbb Z_2$ symmetry $\sigma\to-\sigma$. Finite $L$: no true transition, $\langle m\rangle=0$
exactly; use $\langle|m|\rangle$, and crossings of the Binder cumulant
$U_L=1-\frac{\langle m^4\rangle}{3\langle m^2\rangle^2}$ ($\to2/3$ ordered, $\to0$
disordered) [S19].

**Data by Metropolis** [S20]. Propose a flip at $i$, $\Delta E=2\sigma_ih_i$,
$h_i=\sum_{j\sim i}\sigma_j$; accept with $\min(1,e^{-\beta\Delta E})$; detailed balance
$\Rightarrow$ Boltzmann stationary distribution. Checkerboard: all sites of one
colour have no same-colour neighbours, so they update simultaneously
(vectorised over sites, temperatures and chains). Thermalise (500 sweeps), then
sample every 10 sweeps; near $T_c$ the autocorrelation time grows like $L^{z}$,
$z\approx2.2$ (critical slowing down), so samples there are correlated. Low-$T$
chains never tunnel between $\pm m$ at $L=16$; we apply random global flips to
restore the symmetry, as an ergodic sampler would. Mehta et al.'s data set: $L=40$,
16 temperatures $\times10^4$ samples [S6 app. A]; ours: $L=16$, 26 temperatures
$1.0..3.5$ $\times200$.

**Check against exact enumeration** ($L=4$, all $2^{16}$ states, $T=2.5$):
$\langle E\rangle/N=-1.3791$, $\langle|m|\rangle=0.7647$; Metropolis $-1.386$, $0.767$.

**Unsupervised: PCA** [S16]. PC1 $=\mathbf 1/L$ exactly ($|\langle w_1,\mathbf 1/L\rangle|=1.000$),
explains $52\,\%$ of the variance (PC2 $1.5\,\%$); $|$score$|\propto|m|$
(corr $0.9999$). Variance of $|$score$|$ per $T$ peaks at $2.4$: $T_c(L=16)$,
shifted up by finite size. Rank-1 error per $T$: $0.17$ at $T=1.5$, $0.98$ at $3.0$ (note 07).

**Supervised** [S15, S6 sec. VII.C.1]. Labels: ordered $T<2.0$, disordered $T>2.5$;
the critical region is excluded from training, then the classifier is applied at
all $T$ and $T_c$ read off where $\bar p(\text{ordered})=\tfrac12$:

| classifier | test accuracy | $T$ at $\bar p=\tfrac12$ |
|---|---|---|
| logistic, raw spins | 0.648 | 2.56 |
| logistic, $(|m|,m^2,E/N)$ | 0.999 | 2.29 |
| MLP, 16 hidden ReLU, raw spins | 0.988 | 2.32 |

Why raw logistic fails: $p=\sigma(w^T\sigma+b)$ is monotone in $w^T\sigma$; with
$\pm$ ordered states in one class and $m\approx0$ in the other, no linear $w$
separates them ($w=\mathbf 1$ would call $m=-1$ disordered). One hidden layer
learns $|m|$ ($\mathrm{ReLU}(m)+\mathrm{ReLU}(-m)$). Mehta et al.'s logistic
regression on this task also stays near 0.7 accuracy (their Fig. 21) [S6 sec. VII.C.1];
the symmetry explanation is ours. Their MIT-licensed notebooks NB6 (logistic, Ising)
and NB5 (logistic, SUSY) are runnable companions, but download the full data [S14].
Exercise 10 does the unsupervised version with k-means on $(m,m')$ and
$(|m|,|m'|)$ (note 06); exercise 11 the low-rank version (note 07) [S5].

**Binder crossing** ($L=8$ vs $16$, 16 chains $\times100$ samples per $T$): $2.24$
(seed-to-seed $2.24$-$2.30$), versus $T_c=2.269$.

## B. Classifying proton collisions (SUSY)

**Physics and data.** Baldi, Sadowski, Whiteson [S17]: simulated LHC events,
signal = a SUSY process with charged leptons and invisible neutralinos, background
= Standard Model processes with the same visible final state; 8 low-level
kinematic variables plus 10 physicist-designed high-level ones, $5\times10^6$
events. Exercise 08: `SGDClassifier` with logistic loss and early stopping;
confusion matrix, accuracy, sensitivity, specificity; which features fail.
Exercise 09: `MLPClassifier`, $3\times3$ hyperparameter grid, and the conclusion
that 80 % accuracy is hard to beat [S5].

**Our toy** (`collisions.make_events`, **not physics**): $p_T$ of two leptons
(harder for signal), MET (larger for signal), $\Delta\phi$, $\eta_1,\eta_2$ with
identical marginals but correlated in signal, $\phi_1$ pure noise; 30 % signal.

| model | AUC | acc. | sens. | spec. | TPR at FPR 1 % |
|---|---|---|---|---|---|
| always background | 0.5 | 0.697 | 0 | 1 | |
| logistic, raw | 0.759 | 0.745 | 0.333 | 0.924 | 0.082 |
| logistic, engineered ($\log p_T$, $|\eta_1-\eta_2|$, MET$/\sum p_T$) | 0.878 | 0.807 | 0.641 | 0.880 | 0.152 |
| MLP 32-32, raw | 0.895 | 0.822 | 0.680 | 0.883 | 0.207 |

Raw logistic weights: $\eta_1,\eta_2$ get $0.02$ (useless linearly), MET $0.81$.
The engineered $|\eta_1-\eta_2|$ recovers most of the MLP's gain: that is what
the high-level SUSY features are.

**ROC and AUC.** Sweep the threshold $c$ on a score $s$:
$\mathrm{TPR}(c)=P(s>c|\text{sig})$, $\mathrm{FPR}(c)=P(s>c|\text{bkg})$.
$\mathrm{AUC}=\int\mathrm{TPR}\,d\mathrm{FPR}=P(s_\text{sig}>s_\text{bkg})$ (+ ties/2): the
Mann-Whitney statistic, invariant under monotone maps of $s$, independent of class
balance. For a search, the relevant point is TPR at a tiny FPR (background
rejection), not accuracy.

## C. Temperature deblurring of spectral functions

Full derivation in note 03. Summary: $A_T=K_T*A+e$ is a first-kind
Fredholm problem; discretised it is least squares with an ill-conditioned design
matrix. Naive inversion amplifies the noise without bound; Tikhonov, truncated
SVD, early-stopped GD and smoothness or positivity priors all regularise it.
Exercise 07 [S5] covers this domain. Wallerberger's research on analytic
continuation and sparse-ir [S23] is the natural extension: same SVD, harsher
kernel.

## Pitfalls across the domains

- Ising: training on the critical region makes labels ambiguous; correlated
  Metropolis samples inflate test accuracy if train and test come from the same
  chain segment; finite-size $T_c(L)\ne T_c$.
- SUSY: accuracy with 30-50 % signal hides the physics; compare ROC curves; keep
  the test set untouched by feature engineering choices.
- Deblurring: never judge by residual; enforce known constraints.

## Test-style questions

**Q1.** Why does logistic regression on raw Ising spins fail to separate phases,
and give two fixes?
**A.** Its score is linear in $\sigma$; the ordered class contains $m\approx\pm1$
symmetric about the disordered $m\approx0$. Fix: symmetric features ($|m|$, $m^2$,
energy) or a hidden layer.

**Q2.** What does PCA find in Ising configurations and how would you estimate $T_c$ from it?
**A.** PC1 $=$ uniform vector, score $\propto m$. Plot $\langle|\text{score}|\rangle$ or its
variance vs $T$; the drop / peak locates $T_c(L)$; repeat for several $L$ to extrapolate.

**Q3.** Show AUC $=P(s_\text{sig}>s_\text{bkg})$.
**A.** $\mathrm{AUC}=\int_{-\infty}^{\infty}\mathrm{TPR}(c)\,(-d\,\mathrm{FPR}(c))=\int P(s_\text{sig}>c)\,p_\text{bkg}(c)\,dc=P(s_\text{sig}>s_\text{bkg})$
for independent draws.

**Q4.** Your SUSY classifier has sensitivity < specificity. What does that mean?
**A.** It misses more signal than it misclassifies background; at threshold $1/2$
with signal the minority, the classifier leans to "background". Lower the
threshold if signal efficiency matters.

**Q5.** Metropolis at $T=1.5$, $L=16$ from a cold start gives only $m>0$. Is that
wrong, and how does it affect ML?
**A.** Not wrong dynamically (tunnelling time is astronomically long) but not
ergodic. A classifier trained on it learns "$m>0$ is ordered", fails on $m<0$;
symmetrise the data (global flips) or the features.

## Code

`src/py/ising.py` (`metropolis`, `exact_small`, `binder`, `random_global_flip`,
`dataset`, `pca_tc`, `supervised_tc`,
`binder_crossing`), `src/py/collisions.py` (`make_events`, `engineered`,
`roc_curve`, `auc`, `auc_mann_whitney`, `tpr_at_fpr`, `fit_all`). Tests assert: exact $L=4$ agreement,
PC1 uniformity, raw-logistic accuracy $<0.8<0.97<$ symmetric-feature accuracy,
$|T_c^\text{est}-T_c|<0.2$ (classifiers) and $<0.1$ (Binder); AUC equal to
`sklearn.metrics.roc_auc_score` to $10^{-12}$.
