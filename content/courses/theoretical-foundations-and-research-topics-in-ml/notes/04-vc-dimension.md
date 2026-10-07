# 04 VC dimension

Notes 02–03 make learnability depend on $\log|\mathcal H|$, which is useless for infinite classes such as thresholds, rectangles or halfspaces, although these are obviously learnable (note 03 proved it for rectangles by hand). The Vapnik–Chervonenkis dimension replaces $\log|\mathcal H|$ by a combinatorial measure of how many *distinct labellings* $\mathcal H$ can produce on $n$ points. The Sauer–Shelah lemma shows this number is polynomial in $n$ once the VC dimension is finite, and the fundamental theorem of statistical learning states that finite VC dimension is *equivalent* to PAC learnability, agnostic PAC learnability, uniform convergence and ERM success, with sample complexity $\Theta((d+\log(1/\delta))/\varepsilon^2)$. This is the central theorem of the first half of the course; later notes (Rademacher complexity, margins, kernels) refine the constants and the data dependence.

## Definitions

Labels are $\{0,1\}$ in this note (as in UML); every statement transfers verbatim to $\{-1,+1\}$.

1. **Restriction.** For $\mathcal H\subseteq\{0,1\}^{\mathcal X}$ and $C=\{c_1,\dots,c_n\}\subseteq\mathcal X$, the restriction is $\mathcal H_C=\{(h(c_1),\dots,h(c_n)):h\in\mathcal H\}\subseteq\{0,1\}^n$, the set of labellings of $C$ realised by $\mathcal H$. Always $|\mathcal H_C|\le2^n$.
2. **Shattering.** $\mathcal H$ shatters $C$ if $\mathcal H_C=\{0,1\}^C$, i.e. $|\mathcal H_C|=2^{|C|}$: every labelling of $C$ is realised by some $h\in\mathcal H$.
3. **VC dimension.** $\mathrm{VCdim}(\mathcal H)=\max\{|C|:C\subseteq\mathcal X,\ \mathcal H\text{ shatters }C\}$, or $\infty$ if $\mathcal H$ shatters arbitrarily large sets. Write $d=\mathrm{VCdim}(\mathcal H)$.
   *Proof obligation.* To show $\mathrm{VCdim}(\mathcal H)=d$ one must (i) exhibit **one** set of size $d$ that is shattered, and (ii) show that **no** set of size $d+1$ is shattered (for *every* set of size $d+1$, find a labelling not realised).
4. **Growth function.** $\tau_{\mathcal H}(n)=\max_{C\subseteq\mathcal X,|C|=n}|\mathcal H_C|$. So $\tau_{\mathcal H}(n)=2^n$ for $n\le d$ and $\tau_{\mathcal H}(n)<2^n$ for $n>d$.
5. **Standard classes.**
   - Thresholds on $\mathbb R$: $\mathcal H_{\mathrm{thr}}=\{h_t:t\in\mathbb R\}$, $h_t(x)=\mathbb 1[x\ge t]$.
   - Intervals: $\mathcal H_{\mathrm{int}}=\{h_{a,b}:a\le b\}$, $h_{a,b}(x)=\mathbb 1[a\le x\le b]$.
   - Axis-aligned rectangles in $\mathbb R^2$: $\mathcal H_{\mathrm{rect}}$, $h(x)=\mathbb 1[a_1\le x^{(1)}\le b_1,\ a_2\le x^{(2)}\le b_2]$.
   - Homogeneous halfspaces in $\mathbb R^k$: $\mathcal H_{\mathrm{hs}}^0=\{x\mapsto\mathbb 1[\langle w,x\rangle\ge0]:w\in\mathbb R^k\}$. Non-homogeneous: $\mathcal H_{\mathrm{hs}}=\{x\mapsto\mathbb 1[\langle w,x\rangle+b\ge0]\}$. (We use $k$ for the ambient dimension to keep $d$ for VC dimension.)
   - Finite unions of intervals: $\mathcal H_{\cup}=\{\mathbb 1_{I_1\cup\dots\cup I_m}:m\in\mathbb N,\ I_j\text{ intervals}\}$.
   - Sine class: $\mathcal H_{\sin}=\{x\mapsto\mathbb 1[\sin(\omega x)\ge0]:\omega\in\mathbb R\}$ on $\mathbb R$.
6. **Convex hull.** $\mathrm{conv}(A)=\{\sum_i\lambda_ia_i:a_i\in A,\lambda_i\ge0,\sum\lambda_i=1\}$.
7. **Uniform convergence, PAC, agnostic PAC, ERM success** as in notes 02–03. "ERM is a successful (agnostic) PAC learner" means the ERM rule satisfies the (agnostic) PAC guarantee with some finite sample complexity.

## Results

### VC dimension examples

**Theorem 4.1 (thresholds)** [S9 §6.3.1]**.** $\mathrm{VCdim}(\mathcal H_{\mathrm{thr}})=1$.

*Proof.* (i) $C=\{0\}$: $h_{1}(0)=0$, $h_{-1}(0)=1$; shattered. (ii) Let $C=\{c_1<c_2\}$. The labelling $(1,0)$ needs $c_1\ge t>c_2$, impossible since $c_1<c_2$. ∎

**Theorem 4.2 (intervals)** [S9 §6.3.2]**.** $\mathrm{VCdim}(\mathcal H_{\mathrm{int}})=2$.

