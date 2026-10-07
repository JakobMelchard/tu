# 10 Deep learning theory

Deep networks are the one hypothesis class in this course whose practical success is not explained by the theory developed so far. This note collects what *is* proven (expressivity, convergence in special regimes, some implicit-regularisation results), what is only empirical (generalisation of practically trained nets, double descent in deep nets), and what is open, so that in the oral exam you can say precisely where the classical VC/Rademacher story applies and where it breaks.

## Definitions

1. **Feedforward network.** A function $f_\theta:\mathbb R^{d}\to\mathbb R$ of the form
$$f_\theta(x)=W_L\,\sigma\big(W_{L-1}\,\sigma(\cdots\sigma(W_1x+b_1)\cdots)+b_{L-1}\big)+b_L,$$
with weight matrices $W_\ell\in\mathbb R^{m_\ell\times m_{\ell-1}}$ ($m_0=d$, $m_L=1$), biases $b_\ell$, and an activation $\sigma:\mathbb R\to\mathbb R$ applied coordinatewise. $L$ is the depth, $m_\ell$ the width of layer $\ell$, $W=\sum_\ell m_\ell(m_{\ell-1}+1)$ the number of parameters. Common $\sigma$: ReLU $\max(0,t)$, sigmoid $1/(1+e^{-t})$, $\tanh$.

2. **One-hidden-layer (shallow) network of width $m$.** $f(x)=\sum_{j=1}^m v_j\,\sigma(\langle w_j,x\rangle+b_j)+c$.

3. **Discriminatory activation (Cybenko).** $\sigma$ is discriminatory if for every finite signed Borel measure $\mu$ on a compact $K\subset\mathbb R^d$, $\int_K\sigma(\langle w,x\rangle+b)\,d\mu(x)=0$ for all $w,b$ implies $\mu=0$.

4. **Neural tangent kernel.** For a parametrised model $f(x;\theta)$, $\Theta_\theta(x,x')=\langle\nabla_\theta f(x;\theta),\nabla_\theta f(x';\theta)\rangle$.

