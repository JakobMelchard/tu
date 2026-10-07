# 11 Quantum channels and operations: CPTP, Kraus, Stinespring, Choi, POVMs (TISS 2.6)

TISS 2.6: "CPTP maps, Kraus operators, Stinespring dilation, church of the larger Hilbert space, POVMs" [S2]. Board-proof chain: Kraus $\Rightarrow$ CPTP; CPTP $\Rightarrow$ Choi $\ge0$ $\Rightarrow$ Kraus; Kraus $\Leftrightarrow$ Stinespring; unitary freedom. Sources: Preskill ch. 3 §3.2-3.4 [S7] (operator-sum §3.2.1, complete positivity §3.2.6, channel-state duality §3.3.1, Stinespring §3.3.2, three channels §3.4) and 1998 §3.2-3.4 [S5]; Wilde Thm 4.4.1 (Choi-Kraus), Def. 4.4.4 (Choi operator), §5.2 (isometric extension) [S11]; Nielsen & Chuang §8.2-8.3 [S13]; Bertlmann & Friis ch. 21 [S14]; primary Stinespring [S44], Choi [S45], Kraus [S46].

## Definitions

A **channel** $\mathcal N:\mathcal L(\mathcal H_A)\to\mathcal L(\mathcal H_B)$ is linear, **trace preserving** ($\operatorname{tr}\mathcal N(X)=\operatorname{tr}X$) and **completely positive**: $\mathrm{id}_R\otimes\mathcal N$ is positive for every reference $R$ (enough: $d_R=d_A$). Linearity is forced by the ensemble interpretation ([S7 §3.2.5]); CP is forced because $\mathcal N$ may act on half of an entangled state. **Quantum operation** = CP and trace non-increasing (one branch of a measurement).
**Choi operator** $J(\mathcal N)=\sum_{ij}|i\rangle\langle j|\otimes\mathcal N(|i\rangle\langle j|)=(\mathrm{id}\otimes\mathcal N)(|\Omega\rangle\langle\Omega|)$, $|\Omega\rangle=\sum_i|ii\rangle$. Inverse: $\mathcal N(X)=\operatorname{tr}_A[J(X^T\otimes I_B)]$.

## Theorems with proofs

**Thm 11.1 (Kraus form is CPTP).** $\mathcal N(\rho)=\sum_kK_k\rho K_k^\dagger$ with $\sum_kK_k^\dagger K_k=I$ is a channel.
*Proof.* TP: $\operatorname{tr}\sum K\rho K^\dagger=\operatorname{tr}\rho\sum K^\dagger K$. CP: $(\mathrm{id}\otimes\mathcal N)(P)=\sum_k(I\otimes K_k)P(I\otimes K_k)^\dagger\ge0$ for $P\ge0$. $\square$

**Thm 11.2 (Choi [S45]).** $\mathcal N$ is CP iff $J(\mathcal N)\ge0$; TP iff $\operatorname{tr}_BJ=I_A$. Then $\mathcal N$ has a Kraus form with at most $\operatorname{rank}J\le d_Ad_B$ operators.
*Proof.* ($\Rightarrow$) $J=(\mathrm{id}\otimes\mathcal N)(|\Omega\rangle\langle\Omega|)$ and $|\Omega\rangle\langle\Omega|\ge0$. ($\Leftarrow$) Decompose $J=\sum_k|v_k\rangle\langle v_k|$ (e.g. eigenvectors scaled by $\sqrt{\lambda_k}$). Any $|v\rangle\in\mathcal H_A\otimes\mathcal H_B$ is $(I\otimes K)|\Omega\rangle$ for a unique $K:\mathcal H_A\to\mathcal H_B$, $K|i\rangle=(\langle i|\otimes I)|v\rangle$. So $J=\sum_k(I\otimes K_k)|\Omega\rangle\langle\Omega|(I\otimes K_k)^\dagger$, and by linearity (both sides agree on every $|i\rangle\langle j|$) $\mathcal N(X)=\sum_kK_kXK_k^\dagger$, which is CP by Thm 11.1. TP: $\operatorname{tr}_BJ=\sum_{ij}|i\rangle\langle j|\operatorname{tr}\mathcal N(|i\rangle\langle j|)=\sum|i\rangle\langle j|\delta_{ij}$. $\square$

