# 13 No-cloning, approximate cloning, no broadcasting, no deleting, state discrimination (TISS 2.8)

TISS 2.8: "**Proof** of no-cloning theorem, approximate cloning, no broadcasting, no deleting, distinguishing non-orthogonal quantum states" [S2], the second syllabus item that names a proof. One idea runs through the note: *unitarity preserves inner products*, so any process that would make non-orthogonal states more distinguishable is forbidden, and the optimal approximate versions are quantified by fidelities and success probabilities. The one-line gate-level no-cloning argument is in [C01](../../quantum-computing-complexity-theory-and-algorithmics/notes/C01-qubits-gates-and-measurement.md) [S62]. Sources: Jozsa §3.1-3.3 (no-cloning, distinguishing non-orthogonal states with the Helstrom-Holevo bound and a remark on unambiguous discrimination, no-signalling) [S10]; Preskill ch. 4 §4.5.2 [S8], 1998 §4.2.3 and Exercise 5.1 [S5]; Preskill ch. 2 Exercise 2.5 "Optimal measurement distinguishing two quantum states" [S6]; Wilde §3.5.4 and Exercise 3.5.8 (no-deletion) [S11]; primary Wootters-Zurek [S48], Dieks [S49], Buzek-Hillery [S50], Gisin-Massar [S51], Bruss-Ekert-Macchiavello [S52], Barnum et al. [S53], Pati-Braunstein [S54], Helstrom [S55], Ivanovic [S56], Dieks [S57], Peres [S58].

## No-cloning [S48, S49]

