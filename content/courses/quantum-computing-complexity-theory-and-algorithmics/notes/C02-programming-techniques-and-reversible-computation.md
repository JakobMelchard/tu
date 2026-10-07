# C02 Programming techniques and reversible computation

Every quantum algorithm contains classical subroutines (evaluate $f$, multiply modulo $N$, compare) that must run *inside* a unitary. This note covers how classical computation is made reversible, why intermediate results ("garbage") must be uncomputed, the two standard forms of oracles, and the gate constructions (controlled-$U$, multi-controlled gates) that the later notes use without comment. References: Nielsen & Chuang 1.4.1, 3.2.5, 4.3-4.4 [S30]; Kaye, Laflamme, Mosca ch. 1.5, 4 [S28]; Rieffel & Polak ch. 6 [S29]; Bennett 1973 and Landauer 1961 [S44]. Lecture section 3, "Preparatory concepts" - multi-controlled gates and Gray code, reversibility and garbage, phase kickback [S20]; Egly's exercises lean heavily on uncomputation [S16, S17]. Exam 2 material.

## Definitions

**Reversible gate.** A bijection $\{0,1\}^k\to\{0,1\}^k$; as a $2^k\times2^k$ permutation matrix it is unitary, so every reversible classical circuit is a quantum circuit. NOT ($X$) and CNOT are reversible; AND, OR and fan-out (copy) are not (not injective / not bijective as maps on the same number of bits).

**Toffoli** $T(a,b,c) = (a,b,c\oplus ab)$ and **Fredkin** (controlled-SWAP) are reversible. With the constant inputs $c=0$, Toffoli computes AND into the third wire; with $b=1$ it is CNOT, with $a=b=1$ it is NOT; with $b=c=1$... Toffoli with $c=1$ gives NAND $= 1\oplus ab$. Since NAND and fan-out (Toffoli$(a,1,0) = (a,1,a)$) are universal for classical circuits, **Toffoli alone is universal for reversible classical computation** given ancilla bits prepared as constants.

**Landauer's principle (motivation)** [S44]**.** Erasing one bit dissipates at least $k_BT\ln2$ of heat; only irreversible operations must dissipate. Bennett (1973) showed any computation can be done reversibly with modest overhead, which is exactly what quantum computing needs, because unitaries are reversible.

**Oracle (black box) for $f:\{0,1\}^n\to\{0,1\}^m$.** Two standard unitaries:
- Bit-flip (XOR) oracle: $U_f|x\rangle|y\rangle = |x\rangle|y\oplus f(x)\rangle$ on $n+m$ qubits. It is a permutation, self-inverse, and well defined for any $f$.
- Phase oracle ($m=1$): $O_f|x\rangle = (-1)^{f(x)}|x\rangle$ on $n$ qubits.

**Query complexity** counts uses of $U_f$ or $O_f$ and ignores the other gates (B06).

**Garbage.** Ancilla qubits that end a computation in a state depending on the input, $|x\rangle|0\rangle\mapsto|x\rangle|f(x)\rangle|g(x)\rangle$.

## Results

