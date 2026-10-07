"""Tests for the educational toy code in r1cs_toy.py: polynomial arithmetic against sympy, R1CS and QAP
satisfaction iff the witness is right, Groth16 equations in the clear."""
import random

import sympy

import r1cs_toy as R


def _sym(coeffs):
    X = sympy.symbols("X")
    return sympy.Poly(list(reversed(coeffs)) or [0], X, modulus=R.P)


def test_poly_ops_against_sympy():
    rng = random.Random(0)
    for _ in range(50):
        a = [rng.randrange(R.P) for _ in range(rng.randrange(1, 6))]
        b = [rng.randrange(R.P) for _ in range(rng.randrange(1, 5))]
        if R._trim(b) == []:
            continue
        assert _sym(R.pmul(a, b)) == _sym(a) * _sym(b)
        q, r = R.pdivmod(a, b)
        sq, sr = sympy.div(_sym(a), _sym(b))
        assert _sym(q) == sq and _sym(r) == sr


def test_lagrange_interpolates():
    xs, ys = [1, 2, 3, 4], [5, 0, 96, 13]
    f = R.lagrange(xs, ys)
    assert [R.peval(f, x) for x in xs] == ys and len(f) <= 4


def test_r1cs_iff_correct_witness():
    for x in range(R.P):
        z = R.witness(x)
        assert R.r1cs_satisfied(z)
        assert z[1] == (x**3 + 2 * x + 7) % R.P
        for k in range(1, len(z)):
            bad = z[:]
            bad[k] = (bad[k] + 1) % R.P
            assert not R.r1cs_satisfied(bad)


def test_qap_divisibility_iff_r1cs():
    Q = R.qap()
    rng = random.Random(1)
    for _ in range(100):
        z = [1] + [rng.randrange(R.P) for _ in range(4)]
        h, rem = R.qap_quotient(z, Q)
        assert (rem == []) == R.r1cs_satisfied(z)
    z = R.witness(3)
    h, rem = R.qap_quotient(z, Q)
    assert rem == [] and len(h) <= len(Q[3]) - 2 + 1   # deg h <= n - 2


def test_qap_columns_reproduce_matrices():
    A, B, C = R.matrices()
    u, v, w, t = R.qap()
    for q in range(len(A)):
        for i in range(len(R.VARS)):
            assert R.peval(u[i], q + 1) == A[q][i]
            assert R.peval(v[i], q + 1) == B[q][i]
            assert R.peval(w[i], q + 1) == C[q][i]
        assert R.peval(t, q + 1) == 0


def test_groth16_in_the_clear():
    Q = R.qap()
    for _ in range(20):
        td = R.setup(Q)
        z = R.witness(3)                      # out = 40
        pf = R.prove(td, z, Q)
        assert R.verify(td, [40], pf, Q)
        # changing out shifts the check by K_out(x) = w_out(x); in F_97 the
        # random x is a root of w_out w.p. <= deg/96 (Schwartz-Zippel): skip
        if R._k(1, td, Q):
            assert not R.verify(td, [41], pf, Q)
        assert R.verify(td, [41], R.simulate(td, [41], Q), Q)   # trapdoor = forge anything
