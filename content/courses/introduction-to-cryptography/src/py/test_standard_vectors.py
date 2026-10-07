"""Reproduce the published test vectors of the standards the notes cite.

Every constant below is copied from a document vendored in `../../refs`, and
each test names the document and section it comes from.  Reproducing a
specification's own numbers is the strongest check available that both the
reading of the standard and the implementation are right.

  FIPS 197 app. B         [S21]  AES-128 single block, with intermediate values
  SP 800-38A app. F.1/F.2/F.5  [S25]  ECB / CBC / CTR with AES-128
  RFC 6234 sec. 8.5       [S23]  SHA-256 digests
  RFC 4231 sec. 4         [S22]  HMAC-SHA-256 test cases 1-7
  RFC 3526 sec. 3         [S26]  the 2048-bit MODP group used by IKE/TLS

Each block-cipher vector runs twice, on the `cryptography` package's AES
and on `aes.PureAES` (FIPS 197 from scratch), and each SHA-256 vector on
`hashlib` and on `hashing.sha256`, so a pass checks our code and the
library against the standard and against each other.  The appendix A/B
round-key and round-state checks are in test_aes.py; RFC 5869, 6979 and
8439 are parsed from the vendored text (test_mac, test_dsa, test_prg).
"""
from __future__ import annotations

import hashlib

import pytest

import dh
import hashing
import rfc_vectors
from aes import PureAES
from mac import hmac_sha256
from numtheory import miller_rabin, modexp
from private_key import (AESBlock, cbc_decrypt_raw, ctr_keystream_from, xor)

CIPHERS = pytest.mark.parametrize("make", [AESBlock, PureAES], ids=["library", "pure"])


def h(s: str) -> bytes:
    return bytes.fromhex(s)


# The key and the four plaintext blocks shared by every AES example in
# SP 800-38A appendix F.
NIST_KEY128 = h("2b7e151628aed2a6abf7158809cf4f3c")
NIST_PLAIN = [h("6bc1bee22e409f96e93d7e117393172a"),
              h("ae2d8a571e03ac9c9eb76fac45af8e51"),
              h("30c81c46a35ce411e5fbc1191a0a52ef"),
              h("f69f2445df4f9b17ad2b417be66c3710")]


# ------------------------------------------------------------ AES, FIPS 197
@CIPHERS
def test_fips197_appendix_b_cipher_example(make):
    """FIPS 197 appendix B [S21]: the worked AES-128 encryption whose
    round-by-round state array the standard prints.  Input and key are the
    famous 3243f6a8... / 2b7e1516... pair; the final state read column-major
    is the ciphertext."""
    cipher = make(h("2b7e151628aed2a6abf7158809cf4f3c"))
    ct = cipher.encrypt_block(h("3243f6a8885a308d313198a2e0370734"))
    assert ct.hex() == "3925841d02dc09fbdc118597196a0b32"
    assert cipher.decrypt_block(ct) == h("3243f6a8885a308d313198a2e0370734")


def test_aes_is_a_permutation_not_a_random_function():
    """AES is a keyed *permutation* (note 05): distinct inputs give distinct
    outputs under a fixed key, unlike a random function."""
    cipher = AESBlock(NIST_KEY128)
    cts = [cipher.encrypt_block(p) for p in NIST_PLAIN]
    assert len(set(cts)) == len(cts)


# ------------------------------------------------- modes, SP 800-38A app. F
@CIPHERS
def test_sp800_38a_f1_ecb_aes128(make):
    """SP 800-38A F.1.1/F.1.2 [S25].  ECB encrypts each block independently,
    which is exactly why it is not CPA-secure."""
    expected = ["3ad77bb40d7a3660a89ecaf32466ef97",
                "f5d3d58503b9699de785895a96fdbaaf",
                "43b1cd7f598ece23881b00e3ed030688",
                "7b0c785e27e8ad3f8223207104725dd4"]
    cipher = make(NIST_KEY128)
    for plain, want in zip(NIST_PLAIN, expected):
        ct = cipher.encrypt_block(plain)
        assert ct.hex() == want
        assert cipher.decrypt_block(ct) == plain


@CIPHERS
def test_sp800_38a_f2_cbc_aes128(make):
    """SP 800-38A F.2.1/F.2.2 [S25]: c_i = E_k(m_i xor c_{i-1}), c_0 = IV."""
    iv = h("000102030405060708090a0b0c0d0e0f")
    expected = ["7649abac8119b246cee98e9b12e9197d",
                "5086cb9b507219ee95db113a917678b2",
                "73bed6b8e3c1743b7116e69e22229516",
                "3ff1caa1681fac09120eca307586e1a7"]
    cipher = make(NIST_KEY128)
    prev = iv
    produced = []
    for plain in NIST_PLAIN:
        prev = cipher.encrypt_block(xor(plain, prev))
        produced.append(prev)
    assert [c.hex() for c in produced] == expected
    # and decrypting the whole chain returns the plaintext
    assert cbc_decrypt_raw(cipher, iv + b"".join(produced)) == b"".join(NIST_PLAIN)