**Example: transpose is positive, not CP.** $T(\rho)=\rho^T$ preserves spectra, so is positive; $J(T)=\sum|i\rangle\langle j|\otimes|j\rangle\langle i|=\mathrm{SWAP}$, eigenvalue $-1$ on the antisymmetric subspace. So $\mathrm{id}\otimes T$ maps the entangled $|\Psi^-\rangle\langle\Psi^-|$ to a non-positive operator: the physics behind PPT ([10](10-entanglement.md)).

**Thm 11.3 (Stinespring dilation [S44]).** For every channel there is an isometry $V:\mathcal H_A\to\mathcal H_B\otimes\mathcal H_E$ with $\mathcal N(\rho)=\operatorname{tr}_E V\rho V^\dagger$; equivalently a unitary $U$ on $A\otimes E$ with environment in $|0\rangle_E$ (when $B=A$): $\mathcal N(\rho)=\operatorname{tr}_E U(\rho\otimes|0\rangle\langle0|)U^\dagger$. $d_E=$ number of Kraus operators suffices.
*Proof.* Given Kraus $\{K_k\}_{k=1}^r$: $V=\sum_kK_k\otimes|k\rangle_E$. $V^\dagger V=\sum_{kl}K_k^\dagger K_l\langle k|l\rangle=\sum K^\dagger K=I$ (isometry iff TP). $\operatorname{tr}_EV\rho V^\dagger=\sum_{kl}K_k\rho K_l^\dagger\langle l|k\rangle=\mathcal N(\rho)$. An isometry extends to a unitary on $A\otimes E$ by completing the columns. Conversely, $K_k=(I\otimes\langle k|_E)U(I\otimes|0\rangle_E)$ recovers Kraus operators from any unitary model. $\square$
The **complementary channel** $\mathcal N^c(\rho)=\operatorname{tr}_BV\rho V^\dagger$ is what leaks to the environment; its matrix elements are $[\mathcal N^c(\rho)]_{kl}=\operatorname{tr}K_k\rho K_l^\dagger$. Amplitude damping with $\gamma$ has complement amplitude damping with $1-\gamma$ (tested).

**Thm 11.4 (unitary freedom).** $\{K_k\}$ and $\{L_j\}$ (padded with zeros to equal length) give the same channel iff $L_j=\sum_ku_{jk}K_k$ for a unitary $u$.
*Proof.* Same channel $\iff$ same Choi operator $\iff$ $\sum|v_k\rangle\langle v_k|=\sum|w_j\rangle\langle w_j|$ with $|v_k\rangle=(I\otimes K_k)|\Omega\rangle$; by the HJW theorem ([04](04-schmidt-decomposition-and-purification.md) Cor. 4.3) two such decompositions differ by a unitary. $\square$ Equivalently: Stinespring isometries are unique up to a unitary on $E$ (purifications of the Choi state).

**Church of the larger Hilbert space.** Every channel is a unitary on a larger space followed by discarding (Thm 11.3); every mixed state is a reduced pure state ([04](04-schmidt-decomposition-and-purification.md)); every POVM is a projective measurement on a larger space ([12](12-generalised-measurements.md)). Irreversibility and noise are ignorance about the environment.

## Three qubit channels [S7 §3.4]

| channel | Kraus | Bloch action | Choi rank |
|---|---|---|---|
| depolarising $\rho\mapsto(1-p)\rho+p\frac I2$ | $\sqrt{1-\frac{3p}4}I,\ \sqrt{\frac p4}X,\sqrt{\frac p4}Y,\sqrt{\frac p4}Z$ | $\vec r\mapsto(1-p)\vec r$ | 4 ($0<p$) |
| dephasing $\rho\mapsto(1-p)\rho+pZ\rho Z$ | $\sqrt{1-p}I,\ \sqrt pZ$ | $(x,y,z)\mapsto((1-2p)x,(1-2p)y,z)$ | 2 |
| amplitude damping $\gamma$ | $\begin{pmatrix}1&0\\0&\sqrt{1-\gamma}\end{pmatrix},\begin{pmatrix}0&\sqrt\gamma\\0&0\end{pmatrix}$ | $(\sqrt{1-\gamma}x,\sqrt{1-\gamma}y,\gamma+(1-\gamma)z)$ | 2 |

