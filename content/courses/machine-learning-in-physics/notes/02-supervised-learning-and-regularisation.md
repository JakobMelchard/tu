# 02 Supervised learning, over- and underfitting, regularisation

TISS topic 2, "Supervised learning, over-/underfitting, regularization" [S2];
2021S videos Learning 2-3, 5 and Regression 2, exercises 04-05 [S5, S11]. Texts:
[S6 sec. II-III, VI], [S8 sec. 3.4, 7.3], [S9 ch. 2, 6]. General-ML depth (CV
protocols, learning curves, nested CV):
[CSE note 04](../../machine-learning/notes/04-model-selection.md),
[CSE note 03, bias-variance](../../machine-learning/notes/03-evaluation.md).

## Definitions

- **Data** $\mathcal D=\{(x_n,y_n)\}_{n=1}^N$ i.i.d. from $p(x,y)$; **model**
  $f(x;\theta)$; **loss** $\ell$; **training (in-sample) error**
  $E_\text{in}=\frac1N\sum_n\ell(f(x_n;\theta),y_n)$; **generalisation
  (out-of-sample) error** $E_\text{out}=\mathbb E_{p}\,\ell$.
- **Protocol** (exercise 04 [S5]): split randomly into training / validation /
  test; fit on training, choose hyperparameters on validation, report test once.
- **Linear model with features** $\phi_k$: $f=\sum_k\theta_k\phi_k(x)=\phi(x)^T\theta$,
  linear in $\theta$, arbitrary in $x$ (polynomials: $\phi_k=x^k$, the Vandermonde
  design matrix of exercise 05-06).
- **Underfitting:** $E_\text{in}$ high (bias). **Overfitting:** $E_\text{in}\ll E_\text{out}$ (variance).
- **Regularisation:** add a penalty $\Omega(\theta)$ or restrict the search to reduce variance at
  the cost of bias. Ridge $\Omega=\lambda^2\|\theta\|_2^2$; lasso $\Omega=\alpha\|\theta\|_1$;
  early stopping (stop GD at $t^*$).

## Bias-variance decomposition (derivation)

$y=f(x)+\epsilon$, $\mathbb E\epsilon=0$, $\mathrm{Var}\,\epsilon=\sigma^2$, estimator
$\hat f_\mathcal D$ trained on a random $\mathcal D$, $\bar f=\mathbb E_\mathcal D\hat f_\mathcal D$. At fixed $x$:

$$\mathbb E_{\mathcal D,\epsilon}(y-\hat f_\mathcal D)^2
=\sigma^2+\underbrace{(f-\bar f)^2}_{\text{bias}^2}+\underbrace{\mathbb E_\mathcal D(\hat f_\mathcal D-\bar f)^2}_{\text{variance}}.$$

Expand $y-\hat f=\epsilon+(f-\bar f)+(\bar f-\hat f)$; cross terms vanish because
$\epsilon$ is independent of $\mathcal D$ with mean 0, and $\mathbb E_\mathcal D(\bar f-\hat f)=0$ [S8 sec. 7.3, S6 sec. III].

**Ridge in the SVD basis** (fixed design $X=\sum_ks_ku_kv_k^T$, $y=X\theta^*+\epsilon$):
$\hat\theta_\lambda=\sum_kf_k\frac{u_k^Ty}{s_k}v_k$, $f_k=\frac{s_k^2}{s_k^2+\lambda^2}$ (note 03). Then

$$\mathbb E\|X\hat\theta_\lambda-X\theta^*\|^2=\sum_k(1-f_k)^2(u_k^TX\theta^*)^2+\sigma^2\sum_kf_k^2 .$$

$\lambda\to0$: bias 0, variance $\sigma^2K$ (OLS). $\lambda\to\infty$: variance 0,
bias $\|X\theta^*\|^2$. The sum is minimised in between. $\mathrm{df}(\lambda)=\sum_kf_k$
is the **effective number of parameters** [S8 sec. 3.4.1].

**Ridge = MAP.** Gaussian likelihood $\propto e^{-\|y-X\theta\|^2/2\sigma^2}$ and prior
$\theta\sim\mathcal N(0,\tau^2\mathbb 1)$ give $-\log$ posterior $=\frac1{2\sigma^2}\big(\|y-X\theta\|^2+\frac{\sigma^2}{\tau^2}\|\theta\|^2\big)$:
ridge with $\lambda^2=\sigma^2/\tau^2$. Lasso is MAP with a Laplace prior [S6 sec. VI.F].

