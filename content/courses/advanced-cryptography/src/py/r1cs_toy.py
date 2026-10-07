"""From an arithmetic circuit to R1CS to a quadratic arithmetic program (QAP),
and the Groth16 prover/verifier equations evaluated *in the clear* over F_p.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). The field has
97 elements. The 'Groth16' part checks the verification equation of [S18
sec. 3.2] on field elements instead of pairing-group elements, so it has NO
hiding and NO soundness (the verifier holds alpha, beta, ...): it shows the
algebra of the scheme, nothing more. QAP construction: [S18 sec. 2.3], [S32].

Example statement (public out, secret x):  x^3 + 2x + 7 = out.
"""
from __future__ import annotations

import secrets

P = 97

# --- polynomials over F_p, coefficient lists low -> high ---------------------


def _trim(a):
    while a and a[-1] % P == 0:
        a = a[:-1]
    return a


def padd(a, b):
    n = max(len(a), len(b))
    return _trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % P for i in range(n)])


def pscale(a, k):
    return _trim([x * k % P for x in a])


def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1) if a and b else []
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % P
    return _trim(out)


def pdivmod(a, b):
    a, b = _trim(list(a)), _trim(list(b))
    q = [0] * max(len(a) - len(b) + 1, 0)
    inv = pow(b[-1], -1, P)
    while len(a) >= len(b) and a:
        k = a[-1] * inv % P
        d = len(a) - len(b)
        q[d] = k
        a = padd(a, pscale([0] * d + b, -k))
    return _trim(q), a


def peval(a, x):
    acc = 0
    for c in reversed(a):
        acc = (acc * x + c) % P
    return acc


def lagrange(xs, ys):
    """The unique polynomial of degree < len(xs) through (xs[i], ys[i])."""
    out = []
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        num, den = [1], 1
        for j, xj in enumerate(xs):
            if j != i:
                num = pmul(num, [-xj % P, 1])
                den = den * (xi - xj) % P
        out = padd(out, pscale(num, yi * pow(den, -1, P)))
    return out


# --- circuit -> R1CS -----------------------------------------------------------
# Variables z = (1, out, x, v1, v2); z[0] = 1, z[1..ELL] public, rest witness.
VARS = ["one", "out", "x", "v1", "v2"]
ELL = 1
# Each constraint <A_q, z> * <B_q, z> = <C_q, z>, as sparse {var: coeff}.
CONSTRAINTS = [
    ({"x": 1}, {"x": 1}, {"v1": 1}),                        # v1 = x * x
    ({"v1": 1}, {"x": 1}, {"v2": 1}),                       # v2 = v1 * x
    ({"v2": 1, "x": 2, "one": 7}, {"one": 1}, {"out": 1}),  # (v2 + 2x + 7) * 1 = out
]


def matrices(constraints=CONSTRAINTS, names=VARS):
    idx = {v: i for i, v in enumerate(names)}
    mats = []
    for k in range(3):
        M = [[0] * len(names) for _ in constraints]
        for q, con in enumerate(constraints):
            for v, c in con[k].items():
                M[q][idx[v]] = c % P
        mats.append(M)
    return mats  # A, B, C


def witness(x: int):
    """Forward evaluation of the circuit: the full assignment z."""
    v1 = x * x % P
    v2 = v1 * x % P
    return [1, (v2 + 2 * x + 7) % P, x % P, v1, v2]


def dot(row, z):
    return sum(a * b for a, b in zip(row, z)) % P


def r1cs_satisfied(z, mats=None) -> bool:
    A, B, C = mats or matrices()
    return all(dot(a, z) * dot(b, z) % P == dot(c, z) for a, b, c in zip(A, B, C))


# --- R1CS -> QAP [S18 sec. 2.3] ------------------------------------------------

def qap(mats=None):
    """Column i of A, B, C becomes u_i, v_i, w_i: interpolate over the points
    r_q = 1..n (one per constraint); t(X) = prod (X - r_q)."""
    A, B, C = mats or matrices()
    n, m = len(A), len(A[0])
    rs = list(range(1, n + 1))
    u = [lagrange(rs, [A[q][i] for q in range(n)]) for i in range(m)]
    v = [lagrange(rs, [B[q][i] for q in range(n)]) for i in range(m)]
    w = [lagrange(rs, [C[q][i] for q in range(n)]) for i in range(m)]
    t = [1]
    for r in rs:
        t = pmul(t, [-r % P, 1])
    return u, v, w, t