*Proof.* (i) $C=\{1,2\}$: $(0,0)$ by $[3,4]$, $(1,0)$ by $[1,1]$, $(0,1)$ by $[2,2]$, $(1,1)$ by $[1,2]$. (ii) Any $C=\{c_1<c_2<c_3\}$: the labelling $(1,0,1)$ requires $a\le c_1$ and $c_3\le b$, hence $a\le c_2\le b$, forcing $h(c_2)=1$. Not realised. ∎

**Theorem 4.3 (axis-aligned rectangles)** [S9 §6.3.3; S10 §3.3]**.** $\mathrm{VCdim}(\mathcal H_{\mathrm{rect}})=4$.

*Proof.* (i) The diamond $C=\{(1,0),(0,1),(-1,0),(0,-1)\}$. For a subset $P\subseteq C$ to be labelled $1$, take the bounding box of $P$ (a degenerate rectangle if $|P|\le2$; the empty rectangle if $P=\emptyset$). Each point of $C$ is the unique extreme point of $C$ in its direction ($(1,0)$ is the only point with $x^{(1)}=1$, etc.), so a point $c\notin P$ has a coordinate strictly outside the range of that coordinate over $P$; hence $c$ is outside the bounding box. Example: $P=\{(1,0),(-1,0)\}$ gives box $[-1,1]\times\{0\}$, which excludes $(0,\pm1)$. All $16$ labellings realised.
(ii) Let $|C|=5$. Pick a point of $C$ with minimal $x^{(1)}$, one with maximal $x^{(1)}$, one with minimal $x^{(2)}$, one with maximal $x^{(2)}$ (at most four distinct points); some fifth point $p\in C$ is none of these, so $p$ lies in the bounding box $B$ of the other four (both its coordinates are within the ranges attained by them). Label the four extreme points $1$ and $p$ as $0$. Any rectangle containing the four extreme points contains $B\ni p$, so it labels $p$ as $1$. Not realised. ∎

