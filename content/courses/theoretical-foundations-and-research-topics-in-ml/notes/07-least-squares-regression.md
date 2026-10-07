# 07 Least-squares regression

Least squares is the one learning problem where everything can be computed in closed form: the ERM solution, its geometry (a projection), its bias and variance, the effect of Tikhonov regularisation (ridge), and its kernelised version.
It is therefore the reference model for the abstract theory of notes 03–06: the fixed-design analysis gives an *exact* estimation error $\sigma^2d/n$ to compare with the $O(\sqrt{d/n})$ uniform-convergence bounds, ridge is the concrete instance of RLM and of the bias–variance trade-off, and kernel ridge regression is the first application of the representer theorem (note 08).
The reader is a physicist; linear algebra is assumed.

## Definitions

1. **Regression setting.** $\mathcal X=\mathbb R^d$, $\mathcal Y=\mathbb R$, squared loss $\ell(h(x),y)=(h(x)-y)^2$.
   Linear predictors $h_w(x)=\langle w,x\rangle$ (an intercept is absorbed by appending a constant feature $1$).
   $L_{\mathcal D}(w)=\mathbb E(\langle w,x\rangle-y)^2$, $L_S(w)=\frac1n\sum_i(\langle w,x_i\rangle-y_i)^2$.

2. **Design matrix.** $X\in\mathbb R^{n\times d}$ with rows $x_i^\top$; $y\in\mathbb R^n$.
   Then $L_S(w)=\frac1n\|Xw-y\|^2$. **Fixed design:** $X$ is treated as deterministic and randomness comes only from the noise. **Random design:** $x_i\sim\mathcal D_x$ i.i.d.

3. **Well-specified model.** $y=Xw^*+\epsilon$ with $\mathbb E\epsilon=0$, $\mathrm{Cov}(\epsilon)=\sigma^2I_n$ (no distributional assumption beyond second moments unless stated).
   More generally $y_i=f(x_i)+\epsilon_i$ with an arbitrary regression function $f$.

4. **Ordinary least squares (OLS).** $\hat w\in\arg\min_w\|Xw-y\|^2$ (ERM). **Hat matrix** $H=X(X^\top X)^{-1}X^\top$ when $X^\top X$ is invertible (i.e. $\mathrm{rank}X=d\le n$); fitted values $\hat y=X\hat w=Hy$; residual $r=y-\hat y$.

5. **Moore–Penrose pseudo-inverse.** For $X=U\Sigma V^\top$ (thin SVD, $\Sigma=\mathrm{diag}(\sigma_1,\dots,\sigma_r)$, $r=\mathrm{rank}X$), $X^+=V\Sigma^{-1}U^\top$.
   When $X^\top X$ is invertible, $X^+=(X^\top X)^{-1}X^\top$.

6. **Ridge regression / Tikhonov.** For $\lambda>0$, $\hat w_\lambda=\arg\min_w\big[\|Xw-y\|^2+\lambda\|w\|^2\big]$.
   (In the per-sample convention $\frac1n\|Xw-y\|^2+\lambda'\|w\|^2$ of note 06, $\lambda=n\lambda'$.) **Ridge hat matrix** $H_\lambda=X(X^\top X+\lambda I)^{-1}X^\top$; **effective degrees of freedom** $\mathrm{df}(\lambda)=\mathrm{tr}H_\lambda$.

7. **Bias–variance decomposition.** For a fixed test point $x$, a training set $S$ (random), an estimator $\hat f_S$, and $y=f(x)+\epsilon$ with $\epsilon$ independent of $S$, $\mathbb E\epsilon=0$, $\mathrm{Var}\,\epsilon=\sigma^2$: $\mathrm{Bias}(x)=\mathbb E_S\hat f_S(x)-f(x)$, $\mathrm{Var}(x)=\mathbb E_S(\hat f_S(x)-\mathbb E_S\hat f_S(x))^2$.

8. **Kernel ridge regression (KRR).** Given a PSD kernel $k$ with feature map $\phi$ (note 08), Gram matrix $K_{ij}=k(x_i,x_j)$, KRR is ridge regression on $\Phi=[\phi(x_1)^\top;\dots;\phi(x_n)^\top]$, expressed through $K=\Phi\Phi^\top$: $\hat\alpha=(K+\lambda I)^{-1}y$, $\hat f(x)=\sum_i\hat\alpha_ik(x_i,x)$.

## Results

**Theorem 7.1 (normal equations and closed form)** [S9 §9.2.1; S12 ch. 3]**.** $w$ minimises $\|Xw-y\|^2$ iff $X^\top Xw=X^\top y$.
If $\mathrm{rank}X=d$ the minimiser is unique, $\hat w=(X^\top X)^{-1}X^\top y$.
In general the set of minimisers is $\{X^+y+v:v\in\ker X\}$ and $X^+y$ is the unique minimiser of smallest Euclidean norm.

*Proof.* $J(w)=\|Xw-y\|^2$ is convex with $\nabla J=2X^\top(Xw-y)$, so stationarity $\Leftrightarrow$ global minimality $\Leftrightarrow X^\top Xw=X^\top y$.
If $X^\top X$ is invertible, solve. Otherwise write $X=U\Sigma V^\top$ and $w=Vz+v$ with $v\in\ker X=(\mathrm{row}\,X)^\perp$, $z\in\mathbb R^r$: $\|Xw-y\|^2=\|U\Sigma z-y\|^2=\|\Sigma z-U^\top y\|^2+\|(I-UU^\top)y\|^2$ (Pythagoras, $U$ has orthonormal columns), minimised uniquely at $z=\Sigma^{-1}U^\top y$, i.e. $Vz=X^+y$; $v$ is free.
Since $Vz\perp v$, $\|w\|^2=\|X^+y\|^2+\|v\|^2$ is minimal at $v=0$. ∎

