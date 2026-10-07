"""Digital signatures: textbook RSA and its forgeries, RSA-FDH, the
RSASSA-PKCS1-v1_5 hash-and-sign scheme that is actually deployed, Schnorr
identification and its Fiat-Shamir signature, and the two ways a Schnorr
key leaks (special soundness, nonce reuse).

Primitive: EUF-CMA signatures (Katz-Lindell Def. 13.2 [S10]); hash-and-sign;
Sigma protocols and the Fiat-Shamir transform.
Note: notes/11-digital-signatures.md (lectures 12 and 13); DSA and its
deterministic nonces are `dsa.py`.
Standard: `rsassa_pkcs1_v15_sign` / `_verify` are RFC 8017 sec. 8.2 with the
EMSA-PKCS1-v1_5 encoding of sec. 9.2 [S20], cross-checked in both
directions against the `cryptography` package.  RSA-FDH and Schnorr over
Z_p^* are not standardised (FIPS 186-5 [S30] approves EdDSA, Schnorr over
an Edwards curve, instead); they follow lecture 13 [S8] and are checked by
their algebra, including the exam's nonce-reuse question [S16, S15].

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
"Full domain hash" is emulated by hashing counter blocks into Z_n with
SHA-256; the Schnorr groups are toy-sized unless built on RFC 3526.
Do not sign anything real with this.
"""
from __future__ import annotations

import hashlib

import rng
import rsa
from dh import DHParams
from numtheory import modexp, modinv


# ------------------------------------------------- textbook RSA signatures
def rsa_sign_textbook(priv: dict, m: int) -> int:
    """sigma = m^d mod n. No hashing: this is the INSECURE scheme, kept only
    to exhibit the forgeries below."""
    return modexp(m, priv["d"], priv["n"])


def rsa_verify_textbook(pub: dict, m: int, sigma: int) -> bool:
    return modexp(sigma, pub["e"], pub["n"]) == m % pub["n"]


def textbook_forgery(pub: dict) -> tuple[int, int]:
    """No-query existential forgery on textbook RSA: pick any sigma, set
    m = sigma^e mod n.  verify(m, sigma) holds although the signer never
    signed m."""
    sigma = 2 + rng.randbelow(pub["n"] - 2)
    return modexp(sigma, pub["e"], pub["n"]), sigma


def rsa_homomorphic_forgery(pub: dict, m1: int, s1: int, m2: int, s2: int) -> tuple[int, int]:
    """Given signatures on m1, m2 forge one on m1*m2: (s1*s2)^e = m1*m2."""
    return m1 * m2 % pub["n"], s1 * s2 % pub["n"]


# --------------------------------------------------------- RSA-FDH (secure)
def _fdh(m: bytes, n: int) -> int:
    """Full-domain hash: map m into Z_n. Emulated by hashing counter blocks
    and reducing mod n. In the ROM this H behaves as a random oracle, which
    is what the RSA-FDH security proof needs."""
    out = b""
    counter = 0
    while len(out) < (n.bit_length() + 7) // 8 + 16:
        out += hashlib.sha256(m + counter.to_bytes(4, "big")).digest()
        counter += 1
    return int.from_bytes(out, "big") % n


def fdh_sign(priv: dict, m: bytes) -> int:
    """sigma = H(m)^d mod n. Hashing kills the multiplicative structure, so
    the textbook forgery no longer works."""
    return modexp(_fdh(m, priv["n"]), priv["d"], priv["n"])


def fdh_verify(pub: dict, m: bytes, sigma: int) -> bool:
    return modexp(sigma, pub["e"], pub["n"]) == _fdh(m, pub["n"])


# ------------------------------------- RSASSA-PKCS1-v1_5, RFC 8017 sec. 8.2
SHA256_DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")   # sec. 9.2 note 1


def emsa_pkcs1_v15_encode(msg: bytes, em_len: int) -> bytes:
    """RFC 8017 sec. 9.2: EM = 0x00 || 0x01 || PS (0xff...) || 0x00 || T,
    T = DER(DigestInfo(SHA-256, H(m))).  Deterministic hash-and-sign; the
    fixed high-order bytes are what stop the multiplicative forgery."""
    t = SHA256_DIGEST_INFO + hashlib.sha256(msg).digest()
    if em_len < len(t) + 11:
        raise ValueError("intended encoded message length too short")
    return b"\x00\x01" + b"\xff" * (em_len - len(t) - 3) + b"\x00" + t


def rsassa_pkcs1_v15_sign(priv: dict, msg: bytes) -> bytes:
    """Sec. 8.2.1: s = RSASP1(K, OS2IP(EM)), output as k octets."""
    k = (priv["n"].bit_length() + 7) // 8
    em = int.from_bytes(emsa_pkcs1_v15_encode(msg, k), "big")
    return rsa.decrypt_crt(priv, em).to_bytes(k, "big")


def rsassa_pkcs1_v15_verify(pub: dict, msg: bytes, sig: bytes) -> bool:
    """Sec. 8.2.2: re-encode and compare the whole EM.  Parsing EM instead of
    re-encoding it is how Bleichenbacher's e = 3 forgery (2006) got in."""
    k = (pub["n"].bit_length() + 7) // 8
    s = int.from_bytes(sig, "big")
    if len(sig) != k or s >= pub["n"]:
        return False
    return rsa.encrypt(pub, s).to_bytes(k, "big") == emsa_pkcs1_v15_encode(msg, k)


