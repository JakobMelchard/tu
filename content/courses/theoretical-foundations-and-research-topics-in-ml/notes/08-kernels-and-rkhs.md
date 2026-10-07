# 08 Kernels and reproducing kernel Hilbert spaces

A kernel is a similarity function $k(x,x')$ that is secretly an inner product $\langle\phi(x),\phi(x')\rangle$ in some (possibly infinite-dimensional) feature space.
Any algorithm that touches the data only through inner products — ridge regression (note 07), SVMs (note 09), PCA, logistic regression — can be run in that feature space without ever computing $\phi$.
Two theorems make this rigorous and useful: the Moore–Aronszajn correspondence between positive-definite kernels and reproducing kernel Hilbert spaces (RKHS), and the representer theorem, which says that regularised solutions in an infinite-dimensional RKHS live in the $n$-dimensional span of the training points.
The dimension-free Rademacher bound of note 05 is what makes learning in such spaces statistically sound.

## Definitions

1. **Kernel, Gram matrix.** A function $k:\mathcal X\times\mathcal X\to\mathbb R$.
   For points $x_1,\dots,x_n$ the *Gram matrix* is $K\in\mathbb R^{n\times n}$, $K_{ij}=k(x_i,x_j)$.

2. **Positive-definite (Mercer) kernel.** $k$ is symmetric ($k(x,x')=k(x',x)$) and every Gram matrix is positive semidefinite: $\sum_{i,j}c_ic_jk(x_i,x_j)\ge0$ for all $n$, all $x_i\in\mathcal X$, all $c\in\mathbb R^n$.
   (Standard usage: "positive definite kernel" means PSD Gram matrices; "strictly positive definite" means $c^\top Kc>0$ for $c\ne0$ and distinct $x_i$.) We write PSD kernel.

3. **Feature map.** A map $\phi:\mathcal X\to\mathcal H$ into a Hilbert space with $k(x,x')=\langle\phi(x),\phi(x')\rangle_{\mathcal H}$.