**Lemma 4.4 (Radon's theorem)** [S10 Thm 3.13]**.** Any set of $k+2$ points in $\mathbb R^k$ can be partitioned into two disjoint sets $I,J$ with $\mathrm{conv}(I)\cap\mathrm{conv}(J)\neq\emptyset$.

*Proof.* Let the points be $x_1,\dots,x_{k+2}$. The homogeneous linear system in $\lambda\in\mathbb R^{k+2}$
$$\sum_{i=1}^{k+2}\lambda_ix_i=0\ (k\text{ equations}),\qquad\sum_{i=1}^{k+2}\lambda_i=0\ (1\text{ equation})$$
has $k+1$ equations and $k+2$ unknowns, so it has a nonzero solution $\lambda$. Let $I=\{i:\lambda_i>0\}$, $J=\{i:\lambda_i\le0\}$. Since $\sum\lambda_i=0$ and $\lambda\neq0$, both $I$ and $\{i:\lambda_i<0\}\subseteq J$ are nonempty, and $\Lambda:=\sum_{i\in I}\lambda_i=-\sum_{j\in J}\lambda_j>0$. Then
$$z:=\sum_{i\in I}\frac{\lambda_i}{\Lambda}x_i=\sum_{j\in J}\frac{-\lambda_j}{\Lambda}x_j,$$
where both coefficient vectors are non-negative and sum to $1$. So $z\in\mathrm{conv}(I)\cap\mathrm{conv}(J)$. ∎

**Theorem 4.5 (halfspaces)** [S9 §9.1.3; S10 §3.3]**.** $\mathrm{VCdim}(\mathcal H_{\mathrm{hs}}^0)=k$ and $\mathrm{VCdim}(\mathcal H_{\mathrm{hs}})=k+1$ in $\mathbb R^k$.

*Proof.* Non-homogeneous, lower bound. $C=\{0,e_1,\dots,e_k\}$. For a labelling $(y_0,y_1,\dots,y_k)\in\{0,1\}^{k+1}$ put $s_i=2y_i-1\in\{\pm1\}$, $w=(s_1,\dots,s_k)$, $b=s_0/2$. Then $\langle w,0\rangle+b=s_0/2$ has the sign of $s_0$, and $\langle w,e_i\rangle+b=s_i+s_0/2$ has the sign of $s_i$ (since $|s_0/2|<1$). So $\mathbb 1[\langle w,x\rangle+b\ge0]$ realises the labelling. (Strict signs, so the boundary convention is irrelevant.)

Non-homogeneous, upper bound. Let $|C|=k+2$. By Radon, $C=I\sqcup J$ with a point $z\in\mathrm{conv}(I)\cap\mathrm{conv}(J)$. Label $I$ by $1$, $J$ by $0$. Suppose $h(x)=\mathbb 1[\langle w,x\rangle+b\ge0]$ realises it. The positive region $\{\langle w,x\rangle+b\ge0\}$ is convex and contains $I$, hence contains $\mathrm{conv}(I)\ni z$; the negative region $\{\langle w,x\rangle+b<0\}$ is convex and contains $J$, hence $z$. Contradiction: the two regions are disjoint. So no set of $k+2$ points is shattered.

Homogeneous, lower bound. $C=\{e_1,\dots,e_k\}$, $w=(s_1,\dots,s_k)$: $\langle w,e_i\rangle=s_i$.

Homogeneous, upper bound. Let $x_1,\dots,x_{k+1}\in\mathbb R^k$; they are linearly dependent: $\sum_ia_ix_i=0$ with $a\neq0$. Let $I=\{i:a_i>0\}$, $J=\{i:a_i<0\}$; at least one is nonempty, say $I$ (else negate $a$). Suppose $C$ is shattered. Case $J=\emptyset$: label all of $I$ by $0$, so some $w$ has $\langle w,x_i\rangle<0$ for $i\in I$; then $0=\langle w,\sum_Ia_ix_i\rangle=\sum_Ia_i\langle w,x_i\rangle<0$. Contradiction. Case $J\neq\emptyset$: label $I$ by $1$ and $J$ by $0$, so $\langle w,x_i\rangle\ge0$ on $I$ and $<0$ on $J$. Then
$$0\le\sum_{i\in I}a_i\langle w,x_i\rangle=\Bigl\langle w,\sum_{i\in I}a_ix_i\Bigr\rangle=\Bigl\langle w,\sum_{j\in J}(-a_j)x_j\Bigr\rangle=\sum_{j\in J}(-a_j)\langle w,x_j\rangle<0.$$
Contradiction. ∎

**Proposition 4.6 (finite classes)** [S9 §6.3]**.** $\mathrm{VCdim}(\mathcal H)\le\log_2|\mathcal H|$.

*Proof.* If $C$ is shattered then $2^{|C|}=|\mathcal H_C|\le|\mathcal H|$. ∎

The inequality can be strict by an arbitrary amount: $\mathcal H=\{h_{t}:t\in\{1,\dots,N\}\}$ (thresholds on a grid) has $|\mathcal H|=N$ but VC dimension $1$. VC dimension is the right quantity; $\log|\mathcal H|$ is only an upper bound on it.

**Proposition 4.7 (infinite VC dimension)** [S9 §6.3.4, Exercise 6.8]**.** (a) $\mathrm{VCdim}(\mathcal H_{\cup})=\infty$. (b) $\mathrm{VCdim}(\mathcal H_{\sin})=\infty$, although $\mathcal H_{\sin}$ has a single real parameter.

*Proof.* (a) Let $C=\{c_1<\dots<c_n\}$ be any $n$ distinct reals and $P\subseteq C$ a subset. Let $\rho=\min_i(c_{i+1}-c_i)/3$ and take $\bigcup_{c\in P}[c-\rho,c+\rho]$: it contains exactly the points of $P$. So every finite set is shattered.
(b) Statement only (UML Exercise 6.8 / 7.4): for $x_i=2^{-i}$, $i=1,\dots,n$, and any labelling $(y_1,\dots,y_n)$, the choice $\omega=\pi\bigl(1+\sum_{i=1}^n(1-y_i)2^i\bigr)$ gives $\mathbb 1[\sin(\omega x_i)\ge0]=y_i$: the binary expansion of $\omega/\pi$ is read off bit by bit by $\sin(\omega2^{-i})$. So $\{2^{-1},\dots,2^{-n}\}$ is shattered for every $n$. ∎

### Growth function and Sauer–Shelah

**Theorem 4.8 (Sauer–Shelah lemma)** [S9 Lemma 6.10; S10 Thm 3.17; S17]**.** If $\mathrm{VCdim}(\mathcal H)=d<\infty$ then for all $n$,
$$\tau_{\mathcal H}(n)\le\sum_{i=0}^{d}\binom ni.$$
More precisely, for every finite $C\subseteq\mathcal X$,
$$|\mathcal H_C|\le\bigl|\{B\subseteq C:\ \mathcal H\text{ shatters }B\}\bigr|.\tag{S}$$

*Proof.* (S) implies the lemma: if $\mathrm{VCdim}(\mathcal H)=d$, every shattered $B$ has $|B|\le d$, and the number of subsets of an $n$-set of size $\le d$ is $\sum_{i\le d}\binom ni$.

We prove (S) by induction on $n=|C|$. Note that $\emptyset$ is always shattered (the empty labelling is realised by any $h$), so the right side is $\ge1$.

*Base $n=1$.* $|\mathcal H_C|\in\{1,2\}$. If $1$, the right side is $\ge1$ (the empty set). If $2$, $C$ itself is shattered and the right side is $2$.

*Step.* Let $C=\{c_1,\dots,c_n\}$, $C'=\{c_2,\dots,c_n\}$, and assume (S) for all classes and all sets of size $n-1$. Split the labellings in $\mathcal H_C$ according to the label of $c_1$:
$$Y_0=\{(y_2,\dots,y_n):\ (0,y_2,\dots,y_n)\in\mathcal H_C\ \text{or}\ (1,y_2,\dots,y_n)\in\mathcal H_C\},$$
$$Y_1=\{(y_2,\dots,y_n):\ (0,y_2,\dots,y_n)\in\mathcal H_C\ \text{and}\ (1,y_2,\dots,y_n)\in\mathcal H_C\}.$$
Each labelling in $\mathcal H_C$ projects to an element of $Y_0$; those projected patterns that arise from *two* labellings (differing at $c_1$) are counted once in $Y_0$ and once more in $Y_1$. Hence
$$|\mathcal H_C|=|Y_0|+|Y_1|.$$

*Bound $Y_0$.* $Y_0=\mathcal H_{C'}$. By the induction hypothesis applied to $\mathcal H$ and $C'$:
$$|Y_0|\le|\{B\subseteq C':\mathcal H\text{ shatters }B\}|=|\{B\subseteq C:\ c_1\notin B,\ \mathcal H\text{ shatters }B\}|.$$

*Bound $Y_1$.* Define the subclass
$$\mathcal H'=\{h\in\mathcal H:\ \exists h'\in\mathcal H\text{ with }h'(c_1)\neq h(c_1)\text{ and }h'(c_i)=h(c_i)\ \forall i\ge2\},$$
the hypotheses whose $c_1$-flipped restriction is also realised. Then $Y_1=\mathcal H'_{C'}$. Key observation: if $\mathcal H'$ shatters $B\subseteq C'$, then $\mathcal H'$ (hence $\mathcal H$) shatters $B\cup\{c_1\}$, because every labelling of $B$ is realised by some $h\in\mathcal H'$, and both values at $c_1$ are available by definition of $\mathcal H'$. By the induction hypothesis applied to $\mathcal H'$ and $C'$:
$$|Y_1|=|\mathcal H'_{C'}|\le|\{B\subseteq C':\mathcal H'\text{ shatters }B\}|=|\{B\subseteq C:\ c_1\in B,\ \mathcal H'\text{ shatters }B\}|\le|\{B\subseteq C:\ c_1\in B,\ \mathcal H\text{ shatters }B\}|,$$
where the equality is the bijection $B\mapsto B\cup\{c_1\}$ justified by the key observation, and the last step is $\mathcal H'\subseteq\mathcal H$.

*Assemble.* $|\mathcal H_C|=|Y_0|+|Y_1|\le|\{B:c_1\notin B,\text{ shattered}\}|+|\{B:c_1\in B,\text{ shattered}\}|=|\{B\subseteq C:\mathcal H\text{ shatters }B\}|$. ∎

**Lemma 4.9 (polynomial bound)** [S9 Lemma 6.10; S10 Cor. 3.18]**.** For $n\ge d\ge1$,
$$\sum_{i=0}^d\binom ni\le\Bigl(\frac{en}{d}\Bigr)^d.$$

*Proof.* Since $n/d\ge1$, $(n/d)^{d-i}\ge1$ for $i\le d$, so
$$\sum_{i=0}^d\binom ni\le\sum_{i=0}^d\binom ni\Bigl(\frac nd\Bigr)^{d-i}=\Bigl(\frac nd\Bigr)^d\sum_{i=0}^d\binom ni\Bigl(\frac dn\Bigr)^i\le\Bigl(\frac nd\Bigr)^d\sum_{i=0}^n\binom ni\Bigl(\frac dn\Bigr)^i=\Bigl(\frac nd\Bigr)^d\Bigl(1+\frac dn\Bigr)^n\le\Bigl(\frac nd\Bigr)^de^d,$$
using the binomial theorem and $1+x\le e^x$. ∎

Consequently $\tau_{\mathcal H}(n)\le(en/d)^d$ for $n\ge d$: a class with finite VC dimension realises only polynomially many labellings, and $\log\tau_{\mathcal H}(n)\le d\log(en/d)$ plays the role of $\log|\mathcal H|$.

### Uniform convergence from the growth function

**Theorem 4.10 (symmetrisation + Massart)** [S9 Thm 6.11]**.** For any $\mathcal H\subseteq\{0,1\}^{\mathcal X}$, any $\mathcal D$, and $\ell_{0\text{-}1}$,
$$\mathbb E_{S\sim\mathcal D^n}\sup_{h\in\mathcal H}\bigl|L_{\mathcal D}(h)-L_S(h)\bigr|\le\frac{4+\sqrt{\log\tau_{\mathcal H}(2n)}}{\sqrt{2n}}.$$
By Markov, with probability $\ge1-\delta$, $\sup_h|L_{\mathcal D}(h)-L_S(h)|\le\frac{4+\sqrt{\log\tau_{\mathcal H}(2n)}}{\delta\sqrt{2n}}$; by McDiarmid (Theorem 2.8, $c_i=1/n$) the $1/\delta$ improves to an additive $\sqrt{\log(1/\delta)/(2n)}$.

*Proof sketch (double-sample trick).*
*Step 1 (ghost sample).* Let $S'=(z'_1,\dots,z'_n)\sim\mathcal D^n$ be an independent copy of $S$. For each fixed $h$, $L_{\mathcal D}(h)=\mathbb E_{S'}L_{S'}(h)$. Hence
$$\mathbb E_S\sup_h|L_{\mathcal D}(h)-L_S(h)|=\mathbb E_S\sup_h\bigl|\mathbb E_{S'}[L_{S'}(h)-L_S(h)]\bigr|\le\mathbb E_{S,S'}\sup_h|L_{S'}(h)-L_S(h)|,$$
by Jensen ($|\cdot|$ convex, $\sup$ of expectations $\le$ expectation of sup). The unknown $L_{\mathcal D}$ has disappeared: only the $2n$ sample points matter.
*Step 2 (symmetrisation).* Write $L_{S'}(h)-L_S(h)=\frac1n\sum_i(\ell(h,z'_i)-\ell(h,z_i))$. Since $(z_i,z'_i)$ are i.i.d. pairs, swapping $z_i\leftrightarrow z'_i$ for any subset of indices leaves the joint distribution of $(S,S')$ unchanged. So, for independent Rademacher signs $\sigma_i\in\{\pm1\}$ uniform,
$$\mathbb E_{S,S'}\sup_h\Bigl|\frac1n\sum_i(\ell(h,z'_i)-\ell(h,z_i))\Bigr|=\mathbb E_{S,S'}\mathbb E_\sigma\sup_h\Bigl|\frac1n\sum_i\sigma_i(\ell(h,z'_i)-\ell(h,z_i))\Bigr|.$$
*Step 3 (finitely many hypotheses matter).* Fix $S,S'$ and let $C=\{x_1,\dots,x_n,x'_1,\dots,x'_n\}$. The vector $(\ell(h,z'_i)-\ell(h,z_i))_i$ depends on $h$ only through $h|_C\in\mathcal H_C$, which has at most $\tau_{\mathcal H}(2n)$ elements. So the inner sup is a maximum over $N\le\tau_{\mathcal H}(2n)$ fixed vectors $v^{(1)},\dots,v^{(N)}\in[-1,1]^n$ of $|\frac1n\sum_i\sigma_iv_i|$.
*Step 4 (maximal inequality; Massart).* For each fixed $v$, $\frac1n\sum_i\sigma_iv_i$ is a sum of $n$ independent zero-mean terms in $[-|v_i|/n,|v_i|/n]$, so by Hoeffding $P_\sigma(|\frac1n\sum\sigma_iv_i|\ge t)\le2e^{-nt^2/2}$. A union bound over $N$ vectors and integrating the tail ($\mathbb EX\le a+\int_a^\infty P(X\ge t)\,dt$ with $a=\sqrt{2\log N/n}$) gives
$$\mathbb E_\sigma\max_{j\le N}\Bigl|\frac1n\sum_i\sigma_iv^{(j)}_i\Bigr|\le\frac{4+\sqrt{\log N}}{\sqrt{2n}}.$$
(The sharper Massart lemma gives $\sqrt{2\log N/n}\cdot\max_j\|v^{(j)}\|/\sqrt n$, same rate.)
*Step 5.* Combine: the bound holds for every $(S,S')$ with $N\le\tau_{\mathcal H}(2n)$; take $\mathbb E_{S,S'}$. ∎

