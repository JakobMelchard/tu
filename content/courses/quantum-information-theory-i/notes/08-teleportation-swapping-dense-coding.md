# 08 Teleportation, entanglement swapping, dense coding (TISS 2.3)

TISS 2.3: "teleportation protocol, entanglement swapping and dense coding" [S2]. The circuit-level derivation (Alice's CNOT and $H$, the $00/01/10/11$ table, correction order) is already in the ws2026 note [C03](../../quantum-computing-complexity-theory-and-algorithmics/notes/C03-deutsch-jozsa-bernstein-vazirani-teleportation.md) [S62]; this note gives the Bell-basis identity proof, which is shorter at the board, generalises to swapping, and adds the resource and noisy-resource statements an information-theory exam asks for. Sources: Preskill ch. 4 §4.4.1-4.4.3 [S8]; Jozsa §3.4 (dense coding), §4 (teleportation) [S10]; Wilde §6.1-6.3 (unit protocols and their optimality) [S11]; Nielsen & Chuang §1.3.7, §2.3 [S13]; Bertlmann & Friis ch. 14 [S14]; primary Bennett et al. 1993 [S27], Zukowski et al. 1993 [S28], Bennett-Wiesner 1992 [S29]. The sibling course 141.320 (Mon, same room) uses these protocols as building blocks for QKD and repeaters.

## Notation

$U_{m}=Z^{m_0}X^{m_1}$ for $m=(m_0,m_1)\in\{0,1\}^2$, and the Bell basis $|B_m\rangle=(U_m\otimes I)|\Phi^+\rangle$: $B_{00}=\Phi^+$, $B_{01}=\Psi^+$, $B_{10}=\Phi^-$, $B_{11}=\Psi^-$ (the last up to sign convention: $(ZX\otimes I)|\Phi^+\rangle=|\Psi^-\rangle$ with $|\Psi^-\rangle=\tfrac1{\sqrt2}(|01\rangle-|10\rangle)$).

**Lemma 8.1 (transfer identity).** $\big(\langle\Phi^+|_{12}\otimes I_3\big)\,|\psi\rangle_1|\Phi^+\rangle_{23}=\tfrac12|\psi\rangle_3$.
*Proof.* $\tfrac12\sum_{i,j}\langle ii|_{12}\,\psi_k|k\rangle_1|jj\rangle_{23}$ summed over $k$ keeps $k=j=i$: $\tfrac12\sum_i\psi_i|i\rangle_3$. $\square$
**Lemma 8.2 (transpose trick).** $(A\otimes I)|\Phi^+\rangle=(I\otimes A^T)|\Phi^+\rangle$. Componentwise: both equal $\tfrac1{\sqrt2}\sum_{ij}A_{ij}|ij\rangle$. $\square$

## Teleportation [S27]

Resource: one shared $|\Phi^+\rangle_{23}$ (Alice holds 2, Bob 3), two classical bits Alice $\to$ Bob. Alice measures qubits 1,2 in the Bell basis.
**Thm 8.3.** $|\psi\rangle_1|\Phi^+\rangle_{23}=\tfrac12\sum_m|B_m\rangle_{12}\otimes U_m^\dagger|\psi\rangle_3$. Each outcome has probability $\tfrac14$ and Bob recovers $|\psi\rangle$ by applying $U_m=Z^{m_0}X^{m_1}$ (first $X^{m_1}$, then $Z^{m_0}$).
*Proof.* $\langle B_m|=\langle\Phi^+|(U_m^\dagger\otimes I)$ on qubits 1,2; $U_m^\dagger$ acts on qubit 1, i.e. on $|\psi\rangle$, so by Lemma 8.1 the projection gives $\tfrac12U_m^\dagger|\psi\rangle_3$, of norm $\tfrac12$. The four Bell projections resolve the identity, which gives the expansion. $\square$ ($U_{11}^\dagger=XZ$: Bob holds $XZ|\psi\rangle=\alpha|1\rangle-\beta|0\rangle$, matching C03.)

Consistency: (i) **no signalling**: without the bits Bob's state is $\sum_m\tfrac14U_m^\dagger\psi U_m=I/2$ (Pauli twirl), independent of $\psi$ ([02](02-composite-systems-and-partial-trace.md) Prop. 2.3). (ii) **no cloning**: Alice's qubits end in $|B_m\rangle$, no copy of $\psi$ survives ([13](13-no-cloning-and-state-discrimination.md)). (iii) Two bits cannot carry the continuum of $(\alpha,\beta)$: the information is in the correlation, not the message.
Resource inequality: $1\ \text{ebit}+2\ \text{cbits}\ge1\ \text{qubit}$; both costs are optimal (fewer cbits would allow signalling via the no-signalling argument; fewer ebits is ruled out since LOCC cannot create entanglement) [S11 §6.3].

**Noisy resource.** Replace $\Phi^+$ by $\rho=p|\Phi^+\rangle\langle\Phi^+|+(1-p)I/4$. The protocol is linear in $\rho$: with $\Phi^+$ it is the identity channel, with $I/4$ Bob gets $I/2$. So the teleportation channel is depolarising, $\psi\mapsto p\psi+(1-p)I/2$, fidelity $(1+p)/2$ for every input. Classical measure-and-prepare achieves at most $2/3$ average fidelity for a Haar-random qubit, so the noisy resource beats classical iff $p>1/3$: exactly the entanglement threshold of this state ([10](10-entanglement.md)), including the range $1/3<p\le1/\sqrt2$ without CHSH violation ([06](06-non-locality-and-bell-inequalities.md)); Preskill discusses this for Werner states [S8 §4.6]. In general $F_{\rm avg}=(2f+1)/3$ with $f$ the fully entangled fraction.

## Entanglement swapping [S28]

Start with $|\Phi^+\rangle_{01}|\Phi^+\rangle_{23}$; a Bell measurement on 1,2 (the two middle qubits, which never interacted with 0 or 3).
**Thm 8.4.** Outcome $m$ occurs with probability $\tfrac14$ and leaves $0,3$ in $|B_m\rangle_{03}$.
*Proof.* Teleportation of qubit 1 (which is half of $\Phi^+_{01}$) through $\Phi^+_{23}$: by Thm 8.3 applied with qubit 0 as a spectator, the post-measurement state is $(I_0\otimes U_m^\dagger)|\Phi^+\rangle_{03}$. By Lemma 8.2 this is $((U_m^\dagger)^T\otimes I)|\Phi^+\rangle$, and $(U_m^\dagger)^T=(X^{m_1}Z^{m_0})^T=Z^{m_0}X^{m_1}=U_m$ ($X,Z$ real symmetric), so the state is $(U_m\otimes I)|\Phi^+\rangle=|B_m\rangle_{03}$. $\square$
Meaning: entanglement between systems that never met; after correcting with $U_m$ on qubit 3 the pair is $\Phi^+$. Uses: quantum repeaters (chain swaps over elementary links), event-ready Bell tests (the swap heralds that 0,3 are entangled). Monogamy bookkeeping: the 0-1 and 2-3 ebits are consumed, 1-2 end in $B_m$ (product with 0-3).

## Dense coding [S29]

Shared $|\Phi^+\rangle$; Alice applies $U_m$ to her qubit (2 bits of choice), sends it; Bob measures the Bell basis.
**Thm 8.5.** Bob decodes $m$ with certainty. *Proof.* $(U_m\otimes I)|\Phi^+\rangle=|B_m\rangle$, an orthonormal basis. $\square$
Resource inequality $1\ \text{ebit}+1\ \text{qubit}\ge2\ \text{cbits}$. Optimal: Holevo's bound [S9 §10.6.2] caps a $d$-dimensional quantum message at $\log d$ bits without entanglement; with prior entanglement the cap is $2\log d$, which dense coding attains. The ebit alone carries nothing (Bob's reduced state is $I/2$ before the qubit arrives, whatever $m$ is).
Teleportation and dense coding are *dual*: swapping the roles of quantum and classical channel, with the Bell basis doing the conversion in both.

