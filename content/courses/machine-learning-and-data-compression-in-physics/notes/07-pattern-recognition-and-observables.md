# 07 Pattern recognition and prediction of observables

TISS names "pattern recognition and the prediction of observables" as project
themes next to compression [S2]; Mehta et al. [S17], on the 138.128 list [S4], build
their notebooks on Ising-model data too. The physics content of such a project is almost
always the same lesson: **the symmetry and locality of the Hamiltonian decide
which features and models can work**, and the right features beat a bigger model.

Code: [`../src/py/observables.py`](../src/py/observables.py),
data from [`../src/py/ising_snapshots.py`](../src/py/ising_snapshots.py).

## 1 Setting and definitions

2D Ising, $H=-\sum_{\langle ij\rangle}s_is_j$, $L\times L$ periodic, $N=L^2$,
$T_c=2/\ln(1+\sqrt2)=2.2692$. Snapshots by checkerboard Metropolis, one
independent chain per snapshot (`sample_ising`), checked against Onsager/Yang [S20]
($\langle\lvert m\rvert\rangle$, $\langle e\rangle$ within 0.02 away from $T_c$ at $L=16$).
Observables: $e=-\frac1N\sum_{\langle ij\rangle}s_is_j$, $m=\frac1N\sum_is_i$.

- **Coefficient of determination** on held-out data
  $R^2=1-\sum(y-\hat y)^2/\sum(y-\bar y)^2$; $R^2<0$ means worse than predicting the mean (`r2`).
- **Ridge** $\hat w=(X_c^TX_c+\lambda I)^{-1}X_c^Ty_c$, intercept unpenalised (`ridge`).
- **Kernel ridge** $\hat y(x)=\bar y+k(x,X)(K+\lambda I)^{-1}(y-\bar y)$ (`kernel_ridge`).
- **Logistic regression** $P(y=1|x)=\sigma(w^Tx+b)$ by Newton (`logistic_newton`).

## 2 The symmetry obstruction

$P(s)=P(-s)$ (no field) and $e(s)=e(-s)$, $m^2(s)=m^2(-s)$. For any linear
predictor the population least-squares optimum solves
$\operatorname{Cov}(s)\,w=\operatorname{Cov}(s,y)=\mathbb E[s\,y]-\mathbb E s\,\mathbb Ey=0$,
because $s\,y(s)$ is odd and $\mathbb Es=0$. So $w=0$ and $R^2=0$: **no linear
function of the spins predicts an even observable**. On a finite sample the fitted
noise makes the test $R^2$ negative ($-0.21$ below). Same argument for logistic
regression of the phase: $\sigma(w^Ts+b)$ must equal $\sigma(-w^Ts+b)$, so the
optimum has $w=0$; accuracy is chance.

## 3 Features, kernels and sample complexity

- **Bond features** $b_{i,\mu}=s_is_{i+\hat\mu}$ ($2N$ of them, `bond_features`):
  $e=-\frac1N\sum b$ is **exactly linear**. Ridge on bonds: $R^2=1.0000$.
- **Degree-2 polynomial kernel** $k(x,y)=(1+x^Ty/N)^2$ (`poly2_kernel`). Its
  feature map contains $\phi_{ij}(x)=x_ix_j/N$ for all ordered pairs, since
  $(x^Ty/N)^2=\sum_{ij}\phi_{ij}(x)\phi_{ij}(y)$. Both targets are linear in $\phi$:
  $$m^2=\sum_{ij}\tfrac1N\phi_{ij},\ \lVert w\rVert^2=1;\qquad
  e=-\tfrac12\sum_{(ij)\ \rm nn,\ ordered}\phi_{ij},\ \lVert w\rVert^2=\tfrac14\cdot4N=N .$$
  Kernel ridge generalisation bounds scale with the RKHS norm $\lVert w\rVert$ over
  $\sqrt n$, so $e$ needs about $N$ times more data than $m^2$. With $N=100$ and 672
  samples: $R^2(m^2)=1.0000$, $R^2(e)=0.964$.

The lesson: a kernel or network that *can* represent the target is not enough;
the norm of the target in the model's geometry sets the data cost. Locality
(nearest-neighbour bonds) is prior knowledge worth a factor $N$.

## 4 Phase classification (Carrasquilla-Melko [S23])

