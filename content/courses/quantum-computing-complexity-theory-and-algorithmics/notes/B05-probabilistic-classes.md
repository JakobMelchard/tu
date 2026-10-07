# B05 Probabilistic classes: RP, ZPP, BPP, PP

Randomised algorithms flip coins and may err with small probability; primality testing (Miller-Rabin) and polynomial identity testing are the classic examples where randomness gives simple polynomial algorithms and no deterministic one was known (for primality until 2002, for PIT still). BPP is the class of problems that are "feasible in practice" for a classical computer, and it is the right classical baseline for BQP (B06): the definitions of BQP, QMA and the amplification arguments are copies of the ones here. References: Papadimitriou ch. 11 (randomised computation, Adleman's theorem, PP) [S26]; Adleman, Lautemann/Sipser, Impagliazzo-Wigderson, Toda [S56]; class definitions cross-checked against the Complexity Zoo [S34]. TISS bullet: "probabilistic complexity classes (BPP, PP)" [S1]. Exam 1 material.

## Definitions

- **Probabilistic TM (PTM).** A TM with two transition functions $\delta_0, \delta_1$; at each step one is chosen by a fair coin. Equivalently a deterministic TM with an extra read-only tape of random bits $r \in \{0,1\}^{m}$, $m = \mathrm{poly}(n)$; $\Pr_r[M(x, r) = 1]$ is the acceptance probability. Same tree as an NTM, but the *fraction* of accepting branches matters, not their existence.
- $\mathrm{RP}$ (one-sided, Monte Carlo): polynomial-time $M$ with $x \in L \Rightarrow \Pr[M(x) = 1] \ge 1/2$ and $x \notin L \Rightarrow \Pr[M(x) = 1] = 0$. $\mathrm{coRP}$: errors only on no-instances.
- $\mathrm{ZPP}$ (zero error, Las Vegas): $L$ decided by a PTM that never errs and has **expected** polynomial running time (or: outputs "yes"/"no"/"?" in worst-case polynomial time, "?" with probability $\le 1/2$).
- $\mathrm{BPP}$ (bounded two-sided error): $\Pr[M(x) = [x \in L]] \ge 2/3$ for all $x$.
- $\mathrm{PP}$ (unbounded error): $x \in L \iff \Pr[M(x) = 1] > 1/2$.
- $\#\mathrm P$: functions $f(x) = $ number of accepting branches of a polynomial-time NTM (e.g. #SAT). $\mathrm P^{\#\mathrm P}$: polynomial time with a #P oracle.
- Inclusions by definition: $\mathrm P \subseteq \mathrm{ZPP} \subseteq \mathrm{RP} \subseteq \mathrm{BPP} \subseteq \mathrm{PP}$, $\mathrm{RP} \subseteq \mathrm{NP}$ (an accepting random string is a certificate), $\mathrm{coRP} \subseteq \mathrm{coNP}$, $\mathrm{NP} \cup \mathrm{coNP} \subseteq \mathrm{PP} \subseteq \mathrm{PSPACE}$.

## Results

**Theorem.** $\mathrm{ZPP} = \mathrm{RP} \cap \mathrm{coRP}$.
*Proof.* ($\subseteq$) Let $M$ decide $L$ with zero error in expected time $t(n)$. Run $M$ for $2t(n)$ steps; by Markov's inequality the probability that it has not halted is $\le 1/2$. RP machine: answer as $M$ if it halted, else "no": never accepts a no-instance, accepts a yes-instance with probability $\ge 1/2$. coRP machine: same with default "yes". ($\supseteq$) Let $A$ be an RP machine and $B$ a coRP machine for $L$. Repeat: run both; if $A$ accepts output "yes" (certain: $A$ never accepts no-instances); if $B$ rejects output "no" (certain). If $x \in L$, $A$ accepts with probability $\ge 1/2$ per round; if $x \notin L$, $B$ rejects with probability $\ge 1/2$. Either way the expected number of rounds is $\le 2$, so expected polynomial time and no error. $\square$

**Chernoff-Hoeffding bound (derivation).** Let $X_1, \dots, X_k$ be independent, $X_i \in \{0,1\}$, $\Pr[X_i = 1] = p$, $X = \sum X_i$. For $\varepsilon > 0$,
$$\Pr[X \le (p - \varepsilon) k] \le e^{-2 \varepsilon^2 k}.$$
*Derivation.* For $\lambda > 0$, by Markov applied to $e^{-\lambda X}$: $\Pr[X \le (p-\varepsilon)k] = \Pr[e^{-\lambda X} \ge e^{-\lambda (p - \varepsilon) k}] \le e^{\lambda (p-\varepsilon) k}\, \mathbb E[e^{-\lambda X}] = e^{\lambda(p-\varepsilon)k} \prod_i \mathbb E[e^{-\lambda X_i}]$ by independence. Hoeffding's lemma: a random variable $Y \in [0, 1]$ with mean $p$ satisfies $\mathbb E[e^{-\lambda(Y - p)}] \le e^{\lambda^2 / 8}$ (convexity of $e^{-\lambda y}$ on $[0,1]$ plus a second-order Taylor bound). Hence $\Pr \le e^{-\lambda \varepsilon k + k \lambda^2 / 8}$; minimise over $\lambda$: $\lambda = 4\varepsilon$ gives $e^{-2 \varepsilon^2 k}$. $\square$
(The multiplicative form $\Pr[X \le (1 - \delta) pk] \le e^{-\delta^2 pk / 2}$ follows from the same moment computation with $1 - p + p e^{-\lambda}$ kept exactly.)

**Theorem (amplification for BPP).** If $M$ has success probability $p \ge 1/2 + \eta$ with $\eta \ge 1/\mathrm{poly}(n)$, then the majority vote of $k$ independent runs errs with probability $\le e^{-2 \eta^2 k}$. To reach error $2^{-s}$ take $k \ge \dfrac{s \ln 2}{2 \eta^2}$.
*Proof.* Majority wrong $\iff X \le k/2 = (p - \eta')k$ with $\eta' = p - 1/2 \ge \eta$; apply Chernoff. $\square$ Numbers: from $2/3$ ($\eta = 1/6$) to $1 - 2^{-s}$: $k \ge 18 \ln 2 \cdot s \approx 12.5\, s$, i.e. $k = 125$ for $s = 10$, $k = 251$ for $s = 20$ (odd $k$ to avoid ties). The exact binomial tail is smaller: $2^{-10}$ is already reached at $k = 81$ and $2^{-20}$ at $k = 193$ (`bpp_amplify.py`). From $1/2 + n^{-2}$: $k = O(n^4 s)$, still polynomial. This is why the constant $2/3$ in the definition of BPP is immaterial: any threshold $1/2 + 1/\mathrm{poly}$ up to $1 - 2^{-\mathrm{poly}}$ gives the same class. The argument needs only that the runs are independent and that the machine can be rerun with fresh coins; the same argument applies verbatim to BQP (B06) but **not** to PP, where $\eta$ may be $2^{-n}$ and $k$ would be exponential.

**Amplification for RP.** $k$ runs, accept iff any run accepts: no-instances are never accepted; a yes-instance is missed with probability $\le (1 - p)^k = 2^{-k}$ for $p = 1/2$. No majority needed, hence no Chernoff.

**Theorem (Adleman 1978 [S56]).** $\mathrm{BPP} \subseteq \mathrm{P/poly}$.
*Proof.* Let $L \in \mathrm{BPP}$. Amplify to error $< 2^{-(n+1)}$ ($k = O(n)$ repetitions), giving $M'(x, r)$ with $|r| = m = \mathrm{poly}(n)$ and, for every fixed $x$, $\Pr_r[M'(x, r) \ne [x \in L]] < 2^{-(n+1)}$. Call $r$ **bad for $x$** if $M'(x, r)$ is wrong. By the union bound over the $2^n$ inputs of length $n$,
$$\Pr_r[\exists x \in \{0,1\}^n : r \text{ bad for } x] \le 2^n \cdot 2^{-(n+1)} = 1/2 < 1,$$
so some $r_n \in \{0,1\}^m$ is good for **all** $x$ of length $n$. Use $r_n$ as the advice string: $M'(x, r_n)$ is a deterministic polynomial-time computation with polynomial advice, i.e. a polynomial-size circuit family (B04). $\square$ The family is not uniform: finding $r_n$ is the hard part (derandomisation).

**Theorem (Sipser-Gács 1983, Lautemann 1983 [S56]).** $\mathrm{BPP} \subseteq \Sigma_2^p \cap \Pi_2^p$.
*Proof sketch.* Amplify to error $\le 2^{-n}$ with random strings of length $m$. For $x$ let $S_x = \{r \in \{0,1\}^m : M(x, r) = 1\}$. Then $x \in L \Rightarrow |S_x| \ge (1 - 2^{-n}) 2^m$ and $x \notin L \Rightarrow |S_x| \le 2^{-n} 2^m$. Claim: with $k = \lceil m / n \rceil + 1$ shifts $u_1, \dots, u_k \in \{0,1\}^m$,
$$x \in L \iff \exists u_1, \dots, u_k\ \forall r \in \{0,1\}^m : \bigvee_{i=1}^k M(x, r \oplus u_i) = 1 .$$
If $x \notin L$: $\bigcup_i (S_x \oplus u_i)$ has size $\le k\, 2^{m-n} < 2^m$ for large $n$, so some $r$ is uncovered whatever the shifts. If $x \in L$: pick the $u_i$ uniformly at random; for a fixed $r$, $\Pr[r \notin S_x \oplus u_i] = \Pr[r \oplus u_i \notin S_x] \le 2^{-n}$, independently over $i$, so $\Pr[r \text{ uncovered}] \le 2^{-nk}$; union bound over the $2^m$ strings $r$: $\Pr[\text{some } r \text{ uncovered}] \le 2^{m - nk} < 1$, so good shifts exist. The right-hand side is a $\Sigma_2^p$ predicate (polynomially many quantified bits, polynomial-time matrix). BPP is closed under complement, so also $\mathrm{BPP} \subseteq \Pi_2^p$. $\square$ Consequence: $\mathrm P = \mathrm{NP} \Rightarrow \mathrm{PH} = \mathrm P \Rightarrow \mathrm{BPP} = \mathrm P$.

**PP.** $\mathrm{NP} \subseteq \mathrm{PP}$: for SAT, flip a coin; with probability $1/2$ accept outright, otherwise draw a uniformly random assignment and accept iff it satisfies $\varphi$. Acceptance probability $\frac12 + \frac{\#\mathrm{sat}(\varphi)}{2^{n+1}}$, which is $> 1/2$ iff $\varphi$ is satisfiable. (To make the no-case strictly $\le 1/2$ compatible with the definition, reduce the outright-accept probability to $\frac12 - 2^{-n-2}$; then unsatisfiable gives $< 1/2$ and satisfiable gives $\ge \frac12 - 2^{-n-2} + 2^{-n-1} > \frac12$.) PP is closed under complement (swap accept/reject after the same tie-breaking), so $\mathrm{coNP} \subseteq \mathrm{PP}$; $\mathrm{BPP} \subseteq \mathrm{PP}$ trivially. **PP and #P.** $\mathrm P^{\mathrm{PP}} = \mathrm P^{\#\mathrm P}$: a #P oracle answers "is the number of accepting branches $> 2^{m-1}$" (that is PP), and conversely binary search with a PP oracle (on padded machines) recovers the count. **Toda (1991):** $\mathrm{PH} \subseteq \mathrm P^{\#\mathrm P} = \mathrm P^{\mathrm{PP}}$: counting is at least as hard as the whole polynomial hierarchy. In B06 the same class bounds quantum computation: $\mathrm{BQP} \subseteq \mathrm{PP}$, $\mathrm{QMA} \subseteq \mathrm{PP}$.

**Primality.** Miller-Rabin: for odd $N$ write $N - 1 = 2^s d$ with $d$ odd. Base $a \in [2, N-2]$ is a **witness** of compositeness unless $a^d \equiv 1$ or $a^{2^j d} \equiv -1 \pmod N$ for some $0 \le j < s$. If $N$ is prime no $a$ is a witness (Fermat plus: $\pm 1$ are the only square roots of $1$ modulo a prime). If $N$ is composite at least $3/4$ of the bases are witnesses (Rabin 1980), so COMPOSITES $\in \mathrm{RP}$ and PRIMES $\in \mathrm{coRP}$ with error $4^{-k}$ after $k$ bases; $O(k \log^3 N)$ bit operations. Also PRIMES $\in \mathrm{ZPP}$ (Adleman-Huang 1992) and PRIMES $\in \mathrm P$ (Agrawal-Kayal-Saxena 2002, $\tilde O(\log^{6} N)$ in the improved analysis, deterministic via the polynomial identity $(X + a)^N \equiv X^N + a \pmod{N, X^r - 1}$). Miller-Rabin remains the algorithm used in practice.

**Polynomial identity testing (PIT).** Given an arithmetic circuit (or a formula, a determinant with symbolic entries, ...) computing a polynomial $p(x_1, \dots, x_n)$ of degree $\le d$ over a field, decide $p \equiv 0$. Expanding $p$ may take exponential size. **Schwartz-Zippel:** if $p \not\equiv 0$ and $r_1, \dots, r_n$ are drawn independently and uniformly from a finite set $S$, then $\Pr[p(r) = 0] \le d / |S|$ (induction on $n$ using the degree in $x_n$). Evaluate at a random point with $|S| = 2d$: PIT $\in \mathrm{coRP}$ (error only when $p \not\equiv 0$). No deterministic polynomial algorithm is known; Kabanets-Impagliazzo (2004) showed that derandomising PIT implies circuit lower bounds (either $\mathrm{NEXP} \not\subseteq \mathrm{P/poly}$ or the permanent has no polynomial-size arithmetic circuits), which is why it is the canonical "hard to derandomise" problem. Applications: bipartite perfect matching via $\det$ of the Tutte/Edmonds matrix (in randomised NC), verifying $AB = C$ (Freivalds), equality testing of read-once programs.

**Derandomisation.** Conjecture: $\mathrm{BPP} = \mathrm P$. Evidence: Impagliazzo-Wigderson (1997) [S56]: if some language in $\mathrm E = \mathrm{DTIME}(2^{O(n)})$ requires circuits of size $2^{\Omega(n)}$, then $\mathrm{BPP} = \mathrm P$. Mechanism: a hard function yields a pseudorandom generator (Nisan-Wigderson) stretching $O(\log n)$ truly random bits to $\mathrm{poly}(n)$ bits that no polynomial-size circuit distinguishes from uniform; enumerate all $2^{O(\log n)} = \mathrm{poly}(n)$ seeds and take the majority. Conversely, $\mathrm{BPP} = \mathrm P$-style derandomisation implies (weak) circuit lower bounds, so the question is tied to B04. Unconditionally only $\mathrm{BPP} \subseteq \mathrm{P/poly} \cap \Sigma_2^p$ (above) is known; even $\mathrm{BPP} \subseteq \mathrm{NP}$ is open. For the log-space analogue BPL, partial derandomisation is unconditional: $\mathrm{BPL} \subseteq \mathrm{SPACE}(\log^{3/2} n)$ (Saks-Zhou 1999), conjectured $\mathrm{BPL} = \mathrm L$.

## Worked example

*Majority vote, $p = 2/3$.* Empirical error of the majority of $k$ runs ($2 \cdot 10^4$ trials), exact binomial tail $\Pr[\mathrm{Bin}(k, 2/3) \le k/2]$, and Chernoff $e^{-k/18}$:

| $k$ | empirical | exact tail | Chernoff |
|---|---|---|---|
| 1 | 0.337 | 0.333 | 0.946 |
| 5 | 0.210 | 0.210 | 0.757 |
| 21 | 0.057 | 0.0557 | 0.311 |
| 51 | 0.0072 | 0.0069 | 0.059 |
| 101 | 0.0003 | 0.00027 | 0.0037 |

Chernoff is loose by a constant in the exponent (the exact rate is the relative entropy $D(\tfrac12 \| \tfrac23) \approx 0.059$ nats per trial, i.e. the tail decays like $2^{-0.085 k}$, against Chernoff's $2^{-0.080 k}$) but it is what the proofs need: polynomial $k$ for exponentially small error.

*Adleman's advice length.* $n = 20$: need error $< 2^{-21}$; Chernoff gives $k = 263$ repetitions, so the advice is $263$ copies of the base algorithm's random string, e.g. $263 \cdot 100$ bits if the base algorithm uses 100 random bits. The union bound: $2^{20}$ inputs times error $2^{-21}$: half the strings $r$ are good for all inputs simultaneously.

*Miller-Rabin on the Carmichael number $561 = 3 \cdot 11 \cdot 17$* (Fermat's test fails for every base coprime to 561). $560 = 2^4 \cdot 35$. Base $a = 2$: $2^{35} \equiv 263$, squaring: $263^2 \equiv 166$, $166^2 \equiv 67$, $67^2 \equiv 1$, $1^2 \equiv 1 \pmod{561}$. The sequence reaches $1$ from $67 \ne \pm 1$: $67$ is a nontrivial square root of $1$, so $2$ is a witness and 561 is composite ($\gcd(67 - 1, 561) = 33$ even factors it). Base $a = 5$: $23, 529, 463, 67, 1$: again a witness. On the prime $N = 13$, $12 = 2^2 \cdot 3$, $a = 2$: $2^3 = 8$, $8^2 = 64 \equiv 12 \equiv -1$: not a witness, as it must be.

*Schwartz-Zippel.* Is $(x + y)^2 - x^2 - 2xy - y^2 \equiv 0$? Degree 2; pick $x, y \in \{0, \dots, 99\}$ at random; a nonzero polynomial of degree 2 vanishes on at most a $2/100$ fraction of the points. One evaluation gives error $\le 0.02$; ten give $\le 2^{-56}$.

## Pitfalls

- RP is one-sided in a specific direction: "yes" answers are always right, "no" answers may be wrong. coRP is the mirror image. Miller-Rabin says "composite" only when it is sure, so it is an RP algorithm for COMPOSITES, equivalently coRP for PRIMES.
- ZPP is about **expected** time; a Las Vegas algorithm can run long, but never lies. Randomised quicksort is the standard example (A-notes).
- The constant $2/3$ in BPP (and $1/2$ in RP) is arbitrary; any $1/2 + 1/\mathrm{poly}$ works by amplification. The $1/2$ in PP is **not** arbitrary: PP has no amplification, and $\mathrm{PP} \supseteq \mathrm{NP}$ shows it is (probably) not a feasible class.
- Chernoff needs independent trials; rerunning with the *same* random string proves nothing.
- $\mathrm{BPP} \subseteq \mathrm{P/poly}$ does not give a polynomial-time deterministic algorithm: the good advice string exists but is not known to be findable.
- Randomness and nondeterminism are different: an NTM accepts if one branch accepts, a BPP machine needs $2/3$ of the branches. $\mathrm{RP} \subseteq \mathrm{NP}$ holds; $\mathrm{BPP} \subseteq \mathrm{NP}$ is open.
- PRIMES $\in \mathrm P$ (AKS) does not make Miller-Rabin obsolete or put FACTORING in P. FACTORING is in $\mathrm{NP} \cap \mathrm{coNP}$ and in BQP (Shor, B06), not known in BPP.

## Exam-style questions

1. *Define RP, coRP, ZPP, BPP, PP and give the known inclusions among them and with P, NP, PSPACE.* $\mathrm P \subseteq \mathrm{ZPP} = \mathrm{RP} \cap \mathrm{coRP} \subseteq \mathrm{RP} \subseteq \mathrm{BPP} \subseteq \mathrm{PP} \subseteq \mathrm{PSPACE}$; $\mathrm{RP} \subseteq \mathrm{NP} \subseteq \mathrm{PP}$; $\mathrm{BPP} \subseteq \Sigma_2^p \cap \Pi_2^p$.
2. *State the Chernoff bound and compute how many repetitions bring a BPP algorithm from $2/3$ to error $2^{-30}$.* $e^{-2 \varepsilon^2 k}$ with $\varepsilon = 1/6$: $k \ge 18 \cdot 30 \ln 2 \approx 374$, so $k = 375$.
3. *Prove $\mathrm{BPP} \subseteq \mathrm{P/poly}$.* Amplify to error $2^{-(n+1)}$, union bound over $2^n$ inputs, fix a universally good random string as advice.
4. *Why can PP not be amplified the way BPP can?* The gap $\eta$ between acceptance probabilities of yes- and no-instances may be $2^{-\mathrm{poly}}$, so Chernoff needs $k = \Omega(\eta^{-2})$, exponentially many repetitions.
5. *Show $\mathrm{NP} \subseteq \mathrm{PP}$.* Accept outright with probability just under $1/2$, otherwise test a random assignment; acceptance probability exceeds $1/2$ iff a satisfying assignment exists.
6. *Explain why polynomial identity testing is in coRP and what would follow from a deterministic polynomial-time algorithm.* Schwartz-Zippel; Kabanets-Impagliazzo: circuit lower bounds, so derandomising PIT is at least as hard as proving such bounds.

## Code

`src/py/complexity/bpp_amplify.py`: `chernoff_bound(k, p)`, `exact_majority_error(k, p)` (binomial tail via `scipy.stats.binom`), `majority_vote(base, k, rng)`, `empirical_error(p, k, trials, rng)`, `repetitions_needed(p, target_error)`, `rp_amplify`, `rp_error`. Tests: exact tail $\le$ Chernoff for all odd $k < 200$, empirical error within sampling slack of the exact tail, monotonicity in $k$ and $p$, minimality of `repetitions_needed`, RP simulation.
