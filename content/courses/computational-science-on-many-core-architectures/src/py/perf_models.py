"""Closed-form performance models for notes 01, 03, 04, 06 and 07.

Amdahl [S9], Gustafson [S10] and Shi's conversion between them [S37];
Karp-Flatt; Little's law [S12]; the latency-bandwidth (alpha-beta) model and
Hockney's half-performance length [S14]; a CUDA occupancy calculator using
the compute-capability limits of the CUDA C++ Programming Guide 13.4, Table 27
[S15]; hardware-pipeline cycle counts for FPGAs [S27]; energy per flop from
data-sheet TDP and peak [S29] [S30] [S5].

Run `python perf_models.py` for the worked examples used in the notes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# --- scaling laws -----------------------------------------------------------

def amdahl(f: float, p: float) -> float:
    """Fixed-size speedup; f = serial fraction of the 1-processor time."""
    return 1.0 / (f + (1.0 - f) / p)


def gustafson(s: float, p: float) -> float:
    """Scaled speedup; s = serial fraction of the p-processor time."""
    return s + (1.0 - s) * p


def amdahl_f_from_gustafson_s(s: float, p: float) -> float:
    """Shi [S37]: the same run seen from the 1-processor side."""
    return s / (s + (1.0 - s) * p)


def karp_flatt(speedup: float, p: float) -> float:
    """Experimentally determined serial fraction e(p)."""
    return (1.0 / speedup - 1.0 / p) / (1.0 - 1.0 / p)


def offload_speedup(f_accel: float, kernel_speedup: float, transfer_fraction: float = 0.0) -> float:
    """Amdahl for GPU offload: a fraction f_accel of the CPU runtime runs
    kernel_speedup times faster; transfers add transfer_fraction of the
    original runtime."""
    return 1.0 / ((1.0 - f_accel) + f_accel / kernel_speedup + transfer_fraction)


# --- latency, bandwidth, concurrency -----------------------------------------

def little_bytes_in_flight(latency_s: float, bandwidth_Bps: float) -> float:
    """Little's law L = lambda W: bytes that must be outstanding to sustain
    bandwidth_Bps when each request takes latency_s."""
    return latency_s * bandwidth_Bps


def alpha_beta_time(nbytes: float, alpha_s: float, beta_Bps: float) -> float:
    """T(n) = alpha + n / beta."""
    return alpha_s + nbytes / beta_Bps


def n_half(alpha_s: float, beta_Bps: float) -> float:
    """Hockney's n_1/2: message/array size reaching half the asymptotic rate."""
    return alpha_s * beta_Bps


def effective_bandwidth(nbytes: float, alpha_s: float, beta_Bps: float) -> float:
    return nbytes / alpha_beta_time(nbytes, alpha_s, beta_Bps)


# --- CUDA occupancy -----------------------------------------------------------

@dataclass(frozen=True)
class SMLimits:
    """Per-SM limits of one compute capability, from [S15] Table 27."""
    name: str
    max_warps: int
    max_blocks: int
    regs: int  # 32-bit registers per SM
    smem_bytes: int  # max shared memory per SM
    warp: int = 32


CC_90 = SMLimits("cc 9.0 (Hopper)", max_warps=64, max_blocks=32, regs=64 * 1024, smem_bytes=228 * 1024)
CC_80 = SMLimits("cc 8.0 (A100)", max_warps=64, max_blocks=32, regs=64 * 1024, smem_bytes=164 * 1024)
CC_86 = SMLimits("cc 8.6", max_warps=48, max_blocks=16, regs=64 * 1024, smem_bytes=100 * 1024)


def occupancy(lim: SMLimits, threads_per_block: int, regs_per_thread: int, smem_per_block: int = 0):
    """Resident blocks per SM and occupancy = resident warps / max warps.

    Simplified: ignores register-allocation granularity and the per-block
    shared-memory reservation, which the CUDA Occupancy Calculator applies
    [S15] ("Hardware Multithreading"). Returns (blocks, occupancy, limiter)."""
    warps_per_block = math.ceil(threads_per_block / lim.warp)
    limits = {
        "warps": lim.max_warps // warps_per_block,
        "blocks": lim.max_blocks,
        "registers": lim.regs // (regs_per_thread * warps_per_block * lim.warp),
        "shared memory": lim.smem_bytes // smem_per_block if smem_per_block else 10**9,
    }
    limiter = min(limits, key=limits.get)
    blocks = limits[limiter]
    return blocks, blocks * warps_per_block / lim.max_warps, limiter


