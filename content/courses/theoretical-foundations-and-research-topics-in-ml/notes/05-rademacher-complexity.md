# 05 Rademacher complexity

Rademacher complexity is the modern, data-dependent replacement for the growth function and VC dimension.
Instead of counting how many labelings a class can realise, it measures how well the class can correlate with pure noise on the actual sample $S$.
Its two big advantages over VC theory: it applies to real-valued function classes (losses, margins, regressors) and it yields dimension-free bounds for linear and kernel methods.
In the course it sits between VC theory (note 04) and the regularisation / kernel / SVM notes (06–09), whose generalisation bounds all rest on it.

## Definitions

Throughout, $\mathcal F$ is a class of functions $f:\mathcal Z\to\mathbb R$, $S=(z_1,\dots,z_n)$ is an i.i.d. sample from $\mathcal D$, $\mathbb E f := \mathbb E_{z\sim\mathcal D} f(z)$ and $\hat{\mathbb E}_S f := \frac1n\sum_{i=1}^n f(z_i)$.
A *Rademacher variable* $\sigma$ takes values $\pm1$ with probability $\tfrac12$ each; $\sigma=(\sigma_1,\dots,\sigma_n)$ is a vector of independent Rademacher variables.

1. **Empirical Rademacher complexity** of $\mathcal F$ on $S$:
$$\mathfrak R_S(\mathcal F)=\mathbb E_\sigma\Big[\sup_{f\in\mathcal F}\frac1n\sum_{i=1}^n\sigma_i f(z_i)\Big].$$
   Writing $f|_S=(f(z_1),\dots,f(z_n))\in\mathbb R^n$, this is $\frac1n\mathbb E_\sigma\sup_{f}\langle\sigma,f|_S\rangle$: the expected maximal correlation of the class with a random sign vector.

2. **Expected (average) Rademacher complexity**: $\mathfrak R_n(\mathcal F)=\mathbb E_{S\sim\mathcal D^n}\,\mathfrak R_S(\mathcal F)$.

3. **Loss class.** For a hypothesis class $\mathcal H$ and loss $\ell$, the loss class is $\ell\circ\mathcal H=\{(x,y)\mapsto\ell(h(x),y):h\in\mathcal H\}$.
   Generalisation bounds are stated for $\mathcal F=\ell\circ\mathcal H$; then $\mathbb E f=L_{\mathcal D}(h)$ and $\hat{\mathbb E}_Sf=L_S(h)$.

4. **Representativeness** of $S$ for $\mathcal F$: $\mathrm{Rep}_{\mathcal D}(\mathcal F,S)=\sup_{f\in\mathcal F}(\mathbb E f-\hat{\mathbb E}_S f)$, the worst-case one-sided generalisation gap.

5. **Bounded differences.** $g:\mathcal Z^n\to\mathbb R$ has the bounded-differences property with constants $c_1,\dots,c_n$ if for every $i$ and every $z_1,\dots,z_n,z_i'$: $|g(z_1,\dots,z_i,\dots,z_n)-g(z_1,\dots,z_i',\dots,z_n)|\le c_i$.

6. **$\varepsilon$-cover and covering number.** Equip $\mathcal F$ with the empirical $L_2(S)$ pseudo-metric $d_S(f,g)=\big(\frac1n\sum_i(f(z_i)-g(z_i))^2\big)^{1/2}$.
   A set $C\subset\mathbb R^n$ is an $\varepsilon$-cover of $\mathcal F$ if every $f|_S$ is within $d_S$-distance $\varepsilon$ of some element of $C$.
   $\mathcal N(\varepsilon,\mathcal F,L_2(S))$ is the smallest cardinality of an $\varepsilon$-cover; $\log\mathcal N$ is the *metric entropy*.

7. **Interpretation.** $\mathfrak R_S(\mathcal F)$ is small if no $f\in\mathcal F$ can fit random labels on $S$.
   For $\mathcal F\subset\{\pm1\}^{\mathcal X}$ (binary classifiers), $\frac1n\sum_i\sigma_i h(x_i)=1-2\,\hat{\mathbb E}_S\ell_{0\text{-}1}(h,\sigma)$, so $\mathfrak R_S(\mathcal H)=1-2\,\mathbb E_\sigma\min_h L_S(h;\sigma)$: one minus twice the best achievable training error on random labels.
   If $\mathcal H$ shatters $S$, $\mathfrak R_S(\mathcal H)=1$.

## Results

**Theorem 5.1 (symmetrisation)** [S9 Lemma 26.2; S19]**.** For any class $\mathcal F$ and $n$,
$$\mathbb E_S\Big[\sup_{f\in\mathcal F}\big(\mathbb E f-\hat{\mathbb E}_Sf\big)\Big]\le 2\,\mathfrak R_n(\mathcal F).$$

