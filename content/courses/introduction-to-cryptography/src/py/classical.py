"""Historical ciphers and their cryptanalysis -- lecture 1 of the course.

Scytale, shift/Caesar, general monoalphabetic substitution, polyalphabetic
substitution (Vigenere), and the Vernam cipher over Z_26.  Every one of them
is broken here, because the point of the lecture is the contrast: these
schemes were designed by intuition, and each falls to a short, mechanical
attack.  From lecture 2 on, nothing is called secure without a definition
and a proof.

Primitive: classical substitution and transposition ciphers, and their
breaks (exhaustive search, frequency analysis).
Note: notes/01-historical-ciphers.md (lecture 1); the Vernam cipher's
perfect secrecy is notes/02-perfect-secrecy.md.
Standard: none exists; these are the Katz-Lindell sec. 1.1-1.4 schemes [S10] in
the lecture's notation [S8].  The tests check textbook known answers
(Caesar HELLO -> KHOOR) and round trips instead.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
Historical interest only -- none of this is secure against anything.

Alphabet is Sigma = {A..Z} throughout, and messages are upper-case letters
with no spaces, as in the exercise sheets.
"""
from __future__ import annotations

from collections import Counter

import rng

N = 26
A = ord("A")

# Relative letter frequencies of English text, in percent, A..Z.  These are the
# conventional textbook values; no primary corpus was consulted, and none is
# needed -- the attacks below only require the reference distribution to be
# roughly right, because they rank letters rather than match probabilities.
ENGLISH_FREQ = [8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.09, 6.97, 0.15,
                0.77, 4.03, 2.41, 6.75, 7.51, 1.93, 0.10, 5.99, 6.33, 9.06,
                2.76, 0.98, 2.36, 0.15, 1.97, 0.07]


def to_nums(text: str) -> list[int]:
    return [ord(c) - A for c in text.upper() if "A" <= c.upper() <= "Z"]


def to_text(nums: list[int]) -> str:
    return "".join(chr(A + n % N) for n in nums)


# --------------------------------------------------------------- scytale
# Gen: a circumference k, the number of letters once round the rod.  Enc:
# write along the rod, so the message fills k rows of n/k letters; unwinding
# the strip reads the grid column by column:
#     Enc_k(m_1 ... m_n) = (m_1, m_{n/k+1}, m_{2n/k+1}, ..., m_2, m_{n/k+2}, ...)
# (note 01).  A transposition: the multiset of letters is unchanged, which is
# already enough to distinguish it from a substitution cipher.
def scytale_encrypt(msg: str, k: int) -> str:
    if len(msg) % k:
        raise ValueError("message length must be a multiple of k")
    cols = len(msg) // k
    return "".join(msg[r * cols + c] for c in range(cols) for r in range(k))


