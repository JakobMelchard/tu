# 06 Regularisation and structural risk minimisation

PAC and VC theory (notes 03–04) tell us how well ERM does *inside a fixed class* $\mathcal H$.
They do not say which class to use. This note is about that choice: the bias–complexity trade-off, Vapnik's structural risk minimisation (choose the class by penalising its complexity), the description-length variant (Occam), and the smooth version of the same idea — Tikhonov regularisation, analysed through algorithmic stability instead of uniform convergence.
It closes with model selection in practice (validation, cross-validation, learning curves).
Notes 07–09 apply the machinery to least squares, kernels and SVMs.

## Definitions

1. **Approximation and estimation error.** For a learner returning $h_S\in\mathcal H$, write $L_{\mathcal D}(h_S)=\underbrace{\min_{h\in\mathcal H}L_{\mathcal D}(h)}_{\varepsilon_{\mathrm{app}}(\mathcal H)}+\underbrace{L_{\mathcal D}(h_S)-\min_{h\in\mathcal H}L_{\mathcal D}(h)}_{\varepsilon_{\mathrm{est}}(\mathcal H,S)}$.
   The approximation error (bias) decreases as $\mathcal H$ grows; the estimation error (variance/complexity) increases.
   For ERM, uniform convergence bounds the estimation term: $\varepsilon_{\mathrm{est}}\le2\sup_{h\in\mathcal H}|L_{\mathcal D}(h)-L_S(h)|$, and for VC classes this is $O\big(\sqrt{(d+\log(1/\delta))/n}\big)$ (note 04).
   Plotting $L_{\mathcal D}(h_S)$ against the complexity of $\mathcal H$ gives the U-shaped curve: bias falling, estimation rising, optimum in between.

2. **Uniform convergence (UC) property.** $\mathcal H$ has UC with sample complexity $m^{\mathrm{UC}}_{\mathcal H}(\varepsilon,\delta)$ if for every $\mathcal D$ and $n\ge m^{\mathrm{UC}}_{\mathcal H}(\varepsilon,\delta)$, with probability $\ge1-\delta$ over $S\sim\mathcal D^n$, $|L_{\mathcal D}(h)-L_S(h)|\le\varepsilon$ for all $h\in\mathcal H$.
   Define the inverse function $\varepsilon_{\mathcal H}(n,\delta)=\min\{\varepsilon:m^{\mathrm{UC}}_{\mathcal H}(\varepsilon,\delta)\le n\}$, the accuracy guaranteed by $n$ samples.
   For $\mathrm{VCdim}(\mathcal H)=d$: $\varepsilon_{\mathcal H}(n,\delta)\le C\sqrt{(d+\log(1/\delta))/n}$.

3. **Nested structure.** $\mathcal H=\bigcup_{k\ge1}\mathcal H_k$ with $\mathcal H_1\subset\mathcal H_2\subset\cdots$, each $\mathcal H_k$ having the UC property with $\varepsilon_k(n,\delta):=\varepsilon_{\mathcal H_k}(n,\delta)$.
   Weights $w:\mathbb N\to[0,1]$ with $\sum_kw_k\le1$ (e.g. $w_k=2^{-k}$ or $w_k=6/(\pi^2k^2)$).
   For $h\in\mathcal H$ let $k(h)=\min\{k:h\in\mathcal H_k\}$.

4. **Structural risk minimisation (SRM).** The rule
$$h_S^{\mathrm{SRM}}\in\arg\min_{h\in\mathcal H}\Big[L_S(h)+\varepsilon_{k(h)}\big(n,w_{k(h)}\delta\big)\Big].$$
Equivalently: run ERM in each $\mathcal H_k$, then pick $k$ minimising empirical risk plus the class penalty.

5. **Nonuniform learnability.** $\mathcal H$ is nonuniformly learnable if there is an algorithm $A$ and a function $m^{\mathrm{NUL}}_{\mathcal H}(\varepsilon,\delta,h)$ such that for every $\varepsilon,\delta\in(0,1)$, every $h\in\mathcal H$ and every $\mathcal D$, if $n\ge m^{\mathrm{NUL}}(\varepsilon,\delta,h)$ then with probability $\ge1-\delta$, $L_{\mathcal D}(A(S))\le L_{\mathcal D}(h)+\varepsilon$.
   The difference from agnostic PAC: the sample size may depend on the competitor $h$, not only on $\varepsilon,\delta$.

6. **Description length.** Fix a prefix-free binary code for $\mathcal H$ (no codeword is a prefix of another); $|h|$ is the length of the codeword of $h$. **Minimum description length (MDL)** rule: $\arg\min_h\big[L_S(h)+\sqrt{(|h|+\log(2/\delta))/(2n)}\big]$.
   Logarithms are natural throughout.

7. **Regularised loss minimisation (RLM) / Tikhonov regularisation.** For $\mathcal H=\{w\in\mathbb R^d\}$ (or a Hilbert space), a convex loss $\ell(w,z)$ and $\lambda>0$,
$$A(S)=\arg\min_w\Big[L_S(w)+\lambda\|w\|_2^2\Big],\qquad L_S(w)=\tfrac1n\sum_i\ell(w,z_i).$$

