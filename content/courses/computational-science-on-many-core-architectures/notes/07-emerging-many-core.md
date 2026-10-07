# 07 Emerging many-core architectures

TISS topic 7 [S2]. "Emerging" is a moving target: in the lecturer's 2015
tutorial it was the Xeon Phi [S4 `mics.tex`]; in 2026 it is unified-memory
SoCs, matrix engines, very large GPU packages and dataflow chips. The constant
is the argument of notes 02-03: FLOPs are cheap, bytes are not [S6], and
energy now caps both. Code: `src/py/perf_models.py` (`pj_per_flop`).

## Why many-core at all

Rupp's trend data [S39]: the highest clock in the data set reached 3.65 GHz by
2004 and is 3.2 GHz in the 2020-2021 entries; the largest core count went from
1 (2000) to 128 (2020) and 208 (2021). Frequency stopped scaling (power density),
transistor counts did not, so performance growth became parallelism: more cores
and wider SIMD per core [S7]. Everything below is a variation on "spend the
transistors on more, simpler, lock-step lanes, and feed them".

## The 2015 case study: Xeon Phi [S4 `mics.tex`]

- Knights Corner (2012): ~1 TFLOP/s FP64, 320 GB/s ideal and 160 GB/s real, 8-16 GB, custom OS, very low single-thread performance, PCIe slower than for GPUs; "'Just recompile' almost never enough".
- Knights Landing (2016): 72 cores, 3+ TFLOP/s FP64, 16 GB on-package memory at 5x DDR4 bandwidth, binary compatible with Xeon.
- Lesson the slides draw: a programming model that looks familiar (x86 + OpenMP) does not remove the need to restructure for bandwidth, SIMD and many threads. *(unsourced: the Xeon Phi line was later discontinued.)*

## Unified-memory SoCs (Apple silicon, this Mac)

M3 Pro [S31]: 12-core CPU (6P + 6E), 18-core GPU, 16-core Neural Engine, one
**150 GB/s** memory system shared by all of them.

- No PCIe between CPU and GPU: the $\alpha$ = 10 us, $\beta$ = 16 GB/s transfer row of note 03 disappears; "offload" is a pointer hand-over. The offload Amdahl formula of note 01 loses its $\tau$ term.
- The bandwidth is shared, not added: CPU triad already draws 121 GB/s (81 %, note 02), so a memory-bound kernel gains little from moving to the on-chip GPU.
- **No FP64 on the GPU** through Metal: "Metal does not support the double ... data types" [S36]. For FP64 science this GPU is irrelevant; for FP32/FP16 it is a many-core device of the same SIMT kind as note 04. *(unsourced: FP32 peak of the 18-core GPU.)*
- Balance: $I^* \approx 161/121 = 1.3$ flop/B for the CPU (measured, note 02) vs 10-31 on data-centre GPUs. A laptop is far less starved for bandwidth per flop.

## Data-centre GPUs: bigger packages, matrix engines

| | H100 SXM [S29] | MI300X [S30] |
|---|---|---|
| compute units | (unsourced SM count) | 304 CUs, 64-wide wavefronts [S26] |
| FP64 vector / matrix | 34 / 67 TFLOP/s | 81.7 / 163.4 TFLOP/s |
| FP16 matrix | 1 979 TFLOP/s *with sparsity* | - |
| memory | 80 GB, 3.35 TB/s | 192 GB HBM3, 5.3 TB/s, 256 MB Infinity Cache |
| power | up to 700 W | 750 W TBP |
| ridge, FP64 vector / matrix | 10.1 / 20.0 flop/B | 15.4 / 30.8 flop/B |

