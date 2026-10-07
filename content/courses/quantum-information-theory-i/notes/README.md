# Notes: 141.282 Quantum Information Theory I

One note per item of the TISS subject outline (1.1-1.5, 2.1-2.8) [S2], in the outline's order, plus the exam focus and a question bank. Notes 01-13 each carry definitions, statements with proofs, a worked example, pitfalls, five oral-exam questions with model answers, and pointers into [`../src/py`](../src/README.md).

**Start with [00](00-exam-focus.md).** Every claim is cited `[S<n>]` against [`../refs/SOURCES.md`](../refs/SOURCES.md), chiefly the TISS-named free texts: Preskill's notes (S5-S9), Jozsa's QIC notes (S10), Wilde's arXiv book (S11, the free version of the CUP 2nd edition TISS names, S12); Nielsen & Chuang (S13) and Bertlmann & Friis (S14, by the two lecturers) are cited only. [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md) maps each outline item to source sections, note and code.

| # | TISS | Note | One line |
|---|---|---|---|
| **00** | - | [**Exam focus**](00-exam-focus.md) | **Read first.** Status 2026-09-28 (2027S published, Thu 10:00-12:00 SR ZE 01-1, 04.03-24.06.2027, no registration, oral exam at the end), how VO orals usually run, the "prove it" table, a 30-minute board plan per section. |
| 01 | 1.1 | [States and operators](01-states-and-operators.md) | Density operators, purity bounds (proved), linear entropy, Bloch ball (proved), precession, generalised Bloch vector for qudits. |
| 02 | 1.2 | [Composite systems](02-composite-systems-and-partial-trace.md) | Tensor products, partial trace forced by local statistics (proved), no-signalling, generalised bipartite Bloch decomposition, LU normal form. |
| 03 | 1.3 | [Entropy](03-entropy.md) | Shannon/von Neumann, Klein, subadditivity, Araki-Lieb, concavity, mixing upper bound (all proved), SSA stated, negative conditional entropy, relative entropy. |
| 04 | 1.4 | [Schmidt and purification](04-schmidt-decomposition-and-purification.md) | Schmidt theorem with two proofs (TISS asks for it), uniqueness, purification existence and uniqueness, HJW, church of the larger Hilbert space. |
| 05 | 1.5 | [Hilbert-space geometry](05-hilbert-space-geometry.md) | Fidelity convention, Uhlmann (proof), trace distance as optimal bias, Fuchs-van de Graaf, Bures distance, Pinsker. |
| 06 | 2.1 | [Non-locality](06-non-locality-and-bell-inequalities.md) | EPR, LHV models, CHSH (proved), $2\sqrt2$, Tsirelson (two proofs), Horodecki criterion, Gisin, Werner table: entanglement is not non-locality. |
| 07 | 2.2 | [Contextuality](07-contextuality.md) | Gleason (statement, POVM version proved), Kochen-Specker, Cabello 18 vectors, Peres-Mermin square, Mermin pentagram, GHZ link. |
| 08 | 2.3 | [Teleportation family](08-teleportation-swapping-dense-coding.md) | Bell-basis identity proof, no-signalling, noisy resource $(1+p)/2$, entanglement swapping, dense coding and optimality. Circuit version in ws2026 C03. |
| 09 | 2.4 | [Quantum cryptography](09-quantum-cryptography.md) | BB84, intercept-resend $Q=\tfrac14$, information-disturbance, 11% threshold, E91 with Ekert's angles, BBM92. Depth in sibling 141.320. |
| 10 | 2.5 | [Entanglement](10-entanglement.md) | Pure and mixed separability, entropy of entanglement, mutual information, PPT (proved; 2x2/2x3 sufficiency), Werner both directions, witnesses, negativity, bound entanglement. |
| 11 | 2.6 | [Quantum channels](11-quantum-channels.md) | CP vs positive, Choi's theorem, Kraus, Stinespring, unitary freedom (all proved), three qubit channels, POVMs as channels. |
| 12 | 2.7 | [Generalised measurements](12-generalised-measurements.md) | PVMs and observables, POVMs from ancillas, Neumark in both forms (proved), perfect discrimination iff orthogonal, trine. |
| 13 | 2.8 | [No-cloning and discrimination](13-no-cloning-and-state-discrimination.md) | No-cloning (TISS asks for the proof), Buzek-Hillery $\tfrac56$, $1\to M$, no broadcasting, no deleting, Helstrom, unambiguous discrimination. |
| 14 | all | [Oral exam question bank](14-oral-exam-question-bank.md) | 80 questions with model answers grouped by TISS item; (P) marks proof requests, (P!) the two the syllabus names. |

Suggested order: 00, then 01 → 05 in one block (formalism; 03 and 04 feed 05), then 10 and 11 (entanglement and channels, the lecturers' home ground), then 06, 07, 08, 09, 12, 13, and use 14 to test yourself.

Related notes elsewhere in the repo: ws2026 quantum computing [C01](../../quantum-computing-complexity-theory-and-algorithmics/notes/C01-qubits-gates-and-measurement.md) (qubit and gate conventions, no-cloning one-liner) and [C03](../../quantum-computing-complexity-theory-and-algorithmics/notes/C03-deutsch-jozsa-bernstein-vazirani-teleportation.md) (teleportation circuit, superdense coding). Sibling ss2027 course [141.320 Quantum Communication and Security](../../quantum-communication-and-security/index.md) covers QKD in depth.

History: `CHANGELOG.md`.
