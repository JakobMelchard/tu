"""Tests for elgamal.py (note 10).  The group is RFC 3526 group 14 [S26];
the ElGamal mask h^y is cross-checked against the `cryptography` package's
Diffie-Hellman (OpenSSL), the KEM/DEM key derivation is RFC 5869 HKDF
(checked against its own vectors in test_mac.py), and the IND-CPA claim is
tested where it fails: on messages outside the group."""
import pytest
import sympy
from cryptography.hazmat.primitives.asymmetric import dh as libdh

import dh
import elgamal as eg
import rng
from numtheory import modexp

G14 = eg.ElGamalParams.from_values(dh.MODP2048, 2)
pytestmark = pytest.mark.filterwarnings("ignore:Diffie-Hellman over finite fields")


def _setup(params=G14):
    x, h = eg.keygen(params)
    return params, x, h


def test_mask_matches_openssl_dh():
    """c2 / m = h^y = g^{xy}: exactly the value a DH exchange between the
    key pair (x, h) and the ephemeral pair (y, c1) produces."""
    params, x, h = _setup()
    y = 1 + rng.randbelow(params.q - 1)
    m = eg.encode(params, 20270928)
    c1, c2 = eg.encrypt(params, h, m, y)
    numbers = libdh.DHParameterNumbers(params.p, params.g, params.q)
    lib_y = libdh.DHPrivateNumbers(y, libdh.DHPublicNumbers(c1, numbers)).private_key()
    shared = lib_y.exchange(libdh.DHPublicNumbers(h, numbers).public_key())
    assert c2 * pow(m, -1, params.p) % params.p == int.from_bytes(shared, "big")
    assert eg.decode(params, eg.decrypt(params, x, (c1, c2))) == 20270928


def test_roundtrip_and_randomised():
    params, x, h = _setup()
    m = eg.encode(params, 12345)
    ct = eg.encrypt(params, h, m)
    assert eg.decrypt(params, x, ct) == m
    assert eg.encrypt(params, h, m) != eg.encrypt(params, h, m)


def test_encoding_lands_in_the_group_and_inverts():
    params = eg.ElGamalParams(64)
    for m in list(range(1, 200)) + [params.q]:
        e = eg.encode(params, m)
        assert eg.is_group_element(params, e) and eg.decode(params, e) == m
        assert eg.is_group_element(params, m) == (sympy.legendre_symbol(m, params.p) == 1)


def test_messages_outside_the_group_break_ind_cpa():
    """Note 10 says 'encrypt m in G'.  Ignore it and the Legendre symbol of
    c2 is that of m, because h^y is a residue: pick m0 a residue, m1 not,
    and the adversary wins every time."""
    params, x, h = _setup(eg.ElGamalParams(64))
    m0 = next(m for m in range(2, 100) if eg.is_group_element(params, m))
    m1 = next(m for m in range(2, 100) if not eg.is_group_element(params, m))
    for _ in range(50):
        b = rng.randbelow(2)
        _, c2 = eg.encrypt(params, h, (m0, m1)[b])
        guess = 0 if modexp(c2, params.q, params.p) == 1 else 1
        assert guess == b


def test_rerandomize_preserves_plaintext():
    params, x, h = _setup()
    m = eg.encode(params, 424242)
    ct = eg.encrypt(params, h, m)
    ct2 = eg.rerandomize(params, h, ct)
    assert ct2 != ct and eg.decrypt(params, x, ct2) == m


def test_multiplicative_malleability():
    params, x, h = _setup()
    m = eg.encode(params, 1000)
    ct3 = eg.malleability_demo(params, eg.encrypt(params, h, m), 7)
    assert eg.decrypt(params, x, ct3) == 7 * m % params.p


def test_hybrid_kem_dem_roundtrip():
    params, x, h = _setup()
    msg = b"hybrid encryption carries arbitrary-length messages"
    ct = eg.hybrid_encrypt(params, h, msg)
    assert eg.is_group_element(params, eg.decrypt(params, x, ct[0]))   # k in G
    assert eg.hybrid_decrypt(params, x, ct) == msg


def test_hybrid_with_malleable_kem_is_not_cca_secure():
    """Final exam, 26 January 2024, question 5b [S12].  The DEM is a
    CCA-secure symmetric scheme and the composition is still broken, because
    the ElGamal KEM is re-randomisable: one oracle query on a ciphertext
    that differs from the challenge but decrypts to the same plaintext."""
    params, x, h = _setup()
    msg = b"the bid is 4200 euro"
    ct = eg.hybrid_encrypt(params, h, msg)
    queried = []

    def oracle(c):
        assert c != ct, "CCA game forbids querying the challenge itself"
        queried.append(c)
        return eg.hybrid_decrypt(params, x, c)

    assert eg.hybrid_cca_attack(params, h, ct, oracle) == msg
    assert len(queried) == 1


def test_dhies_resists_the_same_attack():
    """DHIES/ECIES (lecture 12) binds c1 into the key derivation, so mauling
    c1 changes the DEM key and the authentication tag fails."""
    params, x, h = _setup()
    msg = b"the bid is 4200 euro"
    c1, dem = eg.dhies_encrypt(params, h, msg)
    assert eg.dhies_decrypt(params, x, (c1, dem)) == msg
    mauled = c1 * modexp(params.g, 5, params.p) % params.p
    with pytest.raises(ValueError):
        eg.dhies_decrypt(params, x, (mauled, dem))
