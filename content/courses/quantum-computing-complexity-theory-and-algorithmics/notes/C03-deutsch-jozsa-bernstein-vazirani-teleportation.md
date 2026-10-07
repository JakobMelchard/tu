# C03 Deutsch, Deutsch–Jozsa, Bernstein–Vazirani, teleportation, superdense coding

The first three are one-query algorithms that show the mechanism of every later speedup: put the input in uniform superposition, let the oracle imprint a phase, and use $H^{\otimes n}$ to turn a *global* property of the phase pattern into a single basis state. Teleportation and superdense coding show that entanglement is a resource that can be traded against classical and quantum communication. References: Nielsen & Chuang 1.3.7, 1.4.3-1.4.4, 2.3 [S30]; Kaye, Laflamme, Mosca 5.3, 6.1-6.5 [S28]; Rieffel & Polak 5.3, 7.2-7.3 [S29]; de Wolf ch. 4 [S31]; primary: Deutsch [S35], Deutsch-Jozsa [S36], Bernstein-Vazirani [S37], teleportation [S42], superdense coding [S43]. Lecture section 4, in which **superdense coding comes first**, then teleportation, Deutsch, Deutsch-Jozsa, Bernstein-Vazirani [S20]. Exam 2 material.

## Definitions

**Deutsch's problem.** Given an oracle for $f:\{0,1\}\to\{0,1\}$, decide whether $f$ is constant ($f(0)=f(1)$) or balanced ($f(0)\ne f(1)$), i.e. compute $f(0)\oplus f(1)$.

**Deutsch–Jozsa problem.** Given $f:\{0,1\}^n\to\{0,1\}$ with the *promise* that $f$ is constant or balanced (equals 1 on exactly $2^{n-1}$ inputs), decide which. A *promise problem* only requires correct answers on inputs satisfying the promise.

**Bernstein–Vazirani problem.** Given $f(x) = s\cdot x = \bigoplus_i s_ix_i$ for an unknown $s\in\{0,1\}^n$, find $s$.

**Teleportation.** Alice holds an unknown $|\psi\rangle$ and one half of $|\Phi^+\rangle$ shared with Bob; using only two classical bits she transfers $|\psi\rangle$ to Bob.

**Superdense coding.** Sharing $|\Phi^+\rangle$, Alice sends one qubit and thereby communicates two classical bits.

## Results

