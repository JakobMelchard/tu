# 09 Support vector machines

The SVM is the canonical *margin-based* learner: among all hyperplanes that separate the data it picks the one furthest from the closest points, and with slack variables it trades margin against training errors. It ties together three earlier threads of the course: it is regularised loss minimisation (hinge loss + $\|w\|^2$, note 06), it is a kernel method through its dual and the representer theorem (note 08), and its generalisation is governed by the Rademacher complexity of a norm-bounded linear class (note 05), which is dimension-free and hence survives the kernel trick.

## Definitions

1. **Affine classifier.** $h_{w,b}(x)=\operatorname{sign}(\langle w,x\rangle+b)$, $w\in\mathbb R^d$, $b\in\mathbb R$. The decision boundary is the hyperplane $\{x:\langle w,x\rangle+b=0\}$.

2. **Functional and geometric margin.** For a labelled point $(x_i,y_i)$, $y_i\in\{-1,+1\}$, the functional margin is $\hat\gamma_i=y_i(\langle w,x_i\rangle+b)$ and the geometric margin is
$$\gamma_i=\frac{y_i(\langle w,x_i\rangle+b)}{\|w\|},$$
the signed Euclidean distance from $x_i$ to the hyperplane (positive iff correctly classified). The margin of the sample is $\gamma=\min_i\gamma_i$.

3. **Linearly separable.** $S$ is separable if some $(w,b)$ has $\gamma>0$.

4. **Canonical form.** Since $(w,b)$ and $(cw,cb)$, $c>0$, define the same hyperplane, we may rescale so that $\min_i y_i(\langle w,x_i\rangle+b)=1$. Then the geometric margin is exactly $1/\|w\|$.

5. **Hinge loss.** $\ell_{\text{hinge}}(h(x),y)=\max\{0,1-y\,h(x)\}$, a convex upper bound on the 0-1 loss (with $h(x)=\langle w,x\rangle+b$).

6. **$\rho$-margin loss.** $\ell_\rho(t)=1$ if $t\le0$, $1-t/\rho$ if $0<t\le\rho$, $0$ if $t\ge\rho$, applied to $t=y\,h(x)$. It is $1/\rho$-Lipschitz and satisfies $\ell_{0\text{-}1}\le\ell_\rho\le\mathbb 1[t\le\rho]$.

7. **Support vector.** A training point whose dual variable $\alpha_i$ is strictly positive; equivalently (see KKT below) a point that lies on or inside the margin.

## Results

### Hard-margin primal

Maximising the geometric margin over separating hyperplanes means solving $\max_{w,b}\min_i y_i(\langle w,x_i\rangle+b)/\|w\|$. Fix the canonical scaling: the problem becomes $\max 1/\|w\|$ subject to $y_i(\langle w,x_i\rangle+b)\ge1$, i.e.

$$\text{(P)}\qquad\min_{w,b}\ \tfrac12\|w\|^2\quad\text{s.t.}\quad y_i(\langle w,x_i\rangle+b)\ge1,\ i=1,\dots,n.$$

A convex quadratic objective with affine constraints: a convex QP with a unique minimiser $w^*$ (strictly convex in $w$; $b$ is then determined whenever both classes are present).

**Theorem 9.1 (Dual of the hard-margin SVM)** [S9 §15.5; S10 §5.2]**.** The Lagrange dual of (P) is
$$\text{(D)}\qquad\max_{\alpha\ge0}\ \sum_{i=1}^n\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle\quad\text{s.t.}\quad\sum_i\alpha_iy_i=0,$$
strong duality holds, and the primal solution is $w^*=\sum_i\alpha_i^*y_ix_i$.

