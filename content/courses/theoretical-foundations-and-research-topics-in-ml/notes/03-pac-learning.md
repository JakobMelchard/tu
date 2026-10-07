# 03 PAC learning

PAC ("probably approximately correct", Valiant 1984) is the formal definition of what it means for a hypothesis class to be *learnable*: a learner must, from a polynomial number of i.i.d. examples, output with probability at least $1-\delta$ a hypothesis with risk at most $\varepsilon$ (realisable) or at most $\varepsilon$ above the best in class (agnostic), for *every* data distribution. The bounds of note 02 say precisely that finite classes are PAC learnable with ERM. This note fixes the definitions, works two classic direct PAC proofs (conjunctions, rectangles), and proves the No-Free-Lunch theorem: without restricting $\mathcal H$ nothing is learnable, so inductive bias is a necessity, not a convenience. Note 04 characterises exactly which infinite classes are PAC learnable (finite VC dimension).

## Definitions

1. **Realisability assumption.** There exists $h^\star\in\mathcal H$ with $L_{\mathcal D}(h^\star)=0$. (Stronger than "labels are a deterministic function of $x$": the labelling function must lie in $\mathcal H$.)
2. **PAC learnability (realisable).** $\mathcal H$ is PAC learnable if there exist a function $n_{\mathcal H}:(0,1)^2\to\mathbb N$ and an algorithm $A$ such that for every $\varepsilon,\delta\in(0,1)$, every distribution $\mathcal D$ over $\mathcal X\times\mathcal Y$ satisfying realisability w.r.t. $\mathcal H$, and every $n\ge n_{\mathcal H}(\varepsilon,\delta)$:
   $$P_{S\sim\mathcal D^n}\bigl(L_{\mathcal D}(A(S))\le\varepsilon\bigr)\ge1-\delta.$$
   $\varepsilon$ is the accuracy parameter ("approximately correct"), $\delta$ the confidence parameter ("probably").
