# C07 Shor's algorithm

Shor (1994) factors an $n$-bit integer in $O(n^3)$ quantum gates (with $O(n^2\log n\log\log n)$ using fast multiplication), against $\exp(O(n^{1/3}\log^{2/3}n))$ for the best classical method (number field sieve). It is the strongest evidence against the extended Church–Turing thesis (B06) and the reason RSA, Diffie–Hellman and elliptic-curve cryptography are considered broken by large fault-tolerant quantum computers. The quantum part is order finding (C06); everything else is number theory. References: Nielsen & Chuang 5.3, Appendix 4 [S30]; Kaye, Laflamme, Mosca 7.3-7.4 [S28]; Rieffel & Polak 8.4-8.5 [S29]; de Wolf ch. 7 [S31]; Aaronson ch. 10 [S27]; primary: Shor [S40]; resource estimates [S58]. Lecture section 7 [S20], which states the register-size rule $N^2 \le q \le 2N^2$ with $q = 2^\ell$. An oral protocol records the question "was wird berechnet? wie? wieso soll $q$ eine grosse Zahl sein?" [S21]. Exam 2 material.

## Definitions

**Factoring.** Given composite $N$, find a nontrivial divisor. Decision version ("does $N$ have a factor $<k$?") is in NP $\cap$ coNP; not known to be NP-hard, not known to be in P.

**Order.** For $\gcd(a,N)=1$, $r = \mathrm{ord}_N(a) = \min\{r\geq1: a^r\equiv1\pmod N\}$; $r$ divides $\phi(N)$ (Euler).

**Reduction.** Factoring $\leq_p$ order finding: the algorithm below makes $O(1)$ expected calls to an order-finding oracle plus polynomial classical work.

## Results

**Lemma 1 (nontrivial square root gives a factor).** If $x^2\equiv1\pmod N$ with $x\not\equiv\pm1$, then $\gcd(x-1,N)$ and $\gcd(x+1,N)$ are nontrivial factors of $N$.
*Proof.* $N\mid(x-1)(x+1)$ but $N\nmid x-1$ and $N\nmid x+1$ (since $x\not\equiv\pm1$), so the prime factors of $N$ are split between the two factors; $\gcd(x-1,N)$ is neither 1 (else $N\mid x+1$) nor $N$. $\square$

**Lemma 2 (order gives a square root).** If $r=\mathrm{ord}_N(a)$ is even, $x = a^{r/2}$ satisfies $x^2\equiv1$ and $x\not\equiv1$ (else the order would be $\leq r/2$). If additionally $x\not\equiv-1$, Lemma 1 yields a factor.

**Lemma 3 (probability of success; N&C Thm A4.13 [S30]).** Let $N$ be odd with $k\geq2$ distinct prime factors. For $a$ uniform among the units mod $N$,
$$\Pr\big[r\text{ even and }a^{r/2}\not\equiv-1\big]\;\geq\;1-\frac{1}{2^{k-1}}\;\geq\;\frac12 .$$
*Proof sketch (N&C Theorem A4.13).* By CRT, $a\leftrightarrow(a_1,\dots,a_k)$ with $a_i = a\bmod p_i^{\alpha_i}$, and choosing $a$ uniformly chooses the $a_i$ independently and uniformly in the cyclic groups $\mathbb{Z}_{p_i^{\alpha_i}}^*$. Let $r_i=\mathrm{ord}(a_i)$ and write $r_i = 2^{d_i}\cdot\text{odd}$; then $r=\mathrm{lcm}(r_i)$. The failure events are "$r$ odd" (all $d_i=0$) and "$a^{r/2}\equiv-1$" (then $a_i^{r/2}\equiv-1$ for every $i$, which forces all $d_i$ to equal the maximum $d = \max_i d_i$). So failure implies $d_1=\dots=d_k$. In a cyclic group of even order $2^{e}m$ ($m$ odd), the power of 2 in the order of a uniformly random element takes each value $0$ with probability $2^{-e}$ and $j\in\{1..e\}$ with probability $2^{j-1-e}$... in any case each specific value has probability $\leq\frac12$, so $\Pr[d_1=\dots=d_k]\leq\frac{1}{2^{k-1}}$ by independence (fix $d_1$, each other $d_i$ matches with probability $\leq\frac12$). $\square$

