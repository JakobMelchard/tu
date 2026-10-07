# 14 Oral exam question bank

> **Provenance: every question is ours.** No past exam material for 141.282 exists in public: there is no VoWi page, the follow-up course's pages are empty stubs [S4], and the weekly lecture notes are in TUWEL (not accessed). Questions are derived from the TISS outline 1.1-2.8 [S2] and the literature it names. See [00](00-exam-focus.md) §3. Exam: oral, "at the end of the lecture", format unpublished [S1].

80 questions, grouped by TISS item, each with a model answer: the key formula and the key proof step. Practise by covering the answer and speaking for two to three minutes. Items marked **(P)** are proof requests; the two the syllabus itself names are **(P!)**. Conventions: $F$ is the squared fidelity, $|B_m\rangle=(Z^{m_0}X^{m_1}\otimes I)|\Phi^+\rangle$, Choi input first.

## 1.1 States and operators (note 01)

**1.** *Density operator: definition, both ways.* Ensemble $\sum p_i|\psi_i\rangle\langle\psi_i|$; axioms Hermitian, $\ge0$, trace 1; equivalence by spectral theorem. Convex set, extreme points pure.
**2. (P)** *Bounds on purity.* $\sum\lambda_k^2\le\max\lambda\le1$, equality iff pure; Cauchy-Schwarz $1\le d\sum\lambda^2$, equality iff $I/d$. $S_L=1-\operatorname{tr}\rho^2\in[0,1-1/d]$.
**3. (P)** *Bloch ball.* $\rho=\tfrac12(I+\vec r\cdot\vec\sigma)$, eigenvalues $\tfrac12(1\pm|\vec r|)$, $\det\rho=\tfrac14(1-|\vec r|^2)$; pure iff $|\vec r|=1$; $\operatorname{tr}\rho^2=\tfrac12(1+r^2)$.
**4.** *Unitary evolution on the Bloch sphere.* $H=\tfrac{\hbar\omega}2\hat n\cdot\vec\sigma$ gives $\dot{\vec r}=\omega\hat n\times\vec r$: rotation; spectrum and purity conserved.
**5.** *Two ensembles, same $\rho$: example and criterion.* $\{|0\rangle,|1\rangle\}$ and $\{|{\pm}\rangle\}$ both give $I/2$; HJW: $\sqrt{p_i}\psi_i=\sum_jU_{ij}\sqrt{q_j}\phi_j$.
**6.** *Qudit Bloch vector: why not a ball?* $\rho=I/d+\tfrac12\vec b\cdot\vec\lambda$, $|\vec b|^2=2(\operatorname{tr}\rho^2-1/d)$; positivity cuts a convex body between radii $\sqrt{2/(d(d-1))}$ and $\sqrt{2(d-1)/d}$.

## 1.2 Composite systems (note 02)

**7. (P)** *Why the partial trace?* Unique $\rho_A$ with $\operatorname{tr}\rho_AX=\operatorname{tr}\rho_{AB}(X\otimes I)$ for all $X$; take $X=|k\rangle\langle i|$.
**8. (P)** *Local operations on B do not change $\rho_A$.* Cyclicity inside $\operatorname{tr}_B$ for operators on $B$; applies to unitaries, channels, measurements averaged over outcomes.
**9.** *Reduced state of a pure bipartite state.* $\rho_A=CC^\dagger$, $\rho_B=C^TC^*$, same nonzero spectrum; pure iff product.
**10.** *Two-qubit Bloch decomposition.* $\tfrac14(I+\vec a\cdot\vec\sigma\otimes I+I\otimes\vec b\cdot\vec\sigma+\sum t_{ij}\sigma_i\otimes\sigma_j)$; marginals from $\vec a,\vec b$; purity $\tfrac14(1+a^2+b^2+\|T\|^2)$; product $\Rightarrow T=\vec a\vec b^T$.
**11.** *Local unitaries on $(\vec a,\vec b,T)$.* $SO(3)$ rotations, $T\mapsto O_ATO_B^T$; signed SVD diagonalises $T$.
**12.** *Same marginals, different states.* $\Phi^+$ vs $\tfrac12(|00\rangle\langle00|+|11\rangle\langle11|)$: $T=\operatorname{diag}(1,-1,1)$ vs $\operatorname{diag}(0,0,1)$.

