# C05 Simon's algorithm

Simon's problem (1994) was the first with an *exponential* separation between quantum and classical randomised query complexity. Its structure — a hidden subgroup of $\mathbb{Z}_2^n$, revealed by Fourier sampling and classical linear algebra — is the template that Shor generalised from $\mathbb{Z}_2^n$ to $\mathbb{Z}_N$ (C06, C07). References: Nielsen & Chuang problem 6.15 / 5.4.3 (hidden subgroup) [S30]; Kaye, Laflamme, Mosca 6.5 [S28]; Rieffel & Polak 8.3 [S29]; de Wolf ch. 5 [S31]; primary: Simon [S38]. Lecture section 5, after Grover [S20]. Exam 2 material.

## Definitions

**Simon's problem.** Given an XOR oracle for $f:\{0,1\}^n\to\{0,1\}^n$ with the promise that there is a nonzero $s\in\{0,1\}^n$ such that
$$f(x) = f(y)\iff y\in\{x,\ x\oplus s\},$$
i.e. $f$ is two-to-one with period $s$ under bitwise XOR. Find $s$.

**GF(2) linear algebra.** $\mathbb{F}_2=\{0,1\}$ with XOR as addition and AND as multiplication; $\{0,1\}^n$ is the vector space $\mathbb{F}_2^n$; the inner product $y\cdot s=\bigoplus_i y_is_i$; the orthogonal complement $s^\perp=\{y: y\cdot s=0\}$ is a subspace of dimension $n-1$ (a hyperplane; note $s\in s^\perp$ is possible, e.g. $s=11$, since the form is not positive definite).

## Results

**Simon's algorithm (quantum part).** Registers: $n$ input qubits and $n$ output qubits.
$$|0^n\rangle|0^n\rangle\xrightarrow{H^{\otimes n}\otimes I}\frac{1}{\sqrt{2^n}}\sum_x|x\rangle|0^n\rangle\xrightarrow{U_f}\frac{1}{\sqrt{2^n}}\sum_x|x\rangle|f(x)\rangle .$$
Measure the second register (or not — by implicit measurement it makes no difference); outcome some value $f(x_0)$, and the first register collapses to the two preimages
$$\frac{1}{\sqrt2}\big(|x_0\rangle+|x_0\oplus s\rangle\big).$$
Apply $H^{\otimes n}$:
$$\frac{1}{\sqrt2}\cdot\frac{1}{\sqrt{2^n}}\sum_y\Big[(-1)^{x_0\cdot y}+(-1)^{(x_0\oplus s)\cdot y}\Big]|y\rangle = \frac{1}{\sqrt{2^{n+1}}}\sum_y(-1)^{x_0\cdot y}\big[1+(-1)^{s\cdot y}\big]|y\rangle .$$
The bracket is $2$ if $s\cdot y=0$ and $0$ otherwise. Hence the measured $y$ is **uniformly distributed over $s^\perp$** (each of the $2^{n-1}$ elements has probability $\big(\frac{2}{\sqrt{2^{n+1}}}\big)^2 = 2^{-(n-1)}$), independently of $x_0$. One query yields one random linear equation $y\cdot s = 0$ about $s$.

**Classical post-processing.** Repeat until the collected $y^{(1)},\dots,y^{(m)}$ span an $(n-1)$-dimensional subspace, i.e. have rank $n-1$ over $\mathbb{F}_2$. Then the homogeneous system $Y s = 0$ has the solution space $\{0, s\}$ (dimension $n-(n-1)=1$); Gaussian elimination over $\mathbb{F}_2$ yields the unique nonzero solution $s$ in $O(n^3)$ bit operations. Verify with two classical queries: $f(0)=f(s)$. If the rank is $<n-1$ after the budgeted number of runs, collect more.

