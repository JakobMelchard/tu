# 06 Non-locality: EPR, Bell and CHSH inequalities, Tsirelson's bound (TISS 2.1)

TISS 2.1: "EPR Paradox, Bell inequalities, CHSH inequalities, entanglement vs. non-locality, Tsirelson's bound" [S2]. Proofs to own: CHSH $\le2$ for local models, quantum value $2\sqrt2$, Tsirelson $\le2\sqrt2$, and the Werner-state gap between entanglement and violation. Sources: Preskill ch. 4 §4.1-4.3 [S8] (maximal violation = "Cirel'son's inequality", §4.3.2; all pure entangled states violate, §4.3.4); Preskill 1998 §4.1 [S5]; Wilde §3.6.2 (CHSH game) [S11]; Bertlmann & Friis ch. 12-13 [S14]; primary EPR [S15], Bell [S16], CHSH [S17], Tsirelson [S18], Horodecki criterion [S19], Werner [S20]. Mermin's review [S25] is the best short read.

## EPR (1935) [S15]

Premises: (i) *realism*: if without disturbing a system we can predict a value with certainty, there is an element of reality for it; (ii) *locality*: no action at a distance; (iii) QM predictions are correct. Singlet $|\Psi^-\rangle=\frac1{\sqrt2}(|01\rangle-|10\rangle)$ is rotationally invariant: $|\Psi^-\rangle=\frac1{\sqrt2}(|\hat n,-\hat n\rangle-|-\hat n,\hat n\rangle)$ for every direction, so measuring $\hat n\cdot\vec\sigma$ on A predicts $-$(outcome) for $\hat n\cdot\vec\sigma$ on B with certainty, for *every* $\hat n$. By (i)+(ii) B carries simultaneous definite values of $\sigma_x,\sigma_z$, which QM cannot represent, so QM is "incomplete". In modern language this is **steering** (HJW, [04](04-schmidt-decomposition-and-purification.md) Cor. 4.3): A's choice of basis selects B's ensemble without changing $\rho_B=I/2$. Bell turned the philosophical claim into a testable inequality.

## Local hidden-variable (LHV) models

A behaviour $p(ab|xy)$ (inputs $x,y$, outputs $a,b\in\{\pm1\}$) is **local** if
$$p(ab|xy)=\int d\lambda\,q(\lambda)\,p(a|x,\lambda)\,p(b|y,\lambda).$$
**Lemma 6.1.** Every local behaviour is a convex mixture of deterministic local strategies $a=f(x,\lambda)$, $b=g(y,\lambda)$ (absorb the local randomness into $\lambda$). Hence linear Bell expressions are maximised on deterministic strategies: finitely many, enumerate them.

## CHSH [S17]