*Proof.* Lagrangian with multipliers $\alpha_i\ge0$ for the constraints $1-y_i(\langle w,x_i\rangle+b)\le0$:
$$\mathcal L(w,b,\alpha)=\tfrac12\|w\|^2-\sum_i\alpha_i\big[y_i(\langle w,x_i\rangle+b)-1\big].$$
The dual function is $g(\alpha)=\inf_{w,b}\mathcal L$. $\mathcal L$ is convex in $(w,b)$, so the infimum is at a stationary point:
$$\nabla_w\mathcal L=w-\sum_i\alpha_iy_ix_i=0\ \Rightarrow\ w=\sum_i\alpha_iy_ix_i,\qquad
\partial_b\mathcal L=-\sum_i\alpha_iy_i=0.$$
If $\sum_i\alpha_iy_i\ne0$ then $\mathcal L$ is linear and unbounded below in $b$, so $g(\alpha)=-\infty$; hence the constraint $\sum\alpha_iy_i=0$ in (D). Substituting $w$ back:
$$\tfrac12\|w\|^2=\tfrac12\sum_{i,j}\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle,\qquad
\sum_i\alpha_iy_i\langle w,x_i\rangle=\sum_{i,j}\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle,$$
and the $b$ term vanishes, so $g(\alpha)=\sum_i\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle$. Strong duality: the problem is convex and Slater's condition holds (separability gives a strictly feasible point after scaling $w$ up). The KKT conditions are then necessary and sufficient:
- stationarity: $w^*=\sum_i\alpha_i^*y_ix_i$, $\sum_i\alpha_i^*y_i=0$;
- primal feasibility: $y_i(\langle w^*,x_i\rangle+b^*)\ge1$;
- dual feasibility: $\alpha_i^*\ge0$;
- complementary slackness: $\alpha_i^*\big[y_i(\langle w^*,x_i\rangle+b^*)-1\big]=0$. ∎

**Corollary 9.2 (Support vectors, sparsity, $b$)** [S9 Thm 15.8; S10 §5.2.2]**.** By complementary slackness, $\alpha_i^*>0$ implies $y_i(\langle w^*,x_i\rangle+b^*)=1$: the point lies exactly on the margin. Points strictly outside the margin have $\alpha_i^*=0$ and do not enter $w^*$. For any support vector $s$, $b^*=y_s-\langle w^*,x_s\rangle$ (average over support vectors in practice for numerical stability). The margin satisfies $1/\gamma^2=\|w^*\|^2=\sum_{i,j}\alpha_i^*\alpha_j^*y_iy_j\langle x_i,x_j\rangle=\sum_i\alpha_i^*$ (the last equality from $\sum_i\alpha_i^*y_i(\langle w^*,x_i\rangle+b^*)=\sum_i\alpha_i^*$ and $\sum\alpha_i^*y_i=0$).

### Soft margin

For non-separable data introduce slack $\xi_i\ge0$:
$$\text{(P}_C)\qquad\min_{w,b,\xi}\ \tfrac12\|w\|^2+C\sum_i\xi_i\quad\text{s.t.}\quad y_i(\langle w,x_i\rangle+b)\ge1-\xi_i,\ \xi_i\ge0.$$

**Proposition 9.3 (Soft margin = hinge-loss RLM)** [S9 §15.2.1; S23]**.** (P$_C$) is equivalent to
$$\min_{w,b}\ \lambda\|w\|^2+\frac1n\sum_{i=1}^n\max\{0,1-y_i(\langle w,x_i\rangle+b)\},\qquad\lambda=\frac{1}{2Cn}.$$

*Proof.* For fixed $(w,b)$ the optimal slack is the smallest feasible one, $\xi_i=\max\{0,1-y_i(\langle w,x_i\rangle+b)\}$, i.e. the hinge loss. Substituting gives $\frac12\|w\|^2+C\sum_i\ell_{\text{hinge},i}$; dividing by $Cn$ gives $\frac{1}{2Cn}\|w\|^2+\frac1n\sum_i\ell_{\text{hinge},i}$. ∎

So the SVM is regularised loss minimisation in the sense of note 06 with a convex, $R$-Lipschitz loss (for $\|x\|\le R$), and all of the stability theory applies.

**Theorem 9.4 (Dual of the soft-margin SVM)** [S23; S10 §5.3]**.**
$$\text{(D}_C)\qquad\max_{\alpha}\ \sum_i\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle\quad\text{s.t.}\quad\sum_i\alpha_iy_i=0,\ \ 0\le\alpha_i\le C.$$