**Expected number of runs.** Draw $y$'s uniformly from the $(n-1)$-dimensional space $s^\perp$. The probability that $n-1$ independent uniform draws from $\mathbb{F}_2^{n-1}$ are linearly independent is
$$\prod_{i=0}^{n-2}\Big(1-\frac{2^i}{2^{n-1}}\Big) = \prod_{j=1}^{n-1}(1-2^{-j}) \;\geq\; \prod_{j=1}^{\infty}(1-2^{-j}) = 0.2888\ldots > \frac14,$$
because the $i$-th draw must avoid the $2^i$ vectors of the span of the previous ones. (The bound $\prod(1-2^{-j})>\frac14$ follows from $\prod_{j\geq2}(1-2^{-j})\geq 1-\sum_{j\geq2}2^{-j}=\frac12$, times $\frac12$ for $j=1$.) So $n-1$ runs succeed with probability $>\frac14$, and $O(n)$ runs succeed with high probability: with $n-1+k$ runs the failure probability is at most $2^{-k}$ (each extra run increases the rank with probability $\geq\frac12$ while it is deficient). Total: $O(n)$ queries, $O(n^3)$ classical time. Simon's algorithm is a *bounded-error* (Las Vegas after verification) algorithm, unlike DJ/BV.

**Classical lower bound** [S38]**.** Any classical randomised algorithm needs $\Omega(2^{n/2})$ queries. *Birthday-style argument.* Classical information about $s$ arises only from a collision $f(x)=f(x')$ with $x\ne x'$ (then $s=x\oplus x'$). Until a collision occurs, the transcript of $k$ distinct queries with $k$ distinct answers is consistent with every $s$ outside the set $\{x_i\oplus x_j\}$ of $\binom k2$ values, and with a uniformly random $s$ (or with a random one-to-one $f$, which one may not be able to distinguish from the two-to-one case). The probability that $k$ queries produce a collision is at most $\binom k2/(2^n-1) = O(k^2/2^n)$, so distinguishing "$f$ has a period" from "$f$ is a random injection" with constant probability needs $k=\Omega(2^{n/2})$. The bound is tight (query random inputs, wait for the birthday collision). Hence Simon gives $O(n)$ vs $\Omega(2^{n/2})$: an exponential separation in the query model, valid against randomised algorithms — but only for a *promise* (partial) problem; for total functions the separation is at most polynomial (B06).

**Hidden subgroup view.** $f$ is constant on cosets of the subgroup $K=\{0,s\}\leq\mathbb{Z}_2^n$ and distinct across cosets. The algorithm samples from the Fourier transform of the coset state, which is supported on the "dual" $K^\perp$; linear algebra recovers $K$ from $K^\perp$. Replacing $\mathbb{Z}_2^n$ by $\mathbb{Z}_N$ (or $\mathbb{Z}$), $H^{\otimes n}$ by the QFT, and Gaussian elimination by continued fractions yields period finding, i.e. Shor. The abelian hidden subgroup problem is solvable in polynomial time in general; non-abelian cases (graph isomorphism via $S_n$, dihedral via lattice problems) are open.

## Worked example

$n=3$, $s=110$. A valid $f$ (two-to-one with period $110$): $f(000)=f(110)=a$, $f(001)=f(111)=b$, $f(010)=f(100)=c$, $f(011)=f(101)=d$ with distinct $a,b,c,d\in\{0,1\}^3$. $s^\perp = \{y: y_0\oplus y_1 = 0\} = \{000, 001, 110, 111\}$: each run returns one of these uniformly.

Suppose three runs return $y^{(1)}=110$, $y^{(2)}=001$, $y^{(3)}=111$. Gaussian elimination over $\mathbb{F}_2$ on the matrix with these rows:
$$\begin{pmatrix}1&1&0\\0&0&1\\1&1&1\end{pmatrix}\xrightarrow{R_3\leftarrow R_3\oplus R_1}\begin{pmatrix}1&1&0\\0&0&1\\0&0&1\end{pmatrix}\xrightarrow{R_3\leftarrow R_3\oplus R_2}\begin{pmatrix}1&1&0\\0&0&1\\0&0&0\end{pmatrix}.$$
Rank 2 $=n-1$ ✓. Pivot columns 0 and 2; free column 1. Set the free variable $s_1=1$: row 2 gives $s_2=0$, row 1 gives $s_0=s_1=1$. Solution $s=110$ ✓. If instead the runs had returned $110, 001, 111$ with one repeated ($110,110,001$), rank would be 2 as well; $000,001,001$ would give rank 1 and require more runs. Verification: $f(000)=f(110)$ ✓ with two classical queries.

Probability calculation for $n=3$: $\prod_{j=1}^{2}(1-2^{-j}) = \frac12\cdot\frac34=\frac38$ that two runs already suffice; with 4 runs failure probability $\leq(1-\frac38)\cdot\frac12\cdot\frac12\approx0.16$, in practice lower. In code `simon(f, n, rng)` in `src/py/quantum/simon.py` collects samples until rank $n-1$ and solves with `nullspace_gf2`.

## Pitfalls

- Forgetting that the samples $y$ can repeat or be $0^n$ (which carries no information): "$n-1$ runs" is the expected order, not a guarantee; always check the rank.
- Solving $Ys=0$ over the reals or integers: the arithmetic is mod 2; the nullspace over $\mathbb{Q}$ is different (e.g. rows $110$ and $011$ have real nullspace spanned by $(1,-1,1)$, but the $\mathbb{F}_2$ nullspace is $\{000, 111\}$).
- Measuring the second register is unnecessary; deferring it is fine. But omitting the oracle's output register (using a phase oracle) does not work: the collapse onto a coset is what produces the 2-term superposition.
- $s$ can lie in $s^\perp$ ($s\cdot s = $ parity of $s$); do not "reject" such samples.
- Claiming Simon shows BPP $\ne$ BQP: it is an oracle separation (relative to Simon's oracle), not an unconditional one.

## Exam-style questions

1. *Derive the distribution of the measured $y$ in Simon's algorithm.* See the computation above: amplitude $2^{-(n+1)/2}(-1)^{x_0\cdot y}[1+(-1)^{s\cdot y}]$, hence $P(y) = 2^{-(n-1)}$ for $y\in s^\perp$ and 0 otherwise.
2. *Why is the answer of a single run insufficient, and how many runs are needed?* One run gives one linear constraint on $s$; $n-1$ independent constraints are needed to pin down the one-dimensional solution space $\{0,s\}$; $n-1$ uniform samples from $s^\perp$ are independent with probability $>\frac14$, so $O(n)$ runs suffice with high probability.
3. *For $n=2$, $s=11$, list $s^\perp$ and explain what a run can return.* $s^\perp=\{00, 11\}$; a run returns $00$ (useless) or $11$ (determines $s=11$ since the only nonzero solution of $s_0\oplus s_1=0$ is $11$) with probability $\frac12$ each.
4. *Give the classical lower bound and its proof idea.* $\Omega(2^{n/2})$: without a collision the answers are indistinguishable from those of a random injective function; $k$ queries collide with probability $O(k^2/2^n)$.
5. *Explain in one paragraph how Simon's algorithm relates to Shor's.* Both are hidden-subgroup algorithms over an abelian group: create a superposition over a coset of the hidden subgroup by evaluating $f$ and measuring its value, apply the group's Fourier transform ($H^{\otimes n}$ for $\mathbb{Z}_2^n$, QFT for $\mathbb{Z}_{2^t}$), sample from the dual, and post-process classically (Gaussian elimination mod 2 vs continued fractions).

## Code

`src/py/quantum/simon.py`: `simon_oracle(s, rng)` (random two-to-one $f$ with period $s$, returned as a table and as a permutation for `Register.apply_permutation`), `simon_sample(f, n, rng)` (one quantum run returning $y$), `simon(f, n, rng)` (collect, solve, verify), `rank_gf2`, `solve_gf2`, `nullspace_gf2` (Gaussian elimination over $\mathbb{F}_2$). `test_simon.py`: random $s$ for $n=3..5$, correct recovery in $\geq95\%$ of seeded trials; unit tests for the GF(2) solver (rank, nullspace dimension, $Ys=0$).
