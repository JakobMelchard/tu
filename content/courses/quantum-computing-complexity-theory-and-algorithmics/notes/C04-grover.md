# C04 Grover's algorithm and amplitude amplification

Grover's algorithm finds a marked element among $N=2^n$ with $O(\sqrt N)$ oracle queries instead of the classical $\Theta(N)$. It is the only *provably optimal* quantum speedup for a generic (unstructured) problem, and it is quadratic, not exponential: this matters enormously for the relation between BQP and NP (B06). References: Nielsen & Chuang ch. 6 [S30]; Kaye, Laflamme, Mosca ch. 8 [S28]; Rieffel & Polak ch. 9 [S29]; de Wolf ch. 9-10 [S31]; primary: Grover [S39], BBBV [S41], amplitude amplification [S46], BBHT [S47]. Lecture section 5 [S20]. The oral protocols show Grover and amplitude amplification are the two algorithms Egly asks about most [S19, S21]. Exam 2 material.

## Definitions

**Unstructured search.** Given a phase oracle $O_f|x\rangle = (-1)^{f(x)}|x\rangle$ for $f:\{0,1\}^n\to\{0,1\}$ with $M\geq1$ marked inputs ($f(x)=1$), find an $x$ with $f(x)=1$.

**Good and bad states.** With $N=2^n$, define the normalised superpositions of marked and unmarked inputs
$$|\beta\rangle = \frac{1}{\sqrt M}\sum_{f(x)=1}|x\rangle,\qquad |\alpha\rangle=\frac{1}{\sqrt{N-M}}\sum_{f(x)=0}|x\rangle,$$
and the uniform state $|\psi\rangle = H^{\otimes n}|0^n\rangle = \frac{1}{\sqrt N}\sum_x|x\rangle = \cos\frac\theta2|\alpha\rangle+\sin\frac\theta2|\beta\rangle$ with $\sin\frac\theta2 = \sqrt{M/N}$.

**Grover iteration.** $G = D\,O_f$ with the *diffusion* (inversion about the mean) operator $D = 2|\psi\rangle\langle\psi|-I = H^{\otimes n}(2|0^n\rangle\langle0^n|-I)H^{\otimes n}$ — the form the lecture uses [S20, §5.1]. The middle factor is "$-1$ on every state except $|0^n\rangle$", implemented as $X^{\otimes n}\,(\text{C}^{n-1}Z)\,X^{\otimes n}$. **The gate-level circuit realises $-D$, not $D$:**
$$-D \;=\; H^{\otimes n}X^{\otimes n}\,C^{n-1}Z\,X^{\otimes n}H^{\otimes n}.$$
The sign is a global phase per iteration and harmless, but writing $+D$ is the standard slip.

**Amplitude amplification (Brassard–Høyer–Mosca–Tapp [S46]).** Replace $H^{\otimes n}$ by any unitary $A$ with $A|0\rangle = \sin\frac\theta2|\beta\rangle+\cos\frac\theta2|\alpha\rangle$ (success probability $p = \sin^2\frac\theta2$ of the algorithm $A$); the iterate is $Q = -A S_0 A^\dagger S_f$ with $S_0 = I - 2|0\rangle\langle0|$, $S_f = O_f$. Grover is the case $A = H^{\otimes n}$.

## Results

**Theorem (two-dimensional rotation).** $G$ preserves the plane $\mathrm{span}\{|\alpha\rangle,|\beta\rangle\}$ and acts on it as a rotation by $\theta$:
$$G^k|\psi\rangle = \cos\Big(\frac{2k+1}{2}\theta\Big)|\alpha\rangle+\sin\Big(\frac{2k+1}{2}\theta\Big)|\beta\rangle .$$
*Proof.* On the plane, $O_f$ is the reflection about $|\alpha\rangle$ (it negates $|\beta\rangle$): $O_f = I - 2|\beta\rangle\langle\beta|$. $D = 2|\psi\rangle\langle\psi|-I$ is minus the reflection about the line orthogonal to $|\psi\rangle$, i.e. the reflection about $|\psi\rangle$. The product of two reflections about lines at angle $\theta/2$ is a rotation by $\theta$ (in the direction from $|\alpha\rangle$ towards $|\psi\rangle$, i.e. towards $|\beta\rangle$). Start angle $\theta/2$, after $k$ iterations angle $(2k+1)\theta/2$. $\square$