**Tensor (matrix) cores** execute small matrix-multiply-accumulate tiles per
instruction. Only GEMM-shaped work benefits: the FP64 matrix rate is 2x the
vector rate on both parts, the FP16 rate on H100 ~58x (a *with sparsity* figure [S29]). Consequences:
- the ridge moves right (20-31 flop/B for FP64 matrix); SpMV, stencils and CG gain nothing;
- low precision is where the FLOPs are, so mixed-precision algorithms (factorise in low precision, refine in FP64) become attractive *(unsourced: e.g. the HPL-MxP benchmark)*;
- "with sparsity" peaks assume a structured-sparsity pattern [S29]; compare dense to dense.

## Dataflow and wafer-scale chips

Cerebras WSE-3 [S35]: one wafer-sized chip, 46 225 mm$^2$, 4 trillion
transistors, 900 000 cores, "250 petaflops" (AI precision). The design point:
memory is SRAM distributed next to the cores, and the program is laid out
spatially with data flowing core to core, closer to an FPGA's dataflow (note
06) than to a GPU's shared DRAM *(unsourced details of the memory system)*. For
a stencil or SpMV the question is again note 03's: where do the bytes come
from, and at what $\alpha$ and $\beta$.

## Energy per flop

At TDP and peak (upper bounds; real codes run below peak and below TDP)
[S5] [S29] [S30], `perf_models.py`:

| machine | FP64 pJ/flop |
|---|---|
| Xeon Platinum 8180 (2017) | 91.5 |
| Tesla V100 (2017) | 38.5 |
| H100 SXM, vector / tensor | 20.6 / 10.4 |
| MI300X, vector / matrix | 9.2 / 4.6 |

$P = E_\text{flop}\cdot\text{FLOP/s}$: at H100 vector efficiency, 20.6 pJ/flop, an
exaflop/s FP64 machine built from such GPUs draws ~21 MW at peak, before hosts
and network. Matrix engines halve the energy
per flop, which is why they spread.

**Moving data costs more than computing on it.** Horowitz's ISSCC 2014 talk
[S34] is the standard reference for this *(paywalled; not read for this note,
cited for the claim only)*. Worked from data sheets instead: a triad of $10^9$
doubles on an H100 is bandwidth-bound, $24\,\text{GB}/3.35\,\text{TB/s} = 7.2$
ms; at 700 W that is up to 5 J, while its $2\cdot10^9$ flops at 20.6 pJ would
need 0.04 J. Energy follows runtime, runtime follows bytes.

## Pitfalls

- Treating "unified memory" as "infinite bandwidth": the CPU and GPU share one memory system.
- Quoting tensor-core or sparsity peaks for general FP64 codes.
- Comparing energy per flop at TDP across machines as if all ran at peak.
- Believing a familiar programming model makes a new architecture easy (Xeon Phi [S4]).

## Oral-exam questions

1. **Why did processors become many-core?** Clock frequency stalled around 3-4 GHz after 2004 [S39] (power density), transistor counts kept growing; the extra transistors went into more cores and wider vector units [S7].
2. **What changes for performance modelling on a unified-memory SoC?** No host-device transfer term ($\alpha$, $\beta$ of PCIe vanish), but CPU and GPU share one bandwidth roof (150 GB/s here [S31]).
3. **What are tensor cores good for, and why do they not help a CG solver?** Small dense matrix-multiply-accumulate tiles; CG is SpMV + vector ops at $I < 1$, bandwidth-bound; a higher compute roof is irrelevant left of the ridge.
4. **Estimate the energy per FP64 flop of an H100 and what that means for an exascale machine.** $700/34\cdot10^{12} \approx 21$ pJ; $10^{18}$ flop/s x 21 pJ = 21 MW at peak, before memory and network.
5. **The 2015 "emerging" architecture was the Xeon Phi. What did it teach?** Recompiling OpenMP code was "almost never enough" [S4]: many slow cores need restructuring for SIMD, bandwidth (on-package memory) and thread count, as GPUs do.

Code: `src/py/perf_models.py` (`pj_per_flop`), `src/py/roofline.py` (`machines`). Sources: [S4]-[S7] [S26] [S29]-[S31] [S34]-[S36] [S39].