**Theorem 7.2 (geometry)** [S12 ch. 3]**.** With $\mathrm{rank}X=d$: (a) $H^2=H$ and $H^\top=H$, so $H$ is the orthogonal projector onto $\mathrm{col}(X)$; (b) $\mathrm{tr}H=d$; (c) the residual $r=(I-H)y$ is orthogonal to every column of $X$: $X^\top r=0$; (d) $\|y\|^2=\|\hat y\|^2+\|r\|^2$.

*Proof.* (a) $H^2=X(X^\top X)^{-1}X^\top X(X^\top X)^{-1}X^\top=X(X^\top X)^{-1}X^\top=H$; $H^\top=X((X^\top X)^{-1})^\top X^\top=H$ since $X^\top X$ is symmetric.
An idempotent symmetric matrix is an orthogonal projector; its range is $\mathrm{col}(X)$ because $HXa=Xa$ and $Hy\in\mathrm{col}(X)$ for all $y$.
(b) $\mathrm{tr}H=\mathrm{tr}\big((X^\top X)^{-1}X^\top X\big)=\mathrm{tr}I_d=d$.
(c) $X^\top(I-H)=X^\top-X^\top X(X^\top X)^{-1}X^\top=0$. (d) $\hat y\perp r$ by (c) since $\hat y\in\mathrm{col}(X)$. ∎

**Theorem 7.3 (statistical properties under the well-specified model)** [S12 ch. 3]**.** Let $y=Xw^*+\epsilon$, $\mathbb E\epsilon=0$, $\mathrm{Cov}\,\epsilon=\sigma^2I$, $X$ fixed with rank $d$.
Then
(a) $\mathbb E\hat w=w^*$ (unbiased);
(b) $\mathrm{Cov}(\hat w)=\sigma^2(X^\top X)^{-1}$;
(c) $\mathbb E\|X\hat w-Xw^*\|^2=\sigma^2d$, i.e. the in-sample excess risk $\frac1n\mathbb E\|X\hat w-Xw^*\|^2=\sigma^2d/n$;
(d) $\mathbb E\|r\|^2=\sigma^2(n-d)$, so $\hat\sigma^2=\|r\|^2/(n-d)$ is unbiased for $\sigma^2$.

*Proof.* $\hat w=(X^\top X)^{-1}X^\top(Xw^*+\epsilon)=w^*+(X^\top X)^{-1}X^\top\epsilon$.
(a) Take expectations. (b) $\mathrm{Cov}(\hat w)=(X^\top X)^{-1}X^\top\,\sigma^2I\,X(X^\top X)^{-1}=\sigma^2(X^\top X)^{-1}$.
(c) $X\hat w-Xw^*=H\epsilon$, and $\mathbb E\|H\epsilon\|^2=\mathbb E\,\epsilon^\top H^\top H\epsilon=\mathbb E\,\epsilon^\top H\epsilon=\mathrm{tr}(H\,\mathrm{Cov}\,\epsilon)=\sigma^2\mathrm{tr}H=\sigma^2d$.
(d) $r=(I-H)(Xw^*+\epsilon)=(I-H)\epsilon$; $I-H$ is a projector of rank $n-d$, so $\mathbb E\|r\|^2=\sigma^2\mathrm{tr}(I-H)=\sigma^2(n-d)$. ∎

*Out-of-sample heuristic.* In random design with $\mathbb E[xx^\top]=\Sigma$, the excess risk of $\hat w$ on a fresh point is $L_{\mathcal D}(\hat w)-L_{\mathcal D}(w^*)=(\hat w-w^*)^\top\Sigma(\hat w-w^*)$, with conditional expectation $\sigma^2\mathrm{tr}\big(\Sigma(X^\top X)^{-1}\big)$.
Since $X^\top X\approx n\Sigma$ by the law of large numbers, this is $\approx\sigma^2d/n$ — the same $d/n$ as in-sample (exactly $\sigma^2d/(n-d-1)$ for Gaussian design).
Compare with uniform convergence: ERM in a $d$-parameter class gives $O(\sqrt{d/n})$ for *bounded* losses; for squared loss the well-specified rate is the faster $O(d/n)$ — see Theorem 7.9(d).

**Theorem 7.4 (Gauss–Markov)** [S12 ch. 3]**.** Under the assumptions of 7.3, among all linear unbiased estimators $\tilde w=Cy$ ($C\in\mathbb R^{d\times n}$, $CX=I_d$), OLS has the smallest covariance in the PSD order: $\mathrm{Cov}(\tilde w)-\mathrm{Cov}(\hat w)\succeq0$.

*Proof.* Write $C=(X^\top X)^{-1}X^\top+D$; unbiasedness $CX=I$ forces $DX=0$.
Then $\mathrm{Cov}(Cy)=\sigma^2CC^\top=\sigma^2\big[(X^\top X)^{-1}+(X^\top X)^{-1}X^\top D^\top+DX(X^\top X)^{-1}+DD^\top\big]=\sigma^2(X^\top X)^{-1}+\sigma^2DD^\top$, and $DD^\top\succeq0$. ∎