## Worked example

$|\psi\rangle=\cos0.3|0\rangle+e^{0.7i}\sin0.3|1\rangle$, outcome $m=(1,0)$ ($\Phi^-$): Bob holds $Z|\psi\rangle=\cos0.3|0\rangle-e^{0.7i}\sin0.3|1\rangle$, applies $Z$, done. `protocols.teleport` computes all four branches from projectors, probabilities $0.25$ each, fidelity 1. With $p=0.5$ noise: fidelity $0.75>2/3$.

## Pitfalls

- Correction order: Bob holds $U_m^\dagger\psi=X^{m_1}Z^{m_0}\psi$; he applies $X^{m_1}$ first, then $Z^{m_0}$. The other order is off by a global sign for $m=11$ only (harmless, but say so).
- Bell-state labels vary between books; fix $|B_m\rangle=(U_m\otimes I)|\Phi^+\rangle$ on the board.
- Teleportation is not faster than light and does not move matter; it consumes the ebit.
- Swapping produces entanglement between 0 and 3 only *conditioned on* the outcome; unconditionally $\rho_{03}=I/4$.
- Dense coding does not beat Holevo: two qubits in total reached Bob (one earlier, as half of the ebit).

## Oral-exam questions (model answers)

1. *Prove that teleportation works.* Thm 8.3 via Lemma 8.1 and $\langle B_m|=\langle\Phi^+|(U_m^\dagger\otimes I)$.
2. *Why does teleportation not allow signalling or cloning?* Pauli twirl gives $I/2$ without the bits; Alice's copy is destroyed by the Bell measurement.
3. *Teleport with a Werner-type resource: what fidelity, and when is it better than classical?* Depolarising channel with parameter $p$; $(1+p)/2>2/3\iff p>1/3$.
4. *Explain entanglement swapping and its use.* Teleport half of a Bell pair; transpose trick gives $|B_m\rangle_{03}$; repeaters, heralded Bell tests.
5. *Dense coding: protocol, resource count, optimality.* Four Paulis map $\Phi^+$ to the Bell basis; 1 ebit + 1 qubit $\ge$ 2 cbits; Holevo.

## Code

`src/py/protocols.py`: `teleport(psi)` (all outcomes from Bell projectors, corrected states), `teleport_with_resource(psi, rho)`, `entanglement_swapping()`, `dense_coding()`, constant `BELL_BY_BITS`. Tests `test_protocols.py`: probabilities $\tfrac14$ and exact recovery for random inputs, swapping overlap 1 for all outcomes, dense-coding decoding table, noisy-resource fidelity $(1+p)/2$ for $p\in\{0,\tfrac13,\tfrac12,1\}$.
