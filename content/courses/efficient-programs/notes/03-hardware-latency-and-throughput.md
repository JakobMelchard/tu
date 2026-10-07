# 03 Hardware: latency and throughput

Slides 14 to 19 and 26 to 27 [S3]; the script's 2001 table for comparison
[S4]; Agner Fog for per-core numbers [S13]. Exercise 2 [S6] covers this topic.
The topic: what a modern core does with a stream of instructions, and the
one quantity that decides how fast a loop can run: the longest chain of
dependent operations per iteration.

## The latency table [S3 p.14]

Approximate costs as the slide gives them (its text layer encodes the range
dashes as a control character that `pdftotext` drops, so the `.txt` in
`refs/cite-only/` reads "28", "35c", "30 90c"; restored here from the
rendered slide):

| operation | cost |
|---|---|
| independent instructions per cycle | 2 to 8 |
| ALU instruction latency | 1 c |
| load, L1 hit | 3 to 5 c |
| load, L1 miss, L2 hit | 14 c |
| load, L2 miss, L3 hit | 50 c |
| load, L3 miss, DRAM | "50–ns" as printed (upper bound missing); p.21 says RAM ≈ 50 ns |
| transfer of one 64 B line, DDR4-2666 / DDR5-5200 | 3 ns |
| correctly predicted branch | 0 to 1 c |
| mispredicted branch | 20 c |
| integer multiply latency | 4 c |
| FP add / multiply latency | 4 c |
| division latency | 30 to 90 c |
| IP ping, local Ethernet | > 100 µs |
| 1 KB over GB Ethernet | 10 µs |
| disk seek + rotation | 10 ms |
| 2 500 KB sequential disk read | 10 ms |

Against the script's 2001 table [S4] (1 c = 0.5 to 2 ns then; 3 to 4
independent instructions; L1 hit 2 to 3 c; L2 hit 10 c; DRAM 100 ns;
mispredict 10 c; division 50 c; 100 Mb Ethernet 100 µs): latencies in cycles
grew, DRAM in ns halved, the memory wall widened. The consequences the
script draws: cache misses matter more than instruction counts now, branch
prediction did not exist when Bentley wrote, and some of his optimisations
no longer pay [S4].

## Out-of-order execution [S3 p.15] [S21]

The slide is a Sandy Bridge block diagram [S21]; the mechanism, in general
terms: the core fetches and decodes in program order into a window of some
hundred instructions (352-entry reorder buffer on Ice Lake [S13]), executes any instruction whose operands are ready on any free
unit, and retires in order. Consequences: independent instructions overlap,
so *throughput* is up to 2 to 8 per cycle; dependent instructions cannot
overlap, so a chain of them costs the sum of their *latencies* whatever the
width of the machine; a mispredicted branch flushes the window, so the 20 c
is the refill time.

## Recurrences and the cycles-per-iteration bound [S3 p.16 to 18] [S8]

A **recurrence** is a value that lives from one iteration to the next: a
loop counter, an accumulator, a pointer being chased. Its operations form a
chain across iterations. If the chain that closes on itself after one
iteration has latency $L$ cycles, then for a long loop

$$\frac{\text{cycles}}{\text{iteration}} \;\ge\; \max\Bigl(\; \max_{\text{recurrences } r} \frac{L_r}{d_r},\; \max_{\text{resources } u} \frac{n_u}{T_u}\Bigr),$$

where $d_r$ is the number of iterations the recurrence spans (1 for
`r += a[i]`), $n_u$ the number of operations per iteration needing unit
class $u$ and $T_u$ that class's throughput per cycle. The first term is the
**latency bound**, the second the **throughput bound**; out-of-order
execution hides everything else, so measured loops sit close to the larger
of the two (short loops can do better: the window overlaps the start of the
next chain with the end of the current one [S8]).

The slides' Rocket Lake measurements [S3 p.16 to 18]:

