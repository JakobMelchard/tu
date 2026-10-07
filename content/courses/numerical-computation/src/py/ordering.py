"""Fill-in and ordering strategies for sparse Cholesky (note 05).

Implements [S4 §4.6] (CSE).  The Cholesky factor of a sparse SPD matrix
inherits the sparsity pattern only up to fill-in, and how much fill-in there is
depends on how the unknowns are numbered ([S4] Thm 4.35).  Reverse
Cuthill-McKee ([S4] Alg. 12-13) attacks the bandwidth, minimum degree
([S4] Alg. 14) attacks the fill directly; symbolic_cholesky_nnz counts it.
"""
from collections import deque

import numpy as np


# ----------------------------------------------- graphs, fill-in, ordering
def adjacency_graph(A, tol=0.0):
    """Neighbour lists of the (symmetrised) sparsity graph G(A)."""
    A = np.asarray(A, float)
    n = A.shape[0]
    S = (np.abs(A) > tol) | (np.abs(A.T) > tol)
    np.fill_diagonal(S, False)
    return [list(np.flatnonzero(S[i])) for i in range(n)]


def cuthill_mckee(A, start=None):
    """[S4] Alg. 12.  FIFO; a node's unnumbered neighbours are queued in
    ascending order of degree.  Handles disconnected graphs."""
    g = adjacency_graph(A)
    n = len(g)
    deg = np.array([len(gi) for gi in g])
    order, seen = [], np.zeros(n, bool)
    roots = [start] if start is not None else []
    while len(order) < n:
        if roots:
            v = roots.pop(0)
        else:
            remaining = np.flatnonzero(~seen)
            v = int(remaining[np.argmin(deg[remaining])])
        if seen[v]:
            continue
        fifo = deque([v])
        seen[v] = True
        while fifo:
            u = fifo.popleft()
            order.append(u)
            nbrs = [w for w in g[u] if not seen[w]]
            for w in sorted(nbrs, key=lambda w: deg[w]):
                seen[w] = True
                fifo.append(w)
    return np.array(order)


def pseudo_peripheral_node(A):
    """A cheap stand-in for a peripheral start node ([S4] sec. 4.6.2): repeatedly
    take the last node of a breadth-first sweep."""
    g = adjacency_graph(A)
    n = len(g)
    v = int(np.argmin([len(gi) for gi in g]))
    for _ in range(3):
        seen = np.zeros(n, bool)
        seen[v] = True
        level, last = [v], v
        while level:
            nxt = []
            for u in level:
                for w in g[u]:
                    if not seen[w]:
                        seen[w] = True
                        nxt.append(w)
            if nxt:
                last = nxt[-1]
            level = nxt
        v = last
    return v


def reverse_cuthill_mckee(A, start=None):
    """[S4] Alg. 13: Cuthill-McKee from a pseudo-peripheral node, reversed."""
    if start is None:
        start = pseudo_peripheral_node(A)
    return cuthill_mckee(A, start)[::-1].copy()


def minimum_degree(A):
    """[S4] Alg. 14.  Greedily eliminate a node of minimum degree, adding the
    clique edges its elimination creates, and repeat."""
    g = [set(v) for v in adjacency_graph(A)]
    n = len(g)
    alive = set(range(n))
    order = []
    while alive:
        v = min(alive, key=lambda u: (len(g[u] & alive), u))
        order.append(v)
        nbrs = g[v] & alive - {v}
        for a in nbrs:                       # eliminating v makes its neighbours a clique
            g[a] |= nbrs - {a}
        alive.discard(v)
    return np.array(order)


def symbolic_cholesky_nnz(A, order=None, tol=0.0):
    """Non-zeros in the Cholesky factor of A (symmetrised) under a permutation.

    Pure symbolic elimination on the graph, so it counts structural non-zeros
    exactly as [S4] Ex. 4.37 does (the diagonal is included).
    """
    A = np.asarray(A, float)
    n = A.shape[0]
    if order is None:
        order = np.arange(n)
    inv = np.empty(n, int)
    inv[order] = np.arange(n)
    g = [set() for _ in range(n)]
    for i, row in enumerate(adjacency_graph(A, tol)):
        for j in row:
            g[inv[i]].add(inv[j])
    nnz = n                                   # the diagonal
    for k in range(n):
        later = {j for j in g[k] if j > k}
        nnz += len(later)
        for a in later:                       # fill-in: later neighbours form a clique
            g[a] |= later - {a}
    return nnz


def poisson_2d_pattern(m):
    """The 5-point Laplacian on an m x m grid, lexicographic ordering.

    [S4] Ex. 4.37 uses m = 30, i.e. A in R^{900 x 900} with 5 non-zeros per row.
    """
    n = m * m
    A = np.zeros((n, n))
    for i in range(m):
        for j in range(m):
            k = i * m + j
            A[k, k] = 4.0
            if i > 0:
                A[k, k - m] = -1.0
            if i < m - 1:
                A[k, k + m] = -1.0
            if j > 0:
                A[k, k - 1] = -1.0
            if j < m - 1:
                A[k, k + 1] = -1.0
    return A


if __name__ == "__main__":
    print("--- fill-in on the 2-D Poisson matrix [S4 Ex. 4.37] ---")
    P = poisson_2d_pattern(30)
    print(f"  A is {P.shape[0]}x{P.shape[0]}, nnz(A) = {int((P != 0).sum())}")
    print(f"  Cholesky, lexicographic        : {symbolic_cholesky_nnz(P):6d}   (S4: 27029)")
    print(f"  Cholesky, reverse Cuthill-McKee: "
          f"{symbolic_cholesky_nnz(P, reverse_cuthill_mckee(P)):6d}   (S4: 19315)")
    print(f"  Cholesky, minimum degree       : "
          f"{symbolic_cholesky_nnz(P, minimum_degree(P)):6d}   (S4: 10042, approximate MD)")

    print("\n--- what RCM actually buys on a regular grid ---")
    from banded import bandwidths
    print("  the lexicographic ordering of an m x m grid already has bandwidth m,")
    print("  so RCM cannot improve THAT -- what it reduces is the envelope, and")
    print("  with it the fill-in:")
    for m in (6, 10, 16, 30):
        A = poisson_2d_pattern(m)
        o = reverse_cuthill_mckee(A)
        print(f"  {m:2d}x{m:2d} grid: bandwidth {bandwidths(A)[0]:3d} ->"
              f" {bandwidths(A[np.ix_(o, o)])[0]:3d},   Cholesky nnz"
              f" {symbolic_cholesky_nnz(A):6d} -> {symbolic_cholesky_nnz(A, o):6d}")
