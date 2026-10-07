# 01 Amdahl's law, Gustafson's law, strong and weak scaling

TISS topic 1, spelled "Ahmdal's Law" on the page [S2]. The lecturer's own
version is one line: $T_\text{total} = T_\text{serial} + T_\text{parallel}/p$,
"speed-up limited by serial portion of an algorithm" [S4 `bottlenecks.tex`].
The OpenMP-side treatment (Karp-Flatt on a measured thread sweep, E-cores vs
P-cores on this Mac) is in NSSC I note 07 [S40]; this note adds the many-core
view: offload, scaled problems, and what a bandwidth limit does to the laws.
Code: `src/py/perf_models.py`.

## Definitions

- $T_1$: time of the **best serial** code; $T_p$: time on $p$ processing elements.
- Speedup $S(p) = T_1/T_p$, efficiency $E(p) = S(p)/p$.
- **Strong scaling**: fixed problem, vary $p$. Ideal $S = p$.
- **Weak scaling**: problem size $\propto p$, vary $p$. Ideal $T_p = T_1$, i.e. scaled speedup $= p$.
- Serial fraction, two different normalisations [S37]:
  - Amdahl: $f = t_s / (t_s + t_p)$ of the **1-processor** run [S9];
  - Gustafson: $s = t_s' / (t_s' + t_p')$ of the **$p$-processor** run [S10].

## Amdahl (fixed size)