The quantity $\mathbb E_\sigma\sup_h\frac1n\sum_i\sigma_i\ell(h,z_i)$ appearing in Step 2 is the empirical Rademacher complexity $\mathfrak R_S$; the Rademacher note develops it directly.

### The fundamental theorem

**Theorem 4.11 (Fundamental theorem of statistical learning)** [S9 Thm 6.7 and Thm 6.8; S18]**.** Let $\mathcal H\subseteq\{0,1\}^{\mathcal X}$ with $\ell_{0\text{-}1}$. The following are equivalent:
1. $\mathcal H$ has the uniform convergence property;
2. any ERM rule is a successful agnostic PAC learner for $\mathcal H$;
3. $\mathcal H$ is agnostic PAC learnable;
4. any ERM rule is a successful PAC learner for $\mathcal H$;
5. $\mathcal H$ is PAC learnable;
6. $\mathrm{VCdim}(\mathcal H)=d<\infty$.

Moreover there are absolute constants $C_1,C_2$ such that

- agnostic: $\displaystyle C_1\frac{d+\log(1/\delta)}{\varepsilon^2}\le n_{\mathcal H}(\varepsilon,\delta)\le n^{\mathrm{UC}}_{\mathcal H}(\varepsilon/2,\delta)\le C_2\frac{d+\log(1/\delta)}{\varepsilon^2}$;
- realisable: $\displaystyle C_1\frac{d+\log(1/\delta)}{\varepsilon}\le n_{\mathcal H}(\varepsilon,\delta)\le C_2\frac{d\log(1/\varepsilon)+\log(1/\delta)}{\varepsilon}$.