8. **Strong convexity.** $f$ is $\lambda$-strongly convex if for all $u,v$ and $\alpha\in[0,1]$: $f(\alpha u+(1-\alpha)v)\le\alpha f(u)+(1-\alpha)f(v)-\frac\lambda2\alpha(1-\alpha)\|u-v\|^2$. **Lipschitz loss:** $\ell(\cdot,z)$ is $\rho$-Lipschitz if $|\ell(u,z)-\ell(v,z)|\le\rho\|u-v\|$ for all $z$.

9. **On-average-replace-one stability.** Let $S=(z_1,\dots,z_n)\sim\mathcal D^n$, $z'\sim\mathcal D$ independent, $i$ uniform on $\{1..n\}$, and $S^{(i)}=(z_1,\dots,z_{i-1},z',z_{i+1},\dots,z_n)$.
   Algorithm $A$ is on-average-replace-one stable with rate $\epsilon(n)$ if
$$\mathbb E_{S,z',i}\big[\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)\big]\le\epsilon(n).$$
Interpretation: the loss on $z_i$ does not increase much when $z_i$ is removed from the training set (and replaced by a fresh point).

10. **Validation.** Split the data into a training set $S$ ($n$ points) and a validation set $V$ ($n_v$ points), independent.
    $L_V(h)$ is the empirical risk on $V$. **$k$-fold cross-validation:** partition the data into $k$ folds, train on $k-1$ and evaluate on the held-out one, average the $k$ errors; leave-one-out (LOO) is $k=n$.

## Results

**Theorem 6.1 (SRM uniform bound)** [S9 Thm 7.4]**.** With the setting of Definition 3, for every $\delta\in(0,1)$ and every $n$, with probability $\ge1-\delta$ over $S\sim\mathcal D^n$, simultaneously for all $k$ and all $h\in\mathcal H_k$:
$$|L_{\mathcal D}(h)-L_S(h)|\le\varepsilon_k(n,w_k\delta).$$
Consequently, for every $h\in\mathcal H$: $L_{\mathcal D}(h)\le L_S(h)+\min_{k:h\in\mathcal H_k}\varepsilon_k(n,w_k\delta)=L_S(h)+\varepsilon_{k(h)}(n,w_{k(h)}\delta)$ (for nested classes the minimum is at $k(h)$ provided $\varepsilon_k$ is non-decreasing in $k$, which holds for nested classes since UC accuracy only worsens for larger classes).

*Proof.* Fix $k$. By the UC property of $\mathcal H_k$ applied at confidence $w_k\delta$ (this is exactly what $\varepsilon_k(n,w_k\delta)$ means): the event $E_k=\{\exists h\in\mathcal H_k:|L_{\mathcal D}(h)-L_S(h)|>\varepsilon_k(n,w_k\delta)\}$ has $\Pr[E_k]\le w_k\delta$.
Union bound over the countably many $k$:
$$\Pr\Big[\bigcup_kE_k\Big]\le\sum_kw_k\delta\le\delta.$$
On the complement, every class enjoys its own guarantee. The consequence follows because $h\in\mathcal H_k$ for every $k\ge k(h)$. ∎

**Theorem 6.2 (SRM guarantee)** [S9 Thm 7.5, with $w(n)=6/(\pi^2n^2)$]**.** With probability $\ge1-\delta$, for every $h^*\in\mathcal H$ with $k^*=k(h^*)$,
$$L_{\mathcal D}(h^{\mathrm{SRM}}_S)\le L_{\mathcal D}(h^*)+2\varepsilon_{k^*}(n,w_{k^*}\delta).$$
Hence $\mathcal H$ is nonuniformly learnable with $m^{\mathrm{NUL}}(\varepsilon,\delta,h)\le m^{\mathrm{UC}}_{k(h)}(\varepsilon/2,w_{k(h)}\delta)$.

*Proof.* On the good event of Theorem 6.1, writing $\mathrm{pen}(h)=\varepsilon_{k(h)}(n,w_{k(h)}\delta)$:
$$L_{\mathcal D}(h_S^{\mathrm{SRM}})\le L_S(h_S^{\mathrm{SRM}})+\mathrm{pen}(h_S^{\mathrm{SRM}})\le L_S(h^*)+\mathrm{pen}(h^*)\le L_{\mathcal D}(h^*)+2\,\mathrm{pen}(h^*),$$
using the upper bound of 6.1, the definition of the SRM minimiser, and the lower bound of 6.1 for $h^*$.
If $n\ge m^{\mathrm{UC}}_{k^*}(\varepsilon/2,w_{k^*}\delta)$ then $\mathrm{pen}(h^*)\le\varepsilon/2$. ∎

*Cost of nonuniformity.* Compared with ERM in $\mathcal H_{k^*}$ alone (which knows $k^*$ in advance), SRM pays $\delta\to w_{k^*}\delta$, i.e. an additive $\log(1/w_{k^*})$ inside the square root — for $w_k=2^{-k}$ this is $k^*\log2$: a price logarithmic in the "index" of the right class.
It never pays for the complexity of classes it does not use.

**Theorem 6.3 (characterisation of nonuniform learnability)** [S9 Thm 7.2, Thm 7.3]**.** For binary classification with $0$-$1$ loss, $\mathcal H$ is nonuniformly learnable if and only if it is a countable union of classes each having the uniform convergence property (equivalently, each of finite VC dimension).

*Proof sketch.* ($\Leftarrow$) Theorem 6.2 with any weights $\sum w_k\le1$; each finite-VC class has UC by the fundamental theorem of statistical learning.
($\Rightarrow$) Let $A$ witness nonuniform learnability and set $\mathcal H_k=\{h\in\mathcal H:m^{\mathrm{NUL}}(\tfrac18,\tfrac17,h)\le k\}$.
Then $\mathcal H=\bigcup_k\mathcal H_k$. If some $\mathcal H_k$ had infinite VC dimension, the no-free-lunch theorem (note 04) applied to a shattered set of size $2k$ yields a distribution $\mathcal D$ with a zero-risk $h\in\mathcal H_k$ for which $\Pr[L_{\mathcal D}(A(S))\ge\tfrac18]>\tfrac17$ when $n=k$, contradicting $m^{\mathrm{NUL}}(\tfrac18,\tfrac17,h)\le k$.
So every $\mathcal H_k$ has finite VC dimension. ∎

*Consequence.* The class of all polynomial-threshold classifiers, or of all finite-degree polynomials, is nonuniformly learnable but not PAC learnable (infinite VC dimension).
No-free-lunch is not violated: the sample size depends on the competitor.

**Theorem 6.4 (Occam / MDL bound)** [S9 Thm 7.7, via the Kraft inequality Lemma 7.6]**.** Let $\mathcal H$ be countable with a prefix-free description $h\mapsto|h|$, and let $\ell\in[0,1]$.
With probability $\ge1-\delta$, for all $h\in\mathcal H$:
$$L_{\mathcal D}(h)\le L_S(h)+\sqrt{\frac{|h|+\log(2/\delta)}{2n}}.$$

*Proof.* *Kraft's inequality:* for a prefix-free code, $\sum_h2^{-|h|}\le1$.
(Proof: pick a uniformly random infinite bit string; the events "it starts with the codeword of $h$" are disjoint by prefix-freeness and have probabilities $2^{-|h|}$; disjoint probabilities sum to at most $1$.) So $w_h=2^{-|h|}$ are admissible weights for the singleton classes $\mathcal H_h=\{h\}$.
For a singleton, Hoeffding gives $\Pr[|L_{\mathcal D}(h)-L_S(h)|>\varepsilon]\le2e^{-2n\varepsilon^2}$; setting the right side equal to $w_h\delta=2^{-|h|}\delta$ and solving,
$$\varepsilon_h=\sqrt{\frac{\log(2\cdot2^{|h|}/\delta)}{2n}}=\sqrt{\frac{|h|\log2+\log(2/\delta)}{2n}}\le\sqrt{\frac{|h|+\log(2/\delta)}{2n}}.$$
Theorem 6.1 (union bound with weights $w_h$) finishes. ∎

*Reading.* Among hypotheses with the same training error, prefer the one with the shortest description — Occam's razor, quantified.
The description language is fixed *before* seeing data; otherwise one could encode $S$ itself.

**Theorem 6.5 (strong convexity facts)** [S9 Lemma 13.5]**.** (a) $w\mapsto\lambda\|w\|^2$ is $2\lambda$-strongly convex.
(b) If $f$ is $\lambda$-strongly convex and $g$ convex, $f+g$ is $\lambda$-strongly convex.
(c) If $f$ is $\lambda$-strongly convex and $u$ minimises $f$, then for every $v$: $f(v)-f(u)\ge\frac\lambda2\|v-u\|^2$.

*Proof.* (a) Expand $\|\alpha u+(1-\alpha)v\|^2=\alpha\|u\|^2+(1-\alpha)\|v\|^2-\alpha(1-\alpha)\|u-v\|^2$ (parallelogram-type identity).
(b) Add the two defining inequalities. (c) By the definition with $\alpha\to0^+$: $f(u+\alpha(v-u))\le f(u)+\alpha(f(v)-f(u))-\frac\lambda2\alpha(1-\alpha)\|v-u\|^2$; since $u$ is a minimiser the left side is $\ge f(u)$, so $\alpha(f(v)-f(u))\ge\frac\lambda2\alpha(1-\alpha)\|v-u\|^2$; divide by $\alpha$ and let $\alpha\to0$. ∎

**Theorem 6.6 (stability controls the generalisation gap)** [S9 Thm 13.2; S20]**.** For any learning algorithm $A$ and any loss,
$$\mathbb E_S\big[L_{\mathcal D}(A(S))-L_S(A(S))\big]=\mathbb E_{S,z',i}\big[\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)\big].$$
In particular, if $A$ is on-average-replace-one stable with rate $\epsilon(n)$, then $\mathbb E_SL_{\mathcal D}(A(S))\le\mathbb E_SL_S(A(S))+\epsilon(n)$.

*Proof.* This is an exchange-of-indices identity. First, since $z'$ is independent of $S$ and distributed as $\mathcal D$,
$$\mathbb E_SL_{\mathcal D}(A(S))=\mathbb E_{S,z'}\ell(A(S),z').$$
Now fix $i$. The tuple $(z_1,\dots,z_n,z')$ is i.i.d., so swapping the names of $z_i$ and $z'$ does not change its joint law.
Under the swap, $S$ becomes $S^{(i)}$ and $z'$ becomes $z_i$, hence
$$\mathbb E_{S,z'}\ell(A(S),z')=\mathbb E_{S,z'}\ell(A(S^{(i)}),z_i)\quad\text{for every }i,$$
and averaging over uniform $i$ changes nothing: $\mathbb E_SL_{\mathcal D}(A(S))=\mathbb E_{S,z',i}\ell(A(S^{(i)}),z_i)$.
Second, by definition $L_S(A(S))=\frac1n\sum_i\ell(A(S),z_i)=\mathbb E_i\ell(A(S),z_i)$, so $\mathbb E_SL_S(A(S))=\mathbb E_{S,i}\ell(A(S),z_i)$, and $z'$ can be added to the expectation for free.
Subtract. ∎

**Theorem 6.7 (RLM is stable)** [S20; S9 Cor. 13.6]**.** Let $\ell(\cdot,z)$ be convex and $\rho$-Lipschitz for every $z$.
Then RLM with regulariser $\lambda\|w\|^2$ is on-average-replace-one stable with rate $\frac{2\rho^2}{\lambda n}$.
More precisely, for every $S,z',i$ (not only on average):
$$\|A(S^{(i)})-A(S)\|\le\frac{2\rho}{\lambda n}\qquad\text{and}\qquad\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)\le\frac{2\rho^2}{\lambda n}.$$

*Proof.* Let $f_S(w)=L_S(w)+\lambda\|w\|^2$; by Theorem 6.5(a,b) it is $2\lambda$-strongly convex.
Write $u=A(S)$ (minimiser of $f_S$) and $v=A(S^{(i)})$ (minimiser of $f_{S^{(i)}}$).
By Theorem 6.5(c),
$$f_S(v)-f_S(u)\ge\lambda\|v-u\|^2.\tag{1}$$
On the other hand, $S$ and $S^{(i)}$ differ in one point, so for every $w$: $f_S(w)=f_{S^{(i)}}(w)+\frac1n\big[\ell(w,z_i)-\ell(w,z')\big]$. Therefore
$$f_S(v)-f_S(u)=\underbrace{f_{S^{(i)}}(v)-f_{S^{(i)}}(u)}_{\le0\text{ since }v\text{ minimises }f_{S^{(i)}}}+\frac{\ell(v,z_i)-\ell(u,z_i)}n+\frac{\ell(u,z')-\ell(v,z')}n\le\frac{2\rho\|v-u\|}{n},\tag{2}$$
using the Lipschitz property twice. Combining (1) and (2): $\lambda\|v-u\|^2\le\frac{2\rho}n\|v-u\|$, so $\|v-u\|\le\frac{2\rho}{\lambda n}$.
Finally $\ell(v,z_i)-\ell(u,z_i)\le\rho\|v-u\|\le\frac{2\rho^2}{\lambda n}$. ∎

**Theorem 6.8 (oracle inequality for RLM)** [S9 Cor. 13.8; the optimised-$\lambda$ form is Cor. 13.9]**.** Under the assumptions of Theorem 6.7,
$$\mathbb E_SL_{\mathcal D}(A(S))\le\min_w\Big[L_{\mathcal D}(w)+\lambda\|w\|^2\Big]+\frac{2\rho^2}{\lambda n}.$$
If the comparator satisfies $\|w^*\|\le B$, then choosing $\lambda=\sqrt{2\rho^2/(B^2n)}$ gives
$$\mathbb E_SL_{\mathcal D}(A(S))\le L_{\mathcal D}(w^*)+2\rho B\sqrt{\frac2n}=L_{\mathcal D}(w^*)+O\Big(\frac{\rho B}{\sqrt n}\Big).$$

*Proof.* By Theorems 6.6 and 6.7, $\mathbb EL_{\mathcal D}(A(S))\le\mathbb EL_S(A(S))+\frac{2\rho^2}{\lambda n}$.
Since $A(S)$ minimises $f_S$, for any fixed $w$: $L_S(A(S))\le L_S(A(S))+\lambda\|A(S)\|^2\le L_S(w)+\lambda\|w\|^2$.
Take expectations: $\mathbb EL_S(w)=L_{\mathcal D}(w)$ for fixed $w$.
So $\mathbb EL_{\mathcal D}(A(S))\le L_{\mathcal D}(w)+\lambda\|w\|^2+\frac{2\rho^2}{\lambda n}$ for every $w$.
With $\|w^*\|\le B$ the bound is $\lambda B^2+\frac{2\rho^2}{\lambda n}$, minimised at $\lambda^2=2\rho^2/(B^2n)$ with value $2\sqrt{2\rho^2B^2/n}$. ∎

*Comparison with uniform convergence.* The Rademacher route (note 05) for $\{\|w\|\le B\}$ with a $\rho$-Lipschitz loss gives $2\rho BR/\sqrt n$ where $R$ bounds $\|x\|$; the stability route gives $2\sqrt2\rho B/\sqrt n$ with $\rho$ typically $\propto R$ — the same rate, no VC dimension, no sup over the class, but only in expectation (high-probability versions need extra work, e.g. Bousquet–Elisseeff via McDiarmid, or Feldman–Vondrák 2019 for sharp constants).

**Theorem 6.9 (validation bounds)** [S9 §11.2]**.** Let $\ell\in[0,1]$ and $V$ be a validation set of $n_v$ i.i.d. points independent of $h$.
(a) For a single fixed $h$, with probability $\ge1-\delta$: $|L_{\mathcal D}(h)-L_V(h)|\le\sqrt{\log(2/\delta)/(2n_v)}$.
(b) For $k$ candidates $h_1,\dots,h_k$ (all chosen independently of $V$, e.g. trained on $S$), with probability $\ge1-\delta$, simultaneously for all $j$: $|L_{\mathcal D}(h_j)-L_V(h_j)|\le\sqrt{\log(2k/\delta)/(2n_v)}$.
Hence the validation-selected $\hat h=\arg\min_jL_V(h_j)$ satisfies $L_{\mathcal D}(\hat h)\le\min_jL_{\mathcal D}(h_j)+2\sqrt{\log(2k/\delta)/(2n_v)}$.

*Proof.* (a) Conditional on $h$ (fixed w.r.t. $V$), $L_V(h)$ is an average of $n_v$ i.i.d.
$[0,1]$-valued variables with mean $L_{\mathcal D}(h)$; two-sided Hoeffding: $\Pr[|L_V-L_{\mathcal D}|>\varepsilon]\le2e^{-2n_v\varepsilon^2}$; set equal to $\delta$.
(b) Apply (a) with $\delta/k$ to each $h_j$ and union bound; the finite class $\{h_1,\dots,h_k\}$ is being treated exactly as in the finite-class PAC bound (note 03), but $k$ is tiny compared with the original $\mathcal H$.
For the selection claim, $L_{\mathcal D}(\hat h)\le L_V(\hat h)+\varepsilon\le L_V(h_{j^*})+\varepsilon\le L_{\mathcal D}(h_{j^*})+2\varepsilon$. ∎

*Train–validation–test.* Validation is used to *choose* among candidates, so $L_V(\hat h)$ is optimistically biased (it is a minimum over $k$ noisy estimates — by exactly the $\sqrt{\log k}$ in (b)).
To report an unbiased final error, evaluate $\hat h$ once on a third, untouched test set; then (a) applies.

*$k$-fold cross-validation.* Each fold's error is an unbiased estimate of $L_{\mathcal D}(A(S'))$ for a training set $S'$ of size $n(1-1/k)$, so CV estimates the risk of the *algorithm* trained on slightly fewer points — slightly pessimistic for the final model trained on all $n$ (more so for small $k$).
The $k$ estimates are dependent (overlapping training sets), so the variance is not $\frac1k$ of a single fold's, and there is no clean finite-sample bound for the CV-selected model comparable to Theorem 6.9; the usable theory is stability-based (LOO error is close to the true risk for stable algorithms; Bousquet–Elisseeff 2002) or asymptotic.
In practice $k=5$ or $10$ is the standard compromise between bias ($k$ small) and cost/variance ($k$ large).

*Learning curves.* Plot training and validation error against $n$.
High bias (underfitting): both curves converge quickly to a common high plateau — more data will not help, enlarge $\mathcal H$.
High variance (overfitting): large gap, training error far below validation error, gap shrinking slowly with $n$ — more data or more regularisation helps.
This is the empirical shadow of $L_{\mathcal D}(h_S)\le L_S(h_S)+\varepsilon_{\mathrm{est}}(n)$: the gap is the estimation term, the plateau is the approximation term.

## Worked example

**Polynomial regression on a noisy sine.** Data $x_i$ uniform on $[0,1]$, $y_i=\sin(2\pi x_i)+\epsilon_i$, $\epsilon_i\sim N(0,0.3^2)$, $n=30$ training points, classes $\mathcal H_k=\{$polynomials of degree $\le k\}$, $k=0,\dots,15$, squared loss. `nested_poly_erm` fits each degree by least squares (`poly_features`, `fit_least_squares`).

Qualitative numbers the code produces: training MSE decreases monotonically in $k$ — about $0.55$ at $k=0$ (variance of the sine, $\tfrac12$, plus noise $0.09$), $\approx0.25$ at $k=1$, $\approx0.10$ at $k=3$ (a cubic already captures one period reasonably), $\approx0.08$ for $k=5..9$, and drops towards $0.03$ for $k\ge12$ as the polynomial starts to interpolate noise.
Validation MSE (fresh $n_v=1000$ points, `validation_select`) is U-shaped: $\approx0.55,0.28,\dots$, minimum $\approx0.10$–$0.11$ around $k=3$–$7$, then explodes for $k\ge11$ ($>1$ by $k=15$, with wild oscillations near the boundary of $[0,1]$).
The noise floor is $\sigma^2=0.09$, so the best degrees are essentially optimal.

SRM (`srm_select`): the class $\mathcal H_k$ has $k+1$ parameters (pseudo-dimension $k+1$), so the penalty used is $\varepsilon_k(n,w_k\delta)\approx C\sqrt{\big((k+1)+k\log2+\log(1/\delta)\big)/n}$ with $w_k=2^{-k}$.
The penalty grows like $\sqrt{k/n}$: at $n=30$ it is $\approx0.2$ for $k=1$ and $\approx0.6$ for $k=15$ (with $C=1$, $\delta=0.05$).
Adding it to the training error gives a curve minimised at $k=3$ or $4$ — slightly *more conservative* than validation, which is typical: SRM penalties are worst-case, validation is data-driven.
Both reject $k\ge10$ decisively. `bias_complexity_curve` overlays the three curves (train, validation, train+penalty) to show the U shape.

**Stability of ridge, one point replaced.** One-dimensional ridge: $f_S(w)=\frac1n\sum_i(wx_i-y_i)^2+\lambda w^2$, minimiser $w_S=\frac{\sum_ix_iy_i}{\sum_ix_i^2+n\lambda}$ (set the derivative $\frac2n\sum_ix_i(wx_i-y_i)+2\lambda w$ to zero).
Take $S=\{(1,1),(2,2),(3,2)\}$, $\lambda=1$:
$$u=w_S=\frac{1+4+6}{14+3}=\frac{11}{17}\approx0.647.$$
Replace $z_3=(3,2)$ by $z'=(3,-1)$: $\sum x_iy_i=1+4-3=2$, so
$$v=w_{S^{(3)}}=\frac2{17}\approx0.118,\qquad\|v-u\|=\frac9{17}\approx0.529.$$
Check inequality (1)–(2) of Theorem 6.7 numerically. Losses: $\ell(v,z_3)=(6/17-2)^2=(28/17)^2\approx2.713$; $\ell(u,z_3)=(33/17-2)^2=(1/17)^2\approx0.003$; $\ell(u,z')=(33/17+1)^2=(50/17)^2\approx8.651$; $\ell(v,z')=(6/17+1)^2=(23/17)^2\approx1.830$.
Right side of (2): $\frac13[2.713-0.003+8.651-1.830]=\frac13\cdot9.531\approx3.18$.
Left side of (1): $\lambda\|v-u\|^2=(9/17)^2\approx0.280$. Indeed $0.280\le3.18$.
The replace-one loss increase on the removed point is $\ell(v,z_3)-\ell(u,z_3)\approx2.71$ — large, because squared loss is not globally Lipschitz and the replaced point is an outlier; on a bounded domain $|x|\le3,|y|\le2,|w|\le1$ the loss is $\rho$-Lipschitz with $\rho=2\max|x||wx-y|\le30$, and the general bound $2\rho^2/(\lambda n)=600$ is valid but vacuous.
Increasing $\lambda$ to $10$: $u=11/44=0.25$, $v=2/44\approx0.045$, $\|v-u\|\approx0.205$ — the $1/\lambda$ dependence of $\|v-u\|\le2\rho/(\lambda n)$ is visible. `tikhonov(Phi, y, lam)` computes the multivariate version.

## Pitfalls

- SRM is not "pick the class with smallest training error" (that always picks the largest class) nor "pick the smallest class" — it balances $L_S$ against a penalty that must be a *valid* uniform-convergence bound at confidence $w_k\delta$.
- The weights $w_k$ must be fixed before seeing the data. They encode a prior preference; they are not estimated.
- Nonuniform learnability does not contradict no-free-lunch: the sample size depends on the competitor $h$.
  A countable union of finite-VC classes typically has infinite VC dimension and is *not* PAC learnable.
- In the MDL bound the code must be prefix-free (Kraft); the penalty is $|h|$ in *bits* and the bound has $|h|\log2\le|h|$ inside the square root — the constant is often written sloppily.
- Stability is a property of the *algorithm*, not the class. ERM over a large class can be unstable; RLM over the same class is stable because of strong convexity, not because of a VC argument.
- Theorem 6.7 needs the loss to be convex *and* Lipschitz in $w$.
  Squared loss is not globally Lipschitz; for it one either restricts to a bounded domain or uses the smoothness-based variant (UML Cor. 13.7: $\beta$-smooth loss, stability $\frac{48\beta}{\lambda n}\cdot L_S$-dependent).
- Theorem 6.8 bounds the risk *in expectation over $S$*; converting to a high-probability statement requires additional concentration, not just Markov (which gives only a $1/\delta$ factor).
- Validation error of the *selected* model is optimistically biased; report the test-set error.
  Do not tune anything on the test set — after tuning it has become a validation set.
- Cross-validation estimates the risk of the algorithm at sample size $n(1-1/k)$, not of the final model; its folds are dependent, so a standard error computed as if independent is understated.
- Learning curves: a small gap does not mean a good model (could be high bias); a large gap does not mean more capacity is needed (it means less).

## Questions

**Q:** What are approximation and estimation error, and how does the VC bound enter?
**A:** $L_{\mathcal D}(h_S)=\min_{\mathcal H}L_{\mathcal D}+[L_{\mathcal D}(h_S)-\min_{\mathcal H}L_{\mathcal D}]$; the first term is approximation error (decreasing in $\mathcal H$), the second estimation error, bounded for ERM by twice the uniform deviation $\sup_h|L_{\mathcal D}-L_S|=O(\sqrt{(d+\log(1/\delta))/n})$ (increasing in $\mathcal H$).
Their sum is the U-shaped curve.

**Q:** State the SRM rule and prove the bound it relies on.
**A:** Minimise $L_S(h)+\varepsilon_{k(h)}(n,w_{k(h)}\delta)$ over $h\in\bigcup_k\mathcal H_k$.
Proof: for each $k$ the UC property at confidence $w_k\delta$ gives $\sup_{\mathcal H_k}|L_{\mathcal D}-L_S|\le\varepsilon_k(n,w_k\delta)$ except with probability $w_k\delta$; a union bound over $k$ costs $\sum_kw_k\delta\le\delta$.
Then $L_{\mathcal D}(h_S)\le L_S(h_S)+\mathrm{pen}(h_S)\le L_S(h^*)+\mathrm{pen}(h^*)\le L_{\mathcal D}(h^*)+2\mathrm{pen}(h^*)$.

**Q:** Define nonuniform learnability and characterise it.
**A:** Sample complexity may depend on the competitor $h$: for all $h,\mathcal D$, $n\ge m(\varepsilon,\delta,h)$ implies $L_{\mathcal D}(A(S))\le L_{\mathcal D}(h)+\varepsilon$ w.p.
$\ge1-\delta$. For binary classification, $\mathcal H$ is nonuniformly learnable iff it is a countable union of finite-VC classes: $\Leftarrow$ by SRM; $\Rightarrow$ by setting $\mathcal H_k=\{h:m(\frac18,\frac17,h)\le k\}$ and invoking no-free-lunch.

**Q:** Derive the Occam bound.
**A:** Kraft: prefix-free $\Rightarrow\sum_h2^{-|h|}\le1$, so $w_h=2^{-|h|}$ are valid weights for singleton classes.
Hoeffding for a singleton at confidence $2^{-|h|}\delta$: $\varepsilon_h=\sqrt{(|h|\log2+\log(2/\delta))/(2n)}\le\sqrt{(|h|+\log(2/\delta))/(2n)}$.
Union bound over $h$.

**Q:** Define on-average-replace-one stability and prove that it controls the expected generalisation gap.
**A:** $\mathbb E_{S,z',i}[\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)]\le\epsilon(n)$.
Identity: $\mathbb EL_{\mathcal D}(A(S))=\mathbb E\ell(A(S),z')=\mathbb E\ell(A(S^{(i)}),z_i)$ by swapping the names of the i.i.d. variables $z_i,z'$; and $\mathbb EL_S(A(S))=\mathbb E_{S,i}\ell(A(S),z_i)$.
Subtracting gives gap $=$ stability term exactly.

**Q:** Why is RLM with a convex Lipschitz loss stable, and with what rate?
**A:** $f_S=L_S+\lambda\|w\|^2$ is $2\lambda$-strongly convex, so $f_S(v)-f_S(u)\ge\lambda\|v-u\|^2$ at the minimiser $u$.
Since $f_S$ and $f_{S^{(i)}}$ differ by $\frac1n[\ell(\cdot,z_i)-\ell(\cdot,z')]$ and $v$ minimises $f_{S^{(i)}}$, $f_S(v)-f_S(u)\le\frac{2\rho}n\|v-u\|$.
Hence $\|v-u\|\le\frac{2\rho}{\lambda n}$ and the loss on $z_i$ changes by at most $\frac{2\rho^2}{\lambda n}$.

**Q:** How do you choose $\lambda$ from the stability analysis, and what rate results?
**A:** Oracle inequality $\mathbb EL_{\mathcal D}(A(S))\le L_{\mathcal D}(w^*)+\lambda\|w^*\|^2+\frac{2\rho^2}{\lambda n}$; with $\|w^*\|\le B$, minimise $\lambda B^2+2\rho^2/(\lambda n)$ at $\lambda=\sqrt{2\rho^2/(B^2n)}$, giving excess risk $2\rho B\sqrt{2/n}=O(\rho B/\sqrt n)$ — the same rate as the Rademacher bound for the $B$-ball.

**Q:** Why is the validation error of the selected model biased, and what does $k$-fold CV actually estimate?
**A:** The selected model minimises $L_V$ over $k$ candidates, and the minimum of noisy estimates is biased downward — by up to $\sqrt{\log(2k/\delta)/(2n_v)}$ (union-bound Hoeffding); an untouched test set removes the bias.
$k$-fold CV averages unbiased estimates of the risk of the algorithm trained on $n(1-1/k)$ points, so it is slightly pessimistic for the final model; the folds are dependent, and there is no clean finite-sample theory for CV-based selection beyond stability arguments.

## Code

`src/py/srm.py` (Theorems 6.1, 6.2 with exact risks): nested classes $\mathcal H_k$ = thresholds on the dyadic grid $\{j2^{-k}\}$, $|\mathcal H_k|=2^k+1$, with $\varepsilon_k(n,\delta')=\sqrt{\log(2|\mathcal H_k|/\delta')/(2n)}$ from note 02 and $w_k=6/(\pi^2k^2)$.

- `dyadic_class(k)`, `srm_weight(k)`, `uc_epsilon(size, n, delta)`, `srm_penalties(n, K, delta)`.
- `srm_threshold_select(X, y, K, delta)`: the SRM rule of Definition 4.
- `srm_experiment(problem, n, K, delta, trials, rng)`: frequency with which Theorem 6.1's uniform event and Theorem 6.2's guarantee fail (both $\le\delta$), mean selected $k$ (grows with $n$: nonuniform learning), and SRM vs ERM over the largest class. ERM over $\mathcal H_K$ wins on this problem because $\log|\mathcal H_K|$ overstates the complexity of thresholds (VC dimension 1): SRM's price for not knowing $k$.

`src/py/regularisation.py`:

- `poly_features(x, d)`, `fit_least_squares(Phi, y)`: the nested classes $\mathcal H_k$ and ERM within each (squared loss).
- `nested_poly_erm(x, y, degrees)`: training error as a function of degree; shows monotone decrease.
- `srm_select(x, y, degrees, n, delta)`: adds a VC-style penalty with weights $6/(\pi^2(d+1)^2)$ and a free constant `scale` to the training error; for squared loss this penalty is a heuristic, not a proven $\varepsilon_k$ (use `srm.py` for that).
- `validation_select(x_tr, y_tr, x_val, y_val, degrees)`: held-out selection, Theorem 6.9(b); compare the chosen degree with SRM's.
- `bias_complexity_curve(n, degrees, sigma, rng)`: train and test MSE versus degree, the U shape of Definition 1.
- `tikhonov(Phi, y, lam)`: RLM with squared loss (ridge); cross-checked against `sklearn.linear_model.Ridge` with $\alpha=n\lambda$.
- `rlm_logistic(X, y, lam)`: RLM with the logistic loss (convex, $\|x\|$-Lipschitz) by Newton's method; cross-checked against `LogisticRegression` with $C=1/(2n\lambda)$.
- `stability_experiment(n, d, lam, trials, rng)`: on the unit ball ($\rho=R=1$) measures $\|A(S^{(i)})-A(S)\|$ and $\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)$ against $2\rho/(\lambda n)$ and $2\rho^2/(\lambda n)$ (Theorem 6.7), and the two sides of the identity of Theorem 6.6 over many draws of $(S,z',i)$.
- `validation_bound(k, n_val, delta)`, `validation_experiment(n_val, delta, trials, rng)`: Theorem 6.9(a) over many validation sets.

## References

- Shalev-Shwartz, Ben-David, *Understanding Machine Learning*, Ch. 7 (nonuniform learnability: Thm 7.2, SRM Thms 7.4–7.5, MDL Thm 7.7), Ch. 11 (model selection, validation Thms 11.1–11.2, $k$-fold CV, learning curves), Ch. 13 (regularisation and stability: Thm 13.2, Lemma 13.5, Cor. 13.6–13.8).
- Mohri, Rostamizadeh, Talwalkar, *Foundations of Machine Learning*, Ch. 4.3–4.5 (SRM, penalised ERM, cross-validation), Ch. 14 (algorithmic stability).
- Vapnik, *The Nature of Statistical Learning Theory* (1995), Ch. 4 (structural risk minimisation); Vapnik & Chervonenkis 1974.
- O. Bousquet, A. Elisseeff, "Stability and generalization", *JMLR* 2 (2002).
- V. Feldman, J. Vondrák, "High probability generalization bounds for uniformly stable algorithms with nearly optimal rate", COLT 2019.
- A. Blumer, A. Ehrenfeucht, D. Haussler, M. Warmuth, "Occam's razor", *Inf. Proc. Letters* 24 (1987); J. Rissanen, "Modeling by shortest data description", *Automatica* 14 (1978).
- A. N. Tikhonov, "On the stability of inverse problems", *Dokl. Akad. Nauk SSSR* 39 (1943).
- Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning*, Ch. 7 (model assessment and selection, cross-validation, effective number of parameters).