| loop | chain | c/iteration |
|---|---|---|
| `r += a[i]; i++` (64-bit integers, `add (%rdi),%rax`) | `add` on `r`: 1 c; `add` on the pointer: 1 c; the load (5 c in the slide's diagram) is *not* on a chain | 1.52: above the 1 c latency bound; the slide does not say what the other half cycle is |
| `r += a->val; a = a->next` | `mov (%rdi),%rdi` feeds the next load: the diagram labels it 4 c | 5 (measured; ex3's L1-hit chase also gives 5 c [S7]) |
| `r += a[i]` (doubles) | FP add latency 4 c [S3 p.14] | 3.73 |
| `a[i] = a[i] + f` (doubles) | none: iterations independent | 1.27; 0.16 vectorised with `gcc -O3 -march=rocketlake -mtune=znver5` |
| `r += a[i]` with `gcc -O3 -ffast-math -march=rocketlake -mtune=znver5` | compiler reassociates into several accumulators and vectorises | 0.3 |

Same instruction count (4), factor 3.3 between the first two: the pointer
chase puts the load on the chain. Same shape for the FP sum: `-ffast-math`
permits reassociation, the compiler splits the chain into $k$ partial sums
and the bound drops to $L/k$ until the throughput bound of the adders takes
over; without the flag the compiler must keep the order (FP addition is not
associative [S3 p.47]) and the programmer does the split by hand:

$$\frac{\text{cycles}}{\text{element}} \approx \max\Bigl(\frac{L_{\text{add}}}{k},\; \frac{1}{T_{\text{add}}}\Bigr).$$

**Measured here** (`src/c/recurrence.c --bench`, 4 096 doubles in L1, M3
Pro [S19]; ranges over four `make bench` runs on 2026-09-28, which differ
by up to 10 % because the clock is not fixed; "~c" = ns × 4.05 GHz, an
**assumed** clock, so the cycle column is an estimate):

| kernel | ns/elem | ~c/elem | reading |
|---|---|---|---|
| `sum1` one chain | 0.68 to 0.75 | 2.7 to 3.05 | $L_{\text{add}} \approx 3$ c on this core |
| `sum2` | 0.32 to 0.36 | 1.3 to 1.45 | $L/2$ |
| `sum4` | 0.173 to 0.188 | 0.70 to 0.76 | $L/4$ |
| `sum8` | 0.094 to 0.099 | 0.38 to 0.40 | $L/8 = 0.34$ to $0.38$ predicted; still at the latency bound |
| `isum1` int64 | 0.068 to 0.072 | 0.28 to 0.29 | associative: clang vectorised it (`-Rpass=loop-vectorize`: width 2, interleave 4), several lanes in flight |
| `isum4` int64, 4 chains in the source | 0.135 to 0.142 | 0.55 to 0.58 | clang vectorised this one too, but only with interleave 2 (`-Rpass`: width 2, interleave 2); half the speed of the one-chain source, not investigated further |
| `list` dependent loads | 1.01 to 1.14 | 4.1 to 4.6 | load-to-use latency ≈ 4 c at the assumed clock (the list is 64 KB, in the 128 KB L1d) |
| `axpy` independent | 0.087 to 0.102 | 0.35 to 0.41 | throughput bound: loads, adds, stores of 2-wide vectors |

Clang's remark says `sum1` was "vectorized (width 2, interleaved 4)", yet it
runs at $L_{\text{add}}$: the loads were vectorised, the additions kept their
order. Read the remark and the time, not one of them.

## Latency-dominated vs throughput-dominated programs [S3 p.19]

| latency dominated | throughput dominated |
|---|---|
| dependent operations on the same data; data mostly in cache | the same operation on lots of data: images, audio, matrices, tensors, neural nets |
| most code (by lines) | little code, much run time |
| helped by out-of-order execution, branch prediction, caches | often needs DRAM bandwidth; helped by SIMD, multi-core, GPUs |
| sometimes independent instances (compilers, servers): multi-core helps | |

Exercise 2 [S6] is built on this split: its stated purpose is hands-on
experience of how latency and instruction bandwidth influence performance.

## Branch prediction [S3 p.14] [S3 p.49 to 51]

A predicted branch is free (0 to 1 c); a mispredicted one costs the pipeline
refill, ~20 c. Predictable: loop exits, monotone conditions, anything with a
pattern the predictor's history can learn. Unpredictable: data-dependent
50/50 decisions. Cost model for a branch taken with probability $p$ that the
predictor cannot learn: mispredictions per execution $\approx \min(p, 1-p)$.

**Measured** (`src/c/branch_predict.c --bench`, filter of $2^{24}$ values
< 128 vs ≥ 128, M3 Pro [S19]):

| variant | ns/element (four runs) |
|---|---|
| `if` on unsorted data (50 % taken, random) | 2.42 to 2.69 |
| `if` on sorted data (never, then always) | 0.263 to 0.280 |
| branchless `out[k]=v; k+=(v>=128)` unsorted | 0.267 to 0.280 |
| branchless, sorted | 0.266 to 0.283 |

$(2.42 - 0.26)\,\text{ns} / 0.5 \approx 4.3$ ns per misprediction (4.3 to
4.8 ns over the runs) $\approx 17$ to 19.5 cycles at the assumed 4.05 GHz;
the slide says 20 c [S3 p.14], Agner Fog measures 16 to 20 c on Ice Lake
[S13]. The branchless form costs the same on both inputs and the same as the
perfectly predicted branch within run-to-run noise: slide 51's rule, use arithmetic (`A & B`, `x += cond`) when the condition is hard to
predict and cheap to compute, a branch when it is predictable [S3 p.49 to 51].

One subtlety that note 08 needs: a **predicted branch breaks a data
recurrence, a select does not**. `if (d < best) best = d` compiled as a
compare-and-select makes `best` a chain (compare → select → compare; 4.2 to
4.6 c per candidate at the assumed clock in `tsp_greedy` v3, note 08);
compiled as a rarely taken branch, the next
iteration proceeds speculatively without waiting for `best`, and the loop
runs at the throughput bound. The compiler chooses; you find out from the
assembly.

## Parallelism the hardware and the system exploit [S3 p.26 to 27]

Problems: finding it, expressing it, synchronisation overhead. Levels:
between cores (threads); between CPU and mass storage (prefetching, write
buffering); between graphics card and screen (triple buffering: double
buffering without vsync tears, with vsync waits, a third buffer removes
both); between CPU and DRAM (hardware prefetching, note 04); between
instructions (scheduling, out-of-order); within an instruction (SIMD, note
06).

## Worked example: predict a loop's cycles per iteration

```c
for (i = 0; i < n; i++) s += a[i] * b[i];      /* doubles */
```

Per iteration: 2 loads, 1 multiply, 1 add (or 1 FMA), 1 counter add, 1
compare-branch. Recurrences: `s` through the add, $L = 4$ c [S3 p.14];
`i` through the counter add, 1 c. Throughput: 2 loads per cycle on an Ice
Lake-class core [S13], so 1 c for the two loads. Bound: $\max(4, 1) = 4$ c
per iteration, so $2 \times 10^9$ elements take $8 \times 10^9$ cycles
$\approx 2.7$ s at 3 GHz. With 4 accumulators: $\max(4/4, 1) = 1$ c, 0.7 s,
and now vectorising (4 doubles per AVX2 operation, 2 loads of 32 B per cycle)
is what pays next.
The matmul page shows the first half of this argument live with `perf
annotate` on `mm1` (`addsd` at 4 c/iteration) [S8].

## Pitfalls

- Counting instructions instead of finding the chain: the slide's two loops
  have the same instruction count and differ by 3× [S3 p.16].
- Assuming the compiler will split an FP reduction: it may not without
  `-ffast-math`; it *will* split an integer one.
- Reading "vectorized" in a compiler remark as "fast".
- Converting cycles with a guessed clock (as the "~c" columns here do,
  stated as an estimate); on g0 read `cycles:u`.
- Making a branch branchless when it was predictable: no gain, sometimes a
  loss, and possibly a new recurrence.
- Micro-benchmarking a chain in a short loop: the out-of-order window
  overlaps consecutive calls and understates $L$.

## Exam-style questions

1. **Define recurrence and state the bound it imposes.** A value carried from one iteration to the next through a chain of dependent operations of total latency $L$ over $d$ iterations; cycles per iteration $\ge L/d$, independent of how many execution units exist [S3 p.16 to 17] [S8].
2. **`r += a[i]` over ints takes 1.5 c/iteration, `r += p->val; p = p->next` 5 c. Same instruction count. Explain and say how you would confirm it with `perf`.** In the list the load's address depends on the previous load: the load latency is on the recurrence (4 c in the slide's diagram, 5 c/iteration measured). In the array the address comes from the counter (1 c add) and the loads overlap. Confirm: `perf stat -e cycles:u -e instructions:u` shows equal instructions, cycles differing by 3×; `L1-dcache-load-misses:u` ≈ 0 in both, so it is latency, not misses [S3 p.16 to 17].
3. **How would you halve the time of a double-precision sum loop without changing the flags, and what limits the trick?** Two (or $k$) accumulators, summed at the end: the chain latency is divided by $k$ until the adder throughput or the load ports bound the loop, at $k \approx L \cdot T$ ($T$ adds per cycle); our `sum8` still runs at $L/8$, so on the M3 $T \ge 8/L \approx 2.7$. Results change in the last bits because FP addition is not associative; decide whether that is acceptable [S3 p.18, 47].
4. **A branch inside a hot loop is taken 50 % of the time at random. Estimate its cost per iteration and name two remedies with their trade-offs.** ~0.5 mispredictions × 20 c = 10 c per iteration. Remedies: make it arithmetic (`x += cond`, `A & B`): constant cost, but may create a recurrence through the select; change the data or the algorithm so the test disappears (sort the input; drop `visited[]` by compaction as in tsp4) [S3 p.49 to 51] [S3 p.79].

Code: `src/c/recurrence.c`, `src/c/branch_predict.c`. Sources: [S3 p.14 to 19, 26, 27, 47, 49 to 51] [S4] [S6] [S7] [S8] [S13] [S19] [S21].
