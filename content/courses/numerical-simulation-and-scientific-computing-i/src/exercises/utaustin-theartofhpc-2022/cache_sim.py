"""Set-associative cache simulator, and three experiments run on it.

Our solution to three exercises in V. Eijkhout, *The Art of HPC, volume 1:
Introduction to High-Performance Scientific Computing* [S43], chapter
"Single-processor Computing". The exercise texts are restated in our words;
the code is ours. [S43] is CC BY 4.0.

  E1  "Caches > Direct mapped caches". His worked conflict example is a
      64 KB direct-mapped cache, 32-bit addresses, and `double A[3][8192]`
      summed row-wise: the three rows sit exactly 64 KB apart, so the *last*
      16 address bits agree and every access evicts the previous one. Show
      the conflicts vanish if the *first* 16 bits are used as the cache
      address, and say why that is a bad rule in general.
  E2  "Caches > Associative caches". Simulate a k-way associative cache of
      32 entries with 16-bit addresses; for k = 1, 2, 4, ... store 32 random
      addresses, count how many are still resident, repeat 100 times, and
      report median, mean and stdev. What is the limit behaviour in k?
  E3  "Locality > Spatial locality". Contrast the locality of the pairwise
      (tree) summation of n numbers with the straight linear sum.

NOT a 360.242 exercise sheet -- 360.242 publishes none. See README.md.
Run ``python cache_sim.py`` for all three.
"""

from __future__ import annotations

import random
from statistics import mean, median, pstdev

WORD = 8  # bytes in a double


class Cache:
    """`n_sets * assoc` lines of `line_bytes` bytes each, LRU within a set.

    `index_bits="low"`  takes the set index from the low address bits, after
    dropping the line offset -- what every real cache does, and what E1's
    example assumes.
    `index_bits="high"` takes it from the most significant bits of the address,
    which is the alternative E1 asks about.
    """

    def __init__(self, n_sets: int, assoc: int = 1, line_bytes: int = 1,
                 index_bits: str = "low", addr_bits: int = 32) -> None:
        if n_sets & (n_sets - 1) or line_bytes & (line_bytes - 1):
            raise ValueError("n_sets and line_bytes must be powers of two")
        if index_bits not in ("low", "high"):
            raise ValueError("index_bits must be 'low' or 'high'")
        self.n_sets, self.assoc = n_sets, assoc
        self.line_bytes, self.index_bits, self.addr_bits = line_bytes, index_bits, addr_bits
        # "high" drops as many bits as the cache is wide: with a 64 KB cache
        # and 32-bit addresses that is the top 16 bits, which is exactly the
        # alternative mapping E1 proposes.
        self.high_shift = max(addr_bits - (n_sets * line_bytes - 1).bit_length(), 0)
        self.hits = self.misses = self.evictions = 0
        self._sets: dict[int, list[int]] = {}

    @property
    def n_lines(self) -> int:
        return self.n_sets * self.assoc

    def line_of(self, addr: int) -> int:
        return addr // self.line_bytes

    def set_of(self, addr: int) -> int:
        if self.n_sets == 1:
            return 0
        if self.index_bits == "low":
            return self.line_of(addr) % self.n_sets
        return (addr >> self.high_shift) % self.n_sets

    def access(self, addr: int) -> bool:
        """Touch `addr`; True on a hit. List order is LRU order, newest last."""
        line, s = self.line_of(addr), self.set_of(addr)
        ways = self._sets.setdefault(s, [])
        if line in ways:
            ways.remove(line)
            ways.append(line)
            self.hits += 1
            return True
        self.misses += 1
        if len(ways) == self.assoc:
            ways.pop(0)
            self.evictions += 1
        ways.append(line)
        return False

    def run(self, addresses) -> "Cache":
        for a in addresses:
            self.access(a)
        return self

    def resident_lines(self) -> set[int]:
        return {ln for ways in self._sets.values() for ln in ways}


# --------------------------------------------------------------------- E1
def three_row_trace(n_iter: int = 512, row_words: int = 8192) -> list[int]:
    """`for i < n_iter: a[2][i] = (a[0][i] + a[1][i])/2` as byte addresses."""
    return [WORD * (r * row_words + i) for i in range(n_iter) for r in (0, 1, 2)]