*Proof.* Let $S'=(z'_1,\dots,z'_n)$ be an independent *ghost sample* from $\mathcal D^n$.
Since $\mathbb E f=\mathbb E_{S'}\hat{\mathbb E}_{S'}f$ for every fixed $f$,
$$\mathbb E_S\sup_f\big(\mathbb E f-\hat{\mathbb E}_Sf\big)=\mathbb E_S\sup_f\mathbb E_{S'}\big(\hat{\mathbb E}_{S'}f-\hat{\mathbb E}_Sf\big)\le\mathbb E_{S,S'}\sup_f\big(\hat{\mathbb E}_{S'}f-\hat{\mathbb E}_Sf\big),$$
by Jensen (the supremum is convex, so $\sup\mathbb E\le\mathbb E\sup$).
Now $\hat{\mathbb E}_{S'}f-\hat{\mathbb E}_Sf=\frac1n\sum_i(f(z'_i)-f(z_i))$.
For each fixed $i$, swapping $z_i\leftrightarrow z'_i$ does not change the joint law of $(S,S')$, and it flips the sign of the $i$-th summand.
Hence for any fixed sign vector $\sigma\in\{\pm1\}^n$,
$$\mathbb E_{S,S'}\sup_f\frac1n\sum_i(f(z'_i)-f(z_i))=\mathbb E_{S,S'}\sup_f\frac1n\sum_i\sigma_i(f(z'_i)-f(z_i)).$$
Averaging over uniformly random $\sigma$ (sign symmetry):
$$=\mathbb E_{\sigma,S,S'}\sup_f\frac1n\sum_i\sigma_i(f(z'_i)-f(z_i))\le\mathbb E_{\sigma,S'}\sup_f\frac1n\sum_i\sigma_if(z'_i)+\mathbb E_{\sigma,S}\sup_f\frac1n\sum_i(-\sigma_i)f(z_i),$$
using $\sup(a+b)\le\sup a+\sup b$. Both terms equal $\mathfrak R_n(\mathcal F)$ because $-\sigma$ has the same law as $\sigma$. ∎

