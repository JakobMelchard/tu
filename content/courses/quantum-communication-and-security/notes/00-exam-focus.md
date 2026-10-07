# 00 Exam focus: what is assessed and how to prepare

Built from the 2027S TISS page and API record, both read 2026-09-28 [S1, S2], and the semester calendar [S36]. The course is five months away; everything below about the exam itself is inferred from the TISS text and must be checked in the first session (§6).

## 0. Status as of 2026-09-28

| what | state | source |
|---|---|---|
| TISS 2027S page | **published** (third offering after 2025S, 2026S) | [S1] |
| Type | VU 3.0 h, 4.5 ECTS, English, mode of examination "immanent" | [S1] |
| Curriculum | 066 558 QIST, **mandatory elective** (only curriculum listed) | [S1] |
| Lecturer | Glaucia Murta Guimaraes, E141 Atominstitut | [S1] |
| Weekly | **Mon 13:00-16:00**, Seminarraum ZE 01-1, Atominstitut (Stadionallee 2), 01.03-21.06.2027 | [S1] |
| Time discrepancy | TISS "Additional information" says "Mondays, 14:00 - 16:30"; the date row says 13:00-16:00; 2026S had the same shape (row 13:00-16:00, text 13:00-15:30). **Unresolved; 13:00 assumed** | [S1, S2] |
| Final exam | **Mon 28.06.2027 14:00-16:00**, Seminarraum ZE 01-1 | [S1] |
| Nachtest (retake) | **Mon 26.07.2027 14:00-16:00**, same room | [S1] |
| Registration | **31.01.2027 08:00 - 26.03.2027 23:00**; no deregistration end given | [S1] |
| Material | "lecture notes and exercises provided in advance"; nothing on TISS itself | [S1] |
| Previous knowledge | quantum mechanics | [S1] |
| TUWEL | not used for anything here; whether the course distributes notes there is unverified | - |


## 1. The grade: 100 points, one hard hurdle

| component | points | hurdle |
|---|---|---|
| Exercises, presentation and participation in the exercise class | up to 20 | none stated |
| Homework assignment | up to 10 | none stated |
| **Final exam** | **up to 70** | **$\ge35/70$ required** |

Scale (only if the exam hurdle is met): 1 at 88-100, 2 at 75-87.99, 3 at 63-74.99, 4 at 50-62.99, 5 below 50 **or** under 50 % in the final exam [S1, S2].

Arithmetic worth doing now:
- **The exam decides.** With full 30 coursework points you still need 35 on the exam to pass at all, and 58/70 for a 1.
- With 20/30 coursework: 30 exam points is a fail (hurdle), 35 gives 55 (grade 4), 55 gives 75 (grade 2).
- Exercises and homework are worth 30 points, a bit more than two grade steps (the steps are 12-13 points wide); they cannot rescue a failed exam.
- The **Nachtest** on 26.07.2027 is the second chance for the exam; whether coursework points carry over is not stated (assume yes, verify).
- The 2027S wording is new: 2026S said only "final exam plus regular participation and presentations" [S1]. Do not rely on second-hand reports from 2025S/2026S.

## 2. What a QKD security exam asks

No past exam of this course is public: TISS has none, and the VoWi page could not be read (access blocked by a bot filter on 2026-09-28, [S35]). So the question types below are **derived from the four TISS learning outcomes** [S2], not from real papers. Each note ends with five questions in this style.

| learning outcome [S2] | typical task | where |
|---|---|---|
| Describe the steps of a QKD protocol | list BB84 steps, say what is public, explain sifting and parameter estimation; intercept-resend QBER 25 % derivation | [02](02-bb84.md) |
| Compute asymptotic key rates and apply entropic relations | $1-2h(e)$ from Devetak-Winter or from the uncertainty relation; Bell-diagonal $H(Z\mid E)$; threshold 11 %; decoy rate formula; $\chi(Z{:}E)=h(e)$ | [03](03-theoretical-tools.md), [05](05-security-proofs.md), [06](06-imperfections-decoy-and-mdi.md) |
| Explain how techniques and theorems are used in a security proof | composable definition; leftover hash lemma and key length; chain rule for leakage; de Finetti / post-selection / uncertainty relation; Shor-Preskill structure | [01](01-elements-of-secure-communication.md), [04](04-reconciliation-and-privacy-amplification.md), [05](05-security-proofs.md) |
| Identify assumptions and weaknesses | PNS and GLLP, decoy assumptions (phase randomisation), detector attacks, MDI and DI trust models, authentication | [01](01-elements-of-secure-communication.md), [06](06-imperfections-decoy-and-mdi.md) |

