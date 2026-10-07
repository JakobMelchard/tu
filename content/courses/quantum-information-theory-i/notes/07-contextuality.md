# 07 Contextuality: Gleason, Kochen-Specker, Peres square, Mermin pentagram (TISS 2.2)

TISS 2.2: "Gleason's theorem, Kochen-Specker Theorem, Peres' square, Mermin's pentagram" [S2]. The two parity proofs (square, pentagram) are short enough to be asked in full; Gleason is asked as a statement plus the easy POVM version. Sources: Preskill 1998 §2.3.3 "Gleason's theorem" [S5]; Preskill ch. 2 Exercise 2.8 "The power of noncontextuality" (exactly the Peres-Mermin square) [S6]; Mermin's review [S25] (§V square, §VI star); Bertlmann & Friis ch. 12 "Hidden-Variable Theories" (mapping by chapter title only) [S14]; primary Gleason [S21], Kochen-Specker [S22], Peres [S23], Mermin [S24], Cabello et al. [S26], Busch [S59].

## Setting

A **context** is a set of mutually commuting observables (jointly measurable). A **noncontextual hidden-variable (NCHV) model** assigns to each observable $A$ a value $v(A)\in\operatorname{spec}(A)$, independent of the context in which $A$ is measured, and respecting functional relations inside every context: if $A,B,C$ commute and $C=f(A,B)$ then $v(C)=f(v(A),v(B))$. For projectors: $v(P)\in\{0,1\}$ and $\sum_iv(P_i)=1$ for every resolution of the identity $\sum_iP_i=I$ (a "KS colouring").

## Gleason's theorem [S21]

**Thm 7.1.** Let $d=\dim\mathcal H\ge3$ and $f$ a *frame function*: $f(P)\ge0$ on rank-1 projectors with $\sum_if(P_i)=1$ for every orthonormal basis. Then $f(P)=\operatorname{tr}(\rho P)$ for a unique density operator $\rho$.
Meaning: noncontextual probability assignment on projectors + $d\ge3$ $\Rightarrow$ Born rule; density operators are the only states. Corollary: no *dispersion-free* (0/1-valued) frame function exists for $d\ge3$, since $\operatorname{tr}\rho P$ is continuous in $P$ and the unit sphere is connected, so a $\{0,1\}$-valued continuous function is constant, contradicting $\sum_if(P_i)=1$ with $d\ge2$ terms. Preskill: "Gleason's theorem ... proof will not be given here" [S5 §2.3.3]; the original is long.