Depolarising and dephasing are **unital** ($\mathcal N(I)=I$), amplitude damping is not (fixed point $|0\rangle$). Depolarising is CP for $0\le p\le\tfrac43$ (Choi positivity), not only $p\le1$. Physical models: dephasing = random $Z$ kicks or a qubit coupled to a which-path environment ($T_2$); amplitude damping = spontaneous emission ($T_1$), Stinespring $U|10\rangle=\sqrt{1-\gamma}|10\rangle+\sqrt\gamma|01\rangle$.

## POVMs as channels

A POVM $\{E_m\}$ ($E_m\ge0$, $\sum E_m=I$) gives outcome probabilities $\operatorname{tr}\rho E_m$; as a **quantum-classical channel** $\rho\mapsto\sum_m\operatorname{tr}(\rho E_m)|m\rangle\langle m|$ (Kraus $|m\rangle\langle\phi_{m,j}|$ from $E_m=\sum_j|\phi_{m,j}\rangle\langle\phi_{m,j}|$). An **instrument** keeps the post-measurement state: operations $\mathcal N_m(\rho)=\sum_jA_{m,j}\rho A_{m,j}^\dagger$ with $\sum_jA_{m,j}^\dagger A_{m,j}=E_m$; the post-measurement state is *not* determined by the POVM alone. Details and Neumark in [12](12-generalised-measurements.md).

## Worked example

Amplitude damping $\gamma=0.4$ on $\vec r=(0.3,-0.2,0.5)$: $(0.232,-0.155,0.7)$. Choi $J=\begin{pmatrix}1&0&0&\sqrt{0.6}\\0&0&0&0\\0&0&0.4&0\\\sqrt{0.6}&0&0&0.6\end{pmatrix}$ (basis $|00\rangle,|01\rangle,|10\rangle,|11\rangle$, input first): eigenvalues $1.6,0.4,0,0$, rank 2 = number of Kraus operators; $\operatorname{tr}_BJ=\operatorname{diag}(1,1)$. The Kraus operators rebuilt from the eigenvectors of $J$ differ from the textbook ones by a unitary (Thm 11.4) but give the same channel (`kraus_from_choi`).

## Pitfalls

- Positive $\ne$ completely positive (transpose). Always check $J\ge0$, not just positivity on states.
- Choi index order: here input first. Swapping it transposes the reconstruction formula.
- Kraus operators are not unique; the channel and $\operatorname{rank}J$ are.
- A non-TP quantum operation's Stinespring map is a contraction, not an isometry.
- "Unital" is about $\mathcal N(I)=I$; TP is about the dual being unital. For qubit channels unital $\iff$ Bloch centre fixed.

## Oral-exam questions (model answers)

1. *Why must physical maps be completely positive, not just positive?* Acting on half of an entangled state; transpose counterexample, $J(T)=\mathrm{SWAP}$.
2. *Prove Choi's theorem and derive the Kraus representation.* Thm 11.2; $|v\rangle=(I\otimes K)|\Omega\rangle$ correspondence.
3. *Prove the Stinespring dilation from Kraus operators and back.* $V=\sum K_k\otimes|k\rangle$; $K_k=\langle k|U|0\rangle$; complementary channel.
4. *When do two Kraus sets describe the same channel?* Unitary mixing, via HJW on the Choi operator.
5. *Give Kraus operators and Bloch-sphere action of depolarising, dephasing, amplitude damping; which are unital?* Table; first two unital.

## Code

`src/py/channels.py`: `depolarising`, `dephasing`, `amplitude_damping`, `apply_kraus`, `is_trace_preserving`, `choi`, `is_cptp_choi`, `kraus_from_choi`, `transpose_map`, `stinespring`, `stinespring_apply(keep=0|1)`. Tests `test_channels.py`: three channels CPTP by Kraus and by Choi, Bloch actions, transpose $J=\mathrm{SWAP}$ (CP false, TP true), Kraus from Choi and unitary mixing reproduce the channel, Stinespring isometry and output, complement of amplitude damping $\gamma$ is amplitude damping $1-\gamma$.
