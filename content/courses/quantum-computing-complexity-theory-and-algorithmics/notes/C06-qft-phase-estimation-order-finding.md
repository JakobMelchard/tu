# C06 Quantum Fourier transform, phase estimation, order finding

The QFT is the Fourier transform over $\mathbb{Z}_N$ implemented with $O(n^2)$ gates on $n=\log N$ qubits (versus $O(N\log N)$ for the classical FFT — but only for producing a *quantum state*, whose amplitudes cannot all be read out). Its main use is phase estimation, which turns an eigenvalue $e^{2\pi i\varphi}$ of a unitary into a binary string, and order finding is phase estimation applied to modular multiplication. Together they are the quantum core of Shor's algorithm (C07). References: Nielsen & Chuang 5.1-5.3, Appendix 4 (continued fractions) [S30]; Kaye, Laflamme, Mosca ch. 7 [S28]; Rieffel & Polak 7.1, 8.2 [S29]; de Wolf ch. 6 [S31]; primary: Kitaev [S45]. Lecture section 6 [S20], whose conventions this note follows: the QFT output comes out **bit-reversed** and the error of the phase estimate is bounded by $2^{-(t+1)}$. The QFT also has a recursive construction from $K_n$ and $D_N$ (below). Exam 2 material.

## Definitions

