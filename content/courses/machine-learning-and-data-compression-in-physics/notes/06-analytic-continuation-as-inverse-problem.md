# 06 Analytic continuation and inverse problems as ML

Note 03 read the kernel forwards: $\rho\to G$ loses information, so $G$
compresses. This note reads it backwards: recovering $\rho$ (here $A$) from noisy
$G(\tau)$ is therefore ill-posed, and every method is a choice of prior.
Analytic continuation is a standing E138 problem (the `ana_cont` package is from
the Held group [S28]) and a natural ML project.

Code: [`../src/py/continuation.py`](../src/py/continuation.py).

## 1 Problem and ill-posedness

Data $G_i=G(\tau_i)+\eta_i$, $\eta_i\sim\mathcal N(0,\sigma^2)$, $i=1..N$. Discretise
$\omega_j$ with weight $\Delta\omega$: $G=\mathsf KA$, $\mathsf K_{ij}=-K(\tau_i,\omega_j)\Delta\omega$
(`kernel_matrix`). Constraints: $A\ge0$, $\int A=1$ ($=-G(0)-G(\beta)$).

SVD $\mathsf K/\sigma=U\Sigma V^T$. The least-squares solution
$$A_{\rm LS}=\sum_l\frac{u_l^T(G/\sigma)}{s_l}v_l=A_{\rm true}+\sum_l\frac{u_l^T\eta/\sigma}{s_l}v_l$$
adds noise of size $1/s_l$ in direction $v_l$. With $\beta=10$, 81 $\tau$ points,
321 $\omega$ points: $s_0/s_{10}=2.5\times10^2$, $s_0/s_{20}=2.2\times10^6$,
$s_0/s_{40}=1.1\times10^{16}$ (`condition`). Existence and uniqueness are not the
problem; **stability** is (Hadamard). Picard: only coefficients with
$\lvert u_l^TG\rvert/\sigma\gtrsim1$ carry information; beyond, the data are noise.
This is the IR truncation of note 03 seen from the other side.

## 2 Tikhonov and the Gaussian prior [S30]

$$A_\alpha=\arg\min_A\ \chi^2(A)+\alpha\lVert A-m\rVert^2,\qquad \chi^2=\lVert(\mathsf KA-G)/\sigma\rVert^2 .$$
Normal equations $(\mathsf K_\sigma^T\mathsf K_\sigma+\alpha)(A-m)=\mathsf K_\sigma^Tr$,
$r=(G-\mathsf Km)/\sigma$; in the SVD basis
$$A_\alpha=m+\sum_lf_l\frac{u_l^Tr}{s_l}v_l,\qquad f_l=\frac{s_l^2}{s_l^2+\alpha}$$
(`tikhonov`; checked against the normal equations). **Filter factors**: $f_l\approx1$
for $s_l^2\gg\alpha$, $\approx s_l^2/\alpha$ beyond. Bayesian reading: likelihood
$e^{-\chi^2/2}$, prior $\mathcal N(m,\alpha^{-1}I)$ (objective $=2\times$ negative log posterior), $A_\alpha$ = MAP = posterior mean.
Per direction: bias $(1-f_l)\,v_l^T(A_{\rm true}-m)$, noise std $f_l/s_l$.
Tikhonov knows nothing of $A\ge0$.

**Choosing $\alpha$.** At the truth $\mathbb E\chi^2=N$. **Discrepancy principle**
(Morozov; "historic" MaxEnt [S28]): solve $\chi^2(\alpha)=N$, monotone in $\alpha$,
by bisection in $\log\alpha$ (`discrepancy_alpha`). Alternatives: L-curve, GCV [S30];
classic and Bryan MaxEnt (Bayesian marginalisation over $\alpha$) and chi2kink [S28].
If positivity makes $\chi^2=N$ unreachable, our code aims at $1.1\times$ the $\chi^2$ floor.

