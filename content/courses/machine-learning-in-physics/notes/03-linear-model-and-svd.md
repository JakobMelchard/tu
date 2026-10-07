# 03 The linear model, the SVD and regularised inverse problems

TISS topic 3, "Linear model, singular value decomposition" [S2]; the course's
"centrepiece" [S4]. 2021S videos Regression 1-5, Learning 4-5; exercises 04-07
[S5, S11]. Texts: [S7 sec. 4.5-4.6, ch. 9], [S8 sec. 3.2, 3.4.1], [S6 sec. VI],
and for inverse problems [S10 ch. 2-6], [S21]. OLS statistics and ridge basics
from the ML side: [CSE note 08](../../machine-learning/notes/08-linear-models.md).

## Definitions

- Design matrix $X\in\mathbb R^{N\times K}$ (rows = observations, columns =
  features), labels $y\in\mathbb R^N$, model $\hat y=X\theta$.
- **Least squares:** $\hat\theta=\arg\min\|y-X\theta\|^2$; **normal equations**
  $X^TX\theta=X^Ty$.
- **Thin SVD:** $X=USV^T=\sum_{k<r}s_ku_kv_k^T$, $U^TU=V^TV=\mathbb 1_r$,
  $s_0\ge\dots\ge s_{r-1}>0$. $u_k$ live in observation space ($\mathbb R^N$),
  $v_k$ in parameter space ($\mathbb R^K$).
- **Pseudo-inverse:** $X^+=\sum_k s_k^{-1}v_ku_k^T=VS^{-1}U^T$.
- **Condition number** $\kappa(X)=s_0/s_{r-1}$.
- **Filter factors:** every linear regulariser here is
  $\hat\theta=\sum_kf_k\frac{u_k^Ty}{s_k}v_k$: pinv $f_k=1$; TSVD $f_k=[k<r]$;
  Tikhonov $f_k=\frac{s_k^2}{s_k^2+\lambda^2}$; GD after $t$ steps
  $f_k=1-(1-\eta s_k^2)^t$ [S10 ch. 4, 6].

## Least squares via the SVD

$\|y-X\theta\|^2=\|U^Ty-SV^T\theta\|^2+\|(\mathbb 1-UU^T)y\|^2$ (Pythagoras). With
$z=V^T\theta$: minimised by $z_k=u_k^Ty/s_k$, so $\hat\theta=X^+y$, the
**minimum-norm** solution when $X$ is rank deficient. Residual $\perp\mathrm{col}(X)$;
$\hat y=UU^Ty$ is the orthogonal projection [S7 sec. 9.4].

**Why not the normal equations:** $\kappa(X^TX)=\kappa(X)^2$. For the $101\times30$
Vandermonde matrix $\kappa=5.18\times10^{10}$ (the exercise-06 assert [S5]); squared
it exceeds $1/\epsilon_\text{mach}\approx4.5\times10^{15}$.

**Noise amplification.** $y=X\theta^*+e$:
$\hat\theta-\theta^*=\sum_k\frac{u_k^Te}{s_k}v_k$. White noise has
$|u_k^Te|\approx\sigma$ in every direction, so the error in direction $k$ is
$\sigma/s_k$. Small singular values amplify noise; this is the whole story of
ill-posedness and of the exercise-06 coefficients of size $10^8$.

**Discrete Picard condition** [S10 ch. 3]: a meaningful solution needs
$|u_k^Ty_\text{true}|$ to decay faster than $s_k$. Plot $s_k$, $|u_k^Ty|$ and
their ratio: where $|u_k^Ty|$ levels off at the noise $\sigma$, truncate.

## Regularisation of the inverse

**Tikhonov:** $\min\|X\theta-y\|^2+\lambda^2\|\theta\|^2$ $\Rightarrow$
$\hat\theta=(X^TX+\lambda^2)^{-1}X^Ty=\sum_k\frac{s_k}{s_k^2+\lambda^2}(u_k^Ty)v_k$.
Proof: $X^TX+\lambda^2=V(S^2+\lambda^2)V^T$ on the row space. $f_k\approx1$ for
$s_k\gg\lambda$, $\approx s_k^2/\lambda^2$ for $s_k\ll\lambda$. The exercise-06 form
$N\lambda^2$ just rescales $\lambda$ [S5]. Equivalent stacked problem:
$\min\big\|\binom{X}{\lambda\mathbb 1}\theta-\binom y0\big\|$. General form
$\lambda^2\|L\theta\|^2$ with $L$ a difference operator penalises roughness
instead of size [S10 ch. 8].

**TSVD:** keep the $r$ largest components. Sharp cutoff vs Tikhonov's smooth one.

**Parameter choice** [S10 ch. 5]:

- **L-curve** [S21]: plot $(\log\|X\hat\theta_\lambda-y\|,\log\|\hat\theta_\lambda\|)$;
  choose the corner (maximum curvature). Left branch (small $\lambda$): solution
  norm explodes, noise; right branch: residual grows, over-smoothing.
- **Discrepancy principle:** largest $\lambda$ with $\|X\hat\theta_\lambda-y\|\le\tau\|e\|$;
  needs the noise level.
- **GCV:** minimise $\|X\hat\theta_\lambda-y\|^2/(N-\sum_kf_k)^2$ [S8 sec. 7.10];
  no noise level needed, fails for correlated noise and sometimes under-regularises.
- **Validation / early stopping:** the course's route in exercise 07 [S5].

## Temperature deblurring as a Fredholm problem

A measured spectrum at temperature $T$ is a smoothed version of the $T=0$ one,

$$A_T(\omega)=\int d\omega'\,K_T(\omega-\omega')\,A(\omega')+e(\omega),$$

a Fredholm equation of the first kind [S10 ch. 2]. Two kernels:

- **Thermal (tunnelling) broadening** $K_T(x)=-\partial_xf(x)=\frac{\beta}{4\cosh^2(\beta x/2)}$,
  $\int K_T=1$, FWHM $=4\ln(1+\sqrt2)\,T\approx3.53\,T$.
- **Doppler (Gaussian)** $K(x)=e^{-x^2/2\sigma^2}/\sqrt{2\pi}\sigma$, $\sigma\propto\sqrt T$:
  exercise 07 "Undoing temperature" [S5].

Discretise on a grid ($K_{nk}=K_T(\omega_n-\omega'_k)\Delta\omega$): $b=Kx+e$, i.e.
linear regression with $K$ as design matrix and $x=A(\omega')$ as parameters.
Convolution with a smooth kernel damps high Fourier modes like $\hat K(q)$
($\propto q/\sinh(\pi q T)$ for $-f'$, $e^{-\sigma^2q^2/2}$ for the Gaussian), so the
$s_k$ decay fast and the inverse amplifies high-frequency noise.

**Analytic-continuation flavour.** Imaginary-time data
$G(\tau)=-\int d\omega\,\frac{e^{-\tau\omega}}{1+e^{-\beta\omega}}A(\omega)$ is the same
problem with a far worse kernel: its singular values decay exponentially fast, so
only $O(10)$ numbers of $A$ are recoverable from any realistic $G(\tau)$. MaxEnt
[S22] and sparse-ir [S23] exploit exactly this SVD structure.

## Pitfalls

- Solving the normal equations for ill-conditioned $X$; use `lstsq`/SVD.
- Reporting $\|X\hat\theta-y\|$ as quality: it is smallest for the worst solution.
- Grid edges: rows of $K$ near the boundary do not integrate to 1.
- Prior knowledge ($A\ge0$, smoothness, normalisation) is worth more than tuning $\lambda$.
- The oracle $\lambda$ needs the truth; in practice use L-curve, discrepancy or validation.

## Test-style questions

**Q1.** Prove $(X^TX+N\lambda^2)^{-1}X^T=\sum_k\frac{s_k}{s_k^2+N\lambda^2}v_ku_k^T$. Need $s_k\ne0$?
**A.** $X^TX=VS^2V^T$; on $\mathrm{row}(X)$ the inverse is $V(S^2+N\lambda^2)^{-1}V^T$,
and $X^T=VSU^T$ maps into $\mathrm{row}(X)$. No: $\lambda>0$ keeps every denominator
positive, and $s_k=0$ terms simply vanish.

**Q2.** Why are the pinv coefficients of a 30-term polynomial fit of order $10^8$?
**A.** $\hat\theta-\theta^*=\sum_k(u_k^Te/s_k)v_k$ with $s_{29}\approx2\times10^{-10}$ and
$|u_k^Te|\approx\sigma=0.1$; the smallest-$s$ right singular vectors (high-order,
alternating coefficients) carry the blow-up.

**Q3.** Sketch the L-curve and explain both branches.
**A.** Small $\lambda$: residual $\approx$ noise level, solution norm huge (vertical
branch). Large $\lambda$: norm small, residual grows (horizontal branch). Corner =
balance of perturbation and regularisation error.

**Q4.** Why do deblurred spectra get spikier with more GD steps?
**A.** Step $t$ has filter $1-(1-\eta s_k^2)^t$: late steps unlock small-$s_k$
directions, which are high-frequency and noise-dominated. Stop when the
validation error is minimal.

**Q5.** Why is analytic continuation from $G(\tau)$ harder than thermal deblurring?
**A.** Same Fredholm structure, but $K(\tau,\omega)$ has exponentially decaying
singular values, so far fewer components survive above the noise.

## Code

No reference code here: the course's graded weekly exercises implement the SVD,
Tikhonov and deblurring steps [S5].
