# 12 Oral exam question bank

> **Provenance: every question here is ours.** None is modelled on a real past
> paper, because **no past exam material for this course exists in public**: the
> assessment ends in an *oral* exam, the VoWi page is an empty stub with no
> attachments [S8], and all course material is behind the TUWEL login [S6]
> (not accessed here). See [`00-exam-focus.md`](00-exam-focus.md) §3.
> These questions are derived from the TISS learning outcomes [S2], in particular
> "**prove** learning theoretical results and algorithmic properties", and from
> the theorems the published topic list rests on. Use them as a self-test, not as
> a prediction.
>
> **The oral exam (state 2026-09-27, TISS unchanged):** a separate hurdle,
> $\ge50\%$ of its points on its own, independent of the $\ge50\%$ on
> coursework+project combined; repeatable once; date communicated via TUWEL only
> [S1]. Format, length and whether the project is defended in the same session
> are not public.

Forty questions spanning notes 01–11, each with a compact model answer containing the key formula and the key proof step. Practise by covering the answer, speaking the answer aloud in under three minutes, and writing the central inequality on paper. Notation as in the other notes: $n$ sample size, $\mathcal H$ hypothesis class, $L_{\mathcal D}$ true risk, $L_S$ empirical risk, $d$ VC dimension, $\mathfrak R$ Rademacher complexity.

## Framework (note 01)

**1. Define true risk, empirical risk, Bayes risk and the ERM rule. Derive the Bayes optimal classifier for 0-1 loss.**
$L_{\mathcal D}(h)=\mathbb E_{(x,y)\sim\mathcal D}\,\ell(h(x),y)$; $L_S(h)=\frac1n\sum_i\ell(h(x_i),y_i)$; $L^*=\inf_{h\text{ measurable}}L_{\mathcal D}(h)$; $\mathrm{ERM}_{\mathcal H}(S)\in\arg\min_{h\in\mathcal H}L_S(h)$. With $\eta(x)=P(y=1\mid x)$, the conditional risk of predicting $\hat y$ at $x$ is $P(y\ne\hat y\mid x)=\eta(x)\mathbb 1[\hat y=-1]+(1-\eta(x))\mathbb 1[\hat y=1]$, minimised pointwise by $h^*(x)=\operatorname{sign}(\eta(x)-\tfrac12)$; $L^*=\mathbb E\min\{\eta(x),1-\eta(x)\}$.

**2. Prove that $\mathbb E_S L_S(h)=L_{\mathcal D}(h)$ for a fixed $h$, and that $\mathbb E_S L_S(h_S)\le\min_{h\in\mathcal H}L_{\mathcal D}(h)$ for the ERM output $h_S$. Why is the second inequality not an equality?**
Fixed $h$: linearity of expectation over i.i.d. terms. ERM: for any fixed $h'\in\mathcal H$, $L_S(h_S)\le L_S(h')$ pointwise in $S$, so $\mathbb E L_S(h_S)\le\mathbb E L_S(h')=L_{\mathcal D}(h')$; take the min over $h'$. Not an equality because $h_S$ depends on $S$: the empirical risk of the chosen hypothesis is biased downward (optimism); the gap is the generalisation gap, which grows with the richness of $\mathcal H$.

**3. Write the excess risk of $h_S$ as approximation plus estimation error and explain the trade-off.**
$L_{\mathcal D}(h_S)-L^*=\underbrace{L_{\mathcal D}(h_S)-\min_{h\in\mathcal H}L_{\mathcal D}(h)}_{\text{estimation}}+\underbrace{\min_{h\in\mathcal H}L_{\mathcal D}(h)-L^*}_{\text{approximation}}$. Enlarging $\mathcal H$ decreases approximation error and increases estimation error (bounded by $2\sup_h|L_{\mathcal D}(h)-L_S(h)|$, which grows with the capacity of $\mathcal H$). Choosing the size of $\mathcal H$ is model selection (note 06).

## Concentration and finite classes (note 02)

**4. State Hoeffding's lemma and prove Hoeffding's inequality from it.**
Lemma: $X\in[a,b]$ a.s. ⇒ $\mathbb E e^{\lambda(X-\mathbb EX)}\le e^{\lambda^2(b-a)^2/8}$. Inequality: for independent $X_i\in[a,b]$ and $\bar X=\frac1n\sum X_i$, $P(\bar X-\mathbb E\bar X\ge\varepsilon)\le e^{-2n\varepsilon^2/(b-a)^2}$. Proof (Chernoff): for $\lambda>0$, $P(\sum(X_i-\mathbb EX_i)\ge n\varepsilon)\le e^{-\lambda n\varepsilon}\prod_i\mathbb Ee^{\lambda(X_i-\mathbb EX_i)}\le\exp(-\lambda n\varepsilon+n\lambda^2(b-a)^2/8)$; minimise over $\lambda$: $\lambda^*=4\varepsilon/(b-a)^2$ gives the exponent $-2n\varepsilon^2/(b-a)^2$. Two-sided by symmetry (factor 2).