**Why lasso is sparse.** Proximal step of $\alpha\|\theta\|_1$ is soft thresholding
$S_a(z)=\mathrm{sign}(z)\max(|z|-a,0)$: small coefficients become exactly 0.
Geometrically the $\ell_1$ ball has corners on the axes [S8 sec. 3.4.2, S31].
No closed form; solve by coordinate descent or ISTA.

**Early stopping = implicit ridge.** GD from $\theta_0=0$ on $\frac12\|X\theta-y\|^2$
has filter factors $f_k(t)=1-(1-\eta s_k^2)^t$. For $\eta s_k^2\ll1$,
$f_k\approx1-e^{-t\eta s_k^2}$: directions with $s_k^2\gg1/(\eta t)$ are fitted,
the rest not; ridge does the same with the threshold $s_k^2\approx\lambda^2$. So
$t\leftrightarrow1/(\eta\lambda^2)$.

**Feature scaling.** Ridge and lasso penalise all coefficients equally, so their
effect depends on units: standardise features (training-set mean/std) first. Do
not penalise the intercept.

For an ill-conditioned design such as a high-order polynomial fit, the
coefficients are wild long before the *predictions* are: $\theta$ lives in the
badly conditioned directions $v_k$, $\hat y$ only through $s_kv_k^T\theta$.

## Pitfalls

- Choosing $\lambda$ or the stopping time on the **test** set: the reported error
  is then optimistic. Use validation or CV.
- Training error always decreases with model size (nested models) and with GD
  iterations for a linear model; it cannot select a model.
- Two conventions for ridge: $(X^TX+N\lambda^2)^{-1}$ (the course's [S5])
  vs $(X^TX+\lambda^2)^{-1}$ or $\alpha$ in sklearn (`Ridge(alpha=lam**2)`). State
  which.
- Unscaled polynomial features: condition number $5.2\times10^{10}$ for $K=30$
  (note 03). Orthogonal polynomials or rescaled $x$ fix the conditioning, not the
  overfitting.
- "More data" reduces variance only; it does not cure bias.

## Test-style questions

**Q1.** Derive the bias-variance decomposition and name the irreducible term.
**A.** As above; $\sigma^2$ is irreducible, independent of the estimator.

**Q2.** Show that ridge shrinks each SVD component by $s_k^2/(s_k^2+\lambda^2)$.
**A.** $(X^TX+\lambda^2\mathbb 1)^{-1}X^T=V(S^2+\lambda^2)^{-1}SU^T$, so
$\hat\theta=\sum_k\frac{s_k}{s_k^2+\lambda^2}(u_k^Ty)v_k=\sum_kf_k\frac{u_k^Ty}{s_k}v_k$. No $s_k\ne0$ needed ($\lambda>0$).

**Q3.** Why does early stopping regularise a linear least-squares fit?
**A.** From $\theta_0=0$ GD fills in direction $k$ with factor $1-(1-\eta s_k^2)^t$;
small-$s_k$ (noise-dominated) directions are reached only after $t\sim1/(\eta s_k^2)$
steps. Stopping at $t^*$ acts like ridge with $\lambda^2\sim1/(\eta t^*)$.

**Q4.** Lasso vs ridge: which gives exact zeros, and why?
**A.** Lasso. Its optimality condition $0\in X^T(X\theta-y)/N+\alpha\,\partial\|\theta\|_1$
admits $\theta_j=0$ whenever $|X_j^T(y-X\theta)|/N\le\alpha$; ridge's gradient
$2\lambda^2\theta_j$ vanishes only at 0, so the minimiser has no reason to sit
there.

**Q5.** Training error $0.01$, validation error $0.3$: diagnosis and two fixes?
**A.** Overfitting (variance). Increase regularisation ($\lambda$, stop earlier,
fewer features) or get more data.

## Code

Linear regularisation has no reference code here: the course's graded weekly
exercises implement it [S5]. Neural-network early stopping:
`src/py/nn_numpy.train(..., X_val, Y_val)` (note 05).
