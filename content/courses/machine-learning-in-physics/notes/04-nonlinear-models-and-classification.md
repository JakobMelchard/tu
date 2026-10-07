# 04 Non-linear models and classification

TISS topic 4, "Non-linear models, classification problems" [S2]; 2021S videos
Regression 3 (generalised/extended linear models), Classification 1-3; exercise
08 (SUSY, logistic) [S5, S11]. Texts: [S6 sec. VII], [S8 sec. 4.4], [S9 sec. 4.3].
Metrics in depth (ROC, PR, micro/macro):
[CSE note 03](../../machine-learning/notes/03-evaluation.md);
SVMs and kernels: [CSE note 10](../../machine-learning/notes/10-svm.md).

## Definitions

- **Classification:** $y\in\{0,1\}$ (or $\{1..C\}$); a classifier outputs a score or
  probability $p(y=1|x)$ and a decision $\hat y=[p>\tfrac12]$ (threshold adjustable).
- **Extended linear model:** $f(x)=\theta^T\phi(x)$ with fixed non-linear features
  $\phi$; still linear in $\theta$, so notes 01-03 apply unchanged.
- **Generalised linear model:** $\mathbb E[y|x]=g^{-1}(\theta^Tx)$ with link $g$;
  logistic regression is the Bernoulli GLM with the logit link.
- **Logistic regression:** $p(y=1|x)=\sigma(\theta^Tx)$, $\sigma(z)=1/(1+e^{-z})$,
  $\sigma'=\sigma(1-\sigma)$, $\sigma(-z)=1-\sigma(z)$.
- **Softmax regression:** $p(y=c|x)=e^{z_c}/\sum_{c'}e^{z_{c'}}$, $z=W^Tx$.
- **Decision boundary:** $\{x:p(y=1|x)=\tfrac12\}=\{\theta^Tx=0\}$, a hyperplane in
  $x$ (or in $\phi(x)$ for extended models).
- **Confusion matrix** $\begin{pmatrix}TN&FP\\FN&TP\end{pmatrix}$; accuracy
  $\frac{TP+TN}{N}$, **sensitivity** (recall, TPR) $\frac{TP}{TP+FN}$, **specificity**
  (TNR) $\frac{TN}{TN+FP}$ [S5 Ex08].

## Derivations

**Cross-entropy from maximum likelihood.** $p(y|x)=p^y(1-p)^{1-y}$, so
$-\log L=E(\theta)=-\sum_n[y_n\log p_n+(1-y_n)\log(1-p_n)]$, $p_n=\sigma(\theta^Tx_n)$.
Using $\partial_z\log\sigma=1-\sigma$, $\partial_z\log(1-\sigma)=-\sigma$:

$$\nabla E=\sum_n(p_n-y_n)x_n=X^T(p-y),\qquad \nabla^2E=X^TWX,\ W=\mathrm{diag}\,p_n(1-p_n)\succeq0 .$$

Same form as least squares' $X^T(X\theta-y)$ with the prediction replaced by $p$.
$E$ is **convex**: GD/Newton find the global minimum. Newton step
$\theta\leftarrow\theta-(X^TWX)^{-1}X^T(p-y)$ = weighted least squares, hence IRLS
[S8 sec. 4.4.1]. Stable evaluation: $E=\sum_n[\log(1+e^{z_n})-y_nz_n]$.

**Separable data.** If some $\theta$ classifies all points correctly, then
$E(c\theta)\to0$ as $c\to\infty$: no finite minimiser, $\|\theta\|$ grows forever.
Ridge ($+\frac\lambda2\|\theta\|^2$) or early stopping fixes it.

**Log-odds.** $\log\frac{p}{1-p}=\theta^Tx$: each $\theta_j$ is the change in log-odds
per unit of $x_j$. For two Gaussian classes with equal covariance $\Sigma$ the Bayes
posterior is exactly logistic with $\theta=\Sigma^{-1}(\mu_1-\mu_0)$ (LDA), so the
linear boundary is optimal there.

