# 00: Exam focus

*Sources: TISS 2026S [S1, S2], the 2028S schedule notes [S3], the lecturer's
page [S24]. No past paper, exercise sheet or slide deck of 192.115 was
readable: TUWEL is not used and VoWi
[S44] is behind a bot check. Everything below about **content** is inference
and marked so.*

## What is fixed (2026S pattern)

| Item | 2026S value [S1, S2] |
|---|---|
| Offered | 2021S, 2023S, 2025S, 2026S [S1, S24]; **not annual**; 2028S unconfirmed [S3] |
| Type | VU 4.0 h, 6.0 ECTS, English, QIST elective [S1] |
| Lecture | Thu 12:00-14:00, EI 11, 05.03-18.06 [S1] |
| Exercises | Fri 10:00-13:00, EI 11; some Fridays 10:00-12:00 are lectures instead [S1] |
| Mandatory sessions | six: 13 and 27 Mar, 24 Apr, 22 and 29 May, 19 Jun; presence until 12:00 [S1] |
| Week 1 | tutorial on provable security, Fri 6 Mar [S1] |
| Registration | 21.01.2026 00:00 to 13.03.2026 10:00; deregistration until 11.03.2026 10:00 [S1] |
| Partial exams | 8 May and 26 June 2026 [S2] |
| Retake | Mon 28.09.2026 12:00-14:00, EI 9: retake of final and of midterm [S1] |
| ECTS split | 24 h lecture, 20 h self-study, 3 h exam, 12 h tutorials, **91 h homework** [S2] |

## The grade

$$\text{grade} = 0.4\,E + 0.6\,X,\qquad X = \tfrac12(X_1+X_2),$$

$E$ = percentage of exercises ticked (and not withdrawn), $X_i$ the two
partial exams [S2]. Conditions: $X \ge 50\,\%$ and **both** $E$ and $X$
positive [S2]. The pass threshold for $E$ is not stated (unverified; 50 % is
the TU default one would guess).

- **The mean, not each part.** $X_1 = 35\,\%$, $X_2 = 70\,\%$ passes the exam
  part ($X = 52.5\,\%$).
- **Retake wording differs by language.** English: "two attempts at the final
  exam, for which the latter grade counts". German: *one* negative partial
  exam may be repeated at the end of September [S2]. The 2026S exam list shows
  one date offering both retakes [S1]. Ask which rule holds in 2028S.
- **Homework dominates the hours.** 91 of 150 h [S2], i.e. about 6 h per week
  over 15 weeks. The exercise part is 40 % of the grade and the exams test the
  same skills.

### Ticking rules [S2]

1. Tick = "I solved it and can present it". A random ticker presents.
2. No real attempt, or not your own work: **the whole sheet's points** go.
3. Unexcused absence from a mandatory session: that session's ticks go.
4. **A second unexcused absence: negative grade.**

Expected-value rule for one extra tick: if $p$ is the chance you are called
for that exercise and $s$ the chance you can defend it, ticking gains its
points with certainty unless called and failing, which costs the sheet. Tick
iff $\text{points(ex)} > p\,(1-s)\,\text{points(sheet)}$. With $n$ tickers,
$p \approx 1/n$; with a sheet worth 5 exercises, an exercise you are only
50 % sure of is worth ticking only when $n > 2.5$. Tick what you can derive at
the board, not what you copied.

## What the exercise style implies (inference)

Planning assumption, not verified from a sheet: the homework looks like
Boneh-Shoup end-of-chapter problems [S4]. Those come in four kinds;
each note ends with questions of all four.

1. **Reduction with a concrete bound.** "Prove that construction $X$ is
   secure if $Y$ is; give the advantage relation." Method: intro note 13's
   template plus the difference lemma (note 01).
2. **Attack.** "Show that variant $X'$ is insecure": a distinguisher or
   forger with its success probability. Typical: a nonce reused, a hash that
   omits the statement, a check that is skipped.
3. **Protocol surgery.** AND/OR composition, generalising a Sigma protocol,
   adding malicious security.
4. **Computation on toy parameters.** A point addition, a Lagrange
   coefficient, a Regev decryption by hand. The `src/py` demos print such
   numbers.

Practice problems in [S4] v0.6 by note (titles are Boneh-Shoup's; which ones
the course uses is unknown):

| Note | Boneh-Shoup exercises |
|---|---|
| 01 | 8.31 (trouble with random oracles), 13.4 (signer confusion on RSA-FDH), 13.10 (probabilistic FDH) |
| 02 | 15.1 (CCA attack on EC-ElGamal), 15.2 (multiplication without $y$), 15.3, 15.4 (Montgomery ladder) |
| 03 | 19.1 (bad randomness in Schnorr), 19.5 (rewinding variants), 19.7 (soundness bound), 19.12 and 20.13 (broken Fiat-Shamir), 19.26 (general AND/OR) |
| 04 | 20.5, 20.7 (range proofs); 19.31 (compressed $n$-wise Schnorr, the idea behind Bulletproofs) |
| 05 | 22.1 (special thresholds), 22.5 (proactive security) |
| 06 | 11.17, 11.18, 11.20 (oblivious transfer variants and an attack) |
| 07, 08 | none: [S4] ch. 17 is "to be written" in v0.6. Use [S6] and the computations in the notes |

## Split between the two partial exams (inference)

Five headings, fifteen weeks, first partial exam in week 10 (8 May 2026 in a
semester starting 5 March). A natural cut puts ROM, elliptic curves and
zero-knowledge in part 1 and MPC and lattices in part 2 (unverified; the
lecture order inside the headings is unknown).

## Checklist for January 2028

- [ ] TISS has a **2028S** tab for 192.115 at all. If not, the next chance is
      likely 2029S or later.
- [ ] Registration window (2026S: 21 Jan to 13 Mar). Register early.
- [ ] **TUWEL access works**: homework is ticked and uploaded there [S2].
- [ ] Dates of the six mandatory sessions; put them in the calendar with the
      12:00 presence rule; check for overlaps with other 2028S courses.
- [ ] Partial-exam dates and the retake rule (the language discrepancy above).
- [ ] Literature list unchanged? Boneh-Shoup may have a newer version than
      v0.6 with chapter 17 (lattices) written; renumber the citations if so.
- [ ] Week-1 provable-security tutorial exists again; attend it.
- [ ] 192.125 results in hand (TISS lists it as expected prior knowledge, not
      a formal prerequisite [S2]).
