# 01 Pure and mixed states, operators, Bloch decomposition (TISS 1.1)

TISS 1.1: "Hilbert space, pure states, review of Dirac notation, qubits, linear operators, Hermitian operators, unitary operators, projectors, expectation values, trace, mixedness/linear entropy, time evolution, Bloch decomposition, single-qubit examples" [S2]. The QM refresher is skipped; what is kept is what the oral exam can ask you to *prove*: the density-operator axioms, the purity bounds, and the Bloch ball. Sources: Preskill ch. 2 §2.1-2.3.2 [S6] (1998 version §2.1-2.3 [S5]); Jozsa §2.1-2.2 [S10]; Wilde §3.2-3.4, §4.1 [S11]; Nielsen & Chuang §2.1-2.4 [S13]; Bertlmann & Friis ch. 11 "Density Matrices" [S14]. Gate-level qubit conventions (ordering, $H$, $S$, $T$, rotations) are in the ws2026 quantum-computing note [C01](../../quantum-computing-complexity-theory-and-algorithmics/notes/C01-qubits-gates-and-measurement.md) [S62]; not repeated here.

## Definitions

- **Pure state:** ray $\{e^{i\gamma}|\psi\rangle\}$ in a Hilbert space $\mathcal H\cong\mathbb C^d$, $\langle\psi|\psi\rangle=1$; as an operator $P_\psi=|\psi\rangle\langle\psi|$ (removes the phase).
- **Ensemble** $\{p_i,|\psi_i\rangle\}$ ($p_i\ge0$, $\sum p_i=1$, $\psi_i$ not necessarily orthogonal) $\mapsto$ **density operator** $\rho=\sum_i p_i|\psi_i\rangle\langle\psi_i|$.
- **Abstract definition:** $\rho\in\mathcal L(\mathcal H)$ is a state iff $\rho=\rho^\dagger$, $\rho\ge0$, $\operatorname{tr}\rho=1$. The set $\mathcal D(\mathcal H)$ is convex; its extreme points are the pure states.
- **Operators.** Hermitian $A=A^\dagger$ (observables, real spectrum, $A=\sum_a aP_a$); unitary $U^\dagger U=I$; projector $P=P^\dagger=P^2$. **Expectation value** $\langle A\rangle_\rho=\operatorname{tr}(\rho A)$; **Born rule** $p(a)=\operatorname{tr}(\rho P_a)$.
- **Trace:** $\operatorname{tr}A=\sum_i\langle i|A|i\rangle$, basis independent, cyclic, $\operatorname{tr}(|\phi\rangle\langle\psi|)=\langle\psi|\phi\rangle$.
- **Purity** $\gamma(\rho)=\operatorname{tr}\rho^2$; **linear entropy** $S_L(\rho)=1-\operatorname{tr}\rho^2$ (some texts normalise: $\tfrac{d}{d-1}(1-\operatorname{tr}\rho^2)\in[0,1]$; say which one you use).
- **Time evolution:** closed system $\rho(t)=U(t)\rho(0)U(t)^\dagger$, $U=e^{-iHt/\hbar}$, equivalently the von Neumann equation $i\hbar\dot\rho=[H,\rho]$.

## Results with proofs

**Prop. 1.1 (ensemble $\Rightarrow$ state).** $\rho=\sum p_i|\psi_i\rangle\langle\psi_i|$ is Hermitian, positive, trace one.
*Proof.* Hermiticity termwise. $\langle\phi|\rho|\phi\rangle=\sum_ip_i|\langle\phi|\psi_i\rangle|^2\ge0$. $\operatorname{tr}\rho=\sum p_i\langle\psi_i|\psi_i\rangle=1$. Conversely every state is an ensemble: its spectral decomposition $\rho=\sum_k\lambda_k|k\rangle\langle k|$. $\square$

**Prop. 1.2 (purity bounds).** $\tfrac1d\le\operatorname{tr}\rho^2\le1$, with $\operatorname{tr}\rho^2=1$ iff $\rho$ is pure and $\operatorname{tr}\rho^2=1/d$ iff $\rho=I/d$.
*Proof.* With eigenvalues $\lambda_k\ge0$, $\sum\lambda_k=1$: $\operatorname{tr}\rho^2=\sum\lambda_k^2\le(\max_k\lambda_k)\sum\lambda_k\le1$, equality iff one $\lambda_k=1$. Lower bound: Cauchy-Schwarz, $1=(\sum_k1\cdot\lambda_k)^2\le d\sum\lambda_k^2$, equality iff all $\lambda_k=1/d$. $\square$ Hence $0\le S_L\le1-1/d$.