**Theorem 5.2 (McDiarmid's bounded-differences inequality)** [S14; S9 Lemma 26.4; S10 Thm D.8]**.** Let $Z_1,\dots,Z_n$ be independent and $g$ satisfy the bounded-differences property with constants $c_i$.
Then for all $t>0$,
$$\Pr\big[g(Z_1,\dots,Z_n)-\mathbb E g\ge t\big]\le\exp\Big(-\frac{2t^2}{\sum_ic_i^2}\Big),$$
and the same bound holds for $\Pr[\mathbb E g-g\ge t]$.

*Proof sketch.* Write $g-\mathbb E g$ as the telescoping martingale-difference sum $\sum_i V_i$ with $V_i=\mathbb E[g\mid Z_1..Z_i]-\mathbb E[g\mid Z_1..Z_{i-1}]$.
Bounded differences give $V_i\in[A_i,A_i+c_i]$ for some $A_i$ measurable w.r.t. $Z_1..Z_{i-1}$.
Hoeffding's lemma applied conditionally gives $\mathbb E[e^{sV_i}\mid Z_{<i}]\le e^{s^2c_i^2/8}$; iterate the tower property, apply Markov to $e^{s(g-\mathbb Eg)}$ and optimise $s=4t/\sum c_i^2$.
(Hoeffding's inequality is the special case $g=\frac1n\sum Z_i$.) ∎

**Theorem 5.3 (Rademacher generalisation bound)** [S19; constants as in S10 Thm 3.3 — S9 Thm 26.5 states the same result with different constants]**.** Let $\mathcal F$ be a class of functions $\mathcal Z\to[0,1]$.
For any $\delta\in(0,1)$, with probability at least $1-\delta$ over $S\sim\mathcal D^n$, simultaneously for all $f\in\mathcal F$:
$$\mathbb E f\le\hat{\mathbb E}_Sf+2\mathfrak R_n(\mathcal F)+\sqrt{\frac{\log(1/\delta)}{2n}}\qquad\text{and}\qquad\mathbb E f\le\hat{\mathbb E}_Sf+2\mathfrak R_S(\mathcal F)+3\sqrt{\frac{\log(2/\delta)}{2n}}.$$

*Proof.* Let $g(S)=\sup_{f}(\mathbb E f-\hat{\mathbb E}_Sf)=\mathrm{Rep}_{\mathcal D}(\mathcal F,S)$.

*Bounded-differences check for $g$.* Let $S^{(i)}$ differ from $S$ only in the $i$-th point, $z_i\to z_i'$.
For every $f$, $\hat{\mathbb E}_{S}f-\hat{\mathbb E}_{S^{(i)}}f=\frac1n(f(z_i)-f(z_i'))\in[-\frac1n,\frac1n]$ since $f\in[0,1]$.
Hence
$$g(S^{(i)})-g(S)=\sup_f(\mathbb Ef-\hat{\mathbb E}_{S^{(i)}}f)-\sup_f(\mathbb Ef-\hat{\mathbb E}_{S}f)\le\sup_f\big[(\mathbb Ef-\hat{\mathbb E}_{S^{(i)}}f)-(\mathbb Ef-\hat{\mathbb E}_{S}f)\big]=\sup_f\tfrac1n(f(z_i)-f(z_i'))\le\tfrac1n,$$
using $\sup a-\sup b\le\sup(a-b)$; by symmetry $|g(S^{(i)})-g(S)|\le\frac1n$. So $c_i=1/n$, $\sum c_i^2=1/n$.

*First bound.* McDiarmid with $t=\sqrt{\log(1/\delta)/(2n)}$: with probability $\ge1-\delta$, $g(S)\le\mathbb E g+\sqrt{\log(1/\delta)/(2n)}$.
By Theorem 5.1, $\mathbb E g\le2\mathfrak R_n(\mathcal F)$. Since $g(S)\ge\mathbb Ef-\hat{\mathbb E}_Sf$ for every $f$, the first inequality follows for all $f$ simultaneously.

*Second bound.* The map $S\mapsto\mathfrak R_S(\mathcal F)$ also has bounded differences with constant $\frac1n$ (same computation inside the expectation over $\sigma$: changing $z_i$ changes $\frac1n\sigma_if(z_i)$ by at most $\frac1n$ for every $f,\sigma$).
McDiarmid (lower tail) with confidence $\delta/2$: $\mathfrak R_n(\mathcal F)\le\mathfrak R_S(\mathcal F)+\sqrt{\log(2/\delta)/(2n)}$ with probability $\ge1-\delta/2$.
Apply the first bound with $\delta/2$ and a union bound over the two events: with probability $\ge1-\delta$,
$$\mathbb E f\le\hat{\mathbb E}_Sf+2\mathfrak R_S(\mathcal F)+2\sqrt{\tfrac{\log(2/\delta)}{2n}}+\sqrt{\tfrac{\log(2/\delta)}{2n}}.$$
∎

*Remark.* For a hypothesis class $\mathcal H$ and the $0$-$1$ loss, apply the theorem to $\mathcal F=\ell_{0\text{-}1}\circ\mathcal H$: $L_{\mathcal D}(h)\le L_S(h)+2\mathfrak R_n(\ell\circ\mathcal H)+\sqrt{\log(1/\delta)/(2n)}$.
Since $\ell_{0\text{-}1}(h(x),y)=\frac{1-yh(x)}2$ for $\pm1$ labels, $\mathfrak R_S(\ell_{0\text{-}1}\circ\mathcal H)=\frac12\mathfrak R_S(\mathcal H)$ (the constant $\frac12$ contributes nothing after taking $\mathbb E_\sigma$ because $\mathbb E\sigma_i=0$, and $y_i\sigma_i$ has the law of $\sigma_i$).

**Theorem 5.4 (structural properties)** [S19; S9 Lemma 26.6, Lemma 26.7]**.** For classes $\mathcal F,\mathcal G$ of functions on $\mathcal Z$ and any sample $S$:

(a) *Monotonicity:* $\mathcal F\subset\mathcal G\Rightarrow\mathfrak R_S(\mathcal F)\le\mathfrak R_S(\mathcal G)$.

(b) *Scaling and translation:* $\mathfrak R_S(c\mathcal F)=|c|\,\mathfrak R_S(\mathcal F)$ and $\mathfrak R_S(\mathcal F+g)=\mathfrak R_S(\mathcal F)$ for a fixed $g$.

(c) *Sums:* $\mathfrak R_S(\mathcal F+\mathcal G)\le\mathfrak R_S(\mathcal F)+\mathfrak R_S(\mathcal G)$.

(d) *Convex hull invariance:* $\mathfrak R_S(\mathrm{conv}\,\mathcal F)=\mathfrak R_S(\mathcal F)$.

(e) *Absolute convex hull:* $\mathfrak R_S(\mathrm{absconv}\,\mathcal F)=\mathfrak R_S(\mathcal F\cup-\mathcal F)\le2\mathfrak R_S(\mathcal F)+$ (zero if $0\in\mathrm{conv}\mathcal F$); precisely $\mathfrak R_S(\mathcal F\cup-\mathcal F)\le \mathfrak R_S(\mathcal F)+\mathfrak R_S(-\mathcal F)$ when both are non-negative.

*Proof.* (a) A supremum over a larger set is larger. (b) $\sup_f\sum\sigma_i cf(z_i)=c\sup_f\sum\sigma_if(z_i)$ for $c>0$; for $c<0$ use that $-\sigma\overset d=\sigma$.
Translation: $\mathbb E_\sigma\frac1n\sum\sigma_ig(z_i)=0$. (c) $\sup(a+b)\le\sup a+\sup b$.
(d) "$\ge$" is monotonicity. "$\le$": a linear functional $\langle\sigma,\cdot\rangle$ on a convex hull of a set attains its supremum on the set: $\sup_{\alpha\in\Delta}\sum_j\alpha_j\langle\sigma,f_j|_S\rangle=\max_j\langle\sigma,f_j|_S\rangle$ for each $\sigma$.
(e) Apply (c)-style reasoning to $\mathcal F\cup-\mathcal F$ and use $-\sigma\overset d=\sigma$ for the $-\mathcal F$ part. ∎

**Theorem 5.5 (Talagrand's contraction lemma)** [S28 Thm 4.12; S10 Lemma 5.7; S9 Lemma 26.9]**.** Let $\phi_i:\mathbb R\to\mathbb R$ be $L$-Lipschitz for each $i$ (typically all equal to one $\phi$).
Then
$$\mathbb E_\sigma\sup_{f\in\mathcal F}\frac1n\sum_i\sigma_i\phi_i(f(z_i))\le L\,\mathbb E_\sigma\sup_{f\in\mathcal F}\frac1n\sum_i\sigma_if(z_i),$$
i.e. $\mathfrak R_S(\phi\circ\mathcal F)\le L\,\mathfrak R_S(\mathcal F)$.

*Proof sketch.* Peel off one coordinate at a time. Fix $\sigma_2,\dots,\sigma_n$ and write $u_n(f)=\sum_{i\ge2}\sigma_i\phi_i(f(z_i))$. Then
$$\mathbb E_{\sigma_1}\sup_f\big[u_n(f)+\sigma_1\phi_1(f(z_1))\big]=\tfrac12\sup_{f,f'}\big[u_n(f)+\phi_1(f(z_1))+u_n(f')-\phi_1(f'(z_1))\big].$$
By the Lipschitz property $\phi_1(f(z_1))-\phi_1(f'(z_1))\le L|f(z_1)-f'(z_1)|$; the pair $(f,f')$ attaining the sup can be ordered so the absolute value is $\pm L(f(z_1)-f'(z_1))$ with the right sign, giving $\le\frac12\sup_{f,f'}[u_n(f)+Lf(z_1)+u_n(f')-Lf'(z_1)]=\mathbb E_{\sigma_1}\sup_f[u_n(f)+\sigma_1Lf(z_1)]$.
Repeat for $i=2,\dots,n$. ∎

*Use.* To bound $\mathfrak R(\ell\circ\mathcal H)$ for a margin-type loss $\ell(h(x),y)=\phi(yh(x))$ with $\phi$ $L_\ell$-Lipschitz (hinge $\phi(u)=\max(0,1-u)$, $L=1$; logistic; truncated ramp $\phi(u)=\min(1,\max(0,1-u/\gamma))$, $L=1/\gamma$), apply Theorem 5.5 to $\mathcal F=\{(x,y)\mapsto yh(x)\}$ and then note $\mathfrak R_S(\{yh\})=\mathfrak R_S(\mathcal H)$ since $y_i\sigma_i\overset d=\sigma_i$.
Result: $\mathfrak R_S(\ell\circ\mathcal H)\le L_\ell\,\mathfrak R_S(\mathcal H)$.
This is how the hypothesis class enters every SVM/margin bound (note 09).

**Theorem 5.6 (Massart's finite-class lemma)** [S10 Thm 3.7; S9 Lemma 26.8 gives a sharper *centred* form, $\max_a\|a-\bar a\|$ in place of $\max_a\|a\|$]**.** Let $\mathcal F$ be finite and $r=\max_{f\in\mathcal F}\|f|_S\|_2=\max_f\big(\sum_if(z_i)^2\big)^{1/2}$. Then
$$\mathfrak R_S(\mathcal F)\le\frac{r\sqrt{2\log|\mathcal F|}}{n}.$$
In particular, if $|f|\le1$, then $r\le\sqrt n$ and $\mathfrak R_S(\mathcal F)\le\sqrt{2\log|\mathcal F|/n}$.

*Proof.* Let $A=\{f|_S:f\in\mathcal F\}\subset\mathbb R^n$, $|A|\le|\mathcal F|$.
For any $s>0$, by Jensen ($\exp$ convex) and then bounding the max of positive terms by their sum,
$$\exp\Big(s\,\mathbb E_\sigma\max_{a\in A}\langle\sigma,a\rangle\Big)\le\mathbb E_\sigma\exp\Big(s\max_{a}\langle\sigma,a\rangle\Big)=\mathbb E_\sigma\max_a e^{s\langle\sigma,a\rangle}\le\sum_{a\in A}\mathbb E_\sigma e^{s\langle\sigma,a\rangle}=\sum_{a\in A}\prod_{i=1}^n\mathbb E_{\sigma_i}e^{s\sigma_ia_i}.$$
Now $\mathbb E e^{s\sigma_ia_i}=\cosh(sa_i)\le e^{s^2a_i^2/2}$ (Hoeffding's lemma for a variable in $[-a_i,a_i]$ with mean $0$, or compare Taylor series termwise: $\frac{x^{2k}}{(2k)!}\le\frac{x^{2k}}{2^kk!}$).
Hence the right side is at most $\sum_ae^{s^2\|a\|^2/2}\le|A|e^{s^2r^2/2}$.
Taking logs and dividing by $s$:
$$\mathbb E_\sigma\max_a\langle\sigma,a\rangle\le\frac{\log|A|}{s}+\frac{sr^2}{2}.$$
Optimise: $s=\sqrt{2\log|A|}/r$ gives $r\sqrt{2\log|A|}$. Divide by $n$. ∎

**Theorem 5.7 (linear classes, $\ell_2$ constraint)** [S10 Thm 5.10; S9 Lemma 26.10]**.** Let $\mathcal F=\{x\mapsto\langle w,x\rangle:\|w\|_2\le B\}$ and $S=(x_1,\dots,x_n)$ with $\|x_i\|_2\le R$.
Then
$$\mathfrak R_S(\mathcal F)=\frac Bn\,\mathbb E_\sigma\Big\|\sum_{i=1}^n\sigma_ix_i\Big\|_2\le\frac{B}{n}\sqrt{\sum_i\|x_i\|_2^2}\le\frac{BR}{\sqrt n}.$$

*Proof.* For fixed $\sigma$, put $v=\sum_i\sigma_ix_i$. Then $\sup_{\|w\|\le B}\frac1n\sum_i\sigma_i\langle w,x_i\rangle=\frac1n\sup_{\|w\|\le B}\langle w,v\rangle=\frac Bn\|v\|_2$: Cauchy–Schwarz gives $\le$, and $w=Bv/\|v\|$ attains it.
This proves the exact expression. Next, by Jensen ($\sqrt{\cdot}$ is concave),
$$\mathbb E_\sigma\|v\|_2\le\sqrt{\mathbb E_\sigma\|v\|_2^2}=\sqrt{\mathbb E_\sigma\sum_{i,j}\sigma_i\sigma_j\langle x_i,x_j\rangle}=\sqrt{\sum_i\|x_i\|_2^2},$$
because $\mathbb E\sigma_i\sigma_j=\delta_{ij}$ (independence, mean zero, $\sigma_i^2=1$). Finally $\sum_i\|x_i\|^2\le nR^2$. ∎

*Dimension independence.* Neither $d$ nor any property of the data beyond the norms enters.
Replacing $x$ by a feature map $\phi(x)$ into an infinite-dimensional RKHS with $k(x,x)\le R^2$, the bound reads $\mathfrak R_S\le\frac Bn\sqrt{\sum_ik(x_i,x_i)}=\frac Bn\sqrt{\mathrm{tr}K}$, which is why kernel machines generalise at all (notes 08–09).
A VC argument for halfspaces in $\mathbb R^d$ would give $\sqrt{d/n}$ — useless for $d=\infty$.
The exact value $\frac Bn\mathbb E\|\sum\sigma_ix_i\|$ is what `rademacher_linear_exact` estimates by Monte Carlo over $\sigma$.

**Theorem 5.8 (linear classes, $\ell_1/\ell_\infty$ constraint)** [S10 Thm 11.15; S9 Lemma 26.11]**.** Let $\mathcal F=\{x\mapsto\langle w,x\rangle:\|w\|_1\le B_1\}$ and $\|x_i\|_\infty\le R_\infty$, $x_i\in\mathbb R^d$.
Then $\mathfrak R_S(\mathcal F)\le B_1R_\infty\sqrt{2\log(2d)/n}$.

*Proof sketch.* The $\ell_1$-ball is the convex hull of the $2d$ vertices $\pm B_1e_j$.
By Theorem 5.4(d), $\mathfrak R_S(\mathcal F)=\mathfrak R_S(\{x\mapsto\pm B_1x_j\})$, a class of $2d$ functions with $|f(x_i)|\le B_1R_\infty$, so $r\le B_1R_\infty\sqrt n$.
Massart (Theorem 5.6) gives $B_1R_\infty\sqrt{2\log(2d)/n}$. ∎ This is the bound behind $\ell_1$ regularisation/boosting: logarithmic in the dimension.

**Theorem 5.9 (Rademacher vs VC)** [S10 Cor. 3.8, Cor. 3.18]**.** Let $\mathcal H\subset\{\pm1\}^{\mathcal X}$ with $\mathrm{VCdim}(\mathcal H)=d$ and $n\ge d$. Then
$$\mathfrak R_S(\mathcal H)\le\sqrt{\frac{2\log\tau_{\mathcal H}(n)}{n}}\le\sqrt{\frac{2d\log(en/d)}{n}},$$
and therefore $\mathfrak R_n(\mathcal H)\le\sqrt{2d\log(en/d)/n}$.

*Proof.* $\mathfrak R_S(\mathcal H)$ depends only on the finite set $\mathcal H|_S=\{h|_S\}\subset\{\pm1\}^n$, of size at most $\tau_{\mathcal H}(n)$ (growth function).
Each $h|_S$ has $\|h|_S\|_2=\sqrt n$. Massart with $r=\sqrt n$: $\mathfrak R_S\le\sqrt{2\log|\mathcal H|_S|/n}\le\sqrt{2\log\tau_{\mathcal H}(n)/n}$.
Sauer–Shelah: $\tau_{\mathcal H}(n)\le\sum_{k\le d}\binom nk\le(en/d)^d$ for $n\ge d$.
Take expectation over $S$ for $\mathfrak R_n$. ∎

*Comparison.* Plugging into Theorem 5.3 recovers the VC generalisation bound $L_{\mathcal D}(h)\le L_S(h)+\sqrt{2d\log(en/d)/n}+\sqrt{\log(1/\delta)/(2n)}$ (note 04, up to constants).
The important direction is that Rademacher can be *much smaller* than the VC bound: it is data-dependent.
Halfspaces in $\mathbb R^d$ have $\mathrm{VCdim}=d+1$, but if the data lie in a ball of radius $R$ and one restricts to $\|w\|\le B$ (margin $1/B$), Theorem 5.7 gives $BR/\sqrt n$ regardless of $d$.
Similarly, if the sample happens to be degenerate (e.g. all $x_i$ nearly parallel), $\mathbb E_\sigma\|\sum\sigma_ix_i\|$ is what it is, not the worst case.
The reverse inequality (VC $\lesssim$ Rademacher) fails in general: no lower bound of order $\sqrt{d/n}$ holds for every sample.

**Theorem 5.10 (Dudley's entropy integral, via chaining)** [S27]**.** For $\mathcal F$ with values in $\mathbb R$ and any $\alpha\ge0$,
$$\mathfrak R_S(\mathcal F)\le\inf_{\alpha>0}\Big(4\alpha+\frac{12}{\sqrt n}\int_\alpha^{\infty}\sqrt{\log\mathcal N(\varepsilon,\mathcal F,L_2(S))}\,d\varepsilon\Big).$$
(The integrand vanishes for $\varepsilon\ge\sup_fd_S(f,0)$, so the integral is finite for bounded classes.)

*Proof sketch (chaining).* Let $\varepsilon_j=2^{-j}\sup_f\|f|_S\|/\sqrt n$ and $C_j$ a minimal $\varepsilon_j$-cover; write $\pi_j(f)$ for the nearest element of $C_j$ to $f$.
Telescope: $f=\pi_0(f)+\sum_{j\ge1}(\pi_j(f)-\pi_{j-1}(f))+(f-\pi_J(f))$.
The last term contributes at most $\varepsilon_J$ to the Rademacher average (Cauchy–Schwarz with $\|\sigma\|=\sqrt n$).
Each link $\pi_j(f)-\pi_{j-1}(f)$ ranges over a set of at most $|C_j||C_{j-1}|\le|C_j|^2$ vectors with $d_S$-norm $\le\varepsilon_j+\varepsilon_{j-1}=3\varepsilon_j$; Massart bounds its contribution by $\frac{3\varepsilon_j\sqrt n\sqrt{2\log|C_j|^2}}{n}=\frac{6\varepsilon_j\sqrt{\log\mathcal N(\varepsilon_j)}}{\sqrt n}$.
Summing over $j$ and comparing the sum with the integral ($\varepsilon_j-\varepsilon_{j+1}=\varepsilon_j/2$) gives $\frac{12}{\sqrt n}\int\sqrt{\log\mathcal N(\varepsilon)}d\varepsilon$; stopping the chain at scale $\alpha$ leaves the $4\alpha$ term.
A single-scale (no chaining) argument would give only $\alpha+\sqrt{2\log\mathcal N(\alpha)/n}$, which is worse whenever $\log\mathcal N$ grows polynomially in $1/\varepsilon$. ∎

*Interpolation.* Finite class: $\mathcal N(\varepsilon)\le|\mathcal F|$ for all $\varepsilon$, so Dudley (with $\alpha\to0$, integral up to $r/\sqrt n$) reproduces Massart up to constants.
VC class: **Haussler's bound** [S26] states that for $\mathcal H$ with $\mathrm{VCdim}=d$ and any empirical $L_2(S)$ metric, $\mathcal N(\varepsilon,\mathcal H,L_2(S))\le\big(\frac{c}{\varepsilon}\big)^{O(d)}$ (specifically $\le e(d+1)(2e/\varepsilon^2)^d$), *independently of $n$*.
Then $\int_0^1\sqrt{d\log(c/\varepsilon)}\,d\varepsilon=O(\sqrt d)$, and Dudley gives $\mathfrak R_S(\mathcal H)\le C\sqrt{d/n}$ — removing the $\log(n/d)$ factor of Theorem 5.9.
For smooth classes ($\log\mathcal N\sim\varepsilon^{-p}$, $p<2$) the integral still converges and gives $n^{-1/2}$ rates; for $p>2$ it diverges at $0$ and one takes $\alpha>0$, giving slower rates $n^{-1/p}$.

## Worked example

**Thresholds on two points.** $\mathcal H=\{h_t:x\mapsto\mathrm{sign}(x-t)\}$ on $\mathbb R$ with $\pm1$ outputs, $S=(x_1,x_2)$ with $x_1<x_2$.
Realisable sign patterns $h|_S$: $(-,-)$ (t large), $(-,+)$, $(+,+)$; not $(+,-)$.
For each $\sigma\in\{\pm1\}^2$ compute $\max_h\frac12\langle\sigma,h|_S\rangle$:

| $\sigma$ | best $h\vert_S$ | $\frac12\langle\sigma,h\vert_S\rangle$ |
|---|---|---|
| $(+,+)$ | $(+,+)$ | $1$ |
| $(-,-)$ | $(-,-)$ | $1$ |
| $(-,+)$ | $(-,+)$ | $1$ |
| $(+,-)$ | $(+,+)$ or $(-,-)$ | $0$ |

$\mathfrak R_S(\mathcal H)=\frac14(1+1+1+0)=\frac34$. Check via the interpretation: $\mathfrak R_S=1-2\mathbb E_\sigma\min_hL_S(h;\sigma)$; min training error is $0$ in three cases and $\frac12$ in one, average $\frac18$, so $1-\frac14=\frac34$.
Compare: the full cube ($\mathcal H$ shattering $S$) would give $1$; Massart with $|\mathcal H|_S|=3$ gives $\sqrt{2\log3/2}\approx1.05$ — vacuous at $n=2$, as expected. `rademacher_threshold` reproduces $0.75$ by Monte Carlo for such an $S$.

**Linear bound, $n=100$, $B=R=1$.** Theorem 5.7: $\mathfrak R_S\le BR/\sqrt n=0.1$.
Via Theorem 5.3 with hinge loss ($L_\ell=1$) and the contraction lemma: $L^{\mathrm{hinge}}_{\mathcal D}(w)\le L^{\mathrm{hinge}}_S(w)+2\cdot0.1+\sqrt{\log(1/\delta)/200}$; at $\delta=0.05$ the last term is $\sqrt{2.996/200}\approx0.122$, total slack $\approx0.32$.
For $n=10^4$ the slack is $0.02+0.012=0.032$. For comparison, the VC route for halfspaces in $\mathbb R^{d}$ with $d=1000$ gives $\sqrt{2\cdot1001\log(e\cdot100/1001)/100}$, whose logarithm is negative (the bound $(en/d)^d$ needs $n\ge d$) — the VC bound is simply unavailable in this regime, while $0.1$ stands.

**Exact vs bound for random data.** If $x_i$ are i.i.d. uniform on the unit sphere in $\mathbb R^d$ with $d$ large, $\mathbb E\|\sum\sigma_ix_i\|\approx\sqrt n$ (the $x_i$ are nearly orthogonal), so the exact value $\frac Bn\mathbb E\|\sum\sigma_ix_i\|\approx B/\sqrt n$ matches the bound.
If instead all $x_i=x$ (one direction), $\|\sum\sigma_ix_i\|=|\sum\sigma_i|$ and $\mathbb E|\sum\sigma_i|\approx\sqrt{2n/\pi}$, so the exact value is $\approx0.8\,B/\sqrt n$ — data-dependence in action.

## Pitfalls

- Confusing $\mathfrak R_S$ (a number computed from the sample, random through $S$) with $\mathfrak R_n$ (its expectation).
  Theorem 5.3 has two forms precisely because one can be computed and the other cannot; the price is $3\sqrt{\cdot}$ instead of $\sqrt{\cdot}$.
- The definition is sometimes written with $|\cdot|$ inside the sup (Bartlett–Mendelson) or without the $\frac1n$ (Bousquet).
  The "absolute" version is at most twice the signed one when $0\in\mathcal F$; the generalisation theorem here uses the signed version.
- Rademacher complexity is of the *loss class* $\ell\circ\mathcal H$, not of $\mathcal H$.
  Passing between them requires the contraction lemma (Lipschitz loss) or the $\frac12$ identity for $0$-$1$ loss.
  Squared loss is only Lipschitz on a bounded range — this matters in note 07.
- Massart needs the class restricted to $S$ to be finite; for infinite $\mathcal H$ use $|\mathcal H|_S|\le\tau_{\mathcal H}(n)$, not $|\mathcal H|$.
- In Theorem 5.7 the bound is $BR/\sqrt n$, not $BR/n$: the $\frac1n$ prefactor combines with $\sqrt{nR^2}$.
- Symmetrisation gives a factor $2$ and is one-sided. The two-sided version $\mathbb E\sup|\mathbb Ef-\hat{\mathbb E}f|\le2\mathfrak R_n$ holds for the absolute-value Rademacher complexity.
- McDiarmid needs *independent* coordinates and bounded differences for *every* configuration, not just on average; $c_i=1/n$ relies on $f\in[0,1]$ (for $[a,b]$-valued $f$ the constant is $(b-a)/n$ and the tail term scales by $(b-a)$).
- Dudley's integral starts at $\alpha$, not $0$, in general: if $\log\mathcal N(\varepsilon)\gtrsim\varepsilon^{-2}$ the integral diverges at $0$ and $\alpha$ must be optimised.

## Questions

**Q:** Define empirical Rademacher complexity and explain in one sentence what it measures.
**A:** $\mathfrak R_S(\mathcal F)=\mathbb E_\sigma\sup_f\frac1n\sum_i\sigma_if(z_i)$ with i.i.d. uniform signs $\sigma_i$; it is the expected maximal correlation between a function in $\mathcal F$ and random noise on the sample, i.e. how well $\mathcal F$ can fit random labels.

**Q:** State and prove the symmetrisation lemma.
**A:** $\mathbb E_S\sup_f(\mathbb Ef-\hat{\mathbb E}_Sf)\le2\mathfrak R_n(\mathcal F)$.
Introduce a ghost sample $S'$, write $\mathbb Ef=\mathbb E_{S'}\hat{\mathbb E}_{S'}f$, pull $\mathbb E_{S'}$ outside the sup by Jensen, insert signs $\sigma_i$ using that swapping $z_i\leftrightarrow z_i'$ preserves the joint law, split the sup of a sum into two sups, and use $-\sigma\overset d=\sigma$.

**Q:** State McDiarmid's inequality and verify the bounded-differences property for $S\mapsto\sup_f(\mathbb Ef-\hat{\mathbb E}_Sf)$.
**A:** For independent $Z_i$ and $g$ with $|g(z)-g(z^{(i)})|\le c_i$: $\Pr[g-\mathbb Eg\ge t]\le\exp(-2t^2/\sum c_i^2)$.
Changing one $z_i$ moves each $\hat{\mathbb E}_Sf$ by at most $\frac1n$ for $[0,1]$-valued $f$, and $|\sup a-\sup b|\le\sup|a-b|$, so $c_i=\frac1n$, $\sum c_i^2=\frac1n$, yielding the $\sqrt{\log(1/\delta)/(2n)}$ term.

**Q:** Why is the $\mathfrak R_S$ version of the generalisation bound useful, and where does the $3$ come from?
**A:** $\mathfrak R_S$ can be computed or estimated from the data (Monte Carlo over $\sigma$, or the exact formula for linear classes), while $\mathfrak R_n$ needs $\mathcal D$.
The $3$ is $2$ from replacing $2\mathfrak R_n$ by $2\mathfrak R_S+2\sqrt{\cdot}$ (McDiarmid on $\mathfrak R_S$, constant $\frac1n$) plus $1$ from the original deviation term, with $\delta\to\delta/2$ for the union bound.

**Q:** Prove Massart's lemma.
**A:** Jensen: $e^{s\mathbb E\max}\le\mathbb Ee^{s\max}\le\sum_a\prod_i\mathbb Ee^{s\sigma_ia_i}=\sum_a\prod_i\cosh(sa_i)\le|A|e^{s^2r^2/2}$; take logs, divide by $s$, choose $s=\sqrt{2\log|A|}/r$ to get $r\sqrt{2\log|A|}$, divide by $n$.

**Q:** Derive the Rademacher complexity of $\{x\mapsto\langle w,x\rangle:\|w\|\le B\}$ and explain why it is dimension-free.
**A:** For fixed $\sigma$ the sup is $\frac Bn\|\sum\sigma_ix_i\|$ by Cauchy–Schwarz (attained at $w\propto\sum\sigma_ix_i$); Jensen gives $\mathbb E\|\cdot\|\le\sqrt{\mathbb E\|\cdot\|^2}=\sqrt{\sum\|x_i\|^2}\le R\sqrt n$, since cross terms $\mathbb E\sigma_i\sigma_j$ vanish.
Only norms appear, so it holds verbatim in any Hilbert space, e.g. an RKHS with $k(x,x)\le R^2$.

**Q:** How does Rademacher complexity relate to VC dimension, in both directions?
**A:** Upper: $\mathfrak R_S(\mathcal H)\le\sqrt{2\log\tau_{\mathcal H}(n)/n}\le\sqrt{2d\log(en/d)/n}$ by Massart on the $\le\tau_{\mathcal H}(n)$ restrictions plus Sauer; Dudley + Haussler improve this to $O(\sqrt{d/n})$.
Lower: there is no matching lower bound for every sample — Rademacher is data-dependent and can be far smaller (large-margin linear classes: $BR/\sqrt n$ independent of $d$).

**Q:** What is the contraction lemma used for?
**A:** To pass from a loss class to the hypothesis class: for $\ell(h(x),y)=\phi(yh(x))$ with $\phi$ $L$-Lipschitz, $\mathfrak R_S(\ell\circ\mathcal H)\le L\,\mathfrak R_S(\mathcal H)$.
Combined with Theorem 5.3 and Theorem 5.7 it yields margin bounds for SVMs and bounds for logistic regression, with $L=1$ for hinge and $L=1/\gamma$ for the $\gamma$-ramp loss.

**Q:** Explain the chaining idea behind Dudley's bound in two sentences.
**A:** Approximate each $f$ by a chain of nested covers at geometrically decreasing scales and bound the Rademacher average of each link by Massart's lemma applied to the finite set of differences, whose norm is of the order of the scale.
Summing over scales turns $\sum_j\varepsilon_j\sqrt{\log\mathcal N(\varepsilon_j)}$ into $\int\sqrt{\log\mathcal N(\varepsilon)}d\varepsilon$, which is tighter than a single-scale cover whenever the entropy grows polynomially in $1/\varepsilon$.

## Code

`src/py/rademacher.py`:

- `empirical_rademacher_finite(predictions, n_sigma, rng)`: Monte Carlo estimate of $\mathfrak R_S$ for a finite class given as the matrix of predictions $f|_S$; use with the three threshold labelings of the worked example to recover $0.75$; `empirical_rademacher_exact(predictions)` enumerates all $2^n$ sign vectors and returns exactly $0.75$.
- `rademacher_linear_exact(X, B, n_sigma, rng)`: evaluates $\frac Bn\mathbb E_\sigma\|\sum_i\sigma_ix_i\|$ by sampling $\sigma$; demonstrates the exact formula from Theorem 5.7 and its dependence on the geometry of $X$.
- `rademacher_linear_bound(X, B)`: the closed-form bound $BR/\sqrt n$ with $R=\max_i\|x_i\|$; compare with the exact value to see the Jensen gap.
- `rademacher_threshold(X, n_sigma, rng)`: $\mathfrak R_S$ of thresholds in $O(n)$ per $\sigma$: in sorted order the $n+1$ labelings score $T-2P_k$ ($P_k$ prefix sums of $\sigma$), so the sup is $T-2\min_kP_k$; illustrates Theorem 5.9 with $d=1$.
- `generalisation_bound(emp_risk, rad, n, delta)` and `rademacher_bound_experiment(problem, n, delta, trials, n_sigma, rng)`: Theorem 5.3 with $\mathfrak R_S(\ell\circ\mathcal H)=\tfrac12\mathfrak R_S(\mathcal H)$, checked on many resamples against the exact one-sided sup from `vc.py`.
- `massart_bound(n_hyps, n)`: $\sqrt{2\log|\mathcal F|/n}$ for $[-1,1]$-valued classes; shows when the finite-class bound is vacuous (small $n$).

## References

- Mohri, Rostamizadeh, Talwalkar, *Foundations of Machine Learning*, 2nd ed., Ch. 3 (Thm 3.3 Rademacher bound, Thm 3.7 Massart, Cor. 3.8 and 3.18 Rademacher vs growth function/VC), Ch. 5.4 (contraction lemma, Lemma 5.7), Appendix D (McDiarmid, Thm D.8).
- Shalev-Shwartz, Ben-David, *Understanding Machine Learning*, Ch. 26 (Lemma 26.2 symmetrisation, Thm 26.5 generalisation, Lemma 26.8 Massart, Lemma 26.9 contraction, Lemma 26.10 linear classes with $\ell_2$, Lemma 26.11 with $\ell_1$).
- P. L. Bartlett, S. Mendelson, "Rademacher and Gaussian complexities: risk bounds and structural results", *JMLR* 3 (2002).
- V. Koltchinskii, D. Panchenko, "Rademacher processes and bounding the risk of function learning", 2000.
- C. McDiarmid, "On the method of bounded differences", *Surveys in Combinatorics* (1989).
- M. Ledoux, M. Talagrand, *Probability in Banach Spaces* (1991), Thm 4.12 (contraction).
- R. M. Dudley, "The sizes of compact subsets of Hilbert space and continuity of Gaussian processes", *J. Funct. Anal.* 1 (1967).
- D. Haussler, "Sphere packing numbers for subsets of the Boolean $n$-cube with bounded VC dimension", *J. Comb. Theory A* 69 (1995).