**5. Prove that a finite class has the uniform convergence property with $n\ge\frac{\log(2|\mathcal H|/\delta)}{2\varepsilon^2}$, and deduce the guarantee for ERM.**
For each fixed $h$, Hoeffding with loss in $[0,1]$: $P(|L_S(h)-L_{\mathcal D}(h)|>\varepsilon)\le2e^{-2n\varepsilon^2}$. Union bound over $\mathcal H$: $P(\exists h:|L_S(h)-L_{\mathcal D}(h)|>\varepsilon)\le2|\mathcal H|e^{-2n\varepsilon^2}\le\delta$ for the stated $n$. On the complement, $L_{\mathcal D}(h_S)\le L_S(h_S)+\varepsilon\le L_S(h')+\varepsilon\le L_{\mathcal D}(h')+2\varepsilon$ for every $h'$: ERM is $2\varepsilon$-optimal.

**6. In the realisable case the sample complexity is $\frac{\log(|\mathcal H|/\delta)}{\varepsilon}$. Prove it and explain why $1/\varepsilon$ instead of $1/\varepsilon^2$.**
Call $h$ bad if $L_{\mathcal D}(h)>\varepsilon$. A bad $h$ is consistent with $S$ with probability $(1-L_{\mathcal D}(h))^n\le(1-\varepsilon)^n\le e^{-\varepsilon n}$. Union bound over the at most $|\mathcal H|$ bad hypotheses: $P(\text{some bad }h\text{ is consistent})\le|\mathcal H|e^{-\varepsilon n}\le\delta$. Any consistent learner then outputs a good $h$. The rate is $1/\varepsilon$ because the events have probability near 0: the variance of a Bernoulli($p$) is $p(1-p)\approx p$, so deviations of order $p$ concentrate exponentially in $np$ rather than $n\varepsilon^2$ (Bernstein/Chernoff regime).

**7. True or false: "Hoeffding's inequality applied to $L_S(h_S)$ shows that the ERM's training error is close to its true risk." Justify.**
False. Hoeffding needs the summands $\ell(h(x_i),y_i)$ to be independent for a *fixed* $h$; $h_S$ depends on all $(x_i,y_i)$ so the summands are dependent. The fix is uniform convergence over $\mathcal H$ (union bound or Rademacher), which costs a capacity term.

## PAC learning (note 03)

**8. Define PAC learnability and agnostic PAC learnability. What are the roles of $\varepsilon$ and $\delta$?**
$\mathcal H$ is PAC learnable if there is a learner $A$ and $n_{\mathcal H}(\varepsilon,\delta)$ such that for every $\varepsilon,\delta\in(0,1)$, every $\mathcal D$ over $\mathcal X$ and every target $f\in\mathcal H$ (realisable), with probability $\ge1-\delta$ over $S\sim\mathcal D^n$, $n\ge n_{\mathcal H}$: $L_{\mathcal D}(A(S))\le\varepsilon$. Agnostic: no target, arbitrary $\mathcal D$ over $\mathcal X\times\mathcal Y$, guarantee $L_{\mathcal D}(A(S))\le\min_{h\in\mathcal H}L_{\mathcal D}(h)+\varepsilon$. $\varepsilon$ = accuracy ("approximately correct"), $\delta$ = confidence ("probably"); the bound is distribution-free but class-dependent.

**9. State the No-Free-Lunch theorem and sketch the proof. What does it imply?**
For any learner $A$ over a domain $\mathcal X$ with $|\mathcal X|\ge2n$, there is a distribution $\mathcal D$ and a target $f$ with $L_{\mathcal D}(f)=0$ such that $\mathbb E_S L_{\mathcal D}(A(S))\ge1/4$, hence $P(L_{\mathcal D}(A(S))\ge1/8)\ge1/7$. Sketch: take $C\subseteq\mathcal X$, $|C|=2n$, $\mathcal D$ uniform on $C$, and average over all $2^{2n}$ labellings $f$ of $C$. For any sample $S$ of $n$ points at least $n$ points of $C$ are unseen; for each unseen $x$ and each labelling $f$, the labelling $f'$ that flips $f(x)$ produces the same $S$, so $A$ errs on $x$ for exactly one of $f,f'$: the average error on unseen points is $1/2$, giving expected risk $\ge\frac12\cdot\frac12=\frac14$ for the worst $f$. The tail bound follows from $\mathbb E Z\ge1/4$ for $Z\in[0,1]$ (reverse Markov). Implication: the class of all functions is not PAC learnable; prior knowledge (a restricted $\mathcal H$) is necessary.

**10. Give a PAC learner for axis-aligned rectangles and prove its sample complexity.**
Output the tightest rectangle $R_S$ containing the positive examples ($R_S\subseteq R^*$). Define four strips inside $R^*$ along its sides, each of $\mathcal D$-mass exactly $\varepsilon/4$ (shrink from each side). If $S$ hits all four strips then $R^*\setminus R_S\subseteq$ union of strips, so $L_{\mathcal D}(R_S)\le\varepsilon$. A strip is missed with probability $(1-\varepsilon/4)^n\le e^{-\varepsilon n/4}$; union bound: failure $\le4e^{-\varepsilon n/4}\le\delta$ iff $n\ge\frac4\varepsilon\log\frac4\delta$.

