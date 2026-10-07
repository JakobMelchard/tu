# Map: TISS outline → sources → notes → code

**The course's weekly lecture notes are not public** (TUWEL, unseen). This map therefore aligns the TISS outline [S2] with the free texts TISS names and with the lecturers' book by chapter title. Locators in S5-S11 were read from the PDFs on 2026-09-28; S13 locators are from memory of the 2010 edition; S14 by chapter title only (Crossref). Update this file with the real lecture-note numbering once the course starts.

S5 Preskill 1998 (Leiden, ch. 1-6) · S6/S7/S8/S9 Preskill ch. 2/3/4/10 · S10 Jozsa 2019 · S11 Wilde arXiv v8 · S13 Nielsen & Chuang · S14 Bertlmann & Friis.

| TISS | topic | free sources | cite-only | note | code |
|---|---|---|---|---|---|
| 1.1 | pure and mixed states, operators, linear entropy, Bloch | S6 §2.1-2.3.2; S5 §2.1-2.3; S10 §2.1-2.2; S11 §3.2-3.4, §4.1 | S13 §2.1-2.4; S14 ch. 11 | [01](../notes/01-states-and-operators.md) | `states.py`: `purity`, `linear_entropy`, `bloch_vector`, `gell_mann`, `generalised_bloch` |
| 1.2 | tensor products, partial trace, generalised Bloch | S6 §2.3.1; S11 §3.5, §4.3.3 | S13 §2.2.8, §2.4.3; S14 ch. 11 | [02](../notes/02-composite-systems-and-partial-trace.md) | `states.py`: `partial_trace`, `two_qubit_decomposition`, `bipartite_bloch` |
| 1.3 | Shannon/von Neumann, subadditivity, Araki-Lieb, concavity, relative entropy | S5 §5.2.1; S9 §10.2-10.2.3; S11 ch. 11 (Thm 11.8.2, Cor. 11.8.1, Ex. 11.7.10, Prop. 11.1.4, Thm 11.7.1) | S13 §11.1-11.3; S14 ch. 19-20 | [03](../notes/03-entropy.md) | `entropies.py`: `check_inequalities`, `check_ssa` |
| 1.4 | Schmidt theorem and proof, purification | S6 §2.4, §2.5.5; S5 §2.4, §2.5.5; S11 Thm 3.8.1, §5.1, Thm 5.1.1 | S13 §2.5; S14 ch. 15 | [04](../notes/04-schmidt-decomposition-and-purification.md) | `schmidt.py` |
| 1.5 | overlap, Uhlmann fidelity and theorem, Bures, trace distance | S6 §2.6.1-2.6.2; S11 ch. 9 (Thm 9.2.1, 9.2.2, 9.3.1), Thm 11.9.1 | S13 §9.2; S14 ch. 24 (Bures in metrology, by title) | [05](../notes/05-hilbert-space-geometry.md) | `distances.py` |
| 2.1 | EPR, Bell, CHSH, Tsirelson, entanglement vs non-locality | S8 §4.1-4.3 (Cirel'son §4.3.2, §4.3.4); S5 §4.1; S11 §3.6.2; S25 | S13 §2.6; S14 ch. 12-13 | [06](../notes/06-non-locality-and-bell-inequalities.md) | `bell.py`: `chsh_*`, `horodecki_max_chsh`, `werner` |
| 2.2 | Gleason, Kochen-Specker, Peres square, Mermin pentagram | S5 §2.3.3; S6 Ex. 2.8; S25 §V-VI | S14 ch. 12 (by title) | [07](../notes/07-contextuality.md) | `bell.py`: `square_contexts`, `pentagram`, `cabello_check` |
| 2.3 | teleportation, swapping, dense coding | S8 §4.4.1-4.4.3; S10 §3.4, §4; S11 §6.1-6.3; ws2026 C03 | S13 §1.3.7, §2.3; S14 ch. 14 | [08](../notes/08-teleportation-swapping-dense-coding.md) | `protocols.py`: `teleport`, `teleport_with_resource`, `entanglement_swapping`, `dense_coding` |
| 2.4 | BB84, Ekert 91 | S10 §5; S8 §4.5.1; S5 §4.2.2 | S13 §12.6 | [09](../notes/09-quantum-cryptography.md) | `protocols.py`: `bb84`, `e91_exact`, `e91_sampled` |
| 2.5 | separability, entropy of entanglement, mutual information, PPT, witnesses | S8 §4.6-4.6.1, Ex. 4.10; S9 §10.4-10.5; S11 Def. 4.3.2 | S14 ch. 15-16 | [10](../notes/10-entanglement.md) | `entanglement.py` |
| 2.6 | CPTP, Kraus, Stinespring, larger Hilbert space, POVMs | S7 §3.2-3.4; S5 §3.2-3.4; S11 Thm 4.4.1, Def. 4.4.4, §5.2 | S13 §8.2-8.3; S14 ch. 21 | [11](../notes/11-quantum-channels.md) | `channels.py`: Kraus sets, `choi`, `kraus_from_choi`, `stinespring` |
| 2.7 | projective vs generalised measurements, Neumark | S7 §3.1; S5 §3.1.2-3.1.4; S10 §2.2, §3.2; S11 Def. 4.2.1 | S13 §2.2.3-2.2.6; S14 ch. 23 | [12](../notes/12-generalised-measurements.md) | `channels.py`: `trine`, `neumark_isometry`, `neumark_direct_sum` |
| 2.8 | no-cloning proof, approximate cloning, broadcasting, deleting, discrimination | S10 §3.1-3.3; S8 §4.5.2; S5 §4.2.3, Ex. 5.1; S6 Ex. 2.5; S11 §3.5.4, Ex. 3.5.8 | S13 §1.3.5 | [13](../notes/13-no-cloning-and-state-discrimination.md) | `cloning.py` |

## Gaps in the free sources

- **Approximate cloning** (2.8) and **Mermin's pentagram** (2.2) are not in Preskill or Jozsa; they rest on primary papers [S50-S52] and Mermin [S24, S25].
- **Gleason** is stated without proof in S5 §2.3.3; note 07 proves Busch's POVM version [S59] instead.
- **Entanglement witnesses** appear in none of the free texts at the depth of note 10; they rest on [S34, S35].
- **Bures distance** appears in none of S5-S11 (text search of the PDFs, 2026-09-28); note 05 derives what is needed from Uhlmann.