**Deutsch's algorithm (1 query, exact)** [S35]**.** Circuit: $|0\rangle|1\rangle \xrightarrow{H\otimes H} |+\rangle|-\rangle \xrightarrow{U_f} \frac{1}{\sqrt2}\sum_x (-1)^{f(x)}|x\rangle|-\rangle \xrightarrow{H\otimes I}$ measure qubit 0.
Full state calculation: after the oracle the first qubit is $\frac{1}{\sqrt2}\big((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle\big) = (-1)^{f(0)}\frac{1}{\sqrt2}\big(|0\rangle+(-1)^{f(0)\oplus f(1)}|1\rangle\big)$, which is $\pm|+\rangle$ if constant and $\pm|-\rangle$ if balanced. $H$ maps these to $\pm|0\rangle$, $\pm|1\rangle$. Measurement outcome $= f(0)\oplus f(1)$ with probability 1. Classically two queries are necessary (one value of $f$ says nothing about the XOR).

**Deutsch–Jozsa (1 query, exact)** [S36]**.** Same circuit with $H^{\otimes n}$ on an $n$-qubit input register:
$$|0^n\rangle|-\rangle \xrightarrow{H^{\otimes n}} \frac{1}{\sqrt{2^n}}\sum_x|x\rangle|-\rangle \xrightarrow{U_f} \frac{1}{\sqrt{2^n}}\sum_x(-1)^{f(x)}|x\rangle|-\rangle \xrightarrow{H^{\otimes n}} \sum_y\Big[\frac{1}{2^n}\sum_x(-1)^{f(x)+x\cdot y}\Big]|y\rangle|-\rangle .$$
Amplitude of $|0^n\rangle$: $a_0 = \frac{1}{2^n}\sum_x(-1)^{f(x)}$. If $f$ is constant, $a_0=\pm1$ and the outcome is $0^n$ with certainty. If $f$ is balanced, the sum has $2^{n-1}$ terms $+1$ and $2^{n-1}$ terms $-1$, so $a_0 = 0$ and the outcome is never $0^n$. Decision rule: output "constant" iff the measurement gives $0^n$.

Classical comparison. Deterministic: in the worst case $2^{n-1}+1$ queries are needed (after $2^{n-1}$ identical answers both cases are still possible). Randomised with error $\varepsilon$: $O(\log 1/\varepsilon)$ queries suffice (query random inputs; a balanced $f$ returns two different values after $k$ queries except with probability $2^{1-k}$). So the DJ separation is exact-quantum vs deterministic-classical only; it is *not* evidence of a speedup over probabilistic computation. Its role is pedagogical: it isolates the interference mechanism. (In query complexity terms, B06: $Q_E(\mathrm{DJ})=1$, $D(\mathrm{DJ}) = 2^{n-1}+1$, $R(\mathrm{DJ})=O(1)$.)

**Bernstein–Vazirani (1 query, exact)** [S37]**.** For $f(x)=s\cdot x$ the same circuit gives amplitude of $|y\rangle$
$$a_y = \frac{1}{2^n}\sum_x(-1)^{s\cdot x + y\cdot x} = \frac{1}{2^n}\sum_x(-1)^{(s\oplus y)\cdot x} = \delta_{y,s},$$
using $\sum_x(-1)^{z\cdot x} = 2^n\delta_{z,0}$ (for $z\ne0$ pick a coordinate with $z_i=1$; pairing $x$ with $x\oplus e_i$ cancels the sum). The state after $H^{\otimes n}$ is exactly $|s\rangle$; measure to read $s$. Classically each query $x$ reveals one bit of information ($s\cdot x$), and $s$ has $n$ bits, so $n$ queries are necessary and sufficient (query $e_1,\dots,e_n$). Separation $1$ vs $n$, even against randomised algorithms (information-theoretic: $n$ bits cannot be learned from fewer than $n$ one-bit answers). The recursive version (Bernstein–Vazirani 1993) gives a superpolynomial separation versus randomised query algorithms.

**Teleportation** [S42]**.** Qubits: 0 = $|\psi\rangle = \alpha|0\rangle+\beta|1\rangle$ (Alice), 1 = Alice's half of $|\Phi^+\rangle$, 2 = Bob's half. Initial state
$$|\psi\rangle|\Phi^+\rangle = \frac{1}{\sqrt2}\big(\alpha|000\rangle+\alpha|011\rangle+\beta|100\rangle+\beta|111\rangle\big).$$
Alice applies CNOT$_{0\to1}$ then $H_0$:
$$\xrightarrow{\mathrm{CNOT}} \frac{1}{\sqrt2}\big(\alpha|000\rangle+\alpha|011\rangle+\beta|110\rangle+\beta|101\rangle\big)
\xrightarrow{H_0} \frac12\big[\alpha(|0\rangle+|1\rangle)(|00\rangle+|11\rangle)+\beta(|0\rangle-|1\rangle)(|10\rangle+|01\rangle)\big].$$
Regroup by Alice's two qubits $m_0m_1$:
$$=\frac12\Big[|00\rangle(\alpha|0\rangle+\beta|1\rangle)+|01\rangle(\alpha|1\rangle+\beta|0\rangle)+|10\rangle(\alpha|0\rangle-\beta|1\rangle)+|11\rangle(\alpha|1\rangle-\beta|0\rangle)\Big].$$
Alice measures $m_0m_1$ (each outcome probability $\frac14$, independent of $\alpha,\beta$) and sends the two bits; Bob applies the correction $Z^{m_0}X^{m_1}$:

| $m_0m_1$ | Bob has | correction |
|---|---|---|
| 00 | $\alpha|0\rangle+\beta|1\rangle$ | $I$ |
| 01 | $\alpha|1\rangle+\beta|0\rangle$ | $X$ |
| 10 | $\alpha|0\rangle-\beta|1\rangle$ | $Z$ |
| 11 | $\alpha|1\rangle-\beta|0\rangle$ | $ZX$ (apply $X$ then $Z$) |

Bob ends with $|\psi\rangle$ exactly. Consistency checks: (i) no faster-than-light signalling: before receiving the bits Bob's reduced state is $\frac14\sum_{m}Z^{m_0}X^{m_1}|\psi\rangle\langle\psi|X^{m_1}Z^{m_0} = I/2$, independent of $\psi$. (ii) No cloning: Alice's qubit 0 ends in a computational basis state $|m_0\rangle$; the original is destroyed. (iii) The unknown $\alpha,\beta$ never became classical information: two bits cannot encode a continuum. Resource statement: $1\ \text{ebit} + 2\ \text{cbits} \geq 1\ \text{qubit}$ of communication. Gate teleportation (Gottesman–Chuang): if Bob applies $U$ to his half of the Bell pair beforehand, he receives $U|\psi\rangle$ with corrections $UZ^{m_0}X^{m_1}U^\dagger$; for Clifford $U$ these are again Paulis, which is the basis of fault-tolerant T-gate injection.

**Superdense coding** [S43]**.** Shared $|\Phi^+\rangle$; Alice applies $I, X, Z, XZ$ (encoding $00,01,10,11$) to her qubit, mapping $|\Phi^+\rangle$ to $|\Phi^+\rangle,|\Psi^+\rangle,|\Phi^-\rangle,|\Psi^-\rangle$ (up to sign) — the four Bell states, which are orthogonal. She sends her qubit; Bob applies CNOT then $H$ (the inverse of the Bell preparation) and measures both qubits, recovering the two bits. Resource statement: $1\ \text{ebit}+1\ \text{qubit}\geq 2\ \text{cbits}$. Holevo's bound forbids more than 2 bits per qubit (with the ebit) and more than 1 without it, so both protocols are optimal. Entanglement itself carries no information (Bob's reduced state is $I/2$ regardless of the encoding); it must be *consumed* together with a message (LOCC = local operations and classical communication cannot create entanglement).

## Worked example