## 1.3 Entropy (note 03)

**13. (P)** *Klein's inequality.* Eigenbases, $P_{ij}=|\langle i|j\rangle|^2$ doubly stochastic, concavity of $\log$, then $\ln x\le x-1$; equality iff $\rho=\sigma$.
**14. (P)** *Subadditivity.* $I(A:B)=D(\rho_{AB}\|\rho_A\otimes\rho_B)\ge0$, using $\log(\rho_A\otimes\rho_B)=\log\rho_A\otimes I+I\otimes\log\rho_B$.
**15. (P)** *Araki-Lieb.* Purify to $ABC$: $S(AB)=S(C)$, $S(A)=S(BC)\le S(B)+S(C)$. Equality for pure $AB$.
**16. (P)** *Concavity.* $\rho_{AB}=\sum p_i\rho_i\otimes|i\rangle\langle i|$, $S(AB)=H(p)+\sum p_iS(\rho_i)$, subadditivity.
**17.** *Upper bound on the entropy of a mixture.* $S(\sum p_i\rho_i)\le H(p)+\sum p_iS(\rho_i)$, equality iff orthogonal supports; pure case via purification and dephasing.
**18.** *Negative conditional entropy.* $S(A|B)=-1$ for Bell states; $\ge0$ for separable; sufficient not necessary for entanglement (Werner $p=0.6$: $+0.357$).
**19.** *Strong subadditivity: statement and equivalents.* $I(A:C|B)\ge0$; conditioning reduces entropy; monotonicity of $D$ under partial trace/channels (Lieb-Ruskai, no proof).
**20.** *Why is relative entropy not a metric; what does it bound?* Asymmetric, no triangle inequality, can be infinite; Pinsker $D\ge\frac2{\ln2}T^2$; Stein exponent.

## 1.4 Schmidt and purification (note 04)

**21. (P!)** *Schmidt decomposition theorem with proof.* SVD $C=U\Sigma V^\dagger$, $|a_k\rangle=U|k\rangle$, $|b_k\rangle=V^*|k\rangle$; or via spectral decomposition of $\rho_A$ and $|\tilde b_k\rangle=(\langle a_k|\otimes I)|\psi\rangle$ orthogonal with norms $p_k$.
**22.** *Uniqueness of the Schmidt decomposition.* Coefficients unique; vectors up to phases, or $U\otimes U^*$ in degenerate blocks ($\Phi^+$ invariant under $U\otimes U^*$).
**23. (P)** *Purification: existence and minimal dimension.* $\sum\sqrt{p_k}|k\rangle|k\rangle$, $d_R=\operatorname{rank}\rho$; canonical $(\sqrt\rho\otimes I)|\Omega\rangle$.
**24. (P)** *All purifications are related by isometries on R.* Schmidt both; same $|a_k\rangle$ and $\sqrt{p_k}$; map $|r_k\rangle\mapsto|r'_k\rangle$.
**25.** *HJW and steering.* Two ensembles of $\rho$ relate by a unitary; Bob measuring $R$ prepares any ensemble for Alice without changing $\rho_A$.
**26.** *Does a tripartite Schmidt decomposition exist?* No: W state $\tfrac1{\sqrt3}(|001\rangle+|010\rangle+|100\rangle)$ is not of the form $\sum s_k|a_kb_kc_k\rangle$; multipartite classes (GHZ vs W) are inequivalent.

## 1.5 Geometry (note 05)

**27. (P)** *Uhlmann's theorem.* Canonical purifications, others via $I\otimes U$, transpose trick: overlap $\operatorname{tr}(\sqrt\rho\sqrt\sigma U^T)$, max over $U$ is $\|\sqrt\rho\sqrt\sigma\|_1$ (SVD lemma).
**28.** *Properties of fidelity that follow from Uhlmann.* Symmetry, $F=1$ iff equal, monotone under channels (Stinespring), multiplicative, $F(\psi,\sigma)=\langle\psi|\sigma|\psi\rangle$.
**29. (P)** *Trace distance as optimal bias.* Jordan decomposition $\rho-\sigma=Q-S$, $\operatorname{tr}Q=T$; projector onto $Q$'s support; qubits $T=\tfrac12|\vec r-\vec s|$.
**30. (P)** *Fuchs-van de Graaf.* Pure: $T=\sqrt{1-F}$ from the $2\times2$ matrix with eigenvalues $\pm\sin\theta$; mixed upper bound by purification + monotonicity; lower bound via fidelity-achieving POVM and $\sum(\sqrt p-\sqrt q)^2\le\sum|p-q|$.
**31.** *Bures distance and angle.* $D_B^2=2(1-\sqrt F)=\min\|\psi_\rho-\psi_\sigma\|^2$; angle $\arccos\sqrt F$; infinitesimally $\tfrac14$ quantum Fisher information.
**32.** *Qubit fidelity formula.* $F=\operatorname{tr}\rho\sigma+2\sqrt{\det\rho\det\sigma}=\tfrac12(1+\vec r\cdot\vec s+\sqrt{(1-r^2)(1-s^2)})$.