@CIPHERS
def test_sp800_38a_f5_ctr_aes128(make):
    """SP 800-38A F.5.1 [S25].  Initial counter f0f1..feff, incremented over
    the whole 128-bit block, so block 2's input is ...fdff00: the carry
    crosses what a nonce||counter implementation would treat as the nonce.
    This is the test that `ctr_keystream_from` exists for."""
    init = h("f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff")
    keystream = ["ec8cdf7398607cb0f2d21675ea9ea1e4",
                 "362b7c3c6773516318a077d7fc5073ae",
                 "6a2cc3787889374fbeb4c81b17ba6c44",
                 "e89c399ff0f198c6d40a31db156cabfe"]
    ciphertext = ["874d6191b620e3261bef6864990db6ce",
                  "9806f66b7970fdff8617187bb9fffdff",
                  "5ae4df3edbd5d35e5b4f09020db03eab",
                  "1e031dda2fbe03d1792170a0f3009cee"]
    ks = ctr_keystream_from(make(NIST_KEY128), init, 4)
    assert ks.hex() == "".join(keystream)
    assert xor(b"".join(NIST_PLAIN), ks).hex() == "".join(ciphertext)


# ------------------------------------------------------- SHA-256, RFC 6234
@pytest.mark.parametrize("msg,repeat,digest", [
    (b"abc", 1,
     "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", 1,
     "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
    (b"a", 1000000,
     "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"),
    (b"01234567012345670123456701234567" * 2, 10,
     "594847328451bdfa85056225462cc1d867d877fb388df0ce35f25ab5562bfbb5"),
])
def test_rfc6234_sha256_vectors(msg, repeat, digest):
    """RFC 6234 sec. 8.5 [S23], the four SHA-256 test patterns, through the
    library and through the FIPS 180-4 implementation in hashing.py."""
    assert hashlib.sha256(msg * repeat).hexdigest() == digest
    assert hashing.sha256(msg * repeat).hex() == digest


def test_sha256_empty_string():
    """The digest of the empty string, quoted in countless places and worth
    recognising on sight."""
    assert hashlib.sha256(b"").hexdigest() == hashing.sha256(b"").hex() == \
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


# --------------------------------------------------------- HMAC, RFC 4231
RFC4231 = [
    # (test case, key, data, HMAC-SHA-256)
    (1, h("0b" * 20), b"Hi There",
     "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"),
    (2, b"Jefe", b"what do ya want for nothing?",
     "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"),
    (3, h("aa" * 20), h("dd" * 50),
     "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe"),
    (4, h("0102030405060708090a0b0c0d0e0f10111213141516171819"), h("cd" * 50),
     "82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b"),
    (6, h("aa" * 131), b"Test Using Larger Than Block-Size Key - Hash Key First",
     "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"),
    (7, h("aa" * 131),
     b"This is a test using a larger than block-size key and a larger than "
     b"block-size data. The key needs to be hashed before being used by the "
     b"HMAC algorithm.",
     "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2"),
]


@pytest.mark.parametrize("tc,key,data,tag", RFC4231,
                         ids=[f"rfc4231-tc{c[0]}" for c in RFC4231])
def test_rfc4231_hmac_sha256(tc, key, data, tag):
    """RFC 4231 sec. 4 [S22].  Our from-scratch HMAC must match the RFC's
    published tags -- including cases 6 and 7, where the 131-octet key is
    longer than SHA-256's 64-octet block and so must be hashed first."""
    assert hmac_sha256(key, data).hex() == tag


def test_rfc4231_tc5_truncated_output():
    """Test case 5 checks HMAC-SHA-256-128, i.e. the tag truncated to its
    leading 128 bits.  Truncation is allowed by RFC 2104 sec. 5 [S19] but
    costs security linearly in the bits dropped."""
    tag = hmac_sha256(h("0c" * 20), b"Test With Truncation")
    assert tag[:16].hex() == "a3b6167473100ee06e0c796c2955552b"


# ------------------------------------------------- DH group, RFC 3526
# RFC 3526 sec. 3, the 2048-bit MODP group (group 14).  p = 2^2048 - 2^1984
# - 1 + 2^64 * (floor(2^1918 pi) + 124476), generator 2.
MODP2048 = int("""
FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
15728E5A 8AACAA68 FFFFFFFF FFFFFFFF""".replace("\n", "").replace(" ", ""), 16)


def test_rfc3526_constants_match_the_vendored_rfc():
    """The prime typed in here and in dh.py is the one the RFC prints."""
    assert rfc_vectors.rfc3526_modp2048() == MODP2048 == dh.MODP2048


def test_rfc3526_group14_is_a_safe_prime_with_generator_2():
    """RFC 3526 sec. 3 [S26].  The group is built so that p and q = (p-1)/2
    are both prime -- a *safe* prime, note 09 -- which is what makes the
    order-q subgroup free of small factors (no Pohlig-Hellman) and makes 2
    a generator of that subgroup rather than of all of Z_p^*."""
    assert MODP2048.bit_length() == 2048
    q = (MODP2048 - 1) // 2
    assert miller_rabin(MODP2048, rounds=8)
    assert miller_rabin(q, rounds=8)
    # 2 has order q, not 2q: it is a quadratic residue, so 2^q = 1.
    assert modexp(2, q, MODP2048) == 1
    assert modexp(2, 2, MODP2048) != 1
