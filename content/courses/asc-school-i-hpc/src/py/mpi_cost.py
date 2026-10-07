"""Cost models for MPI communication (notes/08, 09, 16).

Two models, both from primary sources, both here so that the tables in the notes
are *computed* rather than remembered:

1. The point-to-point model  t(n) = alpha + n*beta  and the derived quantity
   n_half = alpha / beta = alpha * B, the message size at which latency and
   transfer cost are equal.  Used with the published ping-pong latencies of the
   ASC/VSC course (notes/08).

2. The collective cost model of Thakur, Rabenseifner and Gropp, "Optimization of
   Collective Communication Operations in MPICH", Int. J. High Perf. Comput.
   Appl. 19(1), 49-66, 2005 (doi:10.1177/1094342005051521).  Notation, from the
   paper's section 3:

       alpha   per-message latency          [s]
       beta    transfer time per byte       [s/byte]   (beta = 1/bandwidth)
       gamma   local reduction cost/byte    [s/byte]
       n       bytes contributed by ONE process
       p       number of processes

   A single message of n bytes costs alpha + n*beta.

   This module exists because the collective table in notes/09 was wrong before
   it was written: it gave 2*lg(p)*alpha for a short-message Allreduce, which is
   the cost of the naive Reduce-then-Bcast, not of recursive doubling.

3. Amdahl's law in the convention the ASC lecturer uses: f is the SEQUENTIAL
   fraction (notes/16).

Run it:  python3 mpi_cost.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "Network",
    "n_half",
    "pt2pt_time",
    "bcast_short",
    "bcast_long",
    "reduce_short",
    "reduce_long",
    "allreduce_recursive_doubling",
    "allreduce_rabenseifner",
    "allgather_recursive_doubling",
    "allgather_ring",
    "alltoall_bruck",
    "alltoall_pairwise",
    "barrier",
    "naive_send_loop",
    "crossover",
    "amdahl",
    "amdahl_limit",
]


@dataclass(frozen=True)
class Network:
    """Machine parameters of the cost model.

    alpha in seconds, beta and gamma in seconds per byte.
    """

    alpha: float
    beta: float
    gamma: float = 0.0

    @classmethod
    def from_latency_bandwidth(cls, latency_us: float, bandwidth_GBs: float,
                               reduce_GBs: float = 0.0) -> "Network":
        """Build from the units people quote: microseconds and GB/s."""
        beta = 1.0 / (bandwidth_GBs * 1e9)
        gamma = 1.0 / (reduce_GBs * 1e9) if reduce_GBs > 0 else 0.0
        return cls(alpha=latency_us * 1e-6, beta=beta, gamma=gamma)


# --------------------------------------------------------------------------
# point to point
# --------------------------------------------------------------------------

def pt2pt_time(net: Network, n_bytes: float) -> float:
    """One-way time for a message of n_bytes: t = alpha + n*beta."""
    return net.alpha + n_bytes * net.beta


def n_half(net: Network) -> float:
    """Message size where latency and transfer cost are equal, in bytes.

    alpha = n*beta  =>  n = alpha/beta = alpha * bandwidth.
    Below n_half a message is latency bound, above it bandwidth bound.
    """
    return net.alpha / net.beta


# --------------------------------------------------------------------------
# collectives - Thakur, Rabenseifner & Gropp (2005), sections 4 and 5
# --------------------------------------------------------------------------

def _lg(p: int) -> float:
    return math.log2(p)


def _ceil_lg(p: int) -> int:
    return math.ceil(math.log2(p))


def bcast_short(net: Network, n: float, p: int) -> float:
    """Binomial tree: ceil(lg p) * (alpha + n*beta)."""
    return _ceil_lg(p) * (net.alpha + n * net.beta)


def bcast_long(net: Network, n: float, p: int) -> float:
    """Van de Geijn, scatter + ring allgather:
    (lg p + p - 1)*alpha + 2*(p-1)/p * n*beta."""
    return (_lg(p) + p - 1) * net.alpha + 2.0 * (p - 1) / p * n * net.beta


def reduce_short(net: Network, n: float, p: int) -> float:
    """Binomial tree: ceil(lg p) * (alpha + n*beta + n*gamma)."""
    return _ceil_lg(p) * (net.alpha + n * net.beta + n * net.gamma)


def reduce_long(net: Network, n: float, p: int) -> float:
    """Rabenseifner, reduce-scatter + gather:
    2*lg p*alpha + 2*(p-1)/p*n*beta + (p-1)/p*n*gamma."""
    f = (p - 1) / p
    return 2.0 * _lg(p) * net.alpha + 2.0 * f * n * net.beta + f * n * net.gamma


def allreduce_recursive_doubling(net: Network, n: float, p: int) -> float:
    """lg p*alpha + n*lg p*beta + n*lg p*gamma.

    NOTE the latency term: ONE lg p, not two.  Two is the cost of implementing
    allreduce as reduce-then-broadcast, which is what MPICH did before 2005 and
    what the earlier version of the table in notes/09 wrongly stated.
    """
    lg = _lg(p)
    return lg * net.alpha + n * lg * net.beta + n * lg * net.gamma


def allreduce_rabenseifner(net: Network, n: float, p: int) -> float:
    """Reduce-scatter + allgather:
    2*lg p*alpha + 2*(p-1)/p*n*beta + (p-1)/p*n*gamma."""
    f = (p - 1) / p
    return 2.0 * _lg(p) * net.alpha + 2.0 * f * n * net.beta + f * n * net.gamma


def allgather_recursive_doubling(net: Network, n_total: float, p: int) -> float:
    """ceil(lg p)*alpha + (p-1)/p * n_total*beta (n_total = the gathered size)."""
    return _ceil_lg(p) * net.alpha + (p - 1) / p * n_total * net.beta


def allgather_ring(net: Network, n_total: float, p: int) -> float:
    """(p-1)*alpha + (p-1)/p * n_total*beta."""
    return (p - 1) * net.alpha + (p - 1) / p * n_total * net.beta


def alltoall_bruck(net: Network, n_total: float, p: int) -> float:
    """lg p*alpha + n_total/2 * lg p * beta."""
    lg = _lg(p)
    return lg * net.alpha + n_total / 2.0 * lg * net.beta


def alltoall_pairwise(net: Network, n: float, p: int) -> float:
    """(p-1)*(alpha + n*beta), n = bytes sent to each peer."""
    return (p - 1) * (net.alpha + n * net.beta)


def barrier(net: Network, p: int) -> float:
    """Dissemination barrier: ceil(lg p) * alpha."""
    return _ceil_lg(p) * net.alpha


def naive_send_loop(net: Network, n: float, p: int) -> float:
    """What a hand-written 'root sends to everyone' loop costs: (p-1)*(alpha + n*beta).

    The comparison that makes the case for collectives in notes/09.
    """
    return (p - 1) * (net.alpha + n * net.beta)


def crossover(short, long_, net: Network, p: int,
              lo: float = 1.0, hi: float = 1 << 30) -> float:
    """Message size in bytes at which `long_` becomes cheaper than `short`.

    Bisection; both arguments are functions (net, n, p) -> seconds.  Returns
    math.inf if the long-message algorithm never wins in [lo, hi].
    """
    if long_(net, hi, p) >= short(net, hi, p):
        return math.inf
    if long_(net, lo, p) < short(net, lo, p):
        return lo
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if long_(net, mid, p) < short(net, mid, p):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------
# scaling - Amdahl in the lecturer's convention
# --------------------------------------------------------------------------

def amdahl(f: float, p: int) -> float:
    """Speedup with f the SEQUENTIAL fraction: S_p = 1 / (f + (1-f)/p).

    This is the form on the ASC slide (asc_intro+login.pdf):
        T_parallel,p = f*T_serial + (1-f)*T_serial/p
    Textbooks that call f the PARALLEL fraction have f and 1-f swapped, so
    always state which you mean.
    """
    if not 0.0 <= f <= 1.0:
        raise ValueError("f is a fraction in [0, 1]")
    if p < 1:
        raise ValueError("p >= 1")
    return 1.0 / (f + (1.0 - f) / p)


def amdahl_limit(f: float) -> float:
    """S_infinity = 1/f, the bound Amdahl's law puts on the speedup."""
    if f <= 0.0:
        return math.inf
    return 1.0 / f