**11. Boolean conjunctions over $d$ variables: size of the class, a consistent learner, and the resulting sample complexity.**
$|\mathcal H|=3^d$ (each variable appears positively, negatively or not at all; plus the always-false conjunction if wanted). Learner: start with all $2d$ literals; for each positive example delete the literals it falsifies; the result is consistent if the data are realisable. Realisable finite-class bound: $n\ge\frac{d\log3+\log(1/\delta)}{\varepsilon}=O\big((d+\log(1/\delta))/\varepsilon\big)$. Also efficient: $O(nd)$ time.

## VC dimension (note 04)

**12. Define shattering, VC dimension and the growth function. What exactly must you show to prove $\mathrm{VCdim}(\mathcal H)=d$?**
$\mathcal H$ shatters $C$ if $\mathcal H_C=\{(h(c_1),\dots,h(c_m)):h\in\mathcal H\}$ has all $2^{|C|}$ labelings. $\mathrm{VCdim}$ = size of the largest shattered set. $\tau_{\mathcal H}(n)=\max_{|C|=n}|\mathcal H_C|$. Two obligations: exhibit *one* set of size $d$ that is shattered, and show that *every* set of size $d+1$ is not shattered (find, for an arbitrary set, one labeling that is impossible).

**13. Prove that axis-aligned rectangles in $\mathbb R^2$ have VC dimension 4.**
Lower bound: the four points $(0,\pm1),(\pm1,0)$ (a diamond) are shattered: for any subset take the bounding box of the subset; the excluded points lie strictly outside it because each is extreme in its own coordinate. Upper bound: for any five points choose a topmost, bottommost, leftmost and rightmost (some may coincide); the fifth point lies in the bounding box of these. Labeling the four extreme points $+$ and the fifth $-$ is impossible, since any rectangle containing the four contains their bounding box.

**14. Prove the Sauer–Shelah lemma.**
Claim: $|\mathcal H_C|\le|\{B\subseteq C:\mathcal H\text{ shatters }B\}|$ (which is $\le\sum_{i\le d}\binom ni$ for $|C|=n$). Induction on $n$. $n=1$: trivial (empty set always shattered). Step: $C=C'\cup\{c\}$. Let $Y_0=\mathcal H_C$ projected to $C'$ and $Y_1=$ those labelings of $C'$ that extend to $C$ in *both* ways at $c$. Then $|\mathcal H_C|=|Y_0|+|Y_1|$. By induction $|Y_0|\le\#\{B\subseteq C'\text{ shattered}\}$. The class $\mathcal H'=\{h\in\mathcal H:\exists h'\in\mathcal H,\ h'=h\text{ on }C',\ h'(c)\ne h(c)\}$ realises $Y_1$ on $C'$, and if $\mathcal H'$ shatters $B\subseteq C'$ then $\mathcal H$ shatters $B\cup\{c\}$; so $|Y_1|\le\#\{B\subseteq C'\text{ shattered by }\mathcal H'\}\le\#\{B\subseteq C: c\in B,\ B\text{ shattered by }\mathcal H\}$. Adding: $|\mathcal H_C|\le\#\{B\subseteq C\text{ shattered}\}$. Since a shattered set has size $\le d$, the count is $\le\sum_{i\le d}\binom ni\le(en/d)^d$.

**15. State the fundamental theorem of statistical learning (qualitative and quantitative forms).**
For binary classification with 0-1 loss the following are equivalent: (i) $\mathcal H$ has the uniform convergence property; (ii) any ERM is a successful agnostic PAC learner; (iii) $\mathcal H$ is agnostic PAC learnable; (iv) any ERM is a successful PAC learner; (v) $\mathcal H$ is PAC learnable; (vi) $\mathrm{VCdim}(\mathcal H)=d<\infty$. Quantitatively, with absolute constants $C_1,C_2$: agnostic $C_1\frac{d+\log(1/\delta)}{\varepsilon^2}\le n_{\mathcal H}\le C_2\frac{d+\log(1/\delta)}{\varepsilon^2}$; realisable $C_1\frac{d+\log(1/\delta)}{\varepsilon}\le n_{\mathcal H}\le C_2\frac{d\log(1/\varepsilon)+\log(1/\delta)}{\varepsilon}$.

**16. Sketch the proof that finite VC dimension implies uniform convergence.**
Sauer gives $\tau_{\mathcal H}(2n)\le(2en/d)^d$. Symmetrisation (ghost sample $S'$): $\mathbb E_S\sup_h|L_{\mathcal D}(h)-L_S(h)|\le\mathbb E_{S,S'}\sup_h|L_{S'}(h)-L_S(h)|$; introducing random signs $\sigma_i$ does not change the distribution of $L_{S'}(h)-L_S(h)$, and conditional on $S\cup S'$ only $\tau_{\mathcal H}(2n)$ distinct labelings matter, so Massart's finite-class lemma gives $\mathbb E\sup_h|L_{\mathcal D}(h)-L_S(h)|\le\frac{4+\sqrt{\log\tau_{\mathcal H}(2n)}}{\sqrt{2n}}=O\big(\sqrt{d\log(n/d)/n}\big)$. Convert expectation to high probability with Markov (or McDiarmid for the sharp form). The $\log$ factor is removed by chaining.