**Thm 7.2 (Busch's POVM version [S59], proof).** Let $v$ assign to every effect $0\le E\le I$ a number $v(E)\in[0,1]$ with $\sum_kv(E_k)=1$ for every POVM. Then $v(E)=\operatorname{tr}\rho E$; valid in every dimension including $d=2$.
*Proof.* (1) Additivity: if $E+F\le I$, both $\{E,F,I-E-F\}$ and $\{E+F,I-E-F\}$ are POVMs, so $v(E+F)=v(E)+v(F)$. (2) Hence $v(\tfrac mnE)=\tfrac mnv(E)$; $v$ is monotone ($E\le F\Rightarrow v(F)=v(E)+v(F-E)\ge v(E)$), which upgrades rational to real homogeneity. (3) Extend to all Hermitian $A=\alpha(E_+-E_-)$ by linearity; $v$ is a real-linear functional on $\mathcal L_{\rm herm}(\mathcal H)$. (4) Riesz: $v(A)=\operatorname{tr}\rho A$ for a Hermitian $\rho$; $\rho\ge0$ from $v\ge0$ on rank-1 projectors; $\operatorname{tr}\rho=v(I)=1$. $\square$ The price for the easy proof is the stronger assumption (noncontextuality on all POVMs, not just projectors).

**$d=2$ is special.** A qubit admits a deterministic noncontextual model: every basis is an antipodal pair $\{\hat n,-\hat n\}$ on the Bloch sphere and contexts do not overlap, so "value 1 on the upper hemisphere" (ties broken by $y$, then $x$) colours every basis (`bell.hemisphere_value`, tested on 500 random directions). Contextuality needs overlapping contexts, i.e. $d\ge3$.

## Kochen-Specker theorem [S22]

**Thm 7.3.** For $d\ge3$ there is a *finite* set of rank-1 projectors admitting no KS colouring. Hence no NCHV model reproduces QM, **for every state** (state-independent), and a finite set suffices (unlike Gleason, which needs the continuum).
Original: 117 vectors in $\mathbb R^3$. Short proofs are parity proofs:

**18 vectors in $\mathbb C^4$ (Cabello, Estebaranz, Garcia-Alcaine [S26]).** Nine orthogonal bases of four vectors; each of the 18 vectors lies in exactly two bases. A colouring picks exactly one vector per basis, so it marks 9 (basis, vector) incidences; but each chosen vector is counted in both of its bases, so the count is even. $9$ is odd: contradiction. $\square$ `bell.cabello_check` verifies orthogonality, the double incidence, and by exhausting all $4^9$ choices that no colouring exists.

## Peres-Mermin square [S23, S24]

Two qubits, nine $\pm1$-valued observables:
$$\begin{array}{ccc|c}X\otimes I&I\otimes X&X\otimes X&\to+I\\ I\otimes Y&Y\otimes I&Y\otimes Y&\to+I\\ X\otimes Y&Y\otimes X&Z\otimes Z&\to+I\\\hline\downarrow+I&\downarrow+I&\downarrow-I&\end{array}$$
Each row and column is a context (three mutually commuting operators: they either act on different qubits or anticommute on *both* qubits). Products: every row gives $+I$; columns 1 and 2 give $+I$; column 3 gives $(X\otimes X)(Y\otimes Y)(Z\otimes Z)=XYZ\otimes XYZ=(iI)\otimes(iI)=-I$.
**Thm 7.4.** No assignment $v:\{9\}\to\{\pm1\}$ respects all six product constraints.
*Proof.* Multiply all six constraints: the left side is $\prod_{\text{all 9}}v^2=+1$ (each observable in one row and one column); the right side is $(+1)^5(-1)=-1$. $\square$ State-independent, and the smallest KS proof with Pauli observables. Preskill's Exercise 2.8 [S6] is this array verbatim. As an experiment: measure any row or column (a two-qubit joint measurement); the product rule holds in every run for every state, while NCHV predicts it must fail in at least one of six contexts.

## Mermin's pentagram (star) [S24, S25]

Three qubits, ten observables on the five lines of a pentagram, four per line, each observable on exactly two lines:
- line 1: $XXX,\ XYY,\ YXY,\ YYX$, product $-I$;
- lines 2-5: $\{X_1,X_2,X_3,XXX\}$, $\{X_1,Y_2,Y_3,XYY\}$, $\{Y_1,X_2,Y_3,YXY\}$, $\{Y_1,Y_2,X_3,YYX\}$, each product $+I$.

Commutation: on line 1, any two of the triple products differ on exactly two qubits, where $X,Y$ anticommute twice, so they commute. Product of line 1: $(XXX)(XYY)=I\otimes XY\otimes XY=-\,I\otimes Z\otimes Z$ and $(YXY)(YYX)=I\otimes XY\otimes YX=+\,I\otimes Z\otimes Z$, total $-I$.
**Thm 7.5.** No $\pm1$ assignment satisfies the five line products. *Proof.* Multiply them: $\prod v^2=+1$ versus $(-1)(+1)^4=-1$. $\square$
Link to non-locality: the GHZ state $\frac1{\sqrt2}(|000\rangle+|111\rangle)$ is a joint eigenstate of line 1 with eigenvalues $XXX=+1$, $XYY=YXY=YYX=-1$. With the three qubits space-like separated, locality *forces* noncontextuality of the single-qubit observables, and the same parity contradiction becomes the GHZ-Mermin "Bell theorem without inequalities" [S24].

## Relation to non-locality ([06](06-non-locality-and-bell-inequalities.md))

Bell locality is noncontextuality with contexts enforced by space-like separation (Alice's observable measured with $B_0$ or $B_1$). KS is state-independent and needs no separation but only rules out *noncontextual* models; Bell rules out *local* ones and needs entangled states. Both require incompatible observables: KS contextuality is the single-system shadow of the same structure.

## Worked example

Assign $+1$ to everything in the square: rows fine, column 3 needs product $-1$, fails. Flip $Z\otimes Z\to-1$: column 3 fine, row 3 now fails. Every flip moves the defect: exactly the parity obstruction, and the exhaustive search over $2^9$ assignments (`noncontextual_assignments`) finds 0 solutions; for the pentagram 0 of $2^{10}$.

## Pitfalls

- Gleason needs $d\ge3$ (projector version); the POVM version holds for $d=2$ too. Do not claim "Gleason fails for qubits" without saying which version.
- KS contextuality is about *deterministic* noncontextual assignments; a qubit has such models.
- The square involves two-qubit joint measurements; a "context" is not a single-qubit basis there.
- "Contextual" does not mean "nonlocal"; the square is a single-site statement about a 4-dimensional system.
- Operator products inside a context must commute before "value of the product = product of values" is meaningful.

## Oral-exam questions (model answers)

1. *What does Gleason's theorem say and why does it rule out dispersion-free states?* Frame functions in $d\ge3$ are $\operatorname{tr}\rho P$; continuity + connectedness forbid $\{0,1\}$ values.
2. *Prove the POVM version of Gleason.* Additivity from two POVMs, homogeneity + monotonicity, linear extension, Riesz, positivity.
3. *State Kochen-Specker and give a parity proof.* No KS colouring of a finite set in $d\ge3$; Cabello's 18 vectors: 9 bases, double incidence, odd vs even.
4. *Present the Peres-Mermin square.* Array, commuting rows/columns, products $+I$ except column 3 $=-I$, multiply all constraints.
5. *Present Mermin's pentagram and its GHZ connection.* Ten observables, five lines, one $-I$ line; GHZ eigenvalues; locality enforces noncontextuality, giving an inequality-free Bell theorem.

## Code

`src/py/bell.py`: `PERES_MERMIN`, `square_contexts` (computes each row/column product as $\pm I$), `pentagram` (products and commutation of each line), `noncontextual_assignments` (exhaustive), `CABELLO_BASES`, `cabello_check`, `hemisphere_value`. Tests `test_bell.py`: signs $\{+,+,+,+,+,-\}$ and 0 assignments; pentagram commuting, one $-I$ line, each observable on two lines, 0 assignments; Cabello orthogonal, 18 vectors, all incidences 2, 0 colourings; qubit hemisphere model consistent.
