# TISS heading to note to source to code

No slide deck of 192.115 is public (see [`README.md`](README.md)), so unlike
the prerequisite's map this one cannot follow lectures. It follows the five
headings of the TISS subject list [S2], in their order, which is also the
order of the notes. The week-1 tutorial on provable security (6 March 2026
[S1]) matches heading 1 coming first.

| TISS heading [S2] | Note | Boneh-Shoup v0.6 [S4] | Other sources | Code (`../src/py/`) |
|---|---|---|---|---|
| (organisation) | [00](../notes/00-exam-focus.md) | exercise lists of ch. 8, 13, 15, 19, 20, 22, 11 | [S1-S3, S24] | - |
| Provable security, the random-oracle model | [01](../notes/01-provable-security-rom.md) | 4.2 (Thm 4.7), 8.10, 11.4, 13.3-13.5, 16.3, 19.2 | [S8, S26-S28, S42, S43] | `rom_reductions.py` |
| Elliptic-curve-based cryptography | [02](../notes/02-elliptic-curves.md) | 15.1-15.5, 16.1, 16.3, 19.3 | [S20-S23, S36, S37] | `ec_toy.py` |
| Zero-knowledge and succinct proof systems | [03](../notes/03-zero-knowledge.md) | 19.1, 19.4-19.7, 20.1-20.3 | [S9, S10, S29, S30, S33, S45] | `sigma_protocols.py`, `commitments.py`, `groups.py` |
| (same) | [04](../notes/04-succinct-proofs.md) | 20.5-20.6 are stubs in v0.6 | [S18, S19, S32] | `r1cs_toy.py`, `commitments.py` |
| Secure multi-party computation | [05](../notes/05-mpc-secret-sharing.md) | 22.1, 23.1-23.2 | [S7 sec. 2-4.2, S13, S14, S31] | `secret_sharing.py` |
| (same) | [06](../notes/06-mpc-ot-gmw-yao.md) | 11.6, 23.3 | [S7 sec. 4.5, S11-S13] | `garbled_circuit_toy.py` |
| Lattice-based cryptography (quantum-secure public-key schemes) | [07](../notes/07-lattices-lwe.md) | ch. 17 is a stub in v0.6 | [S6, S15, S37] | `lattice_toy.py`, `lwe_toy.py` |
| (same) | [08](../notes/08-module-lattices-pqc.md) | 16.5 (Shor) | [S6 sec. 4.4, S16, S17, S34, S35, S39-S41] | `lwe_toy.py` |

## Prerequisite material reused, not repeated

From 192.125 ([notes](../../introduction-to-cryptography/notes/README.md)):

| Needed here | Where in the prerequisite |
|---|---|
| games, PPT, negligible, reduction template, hybrids | notes 04 and 13 |
| hash functions, ROM as background | note 08 |
| cyclic groups, DL/CDH/DDH, NIST key-length table, EC idea | note 09 |
| DH, ElGamal, KEM/DEM | note 10 |
| EUF-CMA, RSA-FDH proof idea, Schnorr ID and signature, (EC)DSA, nonce reuse | note 11 |

Its code (`signatures.py`, `dh.py`, `elgamal.py`) works in $\mathbb Z_p^*$;
this course's code adds elliptic curves, Sigma-protocol machinery, MPC and
lattices, and shares no module with it.
