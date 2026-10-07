# 02 Finite classes and concentration

Note 01 showed that $L_S(h)$ is an unbiased estimate of $L_{\mathcal D}(h)$ for a *fixed* $h$ but not for the data-dependent $h_S$. The fix is to demand that $L_S$ be close to $L_{\mathcal D}$ *simultaneously for every* $h\in\mathcal H$ (uniform convergence); then whatever $h_S$ the algorithm picks, its empirical risk is trustworthy. Two ingredients make this work for finite $\mathcal H$: a concentration inequality (Hoeffding) controlling one hypothesis, and the union bound controlling all $|\mathcal H|$ of them at once. The result is the first sample-complexity bound of the course, $n=O(\log|\mathcal H|/\varepsilon^2)$, improving to $O(\log|\mathcal H|/\varepsilon)$ in the realisable case. Note 03 packages this as PAC learnability; note 04 replaces $\log|\mathcal H|$ by the VC dimension for infinite classes.

## Definitions

1. **Concentration inequality.** A bound on $P(|X-\mathbb EX|\ge t)$ for a random variable $X$, typically a sum of many independent terms.
2. **Moment generating function (mgf).** $M_X(\lambda)=\mathbb E e^{\lambda X}$, $\lambda\in\mathbb R$, when finite.
3. **Chernoff method.** For any $\lambda>0$: $P(X\ge t)=P(e^{\lambda X}\ge e^{\lambda t})\le e^{-\lambda t}M_X(\lambda)$ (Markov applied to $e^{\lambda X}$), then optimise over $\lambda$.
4. **Union bound.** For events $A_1,\dots,A_k$: $P\bigl(\bigcup_iA_i\bigr)\le\sum_iP(A_i)$. (Subadditivity of measure; no independence needed.)
5. **$\varepsilon$-representative sample.** $S$ is $\varepsilon$-representative for $(\mathcal H,\ell,\mathcal D)$ if
   $$\sup_{h\in\mathcal H}\bigl|L_S(h)-L_{\mathcal D}(h)\bigr|\le\varepsilon.$$
6. **Uniform convergence property.** $\mathcal H$ has the uniform convergence property (w.r.t. $\ell$) if there is $n^{\mathrm{UC}}_{\mathcal H}(\varepsilon,\delta)<\infty$ such that for every $\mathcal D$ and every $n\ge n^{\mathrm{UC}}_{\mathcal H}(\varepsilon,\delta)$, $P_{S\sim\mathcal D^n}(S\text{ is }\varepsilon\text{-representative})\ge1-\delta$.
7. **Consistent learner (realisable case).** An algorithm that returns some $h\in\mathcal H$ with $L_S(h)=0$ whenever one exists. In the realisable case with $f\in\mathcal H$ such an $h$ always exists, and every ERM is consistent.
8. **Bad hypothesis (realisable case).** $\mathcal H_B=\{h\in\mathcal H:L_{\mathcal D}(h)>\varepsilon\}$. The learner fails iff it outputs an element of $\mathcal H_B$.
9. **Bounded differences.** $g:\mathcal Z^n\to\mathbb R$ has bounded differences with constants $c_1,\dots,c_n$ if changing the $i$-th argument alone changes $g$ by at most $c_i$.

Throughout, $\ell$ takes values in $[0,1]$ (true for $\ell_{0\text{-}1}$; for other losses clip or rescale).

## Results

**Theorem 2.1 (Markov)** [S9 Lemma B.1]**.** If $X\ge0$ and $a>0$, then $P(X\ge a)\le\mathbb EX/a$.

*Proof.* $a\,\mathbb 1[X\ge a]\le X$ pointwise (if $X\ge a$ the left side is $a\le X$; otherwise it is $0\le X$). Take expectations: $a\,P(X\ge a)\le\mathbb EX$. ∎

**Theorem 2.2 (Chebyshev)** [S9 Lemma B.2]**.** If $\mathrm{Var}X<\infty$ and $t>0$, then $P(|X-\mathbb EX|\ge t)\le\mathrm{Var}X/t^2$.