Label $y=1$ if $T<T_c$. Fully connected net, one hidden layer (they use 100
sigmoid units [S23]); a hidden unit $\tanh(w^Ts+b)$ with $w\propto\mathbf 1$ is a
function of $m$, and two such units with opposite $w$ build $\lvert m\rvert$ (their
3-unit toy model makes this explicit [S23]). **$T_c$ estimate**: the temperature
where the test-averaged output crosses $1/2$ (`estimate_tc`).

Our `MLPClassifier` ($N\to16$ or $32\to1$, AdamW). The $Z_2$ symmetry can be
imposed as **data augmentation**: add $-s$ with the same label.

## 5 Worked example (`python observables.py`, $L=10$, 16 temperatures, 672 / 288 split)

Test $R^2$:

| target | ridge on spins | ridge on bonds | KRR poly-2 on spins |
|---|---|---|---|
| $e$ | $-0.205$ | $1.0000$ | $0.964$ |
| $m^2$ | $-0.202$ | $0.865$ | $1.0000$ |

Phase, test accuracy (all / $\lvert T-T_c\rvert>0.3$):

| model | accuracy |
|---|---|
| logistic on spins | 0.448 / 0.404 |
| logistic on $m^2$ | 0.910 / 1.000 |
| MLP on spins | 0.757 / 0.813 |
| MLP on spins + $Z_2$ augmentation | 0.858 / 0.964 |

$T_c$ from the crossing: 2.233 (exact $2.2692$ for $L=\infty$; finite $L$ shifts it).

## 6 Pitfalls

- **Correlated samples.** Snapshots from one Markov chain are correlated; a random
  train/test split then leaks. Use independent chains (as here) or split by chain
  and quote the autocorrelation time.
- **Circular $T_c$.** Supervised labels use the known $T_c$; the crossing is then
  partly by construction. A real test: several $L$, finite-size scaling of the
  crossing, or an unsupervised method (note 04, PCA's $m$ [S22]).
- **Accuracy dominated by easy samples.** Report accuracy near $T_c$ separately.
- **Leaking the answer.** $T$ or $e$ as an input feature for a phase classifier.
- **Negative test $R^2$ read as a bug.** It is overfitting of an unpredictable target.
- **Extrapolation claims** from an interpolating split: to claim transfer to other
  $T$ or $L$, hold those out.

## 7 Questions

1. **Prove that linear regression on raw spins cannot predict the energy of the
   zero-field Ising model.** $\operatorname{Cov}(s,e)=\mathbb E[s\,e(s)]=0$ by
   $s\to-s$ symmetry, so the population optimum is $w=0$, $R^2=0$.
2. **Which features make the energy exactly linear, and what does that say about
   locality?** Nearest-neighbour products $s_is_{i+\hat\mu}$; the Hamiltonian is a
   sum of local terms, so local features suffice.
3. **Both $e$ and $m^2$ lie in the span of the poly-2 kernel. Why is $m^2$ learnt
   from 672 samples and $e$ not quite?** RKHS norm: 1 for $m^2$ (uniform weight on
   all $N^2$ pair features), $N$ for $e$ (weight concentrated on $4N$ ordered bonds);
   sample cost scales with the norm squared.
4. **How does a one-hidden-layer network detect the ferromagnetic phase, and why
   does $Z_2$ augmentation help?** Hidden units aligned with $\mathbf 1$ compute
   functions of $m$; combining two with opposite signs gives $\lvert m\rvert$.
   Augmentation forces the output to be even in $s$ and removes a spurious
   dependence on the sign of $m$ (0.813 to 0.964 away from $T_c$).
5. **How would you turn the classifier's crossing into a defensible $T_c$ estimate?**
   Repeat at several $L$ with independent data, fit the crossing $T^*(L)$ to
   $T_c+aL^{-1/\nu}$ ($\nu=1$ for 2D Ising), give statistical errors from
   independent training runs, and compare with an unsupervised estimate.

## Code

`dataset`, `r2`, `ridge`, `poly2_kernel`, `kernel_ridge`, `logistic_newton`,
`MLPClassifier`, `accuracy`, `estimate_tc`, `regression_table`,
`classification_table` in [`observables.py`](../src/py/observables.py);
`sample_ising`, `energy_per_spin`, `magnetisation`, `bond_features`,
`onsager_energy`, `onsager_magnetisation` in
[`ising_snapshots.py`](../src/py/ising_snapshots.py); tests in
[`test_observables.py`](../src/py/test_observables.py) (sklearn `Ridge`,
`KernelRidge` cross-checks) and [`test_ising_snapshots.py`](../src/py/test_ising_snapshots.py).
