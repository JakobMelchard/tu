# 06 Random number generation and Monte Carlo

Pseudo-random numbers are a deterministic sequence that passes statistical tests; Monte Carlo turns integrals and expectations into sample averages whose error shrinks as $1/\sqrt{N}$ regardless of dimension.

This is the note with the most *checkable* content in the course: every generator claim below comes from an original paper and three of them are exact, reproducible statements that `src/py/lattice.py` and `src/py/test_lattice.py` verify - Hull & Dobell's full-period theorem [S29], Marsaglia's RANDU lattice [S27], and the test vectors the C++ standard requires [S14]. Reference code: `src/cpp/rng_mc.cpp`, `src/py/montecarlo.py`.

## Linear congruential generators

$$x_{k+1} = (a x_k + c) \bmod m, \qquad u_k = x_k / m \in [0, 1).$$

- Period at most $m$. **Full period for every seed iff** (Hull & Dobell 1962 [S29]) $\gcd(c, m) = 1$, $a - 1$ is divisible by every prime factor of $m$, and $a - 1$ is divisible by 4 if $m$ is. It is an *iff*, and `test_lattice.py` checks it exhaustively over all 256 pairs $(a,c)$ with $m = 16$ and all 16 seeds. With $c = 0$ (multiplicative) Hull-Dobell cannot apply ($\gcd(0,m) = m$); for prime $m$ the period is $m - 1$ iff $a$ is a primitive root mod $m$ [S28].
- **minstd** (Park & Miller 1988 [S28]): $a = 16807$, $c = 0$, $m = 2^{31} - 1$, which is `std::minstd_rand0`: 16807, 282475249, 1622650073, .... The C++ standard *requires* [S14, rand.predef] that the **10000th** consecutive value from the default seed be **1043618065**; for `std::minstd_rand` ($a = 48271$) it is **399268537** and for `std::mt19937` it is **4123659995**. All three are asserted in `test_lattice.py` and `rng_mc.cpp` - the cheapest possible correctness check on any RNG implementation.
- **Weakness: the lattice.** Overlapping $k$-tuples $(u_i, \dots, u_{i+k-1})$ of *any* LCG lie on a lattice, hence on at most $(k!\,m)^{1/k}$ parallel hyperplanes - Marsaglia 1968, "Random numbers fall mainly in the planes" [S27]. For $m = 2^{31}$ and $k = 3$ that generic bound is about **2344** planes. **RANDU** ($a = 65539 = 2^{16}+3$, $c = 0$, $m = 2^{31}$) is far worse than the bound allows: since $(a-3)^2 = 2^{32} \equiv 0 \pmod{2^{31}}$,
  $$x_{k+2} - 6x_{k+1} + 9x_k \equiv 0 \pmod{2^{31}}$$
  **identically**, and the coefficients $(9,-6,1)$ force every triple onto one of **15** planes. Both statements are exact and both are tested: `test_lattice.py` finds residual 0 over 50 000 triples from three seeds, and exactly 15 occupied planes.
- With $m = 2^{32}$ the low bits have tiny periods (bit $j$ cycles with period $2^{j+1}$), so never use `x % 6` from such a generator. `rand()` in C is often an LCG of this kind.
- Toy example in `rng_mc`: $a = 5, c = 1, m = 16$ from 0: 1 6 15 12 13 2 11 8 9 14 7 4 5 10 3 0 and back to 1.

## Mersenne Twister (MT19937)