## 2.1 Non-locality (note 06)

**33.** *EPR argument.* Realism + locality + perfect singlet anticorrelation in every basis $\Rightarrow$ simultaneous elements of reality for non-commuting spins $\Rightarrow$ QM incomplete.
**34. (P)** *CHSH for LHV.* Deterministic strategies suffice (convexity); $a_0(b_0+b_1)+a_1(b_0-b_1)=\pm2$.
**35.** *Quantum violation.* Singlet $E=-\hat a\cdot\hat b$; $\hat a_0=\hat z$, $\hat a_1=\hat x$, $\hat b_{0,1}=-(\hat z\pm\hat x)/\sqrt2$: $S=2\sqrt2$; game $\cos^2\frac\pi8$ vs $\tfrac34$.
**36. (P)** *Tsirelson's bound.* $\mathcal B^2=4I-[A_0,A_1]\otimes[B_0,B_1]$, $\|[\cdot,\cdot]\|\le2$; or SOS $2\sqrt2-\mathcal B=\frac1{\sqrt2}\sum(\ldots)^2$.
**37.** *Horodecki criterion and Gisin's theorem.* $\max S=2\sqrt{m_1+m_2}$ from $T^TT$; $\cos\theta|00\rangle+\sin\theta|11\rangle$: $2\sqrt{1+\sin^22\theta}>2$.
**38.** *Entanglement vs non-locality.* Werner: separable $p\le\tfrac13$; entangled but LHV for projective measurements $p\le\tfrac12$; no CHSH violation $p\le\tfrac1{\sqrt2}$.
**39.** *Why must measurements be incompatible for a violation?* If $[A_0,A_1]=0$ then $\mathcal B^2=4I$ and $|S|\le2$; joint measurability gives a local model.

## 2.2 Contextuality (note 07)

**40.** *Gleason: statement and consequence.* $d\ge3$ frame functions are $\operatorname{tr}\rho P$; continuity forbids 0/1 assignments.
**41. (P)** *Gleason for POVMs.* Additivity from two POVMs, homogeneity via monotonicity, linear extension, Riesz, positivity.
**42.** *Kochen-Specker and a parity proof.* Finite uncolourable set; Cabello's 18 vectors in 9 bases, each vector twice: 9 odd vs even.
**43. (P)** *Peres-Mermin square.* Rows $XI,IX,XX$; $IY,YI,YY$; $XY,YX,ZZ$; row products $+I$, columns $+I,+I,-I$; multiply constraints: $+1=-1$.
**44. (P)** *Mermin pentagram.* $XXX,XYY,YXY,YYX$ product $-I$; four lines with single-qubit observables, product $+I$; every observable on two lines.
**45.** *Why does a qubit admit a noncontextual model?* Contexts (antipodal pairs) do not overlap; hemisphere assignment.
**46.** *Contextuality vs non-locality.* Locality enforces noncontextuality across space-like separation; GHZ is the pentagram with separated qubits; KS is state-independent.

## 2.3 Teleportation and friends (note 08)