With $T_1 = t_s + t_p$ and perfect parallelisation of $t_p$:
$$T_p = t_s + \frac{t_p}{p}\;\Rightarrow\; S_A(p) = \frac{1}{f + (1-f)/p} \xrightarrow{p\to\infty} \frac{1}{f}.$$
$\partial S_A/\partial f$ at $f=0$ is $-p(p-1) \approx -p^2$: at $p = 1024$ the curve is so steep that 1 % serial work caps you at 91x, 4 % at 24x (Gustafson's Figure 1 [S10]).

**Worked example, $f = 0.05$** (`perf_models.py`):

| $p$ | 1 | 12 | 132 | 1024 | $\infty$ |
|---|---|---|---|---|---|
| $S_A$ | 1 | 7.74 | 17.48 | 19.64 | 20 |
| $E$ | 1 | 0.65 | 0.13 | 0.019 | 0 |

A GPU with $10^4$ threads in flight [S4 `cuda.tex`] is Amdahl's worst case: any
code left on the host becomes $f$.

**Offload form.** Accelerate a fraction $a$ of the runtime by a factor $k$; data
transfers add $\tau$ (as a fraction of the old runtime):
$$S = \frac{1}{(1-a) + a/k + \tau}.$$
$a = 0.9$, $k = 20$: $S = 6.90$; with transfers worth 10 % of the old runtime,
$S = 4.08$ (`offload_speedup`). A 20x kernel became a 4x application. This is
why Rupp calls speedups $\gg 10$ "(usually) not backed by hardware" [S4
`gpus.tex`] [S6]: bandwidth ratios between a GPU and one CPU socket are ~10x
[S6], so a memory-bound kernel cannot gain much more, and the rest of the code
dilutes even that.

## Gustafson (scaled size)

Keep the parallel wall time fixed and let the problem grow with $p$ [S10]:
$t_s'$ and $t_p'$ measured on the parallel machine, serial time would be
$t_s' + p\,t_p'$, so
$$S_G(p) = s + (1-s)\,p = p - (p-1)\,s.$$
Linear in $p$ with slope $1-s$. Gustafson's 1024-processor hypercube: speedups
1021, 1020, 1016 for three applications with $s$ = 0.4-0.8 % [S10]; the formula
gives $S_G(1024) = 1019.9$ at $s = 0.004$ and 1015.8 at $0.008$
(`test_perf_models.py::test_gustafson_reproduces_the_1988_paper`).

**They are one law** [S37]. The same run has $f = s/(s + (1-s)p)$; substituting
turns $S_A$ into $S_G$ exactly (`test_the_two_laws_are_one_law`). For
Gustafson's run, $s = 0.004$ at $p = 1024$ corresponds to $f = 3.9\cdot10^{-6}$:
the serial part did not grow with the problem, so as a fraction of the (huge)
1-processor run it is tiny. Amdahl is not "broken"; the problem changed.

## Karp-Flatt (reading a measurement)

Invert Amdahl for the measured serial fraction
$$e(p) = \frac{1/S(p) - 1/p}{1 - 1/p}.$$
Constant $e$: true serial part. Rising $e$: overhead, contention or a shared
resource.

**Worked example, measured on this Mac** (`make -C src/cpp bench`, 2026-09-28,
[S32]): STREAM triad bandwidth 104.9 GB/s on 1 thread, 121.4 GB/s best (6
threads). So $S(6) = 1.16$ and $e(6) = (0.864 - 0.167)/0.833 = 0.84$. Nobody
wrote 84 % serial code: the kernel is **bandwidth bound** and one core already
draws 86 % of the chip's DRAM bandwidth. Amdahl assumes the parallel part
scales; a shared resource violates that assumption, and Karp-Flatt reports the
violation as a fake serial fraction.

Second example, a sum reduction over $2^{25}$ doubles: naive serial loop
27.55 ms, OpenMP `reduction` on 12 threads 4.36 ms, "speedup" 6.3 (a second run: 25.7 and 3.02 ms, 8.5; the machine was shared, note 02). The serial
loop is latency bound (one dependent add per iteration, 9.7 GB/s), so it is not
the best serial code: a 4- or 8-accumulator serial loop runs several times
faster (NSSC I note 01 [S40]). Baseline choice changes $S$ more than the
threading does.

## Strong vs weak scaling on many-core hardware

| | strong | weak |
|---|---|---|
| question | same problem, faster? | $p$ times bigger problem, same time? |
| limited by | $f$, per-kernel latency ($\alpha$, note 03), load imbalance | communication/halo growth, global reductions |
| GPU symptom | small $N$ cannot fill the device: $N < n_{1/2}$ | memory capacity per device fixes $N/p$ |

Weak scaling of a 2-D stencil on $p$ subdomains of $m\times m$ points: work
$\propto m^2$, halo exchange $\propto 4m$ per iteration, so the
communication-to-computation ratio $4/m$ is independent of $p$: ideal weak
scaling, as long as the exchange latency $\alpha$ is small against $m^2$ work.
Strong scaling of the same stencil: $m = M/\sqrt p$, ratio $4\sqrt p/M$ grows.
`src/cpp/stencil_halo.cpp` (`Strips`) runs 12 strips with an explicit halo
exchange at 6574 MLUP/s vs 6446 for the global sweep: the exchange is 12 rows of
4096 doubles per sweep, negligible here.

## Pitfalls

- Measuring $S$ against the parallel code on 1 thread instead of the best serial code.
- Calling a bandwidth plateau a "serial fraction" (above).
- Quoting Gustafson's $s$ in Amdahl's formula (the 1988 controversy [S37]).
- Ignoring transfers in an offload estimate (`offload_speedup` with $\tau$).
- Heterogeneous hardware: 6 P-cores + 6 E-cores are not 12 equal $p$ (NSSC I note 07 [S40]).

## Oral-exam questions

1. **State and derive Amdahl's law. What is the maximum speedup for $f = 2\%$?**
   $T_p = fT_1 + (1-f)T_1/p$; $S = 1/(f + (1-f)/p)$; limit $1/f = 50$.
2. **A kernel taking 80 % of the runtime is ported to a GPU and runs 50x faster. Application speedup?**
   $1/(0.2 + 0.8/50) = 4.6$. Upper bound 5 however fast the GPU is.
3. **Why do Amdahl and Gustafson predict such different numbers? Are they contradictory?**
   Different assumptions: fixed size vs fixed time. Same law with $f = s/(s+(1-s)p)$ [S37]; Gustafson's problems grew with $p$, so $f$ shrank.
4. **Your code's speedup saturates at 1.2 on 12 cores. How do you decide between a serial bottleneck and a bandwidth limit?**
   Compute the arithmetic intensity and compare the achieved GB/s with STREAM (note 02); if achieved bandwidth equals STREAM, it is bandwidth. Karp-Flatt alone cannot tell them apart.
5. **Strong vs weak scaling: which one is relevant for a GPU cluster running a 3-D PDE, and why?**
   Usually weak: one fills each GPU's memory; strong scaling runs out of work per GPU once $N/p < n_{1/2}$ and the per-step latency (launch, halo, reduction) dominates.

Code: `src/py/perf_models.py` (`amdahl`, `gustafson`, `amdahl_f_from_gustafson_s`, `karp_flatt`, `offload_speedup`), tests `src/py/test_perf_models.py`; `src/cpp/stencil_halo.cpp` (`Strips`). Sources: [S4] [S6] [S9] [S10] [S32] [S37] [S40].