Matsumoto & Nishimura 1998 [S26]. State of 624 32-bit words (2.5 KB), period $2^{19937} - 1$, and - this is the paper's title claim - **623-dimensionally equidistributed to 32-bit accuracy**, meaning every 623-tuple of successive outputs occurs equally often over a period. ~1 ns per number. `std::mt19937` (default seed 5489; 10000th value 4123659995), `numpy.random.RandomState`. Not cryptographic (624 outputs reveal the state); slow to seed properly (needs a full state, use `std::seed_seq`); fails a few linear-complexity tests. numpy's default is now PCG64 (small state, faster, passes TestU01), and xoshiro256** is common in C++ codes. *(Unsourced: the PCG/xoshiro comparison. Neither generator has a course-relevant primary source here and the claim is from their authors' own documentation; nothing in the notes depends on it.)* For cryptography use `std::random_device` / OS sources only.

## Seeding

- Reproducibility: fix the seed and record it; a run you cannot repeat cannot be debugged.
- `std::random_device` for a non-reproducible seed; do not seed with `time(0)` in a loop (identical seeds within one second).
- Parallel streams: one generator per thread, seeded differently (`seed + thread_id` is acceptable for MT; better: `std::seed_seq`, or generators with `jump()`/streams such as PCG and `numpy.random.SeedSequence.spawn`). Sharing one generator between threads is a data race and also serialises the code.

## From uniform to other distributions

**Inverse transform**: if $U \sim \mathcal{U}(0,1)$ then $X = F^{-1}(U)$ has CDF $F$. Exponential: $F(x) = 1 - e^{-\lambda x}$, $X = -\ln(1 - U)/\lambda$ (use `log1p(-u)` for accuracy, and $1 - U$ rather than $U$ to avoid $\ln 0$). Discrete distributions: binary search in the cumulative table.

**Box-Muller** (Box & Muller 1958 [S30], two pages): two independent uniforms give two independent standard normals,
$$Z_0 = \sqrt{-2 \ln U_1}\cos 2\pi U_2, \qquad Z_1 = \sqrt{-2 \ln U_1}\sin 2\pi U_2.$$
Derivation: the joint density of $(Z_0, Z_1)$ is $\frac{1}{2\pi} e^{-r^2/2}$; in polar coordinates $R^2 \sim \text{Exp}(1/2)$, hence $R = \sqrt{-2 \ln U_1}$, and $\Theta \sim \mathcal{U}(0, 2\pi)$. The polar (Marsaglia) variant avoids the trig calls by rejection. Libraries use the ziggurat method instead (faster); `std::normal_distribution`, `rng.normal()`.

**Rejection sampling**: to sample density $f \le M g$, draw $X \sim g$, accept with probability $f(X)/(M g(X))$; acceptance rate $1/M$. **Transformations**: $\mu + \sigma Z$, $\chi^2$ as a sum of squares, etc.

## Monte Carlo integration

$$I = \int_\Omega f\,dx = |\Omega|\,\mathbb{E}[f(X)], \quad X \sim \mathcal{U}(\Omega); \qquad \hat{I}_N = \frac{|\Omega|}{N} \sum_{k=1}^N f(X_k).$$

Unbiased; by the central limit theorem
$$\hat{I}_N - I \approx \mathcal{N}\!\left(0, \frac{\sigma_f^2 |\Omega|^2}{N}\right), \qquad \text{std. error} = \frac{|\Omega|\,\sigma_f}{\sqrt{N}}, \quad \sigma_f^2 = \text{Var}\,f(X),$$
estimated from the same sample by $\hat{\sigma}_f^2 = \frac{1}{N-1}\sum (f_k - \bar{f})^2$. Error $\propto N^{-1/2}$ **independent of dimension** $d$; a product quadrature rule of order $p$ has error $N^{-p/d}$, so MC wins for $d > 2p$ (in practice $d \gtrsim 6$-$10$), and for non-smooth integrands.

Estimating $\pi$: $f = 4 \cdot \mathbb{1}[x^2 + y^2 < 1]$, $\sigma_f = 4\sqrt{p(1-p)}$ with $p = \pi/4$: std. error $1.64/\sqrt{N}$.

Quasi-Monte Carlo (Sobol, Halton low-discrepancy sequences): error $O((\log N)^d / N)$, much better than $N^{-1/2}$ for moderate $d$ and smooth $f$; `scipy.stats.qmc`.

## Variance reduction

The only lever is $\sigma_f$; the $1/\sqrt{N}$ law itself cannot be beaten.

- **Antithetic variates**: average $f(U)$ and $f(1 - U)$; for monotone $f$ they are negatively correlated, $\text{Var} = \frac{1}{2}(\sigma_f^2 + \text{Cov})$.
- **Control variates**: $\hat{I} = \overline{f - c\,g} + c\,\mathbb{E}[g]$ with a $g$ of known mean; optimal $c = \text{Cov}(f,g)/\text{Var}(g)$ reduces the variance by the factor $1 - \rho_{fg}^2$.
- **Importance sampling**: sample $X \sim p$, average $f(X)/p(X)$; the variance vanishes for $p \propto |f|$. Essential for rare events and peaked integrands.
- **Stratified sampling**: split $\Omega$ into cells, sample each proportionally; removes the variance between strata.

## Worked example (`./bin/rng_mc`)

```
         N   rms err pi   4*sqrt(p(1-p)/N)  ratio
       100     1.75e-01     1.64e-01        1.06
      1000     5.64e-02     5.19e-02        1.09
     10000     1.58e-02     1.64e-02        0.96
    100000     5.49e-03     5.19e-03        1.06
   1000000     1.90e-03     1.64e-03        1.16
fitted slope of log(err) vs log(N): -0.494 (theory -0.5)
```
Each RMS error is over 20 independent runs; a single run's error would scatter by a factor of 2-3 around the line. To gain one decimal digit you need 100x the samples.

$\int_0^1 e^x dx = e - 1$ with $N = 10^5$, RMS error over 20 runs: plain 1.5e-3, antithetic 2.0e-4 (variance reduction 54x, because $e^u$ and $e^{1-u}$ are strongly anti-correlated), control variate $g = 1 + u$ 6.8e-4 (4.8x with fixed $c = 1$; the optimal $c$ used in the Python version gives 100x).

## Pitfalls

- Reporting an MC result without an error bar; or estimating the error from a single run's deviation from a value you happen to know.
- `rand() % n`: modulo bias plus weak low bits. Use `std::uniform_int_distribution`.
- Generating `float` uniforms: only $2^{24}$ distinct values, rounding to exactly 1.0 possible; `log(0)` in Box-Muller.
- Same seed in every MPI rank or OpenMP thread: $p$ copies of the same sample, no extra information.
- Re-seeding inside a loop (each iteration restarts the sequence).
- Comparing MC to a quadrature rule at low dimension and concluding MC is useless; or at high dimension with a smooth integrand and ignoring QMC.
- Testing a normal generator only by mean and variance: use a KS test (`test_montecarlo.py`) or a histogram against the density.

## Exam-style questions

1. **State the LCG recurrence and the conditions for full period. Why is an LCG with $m = 2^{32}$ a poor choice for `x % 2`?** $x_{k+1} = (a x_k + c) \bmod m$; full period iff $\gcd(c,m) = 1$, $a - 1$ divisible by all prime factors of $m$, and by 4 if $4 \mid m$ [S29]. With a power-of-two modulus the lowest bit alternates with period 2, so `x % 2` gives 0,1,0,1,...

   *(1b, and the one with a single right answer: **show that every RANDU triple lies on one of 15 planes.** $a = 65539 = 2^{16}+3$, so $a^2 = 2^{32} + 6\cdot2^{16} + 9 \equiv 6a - 9 \pmod{2^{31}}$, hence $x_{k+2} \equiv 6x_{k+1} - 9x_k$. The integer $9x_k - 6x_{k+1} + x_{k+2}$ is a multiple of $2^{31}$ and lies strictly between $-6\cdot2^{31}$ and $10\cdot2^{31}$, so it takes at most 15 values. [S27].)*
2. **Derive the Box-Muller transform.** Two independent standard normals have joint density $\frac{1}{2\pi} e^{-(x^2+y^2)/2}$. In polar coordinates the angle is uniform on $[0, 2\pi)$ and $R^2$ has density $\frac{1}{2} e^{-s/2}$, i.e. exponential with mean 2, so $R^2 = -2 \ln U_1$ by inverse transform. Hence $Z_0 = R \cos\Theta$, $Z_1 = R \sin \Theta$.
3. **How many samples are needed to estimate $\pi$ to $\pm 10^{-4}$ (one standard error), and what does that cost at 10 ns per sample?** $1.64/\sqrt{N} = 10^{-4} \Rightarrow N = 2.7 \cdot 10^8$, about 3 s. To $\pm 10^{-6}$: $2.7 \cdot 10^{12}$ samples, 7.5 hours; quadrature would do it in microseconds. MC is for high dimensions, not for $\pi$.
4. **Explain why MC integration beats tensor-product quadrature in high dimensions.** Quadrature with $m$ points per axis needs $N = m^d$ evaluations for error $O(m^{-p}) = O(N^{-p/d})$; MC error is $O(N^{-1/2})$ independent of $d$. The crossover is $d = 2p$: for Simpson ($p = 4$) at $d = 8$ both scale alike; beyond that MC wins, and it also needs no smoothness.
5. **What is a control variate and how do you choose the coefficient?** A function $g$ correlated with $f$ whose mean is known. Estimate $\mathbb{E}[f - c(g - \mathbb{E}g)]$; the variance is $\sigma_f^2 - 2c\,\text{Cov}(f,g) + c^2 \sigma_g^2$, minimised at $c^* = \text{Cov}(f,g)/\sigma_g^2$, leaving $\sigma_f^2 (1 - \rho^2)$. Estimate $c^*$ from a pilot sample (or the same sample, at the cost of a small bias).

Code: `src/cpp/rng_mc.cpp` (`LCG`, `exponential`, `box_muller`, `mc_pi`, `mc_exp_integral`), `src/py/montecarlo.py` (`LCG`, `box_muller`, `mc_integral`, `mc_antithetic`, `mc_control_variate`, `error_scaling`), `src/py/lattice.py` (`hull_dobell`, `period`, `marsaglia_plane_bound`, `randu_triple_residual`, `randu_plane_count`); tests `src/py/test_montecarlo.py`, `src/py/test_lattice.py`. Sources: [S14] [S26] [S27] [S28] [S29] [S30].
