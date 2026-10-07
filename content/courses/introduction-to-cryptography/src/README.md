# Reference implementations — 192.125 Introduction to Cryptography

**Educational toy cryptography.** Every module is a teaching prototype for the
security definitions, constructions, and attacks in the [notes](../notes/README.md).
Parameters are small so attacks finish in milliseconds; nothing here is
constant-time or hardened. Each file says so in its header.

Every module docstring names three things: the **primitive** it implements, the
**note** it belongs to, and the **standard** it follows (or says that none
exists). Every test module checks the code against a test vector printed in a
vendored standard under [`../refs`](../refs/README.md), or against a library
(`cryptography`, `hashlib`, `sympy`), or both. Where a standard is vendored as
text (RFC 3526, 5869, 6979, 8439), the tests read the numbers out of the file
instead of retyping them ([`py/rfc_vectors.py`](py/rfc_vectors.py)).

## Layout

Python only (this course is maths and proofs first; a single prototype language
is enough). One module per topic plus a `test_<module>.py`; every module has a
seeded `__main__` demo.

| Module | Topic (note) | Standard it is checked against |
|---|---|---|
| [`py/classical.py`](py/classical.py) | historical ciphers (01) | none exists; textbook known answers |
| [`py/otp.py`](py/otp.py) | perfect secrecy (02) | exact enumeration; RFC 8439 sec. 2.4.2 as a pseudo-one-time pad |
| [`py/block_ciphers.py`](py/block_ciphers.py) | block ciphers (03) | FIPS 197 sec. 4.2 and Table 4 (the derived S-box); meet-in-the-middle on 2DES |
| [`py/aes.py`](py/aes.py) | AES (03) | **FIPS 197 from scratch**: appendix A.1-A.3, appendix B, SP 800-38A F.1 for 128/192/256, `cryptography` |
| [`py/prg.py`](py/prg.py) | pseudorandomness (04, 05, 06) | **ChaCha20, RFC 8439 sec. 2.3.2 / 2.4.2**, `cryptography`; LCG distinguisher, toy PRF vs `hashlib` |
| [`py/private_key.py`](py/private_key.py) | private-key encryption (06) | SP 800-38A F.1/F.2/F.5 (in `test_standard_vectors.py`), `cryptography` AES-CBC/CTR and PKCS #7; padding-oracle attack |
| [`py/mac.py`](py/mac.py) | MACs & AE (07) | HMAC: RFC 4231, stdlib and `cryptography`; **HKDF: all seven RFC 5869 cases**; CBC-MAC vs `cryptography` AES-CBC |
| [`py/hashing.py`](py/hashing.py) | hash functions (08) | **SHA-256 from FIPS 180-4** (constants derived, RFC 6234 vectors, `hashlib`); length extension on SHA-256 and on the toy hash; birthday bound |
| [`py/numtheory.py`](py/numtheory.py) | number theory (09) | `sympy` for primality, totient, order, primitive roots; the exam's `[a^b mod N]` items |
| [`py/dh.py`](py/dh.py) | key exchange (10) | **RFC 3526 group 14**, OpenSSL's DH via `cryptography` |
| [`py/rsa.py`](py/rsa.py) | RSA (10) | RFC 8017 key format and Garner CRT, `cryptography` key validation; small-e / Hastad / common-modulus / shared-prime attacks |
| [`py/oaep.py`](py/oaep.py) | RSA padding (10) | **RSAES-OAEP per RFC 8017 sec. 7.1**, 37 Wycheproof vectors, `cryptography` both ways |
| [`py/elgamal.py`](py/elgamal.py) | ElGamal (10) | RFC 3526 group, OpenSSL DH for the mask, HKDF key derivation; hybrid KEM/DEM CCA break, DHIES |
| [`py/signatures.py`](py/signatures.py) | signatures (11) | **RSASSA-PKCS1-v1_5, RFC 8017 sec. 8.2**, `cryptography` both ways; RSA-FDH, Schnorr, special soundness, nonce reuse |
| [`py/dsa.py`](py/dsa.py) | DSA (11) | **all twenty RFC 6979 A.2.1/A.2.2 signatures**, `cryptography` verification; nonce-reuse key recovery |
| [`py/rng.py`](py/rng.py) | randomness (all) | `secrets` by default, `random.Random(seed)` for reproducible demos and tests |
| [`py/rfc_vectors.py`](py/rfc_vectors.py) | test infrastructure | parses RFC 3526/5869/6979/8439 and checks every `SHA256SUMS` manifest |

Test modules that belong to no single topic:

| Test module | What it does |
|---|---|
| [`py/test_standard_vectors.py`](py/test_standard_vectors.py) | the published numbers of FIPS 197 app. B, SP 800-38A (ECB/CBC/CTR, each on the library AES **and** on `aes.PureAES`), RFC 6234 (on `hashlib` **and** `hashing.sha256`), RFC 4231 and RFC 3526 |
| [`py/test_oaep.py`](py/test_oaep.py) | 37 published RSAES-OAEP vectors (18 valid, 19 malformed) from `../refs/vectors/`, and the `cryptography` library in both directions |
| [`py/test_note_pointers.py`](py/test_note_pointers.py) | every name in a note's `## Code` section, every `module.name` and `file.py::name` pointer and every relative link in the notes and READMEs resolves; every module keeps its docstring contract, seeded demo, test file and 300-line limit |
| [`py/test_rfc_vectors.py`](py/test_rfc_vectors.py) | the vendored standards match their `SHA256SUMS`; the RFC parsers find every vector |

## Running

From this course folder, with the repo's Python environment (Python 3.12):

```sh
# everything: 321 tests, offline, seeded
python -m pytest src -q

# just the published-vector checks
python -m pytest -q src/py/test_standard_vectors.py src/py/test_aes.py \
    src/py/test_oaep.py src/py/test_dsa.py src/py/test_mac.py src/py/test_prg.py

# one module's demo (every module has one)
python src/py/aes.py

# the vendored standards, by hand
(cd refs/nist && shasum -a 256 -c SHA256SUMS); (cd refs/rfc && shasum -a 256 -c SHA256SUMS)
```

**Seeds.** [`conftest.py`](conftest.py) seeds `rng` with a fixed value before
every test, so a failing test reproduces on its own; every demo seeds itself
with `rng.seed(2027)` and prints the same output on every run. Unseeded, the
modules draw from `secrets`. A seeded run has no secrets at all, which is the
point of seeding it and one more reason this code protects nothing.

**No network access at test time**: the standards and test vectors are vendored
in [`../refs`](../refs/README.md), and the tests read them from disk.

Run this suite in its own pytest session with the path as above: courses reuse
test-file basenames, so one bare `pytest` over all courses can collide.

## Dependencies

Standard library plus `cryptography` (AES, ChaCha20, HMAC, HKDF, DH, DSA and RSA
cross-checks; its finite-field DH and DSA are deprecated and warn, which the
tests silence) and `sympy` (number-theory cross-checks), all dependencies of the
repo's Python environment.
