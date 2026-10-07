"""Roofline model [S11] with real FP64 numbers. Note 03.

P(I) = min(P_peak, I * B), ridge point I* = P_peak / B.

Machines:
  - Xeon Platinum 8180 and Tesla V100 from Rupp's CC BY 4.0 data set [S5],
    vendored under refs/vendor/rupp-cpu-gpu-mic-comparison/ and parsed here;
  - H100 SXM [S29] and MI300X [S30] from the vendors' data sheets;
  - this Mac (M3 Pro): bandwidth 150 GB/s spec [S31] and the measured triad
    (src/cpp/stream_triad), compute roof = measured tiled matmul (a lower bound,
    Apple publishes no FP64 peak) [S32].

Usage: python roofline.py [--png out.png] [--bw GBs] [--peak GFLOPs]
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[2] / "refs" / "vendor" / "rupp-cpu-gpu-mic-comparison"


@dataclass(frozen=True)
class Machine:
    name: str
    peak_gflops: float  # FP64
    bw_gbs: float
    source: str

    @property
    def ridge(self) -> float:
        return self.peak_gflops / self.bw_gbs

    def attainable(self, ai: float) -> float:
        return min(self.peak_gflops, ai * self.bw_gbs)

    def bound(self, ai: float) -> str:
        return "memory" if ai < self.ridge else "compute"


def load_rupp(fname: str, dp_col: int, bw_col: int) -> list[tuple[int, str, float, float]]:
    """Parse one of Rupp's whitespace tables: (year, name, GFLOP/s DP, GB/s)."""
    rows = []
    for line in (VENDOR / fname).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name = line.split('"')[1]
        f = line.split('"')[0].split()
        rows.append((int(f[0]), name, float(f[dp_col]), float(f[bw_col])))
    return rows


def rupp_machine(fname: str, dp_col: int, bw_col: int, name: str) -> Machine:
    for _, n, dp, bw in load_rupp(fname, dp_col, bw_col):
        if n == name:
            return Machine(name, dp, bw, "[S5]")
    raise KeyError(name)


def machines(mac_bw: float = 121.0, mac_peak: float = 161.0) -> list[Machine]:
    return [
        rupp_machine("data-intel.txt", 2, 4, "Xeon Platinum 8180"),  # Year SP DP Cores BW ...
        rupp_machine("data-dp-nvidia.txt", 1, 3, "Tesla V100"),      # Year GFLOPs Pixel BW ...
        Machine("H100 SXM (vector)", 34_000, 3_350, "[S29]"),
        Machine("MI300X (vector)", 81_700, 5_300, "[S30]"),
        Machine("M3 Pro CPU (measured)", mac_peak, mac_bw, "[S32]"),
    ]


# FP64 kernels: flops and compulsory DRAM bytes per unit of work
KERNELS = {
    "triad a=b+s*c": 2 / 24,
    "SpMV CSR (12 B/nnz)": 2 / 12,
    "Jacobi 5-pt (16 B/LUP)": 4 / 16,
    "tiled matmul T=32": 32 / 8,
    "DGEMM n=4096 (3 n^2 moved)": 2 * 4096**3 / (3 * 8 * 4096**2),
}


def table(ms: list[Machine]) -> str:
    out = [f"{'machine':24s} {'GFLOP/s':>9s} {'GB/s':>7s} {'ridge':>7s} {'src':>6s}"]
    for m in ms:
        out.append(f"{m.name:24s} {m.peak_gflops:9.0f} {m.bw_gbs:7.0f} {m.ridge:7.2f} {m.source:>6s}")
    out.append("")
    out.append(f"{'kernel':28s} {'AI':>7s} " + " ".join(f"{m.name.split()[0]:>9s}" for m in ms))
    for k, ai in KERNELS.items():
        out.append(f"{k:28s} {ai:7.3f} " + " ".join(f"{m.attainable(ai):9.1f}" for m in ms))
    out.append("(attainable GFLOP/s = min(peak, AI x B))")
    return "\n".join(out)


def plot(ms: list[Machine], path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]  # fixed categorical order
    fig, ax = plt.subplots(figsize=(7.5, 4.8), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ai = np.logspace(-2, 3, 400)
    for m, c in zip(ms, colors):
        ax.loglog(ai, np.minimum(m.peak_gflops, ai * m.bw_gbs), color=c, lw=2, label=m.name)
        ax.plot([m.ridge], [m.peak_gflops], "o", ms=8, color=c, mec="#fcfcfb", mew=2)
        ax.annotate(f"{m.ridge:.1f}", (m.ridge, m.peak_gflops), textcoords="offset points",
                    xytext=(6, -12), fontsize=8, color="#52514e")
    for k, x in KERNELS.items():
        ax.axvline(x, color="#b8b7b0", lw=0.8, ls=":")
        ax.text(x, 0.9, k.split(" (")[0], rotation=90, fontsize=7, color="#52514e", va="bottom", ha="right")
    ax.set_xlabel("arithmetic intensity [flop / DRAM byte]", color="#0b0b0b")
    ax.set_ylabel("attainable FP64 [GFLOP/s]", color="#0b0b0b")
    ax.grid(True, which="major", color="#e4e3dd", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper left", title="M3 Pro and Xeon 8180 share the bandwidth slope (121 vs 120 GB/s)", title_fontsize=7)
    ax.set_title("Roofline, FP64; dots = ridge points (labels: flop/B)", fontsize=10, color="#0b0b0b")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--png", help="write the roofline plot to this file")
    ap.add_argument("--bw", type=float, default=121.0, help="measured triad GB/s of this machine")
    ap.add_argument("--peak", type=float, default=161.0, help="measured GFLOP/s of this machine")
    a = ap.parse_args()
    ms = machines(a.bw, a.peak)
    print(table(ms))
    if a.png:
        plot(ms, a.png)
        print("wrote", a.png)


if __name__ == "__main__":
    main()