**Prop. 1.3 (purity is conserved by unitary evolution).** $\operatorname{tr}(U\rho U^\dagger)^2=\operatorname{tr}\rho^2$ by cyclicity; the spectrum is invariant. Mixing (a non-unitary process) is needed to change it: $\operatorname{tr}(\lambda\rho+(1-\lambda)\sigma)^2\le\lambda\operatorname{tr}\rho^2+(1-\lambda)\operatorname{tr}\sigma^2$ (convexity of $x\mapsto\operatorname{tr}x^2$), so mixing never increases purity.

**Prop. 1.4 (Bloch decomposition, qubit).** $\{I,X,Y,Z\}$ is an orthogonal basis of $2\times2$ matrices w.r.t. $\langle A,B\rangle=\operatorname{tr}A^\dagger B$ ($\operatorname{tr}\sigma_i\sigma_j=2\delta_{ij}$). Every qubit state is
$$\rho=\tfrac12\big(I+\vec r\cdot\vec\sigma\big),\qquad r_i=\operatorname{tr}(\rho\sigma_i)\in\mathbb R,\qquad |\vec r|\le1 .$$
*Proof.* Hermitian $\Rightarrow$ real coefficients; $\operatorname{tr}\rho=1$ fixes the $I$ coefficient; $r_i$ by orthogonality. Eigenvalues of $\vec r\cdot\vec\sigma$ are $\pm|\vec r|$ (since $(\vec r\cdot\vec\sigma)^2=|\vec r|^2I$), so $\rho$ has eigenvalues $\tfrac12(1\pm|\vec r|)$ and $\rho\ge0\iff|\vec r|\le1$. Equivalently $\det\rho=\tfrac14(1-|\vec r|^2)\ge0$. $\square$
Consequences: $\operatorname{tr}\rho^2=\tfrac12(1+|\vec r|^2)$; pure $\iff|\vec r|=1$ (Bloch sphere), $I/2\iff\vec r=0$. Pure-state parametrisation $|\psi\rangle=\cos\tfrac\theta2|0\rangle+e^{i\phi}\sin\tfrac\theta2|1\rangle\mapsto\vec r=(\sin\theta\cos\phi,\sin\theta\sin\phi,\cos\theta)$; orthogonal states are antipodal.

**Prop. 1.5 (generalised Bloch decomposition, qudit).** With the $d^2-1$ generalised Gell-Mann matrices $\lambda_i$ (Hermitian, traceless, $\operatorname{tr}\lambda_i\lambda_j=2\delta_{ij}$):
$$\rho=\tfrac1dI+\tfrac12\sum_{i=1}^{d^2-1}b_i\lambda_i,\quad b_i=\operatorname{tr}\rho\lambda_i,\quad \operatorname{tr}\rho^2=\tfrac1d+\tfrac12|\vec b|^2 .$$
So $|\vec b|^2\le2(1-1/d)$, but for $d\ge3$ **not every** $\vec b$ in that ball is a state: positivity carves out a proper convex subset (the ball of radius $\sqrt{2/(d(d-1))}$ is inside, the sphere of radius $\sqrt{2(1-1/d)}$ touches it only at pure states). Composite version in [02](02-composite-systems-and-partial-trace.md).

**Prop. 1.6 (qubit dynamics = rotation).** For $H=\tfrac{\hbar\omega}2\hat n\cdot\vec\sigma$, $U(t)=e^{-i\omega t\,\hat n\cdot\vec\sigma/2}=\cos\tfrac{\omega t}2I-i\sin\tfrac{\omega t}2\hat n\cdot\vec\sigma$ and $\dot{\vec r}=\omega\,\hat n\times\vec r$: Larmor precession about $\hat n$. *Proof.* $i\hbar\dot\rho=[H,\rho]$ with $[\sigma_j,\sigma_k]=2i\epsilon_{jkl}\sigma_l$ gives $\tfrac12\dot r_k\sigma_k=-\tfrac{i\omega}{4}n_jr_k2i\epsilon_{jkl}\sigma_l$, i.e. $\dot r_l=\omega\epsilon_{jkl}n_jr_k=\omega(\hat n\times\vec r)_l$. $\square$ $SU(2)\to SO(3)$ is the 2:1 cover (angle $\omega t$ on the sphere, $\omega t/2$ in the ket).