**Shor's algorithm.**
1. If $N$ is even, return 2. If $N = p^k$ for a prime $p$ (test $\lfloor N^{1/k}\rfloor$ for $k\leq\log_2N$), return $p$. (Both are polynomial classical checks; they exclude the cases where Lemma 3 does not apply.)
2. Pick $a\in\{2,\dots,N-1\}$ uniformly. If $g=\gcd(a,N)>1$, return $g$ (lucky).
3. Find $r=\mathrm{ord}_N(a)$ with quantum order finding (C06): $n=\lceil\log_2N\rceil$ work qubits, $t=2n+1$ counting qubits (or $2n$ in practice), modular exponentiation, inverse QFT, continued fractions, verify $a^r\equiv1$.
4. If $r$ is odd or $a^{r/2}\equiv-1\pmod N$, go to 2.
5. Return $\gcd(a^{r/2}-1,N)$ and $\gcd(a^{r/2}+1,N)$.

Expected number of rounds $\leq2$ by Lemma 3; each round: $O(n^3)$ gates (modular exponentiation dominates), $O(n^2)$ for the QFT, classical $O(n^3)$ for gcd/continued fractions/modular arithmetic. Total $O(n^3)$, polynomial in the input length $n=\log N$. Repeating order finding $O(1)$ times handles the $\gcd(s,r)>1$ case and the $\geq4/\pi^2$ phase-estimation success probability. Complete factorisation: recurse on the factors, at most $\log_2 N$ times.

