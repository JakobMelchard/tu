"""Query complexity: decision-tree depth D(f), quantum phase-oracle algorithms
(Deutsch pair-parity, Deutsch-Jozsa, Grover), and the polynomial-method check.

Belongs to the complexity note B06 (quantum complexity, query complexity).

Query model: the input is an n-bit string x, hidden behind the phase oracle
O_x |i> = (-1)^{x_i} |i> on an index register of dimension n (a 2^m-dimensional
register when n = 2^m).  A t-query quantum algorithm is
U_t O_x U_{t-1} ... O_x U_0 |0>, followed by a projective measurement.

Implements: decision_tree_depth (exhaustive minimax, n <= 4), phase_oracle,
deutsch_pair_parity (x_i xor x_j with one query), parity_via_pairs (n/2 queries),
deutsch_jozsa (constant vs balanced with one query), grover_or / grover_iterations
(OR_N in ~ pi/4 sqrt(N) queries), multilinear_coefficients and
acceptance_polynomial_degree (Beals et al.: t queries => degree <= 2t).
"""
from functools import lru_cache
from itertools import product
import math

import numpy as np


# ---------------------------------------------------------- deterministic D(f)
def decision_tree_depth(f, n):
    """D(f) = min over decision trees of max path length, by exhaustive minimax.

    depth(restriction) = 0 if f is constant on all completions, else
    min_i unqueried [1 + max_b depth(restriction + {x_i = b})].
    Restrictions are encoded as (known mask, value mask).  2^n * 3^n work: n <= 4.
    """
    @lru_cache(maxsize=None)
    def depth(known, vals):
        outs = {f(tuple(((vals >> i) & 1) if (known >> i) & 1 else free[i] for i in range(n)))
                for free in product((0, 1), repeat=n)}
        if len(outs) == 1:
            return 0
        return min(1 + max(depth(known | (1 << i), vals | (b << i)) for b in (0, 1))
                   for i in range(n) if not (known >> i) & 1)

    return depth(0, 0)


OR = lambda x: int(any(x))
PARITY = lambda x: sum(x) % 2
AND = lambda x: int(all(x))


# ------------------------------------------------------------ phase oracle
def phase_oracle(x):
    """Diagonal n x n matrix with entries (-1)^{x_i}."""
    return np.diag([(-1.0) ** b for b in x])


def deutsch_pair_parity(x, i, j):
    """x_i xor x_j with ONE query (Deutsch).  Prepare (|i>+|j>)/sqrt2, query,
    measure in the {|+>, |->} basis of span{|i>, |j>}: the relative phase
    (-1)^{x_i + x_j} moves |+> to |-> exactly when the parity is odd."""
    n = len(x)
    psi = np.zeros(n)
    psi[i] = psi[j] = 1 / math.sqrt(2)
    psi = phase_oracle(x) @ psi
    minus = np.zeros(n)
    minus[i], minus[j] = 1 / math.sqrt(2), -1 / math.sqrt(2)
    p_odd = abs(minus @ psi) ** 2  # deterministic: exactly 0 or 1
    assert abs(p_odd - round(p_odd)) < 1e-12
    return int(round(p_odd))


def parity_via_pairs(x):
    """PARITY_n with ceil(n/2) queries: one Deutsch query per pair, XOR classically.
    Returns (parity, number_of_queries).  Lower bound: Q(PARITY) >= n/2 (B06)."""
    n = len(x)
    acc, queries = 0, 0
    for i in range(0, n - 1, 2):
        acc ^= deutsch_pair_parity(x, i, i + 1)
        queries += 1
    if n % 2:  # odd n: read the last bit with one classical query
        acc ^= x[-1]
        queries += 1
    return acc, queries


def hadamard(m):
    H = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
    out = np.array([[1.0]])
    for _ in range(m):
        out = np.kron(out, H)
    return out


def deutsch_jozsa(truth_table):
    """truth_table: 2^m bits of f promised constant or balanced.  One query:
    H^m O_f H^m |0..0>; amplitude of |0..0> is (1/N) sum_x (-1)^{f(x)} = +-1 or 0."""
    N = len(truth_table)
    m = int(math.log2(N))
    H = hadamard(m)
    psi = H @ phase_oracle(truth_table) @ H @ np.eye(N)[0]
    p0 = abs(psi[0]) ** 2
    return "constant" if p0 > 0.5 else "balanced"


