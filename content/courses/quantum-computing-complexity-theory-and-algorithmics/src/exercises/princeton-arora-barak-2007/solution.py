"""Substitute practice for block B: Arora & Barak, *Computational Complexity*.

SOURCE [S60]: Sanjeev Arora, Boaz Barak, "Computational Complexity: A Modern
Approach", the authors' free internet draft (dated January 2007) at
<https://theory.cs.princeton.edu/complexity/book.pdf>.  Its title page says
"Not to be reproduced or distributed without the authors' permission", so this
folder is **cite-only**: nothing is vendored and no exercise text is copied.
Every exercise below is one we built ourselves for the theorem the book states;
README.md says which theorem and which chapter.

This folder covers exactly the four B-topics that [S59], the MIT paper in the
sibling folder, never reaches: the polynomial hierarchy, circuit complexity and
P/poly, Adleman's theorem, and BQP.

Run:  ../../../../../.venv/bin/python solution.py
"""
import itertools
import math
import os
import sys

import numpy as np
from scipy.stats import binom

_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py"))
sys.path.insert(0, os.path.join(_py, "complexity"))
sys.path.insert(0, os.path.join(_py, "quantum"))

import sat as S                                                   # noqa: E402
from sim import Register                                          # noqa: E402


# --- 1. The polynomial hierarchy (B02; AB ch. 5) ------------------------------
def eval_qbf(prefix, cnf, n, negate=False):
    """Evaluate Q_1 x_1 ... Q_n x_n phi with prefix a string over {'E','A'}.

    With negate=True the matrix is (not phi), which is what the Pi_2 dual of a
    Sigma_2 instance needs.  Recursion depth n, one bit of state per level: the
    whole of PH sits inside PSPACE because *this function* is the decider and
    its stack is O(n).
    """
    def rec(i, assign):
        if i == n:
            return S.evaluate(cnf, assign) != negate
        results = []
        for b in (False, True):
            assign[i + 1] = b
            results.append(rec(i + 1, assign))
        assign.pop(i + 1, None)
        return any(results) if prefix[i] == "E" else all(results)
    return rec(0, {})


def sigma2_sat(cnf, n_exists, n):
    """exists x_1..x_k forall x_{k+1}..x_n . phi   -- the canonical Sigma_2^p problem."""
    return eval_qbf("E" * n_exists + "A" * (n - n_exists), cnf, n)


def pt1_polynomial_hierarchy(n=4, trials=200, seed=7):
    """Three facts, all checkable:

    (a) Sigma_2 and Pi_2 are complements:
            not (exists x forall y . phi)  ==  forall x exists y . not phi.
        Checked by swapping the prefix *and* complementing the matrix.
    (b) Sigma_1 = NP: with prefix 'EEEE' the evaluator agrees with brute-force SAT.
    (c) PH subseteq PSPACE: the evaluator's workspace is the assignment plus the
        recursion stack, both O(n); it never stores the 2^n branches.
    """
    rng = np.random.default_rng(seed)
    lits = [l for i in range(1, n + 1) for l in (i, -i)]
    dual_ok = sigma1_ok = 0
    for _ in range(trials):
        m = int(rng.integers(1, 6))
        cnf = [[int(lits[j]) for j in rng.choice(len(lits), 3, replace=False)]
               for _ in range(m)]
        k = int(rng.integers(1, n))
        val = sigma2_sat(cnf, k, n)
        # (a) Sigma_2 / Pi_2 duality
        dual = eval_qbf("A" * k + "E" * (n - k), cnf, n, negate=True)
        assert val == (not dual)
        dual_ok += 1
        # (b) Sigma_1 = NP
        assert eval_qbf("E" * n, cnf, n) == (S.brute_force_sat(cnf) is not None)
        sigma1_ok += 1
    # (c) one instance where moving a variable across the quantifier alternation
    #     changes the answer -- the reason the levels are not obviously equal
    phi = [[1, -2, 4], [1, -2, 3], [-2, -3, -4], [1, 3, -4], [-2, 3]]
    assert not sigma2_sat(phi, 1, 4) and sigma2_sat(phi, 2, 4)
    return {"instances": trials, "sigma1 = NP checks": sigma1_ok,
            "duality checks": dual_ok,
            "example: exists x1 forall x2 x3 x4": sigma2_sat(phi, 1, 4),
            "example: exists x1 x2 forall x3 x4": sigma2_sat(phi, 2, 4),
            "workspace": "assignment + stack = O(n) bits, hence PH subseteq PSPACE"}


# --- 2. Circuit complexity and P/poly (B04; AB ch. 6) -------------------------
def circuits_of_size_at_most(n, s):
    """Upper bound on the number of fan-in-2 circuits with s gates over n inputs.

    Each gate picks one of 16 binary truth tables and two sources among the
    n inputs, the constants 0 and 1, and the s gates: (16 (n + s + 2)^2)^s.
    """
    return (16 * (n + s + 2) ** 2) ** s


def pt2_shannon_counting(max_n=12):
    """Shannon's counting argument: there are 2^(2^n) functions on n bits but
    far fewer small circuits, so *most* functions need circuits of size about
    2^n / n.  We compute, for each n, the smallest s whose circuit count can
    still cover all 2^(2^n) functions, and compare it with 2^n / n.
    """
    rows = []
    for n in range(2, max_n + 1):
        target = (2 ** n) * math.log(2)                # log of 2^(2^n)
        s = 1
        while math.log(circuits_of_size_at_most(n, s)) < target:
            s += 1
        rows.append((n, s, 2 ** n / n))
        assert s > 2 ** n / (4 * n), "the bound must grow like 2^n / n"
    return {"n, min gates to cover all functions, 2^n/n": rows}


