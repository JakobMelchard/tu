# 00 Exam focus: an oral exam on a proof-heavy syllabus

Built from the 2027S TISS page and API record [S1, S2], the ss2027 semester calendar [S3] and a VoWi search [S4], all read 2026-09-28. Sources registered in [`../refs/SOURCES.md`](../refs/SOURCES.md). This page covers the **2027S offering**; nothing here has been checked against the lecture itself, which has not started.

## 0. Status as of 2026-09-28

| what | state | source |
|---|---|---|
| TISS page | **2027S published** (offerings 2023W, 2024W, 2025S, 2026S, 2027S); full subject outline 1.1-2.8 transcribed in `../docs/` | [S1, S2] |
| Type | VO, 2.0 h/week, **3.0 ECTS**, English, presence | [S1] |
| Slot | **Thu 10:00-12:00, Seminarraum ZE 01-1, Atominstitut** (Stadionallee 2), **04.03.2027-24.06.2027** | [S1] |
| Sessions | 17 Thursdays in the range; Ascension (06.05.2027) and Corpus Christi (27.05.2027) are public holidays on Thursdays, so **15 sessions**, 14 if the TU Easter week (around Easter Monday 29.03.2027) is lecture-free, which is not confirmed | [S3] |
| Registration | **none** ("Not necessary") | [S1] |
| Exam | **oral exam at the end of the lecture**; no date, no registration window, no format published | [S1, S2] |
| Lecture notes | "made available on a weekly basis"; the 2026S page links "Go to Course Materials" (TUWEL) | [S1] |
| Lecturers | Marcus Huber, Nicolai Friis (E141 Atomic and Subatomic Physics) | [S1] |
| Curriculum | **mandatory elective in 066 558 QIST**; also 066 461 Technical Physics | [S1] |
| Neighbours | 141.320 Quantum Communication and Security, Mon 13:00-16:00, **same room**, final exam 28.06.2027 [S3]: shares BB84/E91 and teleportation (notes [08](08-teleportation-swapping-dense-coding.md), [09](09-quantum-cryptography.md)) | [S3] |


## 1. What is assessed

A VO: no exercises, no homework, no midterm. The grade is **one oral exam** "at the end of the lecture" [S1]. Everything therefore rides on being able to **explain and derive at a board** the thirteen numbered items (1.1-1.5, 2.1-2.8) of the TISS outline. The learning outcomes say what the examiners want: "formally describing quantum information systems", "identifying, characterizing, and quantifying entanglement", "understanding paradigmatic protocols for quantum communication" [S2]. Formalism, entanglement, protocols: in that order of weight is a reasonable guess, and entanglement is the lecturers' research field (their 2023 book has three entanglement chapters, 15, 16, 18 [S14]).

## 2. How oral VO exams typically run (general, not verified for this course)

What follows is general practice for physics VO orals at TU Wien, **not** information about 141.282; no public account of this exam exists (§3). Treat it as a planning assumption.

- Individual appointment (often arranged by e-mail or a TISS exam date near semester end), 20-40 minutes, one or both lecturers.
- Opening "tell me about X" on a topic from the outline; you steer the first minutes. Then follow-ups: "prove that", "why is this assumption needed", "give an example", "what happens for mixed states".
- Board or paper; notation is yours, but define it (fidelity convention, Bell-state labels, Choi ordering).
- Typically two or three topics, one from each half of the outline.
- Grade announced at the end.

Ask in the first lecture (04.03.2027): exam dates or appointment procedure, duration, whether the weekly notes define the examinable content, whether one opening topic may be chosen.

## 3. There are no past exam questions

- **VoWi has no page for 141.282 Quantum Information Theory I** (searched by title and lecturer 2026-09-28). The pages for the follow-up course *Quanteninformationstheorie II VO* exist under both lecturers (Friis, 141.300, last held 2025W; Huber, 141B21, last held 2024S) and **every section reads "noch offen"** [S4].
- The course material is in TUWEL (weekly lecture notes), unseen.

> **Every question in [note 14](14-oral-exam-question-bank.md) is ours**, derived from the TISS outline and the standard literature it names. Use it as a self-test, not as a leaked syllabus.

## 4. The "prove it" items

The outline says "proof" **twice**: "Schmidt decomposition theorem **and proof**" (1.4) and "**Proof** of no-cloning theorem" (2.8) [S2]. Those two are certain. The others below are the proofs a physics examiner reaches for when a named result appears, ranked by how likely a "prove it" follow-up is.

