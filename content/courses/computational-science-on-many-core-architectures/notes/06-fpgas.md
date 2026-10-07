# 06 Field-programmable gate arrays

TISS topic 6 [S2]. The lecturer's 2015 tutorial has no FPGA slide [S4], so
this note rests on Kastner, Matai and Neuendorffer's CC BY 4.0 HLS textbook
[S27] (ch. 1 architecture and HLS, ch. 2 the FIR filter as the running example)
and AMD's Vitis HLS guide [S28]. There is no FPGA toolchain on this Mac; the
cycle model is in `src/py/perf_models.py` (`pipeline_cycles`,
`accumulation_ii`).

## What an FPGA is

A chip of configurable logic and wiring, programmed by a bitstream after
manufacture [S27 §1.2]:

- **LUT** (look-up table): an $n$-input LUT is a $2^n$-bit memory addressed by
  its inputs, so it implements *any* Boolean function of $n$ inputs by storing
  the truth table; most FPGAs use 4-6-input LUTs [S27 §1.2]. A 2-LUT has 4
  configuration bits and can be one of $2^{2^2} = 16$ functions.
- **FF** (flip-flop): one stored bit, clocked; with LUTs and multiplexers forms a **slice** [S27 §1.2].
- **DSP blocks** (e.g. DSP48): hardened multiply-accumulate datapaths, much cheaper than a multiplier built from LUTs [S27 §1.2].
- **BRAM**: hardened on-chip memories, typically ~32 Kbit each, configurable width and depth, "configurable register files" next to the DSPs [S27 §1.2].
- **Routing**: programmable interconnect between all of the above; it, not the logic, often limits the clock.

No instruction stream, no cache hierarchy: the *program is the circuit*.
Parallelism is spatial (copies of a datapath) and temporal (pipelining).

## Pipelining, latency, initiation interval

For a loop body scheduled into a pipeline of depth $D$ cycles that accepts a
new iteration every **II** (initiation interval) cycles [S27 §2.9]:
$$T(N) = \bigl(D + (N-1)\,\mathrm{II}\bigr)\,/\,f_\text{clk},\qquad \text{throughput} \to f_\text{clk}/\mathrm{II}\ \text{iterations/s}.$$
The FIR MAC loop of [S27 §2.9], with `#pragma HLS pipeline II=1`, starts one
iteration every cycle.

**Worked example** (`perf_models.py`): $10^6$ MACs, $D = 10$, at 300 MHz
*(unsourced clock; typical HLS designs run at a few hundred MHz)*:

| II | cycles | time | GFLOP/s (2 flop/MAC) |
|---|---|---|---|
| 1 | 1 000 009 | 3.33 ms | 0.60 |
| 4 | 4 000 006 | 13.3 ms | 0.15 |

One pipelined MAC is 0.6 GFLOP/s. To compete, replicate: $U$ parallel MACs
need $U$ operand pairs per cycle, i.e. arrays **partitioned** over $U$
memories, because a BRAM serves only a few accesses per cycle [S27 §1.2]
*(unsourced: dual-ported, 2)*. $U = 1000$ at 300 MHz gives 600 GFLOP/s, if the
device has 1000 multipliers of the needed precision and the memory can feed
them.

**The loop-carried dependency** is the FPGA version of the CPU dot-product
problem (NSSC I note 01 [S40]): `acc += a[i]*b[i]` reads the previous `acc`,
a read-after-write dependency across iterations [S27 §2.9]. With a
floating-point adder of latency $L$ cycles, $\mathrm{II} \ge L$. Fix: $L$
independent partial sums, $\mathrm{II} = \lceil L/\text{partials} \rceil$
(`accumulation_ii(4, 1) = 4`, `accumulation_ii(4, 4) = 1`). Same algebra as
eight accumulators on a CPU core or a tree in a GPU block (note 04).

## High-level synthesis (HLS)

C/C++ in, register-transfer-level hardware out; directives steer the
architecture [S27 §1.1, §1.4] [S28]:

```cpp
void dot(const float a[N], const float b[N], float* out) {
#pragma HLS array_partition variable=a type=cyclic factor=8
#pragma HLS array_partition variable=b type=cyclic factor=8
    float part[8] = {0};                       // 8 partial sums: breaks the RAW chain
    for (int i = 0; i < N; i += 8) {
#pragma HLS pipeline II=1
        for (int u = 0; u < 8; ++u) {
#pragma HLS unroll
            part[u] += a[i + u] * b[i + u];    // 8 MACs per cycle, 16 reads from 16 banks
        }
    }
    float s = 0;
    for (int u = 0; u < 8; ++u) s += part[u];
    *out = s;
}
```

- `pipeline II=1`: overlap iterations; the tool reports the II it achieved, which may be larger because of resource limits or dependencies [S27 §2.9].
- `unroll`: replicate the body (spatial parallelism) [S27 §2.8].
- `array_partition type=cyclic factor=8` (Vitis spelling [S28]; [S27] uses Vivado HLS): element $i$ goes to bank $i \bmod 8$, so 8 consecutive elements are readable in one cycle (the FPGA's answer to bank conflicts, note 04) [S27 §4.5].
- Bitwidth optimisation: arbitrary-precision types (`ap_int<12>`, `ap_fixed`) make every operator exactly as wide as needed [S27 §2.10]; this is where FPGAs gain most over fixed 32/64-bit ALUs.
- Flow after HLS: synthesis, place and route, bitstream [S27 §1.3]; *(unsourced: hours for a large design, against seconds for `nvcc`)*.

## When FPGAs win, and when they lose

| win | lose |
|---|---|
| streaming with a fixed dataflow (filters, FFT, compression, packet processing) [S27 ch. 2-5] | FP64 dense linear algebra: a GPU has 34-82 TFLOP/s FP64 [S29] [S30] |
| deterministic low latency, no OS or cache in the path | irregular memory access, pointer chasing |
| custom and narrow precision (bit-level, fixed point) | code that changes often (compile time, verification) |
| I/O attached directly to the fabric (network, sensors) | small teams without hardware-design experience |
| energy per operation for fixed-point work *(unsourced magnitude)* | anything that fits a library call on a GPU |

The roofline still applies (note 03): an FPGA card with DDR or HBM has a
bandwidth roof like any accelerator, and a streaming kernel is bound by it. The
gain is in doing *more per byte on chip* (deep pipelines, dataflow between
stages without DRAM round trips), and in latency.

## Pitfalls

- Reading "II=1" in the source as "II=1 achieved": check the synthesis report [S27 §2.9].
- Floating-point accumulation in a pipelined loop without partial sums (II = adder latency).
- Unrolling without partitioning: the memory ports, not the multipliers, set the throughput.
- Comparing an FPGA's fixed-point throughput with a GPU's FP64 peak.

## Oral-exam questions

1. **What is a LUT, and how many functions can a 4-input LUT implement?** A $2^4 = 16$-bit memory addressed by the inputs, holding the truth table; $2^{16} = 65\,536$ functions [S27 §1.2].
2. **Define initiation interval and loop latency. What is the time for $N$ iterations?** II: cycles between the starts of successive iterations; latency $D$: cycles for one iteration; $T = D + (N-1)\mathrm{II}$ cycles.
3. **Why does `acc += a[i]*b[i]` not reach II=1 in floating point, and how do you fix it?** RAW dependency through `acc`; the adder's latency $L$ forces $\mathrm{II} \ge L$; use $L$ partial sums, reduce at the end.
4. **What do UNROLL and ARRAY_PARTITION do, and why do you need both?** Unroll replicates the datapath; partition splits an array over several memories so the replicated datapath gets its operands in the same cycle.
5. **Name two workloads where an FPGA beats a GPU and one where it does not.** Wins: low-latency streaming, custom-precision signal processing; loses: FP64 dense linear algebra.

Code: `src/py/perf_models.py` (`pipeline_cycles`, `accumulation_ii`), tests `test_perf_models.py::test_pipeline_model`. Sources: [S4] [S27] [S28] [S29] [S30] [S40].