4. **Reproducing kernel Hilbert space.** A Hilbert space $\mathcal H$ of functions $f:\mathcal X\to\mathbb R$ is an RKHS if every evaluation functional $\delta_x:f\mapsto f(x)$ is bounded (continuous): $|f(x)|\le C_x\|f\|_{\mathcal H}$.
   By the Riesz representation theorem there is then a unique $k_x\in\mathcal H$ with $f(x)=\langle f,k_x\rangle$; the *reproducing kernel* of $\mathcal H$ is $k(x,x')=\langle k_x,k_{x'}\rangle=k_{x'}(x)$. **Reproducing property:** $\langle f,k(x,\cdot)\rangle_{\mathcal H}=f(x)$ for all $f\in\mathcal H$, $x\in\mathcal X$.

5. **$\varepsilon$-notation for standard kernels** on $\mathbb R^d$: linear $\langle x,x'\rangle$; polynomial $(\langle x,x'\rangle+c)^p$, $c\ge0$, $p\in\mathbb N$; Gaussian RBF $\exp(-\gamma\|x-x'\|_2^2)$, $\gamma>0$ (also written with $1/(2\sigma^2)$); Laplacian $\exp(-\gamma\|x-x'\|_1)$ or $\exp(-\gamma\|x-x'\|_2)$.

6. **Normalised kernel.** $k_{\mathrm{norm}}(x,x')=\dfrac{k(x,x')}{\sqrt{k(x,x)k(x',x')}}$ (cosine of the angle between $\phi(x),\phi(x')$); $k_{\mathrm{norm}}(x,x)=1$.

7. **Convolution kernel (Haussler 1999).** Let $R\subset\mathcal X_1\times\dots\times\mathcal X_D\times\mathcal X$ be a "decomposition" relation, $R^{-1}(x)$ the finite set of tuples $\vec x$ that decompose $x$, and $k_d$ PSD on $\mathcal X_d$.
   Then $k(x,x')=\sum_{\vec x\in R^{-1}(x)}\sum_{\vec x'\in R^{-1}(x')}\prod_{d=1}^Dk_d(x_d,x'_d)$.

8. **Regularised empirical risk in an RKHS.** For a loss functional $c:(\mathcal X\times\mathbb R\times\mathbb R)^n\to\mathbb R\cup\{\infty\}$ and a strictly increasing $\Omega:[0,\infty)\to\mathbb R$,
$$\min_{f\in\mathcal H_k}\ c\big((x_1,y_1,f(x_1)),\dots,(x_n,y_n,f(x_n))\big)+\Omega(\|f\|_{\mathcal H_k}).$$
Example: KRR has $c=\sum_i(f(x_i)-y_i)^2$, $\Omega(t)=\lambda t^2$.

9. **Centred Gram matrix.** With $\mathbf 1$ the all-ones vector and $P=I-\frac1n\mathbf 1\mathbf 1^\top$, $\tilde K=PKP$ is the Gram matrix of the centred features $\phi(x_i)-\frac1n\sum_j\phi(x_j)$.

## Results

**Theorem 8.1 (PSD $\Leftrightarrow$ feature map)** [S9 Lemma 16.2; S10 Thm 6.8]**.** $k$ is a PSD kernel if and only if there exist a Hilbert space $\mathcal H$ and $\phi:\mathcal X\to\mathcal H$ with $k(x,x')=\langle\phi(x),\phi(x')\rangle$.

*Proof of $\Leftarrow$.* Symmetry is that of the inner product.
For any $x_i$, $c_i$: $\sum_{ij}c_ic_j\langle\phi(x_i),\phi(x_j)\rangle=\big\|\sum_ic_i\phi(x_i)\big\|^2\ge0$. ∎

*Proof of $\Rightarrow$ (RKHS construction).* Step 1, pre-Hilbert space.
Let $\mathcal H_0=\mathrm{span}\{k(x,\cdot):x\in\mathcal X\}$, the functions $f=\sum_{i=1}^m\alpha_ik(x_i,\cdot)$.
Define, for $f=\sum_i\alpha_ik(x_i,\cdot)$ and $g=\sum_j\beta_jk(x'_j,\cdot)$,
$$\langle f,g\rangle:=\sum_{i,j}\alpha_i\beta_jk(x_i,x'_j).$$
*Well-defined:* $\sum_{ij}\alpha_i\beta_jk(x_i,x'_j)=\sum_j\beta_jf(x'_j)=\sum_i\alpha_ig(x_i)$; the middle expression depends on $g$ only through $\beta,x'$ and on $f$ only as a function, the right one symmetrically, so the value does not depend on the chosen representations.
It is bilinear and symmetric (symmetry of $k$). *Reproducing property:* taking $g=k(x,\cdot)$ (one term, $\beta=1$) gives $\langle f,k(x,\cdot)\rangle=f(x)$. *Positivity:* $\langle f,f\rangle=\alpha^\top K\alpha\ge0$ by PSD-ness.

Step 2, definiteness via Cauchy–Schwarz. For a symmetric bilinear PSD form, $\langle f,g\rangle^2\le\langle f,f\rangle\langle g,g\rangle$ (expand $\langle f-tg,f-tg\rangle\ge0$ for all $t$; nonnegative discriminant).
Hence $|f(x)|^2=\langle f,k(x,\cdot)\rangle^2\le\langle f,f\rangle k(x,x)$.
So $\langle f,f\rangle=0$ implies $f(x)=0$ for all $x$: the form is an inner product, and $\mathcal H_0$ is a pre-Hilbert space of functions in which evaluation is bounded with $C_x=\sqrt{k(x,x)}$.

Step 3, completion. Let $(f_m)$ be Cauchy in $\mathcal H_0$. By the bound of Step 2, $|f_m(x)-f_l(x)|\le\|f_m-f_l\|\sqrt{k(x,x)}$, so $(f_m(x))$ is Cauchy in $\mathbb R$ for each $x$; define $f(x)=\lim f_m(x)$.
Let $\mathcal H_k$ be the set of all such pointwise limits with $\langle f,g\rangle=\lim\langle f_m,g_m\rangle$ (well-defined by the Cauchy property; two Cauchy sequences with the same pointwise limit have $\|f_m-g_m\|\to0$, which follows from the reproducing property on $\mathcal H_0$ and a density argument).
This is a Hilbert space of functions, contains $\mathcal H_0$ densely, and the reproducing property passes to the limit: $\langle f,k(x,\cdot)\rangle=\lim\langle f_m,k(x,\cdot)\rangle=\lim f_m(x)=f(x)$.

Step 4, feature map. Set $\phi(x)=k(x,\cdot)\in\mathcal H_k$.
Then $\langle\phi(x),\phi(x')\rangle=\langle k(x,\cdot),k(x',\cdot)\rangle=k(x,x')$ by the reproducing property. ∎

**Theorem 8.2 (Moore–Aronszajn)** [S22; S10 Thm 6.8]**.** For every PSD kernel $k$ on $\mathcal X$ there is a *unique* RKHS $\mathcal H_k$ of functions on $\mathcal X$ whose reproducing kernel is $k$; conversely every RKHS has a unique reproducing kernel, and it is PSD.

*Proof sketch.* Existence is Theorem 8.1 ($\Rightarrow$). Uniqueness: if $\mathcal H'$ is another RKHS with kernel $k$, it contains $\mathcal H_0$ with the same inner product (reproducing property forces $\langle k(x,\cdot),k(x',\cdot)\rangle=k(x,x')$), hence contains its closure $\mathcal H_k$ isometrically; if $f\in\mathcal H'\ominus\mathcal H_k$ then $f(x)=\langle f,k(x,\cdot)\rangle=0$ for all $x$, so $f=0$.
Converse: Riesz gives $k_x$ with $f(x)=\langle f,k_x\rangle$; uniqueness of Riesz representers gives uniqueness of $k$; PSD-ness by Theorem 8.1 ($\Leftarrow$) with $\phi(x)=k_x$. ∎

**Theorem 8.3 (Mercer; statement)** [S10 Thm 6.2]**.** Let $\mathcal X$ be compact, $\mu$ a finite Borel measure with full support, and $k$ continuous, symmetric and PSD.
Then the integral operator $T_kf(x)=\int k(x,x')f(x')d\mu(x')$ on $L_2(\mu)$ is compact, self-adjoint, positive, with eigenvalues $\lambda_1\ge\lambda_2\ge\dots\ge0$, $\sum_j\lambda_j<\infty$, and continuous orthonormal eigenfunctions $\psi_j$, and
$$k(x,x')=\sum_{j\ge1}\lambda_j\psi_j(x)\psi_j(x'),$$
with absolute and uniform convergence. Consequently $\phi(x)=(\sqrt{\lambda_j}\psi_j(x))_{j\ge1}\in\ell_2$ is an explicit feature map, and $\mathcal H_k=\{f=\sum_ja_j\psi_j:\|f\|^2_{\mathcal H_k}=\sum_ja_j^2/\lambda_j<\infty\}$.
The decay of $\lambda_j$ measures the "size" of the RKHS (it governs the effective dimension $\mathrm{df}(\lambda)$ of note 07 and the covering numbers of note 05).

**Theorem 8.4 (closure properties)** [S10 Thm 6.10]**.** Let $k_1,k_2$ be PSD kernels on $\mathcal X$, $a\ge0$, $f:\mathcal X\to\mathbb R$, $\psi:\mathcal X'\to\mathcal X$.
Then the following are PSD kernels:
(a) $k_1+k_2$; (b) $ak_1$; (c) $k_1k_2$ (pointwise product); (d) $(x,x')\mapsto f(x)f(x')$; (e) $\lim_mk^{(m)}$ if each $k^{(m)}$ is PSD and the limit exists pointwise; (f) $(x,x')\mapsto k_1(\psi(x),\psi(x'))$ on $\mathcal X'$; (g) $p(k_1)$ for any polynomial $p$ with nonnegative coefficients, and $\exp(k_1)$; (h) the normalised kernel $k_1/\sqrt{k_1(x,x)k_1(x',x')}$ when $k_1(x,x)>0$.

*Proof.* (a),(b): $c^\top(K_1+K_2)c=c^\top K_1c+c^\top K_2c\ge0$; $c^\top(aK_1)c\ge0$.
(d): $\sum_{ij}c_ic_jf(x_i)f(x_j)=(\sum_ic_if(x_i))^2\ge0$; equivalently the feature map $\phi(x)=f(x)\in\mathbb R$.
(e): $c^\top K^{(m)}c\ge0$ for all $m$ and the limit of nonnegative numbers is nonnegative.
(f): Gram matrices of the composed kernel are Gram matrices of $k_1$ at the points $\psi(x_i)$.
(c), *Schur product theorem:* with feature maps $\phi_1,\phi_2$,
$$k_1(x,x')k_2(x,x')=\langle\phi_1(x),\phi_1(x')\rangle\langle\phi_2(x),\phi_2(x')\rangle=\langle\phi_1(x)\otimes\phi_2(x),\phi_1(x')\otimes\phi_2(x')\rangle_{\mathcal H_1\otimes\mathcal H_2},$$
since $\langle u\otimes v,u'\otimes v'\rangle=\langle u,u'\rangle\langle v,v'\rangle$ by definition of the tensor-product inner product; so $\phi_1\otimes\phi_2$ is a feature map and Theorem 8.1 ($\Leftarrow$) applies.
Matrix version: for PSD $K_1=\sum_a\lambda_au_au_a^\top$, $K_2=\sum_b\mu_bv_bv_b^\top$ (spectral decompositions, $\lambda_a,\mu_b\ge0$), the Hadamard product is $K_1\circ K_2=\sum_{a,b}\lambda_a\mu_b(u_a\circ v_b)(u_a\circ v_b)^\top\succeq0$.
(g): polynomials with nonnegative coefficients by (a),(b),(c) and the constant kernel $1$ (case (d) with $f\equiv1$); $\exp(k_1)=\lim_M\sum_{m\le M}k_1^m/m!$ by (e).
(h): product of $k_1$ with the kernel $f(x)f(x')$ for $f(x)=k_1(x,x)^{-1/2}$, using (c),(d). ∎

**Theorem 8.5 (standard kernels are PSD)** [S10 §6.2, Thm 6.24 (Bochner)]**.**
(a) *Linear:* $\phi=\mathrm{id}$.
(b) *Polynomial* $(\langle x,x'\rangle+c)^p$, $c\ge0$: polynomial with nonnegative coefficients in the linear kernel plus a constant (Theorem 8.4(g)).
Explicitly for $p=2$, $d=2$, $c=1$:
$$(1+x_1x_1'+x_2x_2')^2=1+x_1^2x_1'^2+x_2^2x_2'^2+2x_1x_1'+2x_2x_2'+2x_1x_2x_1'x_2',$$
so $\phi(x)=\big(1,\ \sqrt2x_1,\ \sqrt2x_2,\ x_1^2,\ x_2^2,\ \sqrt2x_1x_2\big)\in\mathbb R^6$; in general $\dim=\binom{d+p}{p}$.
(c) *Gaussian RBF.* Write
$$\exp(-\gamma\|x-x'\|^2)=\exp(-\gamma\|x\|^2)\exp(2\gamma\langle x,x'\rangle)\exp(-\gamma\|x'\|^2).$$
The middle factor is $\exp$ of a PSD kernel (Theorem 8.4(g)), the outer factors form the kernel $f(x)f(x')$ with $f(x)=e^{-\gamma\|x\|^2}$ (8.4(d)); the product is PSD by 8.4(c).
Equivalently, the RBF kernel is the *normalisation* (8.4(h)) of $\tilde k(x,x')=\exp(2\gamma\langle x,x'\rangle)$: $\tilde k(x,x')/\sqrt{\tilde k(x,x)\tilde k(x',x')}=\exp(2\gamma\langle x,x'\rangle-\gamma\|x\|^2-\gamma\|x'\|^2)$. *Infinite-dimensional feature map* (for $d=1$): Taylor-expanding the middle factor,
$$e^{-\gamma(x-x')^2}=\sum_{m=0}^\infty\Big(e^{-\gamma x^2}\sqrt{\tfrac{(2\gamma)^m}{m!}}\,x^m\Big)\Big(e^{-\gamma x'^2}\sqrt{\tfrac{(2\gamma)^m}{m!}}\,x'^m\Big),$$
so $\phi(x)=\big(e^{-\gamma x^2}\sqrt{(2\gamma)^m/m!}\,x^m\big)_{m\ge0}\in\ell_2$: all monomials, with rapidly decaying weights.
For $d>1$ use multi-indices. The RKHS is infinite-dimensional and strictly positive definite: Gram matrices at distinct points are invertible (Micchelli 1986).
(d) *Laplacian* $\exp(-\gamma\|x-x'\|_2)$: PSD by Bochner's theorem (a continuous translation-invariant kernel $\kappa(x-x')$ is PSD iff $\kappa$ is the Fourier transform of a nonnegative finite measure); the transform of $e^{-\gamma\|u\|}$ is a multivariate Cauchy density $\propto(\gamma^2+\|\omega\|^2)^{-(d+1)/2}>0$.
The $\ell_1$ version is the product over coordinates of 1-D Laplacian kernels (8.4(c)).
(e) *Convolution kernels* (Definition 7) are PSD: the product $\prod_dk_d$ is PSD on tuples (8.4(c),(f)), and a sum over finite sets of tuples is a sum of PSD kernels composed with the set-valued map — concretely $\sum_{ij}c_ic_jk(x_i,x_j)=\sum_{\vec x,\vec x'}\tilde c_{\vec x}\tilde c_{\vec x'}\prod_dk_d\ge0$ with $\tilde c_{\vec x}=c_i$ for $\vec x\in R^{-1}(x_i)$.
*Strings and graphs.* The $p$-spectrum kernel counts shared substrings of length $p$: $k(s,s')=\sum_{u\in\Sigma^p}\#_u(s)\#_u(s')$, an explicit finite feature map (8.1 $\Leftarrow$); computable in $O(|s|+|s'|)$ with suffix trees.
The random-walk graph kernel $k(G,G')=\sum_{t}\lambda^t\,\mathbf 1^\top A_\times^t\mathbf 1$ counts common walks via the adjacency matrix $A_\times$ of the direct product graph; it is a convolution-type kernel and PSD for small $\lambda$ (Gärtner, Flach, Wrobel 2003).
Both illustrate the point of the kernel view: define similarity on structured objects without a vector representation.

**Theorem 8.6 (kernel trick, distances, centring)** [S9 §16.2; S10 §6.1]**.** (a) Any algorithm whose input enters only through inner products $\langle x_i,x_j\rangle$ and $\langle x_i,x\rangle$ can be run in feature space by replacing them with $k(x_i,x_j)$ and $k(x_i,x)$.
(b) $\|\phi(x)-\phi(x')\|^2=k(x,x)-2k(x,x')+k(x',x')$. (c) The Gram matrix of centred features $\tilde\phi(x_i)=\phi(x_i)-\bar\phi$, $\bar\phi=\frac1n\sum_j\phi(x_j)$, is $\tilde K=PKP$ with $P=I-\frac1n\mathbf 1\mathbf 1^\top$.

*Proof.* (a) is tautological given Theorem 8.1. (b) Expand $\langle\phi(x)-\phi(x'),\phi(x)-\phi(x')\rangle$.
(c) $\tilde K_{ij}=K_{ij}-\frac1n\sum_lK_{il}-\frac1n\sum_lK_{lj}+\frac1{n^2}\sum_{lm}K_{lm}$, which is $(PKP)_{ij}$. ∎

*Examples of the trick.* Kernel perceptron: the primal update $w\leftarrow w+y_i\phi(x_i)$ keeps $w=\sum_j\alpha_j\phi(x_j)$, so the prediction $\langle w,\phi(x)\rangle=\sum_j\alpha_jk(x_j,x)$ needs only kernel values.
Kernel PCA: the principal directions of the centred features are $v=\sum_i\alpha_i\tilde\phi(x_i)$ with $\tilde K\alpha=n\mu\alpha$, and the projection of a new point is $\sum_i\alpha_i\tilde k(x_i,x)$ — an eigenproblem on $\tilde K$ instead of on a $D\times D$ covariance.
Nearest-mean and $k$-means in feature space use only (b). In every case the algorithm is *identical* to its linear version with $\langle\cdot,\cdot\rangle$ replaced by $k$; the statistical price is governed by $\|w\|$ and $\mathrm{tr}K$ (note 05, Theorem 5.7), not by $D$.

**Theorem 8.7 (representer theorem)** [S21; S9 Thm 16.1; S10 Thm 6.11]**.** Let $k$ be a PSD kernel with RKHS $\mathcal H_k$, $c$ an arbitrary loss functional and $\Omega:[0,\infty)\to\mathbb R$ strictly increasing.
Then every minimiser $f^*$ of
$$J(f)=c\big((x_i,y_i,f(x_i))_{i=1}^n\big)+\Omega(\|f\|_{\mathcal H_k})$$
over $\mathcal H_k$ has the form $f^*=\sum_{i=1}^n\alpha_ik(x_i,\cdot)$ for some $\alpha\in\mathbb R^n$.
If $\Omega$ is only non-decreasing, some minimiser has this form.

*Proof.* Let $V=\mathrm{span}\{k(x_i,\cdot):i=1..n\}\subset\mathcal H_k$, a finite-dimensional hence closed subspace.
Decompose any $f\in\mathcal H_k$ orthogonally: $f=f_\parallel+f_\perp$ with $f_\parallel\in V$, $f_\perp\in V^\perp$.

*Step 1: $f_\perp$ is invisible on the data.* By the reproducing property, for each training point $f_\perp(x_i)=\langle f_\perp,k(x_i,\cdot)\rangle=0$ since $k(x_i,\cdot)\in V$.
Hence $f(x_i)=f_\parallel(x_i)$ for all $i$ and the loss term satisfies $c(\dots,f(x_i),\dots)=c(\dots,f_\parallel(x_i),\dots)$.

*Step 2: $f_\perp$ only increases the regulariser.* Pythagoras: $\|f\|^2=\|f_\parallel\|^2+\|f_\perp\|^2\ge\|f_\parallel\|^2$, with equality iff $f_\perp=0$.
Since $\Omega$ is strictly increasing, $\Omega(\|f\|)\ge\Omega(\|f_\parallel\|)$ with equality iff $f_\perp=0$.

*Step 3.* Therefore $J(f)\ge J(f_\parallel)$ with equality iff $f_\perp=0$.
If $f^*$ is a minimiser, $J(f^*_\parallel)\le J(f^*)$ forces $J(f^*_\parallel)=J(f^*)$ and thus $f^*_\perp=0$, i.e. $f^*=f^*_\parallel\in V$, which is exactly $\sum_i\alpha_ik(x_i,\cdot)$.
If $\Omega$ is merely non-decreasing, $f^*_\parallel$ is a minimiser in $V$. ∎

*Consequences.* (i) The infinite-dimensional problem over $\mathcal H_k$ becomes a problem over $\alpha\in\mathbb R^n$: with $f=\sum\alpha_ik(x_i,\cdot)$, $f(x_j)=(K\alpha)_j$ and $\|f\|^2_{\mathcal H_k}=\alpha^\top K\alpha$ (by the inner product of Theorem 8.1).
(ii) *KRR:* $\min_\alpha\|K\alpha-y\|^2+\lambda\alpha^\top K\alpha$, solved by $\alpha=(K+\lambda I)^{-1}y$ (note 07, Theorem 7.8).
(iii) *SVM:* hinge loss $c=\sum_i\max(0,1-y_if(x_i))$, $\Omega=\lambda\|f\|^2$; the dual variables of note 09 are $\alpha_i=y_i\alpha_i^{\mathrm{dual}}$, and support vectors are the $i$ with $\alpha_i\ne0$.
(iv) *Kernel logistic regression:* $c=\sum_i\log(1+e^{-y_if(x_i)})$, solved by Newton's method in $\alpha$.
(v) Any $\Omega$ strictly increasing works — $\|f\|$, $\|f\|^2$, $e^{\|f\|}$ — and $c$ need not be convex; convexity is needed only to *find* the minimiser, not for its form.

**RKHS norm and smoothness (Fourier form).** For a translation-invariant kernel $k(x,x')=\kappa(x-x')$ on $\mathbb R^d$ with $\hat\kappa(\omega)>0$ (Bochner), the RKHS is $\mathcal H_k=\{f\in L_2:\int|\hat f(\omega)|^2/\hat\kappa(\omega)\,d\omega<\infty\}$ with $\|f\|^2_{\mathcal H_k}=(2\pi)^{-d}\int\frac{|\hat f(\omega)|^2}{\hat\kappa(\omega)}d\omega$ (check: $\langle f,\kappa(x-\cdot)\rangle=(2\pi)^{-d}\int\hat f(\omega)\overline{\hat\kappa(\omega)e^{-i\omega x}}/\hat\kappa(\omega)\,d\omega=f(x)$, the reproducing property).
For the Gaussian kernel $\hat\kappa(\omega)\propto\exp(-\|\omega\|^2/(4\gamma))$, so $\|f\|^2_{\mathcal H_k}\propto\int|\hat f(\omega)|^2e^{\|\omega\|^2/(4\gamma)}d\omega$: the norm weights frequency $\omega$ by $e^{+\|\omega\|^2/4\gamma}$, i.e. penalises high frequencies super-exponentially; functions in the Gaussian RKHS are real-analytic.
Small $\gamma$ (wide kernel) penalises even moderate frequencies — smooth, nearly linear fits; large $\gamma$ admits wiggly functions.
The Laplacian kernel has $\hat\kappa\sim\|\omega\|^{-(d+1)}$, a polynomial weight $\|\omega\|^{d+1}$: its RKHS is a Sobolev space of order $(d+1)/2$, containing non-differentiable functions.
This is the precise sense in which regularising $\|f\|_{\mathcal H_k}$ is a smoothness penalty, and it is why the choice of kernel is a choice of inductive bias.

## Worked example

**Explicit quadratic feature map.** $x=(1,2)$, $x'=(3,-1)$, $k(x,x')=(1+\langle x,x'\rangle)^2$.
Directly: $\langle x,x'\rangle=3-2=1$, $k=(1+1)^2=4$. Via $\phi$ from Theorem 8.5(b): $\phi(x)=(1,\sqrt2,2\sqrt2,1,4,2\sqrt2)$, $\phi(x')=(1,3\sqrt2,-\sqrt2,9,1,-3\sqrt2)$, and
$$\langle\phi(x),\phi(x')\rangle=1+6-4+9+4-12=4.\ \checkmark$$
`poly2_feature_map` builds exactly this $\phi$, and `polynomial_kernel(X, Y, 2, 1)` agrees with $\phi(X)\phi(Y)^\top$ to machine precision.

**RBF Gram matrix, $3\times3$, PSD by hand.** Points $x_1=0,x_2=1,x_3=2$ on the line, $\gamma=1$:
$$K=\begin{pmatrix}1&e^{-1}&e^{-4}\\e^{-1}&1&e^{-1}\\e^{-4}&e^{-1}&1\end{pmatrix}\approx\begin{pmatrix}1&0.3679&0.0183\\0.3679&1&0.3679\\0.0183&0.3679&1\end{pmatrix}.$$
Sylvester's criterion (all leading principal minors positive $\Leftrightarrow$ positive definite): $1>0$; $1-e^{-2}=0.8647>0$; $\det K=(1-e^{-2})-e^{-1}(e^{-1}-e^{-5})+e^{-4}(e^{-2}-e^{-4})=0.8647-0.1329+0.0021=0.7339>0$.
So $K\succ0$. Eigenvalues: the antisymmetric vector $(1,0,-1)$ gives $\mu=1-e^{-4}=0.9817$; the symmetric ones $(1,a,1)$ solve $e^{-1}a^2+e^{-4}a-2e^{-1}=0$, giving $\mu\approx1.5295$ and $0.4888$.
Check: trace $3.000$, product $0.7339$. `rbf_kernel` + `is_psd` confirm (smallest eigenvalue $0.489>0$).
Increasing $\gamma$ to $100$ makes $K\approx I$ (each point similar only to itself); decreasing to $0.001$ makes $K\approx\mathbf 1\mathbf 1^\top$ with smallest eigenvalue $\approx10^{-6}$ — still PSD, but numerically singular.

**Closure check on the same points.** The linear kernel has Gram matrix $K_{\mathrm{lin}}=\begin{pmatrix}0&0&0\\0&1&2\\0&2&4\end{pmatrix}$ (rank one, PSD).
The Schur product with the RBF Gram matrix is
$$K\circ K_{\mathrm{lin}}=\begin{pmatrix}0&0&0\\0&1&2e^{-1}\\0&2e^{-1}&4\end{pmatrix},$$
whose nonzero block has trace $5>0$ and determinant $4-4e^{-2}=3.459>0$, so the eigenvalues are $0$ and two positive numbers: PSD, as Theorem 8.4(c) promises.
The sum $K+K_{\mathrm{lin}}$ is PSD by 8.4(a) — its leading minors are $1$, $1.865$ and $\det>0$.

**A non-kernel by hand.** For the sigmoid $\tanh(\langle x,x'\rangle-1)$ and the single point $x=0$, the $1\times1$ Gram matrix is $\tanh(-1)=-0.762<0$.
But $k(x,x)=\|\phi(x)\|^2\ge0$ for any PSD kernel, so no feature map exists; `is_psd` on the $3\times3$ Gram matrix at $x\in\{0,1,2\}$ reports a negative eigenvalue as well.

**Feature-space distance.** From the Gram matrix, $\|\phi(x_1)-\phi(x_3)\|^2=1-2e^{-4}+1=1.963$, while $\|\phi(x_1)-\phi(x_2)\|^2=2-2e^{-1}=1.264$; all RBF feature vectors lie on the unit sphere ($k(x,x)=1$) and distances saturate at $\sqrt2$.

**Representer demo (qualitative).** `representer_demo` draws $n=20$ points in $\mathbb R^2$, maps them with `poly2_feature_map` to $\mathbb R^6$, solves ridge in the explicit feature space ($w^*\in\mathbb R^6$), then (i) projects $w^*$ onto $\mathrm{span}\{\phi(x_i)\}$ and reports a residual of order $10^{-13}$ — the projection is exact, $w^*$ lies in the span; (ii) solves KRR with `polynomial_kernel` and shows $\Phi^\top\hat\alpha=w^*$ to $10^{-12}$.
With $n=3<6$ the same holds and the span is a proper 3-dimensional subspace of $\mathbb R^6$: the regulariser prevents the solution from using the other three directions, exactly as in the proof.

## Pitfalls

- "Positive definite kernel" (PSD Gram matrices) vs positive definite *matrix* $K\succ0$: a PSD kernel can have singular Gram matrices (repeated points, linear kernel with $n>d$).
  Strictly PD kernels (Gaussian, Laplacian) give invertible $K$ for distinct points, but the condition number can still be astronomical.
- A kernel is a similarity, not a distance: $k$ need not satisfy the triangle inequality, may be negative (linear kernel), and $k(x,x)$ need not be constant.
  The induced distance is $\sqrt{k(x,x)-2k(x,x')+k(x',x')}$.
- The sigmoid "kernel" $\tanh(a\langle x,x'\rangle+b)$ is *not* PSD in general (its Gram matrices can have negative eigenvalues); SVM software accepts it, but the theory (RKHS, representer theorem, convex dual) does not apply.
  Similarly $\exp(-\gamma\|x-x'\|_2^p)$ is PSD only for $0<p\le2$.
- RBF with tiny $\gamma$: $K\approx\mathbf 1\mathbf 1^\top$, all points look alike, predictions nearly constant (underfitting, ill-conditioning).
  Huge $\gamma$: $K\approx I$, each training point is an island, the predictor is $\approx0$ away from the data (overfitting / memorisation).
  Scale $\gamma$ with $1/\mathrm{median}\|x_i-x_j\|^2$ as a starting heuristic and tune by validation.
- The representer theorem needs $\Omega$ *strictly* increasing in $\|f\|_{\mathcal H_k}$ (the RKHS norm, not some other norm).
  Regularising $\|f\|_{L_2}$ or $\|\alpha\|_2$ instead breaks the argument.
- The RKHS norm is not the sup norm or the $L_2$ norm; two functions can be uniformly close yet far apart in $\mathcal H_k$ (add a tiny high-frequency wiggle).
  $\|f\|_{\mathcal H_k}$ measures smoothness in the sense determined by $\hat\kappa$.
- Mercer's expansion needs a measure and compactness; the RKHS itself (Moore–Aronszajn) needs neither.
  Do not confuse the Mercer feature map $(\sqrt{\lambda_j}\psi_j)$ with the canonical one $k(x,\cdot)$ — they give isometric but different-looking feature spaces.
- Centring: kernel PCA and some SVM formulations assume centred features; centring must be done on $K$ (via $PKP$), not by subtracting the mean of the raw $x$.
- Adding a constant $c>0$ to a PSD kernel keeps it PSD (Theorem 8.4(a) with the kernel $\equiv c$), but adding a constant to the *Gram matrix diagonal* ($K+\lambda I$) is regularisation, not a change of kernel — do not confuse the two even though both make $K$ better conditioned.
- Composition works one way only: $k(\psi(x),\psi(x'))$ is PSD for any map $\psi$, but $\psi(k(x,x'))$ for a scalar function $\psi$ is PSD only for special $\psi$ (nonnegative-coefficient power series, Theorem 8.4(g)); e.g. $\sqrt{k}$ and $\log(1+k)$ are not PSD in general.
- Feature-space dimension is irrelevant for generalisation; what matters is $\|f\|_{\mathcal H_k}$ (or $\|w\|$) and $\max_ik(x_i,x_i)$ — the Rademacher bound $\frac Bn\sqrt{\mathrm{tr}K}$ of note 05.

## Questions

**Q:** Define a positive-definite kernel and prove that an inner product of feature maps is one.
**A:** Symmetric $k$ with all Gram matrices PSD. If $k=\langle\phi(x),\phi(x')\rangle$ then $\sum_{ij}c_ic_jk(x_i,x_j)=\|\sum_ic_i\phi(x_i)\|^2\ge0$ and symmetry is inherited from the inner product.

**Q:** Sketch the construction of the RKHS from a PSD kernel, and say where PSD-ness and Cauchy–Schwarz are used.
**A:** On $\mathrm{span}\{k(x,\cdot)\}$ define $\langle\sum\alpha_ik(x_i,\cdot),\sum\beta_jk(x'_j,\cdot)\rangle=\sum\alpha_i\beta_jk(x_i,x'_j)$; it is well-defined because it equals $\sum_j\beta_jf(x'_j)$, symmetric, bilinear, and $\langle f,f\rangle=\alpha^\top K\alpha\ge0$ by PSD-ness.
Cauchy–Schwarz for PSD forms plus the reproducing property gives $|f(x)|^2\le\langle f,f\rangle k(x,x)$, so $\langle f,f\rangle=0\Rightarrow f=0$ (definiteness) and evaluation is bounded; complete the space, the limits are functions because Cauchy sequences converge pointwise.
$\phi(x)=k(x,\cdot)$ is then a feature map.

**Q:** What is the reproducing property and why does it imply evaluation functionals are bounded?
**A:** $f(x)=\langle f,k(x,\cdot)\rangle$ for all $f\in\mathcal H_k$.
Cauchy–Schwarz: $|f(x)|\le\|f\|\,\|k(x,\cdot)\|=\|f\|\sqrt{k(x,x)}$.
Conversely (Riesz) bounded evaluation gives a representer $k_x$, and $k(x,x')=\langle k_x,k_{x'}\rangle$ is the unique reproducing kernel — Moore–Aronszajn.

**Q:** Prove that the product of two PSD kernels is PSD and deduce that the Gaussian kernel is PSD.
**A:** $k_1k_2=\langle\phi_1\otimes\phi_2(x),\phi_1\otimes\phi_2(x')\rangle$, a feature map into the tensor product; matrix form: Hadamard product of $\sum\lambda_au_au_a^\top$ and $\sum\mu_bv_bv_b^\top$ is $\sum\lambda_a\mu_b(u_a\circ v_b)(u_a\circ v_b)^\top\succeq0$.
Then $e^{-\gamma\|x-x'\|^2}=e^{-\gamma\|x\|^2}\cdot e^{2\gamma\langle x,x'\rangle}\cdot e^{-\gamma\|x'\|^2}$: the middle is $\exp$ of a PSD kernel (limit of nonnegative polynomials), the outer product is $f(x)f(x')$; multiply.

**Q:** State and prove the representer theorem.
**A:** For $\min_f c((x_i,y_i,f(x_i))_i)+\Omega(\|f\|)$ with $\Omega$ strictly increasing, every minimiser is $\sum_i\alpha_ik(x_i,\cdot)$.
Proof: decompose $f=f_\parallel+f_\perp$ against $V=\mathrm{span}\{k(x_i,\cdot)\}$; $f_\perp(x_i)=\langle f_\perp,k(x_i,\cdot)\rangle=0$ so the loss ignores $f_\perp$; $\|f\|^2=\|f_\parallel\|^2+\|f_\perp\|^2$ so $\Omega(\|f\|)\ge\Omega(\|f_\parallel\|)$ with equality iff $f_\perp=0$; hence $J(f)\ge J(f_\parallel)$ and a minimiser must have $f_\perp=0$.

**Q:** Why does the representer theorem matter computationally, and give three algorithms that use it.
**A:** It reduces optimisation over an infinite-dimensional $\mathcal H_k$ to $\alpha\in\mathbb R^n$ with $f(x_j)=(K\alpha)_j$ and $\|f\|^2=\alpha^\top K\alpha$.
KRR: $\alpha=(K+\lambda I)^{-1}y$. SVM: hinge loss, $\alpha$ sparse (support vectors).
Kernel logistic regression: Newton in $\alpha$. Also kernel PCA and Gaussian process regression.

**Q:** What does the RKHS norm of the Gaussian kernel measure?
**A:** In Fourier terms $\|f\|^2_{\mathcal H_k}\propto\int|\hat f(\omega)|^2e^{\|\omega\|^2/(4\gamma)}d\omega$: frequency $\omega$ is penalised by $e^{\|\omega\|^2/4\gamma}$, so the norm is a very strong smoothness penalty (functions are analytic); small $\gamma$ penalises harder.
For the Laplacian kernel the weight is polynomial, $\|\omega\|^{d+1}$, a Sobolev norm.

**Q:** State Mercer's theorem and relate it to the feature map.
**A:** For continuous PSD $k$ on a compact $\mathcal X$ with a full-support measure, $k(x,x')=\sum_j\lambda_j\psi_j(x)\psi_j(x')$ with $\lambda_j\ge0$ summable and $\psi_j$ orthonormal eigenfunctions of $T_kf=\int k(\cdot,x')f(x')d\mu$, converging uniformly.
Hence $\phi(x)=(\sqrt{\lambda_j}\psi_j(x))_j\in\ell_2$ is a feature map and $\|f\|_{\mathcal H_k}^2=\sum a_j^2/\lambda_j$ for $f=\sum a_j\psi_j$; eigenvalue decay quantifies the size of the RKHS.

## Code

`src/py/kernels.py`:

- `linear_kernel`, `polynomial_kernel(X, Y, degree, c)`, `rbf_kernel(X, Y, gamma)`, `laplacian_kernel`: the standard kernels of Theorem 8.5; `gram_matrix(k, X, Y)` assembles $K$ for any callable.
- `is_psd(K)`: checks symmetry and the smallest eigenvalue (with tolerance); use it on the $3\times3$ RBF example, on $\tanh$ Gram matrices (fails), and on products/sums of Gram matrices (Theorem 8.4).
- `poly2_feature_map(X)`: the explicit 6-dimensional map for $(1+\langle x,x'\rangle)^2$; verify $\phi(X)\phi(Y)^\top=$ `polynomial_kernel(X, Y, 2, 1)`.
- `feature_distance(k, x, y)`, `centre_gram(K)`: Theorem 8.6(b,c).
- `kernel_rademacher_mc(K, B, n_sigma, rng)`, `kernel_rademacher_bound(K, B)`: $\mathfrak R_S$ of the RKHS ball $\{\|f\|_{\mathcal H}\le B\}$, $\frac Bn\mathbb E\sqrt{\sigma^\top K\sigma}\le\frac Bn\sqrt{\mathrm{tr}K}$ (note 05, Theorem 5.7 in feature space; the complexity term of note 09's margin bound).
- `representer_demo`: regularised least squares in explicit feature space versus the kernel solution: shows $w^*\in\mathrm{span}\{\phi(x_i)\}$ (Theorem 8.7) and $w^*=\Phi^\top\hat\alpha$ (note 07, Theorem 7.8).

## References

- Schölkopf, Smola, *Learning with Kernels* (2002), Ch. 2 (kernels, feature spaces, Mercer, RKHS construction 2.2.2–2.2.3, closure properties 13.1), Ch. 4.2 (representer theorem, Thm 4.2), Ch. 13 (designing kernels: string, convolution kernels).
- Shalev-Shwartz, Ben-David, *Understanding Machine Learning*, Ch. 16 (kernel methods: representer theorem Thm 16.1, characterisation of kernels Lemma 16.2, closure properties Exercise 16.1).
- Mohri, Rostamizadeh, Talwalkar, *Foundations of Machine Learning*, Ch. 6 (PDS kernels Thm 6.2, closure Thms 6.10–6.12, normalised kernels, RKHS, sequence kernels 6.4).
- Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning*, Ch. 5.8 (RKHS), 12.3.
- N. Aronszajn, "Theory of reproducing kernels", *Trans. AMS* 68 (1950).
- J. Mercer, "Functions of positive and negative type and their connection with the theory of integral equations", *Phil. Trans. R. Soc. A* 209 (1909).
- G. Kimeldorf, G. Wahba, "Some results on Tchebycheffian spline functions", *J. Math. Anal. Appl.* 33 (1971); B. Schölkopf, R. Herbrich, A. Smola, "A generalized representer theorem", COLT 2001.
- D. Haussler, "Convolution kernels on discrete structures", UCSC tech. report 1999; T. Gärtner, P. Flach, S. Wrobel, "On graph kernels: hardness results and efficient alternatives", COLT 2003; C. Leslie, E. Eskin, W. Noble, "The spectrum kernel", PSB 2002.
- C. A. Micchelli, "Interpolation of scattered data: distance matrices and conditionally positive definite functions", *Constr. Approx.* 2 (1986).
- I. Steinwart, A. Christmann, *Support Vector Machines* (2008), Ch. 4 (RKHS theory in full generality).