**47. (P)** *Teleportation.* $|\psi\rangle|\Phi^+\rangle=\tfrac12\sum_m|B_m\rangle U_m^\dagger|\psi\rangle$ from $\langle\Phi^+|_{12}|\psi\rangle_1|\Phi^+\rangle_{23}=\tfrac12|\psi\rangle_3$; probabilities $\tfrac14$; Bob applies $U_m$.
**48.** *No signalling and no cloning in teleportation.* Without bits Bob holds $I/2$ (Pauli twirl); Alice's qubits end in $|B_m\rangle$.
**49.** *Noisy resource.* $p\Phi^++(1-p)I/4$: depolarising channel, $F=(1+p)/2>\tfrac23$ iff $p>\tfrac13$.
**50. (P)** *Entanglement swapping.* Teleport half of $\Phi^+_{01}$: $(I\otimes U_m^\dagger)|\Phi^+\rangle_{03}=(U_m\otimes I)|\Phi^+\rangle=|B_m\rangle$; repeaters, heralding.
**51.** *Dense coding and its optimality.* $U_m$ maps $\Phi^+$ to the Bell basis; 1 ebit + 1 qubit $\ge$ 2 cbits; Holevo caps at $2\log d$ with entanglement.

## 2.4 Quantum cryptography (note 09)

**52.** *BB84 steps.* Random bits and bases, measure, sift ($\tfrac12$), estimate QBER, error correction, privacy amplification; authenticated classical channel.
**53. (P)** *Intercept-resend.* Wrong basis w.p. $\tfrac12$, then error w.p. $\tfrac12$: $Q=\tfrac14$; Eve's information $\tfrac12$ bit per sifted bit.
**54. (P)** *Information gain implies disturbance.* $\langle\psi|\phi\rangle=\langle\psi|\phi\rangle\langle e_\psi|e_\phi\rangle$ forces $\langle e_\psi|e_\phi\rangle=1$ for non-orthogonal states.
**55.** *E91.* Singlets, Alice $\{0,\tfrac\pi4,\tfrac\pi2\}$, Bob $\{\tfrac\pi4,\tfrac\pi2,\tfrac{3\pi}4\}$; equal angles give key; $S=-2\sqrt2$; monogamy; $|S|=\sqrt2$ after intercept.
**56.** *BB84 vs E91 (BBM92) and the 11% threshold.* Entanglement-based BB84 has identical statistics; $r=1-2h(Q)>0$ for $Q<11\%$.

## 2.5 Entanglement (note 10)

**57.** *Separable mixed states and why correlation is not entanglement.* Convex hull of products; $\tfrac12(|00\rangle\langle00|+|11\rangle\langle11|)$ has $I=1$; separable $\Rightarrow I\le\log d$.
**58. (P)** *PPT criterion.* $\sum p_i\rho_i\otimes(\rho_i^B)^T\ge0$; sufficient for $2\times2$, $2\times3$ (decomposable positive maps); bound entanglement beyond.
**59. (P)** *Werner threshold both ways.* $\lambda_{\min}(\rho_p^{T_B})=\tfrac{1-3p}4$; for $p=\tfrac13$ average of $|\hat n,-\hat n\rangle$ over the sphere; mix with $I/4$.
**60. (P)** *Witness existence and construction.* Hahn-Banach on the compact convex separable set; $(|v\rangle\langle v|)^{T_B}$ from a negative eigenvector.
**61.** *Fidelity witness.* $W=s_1^2I-|\psi\rangle\langle\psi|$ since $\max|\langle ab|\psi\rangle|^2=s_1^2$; for $\Psi^-$: $\operatorname{tr}W\rho_p=\tfrac{1-3p}4$.
**62.** *Entropy of entanglement: why the right measure for pure states?* LU invariant, LOCC monotone, additive, asymptotic conversion rate to Bell pairs.
**63.** *Negativity.* $N=\tfrac12(\|\rho^{T_B}\|_1-1)$; Werner $(3p-1)/4$; zero on PPT, so blind to bound entanglement; equals zero iff concurrence zero for two qubits.

## 2.6 Channels (note 11)

**64. (P)** *Why complete positivity; transpose example.* Acting on half of an entangled state; $J(T)=\mathrm{SWAP}$ has eigenvalue $-1$.
**65. (P)** *Choi's theorem.* $J=(\mathrm{id}\otimes\mathcal N)(|\Omega\rangle\langle\Omega|)\ge0$; eigenvectors $|v_k\rangle=(I\otimes K_k)|\Omega\rangle$ give Kraus; TP iff $\operatorname{tr}_BJ=I$.
**66. (P)** *Stinespring.* $V=\sum K_k\otimes|k\rangle$, $V^\dagger V=\sum K^\dagger K=I$; $K_k=\langle k|U|0\rangle$; complementary channel.
**67.** *Kraus freedom.* Same channel iff $L_j=\sum u_{jk}K_k$ (HJW on the Choi operator); minimal number $\operatorname{rank}J$.
**68.** *Three qubit channels.* Depolarising $\vec r\mapsto(1-p)\vec r$, dephasing shrinks $x,y$ by $1-2p$, amplitude damping $(\sqrt{1-\gamma}x,\sqrt{1-\gamma}y,\gamma+(1-\gamma)z)$; first two unital.