**Thm 13.1.** There is no unitary $U$ on $\mathcal H\otimes\mathcal H\otimes\mathcal H_M$ and blank $|b\rangle$, machine $|m\rangle$ with $U|\psi\rangle|b\rangle|m\rangle=|\psi\rangle|\psi\rangle|m_\psi\rangle$ for two states $\psi,\phi$, unless they are orthogonal or equal up to a phase.
*Proof (inner product).* Inner product of the two instances: $\langle\psi|\phi\rangle=\langle\psi|\phi\rangle^2\langle m_\psi|m_\phi\rangle$. If $\langle\psi|\phi\rangle\ne0$: $1=\langle\psi|\phi\rangle\langle m_\psi|m_\phi\rangle$, and $|\langle m_\psi|m_\phi\rangle|\le1$ forces $|\langle\psi|\phi\rangle|=1$. $\square$ So a cloner can only copy a set of mutually orthogonal states (e.g. a classical basis via CNOT).
*Proof (linearity).* If $U|0\rangle|b\rangle=|00\rangle$, $U|1\rangle|b\rangle=|11\rangle$, then $U|{+}\rangle|b\rangle=\tfrac1{\sqrt2}(|00\rangle+|11\rangle)\ne|{+}{+}\rangle$; fidelity with $|{+}{+}\rangle$ is $\tfrac12$ (`cnot_clone_fidelity`). $\square$
**General channels.** A CPTP cloner $\mathcal C(\psi)=\psi\otimes\psi$ for non-orthogonal $\psi,\phi$ contradicts monotonicity of fidelity: $F(\psi,\phi)^2=F(\psi^{\otimes2},\phi^{\otimes2})\ge F(\psi,\phi)$ fails for $0<F<1$ ([05](05-hilbert-space-geometry.md)). **Consequences:** cloning would permit perfect discrimination of non-orthogonal states (clone many times, do tomography) and superluminal signalling via a shared singlet (Bob clones his half to learn Alice's basis) [S10 §3.3, S11 Ex. 3.6.3]; it would break BB84 ([09](09-quantum-cryptography.md)).

## Approximate cloning

**Buzek-Hillery universal $1\to2$ qubit cloner [S50].** On input $\otimes$ blank $|0\rangle\otimes$ machine $|0\rangle$:
$$|0\rangle\mapsto\sqrt{\tfrac23}|00\rangle|0\rangle+\sqrt{\tfrac16}(|01\rangle+|10\rangle)|1\rangle,\quad|1\rangle\mapsto\sqrt{\tfrac23}|11\rangle|1\rangle+\sqrt{\tfrac16}(|01\rangle+|10\rangle)|0\rangle .$$
Isometry: the two images have norm $\tfrac23+\tfrac16+\tfrac16=1$ and are orthogonal (machine states and two-qubit parts are orthogonal term by term).
**Thm 13.2.** For every input $\psi$ each copy is $\rho_{\rm out}=\tfrac23\psi+\tfrac13\tfrac I2$ (Bloch vector shrunk by $\eta=\tfrac23$), so the single-copy fidelity is
$$F=\langle\psi|\rho_{\rm out}|\psi\rangle=\tfrac23+\tfrac16=\tfrac56,$$
independent of $\psi$ (universal) and equal for both copies (symmetric).
*Proof (computational basis, then covariance).* For input $|0\rangle$, trace out copy 2 and the machine: $\tfrac23|0\rangle\langle0|+\tfrac16|0\rangle\langle0|+\tfrac16|1\rangle\langle1|=\tfrac56|0\rangle\langle0|+\tfrac16|1\rangle\langle1|=\tfrac23|0\rangle\langle0|+\tfrac13\tfrac I2$. The two-copy output equals $\tfrac23P_{\rm sym}(\psi\otimes I)P_{\rm sym}$ (checked numerically), which is manifestly covariant: $U^{\otimes2}$ commutes with $P_{\rm sym}$, so the result for $|0\rangle$ transports to every $\psi=U|0\rangle$. $\square$
**Optimality (stated).** $\tfrac56$ is the maximal universal symmetric $1\to2$ fidelity [S51, S52]; for $1\to M$ qubit clones Werner's symmetric-projector cloner $\frac2{M+1}P_{\rm sym}(\rho\otimes I^{\otimes M-1})P_{\rm sym}$ is optimal with
$$F_{1\to M}=\frac{2M+1}{3M}:\quad\tfrac56,\ \tfrac79,\ \tfrac34,\dots\to\tfrac23,$$
and $\tfrac23$ is the optimal fidelity of measuring a single qubit and preparing a guess: infinitely many clones are no better than classical estimation [S52]. Optimality itself is not re-proved numerically here (it needs an SDP); the formula is checked for $M=2,3,4$.
Contrast: measure-and-prepare cloning gives $\tfrac23$; teleportation with a noisy resource needs $(1+p)/2>\tfrac23$ to beat it ([08](08-teleportation-swapping-dense-coding.md)).

## No broadcasting [S53]

Broadcasting $\rho$: produce $\rho_{AB}$ with *marginals* $\rho_A=\rho_B=\rho$ (correlations allowed), weaker than cloning $\rho\otimes\rho$. **Thm.** A set $\{\rho_i\}$ can be broadcast by one channel iff the $\rho_i$ pairwise commute. Commuting states are diagonal in a common basis and CNOT-copying that basis broadcasts them: $\operatorname{diag}(p,1-p)\mapsto p|00\rangle\langle00|+(1-p)|11\rangle\langle11|$, both marginals $\operatorname{diag}(p,1-p)$. Non-commuting sets: impossible; for pure states broadcasting reduces to cloning and Thm 13.1 applies; the mixed case uses fidelity monotonicity (proof in [S53]). `cnot_broadcast_marginals` shows success on $\operatorname{diag}(0.7,0.3)$, failure on $|{+}\rangle$ (marginal $I/2$).

## No deleting [S54]

There is no unitary with $U|\psi\rangle|\psi\rangle|A\rangle=|\psi\rangle|0\rangle|A_\psi\rangle$ for all $\psi$ *unless the ancilla ends up holding $\psi$*.
*Proof.* Inner products of two instances: $\langle\psi|\phi\rangle^2=\langle\psi|\phi\rangle\langle A_\psi|A_\phi\rangle$, so $\langle A_\psi|A_\phi\rangle=\langle\psi|\phi\rangle$ whenever $\langle\psi|\phi\rangle\ne0$. The map $\psi\mapsto A_\psi$ preserves all inner products (on a spanning set), hence is an isometry: the ancilla contains a perfect copy of $\psi$. The information was *moved*, not deleted. $\square$ Together: quantum information can be neither copied (no-cloning) nor destroyed (no-deleting) by unitary dynamics; only moved (teleportation, swap). Wilde poses this as Exercise 3.5.8 [S11].

## Distinguishing non-orthogonal states

Perfect discrimination is impossible ([12](12-generalised-measurements.md) Prop. 12.4). Two optimal relaxations:

**Minimum error (Helstrom [S55]).** States $\rho_0,\rho_1$ with priors $p_0,p_1$, two-outcome POVM $\{E_0,E_1\}$:
$$P_{\rm succ}=p_1+\operatorname{tr}E_0\Gamma,\quad\Gamma=p_0\rho_0-p_1\rho_1,\qquad\max P_{\rm succ}=\tfrac12\big(1+\|p_0\rho_0-p_1\rho_1\|_1\big),$$
attained by $E_0=$ projector onto the positive part of $\Gamma$. *Proof.* $\operatorname{tr}E_0\Gamma\le\operatorname{tr}\Gamma_+$ (as in Thm 5.3); $\operatorname{tr}\Gamma_+-\operatorname{tr}\Gamma_-=p_0-p_1$ and $\operatorname{tr}\Gamma_++\operatorname{tr}\Gamma_-=\|\Gamma\|_1$. $\square$ Pure states, $|\langle\psi|\phi\rangle|=c$: $P=\tfrac12(1+\sqrt{1-4p_0p_1c^2})$; equal priors $\tfrac12(1+\sqrt{1-c^2})=\tfrac12(1+T)$ ("Helstrom-Holevo bound" [S10 §3.2]). The optimal measurement is projective.

**Unambiguous discrimination (Ivanovic-Dieks-Peres [S56-S58]).** Never err, allow an inconclusive outcome "?". For pure $|a\rangle,|b\rangle$, equal priors, $c=|\langle a|b\rangle|$:
$$E_a=\frac{|b^\perp\rangle\langle b^\perp|}{1+c},\quad E_b=\frac{|a^\perp\rangle\langle a^\perp|}{1+c},\quad E_?=I-E_a-E_b,\qquad P_{\rm succ}=1-c .$$
*Why.* $E_a$ never fires on $b$ (orthogonal to $b$), so no error. $\langle a|E_a|a\rangle=\frac{1-c^2}{1+c}=1-c$. $E_?\ge0$ requires $\lambda_{\max}(|a^\perp\rangle\langle a^\perp|+|b^\perp\rangle\langle b^\perp|)=1+|\langle a^\perp|b^\perp\rangle|=1+c$ times the prefactor to be $\le1$: the prefactor $\frac1{1+c}$ is the largest allowed, which gives optimality within this family (full optimality: [S58]). Three outcomes on a qubit: a genuine POVM (Neumark with an extra level, [12](12-generalised-measurements.md)). Always $1-c\le\tfrac12(1+\sqrt{1-c^2})$: certainty costs success probability.

## Worked example

$|a\rangle=|0\rangle$, $|b\rangle=\cos0.4|0\rangle+\sin0.4|1\rangle$, $c=0.921$: Helstrom $P=0.6947$; USD success $0.0789$ with zero error (`cloning.py` demo). Buzek-Hillery on 200 random inputs: fidelity $0.833333$ for every input and both copies.

## Pitfalls

- No-cloning forbids copying *unknown* states from a non-orthogonal set; known states can be prepared as often as you like, orthogonal sets can be copied.
- Approximate cloning fidelity $\tfrac56$ is per copy; the joint two-copy fidelity with $\psi\otimes\psi$ is $\tfrac23$.
- Broadcasting is weaker than cloning (marginals only), yet still impossible for non-commuting sets.
- "No deleting" does not forbid erasure by discarding into an environment; it forbids unitary deletion that leaves no trace.
- Helstrom's formula uses the trace norm of $p_0\rho_0-p_1\rho_1$ (priors inside), not $T(\rho_0,\rho_1)$, when priors are unequal.

## Oral-exam questions (model answers)

1. *Prove the no-cloning theorem.* Inner product $\langle\psi|\phi\rangle=\langle\psi|\phi\rangle^2\langle m_\psi|m_\phi\rangle$; or linearity with $|{+}\rangle$; channel version via fidelity monotonicity.
2. *What is the best approximate universal cloner for qubits?* Buzek-Hillery, reduced state $\tfrac23\psi+\tfrac16I$, $F=\tfrac56$; $1\to M$: $\frac{2M+1}{3M}\to\tfrac23$ (state estimation).
3. *State no-broadcasting and give a case where broadcasting works.* Commuting sets only; CNOT broadcasts diagonal states.
4. *Prove the no-deleting theorem.* Inner products give $\langle A_\psi|A_\phi\rangle=\langle\psi|\phi\rangle$: ancilla holds a copy.
5. *How well can two non-orthogonal pure states be distinguished?* Helstrom $\tfrac12(1+\sqrt{1-c^2})$ with error; IDP $1-c$ without error, POVM $E_a\propto|b^\perp\rangle\langle b^\perp|$.

## Code

`src/py/cloning.py`: `cnot_clone_fidelity`, `buzek_hillery`, `bh_output`, `sym_projector`, `symmetric_cloner`, `single_copy_fidelity`, `cnot_broadcast_marginals`, `helstrom`, `helstrom_pure`, `usd_povm`, `usd_success`. Tests `test_cloning.py`: CNOT fidelity $1$ vs $\tfrac12$, BH isometry and $F=\tfrac56$ with reduced state $\tfrac23\psi+\tfrac13\tfrac I2$ on 50 random inputs, $1\to M$ fidelities for $M=2,3,4$, broadcasting only for commuting states, Helstrom matches the pure formula and beats 300 random projective measurements, USD error 0 and success $1-c$.
