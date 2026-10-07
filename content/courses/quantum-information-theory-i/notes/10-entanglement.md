# 10 Entanglement: separability, entropy of entanglement, PPT, witnesses (TISS 2.5)

TISS 2.5: "Separability of pure states, entropy of entanglement, Example: Bell states, separability of mixed states, classical correlations vs. entanglement, mutual information, PPT criterion, entanglement witnesses" [S2]. This is the lecturers' research area (Huber, Friis); expect depth. Proofs: PPT necessary, witness existence and construction, the Werner threshold $p>1/3$ in both directions. Sources: Preskill ch. 4 §4.6-4.6.1 and Exercise 4.10 [S8]; Preskill ch. 10 §10.4-10.5 [S9]; Wilde Def. 4.3.2 [S11]; Bertlmann & Friis ch. 15-16 [S14]; primary Werner [S20], Peres [S33], Horodecki$^3$ [S34], Terhal [S35], Vidal-Werner [S36], Wootters [S37], P. Horodecki [S60], Chen-Wu [S61].

## Pure states

$|\psi\rangle_{AB}$ is **separable** iff $|\psi\rangle=|a\rangle|b\rangle$ iff Schmidt rank 1 iff $\rho_A$ pure iff $S(\rho_A)=0$ ([04](04-schmidt-decomposition-and-purification.md)). **Entropy of entanglement** $E(\psi)=S(\rho_A)=H(\{s_k^2\})\in[0,\log\min(d_A,d_B)]$. It is invariant under local unitaries, non-increasing under LOCC, additive, and asymptotically the *unique* pure-state measure: $n$ copies of $\psi$ convert reversibly by LOCC into $nE(\psi)$ Bell pairs (concentration and dilution [S9 §10.4]).
**Bell states** $|\Phi^\pm\rangle=\tfrac1{\sqrt2}(|00\rangle\pm|11\rangle)$, $|\Psi^\pm\rangle=\tfrac1{\sqrt2}(|01\rangle\pm|10\rangle)$: orthonormal basis of maximally entangled states, $\rho_A=I/2$, $E=1$ ebit, related by local Paulis ([08](08-teleportation-swapping-dense-coding.md)). $\cos\theta|00\rangle+\sin\theta|11\rangle$: $E=h(\cos^2\theta)$, concurrence $\sin2\theta$.

## Mixed states

**Def (Werner [S20]).** $\rho_{AB}$ is **separable** if $\rho=\sum_ip_i\rho_i^A\otimes\rho_i^B$ ($p_i\ge0$, $\sum p_i=1$); equivalently a convex combination of pure product states. Otherwise **entangled**. The separable set $\mathcal S$ is convex and compact; by Carathéodory $(d_Ad_B)^2$ terms suffice. Deciding membership is NP-hard in general, hence criteria.
Operational meaning: separable states are exactly those preparable by LOCC from nothing. They can be highly **correlated**: $\tfrac12(|00\rangle\langle00|+|11\rangle\langle11|)$ has $I(A:B)=1$.

**Classical correlations vs entanglement.** Mutual information $I(A:B)=D(\rho_{AB}\|\rho_A\otimes\rho_B)$ measures *total* correlation ([03](03-entropy.md)). For separable states $S(A|B)\ge0$, hence $I(A:B)\le\min(S(A),S(B))\le\log\min(d_A,d_B)$; entangled states reach $2\log d$ (Bell: $I=2$). Correlations present in *one* basis ($\langle ZZ\rangle=1$) are classical; entanglement shows up as simultaneous correlations in complementary bases ($\langle ZZ\rangle=\langle XX\rangle=1$, impossible for separable states since $\langle XX\rangle+\langle ZZ\rangle\le1$ on products and hence on mixtures; this is itself a witness, $W=I-X\otimes X-Z\otimes Z$ up to normalisation).

## PPT criterion