*Proof sketch.* The trivial implications: $1\Rightarrow2$ is Lemma 2.5; $2\Rightarrow3$ and $4\Rightarrow5$ are by definition; $2\Rightarrow4$ and $3\Rightarrow5$ because realisable is a special case of agnostic.

$5\Rightarrow6$ (infinite VC ⇒ not learnable). If $\mathrm{VCdim}=\infty$, for every $n$ there is a shattered $C$ with $|C|=2n$. Run the No-Free-Lunch argument (Theorem 3.4) with distributions uniform on $C$ and labels given by the $2^{2n}$ functions $C\to\{0,1\}$; each is realised by some $h\in\mathcal H$ (shattering), so each $\mathcal D_i$ is realisable w.r.t. $\mathcal H$. The proof of 3.4 goes through unchanged and yields, for any learner and any $n$, a realisable $\mathcal D$ with $P_S(L_{\mathcal D}(A(S))\ge\tfrac18)\ge\tfrac17$, contradicting PAC learnability with $\varepsilon<\tfrac18,\delta<\tfrac17$.

$6\Rightarrow1$ (finite VC ⇒ uniform convergence). Sauer–Shelah and Lemma 4.9: $\tau_{\mathcal H}(2n)\le(2en/d)^d$, so $\log\tau_{\mathcal H}(2n)\le d\log(2en/d)$. Theorem 4.10 with McDiarmid: with probability $\ge1-\delta$,
$$\sup_h|L_{\mathcal D}(h)-L_S(h)|\le\frac{4+\sqrt{d\log(2en/d)}}{\sqrt{2n}}+\sqrt{\frac{\log(1/\delta)}{2n}}.$$
Setting the right side $\le\varepsilon$ and solving (the $\log n$ can be absorbed into the constant by a standard argument, [S9 Lemma A.2]) gives $n^{\mathrm{UC}}_{\mathcal H}(\varepsilon,\delta)\le C_2\frac{d+\log(1/\delta)}{\varepsilon^2}$. This is the upper bound in the agnostic case; the realisable upper bound with $d\log(1/\varepsilon)/\varepsilon$ uses the same double-sample trick but exploits $L_S(h_S)=0$ (relative deviations; S9 Thm 28.3; S10 Thm 3.20).

