"""Tests for the educational toy code in commitments.py: Pedersen hiding checked exhaustively on the TINY
group, binding via the double-opening reduction, and the inner-product
argument of [S19] for several dimensions."""
from collections import Counter

import pytest

import commitments as C
from groups import MEDIUM, TINY, TOY


def test_pedersen_perfectly_hiding_exact():
    """For every m the commitment is uniform on the group: the distribution
    of C over r does not depend on m (information-theoretic hiding)."""
    G = TINY
    h = C.pedersen_setup(G)
    dists = [Counter(C.pedersen_commit(G, h, m, r)[0] for r in range(G.q)) for m in range(G.q)]
    assert all(d == dists[0] for d in dists)
    assert all(v == 1 for v in dists[0].values()) and len(dists[0]) == G.q


def test_pedersen_open_and_homomorphism():
    G = MEDIUM
    h = C.pedersen_setup(G)
    c1, r1 = C.pedersen_commit(G, h, 5)
    c2, r2 = C.pedersen_commit(G, h, 7)
    assert C.pedersen_open(G, h, c1, 5, r1) and not C.pedersen_open(G, h, c1, 6, r1)
    assert C.pedersen_open(G, h, G.mul(c1, c2), 12, (r1 + r2) % G.q)


def test_binding_break_gives_discrete_log():
    """Anyone with log_g h can equivocate; conversely any double opening
    reveals log_g h. On TOY we brute-force a double opening to show it."""
    G = TOY
    h = C.pedersen_setup(G)
    tau = G.dlog_bruteforce(h)                 # only possible because TOY is tiny
    c, r = C.pedersen_commit(G, h, 1)
    r2 = C.pedersen_equivocate(G, tau, 1, r, 2)
    assert C.pedersen_open(G, h, c, 2, r2)
    assert C.pedersen_dlog_from_double_opening(G, 1, r, 2, r2) == tau


def test_hash_commitment():
    c, r = C.hash_commit(b"bid: 100")
    assert C.hash_commit(b"bid: 100", r)[0] == c
    assert C.hash_commit(b"bid: 101", r)[0] != c


@pytest.mark.parametrize("n", [1, 2, 4, 8, 32])
def test_inner_product_argument(n):
    G = MEDIUM
    g, h, u = C.generators(G, n, "g"), C.generators(G, n, "h"), G.hash_to_group("u")
    a = [G.rand_scalar() for _ in range(n)]
    b = [G.rand_scalar() for _ in range(n)]
    P = C.multiexp(G, g + h, a + b)
    c = C.ip(a, b, G.q)
    pf = C.ipa_relation2_prove(G, g, h, u, P, c, a, b)
    assert len(pf[0]) == len(pf[1]) == n.bit_length() - 1      # log2 n rounds
    assert C.ipa_relation2_verify(G, g, h, u, P, c, pf)
    assert not C.ipa_relation2_verify(G, g, h, u, P, (c + 1) % G.q, pf)
    a_bad = a[:]
    a_bad[0] = (a_bad[0] + 1) % G.q
    pf_bad = C.ipa_relation2_prove(G, g, h, u, P, c, a_bad, b)    # wrong witness
    assert not C.ipa_relation2_verify(G, g, h, u, P, c, pf_bad)


def test_ipa_protocol2_direct():
    G = MEDIUM
    n = 8
    g, h, u = C.generators(G, n, "g2"), C.generators(G, n, "h2"), G.hash_to_group("u2")
    a = list(range(1, n + 1))
    b = list(range(n, 0, -1))
    P = C.multiexp(G, g + h + [u], a + b + [C.ip(a, b, G.q)])
    assert C.ipa_verify(G, g, h, u, P, C.ipa_prove(G, g, h, u, P, a, b))