**Theorem 7.5 (ridge regression)** [S9 §13.4; S10 §11.3]**.** (a) $\hat w_\lambda=(X^\top X+\lambda I)^{-1}X^\top y$, unique for every $\lambda>0$ regardless of rank.
(b) With $X=U\Sigma V^\top$ (full SVD, $\sigma_j=0$ beyond the rank),
$$\hat w_\lambda=\sum_j\frac{\sigma_j}{\sigma_j^2+\lambda}\,(u_j^\top y)\,v_j,\qquad\hat y_\lambda=H_\lambda y=\sum_j\frac{\sigma_j^2}{\sigma_j^2+\lambda}(u_j^\top y)\,u_j,\qquad\mathrm{df}(\lambda)=\sum_j\frac{\sigma_j^2}{\sigma_j^2+\lambda}.$$
OLS corresponds to $\lambda=0$ with factors $1$ on the range; ridge shrinks the component along $u_j$ by the factor $\sigma_j^2/(\sigma_j^2+\lambda)\in(0,1)$, most strongly in directions of small singular value.
$\mathrm{df}(\lambda)$ decreases from $\mathrm{rank}X$ to $0$ as $\lambda$ goes from $0$ to $\infty$.
(c) Under the well-specified model, $\mathbb E\hat w_\lambda=w^*-\lambda(X^\top X+\lambda I)^{-1}w^*$ (biased towards $0$) and $\mathrm{Cov}(\hat w_\lambda)=\sigma^2(X^\top X+\lambda I)^{-1}X^\top X(X^\top X+\lambda I)^{-1}\preceq\mathrm{Cov}(\hat w)$.
(d) *Bayesian reading:* if $w\sim N(0,\tau^2I)$ a priori and $\epsilon\sim N(0,\sigma^2I)$, the posterior mode (and mean) is $\hat w_\lambda$ with $\lambda=\sigma^2/\tau^2$.

*Proof.* (a) The objective $\|Xw-y\|^2+\lambda\|w\|^2$ is $2\lambda$-strongly convex (note 06, Theorem 6.5); its gradient $2X^\top(Xw-y)+2\lambda w$ vanishes iff $(X^\top X+\lambda I)w=X^\top y$, and $X^\top X+\lambda I\succeq\lambda I\succ0$.
(b) $X^\top X=V\Sigma^2V^\top$, so $(X^\top X+\lambda I)^{-1}=V(\Sigma^2+\lambda I)^{-1}V^\top$ and $X^\top y=V\Sigma U^\top y$; multiply.
For $H_\lambda=X(X^\top X+\lambda I)^{-1}X^\top=U\Sigma(\Sigma^2+\lambda I)^{-1}\Sigma U^\top$; the trace is the sum of the diagonal factors.
(c) Substitute $y=Xw^*+\epsilon$: $\mathbb E\hat w_\lambda=(X^\top X+\lambda I)^{-1}X^\top Xw^*=(X^\top X+\lambda I)^{-1}\big[(X^\top X+\lambda I)-\lambda I\big]w^*$.
The covariance formula is direct; in the SVD basis its eigenvalues are $\sigma^2\sigma_j^2/(\sigma_j^2+\lambda)^2\le\sigma^2/\sigma_j^2$.
(d) $-\log p(w\mid y)=\frac{1}{2\sigma^2}\|Xw-y\|^2+\frac1{2\tau^2}\|w\|^2+\mathrm{const}$; multiply by $2\sigma^2$. ∎

**Theorem 7.6 (bias–variance decomposition)** [S12 ch. 3]**.** Fix $x$. Let $y=f(x)+\epsilon$ with $\epsilon$ independent of $S$, $\mathbb E\epsilon=0$, $\mathrm{Var}\,\epsilon=\sigma^2$.
Then
$$\mathbb E_{S,\epsilon}\big(\hat f_S(x)-y\big)^2=\sigma^2+\big(\mathbb E_S\hat f_S(x)-f(x)\big)^2+\mathrm{Var}_S\hat f_S(x).$$

*Proof.* Abbreviate $\hat f=\hat f_S(x)$, $\bar f=\mathbb E_S\hat f$, $f=f(x)$. Write $\hat f-y=(\hat f-\bar f)+(\bar f-f)-\epsilon$ and expand the square:
$$(\hat f-\bar f)^2+(\bar f-f)^2+\epsilon^2+2(\hat f-\bar f)(\bar f-f)-2(\hat f-\bar f)\epsilon-2(\bar f-f)\epsilon.$$
Take $\mathbb E_{S,\epsilon}$. The three squares give $\mathrm{Var}_S\hat f$, $\mathrm{Bias}^2$ and $\sigma^2$.
Cross term 1: $(\bar f-f)$ is a constant and $\mathbb E_S(\hat f-\bar f)=0$, so it vanishes.
Cross term 2: $\hat f$ depends on $S$ only and $\epsilon$ is independent of $S$ with mean $0$, so $\mathbb E[(\hat f-\bar f)\epsilon]=\mathbb E[\hat f-\bar f]\,\mathbb E\epsilon=0$.
Cross term 3: $(\bar f-f)\mathbb E\epsilon=0$. ∎