Bernstein–Vazirani with $n=3$, $s=101$. After $H^{\otimes3}$ and the phase oracle the amplitudes $(-1)^{s\cdot x}/\sqrt8$ are, for $x=000,\dots,111$: $s\cdot x = x_0\oplus x_2$, so signs $+,-,+,-,-,+,-,+$ (index order $000,001,010,011,100,101,110,111$). Apply $H^{\otimes3}$: amplitude of $|y\rangle$ is $\frac18\sum_x(-1)^{x\cdot(s\oplus y)}$. For $y=101$: $s\oplus y=000$, all eight signs are $+$, amplitude 1. For any other $y$ the signs cancel, e.g. $y=000$: $\sum_x(-1)^{s\cdot x} = 4-4=0$. Measurement returns $101$ with certainty after one query. Classically, querying $x=100, 010, 001$ returns $1,0,1$: three queries. In code: `bernstein_vazirani([1,0,1])` in `src/py/quantum/bernstein_vazirani.py`.

## Pitfalls

- Deutsch–Jozsa needs the promise; for an $f$ that is neither constant nor balanced the outcome $0^n$ has probability $|a_0|^2\in(0,1)$ and the algorithm's answer is meaningless.
- Claiming DJ shows exponential quantum speedup: it is only exponential versus *deterministic* classical query complexity; a randomised classical algorithm needs $O(1)$ queries.
- Bernstein–Vazirani's $n$-vs-$1$ is a genuine separation against randomised algorithms, but only linear; it is not an argument for BQP $\ne$ BPP.
- In teleportation the correction order matters for the $11$ outcome: Bob has $\alpha|1\rangle-\beta|0\rangle$; $X$ gives $\alpha|0\rangle-\beta|1\rangle$, then $Z$ gives $\alpha|0\rangle+\beta|1\rangle$. Applying $Z$ first gives $-\alpha|1\rangle-\beta|0\rangle$, then $X$: $-\alpha|0\rangle-\beta|1\rangle$, correct only up to global phase — acceptable, but write $ZX$ in the order "first $X$".
- Teleportation does not transmit the qubit instantaneously: without the two classical bits Bob has $I/2$.
- Superdense coding does not violate Holevo: the Bell pair was distributed earlier, so two qubits in total travelled to Bob.

## Exam-style questions

1. *Compute the final state of the Deutsch–Jozsa circuit for $n=2$, $f(x)=x_0$, and give the outcome distribution.* $f$ is balanced. Signs $(-1)^{x_0}$: $+,+,-,-$ for $00,01,10,11$. After $H^{\otimes2}$: $a_y = \frac14\sum_x(-1)^{x_0+x\cdot y}$; nonzero only when $y=10$ ($x\cdot y = x_0$, all signs $+$): $a_{10}=1$. Outcome $10$ with certainty; since it is not $00$ the answer is "balanced". (Indeed $f=s\cdot x$ with $s=10$, so this is also Bernstein–Vazirani.)
2. *Prove the classical lower bound of $n$ queries for Bernstein–Vazirani.* Each query $x$ yields the single bit $s\cdot x$, a linear functional of $s$ over $\mathbb{F}_2$; after $k$ queries the set of $s$ consistent with the answers is an affine subspace of dimension $\geq n-k$; for $k<n$ it has at least 2 elements, so no algorithm (even randomised, on the worst case) can determine $s$ with certainty; a randomised algorithm with error $<\frac12$ still needs $\Omega(n)$ by an information argument.
3. *Why does teleportation not contradict no-cloning?* Alice's copy is destroyed by her Bell measurement (her qubits end in $|m_0m_1\rangle$); exactly one copy of $|\psi\rangle$ exists at all times.
4. *Show that Bob's state before receiving Alice's bits is $I/2$.* The four branches have equal probability and Bob's states are $P_m|\psi\rangle$ with $P_m\in\{I,X,Z,ZX\}$; $\frac14\sum_m P_m\rho P_m^\dagger = I/2$ for any single-qubit $\rho$ (Pauli twirl: write $\rho = \frac12(I+\vec r\cdot\vec\sigma)$; each Pauli component is flipped in sign by two of the four $P_m$ and preserved by two, so it averages to zero).
5. *Alice wants to send 4 classical bits using superdense coding. What resources does she need?* Two shared Bell pairs and two transmitted qubits (2 bits per ebit-plus-qubit). By Holevo's bound, without entanglement she would need 4 transmitted qubits, and with entanglement no protocol beats 2 bits per transmitted qubit, so 2 qubits is optimal.

## Code

`src/py/quantum/deutsch_jozsa.py`: `deutsch(f)`, `deutsch_jozsa(f, n)`, `xor_oracle`, `phase_oracle`. `src/py/quantum/bernstein_vazirani.py`: `bernstein_vazirani(s)`. `src/py/quantum/teleport.py`: `teleport(state, rng)` (returns Bob's state and the classical bits), `superdense_encode(bits)`, `superdense_decode(register)`. Tests assert exact classification for all one-bit functions, random balanced/constant $f$ for $n=3,4$, random $s$ up to $n=6$, and teleportation fidelity 1 for random input states.