| TISS | must prove | should prove | state only |
|---|---|---|---|
| 1.1 | $1/d\le\operatorname{tr}\rho^2\le1$; Bloch ball $\lvert\vec r\rvert\le1$ | precession $\dot{\vec r}=\omega\hat n\times\vec r$ | Gell-Mann state space shape |
| 1.2 | partial trace is the unique consistent reduction | no-signalling for local operations | LU normal form of $T$ |
| 1.3 | subadditivity (via Klein), Araki-Lieb (via purification), concavity | Klein's inequality | strong subadditivity |
| 1.4 | **Schmidt decomposition** (both proofs), purification exists | purifications unique up to $U_R$; HJW | no tripartite Schmidt |
| 1.5 | Uhlmann (sketch as TISS says "theorem"), $T=\max_P\operatorname{tr}P(\rho-\sigma)$ | Fuchs-van de Graaf upper bound | FvdG lower bound, Pinsker |
| 2.1 | CHSH $\le2$ for LHV; $2\sqrt2$ attained | **Tsirelson** via $\mathcal B^2$ | Horodecki criterion, Werner LHV model |
| 2.2 | Peres-Mermin square, Mermin pentagram (parity) | POVM-Gleason (Busch) | Gleason, KS 117 vectors |
| 2.3 | teleportation via Bell-basis identity | swapping; dense coding | noisy-resource fidelity |
| 2.4 | intercept-resend QBER $\tfrac14$ | information-disturbance lemma | 11% threshold |
| 2.5 | PPT necessary; Werner threshold $\tfrac13$ | witness existence (Hahn-Banach); PPT witness | 2x2/2x3 sufficiency, bound entanglement |
| 2.6 | Kraus $\Rightarrow$ CPTP; Stinespring from Kraus | Choi's theorem; unitary freedom | minimal Kraus number |
| 2.7 | Neumark (ancilla form) | non-orthogonal states not perfectly distinguishable | direct-sum Neumark details |
| 2.8 | **no-cloning** (inner product + linearity) | Helstrom; no-deleting; BH fidelity $\tfrac56$ | cloning optimality, broadcasting proof |

## 5. A 30-minute board talk per section

Template (practise aloud with a timer): **3 min** definitions and notation on the left board; **15 min** the main theorem and its proof; **5 min** one worked example with numbers; **5 min** connections to two other sections; **2 min** limitations and open ends. The plans below fill the template; each note's worked example and "oral-exam questions" supply the material.

| # | open with | central proof | example | connect to |
|---|---|---|---|---|
| [01](01-states-and-operators.md) | ensembles vs $\rho$ axioms | Bloch ball, purity bounds | $\vec r=(0.3,0,0.4)$ | 03 (entropy vs purity), 11 (channels shrink $\vec r$) |
| [02](02-composite-systems-and-partial-trace.md) | tensor products | uniqueness of $\operatorname{tr}_B$, no-signalling | classical vs Bell with equal marginals | 04, 08 |
| [03](03-entropy.md) | $S=H(\lambda)$ | Klein $\to$ subadditivity $\to$ Araki-Lieb $\to$ concavity | Bell, classical, Werner table | 10 (negative $S(A\vert B)$), 05 (Pinsker) |
| [04](04-schmidt-decomposition-and-purification.md) | coefficient matrix $C$ | Schmidt (SVD and reduced-state proofs), purification uniqueness | golden-ratio state | 03 (P4), 05 (Uhlmann), 11 (Stinespring) |
| [05](05-hilbert-space-geometry.md) | overlap, convention box | Uhlmann; $T$ as optimal bias | $\lvert0\rangle$ vs $\tfrac12(I+0.6X)$ | 13 (Helstrom), 11 (monotonicity) |
| [06](06-non-locality-and-bell-inequalities.md) | EPR premises | CHSH, Tsirelson $\mathcal B^2$ | Werner table | 10 (entangled not non-local), 09 (E91) |
| [07](07-contextuality.md) | NCHV definition | square and pentagram parity | GHZ eigenvalues | 06 (locality as noncontextuality), 01 (Gleason) |
| [08](08-teleportation-swapping-dense-coding.md) | resource counting | Bell-basis identity | noisy resource $(1+p)/2$ | 02 (no-signalling), 13 (no-cloning) |
| [09](09-quantum-cryptography.md) | authenticated channel | intercept-resend $Q=\tfrac14$; CHSH monogamy | E91 angles | 06, 13 |
| [10](10-entanglement.md) | separable set | PPT; Werner both directions; witnesses | $p=0.6$ Werner | 06, 03, 11 (transpose not CP) |
| [11](11-quantum-channels.md) | why CP | Choi $\Leftrightarrow$ Kraus $\Leftrightarrow$ Stinespring | amplitude damping Choi | 04 (HJW), 12 |
| [12](12-generalised-measurements.md) | PVM vs POVM | Neumark both forms | trine | 13 (USD), 11 |
| [13](13-no-cloning-and-state-discrimination.md) | unitarity preserves overlaps | no-cloning, no-deleting, Helstrom | BH cloner $\tfrac56$ | 05, 09, 12 |

## 6. Plan (75 h = 3 ECTS)

1. **Before 04.03.2027:** make sure TUWEL access works; read notes 01-05 (formalism) once; run `src` tests and demos.
2. **During the term (15 sessions):** after each lecture, map the weekly lecture notes onto the TISS item and the matching note here; record the lecturers' conventions (fidelity squared or not, Bell labels, Choi ordering) in this file.
3. **Last four weeks:** one 30-minute board talk per day from §5; self-test with note 14, answers covered, spoken aloud.
4. **Exam:** date by appointment or TISS, unknown; ask in the first lecture.

## What this page cannot tell you

Exam format, length, number of questions, grading scale, exam dates, whether the lecture notes define the examinable scope, and any real past question. None is public; all are decided in the lecture and TUWEL.
