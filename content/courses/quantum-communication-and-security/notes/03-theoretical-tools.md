# 03 Theoretical tools

Third TISS topic: "mixed states formalism, probability and information theory, conditional entropies" [S2]; learning outcome "apply different entropic relations and properties". The sibling course 141.282 (QIT I) covers mixed states and partial trace ([`02`](../../quantum-information-theory-i/notes/02-composite-systems-and-partial-trace.md)), Shannon and von Neumann entropy ([`03`](../../quantum-information-theory-i/notes/03-entropy.md)), Schmidt decomposition and purification ([`04`](../../quantum-information-theory-i/notes/04-schmidt-decomposition-and-purification.md)), fidelity and trace distance ([`05`](../../quantum-information-theory-i/notes/05-hilbert-space-geometry.md)) and channels ([`11`](../../quantum-information-theory-i/notes/11-quantum-channels.md)) (written concurrently on 2026-09-28; file names may change); here only what the QKD proofs use, plus the one-shot entropies that QIT I does not cover.

## Definitions

1. **cq state.** $\rho_{XE}=\sum_xP_X(x)\,|x\rangle\langle x|_X\otimes\rho_E^x$: classical $X$ (Alice's raw key), quantum $E$ (Eve).
2. **Purification.** For $\rho_A=\sum_i\lambda_i|i\rangle\langle i|$, $|\psi\rangle_{AR}=\sum_i\sqrt{\lambda_i}|i\rangle_A|i\rangle_R$ has $\mathrm{tr}_R|\psi\rangle\langle\psi|=\rho_A$. Any two purifications are related by an isometry on $R$ (Uhlmann). **Consequence for QKD:** if Alice and Bob know $\rho_{AB}$, the worst case is that Eve holds a purification $|\psi\rangle_{ABE}$; anything else Eve holds is obtained from it by a channel, which cannot help her (data processing).
3. **Shannon quantities.** $H(X)=-\sum p\log p$, $H(X|Y)=H(XY)-H(Y)$, $I(X{:}Y)=H(X)-H(X|Y)$; binary entropy $h(p)$. All logs base 2.
4. **von Neumann quantities.** $S(\rho)=-\mathrm{tr}\rho\log\rho$, $H(A|B)=S(AB)-S(B)$ (can be negative: $-1$ for $|\Phi^+\rangle$), $I(A{:}B)=S(A)+S(B)-S(AB)$.
5. **Holevo quantity.** $\chi(X{:}E)=S(\sum_xP_X(x)\rho_E^x)-\sum_xP_X(x)S(\rho_E^x)=I(X{:}E)_{\rho_{XE}}$.
6. **Min-entropy** [S4 Def. 3.1.1-3.1.2; S5 Def. 3].
   $$H_{\min}(A|B)_\rho=\sup_{\sigma_B}\sup\{\lambda:\rho_{AB}\le2^{-\lambda}\mathbb 1_A\otimes\sigma_B\}.$$
   For cq states $H_{\min}(X|E)=-\log p_{\rm guess}(X|E)$, the optimal probability of guessing $X$ by measuring $E$ [S5 Eq. (12)]. Unconditional: $H_{\min}(X)=-\log\max_xP_X(x)$. Classical conditional: $H_{\min}(X|Y)=-\log\sum_y\max_xP(x,y)$.
7. **Max-entropy.** Unconditional classical form used here: $H_{\max}(X)=2\log\sum_x\sqrt{P_X(x)}$ (Rényi-1/2, the form dual to $H_{\min}$ in [S5]); [S4 Def. 3.1.1] uses $\log|\mathrm{supp}|$. Ordering $H_{\min}\le H\le H_{\max}\le\log|\mathrm{supp}|$ [S5 Eq. (15)].
8. **Smooth entropies.** $H_{\min}^\varepsilon(A|B)_\rho=\sup_{\tilde\rho\in\mathcal B^\varepsilon(\rho)}H_{\min}(A|B)_{\tilde\rho}$, $H_{\max}^\varepsilon$ with inf. The ball: subnormalised states with $\|\tilde\rho-\rho\|_1\le\varepsilon$ in [S4 Def. 3.2.1], purified distance $\le\varepsilon$ in [S5 Def. 5]. Constants in theorems depend on which ball; do not mix.

## Results

**Properties used in every proof** [S5 Eqs. (17)-(19); S4 §3.1-3.2].
- Duality: for pure $\rho_{ABC}$, $H_{\min}^\varepsilon(A|B)=-H_{\max}^\varepsilon(A|C)$.
- Data processing: $H^\varepsilon_{\min}(X|B)\le H^\varepsilon_{\min}(X|C)_{\mathcal E(\rho)}$ for any channel $\mathcal E_{B\to C}$ (same for $H_{\max}$).
- Chain rule for classical leakage: $H^\varepsilon_{\min}(A|BX)\ge H^\varepsilon_{\min}(A|B)-\log|X|$. **This is how error-correction leakage enters the key length**: $\mathrm{leak_{EC}}+t$ bits of public syndrome and hash cost at most that many bits of min-entropy.
- Asymptotic equipartition: $\frac1nH^\varepsilon_{\min}(A^n|B^n)_{\rho^{\otimes n}}\to H(A|B)_\rho$ with a correction $O(\sqrt{\log(1/\varepsilon)/n})$ [S4 Thm 3.3.6]. One-shot entropies of i.i.d. states become von Neumann entropies; this is how the finite-key formula tends to Devetak-Winter.

**Entropic uncertainty relation with quantum memory** [S20]. For measurements $X,Z$ on $A$ with overlap $c=\max_{x,z}|\langle x|z\rangle|^2$ and any $\rho_{ABC}$:
$$H(X|B)+H(Z|C)\ge\log\frac1c.$$
Smooth version [S21; S5 Prop. 4 Eq. (66)]: $H^\varepsilon_{\min}(X|E)+H^\varepsilon_{\max}(Z|B)\ge\log\frac1c$, per round, so $n\log\frac1c$ for $n$ rounds [S5 Cor. 5 Eq. (68)]. For BB84 $c=\tfrac12$, $\log\frac1c=1$.

**Corollary 3.1 (BB84 rate in three lines).** Key from $Z$, Eve holds $E$, Bob holds $B$. Apply the relation with $C=E$ to the conjugate pair:
$$H(Z_A|E)\ge1-H(X_A|B)\ge1-H(X_A|X_B)=1-h(e_X),$$
(the second step is data processing: Bob measuring $X$ can only increase uncertainty; the third uses that $X_A\oplus X_B$ is Bernoulli$(e_X)$). Devetak-Winter (note 05): $r=H(Z_A|E)-H(Z_A|Z_B)\ge1-h(e_X)-h(e_Z)$. With $e_X=e_Z=e$: **$1-2h(e)$**, no eavesdropping model needed.

**Proposition 3.2 (Bell-diagonal states).** For $\rho_{AB}=\sum_i\lambda_i|B_i\rangle\langle B_i|$ (order $\Phi^+,\Phi^-,\Psi^+,\Psi^-$) and $E$ a purification: $e_Z=\lambda_3+\lambda_4$, $e_X=\lambda_2+\lambda_4$, and
$$H(Z_A|E)=1-H(\boldsymbol\lambda)+h(\lambda_1+\lambda_2).$$
*Derivation.* $S(E)=S(AB)=H(\boldsymbol\lambda)$. Conditioned on $Z_A=z$, the state of $BE$ is pure, so $S(E|Z_A=z)=S(B|Z_A=z)$; $B$ given $z$ is $|z\rangle$ with probability $\lambda_1+\lambda_2$ and $|\bar z\rangle$ otherwise, entropy $h(\lambda_1+\lambda_2)$. So $H(Z|E)=H(Z)+S(E|Z)-S(E)=1+h(\lambda_1+\lambda_2)-H(\boldsymbol\lambda)$. ∎ (Checked numerically against the full four-party state in `test_entropies.py`.)

**Proposition 3.3 (smooth min-entropy of a distribution, trace-distance ball).** Optimal smoothing cuts the largest probabilities to a common level $\lambda$ with $\sum_x(P(x)-\lambda)_+=\varepsilon$; then $H^\varepsilon_{\min}(X)=-\log\lambda$. (Lowering the maximum is all that matters; any other change costs distance without lowering it.)

## Worked example

**Negative conditional entropy.** $|\Phi^+\rangle$: $S(AB)=0$, $S(B)=1$, $H(A|B)=-1$, $I(A{:}B)=2$, $H_{\min}(A|B)=-2\log\sum_i\sqrt{\lambda_i}=-2\log(2/\sqrt2)=-1$. Bob with quantum memory can predict *both* $X_A$ and $Z_A$: the uncertainty relation's bound $1+H(A|B)$ becomes $0$ [S20].

**Bell-diagonal numbers** (`entropies.demo`, $e_Z=e_X=5\%$, only $\lambda_4$ free):

| $\lambda_{\Psi^-}$ | $H(Z\mid E)$ | $H(Z\mid E)-h(0.05)$ |
|---|---|---|
| 0 | 0.7174 | 0.4310 |
| $e^2=0.0025$ | 0.7136 | **0.4272** $=1-2h(0.05)$ |
| 0.025 | 0.7832 | 0.4968 |

The worst case over the unobserved $\lambda_4$ is $e_Ze_X$ (the product distribution); it equals the uncertainty-relation bound exactly.

**Smoothing.** $P=(0.5,\,0.5/7\times7)$: $H_{\min}=1$; $H^{0.1}_{\min}=-\log0.4=1.32$; $H^{0.3}_{\min}=-\log0.2=2.32$; $H=1+\tfrac12\log7=2.40$. With $\varepsilon=0.3$ one sacrifices 30 % probability to get almost the Shannon entropy: that is the AEP at work for i.i.d. strings.

**Guessing.** Eve holds $|0\rangle$ or $|+\rangle$ for $X=0,1$: $p_{\rm guess}=\tfrac12(1+\tfrac1{\sqrt2})=0.854$, $H_{\min}(X|E)=0.228$.

**Uncertainty relation.** Over 200 random pure three-qubit states $\min[H(X|B)+H(Z|C)]=1.047\ge1$; equality for $|0\rangle_A$ uncorrelated with $BC$.

## Pitfalls

- $H(A|B)<0$ is possible for quantum $B$, never for classical $B$; min-entropy chain rules with classical registers lose at most $\log|X|$, with quantum ones more care is needed.
- The conditional min-entropy is **not** $-\log\max$ of the conditional distribution averaged; it is $-\log$ of the *average of the maxima*, $\sum_y\max_xP(x,y)$.
- $\varepsilon$ in $H^\varepsilon$ is a distance on states, not a failure probability of an event; converting between them costs square roots (purified vs trace distance).
- The uncertainty relation needs the *measurement* on Alice's side to be the ideal $X$/$Z$; that is the device assumption that fails in note 06 and is removed by DI-QKD.
- $\chi$ bounds Eve's information for collective attacks only; coherent attacks need the one-shot quantities (note 05).

## Questions

1. *Why may we assume Eve holds a purification of $\rho_{AB}$?* Every extension $\rho_{ABE'}$ arises from the purification by a channel on $E$ (isometry equivalence); data processing means a channel never helps Eve, so the purification is the worst case.
2. *Define $H_{\min}(X|E)$ for a cq state and give its operational meaning.* $-\log p_{\rm guess}$, the optimal probability of guessing $X$ from a measurement on $E$; equivalently Def. 6.
3. *Compute $H(A|B)$, $I(A{:}B)$ and $H_{\min}(A|B)$ of $|\Phi^+\rangle$.* $-1$, $2$, $-1$.
4. *Derive $1-2h(e)$ from the entropic uncertainty relation.* Corollary 3.1.
5. *State the chain rule used for leakage and explain why the leak costs at most its length.* $H^\varepsilon_{\min}(X|EC)\ge H^\varepsilon_{\min}(X|E)-\log|C|$; conditioning on a register of $2^m$ values can at most multiply the guessing probability by $2^m$.

## Code

`src/py/entropies.py`: `h2`, `shannon`, `von_neumann`, `partial_trace`, `conditional_entropy`, `mutual_information`, `holevo_chi`, `min_entropy_classical`, `max_entropy_classical`, `cond_min_entropy_classical`, `smooth_min_entropy_classical`, `helstrom_guess`, `min_entropy_cq_binary`, `min_entropy_pure`, `bell_diagonal`, `bb84_lams`, `purify`, `h_z_given_e`, `uncertainty_sum`. Tests: `test_entropies.py` (closed forms, chain rule on random distributions, Prop. 3.2 against the four-party computation, uncertainty relation on random states).

## References

[S4 Defs 3.1.1-3.2.2, Thm 3.3.6], [S5 Eqs. (12)-(19), Prop. 4, Cor. 5], [S13 for background on entropies], [S20], [S21].