## 2.7 Generalised measurements (note 12)

**69. (P)** *POVM from a PVM on system+ancilla.* $M_m=(I\otimes\langle m|)U(I\otimes|0\rangle)$, $p(m)=\operatorname{tr}M_m\rho M_m^\dagger$, $\sum M_m^\dagger M_m=I$.
**70. (P)** *Neumark's theorem, both forms.* $V=\sum\sqrt{E_m}\otimes|m\rangle$ is an isometry, ancilla PVM reproduces $\operatorname{tr}\rho E_m$; direct sum: rows of $[\tilde v_1\cdots\tilde v_n]$ orthonormal, complete to a unitary, columns project to $\tilde v_m$.
**71. (P)** *Non-orthogonal states cannot be perfectly distinguished.* $\sqrt{E_2}|\psi\rangle=0\Rightarrow\langle\phi|E_2|\phi\rangle\le|\beta|^2<1$.
**72.** *A three-outcome qubit POVM and what it does that no PVM can.* Trine $\tfrac23|\psi_k\rangle\langle\psi_k|$, $\sum|\psi_k\rangle\langle\psi_k|=\tfrac32I$; anti-trine excludes one state with certainty; USD needs three outcomes.
**73.** *Is the post-measurement state determined by the POVM?* No: $M_m=U_m\sqrt{E_m}$; Lüders choice $\sqrt{E_m}\rho\sqrt{E_m}/p$; instruments.

## 2.8 No-cloning and discrimination (note 13)

**74. (P!)** *No-cloning theorem with proof.* $\langle\psi|\phi\rangle=\langle\psi|\phi\rangle^2\langle m_\psi|m_\phi\rangle\Rightarrow\langle\psi|\phi\rangle\in\{0\}$ or modulus 1; linearity with $|{+}\rangle$ gives a Bell state; channel version $F^2\ge F$ contradiction.
**75.** *Consequences of cloning if it were possible.* Signalling through a shared singlet, perfect discrimination by tomography of copies, broken BB84.
**76. (P)** *Buzek-Hillery cloner.* Isometry on input, blank, machine; each copy $\tfrac23\psi+\tfrac13\tfrac I2$, $F=\tfrac56$ for every input; $1\to M$: $\frac{2M+1}{3M}\to\tfrac23$ = estimation limit.
**77.** *No broadcasting.* Marginals only; possible iff pairwise commuting; CNOT broadcasts diagonal states, not $|{+}\rangle$.
**78. (P)** *No deleting.* $\langle A_\psi|A_\phi\rangle=\langle\psi|\phi\rangle$: the ancilla holds a copy; information moved, not erased.
**79. (P)** *Helstrom bound.* $P=p_1+\operatorname{tr}E_0\Gamma\le p_1+\operatorname{tr}\Gamma_+=\tfrac12(1+\|p_0\rho_0-p_1\rho_1\|_1)$; pure equal priors $\tfrac12(1+\sqrt{1-c^2})$.
**80.** *Unambiguous discrimination.* $E_a=|b^\perp\rangle\langle b^\perp|/(1+c)$, $E_b$ likewise, $E_?=I-E_a-E_b\ge0$ fixes the prefactor; $P=1-c\le$ Helstrom; never wrong.

## Cross-cutting

- *Church of the larger Hilbert space in three theorems:* purification (04), Stinespring (11), Neumark (12).
- *Unitarity preserves inner products, and what it forbids:* no-cloning, no-deleting, information-disturbance (13, 09).
- *Everything monotone under channels:* $F\uparrow$, $T\downarrow$, $D\downarrow$, $I(A:B)\downarrow$ (05, 03).
- *Werner state as the running example:* $p>\tfrac13$ entangled, $p>\tfrac12$ no LHV model known to Werner, $p>\tfrac1{\sqrt2}$ CHSH, teleportation fidelity $(1+p)/2$ (06, 08, 10).