Expect short derivations with numbers. The formulas to be able to write from memory:
$$e_{\rm IR}=\tfrac14,\quad r=1-h(e_Z)-h(e_X),\quad r=H(A|E)-H(A|B),\quad \ell=H^\varepsilon_{\min}(X|E)-\mathrm{leak_{EC}}-t-2\log\tfrac1{2\varepsilon_{\rm pa}},$$
$$R=q\{-Q_\mu fh(E_\mu)+Q_1[1-h(e_1)]\},\qquad Y_1^L=\tfrac{\mu}{\mu\nu-\nu^2}\bigl(Q_\nu e^\nu-Q_\mu e^\mu\tfrac{\nu^2}{\mu^2}-\tfrac{\mu^2-\nu^2}{\mu^2}Y_0\bigr).$$

The exam format (written or oral, open or closed book, formula sheet) is not stated. The 2-hour slot in a seminar room with a separate Nachtest date suggests a written exam; **unverified**.

## 3. Exercise class and presentation (20 points)

TISS: "lectures cover the main content, exercise classes focus on examples and specific proofs, students present solutions" [S1]. Since the exercises are handed out in advance, the 20 points reward preparing every sheet so you can present at the board. Proofs that are natural presentation material, each worked out in the notes:
- OTP perfect secrecy and Shannon's key bound (note 01 Thms 1.1-1.2); no key from public discussion (Thm 1.3).
- Intercept-resend QBER and information (note 02 Prop. 2.1).
- Bell-diagonal $H(Z\mid E)$ and the minimisation to $1-2h(e)$ (note 03 Prop. 3.2, note 05 Prop. 5.2).
- Toeplitz two-universality and the leftover hash lemma sketch (note 04 Prop. 4.1, Thm 4.2).
- Vacuum+weak decoy bound (note 06 Thm 6.3).
- MDI sifting table from HOM interference (note 06; `mdi_qkd.single_photon_bsm`).

## 4. Homework (10 points)

One "homework assignment" [S1]. Form (written derivations, a simulation, a report) and deadline: not public. The code in [`../src`](../src/README.md) covers the obvious computational candidates (key rate vs distance, decoy estimation, finite-key lengths).

## 5. Calendar (from [S36])

- 17 Mondays 01.03-21.06.2027; **Easter Monday 29.03.2027 and Whit Monday 17.05.2027 are public holidays**, so at most 15 sessions (TU Wien's Easter lecture-free week for 2027 is not confirmed).
- 141.282 QIT I runs in the same semester and teaches the background of note 03 (entropies, purification, fidelity, channels, BB84/E91) *in parallel*, not before. Read its notes ahead: `../../quantum-information-theory-i/notes/` (written concurrently).
- 192.125 Cryptography is a winter-semester course, so it does not come before this one; classical crypto background has to come from note 01.


## 6. What to verify in the first session (Mon 01.03.2027)

1. Start time: 13:00 or 14:00, end 16:00 or 16:30 (TISS contradicts itself).
2. Where lecture notes and exercise sheets are distributed (TUWEL?).
3. Exam format: written or oral, allowed aids, formula sheet; whether the Nachtest replaces or adds to the exam.
4. How the 20 exercise points split between presentation, participation and prepared solutions; whether presenting is compulsory.
5. Homework: topic, form, deadline, group or individual.
6. Whether coursework points carry over to the Nachtest.
7. Which lecture falls on the Easter break; whether 29.03 and 17.05 are made up.
8. The literature the lecturer follows (TISS names none; [S3, S4, S5] are the standard choices, [S32] is the lecturer's own review).

## 7. Preparation before March 2027

1. Register in TISS between 31.01.2027 08:00 and 26.03.2027 23:00.
2. Read notes 01-06 in order; run `src/py` demos. Notes 03 and 05 carry the mathematics the exam will lean on.
3. Read [S5] §§2-6 (self-contained, 40 pages, CC BY) and [S3] §§I-III; [S32] for topic 6.
4. Make sure TUWEL access works in time for the first sheet.

## What this page cannot tell you

- Exam format, length, aids; any real past question.
- How presentation points are awarded; homework form and deadline.
- Whether the lecture follows a textbook or only its own notes.
- The Easter break dates for 2027.
- Anything behind TUWEL (not accessed).