def e1_index_bits(n_sets: int = 2048, line_bytes: int = 32) -> dict:
    """The conflict loop, and a contiguous stream, under both mappings.

    64 KB of cache either way: 2048 lines of 32 bytes, direct mapped.
    """
    out: dict[str, dict[str, int]] = {}
    for which in ("low", "high"):
        c = Cache(n_sets, 1, line_bytes, index_bits=which).run(three_row_trace())
        out[which] = {"conflict_hits": c.hits, "conflict_misses": c.misses}
        # Why "high" is not a general rule: a contiguous array smaller than
        # 2**16 bytes has identical high bits, so it collapses onto one set.
        c2 = Cache(n_sets, 1, line_bytes, index_bits=which)
        c2.run(range(0, n_sets * line_bytes, WORD))
        out[which]["stream_resident_lines"] = len(c2.resident_lines())
        out[which]["stream_misses"] = c2.misses
    return out


# --------------------------------------------------------------------- E2
def occupancy_trial(n_entries: int, assoc: int, rng: random.Random,
                    addr_bits: int = 16) -> int:
    """Throw `n_entries` distinct random addresses in; how many survive?"""
    addrs = rng.sample(range(1 << addr_bits), n_entries)
    cache = Cache(n_entries // assoc, assoc, 1, addr_bits=addr_bits)
    return len(cache.run(addrs).resident_lines())


def associativity_sweep(n_entries: int = 32, trials: int = 100,
                        seed: int = 20260922) -> dict[int, dict[str, float]]:
    rng = random.Random(seed)
    out, k = {}, 1
    while k <= n_entries:
        counts = [occupancy_trial(n_entries, k, rng) for _ in range(trials)]
        out[k] = {"median": median(counts), "mean": mean(counts),
                  "stdev": pstdev(counts), "min": min(counts), "max": max(counts)}
        k *= 2
    return out


def expected_occupancy_direct_mapped(n: int) -> float:
    """Closed form for k = 1: n slots, n addresses thrown in at random.

    A given slot stays empty with probability (1 - 1/n)**n, so the expected
    occupancy is n(1 - (1 - 1/n)**n) -> n(1 - 1/e) ~ 0.632 n. This is what makes
    E2 checkable rather than merely plottable; k = n gives n exactly.
    """
    return n * (1.0 - (1.0 - 1.0 / n) ** n)


# --------------------------------------------------------------------- E3
def linear_sum_trace(n: int) -> list[int]:
    """`for i: sum += x[i]` -- one unit-stride pass over n doubles."""
    return [WORD * i for i in range(n)]


def tree_sum_trace(n: int) -> list[int]:
    """Eijkhout's pairwise scheme: for s = 2,4,...,n: x[i] += x[i+s/2]."""
    trace: list[int] = []
    s = 2
    while s <= n:
        for i in range(0, n, s):
            trace += [WORD * i, WORD * (i + s // 2), WORD * i]
        s *= 2
    return trace


def e3_locality(n: int = 1024, n_sets: int = 8, assoc: int = 4,
                line_bytes: int = 32) -> dict:
    """Miss counts for the two summation orders on the same small cache."""
    out = {}
    for name, trace in (("linear", linear_sum_trace(n)),
                        ("tree", tree_sum_trace(n))):
        c = Cache(n_sets, assoc, line_bytes).run(trace)
        out[name] = {"accesses": len(trace), "misses": c.misses,
                     "misses_per_element": c.misses / n}
    return out


def _main() -> None:
    print("E1  64 KB direct-mapped cache, 32-byte lines, double A[3][8192]")
    for which, r in e1_index_bits().items():
        print(f"  index from {which:>4} bits: conflict loop {r['conflict_hits']:5d} hits /"
              f" {r['conflict_misses']:5d} misses;"
              f" 64 KB stream leaves {r['stream_resident_lines']:5d} lines resident")
    print("\nE2  resident addresses out of 32, 16-bit addresses, 100 trials")
    print(f"  {'k':>3} {'median':>7} {'mean':>7} {'stdev':>7} {'min':>4} {'max':>4}")
    for k, s in associativity_sweep().items():
        print(f"  {k:>3} {s['median']:>7.1f} {s['mean']:>7.2f} {s['stdev']:>7.2f}"
              f" {s['min']:>4} {s['max']:>4}")
    print("  k=1 predicted mean n(1-(1-1/n)^n) = "
          f"{expected_occupancy_direct_mapped(32):.2f}")
    print("\nE3  linear vs tree summation of 1024 doubles, 8 sets x 4 ways x 32 B")
    for name, r in e3_locality().items():
        print(f"  {name:>6}: {r['accesses']:6d} accesses, {r['misses']:6d} misses,"
              f" {r['misses_per_element']:.3f} per element")


if __name__ == "__main__":
    _main()