*Proof.* Markov applied to $(X-\mathbb EX)^2\ge0$ with $a=t^2$. ∎

For an average $\bar X_n$ of $n$ i.i.d. variables with variance $\sigma^2$, Chebyshev gives $P(|\bar X_n-\mu|\ge\varepsilon)\le\sigma^2/(n\varepsilon^2)$: only polynomial decay in $n$. Bounded variables allow exponential decay.

**Lemma 2.3 (Hoeffding's lemma)** [S13; S10 Lemma D.1]**.** Let $X\in[a,b]$ a.s. Then for all $\lambda\in\mathbb R$,
$$\mathbb E\,e^{\lambda(X-\mathbb EX)}\le\exp\Bigl(\frac{\lambda^2(b-a)^2}{8}\Bigr).$$

*Proof.* Replace $X$ by $X-\mathbb EX$, so assume $\mathbb EX=0$, $a\le0\le b$. By convexity of $x\mapsto e^{\lambda x}$, for $x\in[a,b]$ (write $x$ as the convex combination $\frac{b-x}{b-a}a+\frac{x-a}{b-a}b$):
$$e^{\lambda x}\le\frac{b-x}{b-a}e^{\lambda a}+\frac{x-a}{b-a}e^{\lambda b}.$$
Take expectations, using $\mathbb EX=0$:
$$\mathbb Ee^{\lambda X}\le\frac{b}{b-a}e^{\lambda a}-\frac{a}{b-a}e^{\lambda b}=:e^{\varphi(u)},\qquad u=\lambda(b-a),\ p=\frac{-a}{b-a}\in[0,1],$$
where a direct computation gives $\varphi(u)=-pu+\log\bigl(1-p+pe^u\bigr)$. Now $\varphi(0)=0$,
$$\varphi'(u)=-p+\frac{pe^u}{1-p+pe^u},\qquad\varphi'(0)=0,\qquad\varphi''(u)=\frac{pe^u(1-p)}{(1-p+pe^u)^2}=q(1-q)\le\frac14,$$
with $q=pe^u/(1-p+pe^u)\in[0,1]$. Taylor's theorem with Lagrange remainder: $\varphi(u)=\varphi(0)+\varphi'(0)u+\tfrac12\varphi''(\xi)u^2\le u^2/8=\lambda^2(b-a)^2/8$. ∎

**Theorem 2.4 (Hoeffding's inequality)** [S13; S9 Lemma 4.5]**.** Let $X_1,\dots,X_n$ be independent with $X_i\in[a_i,b_i]$ a.s., and $S_n=\sum_i(X_i-\mathbb EX_i)$. For every $t>0$,
$$P(S_n\ge t)\le\exp\Bigl(-\frac{2t^2}{\sum_i(b_i-a_i)^2}\Bigr),\qquad P(|S_n|\ge t)\le2\exp\Bigl(-\frac{2t^2}{\sum_i(b_i-a_i)^2}\Bigr).$$
In particular, for $X_i\in[0,1]$ and the mean $\bar X_n=\frac1n\sum X_i$ with $\mu=\mathbb E\bar X_n$:
$$P(\bar X_n-\mu\ge\varepsilon)\le e^{-2n\varepsilon^2},\qquad P(|\bar X_n-\mu|\ge\varepsilon)\le2e^{-2n\varepsilon^2}.$$

*Proof.* (One-sided.) Chernoff method: for any $\lambda>0$,
$$P(S_n\ge t)\le e^{-\lambda t}\,\mathbb Ee^{\lambda S_n}=e^{-\lambda t}\prod_{i=1}^n\mathbb Ee^{\lambda(X_i-\mathbb EX_i)}\le e^{-\lambda t}\prod_{i=1}^n e^{\lambda^2(b_i-a_i)^2/8}=\exp\Bigl(-\lambda t+\frac{\lambda^2}{8}\sum_i(b_i-a_i)^2\Bigr),$$
using independence for the product and Lemma 2.3 for each factor. The exponent is a quadratic in $\lambda$ minimised at $\lambda^\star=4t/\sum_i(b_i-a_i)^2>0$, giving the value $-2t^2/\sum_i(b_i-a_i)^2$.
(Two-sided.) Apply the one-sided bound to $-X_i\in[-b_i,-a_i]$ to get the same bound for $P(-S_n\ge t)$, and the union bound for $P(|S_n|\ge t)=P(S_n\ge t)+P(S_n\le-t)$.
(Mean form.) $|\bar X_n-\mu|\ge\varepsilon$ iff $|S_n|\ge n\varepsilon$; with $b_i-a_i=1$ the exponent is $-2(n\varepsilon)^2/n=-2n\varepsilon^2$. ∎

Applied to learning: for a fixed $h$, $X_i=\ell(h(x_i),y_i)\in[0,1]$ are i.i.d. with mean $L_{\mathcal D}(h)$ and $\bar X_n=L_S(h)$. So
$$P_S\bigl(|L_S(h)-L_{\mathcal D}(h)|\ge\varepsilon\bigr)\le2e^{-2n\varepsilon^2}.\tag{$*$}$$

**Lemma 2.5 (uniform convergence ⇒ ERM is $2\varepsilon$-good)** [S9 Lemma 4.2, stated there for $\varepsilon/2$]**.** If $S$ is $\varepsilon$-representative, then every $h_S\in\mathrm{ERM}_{\mathcal H}(S)$ satisfies
$$L_{\mathcal D}(h_S)\le\min_{h\in\mathcal H}L_{\mathcal D}(h)+2\varepsilon.$$

*Proof.* For any $h\in\mathcal H$:
$$L_{\mathcal D}(h_S)\le L_S(h_S)+\varepsilon\le L_S(h)+\varepsilon\le L_{\mathcal D}(h)+2\varepsilon,$$
using representativeness at $h_S$, the ERM property $L_S(h_S)\le L_S(h)$, and representativeness at $h$. Take $h$ to be a minimiser of $L_{\mathcal D}$ over $\mathcal H$ (or an infimising sequence). ∎

Consequently: uniform convergence with parameters $(\varepsilon/2,\delta)$ implies that ERM is $(\varepsilon,\delta)$-successful in the agnostic sense (note 03), i.e. $n_{\mathcal H}(\varepsilon,\delta)\le n^{\mathrm{UC}}_{\mathcal H}(\varepsilon/2,\delta)$.

**Theorem 2.6 (finite classes have the uniform convergence property)** [S9 Cor. 4.6; S10 §2.3]**.** Let $|\mathcal H|<\infty$ and $\ell\in[0,1]$. Then for every $\mathcal D$, $\varepsilon,\delta\in(0,1)$,
$$n\ \ge\ \frac{\log(2|\mathcal H|/\delta)}{2\varepsilon^2}\quad\Longrightarrow\quad P_{S\sim\mathcal D^n}\Bigl(\sup_{h\in\mathcal H}|L_S(h)-L_{\mathcal D}(h)|\le\varepsilon\Bigr)\ge1-\delta.$$
Hence ERM over $\mathcal H$ satisfies $L_{\mathcal D}(h_S)\le\min_{\mathcal H}L_{\mathcal D}+\varepsilon$ with probability $\ge1-\delta$ once $n\ge\frac{2\log(2|\mathcal H|/\delta)}{\varepsilon^2}$.

*Proof.* The bad event is $B=\bigcup_{h\in\mathcal H}B_h$ with $B_h=\{|L_S(h)-L_{\mathcal D}(h)|>\varepsilon\}$. By the union bound and $(*)$,
$$P(B)\le\sum_{h\in\mathcal H}P(B_h)\le|\mathcal H|\cdot2e^{-2n\varepsilon^2}.$$
This is $\le\delta$ iff $e^{2n\varepsilon^2}\ge2|\mathcal H|/\delta$ iff $n\ge\log(2|\mathcal H|/\delta)/(2\varepsilon^2)$. The ERM statement follows from Lemma 2.5 with $\varepsilon$ replaced by $\varepsilon/2$. ∎

Equivalently, solving for $\varepsilon$: with probability $\ge1-\delta$, simultaneously for all $h\in\mathcal H$,
$$|L_S(h)-L_{\mathcal D}(h)|\le\sqrt{\frac{\log(2|\mathcal H|/\delta)}{2n}}.$$

**Theorem 2.7 (realisable case, consistent learners)** [S9 Cor. 2.3; S10 §2.2]**.** Assume $f\in\mathcal H$ with $L_{\mathcal D}(f)=0$ (realisable), $|\mathcal H|<\infty$, and let $A$ be any consistent learner (Definition 7). Then
$$n\ \ge\ \frac{\log(|\mathcal H|/\delta)}{\varepsilon}\quad\Longrightarrow\quad P_{S\sim\mathcal D^n}\bigl(L_{\mathcal D}(A(S))\le\varepsilon\bigr)\ge1-\delta.$$

*Proof.* Fix a bad hypothesis $h\in\mathcal H_B$, i.e. $L_{\mathcal D}(h)>\varepsilon$. Since labels are $f(x_i)$, $h$ is consistent with $S$ iff $h(x_i)=f(x_i)$ for all $i$. The events $\{h(x_i)=f(x_i)\}$ are independent, each of probability $1-L_{\mathcal D}(h)<1-\varepsilon$, so
$$P_S\bigl(L_S(h)=0\bigr)=\bigl(1-L_{\mathcal D}(h)\bigr)^n\le(1-\varepsilon)^n\le e^{-\varepsilon n},$$
using $1-x\le e^{-x}$ (convexity of $e^{-x}$; tangent line at $0$). The learner fails only if it outputs a bad hypothesis, which requires *some* bad hypothesis to be consistent:
$$P_S\bigl(L_{\mathcal D}(A(S))>\varepsilon\bigr)\le P_S\Bigl(\exists h\in\mathcal H_B:\ L_S(h)=0\Bigr)\le\sum_{h\in\mathcal H_B}P_S(L_S(h)=0)\le|\mathcal H_B|\,e^{-\varepsilon n}\le|\mathcal H|\,e^{-\varepsilon n}.$$
This is $\le\delta$ iff $n\ge\log(|\mathcal H|/\delta)/\varepsilon$. ∎

Note the proof does not require $A$ to be ERM in any optimisation sense: *any* rule that outputs a consistent hypothesis works, and the bound holds uniformly over such rules.

**Discussion: $1/\varepsilon$ versus $1/\varepsilon^2$.** Theorem 2.6 needs $n\propto\varepsilon^{-2}$, Theorem 2.7 only $n\propto\varepsilon^{-1}$. The reason is variance. $L_S(h)$ is an average of $n$ Bernoulli$(p)$ variables with $p=L_{\mathcal D}(h)$ and variance $p(1-p)/n$. Hoeffding ignores $p$ and uses the worst case $p=\tfrac12$ (variance $\tfrac1{4n}$), whence deviations of order $n^{-1/2}$ and $n\propto\varepsilon^{-2}$ to resolve $\varepsilon$. In the realisable case the only hypotheses to rule out have $L_S(h)=0$, and for those the relevant question is "how likely is a Bernoulli$(p)$ average to be exactly $0$ when $p>\varepsilon$", which is $(1-p)^n$: the tail is governed by $p$ itself, not by $\sqrt{p(1-p)}$. Bernstein's inequality makes this general: for i.i.d. $X_i\in[0,1]$ with variance $\sigma^2$,
$$P(\bar X_n-\mu\ge\varepsilon)\le\exp\Bigl(-\frac{n\varepsilon^2}{2\sigma^2+2\varepsilon/3}\Bigr).\qquad\text{[S15 Thm 2.10]}$$
When $\sigma^2\le\mu$ (Bernoulli) and $\mu\lesssim\varepsilon$, the denominator is $O(\varepsilon)$ and the exponent is $-\Omega(n\varepsilon)$, i.e. sample complexity $O(1/\varepsilon)$. So the $1/\varepsilon$ rate is really a *low-noise* phenomenon; the same interpolation appears in the agnostic case as "relative deviation" or "Tsybakov noise condition" bounds.

**Theorem 2.8 (bounded differences / McDiarmid; statement only)** [S14; S9 Lemma 26.4; S10 Thm D.8]**.** Let $Z_1,\dots,Z_n$ be independent and $g:\mathcal Z^n\to\mathbb R$ have bounded differences with constants $c_1,\dots,c_n$. Then for $t>0$,
$$P\bigl(g(Z_1,\dots,Z_n)-\mathbb Eg\ge t\bigr)\le\exp\Bigl(-\frac{2t^2}{\sum_ic_i^2}\Bigr),$$
and the same for the lower tail. Hoeffding is the special case $g=\sum_i Z_i$, $c_i=b_i-a_i$. In note 04 and in the Rademacher-complexity note it is applied to $g(S)=\sup_{h\in\mathcal H}(L_{\mathcal D}(h)-L_S(h))$, which has bounded differences with $c_i=1/n$ when $\ell\in[0,1]$: replacing one example changes each $L_S(h)$ by at most $1/n$, hence the supremum by at most $1/n$. The conclusion is that $\sup_h(L_{\mathcal D}-L_S)$ concentrates around its expectation within $\sqrt{\log(1/\delta)/(2n)}$, so only the *expectation* needs to be bounded.

## Worked example

**Sample complexities for $|\mathcal H|=1000$, $\varepsilon=0.05$, $\delta=0.05$.**

Agnostic (Theorem 2.6, $\varepsilon$-representative):
$$n\ge\frac{\log(2\cdot1000/0.05)}{2\cdot0.05^2}=\frac{\log 40000}{0.005}=\frac{10.597}{0.005}\approx2119.3\ \Rightarrow\ n=2120.$$
If one wants ERM to be $\varepsilon$-good (Lemma 2.5 with $\varepsilon/2$): $n\ge\frac{2\log 40000}{0.05^2}\approx8477$.

Realisable (Theorem 2.7):
$$n\ge\frac{\log(1000/0.05)}{0.05}=\frac{\log 20000}{0.05}=\frac{9.903}{0.05}\approx198.1\ \Rightarrow\ n=199.$$

Ratio $2120/199\approx10.7$; the $\varepsilon^{-2}$ vs $\varepsilon^{-1}$ factor is $1/\varepsilon=20$, reduced by the factor $2$ in the denominator and the slightly different logarithms. Note how weak the dependence on $|\mathcal H|$ is: doubling $|\mathcal H|$ adds $\log2/(2\varepsilon^2)\approx139$ samples in the agnostic case and $\log 2/\varepsilon\approx14$ in the realisable case.

**Numeric Hoeffding check for a coin.** Fair coin, $n=100$ tosses, $\varepsilon=0.1$, so the event is $|\bar X_n-\tfrac12|\ge0.1$, i.e. at most $40$ or at least $60$ heads.
- Hoeffding: $2e^{-2\cdot100\cdot0.01}=2e^{-2}\approx0.271$.
- Chebyshev: $\mathrm{Var}\bar X_n=\tfrac{1/4}{100}=0.0025$, bound $0.0025/0.01=0.25$.
- Exact: $2\,P(\mathrm{Bin}(100,\tfrac12)\le40)\approx2\cdot0.0284\approx0.057$.

At $n=100$ Hoeffding and Chebyshev are comparable and both loose by a factor $\approx5$. At $n=1000$: Hoeffding $2e^{-20}\approx4\cdot10^{-9}$, Chebyshev $0.025$, exact $\approx2\cdot P(\mathrm{Bin}(1000,\tfrac12)\le400)\approx4\cdot10^{-10}$. Hoeffding captures the exponential rate; Chebyshev does not. `hoeffding_empirical` in the code reproduces the exact figures by simulation.

**Union bound in action.** $|\mathcal H|=1000$ hypotheses, each with $L_{\mathcal D}(h)=\tfrac12$ and independent losses (worst case for the union bound), $n=100$, $\varepsilon=0.1$. Per-hypothesis deviation probability $\approx0.057$; the union bound gives $P(\text{some }h\text{ deviates})\le57$, vacuous, but the true value is $1-(1-0.057)^{1000}\approx1$: some hypothesis *will* look $10\%$ better than it is. This is the optimism of Theorem 1.3(b) quantified: with $n=100$ one cannot trust the training error of the best of $1000$ hypotheses to within $0.1$. At $n=2120$ (the computed bound), per-hypothesis probability is $\le2e^{-2\cdot2120\cdot0.0025}=2e^{-10.6}\approx5\cdot10^{-5}$ and the union bound gives $\le0.05$.

## Pitfalls

- Hoeffding requires *bounded* and *independent* summands; it does not require identical distributions. For unbounded losses (squared loss on $\mathbb R$) one needs truncation or sub-Gaussian assumptions.
- The union bound does not need independence between the events $B_h$; it is loose when they are highly correlated (similar hypotheses), which is why $\log|\mathcal H|$ is replaced by growth-function / covering-number quantities later.
- Uniform convergence is a property of $(\mathcal H,\ell)$, holding for *all* $\mathcal D$; the sample size bound is distribution-free.
- Lemma 2.5 has a factor $2$: $\varepsilon$-representative gives $2\varepsilon$-good ERM. Sample-complexity statements must say which $\varepsilon$ they mean; UML states $n^{\mathrm{UC}}(\varepsilon/2,\delta)$ for this reason.
- In Theorem 2.7 the bound holds for *any* consistent learner; in the agnostic case (Theorem 2.6) it holds for ERM specifically, via uniform convergence. "Consistent" is not defined in the agnostic case because no $h$ has $L_S=0$ in general.
- $(1-\varepsilon)^n\le e^{-\varepsilon n}$ is a tangent-line bound, tight for small $\varepsilon$; do not replace it by $(1-\varepsilon)^n\approx1-n\varepsilon$, which is wrong for $n\varepsilon\gtrsim1$.
- The realisable bound assumes $f\in\mathcal H$ exactly. If $\min_{\mathcal H}L_{\mathcal D}=\gamma>0$ but small, no consistent hypothesis exists in general and one must fall back to the $\varepsilon^{-2}$ bound (or use relative-deviation bounds giving $n\propto(\gamma+\varepsilon)/\varepsilon^2$).
- $\log$ means natural logarithm throughout; constants change with the base.

## Questions

**Q:** State and prove Hoeffding's lemma.
**A:** $X\in[a,b]$, $\mathbb Ee^{\lambda(X-\mathbb EX)}\le e^{\lambda^2(b-a)^2/8}$. Centre $X$; bound $e^{\lambda x}$ above by the chord of the convex function on $[a,b]$; take expectations to get $e^{\varphi(u)}$ with $\varphi(u)=-pu+\log(1-p+pe^u)$, $u=\lambda(b-a)$, $p=-a/(b-a)$; $\varphi(0)=\varphi'(0)=0$, $\varphi''\le\tfrac14$; Taylor gives $\varphi(u)\le u^2/8$.

**Q:** Derive Hoeffding's inequality from the lemma.
**A:** Chernoff: $P(S_n\ge t)\le e^{-\lambda t}\prod_i\mathbb Ee^{\lambda(X_i-\mathbb EX_i)}\le\exp(-\lambda t+\lambda^2\sum(b_i-a_i)^2/8)$ by independence and the lemma; optimise $\lambda=4t/\sum(b_i-a_i)^2$ to get $\exp(-2t^2/\sum(b_i-a_i)^2)$; two-sided by symmetry plus union bound.

**Q:** What does "$\varepsilon$-representative" mean and why does it make ERM work?
**A:** $\sup_{h\in\mathcal H}|L_S(h)-L_{\mathcal D}(h)|\le\varepsilon$. Then $L_{\mathcal D}(h_S)\le L_S(h_S)+\varepsilon\le L_S(h^\ast)+\varepsilon\le L_{\mathcal D}(h^\ast)+2\varepsilon$, so ERM is within $2\varepsilon$ of the best in class. Uniformity is essential because $h_S$ is data-dependent.

**Q:** Prove that finite classes have the uniform convergence property and give the sample size.
**A:** Hoeffding per hypothesis: $P(|L_S(h)-L_{\mathcal D}(h)|>\varepsilon)\le2e^{-2n\varepsilon^2}$; union bound over $|\mathcal H|$: total $\le2|\mathcal H|e^{-2n\varepsilon^2}\le\delta$ iff $n\ge\log(2|\mathcal H|/\delta)/(2\varepsilon^2)$.

**Q:** Prove the $O(\log(|\mathcal H|/\delta)/\varepsilon)$ bound in the realisable case.
**A:** A bad $h$ ($L_{\mathcal D}(h)>\varepsilon$) survives $n$ i.i.d. labelled points with probability $(1-L_{\mathcal D}(h))^n\le(1-\varepsilon)^n\le e^{-\varepsilon n}$; union bound over at most $|\mathcal H|$ bad hypotheses; set $|\mathcal H|e^{-\varepsilon n}\le\delta$. Any consistent learner outputs a surviving hypothesis, so it fails with probability $\le\delta$.

**Q:** Why is the realisable rate $1/\varepsilon$ but the agnostic rate $1/\varepsilon^2$?
**A:** Agnostic: must estimate each $L_{\mathcal D}(h)$ to accuracy $\varepsilon$; Bernoulli averages have standard deviation $\sqrt{p(1-p)/n}$, worst case $\tfrac1{2\sqrt n}$, so $n\sim\varepsilon^{-2}$. Realisable: only need to kill hypotheses with $p>\varepsilon$ that show zero errors; probability $(1-p)^n\le e^{-\varepsilon n}$, so $n\sim\varepsilon^{-1}$. Bernstein's inequality interpolates: exponent $-n\varepsilon^2/(2\sigma^2+2\varepsilon/3)$ becomes $-\Omega(n\varepsilon)$ when $\sigma^2=O(\varepsilon)$.

**Q:** What is McDiarmid's inequality and what is it used for in learning theory?
**A:** For independent $Z_i$ and $g$ with bounded differences $c_i$, $P(g-\mathbb Eg\ge t)\le\exp(-2t^2/\sum c_i^2)$. Applied to $g(S)=\sup_h(L_{\mathcal D}(h)-L_S(h))$ with $c_i=1/n$: the worst-case gap concentrates around its mean within $\sqrt{\log(1/\delta)/(2n)}$, reducing generalisation bounds to bounding $\mathbb E\sup_h(L_{\mathcal D}-L_S)$ (Rademacher complexity, VC via symmetrisation).

**Q:** Is the union bound tight? When is it very loose?
**A:** Tight when the events are disjoint or nearly so; loose when they overlap heavily. For a hypothesis class with many near-identical hypotheses the events $B_h$ almost coincide, and $\log|\mathcal H|$ overcounts; growth function and covering numbers count "effectively distinct" hypotheses instead.

## Cards

```card id=tfml-hoeffding-inequality
State Hoeffding's inequality (two-sided) for independent $X_i\in[a_i,b_i]$, $S_n=\sum_i(X_i-\mathbb EX_i)$.
---
$$P(|S_n|\ge t)\le 2\exp\!\left(-\frac{2t^2}{\sum_i(b_i-a_i)^2}\right)$$
Needs bounded and independent summands, not identical distributions.
```

```card id=tfml-finite-agnostic-sample-complexity
Sample complexity of uniform convergence for a finite class $\mathcal H$, loss in $[0,1]$, accuracy $\varepsilon$, confidence $\delta$?
---
$$n\ge\frac{\log(2|\mathcal H|/\delta)}{2\varepsilon^2}$$
Hoeffding per hypothesis, union bound over $|\mathcal H|$.
```

```card id=tfml-finite-realisable-sample-complexity
Realisable case, finite $\mathcal H$: how many samples so any consistent learner has $L_{\mathcal D}\le\varepsilon$ w.p. $\ge1-\delta$?
---
$$n\ge\frac{\log(|\mathcal H|/\delta)}{\varepsilon}$$
A bad $h$ survives with probability $(1-\varepsilon)^n\le e^{-\varepsilon n}$; union bound over bad hypotheses.
```

```card id=tfml-eps-vs-eps2
Why $1/\varepsilon$ in the realisable case but $1/\varepsilon^2$ in the agnostic case?
---
Variance. Hoeffding ignores $p=L_{\mathcal D}(h)$ and pays the worst case $p=\tfrac12$, so deviations are $n^{-1/2}$. In the realisable case one only rules out $h$ with $L_S(h)=0$, whose probability $(1-p)^n$ is governed by $p$ itself.
```

## Code

`src/py/concentration.py`:
- `hoeffding_bound(n, eps)`: evaluates $2e^{-2n\varepsilon^2}$ (Theorem 2.4, mean form).
- `hoeffding_empirical(p, n, eps, trials, rng)`: Monte-Carlo estimate of $P(|\bar X_n-p|\ge\varepsilon)$ for Bernoulli$(p)$ coins, to compare against the bound (the coin check above).
- `union_bound_experiment(n_hyps, n, eps, trials, rng)`: simulates `n_hyps` independent hypotheses with risk $\tfrac12$ and reports how often at least one has $|L_S-L_{\mathcal D}|>\varepsilon$, versus the union-bound prediction.
- `sample_complexity_finite(size_H, eps, delta, realisable)`: the two sample sizes of Theorems 2.6 and 2.7 (used in the worked example).
- `epsilon_from_n(n, size_H, delta, realisable)`: inverts the bounds to give the accuracy $\varepsilon$ guaranteed at sample size $n$.
- `binomial_tail_exact(p, n, eps)`: the exact $P(|\mathrm{Bin}(n,p)/n-p|\ge\varepsilon)$ of the coin check ($0.0569$ at $n=100$).
- `uniform_deviation_finite(problem, k, n, trials, rng)`: $\sup_{h\in\mathcal H_k}|L_S(h)-L_{\mathcal D}(h)|$ on many resamples with exact $L_{\mathcal D}$; the demo compares its 95 % quantile with $\varepsilon(n)=\sqrt{\log(2k/\delta)/(2n)}$ (Theorem 2.6).

## References

- Shalev-Shwartz & Ben-David, *UML* (2014): Ch. 2.3 (finite classes, realisable bound), Ch. 4 (uniform convergence, $\varepsilon$-representative, finite classes agnostic), Appendix B (Markov, Chebyshev, Hoeffding, McDiarmid; Lemma B.4 for $(1-\varepsilon)^n\le e^{-\varepsilon n}$), Lemma B.10 (Bernstein).
- Mohri, Rostamizadeh & Talwalkar, *FoML* (2018): Ch. 2.2 (finite consistent case), Ch. 2.3 (finite inconsistent case), Appendix D (concentration inequalities, Hoeffding's lemma D.1, McDiarmid D.8).
- Boucheron, Lugosi & Massart, *Concentration Inequalities* (2013): Ch. 2 (Chernoff method, Hoeffding, Bernstein), Ch. 6 (bounded differences).
- W. Hoeffding, "Probability inequalities for sums of bounded random variables", *JASA* 58 (1963).
- C. McDiarmid, "On the method of bounded differences", *Surveys in Combinatorics* (1989).