Partial transpose $(|i\rangle\langle k|\otimes|j\rangle\langle l|)^{T_B}=|i\rangle\langle k|\otimes|l\rangle\langle j|$. Its spectrum does not depend on the basis used (changing basis on $B$ is a local unitary conjugation).
**Thm 10.1 (Peres [S33]).** $\rho$ separable $\Rightarrow\rho^{T_B}\ge0$.
*Proof.* $\rho^{T_B}=\sum_ip_i\rho_i^A\otimes(\rho_i^B)^T$ and $(\rho_i^B)^T=(\rho_i^B)^*$ is again a density operator (same spectrum). A convex sum of positive operators is positive. $\square$
**Thm 10.2 (Horodecki$^3$ [S34]).** For $2\times2$ and $2\times3$: $\rho^{T_B}\ge0\iff\rho$ separable. In higher dimensions PPT entangled ("bound entangled") states exist.
*Idea.* $\rho$ is separable iff $(\mathrm{id}\otimes\Lambda)\rho\ge0$ for *every* positive map $\Lambda$ (Hahn-Banach + Jamiołkowski). In dimensions $2\times2$, $2\times3$ every positive map is decomposable, $\Lambda=\Lambda_1+\Lambda_2\circ T$ with $\Lambda_i$ completely positive (Størmer, Woronowicz), so the transpose is the only test needed. In $3\times3$ and $2\times4$ non-decomposable positive maps exist. Example: P. Horodecki's $3\times3$ family $\rho_a$ [S60] is PPT for all $0<a<1$ yet entangled; realignment detects it, $\|R(\rho_a)\|_1>1$ [S61] (1.0023 at $a=0.5$, `entanglement.py`).
**Negativity** $N(\rho)=\sum_{\lambda<0}|\lambda(\rho^{T_B})|=\tfrac12(\|\rho^{T_B}\|_1-1)$ and log-negativity $\log_2\|\rho^{T_B}\|_1$ are computable entanglement monotones [S36]; zero on PPT states. For two qubits $\rho^{T_B}$ has at most one negative eigenvalue, and $N>0\iff$ concurrence $C>0$ [S37]; the tests check this agreement on 300 random states.

## Werner state, both directions

$\rho_p=p|\Psi^-\rangle\langle\Psi^-|+(1-p)\tfrac I4$ ($p\in[-\tfrac13,1]$).
*Entangled for $p>\tfrac13$:* $(|\Psi^-\rangle\langle\Psi^-|)^{T_B}$ has eigenvalues $\tfrac12,\tfrac12,\tfrac12,-\tfrac12$ (it is LU-equivalent to $\tfrac12\mathrm{SWAP}$), so $\lambda_{\min}(\rho_p^{T_B})=\tfrac{1-p}4-\tfrac p2=\tfrac{1-3p}4<0\iff p>\tfrac13$; $N=\tfrac{3p-1}4$. [S8 §4.6.1, Ex. 4.10]
*Separable for $p\le\tfrac13$ (explicit decomposition):* average the product states $|\hat n\rangle\langle\hat n|\otimes|{-\hat n}\rangle\langle{-\hat n}|$ over the sphere: $\int\frac{d\hat n}{4\pi}\tfrac14(I+\hat n\cdot\vec\sigma)\otimes(I-\hat n\cdot\vec\sigma)=\tfrac14\big(I-\tfrac13\sum_i\sigma_i\otimes\sigma_i\big)=\rho_{1/3}$ (using $\int n_in_j=\delta_{ij}/3$ and $T(\Psi^-)=-I$). Mixing with the product state $I/4$ gives every $p\in[0,\tfrac13]$. $\square$

## Entanglement witnesses