Lower bounds ($C_1$). Realisable: a shattered set of size $d$ with a distribution putting mass $1-8\varepsilon$ on one point and $8\varepsilon/(d-1)$ on the others; a learner seeing fewer than $\approx d/(32\varepsilon)$ samples misses about half of the light points and errs on half of those, giving risk $>\varepsilon$ with constant probability [S9 §28.2]; the $\log(1/\delta)/\varepsilon$ term comes from a two-point distribution. Agnostic: two-point distributions with $\eta(x)=\tfrac12\pm\varepsilon$ need $\Omega(1/\varepsilon^2)$ samples to tell apart (Le Cam / Bernoulli testing), and a shattered $d$-set with independent such coins gives $\Omega(d/\varepsilon^2)$. ∎

**Theorem 4.12 (VC generalisation bound, Vapnik-style form)** [S16; see the constants warning below]**.** Let $\mathrm{VCdim}(\mathcal H)=d$, $n\ge d$. With probability $\ge1-\delta$ over $S\sim\mathcal D^n$, simultaneously for all $h\in\mathcal H$,
$$L_{\mathcal D}(h)\le L_S(h)+\sqrt{\frac{8d\log(2en/d)+8\log(4/\delta)}{n}}.$$

*Proof sketch.* Vapnik–Chervonenkis' original route: for $n\varepsilon^2\ge2$,
$$P_S\Bigl(\sup_h|L_{\mathcal D}(h)-L_S(h)|>\varepsilon\Bigr)\le2P_{S,S'}\Bigl(\sup_h|L_{S'}(h)-L_S(h)|>\varepsilon/2\Bigr)\le2\tau_{\mathcal H}(2n)\cdot2e^{-n\varepsilon^2/8}=4\tau_{\mathcal H}(2n)e^{-n\varepsilon^2/8}.$$
The first inequality is the double-sample step done at the level of probabilities (Chebyshev on the ghost sample shows the ghost sample is on the right side with probability $\ge\tfrac12$); the second is the union bound over the $\le\tau_{\mathcal H}(2n)$ behaviours on $S\cup S'$ plus Hoeffding for the symmetrised difference. Bound $\tau_{\mathcal H}(2n)\le(2en/d)^d$, set equal to $\delta$ and solve for $\varepsilon$. ∎

This form (from Vapnik 1998 / Devroye–Györfi–Lugosi) is what one usually sees quoted; UML's Theorem 6.11 form has the $1/\delta$ or the additive McDiarmid term; [S10] Cor. 3.19 writes $\sqrt{\frac{2d\log(en/d)}{n}}+\sqrt{\frac{\log(1/\delta)}{2n}}$. **The constants ($8$, $2e$, $4/\delta$) vary between books; only the structure $\sqrt{(d\log(n/d)+\log(1/\delta))/n}$ is canonical.** Always say which form you use.

## Worked example

**Growth function of intervals.** Let $C=\{c_1<\dots<c_n\}$. Restricting $h_{a,b}$ to $C$ gives $1$ exactly on the points in $[a,b]$, which form a contiguous block $\{c_i,\dots,c_j\}$ ($i\le j$), or the empty set. Distinct blocks are distinct labellings, and every block is realised (take $a=c_i,b=c_j$). The number of nonempty blocks is the number of pairs $i\le j$, i.e. $\binom n2+n$; add the empty labelling:
$$\tau_{\mathcal H_{\mathrm{int}}}(n)=\binom n2+n+1=\frac{n^2+n+2}{2}.$$
Sauer with $d=2$: $\binom n0+\binom n1+\binom n2=1+n+\binom n2$. Identical: Sauer–Shelah is tight for intervals. Compare with $(en/2)^2$ and $2^n$:

| $n$ | $\tau_{\mathrm{int}}(n)$ | Sauer $\sum_{i\le2}\binom ni$ | $(en/2)^2$ | $2^n$ |
|---|---|---|---|---|
| 1 | 2 | 2 | 1.85 (not valid, $n<d$) | 2 |
| 2 | 4 | 4 | 7.4 | 4 |
| 3 | 7 | 7 | 16.6 | 8 |
| 4 | 11 | 11 | 29.6 | 16 |
| 5 | 16 | 16 | 46.2 | 32 |
| 6 | 22 | 22 | 66.5 | 64 |

For $n\le d=2$ the growth function is $2^n$ as it must be; from $n=3$ on it falls behind $2^n$ and is quadratic. For thresholds the same count gives $\tau_{\mathrm{thr}}(n)=n+1$ (Sauer with $d=1$: $1+n$, again tight).

**Numeric VC bound.** $d=3$, $n=10^4$, $\delta=0.05$, Theorem 4.12:
$$8d\log(2en/d)=24\log\Bigl(\frac{2e\cdot10^4}{3}\Bigr)=24\log(18122)=24\cdot9.805=235.3,\qquad8\log(4/\delta)=8\log80=35.1,$$
$$\sqrt{\frac{235.3+35.1}{10^4}}=\sqrt{0.02704}\approx0.164.$$
So $L_{\mathcal D}(h)\le L_S(h)+0.164$ for all $h$ simultaneously, with probability $0.95$. The same computation for $n=10^5$ gives $\sqrt{(290.6+35.1)/10^5}\approx0.057$, and for $n=10^6$ about $0.020$. The $\log(4/\delta)$ term is negligible next to the $d\log(2en/d)$ term; the bound scales as $\sqrt{d\log n/n}$. The FoML form gives $\sqrt{6\log(e\cdot10^4/3)/10^4}+\sqrt{\log20/(2\cdot10^4)}\approx0.073+0.012=0.085$ at $n=10^4$: same order, different constants.

