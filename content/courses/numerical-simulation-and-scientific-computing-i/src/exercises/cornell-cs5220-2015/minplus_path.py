"""All-pairs shortest paths as a matrix product in the (min, +) semiring.

Our solution to the analysis half of HW3 of Cornell CS 5220 *Applications of
Parallel Computers*, Fall 2015 (D. Bindel) [S44]. The assignment ships a C
reference that repeatedly squares the distance matrix under (min, +) and asks
for a profile, a parallelisation and a tuning study; the parts we can carry
into this course's shared-memory, single-node setting are:

  A  the cost model -- why repeated squaring is O(n^3 log n) where
     Floyd-Warshall is O(n^3), and how many squarings are actually needed;
  B  blocking -- the kernel is a matrix product with min for + and + for *,
     so the same cache-blocking argument as GEMM applies verbatim;
  C  correctness -- both routes must agree with each other and with a library.

NOT a 360.242 exercise sheet -- 360.242 publishes none. See README.md.
[S44] is MIT licensed; the exercise is restated in our words, the code is ours.

Run ``python minplus_path.py`` for a cost table.
"""

from __future__ import annotations

import numpy as np

INF = np.inf


def random_graph(n: int, p: float = 0.05, seed: int = 20260922,
                 max_weight: float = 10.0) -> np.ndarray:
    """Directed graph as a dense distance matrix; missing edges are INF.

    This is the generator shape the CS 5220 reference uses: an Erdos-Renyi
    graph with a fixed density, zero diagonal, INF elsewhere.
    """
    rng = np.random.default_rng(seed)
    w = rng.uniform(1.0, max_weight, size=(n, n))
    l = np.where(rng.random((n, n)) < p, w, INF)
    np.fill_diagonal(l, 0.0)
    return l


# ----------------------------------------------------------------------- A
def floyd_warshall(l: np.ndarray) -> np.ndarray:
    """O(n^3): n rank-1 relaxations, each O(n^2). One pass, no iteration."""
    d = l.copy()
    n = d.shape[0]
    for k in range(n):
        # d = min(d, d[:,k] + d[k,:]) -- the outer-product update
        np.minimum(d, d[:, k, None] + d[None, k, :], out=d)
    return d


def minplus_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """c[i,j] = min_k (a[i,k] + b[k,j]): matrix product in the (min,+) semiring."""
    return np.min(a[:, :, None] + b[None, :, :], axis=1)


def shortest_paths_squaring(l: np.ndarray, max_steps: int | None = None,
                            tol: float = 1e-12) -> tuple[np.ndarray, int]:
    """Repeated squaring until the matrix stops changing.

    After s squarings the entries are the shortest walks using at most 2**s
    edges, so a graph whose shortest paths use at most n-1 edges converges in
    ceil(log2(n-1)) squarings -- one more is spent detecting it. That is the
    log n factor the assignment asks you to account for.

    The stopping test needs a tolerance, not equality: min_k(d[i,k] + d[k,j])
    re-adds the two halves of an already-optimal path, and in floating point
    that sum can come out one ulp below the stored value. With `==` the loop
    then chases last bits and runs far past the log n bound -- a good example
    of a convergence test that is wrong for numerical rather than algorithmic
    reasons.
    """
    d = l.copy()
    n = d.shape[0]
    limit = n if max_steps is None else max_steps
    for step in range(1, limit + 1):
        nxt = minplus_product(d, d)
        if max_abs_diff(nxt, d) <= tol:
            return d, step
        d = nxt
    return d, limit


def squarings_needed(n: int) -> int:
    """Upper bound on the squarings before the fixed point is reached."""
    return 1 if n <= 2 else int(np.ceil(np.log2(n - 1)))


def flop_counts(n: int) -> dict[str, float]:
    """Semiring operations, the quantity the assignment's cost model is about.

    Floyd-Warshall does n passes of n^2 relaxations. Repeated squaring does one
    n^3 product per squaring, and needs ceil(log2(n-1)) + 1 of them, so it is
    a log n factor more work -- bought in exchange for a kernel that is a plain
    matrix product and therefore blocks and parallelises like GEMM.
    """
    steps = squarings_needed(n) + 1
    return {"floyd_warshall": float(n) ** 3,
            "squaring": steps * float(n) ** 3,
            "ratio": float(steps)}


# ----------------------------------------------------------------------- B
def minplus_product_blocked(a: np.ndarray, b: np.ndarray, block: int = 32
                            ) -> np.ndarray:
    """The same product, tiled i/j/k -- the GEMM blocking argument unchanged.

    Nothing about (min, +) breaks the argument: `min` is associative and
    commutative and `+` distributes over it, so partial results over disjoint
    k-blocks can be combined afterwards, exactly as partial sums are.
    """
    n = a.shape[0]
    c = np.full((n, n), INF)
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        for j0 in range(0, n, block):
            j1 = min(j0 + block, n)
            acc = c[i0:i1, j0:j1]
            for k0 in range(0, n, block):
                k1 = min(k0 + block, n)
                part = np.min(a[i0:i1, k0:k1, None] + b[None, k0:k1, j0:j1],
                              axis=1)
                np.minimum(acc, part, out=acc)
    return c


def working_set_bytes(block: int, itemsize: int = 8) -> int:
    """Three block^2 tiles must fit in cache for the tiled kernel to pay off."""
    return 3 * block * block * itemsize


def largest_block_for_cache(cache_bytes: int, itemsize: int = 8) -> int:
    """Largest power-of-two tile whose three tiles still fit in `cache_bytes`.

    The exam-shaped version of the tuning half of the assignment: given L1 or
    L2, what tile do you pick, and why three tiles and not two?
    """
    b = 1
    while working_set_bytes(2 * b, itemsize) <= cache_bytes:
        b *= 2
    return b


# ----------------------------------------------------------------------- C
def max_abs_diff(a: np.ndarray, b: np.ndarray) -> float:
    """Largest finite discrepancy; INF must line up with INF exactly."""
    both_inf = np.isinf(a) & np.isinf(b)
    if not np.array_equal(np.isinf(a), np.isinf(b)):
        return float("inf")
    d = np.where(both_inf, 0.0, np.abs(np.where(both_inf, 0.0, a) -
                                       np.where(both_inf, 0.0, b)))
    return float(np.max(d))


def has_negative_cycle(d: np.ndarray) -> bool:
    """A negative diagonal entry after convergence is the standard test."""
    return bool(np.any(np.diag(d) < 0))


def _main() -> None:
    print(f"{'n':>5} {'squarings':>10} {'bound':>6} {'FW ops':>12} {'sq ops':>12}"
          f" {'ratio':>6} {'max|diff|':>10}")
    for n in (8, 16, 32, 64):
        l = random_graph(n, p=0.08)
        d_fw = floyd_warshall(l)
        d_sq, steps = shortest_paths_squaring(l)
        c = flop_counts(n)
        diff = max_abs_diff(d_fw, d_sq)
        print(f"{n:>5} {steps:>10} {squarings_needed(n) + 1:>6}"
              f" {c['floyd_warshall']:>12.3g} {c['squaring']:>12.3g}"
              f" {c['ratio']:>6.0f} {diff:>10.2e}")
    for name, cache in (("L1 128 KB", 128 * 1024), ("L2 16 MB", 16 * 1024 * 1024)):
        b = largest_block_for_cache(cache)
        print(f"{name}: largest tile {b}x{b}, working set "
              f"{working_set_bytes(b) / 1024:.1f} KB")


if __name__ == "__main__":
    _main()
