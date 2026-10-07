# Reference implementations: 192.115 Advanced Cryptography

**Educational toy cryptography.** Every module is a teaching prototype for a
construction, reduction or attack in the [notes](../notes/README.md).
Parameters are tiny (groups of order 11 or 1019, a curve with 1013 points,
lattices of dimension 2 to 32, a 16-coefficient "Kyber"), so that tests can
enumerate whole distributions and demos finish instantly. Nothing is constant
time, nothing is hardened, and nothing here is production-ready; each file
says so in its header.

The two exceptions *in fidelity, not in status*: `x25519` and the Ed25519
functions in `ec_toy.py` are written from RFC 7748 sec. 5 and RFC 8032 sec.
5.1 and reproduce their published test vectors, read from the vendored RFCs
in `../refs/rfc/`. They are still toy code (variable-time big
integers, affine inversions).

## Layout

Python only: the course is proofs and algebra, and one prototype language is
enough. One module per topic, one `test_<module>.py` each, every module has a
`__main__` demo.

| Module | Note | What it shows |
|---|---|---|
| [`py/groups.py`](py/groups.py) | 03, 06 | Schnorr groups TINY ($q=11$), TOY ($q=1019$), MEDIUM (128-bit); hash to $\mathbb Z_q$ and to the group |
| [`py/rom_reductions.py`](py/rom_reductions.py) | 01 | lazily sampled, logged, programmable random oracle; BR93 $f(r)\,\|\,G(r)\oplus m$ and the inverter that reads the query log; keyless Schnorr signing by programming; forking-lemma rewinding extracting the key, success vs. $\mathrm{acc}(\mathrm{acc}/q-1/h)$ |
| [`py/ec_toy.py`](py/ec_toy.py) | 02 | Weierstrass group law, double-and-add and Montgomery ladder, brute-force point counting, ECDH, EC-Schnorr, ECDSA and its nonce-reuse break, secp256k1 [S21], **X25519 per RFC 7748**, **Ed25519 per RFC 8032** |
| [`py/sigma_protocols.py`](py/sigma_protocols.py) | 03 | Schnorr Sigma protocol, HVZK simulator, special-soundness extractor, strong and weak Fiat-Shamir (and the weak-FS forgery), Chaum-Pedersen, OR-proof with extractor and NIZK version |
| [`py/commitments.py`](py/commitments.py) | 03, 04 | Pedersen (hiding, binding reduction, trapdoor equivocation, homomorphism), hash commitment, **Bulletproofs inner-product argument** (Protocols 1-2 of [S19]) |
| [`py/r1cs_toy.py`](py/r1cs_toy.py) | 04 | circuit $x^3+2x+7=\text{out}$ over $\mathbb F_{97}$ to R1CS to QAP, quotient $h(X)$, **Groth16 equations in the clear** (prove, verify, simulate with the trapdoor) |
| [`py/secret_sharing.py`](py/secret_sharing.py) | 05 | Shamir share/reconstruct, BGW addition, multiplication with degree reduction by resharing and by double sharing, Beaver triples, 5-party evaluation of $(x_0+x_1)x_2+3x_3x_4$ |
| [`py/garbled_circuit_toy.py`](py/garbled_circuit_toy.py) | 06 | DH-based 1-out-of-$n$ OT [S4 sec. 11.6.1], Yao garbling and evaluation, GMW with 1-of-4 OT per AND gate, 2-bit millionaires comparator |
| [`py/lattice_toy.py`](py/lattice_toy.py) | 07 | Gram-Schmidt, Lagrange-Gauss, LLL, Babai rounding and nearest plane, brute-force SVP/CVP, good vs bad basis |
| [`py/lwe_toy.py`](py/lwe_toy.py) | 07, 08 | Regev encryption and its measured failure rate vs. the Gaussian estimate, noiseless LWE by elimination, FIPS 203 Compress/Decompress, a Kyber-shaped module-LWE KEM with FO and implicit rejection |

## What the tests check

- **Against published numbers:** RFC 7748 sec. 5.2 (two function vectors, 1
  and 1000 iterations) and sec. 6.1 (DH) and the edwards25519 constants of
  sec. 4.1; RFC 8032 sec. 7.1 TEST 1-3. Each test first asserts that the hex
  string is printed in the vendored RFC, then that the code reproduces it.
- **Against libraries:** `cryptography` for X25519, Ed25519 (byte-identical
  signatures) and SECP256K1 public keys; `sympy` for primality, polynomial
  division and negacyclic multiplication.
- **Exact distributions** (by enumeration on tiny groups/fields): Schnorr
  HVZK, OR-proof witness indistinguishability, Pedersen perfect hiding,
  Shamir $t$-privacy, OT receiver privacy.
- **Textbook facts:** Hasse bound for every curve over $\mathbb F_p$,
  $p\le17$; [S4 eq. (15.4)] point set; the FIPS 203 compression identities;
  LLL output bound; Babai vs brute-force CVP.
- **Statistics:** forking success vs. the [S27] bound; programming-failure
  rate vs. [S4 eq. (19.5)]; Regev failure rate vs. the Gaussian estimate.

## Running

From the course folder, with the repo's Python environment (Python 3.12):

```sh
# everything (about 5 s)
python -m pytest src -q

# one module's demo
python src/py/ec_toy.py
```

or from this folder: `python -m pytest . -q`. No network at
test time: RFC vectors are read from `../refs/rfc/`.

## Dependencies

Standard library, `numpy` (Regev, toy KEM), `cryptography` (cross-checks),
`sympy` (cross-checks in tests). All dependencies of the repo's Python environment.
