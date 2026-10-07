"""Tests for the educational toy code in ec_toy.py. Toy curves are checked against brute force and the
Hasse bound; X25519/Ed25519 against the RFC 7748 / RFC 8032 vectors (read from
the vendored RFC text) and against the `cryptography` package."""
import math
import pathlib
import random
import secrets

import pytest
import sympy
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, x25519 as cx

import ec_toy as E
from ec_toy import INF, Curve

RFC = pathlib.Path(__file__).resolve().parents[2] / "refs" / "rfc"


def _in_rfc(name: str, hexstr: str) -> bool:
    """The vector really is printed in the vendored RFC (whitespace-insensitive)."""
    text = "".join((RFC / name).read_text().split())
    return hexstr in text


def test_bs_example_y2_x3_plus_1_over_f11():
    # [S4 eq. (15.4)]: 12 points, the listed ones, t = 0
    C = Curve(11, 0, 1)
    pts = set(C.points())
    assert len(pts) == 12
    assert {(10, 0), (0, 1), (0, 10), (2, 3), (2, 8), (5, 4), (5, 7),
            (7, 5), (7, 6), (9, 2), (9, 9)} <= pts


@pytest.mark.parametrize("p", [5, 7, 11, 13, 17])
def test_hasse_bound_all_curves(p):
    for a in range(p):
        for b in range(p):
            try:
                C = Curve(p, a, b)
            except ValueError:
                continue
            assert abs(C.order() - (p + 1)) <= 2 * math.sqrt(p)


def test_group_axioms_on_toy_curve():
    C, pts = E.TOY, E.TOY.points()
    rng = random.Random(1)
    for _ in range(200):
        P, Q, R = (rng.choice(pts) for _ in range(3))
        assert C.on_curve(C.add(P, Q))
        assert C.add(P, Q) == C.add(Q, P)
        assert C.add(C.add(P, Q), R) == C.add(P, C.add(Q, R))
        assert C.add(P, INF) == P and C.add(P, C.neg(P)) is INF


def test_toy_curve_prime_order_and_generator():
    assert E.TOY.order() == E.TOY_N and sympy.isprime(E.TOY_N)
    assert E.TOY.mul(E.TOY_N, E.TOY_G) is INF
    assert E.TOY.point_order(E.TOY_G, E.TOY_N) == E.TOY_N


def test_scalar_mult_ladder_and_repeated_addition():
    C, G = E.TOY, E.TOY_G
    acc = INF
    for k in range(60):
        assert C.mul(k, G) == acc == C.ladder(k, G)
        acc = C.add(acc, G)


def test_ecdh_schnorr_ecdsa():
    da, Qa = E.keygen()
    db, Qb = E.keygen()
    assert E.ecdh(da, Qb) == E.ecdh(db, Qa)
    assert E.schnorr_verify(Qa, "m", E.schnorr_sign(da, "m"))
    assert E.ecdsa_verify(Qa, "m", E.ecdsa_sign(da, "m"))
    # rejections on secp256k1: on the toy curve a wrong input still verifies
    # with probability about 1/1013, which would make the test flaky
    C, G, n = E.SECP256K1, E.SECP256K1_G, E.SECP256K1_N
    d1, d2 = 12345678901234567890, 98765432109876543210
    P1, P2 = C.mul(d1, G), C.mul(d2, G)
    sig = E.schnorr_sign(d1, "m", C, G, n)
    assert E.schnorr_verify(P1, "m", sig, C, G, n)
    assert not E.schnorr_verify(P1, "m'", sig, C, G, n)
    assert not E.schnorr_verify(P2, "m", sig, C, G, n)
    sig = E.ecdsa_sign(d1, "m", C, G, n)
    assert E.ecdsa_verify(P1, "m", sig, C, G, n)
    assert not E.ecdsa_verify(P1, "m'", sig, C, G, n)
    assert not E.ecdsa_verify(P2, "m", sig, C, G, n)


def test_ecdsa_nonce_reuse_leaks_key():
    for _ in range(20):
        d, _ = E.keygen()
        k = 1 + secrets.randbelow(E.TOY_N - 1)
        try:
            s1, s2 = E.ecdsa_sign(d, "a", k=k), E.ecdsa_sign(d, "b", k=k)
        except ValueError:
            continue
        if s1[1] != s2[1]:
            assert E.ecdsa_nonce_reuse("a", s1, "b", s2) == d


