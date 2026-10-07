# 12 Generalised measurements: projective vs POVM, Neumark dilation (TISS 2.7)

TISS 2.7: "projective measurements, observables, distinguishing quantum states, Neumark dilations" [S2]. Proofs: POVM from a projective measurement on system+ancilla; Neumark's theorem in both forms; impossibility of perfectly distinguishing non-orthogonal states. Sources: Preskill ch. 3 §3.1.1-3.1.2 [S7]; Preskill 1998 §3.1.2-3.1.4 (one-qubit POVM, "Neumark's theorem", pp. 81-86) [S5]; Jozsa §2.2, §3.2 [S10]; Wilde Def. 4.2.1 [S11]; Nielsen & Chuang §2.2.3-2.2.6 [S13]; Bertlmann & Friis ch. 23 "Quantum Measurements" [S14]; primary Naimark 1940 [S47] (not fetched; cited via Preskill and Peres). Spelling: Neumark = Naimark (Наймарк).

## Projective measurements and observables

A **projective measurement (PVM)** is $\{P_m\}$ with $P_mP_n=\delta_{mn}P_m$, $\sum_mP_m=I$: outcome probability $p(m)=\operatorname{tr}\rho P_m$, post-measurement state $P_m\rho P_m/p(m)$ (Lüders). An **observable** $A=\sum_ma\,P_a$ is the same data plus labels; $\langle A\rangle=\operatorname{tr}\rho A$, $\Delta A^2=\langle A^2\rangle-\langle A\rangle^2$. Properties: repeatable (measuring again gives the same outcome), at most $d$ outcomes with nonzero rank, commuting observables are jointly measurable (common spectral projectors). Unread outcome: dephasing $\rho\mapsto\sum_mP_m\rho P_m$, which never lowers entropy ([03](03-entropy.md) Cor. 3.2).

## POVMs

**Def.** A POVM is $\{E_m\}$ with $E_m\ge0$, $\sum_mE_m=I$; $p(m)=\operatorname{tr}\rho E_m$. Number of outcomes unbounded by $d$; effects need not be projectors or commute. With measurement operators $M_m$ ($E_m=M_m^\dagger M_m$) the post-measurement state is $M_m\rho M_m^\dagger/p(m)$; $M_m=U_m\sqrt{E_m}$ for any unitary $U_m$ (polar decomposition), so the POVM fixes the statistics but not the state update (instrument, [11](11-quantum-channels.md)).

**Prop. 12.1 (POVMs arise from PVMs on a larger system).** Couple the system to an ancilla in $|0\rangle$, apply a unitary $U$, measure the ancilla projectively with $\{I\otimes|m\rangle\langle m|\}$. Then $p(m)=\operatorname{tr}\rho E_m$ with $E_m=M_m^\dagger M_m$, $M_m=(I\otimes\langle m|)U(I\otimes|0\rangle)$, and $\sum E_m=I$.
*Proof.* $p(m)=\operatorname{tr}[(I\otimes|m\rangle\langle m|)U(\rho\otimes|0\rangle\langle0|)U^\dagger]=\operatorname{tr}M_m\rho M_m^\dagger$. $\sum_mM_m^\dagger M_m=(I\otimes\langle0|)U^\dagger U(I\otimes|0\rangle)=I$. $\square$ Hence POVMs are forced by the formalism once ancillas are allowed [S7 §3.1.2].

## Neumark's theorem

**Thm 12.2 (ancilla form).** Every POVM $\{E_m\}_{m=1}^n$ on $\mathcal H$ is a PVM on $\mathcal H\otimes\mathbb C^n$ after an isometry: $V=\sum_m\sqrt{E_m}\otimes|m\rangle$, then measure $\{I\otimes|m\rangle\langle m|\}$.
*Proof.* $V^\dagger V=\sum_m\sqrt{E_m}^2=I$, so $V$ is an isometry (extend to a unitary with ancilla input $|0\rangle$). $\operatorname{tr}[(I\otimes|m\rangle\langle m|)V\rho V^\dagger]=\operatorname{tr}\sqrt{E_m}\rho\sqrt{E_m}=\operatorname{tr}\rho E_m$. $\square$ (The converse of Prop. 12.1; post-measurement state $\sqrt{E_m}\rho\sqrt{E_m}/p$, the Lüders instrument.)

**Thm 12.3 (direct-sum form, rank-1 POVMs [S5 §3.1.4]).** Let $E_m=|\tilde v_m\rangle\langle\tilde v_m|$ on $\mathbb C^d$, $m=1,\dots,n$. Embed $\mathbb C^d\subset\mathbb C^n$. There is an orthonormal basis $\{|u_m\rangle\}$ of $\mathbb C^n$ whose projections onto $\mathbb C^d$ are $|\tilde v_m\rangle$; the PVM $\{|u_m\rangle\langle u_m|\}$ applied to states in $\mathbb C^d$ reproduces the POVM.
*Proof.* The $d\times n$ matrix $M=[\tilde v_1\cdots\tilde v_n]$ satisfies $MM^\dagger=\sum_m|\tilde v_m\rangle\langle\tilde v_m|=I_d$: its $d$ rows are orthonormal in $\mathbb C^n$. Complete them by $n-d$ further orthonormal rows to a unitary $U$ ($n\times n$). Its columns $|u_m\rangle$ are orthonormal and their first $d$ entries are $|\tilde v_m\rangle$. For $|\psi\rangle\in\mathbb C^d$ (padded with zeros), $\langle u_m|\psi\rangle=\langle\tilde v_m|\psi\rangle$, so $|\langle u_m|\psi\rangle|^2=\operatorname{tr}E_m\psi$. $\square$ Preskill's illustration is exactly this completion ("the two rows are orthonormal") for a qubit POVM [S5 §3.1.4]. Higher-rank effects: split them into rank-1 pieces first.