# ----------------------------------------------- Schnorr identification / signature
class SchnorrParams(DHParams):
    """(p, q, g) with g of prime order q: a DH group, as for ElGamal."""


def schnorr_keygen(params: SchnorrParams) -> tuple[int, int]:
    """Secret x in [1, q), public y = g^x. DLP hides x."""
    x = 1 + rng.randbelow(params.q - 1)
    return x, modexp(params.g, x, params.p)


def schnorr_transcript(params: SchnorrParams, x: int, challenge_fn,
                       r: int | None = None) -> tuple[int, int, int]:
    """Sigma protocol (commit, challenge, response):
      P: r random, t = g^r          (commitment)
      V: c random                    (challenge)
      P: s = r + c*x mod q           (response)
    Returns the transcript (t, c, s)."""
    r = r if r is not None else 1 + rng.randbelow(params.q - 1)
    t = modexp(params.g, r, params.p)
    c = challenge_fn(t)
    return t, c, (r + c * x) % params.q


def schnorr_check(params: SchnorrParams, y: int, t: int, c: int, s: int) -> bool:
    """V: accept iff g^s == t * y^c (since g^{r+cx} = g^r (g^x)^c)."""
    return modexp(params.g, s, params.p) == t * modexp(y, c, params.p) % params.p


def schnorr_identify(params: SchnorrParams, x: int, challenge_fn) -> bool:
    """One honest run of the identification protocol; True if V accepts."""
    y = modexp(params.g, x, params.p)
    return schnorr_check(params, y, *schnorr_transcript(params, x, challenge_fn))


def schnorr_extract(params: SchnorrParams, tr1, tr2) -> int:
    """Special soundness: two accepting transcripts (t, c, s), (t, c', s')
    with the same t and c != c' give x = (s - s') / (c - c') mod q."""
    (t1, c1, s1), (t2, c2, s2) = tr1, tr2
    if t1 != t2 or c1 == c2:
        raise ValueError("need the same commitment and different challenges")
    return (s1 - s2) * modinv(c1 - c2, params.q) % params.q


def schnorr_sign(params: SchnorrParams, x: int, msg: bytes,
                 r: int | None = None) -> tuple[int, int]:
    """Fiat-Shamir: replace the verifier's challenge by c = H(t || msg),
    turning the identification scheme into a signature. Returns (c, s).
    Pass `r` only to demonstrate what a repeated nonce does."""
    t, c, s = schnorr_transcript(params, x, lambda t: _hash_challenge(params, t, msg), r)
    return c, s


def schnorr_verify(params: SchnorrParams, y: int, msg: bytes, sig: tuple[int, int]) -> bool:
    """Recompute t' = g^s * y^{-c} and check c == H(t' || msg)."""
    c, s = sig
    t = modexp(params.g, s, params.p) * modexp(y, -c, params.p) % params.p
    return c == _hash_challenge(params, t, msg)


def schnorr_nonce_reuse_attack(params: SchnorrParams, sig1, sig2) -> int:
    """Final exam 31 Jan 2025 q5b and 2 Feb 2021 q6b [S16, S15]: two
    signatures (c1, s1), (c2, s2) made with the same nonce r satisfy
    s1 - s2 = (c1 - c2) x, so x = (s1 - s2)(c1 - c2)^-1 mod q.  It is
    `schnorr_extract` with the challenges supplied by the hash."""
    (c1, s1), (c2, s2) = sig1, sig2
    return (s1 - s2) * modinv(c1 - c2, params.q) % params.q


def _hash_challenge(params: SchnorrParams, t: int, msg: bytes) -> int:
    data = t.to_bytes((params.p.bit_length() + 7) // 8, "big") + msg
    return int.from_bytes(hashlib.sha256(data).digest(), "big") % params.q


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    key = rsa.keygen(512)

    m, sigma = textbook_forgery(key)
    print("textbook RSA no-query forgery verifies:", rsa_verify_textbook(key, m, sigma))
    s1, s2 = rsa_sign_textbook(key, 111), rsa_sign_textbook(key, 222)
    fm, fs = rsa_homomorphic_forgery(key, 111, s1, 222, s2)
    print("textbook RSA product forgery verifies:", rsa_verify_textbook(key, fm, fs))

    sig = fdh_sign(key, b"transfer 100 euro")
    print("\nRSA-FDH verifies:", fdh_verify(key, b"transfer 100 euro", sig),
          "| rejects tampered message:", not fdh_verify(key, b"transfer 900 euro", sig))
    ps = rsassa_pkcs1_v15_sign(key, b"transfer 100 euro")
    print("RSASSA-PKCS1-v1_5 (RFC 8017 sec. 8.2) verifies:",
          rsassa_pkcs1_v15_verify(key, b"transfer 100 euro", ps))

    params = SchnorrParams(128)
    x, y = schnorr_keygen(params)
    print("\nSchnorr identification accepts honest prover:",
          schnorr_identify(params, x, lambda t: 1 + rng.randbelow(params.q - 1)))
    ssig = schnorr_sign(params, x, b"I approve this message")
    print("Schnorr signature verifies:", schnorr_verify(params, y, b"I approve this message", ssig),
          "| rejects other message:", not schnorr_verify(params, y, b"different", ssig))
    r = 1 + rng.randbelow(params.q - 1)
    a, b = schnorr_sign(params, x, b"m1", r), schnorr_sign(params, x, b"m2", r)
    print("nonce reused once -> secret key recovered:",
          schnorr_nonce_reuse_attack(params, a, b) == x)