def pt2_ppoly_contains_undecidable(max_n=8, seed=11):
    """P/poly is not contained in the decidable languages.

    Take any set A of naturals and put L = {1^n : n in A}.  L has one input
    length per n, so a *constant* circuit (the constant 0 or the constant 1)
    decides it: circuit complexity 1 regardless of how uncomputable A is.
    We build A from a pseudo-random oracle to make the point concrete.
    """
    rng = np.random.default_rng(seed)
    membership = {n: bool(rng.integers(0, 2)) for n in range(max_n + 1)}
    advice = {n: int(membership[n]) for n in membership}     # the whole "circuit"
    for n in membership:
        assert (advice[n] == 1) == membership[n]
    return {"lengths": max_n + 1, "circuit size per length": 1,
            "moral": "P/poly contains undecidable unary languages; "
                     "non-uniformity is the whole difference"}


# --- 3. Adleman: BPP subseteq P/poly (B05; AB ch. 7) --------------------------
def pt3_adleman(n=6, pool=400, p=2 / 3, alpha=1.0, seed=3, max_draws=200):
    """Amplify, then fix one random string that works for *every* input.

    Model: a BPP machine whose correctness on input x with random string r is a
    Bernoulli(p) table.  Amplifying by t repetitions and taking the majority
    drops the per-input error below 2^-n; a union bound over the 2^n inputs then
    leaves a positive probability that some single t-tuple is correct on all of
    them, so one exists -- and it is the advice string.  Non-constructive in the
    proof, findable by sampling here.
    """
    rng = np.random.default_rng(seed)
    t = 1
    while binom.cdf((t - 1) // 2, t, p) * 2 ** n >= alpha:
        t += 2                                   # odd t, no ties
    per_input_error = float(binom.cdf((t - 1) // 2, t, p))
    table = rng.random((2 ** n, pool)) < p       # table[x][r] = "correct"
    for draw in range(max_draws):
        pick = rng.choice(pool, t, replace=False)
        if bool(np.all(table[:, pick].sum(axis=1) * 2 > t)):
            return {"inputs": 2 ** n, "repetitions t": t,
                    "per-input error": per_input_error,
                    "union bound": per_input_error * 2 ** n,
                    "advice found after draws": draw + 1,
                    "advice length": f"{t} random strings"}
    raise AssertionError("no advice string found; raise max_draws or t")


# --- 4. BQP by the Feynman path sum (B06; AB ch. 10) -------------------------
# CONVENTION.  Arora & Barak write a basis state as |x_1 ... x_n> with x_1 the
# leftmost tensor factor, which is also Egly's convention: leftmost symbol =
# first factor = most significant bit [S16, S20].  Qiskit reverses it [S17].
# This module therefore builds every gate matrix *through* src/py/quantum/sim.py,
# whose big-endian convention is the course's, rather than writing kron products
# by hand -- see the endianness assertion at the end of path_sum_amplitude.
def _full_matrix(n, apply_fn):
    """The 2^n x 2^n matrix of one circuit step, in the course's qubit order."""
    cols = []
    for j in range(2 ** n):
        reg = Register(n, np.eye(2 ** n)[j])
        apply_fn(reg)
        cols.append(reg.state)
    return np.array(cols).T


def pt4_path_sum(n=3):
    """Amplitude of an output string as a sum over all intermediate basis paths.

    Feynman's path sum computes <y|U_d ... U_1|0> by summing 2^(n(d-1)) products
    of single entries.  Each term needs only O(n d) bits of bookkeeping, so the
    amplitude -- and hence the acceptance probability -- is computable in
    polynomial space: that is the proof of BQP subseteq PSPACE.
    """
    steps = [lambda r: r.h(0), lambda r: r.cx(0, 1), lambda r: r.h(2),
             lambda r: r.cz(1, 2), lambda r: r.t(0)]
    mats = [_full_matrix(n, f) for f in steps]

    reg = Register(n)
    for f in steps:
        f(reg)
    statevector = reg.state

    dim = 2 ** n
    path_sum = np.zeros(dim, dtype=complex)
    for y in range(dim):
        total = 0j
        for mids in itertools.product(range(dim), repeat=len(steps) - 1):
            idx = (0,) + mids + (y,)
            term = 1.0 + 0j
            for k, M in enumerate(mats):
                term *= M[idx[k + 1], idx[k]]
                if term == 0:
                    break
            total += term
        path_sum[y] = total
    assert np.allclose(path_sum, statevector), "path sum must reproduce the statevector"

    # The endianness check the course demands of any borrowed quantum exercise
    # [S17]: read the SAME amplitude under the reversed (Qiskit) bit order and
    # confirm it is a different number, so the convention is not cosmetic here.
    reversed_order = np.array([statevector[int(format(i, f"0{n}b")[::-1], 2)]
                               for i in range(dim)])
    assert not np.allclose(reversed_order, statevector), \
        "this circuit was chosen so that bit order visibly matters"
    amp_011 = complex(reg.amplitude("011"))
    return {"paths summed per output": dim ** (len(steps) - 1),
            "outputs": dim,
            "matches statevector": True,
            "amplitude of |011> (course order, qubit 0 = MSB)": amp_011,
            "same index read in Qiskit order": complex(reg.amplitude("110")),
            "workspace": "one path index + one running product = O(n d) bits"}


def solve():
    return {"pt1": pt1_polynomial_hierarchy(),
            "pt2_counting": pt2_shannon_counting(),
            "pt2_ppoly": pt2_ppoly_contains_undecidable(),
            "pt3": pt3_adleman(),
            "pt4": pt4_path_sum()}


if __name__ == "__main__":
    for key, value in solve().items():
        print(key, "->", value)
