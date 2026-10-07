# 05 Hilbert-space geometry: fidelity, Uhlmann, Bures and trace distance (TISS 1.5)

TISS 1.5: "Overlap of quantum states, Uhlmann fidelity, Uhlmann theorem, Bures distance, trace distance, relative entropy revisited" [S2]. Sources: Preskill ch. 2 §2.6.1-2.6.2 [S6]; Wilde ch. 9 [S11] (trace distance §9.1, Uhlmann Thm 9.2.1, measurement achieves fidelity Thm 9.2.2, Fuchs-van de Graaf Thm 9.3.1) and quantum Pinsker Thm 11.9.1; Nielsen & Chuang §9.2 [S13]; primary Uhlmann 1976 [S38], Jozsa 1994 [S39], Fuchs-van de Graaf 1999 [S40].

**Convention (state it in the exam).** Here, as in Jozsa [S39] and Wilde [S11], the fidelity is the *squared* quantity
$$F(\rho,\sigma)=\big(\operatorname{tr}\sqrt{\sqrt\rho\,\sigma\sqrt\rho}\big)^2=\|\sqrt\rho\sqrt\sigma\|_1^2,\qquad F(\psi,\phi)=|\langle\psi|\phi\rangle|^2 .$$
Nielsen & Chuang [S13] call $\sqrt F$ the fidelity. Every formula below changes shape under the other convention; the lecturers' own convention is not known (their book [S14] was not accessible), so write the definition first.

## Definitions

- **Overlap** of pure states $|\langle\psi|\phi\rangle|$; $\arccos|\langle\psi|\phi\rangle|$ is the Fubini-Study angle, the geodesic distance on projective space.
- **Trace norm** $\|A\|_1=\operatorname{tr}|A|=\operatorname{tr}\sqrt{A^\dagger A}=\sum$ singular values. **Trace distance** $T(\rho,\sigma)=\tfrac12\|\rho-\sigma\|_1\in[0,1]$.
- **Bures distance** $D_B(\rho,\sigma)=\sqrt{2(1-\sqrt{F(\rho,\sigma)})}$; **Bures angle** $A(\rho,\sigma)=\arccos\sqrt{F(\rho,\sigma)}$.

## Theorems with proofs

**Lemma 5.1.** For any $A$, $\max_{U\text{ unitary}}|\operatorname{tr}(AU)|=\|A\|_1$, attained at $U=V W^\dagger$ where $A=W\Sigma V^\dagger$ (SVD).
*Proof.* $|\operatorname{tr}(W\Sigma V^\dagger U)|=|\operatorname{tr}(\Sigma\,V^\dagger UW)|=|\sum_k s_kM_{kk}|\le\sum_ks_k$ since $M=V^\dagger UW$ is unitary, $|M_{kk}|\le1$. Equality at $M=I$. $\square$

**Thm 5.2 (Uhlmann).** $F(\rho,\sigma)=\max|\langle\psi_\rho|\psi_\sigma\rangle|^2$ over all purifications $|\psi_\rho\rangle,|\psi_\sigma\rangle$ on a common $\mathcal H_A\otimes\mathcal H_R$ ($d_R\ge d_A$).
*Proof sketch.* Take canonical purifications $|\psi_\rho\rangle=(\sqrt\rho\otimes I)|\Omega\rangle$, $|\psi_\sigma\rangle=(\sqrt\sigma\otimes I)|\Omega\rangle$, $|\Omega\rangle=\sum_i|ii\rangle$. By Thm 4.2 ([04](04-schmidt-decomposition-and-purification.md)) every purification pair is, up to a joint unitary on $R$ (which does not change the overlap), $|\psi_\rho\rangle$ and $(I\otimes U)|\psi_\sigma\rangle$. Using the transpose trick $(I\otimes U)|\Omega\rangle=(U^T\otimes I)|\Omega\rangle$ and $\langle\Omega|X\otimes I|\Omega\rangle=\operatorname{tr}X$:
$$\langle\psi_\rho|(I\otimes U)|\psi_\sigma\rangle=\langle\Omega|(\sqrt\rho\sqrt\sigma U^T\otimes I)|\Omega\rangle=\operatorname{tr}(\sqrt\rho\sqrt\sigma\,U^T).$$
Maximise over $U$ with Lemma 5.1: $\max=\|\sqrt\rho\sqrt\sigma\|_1$. Square. $\square$