Correlators $E_{xy}=\langle ab\rangle$. **Thm 6.2 (CHSH).** Local models satisfy
$$S=E_{00}+E_{01}+E_{10}-E_{11},\qquad|S|\le2 .$$
*Proof.* Deterministic: $a_0(b_0+b_1)+a_1(b_0-b_1)$; one bracket is $0$, the other $\pm2$; so the value is $\pm2$. Average over $\lambda$: $|S|\le2$. $\square$ (Bell's original [S16] needs perfect anticorrelation: $|E(\hat a,\hat b)-E(\hat a,\hat c)|\le1+E(\hat b,\hat c)$; CHSH does not, hence is the experimentally relevant form.)

**Quantum value.** Singlet: $E(\hat a,\hat b)=\langle\Psi^-|\hat a\cdot\vec\sigma\otimes\hat b\cdot\vec\sigma|\Psi^-\rangle=-\hat a\cdot\hat b$. Choose coplanar $\hat a_0=\hat z$, $\hat a_1=\hat x$, $\hat b_0=-(\hat z+\hat x)/\sqrt2$, $\hat b_1=-(\hat z-\hat x)/\sqrt2$: $E_{00}=E_{01}=E_{10}=\tfrac1{\sqrt2}$, $E_{11}=-\tfrac1{\sqrt2}$, so $S=2\sqrt2$. As a game (win iff $a\oplus b=x\wedge y$ with bits): $p_{\rm win}=\tfrac12+\tfrac S8$: classical $3/4$, quantum $\cos^2\frac\pi8\approx0.854$ [S11 §3.6.2].

## Tsirelson's bound [S18]

**Thm 6.3.** For any state and any $\pm1$-valued observables ($A_x^2=B_y^2=I$, $A_x=A_x^\dagger$, $[A_x,B_y]=0$ via the tensor structure, arbitrary dimension): $|\langle\mathcal B\rangle|\le2\sqrt2$ for $\mathcal B=A_0\otimes(B_0+B_1)+A_1\otimes(B_0-B_1)$.
*Proof 1 (operator square).* Expand:
$$\mathcal B^2=A_0^2\otimes(B_0+B_1)^2+A_1^2\otimes(B_0-B_1)^2+A_0A_1\otimes(B_0+B_1)(B_0-B_1)+A_1A_0\otimes(B_0-B_1)(B_0+B_1).$$
$(B_0\pm B_1)^2=2I\pm\{B_0,B_1\}$ sum to $4I$; $(B_0+B_1)(B_0-B_1)=-[B_0,B_1]$, $(B_0-B_1)(B_0+B_1)=[B_0,B_1]$. Hence
$$\mathcal B^2=4I-[A_0,A_1]\otimes[B_0,B_1].$$
$\|[A_0,A_1]\|\le2\|A_0\|\|A_1\|=2$, likewise for $B$, so $\|\mathcal B^2\|\le8$ and $|\langle\mathcal B\rangle|\le\|\mathcal B\|\le2\sqrt2$. $\square$ Equality needs maximally anticommuting pairs on both sides (e.g. Pauli $Z,X$); with commuting observables on one side $\mathcal B^2=4I$ and the local bound returns: incompatibility on both sides is necessary for violation.
*Proof 2 (sum of squares).* $2\sqrt2\,I-\mathcal B=\frac1{\sqrt2}\big[(A_0-\tfrac{B_0+B_1}{\sqrt2})^2+(A_1-\tfrac{B_0-B_1}{\sqrt2})^2\big]\ge0$ (expand using $A^2=B^2=I$; tensor symbols suppressed). The SOS form also shows *what* achieves the bound: $A_0|\psi\rangle=\frac{B_0+B_1}{\sqrt2}|\psi\rangle$ etc., the starting point of self-testing.

## Which states violate?

**Thm 6.4 (Horodecki criterion [S19]).** For a two-qubit state with correlation tensor $T$ (note [02](02-composite-systems-and-partial-trace.md)), $\max_{\text{settings}}\langle\mathcal B\rangle=2\sqrt{m_1+m_2}$, $m_1\ge m_2$ the two largest eigenvalues of $T^TT$.
*Idea.* $\langle\mathcal B\rangle=\hat a_0^TT(\hat b_0+\hat b_1)+\hat a_1^TT(\hat b_0-\hat b_1)$; write $\hat b_0\pm\hat b_1=2\cos\theta\,\hat c,\ 2\sin\theta\,\hat c^\perp$; optimise $\hat a$'s to get $2(\cos\theta|T\hat c|+\sin\theta|T\hat c^\perp|)\le2\sqrt{|T\hat c|^2+|T\hat c^\perp|^2}\le2\sqrt{m_1+m_2}$.
Examples. $\cos\theta|00\rangle+\sin\theta|11\rangle$: $T=\operatorname{diag}(\sin2\theta,-\sin2\theta,1)$, max $2\sqrt{1+\sin^22\theta}>2$ whenever entangled: **every pure entangled two-qubit state violates CHSH** (Gisin; Preskill §4.3.4 [S8]). Werner $\rho_p=p|\Psi^-\rangle\langle\Psi^-|+(1-p)I/4$: $T=-pI$, max $2\sqrt2p$, violation iff $p>1/\sqrt2\approx0.707$.

## Entanglement vs non-locality

Separable $\Rightarrow$ local (a separable state is itself an LHV model: $\lambda$ = which product term). Converse fails for mixed states:

| Werner $p$ | status |
|---|---|
| $p\le1/3$ | separable (PPT, [10](10-entanglement.md)) |
| $1/3<p\le1/2$ | entangled, but Werner's explicit LHV model reproduces *all projective* measurements [S20] |
| $1/3<p\le1/\sqrt2$ | entangled, no CHSH violation (Thm 6.4) |
| $p>1/\sqrt2$ | CHSH-violating |

So non-locality is a strictly stronger resource than entanglement; yet entangled Werner states with $p\le1/2$ still teleport better than classically and can be distilled [S8 §4.6]. Hierarchy: Bell non-local $\subsetneq$ steerable $\subsetneq$ entangled. Also: violations need *incompatible* measurements on both sides (Thm 6.3 remark), which links to contextuality ([07](07-contextuality.md)).

**Loopholes** (context, not proofs): locality (space-like separation), detection (fair sampling), freedom of choice; all closed simultaneously in 2015 experiments. Device-independent QKD uses the CHSH value as a security certificate ([09](09-quantum-cryptography.md)).

## Worked example

Werner $p=0.9$: $T=-0.9I$, $m_1=m_2=0.81$, max $S=2\sqrt{1.62}=2.546$; multistart optimisation over all eight angles gives the same number (`bell.py` demo). At $p=0.5$: $1.414<2$ although PPT fails ($p>1/3$). Operator check: $\|\mathcal B\|$ over 500 random settings stays below $2\sqrt2$ (max seen $2.828027$) and $\mathcal B^2-(4I-[A_0,A_1]\otimes[B_0,B_1])=0$ to $10^{-15}$.

## Pitfalls

- $|S|\le2$ holds for local models of *correlators*; mixing correlators from different runs (no fair sampling) is the detection loophole.
- Tsirelson bounds quantum mechanics, not "physics": the PR box reaches $S=4$ without signalling.
- Violation certifies entanglement (device-independently); non-violation certifies nothing.
- Singlet correlator is $-\hat a\cdot\hat b$, $|\Phi^+\rangle$ has $T=\operatorname{diag}(1,-1,1)$: settings optimal for one Bell state are wrong by signs for another.
- For polarisation photons the angle on the Poincaré sphere is twice the polariser angle; the "22.5 degree" settings are $45^\circ$ on the sphere.

## Oral-exam questions (model answers)

1. *Explain the EPR argument and what Bell added.* Premises (realism, locality, completeness claim), singlet perfect anticorrelation in every basis; Bell: LHV models give testable inequalities that QM violates.
2. *Derive CHSH for local hidden variables.* Lemma 6.1 (deterministic suffices), bracket argument, convexity.
3. *Show QM reaches $2\sqrt2$.* $E=-\hat a\cdot\hat b$ and the settings above; game version $\cos^2(\pi/8)$.
4. *Prove Tsirelson's bound.* $\mathcal B^2=4I-[A_0,A_1]\otimes[B_0,B_1]$, commutator norm $\le2$; or SOS.
5. *Is every entangled state non-local?* No: Werner $1/3<p\le1/\sqrt2$ is entangled without CHSH violation (Horodecki criterion $2\sqrt2p$); Werner's LHV model for $p\le1/2$; pure entangled states always violate (Gisin).

## Code

`src/py/bell.py`: `chsh_operator`, `chsh_value`, `local_bound` (16 deterministic strategies), `tsirelson_identity_error`, `max_chsh_numeric` (multistart BFGS over 8 angles), `horodecki_max_chsh`, `werner`. Tests `test_bell.py`: local bound 2, singlet attains $2\sqrt2$, operator norm never exceeds it, numeric optimum = Horodecki formula for random pure states, Gisin formula $2\sqrt{1+\sin^22\theta}$, Werner threshold $1/\sqrt2$.