Physical reading: the extra dimensions are real levels (e.g. other photon modes); the POVM is a projective measurement you cannot see all of from inside $\mathcal H$. Another brick of the "church of the larger Hilbert space".

## Distinguishing quantum states

**Prop. 12.4.** A set of states can be identified with certainty by some measurement iff they are mutually orthogonal (pure) or have mutually orthogonal supports (mixed).
*Proof ($\Rightarrow$, two pure states).* Suppose $\operatorname{tr}\psi E_1=1$, $\operatorname{tr}\phi E_2=1$, $E_1+E_2\le I$. Then $\langle\psi|E_2|\psi\rangle=0$, so $\sqrt{E_2}|\psi\rangle=0$. Write $|\phi\rangle=\alpha|\psi\rangle+\beta|\psi^\perp\rangle$: $\langle\phi|E_2|\phi\rangle=|\beta|^2\langle\psi^\perp|E_2|\psi^\perp\rangle\le|\beta|^2<1$ unless $\alpha=0$. $\square$
For non-orthogonal states two optimisation problems replace perfect discrimination ([13](13-no-cloning-and-state-discrimination.md)): **minimum error** (Helstrom, optimum is projective for two states) and **unambiguous** (never wrong, sometimes "don't know"; needs a three-outcome POVM on a qubit, i.e. Neumark with $n=3>d=2$). Measurements cannot increase distinguishability: the classical total-variation distance of outcome statistics is at most $T(\rho,\sigma)$, with equality for the Helstrom projector ([05](05-hilbert-space-geometry.md) Thm 5.3).

## Worked example: the trine

Three qubit states $|\psi_k\rangle$ at Bloch angles $0,120^\circ,240^\circ$ in the $xz$-plane, $|\psi_k\rangle=\cos\tfrac{\theta_k}2|0\rangle+\sin\tfrac{\theta_k}2|1\rangle$. Since $\sum_k\hat n_k=0$, $\sum_k|\psi_k\rangle\langle\psi_k|=\tfrac32I$, so $E_k=\tfrac23|\psi_k\rangle\langle\psi_k|$ is a POVM (three outcomes on a qubit: not projective). On $|\psi_0\rangle$: $p=(\tfrac23,\tfrac16,\tfrac16)$ since $|\langle\psi_0|\psi_{1,2}\rangle|^2=\cos^2 60^\circ=\tfrac14$. The *anti-trine* $E_k=\tfrac23|\psi_k^\perp\rangle\langle\psi_k^\perp|$ never fires on $\psi_k$: it rules out one of the three states with certainty (state exclusion), impossible with any two-outcome PVM. Neumark: $M=\sqrt{2/3}\,[\psi_0\ \psi_1\ \psi_2]$ has orthonormal rows $\sqrt{2/3}(1,\tfrac12,-\tfrac12)$ and $\sqrt{2/3}(0,\tfrac{\sqrt3}2,\tfrac{\sqrt3}2)$; the third row $(-1,1,-1)/\sqrt3$ completes it to a $3\times3$ orthogonal matrix (in code: QR completion, same up to sign). `channels.py` demo reproduces $p=(\tfrac16,\tfrac23,\tfrac16)$ on $|\psi_1\rangle$ both ways.

## Pitfalls

- A POVM element is not an observable's eigenprojector; POVM outcomes are not repeatable in general.
- The POVM does not determine the post-measurement state; the Lüders choice $\sqrt{E_m}$ is one of many.
- Neumark's direct-sum form needs rank-1 effects (or a rank-1 refinement); the ancilla form works always.
- Prop. 12.1 and Thm 12.2 are converses; say which direction you prove.
- "Generalised measurement" in Nielsen & Chuang means measurement operators $M_m$ (with state update); "POVM" means only the effects.

## Oral-exam questions (model answers)

1. *Define projective measurements and POVMs; why are POVMs needed?* PVM axioms, POVM axioms; they arise from PVMs on system+ancilla (Prop. 12.1) and do tasks PVMs cannot (USD on a qubit, trine exclusion).
2. *Prove Neumark's theorem.* Ancilla isometry $V=\sum\sqrt{E_m}\otimes|m\rangle$, or direct sum with orthonormal rows completed to a unitary.
3. *Show that non-orthogonal states cannot be perfectly distinguished.* Prop. 12.4.
4. *Give a qubit POVM with three outcomes and its Neumark dilation.* Trine, $\sum|\psi_k\rangle\langle\psi_k|=\tfrac32I$, $3\times3$ completion.
5. *What does a measurement do to the state? Is it fixed by the POVM?* $M_m\rho M_m^\dagger/p$, $M_m=U_m\sqrt{E_m}$: not fixed; Lüders instrument for PVMs.

## Code

`src/py/channels.py`: `is_povm`, `born`, `trine`, `neumark_isometry`, `neumark_direct_sum`, `psd_sqrt`. Tests `test_channels.py::test_trine_povm_and_neumark_dilations`: trine is a POVM (two of its elements are not), ancilla-dilation statistics equal Born probabilities on a random state, direct-sum $U$ unitary and reproducing the POVM on all three trine states. State discrimination code in `cloning.py` (note [13](13-no-cloning-and-state-discrimination.md)).