**Consequences (each a one-liner from Uhlmann).**
1. $0\le F\le1$ (Cauchy-Schwarz), $F=1$ iff $\rho=\sigma$; symmetric $F(\rho,\sigma)=F(\sigma,\rho)$ (not obvious from the formula).
2. **Monotonicity (data processing):** $F(\mathcal N(\rho),\mathcal N(\sigma))\ge F(\rho,\sigma)$ for every channel. Proof: Stinespring $V$ ([11](11-quantum-channels.md)) maps optimal purifications of $\rho,\sigma$ to purifications of $\mathcal N(\rho),\mathcal N(\sigma)$ with the same overlap; the max for the outputs can only be larger.
3. Pure vs mixed: $F(\psi,\sigma)=\langle\psi|\sigma|\psi\rangle$.
4. Joint concavity of $\sqrt F$, multiplicativity $F(\rho_1\otimes\rho_2,\sigma_1\otimes\sigma_2)=F(\rho_1,\sigma_1)F(\rho_2,\sigma_2)$.
5. **Qubits:** $F=\operatorname{tr}\rho\sigma+2\sqrt{\det\rho\det\sigma}=\tfrac12\big(1+\vec r\cdot\vec s+\sqrt{(1-|\vec r|^2)(1-|\vec s|^2)}\big)$ (for $2\times2$, $\sqrt{\sqrt\rho\sigma\sqrt\rho}$ has trace $\sqrt{\operatorname{tr}M+2\sqrt{\det M}}$).

**Thm 5.3 (trace distance as optimal bias).** $T(\rho,\sigma)=\max_{0\le P\le I}\operatorname{tr}P(\rho-\sigma)$, attained by the projector $P_+$ onto the positive eigenspace of $\rho-\sigma$.
*Proof.* $\rho-\sigma=Q-S$ with $Q,S\ge0$ on orthogonal supports; $\operatorname{tr}(\rho-\sigma)=0\Rightarrow\operatorname{tr}Q=\operatorname{tr}S=T$. For $0\le P\le I$: $\operatorname{tr}P(Q-S)\le\operatorname{tr}PQ\le\operatorname{tr}Q=T$; $P_+$ gives $\operatorname{tr}Q$. $\square$ Hence the **Helstrom** success probability for equal priors is $\tfrac12(1+T)$ ([13](13-no-cloning-and-state-discrimination.md)), $T$ is contractive under channels (apply the theorem to $\mathcal N^\dagger(P)$, which is again an effect), and for qubits $T=\tfrac12|\vec r-\vec s|$ (eigenvalues of $\tfrac12(\vec r-\vec s)\cdot\vec\sigma$ are $\pm\tfrac12|\vec r-\vec s|$). The trace distance is a metric (triangle inequality from the norm).

**Thm 5.4 (Fuchs-van de Graaf [S40]).** $1-\sqrt F\le T\le\sqrt{1-F}$.
*Proof.*
Upper: pure states first. $|\phi\rangle=\cos\theta|\psi\rangle+\sin\theta|\psi^\perp\rangle$; in the basis $\{\psi,\psi^\perp\}$, $\psi-\phi=\begin{pmatrix}\sin^2\theta&-\sin\theta\cos\theta\\-\sin\theta\cos\theta&-\sin^2\theta\end{pmatrix}$, traceless with determinant $-\sin^2\theta$, eigenvalues $\pm\sin\theta$, so $T=\sin\theta=\sqrt{1-F}$ exactly. Mixed: take Uhlmann-optimal purifications; $T$ is non-increasing under $\operatorname{tr}_R$, so $T(\rho,\sigma)\le T(\psi_\rho,\psi_\sigma)=\sqrt{1-F(\rho,\sigma)}$.
Lower: $F$ equals the minimum over POVMs of the classical fidelity $(\sum_x\sqrt{p_xq_x})^2$ [S11 Thm 9.2.2], and $T\ge\tfrac12\sum_x|p_x-q_x|$ for every POVM. Classically $\sum_x(\sqrt{p_x}-\sqrt{q_x})^2\le\sum_x|\sqrt{p_x}-\sqrt{q_x}||\sqrt{p_x}+\sqrt{q_x}|=\sum_x|p_x-q_x|$, i.e. $1-\sum\sqrt{p_xq_x}\le\tfrac12\sum|p_x-q_x|$. Apply with the fidelity-achieving POVM. $\square$ Meaning: $F\to1\iff T\to0$; the two measures are interchangeable up to square roots, which is how security proofs switch between them.