**Ensembles are not unique.** $\tfrac12(|0\rangle\langle0|+|1\rangle\langle1|)=\tfrac12(|+\rangle\langle+|+|-\rangle\langle-|)=I/2$. Two ensembles give the same $\rho$ iff $\sqrt{p_i}|\psi_i\rangle=\sum_jU_{ij}\sqrt{q_j}|\phi_j\rangle$ for a unitary (isometry) $U$ (HJW / Schrödinger mixture theorem [S6 §2.5.5]); proof via purifications in [04](04-schmidt-decomposition-and-purification.md). Operationally only $\rho$ is observable [S6 §2.5.3].

## Worked example

$\rho=\tfrac12\begin{pmatrix}1+z&x-iy\\x+iy&1-z\end{pmatrix}$ with $\vec r=(0.3,0,0.4)$: $|\vec r|=0.5$, eigenvalues $0.75,0.25$, $\operatorname{tr}\rho^2=0.625=\tfrac12(1+0.25)$, $S_L=0.375$, normalised $0.75$. Measuring $Z$: $\langle Z\rangle=0.4$, $p(+1)=0.7$. Under $H=\tfrac{\hbar\omega}2Z$ the vector precesses about $z$: $x(t)=0.3\cos\omega t$, $y(t)=0.3\sin\omega t$, $z=0.4$; purity constant. Checked in `states.py` demo.

## Pitfalls

- $\rho$ does not determine the ensemble; "the system is in $|\psi_i\rangle$ with probability $p_i$" is one of infinitely many stories.
- Bloch angle $\theta$ vs ket angle $\theta/2$: $|0\rangle$ and $|1\rangle$ are orthogonal but $180^\circ$ apart on the sphere.
- $\operatorname{tr}\rho^2$ is not an entropy in the information-theoretic sense (not additive): $S_L(\rho\otimes\sigma)\ne S_L(\rho)+S_L(\sigma)$. Compare von Neumann in [03](03-entropy.md).
- In $d\ge3$ the "Bloch ball" is not a ball; do not claim $|\vec b|\le$ const characterises states.
- Global vs relative phase: $e^{i\gamma}|\psi\rangle$ is the same state; $\alpha|0\rangle+e^{i\varphi}\beta|1\rangle$ is not.

## Oral-exam questions (model answers)

1. *Define a density operator and show both ensemble and axiomatic definitions agree.* Prop. 1.1 both directions (spectral theorem for the converse).
2. *Prove $1/d\le\operatorname{tr}\rho^2\le1$ and characterise equality.* Prop. 1.2: $\sum\lambda^2\le\max\lambda$; Cauchy-Schwarz.
3. *Derive the Bloch ball.* Pauli basis orthogonality, eigenvalues $\tfrac12(1\pm|\vec r|)$ or $\det\rho=\tfrac14(1-|\vec r|^2)$; pure iff on the sphere; purity $\tfrac12(1+|\vec r|^2)$.
4. *What does unitary evolution do on the Bloch sphere?* Rotation, $\dot{\vec r}=\omega\hat n\times\vec r$ (Prop. 1.6); purity conserved (Prop. 1.3); only non-unitary maps (note [11](11-quantum-channels.md)) shrink $\vec r$.
5. *Generalised Bloch decomposition: what changes for $d\ge3$?* $\rho=I/d+\tfrac12\vec b\cdot\vec\lambda$, $\operatorname{tr}\rho^2=1/d+|\vec b|^2/2$; state space is a convex body that is not a ball, pure states form a $2(d-1)$-dimensional manifold inside the $(d^2-2)$-sphere.

## Code

`src/py/states.py`: `dm`, `is_state`, `purity`, `linear_entropy(normalised=)`, `bloch_vector`, `from_bloch`, `gell_mann(d)`, `generalised_bloch`, `from_generalised_bloch`, `random_state`, `random_unitary`. Tests `test_states.py`: Bloch round trip and purity formula, $|\vec r|>1$ rejected, Gell-Mann orthonormality for $d=2,3,4$, $|\vec b|^2=2(\operatorname{tr}\rho^2-1/d)$ for $d=2,3,5$.