*Proof.* Multipliers $\alpha_i\ge0$ for the margin constraints and $\mu_i\ge0$ for $\xi_i\ge0$:
$$\mathcal L=\tfrac12\|w\|^2+C\sum_i\xi_i-\sum_i\alpha_i\big[y_i(\langle w,x_i\rangle+b)-1+\xi_i\big]-\sum_i\mu_i\xi_i.$$
Stationarity: $\nabla_w$: $w=\sum_i\alpha_iy_ix_i$; $\partial_b$: $\sum_i\alpha_iy_i=0$; $\partial_{\xi_i}$: $C-\alpha_i-\mu_i=0$. The last one with $\mu_i\ge0$ gives $\alpha_i\le C$, and the $\xi$ terms cancel: $C\xi_i-\alpha_i\xi_i-\mu_i\xi_i=0$. What remains is exactly the hard-margin dual objective, now with the box constraint. Slater holds trivially (take any $w,b$ and large $\xi$), so strong duality and KKT apply. ∎

**Corollary 9.5 (Three regimes)** [S10 §5.3.1]**.** Complementary slackness for both constraint families, $\alpha_i[y_if(x_i)-1+\xi_i]=0$ and $\mu_i\xi_i=(C-\alpha_i)\xi_i=0$, with $f(x)=\langle w,x\rangle+b$:
- $\alpha_i=0$: $\mu_i=C>0\Rightarrow\xi_i=0$, so $y_if(x_i)\ge1$ — outside or on the margin, not a support vector.
- $0<\alpha_i<C$: $\mu_i>0\Rightarrow\xi_i=0$, and $\alpha_i>0\Rightarrow y_if(x_i)=1$ — exactly on the margin ("free" support vector). Use these to compute $b$.
- $\alpha_i=C$: $\mu_i=0$, $\xi_i\ge0$ free, $y_if(x_i)=1-\xi_i\le1$ — inside the margin or misclassified ("bounded" support vector).

### Kernel SVM

Everything in (D$_C$) and in $f(x)=\sum_i\alpha_iy_i\langle x_i,x\rangle+b$ depends on the data only through inner products. Replacing $\langle x,x'\rangle$ by a PSD kernel $k(x,x')$ (note 08) gives the SVM in the RKHS $\mathcal H_k$:
$$f(x)=\sum_{i=1}^n\alpha_iy_i\,k(x_i,x)+b.$$
This is exactly the form predicted by the representer theorem (Theorem 8.7), since the soft-margin primal is $\min_{f\in\mathcal H_k,b}\ \lambda\|f\|_{\mathcal H_k}^2+\frac1n\sum_i\ell_{\text{hinge}}(f(x_i)+b,y_i)$. The Gram matrix $K_{ij}=k(x_i,x_j)$ enters through the quadratic form $\alpha^\top(yy^\top\odot K)\alpha$, which is convex because $K\succeq0$ and $yy^\top\odot K=DKD$ with $D=\operatorname{diag}(y)$ is again PSD.

### Generalisation

**Theorem 9.6 (Leave-one-out bound)** [S10 Thm 5.4, via Lemma 5.3]**.** Let $h_S$ be the hard-margin SVM trained on $S$ (size $n+1$) and $N_{SV}(S)$ its number of support vectors. Then
$$\mathbb E_{S\sim\mathcal D^{n}}\big[L_{\mathcal D}(h_S)\big]\le\frac{\mathbb E_{S\sim\mathcal D^{n+1}}[N_{SV}(S)]}{n+1}.$$