**Halfspaces sanity check.** In $\mathbb R^2$ non-homogeneous halfspaces have $d=3$: three non-collinear points are shattered (all $8$ labellings by lines), four points are not (either one lies in the triangle of the other three, or they form a convex quadrilateral whose diagonal pairs cannot be separated: Radon partition). Realisable sample complexity by Theorem 4.11 is $O((3\log(1/\varepsilon)+\log(1/\delta))/\varepsilon)$.

## Pitfalls

- **VC dimension is not the number of parameters.** $\mathcal H_{\sin}$ has one parameter and infinite VC dimension; conversely a neural network's VC dimension is (up to logs) the number of weights only for specific activation functions. Finite unions of intervals (no fixed parameter count) also have infinite VC dimension.
- **Shattering one set vs all sets.** $\mathrm{VCdim}\ge d$ needs *one* shattered set of size $d$; $\mathrm{VCdim}<d+1$ needs *every* set of size $d+1$ to fail. A common error is to show a particular set of size $d+1$ is not shattered and conclude $\mathrm{VCdim}=d$ (e.g. three collinear points for halfspaces in $\mathbb R^2$ proves nothing).
- **VC dimension is a property of $\mathcal H$, not of the algorithm.** Two algorithms searching the same $\mathcal H$ get the same VC bound; the bound is about the worst hypothesis in $\mathcal H$, not the one the algorithm actually returns. Algorithm-dependent refinements (margins, stability, PAC-Bayes) are separate theories.
- **Sauer–Shelah is an upper bound**, tight for some classes (intervals, thresholds) and loose for others; the growth function itself, not $d$, enters Theorem 4.10.
- The VC bound is **distribution-free** and therefore pessimistic; real data often generalise far better. It is also vacuous for $n\lesssim d$ (bound $\ge1$).
- Fundamental theorem: the equivalence is for **binary** classification with **zero-one** loss. For real-valued or multiclass problems one needs fat-shattering / Natarajan dimension; learnability without uniform convergence is possible in some multiclass settings.
- Restriction vs projection: $\mathcal H_C$ counts *distinct labellings* of $C$, not hypotheses; many $h$ collapse to the same element of $\mathcal H_C$.
- In the sine example the shattered points are $2^{-i}$, i.e. specially chosen; that suffices for infinite VC dimension since only one shattered set of each size is required.

## Questions

**Q:** Define shattering, VC dimension, and the growth function.
**A:** $\mathcal H$ shatters $C$ if $\mathcal H_C=\{0,1\}^C$. $\mathrm{VCdim}(\mathcal H)$ is the largest $|C|$ that is shattered ($\infty$ if unbounded). $\tau_{\mathcal H}(n)=\max_{|C|=n}|\mathcal H_C|$; equals $2^n$ for $n\le d$.

**Q:** Prove that $\mathrm{VCdim}$ of non-homogeneous halfspaces in $\mathbb R^k$ is $k+1$.
**A:** Lower: $\{0,e_1,\dots,e_k\}$ shattered by $w=(s_1,\dots,s_k)$, $b=s_0/2$. Upper: any $k+2$ points admit a Radon partition $I\sqcup J$ with intersecting convex hulls; labelling $I$ positive and $J$ negative is impossible since both halfspace and complement are convex. Radon: the $k+1$ linear conditions $\sum\lambda_ix_i=0,\sum\lambda_i=0$ in $k+2$ unknowns have a nonzero solution; positive and negative parts give the partition.