**Def.** Hermitian $W$ with $\operatorname{tr}W\sigma\ge0$ for all separable $\sigma$ and $\operatorname{tr}W\rho<0$ for at least one $\rho$ ("$W$ detects $\rho$").
**Thm 10.3 (existence [S34, S35]).** $\rho$ entangled $\Rightarrow$ some witness detects it.
*Proof sketch.* $\mathcal S$ is convex and compact in the real vector space of Hermitian operators with $\langle A,B\rangle=\operatorname{tr}AB$. Hahn-Banach (separating hyperplane) gives $W$ and $c$ with $\operatorname{tr}W\rho<c\le\operatorname{tr}W\sigma$ for all $\sigma\in\mathcal S$; replace $W$ by $W-cI$. $\square$ Geometrically: a hyperplane cutting $\rho$ off from the separable set. A witness is a single observable (measurable locally as a sum of product terms), hence the experimental tool.
**Constructions.**
1. *From PPT:* if $\rho^{T_B}|v\rangle=\lambda|v\rangle$, $\lambda<0$, then $W=(|v\rangle\langle v|)^{T_B}$ detects $\rho$: $\operatorname{tr}W\rho=\langle v|\rho^{T_B}|v\rangle=\lambda<0$, and $\operatorname{tr}W\sigma=\langle v|\sigma^{T_B}|v\rangle\ge0$ for separable $\sigma$ (Thm 10.1). Uses $\operatorname{tr}(A^{T_B}B)=\operatorname{tr}(AB^{T_B})$.
2. *Fidelity witness:* for a pure entangled target $|\psi\rangle$ with largest Schmidt coefficient $s_1$: $W=s_1^2I-|\psi\rangle\langle\psi|$, since $\max_{a,b}|\langle ab|\psi\rangle|^2=s_1^2$ (Schmidt + Cauchy-Schwarz). For $\Psi^-$: $W=\tfrac12I-|\Psi^-\rangle\langle\Psi^-|$, $\operatorname{tr}W\rho_p=\tfrac12-\tfrac{1+3p}4=\tfrac{1-3p}4$: detects exactly $p>\tfrac13$, so for Werner states this witness is as strong as PPT (it is optimal: tangent to $\mathcal S$ at $\rho_{1/3}$).
Witnesses are one-sided: $\operatorname{tr}W\rho\ge0$ says nothing. Bell inequalities are witnesses that do not trust the devices ([06](06-non-locality-and-bell-inequalities.md)).

## Worked example

$\rho=0.6|\Psi^-\rangle\langle\Psi^-|+0.1\,I$: $\rho^{T_B}$ eigenvalues $0.4,0.4,0.4,-0.2$; $N=0.2$, $E_N=\log_2 1.4=0.485$, concurrence $0.4$; $\operatorname{tr}W\rho=-0.2$; $I(A:B)=0.643$; CHSH max $2\sqrt2\cdot0.6=1.70<2$. Entangled, detected by PPT and by the witness, not by CHSH (all printed by `entanglement.py`, `bell.py`).

## Pitfalls

- Correlated $\ne$ entangled: $I(A:B)>0$ for classical mixtures.
- PPT is necessary and sufficient only for $2\times2$ and $2\times3$. In $3\times3$, PPT states can be entangled (bound entanglement: not distillable).
- Partial transpose is not a physical operation (transpose is positive but not completely positive, [11](11-quantum-channels.md)); that is exactly why it detects entanglement.
- Negativity zero does not imply separable beyond $2\times3$.
- The fidelity witness needs the *largest* Schmidt coefficient squared, not $1/d$, unless the target is maximally entangled.

## Oral-exam questions (model answers)

1. *Define separability for pure and mixed states; what is the entropy of entanglement?* Product/Schmidt rank 1; convex hull of products; $E=S(\rho_A)$, unique asymptotic pure-state measure.
2. *Prove the PPT criterion and state when it is sufficient.* Thm 10.1; Horodecki 2x2, 2x3 via decomposability of positive maps; bound entanglement beyond.
3. *Determine for which $p$ the Werner state is entangled.* PT eigenvalue $(1-3p)/4$; explicit twirl decomposition for $p\le1/3$.
4. *What is an entanglement witness? Prove every entangled state has one and construct one.* Hahn-Banach; $(|v\rangle\langle v|)^{T_B}$; fidelity witness $s_1^2I-\psi$.
5. *Classical correlations vs entanglement: how does mutual information distinguish them?* $I\le\log d$ for separable (since $S(A|B)\ge0$), up to $2\log d$ for entangled; example classical mixture vs Bell state; correlations in complementary bases.

## Code

`src/py/entanglement.py`: `partial_transpose`, `is_ppt`, `negativity`, `log_negativity`, `entropy_of_entanglement`, `concurrence`, `werner`, `WERNER_WITNESS`, `witness_value`, `random_separable`, `realignment`, `horodecki_3x3`. Tests `test_entanglement.py`: $(\Phi^+)^{T_B}=\mathrm{SWAP}/2$, Werner thresholds via PPT, witness and negativity $(3p-1)/4$, witness $\ge0$ on 300 random separable states, PPT $\iff C=0$ for two qubits, separable $2\times3$ are PPT, $E$ and $C$ formulas, Horodecki $3\times3$ PPT but realignment $>1$, realignment $\le1$ on separable $3\times3$.
