# 03 Entropy of quantum states (TISS 1.3)

TISS 1.3: "Shannon & von Neumann entropy, properties, entropy of bipartite systems, subadditivity, Araki-Lieb inequality, concavity, relative entropy" [S2]. Everything below follows from **one** inequality, Klein's ($D\ge0$), plus purification; that chain is the natural 30-minute board talk. Sources: Preskill 1998 §5.2.1 [S5] and ch. 10 §10.2-10.2.3 [S9]; Wilde ch. 11 [S11] (Klein = Thm 11.8.2, subadditivity = Cor. 11.8.1, Araki-Lieb = Ex. 11.7.10, concavity = Property 11.1.4, SSA = Thm 11.7.1 / Cor. 11.9.1); Nielsen & Chuang §11.1-11.3 [S13]; Bertlmann & Friis ch. 19-20 [S14]; primary: Klein 1931 [S43], Araki-Lieb 1970 [S41], Lieb-Ruskai 1973 [S42]. Logs base 2 throughout.

## Definitions

- **Shannon entropy** $H(p)=-\sum_xp(x)\log p(x)$ ($0\log0=0$); $0\le H\le\log|X|$.
- **Von Neumann entropy** $S(\rho)=-\operatorname{tr}\rho\log\rho=H(\lambda(\rho))$, the Shannon entropy of the spectrum. Write $S(A)=S(\rho_A)$, $S(AB)=S(\rho_{AB})$.
- **Relative entropy** $D(\rho\|\sigma)=\operatorname{tr}\rho(\log\rho-\log\sigma)$ if $\operatorname{supp}\rho\subseteq\operatorname{supp}\sigma$, else $+\infty$.
- **Conditional entropy** $S(A|B)=S(AB)-S(B)$; **mutual information** $I(A:B)=S(A)+S(B)-S(AB)$; **conditional mutual information** $I(A:C|B)=S(AB)+S(BC)-S(B)-S(ABC)$.

## Basic properties

(P1) $0\le S(\rho)\le\log d$; $S=0$ iff pure, $S=\log d$ iff $\rho=I/d$. (P2) $S(U\rho U^\dagger)=S(\rho)$. (P3) Additivity $S(\rho\otimes\sigma)=S(\rho)+S(\sigma)$ (eigenvalues multiply, logs add). (P4) **Pure bipartite:** $S(A)=S(B)$, since $\rho_A,\rho_B$ share the nonzero spectrum (Schmidt, [04](04-schmidt-decomposition-and-purification.md)). (P5) **cq-states:** $S\big(\sum_ip_i\rho_i\otimes|i\rangle\langle i|\big)=H(p)+\sum_ip_iS(\rho_i)$ (block diagonal, eigenvalues $p_i\lambda^{(i)}_k$).

## Theorems with proofs

