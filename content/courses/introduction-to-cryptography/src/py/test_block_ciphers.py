"""Tests for lecture 3's block-cipher internals.

`test_sbox_matches_fips197_table_4` is the one that matters: the 256-byte
table below is transcribed from FIPS 197 Table 4 [S21], and the module
derives the same bytes from the *definition* in sec. 5.1.1 without ever
looking at it.  Getting all 256 right is strong evidence that the GF(2^8)
arithmetic and the affine map are both correct.
"""
from __future__ import annotations

import block_ciphers as bc
from private_key import AESBlock

# FIPS 197 Table 4, "SBOX(): substitution values for the byte xy" [S21].
FIPS197_SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]


def test_sbox_matches_fips197_table_4():
    """FIPS 197 Table 4 [S21], all 256 entries, derived from sec. 5.1.1."""
    assert bc.aes_sbox() == FIPS197_SBOX


def test_fips197_worked_sbox_example():
    """FIPS 197 sec. 5.1.1: 'if s_{r,c} = {53} ... the substitution value
    would be ... {ed}'."""
    assert bc.aes_sbox()[0x53] == 0xED


def test_sbox_is_a_bijection_and_inverts():
    sbox, inv = bc.aes_sbox(), bc.aes_inv_sbox()
    assert sorted(sbox) == list(range(256))
    assert all(inv[sbox[a]] == a for a in range(256))


def test_sbox_has_no_fixed_points():
    """A design goal of Rijndael: S(a) != a and S(a) != ~a for every byte."""
    sbox = bc.aes_sbox()
    assert all(sbox[a] != a and sbox[a] != a ^ 0xFF for a in range(256))


def test_sbox_is_public_not_secret():
    """Final exam 31 January 2025, question 1f [S16]: must the S-box be kept
    secret?  No -- Kerckhoffs' principle (lecture 1).  It is printed in the
    standard, and this module reconstructs it from the published formula."""
    assert bc.aes_sbox()[0] == 0x63


def test_gf256_field_arithmetic():
    """FIPS 197 sec. 4.2 gives {57} * {83} = {c1} as its worked example."""
    assert bc.gmul(0x57, 0x83) == 0xC1
    assert bc.xtime(0x57) == 0xAE and bc.xtime(0xAE) == 0x47
    assert all(bc.gmul(a, bc.ginv(a)) == 1 for a in range(1, 256))
    assert bc.ginv(0) == 0


def test_aes_diffuses_a_single_bit_over_the_whole_block():
    """Shannon's diffusion goal: one flipped plaintext bit changes about
    half the ciphertext bits."""
    aes = AESBlock(bytes(range(16)))
    assert 0.45 < bc.avalanche(aes.encrypt_block, bytes(16)) < 0.55


def test_one_round_feistel_barely_diffuses():
    """Final exam 2 February 2021, question 1a [S15]: one round of a Feistel
    network is not EAV-secure, because the left half of the ciphertext is a
    verbatim copy of the right half of the plaintext.  The avalanche is far
    from 1/2, and the explicit distinguisher below always wins."""
    cipher = bc.ToyCipher(0xBEEF)
    cipher.rounds = 1
    assert bc.avalanche(cipher.encrypt_block, bytes(8)) < 0.3
    # the distinguisher: ciphertext[:4] == plaintext[4:]
    m0, m1 = b"AAAABBBB", b"AAAACCCC"
    assert cipher.encrypt_block(m0)[:4] == m0[4:]
    assert cipher.encrypt_block(m1)[:4] == m1[4:]


def test_feistel_is_invertible_with_a_non_invertible_round_function():
    """Midterm 3 Dec 2025 question 1e, and final exam 31 Jan 2025 question
    1j [S13, S16]: yes.  The round function is SHA-256 truncated to 4 bytes,
    which is emphatically not invertible, and the network still inverts."""
    cipher = bc.ToyCipher(0x1234)
    for block in (b"\x00" * 8, b"deadbeef", bytes(range(8))):
        assert cipher.decrypt_block(cipher.encrypt_block(block)) == block


def test_meet_in_the_middle_beats_brute_force_on_double_encryption():
    """Midterm 3 Dec 2025, question 1f [S13]: a meet-in-the-middle attack
    breaks E'_(k,k') = E_k' o E_k in about the square root of the time a
    brute force on E' would take.  With 10-bit keys that is ~2 * 2^10 = 2048
    evaluations against 2^20 = 1048576."""
    bits = 10
    k1, k2 = 0x123, 0x2ab
    p1, p2 = b"knownpt1", b"knownpt2"
    c1 = bc.double_encrypt(k1, k2, p1, bits)
    c2 = bc.double_encrypt(k1, k2, p2, bits)

    cands, work = bc.meet_in_the_middle(p1, c1, bits)
    assert work == 2 * (1 << bits)
    assert work < (1 << (2 * bits)) / 100
    assert (k1, k2) in cands
    # a second known pair filters the false positives the first one leaves
    survivors = [(a, b) for a, b in cands
                 if bc.double_encrypt(a, b, p2, bits) == c2]
    assert survivors == [(k1, k2)]


def test_triple_ede_degenerates_to_single_encryption():
    """3DES with k1 = k2 = k3 is DES, which is how it stayed backwards
    compatible [S27]."""
    block = b"abcdefgh"
    k = 0x0F0F
    assert bc.triple_encrypt_ede(k, k, k, block) == \
        bc.ToyCipher(k).encrypt_block(block)


def test_brute_force_finds_a_single_key():
    bits = 10
    key = 0x2c1
    ct = bc.ToyCipher(key, bits).encrypt_block(b"plaintxt")
    found, work = bc.brute_force(b"plaintxt", ct, bits)
    assert found == key and work <= (1 << bits)
