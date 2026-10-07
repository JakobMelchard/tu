"""Tests for dh.py (note 10).  The exchange runs over RFC 3526 group 14 [S26]
and is cross-checked against the `cryptography` package's Diffie-Hellman,
which is OpenSSL's: same private values, same shared value, byte for byte.
`cryptography` 50 deprecates finite-field DH (it warns on every use); the
warning is silenced here, and the cross-check will need replacing once the
library drops FFDH."""
import pytest
from cryptography.hazmat.primitives.asymmetric import dh as libdh

import dh
from numtheory import modexp

GROUP = dh.rfc3526_group14()
pytestmark = pytest.mark.filterwarnings("ignore:Diffie-Hellman over finite fields")


def _lib_private(x: int):
    numbers = libdh.DHParameterNumbers(GROUP.p, GROUP.g, GROUP.q)
    y = modexp(GROUP.g, x, GROUP.p)
    return libdh.DHPrivateNumbers(x, libdh.DHPublicNumbers(y, numbers)).private_key()


def test_shared_value_matches_openssl():
    a, A = dh.keypair(GROUP)
    b, B = dh.keypair(GROUP)
    ours = dh.shared_value(GROUP, a, B)
    lib = _lib_private(a).exchange(_lib_private(b).public_key())
    assert ours == lib.rjust(len(ours), b"\x00")
    assert dh.shared_secret(GROUP, a, B) == dh.shared_secret(GROUP, b, A)


def test_library_public_key_is_ours():
    x, X = dh.keypair(GROUP)
    assert _lib_private(x).public_key().public_numbers().y == X


def test_public_keys_in_subgroup():
    _, A = dh.keypair(GROUP)
    assert modexp(A, GROUP.q, GROUP.p) == 1        # order divides q


def test_degenerate_public_values_rejected():
    """y = 1 or p-1 would force the shared value into {1, p-1}."""
    x, _ = dh.keypair(GROUP)
    for bad in (0, 1, GROUP.p - 1, GROUP.p):
        with pytest.raises(ValueError):
            dh.shared_value(GROUP, x, bad)


def test_small_generated_group_also_agrees():
    params = dh.DHParams(bits=64)
    a, A = dh.keypair(params)
    b, B = dh.keypair(params)
    assert dh.shared_secret(params, a, B) == dh.shared_secret(params, b, A)


def test_mitm_breaks_agreement():
    keys = dh.mitm_demo(GROUP)
    assert keys["alice"] == keys["attacker_alice"]
    assert keys["bob"] == keys["attacker_bob"]
    assert keys["alice"] != keys["bob"]