*Proof.* The leave-one-out error $\hat L_{\text{loo}}(S)=\frac{1}{n+1}\sum_i\mathbb 1[h_{S\setminus i}(x_i)\ne y_i]$ is an unbiased estimate of $\mathbb E L_{\mathcal D}(h_{S'})$ for samples $S'$ of size $n$ (each summand is a fresh test point for a classifier trained on $n$ points). If $x_i$ is not a support vector of $h_S$ then removing it leaves the KKT conditions of the remaining problem satisfied by the same $(w^*,b^*,\alpha^*_{-i})$, so $h_{S\setminus i}=h_S$ and $h_S$ classifies $x_i$ correctly (it has margin $\ge1$). Hence every leave-one-out error is a support vector: $\hat L_{\text{loo}}(S)\le N_{SV}(S)/(n+1)$. Take expectations. ∎

This is a statement in expectation only, and few support vectors do not by themselves guarantee a good classifier on a particular sample.

**Theorem 9.7 (Margin bound)** [S19; S10 Thm 5.8 with Thm 5.10 — the specialisation to $\mathcal H_B$ is S10 Cor. 5.11]**.** Let $\|x\|\le R$ a.s. and $\mathcal H_B=\{x\mapsto\langle w,x\rangle:\|w\|\le B\}$. Fix $\rho>0$. With probability at least $1-\delta$ over $S\sim\mathcal D^n$, for every $h\in\mathcal H_B$:
$$L^{0\text{-}1}_{\mathcal D}(h)\ \le\ \hat L_{S,\rho}(h)+\frac{2}{\rho}\frac{BR}{\sqrt n}+3\sqrt{\frac{\log(2/\delta)}{2n}},$$
where $\hat L_{S,\rho}(h)=\frac1n\sum_i\ell_\rho(y_ih(x_i))\le\frac1n\sum_i\mathbb 1[y_ih(x_i)\le\rho]$ is the empirical margin loss.

*Proof.* Chain of three facts from notes 05 and 08.
1. $\ell_{0\text{-}1}(y h(x))\le\ell_\rho(y h(x))$ pointwise, so $L^{0\text{-}1}_{\mathcal D}(h)\le\mathbb E\,\ell_\rho(yh(x))$.
2. Apply the Rademacher generalisation theorem (Thm 5.3, losses in $[0,1]$) to the class $\mathcal G=\{(x,y)\mapsto\ell_\rho(yh(x)):h\in\mathcal H_B\}$: w.p. $\ge1-\delta$, $\mathbb E\,\ell_\rho(yh(x))\le\hat L_{S,\rho}(h)+2\mathfrak R_S(\mathcal G)+3\sqrt{\log(2/\delta)/(2n)}$.
3. $\ell_\rho$ is $\frac1\rho$-Lipschitz, so Talagrand's contraction lemma gives $\mathfrak R_S(\mathcal G)\le\frac1\rho\mathfrak R_S(\{(x,y)\mapsto yh(x)\})=\frac1\rho\mathfrak R_S(\mathcal H_B)$ (multiplying by $y_i\in\{\pm1\}$ does not change the distribution of $\sigma_iy_i$), and $\mathfrak R_S(\mathcal H_B)\le BR/\sqrt n$ (Thm 5.7, linear class). ∎

Remarks. (i) Nothing depends on the dimension $d$: only on $B$, $R$, $\rho$. Hence the bound holds verbatim in an RKHS with $R^2=\sup_xk(x,x)$ and $B=\|f\|_{\mathcal H_k}$. (ii) For the canonical hard-margin solution, $\rho=1$ and $B=\|w^*\|=1/\gamma$, and the bound reads $L_{\mathcal D}\le0+\frac{2R}{\gamma\sqrt n}+\dots$: large geometric margin relative to the data radius gives good generalisation. (iii) To make the bound hold simultaneously for all $\rho$ (needed because $\rho$ is chosen after seeing the data) one pays an extra $\sqrt{\log\log_2(2RB/\rho)/n}$ term by a union bound over a geometric grid of $\rho$'s. [S10] states this for the normalised case $\rho\in(0,1]$, where the extra term is $\sqrt{\log\log_2(2/\rho)/n}$ (discussion after Cor. 5.11, via Thm 5.9); the $RB$ inside the $\log\log$ above is the general-scale version, since the grid must span $[\rho_{\min},RB]$. (iv) With $\rho$ fixed and the bias $b$ included, the same argument works with $\tilde x=(x,1)$, $\tilde w=(w,b)$ and correspondingly larger $R,B$.

**Theorem 9.8 (Hinge-loss stability bound, statement)** [S9 Cor. 13.9; S10 §5.4]**.** Let $A$ be the soft-margin SVM viewed as RLM with parameter $\lambda$ and $\|x\|\le R$. The hinge loss is convex and $R$-Lipschitz in $w$, so by the stability theorem of note 06, for $\lambda=\sqrt{2R^2/(B^2n)}$,
$$\mathbb E_S\big[L^{\text{hinge}}_{\mathcal D}(A(S))\big]\le\min_{\|w\|\le B}L^{\text{hinge}}_{\mathcal D}(w)+\sqrt{\frac{8R^2B^2}{n}},$$
and since $\ell_{0\text{-}1}\le\ell_{\text{hinge}}$ the left-hand side upper-bounds the expected 0-1 risk. *Sketch:* RLM with a $\rho$-Lipschitz convex loss is $\frac{2\rho^2}{\lambda n}$-stable; expected risk $\le\min_w\big(L_{\mathcal D}(w)+\lambda\|w\|^2\big)+\frac{2\rho^2}{\lambda n}$; optimise $\lambda$ with $\rho=R$. ∎

**Theorem 9.9 (Perceptron mistake bound)** [S24; S9 Thm 9.1]**.** If $\|x_i\|\le R$ and some $w^*$ with $\|w^*\|=1$ has $y_i\langle w^*,x_i\rangle\ge\gamma$ for all $i$, the perceptron ($w\leftarrow w+y_ix_i$ on each mistake, $w_0=0$) makes at most $(R/\gamma)^2$ mistakes on any ordering of the data.

*Proof.* Let $w_k$ be the weight after $k$ mistakes. Lower bound: $\langle w_{k},w^*\rangle=\langle w_{k-1},w^*\rangle+y_i\langle x_i,w^*\rangle\ge\langle w_{k-1},w^*\rangle+\gamma$, so $\langle w_k,w^*\rangle\ge k\gamma$. Upper bound: $\|w_k\|^2=\|w_{k-1}\|^2+2y_i\langle w_{k-1},x_i\rangle+\|x_i\|^2\le\|w_{k-1}\|^2+R^2$ because the middle term is $\le0$ at a mistake, so $\|w_k\|^2\le kR^2$. Cauchy–Schwarz: $k\gamma\le\langle w_k,w^*\rangle\le\|w_k\|\le\sqrt kR$, hence $k\le(R/\gamma)^2$. ∎

The same $R/\gamma$ ratio controls both the perceptron and the SVM margin bound; this is the historical origin of "margin ⇒ generalisation".

### Optimisation

- **Dual QP.** (D$_C$) has $n$ variables, one equality and box constraints. Generic QP solvers (or `scipy.optimize.minimize` with SLSQP, as in the code) work for $n$ up to a few hundred; the Gram matrix costs $O(n^2)$ memory.
- **SMO** [S25]**.** Optimise two dual variables at a time, holding the rest fixed. Two, not one, because the equality $\sum_i\alpha_iy_i=0$ forces $\alpha_iy_i+\alpha_jy_j=\text{const}$, so a single variable cannot move. The two-variable subproblem is a one-dimensional quadratic in, say, $\alpha_j$: with $E_k=f(x_k)-y_k$ and $\eta=K_{ii}+K_{jj}-2K_{ij}\ge0$ the unconstrained optimum is $\alpha_j^{\text{new}}=\alpha_j+y_j(E_i-E_j)/\eta$, then clipped to the segment of the box $[0,C]^2$ that satisfies the equality (with endpoints $L,H$ computed from $y_i=y_j$ or not), and $\alpha_i$ is updated to keep $\alpha_iy_i+\alpha_jy_j$ fixed. Pairs are chosen by heuristics that maximise KKT violation.
- **Pegasos (Shalev-Shwartz et al. 2011).** Stochastic subgradient descent on the primal RLM form with step size $1/(\lambda t)$; reaches $\varepsilon$ accuracy in $\tilde O(1/(\lambda\varepsilon))$ iterations independent of $n$. Works in the kernel setting by maintaining $\alpha$ implicitly.
- Complexity: dual $O(n^2)$–$O(n^3)$; primal SGD $O(nd)$ per epoch; prediction $O(N_{SV}\cdot d)$ or $O(N_{SV})$ kernel evaluations.

## Worked example

Four points in $\mathbb R^2$: $x_1=(1,1),x_2=(2,2)$ with $y=+1$; $x_3=(-1,-1),x_4=(-2,-2)$ with $y=-1$.

*Geometry.* By symmetry the maximum-margin hyperplane is $x^{(1)}+x^{(2)}=0$ with normal direction $(1,1)/\sqrt2$. The closest points are $x_1$ and $x_3$ at distance $\sqrt2$ each, so the geometric margin is $\gamma=\sqrt2$.

*Primal.* Canonical scaling requires $y_1(\langle w,x_1\rangle+b)=1$ and $y_3(\langle w,x_3\rangle+b)=1$ with $w=c(1,1)$: $2c+b=1$ and $2c-b=1$, so $b=0$, $c=1/2$, $w^*=(1/2,1/2)$, $\|w^*\|=1/\sqrt2=1/\gamma$. Check the other constraints: $y_2(\langle w^*,x_2\rangle)=2\ge1$, $y_4(\cdot)=2\ge1$, both inactive.

*Dual / KKT.* Inactive constraints force $\alpha_2=\alpha_4=0$. Stationarity: $w^*=\alpha_1x_1-\alpha_3x_3=(\alpha_1+\alpha_3)(1,1)$, so $\alpha_1+\alpha_3=1/2$; $\sum\alpha_iy_i=\alpha_1-\alpha_3=0$. Hence $\alpha_1=\alpha_3=1/4$. Check $\sum_i\alpha_i^*=1/2=\|w^*\|^2$. Dual objective value $=\frac12-\frac12\cdot\frac12=\frac14=\frac12\|w^*\|^2$: strong duality holds. Support vectors: $\{x_1,x_3\}$.

*Soft margin.* With $C<1/4$ the box constraint is active: $\alpha_1=\alpha_3=C$, $w=2C(1,1)$, the margin widens to $1/(2\sqrt2C)$ and $x_1,x_3$ get slack $\xi=1-4C>0$: the machine trades training margin violations for a larger geometric margin. `src/py/svm.py` reproduces $w^*=(0.5,0.5)$, $b=0$, margin $\sqrt2$, SVs $\{0,2\}$.

## Pitfalls

- $C\to\infty$ recovers the hard-margin machine (on separable data); $C\to0$ makes $w\to0$. $C$ is *not* a margin width.
- The margin bound uses the *empirical margin loss* $\hat L_{S,\rho}$, not $L_S=0$. A separable sample with tiny geometric margin has $\hat L_{S,\rho}$ large for any useful $\rho$.
- Feature scaling changes the solution: the SVM is not invariant to anisotropic rescaling of inputs (the norm $\|w\|$ is). Standardise features.
- A small number of support vectors is evidence of good generalisation only in expectation (Theorem 9.6); with $N_{SV}\approx n$ the SVM is essentially a nearest-neighbour rule and the bound is vacuous.
- The kernel trick needs the dual or representer form; writing $w=\sum\alpha_iy_i\phi(x_i)$ explicitly is impossible for the Gaussian kernel.
- The dual is a QP in $n$ variables regardless of $d$; for $n\gg10^5$ use primal SGD or approximations (random features, Nyström).
- $b$ must be read off *free* support vectors ($0<\alpha_i<C$); bounded ones sit inside the margin and give the wrong $b$.
- "Maximum margin" is a property of the *linear* separator in feature space; with an RBF kernel of tiny bandwidth every sample is separable with a large margin in $\mathcal H_k$ but $R B$ is huge, and the bound is vacuous.

## Questions

**Q: Derive the hard-margin dual and state the KKT conditions.**
**A:** Lagrangian $\frac12\|w\|^2-\sum\alpha_i[y_i(\langle w,x_i\rangle+b)-1]$; set $\nabla_w=0\Rightarrow w=\sum\alpha_iy_ix_i$, $\partial_b=0\Rightarrow\sum\alpha_iy_i=0$; substitute to get $\sum\alpha_i-\frac12\sum\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle$, maximise over $\alpha\ge0$. KKT: stationarity, primal/dual feasibility, and complementary slackness $\alpha_i[y_i(\langle w,x_i\rangle+b)-1]=0$. Slater holds, so KKT characterise the optimum.

**Q: Why are there exactly two multipliers per point in the soft-margin problem, and where does the box constraint come from?**
**A:** One for the margin constraint ($\alpha_i$) and one for $\xi_i\ge0$ ($\mu_i$). $\partial_{\xi_i}\mathcal L=C-\alpha_i-\mu_i=0$ with $\mu_i\ge0$ gives $\alpha_i\le C$.

**Q: Show that the soft-margin SVM is regularised hinge-loss minimisation and identify $\lambda$.**
**A:** For fixed $(w,b)$ the optimal slack is $\xi_i=\max\{0,1-y_if(x_i)\}$; dividing the objective by $Cn$ gives $\frac{1}{2Cn}\|w\|^2+\frac1n\sum\ell_{\text{hinge}}$, so $\lambda=1/(2Cn)$.

**Q: State the margin bound and explain each term.**
**A:** $L^{0\text{-}1}_{\mathcal D}(h)\le\hat L_{S,\rho}(h)+\frac2\rho\frac{BR}{\sqrt n}+3\sqrt{\log(2/\delta)/(2n)}$. First term: empirical $\rho$-margin loss (fraction of points with margin $<\rho$, roughly). Second: twice the Rademacher complexity of the norm-bounded linear class after contraction by the $1/\rho$-Lipschitz margin loss; dimension-free. Third: McDiarmid concentration term.

**Q: Why does the margin bound justify kernel SVMs?**
**A:** It depends only on $B=\|f\|_{\mathcal H_k}$ and $R^2=\sup k(x,x)$, not on the dimension of the feature space, which may be infinite.

**Q: Prove that removing a non-support vector does not change the SVM solution.**
**A:** The KKT conditions of the reduced problem are satisfied by the old $(w^*,b^*)$ with the old $\alpha^*$ restricted to the remaining points: stationarity unchanged ($\alpha_i=0$ contributed nothing), feasibility unchanged, complementary slackness unchanged. By uniqueness of the primal optimum the solution is the same.

**Q: How many mistakes can the perceptron make on separable data with margin $\gamma$ and radius $R$? Prove it.**
**A:** At most $(R/\gamma)^2$: $\langle w_k,w^*\rangle\ge k\gamma$ and $\|w_k\|^2\le kR^2$, combine with Cauchy–Schwarz.

**Q: In SMO, why can one not optimise a single $\alpha_i$?**
**A:** The equality constraint $\sum\alpha_iy_i=0$ fixes $\alpha_i$ once all others are fixed. Two variables give a one-dimensional feasible segment.

## Code

`src/py/svm.py`: `solve_dual(K, y, C)` solves (D$_C$) with SLSQP; `SVM(C, kernel).fit` extracts support vectors, computes $b$ from free support vectors and exposes `decision_function`, `predict`, `w` (linear kernel) and `margin` ($1/\|w\|$ via the Gram matrix). `hard_margin_demo` reproduces the worked example. `leave_one_out_error(X, y, C, only_sv)` counts leave-one-out mistakes, refitting only for support vectors (Theorem 9.6: removing a non-SV leaves the solution unchanged; `only_sv=False` refits every point to confirm it). `perceptron(X, y)` returns the weight vector and the mistake count, checked against $(R/\gamma)^2$ (Theorem 9.9) on `make_margin_data`. `test_svm.py` checks the KKT regimes of Corollary 9.5, the equivalence $C\to\infty$ ⇒ hard margin, and agreement with `sklearn.svm.SVC` for linear and RBF kernels. `src/py/kernels.py` supplies the kernels.

## References

- Shalev-Shwartz & Ben-David, *Understanding Machine Learning*, Ch. 15 (SVM), Ch. 16 (kernels), Ch. 26.3 (margin bounds), Ch. 13 (stability).
- Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning*, Ch. 5 (SVM, margin theory, Thm 5.8), Ch. 6 (kernels).
- Schölkopf & Smola, *Learning with Kernels*, Ch. 7.
- Boser, Guyon & Vapnik (1992), "A training algorithm for optimal margin classifiers"; Cortes & Vapnik (1995), "Support-vector networks"; Platt (1998), "Sequential minimal optimization"; Shalev-Shwartz, Singer, Srebro & Cotter (2011), "Pegasos"; Bartlett & Mendelson (2002), "Rademacher and Gaussian complexities"; Novikoff (1962), "On convergence proofs for perceptrons".