*For OLS in the well-specified fixed-design case*, $\mathrm{Bias}=0$ at every training point and $\frac1n\sum_i\mathrm{Var}(\hat f(x_i))=\frac1n\sigma^2\mathrm{tr}(H)=\sigma^2d/n$ (Theorem 7.3(c)); for ridge, $\frac1n\sum_i\mathrm{Var}=\sigma^2\mathrm{tr}(H_\lambda^2)/n\le\sigma^2\mathrm{df}(\lambda)/n$ and the bias is nonzero (Theorem 7.9(c)).

**Theorem 7.7 (push-through identity)** [S10 Lemma 11.12]**.** For any $X\in\mathbb R^{n\times d}$ and $\lambda>0$: $(X^\top X+\lambda I_d)^{-1}X^\top=X^\top(XX^\top+\lambda I_n)^{-1}$.

*Proof.* Both $X^\top X+\lambda I_d$ and $XX^\top+\lambda I_n$ are invertible ($\succeq\lambda I$).
The identity $X^\top(XX^\top+\lambda I_n)=X^\top XX^\top+\lambda X^\top=(X^\top X+\lambda I_d)X^\top$ holds trivially.
Multiply on the left by $(X^\top X+\lambda I_d)^{-1}$ and on the right by $(XX^\top+\lambda I_n)^{-1}$. ∎

**Theorem 7.8 (kernel ridge regression)** [S10 §11.3.3; S12 ch. 7]**.** Let $\Phi$ be the $n\times D$ feature matrix ($D$ possibly infinite) and $K=\Phi\Phi^\top$.
Then the ridge solution in feature space satisfies
$$\hat w_\lambda=\Phi^\top\hat\alpha,\qquad\hat\alpha=(K+\lambda I_n)^{-1}y,\qquad\hat f(x)=\langle\hat w_\lambda,\phi(x)\rangle=\sum_{i=1}^n\hat\alpha_i\,k(x_i,x),$$
and $\hat y_\lambda=K(K+\lambda I)^{-1}y$, so $H_\lambda=K(K+\lambda I)^{-1}$ and $\mathrm{df}(\lambda)=\sum_j\frac{\mu_j}{\mu_j+\lambda}$ with $\mu_j$ the eigenvalues of $K$.

*Proof (via the identity).* By Theorem 7.5(a) and 7.7, $\hat w_\lambda=(\Phi^\top\Phi+\lambda I)^{-1}\Phi^\top y=\Phi^\top(\Phi\Phi^\top+\lambda I)^{-1}y=\Phi^\top\hat\alpha$.
Then $\langle\hat w_\lambda,\phi(x)\rangle=\hat\alpha^\top\Phi\phi(x)=\sum_i\hat\alpha_ik(x_i,x)$, and $\Phi\hat w_\lambda=K\hat\alpha$.
Note $K$ has eigenvalues $\mu_j=\sigma_j^2$ (the nonzero ones), consistent with 7.5(b).

*Proof (via the representer theorem, note 08).* The objective $\sum_i(\langle w,\phi(x_i)\rangle-y_i)^2+\lambda\|w\|^2$ has the form $c\big((\langle w,\phi(x_i)\rangle)_i\big)+\Omega(\|w\|)$ with $\Omega$ strictly increasing, so the minimiser lies in $\mathrm{span}\{\phi(x_i)\}$: $w=\Phi^\top\alpha$.
Substituting, $\|K\alpha-y\|^2+\lambda\alpha^\top K\alpha$; its gradient $2K(K\alpha-y)+2\lambda K\alpha=2K\big[(K+\lambda I)\alpha-y\big]$ vanishes at $\alpha=(K+\lambda I)^{-1}y$ (and any other stationary $\alpha$ differs by an element of $\ker K$, giving the same $w$). ∎

*Complexity.* Primal: form $X^\top X$ in $O(nd^2)$, solve in $O(d^3)$.
Dual: form $K$ in $O(n^2d)$ (or $O(n^2\cdot\mathrm{cost}(k))$), solve in $O(n^3)$, predict in $O(n)$ kernel evaluations.
Use the primal when $d\ll n$, the dual when $d\gg n$ or $d=\infty$ (Gaussian kernel).
Approximations (Nyström, random features) bring the dual to $O(nm^2)$ for $m\ll n$ landmarks.

**Theorem 7.9 (generalisation bounds for regression)** [S10 Thm 11.3, Thm 11.11; S9 Thm 13.1]**.**

(a) *Rademacher bound, bounded linear class.* Let $\mathcal H=\{x\mapsto\langle w,x\rangle:\|w\|\le B\}$, $\|x\|\le R$, $|y|\le Y$ almost surely, and $M=(BR+Y)^2$.
Then $\mathfrak R_S(\ell\circ\mathcal H)\le2(BR+Y)\,\mathfrak R_S(\mathcal H)\le\frac{2(BR+Y)BR}{\sqrt n}$, and with probability $\ge1-\delta$, for all $w$ with $\|w\|\le B$:
$$L_{\mathcal D}(w)\le L_S(w)+\frac{4(BR+Y)BR}{\sqrt n}+(BR+Y)^2\sqrt{\frac{\log(1/\delta)}{2n}}.$$

(b) *Well-specified fixed design, OLS:* $\frac1n\mathbb E\|X\hat w-Xw^*\|^2=\sigma^2d/n$ (Theorem 7.3(c)).