**Thm 3.1 (Klein's inequality).** $D(\rho\|\sigma)\ge0$, with equality iff $\rho=\sigma$.
*Proof.* $\rho=\sum_ip_i|i\rangle\langle i|$, $\sigma=\sum_jq_j|j\rangle\langle j|$, $P_{ij}=|\langle i|j\rangle|^2$ (doubly stochastic). Then
$$D=\sum_ip_i\log p_i-\sum_ip_i\sum_jP_{ij}\log q_j\ \ge\ \sum_ip_i\log p_i-\sum_ip_i\log r_i,\qquad r_i=\sum_jP_{ij}q_j,$$
by concavity of $\log$ ($\sum_jP_{ij}\log q_j\le\log\sum_jP_{ij}q_j$). The right side is the classical $D(p\|r)$, and $-D(p\|r)=\sum_ip_i\log\frac{r_i}{p_i}\le\frac1{\ln2}\sum_ip_i(\frac{r_i}{p_i}-1)\le0$ since $\sum_ir_i=1$ ($\ln x\le x-1$). Equality forces $r=p$ and equality in the concavity step, i.e. $P$ a permutation on the relevant eigenvalues, whence $\rho=\sigma$. $\square$

**Cor. 3.2 (maximum entropy).** $D(\rho\|I/d)=\log d-S(\rho)\ge0$. **Dephasing increases entropy:** for $\Delta(\rho)=\sum_kP_k\rho P_k$ (projective measurement without reading the result), $D(\rho\|\Delta\rho)=S(\Delta\rho)-S(\rho)\ge0$, because $\operatorname{tr}\rho\log\Delta\rho=\operatorname{tr}\Delta(\rho)\log\Delta\rho$ ($\log\Delta\rho$ is block diagonal).

**Thm 3.3 (subadditivity).** $S(AB)\le S(A)+S(B)$, equality iff $\rho_{AB}=\rho_A\otimes\rho_B$.
*Proof.* $\log(\rho_A\otimes\rho_B)=\log\rho_A\otimes I+I\otimes\log\rho_B$, so $\operatorname{tr}\rho_{AB}\log(\rho_A\otimes\rho_B)=-S(A)-S(B)$ and
$$I(A:B)=S(A)+S(B)-S(AB)=D(\rho_{AB}\|\rho_A\otimes\rho_B)\ge0$$
by Klein, with equality iff product. $\square$

**Thm 3.4 (Araki-Lieb triangle inequality).** $S(AB)\ge|S(A)-S(B)|$.
*Proof.* Purify $\rho_{AB}$ to $|\psi\rangle_{ABC}$. By (P4) $S(AB)=S(C)$, $S(A)=S(BC)$. Subadditivity on $BC$: $S(A)=S(BC)\le S(B)+S(C)=S(B)+S(AB)$, so $S(AB)\ge S(A)-S(B)$; swap $A\leftrightarrow B$. $\square$ Equality for pure $\rho_{AB}$ ($0=|S(A)-S(B)|$ by (P4)). Contrast classical $H(XY)\ge\max(H(X),H(Y))$: quantum joint entropy can be *smaller* than a marginal.

**Thm 3.5 (concavity).** $S(\sum_ip_i\rho_i)\ge\sum_ip_iS(\rho_i)$.
*Proof.* $\rho_{AB}=\sum_ip_i\rho_i\otimes|i\rangle\langle i|$. By (P5) $S(AB)=H(p)+\sum p_iS(\rho_i)$, $S(B)=H(p)$, $S(A)=S(\sum p_i\rho_i)$. Subadditivity $S(AB)\le S(A)+S(B)$ gives the claim. $\square$ Mixing never lowers entropy; together with (P1) this makes $S$ the natural "mixedness".

**Thm 3.6 (upper bound on mixing).** $S(\sum_ip_i\rho_i)\le H(p)+\sum_ip_iS(\rho_i)$, equality iff the $\rho_i$ have orthogonal supports.
*Proof for pure $\rho_i=|\psi_i\rangle\langle\psi_i|$.* $|\Psi\rangle=\sum_i\sqrt{p_i}|\psi_i\rangle|i\rangle$ has $\rho_A=\sum p_i\rho_i$ and $S(A)=S(B)$. $\rho_B$ has diagonal $p_i$ in the $|i\rangle$ basis, so by Cor. 3.2 (dephasing) $S(B)\le H(p)$. General case: spectral-decompose each $\rho_i$ and use concavity of $H$ [S13 §11.3]. $\square$

**Thm 3.7 (strong subadditivity, Lieb-Ruskai [S42]).** $I(A:C|B)\ge0$, i.e. $S(ABC)+S(B)\le S(AB)+S(BC)$. Proof is hard (Lieb concavity); state it, know the equivalent forms: conditioning reduces entropy $S(A|BC)\le S(A|B)$; monotonicity of relative entropy under partial trace, $D(\rho_{AB}\|\sigma_{AB})\ge D(\rho_A\|\sigma_A)$, and in general under any channel (data processing) [S11 Thm 11.8.1, 11.9.2]. SSA $\Rightarrow$ subadditivity (trivial $B$).

**Conditional entropy can be negative.** $|\Phi^+\rangle$: $S(AB)=0$, $S(B)=1$, $S(A|B)=-1$, $I(A:B)=2$. For separable states $S(A|B)\ge0$, so $S(A|B)<0$ certifies entanglement (converse false). Bounds: $-\log d_A\le S(A|B)\le\log d_A$; $0\le I(A:B)\le2\min(\log d_A,\log d_B)$, the factor 2 reached only by entanglement (classical $I\le\min H$).

**Relative entropy, further properties.** Not symmetric, no triangle inequality, not a metric; jointly convex; unitarily invariant; additive on tensor products. Operational meaning: optimal error exponent for distinguishing $\rho^{\otimes n}$ from $\sigma^{\otimes n}$ (quantum Stein) [S9 §10.1.4]. Link to distances: quantum Pinsker $D(\rho\|\sigma)\ge\frac{2}{\ln2}T(\rho,\sigma)^2$ [S11 Thm 11.9.1], see [05](05-hilbert-space-geometry.md).

## Worked example

| state | $S(AB)$ | $S(A)=S(B)$ | $S(A\vert B)$ | $I(A:B)$ |
|---|---|---|---|---|
| $\lvert\Phi^+\rangle$ | 0 | 1 | $-1$ | 2 |
| $\tfrac12(\lvert00\rangle\langle00\rvert+\lvert11\rangle\langle11\rvert)$ | 1 | 1 | 0 | 1 |
| $I/4$ | 2 | 1 | 1 | 0 |
| Werner $p=0.6$ | 1.357 | 1 | 0.357 | 0.643 |

Werner $p\,|\Psi^-\rangle\langle\Psi^-|+(1-p)I/4$: eigenvalues $\tfrac{1+3p}4$ and $\tfrac{1-p}4$ (three times); at $p=0.6$ $I(A:B)=0.643$ (demo of `entanglement.py`). It is entangled (PPT fails, [10](10-entanglement.md)) yet $S(A|B)>0$: negative conditional entropy is sufficient, not necessary.

## Pitfalls

- $S(A|B)$ is not an entropy of a "conditional state"; there is none. It can be negative, which is exactly what state merging interprets [S9 §10.8.2].
- $D(\rho\|\sigma)=\infty$ when $\sigma$ has a kernel that $\rho$ sees; `relative_entropy` returns `inf`.
- Concavity is of $S$ in $\rho$; relative entropy is jointly *convex*. Do not mix the directions.
- Araki-Lieb is a *lower* bound on $S(AB)$; subadditivity the *upper* bound. Together: $|S(A)-S(B)|\le S(AB)\le S(A)+S(B)$.
- Linear entropy (note [01](01-states-and-operators.md)) orders states differently from $S$; do not use it for mutual-information arguments.

## Oral-exam questions (model answers)

1. *Prove Klein's inequality.* Thm 3.1: eigenbases, doubly stochastic overlaps, concavity of $\log$, then $\ln x\le x-1$.
2. *Prove subadditivity and state when it is tight.* $I(A:B)=D(\rho_{AB}\|\rho_A\otimes\rho_B)\ge0$; tight iff product.
3. *Prove Araki-Lieb and explain why it has no classical counterpart in that form.* Purify, $S(AB)=S(C)$, $S(A)=S(BC)$, subadditivity on $BC$. Classically $H(XY)\ge H(X)$; quantumly $S(AB)=0<S(A)$ for Bell states.
4. *Prove concavity of the von Neumann entropy.* cq-state flag, (P5), subadditivity.
5. *What is strong subadditivity; give two equivalent forms and a consequence.* $I(A:C|B)\ge0$; conditioning reduces entropy; monotonicity of $D$ under partial trace/channels; implies subadditivity and data processing of $I(A:B)$.

## Code

`src/py/entropies.py`: `shannon`, `von_neumann`, `relative_entropy` (returns `inf` off-support), `conditional_entropy`, `mutual_information`, `conditional_mutual_information`, `check_inequalities` (Klein, subadditivity, Araki-Lieb, concavity, $I=D(\rho_{AB}\|\rho_A\otimes\rho_B)$ on seeded random $2\times3$ states of random rank), `check_ssa` ($2\times2\times2$). Tests `test_entropies.py`: Bell $S(A|B)=-1$, $D(\rho\|I/d)=\log d-S$, Araki-Lieb saturated by pure states, SSA saturated by products.