**Bures distance.** $D_B^2=2(1-\sqrt F)=\min\||\psi_\rho\rangle-|\psi_\sigma\rangle\|^2$ over purifications (expand the norm, use Uhlmann for the real part of the overlap): the Bures distance is the Euclidean distance between optimally aligned purifications, hence a metric; $A=\arccos\sqrt F$ is the corresponding geodesic (angle) distance. Infinitesimally $D_B^2(\rho,\rho+d\rho)=\tfrac14F_Q\,d\theta^2$, the quantum Fisher information of metrology (context: B&F ch. 24 [S14], not examinable here as far as TISS says).

**Relative entropy revisited.** $D(\rho\|\sigma)$ is not a distance (asymmetric, no triangle inequality) but upper-bounds one: quantum Pinsker $D(\rho\|\sigma)\ge\frac1{2\ln2}\|\rho-\sigma\|_1^2=\frac2{\ln2}T^2$ [S11 Thm 11.9.1] (proof: a measurement achieving $T$ plus classical Pinsker plus monotonicity of $D$). Like $T$ and $F$, $D$ is monotone under channels. Unlike them it can be infinite.

## Worked example

$\rho=|0\rangle\langle0|$, $\sigma=\tfrac12(I+s\,\hat x\cdot\vec\sigma)$ with $s=0.6$: $F=\langle0|\sigma|0\rangle=\tfrac12$; $\sqrt F=0.707$; $T=\tfrac12|\hat z-0.6\hat x|=\tfrac12\sqrt{1.36}=0.583$; FvdG: $0.293\le0.583\le0.707$ ✓; $D_B=\sqrt{2(1-0.707)}=0.765$; $A=\pi/4$. Pure pair $|0\rangle,|{+}\rangle$: $F=\tfrac12$, $T=\sqrt{1-F}=0.707$ (upper bound tight). `distances.py` demo: Uhlmann overlap at the constructed optimal $U$ equals $F$, 2000 random $U$ never exceed it.

## Pitfalls

- Squared vs root fidelity (see convention box). Fuchs-van de Graaf in root convention reads $1-F\le T\le\sqrt{1-F^2}$.
- $\sqrt\rho\sqrt\sigma$ is not Hermitian; its trace norm is the sum of singular values, not of eigenvalues. `root_fidelity` uses singular values.
- $\operatorname{tr}\rho\sigma$ is *not* the fidelity for mixed states (Hilbert-Schmidt overlap: for $\rho=\sigma=I/2$ it gives $\tfrac12$).
- $T$ contracts under channels, $F$ grows; with $D_B$ both statements say "channels bring states closer".
- Uhlmann's max is over purifications on a *common* reference system of dimension at least $d$.

## Oral-exam questions (model answers)

1. *State and prove Uhlmann's theorem.* Canonical purifications, all others via $I\otimes U$, transpose trick gives $\operatorname{tr}(\sqrt\rho\sqrt\sigma U^T)$, Lemma 5.1.
2. *Why is the fidelity monotone under channels?* Stinespring + Uhlmann (consequence 2).
3. *Prove $T=\max_P\operatorname{tr}P(\rho-\sigma)$ and give its operational meaning.* Jordan decomposition; Helstrom $\tfrac12(1+T)$.
4. *State Fuchs-van de Graaf and prove the upper bound.* Pure-state equality $T=\sqrt{1-F}$, then purify and use monotonicity of $T$ under partial trace.
5. *Define the Bures distance and relate it to purifications; how does relative entropy fit in?* $D_B^2=2(1-\sqrt F)=\min\|\psi_\rho-\psi_\sigma\|^2$; Pinsker lower-bounds $D$ by $T^2$; $D$ is not a metric.

## Code

`src/py/distances.py`: `trace_distance`, `trace_distance_by_projector`, `fidelity` (squared), `root_fidelity`, `bures_distance`, `bures_angle`, `uhlmann_optimal_unitary`, `uhlmann_overlap`, `check_fuchs_van_de_graaf` (both FvdG bounds, Pinsker, pure-state equality). Tests `test_distances.py`: pure $F=|\langle\psi|\phi\rangle|^2$, unitary invariance and symmetry, commuting case = Bhattacharyya, Uhlmann max attained and not exceeded by 500 random unitaries, qubit Bloch formula, monotonicity of $F$ and $T$ under partial trace.