**Consequences.** RSA relies on factoring $N=pq$; discrete logarithms in $\mathbb{Z}_p^*$ and in elliptic-curve groups are also hidden-subgroup problems over abelian groups and fall to the same technique (Shor's second algorithm), so ECC/ECDSA and DH are broken too. Symmetric cryptography (AES, hash functions) is only weakened quadratically by Grover (C04). Resource estimates for RSA-2048 dropped from $\sim2\times10^7$ physical noisy qubits for 8 hours (Gidney–Ekerå 2019 [S58]) to under $10^6$ qubits for under a week (Gidney 2025 [S58]); current hardware is orders of magnitude below both. Post-quantum cryptography (lattice-based Kyber/ML-KEM, Dilithium/ML-DSA, hash-based signatures, NIST 2024 standards) uses problems with no known polynomial quantum algorithm. Shor does **not** solve NP-complete problems: factoring is in NP $\cap$ coNP and is believed not to be NP-hard; there is no evidence that BQP $\supseteq$ NP (B06).

## Worked example 1: $N=15$

Classical preliminaries: $15$ is odd, not a prime power. Units mod 15: $\{1,2,4,7,8,11,13,14\}$ ($\phi(15)=8$). Orders:

| $a$ | 1 | 2 | 4 | 7 | 8 | 11 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|
| $r$ | 1 | 4 | 2 | 4 | 4 | 2 | 4 | 2 |
| $a^{r/2}\bmod15$ | – | 4 | 4 | 4 | 4 | 11 | 4 | 14 $\equiv-1$ |
| factors | – | 3, 5 | 3, 5 | 3, 5 | 3, 5 | 5, 3 | 3, 5 | fail |

Six of the seven nontrivial choices succeed, consistent with Lemma 3 ($k=2$: probability $\geq\frac12$).

Take $a=7$: $7^1=7$, $7^2=49\equiv4$, $7^3\equiv28\equiv13$, $7^4\equiv91\equiv1$, so $r=4$.

Quantum order finding. Work register $n=4$ qubits (values $0..15$), counting register $t=2n=8$ qubits ($2^t=256$); 12 qubits in total, 4096 amplitudes.
1. $H^{\otimes8}$: $\frac{1}{16}\sum_{k=0}^{255}|k\rangle|1\rangle$.
2. Controlled multiplications by $7^{2^j}\bmod15$ for $j=0..7$: $7, 4, 1, 1, 1, 1, 1, 1$ (since $7^4\equiv1$, all higher squares are 1 — a peculiarity of tiny $N$). State $\frac1{16}\sum_k|k\rangle|7^k\bmod15\rangle = \frac1{16}\sum_k|k\rangle|\,(1,7,4,13)_{k\bmod4}\rangle$.
3. Measuring the work register gives one of $1,7,4,13$ with probability $\frac14$ each, say $4$: the counting register collapses to $\frac{1}{8}\sum_{j=0}^{63}|2+4j\rangle$ (64 terms, period $r=4$, offset $k_0=2$).
4. Inverse QFT of the comb: since $r\mid2^t$, the result is *exactly* $\frac12\sum_{s=0}^{3}e^{-2\pi i\cdot 2s/4}\,|s\cdot 64\rangle$ (phases from the offset, irrelevant). Measurement gives $m\in\{0,64,128,192\}$ each with probability $\frac14$.
5. Continued fractions of $m/256$: $0/256\to$ useless ($s=0$; repeat). $64/256 = 1/4\to r=4$. $128/256=1/2\to$ candidate $2$ (that is $s/r = 2/4$, $\gcd(s,r)=2$): check $7^2=49\not\equiv1$; try $2\cdot2=4$: $7^4\equiv1$ ✓, or rerun and take the lcm. $192/256 = 3/4$: Euclid $256 = 1\cdot192+64$, $192=3\cdot64$, so $[0;1,3]$, convergents $0/1, 1/1, 3/4$ → $r=4$ ✓.
6. $r=4$ is even; $x = 7^{2} \equiv 4\not\equiv-1$. $\gcd(4-1,15)=\gcd(3,15)=3$, $\gcd(4+1,15)=\gcd(5,15)=5$. $15 = 3\cdot5$. ∎

Overall success per run: $P(m\ne0)\cdot P(\text{coprime or fixed by check}) = \frac34$ directly (or $\frac12$ without the multiple check), then a factor with certainty since $a=7$ is good. In code: `shor(15, rng)` in `src/py/quantum/shor.py`, which calls `order_finding(7, 15)`.

## Worked example 2: $N=21$

Units mod 21 (12 of them). Orders: $2\to6$, $4\to3$, $5\to6$, $8\to2$, $10\to6$, $11\to6$, $13\to2$, $16\to3$, $17\to6$, $19\to6$, $20\to2$. Failures: $4,16$ (odd $r$), $5,17,20$ ($a^{r/2}\equiv-1$: $5^3=125\equiv20$, $17^3\equiv20$, $20^1=20$). Six of eleven succeed.

Take $a=2$: $2^6=64=3\cdot21+1$, so $r=6$; $2^3=8\not\equiv-1$ ✓. Register sizes: $n=5$ work qubits, $t=10$ counting qubits ($2^{10}=1024$), 15 qubits, 32768 amplitudes. Controlled multipliers $2^{2^j}\bmod21$: $2,4,16,4,16,4,16,4,16,4$ (since $2^8 = 256\equiv4$, and $4\to16\to4\to\dots$).

Now $r=6\nmid1024$: $1024/6 = 170.67$, so after the inverse QFT the peaks are *near* $s\cdot170.67$: $m\approx0,171,341,512,683,853$, each with total probability $\gtrsim 0.8/6$ spread over the nearest two integers, plus small tails. Three representative outcomes:

- $m=171$: $\frac{171}{1024}$. Euclid: $1024 = 5\cdot171+169$; $171=1\cdot169+2$; $169=84\cdot2+1$; $2=2\cdot1$. So $[0;5,1,84,2]$. Convergents: $0/1,\ 1/5,\ 1/6,\ 85/509,\ 171/1024$. Last denominator $\leq21$: $1/6$ → $r=6$. Check $|171/1024-1/6| = 3.26\cdot10^{-4}\leq\frac{1}{2\cdot36} = 1.39\cdot10^{-2}$ ✓ and $2^6\equiv1$ ✓. [convergents verified: `test_order_finding.py`]
- $m=683$: $1024 = 1\cdot683+341$; $683 = 2\cdot341+1$; $341 = 341\cdot1$. $[0;1,2,341]$, convergents $0/1, 1/1, 2/3, 683/1024$. Candidate $r=3$: $2^3=8\not\equiv1$ ✗. This is the $\gcd(s,r)=2$ case ($s/r=4/6$). Fix: test $2r=6$: $2^6\equiv1$ ✓; or combine with another run returning e.g. $853/1024\to[0;1,4,1,84,2]\to 5/6$, $\mathrm{lcm}(3,6)=6$.
- $m=512$: $1/2$, $s/r = 3/6$; candidate $2$, $2^2=4\not\equiv1$; $2\cdot2=4$: no; $3\cdot2 = 6$ ✓ (small multiples up to $\log N$ are cheap to test), or lcm with $1/6$ from another run.

With $r=6$: $x = 2^3 = 8$. $\gcd(8-1,21) = 7$, $\gcd(8+1,21)=\gcd(9,21)=3$. $21=3\cdot7$. ∎

Why the peak width matters: the counting register must have $t\geq2n+1 = 11$ for the continued-fraction guarantee $2^{-t-1}\leq1/(2N^2) = 1/882$; with $t=10$ the precision is $1/2048<1/882$ anyway, which is why $t=2n$ works in this example — but for general $N$ the theorem asks for $2^{-(t+1)}\le 1/(2r^2)$ and $r$ can be as large as $N-1$.

## Pitfalls

- Reporting $a^{r/2}$ instead of $\gcd(a^{r/2}\pm1,N)$ as "the factor"; and forgetting that $a^{r/2}$ must be reduced mod $N$ before the gcd only for convenience (gcd is unaffected).
- Choosing $a$ with $\gcd(a,N)>1$ "by luck" is fine, but such $a$ are not units and must not enter the order-finding step.
- Concluding failure when the continued fraction returns a divisor of $r$: verify $a^q\equiv1$ and test small multiples / lcm across runs.
- Expecting the counting register outcome to be exactly $s2^t/r$: only when $r\mid2^t$ (as for $N=15$). In general it is the nearest integer with probability $\geq4/\pi^2$.
- Stating that Shor gives "exponential speedup over the best classical algorithm": the classical best is subexponential ($L_N[1/3]$), so the speedup is superpolynomial, not exponential in the strict sense; still polynomial vs. superpolynomial.
- Claiming Shor breaks all cryptography: symmetric primitives and hash functions survive with doubled key length (Grover); lattice-based schemes are not affected by Shor.
- Even-$N$ and prime-power $N$ must be handled classically first; Lemma 3 assumes $N$ odd with $\geq2$ distinct prime factors.

## Exam-style questions

1. *Prove that if $x^2\equiv1\pmod N$ and $x\not\equiv\pm1$, then $\gcd(x-1,N)$ is a nontrivial factor.* Lemma 1.
2. *Run Shor by hand for $N=15$, $a=2$.* $2^1=2,2^2=4,2^3=8,2^4=16\equiv1$: $r=4$; $x=2^2=4$; $\gcd(3,15)=3$, $\gcd(5,15)=5$.
3. *Why does $a=14$ fail for $N=15$, and what does the algorithm do?* $14\equiv-1$, order $2$, $a^{r/2}=14\equiv-1$: Lemma 1 does not apply ($\gcd(13,15)=1$, $\gcd(15,15)=15$). The algorithm picks a new $a$; the probability of this failure over random $a$ is $\leq\frac12$.
4. *How many qubits and, in order of magnitude, how many gates does factoring a 2048-bit RSA modulus need with the textbook circuit?* Work register $2048$ qubits, counting register $\approx4097$ qubits (plus ancillas for modular multiplication, $O(n)$), gates $O(n^3)\approx10^{10}$ (schoolbook), with a $\Theta(n^2)$ QFT that can be approximated in $O(n\log n)$.
5. *Explain why $|1\rangle$ is used as the initial work state although the eigenstates $|u_s\rangle$ are unknown.* $|1\rangle = r^{-1/2}\sum_s|u_s\rangle$ (C06), so phase estimation on $|1\rangle$ yields $s/r$ for a random $s$; no eigenstate needs to be prepared, and a random $s$ coprime to $r$ (probability $\Omega(1/\log\log r)$, or with the lcm trick $O(1)$ tries) reveals $r$ via continued fractions.
6. *Is factoring NP-complete? What would it mean if it were?* Not known and believed not: FACTORING (decision version) is in NP $\cap$ coNP (certificates: the factorisation with primality proofs), and NP-completeness would imply NP $=$ coNP and the collapse of the polynomial hierarchy (B02). Hence Shor is not evidence that NP $\subseteq$ BQP.

## Code

`src/py/quantum/shor.py`: `shor(N, rng, max_trials)` (full algorithm with the classical checks, using `order_finding.order_finding` for the quantum step), `shor_classical_order(N, rng)` (same control flow with a classical order oracle, for larger $N$ demos), `factor_from_order(a, r, N)`. Tests: $15$ factored in $\geq80\%$ of 20 seeded runs; $21$ in the demo (`python src/py/quantum/shor.py`). `src/py/quantum/order_finding.py`: `order_finding`, `continued_fraction`, `convergents`, `order_classical`.