def combine(polys, z):
    out = []
    for poly, zi in zip(polys, z):
        out = padd(out, pscale(poly, zi))
    return out


def qap_quotient(z, Q=None):
    """h(X) with A(X)B(X) - C(X) = h(X) t(X); remainder 0 iff z satisfies."""
    u, v, w, t = Q or qap()
    Az, Bz, Cz = combine(u, z), combine(v, z), combine(w, z)
    return pdivmod(padd(pmul(Az, Bz), pscale(Cz, -1)), t)


# --- Groth16 equations in the clear [S18 sec. 3.2] -----------------------------

def _rand_nonzero():
    return 1 + secrets.randbelow(P - 1)


def setup(Q=None):
    """Toxic waste tau = (alpha, beta, gamma, delta, x). Real Groth16 publishes
    only [.]_1, [.]_2 encodings of the CRS terms and deletes tau."""
    return {k: _rand_nonzero() for k in ("alpha", "beta", "gamma", "delta", "x")}


def _k(i, td, Q):
    """beta u_i(x) + alpha v_i(x) + w_i(x)."""
    u, v, w, _ = Q
    x = td["x"]
    return (td["beta"] * peval(u[i], x) + td["alpha"] * peval(v[i], x) + peval(w[i], x)) % P


def prove(td, z, Q=None):
    Q = Q or qap()
    u, v, w, t = Q
    x, d = td["x"], td["delta"]
    h, rem = qap_quotient(z, Q)
    assert not rem, "witness does not satisfy the QAP"
    r, s = secrets.randbelow(P), secrets.randbelow(P)
    A = (td["alpha"] + sum(zi * peval(u[i], x) for i, zi in enumerate(z)) + r * d) % P
    B = (td["beta"] + sum(zi * peval(v[i], x) for i, zi in enumerate(z)) + s * d) % P
    priv = sum(z[i] * _k(i, td, Q) for i in range(ELL + 1, len(z)))
    C = ((priv + peval(h, x) * peval(t, x)) * pow(d, -1, P) + A * s + B * r - r * s * d) % P
    return A, B, C


def verify(td, public, proof, Q=None) -> bool:
    """A * B = alpha beta + (sum_{i<=ell} a_i K_i / gamma) gamma + C delta."""
    Q = Q or qap()
    A, B, C = proof
    a = [1] + list(public)
    pub = sum(a[i] * _k(i, td, Q) for i in range(ELL + 1)) * pow(td["gamma"], -1, P)
    return A * B % P == (td["alpha"] * td["beta"] + pub * td["gamma"] + C * td["delta"]) % P


def simulate(td, public, Q=None):
    """Sim with the trapdoor: random A, B, solve for C. Works for FALSE
    statements too: whoever keeps tau can prove anything."""
    Q = Q or qap()
    A, B = _rand_nonzero(), _rand_nonzero()
    a = [1] + list(public)
    pub = sum(a[i] * _k(i, td, Q) for i in range(ELL + 1))
    return A, B, (A * B - td["alpha"] * td["beta"] - pub) * pow(td["delta"], -1, P) % P


if __name__ == "__main__":
    z = witness(3)
    A, B, C = matrices()
    print("z =", dict(zip(VARS, z)), " R1CS ok:", r1cs_satisfied(z))
    for name, M in zip("ABC", (A, B, C)):
        print(f"{name} =", M)
    u, v, w, t = qap()
    print("t(X) =", t, " u_x(X) =", u[2])
    h, rem = qap_quotient(z)
    print("h(X) =", h, " remainder =", rem)
    bad = z[:]
    bad[3] = (bad[3] + 1) % P
    print("tampered v1: R1CS ok:", r1cs_satisfied(bad), " remainder =", qap_quotient(bad)[1])
    td = setup()
    while _k(1, td, qap()) == 0:  # x hit a root of w_out: a 2/96 event in F_97
        td = setup()
    pf = prove(td, z)
    print("Groth16 (in the clear) verifies for out = 40:", verify(td, [40], pf),
          "| for out = 41:", verify(td, [41], pf))
    print("simulated proof of the FALSE out = 41 verifies:", verify(td, [41], simulate(td, [41])))
