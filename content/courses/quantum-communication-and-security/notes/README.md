# Notes: 141.320 Quantum Communication and Security

Ordered by the TISS topic list [S2]: elements of secure communication, BB84, theoretical tools, information reconciliation and privacy amplification, security proofs against collective and coherent attacks, imperfections (decoy states, MDI-QKD). Notes 01-06 each carry definitions, derivations, a worked example with real key-rate numbers, pitfalls, five exam-style questions with answers, and pointers into [`../src/py`](../src/README.md).

**Start with [00](00-exam-focus.md).** TISS names no literature, so every claim is cited `[S<n>]` against [`../refs/SOURCES.md`](../refs/SOURCES.md), chiefly S3 (Scarani et al., RMP 2009), S4 (Renner's thesis), S5 (Tomamichel-Leverrier 2017) and the primary paper for each named result. [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md) maps the TISS topics and the sources onto these notes and the code. The course's own lecture notes are handed out in the course and have not been seen.

| # | Note | One line |
|---|---|---|
| **00** | [**Exam focus**](00-exam-focus.md) | **Read first.** 100 points: 20 exercises/presentation, 10 homework, 70 final exam with a hard $\ge35/70$ hurdle; Mon 28.06.2027 exam, 26.07.2027 Nachtest; the 13:00 vs 14:00 start discrepancy; what to verify on 01.03.2027. |
| 01 | [Elements of secure communication](01-elements-of-secure-communication.md) | OTP, Shannon perfect secrecy and $H(K)\ge H(M)$ (proved), no key from public discussion (proved), authentication, composable $\varepsilon$-security (correctness + secrecy), why not mutual information. |
| 02 | [BB84](02-bb84.md) | Protocol steps, what is public, EB version, intercept-resend $e=\tfrac14$ and $I(A{:}E)=2e$ (derived), biased Eve, QBER with noise, Serfling sampling bound, sifting efficiency. |
| 03 | [Theoretical tools](03-theoretical-tools.md) | cq states, purification (why Eve holds it), von Neumann and Holevo, min-/max-/smooth entropies, duality, data processing, chain rule, AEP, entropic uncertainty relation, $1-2h(e)$ in three lines, Bell-diagonal $H(Z\mid E)$ (derived). |
| 04 | [Reconciliation and privacy amplification](04-reconciliation-and-privacy-amplification.md) | Leakage $\ge nh(e)$, BINARY, Cascade, syndrome and LDPC codes, verification hash, Toeplitz two-universality (proved), leftover hash lemma (proof sketch), composable key length formula. |
| 05 | [Security proofs](05-security-proofs.md) | Individual/collective/coherent attacks, Devetak-Winter, BB84 $1-2h(e)$ as a minimisation (derived), Shor-Preskill structure, de Finetti and post-selection, Tomamichel-Leverrier finite key with a table of $\ell/m$. |
| 06 | [Imperfections: decoy and MDI](06-imperfections-decoy-and-mdi.md) | WCP channel model, PNS and GLLP ($O(\eta^2)$), decoy rate ($O(\eta)$), vacuum+weak bounds (derived), 142 km / 140.6 km reproduced, MDI-QKD BSM and sifting, why it removes detector attacks, a paragraph on DI-QKD. |

Suggested order: 00, then 01 → 02 → 03 → 04 → 05 → 06, which is the TISS topic order. 03 overlaps with the sibling course 141.282 QIT I (same semester, Thu), which covers entropies, purification, fidelity, trace distance and channels in more depth: `../../quantum-information-theory-i/notes/`.

**Code.** Every *Code* section names functions that exist in [`../src/py`](../src/README.md) (checked 2026-09-28). Tests reproduce published numbers: 11.00 % threshold, $\chi(Z{:}E)=h(e)$, 142.05 km and 140.55 km [S9], $\beta_{Y_1}=3.5\%$, $\beta_{e_1}=16.8\%$ [S9], the Ma-Razavi MDI closed forms [S11].

Also here: `CHANGELOG.md`.