**Success probability after $k$ iterations.** $P_k = \sin^2\big(\frac{2k+1}{2}\theta\big)$, $\theta = 2\arcsin\sqrt{M/N}$. It is maximised when $(2k+1)\theta/2\approx\pi/2$:
$$k_{\text{opt}} = \Big\lfloor\frac{\pi}{2\theta}-\frac12\Big\rceil \approx \frac{\pi}{4}\sqrt{\frac NM}\quad(M\ll N),$$
(the lecture states it as $\lfloor\frac\pi4\sqrt{2^n}\rfloor$ for one solution and $\lfloor\frac\pi4\sqrt{2^n/k}\rfloor$ for $k$ solutions [S20, §5.1]; the two agree to within one iteration)
with $P_{k_{\text{opt}}}\geq 1-M/N$ (the residual angle is at most $\theta/2$). **Overshooting:** $P_k$ is periodic in $k$; continuing past $k_{\text{opt}}$ *decreases* the success probability ("cooking too long"), reaching $\approx0$ at $2k_{\text{opt}}+1$. For $M = N/4$: $\theta = \pi/3$, one iteration gives $\sin^2(\pi/2)=1$ exactly. For $M > N/2$... $\theta>\pi/2$ and the first iteration already overshoots; then just sample classically ($P\geq\frac12$ per sample).

**Unknown $M$.** (i) Quantum counting: $G$ has eigenvalues $e^{\pm i\theta}$ on the plane; phase estimation (C06) of $G$ on $|\psi\rangle$ with $t$ bits estimates $\theta$ and hence $M = N\sin^2(\theta/2)$ to accuracy $O(\sqrt{M N}/2^t)$. (ii) BBHT [S47]: choose $k$ uniformly at random in $[0, m)$, run, check the result classically; double $m$ (up to $\sqrt N$) on failure. Expected total queries $O(\sqrt{N/M})$; the analysis uses $\frac1m\sum_{k<m}\sin^2((2k+1)\theta/2) = \frac12 - \frac{\sin(2m\theta)}{4m\sin\theta}\geq\frac14$ once $m\geq1/\sin\theta$.

**Amplitude amplification.** Same rotation argument with $|\psi\rangle = A|0\rangle$: after $k$ iterations of $Q$ the success amplitude is $\sin((2k+1)\theta/2)$ with $\sin^2(\theta/2)=p$; $O(1/\sqrt p)$ iterations instead of the classical $O(1/p)$ repetitions. Applications: speed up any bounded-error subroutine quadratically, quantum minimum finding $O(\sqrt N)$ (Dürr–Høyer), collision finding $O(N^{1/3})$, and the Grover-inside-Shor style "search for the right $a$" tricks.

