# 04 Schmidt decomposition and purification (TISS 1.4)

TISS 1.4 literally says "Schmidt decomposition theorem **and proof**, purification of mixed quantum states" [S2]: this is one of the two items where the syllabus itself names a proof (the other is no-cloning, [13](13-no-cloning-and-state-discrimination.md)). Expect to give it at the board, including the uniqueness statements. Sources: Preskill ch. 2 §2.4, §2.5.5 [S6] (1998: §2.4, §2.5.5 "GHJW" [S5]); Wilde Thm 3.8.1, §5.1, Thm 5.1.1 [S11]; Nielsen & Chuang §2.5 [S13]; Bertlmann & Friis ch. 15 [S14].

## Theorem (Schmidt decomposition)

For every $|\psi\rangle\in\mathcal H_A\otimes\mathcal H_B$ there are orthonormal sets $\{|a_k\rangle\}\subset\mathcal H_A$, $\{|b_k\rangle\}\subset\mathcal H_B$ and $s_1\ge s_2\ge\dots\ge s_r>0$ with
$$|\psi\rangle=\sum_{k=1}^{r}s_k|a_k\rangle|b_k\rangle,\qquad\sum_ks_k^2=1,\qquad r\le\min(d_A,d_B).$$
$r$ is the **Schmidt rank**, $s_k$ the **Schmidt coefficients**.

**Proof 1 (singular value decomposition).** Write $|\psi\rangle=\sum_{ij}C_{ij}|i\rangle|j\rangle$, $C\in\mathbb C^{d_A\times d_B}$. SVD: $C=U\Sigma V^\dagger$, $U,V$ unitary, $\Sigma$ rectangular diagonal with $s_1\ge\dots\ge s_r>0$. Then
$$|\psi\rangle=\sum_{ij}\sum_kU_{ik}s_k(V^\dagger)_{kj}|i\rangle|j\rangle=\sum_ks_k\Big(\sum_iU_{ik}|i\rangle\Big)\Big(\sum_j(V^\dagger)_{kj}|j\rangle\Big).$$
$|a_k\rangle=\sum_iU_{ik}|i\rangle$ are orthonormal (columns of a unitary), $|b_k\rangle=\sum_jV^*_{jk}|j\rangle$ likewise. Normalisation: $1=\operatorname{tr}C^\dagger C=\sum s_k^2$. $\square$