# --------------------------------------------------------------------------

def _demo() -> None:
    # A plausible cluster: 1.5 us latency, 12 GB/s, reduction at 5 GB/s.
    net = Network.from_latency_bandwidth(1.5, 12.0, 5.0)
    print(f"alpha = {net.alpha*1e6:.2f} us, beta = {net.beta:.3e} s/B, "
          f"gamma = {net.gamma:.3e} s/B")
    print(f"n_half = {n_half(net)/1024:.1f} kB  "
          "(below this a message is latency bound)\n")

    print("Allreduce of one double (8 B), recursive doubling vs Rabenseifner:")
    print(f"{'p':>7} {'rec.doubling':>14} {'Rabenseifner':>14} {'naive loop':>14}")
    for p in (4, 16, 64, 256, 1024, 4096):
        a = allreduce_recursive_doubling(net, 8, p) * 1e6
        b = allreduce_rabenseifner(net, 8, p) * 1e6
        c = naive_send_loop(net, 8, p) * 1e6 * 2  # reduce + bcast
        print(f"{p:>7} {a:>12.1f} us {b:>12.1f} us {c:>12.1f} us")

    print("\nBroadcast: tree vs scatter+allgather, p = 1024")
    x = crossover(bcast_short, bcast_long, net, 1024)
    print(f"  crossover at {x/1024:.1f} kB")

    print("\nBatching scalar reductions, p = 1024:")
    one = allreduce_recursive_doubling(net, 8, 1024)
    three = 3 * one
    batched = allreduce_recursive_doubling(net, 24, 1024)
    print(f"  three separate Allreduce(1 double): {three*1e6:.1f} us")
    print(f"  one Allreduce(3 doubles):           {batched*1e6:.1f} us "
          f"({three/batched:.2f}x cheaper)")

    print("\nAmdahl (f = SEQUENTIAL fraction):")
    for f in (0.05, 0.02):
        print(f"  f = {f}:  S_inf = {amdahl_limit(f):.0f}, "
              f"S_64 = {amdahl(f, 64):.2f}, S_100 = {amdahl(f, 100):.2f}, "
              f"E_100 = {amdahl(f, 100)/100:.1%}")


if __name__ == "__main__":
    _demo()