**Lower bound (BBBV 1997 [S41]; Zalka: constant $\frac\pi4$ tight).** Any quantum algorithm that finds a single marked element with probability $\geq\frac23$ needs $\Omega(\sqrt N)$ queries. *Hybrid-argument sketch.* Let $|\psi_t^x\rangle$ be the state after $t$ queries when the marked item is $x$, and $|\psi_t\rangle$ the state with no marked item (oracle = identity). Define the *query magnitude* on $x$ at step $t$ as $q_t(x) = \|P_x|\phi_t\rangle\|^2$, where $|\phi_t\rangle$ is the state just before the $t$-th query and $P_x$ projects onto the register value $x$. Since $\sum_x q_t(x) = 1$ for every $t$, $\sum_x\sum_{t\leq T}q_t(x) = T$, so some $x$ has $\sum_t q_t(x)\leq T/N$. Replacing the oracle by $O_x$ (which differs from identity only on the $x$-component) changes the state at step $t$ by at most $2\sqrt{q_t(x)}$; by the triangle inequality and Cauchy–Schwarz $\||\psi_T^x\rangle-|\psi_T\rangle\| \leq 2\sum_t\sqrt{q_t(x)}\leq 2\sqrt{T\sum_t q_t(x)}\leq 2T/\sqrt N$. But the algorithm must distinguish "marked $x$" from "nothing marked" (or from marked $x'$) with constant probability, which requires the final states to be a constant distance apart; hence $T = \Omega(\sqrt N)$. $\square$
The same argument (B06, polynomial method) shows $Q(\mathrm{OR}_N) = \Theta(\sqrt N)$. **Consequence:** relative to a random oracle, NP $\not\subseteq$ BQP; there is no black-box exponential speedup for NP-complete problems. Any exponential quantum speedup must exploit *structure* (periodicity in Shor, C07).

**Cost of the non-oracle part.** Each iteration uses $O(n)$ gates for $D$ (two layers of $H$ and $X$, one $C^{n-1}Z$ which is $O(n)$ Toffolis with ancillas, C02) plus one oracle call; total $O(\sqrt N\,(n + |O_f|))$.

## Worked example

$n=3$, $N=8$, one marked item $x^*=101$ ($M=1$). $\sin\frac\theta2 = \frac{1}{\sqrt8}$, $\theta = 2\arcsin(0.35355)=0.7227$ rad $=41.4^\circ$. $k_{\text{opt}} = \lfloor\pi/(2\theta)-\frac12\rceil = \lfloor 2.17-0.5\rceil = 2$.

Amplitudes (all 8 entries; marked entry shown separately):

| step | unmarked amplitude (7 entries) | marked amplitude | $P(x^*)$ |
|---|---|---|---|
| $\lvert\psi\rangle$ | $1/\sqrt8 = 0.3536$ | $0.3536$ | $0.125$ |
| $O_f$ | $0.3536$ | $-0.3536$ | $0.125$ |
| $D$ (mean $\mu=\frac{7\cdot0.3536-0.3536}{8}=0.2652$; $a\mapsto2\mu-a$) | $0.1768$ | $0.8839$ | $0.781$ |
| $O_f$ | $0.1768$ | $-0.8839$ | $0.781$ |
| $D$ ($\mu = \frac{7\cdot0.1768-0.8839}{8} = 0.0442$) | $-0.0884$ | $0.9723$ | $0.945$ |

Check with the formula: $P_2 = \sin^2(5\theta/2) = \sin^2(1.807) = 0.945$ ✓, $P_1 = \sin^2(3\theta/2) = \sin^2(1.084)=0.781$ ✓. A third iteration gives $\sin^2(7\theta/2) = \sin^2(2.529)=0.330$: overshoot. Classically, finding $x^*$ with probability $0.945$ needs about $7.6$ of the $8$ queries. In code: `grover(3, [5], iterations=2)` and `success_probability(3, 1, 2)` in `src/py/quantum/grover.py`.

Inversion about the mean as a picture: $D$ maps each amplitude $a_x\mapsto 2\mu - a_x$ with $\mu$ the mean amplitude; the oracle first makes the marked amplitude negative, so that after reflection it lands far above the mean.

## Pitfalls

- Applying $G$ "until it converges": there is no convergence, the state rotates; the number of iterations must be computed from $M/N$ or handled by BBHT/counting.
- Using $k = \frac\pi4\sqrt N$ when $M>1$: the correct count is $\frac\pi4\sqrt{N/M}$; with $M$ unknown and the single-item count you can land near $P\approx0$.
- Believing Grover solves NP-complete problems efficiently: $\sqrt{2^n} = 2^{n/2}$ is still exponential; and it is optimal for black-box search.
- Forgetting the oracle cost: for SAT the oracle is a reversible circuit evaluating the formula, size $O(m)$ per query; the *total* cost is $O(2^{n/2}\,m)$.
- The diffusion operator is $2|\psi\rangle\langle\psi|-I$, not $I - 2|\psi\rangle\langle\psi|$; the sign is a global phase per iteration and harmless, but writing $H^{\otimes n}(I-2|0\rangle\langle0|)H^{\otimes n}$ with the wrong outer basis (e.g. forgetting the $X$ conjugation in the $C^{n-1}Z$ construction) reflects about the wrong state.
- Measuring after each iteration collapses the rotation; measure only at the end.

## Exam-style questions

1. *Derive the state after $k$ Grover iterations and the optimal $k$ for $N=2^{20}$, $M=1$.* Rotation by $\theta=2\arcsin(2^{-10})\approx 2^{-9}$ per iteration from initial angle $\theta/2$; $k_{\text{opt}}\approx \frac{\pi}{4}\cdot 2^{10} \approx 804$ iterations, success $\geq 1-2^{-20}$.
2. *For $M = N/4$ show one iteration succeeds with certainty.* $\sin\frac\theta2 = \frac12\Rightarrow\theta=\frac\pi3$; after one iteration the angle is $\frac{3\theta}{2}=\frac\pi2$, $P_1 = 1$.
3. *State and sketch the proof of the $\Omega(\sqrt N)$ lower bound.* Hybrid argument above: total query magnitude over $T$ steps is $T$, some item receives $\leq T/N$, the final state differs from the no-marked-item run by at most $2T/\sqrt N$, which must be $\Omega(1)$.
4. *Explain how amplitude amplification improves a classical randomised algorithm with success probability $p$ from $O(1/p)$ to $O(1/\sqrt p)$ expected runs.* Make the algorithm reversible as $A$ (C02), its verifier as $S_f$; $Q = -AS_0A^\dagger S_f$ rotates by $\theta=2\arcsin\sqrt p$ per iteration; $O(1/\sqrt p)$ iterations bring the good amplitude to $\Theta(1)$.
5. *Why does Grover not contradict the classical lower bound of $\Omega(N)$ for search?* The classical bound is for classical queries (one $x$ per query); the quantum oracle is queried in superposition, and the quantum bound is $\Omega(\sqrt N)$, which Grover meets. Both bounds are tight in their models.

## Code

`src/py/quantum/grover.py`: `oracle(n, marked)`, `diffusion(n)`, `grover(n, marked, iterations=None, rng=None)`, `success_probability(n, M, k)` (analytic $\sin^2((2k+1)\theta/2)$), `amplitude_amplification(A, good, k)`. `test_grover.py` checks analytic vs simulated probabilities to $10^{-9}$, $P>0.9$ at $k_{\text{opt}}$ for $n=4..6$, and overshooting.