# ---------------------------------------------------------------- Grover
def grover_iterations(N, marked=1):
    """Round((pi/4) sqrt(N/marked) - 1/2): angle theta = asin(sqrt(marked/N)),
    after r iterations success probability is sin^2((2r+1) theta)."""
    theta = math.asin(math.sqrt(marked / N))
    return max(0, round(math.pi / (4 * theta) - 0.5))


def grover_or(x, iterations=None):
    """OR_N by Grover search; returns (iterations, Pr[measure a marked index])."""
    N = len(x)
    marked = sum(x)
    if marked == 0:
        return 0, 0.0
    r = grover_iterations(N, marked) if iterations is None else iterations
    s = np.full(N, 1 / math.sqrt(N))
    diffusion = 2 * np.outer(s, s) - np.eye(N)
    O = phase_oracle(x)
    psi = s.copy()
    for _ in range(r):
        psi = diffusion @ (O @ psi)
    return r, float(sum(psi[i] ** 2 for i in range(N) if x[i]))


# ------------------------------------------------------- polynomial method
def multilinear_coefficients(values):
    """values[mask] = P(x) for every x in {0,1}^n (mask bit i = x_i).  Returns the
    coefficients c[S] of the unique multilinear polynomial sum_S c_S prod_{i in S} x_i
    by the subset Moebius transform c_S = sum_{T subset S} (-1)^{|S|-|T|} P(x_T)."""
    c = np.array(values, dtype=float)
    n = int(math.log2(len(c)))
    for i in range(n):
        for mask in range(len(c)):
            if mask >> i & 1:
                c[mask] -= c[mask ^ (1 << i)]
    return c


def acceptance_polynomial_degree(algorithm, n, tol=1e-9):
    """algorithm(x) -> acceptance probability.  Degree of its multilinear expansion."""
    vals = [algorithm(tuple((mask >> i) & 1 for i in range(n))) for mask in range(2 ** n)]
    c = multilinear_coefficients(vals)
    return max((bin(m).count("1") for m in range(2 ** n) if abs(c[m]) > tol), default=0)


def random_query_algorithm(n, t, rng, ancilla=2):
    """A generic t-query algorithm: Haar-random unitaries U_0..U_t on index (x) ancilla,
    oracle O_x (x) I between them, accept iff the ancilla measures 1.  Returns P(x).

    The index register has n + 1 basis states: index n is a dummy with x_n = 0
    fixed, i.e. a "do not query" branch (equivalent to a controlled query).
    Without it every amplitude monomial in z_i = (-1)^{x_i} has degree == t mod 2,
    so |amplitude|^2 would only contain even-degree monomials.
    """
    d = (n + 1) * ancilla
    us = []
    for _ in range(t + 1):
        z = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
        q, r = np.linalg.qr(z)
        us.append(q * (np.diag(r) / abs(np.diag(r))))
    accept = np.kron(np.eye(n + 1), np.diag([0.0] * (ancilla - 1) + [1.0]))

    def P(x):
        psi = np.eye(d)[0].astype(complex)
        O = np.kron(phase_oracle(tuple(x) + (0,)), np.eye(ancilla))
        psi = us[0] @ psi
        for u in us[1:]:
            psi = u @ (O @ psi)
        return float(np.real(psi.conj() @ accept @ psi))

    return P


if __name__ == "__main__":
    for name, f in (("OR", OR), ("PARITY", PARITY), ("AND", AND)):
        print(name, "D(f) for n=1..4:", [decision_tree_depth(f, n) for n in range(1, 5)])
    for x in ((0, 1, 1, 0), (1, 1, 1, 0), (1, 0, 1)):
        print("parity", x, "->", parity_via_pairs(x), "(value, queries)")
    print("Deutsch-Jozsa:", deutsch_jozsa((0, 0, 0, 0)), deutsch_jozsa((0, 1, 1, 0)))
    for N in (4, 16, 64, 256):
        x = [0] * N
        x[N // 3] = 1
        r, p = grover_or(x)
        print(f"Grover OR_{N}: {r} iterations (pi/4 sqrt N = {math.pi / 4 * math.sqrt(N):.2f}), "
              f"success {p:.4f}")
    rng = np.random.default_rng(0)
    for t in (1, 2):
        deg = acceptance_polynomial_degree(random_query_algorithm(5, t, rng), 5)
        print(f"random {t}-query algorithm on n=5: acceptance polynomial degree {deg} <= {2 * t}")
    P = lambda x: deutsch_pair_parity(x, 0, 1)
    print("Deutsch parity acceptance polynomial coefficients:",
          multilinear_coefficients([P(((m >> 0) & 1, (m >> 1) & 1)) for m in range(4)]))