def test_secp256k1_parameters_and_cryptography_crosscheck():
    C, G, n = E.SECP256K1, E.SECP256K1_G, E.SECP256K1_N
    assert C.on_curve(G) and sympy.isprime(n) and sympy.isprime(C.p)
    assert C.mul(n, G) is INF
    for _ in range(3):
        d = 1 + secrets.randbelow(n - 1)
        pub = ec.derive_private_key(d, ec.SECP256K1()).public_key().public_numbers()
        assert C.mul(d, G) == (pub.x, pub.y)


# RFC 7748 sec. 5.2 (function vectors) and sec. 6.1 (Diffie-Hellman) [S22]
X_VECTORS = [
    ("a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4",
     "e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c",
     "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552"),
    ("4b66e9d4d1b4673c5ad22691957d6af5c11b6421e0ea01d42ca4169e7918ba0d",
     "e5210f12786811d3f4b7959d0538ae2c31dbe7106fc03c3efc4cd549c715a493",
     "95cbde9476e8907d7aade45cb4b873f88b595a68799fa152e6f8f7647aac7957"),
]


@pytest.mark.parametrize("k,u,out", X_VECTORS)
def test_x25519_rfc7748_vectors(k, u, out):
    assert all(_in_rfc("rfc7748.txt", h) for h in (k, u, out))
    assert E.x25519(bytes.fromhex(k), bytes.fromhex(u)).hex() == out


def test_x25519_rfc7748_iterated():
    k = u = (9).to_bytes(32, "little")
    for i in range(1, 1001):
        k, u = E.x25519(k, u), k
        if i == 1:
            assert k.hex() == "422c8e7a6227d7bca1350b3e2bb7279f7897b87bb6854b783c60e80311ae3079"
    target = "684cf59ba83309552800ef566f2f4d3c1c3887c49360e3875f2eb94d99532c51"
    assert _in_rfc("rfc7748.txt", target) and k.hex() == target


def test_x25519_rfc7748_dh_and_cryptography():
    a = bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a")
    b = bytes.fromhex("5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb")
    base = (9).to_bytes(32, "little")
    K = "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742"
    assert _in_rfc("rfc7748.txt", K)
    assert E.x25519(a, E.x25519(b, base)).hex() == K == E.x25519(b, E.x25519(a, base)).hex()
    for _ in range(5):
        sa, sb = secrets.token_bytes(32), secrets.token_bytes(32)
        ka, kb = cx.X25519PrivateKey.from_private_bytes(sa), cx.X25519PrivateKey.from_private_bytes(sb)
        assert E.x25519(sa, base) == ka.public_key().public_bytes_raw()
        assert E.x25519(sa, kb.public_key().public_bytes_raw()) == ka.exchange(kb.public_key())


# RFC 8032 sec. 7.1, TEST 1-3 [S23]
ED_VECTORS = [
    ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
     "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
     "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
    ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
     "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
     "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
    ("c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
     "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025", "af82",
     "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac"
     "18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"),
]


@pytest.mark.parametrize("sk,pk,msg,sig", ED_VECTORS)
def test_ed25519_rfc8032_vectors(sk, pk, msg, sig):
    assert all(_in_rfc("rfc8032.txt", h) for h in (sk, pk, sig))
    sk_b, m = bytes.fromhex(sk), bytes.fromhex(msg)
    assert E.ed25519_public(sk_b).hex() == pk
    assert E.ed25519_sign(sk_b, m).hex() == sig
    assert E.ed25519_verify(bytes.fromhex(pk), m, bytes.fromhex(sig))
    assert not E.ed25519_verify(bytes.fromhex(pk), m + b"x", bytes.fromhex(sig))


def test_ed25519_against_cryptography():
    for _ in range(5):
        sk, m = secrets.token_bytes(32), secrets.token_bytes(40)
        ref = ed25519.Ed25519PrivateKey.from_private_bytes(sk)
        pk = ref.public_key().public_bytes_raw()
        assert E.ed25519_public(sk) == pk
        sig = E.ed25519_sign(sk, m)
        assert sig == ref.sign(m)          # deterministic: byte-identical
        ref.public_key().verify(sig, m)    # raises if invalid


def test_edwards25519_constants_match_rfc7748_sec_4_1():
    assert E.ED_L == 2**252 + 0x14DEF9DEA2F79CD65812631A5CF5D3ED
    assert E.ED_D == 37095705934669439343138083508754565189542113879843219016388785533085940283555
    assert E.ED_B == (15112221349535400772501151409588531511454012693041857206046113283949847762202,
                      46316835694926478169428394003475163141307993866256225615783033603165251855960)
    assert E._ed_mul(E.ED_L, E.ED_B) == (0, 1)          # B has prime order L