**QFT on $\mathbb{Z}_N$, $N=2^n$.** The unitary
$$F_N|j\rangle = \frac{1}{\sqrt N}\sum_{k=0}^{N-1}e^{2\pi i jk/N}|k\rangle,\qquad (F_N)_{kj} = \frac{\omega^{jk}}{\sqrt N},\ \omega = e^{2\pi i/N}.$$
It maps amplitudes $x_j$ to $y_k = \frac{1}{\sqrt N}\sum_j x_j\omega^{jk}$ (same as `numpy.fft.ifft` up to the $1/\sqrt N$ normalisation and sign convention). Unitary since the columns are orthonormal ($\sum_k\omega^{(j-j')k} = N\delta_{jj'}$). Basis labels use the big-endian convention $j = j_0 2^{n-1}+\dots+j_{n-1}2^0$ and binary fractions $0.j_lj_{l+1}\dots j_n = \sum_{m=l}^n j_m 2^{-(m-l+1)}$ (in N&C's 1-indexed notation).

**Phase estimation problem.** Given a unitary $U$ and an eigenstate $|u\rangle$ with $U|u\rangle = e^{2\pi i\varphi}|u\rangle$, $\varphi\in[0,1)$, and the ability to apply controlled-$U^{2^j}$, estimate $\varphi$ to $t$ bits.

**Order finding.** For coprime $a<N$, the order $r$ is the least $r\geq1$ with $a^r\equiv1\pmod N$. $U_a|y\rangle = |ay\bmod N\rangle$ for $0\leq y<N$ (and identity on $y\geq N$ if the register is larger) is a permutation of basis states, hence unitary; $U_a^r = I$.

**Continued fractions.** $[a_0;a_1,a_2,\dots] = a_0+\frac{1}{a_1+\frac{1}{a_2+\cdots}}$; the convergents $p_k/q_k$ satisfy $p_k = a_kp_{k-1}+p_{k-2}$, $q_k=a_kq_{k-1}+q_{k-2}$ with $(p_{-1},q_{-1})=(1,0)$, $(p_{-2},q_{-2}) = (0,1)$. A rational number has a finite expansion computed by the Euclidean algorithm.

## Results

**Product form of the QFT (N&C 5.1).** Writing $k = \sum_l k_l2^{n-l}$ (1-indexed bits) and expanding $e^{2\pi ijk/2^n} = \prod_{l=1}^n e^{2\pi i jk_l2^{-l}}$,
$$F_N|j_1\dots j_n\rangle = \frac{1}{\sqrt{2^n}}\bigotimes_{l=1}^{n}\Big(|0\rangle+e^{2\pi i\,0.j_{n-l+1}\dots j_n}|1\rangle\Big)
= \frac{(|0\rangle+e^{2\pi i0.j_n}|1\rangle)(|0\rangle+e^{2\pi i0.j_{n-1}j_n}|1\rangle)\cdots(|0\rangle+e^{2\pi i0.j_1\dots j_n}|1\rangle)}{\sqrt{2^n}},$$
because only the fractional part of $j2^{-l}$ matters in the exponent. The output is a **product state** (the QFT creates no entanglement from a basis state; all the work is in the phases).

**Circuit.** For qubit $j_1$: $H$ gives $\frac{1}{\sqrt2}(|0\rangle+e^{2\pi i0.j_1}|1\rangle)$; then controlled-$R_k$ from $j_k$ with $R_k = \mathrm{diag}(1, e^{2\pi i/2^k})$ for $k=2,\dots,n$ appends the bits $0.j_1j_2\dots j_n$. Repeat for $j_2$ (with $R_2,\dots,R_{n-1}$), etc. This produces the factors in reverse qubit order, so finish with $\lfloor n/2\rfloor$ SWAPs. Gate count $n + (n-1)+\dots+1 = n(n+1)/2$ Hadamards and controlled phases plus swaps: $\Theta(n^2)$. The lecture states the same thing as "if we measure the qubits, we actually get the reverse order in which the bits were provided. To fix this we can apply SWAP gates at the end … a simpler approach is to just relabel the qubits" [S20, §6.1]. **$F_N$ can also be built recursively:**
$$F_2 = H,\qquad F_{2N} = (H\otimes I^{\otimes n})\bigl(|0\rangle\langle0|\otimes I^{\otimes n}+|1\rangle\langle1|\otimes D_{2^n}\bigr)(I\otimes F_N)\,K_{n+1},$$
with $D_N = \bigotimes_{i=1}^{n}P(\pi/2^i) = \mathrm{diag}(1,\omega_{2N},\dots,\omega_{2N}^{N-1})$ and $K_n$ the one-position qubit rotation ($n-1$ SWAPs). **Watch the direction of $K_n$:** the inverse permutation makes the identity hold at $n=2$ and fail from $n=3$. **Approximate QFT:** dropping controlled-$R_k$ with $k>\log n + O(1)$ (phases $<2^{-k}$) leaves $O(n\log n)$ gates with error $O(n2^{-k})$, sufficient for Shor. Inverse QFT: run the circuit backwards with $R_k^\dagger$.

**Phase estimation (Kitaev [S45]; N&C 5.2 [S30]).** $t$ counting qubits in $|0\rangle$, target register in $|u\rangle$.
1. $H^{\otimes t}$ on the counting register: $\frac{1}{\sqrt{2^t}}\sum_{k=0}^{2^t-1}|k\rangle|u\rangle$.
2. Controlled-$U^{2^j}$ with control qubit $j$ (qubit $j$ has weight $2^{t-1-j}$ in big-endian; label so that control of $U^{2^m}$ is the bit of weight $2^m$). Phase kickback (C01) gives $|k\rangle|u\rangle\mapsto e^{2\pi i\varphi k}|k\rangle|u\rangle$, since $U^k|u\rangle = e^{2\pi i\varphi k}|u\rangle$ and $k = \sum_m k_m2^m$. State: $\frac{1}{\sqrt{2^t}}\sum_k e^{2\pi i\varphi k}|k\rangle|u\rangle$. Note this equals $F_{2^t}|2^t\varphi\rangle$ when $2^t\varphi$ is an integer.
3. Inverse QFT on the counting register, then measure: outcome $m$.

*Exact case.* If $\varphi = m_0/2^t$ exactly, step 2 produces $F_{2^t}|m_0\rangle$ and $F^{-1}$ returns $|m_0\rangle$: outcome $m_0$ with certainty; $\varphi = m_0/2^t$ read off in binary.

*General case.* Amplitude of outcome $m$: $\alpha_m = \frac{1}{2^t}\sum_{k=0}^{2^t-1}e^{2\pi i k(\varphi - m/2^t)} = \frac{1}{2^t}\cdot\frac{1-e^{2\pi i(2^t\varphi-m)}}{1-e^{2\pi i(\varphi-m/2^t)}}$ (geometric sum). Let $\delta = \varphi - m/2^t$ with $|\delta|\leq 2^{-t-1}$ for the *best* $t$-bit approximation $m$. Using $|1-e^{i\theta}| = 2|\sin(\theta/2)|$ and $|\sin x|\geq 2|x|/\pi$ for $|x|\leq\pi/2$, $|\sin x|\leq|x|$:
$$|\alpha_m|^2 = \frac{1}{4^t}\frac{\sin^2(\pi 2^t\delta)}{\sin^2(\pi\delta)}\geq\frac{1}{4^t}\frac{(2\cdot 2^t\delta)^2}{(\pi\delta)^2}=\frac{4}{\pi^2}\approx0.405 .$$
So the nearest $t$-bit approximation is returned with probability $\geq4/\pi^2$, and the two nearest together with probability $\geq 8/\pi^2 \approx 0.81$. To obtain $\varphi$ to $n$ bits with failure probability at most $\epsilon$, use $t = n + \lceil\log_2(2+\frac{1}{2\epsilon})\rceil$ counting qubits (N&C eq. 5.35; proof: bound the tail $\sum_{|m-2^t\varphi|>e}|\alpha_m|^2\leq\frac{1}{2(e-1)}$ with $e = 2^{t-n}-1$).

If the target is not an eigenstate but a superposition $\sum_s c_s|u_s\rangle$, linearity gives outcome "estimate of $\varphi_s$" with probability $|c_s|^2$ (the counting register becomes entangled with the eigenstate index). This is exactly what order finding exploits.

**Order finding as phase estimation (N&C 5.3.1).** The eigenstates of $U_a$ are, for $s=0,\dots,r-1$,
$$|u_s\rangle = \frac{1}{\sqrt r}\sum_{k=0}^{r-1}e^{-2\pi isk/r}|a^k\bmod N\rangle,\qquad U_a|u_s\rangle = e^{2\pi is/r}|u_s\rangle,$$
(shift $k\to k-1$ in the sum) and they satisfy $\frac{1}{\sqrt r}\sum_{s=0}^{r-1}|u_s\rangle = |1\rangle$ (the $k\ne0$ terms cancel since $\sum_s e^{-2\pi isk/r}=0$). So preparing the target register in $|1\rangle$, which needs no knowledge of $r$, and running phase estimation returns a $t$-bit approximation of $s/r$ for a uniformly random $s\in\{0,\dots,r-1\}$. Equivalent "period-finding" picture: the state after the controlled multiplications is $\frac{1}{\sqrt{2^t}}\sum_k|k\rangle|a^k\bmod N\rangle$; measuring the second register collapses the first onto $\{k_0, k_0+r, k_0+2r,\dots\}$, a comb of period $r$; the QFT of a comb of period $r$ is a comb of period $2^t/r$, i.e. peaks at $m\approx s\,2^t/r$.

Controlled-$U_a^{2^j}$ is implemented as controlled multiplication by $a^{2^j}\bmod N$ (precomputed classically by repeated squaring), so the cost is $t$ controlled modular multiplications, each $O(n^2)$ (schoolbook) gates: $O(n^3)$ total with $t = 2n+O(1)$; the QFT adds $O(n^2)$. Register sizes: $n=\lceil\log_2N\rceil$ work qubits plus $t$ counting qubits.

**Recovering $r$ from the estimate (continued fractions).** The measurement gives $m$ with $|m/2^t - s/r|\leq 2^{-t-1}$ (with probability $\geq4/\pi^2$). With $t\geq 2n+1$ this is $\leq\frac{1}{2N^2}\leq\frac{1}{2r^2}$, and:

**Theorem (N&C 5.1 / App. 4).** If $|p/q - x|\leq\frac{1}{2q^2}$ then $p/q$ is a convergent of the continued fraction of $x$.

So compute the convergents of $m/2^t$ and pick the one with denominator $q\leq N$ closest to $m/2^t$; then $q$ is a candidate for $r$ (exactly $r$ when $\gcd(s,r)=1$; otherwise a divisor of $r$). Check $a^q\equiv1$; if not, either try small multiples of $q$ or repeat and take the lcm of two candidates. The probability that a random $s$ is coprime to $r$ is $\phi(r)/r = \Omega(1/\log\log r)$, so $O(\log\log N)$ repetitions suffice; the lcm trick makes it $O(1)$ expected repetitions.

## Worked example

Continued fraction of $x = 1365/2048$ ($t=11$ bits, $m = 1365$; this is what phase estimation returns most often when $s/r = 2/3$, since $2^{11}\cdot\frac23 = 1365.33$). Euclid on $(1365, 2048)$:
$$2048 = 1\cdot1365+683,\quad 1365 = 1\cdot683+682,\quad 683=1\cdot682+1,\quad 682 = 682\cdot1+0 .$$
Thus $x = 1/(1+1/(1+1/(1+1/682))) = [0;1,1,1,682]$. Convergents: $p/q$: $0/1$, $1/1$, $1/2$, $2/3$, $1365/2048$. With $N$ say $N=15$ (so $q\leq15$), the last convergent with $q\le N$ is $2/3$; candidate $r=3$. Check: $|1365/2048 - 2/3| = 1.63\cdot10^{-4}\leq\frac{1}{2\cdot9}$ ✓ [verified: `test_order_finding.py`]. (For $N=15$, $a=4$ has order 2 and $a=2$ has order 4; order 3 does not occur mod 15 — the example is arithmetic only; a real case with $r=6$ is worked in C07.)

Phase estimation numbers: $\varphi = 2/3$, $t=3$: $2^t\varphi = 5.33$; $|\alpha_5|^2 = \frac{1}{64}\frac{\sin^2(\pi\cdot0.333)}{\sin^2(\pi\cdot0.0417)} = \frac{1}{64}\cdot\frac{0.75}{0.017038} = 0.688$, $|\alpha_6|^2 = \frac{1}{64}\frac{\sin^2(\pi\cdot0.667)}{\sin^2(\pi\cdot0.0833)}=\frac{1}{64}\cdot\frac{0.75}{0.06699}=0.175$; sum $0.863\geq8/\pi^2 = 0.811$ ✓. In code: `phase_estimation(U, u, t)` in `src/py/quantum/phase_estimation.py`, `continued_fraction(1365, 2048)` and `convergents` in `src/py/quantum/order_finding.py`.

QFT on 3 qubits applied to $|j\rangle = |5\rangle = |101\rangle$: product form gives $\frac{1}{\sqrt8}(|0\rangle+e^{2\pi i\,0.1}|1\rangle)(|0\rangle+e^{2\pi i\,0.01}|1\rangle)(|0\rangle+e^{2\pi i\,0.101}|1\rangle) = \frac{1}{\sqrt8}(|0\rangle-|1\rangle)(|0\rangle+i|1\rangle)(|0\rangle+e^{5\pi i/4}|1\rangle)$; the first factor belongs to the *least* significant output qubit (hence the final swaps), and the amplitude of $|k\rangle$ is $\omega^{5k}/\sqrt8$ as required.

## Pitfalls

- Reading the QFT output in the wrong bit order: without the final swaps the circuit computes $F_N$ followed by bit reversal. Simulators often skip the swaps and reverse the labels instead; be explicit.
- Confusing $F_N$ with its inverse (sign of the exponent). Phase estimation uses $F^{-1}$ at the end because step 2 *produces* $F|2^t\varphi\rangle$.
- Assuming phase estimation is exact: it is exact only for dyadic $\varphi$; otherwise the best approximation is returned with probability $\geq 4/\pi^2$, and extra counting qubits are needed for a high success probability, not more repetitions of the same $t$.
- Using $t = n$ counting qubits for order finding: the continued-fraction theorem needs $|m/2^t - s/r|\leq 1/(2r^2)$, which requires $t\geq 2n+1$ (precision $2^{-t-1}\leq 1/(2N^2)$).
- Taking the *last* convergent (which is $m/2^t$ itself): the correct rule is the convergent with denominator $\leq N$.
- $\gcd(s,r)>1$ returns a divisor of $r$; always verify $a^q\equiv1\pmod N$.
- The controlled-$U^{2^j}$ gates must be implemented by modular exponentiation, not by $2^j$ repetitions; otherwise the algorithm is exponential.

## Exam-style questions

1. *Write $F_4$ as a matrix and verify that it is unitary.* $F_4 = \frac12\begin{pmatrix}1&1&1&1\\1&i&-1&-i\\1&-1&1&-1\\1&-i&-1&i\end{pmatrix}$; columns are orthonormal because $\sum_k i^{(j-j')k} = 4\delta_{jj'}$.
2. *How many gates does the exact QFT on $n$ qubits need, and why is that not an exponential speedup over the FFT?* $n(n+1)/2$ $H$/controlled-$R_k$ gates plus $\lfloor n/2\rfloor$ swaps, $\Theta(n^2)$ for $N=2^n$ amplitudes. The FFT computes all $N$ output values; the QFT only produces a state whose amplitudes are the transform, and measuring it reveals one sample. The speedup is only useful when a sample from the Fourier distribution suffices (period finding).
3. *Phase estimation with $t=4$ on $\varphi = 0.3$: what is the most likely outcome and a lower bound on its probability?* $2^4\cdot0.3 = 4.8$; nearest integer $m=5$ ($\varphi\approx0.3125$), probability $\geq4/\pi^2\approx0.405$. Actual: with $\delta = \varphi - m/2^t = -0.0125$, $|\alpha_5|^2 = \frac{1}{256}\sin^2(0.2\pi)/\sin^2(0.0125\pi) = 0.8756$ and $|\alpha_4|^2 = \frac{1}{256}\sin^2(0.8\pi)/\sin^2(0.05\pi) = 0.0551$, together $0.931\geq8/\pi^2$. (Note which $\delta$ goes with which $m$: the $0.8\pi$ numerator belongs to $m=4$, not to the nearest estimate.)
4. *Show that $|1\rangle = \frac{1}{\sqrt r}\sum_s|u_s\rangle$.* $\frac{1}{\sqrt r}\sum_s|u_s\rangle = \frac1r\sum_k\big(\sum_s e^{-2\pi isk/r}\big)|a^k\rangle = \frac1r\cdot r|a^0\rangle = |1\rangle$ since the inner sum is $r\delta_{k,0}$.
5. *Given $m = 427$ from $t=9$ counting qubits and $N=21$, find the candidate order.* $427/512$: $512 = 1\cdot427+85$, $427 = 5\cdot85+2$, $85=42\cdot2+1$, so $[0;1,5,42,2]$; convergents $0/1, 1/1, 5/6, 211/253,\dots$; the last with denominator $\leq21$ is $5/6$: candidate $r=6$ (e.g. for $a=2$: $2^6=64\equiv1\pmod{21}$ ✓).

## Code

`src/py/quantum/qft.py`: `qft(reg, qubits)`, `inverse_qft(reg, qubits)` as $H$ + controlled-phase + swap circuits, `qft_matrix(n)` for cross-checks. `src/py/quantum/phase_estimation.py`: `phase_estimation(U, eigenstate, t, rng)` returning the measured $m$ and $m/2^t$. `src/py/quantum/order_finding.py`: `order_finding(a, N, rng)` (permutation-based controlled $U_a^{2^j}$, inverse QFT, continued fractions), `continued_fraction`, `convergents`, `order_classical`. Tests: QFT vs DFT matrix for $n\leq5$; exact recovery of dyadic phases; $\geq40\%$ success on non-dyadic phases; orders of $7, 2, 11$ mod 15.