3. **Sample complexity.** The minimal such function, $n_{\mathcal H}(\varepsilon,\delta)=\min\{n:\text{the guarantee holds for all }n'\ge n\}$. Upper bounds come from exhibiting an algorithm; lower bounds from constructing hard distributions.
4. **Agnostic PAC learnability.** $\mathcal H$ is agnostic PAC learnable (w.r.t. loss $\ell$) if there exist $n_{\mathcal H}$ and $A$ such that for every $\varepsilon,\delta$, every $\mathcal D$ over $\mathcal X\times\mathcal Y$ (no realisability), and every $n\ge n_{\mathcal H}(\varepsilon,\delta)$:
   $$P_{S\sim\mathcal D^n}\Bigl(L_{\mathcal D}(A(S))\le\min_{h\in\mathcal H}L_{\mathcal D}(h)+\varepsilon\Bigr)\ge1-\delta.$$
   Agnostic PAC implies PAC (in the realisable case $\min_{\mathcal H}L_{\mathcal D}=0$).
5. **Efficient PAC learnability.** $\mathcal H=\bigcup_d\mathcal H_d$ is efficiently PAC learnable if $A$ runs in time polynomial in $1/\varepsilon$, $1/\delta$, the instance size $d$ (e.g. number of boolean variables, dimension) and the representation size of the target, while satisfying Definition 2 with $n_{\mathcal H_d}(\varepsilon,\delta)$ polynomial in the same quantities. Information-theoretic learnability (Definition 2) ignores computation; ERM can be NP-hard even when $\mathcal H$ is PAC learnable (e.g. $3$-term DNF, agnostic halfspaces).
6. **Proper vs improper learning.** Proper: $A(S)\in\mathcal H$ always. Improper (representation-independent): $A(S)$ may be any function, judged only by $L_{\mathcal D}$. Definitions 2 and 4 allow improper learners; ERM is proper.
7. **Consistent learner.** Returns $h\in\mathcal H$ with $L_S(h)=0$ (note 02, Def. 7). Meaningful only when such $h$ exists (realisable case).
8. **Boolean conjunctions.** $\mathcal X=\{0,1\}^d$; a literal is $x_i$ or $\bar x_i$; a conjunction is an AND of a subset of literals, $h(x)=1$ iff all its literals are satisfied. $\mathcal H^d_{\mathrm{con}}$ has $3^d$ elements (each variable appears positively, negatively, or not at all; conjunctions containing both $x_i$ and $\bar x_i$ are all the constant-$0$ function, so one may count $3^d+1$ with the empty-always-false conjunction; either way $\log|\mathcal H|=O(d)$).
9. **Axis-aligned rectangles.** $\mathcal X=\mathbb R^2$, $\mathcal H_{\mathrm{rect}}=\{h_{a_1,b_1,a_2,b_2}\}$ with $h(x)=+1$ iff $a_1\le x^{(1)}\le b_1$ and $a_2\le x^{(2)}\le b_2$. Infinite class.
10. **Tightest-fit learner for rectangles.** $A(S)$ = smallest axis-aligned rectangle containing all positive examples of $S$ (the empty rectangle if none).
11. **Labels.** In this note, $\mathcal Y=\{0,1\}$ for boolean classes and the NFL theorem (matching UML); $\{-1,+1\}$ elsewhere. Nothing depends on the choice.

## Results

**Theorem 3.1 (finite classes are PAC learnable)** [S9 Cor. 2.3, Cor. 4.6]**.** Let $|\mathcal H|<\infty$, $\ell\in[0,1]$. Then $\mathcal H$ is agnostic PAC learnable using ERM with
$$n_{\mathcal H}(\varepsilon,\delta)\le\Bigl\lceil\frac{2\log(2|\mathcal H|/\delta)}{\varepsilon^2}\Bigr\rceil,$$
and PAC learnable (realisable) using any consistent learner (in particular ERM) with
$$n_{\mathcal H}(\varepsilon,\delta)\le\Bigl\lceil\frac{\log(|\mathcal H|/\delta)}{\varepsilon}\Bigr\rceil.$$

*Proof.* Agnostic: Theorem 2.6 with $\varepsilon/2$ gives $\varepsilon/2$-representativeness with probability $\ge1-\delta$ for $n\ge\log(2|\mathcal H|/\delta)/(2(\varepsilon/2)^2)=2\log(2|\mathcal H|/\delta)/\varepsilon^2$; Lemma 2.5 then gives $L_{\mathcal D}(h_S)\le\min_{\mathcal H}L_{\mathcal D}+\varepsilon$. Realisable: Theorem 2.7 verbatim. ∎

ERM is thus a *universal* learner for finite classes: one algorithm, no knowledge of $\mathcal D$, works for every finite $\mathcal H$ with sample complexity logarithmic in $|\mathcal H|$. Enumerating $\mathcal H$ may be exponentially slow, which is where efficiency enters.

**Theorem 3.2 (conjunctions are efficiently PAC learnable)** [S9 §8.2.3; S10 §2.1]**.** $\mathcal H^d_{\mathrm{con}}$ is PAC learnable with
$$n(\varepsilon,\delta)\le\frac{d\log3+\log(1/\delta)}{\varepsilon}=O\Bigl(\frac{d+\log(1/\delta)}{\varepsilon}\Bigr),$$
by the following consistent learner running in time $O(nd)$:
1. Start with $h=x_1\wedge\bar x_1\wedge\dots\wedge x_d\wedge\bar x_d$ (all $2d$ literals).
2. For every positive example $(x,1)\in S$ and every $i$: if $x_i=1$ delete $\bar x_i$ from $h$; if $x_i=0$ delete $x_i$ from $h$.
3. Output $h$.

*Proof.* Let $c\in\mathcal H^d_{\mathrm{con}}$ be the target. (Consistency on positives.) After step 2, every literal remaining in $h$ is satisfied by every positive example, so $h(x)=1$ on all positives. (Consistency on negatives.) A literal of $c$ is satisfied by every positive example (since $c(x)=1$), hence is never deleted: the literal set of $h$ contains that of $c$, so $h\le c$ pointwise. On a negative example $c(x)=0$, hence $h(x)=0$. So $h$ is consistent; it lies in $\mathcal H^d_{\mathrm{con}}$. Theorem 3.1 (realisable) with $|\mathcal H|\le3^d+1$ gives the sample bound; the running time is $n$ passes over $2d$ literals. ∎

**Theorem 3.3 (axis-aligned rectangles, direct PAC proof)** [S10 §2.1; S18]**.** $\mathcal H_{\mathrm{rect}}$ is PAC learnable by the tightest-fit learner with
$$n(\varepsilon,\delta)\ge\frac4\varepsilon\log\frac4\delta\quad\Longrightarrow\quad P_S\bigl(L_{\mathcal D}(A(S))\le\varepsilon\bigr)\ge1-\delta,$$
for every distribution $\mathcal D_{\mathcal X}$ on $\mathbb R^2$ and every target rectangle $R\in\mathcal H_{\mathrm{rect}}$.

*Proof.* Let $R=[a_1,b_1]\times[a_2,b_2]$ be the target and $R_S=A(S)$. Since all positive examples lie in $R$, $R_S\subseteq R$, so $A(S)$ makes no false positives and the error region is $R\setminus R_S$: $L_{\mathcal D}(A(S))=\mathcal D_{\mathcal X}(R\setminus R_S)$.

If $\mathcal D_{\mathcal X}(R)\le\varepsilon$ the error is trivially $\le\varepsilon$. Otherwise define four strips inside $R$ along its sides, each of probability mass exactly $\varepsilon/4$ (assume $\mathcal D_{\mathcal X}$ has a density for exactness; in general take the smallest strip with mass $\ge\varepsilon/4$, whose interior has mass $\le\varepsilon/4$, and the argument goes through with the interior):
$$T_1=[a_1,a_1']\times[a_2,b_2]\ \text{with }a_1'=\inf\{a:\mathcal D_{\mathcal X}([a_1,a]\times[a_2,b_2])\ge\varepsilon/4\},$$
and similarly $T_2$ (right), $T_3$ (bottom), $T_4$ (top).

Claim: if $S$ contains a positive example in each $T_i$, then $R\setminus R_S\subseteq T_1\cup T_2\cup T_3\cup T_4$. Indeed, a positive point in $T_1$ forces the left edge of $R_S$ to be $\le a_1'$; similarly for the other three sides; so $R_S\supseteq[a_1',b_1']\times[a_2',b_2']=R\setminus(T_1\cup\dots\cup T_4)$. Then $L_{\mathcal D}(A(S))\le\sum_i\mathcal D_{\mathcal X}(T_i)=\varepsilon$.

Failure therefore requires that some $T_i$ contains no sample point. For fixed $i$, each of the $n$ i.i.d. draws misses $T_i$ with probability $1-\varepsilon/4$, so
$$P_S(S\cap T_i=\emptyset)=(1-\varepsilon/4)^n\le e^{-n\varepsilon/4}.$$
Union bound over $i=1,\dots,4$: $P_S(L_{\mathcal D}(A(S))>\varepsilon)\le4e^{-n\varepsilon/4}\le\delta$ iff $n\ge\frac4\varepsilon\log\frac4\delta$. ∎

The same argument in $\mathbb R^k$ gives $2k$ strips of mass $\varepsilon/(2k)$ and $n\ge\frac{2k}{\varepsilon}\log\frac{2k}\delta$. This is the prototype of the VC bound $O((d\log(1/\varepsilon)+\log(1/\delta))/\varepsilon)$ with $d=2k$ (note 04, $\mathrm{VCdim}=2k$).

**Theorem 3.4 (No-Free-Lunch)** [S9 Thm 5.1]**.** Let $A$ be any learning algorithm for binary classification with $\ell_{0\text{-}1}$ over a domain $\mathcal X$, and let $n\le|\mathcal X|/2$. Then there exists a distribution $\mathcal D$ over $\mathcal X\times\{0,1\}$ such that
1. there is a function $f:\mathcal X\to\{0,1\}$ with $L_{\mathcal D}(f)=0$ (the problem is realisable by *some* function), and
2. $\mathbb E_{S\sim\mathcal D^n}L_{\mathcal D}(A(S))\ge\tfrac14$, hence with probability at least $\tfrac17$ over $S$, $L_{\mathcal D}(A(S))\ge\tfrac18$.

*Proof sketch.* Fix $C\subseteq\mathcal X$ with $|C|=2n$. There are $T=2^{2n}$ functions $f_1,\dots,f_T:C\to\{0,1\}$. For each $f_i$ let $\mathcal D_i$ be uniform on $C$ with labels $y=f_i(x)$; then $L_{\mathcal D_i}(f_i)=0$, which is (1). It suffices to show
$$\max_{i\le T}\ \mathbb E_{S\sim\mathcal D_i^n}L_{\mathcal D_i}(A(S))\ \ge\ \tfrac14.\tag{$\dagger$}$$

*Step 1 (enumerate samples).* There are $k=(2n)^n$ sequences $S_1,\dots,S_k$ of $n$ points from $C$ (with repetition). Let $S_j^i$ denote $S_j$ labelled by $f_i$. Since $\mathcal D_i$ is uniform on $C$,
$$\mathbb E_{S\sim\mathcal D_i^n}L_{\mathcal D_i}(A(S))=\frac1k\sum_{j=1}^kL_{\mathcal D_i}(A(S_j^i)).$$

*Step 2 (max ≥ average ≥ min).*
$$\max_i\frac1k\sum_jL_{\mathcal D_i}(A(S_j^i))\ \ge\ \frac1T\sum_i\frac1k\sum_jL_{\mathcal D_i}(A(S_j^i))\ =\ \frac1k\sum_j\frac1T\sum_iL_{\mathcal D_i}(A(S_j^i))\ \ge\ \min_j\frac1T\sum_iL_{\mathcal D_i}(A(S_j^i)).$$

*Step 3 (the unseen half).* Fix $j$. $S_j$ contains at most $n$ distinct points, so at least $p\ge n$ points $v_1,\dots,v_p$ of $C$ are *not* in $S_j$. For any $h$, since $\mathcal D_i$ is uniform on $C$ and $p\ge n=|C|/2$,
$$L_{\mathcal D_i}(h)=\frac1{2n}\sum_{x\in C}\mathbb 1[h(x)\neq f_i(x)]\ \ge\ \frac1{2n}\sum_{r=1}^p\mathbb 1[h(v_r)\neq f_i(v_r)]\ \ge\ \frac1{2p}\sum_{r=1}^p\mathbb 1[h(v_r)\neq f_i(v_r)].$$
Hence
$$\frac1T\sum_iL_{\mathcal D_i}(A(S_j^i))\ \ge\ \frac1{2p}\sum_{r=1}^p\ \frac1T\sum_i\mathbb 1[A(S_j^i)(v_r)\neq f_i(v_r)].$$

*Step 4 (pairing).* Fix $r$. Partition $\{f_1,\dots,f_T\}$ into $T/2$ pairs $(f_i,f_{i'})$ that agree on $C\setminus\{v_r\}$ and differ at $v_r$. Because $v_r\notin S_j$, the labelled samples coincide: $S_j^i=S_j^{i'}$, so $A(S_j^i)=A(S_j^{i'})=:h$. Exactly one of $h(v_r)\neq f_i(v_r)$, $h(v_r)\neq f_{i'}(v_r)$ holds. Thus $\mathbb 1[\cdot]$ averages to exactly $\tfrac12$ over each pair, and $\frac1T\sum_i\mathbb 1[A(S_j^i)(v_r)\neq f_i(v_r)]=\tfrac12$.

*Step 5 (assemble).* Plugging into Step 3: $\frac1T\sum_iL_{\mathcal D_i}(A(S_j^i))\ge\frac1{2p}\cdot p\cdot\frac12=\frac14$ for every $j$; by Step 2, $(\dagger)$ holds. Pick $\mathcal D=\mathcal D_{i^\star}$ attaining the max.

*Step 6 (from expectation to probability).* Let $Z=L_{\mathcal D}(A(S))\in[0,1]$ with $\mathbb EZ\ge\tfrac14$. Reverse Markov: for $a\in(0,1)$, $\mathbb EZ\le a\,P(Z<a)+1\cdot P(Z\ge a)\le a+(1-a)P(Z\ge a)$, so
$$P(Z\ge a)\ge\frac{\mathbb EZ-a}{1-a}\ \ \Rightarrow\ \ P\bigl(Z\ge\tfrac18\bigr)\ge\frac{1/4-1/8}{7/8}=\frac17.\qquad ∎$$

**Corollary 3.5 (all functions on an infinite domain are not PAC learnable)** [S9 Cor. 5.2]**.** Let $\mathcal X$ be infinite and $\mathcal H=\{0,1\}^{\mathcal X}$ the class of all functions. Then $\mathcal H$ is not PAC learnable.

*Proof.* Suppose it were, with algorithm $A$ and sample complexity $n_{\mathcal H}$. Take $\varepsilon=\tfrac18$, $\delta=\tfrac17$ (any $\varepsilon<\tfrac18$, $\delta<\tfrac17$ works), $n=n_{\mathcal H}(\varepsilon,\delta)$. Since $\mathcal X$ is infinite, $n\le|\mathcal X|/2$, so Theorem 3.4 gives a distribution $\mathcal D$, realisable by some $f\in\mathcal H$ (every function is in $\mathcal H$), with $P_S(L_{\mathcal D}(A(S))\ge\tfrac18)\ge\tfrac17$. The PAC guarantee demands $P_S(L_{\mathcal D}(A(S))>\varepsilon)\le\delta$; with $\varepsilon<\tfrac18$ and $\delta<\tfrac17$ this is violated. ∎

The same argument shows any $\mathcal H$ that shatters arbitrarily large sets (note 04) is not PAC learnable: replace "all functions on $C$" by "all functions on $C$ realised by $\mathcal H$".

**Consequence.** A learner that makes no assumption (uses $\mathcal H$ = all functions, or equivalently is willing to output anything) fails on some realisable task no matter how much data it sees (as long as $n\le|\mathcal X|/2$, i.e. always for infinite $\mathcal X$). Every successful learner encodes *prior knowledge* in the form of a restricted $\mathcal H$ (or a preference over hypotheses), and this knowledge is what allows it to say anything about the unseen half of $C$. The trade-off is Definition 12 of note 01: a small $\mathcal H$ has small estimation error but may have large approximation error. Choosing $\mathcal H$ well is the practitioner's contribution; the theory tells how large $\mathcal H$ can be for a given $n$.

## Worked example

**Conjunctions, $d=10$, $\varepsilon=0.1$, $\delta=0.05$.** $|\mathcal H|=3^{10}=59049$, so
$$n\ge\frac{\log(59049/0.05)}{0.1}=\frac{\log 1180980}{0.1}=\frac{13.98}{0.1}\approx140.$$
Compare with the $2^{2^{10}}=2^{1024}$ boolean functions on $\{0,1\}^{10}$: learning "any function" would need $\log(2^{1024}/\delta)/\varepsilon\approx7100$ examples, and in fact by Theorem 3.4 with $|\mathcal X|=1024$ no learner does better than $\tfrac14$ expected error from $512$ examples without a restricted class.

Run of the learner on $d=3$, target $c=x_1\wedge\bar x_3$: start $h=x_1\bar x_1x_2\bar x_2x_3\bar x_3$. Positive example $(1,1,0)$: delete $\bar x_1,\bar x_2,x_3$, leaving $h=x_1x_2\bar x_3$. Positive example $(1,0,0)$: delete $x_2$, leaving $h=x_1\bar x_3=c$. A negative example $(0,1,0)$ changes nothing and is correctly classified $0$.

**Rectangles, $\varepsilon=0.1$, $\delta=0.05$.** $n\ge\frac4{0.1}\log\frac4{0.05}=40\cdot\log80=40\cdot4.382\approx175.3$, so $n=176$. With $\varepsilon=0.01$: $n\ge400\cdot4.382\approx1753$; the $1/\varepsilon$ scaling, no $\log(1/\varepsilon)$ term, because the direct proof exploits the tightest-fit structure. The generic VC bound of note 04 with $d=4$ carries an extra $\log(1/\varepsilon)$ factor.

**No-Free-Lunch numbers.** $|\mathcal X|=100$, $n=50$, $C=\mathcal X$: $T=2^{100}$ labellings, $k=100^{50}$ samples; the theorem says some labelling forces expected error $\ge\tfrac14$ for the specific $A$ (a different labelling for each $A$). Intuition: $A$ sees at most $50$ of the $100$ points; on the other $\ge50$ it must guess, and a uniformly random labelling makes every guess a coin flip, giving error $\ge\tfrac12\cdot\tfrac12$ on average. With $n=49$ vs $n=50$ nothing changes; with $n\ge|\mathcal X|$ the theorem no longer applies, and indeed memorisation then works on a finite domain.

**Reverse Markov check.** $Z\in[0,1]$ with $\mathbb EZ=\tfrac14$. The extremal distribution for $P(Z\ge\tfrac18)\ge\tfrac17$ puts mass $\tfrac67$ just below $\tfrac18$ (contributing at most $\tfrac18\cdot\tfrac67=\tfrac3{28}$ to the mean) and mass $\tfrac17$ at $1$ (contributing $\tfrac4{28}$): total mean $\tfrac14$, and $P(Z\ge\tfrac18)=\tfrac17$ exactly. So the step from $\mathbb EZ\ge\tfrac14$ to $P(Z\ge\tfrac18)\ge\tfrac17$ cannot be improved; the constants $\tfrac18,\tfrac17$ themselves are conventional choices.

## Pitfalls

- PAC is **distribution-free but class-dependent**: the guarantee holds for *every* $\mathcal D$, but only relative to the chosen $\mathcal H$ (realisability w.r.t. $\mathcal H$, or excess risk over $\min_{\mathcal H}L_{\mathcal D}$). "Learnable" is a property of $\mathcal H$, not of a task.
- Roles of $\varepsilon$ and $\delta$: $\varepsilon$ bounds the *risk* of the output (a property of one hypothesis), $\delta$ bounds the *probability over samples* that the risk bound fails. Sample complexity is polynomial in $1/\varepsilon$ but only logarithmic in $1/\delta$; the two are not interchangeable.
- The NFL theorem does not say "all algorithms are equally good"; it says for each algorithm there is a *bad distribution*. Two algorithms differ on which distributions they fail on. A learner with a good inductive bias for the actual $\mathcal D$ wins.
- The NFL bad distribution is realisable by *some* $f$, but not by a hypothesis of any fixed small $\mathcal H$: it does not contradict learnability of finite or finite-VC classes.
- "Consistent" and "ERM" coincide only in the realisable case. In the agnostic case no hypothesis has $L_S=0$; ERM minimises $L_S$, and its guarantee requires uniform convergence, not just consistency.
- Sample complexity $n_{\mathcal H}$ is the minimal $n$ such that the guarantee holds for **all** $n'\ge n$; upper bounds from proofs are not the true sample complexity.
- Efficient PAC learnability is about computation; a class can be PAC learnable (small $\log|\mathcal H|$ or VC dimension) yet have NP-hard ERM. Improper learners can sometimes circumvent this ($3$-term DNF via $3$-CNF).
- The rectangle proof needs $n$ positive examples to hit the strips; if $\mathcal D_{\mathcal X}(R)\le\varepsilon$ the learner may see no positives and output the empty rectangle, which is still $\varepsilon$-good. Both cases must be treated.

## Questions

**Q:** Define PAC learnability and agnostic PAC learnability. What are the quantifiers?
**A:** $\mathcal H$ is PAC learnable if $\exists A,n_{\mathcal H}$ such that $\forall\varepsilon,\delta\in(0,1)$, $\forall\mathcal D$ realisable by $\mathcal H$, $\forall n\ge n_{\mathcal H}(\varepsilon,\delta)$: $P_S(L_{\mathcal D}(A(S))\le\varepsilon)\ge1-\delta$. Agnostic: drop realisability, replace $\varepsilon$ by $\min_{\mathcal H}L_{\mathcal D}+\varepsilon$. Order: algorithm and sample complexity are chosen before $\mathcal D$; $\mathcal D$ is adversarial.

**Q:** Show that every finite class is agnostic PAC learnable and give the sample complexity.
**A:** ERM. Hoeffding + union bound give $\varepsilon/2$-representativeness w.p. $\ge1-\delta$ for $n\ge2\log(2|\mathcal H|/\delta)/\varepsilon^2$; representativeness implies ERM is $\varepsilon$-good. Realisable: $\log(|\mathcal H|/\delta)/\varepsilon$ via $(1-\varepsilon)^n\le e^{-\varepsilon n}$.

**Q:** Give an efficient PAC learner for conjunctions and prove it is consistent.
**A:** Start with all $2d$ literals, delete every literal falsified by some positive example. Positives satisfy all remaining literals; the target's literals are never deleted so $h\le c$ and negatives are classified $0$. $|\mathcal H|=3^d$ gives $n=(d\log3+\log(1/\delta))/\varepsilon$; time $O(nd)$.

**Q:** Prove directly that axis-aligned rectangles are PAC learnable.
**A:** Tightest fit $R_S\subseteq R$; error $=\mathcal D(R\setminus R_S)$. Four strips of mass $\varepsilon/4$ along the sides of $R$; if each contains a sample point the error is $\le\varepsilon$; a strip is missed w.p. $(1-\varepsilon/4)^n\le e^{-n\varepsilon/4}$; union bound over $4$ strips; $n\ge(4/\varepsilon)\log(4/\delta)$.

**Q:** State the No-Free-Lunch theorem and sketch the proof.
**A:** For any $A$ and $n\le|\mathcal X|/2$ there is a realisable $\mathcal D$ with $\mathbb E_SL_{\mathcal D}(A(S))\ge\tfrac14$, hence $P(L\ge\tfrac18)\ge\tfrac17$. Proof: take $C$ of size $2n$, all $2^{2n}$ labellings, uniform marginal; max over labellings $\ge$ average; for a fixed unlabelled sample at least half of $C$ is unseen; pairing labellings that differ only at an unseen point shows $A$ errs on it w.p. exactly $\tfrac12$; so average error $\ge\tfrac12\cdot\tfrac12$; reverse Markov converts $\mathbb EZ\ge\tfrac14$ to $P(Z\ge\tfrac18)\ge\tfrac17$.

**Q:** Why is the class of all functions on an infinite domain not PAC learnable, and what does this imply?
**A:** For any claimed $n_{\mathcal H}(\tfrac18,\tfrac17)$ the NFL theorem (applicable since $|\mathcal X|=\infty\ge2n$) produces a realisable $\mathcal D$ on which the learner has risk $\ge\tfrac18$ w.p. $\ge\tfrac17$. Hence prior knowledge restricting $\mathcal H$ is necessary for learning: inductive bias is unavoidable.

**Q:** What is the difference between PAC learnability and efficient PAC learnability?
**A:** PAC: polynomial *sample* complexity in $1/\varepsilon,1/\delta$ (information-theoretic). Efficient: additionally polynomial *running time* in $1/\varepsilon,1/\delta$, instance size and target size. Finite/finite-VC classes are always PAC learnable via ERM, but ERM may be computationally hard.

**Q:** Is PAC learnability a property of the algorithm, the distribution, or the class?
**A:** Of the class $\mathcal H$ (and loss). The definition quantifies over all distributions and asks for the existence of some algorithm. A specific algorithm may or may not achieve the sample complexity; ERM does for finite and finite-VC classes.

## Code

`src/py/pac.py`:
- `sample_complexity_finite`: the two bounds of Theorem 3.1 (same as in `concentration.py`).
- `sample_complexity_vc(d, eps, delta, realisable)`: the VC-based bounds of note 04, for comparison with the direct rectangle bound.
- `consistent_threshold_learner(X, y)`: a consistent learner for the realisable threshold class (returns any threshold separating the sample), the one-dimensional analogue of tightest fit.
- `estimate_failure_probability(problem, learner, n, eps, trials, rng)`: Monte-Carlo estimate of $P_S(L_{\mathcal D}(A(S))>\varepsilon)$, the quantity PAC bounds by $\delta$; use it to see how conservative $n_{\mathcal H}(\varepsilon,\delta)$ is.
- `max_negative_threshold_learner(X, y)`, `threshold_failure_exact(eps, n, theta)`: the consistent learner returning the largest negative point fails iff no sample lands in $[\theta-\varepsilon,\theta]$, so $P(\text{fail})=(1-\varepsilon)^n\le e^{-\varepsilon n}$ exactly; the demo checks it over 20 000 resamples per $n$.
- `pac_demo`: runs the above for increasing $n$ and prints the estimated failure probability against the theoretical $\delta$.

## References

- L. G. Valiant, "A theory of the learnable", *Communications of the ACM* 27(11), 1984 (original PAC definition, conjunctions).
- Shalev-Shwartz & Ben-David, *UML* (2014): Ch. 3 (PAC and agnostic PAC definitions, Cor. 3.2 finite classes, Cor. 4.6), Ch. 5 (No-Free-Lunch Thm 5.1, Cor. 5.2, bias-complexity trade-off), Ch. 8 (computational complexity of learning, efficient PAC).
- Mohri, Rostamizadeh & Talwalkar, *FoML* (2018): Ch. 2.1 (PAC model, axis-aligned rectangles Ex. 2.4), Ch. 2.2 (consistent case), Ch. 2.3 (inconsistent case), Ch. 2.4 (deterministic vs stochastic scenarios, Bayes error).
- Kearns & Vazirani, *An Introduction to Computational Learning Theory* (1994): Ch. 1 (rectangles, conjunctions, efficient PAC).
- D. Wolpert, "The lack of a priori distinctions between learning algorithms", *Neural Computation* 8 (1996) (original No-Free-Lunch results).
