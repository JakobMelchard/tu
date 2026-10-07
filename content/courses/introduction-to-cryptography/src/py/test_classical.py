"""Tests for the lecture-1 historical ciphers.

The Caesar/Vigenere frequency-analysis contrast is midterm 3 Dec 2025
question 1b [S13].
"""
from __future__ import annotations

import pytest

import classical as cl
from classical import SAMPLE


def test_known_answers():
    """No standard exists for these ciphers, so the checks are textbook
    known answers: Caesar (k = 3) maps HELLO to KHOOR, the Vigenere key LEMON
    maps ATTACKATDAWN to LXFOPVEFRNHR, and the Scytale with k = 3 rows reads
    ABCD/EFGH/IJKL by columns, which is note 01's formula
    (m_1, m_{n/k+1}, m_{2n/k+1}, m_2, ...)."""
    assert cl.shift_encrypt("HELLO", 3) == "KHOOR"
    lemon = cl.vigenere_key_to_perms("LEMON")
    assert cl.poly_encrypt("ATTACKATDAWN", lemon) == "LXFOPVEFRNHR"
    ct = cl.scytale_encrypt("ABCDEFGHIJKL", 3)
    assert ct == "AEIBFJCGKDHL"
    assert ct[:3] == "ABCDEFGHIJKL"[0] + "ABCDEFGHIJKL"[4] + "ABCDEFGHIJKL"[8]


def test_scytale_is_a_transposition():
    ct = cl.scytale_encrypt(SAMPLE[:60], 5)
    assert cl.scytale_decrypt(ct, 5) == SAMPLE[:60]
    assert sorted(ct) == sorted(SAMPLE[:60])      # multiset of letters unchanged
    assert ct != SAMPLE[:60]


def test_scytale_key_space_is_tiny():
    msg = SAMPLE[:60]
    ct = cl.scytale_encrypt(msg, 5)
    assert cl.scytale_break(ct, lambda t: t == msg) == 5


def test_shift_brute_force_enumerates_the_whole_key_space():
    ct = cl.shift_encrypt(SAMPLE[:200], 11)
    cands = cl.shift_brute_force(ct)
    assert len(cands) == 26
    assert (11, cl.to_text(cl.to_nums(SAMPLE[:200]))) in cands


def test_shift_frequency_analysis_needs_no_human():
    for k in (0, 3, 13, 25):
        assert cl.shift_break_by_frequency(cl.shift_encrypt(SAMPLE, k)) == k


def test_substitution_roundtrip():
    perm = cl.random_substitution()
    ct = cl.substitution_encrypt(SAMPLE, perm)
    assert cl.substitution_decrypt(ct, perm) == cl.to_text(cl.to_nums(SAMPLE))


def test_substitution_leaks_its_frequency_profile():
    """Midterm 3 Dec 2025, question 1b [S13]: a monoalphabetic cipher is a
    permutation of the alphabet, so the *sorted* frequency profile of the
    ciphertext equals that of the plaintext.  The distribution is carried
    over intact; only its labelling is hidden."""
    perm = cl.random_substitution()
    ct = cl.substitution_encrypt(SAMPLE, perm)
    assert sorted(cl.frequency_profile(ct)) == sorted(cl.frequency_profile(SAMPLE))


def test_substitution_frequency_attack_beats_chance():
    """Ranking by unigram frequency does not hand over the whole key, but it
    puts the true image of E in the top few candidates -- far better than
    the 1/26 a blind guess gives, which is all the definition of 'broken'
    requires."""
    perm = cl.random_substitution()
    guess = cl.substitution_break_by_frequency(cl.substitution_encrypt(SAMPLE, perm))
    assert sorted(guess) == list(range(26))       # still a permutation
    ct_rank = [i for i, _ in sorted(enumerate(
        cl.frequency_profile(cl.substitution_encrypt(SAMPLE, perm))),
        key=lambda t: -t[1])]
    assert perm[ord("E") - cl.A] in ct_rank[:3]


def test_vigenere_defeats_naive_frequency_analysis():
    """Midterm 3 Dec 2025, question 1b [S13] asks whether polyalphabetic
    ciphers are *immune* to frequency analysis.  They are not: the whole
    ciphertext looks flat, but each residue class mod L is a plain shift
    cipher and falls to the same attack."""
    key = "CRYPTO"
    perms = cl.vigenere_key_to_perms(key)
    ct = cl.poly_encrypt(SAMPLE, perms)
    nums = cl.to_nums(ct)
    recovered = []
    for j in range(len(key)):
        slice_text = cl.to_text(nums[j::len(key)])
        recovered.append(cl.shift_break_by_frequency(slice_text))
    assert cl.to_text(recovered) == key


def test_vernam_ciphertext_is_uniform_for_a_fixed_message():
    """For a fixed one-letter message every ciphertext letter occurs with
    probability 1/26, so the ciphertext carries no information about m."""
    from collections import Counter
    trials = 26 * 400
    counts = Counter(cl.vernam_encrypt("A", cl.vernam_keygen(1)) for _ in range(trials))
    assert len(counts) == 26
    expected = trials / 26
    assert all(0.7 * expected < c < 1.3 * expected for c in counts.values())


def test_vernam_needs_a_fresh_key():
    """Reuse and the key cancels, exactly as for the binary one-time pad:
    c1 - c2 = m1 - m2 mod 26, with no key involved."""
    key = cl.vernam_keygen(5)
    c1 = cl.to_nums(cl.vernam_encrypt("HELLO", key))
    c2 = cl.to_nums(cl.vernam_encrypt("WORLD", key))
    diff = [(a - b) % 26 for a, b in zip(c1, c2)]
    m_diff = [(a - b) % 26 for a, b in zip(cl.to_nums("HELLO"), cl.to_nums("WORLD"))]
    assert diff == m_diff


def test_decryption_inverts_every_cipher():
    plain = cl.to_text(cl.to_nums(SAMPLE[:80]))
    assert cl.shift_decrypt(cl.shift_encrypt(plain, 11), 11) == plain
    perms = [cl.random_substitution() for _ in range(3)]
    assert cl.poly_decrypt(cl.poly_encrypt(plain, perms), perms) == plain
    key = cl.vernam_keygen(len(plain))
    assert cl.vernam_decrypt(cl.vernam_encrypt(plain, key), key) == plain


def test_vernam_rejects_a_short_key():
    for f in (cl.vernam_encrypt, cl.vernam_decrypt):
        with pytest.raises(ValueError):
            f("HELLO", [1, 2])