## 3 Maximum entropy [S27, S28]

Prior $\propto e^{\alpha S[A]}$ with the Shannon-Jaynes entropy relative to a default model $m$:
$$S[A]=\sum_j\Delta\omega\,(A_j-m_j-A_j\ln(A_j/m_j))\le0,\qquad S=0\iff A=m .$$
Minimise $Q=\chi^2/2-\alpha S$. Stationarity, with $\mathsf K_\sigma=\mathsf K/\sigma$, $G_\sigma=G/\sigma$:
$$\alpha\Delta\omega\ln(A_j/m_j)=-[\mathsf K_\sigma^T(\mathsf K_\sigma A-G_\sigma)]_j
\ \Rightarrow\ A=m\,e^{\mathsf K_\sigma^Tc},\quad c=\frac{G_\sigma-\mathsf K_\sigma A}{\alpha\Delta\omega}.$$
So $\ln(A/m)$ lies in the $N$-dimensional row space of $\mathsf K$ (Bryan's
reduction [S27]); positivity is automatic. **Convex dual** (derived here): $c$ is the
unique minimiser of
$$\Phi(c)=\frac{\alpha\Delta\omega}2\lVert c\rVert^2+\sum_jm_je^{(\mathsf K_\sigma^Tc)_j}-c^TG_\sigma,\qquad
\nabla\Phi=\alpha\Delta\omega\,c+\mathsf K_\sigma A-G_\sigma,\quad
\nabla^2\Phi=\alpha\Delta\omega I+\mathsf K_\sigma\operatorname{diag}(A)\mathsf K_\sigma^T\succ0 .$$
$\nabla\Phi=0$ is exactly the stationarity condition. Newton with Armijo
backtracking on $\Phi$ ($N\times N$ systems, $N=81$) converges from any start
(`maxent`); a first attempt with L-BFGS in $\omega$ space stalled at small $\alpha$.

## 4 Learned inverses [S29]

Supervised continuation: draw spectra $A\sim\mathcal P$, form $G=\mathsf KA+\eta$,
train a map $G\mapsto A$ (Yoon et al.: a CNN, $10^4$-$10^5$ times faster than MaxEnt
at inference [S29]). The best **linear** such map is the Gaussian conditional mean:
with $\mu=\mathbb E A$, $C=\operatorname{Cov}A$,
$$\hat A(G)=\mu+C\mathsf K^T(\mathsf KC\mathsf K^T+\sigma^2I)^{-1}(G-\mathsf K\mu)$$
(Gaussian conditioning; Tikhonov with a learned metric $C^{-1}$ and default $\mu$;
`LearnedLinearInverse`). A network generalises this nonlinearly. What it learns is
the **prior** $\mathcal P$: excellent in distribution, silent failure outside it,
and positivity and sum rule hold only if built into the output layer.

## 5 Uncertainty

- **Noise propagation** (`noise_band`): repeat with fresh noise, take the spread.
  Captures variance only.
- **Regularisation bias** is invisible to resampling and dominates at the
  discrepancy $\alpha$: demo, $\sigma=10^{-4}$, Tikhonov $\alpha=1$: max std 0.111,
  max bias 0.048; $\alpha=150$: max std 0.007, max bias 0.097.
- **Bayesian**: the MaxEnt posterior is sharply peaked; error bars are meaningful
  for averages of $A$ over windows, not pointwise [S27]. Report integrated weights,
  peak positions with a stated window, and the $m$ and $\alpha$ dependence.

## 6 Worked example (`python continuation.py`)

$A$ = Gaussians at $-1.5$ (weight 0.6, width 0.5) and $2.5$ (0.4, 0.7); flat
default model on $[-8,8]$; $\alpha$ by the discrepancy principle.

