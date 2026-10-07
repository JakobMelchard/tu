# 01 Optimisation and gradient descent

TISS topic 1, "Simple optimization problems, gradient descent" [S2]; 2021S videos
Optimization 1-5 and exercises 01-03, 07 [S5, S11]. Learning is minimisation of a
cost $E(\theta)$; everything later in the course (least squares, logistic
regression, networks, Q-learning) reuses these iterations. Textbook: [S6 sec. IV],
[S7 ch. 7].

## Definitions

- **Gradient descent (GD):** $\theta_{t+1}=\theta_t-\eta\nabla E(\theta_t)$, step
  size (learning rate) $\eta>0$.
- **Newton:** $\theta_{t+1}=\theta_t-\eta\,(H+\lambda\mathbb 1)^{-1}\nabla E$, $H=\nabla^2E$;
  $\lambda\ge0$ damps (Levenberg), $\eta\le1$ shortens (exercise 03 signature [S5]).
- **Heavy ball (Polyak):** $v_{t+1}=\beta v_t-\eta\nabla E(\theta_t)$, $\theta_{t+1}=\theta_t+v_{t+1}$.
- **Nesterov:** same, gradient at the look-ahead $\theta_t+\gamma v_t$ [S6 sec. IV.D, S30].
- **Stochastic GD (SGD):** $E=\frac1N\sum_nE_n$; per step use a minibatch
  $B$, $|B|=M$: $g=\frac1M\sum_{n\in B}\nabla E_n$. One **epoch** = $N/M$ steps
  over a shuffled data set.
- **Adam:** per-coordinate step $\eta\,\hat m_t/(\sqrt{\hat v_t}+\epsilon)$ with
  bias-corrected moving averages of $g$ and $g^2$ [S26, S6 sec. IV.E].
- $L$-**smooth**: $\|\nabla E(a)-\nabla E(b)\|\le L\|a-b\|$; $\mu$-**strongly
  convex**: $E(b)\ge E(a)+\nabla E(a)^T(b-a)+\frac\mu2\|b-a\|^2$. Condition number
  $\kappa=L/\mu$.

## Derivations

**Quadratic model.** Near a minimum $\theta^*$, $E\approx E^*+\frac12\delta^TH\delta$,
$\delta=\theta-\theta^*$. GD gives $\delta_{t+1}=(\mathbb 1-\eta H)\delta_t$, so in
the eigenbasis of $H$ (eigenvalues $\mu=h_1\le\dots\le h_K=L$)

$$\delta^{(k)}_t=(1-\eta h_k)^t\,\delta^{(k)}_0 .$$

- Converges iff $|1-\eta h_k|<1\ \forall k$ $\Leftrightarrow$ $0<\eta<2/L$.
- Rate $\rho(\eta)=\max_k|1-\eta h_k|=\max(|1-\eta\mu|,|1-\eta L|)$, minimised
  where the two are equal: $\eta^*=\frac{2}{L+\mu}$, $\rho^*=\frac{\kappa-1}{\kappa+1}$.
- Iterations to reduce the error by $\varepsilon$: $\sim\frac\kappa2\ln\frac1\varepsilon$.
  Ill-conditioning, not dimension, makes GD slow.
- 1D: $\eta=1/E''(\theta^*)$ reaches the minimum of the quadratic in one step
  (that is Newton).

**Heavy ball on the quadratic.** Per eigenvalue $(\delta_{t+1},\delta_t)$ evolves
with the $2\times2$ matrix $\begin{pmatrix}1+\beta-\eta h&-\beta\\1&0\end{pmatrix}$;
choosing $\eta=4/(\sqrt L+\sqrt\mu)^2$, $\beta=\big(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\big)^2$
makes all eigenvalues have modulus $\sqrt\beta$, rate $\frac{\sqrt\kappa-1}{\sqrt\kappa+1}$
[S30]: $\kappa\to\sqrt\kappa$ iterations.

**Newton is affine invariant and quadratic.** Exact on a quadratic in one step
($\delta_1=\delta_0-H^{-1}H\delta_0=0$). Near a non-degenerate minimum,
$\|\delta_{t+1}\|\le C\|\delta_t\|^2$. But it goes to **any** stationary point:
at a saddle or maximum $H$ is indefinite and the Newton step points uphill.
Damping $\lambda>|h_\text{min}|$ restores a descent direction.

**SGD noise.** $g=\nabla E+\xi$ with $\mathbb E\xi=0$,
$\mathrm{Cov}\,\xi\approx\frac1M\,\Sigma_g$. Near $\theta^*$ with constant $\eta$ the
iterates do not converge but fluctuate with stationary covariance $\propto\eta/M$:
a floor. Remedies: decreasing $\eta_t$ ($\sum\eta_t=\infty$, $\sum\eta_t^2<\infty$)
or larger $M$. Upside: cheap steps, and noise escapes shallow minima and saddles.

**Stationary-point classification.** $\nabla E=0$ and eigenvalues of $H$: all
$>0$ minimum, all $<0$ maximum, mixed saddle, zero eigenvalue undetermined.

## Pitfalls

- A single step can land exactly on a stationary point that is not a minimum.
  Always check $\nabla^2E$, or add noise.
- Divergence and slow convergence both come from the **extreme** eigenvalues:
  $\eta$ is capped by $L$, speed is set by $\mu$. Rescale features (note 02).
- Newton without damping on a non-convex $E$ can converge to a maximum.
- Constant-$\eta$ SGD never converges exactly; its training error is not
  monotone.
- $M=N$ SGD is GD; test that identity when implementing.
- Momentum overshoots: on a well-conditioned problem it can be slower than GD.

## Test-style questions

**Q1.** For $E=\frac12\theta^TH\theta$, $H=\mathrm{diag}(1,10)$, which $\eta$ are
stable and which is optimal? What is the rate?
**A.** $0<\eta<2/10=0.2$; $\eta^*=2/11$; $\rho^*=(10-1)/(10+1)=9/11\approx0.82$.

**Q2.** Show that one Newton step solves a quadratic exactly and state its cost.
**A.** $\theta_1=\theta_0-H^{-1}(H\theta_0-b)=H^{-1}b=\theta^*$. Cost: forming and
solving with $H$, $O(K^2N+K^3)$ per step vs $O(KN)$ for GD; infeasible for
networks with $K\sim10^6$.

## Code

No reference code here: the course's graded weekly exercises implement these
methods [S5]. GD as a regulariser (early stopping) is in note 03.

General-ML background: [CSE note 11, section Optimisation](../../machine-learning/notes/11-neural-networks.md).