def scytale_decrypt(ct: str, k: int) -> str:
    """Enc with k rows is Enc with n/k rows run backwards: the transpose of
    a k x (n/k) grid is an (n/k) x k grid."""
    if len(ct) % k:
        raise ValueError("ciphertext length must be a multiple of k")
    return scytale_encrypt(ct, len(ct) // k)


def scytale_break(ct: str, is_plaintext) -> int:
    """Try every circumference dividing the length: at most len(ct) keys."""
    for k in range(1, len(ct) + 1):
        if len(ct) % k == 0 and is_plaintext(scytale_decrypt(ct, k)):
            return k
    raise ValueError("no key found")


# ----------------------------------------------------------- shift cipher
def shift_encrypt(msg: str, k: int) -> str:
    return to_text([(m + k) % N for m in to_nums(msg)])


def shift_decrypt(ct: str, k: int) -> str:
    return shift_encrypt(ct, -k)


def shift_brute_force(ct: str) -> list[tuple[int, str]]:
    """The key space has 26 elements, so exhaustive search is instant.  This
    is the first lesson of the course: a scheme with a small key space is
    broken no matter how clever the transformation."""
    return [(k, shift_decrypt(ct, k)) for k in range(N)]


def shift_break_by_frequency(ct: str) -> int:
    """Pick the shift whose induced letter distribution best matches
    English, by maximising the correlation sum_i f_i * p_{i+k}.  Works on a
    single ciphertext with no crib, unlike brute force which needs a human
    to recognise the plaintext."""
    counts = Counter(to_nums(ct))
    total = max(1, len(to_nums(ct)))
    best, best_score = 0, -1.0
    for k in range(N):
        score = sum(ENGLISH_FREQ[i] * counts[(i + k) % N] / total for i in range(N))
        if score > best_score:
            best, best_score = k, score
    return best


# ------------------------------------------ monoalphabetic substitution
def random_substitution() -> list[int]:
    """Key = a permutation pi of Sigma.  |K| = 26! ~ 2^88, so brute force is
    out -- and yet the cipher is trivially broken, because the key space
    being large is necessary but nowhere near sufficient."""
    perm = list(range(N))
    for i in range(N - 1, 0, -1):
        j = rng.randbelow(i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def substitution_encrypt(msg: str, perm: list[int]) -> str:
    return to_text([perm[m] for m in to_nums(msg)])


def substitution_decrypt(ct: str, perm: list[int]) -> str:
    inv = [0] * N
    for i, p in enumerate(perm):
        inv[p] = i
    return to_text([inv[c] for c in to_nums(ct)])


def frequency_profile(text: str) -> list[float]:
    nums = to_nums(text)
    counts = Counter(nums)
    total = max(1, len(nums))
    return [100.0 * counts[i] / total for i in range(N)]


def substitution_break_by_frequency(ct: str) -> list[int]:
    """Rank ciphertext letters by frequency and match them against the
    English ranking.  On long text this recovers most of the key outright;
    on short text it gives a starting point that a human refines with
    digrams.  Either way the cipher leaks its plaintext's *statistics*,
    which no amount of key-space enlargement repairs.

    Returns a guessed permutation (plaintext letter -> ciphertext letter).
    """
    ct_rank = [i for i, _ in sorted(enumerate(frequency_profile(ct)),
                                    key=lambda t: -t[1])]
    en_rank = [i for i, _ in sorted(enumerate(ENGLISH_FREQ),
                                    key=lambda t: -t[1])]
    guess = [0] * N
    for plain, cipher in zip(en_rank, ct_rank):
        guess[plain] = cipher
    return guess


# ---------------------------------------- polyalphabetic substitution
def poly_encrypt(msg: str, perms: list[list[int]]) -> str:
    """Key = (pi_1, ..., pi_L); position i uses pi_{i mod L}.  Frequency
    analysis on the whole ciphertext is defeated -- but only because it is
    the *wrong* analysis: run it per residue class instead."""
    nums = to_nums(msg)
    return to_text([perms[i % len(perms)][m] for i, m in enumerate(nums)])


def poly_decrypt(ct: str, perms: list[list[int]]) -> str:
    invs = []
    for perm in perms:
        inv = [0] * N
        for i, p in enumerate(perm):
            inv[p] = i
        invs.append(inv)
    nums = to_nums(ct)
    return to_text([invs[i % len(invs)][c] for i, c in enumerate(nums)])


def vigenere_key_to_perms(key: str) -> list[list[int]]:
    """Vigenere is the special case where each pi_j is a *shift*."""
    return [[(x + k) % N for x in range(N)] for k in to_nums(key)]


# -------------------------------------------------------- Vernam over Z_26
def vernam_keygen(length: int) -> list[int]:
    return [rng.randbelow(N) for _ in range(length)]


def vernam_encrypt(msg: str, key: list[int]) -> str:
    """c_i = m_i + k_i mod 26 with a uniform key as long as the message.
    This is the one historical cipher that is *perfectly secret*; see
    notes/02-perfect-secrecy.md."""
    nums = to_nums(msg)
    if len(key) != len(nums):
        raise ValueError("key must be as long as the message")
    return to_text([(m + k) % N for m, k in zip(nums, key)])


def vernam_decrypt(ct: str, key: list[int]) -> str:
    nums = to_nums(ct)
    if len(key) != len(nums):
        raise ValueError("key must be as long as the ciphertext")
    return to_text([(c - k) % N for c, k in zip(nums, key)])


# A sample of ordinary English prose, written here so the demo has a
# realistic letter distribution.  A pangram would not do: frequency
# analysis needs text whose statistics are typical, which is exactly the
# assumption these ciphers rest on and exactly why they fail.
SAMPLE = to_text(to_nums("""
The modern approach to cryptography insists that a scheme is not secure
because nobody has broken it, but because there is a definition of what an
attacker may do and a proof that no efficient attacker can do it. The older
ciphers were not designed that way. They were designed to look confusing,
and looking confusing turns out to be a property of the designer rather
than of the cipher. Once a statistic survives the transformation, the
cipher leaks, and the size of the key space is beside the point. That is
the lesson the first lecture is meant to leave behind before any theorem is
stated at all, and it is worth repeating whenever a new construction looks
too clever to attack.
""" * 4))


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    plain = SAMPLE

    ct = scytale_encrypt(plain[:36], 6)
    print("scytale roundtrip:", scytale_decrypt(ct, 6) == plain[:36],
          "| letters preserved:", sorted(ct) == sorted(plain[:36]))

    ct = shift_encrypt(plain, 7)
    print("shift: brute force gives 26 candidates,",
          "frequency analysis picks k =", shift_break_by_frequency(ct), "(true 7)")

    perm = random_substitution()
    ct = substitution_encrypt(plain, perm)
    guess = substitution_break_by_frequency(ct)
    hits = sum(g == p for g, p in zip(guess, perm))
    e_right = guess[ord("E") - A] == perm[ord("E") - A]
    print(f"substitution: |K| = 26! ~ 2^88, yet unigram frequencies alone pin "
          f"{hits}/26 letters from {len(ct)} characters (E correct: {e_right}); "
          f"digrams finish the job by hand")

    perms = vigenere_key_to_perms("CRYPTO")
    ct = poly_encrypt(plain, perms)
    print("vigenere roundtrip:", poly_decrypt(ct, perms) == to_text(to_nums(plain)))

    key = vernam_keygen(len(to_nums(plain)))
    ct = vernam_encrypt(plain, key)
    print("vernam roundtrip:", vernam_decrypt(ct, key) == to_text(to_nums(plain)),
          "| perfectly secret, key as long as the message")