(c) *Well-specified fixed design, ridge:*
$$\frac1n\mathbb E\|X\hat w_\lambda-Xw^*\|^2=\frac1n\Big[\|(I-H_\lambda)Xw^*\|^2+\sigma^2\mathrm{tr}(H_\lambda^2)\Big]\le\frac{\lambda\|w^*\|^2}{4n}+\frac{\sigma^2\mathrm{df}(\lambda)}{n}.$$
In the per-sample convention $\lambda=n\lambda'$: $\le\frac{\lambda'}4\|w^*\|^2+\frac{\sigma^2}n\mathrm{df}(n\lambda')$ — a bias term linear in $\lambda'$ and a variance term $\sigma^2\times$(effective dimension)$/n$.

(d) *Fast rates (statement).* For squared loss with bounded predictors and responses, the excess risk of ERM (or of ridge with well-chosen $\lambda$) over a $d$-dimensional class is $O\big((d+\log(1/\delta))/n\big)$ with high probability, not $O(\sqrt{d/n})$.
Reason: the excess loss $\ell(w,z)-\ell(w^*,z)$ has variance controlled by its mean (Bernstein condition, a consequence of strong convexity of $u\mapsto(u-y)^2$ and the projection structure of $w^*$), so Bernstein's inequality and a localised Rademacher analysis (Bartlett–Bousquet–Mendelson 2005) replace Hoeffding's $1/\sqrt n$ by $1/n$.

*Proof of (a).* For $\|w\|\le B$, $|\langle w,x\rangle|\le BR$.
On $u\in[-BR,BR]$ the map $\phi_i(u)=(u-y_i)^2$ has derivative $2(u-y_i)$, bounded by $2(BR+Y)$, so each $\phi_i$ is $2(BR+Y)$-Lipschitz; the loss takes values in $[0,M]$.
Talagrand's contraction lemma (note 05, Theorem 5.5, which allows $i$-dependent $\phi_i$) gives $\mathfrak R_S(\ell\circ\mathcal H)\le2(BR+Y)\mathfrak R_S(\mathcal H)$, and $\mathfrak R_S(\mathcal H)\le BR/\sqrt n$ by Theorem 5.7.
Apply the Rademacher generalisation theorem (5.3) to $\ell\circ\mathcal H/M$ (values in $[0,1]$) and multiply back by $M$: $L_{\mathcal D}\le L_S+2\mathfrak R_n(\ell\circ\mathcal H)+M\sqrt{\log(1/\delta)/(2n)}$. ∎

*Proof of (c).* $X\hat w_\lambda=H_\lambda y=H_\lambda Xw^*+H_\lambda\epsilon$, so $X\hat w_\lambda-Xw^*=-(I-H_\lambda)Xw^*+H_\lambda\epsilon$; the first term is deterministic, the second has mean zero, so the expected squared norm is the sum $\|(I-H_\lambda)Xw^*\|^2+\sigma^2\mathrm{tr}(H_\lambda^\top H_\lambda)$.
In the SVD basis, $Xw^*=\sum_j\sigma_j(v_j^\top w^*)u_j$ and $I-H_\lambda$ multiplies the $u_j$-component by $\frac\lambda{\sigma_j^2+\lambda}$, hence
$$\|(I-H_\lambda)Xw^*\|^2=\sum_j\frac{\lambda^2\sigma_j^2}{(\sigma_j^2+\lambda)^2}(v_j^\top w^*)^2\le\frac\lambda4\sum_j(v_j^\top w^*)^2=\frac\lambda4\|w^*\|^2,$$
using $\frac{ab}{(a+b)^2}\le\frac14$ with $a=\sigma_j^2$, $b=\lambda$.
And $\mathrm{tr}(H_\lambda^2)=\sum_j\big(\frac{\sigma_j^2}{\sigma_j^2+\lambda}\big)^2\le\sum_j\frac{\sigma_j^2}{\sigma_j^2+\lambda}=\mathrm{df}(\lambda)$.
Divide by $n$. ∎

*Reading (c).* If the features are isotropic with $\|x_i\|\approx\sqrt d$ then $\sigma_j^2\approx n$ and $\mathrm{df}(\lambda)\approx\frac{dn}{n+\lambda}$; for $\lambda\ll n$ ridge behaves like OLS ($\sigma^2d/n$), for $\lambda\gg n$ the variance is $\approx\sigma^2d/\lambda$ at the price of bias $\le\lambda\|w^*\|^2/(4n)$.
If the spectrum of $X^\top X$ decays, $\mathrm{df}(\lambda)$ can be far below $d$ — this is the mechanism by which ridge/KRR work in infinite dimension: the effective dimension, not $d$, enters.

## Worked example

**3-point OLS by hand.** Data $(x,y)\in\{(0,1),(1,2),(2,2)\}$, model $y=w_0+w_1x$. Design matrix with intercept column:
$$X=\begin{pmatrix}1&0\\1&1\\1&2\end{pmatrix},\quad y=\begin{pmatrix}1\\2\\2\end{pmatrix},\quad X^\top X=\begin{pmatrix}3&3\\3&5\end{pmatrix},\quad X^\top y=\begin{pmatrix}5\\6\end{pmatrix}.$$
$\det(X^\top X)=15-9=6$, $(X^\top X)^{-1}=\frac16\begin{pmatrix}5&-3\\-3&3\end{pmatrix}$, so
$$\hat w=\frac16\begin{pmatrix}25-18\\-15+18\end{pmatrix}=\begin{pmatrix}7/6\\1/2\end{pmatrix}.$$
Fitted values $\hat y=(7/6,\,5/3,\,13/6)$, residuals $r=(-1/6,\,1/3,\,-1/6)$.
Checks (Theorem 7.2(c)): $\sum r_i=0$ and $\sum x_ir_i=0+\frac13-\frac13=0$.
$\mathrm{RSS}=\|r\|^2=\frac1{36}+\frac19+\frac1{36}=\frac16$; $\hat\sigma^2=\mathrm{RSS}/(n-d)=\frac16$; $\mathrm{Cov}(\hat w)=\hat\sigma^2(X^\top X)^{-1}=\frac1{36}\begin{pmatrix}5&-3\\-3&3\end{pmatrix}$, so the slope has standard error $\sqrt{3/36}\approx0.29$. `ols(X, y)` and `hat_matrix(X)` reproduce these; the hat matrix here is $H=\frac16\begin{pmatrix}5&2&-1\\2&2&2\\-1&2&5\end{pmatrix}$ with $\mathrm{tr}H=2$.

**Ridge with $\lambda=1$ on the same $2\times2$ system.** $X^\top X+I=\begin{pmatrix}4&3\\3&6\end{pmatrix}$, determinant $15$, inverse $\frac1{15}\begin{pmatrix}6&-3\\-3&4\end{pmatrix}$:
$$\hat w_1=\frac1{15}\begin{pmatrix}30-18\\-15+24\end{pmatrix}=\begin{pmatrix}0.8\\0.6\end{pmatrix}\quad\text{vs}\quad\hat w=\begin{pmatrix}1.167\\0.5\end{pmatrix}.$$
$\|\hat w\|^2=1.611$ shrinks to $\|\hat w_1\|^2=1.0$, although the slope coordinate *grew* — ridge shrinks along the eigenvectors of $X^\top X$, not coordinatewise.
Eigenvalues of $X^\top X$: $\sigma_j^2=4\pm\sqrt{10}\approx7.16,\,0.84$; shrinkage factors $\sigma_j^2/(\sigma_j^2+1)\approx0.88,\,0.46$; $\mathrm{df}(1)\approx1.33$ (down from $2$).
The weak direction (roughly $(1,-1)/\sqrt2$, "intercept up, slope down") is halved.
A diagonal toy makes the factors visible directly: $X=\mathrm{diag}(2,1)$, $y=(2,1)$ gives OLS $w=(1,1)$ and ridge $w_1=(\tfrac45,\tfrac12)$, exactly the factors $\frac{4}{4+1},\frac{1}{1+1}$.
(In practice one does not penalise the intercept; centre $y$ and the columns of $X$ first.) `ridge(X, y, lam)` implements 7.5(a).

**Bias–variance simulation (qualitative).** `bias_variance_simulation(f, n, sigma, degrees, trials, rng)` with $f(x)=\sin(2\pi x)$, $n=30$, $\sigma=0.3$, polynomial degrees $k=0..15$, $200$ training sets: at a grid of test points it estimates $\mathrm{Bias}^2$ and $\mathrm{Var}$ of the degree-$k$ OLS fit.
Bias$^2$ (averaged over $x$) falls from $\approx0.5$ ($k=0$) to $\approx0.2$ ($k=1$), $\approx0.01$ ($k=3$), $<10^{-3}$ for $k\ge5$.
Variance rises: $\approx0.003$ at $k=0$, $\approx0.006$ at $k=1$, $\approx0.012$ at $k=3$, $\approx0.03$ at $k=9$, $>0.3$ at $k=15$ (explodes near the interval ends).
Averaged over the *training* points, the variance is exactly $\sigma^2(k+1)/n=0.003(k+1)$ — Theorem 7.3(c) — and the simulation matches to within Monte Carlo error.
Test MSE $=0.09+\mathrm{Bias}^2+\mathrm{Var}$ is U-shaped with minimum $\approx0.10$ around $k=3$–$5$, consistent with note 06.

## Pitfalls

- $X^\top X$ invertible requires $n\ge d$ *and* linearly independent columns; with a rank-deficient $X$ the minimiser is not unique and "the" solution means the min-norm one, $X^+y$.
  Numerically, use QR or SVD, never form $(X^\top X)^{-1}$ explicitly for ill-conditioned $X$ (condition number squares).
- $H$ projects $y$ onto $\mathrm{col}(X)$; $\hat w$ is *not* a projection of anything — it is the coordinates of the projection in the basis of columns.
- Gauss–Markov compares only *linear unbiased* estimators; ridge is biased and can have strictly smaller MSE (Stein-type effect).
  It says nothing about non-Gaussian efficiency or about robustness.
- The $\sigma^2d/n$ excess risk is *in-sample* and *well-specified* (and needs $\mathrm{Cov}\,\epsilon=\sigma^2I$).
  Out of sample it holds only approximately; under misspecification, add the approximation error and the noise is no longer homoscedastic.
- Ridge's $\lambda$ has units: the closed form $(X^\top X+\lambda I)^{-1}$ uses the unnormalised objective; with $\frac1n\|Xw-y\|^2+\lambda'\|w\|^2$ one gets $(X^\top X+n\lambda'I)^{-1}$.
  Bounds in the literature use both conventions.
- The bias–variance decomposition is a statement about *expected* squared loss at a *fixed* $x$; for $0$-$1$ loss no such additive decomposition holds.
- $\mathrm{df}(\lambda)=\mathrm{tr}H_\lambda$ is a *variance* proxy ($\mathrm{tr}H_\lambda^2\le\mathrm{df}$); it is not a count of parameters, and for KRR it depends on the spectrum of $K$ and hence on $n$.
- In the Rademacher bound (a), squared loss is Lipschitz only because predictions and labels are bounded; the constants $BR$, $Y$ enter quadratically in $M$.
  The bound is $O(1/\sqrt n)$ and is *not* tight for well-specified squared loss, where $O(1/n)$ holds (d).
- KRR with $\lambda=0$ interpolates the data when $K$ is invertible — the training error is $0$ and tells you nothing; $\lambda$ must be chosen by validation or by the bias–variance bound.

## Questions

**Q:** Derive the normal equations and the min-norm solution in the rank-deficient case.
**A:** $\nabla\|Xw-y\|^2=2X^\top(Xw-y)=0\Leftrightarrow X^\top Xw=X^\top y$ (convexity makes stationarity sufficient).
With $X=U\Sigma V^\top$ and $w=Vz+v$, $v\in\ker X$, the objective depends only on $z$ and is minimised at $z=\Sigma^{-1}U^\top y$; $\|w\|^2=\|Vz\|^2+\|v\|^2$ is smallest for $v=0$, giving $X^+y$.

**Q:** Show that the hat matrix is an orthogonal projector and state what it projects onto.
**A:** $H=X(X^\top X)^{-1}X^\top$ satisfies $H^2=H$ (cancel $(X^\top X)^{-1}X^\top X$) and $H^\top=H$ (symmetry of $X^\top X$); range is $\mathrm{col}(X)$ since $HXa=Xa$.
So $\hat y=Hy$ is the orthogonal projection of $y$ onto the column space and $X^\top(y-Hy)=0$.

**Q:** Under $y=Xw^*+\epsilon$, $\mathrm{Cov}\,\epsilon=\sigma^2I$, compute $\mathbb E\hat w$, $\mathrm{Cov}\hat w$ and the in-sample excess risk.
**A:** $\hat w=w^*+(X^\top X)^{-1}X^\top\epsilon$, so $\mathbb E\hat w=w^*$, $\mathrm{Cov}\hat w=\sigma^2(X^\top X)^{-1}$.
$X\hat w-Xw^*=H\epsilon$ and $\mathbb E\|H\epsilon\|^2=\sigma^2\mathrm{tr}H=\sigma^2d$, so the per-sample excess risk is $\sigma^2d/n$ — a $1/n$ rate, faster than the generic $1/\sqrt n$.

**Q:** Derive ridge from Tikhonov regularisation and explain the shrinkage in the SVD basis.
**A:** Minimising $\|Xw-y\|^2+\lambda\|w\|^2$ (strongly convex) gives $(X^\top X+\lambda I)w=X^\top y$.
With $X=U\Sigma V^\top$, $\hat y_\lambda=\sum_j\frac{\sigma_j^2}{\sigma_j^2+\lambda}(u_j^\top y)u_j$: each singular direction is kept with factor $\sigma_j^2/(\sigma_j^2+\lambda)$, so low-variance directions are suppressed; $\mathrm{df}(\lambda)=\sum_j\sigma_j^2/(\sigma_j^2+\lambda)$ interpolates between $d$ and $0$.
Bayesian view: Gaussian prior $N(0,\tau^2I)$ gives MAP $=$ ridge with $\lambda=\sigma^2/\tau^2$.

**Q:** Prove the bias–variance decomposition and say why the cross terms vanish.
**A:** Expand $(\hat f-y)^2=((\hat f-\bar f)+(\bar f-f)-\epsilon)^2$.
Squares give variance, bias$^2$, $\sigma^2$. Cross terms: $(\hat f-\bar f)(\bar f-f)$ has zero mean because $\bar f-f$ is constant and $\mathbb E_S(\hat f-\bar f)=0$; terms with $\epsilon$ vanish because $\epsilon$ is independent of $S$ with $\mathbb E\epsilon=0$.

**Q:** Prove $(X^\top X+\lambda I)^{-1}X^\top=X^\top(XX^\top+\lambda I)^{-1}$ and derive KRR from it.
**A:** $X^\top(XX^\top+\lambda I)=(X^\top X+\lambda I)X^\top$ identically; multiply by the two inverses (both exist since $\lambda>0$).
Then $\hat w_\lambda=\Phi^\top(K+\lambda I)^{-1}y=\Phi^\top\hat\alpha$ and $\hat f(x)=\sum_i\hat\alpha_ik(x_i,x)$ — an $n\times n$ solve, $O(n^3)$, in place of $O(d^3)$, usable for $d=\infty$.

**Q:** State the Rademacher generalisation bound for squared loss on a bounded linear class and explain each constant.
**A:** With $\|w\|\le B$, $\|x\|\le R$, $|y|\le Y$: $L_{\mathcal D}\le L_S+4(BR+Y)BR/\sqrt n+(BR+Y)^2\sqrt{\log(1/\delta)/(2n)}$.
$BR/\sqrt n$ is $\mathfrak R(\mathcal H)$ for the $B$-ball; $2(BR+Y)$ is the Lipschitz constant of $(u-y)^2$ on $|u|\le BR$ (contraction lemma); $(BR+Y)^2$ is the range of the loss (McDiarmid term scaling).

**Q:** State Gauss–Markov and prove it in three lines.
**A:** Among linear unbiased estimators $Cy$ with $CX=I$, OLS has minimal covariance in the PSD order.
Write $C=(X^\top X)^{-1}X^\top+D$; unbiasedness forces $DX=0$; then $\mathrm{Cov}(Cy)=\sigma^2CC^\top=\sigma^2(X^\top X)^{-1}+\sigma^2DD^\top$ because the cross terms contain $DX=0$, and $DD^\top\succeq0$.
It says nothing about biased estimators such as ridge, which can have smaller mean squared error.

**Q:** When would you solve least squares in the dual, and what does the effective degrees of freedom tell you there?
**A:** When $d\gg n$ or the feature space is infinite-dimensional (kernels): the dual costs $O(n^3)$ instead of $O(d^3)$ and needs only $K$.
$\mathrm{df}(\lambda)=\sum_j\mu_j/(\mu_j+\lambda)$ with $\mu_j$ the eigenvalues of $K$ is the variance-relevant dimension; it can be far smaller than $n$ if the kernel spectrum decays, which is why KRR does not overfit despite $D=\infty$.

**Q:** Derive the ridge fixed-design risk bound $\frac{\lambda\|w^*\|^2}{4n}+\frac{\sigma^2\mathrm{df}(\lambda)}n$.
**A:** $X\hat w_\lambda-Xw^*=-(I-H_\lambda)Xw^*+H_\lambda\epsilon$; expected squared norm $=\|(I-H_\lambda)Xw^*\|^2+\sigma^2\mathrm{tr}H_\lambda^2$.
In the SVD basis the bias is $\sum_j\frac{\lambda^2\sigma_j^2}{(\sigma_j^2+\lambda)^2}(v_j^\top w^*)^2\le\frac\lambda4\|w^*\|^2$ since $ab/(a+b)^2\le\frac14$, and $\mathrm{tr}H_\lambda^2\le\mathrm{tr}H_\lambda=\mathrm{df}(\lambda)$.
Divide by $n$.

## Code

`src/py/least_squares.py`:

- `ols(X, y)`: solves the normal equations via least squares (min-norm when rank-deficient); reproduces $\hat w=(7/6,1/2)$ on the 3-point example.
- `hat_matrix(X)`: builds $H$; check $H^2=H$, $H=H^\top$, $\mathrm{tr}H=d$ and $X^\top(I-H)y=0$ numerically.
- `ridge(X, y, lam)`: $(X^\top X+\lambda I)^{-1}X^\top y$; compare with `ols` to see shrinkage and with the SVD factors $\sigma_j^2/(\sigma_j^2+\lambda)$.
- `bias_variance_simulation(f, n, sigma, degrees, trials, rng)`: Monte Carlo estimate of $\mathrm{Bias}^2(x)$, $\mathrm{Var}(x)$ and total MSE for polynomial OLS of each degree; demonstrates Theorem 7.6 and the $\sigma^2(k+1)/n$ in-sample variance.
- `in_sample_excess_risk(X, w_star, sigma, trials, rng)`: Theorem 7.3(c), $\sigma^2d$ by simulation; `random_design_excess_risk(n, d, sigma, trials, rng)`: the Gaussian-design value $\sigma^2d/(n-d-1)$.
- `ridge_risk_exact`, `ridge_risk_bound`, `ridge_risk_mc(X, w_star, sigma, lam, trials, rng)`: Theorem 7.9(c), the exact bias-plus-variance expression, its bound $\lambda\|w^*\|^2/(4n)+\sigma^2\mathrm{df}(\lambda)/n$, and a simulation.
- `kernel_ridge(K, y, lam)` and `krr_predict`: the dual solution $\hat\alpha=(K+\lambda I)^{-1}y$ and $\hat f(x)=\sum_i\hat\alpha_ik(x_i,x)$; with the linear kernel it coincides with `ridge` (Theorem 7.7).

## References

- Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning*, Ch. 3.2 (OLS, Gauss–Markov), 3.4.1 (ridge, SVD view, effective degrees of freedom), 7.3 (bias–variance), 12.3.7 / 5.8 (kernel ridge).
- Shalev-Shwartz, Ben-David, *Understanding Machine Learning*, Ch. 9.2 (linear regression, least squares), 13.1 (ridge as RLM), 16.2 (kernel ridge via the representer theorem).
- Mohri, Rostamizadeh, Talwalkar, *Foundations of Machine Learning*, Ch. 11 (regression: Rademacher bounds for bounded linear/kernel regression, Thm 11.3 and Thm 11.11 for KRR, Sec. 11.3.2 ridge, dual form).
- Schölkopf, Smola, *Learning with Kernels*, Ch. 4 (regularisation), 16 (kernel ridge / Gaussian processes).
- A. E. Hoerl, R. W. Kennard, "Ridge regression: biased estimation for nonorthogonal problems", *Technometrics* 12 (1970).
- C. Saunders, A. Gammerman, V. Vovk, "Ridge regression learning algorithm in dual variables", ICML 1998.
- P. L. Bartlett, O. Bousquet, S. Mendelson, "Local Rademacher complexities", *Ann. Statist.* 33 (2005) — fast rates.
- T. Hsu, S. Kakade, T. Zhang, "Random design analysis of ridge regression", *FoCM* 14 (2014) — random-design version of Theorem 7.9(c).
