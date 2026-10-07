import random
from itertools import combinations

import fd
from fd import fs, parse


def brute_keys(R, F):
    R = sorted(R)
    supers = [fs(c) for k in range(1, len(R) + 1) for c in combinations(R, k)
              if fd.is_superkey(c, fs(R), F)]
    return {s for s in supers if not any(t < s for t in supers)}


def random_fds(rng, attrs, n):
    F = []
    for _ in range(n):
        lhs = rng.sample(attrs, rng.randint(1, 2))
        rhs = rng.choice([a for a in attrs if a not in lhs])
        F.append((fs(lhs), fs(rhs)))
    return F


def test_closure_textbook():
    F = parse("A->B, A->C, CG->H, CG->I, B->H")      # [S6] ch. 7 closure example
    assert fd.closure("AG", F) == fs("ABCGHI")


def test_demo_schema():
    R, F = fs("ABCDE"), parse("A->B, B->C, CD->E, E->A")
    assert set(fd.candidate_keys(R, F)) == {fs("AD"), fs("BD"), fs("CD"), fs("DE")}
    assert fd.normal_form(R, F) == "3NF"             # every attribute is prime
    assert not fd.is_bcnf(R, F)


def test_normal_form_ladder():
    assert fd.normal_form("AB", parse("A->B")) == "BCNF"
    assert fd.normal_form("ABC", parse("A->B, B->C")) == "2NF"      # transitive
    assert fd.normal_form("ABC", parse("AB->C, A->C")) == "1NF"     # partial
    assert fd.normal_form("ABC", parse("AB->C, C->B")) == "3NF"     # classic 3NF-not-BCNF


def test_candidate_keys_match_brute_force():
    rng = random.Random(1)
    attrs = list("ABCDEF")
    for _ in range(200):
        F = random_fds(rng, attrs, rng.randint(1, 6))
        assert set(fd.candidate_keys(fs(attrs), F)) == brute_keys(attrs, F)


def test_minimal_cover_equivalent_and_minimal():
    rng = random.Random(2)
    for _ in range(200):
        F = random_fds(rng, list("ABCDE"), rng.randint(1, 7))
        G = fd.minimal_cover(F)
        assert fd.equivalent(F, G)
        for i, (l, r) in enumerate(G):
            assert len(r) == 1
            assert not fd.implies(G[:i] + G[i + 1:], (l, r))
            for a in l:
                if len(l) > 1:
                    assert not fd.implies(G, (l - {a}, r))


def test_synthesis_and_bcnf_properties():
    rng = random.Random(3)
    attrs = list("ABCDEF")
    R = fs(attrs)
    for _ in range(150):
        F = random_fds(rng, attrs, rng.randint(1, 6))
        s3 = fd.synthesize_3nf(R, F)
        assert set().union(*s3) == R
        assert fd.is_lossless(R, s3, F) and fd.preserves(F, s3)
        assert all(fd.is_3nf(p, fd.project(F, p)) for p in s3)
        b = fd.bcnf_decompose(R, F)
        assert set().union(*b) == R and fd.is_lossless(R, b, F)
        assert all(fd.is_bcnf(p, fd.project(F, p)) for p in b)


def test_binary_lossless_criterion_agrees_with_chase():
    """R1, R2 lossless iff (R1 cap R2) -> R1 or (R1 cap R2) -> R2 ([S6] ch. 7)."""
    rng = random.Random(4)
    attrs = list("ABCDE")
    for _ in range(300):
        F = random_fds(rng, attrs, rng.randint(1, 5))
        R1 = fs(rng.sample(attrs, 3))
        R2 = fs(rng.sample(attrs, 3)) | (fs(attrs) - R1)
        common = R1 & R2
        rule = fd.closure(common, F) >= R1 or fd.closure(common, F) >= R2
        assert fd.is_lossless(fs(attrs), [R1, R2], F) == rule


def test_bcnf_can_lose_dependency():
    R, F = fs("ABC"), parse("AB->C, C->B")
    parts = fd.bcnf_decompose(R, F)
    assert set(parts) == {fs("BC"), fs("AC")}
    assert not fd.preserves(F, parts)                # AB->C spans both parts
    assert fd.synthesize_3nf(R, F) == [fs("ABC")]    # 3NF keeps R as is


def test_preserves_needs_no_projection():
    R, F = fs("ABC"), parse("A->B, B->C, C->A")
    assert fd.preserves(F, [fs("AB"), fs("BC")])     # C->A via C->B->A