**Proof 2 (via the reduced state, Preskill's version [S6 §2.4]).** Let $\rho_A=\sum_kp_k|a_k\rangle\langle a_k|$ (spectral, $p_k>0$). Expand $|\psi\rangle=\sum_k|a_k\rangle|\tilde b_k\rangle$ with unnormalised $|\tilde b_k\rangle=(\langle a_k|\otimes I)|\psi\rangle$. Then $\rho_A=\sum_{kl}\langle\tilde b_l|\tilde b_k\rangle|a_k\rangle\langle a_l|$; comparing with the spectral form, $\langle\tilde b_l|\tilde b_k\rangle=p_k\delta_{kl}$. So $|b_k\rangle=|\tilde b_k\rangle/\sqrt{p_k}$ are orthonormal and $|\psi\rangle=\sum_k\sqrt{p_k}|a_k\rangle|b_k\rangle$. $\square$ This proof shows directly $s_k^2=p_k$.

**Consequences.**
1. $\rho_A=\sum s_k^2|a_k\rangle\langle a_k|$, $\rho_B=\sum s_k^2|b_k\rangle\langle b_k|$: equal nonzero spectra, hence $S(A)=S(B)$, $\operatorname{tr}\rho_A^2=\operatorname{tr}\rho_B^2$, same rank $r$.
2. **Pure-state entanglement criterion:** $|\psi\rangle$ is product iff $r=1$ iff $\rho_A$ is pure. $r$ is invariant under local unitaries *and cannot increase under LOCC*; $\{s_k\}$ is the complete set of local-unitary invariants of a bipartite pure state.
3. **Entropy of entanglement** $E(\psi)=S(\rho_A)=H(\{s_k^2\})$; maximal $\log d$ for $s_k=1/\sqrt d$ (maximally entangled). See [10](10-entanglement.md).
4. **Uniqueness.** The $s_k$ are unique. The vectors are unique up to phases $|a_k\rangle\to e^{i\phi}|a_k\rangle$, $|b_k\rangle\to e^{-i\phi}|b_k\rangle$ when the $s_k$ are non-degenerate; for degenerate $s_k$ any unitary mixing within the degenerate block works on $A$ with the conjugate on $B$ (e.g. $|\Phi^+\rangle=\frac1{\sqrt2}(|{+}{+}\rangle+|{-}{-}\rangle)$: $(U\otimes U^*)|\Phi^+\rangle=|\Phi^+\rangle$).
5. **No tripartite analogue:** a general $|\psi\rangle_{ABC}$ cannot be written $\sum_ks_k|a_k\rangle|b_k\rangle|c_k\rangle$ (e.g. W state); multipartite entanglement has no single normal form.

## Purification

**Def.** $|\psi\rangle_{AR}$ is a purification of $\rho_A$ if $\operatorname{tr}_R|\psi\rangle\langle\psi|=\rho_A$.

**Thm 4.1 (existence).** Every $\rho_A=\sum_kp_k|k\rangle\langle k|$ has the purification $|\psi\rangle=\sum_k\sqrt{p_k}|k\rangle_A|k\rangle_R$ with $d_R=\operatorname{rank}\rho_A$, which is minimal (Schmidt rank equals $\operatorname{rank}\rho_A$). **Canonical purification:** $|\psi_\rho\rangle=(\sqrt\rho\otimes I)|\Omega\rangle$, $|\Omega\rangle=\sum_i|ii\rangle$ (unnormalised), basis-dependent but needs no diagonalisation; used for Uhlmann's theorem ([05](05-hilbert-space-geometry.md)).
*Proof.* $\operatorname{tr}_R\sum_{kl}\sqrt{p_kp_l}|k\rangle\langle l|\otimes|k\rangle\langle l|=\sum_kp_k|k\rangle\langle k|$. $\square$

**Thm 4.2 (uniqueness up to isometries on R).** If $|\psi\rangle_{AR}$ and $|\phi\rangle_{AR'}$ both purify $\rho_A$, there is an isometry $V:R\to R'$ with $|\phi\rangle=(I\otimes V)|\psi\rangle$ (a unitary if $R=R'$).
*Proof.* Schmidt-decompose both. By consequence 1 both have the form $\sum_k\sqrt{p_k}|a_k\rangle|r_k\rangle$ and $\sum_k\sqrt{p_k}|a_k\rangle|r'_k\rangle$ with the *same* $|a_k\rangle$ (eigenvectors of $\rho_A$; in a degenerate eigenspace re-choose the $|r'_k\rangle$ accordingly, since $\sum_{k\in\text{block}}|a_k\rangle|r_k\rangle$ is basis independent in the block by consequence 4). Define $V|r_k\rangle=|r'_k\rangle$ and extend isometrically. $\square$

**Cor. 4.3 (HJW / Schrödinger mixture theorem [S6 §2.5.5]).** $\sum_ip_i|\psi_i\rangle\langle\psi_i|=\sum_jq_j|\phi_j\rangle\langle\phi_j|$ iff $\sqrt{p_i}|\psi_i\rangle=\sum_jU_{ij}\sqrt{q_j}|\phi_j\rangle$ for some unitary $U$ (pad the shorter list with zeros).
*Proof.* $|\Psi\rangle=\sum_i\sqrt{p_i}|\psi_i\rangle|i\rangle$, $|\Phi\rangle=\sum_j\sqrt{q_j}|\phi_j\rangle|j\rangle$ both purify $\rho$; Thm 4.2 gives $U$ on $R$; expand $(I\otimes U)$ in the $|i\rangle$ basis. $\square$ Physical meaning: every ensemble of $\rho_A$ can be steered by Bob by measuring $R$ in a suitable basis (the "steering" behind EPR, [06](06-non-locality-and-bell-inequalities.md)), and no local measurement on $A$ reveals which one he chose.

**"Church of the larger Hilbert space".** Every mixed state is a pure state on a larger space (Thm 4.1), every measurement is projective on a larger space (Neumark, [12](12-generalised-measurements.md)), every channel is unitary on a larger space (Stinespring, [11](11-quantum-channels.md)). Wilde builds "the purified quantum theory" on exactly these three facts [S11 ch. 5].

## Worked example

$|\psi\rangle=\frac1{\sqrt3}(|00\rangle+|01\rangle+|10\rangle)$: $C=\frac1{\sqrt3}\begin{pmatrix}1&1\\1&0\end{pmatrix}$, $CC^\dagger=\frac13\begin{pmatrix}2&1\\1&1\end{pmatrix}$, eigenvalues $s_k^2=\frac{3\pm\sqrt5}6=0.873,\ 0.127$; Schmidt rank 2, so entangled; $E(\psi)=H(0.873)=0.550$ ebit. $|a_1\rangle\propto(\varphi,1)^T$, $\varphi=\frac{1+\sqrt5}2$ (eigenvector of $\begin{pmatrix}2&1\\1&1\end{pmatrix}$ for $\frac{3+\sqrt5}2$), $|a_2\rangle\perp|a_1\rangle$. $|b_k\rangle=(\langle a_k|\otimes I)|\psi\rangle/s_k$. Purification example: $\rho=\operatorname{diag}(0.7,0.3)$ is purified by $\sqrt{0.7}|00\rangle+\sqrt{0.3}|11\rangle$ and equally by $\sqrt{0.7}|0\rangle|{+}\rangle+\sqrt{0.3}|1\rangle|{-}\rangle$ ($V=H$ on $R$).

## Pitfalls

- The Schmidt bases depend on the state; there is no fixed basis in which all states of $\mathcal H_A\otimes\mathcal H_B$ are Schmidt-diagonal.
- $|b_k\rangle$ comes with a complex conjugate relative to $V$: $|b_k\rangle=\sum_jV^*_{jk}|j\rangle$. Forgetting it is harmless only for real $C$.
- Schmidt rank is not "number of nonzero amplitudes in the computational basis": $|{+}{+}\rangle$ has four nonzero amplitudes and rank 1.
- Purifications are unique up to isometries on $R$ only; $d_R\ge\operatorname{rank}\rho$ is required, $d_R>\operatorname{rank}\rho$ is allowed.
- Degenerate $s_k$: the decomposition is not unique; do not claim the Schmidt vectors are.

## Oral-exam questions (model answers)

1. *State and prove the Schmidt decomposition.* Either proof above; mention $r\le\min(d_A,d_B)$ and $\sum s_k^2=1$.
2. *What does the Schmidt decomposition tell you about the reduced states?* Same nonzero spectrum $\{s_k^2\}$; equal entropies; product iff $r=1$.
3. *Is the Schmidt decomposition unique?* Coefficients yes; vectors up to phases (non-degenerate) or up to $U\otimes U^*$ in degenerate blocks; example $\Phi^+$.
4. *Construct a purification and prove all purifications are related by a unitary on the ancilla.* Thm 4.1, Thm 4.2 via Schmidt; minimal $d_R=\operatorname{rank}\rho$.
5. *Derive the HJW theorem and interpret it.* Cor. 4.3; steering: measurements on $R$ prepare any ensemble of $\rho_A$ without changing $\rho_A$ (no signalling).

## Code

`src/py/schmidt.py`: `schmidt(psi, da, db)` (SVD), `schmidt_rank`, `reconstruct`, `purify` (spectral), `canonical_purification`, `purification_unitary` (finds $U_R$ between two purifications via the polar part of $C_1^\dagger C_2$). Tests `test_schmidt.py`: reconstruction, orthonormality, reduced spectra $=s_k^2$ on both sides, coefficients equal `np.linalg.svd`, product rank 1, Bell coefficients $1/\sqrt2$, purifications of ranks 1-3 related by a unitary.