**Bennett's compute–copy–uncompute** [S44]**.** Given a reversible circuit $C$ with $C|x\rangle|0^a\rangle = |x\rangle|f(x)\rangle|g(x)\rangle$ (garbage $g$), the circuit
$$|x\rangle|0^a\rangle|y\rangle \xrightarrow{C} |x\rangle|f(x)\rangle|g(x)\rangle|y\rangle \xrightarrow{\text{CNOTs}} |x\rangle|f(x)\rangle|g(x)\rangle|y\oplus f(x)\rangle \xrightarrow{C^{-1}} |x\rangle|0^a\rangle|y\oplus f(x)\rangle$$
implements the clean oracle $U_f$ with garbage restored to $|0\rangle$. Cost: $2|C| + m$ gates and $a$ reusable ancillas. Since a classical circuit of size $s$ becomes a reversible circuit of size $O(s)$ with $O(s)$ ancillas (replace each AND by a Toffoli into a fresh ancilla, each fan-out by a CNOT), every polynomial-time classical $f$ has a polynomial-size $U_f$. (Bennett's later pebbling trick reduces space to $O(s^{\epsilon})$ at a polynomial time cost; not needed here.)

**Why garbage must be uncomputed.** Interference requires that different computational paths leading to the same output be *indistinguishable*. Garbage tags each path with $g(x)$ and kills the interference. Worked 2-qubit example: take $f(x)=x$ on one bit and suppose the implementation leaves the garbage $g(x)=x$ on an ancilla, i.e. we get $|x\rangle|g\rangle$ with $g = x$ (a CNOT copy). Start from $|+\rangle|0\rangle = \frac{1}{\sqrt2}(|0\rangle+|1\rangle)|0\rangle$:
- Without garbage: apply a phase oracle $O_f|x\rangle=(-1)^x|x\rangle$, get $|-\rangle|0\rangle$; then $H$ on qubit 0 gives $|1\rangle$ with certainty.
- With garbage: $\frac{1}{\sqrt2}(|0\rangle|0\rangle - |1\rangle|1\rangle)$; $H$ on qubit 0 gives $\frac12(|00\rangle+|10\rangle-|01\rangle+|11\rangle)$, so $P(\text{qubit }0 = 1) = \frac12$: the reduced state of qubit 0 was $I/2$ before $H$, the interference fringe is gone. The garbage qubit "measured" which path was taken.

**Phase kickback: phase oracle from XOR oracle.** Put the target in $|-\rangle=\frac{1}{\sqrt2}(|0\rangle-|1\rangle)$:
$$U_f|x\rangle|-\rangle = |x\rangle\frac{|f(x)\rangle-|1\oplus f(x)\rangle}{\sqrt2} = (-1)^{f(x)}|x\rangle|-\rangle .$$
The ancilla is unchanged and can be discarded; the sign moves onto $|x\rangle$. Conversely a phase oracle gives an XOR oracle by $(I\otimes H)\,\mathrm{C}\text{-}O_f\,(I\otimes H)$ where the control is the target qubit — the two oracle forms are equivalent up to one extra query.

**Controlled-$U$ from single-qubit gates and CNOT (N&C 4.3).** Write $U = e^{i\alpha}AXBXC$ with $ABC = I$ (possible for every $U\in U(2)$ via the Euler decomposition $U=e^{i\alpha}R_z(\beta)R_y(\gamma)R_z(\delta)$: $A=R_z(\beta)R_y(\gamma/2)$, $B=R_y(-\gamma/2)R_z(-(\delta+\beta)/2)$, $C=R_z((\delta-\beta)/2)$). Then apply $C$, CNOT, $B$, CNOT, $A$ to the target and $P(\alpha)$ to the control: if the control is 0 the target sees $ABC=I$; if 1 it sees $AXBXC = e^{-i\alpha}U$, and $P(\alpha)$ fixes the phase. Cost: 2 CNOTs and 4 single-qubit gates.

**Multi-controlled gates.** $C^k$-NOT with $k$ controls: using $k-1$ clean ancillas, compute the AND chain $a_1a_2$, $(a_1a_2)a_3$, … into ancillas with $k-1$ Toffolis, apply CNOT from the last ancilla, then uncompute the chain: $2(k-1)$ Toffolis + 1 CNOT, depth $O(k)$. Without ancillas $O(k^2)$ gates (Barenco et al.), with one dirty ancilla $O(k)$. Toffoli itself needs 6 CNOTs and 7 T-gates in the Clifford+T set (T-count is the standard cost measure in fault-tolerant estimates). Controlled-$U^{2^j}$ for phase estimation (C06): either $2^j$ controlled-$U$ gates (exponential, fine when $U$ is "cheap") or a direct circuit for $U^{2^j}$ (modular exponentiation by repeated squaring, polynomial, C07).

**Hadamard sandwich / basis changes.** $H^{\otimes n}$ turns a phase oracle for a linear function $f(x)=s\cdot x$ into a basis state $|s\rangle$ (C03); more generally, "apply $H^{\otimes n}$, query, apply $H^{\otimes n}$" computes the Fourier transform over $\mathbb{Z}_2^n$ of $(-1)^{f}$: amplitude of $|y\rangle$ equals $2^{-n}\sum_x(-1)^{f(x)+x\cdot y}$. The generalisation to $\mathbb{Z}_N$ is the QFT (C06).

**Quantum parallelism is not enough.** $U_f H^{\otimes n}|0^n\rangle|0\rangle = 2^{-n/2}\sum_x|x\rangle|f(x)\rangle$ contains all $2^n$ values of $f$, but a measurement returns a single random $(x,f(x))$, no better than one classical evaluation. Every algorithm needs a second ingredient: interference that concentrates amplitude on a *global property* of $f$ (constant vs balanced, period, marked element). Holevo's bound (at most $n$ classical bits are retrievable from $n$ qubits) makes this precise.

**Deferred measurement and implicit measurement.** Any measurement in the middle of a circuit can be pushed to the end by replacing classically controlled gates with quantum-controlled ones (used to analyse teleportation, C03). Unmeasured qubits at the end can be assumed measured without changing the statistics of the others (trace them out).

## Worked example

Build a clean XOR oracle for $f(a,b,c) = (a\land b)\lor c$ from Toffolis and CNOTs, for use in Grover (C04).

Identity: $u\lor v = u\oplus v\oplus uv$. With $u = ab$ (needs an ancilla) and $v=c$:
1. Toffoli$(a,b\to w)$: $w = ab$ (ancilla $w$ initialised to 0).
2. CNOT$(w\to y)$, CNOT$(c\to y)$: $y\mathrel{\oplus}= ab\oplus c$.
3. Toffoli$(w,c\to y)$: $y \mathrel{\oplus}= abc$. Now $y = ab\oplus c\oplus abc = (a\land b)\lor c$.
4. Toffoli$(a,b\to w)$ again: uncompute $w$ back to 0.
Total: 3 Toffolis, 2 CNOTs, one ancilla returned clean. Verify on $a=b=c=1$: $w=1$, $y = 1\oplus1 = 0$, then $y \oplus= 1\cdot1 = 1$ ✓ ($1\lor1=1$). On $a=1,b=0,c=0$: $w=0$, $y=0$, no change ✓. Turning this into a phase oracle: prepare $y=|-\rangle$ and run the same circuit. In `sim.py` the same oracle is available directly as `apply_permutation` of the map $(x,y)\mapsto(x,y\oplus f(x))$; the test compares the gate-level construction with the permutation.

## Pitfalls

- Forgetting to uncompute: the algorithm "works" on paper if one only looks at the output register but the interference step then fails. Always check that ancillas are returned to $|0\rangle$ *for every input*, i.e. as a unitary identity, not just for the inputs you tried.
- Using the phase oracle where the analysis needs the XOR oracle or vice versa: they differ by one Hadamard pair and one ancilla in $|-\rangle$; the query count differs by at most one.
- Ancilla count matters for space complexity: BQP is defined with polynomially many ancillas (B06). Reusing ancillas after uncomputation is what keeps width polynomial.
- Measuring the ancilla in the phase-kickback trick: it is in $|-\rangle$, unentangled, so measuring it (in any basis) has no effect on the rest; but if the oracle was *dirty* (ancilla not in an eigenstate), measuring it does damage.
- "Copy the register with CNOTs" to keep a backup: this creates entanglement, not a copy (C01 no-cloning), and acts as garbage.

## Exam-style questions

1. *Show that Toffoli is universal for reversible classical computation.* Toffoli$(a,b,1) = (a,b,\lnot(ab))$ gives NAND; Toffoli$(a,1,0)=(a,1,a)$ gives fan-out; NAND + fan-out is universal for Boolean circuits; every irreversible circuit is thus simulated by a reversible one using constant ancillas $0,1$.
2. *Given $U_f$ as an XOR oracle, construct the phase oracle and prove correctness.* Prepare ancilla $|-\rangle = HX|0\rangle$; $U_f|x\rangle|-\rangle = |x\rangle\frac{1}{\sqrt2}(|f(x)\rangle-|\overline{f(x)}\rangle) = (-1)^{f(x)}|x\rangle|-\rangle$ since for $f(x)=1$ the two terms swap sign. One query.
3. *A student implements $f(x)=x_1\oplus x_2$ as CNOT$(x_1\to a)$, CNOT$(x_2\to a)$, CNOT$(a\to y)$ and leaves $a$ alone. Which register is garbage and what happens in Deutsch–Jozsa?* $a = x_1\oplus x_2$ is garbage entangled with the input; after $H^{\otimes 2}$ on the input the amplitude of $|00\rangle$ is no longer $2^{-n}\sum_x(-1)^{f(x)}$ but is split into branches labelled by $a$, and the algorithm's "balanced" verdict becomes random. Fix: repeat the two CNOTs into $a$ after the copy to restore $a=0$.
4. *How many Toffolis does a $C^5$-NOT need with clean ancillas, and how many ancillas?* Chain: $t_1=a_1a_2$, $t_2 = t_1a_3$, $t_3=t_2a_4$, $t_4 = t_3a_5$ (4 Toffolis, 4 ancillas), CNOT$(t_4\to$target$)$, then 4 Toffolis to uncompute: 8 Toffolis, 4 ancillas (one fewer ancilla if the last Toffoli targets the output directly: $2(k-2)$ Toffolis $+1$ Toffoli, $k-2$ ancillas).
5. *Why does "compute all $2^n$ values of $f$ in superposition" not solve SAT?* A measurement of $\sum_x|x\rangle|f(x)\rangle$ yields a uniformly random $x$; the probability of hitting a satisfying $x$ is the fraction of solutions, same as random guessing. Extracting a solution needs amplitude amplification (C04), which gives only $\Theta(\sqrt{2^n})$, and this is optimal for black-box search (B06).

## Code

`src/py/quantum/sim.py`: `TOFFOLI`, `apply_controlled(U, controls, targets)` (multi-control), `apply_permutation` (classical bijections such as XOR oracles and modular multiplication). `src/py/quantum/deutsch_jozsa.py` builds both oracle forms (`xor_oracle`, `phase_oracle`) from a Python function; `test_deutsch_jozsa.py` checks the phase-kickback equivalence numerically.