**Q:** State and prove the Sauer–Shelah lemma.
**A:** $|\mathcal H_C|\le|\{B\subseteq C:\mathcal H\text{ shatters }B\}|\le\sum_{i\le d}\binom{|C|}{i}$. Induction on $|C|$: split $\mathcal H_C$ by the label of $c_1$ into $Y_0=\mathcal H_{C'}$ (patterns present with at least one $c_1$-label) and $Y_1=\mathcal H'_{C'}$ (patterns present with both), $|\mathcal H_C|=|Y_0|+|Y_1|$; IH bounds $|Y_0|$ by shattered subsets of $C'$ (not containing $c_1$) and $|Y_1|$ by shattered subsets $B$ of $C'$ for $\mathcal H'$, each of which extends to the shattered set $B\cup\{c_1\}$ (containing $c_1$). Add.

**Q:** Why is $\sum_{i\le d}\binom ni\le(en/d)^d$?
**A:** Multiply term $i$ by $(n/d)^{d-i}\ge1$, factor $(n/d)^d$, complete the binomial sum to $(1+d/n)^n\le e^d$.

**Q:** State the fundamental theorem of statistical learning with its sample complexity.
**A:** For binary classes with zero-one loss: uniform convergence, ERM agnostic-PAC, agnostic PAC, ERM PAC, PAC, and finite VC dimension are equivalent. $n_{\mathcal H}=\Theta((d+\log(1/\delta))/\varepsilon^2)$ agnostic; between $\Omega((d+\log(1/\delta))/\varepsilon)$ and $O((d\log(1/\varepsilon)+\log(1/\delta))/\varepsilon)$ realisable.

**Q:** Sketch why finite VC dimension implies uniform convergence.
**A:** Ghost sample: $\mathbb E\sup|L_{\mathcal D}-L_S|\le\mathbb E\sup|L_{S'}-L_S|$ (Jensen). Symmetrise with Rademacher signs (exchangeability of $z_i,z'_i$). On the fixed $2n$ points only $\tau_{\mathcal H}(2n)$ behaviours exist; Hoeffding + union bound (Massart) give $\mathbb E\max\le(4+\sqrt{\log\tau_{\mathcal H}(2n)})/\sqrt{2n}$. Sauer: $\log\tau_{\mathcal H}(2n)\le d\log(2en/d)$. McDiarmid turns expectation into high probability.

**Q:** Sketch why infinite VC dimension implies not PAC learnable.
**A:** For every $n$ there is a shattered set of size $2n$; all $2^{2n}$ labellings are realisable within $\mathcal H$; the No-Free-Lunch argument gives, for any learner, a realisable distribution with expected risk $\ge\tfrac14$ and risk $\ge\tfrac18$ with probability $\ge\tfrac17$; no finite sample complexity can exist.

**Q:** Give a class with one parameter and infinite VC dimension, and explain what this teaches.
**A:** $x\mapsto\mathbb 1[\sin(\omega x)\ge0]$ shatters $\{2^{-1},\dots,2^{-n}\}$ for every $n$ (choose $\omega/\pi$ from the binary expansion of the labelling). Parameter count does not measure capacity; the combinatorial richness of the function class does.

## Code

`src/py/vc.py`:
- `threshold_labelings(points)`, `interval_labelings(points)`, `rectangle_labelings(points)`, `halfspace_labelings(points)`: enumerate $\mathcal H_C$ for the standard classes (halfspaces via an LP feasibility check per labelling), i.e. compute the restriction of Definition 1.
- `is_shattered(labelings, points)`: tests $|\mathcal H_C|=2^{|C|}$.
- `growth_function(labelings, sampler, n, trials, rng)`: estimates $\tau_{\mathcal H}(n)$ by maximising $|\mathcal H_C|$ over random $C$; reproduces the interval table.
- `vc_dimension_estimate(labelings, sampler, max_d, trials, rng)`: searches for shattered sets of increasing size (finds $1,2,4,k+1$ for the four classes; note that a random search can only certify lower bounds).
- `sauer_bound(d, n)` and `verify_sauer`: evaluate $\sum_{i\le d}\binom ni$ and check $\tau_{\mathcal H}(n)\le$ Sauer bound empirically.
- `threshold_sup_deviation(problem, X, y)`: the exact $\sup_t|L_{\mathcal D}(h_t)-L_S(h_t)|$ over **all** thresholds (on each gap between sample points $L_S$ is constant and $L_{\mathcal D}$ convex, so the sup sits at an endpoint or at $\theta$).
- `uc_bound_expectation(tau_2n, n)`, `uc_bound_mcdiarmid(tau_2n, n, delta)`, `vc_bound_vapnik(d, n, delta)`: Theorem 4.10 (expectation and McDiarmid forms) and Theorem 4.12; `vc_bound_experiment(problem, n, trials, rng)` puts the empirical sup gap next to them (thresholds: $d=1$, $\tau(2n)=2n+1$). At $n=1000$ the 95 % quantile is $\approx0.04$ against bounds $0.19$ and $0.32$: correct, and loose by a factor 5 to 8.

`src/py/rademacher.py`: `massart_bound(n_hyps, n)`: the maximal inequality of Step 4 in Theorem 4.10 for $N$ fixed vectors; `rademacher_threshold(X, n_sigma, rng)`: empirical Rademacher complexity of thresholds, which by Step 3 is a maximum over $\tau(n)=n+1$ labellings.

## References

- V. N. Vapnik & A. Ya. Chervonenkis, "On the uniform convergence of relative frequencies of events to their probabilities", *Theory of Probability and its Applications* 16 (1971) (VC dimension, growth function, uniform convergence).
- N. Sauer, "On the density of families of sets", *J. Combinatorial Theory A* 13 (1972); S. Shelah, *Pacific J. Math.* 41 (1972).
- A. Blumer, A. Ehrenfeucht, D. Haussler, M. Warmuth, "Learnability and the Vapnik–Chervonenkis dimension", *JACM* 36 (1989) (finite VC ⇔ PAC learnable).
- Shalev-Shwartz & Ben-David, *UML* (2014): Ch. 6 (VC dimension, examples 6.3, Sauer Lemma 6.10, Thm 6.11, fundamental theorem 6.7/6.8), Ch. 9.1 (halfspaces VC dimension), Ch. 28 (proof of the fundamental theorem, lower bounds), Lemma A.2.
- Mohri, Rostamizadeh & Talwalkar, *FoML* (2018): Ch. 3.2 (growth function), 3.3 (VC dimension, Radon's theorem, Thm 3.13, Sauer's lemma 3.17, Cor. 3.18–3.19 VC bounds), 3.4 (lower bounds).
- Devroye, Györfi & Lugosi, *A Probabilistic Theory of Pattern Recognition* (1996): Ch. 12–13 (VC theory, the $4\tau(2n)e^{-n\varepsilon^2/8}$ bound).
- Vapnik, *Statistical Learning Theory* (1998): Ch. 4 (bounds on the risk).