| $\sigma$ | method | $\alpha$ | $\chi^2/N$ | $L^1$ error | $\min A$ | peaks |
|---|---|---|---|---|---|---|
| $10^{-3}$ | Tikhonov | 107 | 1.00 | 0.585 | $-0.048$ | $-1.20,\ 2.05$ |
| $10^{-3}$ | MaxEnt | 135 | 1.00 | 0.189 | $>0$ | $-1.35,\ 2.25$ |
| $10^{-4}$ | Tikhonov | 156 | 1.00 | 0.360 | $-0.023$ | $-1.30,\ 2.40$ |
| $10^{-4}$ | MaxEnt | 669 | 1.00 | 0.070 | $>0$ | $-1.45,\ 2.40$ |
| $10^{-5}$ | Tikhonov | 223 | 1.00 | 0.248 | $-0.025$ | $-1.35,\ 2.35$ |
| $10^{-5}$ | MaxEnt | 158 | 1.00 | 0.055 | $>0$ | $-1.55,\ 2.55$ |

Error falls slowly with $\sigma$ (a decade of noise buys a few singular directions).
Learned linear inverse on 200 random 1-3 peak spectra ($\sigma=10^{-4}$, trained on
2000): mean $L^1$ error 0.171 vs Tikhonov with flat $m$ 0.330 ($\alpha=150$) and 0.613 ($\alpha=1$).

## 7 Pitfalls

- Correlated QMC noise: use the covariance, $\chi^2=r^T\Sigma^{-1}r$, and rotate to
  its eigenbasis; the diagonal $\chi^2$ with correlated data makes $\alpha$ meaningless.
- Default-model dependence: rerun with two defaults; features that move are prior.
- High-frequency structure at small $\beta$: the kernel damps $\lvert\omega\rvert\gg1/\beta$
  as $e^{-\tau\lvert\omega\rvert}$; peak positions far from 0 are biased inwards (table).
- Comparing methods on different noise draws; always on the same $G$.
- Continuing from IR coefficients (note 03): drop $G_l$ below the noise level first.
- Training a learned inverse with a noise model different from the data's.

## 8 Questions

1. **Why is continuation ill-posed but the forward map well-behaved?** The forward
   map is compact with $s_l\to0$ exponentially; its inverse is unbounded, amplifying
   the noise component along $v_l$ by $1/s_l$ (here up to $10^{16}$).
2. **Derive the Tikhonov filter factors and their Bayesian meaning.** Normal
   equations in the SVD basis give $f_l=s_l^2/(s_l^2+\alpha)$; it is the MAP for
   Gaussian noise and a Gaussian prior centred at $m$ with precision $\alpha$.
3. **Show that the MaxEnt solution has the form $A=m\,e^{\mathsf K^Tc}$ and why that
   helps numerically.** Stationarity of $\chi^2/2-\alpha S$; $\ln(A/m)$ lies in the
   $N$-dimensional row space, so one solves an $N$-dimensional convex problem for $c$
   instead of an $N_\omega$-dimensional one, and positivity is built in.
4. **What does a neural network trained on synthetic $(G,A)$ pairs learn, and when
   does it fail?** A prior over spectra (its linear version is the Gaussian conditional
   mean); fails for spectra unlike the training set or noise unlike the training noise,
   without warning.
5. **Your bootstrap band is narrow. Is the continuation accurate?** Not necessarily:
   the band is the variance; at the discrepancy $\alpha$ the bias (0.097 vs std 0.007
   in the demo) dominates. Check $m$- and $\alpha$-dependence and report windowed
   integrals.

## Code

`grids`, `kernel_matrix`, `condition`, `gaussians`, `two_peak`, `synthetic_data`,
`chi2`, `tikhonov`, `maxent`, `WarmMaxent`, `discrepancy_alpha`, `l1_error`,
`peak_positions`, `LearnedLinearInverse`, `random_spectra`, `noise_band` in
[`continuation.py`](../src/py/continuation.py); tests in
[`test_continuation.py`](../src/py/test_continuation.py).