**Softmax.** $E=-\sum_n\sum_cY_{nc}\log P_{nc}$, $\nabla_WE=X^T(P-Y)$. Adding a
constant vector to every column of $W$ leaves $P$ unchanged: only differences
are identifiable. For $C=2$, $P_1=\sigma((w_1-w_0)^Tx)$: logistic regression.
Physics reading: $P$ is a Boltzmann distribution over classes with energies $-z_c$ [S6 sec. VII.D].

**Kernels, briefly.** Ridge/logistic solutions lie in $\mathrm{span}\{\phi(x_n)\}$
(representer theorem), so $f(x)=\sum_n\alpha_nk(x_n,x)$ with $k(x,x')=\phi(x)^T\phi(x')$;
never form $\phi$. RBF $k=e^{-\gamma\|x-x'\|^2}$ corresponds to infinitely many
features. Cheap version used here: RBF features around $m$ centres, then ordinary
logistic regression.

## Worked example (`src/py/classification.py`, seed 4711)

1. Two unit-variance Gaussians at $(\mp1,0)$, 500 each. Newton:
   $\theta=(0.056,1.951,0.012)$, boundary $x_1=-0.029$ (Bayes: $x_1=0$, slope
   $\Sigma^{-1}\Delta\mu=(2,0)$). Confusion $[[428,72],[75,425]]$: error $0.147$
   vs Bayes error $\Phi(-1)=0.159$ (sampling noise).
2. XOR (sign of $x_0x_1$): linear logistic $0.539$ accuracy (chance); logistic on
   40 RBF features ($\gamma=4$): $0.980$.
3. Three blobs, softmax: training accuracy $1.000$.

Exercise 08 in numbers [S5]: the notebook asserts more than 350 000 of 500 000 test
events correct (70 %) and sensitivity < specificity; see note 10 for the synthetic analogue
(AUC 0.759, sensitivity 0.33 at specificity 0.92).

## Pitfalls

- Accuracy on imbalanced data: "always background" scores the background fraction.
  Report sensitivity/specificity or AUC.
- The $0.5$ threshold is a choice; move it along the ROC curve for the task.
- Logistic regression on separable data without regularisation: weights diverge,
  sklearn warns, probabilities saturate.
- Linear models cannot represent symmetric features ($|x|$, $x_0x_1$,
  $|\eta_1-\eta_2|$): engineer $\phi$ or use a network (the Ising $\mathbb Z_2$ case, note 10).
- sklearn's `C` is $1/\lambda$ and does not penalise the intercept.

## Test-style questions

**Q1.** Derive $\nabla E$ for logistic regression and show $E$ is convex.
**A.** $\nabla E=X^T(\sigma(X\theta)-y)$; $\nabla^2E=X^TWX$ with $W_{nn}=p_n(1-p_n)>0$,
so $v^T\nabla^2Ev=\sum_nW_{nn}(x_n^Tv)^2\ge0$.

**Q2.** What happens to logistic regression on linearly separable data?
**A.** $E$ has infimum 0, not attained; GD increases $\|\theta\|$ without bound
along the separating direction. Regularise.

**Q3.** A model has sensitivity 0.33 and specificity 0.92 on 30 % signal. Accuracy? Good for a SUSY search?
**A.** $0.3\cdot0.33+0.7\cdot0.92=0.743$, barely above the trivial $0.70$. It
misses two thirds of the signal; for discovery one wants high sensitivity at a
fixed low background rate, so judge on the ROC curve, not on accuracy.

**Q4.** Show that two-class softmax equals logistic regression.
**A.** $P_1=\frac{e^{z_1}}{e^{z_0}+e^{z_1}}=\frac1{1+e^{-(z_1-z_0)}}=\sigma((w_1-w_0)^Tx)$.

**Q5.** Why can logistic regression not learn XOR, and name two remedies.
**A.** The boundary is a line; XOR's classes are not linearly separable. Add
features ($x_0x_1$, RBF) or a hidden layer (note 05).

## Code

`src/py/classification.py`: `sigmoid` (overflow-free), `bce`, `bce_grad`,
`logistic_newton` (IRLS; equals `sklearn.linear_model.LogisticRegression(C=1/lam)`
to $10^{-6}$), `logistic_gd`, `softmax`, `softmax_loss_grad` (finite-difference
checked), `softmax_fit`, `rbf_features`, `confusion`, `make_blobs2`, `make_xor`.