5. **Interpolation.** A predictor with $L_S=0$ on a sample with noisy labels. The **interpolation threshold** is the model size at which interpolation first becomes possible (for linear models: #parameters $=n$).

6. **Min-norm interpolator.** For a linear model $\Phi w=y$ with $\Phi\in\mathbb R^{n\times p}$, $p>n$, full row rank: $w^\dagger=\Phi^\top(\Phi\Phi^\top)^{-1}y=\Phi^+y$, the solution of $\min\|w\|_2$ s.t. $\Phi w=y$.

## Results

### Expressivity

**Theorem 10.1 (Universal approximation; Cybenko 1989, Hornik 1991, Leshno–Lin–Pinkus–Schocken 1993) [S29].** Let $K\subset\mathbb R^d$ be compact and $\sigma$ continuous. The set of one-hidden-layer networks $\{\sum_{j=1}^mv_j\sigma(\langle w_j,x\rangle+b_j):m\in\mathbb N\}$ is dense in $C(K)$ with the sup norm **if and only if** $\sigma$ is not a polynomial.

Two things this statement understates. First, Leshno et al. do not need continuity: their hypothesis is that $\sigma$ be **locally bounded and piecewise continuous, with a discontinuity set of Lebesgue measure zero** [S29]. That is strictly weaker and is what lets the theorem cover the step function; "continuous" above is a convenient special case. Second, the **bias $b_j$ is essential** — Leshno et al. point out the theorem is false without it (without biases the class is not even translation-closed).

*Proof idea (Cybenko's functional-analytic argument, for a discriminatory $\sigma$).* Let $\mathcal S$ be the linear span of the functions $x\mapsto\sigma(\langle w,x\rangle+b)$. Suppose its closure $\bar{\mathcal S}\ne C(K)$. By Hahn–Banach there is a nonzero bounded linear functional $\Lambda$ on $C(K)$ vanishing on $\bar{\mathcal S}$; by the Riesz representation theorem $\Lambda(g)=\int_Kg\,d\mu$ for a nonzero finite signed measure $\mu$. Then $\int\sigma(\langle w,x\rangle+b)\,d\mu=0$ for all $w,b$, and discriminatory $\sigma$ forces $\mu=0$, a contradiction. It remains to show that sigmoids are discriminatory: $\sigma(\lambda(\langle w,x\rangle+b)+\varphi)\to$ the indicator of the halfspace $\{\langle w,x\rangle+b>0\}$ (plus $\sigma(\varphi)$ on the boundary hyperplane) as $\lambda\to\infty$; dominated convergence then gives $\mu(\text{halfspace})+\sigma(\varphi)\mu(\text{hyperplane})=0$ for all halfspaces, so $\mu$ vanishes on all halfspaces and hyperplanes; a Fourier-type argument (the map $h\mapsto\int h(\langle w,x\rangle)d\mu$ vanishes on step functions, hence on $\sin,\cos$, hence $\hat\mu=0$) gives $\mu=0$. The "only if" direction: if $\sigma$ is a polynomial of degree $k$, every network is a polynomial of degree $\le k$, which is not dense. ∎

*Constructive 1-D proof for ReLU.* Any continuous $g$ on $[0,1]$ is uniformly approximated by a piecewise-linear interpolant $p$ with knots $0=t_0<\dots<t_{m}=1$. A piecewise-linear function with $m-1$ interior knots $t_1,\dots,t_{m-1}$ is a sum of $m-1$ ReLUs plus an affine term: with slopes $s_k$ on $[t_{k-1},t_k]$,
$$p(x)=p(0)+s_1x+\sum_{k=1}^{m-1}(s_{k+1}-s_k)\,\mathrm{ReLU}(x-t_k),$$
since each ReLU term switches on the slope change at $t_k$. So width $O(m)$ suffices, and for $g$ Lipschitz with constant $\Lambda$ the error is $\le\Lambda/m$. ∎

**Theorem 10.2 (Rates; Barron 1993, Thm 1) [S30].** If $g:\mathbb R^d\to\mathbb R$ has Fourier transform with finite first moment $C_g=\int\|\omega\|\,|\hat g(\omega)|\,d\omega$, then for every $m$ there is a one-hidden-layer sigmoidal network $f_m$ of width $m$ with
$$\|g-f_m\|_{L_2(\mu)}\le\frac{2rC_g}{\sqrt m}$$
on a ball of radius $r$, for any probability measure $\mu$. *Idea:* write $g$ as an expectation over random sigmoidal ridge functions (a "Fourier representation as a mixture"), draw $m$ of them, and apply the Maurey/Pisier $O(1/\sqrt m)$ bound for approximating a point of a convex hull by an $m$-term average. The rate is dimension-free in $m$, but $C_g$ can grow exponentially with $d$. ∎

**Theorem 10.3 (Depth separation; Telgarsky 2016) [S31].** Let $\Delta:[0,1]\to[0,1]$ be the tent map and $\Delta^{\circ k}$ its $k$-fold composition, a sawtooth with $2^{k-1}$ teeth. $\Delta^{\circ k}$ is computed exactly by a ReLU network of depth $2k$ and width $2$ (hence $O(k)$ units), but any ReLU network of depth $\ell$ and width $w$ has at most $2(2w)^\ell$ linear pieces, so a depth-$\ell$ network with fewer than $2^{(k-1)/\ell}/2$ units per layer cannot approximate $\Delta^{\circ k}$ in $L_1$ better than a constant. *Sketch:* the tent is $\mathrm{ReLU}\big(2\,\mathrm{ReLU}(x)-4\,\mathrm{ReLU}(x-1/2)\big)$ — the outer ReLU is what makes one tent two layers; composition multiplies the number of pieces, while adding units within a layer only adds pieces. A function with $2^{k-1}$ oscillations of amplitude $1$ cannot be matched by one with far fewer pieces. ∎

**Quote Telgarsky's actual numbers, not this simplification.** The statement above is the folklore form of the argument, and it is true, but **it is not Telgarsky's Theorem 1.1**. His theorem fixes $k\ge1$, $d\ge1$ and exhibits an $f:\mathbb R^d\to\mathbb R$ computed by a ReLU network with **$2k^3+8$ layers, $3k^3+12$ total nodes** and $4+d$ distinct parameters, such that every $g$ computed by a network of $\le k$ layers and $\le 2^k$ nodes has $\int_{[0,1]^d}|f-g|\ge\tfrac1{64}$ [S31 Thm 1.1]. So the real trade-off is **$\Theta(k^3)$ layers against $k$ layers with $\Omega(2^k)$ nodes**, the shallow side is limited by *total nodes* rather than width, and the separation constant is $1/64$. If you are asked for "Telgarsky's theorem" in the oral, give those.

(Montúfar et al. 2014 give the general count: a ReLU net with $L$ layers of width $m\ge d$ can have $\Omega\big((m/d)^{(L-1)d}m^d\big)$ linear regions [S37].)

**Theorem 10.4 (VC dimension of ReLU networks; Bartlett, Harvey, Liaw & Mehrabian 2019) [S32].** For ReLU networks with $W$ parameters, $U$ units and $L$ layers:
$$\mathrm{VCdim}=O(WL\log W)\quad\text{and}\quad\mathrm{VCdim}=\Omega\big(WL\log(W/L)\big),$$
so $\mathrm{VCdim}=\Theta(WL\log W)$ **provided $L\ll W^{0.99}$** — which holds for every network used in practice, but the two bounds are *not* matched in the narrow regime $W^{0.99}\ll L\ll W$, and the authors say so [S32].

For **piecewise-polynomial** activations the order is *not* the same: the upper bound picks up an extra depth-squared term, $O(WL^2+WL\log W)$ (Bartlett et al. 1998), and the tight statement is instead $\Theta(WU)$ in terms of the number of *units* [S32 Thm 8]. For sigmoids the bound is $O(W^2U^2)$ (Karpinski–Macintyre 1997) — note that the second factor counts **units**, not layer width. ∎

*Consequence.* A network with $W\gg n$ parameters has VC dimension $\gg n$, and the fundamental theorem's bound $\sqrt{d/n}$ exceeds 1: uniform convergence *over the whole class* says nothing. This is consistent with the observation below that such networks can fit random labels.

### Optimisation

**Facts.**
- Training even a 3-node network to zero error on given data is NP-complete (Blum & Rivest 1992). The empirical risk of a deep net is non-convex in $\theta$.
- For deep *linear* networks ($\sigma=\mathrm{id}$), every local minimum of the squared loss is a global minimum and all other critical points are saddles (Kawaguchi 2016) [S44] — though for three or more layers there are "bad" saddles at which the Hessian has **no** negative eigenvalue, so the strict-saddle escape result below does not cover them. Nothing comparable is known for nonlinear nets in general; spurious local minima exist for small ReLU nets (Safran–Shamir 2018).
- Gradient descent with small random initialisation avoids strict saddles almost surely (Lee et al. 2016), but can take exponentially long near them.
- **Overparameterised convergence.** For a one-hidden-layer ReLU net of width $m=\mathrm{poly}(n,1/\delta,1/\lambda_0)$ with random initialisation, gradient descent on the squared loss converges to zero training loss at a linear rate with probability $\ge1-\delta$ (Du, Zhai, Poczos & Singh 2019 [S44]; Allen-Zhu, Li & Song 2019 for deep nets). Here $\lambda_0$ is the smallest eigenvalue of the infinite-width NTK Gram matrix. The mechanism is the NTK regime below.

### The neural tangent kernel

Linearise the network around its initialisation $\theta_0$:
$$f(x;\theta)\approx f(x;\theta_0)+\langle\nabla_\theta f(x;\theta_0),\theta-\theta_0\rangle.$$
Gradient flow on $L(\theta)=\frac12\sum_i(f(x_i;\theta)-y_i)^2$ gives, with $u(t)=(f(x_i;\theta_t))_i\in\mathbb R^n$,
$$\dot\theta=-\nabla_\theta L=-\sum_i(u_i-y_i)\nabla_\theta f(x_i;\theta),\qquad
\dot u_j=\langle\nabla_\theta f(x_j;\theta),\dot\theta\rangle=-\sum_i\Theta_{\theta_t}(x_j,x_i)(u_i-y_i).$$
So the outputs evolve by $\dot u=-\Theta_t(u-y)$ where $\Theta_t$ is the $n\times n$ NTK Gram matrix at time $t$.

**Theorem 10.5 (Jacot, Gabriel & Hongler 2018, statement) [S33].** With the NTK parametrisation ($W_\ell=\frac{1}{\sqrt{m_{\ell-1}}}\tilde W_\ell$, $\tilde W_\ell$ i.i.d. standard Gaussian entries) and widths $m_1,\dots,m_{L-1}\to\infty$:

(i) **[S33 Thm 1]** for $\sigma$ Lipschitz, $\Theta_{\theta_0}$ converges in probability to a deterministic kernel $\Theta_\infty$ depending only on the depth, $\sigma$ and the initialisation variances;

(ii) **[S33 Thm 2]** for $\sigma$ **twice differentiable with bounded second derivative**, and on any horizon $[0,T]$ for which $\int_0^T\|d_t\|\,dt$ stays stochastically bounded, $\Theta_{\theta_t}\to\Theta_\infty$ *uniformly in $t\in[0,T]$*. ∎

**Two hypotheses it is tempting to drop, and should not be.** (ii) is a statement on a **finite** horizon, not "for all $t$" — the $t\to\infty$ limit taken in the Consequence below is an extrapolation, not something Theorem 2 gives. And "twice differentiable with bounded second derivative" **excludes ReLU**, which is the activation the rest of this section and the whole Du et al. line of work actually use; the ReLU case needs the separate finite-width analyses cited under Optimisation.

*Consequence.* In the limit the dynamics are linear: $u(t)-y=e^{-\Theta_\infty t}(u(0)-y)$, so if $\Theta_\infty\succ0$ then $u(t)\to y$ (zero training loss, rate governed by $\lambda_{\min}(\Theta_\infty)$), and the function learned at $t\to\infty$ is
$$f_\infty(x)=f_0(x)+\Theta_\infty(x,X)\,\Theta_\infty(X,X)^{-1}\,(y-f_0(X)),$$
kernel "ridgeless" regression with the NTK (plus the random initial function). All of the kernel theory of notes 07–08 then applies: this is a *proven* generalisation story, but for a kernel machine, not for a feature-learning network.

*Example: NTK of one neuron.* $f(x;\theta)=v\,\sigma(wx)$, $\theta=(w,v)$. $\nabla_\theta f=(v\sigma'(wx)x,\ \sigma(wx))$, so $\Theta(x,x')=v^2\sigma'(wx)\sigma'(wx')xx'+\sigma(wx)\sigma(wx')$. For ReLU with $w>0$ and $x,x'>0$: $\Theta=v^2xx'+w^2xx'=(v^2+w^2)xx'$ — a linear kernel with a random scale. Averaging over $w,v\sim N(0,1)$ over all sign patterns gives the arc-cosine-type NTK $\Theta_\infty(x,x')=\frac{\|x\|\|x'\|}{2\pi}\big((\pi-\varphi)\cos\varphi+\sin\varphi\big)+\frac{\|x\|\|x'\|}{2\pi}(\pi-\varphi)\cos\varphi$ with $\varphi$ the angle between $x,x'$ (Cho–Saul kernels).

*Limits.* The NTK regime is "lazy training" (Chizat, Oyallon & Bach 2019): parameters move by $O(1/\sqrt m)$, features do not change, and the resulting predictor is provably *worse* than practically trained networks on tasks where feature learning matters. Mean-field parametrisations (Mei–Montanari–Nguyen 2018) keep feature learning but give only weaker convergence guarantees.

### Generalisation puzzles

**Observation (Zhang, Bengio, Hardt, Recht & Vinyals 2017)** [S43]**.** Standard architectures trained by SGD reach zero training error on CIFAR-10 with *randomly permuted labels* (and on random pixels), with the same hyperparameters that generalise well on the true labels. Hence: (a) the class realised by the architecture has $\tau_{\mathcal H}(n)=2^n$ at practical $n$, so any bound of the form $L_{\mathcal D}\le L_S+\text{capacity}(\mathcal H)/\sqrt n$ with capacity measured over the whole class is vacuous; (b) explicit regularisers (weight decay, dropout, augmentation) help but are not necessary for generalisation. The explanation must involve the *algorithm* and the *data distribution*, not $\mathcal H$ alone.

**Theorem 10.6 (Implicit regularisation of GD for least squares)** [S36 Prop. 1]**.** Run gradient descent $w_{t+1}=w_t-\eta\Phi^\top(\Phi w_t-y)$ from $w_0=0$ with $0<\eta<2/\|\Phi\|_2^2$ on $\frac12\|\Phi w-y\|^2$ with $\Phi\in\mathbb R^{n\times p}$, $p\ge n$, full row rank. Then $w_t\to w^\dagger=\Phi^+y$, the minimum-$\ell_2$-norm interpolator.

*Proof.* Every iterate is a linear combination of the rows of $\Phi$: $w_{t+1}=w_t-\eta\Phi^\top r_t\in\mathrm{row}(\Phi)$ by induction from $w_0=0$. Convergence: on $\mathrm{row}(\Phi)$ the map $w\mapsto w-\eta\Phi^\top(\Phi w-y)$ is a contraction (the Hessian $\Phi^\top\Phi$ restricted to $\mathrm{row}(\Phi)$ has eigenvalues in $[\sigma_{\min}^2,\sigma_{\max}^2]$ with $\sigma_{\min}>0$, and $|1-\eta\sigma^2|<1$), so $w_t$ converges to the unique interpolator in $\mathrm{row}(\Phi)$. Any interpolator $w$ decomposes as $w=w_\parallel+w_\perp$ with $w_\parallel\in\mathrm{row}(\Phi)$, $\Phi w_\perp=0$, and $\|w\|^2=\|w_\parallel\|^2+\|w_\perp\|^2\ge\|w_\parallel\|^2$; the interpolator in $\mathrm{row}(\Phi)$ is unique (the difference of two lies in $\mathrm{row}(\Phi)\cap\ker\Phi=\{0\}$), so it is $w^\dagger$. ∎

**Theorem 10.7 (Implicit bias for logistic loss; Soudry, Hoffer, Nacson, Gunasekar & Srebro 2018, statement) [S34].** For linearly separable data and any $\beta$-smooth decreasing loss **with an exponential tail** (logistic and exponential both qualify), gradient descent with $\eta<2\beta^{-1}\sigma_{\max}^{-2}(X)$ from any $w_0$ satisfies $w_t=\hat w\log t+\rho(t)$ with $\|\rho(t)\|=O(\log\log t)$, where $\hat w$ is the hard-margin SVM solution; hence $\|w_t\|\to\infty$ and
$$\Big\|\frac{w_t}{\|w_t\|}-\frac{\hat w}{\|\hat w\|}\Big\|=O\!\Big(\frac{\log\log t}{\log t}\Big)\ \text{ in general, improving to } O\!\Big(\frac1{\log t}\Big)\ \text{ for almost every dataset.}$$
So GD "finds a margin" without any explicit regulariser — but **extraordinarily slowly**: the margin itself converges only as $O(1/\log t)$ [S34 Thm 3, Thm 5], which is why the effect is invisible on any practical training budget. Analogues exist for homogeneous deep networks (Lyu & Li 2020). ∎

**Norm-based bounds (Bartlett, Foster & Telgarsky 2017, statement) [S38].** For a network with 1-Lipschitz activations and layer matrices $A_1,\dots,A_L$, with probability $\ge1-\delta$,
$$L^{0\text{-}1}_{\mathcal D}\le\hat L_{S,\rho}+\tilde O\!\left(\frac{\|X\|_F}{\rho\,n}\prod_{\ell}\|A_\ell\|_{\sigma}\Big(\sum_\ell\frac{\|A_\ell^\top\|_{2,1}^{2/3}}{\|A_\ell\|_\sigma^{2/3}}\Big)^{3/2}\right)+O\!\Big(\sqrt{\tfrac{\log(1/\delta)}{n}}\Big),$$
where $\|\cdot\|_\sigma$ is the **spectral** norm and $\|X\|_F=\sqrt{\sum_i\|x_i\|_2^2}$. (Write $\|\cdot\|_\sigma$, not $\|\cdot\|_2$: [S38] reserves $\|\cdot\|_2$ for the entrywise, i.e. Frobenius, norm, so $\|A_\ell\|_2$ means the wrong thing there.)
The capacity is a *norm* of the trained weights (spectral norms times a stable-rank-like factor), not a parameter count, and it does distinguish true from random labels (the margin normalised by the product of spectral norms is much larger on true labels). Numerically the bounds are still far above 1 for real networks.

**PAC-Bayes (McAllester 1999; Langford–Seeger 2001; Maurer 2004; Dziugaite & Roy 2017) [S39, S40].** For a prior $P$ over hypotheses fixed before seeing $S$ and any posterior $Q$, with probability $\ge1-\delta$,
$$\mathrm{kl}\big(\hat L_S(Q)\,\|\,L_{\mathcal D}(Q)\big)\le\frac{\mathrm{KL}(Q\|P)+\log(2\sqrt n/\delta)}{n},$$
where $L(Q)=\mathbb E_{h\sim Q}L(h)$ and $\mathrm{kl}$ is the binary relative entropy. **Attribution matters here:** McAllester's 1999 original is a *square-root*-form bound; this $\mathrm{kl}$ form with the $\log(2\sqrt n/\delta)$ numerator is **Maurer (2004)** [S39], refining Langford–Seeger. Dziugaite–Roy themselves quote the Langford–Seeger variant with numerator $\log(n/\delta)$ and denominator $n-1$ [S40 Thm 2.3] — the constants differ, so say which you mean. Dziugaite–Roy take $Q$ Gaussian around the trained weights with *optimised* variances (the network is robust to that perturbation — "flat minimum"), $P$ Gaussian around the random initialisation, and obtain the first non-vacuous bounds (test error $\le0.16$ on binary MNIST) for a real network. The bound is about the stochastic network $Q$, and it certifies a specific trained model, not an algorithm.

**Nagarajan & Kolter 2019 (statement)** [S42]**.** There are simple overparameterised settings (including linear classifiers trained by GD in high dimension) where the learned predictor generalises well but *every* uniform-convergence bound, even after restricting the class to what the algorithm outputs on typical samples, is vacuous, because a perturbed sample $S'$ exists on which the same predictor errs completely. Uniform convergence may be the wrong tool for explaining these regimes.

**Double descent (Belkin, Hsu, Ma & Mandal 2019)** [S35]**.** Plot test error against model size. Classical theory predicts a U: bias falls, variance rises. Empirically, past the interpolation threshold the test error *decreases again*, often below the classical minimum. The model with $p\to\infty$ parameters trained by GD is the min-norm interpolator, which becomes *smoother* as $p$ grows because there are more directions to spread the fit over.

**Theorem 10.8 (Ridgeless least squares asymptotics; Hastie, Montanari, Rosset & Tibshirani 2022, Thm 1, isotropic case, statement) [S36].** Let $y=\langle x,\beta\rangle+\varepsilon$ with $x\sim N(0,I_p)$, $\mathrm{Var}\,\varepsilon=\sigma^2$, $\|\beta\|^2=r^2$, and let $p,n\to\infty$ with $p/n\to\gamma$. The excess risk of the min-norm least-squares estimator converges to
$$R(\gamma)=\begin{cases}\sigma^2\dfrac{\gamma}{1-\gamma}, & \gamma<1,\\[6pt]
r^2\Big(1-\dfrac1\gamma\Big)+\sigma^2\dfrac{1}{\gamma-1}, & \gamma>1.\end{cases}$$
Both branches diverge at $\gamma=1$: for $\gamma<1$ the variance term $\sigma^2\gamma/(1-\gamma)$ blows up as the smallest singular value of the $n\times p$ design goes to $0$ (Marchenko–Pastur: $\sigma_{\min}\to\sqrt n(1-\sqrt\gamma)$); for $\gamma>1$ the variance $\sigma^2/(\gamma-1)$ decreases in $\gamma$ (more parameters → smaller-norm interpolator → less variance) while the bias $r^2(1-1/\gamma)$ increases towards $r^2$ (the min-norm solution only recovers the component of $\beta$ in $\mathrm{row}(X)$, an $n$-dimensional subspace of $\mathbb R^p$), and at large $\gamma$ the risk tends to $r^2$, the null risk: all variance gone, all signal outside $\mathrm{row}(X)$ lost.

**Does the second descent beat the first minimum? In this model, never.** Read the formula: on $\gamma<1$ the risk is $\sigma^2\gamma/(1-\gamma)\to0$ as $\gamma\to0$, so the underparameterised infimum is $0$ and no overparameterised value can beat it. What the signal-to-noise ratio $\mathrm{SNR}=r^2/\sigma^2$ controls is only the *shape* of the right branch: for $\mathrm{SNR}\le1$ it decreases monotonically on $(1,\infty)$, and for $\mathrm{SNR}>1$ it has an interior local minimum. Either way [S36] states it plainly — the risk "achieves its global minimum in the underparametrized regime". The global minimum can move into $\gamma>1$ **only under model misspecification**, when there is enough approximation bias, and Theorem 10.8 as stated here is the well-specified case. For random-features models (Mei & Montanari 2022) the same picture holds with the feature count playing the role of $p$. Optimal ridge regularisation removes the peak entirely and dominates min-norm least squares at every $\gamma$ and every SNR [S36]. ∎

**Benign overfitting (Bartlett, Long, Lugosi & Tsigler 2020, statement) [S41].** For min-norm linear regression with Gaussian design of covariance $\Sigma$, the excess risk is small (interpolating noise is harmless) iff the eigenvalues $\lambda_1\ge\lambda_2\ge\dots$ of $\Sigma$ satisfy a condition on **two** notions of effective rank,
$$r_k(\Sigma)=\frac{\sum_{i>k}\lambda_i}{\lambda_{k+1}},\qquad R_k(\Sigma)=\frac{\big(\sum_{i>k}\lambda_i\big)^2}{\sum_{i>k}\lambda_i^2},$$
both of which must be large for some $k\ll n$. The picture: there must be many small-variance directions, so the noise is spread thinly over them, while the signal lives in a few large directions that are estimated well — "the number of directions in parameter space that are unimportant for prediction must significantly exceed the sample size" [S41]. Isotropic finite-dimensional covariance is *not* benign; slowly decaying spectra in high dimension are.

### What is proven, empirical, open

| Claim | Status |
|---|---|
| Shallow nets are universal approximators; $O(1/\sqrt m)$ rates for Barron functions | proven (Thm 10.1, 10.2) |
| Depth can be exponentially more efficient than width | proven for specific functions (Thm 10.3) |
| $\mathrm{VCdim}=\Theta(WL\log W)$ for ReLU nets | proven (Thm 10.4) |
| GD converges to zero training loss for very wide nets | proven in the NTK regime (Thm 10.5, Du et al.) |
| Infinite-width nets trained by GD are kernel machines | proven (Jacot et al.); does not describe practical nets |
| GD/SGD on least squares → min-norm; on separable logistic → max margin | proven (Thm 10.6, 10.7) |
| Double descent and benign overfitting in linear / random-features models | proven asymptotically (Thm 10.8, Bartlett et al. 2020) |
| Double descent in deep nets, epoch-wise double descent | empirical (Nakkiran et al. 2020) |
| Why practically trained deep nets generalise | open; norm-based and PAC-Bayes bounds exist but are loose or model-specific |
| Role of SGD noise, batch size, flat minima in generalisation | partially understood, mostly empirical |
| Scaling laws (loss vs compute/data/parameters as power laws) | empirical, with toy-model explanations |

## Worked example

*Hat function with three ReLUs.* Want $g$ on $[0,1]$ rising linearly from $0$ at $a=0.2$ to $1$ at $b=0.5$, then falling to $0$ at $c=0.8$, zero elsewhere. Slopes: $s_1=1/(b-a)=10/3$ on $[a,b]$, $s_2=-1/(c-b)=-10/3$ on $[b,c]$, $0$ after. By the slope-change formula,
$$g(x)=s_1\,\mathrm{ReLU}(x-a)+(s_2-s_1)\,\mathrm{ReLU}(x-b)+(0-s_2)\,\mathrm{ReLU}(x-c)=\tfrac{10}{3}\big[\mathrm{ReLU}(x-0.2)-2\,\mathrm{ReLU}(x-0.5)+\mathrm{ReLU}(x-0.8)\big].$$
Check $x=0.5$: $\frac{10}{3}(0.3)=1$; $x=0.65$: $\frac{10}{3}(0.45-0.30)=0.5$; $x=0.8$: $\frac{10}{3}(0.6-0.6)=0$. This is `hat_network` in the code; a sum of such hats interpolates any continuous function on a grid.

*NTK of one neuron.* $f(x)=v\,\mathrm{ReLU}(wx)$, $\theta=(w,v)=(1,2)$, inputs $x=1,x'=3$: $\nabla_\theta f(x)=(v\mathbb 1[wx>0]x,\ \mathrm{ReLU}(wx))=(2,1)$, $\nabla_\theta f(x')=(6,3)$, so $\Theta(1,3)=12+3=15=(v^2+w^2)xx'=5\cdot3$. Gradient flow on one training point $(x,y)=(1,0)$ gives $\dot u=-\Theta(1,1)(u-0)=-5u$, $u(t)=2e^{-5t}$ in the linearised model.

*Double descent numbers.* `double_descent_curve` (40 training points, noise 0.1, random ReLU features): test MSE $\approx0.08$ at $m=20$ features, $\approx2.2$ at $m=40$ (the threshold; individual runs reach $10^3$), $\approx0.13$ at $m=80$ and $\approx0.06$ at $m=800$, below the classical minimum. With noise $0.3$ the peak is $\sim11$ and the $m=800$ error ($0.23$) stays above the $m=20$ error ($0.17$): interpolating noisy labels is only benign when the noise is small.

## Pitfalls

- "Universal approximation" is about existence of weights, not about finding them by GD, and not about sample complexity; the width needed can be exponential in $d$.
- Depth separation results are for specific hard functions; they do not say depth always helps.
- VC bounds are correct for neural networks; they are just vacuous when $W\gg n$. The theorem is not "wrong", its hypothesis class is too big.
- The NTK regime requires a specific parametrisation and initialisation scale; standard-parametrisation nets with normal learning rates leave the regime and learn features.
- Double descent is a function of *model size at fixed $n$* (or of $n$ at fixed model size, "sample-wise" double descent); do not confuse it with the training-loss curve over epochs.
- Ridge regularisation with the right $\lambda$ removes the double-descent peak; the peak is an artefact of *ridgeless* fitting at $p\approx n$.
- PAC-Bayes bounds certify a randomised predictor $Q$ and require the prior to be data-independent (or chosen by a data-splitting trick).
- Min-norm implicit bias is specific to squared loss and initialisation at $0$ (or in $\mathrm{row}(\Phi)$); other losses/initialisations give other biases.

## Questions

**Q: State the universal approximation theorem precisely and give the idea of the proof.**
**A:** For compact $K$ and continuous non-polynomial $\sigma$, one-hidden-layer networks are dense in $C(K)$. Proof: if not dense, Hahn–Banach + Riesz give a nonzero signed measure $\mu$ annihilating all $\sigma(\langle w,x\rangle+b)$; for a sigmoid, scaling $w,b$ gives indicators of halfspaces, so $\mu$ vanishes on all halfspaces, hence $\mu=0$.

**Q: Construct a ReLU network computing a hat function.**
**A:** $\frac{1}{b-a}\mathrm{ReLU}(x-a)-\big(\frac{1}{b-a}+\frac{1}{c-b}\big)\mathrm{ReLU}(x-b)+\frac{1}{c-b}\mathrm{ReLU}(x-c)$; three units, slopes change at the knots.

**Q: Why do the VC bounds from note 04 say nothing about a ResNet on CIFAR-10?**
**A:** $\mathrm{VCdim}=\Theta(WL\log W)$ with $W\sim10^7\gg n=5\cdot10^4$; the estimation term $\sqrt{d/n}>1$. Zhang et al. confirm the class shatters the training set (random labels are fit).

**Q: What is the NTK and what does it imply for gradient flow on the squared loss?**
**A:** $\Theta(x,x')=\langle\nabla_\theta f(x),\nabla_\theta f(x')\rangle$. Outputs obey $\dot u=-\Theta_t(u-y)$; in the infinite-width NTK-parametrised limit $\Theta_t\equiv\Theta_\infty$ is deterministic and constant, so $u(t)-y=e^{-\Theta_\infty t}(u(0)-y)\to0$ and the learned function is kernel regression with $\Theta_\infty$.

**Q: Prove that GD from zero on least squares converges to the min-norm interpolator.**
**A:** Iterates stay in $\mathrm{row}(\Phi)$; the restricted problem is strongly convex so GD converges to the unique interpolator in $\mathrm{row}(\Phi)$; any interpolator has a $\ker\Phi$ component that only adds norm, so that one is min-norm.

**Q: Explain double descent in the random-features / linear model. Where is the peak and why?**
**A:** At $p\approx n$: the min-norm interpolator has variance $\propto\sigma^2\sum_j1/s_j^2$ over the design's singular values, and $s_{\min}\to0$ at $p=n$. For $p>n$ the norm of the interpolator shrinks with $p$, so variance falls (second descent), at the price of a bias $r^2(1-1/\gamma)$. Ridge with optimal $\lambda$ has no peak.

**Q: What does "implicit regularisation" mean? Give two proven instances.**
**A:** The optimisation algorithm, not an explicit penalty, selects a particular low-complexity solution among all minimisers. GD on least squares → min-$\ell_2$-norm interpolator; GD on logistic loss with separable data → max-margin direction.

**Q: Name one non-vacuous generalisation bound for a real neural network and its main ingredient.**
**A:** Dziugaite–Roy 2017, PAC-Bayes with a Gaussian posterior around the trained weights whose variances are optimised to maximise flatness while keeping $\mathrm{KL}(Q\|P)$ small.

## Code

`src/py/deep_theory.py`: `MLP(hidden, act)` is a one-hidden-layer network with hand-written backpropagation (`gradients`, checked against finite differences in the test) trained by Adam; `universal_approximation_demo` fits $\sin(2\pi x)+$ a bump with widths 2–128 and prints the decreasing MSE; `hat_network(a,b,c)` is the explicit 3-ReLU construction of the worked example; `random_relu_features`, `min_norm_least_squares` and `double_descent_curve` produce the test-error-vs-width curve with its peak at $m=n$ and, with `lam>0`, show that ridge removes the peak (`python deep_theory.py --png` saves the plot). `gd_least_squares(Phi, y, steps)` runs Theorem 10.6's gradient descent from zero; `test_deep_theory.py` checks it converges to `min_norm_least_squares` (pseudo-inverse). `ridgeless_risk(gamma, r2, sigma2)` is Theorem 10.8's formula and `min_norm_risk_simulation(n, p, r2, sigma2, trials, rng)` reproduces it (the demo prints both branches; below the threshold the finite-$n$ value is exactly $\sigma^2p/(n-p-1)$).

## References

Registered in [`../refs/SOURCES.md`](../refs/SOURCES.md) as S9–S12 and S29–S44. Every theorem statement above was checked against the primary paper on 2026-09-22; four errors found and corrected are recorded in `CHANGELOG.md`.

- **Telgarsky, *Deep learning theory lecture notes* [S11]** — the single best free companion to this note, and the source of its approximation/optimisation/generalisation organisation. No licence statement, so cite only; `../refs/fetch-sources.sh` downloads it.
- Shalev-Shwartz & Ben-David, *Understanding Machine Learning* [S9], Ch. 20 (neural networks: expressivity, VC dimension, hardness).
- Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning*, Ch. 3.4 (Rademacher of neural networks), Ch. 4 (margin bounds).
- Cybenko (1989) "Approximation by superpositions of a sigmoidal function"; Hornik (1991); Leshno, Lin, Pinkus & Schocken (1993); Barron (1993) "Universal approximation bounds for superpositions of a sigmoidal function"; Telgarsky (2016) "Benefits of depth in neural networks"; Montúfar, Pascanu, Cho & Bengio (2014); Bartlett, Harvey, Liaw & Mehrabian (2019) "Nearly-tight VC-dimension and pseudodimension bounds for piecewise linear neural networks".
- Blum & Rivest (1992); Kawaguchi (2016) "Deep learning without poor local minima"; Du, Zhai, Poczos & Singh (2019) "Gradient descent provably optimizes over-parameterized neural networks"; Jacot, Gabriel & Hongler (2018) "Neural tangent kernel"; Chizat, Oyallon & Bach (2019) "On lazy training"; Arora et al. (2019) "Fine-grained analysis of optimization and generalization for overparameterized two-layer neural networks".
- Zhang, Bengio, Hardt, Recht & Vinyals (2017) "Understanding deep learning requires rethinking generalization"; Soudry et al. (2018) "The implicit bias of gradient descent on separable data"; Bartlett, Foster & Telgarsky (2017) "Spectrally-normalized margin bounds"; Dziugaite & Roy (2017) "Computing nonvacuous generalization bounds"; Nagarajan & Kolter (2019) "Uniform convergence may be unable to explain generalization in deep learning"; Belkin, Hsu, Ma & Mandal (2019) "Reconciling modern machine-learning practice and the classical bias–variance trade-off"; Hastie, Montanari, Rosset & Tibshirani (2022) "Surprises in high-dimensional ridgeless least squares interpolation"; Bartlett, Long, Lugosi & Tsigler (2020) "Benign overfitting in linear regression"; Nakkiran et al. (2020) "Deep double descent".
