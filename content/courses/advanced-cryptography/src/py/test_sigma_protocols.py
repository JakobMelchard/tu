"""Tests for the educational toy code in sigma_protocols.py. The TINY group (q = 11) is small enough to
compare real and simulated transcript *distributions* exactly."""
from collections import Counter

import sigma_protocols as S
from groups import MEDIUM, TINY, TOY
from sigma_protocols import Transcript


def test_completeness():
    for G in (TINY, TOY, MEDIUM):
        x = G.rand_scalar()
        assert S.schnorr_check(G, G.exp(G.g, x), S.schnorr_run(G, x))


def test_hvzk_exact_distribution():
    """Real transcripts over all (r, c) and simulated over all (c, s) are the
    same multiset: the uniform distribution on accepting transcripts."""
    G = TINY
    for x in range(G.q):
        y = G.exp(G.g, x)
        real = Counter()
        for r in range(G.q):
            for c in range(G.q):
                _, t = S.schnorr_commit(G, r)
                real[Transcript(t, c, S.schnorr_respond(G, x, r, c))] += 1
        sim = Counter(S.schnorr_simulate(G, y, c, s) for c in range(G.q) for s in range(G.q))
        assert real == sim and len(real) == G.q ** 2
        assert all(S.schnorr_check(G, y, tr) for tr in sim)


def test_special_soundness_every_commitment():
    """For every t, any two accepting answers to distinct challenges give x."""
    G = TINY
    x = 7
    y = G.exp(G.g, x)
    for r in range(G.q):
        _, t = S.schnorr_commit(G, r)
        for c1 in range(G.q):
            for c2 in range(c1 + 1, G.q):
                tr1 = Transcript(t, c1, S.schnorr_respond(G, x, r, c1))
                tr2 = Transcript(t, c2, S.schnorr_respond(G, x, r, c2))
                assert S.schnorr_check(G, y, tr1) and S.schnorr_check(G, y, tr2)
                assert S.schnorr_extract(G, tr1, tr2) == x


def test_soundness_error_one_over_q():
    """Without x, a fixed t can be answered for exactly one c per s: a prover
    committed to t survives a random challenge w.p. 1/q unless it knows x."""
    G = TOY
    y = G.exp(G.g, G.rand_scalar())
    t = G.exp(G.g, 123)  # prover committed; pretend it now tries one response
    s = 456
    ok = [c for c in range(G.q) if S.schnorr_check(G, y, Transcript(t, c, s))]
    assert len(ok) <= 1


def test_fiat_shamir_signature():
    G = MEDIUM
    x = G.rand_scalar()
    y = G.exp(G.g, x)
    pr = S.fs_prove(G, x, "msg")
    assert S.fs_verify(G, y, pr, "msg")
    assert not S.fs_verify(G, y, pr, "other")
    assert not S.fs_verify(G, G.mul(y, G.g), pr, "msg")


def test_weak_fiat_shamir_is_unsound_for_adaptive_statements():
    for G in (TOY, MEDIUM):
        y, pr = S.weak_fs_forge(G, "m")
        assert G.is_member(y)
        assert S.fs_verify(G, y, pr, "m", strong=False)   # accepted
        assert not S.fs_verify(G, y, pr, "m", strong=True)


def test_chaum_pedersen():
    G = MEDIUM
    x, a = G.rand_scalar(), G.rand_scalar()
    u = G.exp(G.g, a)
    v, w = G.exp(G.g, x), G.exp(u, x)
    t, c, s = S.cp_prove(G, x, u)
    assert S.cp_check(G, u, v, w, t, c, s)
    assert not S.cp_check(G, u, v, G.mul(w, G.g), t, c, s)   # not a DH tuple


def test_or_proof_completeness_and_extraction():
    G = MEDIUM
    xs = [G.rand_scalar(), G.rand_scalar()]
    ys = tuple(G.exp(G.g, x) for x in xs)
    for b in (0, 1):
        run = S.or_prove(G, ys, b, xs[b])
        assert S.or_check(G, ys, *run)
        coins = (G.rand_scalar(), G.rand_scalar(), G.rand_scalar())
        run1 = S.or_prove(G, ys, b, xs[b], c=11, coins=coins)
        run2 = S.or_prove(G, ys, b, xs[b], c=29, coins=coins)
        i, xi = S.or_extract(G, ys, run1, run2)
        assert xi == xs[i] and i == b     # the simulated branch keeps its c
        assert S.or_fs_verify(G, ys, S.or_fs_prove(G, ys, b, xs[b], "m"), "m")


def test_or_proof_witness_indistinguishable_exact():
    """For fixed challenge c the transcript distribution does not depend on
    which witness the prover used (TINY group, all coins enumerated)."""
    G = TINY
    xs = (3, 8)
    ys = tuple(G.exp(G.g, x) for x in xs)
    c = 5
    dist = []
    for b in (0, 1):
        cnt = Counter()
        for cs in range(G.q):
            for ss in range(G.q):
                for r in range(G.q):
                    ts, _, cc, s = S.or_prove(G, ys, b, xs[b], c=c, coins=(cs, ss, r))
                    cnt[(ts, cc, s)] += 1
        dist.append(cnt)
    assert dist[0] == dist[1]