**17. True or false: "VC dimension equals the number of free parameters."**
False in both directions. $\{x\mapsto\operatorname{sign}(\sin\omega x)\}$ has one parameter and infinite VC dimension (for $x_i=2^{-i}$ any labeling is realised by a suitable $\omega$). Conversely, halfspaces in $\mathbb R^d$ have $d+1$ parameters and VC dimension $d+1$ (here they agree), but a class such as $\{x\mapsto\operatorname{sign}(\langle w,x\rangle):\|w\|\le B\}$ restricted to $\|x\|\le R$ has *margin-based* capacity $B^2R^2/\rho^2$ independent of $d$.

## Rademacher complexity (note 05)

**18. Define empirical and expected Rademacher complexity and prove the symmetrisation lemma $\mathbb E_S\sup_f(\mathbb Ef-\hat{\mathbb E}_Sf)\le2\mathfrak R_n(\mathcal F)$.**
$\mathfrak R_S(\mathcal F)=\mathbb E_\sigma\sup_{f\in\mathcal F}\frac1n\sum_i\sigma_if(z_i)$, $\sigma_i$ i.i.d. uniform $\pm1$; $\mathfrak R_n=\mathbb E_S\mathfrak R_S$. Proof: with a ghost sample $S'$, $\mathbb Ef=\mathbb E_{S'}\hat{\mathbb E}_{S'}f$, so by Jensen $\mathbb E_S\sup_f(\mathbb Ef-\hat{\mathbb E}_Sf)\le\mathbb E_{S,S'}\sup_f\frac1n\sum_i(f(z_i')-f(z_i))$. Swapping $z_i\leftrightarrow z_i'$ for any subset of indices leaves the joint law invariant, so one may insert $\sigma_i$: $=\mathbb E_{S,S',\sigma}\sup_f\frac1n\sum_i\sigma_i(f(z_i')-f(z_i))\le\mathbb E\sup_f\frac1n\sum\sigma_if(z_i')+\mathbb E\sup_f\frac1n\sum(-\sigma_i)f(z_i)=2\mathfrak R_n(\mathcal F)$.

**19. State the Rademacher generalisation bound and explain how McDiarmid enters.**
For $\mathcal F\subseteq[0,1]^{\mathcal Z}$, w.p. $\ge1-\delta$, $\forall f$: $\mathbb Ef\le\hat{\mathbb E}_Sf+2\mathfrak R_n(\mathcal F)+\sqrt{\log(1/\delta)/(2n)}$, and with $\mathfrak R_S$ in place of $\mathfrak R_n$ at the cost of $3\sqrt{\log(2/\delta)/(2n)}$. $\Phi(S)=\sup_f(\mathbb Ef-\hat{\mathbb E}_Sf)$ changes by at most $1/n$ when one $z_i$ is replaced, so McDiarmid gives $\Phi(S)\le\mathbb E\Phi+\sqrt{\log(1/\delta)/(2n)}$ w.p. $1-\delta$; the symmetrisation lemma bounds $\mathbb E\Phi$; a second McDiarmid on $\mathfrak R_S$ (also $1/n$-bounded differences) replaces $\mathfrak R_n$ by $\mathfrak R_S$.

**20. Prove $\mathfrak R_S(\{x\mapsto\langle w,x\rangle:\|w\|\le B\})\le BR/\sqrt n$ for $\|x_i\|\le R$.**
$\sup_{\|w\|\le B}\frac1n\sum_i\sigma_i\langle w,x_i\rangle=\frac Bn\|\sum_i\sigma_ix_i\|$ (Cauchy–Schwarz, attained at $w\parallel\sum\sigma_ix_i$). Jensen: $\mathbb E_\sigma\|\sum\sigma_ix_i\|\le\sqrt{\mathbb E\|\sum\sigma_ix_i\|^2}=\sqrt{\sum_{i,j}\mathbb E[\sigma_i\sigma_j]\langle x_i,x_j\rangle}=\sqrt{\sum_i\|x_i\|^2}\le R\sqrt n$. Hence $\mathfrak R_S\le BR/\sqrt n$, independent of the dimension.

**21. Prove Massart's lemma and use it with Sauer to bound $\mathfrak R_n$ of a VC class.**
For finite $A\subset\mathbb R^n$ with $\|a\|\le r$: $\mathbb E\max_{a\in A}\langle\sigma,a\rangle\le r\sqrt{2\log|A|}$. Proof: for $\lambda>0$, $e^{\lambda\mathbb E\max}\le\mathbb Ee^{\lambda\max}\le\sum_a\prod_i\mathbb Ee^{\lambda\sigma_ia_i}\le|A|e^{\lambda^2r^2/2}$ (Hoeffding's lemma per coordinate); take logs and $\lambda=\sqrt{2\log|A|}/r$. For a VC class restricted to $S$: $|A|=|\mathcal H_S|\le(en/d)^d$, $r=\sqrt n$, so $\mathfrak R_S(\mathcal H)\le\sqrt{2d\log(en/d)/n}$.

## Regularisation, SRM, stability (note 06)

**22. State and prove the SRM bound for a countable family $\mathcal H_1\subseteq\mathcal H_2\subseteq\cdots$.**
Let $\varepsilon_k(n,\delta)$ be the uniform-convergence rate of $\mathcal H_k$ and $w_k\ge0$ with $\sum_kw_k\le1$. Then w.p. $\ge1-\delta$, simultaneously for all $k$ and all $h\in\mathcal H_k$: $|L_{\mathcal D}(h)-L_S(h)|\le\varepsilon_k(n,w_k\delta)$. Proof: apply uniform convergence to $\mathcal H_k$ with confidence $w_k\delta$ and union-bound: total failure probability $\le\sum_kw_k\delta\le\delta$. SRM outputs $\arg\min_{k,h\in\mathcal H_k}L_S(h)+\varepsilon_k(n,w_k\delta)$ and hence satisfies $L_{\mathcal D}(h_{SRM})\le\min_k\big(\min_{h\in\mathcal H_k}L_{\mathcal D}(h)+2\varepsilon_k(n,w_k\delta)\big)$.

**23. Define on-average replace-one stability and prove that it controls the expected generalisation gap.**
$A$ is $\beta(n)$-stable if $\mathbb E_{S,z',i}[\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)]\le\beta(n)$ where $S^{(i)}$ replaces $z_i$ by an independent $z'$. Identity: $\mathbb E_S[L_{\mathcal D}(A(S))-L_S(A(S))]=\mathbb E_{S,z'}\ell(A(S),z')-\mathbb E_{S,i}\ell(A(S),z_i)$. In the first term rename: $(S,z')\mapsto(S^{(i)},z_i)$ has the same joint law, so it equals $\mathbb E\ell(A(S^{(i)}),z_i)$. Hence the gap equals $\mathbb E[\ell(A(S^{(i)}),z_i)-\ell(A(S),z_i)]\le\beta(n)$.

**24. Show that RLM with a convex $\rho$-Lipschitz loss and regulariser $\lambda\|w\|^2$ is $\frac{2\rho^2}{\lambda n}$-stable, and derive the resulting oracle inequality.**
$F_S(w)=L_S(w)+\lambda\|w\|^2$ is $2\lambda$-strongly convex, so for its minimiser $u=A(S)$ and any $v$: $F_S(v)-F_S(u)\ge\lambda\|v-u\|^2$. Take $v=A(S^{(i)})$ and note $F_S(v)-F_S(u)=F_{S^{(i)}}(v)-F_{S^{(i)}}(u)+\frac1n[\ell(v,z_i)-\ell(u,z_i)]+\frac1n[\ell(u,z')-\ell(v,z')]\le\frac{2\rho}{n}\|v-u\|$ (first difference $\le0$, Lipschitz for the rest). So $\|v-u\|\le\frac{2\rho}{\lambda n}$ and $\ell(v,z_i)-\ell(u,z_i)\le\rho\|v-u\|\le\frac{2\rho^2}{\lambda n}$. Then $\mathbb EL_{\mathcal D}(A(S))\le\mathbb EL_S(A(S))+\frac{2\rho^2}{\lambda n}\le\mathbb E F_S(w^*)+\frac{2\rho^2}{\lambda n}=L_{\mathcal D}(w^*)+\lambda\|w^*\|^2+\frac{2\rho^2}{\lambda n}$ for any $w^*$; with $\|w^*\|\le B$ and $\lambda=\sqrt{2\rho^2/(B^2n)}$ the excess is $\le\rho B\sqrt{8/n}$.

**25. You select among $k$ models on a validation set of size $n_v$. What guarantee do you have, and why is cross-validation different?**
Union bound + Hoeffding: w.p. $\ge1-\delta$, for all $k$ candidates $|L_{\mathcal D}(h_j)-L_V(h_j)|\le\sqrt{\log(2k/\delta)/(2n_v)}$, so the selected model is within $2\sqrt{\log(2k/\delta)/(2n_v)}$ of the best candidate. Valid because the candidates are fixed before seeing $V$. $k$-fold cross-validation reuses data: the folds' estimates are dependent and the models retrained on all data differ from the evaluated ones; it estimates the expected risk of the *algorithm* at sample size $n(1-1/k)$ (slightly pessimistic) and has no comparably clean finite-sample guarantee.

## Least squares (note 07)

**26. Derive the OLS solution and show the hat matrix is an orthogonal projector.**
$\min_w\|Xw-y\|^2$: gradient $2X^\top(Xw-y)=0$ ⇒ $X^\top Xw=X^\top y$ ⇒ $\hat w=(X^\top X)^{-1}X^\top y$ (full column rank; otherwise $X^+y$, the min-norm solution). $H=X(X^\top X)^{-1}X^\top$: $H^\top=H$ and $H^2=X(X^\top X)^{-1}X^\top X(X^\top X)^{-1}X^\top=H$; $HX=X$ so $H$ fixes $\mathrm{col}(X)$ and $(I-H)$ kills it; residual $y-Hy\perp\mathrm{col}(X)$; $\mathrm{tr}H=\mathrm{rank}X=d$.

**27. Derive the bias–variance decomposition for a regression estimator $\hat f_S$ at a point $x$.**
Model $y=f(x)+\epsilon$, $\mathbb E\epsilon=0$, $\mathrm{Var}\,\epsilon=\sigma^2$, $\epsilon$ independent of $S$. Write $\bar f(x)=\mathbb E_S\hat f_S(x)$. $\mathbb E_{S,\epsilon}(\hat f_S(x)-y)^2=\mathbb E(\hat f_S-\bar f+\bar f-f-\epsilon)^2=\mathbb E(\hat f_S-\bar f)^2+(\bar f-f)^2+\sigma^2$, the cross terms vanishing because $\mathbb E_S(\hat f_S-\bar f)=0$, $\mathbb E\epsilon=0$ and $\epsilon\perp S$. So risk $=\mathrm{Var}_S\hat f_S(x)+\mathrm{bias}^2+\sigma^2$: flexible models have low bias and high variance.

**28. Compute: fixed design $X\in\mathbb R^{n\times d}$ of rank $d$, $y=Xw^*+\epsilon$, $\epsilon\sim(0,\sigma^2I)$. What is $\mathbb E\|X\hat w-Xw^*\|^2$?**
$X\hat w-Xw^*=H\epsilon$, so $\mathbb E\|H\epsilon\|^2=\sigma^2\mathrm{tr}(H^\top H)=\sigma^2\mathrm{tr}H=\sigma^2d$. Per sample: $\sigma^2d/n$; the in-sample excess risk grows linearly in the dimension and vanishes at rate $1/n$ (a "fast rate", possible because the squared loss is strongly convex).

**29. Derive kernel ridge regression from ridge regression and state the cost trade-off.**
Ridge: $\hat w=(X^\top X+\lambda I)^{-1}X^\top y$. Identity: $(X^\top X+\lambda I)X^\top=X^\top(XX^\top+\lambda I)$, so $\hat w=X^\top(XX^\top+\lambda I)^{-1}y=X^\top\hat\alpha$ with $\hat\alpha=(K+\lambda I)^{-1}y$, $K=XX^\top$. Predictions $\hat f(x)=\langle x,\hat w\rangle=\sum_i\hat\alpha_i\langle x_i,x\rangle$, which only needs inner products: replace by $k(x_i,x)$. Cost $O(d^3)$ (primal) vs $O(n^3)$ (dual); the dual is the only option when the feature space is infinite-dimensional.

## Kernels and RKHS (note 08)

**30. Define a positive-definite kernel and prove that the Gaussian kernel is one.**
$k$ is PD if symmetric and $\sum_{i,j}c_ic_jk(x_i,x_j)\ge0$ for all finite $\{x_i\}$, $c\in\mathbb R^n$. Gaussian: $e^{-\gamma\|x-x'\|^2}=e^{-\gamma\|x\|^2}e^{2\gamma\langle x,x'\rangle}e^{-\gamma\|x'\|^2}$. The middle factor is $\sum_{m\ge0}\frac{(2\gamma)^m}{m!}\langle x,x'\rangle^m$: each power of a PD kernel is PD (Schur product theorem: the entrywise product of PSD matrices is PSD, since it is a principal submatrix of the Kronecker product), nonnegative combinations and limits of PD kernels are PD, and multiplying by $g(x)g(x')$ with $g(x)=e^{-\gamma\|x\|^2}$ preserves PD-ness ($\sum c_ic_jg_ig_jk_{ij}=\sum(c_ig_i)(c_jg_j)k_{ij}\ge0$).

**31. State the reproducing property and prove the representer theorem.**
In the RKHS $\mathcal H_k$, $\langle f,k(x,\cdot)\rangle_{\mathcal H_k}=f(x)$. Theorem: for $\min_{f\in\mathcal H_k}c\big((y_i,f(x_i))_{i\le n}\big)+\Omega(\|f\|)$ with $\Omega$ strictly increasing, every minimiser has the form $f=\sum_i\alpha_ik(x_i,\cdot)$. Proof: decompose $f=f_\parallel+f_\perp$ with $f_\parallel\in V=\mathrm{span}\{k(x_i,\cdot)\}$ and $f_\perp\perp V$. By reproducing, $f(x_j)=\langle f,k(x_j,\cdot)\rangle=\langle f_\parallel,k(x_j,\cdot)\rangle=f_\parallel(x_j)$, so the data term does not see $f_\perp$, while $\|f\|^2=\|f_\parallel\|^2+\|f_\perp\|^2$; since $\Omega$ is strictly increasing, $f_\perp\ne0$ would strictly increase the objective. Hence $f_\perp=0$.

**32. Explain the construction of the RKHS from a PD kernel (Moore–Aronszajn) in four steps.**
(1) Pre-Hilbert space $\mathcal H_0=\{\sum_i\alpha_ik(x_i,\cdot)\}$; (2) inner product $\langle\sum\alpha_ik(x_i,\cdot),\sum\beta_jk(x_j,\cdot)\rangle=\sum\alpha_i\beta_jk(x_i,x_j)$, well defined because it equals $\sum_j\beta_jf(x_j)=\sum_i\alpha_ig(x_i)$, independent of the representation; symmetric, bilinear, and $\langle f,f\rangle\ge0$ by PD-ness; (3) $\langle f,f\rangle=0\Rightarrow f=0$ via Cauchy–Schwarz on the kernel: $|f(x)|^2=|\langle f,k(x,\cdot)\rangle|^2\le\langle f,f\rangle k(x,x)$; (4) complete; evaluation is bounded by the same inequality, and the reproducing property holds by construction. Uniqueness of the RKHS with reproducing kernel $k$ follows because $\mathrm{span}\{k(x,\cdot)\}$ is dense in any such space.

**33. True or false: "$k(x,x')=\tanh(a\langle x,x'\rangle+c)$ is a valid kernel." What goes wrong if a non-PD kernel is used in an SVM or KRR?**
False: the Gram matrix can have negative eigenvalues for some data (checkable numerically). Then the dual SVM objective is non-concave (no unique optimum, solvers may diverge), $K+\lambda I$ may be singular or indefinite, and there is no RKHS so the representer theorem and the Rademacher bound for norm balls do not apply.

## SVM (note 09)

**34. Derive the dual of the hard-margin SVM and read off the support vectors.**
Primal $\min\frac12\|w\|^2$ s.t. $y_i(\langle w,x_i\rangle+b)\ge1$. Lagrangian $\frac12\|w\|^2-\sum\alpha_i[y_i(\langle w,x_i\rangle+b)-1]$, $\alpha\ge0$. Stationarity: $w=\sum\alpha_iy_ix_i$, $\sum\alpha_iy_i=0$. Substituting: dual $\max_{\alpha\ge0,\sum\alpha_iy_i=0}\sum\alpha_i-\frac12\sum_{ij}\alpha_i\alpha_jy_iy_j\langle x_i,x_j\rangle$. Slater ⇒ strong duality and KKT; complementary slackness $\alpha_i[y_i(\langle w,x_i\rangle+b)-1]=0$ ⇒ $\alpha_i>0$ only for points on the margin (support vectors). $b=y_s-\langle w,x_s\rangle$ for any support vector $s$; margin $=1/\|w\|=(\sum_i\alpha_i)^{-1/2}$.

**35. State the margin bound for norm-bounded linear classifiers and explain each term. Why does it justify the kernel trick?**
$L^{0\text{-}1}_{\mathcal D}(h)\le\hat L_{S,\rho}(h)+\frac2\rho\frac{BR}{\sqrt n}+3\sqrt{\frac{\log(2/\delta)}{2n}}$ for $\|w\|\le B$, $\|x\|\le R$, w.p. $\ge1-\delta$. First term: empirical $\rho$-margin loss (upper-bounded by the fraction of points with margin $\le\rho$). Second: $2\times$ Rademacher complexity of the linear class ($BR/\sqrt n$) after Talagrand contraction by the $1/\rho$-Lipschitz margin loss. Third: McDiarmid. No dependence on $d$: in an RKHS, $R^2=\sup_xk(x,x)$ and $B=\|f\|_{\mathcal H_k}$, so the bound is unchanged.

**36. Show that the soft-margin SVM is regularised hinge-loss minimisation and describe the three KKT regimes of $\alpha_i$.**
For fixed $(w,b)$ the optimal slack is $\xi_i=\max\{0,1-y_if(x_i)\}$, so the primal is $\frac12\|w\|^2+C\sum_i\ell_{\text{hinge}}$; dividing by $Cn$ gives $\lambda\|w\|^2+\frac1n\sum\ell_{\text{hinge}}$ with $\lambda=1/(2Cn)$. Dual box constraint $0\le\alpha_i\le C$ from $\partial_{\xi_i}$: $C=\alpha_i+\mu_i$. Regimes: $\alpha_i=0$ ⇒ $y_if(x_i)\ge1$ (outside margin); $0<\alpha_i<C$ ⇒ $\xi_i=0$ and $y_if(x_i)=1$ (on margin, used for $b$); $\alpha_i=C$ ⇒ $y_if(x_i)\le1$ (margin violator or misclassified).

**37. Prove the perceptron mistake bound $(R/\gamma)^2$.**
Separable with $\|w^*\|=1$, $y_i\langle w^*,x_i\rangle\ge\gamma$, $\|x_i\|\le R$; update $w\leftarrow w+y_ix_i$ on mistakes from $w=0$. After $k$ mistakes: $\langle w_k,w^*\rangle\ge k\gamma$ (each update adds $\ge\gamma$) and $\|w_k\|^2\le kR^2$ (each update adds $2y_i\langle w,x_i\rangle+\|x_i\|^2\le R^2$ since the middle term is $\le0$ at a mistake). Cauchy–Schwarz: $k\gamma\le\|w_k\|\le\sqrt kR$ ⇒ $k\le(R/\gamma)^2$.

## Deep learning theory (note 10)

**38. State the universal approximation theorem and explain why it does not resolve the question of generalisation.**
For compact $K\subset\mathbb R^d$ and continuous non-polynomial $\sigma$, one-hidden-layer networks $\sum_jv_j\sigma(\langle w_j,x\rangle+b_j)$ are dense in $C(K)$ (Cybenko/Hornik/Leshno et al.). It is an approximation statement: existence of weights, possibly exponentially many in $d$, with no algorithm and no sample complexity. Generalisation requires controlling estimation error, and the class of all such networks has unbounded capacity; note also that the VC dimension $\Theta(WL\log W)$ exceeds $n$ for practical nets, so classical bounds are vacuous.

**39. Prove that gradient descent from $w_0=0$ on $\frac12\|\Phi w-y\|^2$ with $\Phi\in\mathbb R^{n\times p}$, $p>n$, full row rank, converges to the minimum-norm interpolator, and say why this is called implicit regularisation.**
Each step adds a multiple of $\Phi^\top r_t\in\mathrm{row}(\Phi)$, so $w_t\in\mathrm{row}(\Phi)$ for all $t$. On $\mathrm{row}(\Phi)$ the objective is strongly convex ($\Phi^\top\Phi$ restricted there has eigenvalues $\ge\sigma_{\min}^2>0$), so with step $\eta<2/\sigma_{\max}^2$ GD converges to the unique interpolator in $\mathrm{row}(\Phi)$. For any interpolator $w=w_\parallel+w_\perp$ ($w_\perp\in\ker\Phi$), $\|w\|^2=\|w_\parallel\|^2+\|w_\perp\|^2$, and $w_\parallel$ is itself an interpolator in $\mathrm{row}(\Phi)$, hence the unique one; so the limit is $\Phi^+y=\arg\min\{\|w\|:\Phi w=y\}$. No penalty was added: the algorithm's choice among the infinitely many minimisers is the regularisation.

**40. Explain double descent: what is plotted, where is the peak, and why does the risk fall again? What removes the peak?**
Test risk vs model size at fixed $n$. For $p<n$: classical U (bias down, variance $\sim\sigma^2p/n$ up). At $p\approx n$ the min-norm least-squares interpolator has variance $\sigma^2\sum_j s_j^{-2}$ over singular values of the design, and $s_{\min}\to0$ (Marchenko–Pastur), so the risk peaks (isotropic asymptotics: $\sigma^2\gamma/(1-\gamma)$ for $\gamma=p/n<1$ and $r^2(1-1/\gamma)+\sigma^2/(\gamma-1)$ for $\gamma>1$). For $p>n$ the min-norm interpolator's norm decreases with $p$ and the variance falls again, while the bias rises towards $r^2$. **In the well-specified isotropic model the second descent never beats the classical minimum**: the risk $\sigma^2\gamma/(1-\gamma)\to0$ as $\gamma\to0$, so the global minimum is always underparameterised [S36]; the SNR only decides whether the right branch is monotone ($\mathrm{SNR}\le1$) or has an interior local minimum ($\mathrm{SNR}>1$). The global optimum moves past the threshold only under model misspecification. Optimally tuned ridge regularisation, or early stopping, removes the peak. In deep nets the phenomenon is empirical (model-wise and epoch-wise); it is proven for linear and random-features models.

## Before the exam

Twelve results to be able to prove on a whiteboard in under five minutes each:

1. Bayes optimality of $\operatorname{sign}(\eta(x)-1/2)$ and optimism $\mathbb EL_S(h_S)\le\min_hL_{\mathcal D}(h)$ (Q1, Q2).
2. Hoeffding's inequality via Chernoff and Hoeffding's lemma (Q4).
3. Finite classes: agnostic $\log(2|\mathcal H|/\delta)/(2\varepsilon^2)$ and realisable $\log(|\mathcal H|/\delta)/\varepsilon$ (Q5, Q6).
4. No-Free-Lunch, at least the averaging argument (Q9).
5. $\mathrm{VCdim}$ of thresholds, intervals, rectangles, halfspaces (Q13 and note 04).
6. Sauer–Shelah with the $Y_0/Y_1$ induction (Q14).
7. Symmetrisation and the Rademacher generalisation bound with McDiarmid (Q18, Q19).
8. $\mathfrak R_S\le BR/\sqrt n$ for the linear class and Massart's lemma (Q20, Q21).
9. Stability ⇒ generalisation identity and $2\rho^2/(\lambda n)$-stability of RLM (Q23, Q24).
10. Bias–variance decomposition and $\sigma^2d$ in-sample excess risk (Q27, Q28).
11. Representer theorem and PD-ness of the Gaussian kernel (Q30, Q31).
12. SVM dual with KKT, the margin bound chain, GD ⇒ min-norm interpolator (Q34, Q35, Q39).

## References

- Shalev-Shwartz & Ben-David, *Understanding Machine Learning* (2014): Ch. 2–7 (framework, PAC, VC, NFL, nonuniform learnability), 9 (linear predictors), 11 (model selection), 12–13 (convex learning, RLM, stability), 15–16 (SVM, kernels), 20 (neural networks), 26 (Rademacher), 28 (proof of the fundamental theorem).
- Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning* (2nd ed. 2018): Ch. 2–3 (PAC, Rademacher, VC), 5–6 (SVM, kernels), 11 (regression), Appendix D (concentration).
- Schölkopf & Smola, *Learning with Kernels* (2002): Ch. 2, 4, 7.
- Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning* (2009): Ch. 3, 7.