# --- FPGA / hardware pipelines ------------------------------------------------

def pipeline_cycles(n_iter: int, depth: int, ii: int) -> int:
    """Cycles for n_iter loop iterations through a pipeline of `depth` stages
    started every `ii` cycles (initiation interval) [S27] section 2.9:
    depth + (n_iter - 1) * ii."""
    return 0 if n_iter == 0 else depth + (n_iter - 1) * ii


def accumulation_ii(adder_latency: int, partial_sums: int) -> int:
    """II of a floating-point accumulation s += a[i]*b[i]: the next add needs
    the previous result, so II = ceil(latency / independent partial sums)."""
    return max(1, math.ceil(adder_latency / partial_sums))


# --- energy -------------------------------------------------------------------

def pj_per_flop(watts: float, gflops: float) -> float:
    return watts / (gflops * 1e9) * 1e12


# --- worked examples ------------------------------------------------------------

def main() -> None:
    print("Amdahl, f = 0.05:", ", ".join(f"S({p}) = {amdahl(0.05, p):.2f}" for p in (12, 132, 1024)),
          "; limit 20")
    print("Gustafson, s = 0.05:", ", ".join(f"S({p}) = {gustafson(0.05, p):.1f}" for p in (12, 132, 1024)))
    print("Gustafson 1988 [S10], p = 1024, s = 0.004 / 0.008:",
          f"{gustafson(0.004, 1024):.1f} / {gustafson(0.008, 1024):.1f}")
    print("  equivalent Amdahl f for s = 0.004 at p = 1024:", f"{amdahl_f_from_gustafson_s(0.004, 1024):.2e}")
    print("GPU offload: 90 % of runtime 20x faster:", f"{offload_speedup(0.9, 20):.2f}",
          "; plus transfers worth 10 % of the old runtime:", f"{offload_speedup(0.9, 20, 0.1):.2f}")

    print("\nLittle's law (bytes in flight = latency x bandwidth):")
    for name, lat, bw in (("M3 Pro CPU, 100 ns x 120 GB/s", 100e-9, 120e9),
                          ("H100 SXM, 600 ns (assumed) x 3.35 TB/s", 600e-9, 3.35e12)):
        b = little_bytes_in_flight(lat, bw)
        print(f"  {name}: {b / 1e3:.1f} KB = {b / 128:.0f} lines of 128 B = {b / 8:.0f} doubles")

    print("\nalpha-beta (Rupp [S4]: launch/PCIe latency ~10 us, PCIe 3 16 GB/s):")
    for name, a, bw in (("PCIe 3 x16", 10e-6, 16e9), ("V100 kernel, 900 GB/s", 10e-6, 900e9),
                        ("H100 kernel, 3.35 TB/s", 10e-6, 3.35e12)):
        print(f"  {name}: n_1/2 = {n_half(a, bw) / 1e6:.2f} MB; 1 MB moves at "
              f"{effective_bandwidth(1e6, a, bw) / 1e9:.1f} GB/s")

    print("\noccupancy on", CC_90.name)
    for tpb, regs, smem in ((256, 32, 0), (256, 64, 0), (256, 32, 48 * 1024), (1024, 64, 0), (64, 32, 0)):
        b, occ, lim = occupancy(CC_90, tpb, regs, smem)
        print(f"  {tpb:5d} thr/block, {regs:3d} regs, {smem // 1024:3d} KB smem -> {b:2d} blocks, "
              f"occupancy {occ:.0%} (limited by {lim})")

    print("\nFPGA pipeline: 1e6 MACs, depth 10, at 300 MHz (assumed clock):")
    for ii in (1, 4):
        c = pipeline_cycles(10**6, 10, ii)
        print(f"  II = {ii}: {c} cycles = {c / 300e6 * 1e3:.2f} ms, {2e6 / (c / 300e6) / 1e9:.2f} GFLOP/s")
    print("  float adder latency 4, 1 / 4 partial sums -> II =", accumulation_ii(4, 1), "/", accumulation_ii(4, 4))

    print("\nenergy per FP64 flop at TDP:")
    for name, w, g in (("Xeon Platinum 8180 [S5]", 205, 2240), ("Tesla V100 [S5]", 300, 7800),
                       ("H100 SXM vector [S29]", 700, 34000), ("H100 SXM tensor [S29]", 700, 67000),
                       ("MI300X vector [S30]", 750, 81700), ("MI300X matrix [S30]", 750, 163400)):
        print(f"  {name:26s} {pj_per_flop(w, g):6.1f} pJ/flop")


if __name__ == "__main__":
    main()
