# 192.043 Quantum Computing, Complexity Theory, and Algorithmics — TISS page (2026W)

Transcribed from https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192043&semester=2026W
on 2026-09-21, **re-fetched and extended on 2026-09-22** (single appointments
expanded; year-on-year comparison added; discrepancies recorded); re-read on **2026-09-27**: no field changed, the seven overlapping room bookings and both discrepancies are still there. Re-read on **2026-10-09** (page and API record): the only change is that the API record now links the TUWEL course, id 83986; every date, room, exam and registration row is as below. TUWEL itself [S62] is compared with this page in the last section. Content
sections are in tiss-api.md; the source register is
[`../refs/SOURCES.md`](../refs/SOURCES.md).

VU, 6.0 h, 10.0 ECTS, presence. Mode of examination: immanent.

## Discrepancies inside TISS itself

**Read this before putting anything in a calendar.** Three of them, all still
present on 2026-09-22.

### 1. The first meeting: 14:00 or 15:00?

| where | what it says |
|---|---|
| "Subject of course" prose, 192.043 | "**First meeting on Oct 1st, 14:00-17:00!**" (in both the German and the English field) |
| Course-dates table, 192.043 | Thu **15:00 – 17:00**, 01.10.2026, EI 11 HS – INF, "First meeting" |
| "Subject of course" prose, **192.219** | "**First meeting on Oct 1st, 14:00-17:00!**" |
| Course-dates table, **192.219** | Thu **14:00 – 17:00**, 01.10.2026, EI 11 HS – INF, "First meeting" |

192.219 *Supplementary Course Algorithms and Data Structures* is a different
course number in the same room at the same time, taught by Chen and Pichler, and
it shares five date rows with 192.043 verbatim. Its prose **and** its date table
agree on 14:00–17:00. So three of the four statements say 14:00 and only
192.043's own date row says 15:00.

**Conclusion: go at 14:00**, in EI 11 HS. The 15:00 row is most likely a stale
room booking — the 2025W first lecture was at 15:00 [S2], which is where the
figure probably comes from.

### 2. The March retake: 6 March or 9 March, 13:00 or 14:00?

| where | what it says |
|---|---|
| Exams table, time column | Tue **13:00 – 18:00**, **09.03.2027**, HS 7 Schütte-Lihotzky |
| The same row's exam title | "Exam retake, **March 9, 14:00-18:00**" |
| Group registration, group 1 | "Exam retake for Algorithmics and Complexity, **March 6, 13:00-15:00**" |
| Group registration, group 2 | "Exam retake for Quantum algorithms and complexity, **March 6, 15:00-17:00**" |
| 192.219 exams table | Tue **14:00 – 17:00**, **09.03.2027**, EI 7 Hörsaal |

6 March 2027 is a **Saturday**. The two group labels are almost certainly stale
text carried over from an earlier plan; their *durations* (2 h + 2 h) match the
two halves of the retake. The room is booked 13:00–18:00 but the title and the
parallel 192.219 retake both start at **14:00**.

**Working assumption: Tuesday 9 March 2027, starting 14:00, split into an
Algorithmics-and-Complexity half and a Quantum half.** Confirm at the first
meeting.

### 3. The German learning outcome names topics the English one does not

The German `objective` field ends: students can "den Begriff und die Konsequenzen
der **Dekohärenz** erläutern und **elementare Fehlerkorrekturstrategien**
diskutieren und evaluieren". The English `objective` is one sentence and names
neither, and neither appears in the English subject list. Decoherence is covered
in the opening lecture of the sibling course [S20]; error correction is in no
sibling course. See [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

## Year-on-year comparison

| | 2024W [S3] | 2025W [S2] | **2026W** [S1] |
|---|---|---|---|
| type / hours / ECTS | VU 4.0 h, **7.0** | VU 4.0 h, **7.0** | VU **6.0 h, 10.0** |
| companion course | — | "must be combined with **192.042**" (2.0 h, 3.0 ECTS) [S4] | **none — 192.042 has no 2026W offering**; 7 + 3 = 10 |
| lecturers | Chen, Egly, **Tompits**, Fermüller, Pichler, **De Maio** (6) | Chen, Egly, Fermüller, Pichler (4) | Chen, Egly, Fermüller, Pichler (4) |
| first lecture | "October 28, 14:00, Zemanek" | "October 1st, 15:00, FAV HS 3 Zemanek" | "Oct 1st, 14:00-17:00" (prose) / 15:00-17:00 EI 11 (table) — see above |
| textbooks named | **none** | the six now listed | the same six |
| algorithmics bullets | no O-notation item, no approximation item | **+ "Basic running time analysis: O-notation, asymptotic order of growth"**, **+ "Approximation"** | unchanged |
| network-flow bullet | "Max**Cut** versus Min**Flow**" | "Max**Cut** versus Min**Flow**" | **"MaxFlow versus MinCut"** (typo fixed) |
| complexity / quantum bullets | as now | as now | as now |
| TUWEL course linked | yes | yes | not on 2026-09-27; **yes, course 83986, by 2026-10-09** |
| date rows | 3 (Mon 13-18 + Wed 13-18 Zemanek from 28.10; Fri 09-18 SR 127) | 2 (Wed 15-19 Zemanek; Fri 09-18 SR 384) | **9 rows / 48 single appointments**, four different lecture halls |
| exams | **two written papers, 07.02.2025 and 07.03.2025, 10:00-12:00, FAV HS 1** | (page shows the 2026W rows — TISS serves current exam entries on every semester tab) | 11.12.2026, 21.01.2027, retake 09.03.2027 |
| examination modalities | "Exercises + written exam" | "Exercises + written exam" | "Exercises + written exam" |
| curricula | 066 558 QIST, mandatory, 1st sem | same | same |

**What changed that matters.** The course is 43 % bigger in ECTS and 50 % bigger
in contact hours than in either previous year, because the separate preparation
course was folded in. The examination moved from two end-of-semester papers to
two mid-semester papers plus a retake. Two lecturers left after 2024W: Tompits,
who teaches the mathematical/quantum-mechanical foundations in the sibling course
[S15], and De Maio, whose own course carries the variational material [S10].

## Subject outline

Algorithmics: O-notation, graphs (connectivity, traversal, bipartiteness,
topological order), greedy (interval scheduling, MST), divide and conquer
(recurrences, inversions, closest pair), dynamic programming (weighted interval
scheduling, knapsack, shortest path), network flow (Ford-Fulkerson,
max-flow/min-cut, applications), approximation, LP vs ILP.

Complexity theory: P, NP, PSPACE, EXPTIME; L, NL; circuit classes; BPP, PP;
uniform boolean and quantum circuits; extended Church-Turing thesis; BQP; QMA;
quantum query complexity.

Quantum computing: basics, programming techniques and reverse computation,
Deutsch, Deutsch-Jozsa, Bernstein-Vazirani, teleportation, Grover, Simon, QFT,
phase estimation, order finding, Shor, variational and hybrid algorithms.

**Not on this list but taught in the co-taught 192.219 or in the sibling
courses** (see [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md)):
data structures for graphs, interval partitioning, priority queues, merge sort,
the polynomial hierarchy, random access machines, problem reductions, superdense
coding, phase kickback, Gray-code multi-control constructions, decoherence.

## Textbooks

Kleinberg & Tardos, Algorithm Design (2006). Papadimitriou, Computational
Complexity (1994). Aaronson, Quantum Computing since Democritus (2013). Kaye,
Laflamme, Mosca, An Introduction to Quantum Computing (2006). Rieffel & Polak,
Quantum Computing: A Gentle Introduction (2014). Nielsen & Chuang, Quantum
Computation and Quantum Information (2010).

## Teaching methods

Lectures + exercises.

## Lecturers

Chen, Jiehua; Egly, Uwe; Fermüller, Christian; Pichler, Reinhard. Institute E192
Logic and Computation. Which lecturer teaches which block is **not stated
anywhere public**; the inference and its evidence are in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

## Course dates (as the page groups them)

| Day | Time | Date | Location | Description |
|---|---|---|---|---|
| Thu | 15:00-17:00 | 01.10.2026 | EI 11 HS - INF | First meeting *(prose says 14:00-17:00; see Discrepancies)* |
| Fri | 10:00-13:00 | 02.10.2026 - 06.11.2026 | EI 10 Fritz Paschke HS - UIW | Lectures |
| Mon | 14:00-17:00 | 05.10.2026 - 19.10.2026 | EI 8 Pötzl HS - QUER | Lectures Mondays |
| Wed | 15:00-18:00 | 07.10.2026 - 04.11.2026 | EI 5 Hochenegg HS | Lectures |
| Wed | 15:00-19:00 | 07.10.2026 - 27.01.2027 | FAV Hörsaal 3 Zemanek | Lecture: Quantum Computing, Complexity Theory, and Algorithmics |
| Fri | 10:00-13:00 | 09.10.2026 | EI 10 Fritz Paschke HS - UIW | Lecture Friday |
| Mon | 13:00-18:00 | 12.10.2026 - 18.01.2027 | FAV Hörsaal 3 Zemanek | Lectures Quantum Computing, Complexity Theory, and Algorithmics |
| Fri | 10:00-13:00 | 13.11.2026 - 08.01.2027 | EI 5 Hochenegg HS | Lectures Friday |
| Wed | 13:00-16:00 | 02.12.2026 - 16.12.2026 | Seminarraum FAV 01 A | Lectures |

## The 48 single appointments

Expanded with "Show single appointments" on 2026-09-22 (three pages). Eight
streams plus the first meeting.

| stream | slots | dates |
|---|---|---|
| Thu, EI 11 HS, first meeting | 1 | 01.10 |
| Fri 10:00-13:00, EI 10 Fritz Paschke | 6 | 02.10, 09.10, 16.10, 23.10, 30.10, 06.11 |
| Mon 14:00-17:00, EI 8 Pötzl | 3 | 05.10, 12.10, 19.10 |
| Wed 15:00-18:00, EI 5 Hochenegg | 5 | 07.10, 14.10, 21.10, 28.10, 04.11 |
| Wed 15:00-19:00, FAV HS 3 Zemanek | 14 | 07.10, 14.10, 21.10, 28.10, 04.11, 11.11, 18.11, 25.11, 02.12, 09.12, 16.12, 13.01, 20.01, 27.01 |
| Mon 13:00-18:00, FAV HS 3 Zemanek | 10 | 12.10, 19.10, 09.11, 16.11, 23.11, 30.11, 07.12, 14.12, 11.01, 18.01 |
| Fri 10:00-13:00, EI 5 Hochenegg | 6 | 13.11, 20.11, 27.11, 04.12, 18.12, 08.01 |
| Wed 13:00-16:00, Seminarraum FAV 01 A | 3 | 02.12, 09.12, 16.12 |

Two observations that matter.

- **Ten of the 48 slots are double-booked**, and in every case the EI or
  seminar-room booking lies *inside* the FAV Zemanek booking (Wed 07.10–04.11
  five times, Mon 12.10 and 19.10, Wed 02.12–16.12 three times). One cohort
  cannot be in two rooms at once, so the two Zemanek streams are a blanket
  semester-long room hold and the EI rooms are where the October–November
  teaching happens.
- **There is no Friday lecture on 11.12** — that is Exam 1 day.

## Examination modalities

"Exercises + written exam". TISS publishes no weighting; the TUWEL organization
slides do (30 exercise points + 70 exam points, see below and
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)) [S62].

## Exams

| Day | Time | Date | Room | Application | Exam (TISS title) |
|---|---|---|---|---|---|
| Fri | 09:00-12:00 | 11.12.2026 | HS 8 Heinz Parkus - CEE | 01.11.2026 09:00 - 07.12.2026 09:00 | Exam 1: **QIST** Algorithmics & Complexity Theory |
| Thu | 14:00-17:00 | 21.01.2027 | EI 9 Hlawka HS - ETIT | 01.12.2026 09:00 - 19.01.2027 09:00 | Exam 2: **QIST** Quantum Algorithms and Complexity |
| Tue | 13:00-18:00 | 09.03.2027 | HS 7 Schütte-Lihotzky - ARCH | 01.12.2026 09:00 - 08.03.2027 09:00 | Exam retake, March 9, 14:00-18:00 |

All three are "written". The 11.12 slot is shared with 192.219's main exam
(same date and time, room EI 7) [S5].

Retake groups (registration 25.01.2027 09:00 – 04.03.2027 09:00):
"Exam retake for Algorithmics and Complexity, March 6, 13:00-15:00";
"Exam retake for Quantum algorithms and complexity, March 6, 15:00-17:00".
**See Discrepancies: those dates contradict the exam row.**

## Course registration

31.08.2026 00:00 – 02.10.2026 09:00. Deregistration until 10.10.2026 09:00.

## Curricula

**066 558 QIST: mandatory, 1st semester.** Literature: "No lecture notes are
available." Language: English.

## TISS against TUWEL, 2026-10-09

The TUWEL course [S62] has a schedule page (one row per session, with topic and
room) and organization slides. Where they disagree with this page, TUWEL is the
lecturers' own plan and the safer guide; TISS rows are room bookings.

| item | TISS (this page) | TUWEL [S62] |
|---|---|---|
| first meeting, 01.10 | EI 11 HS, 15:00-17:00 in the date row, 14:00 in the prose | EI 10 HS, 14:00-17:00, "Kickoff + Algorithmics 1" |
| Friday 02.10 | booked (EI 10, first of six Fridays) | no session; the Friday series starts 09.10 |
| Zemanek holds (Mon 13:00-18:00, Wed 15:00-19:00, to 27.01) | booked all semester | used only 09.11-30.11 (quantum computing) and 14.12-18.12; no session in Zemanek after 18.12 |
| exam lengths | 3 h slots (09:00-12:00, 14:00-17:00) | 90 minutes each inside those slots |
| retake, 09.03.2027 | row 13:00-18:00; title "14:00-18:00"; group labels "March 6" | organization slides: 14:00-16:00 and 16:00-18:00 (90 + 90 min); schedule page: 13:30-15:30 and 15:45-18:00 (180 min). TUWEL confirms 9 March, not 6 March |
| Complexity (quantum) 3, 09.12 | SR FAV 01 A booked 13:00-16:00 | time 13:00-16:00, but the room cell holds an unrelated "Nov 13, 14:00-15:00, ..." entry |
| lecturers | Chen, Egly, Fermüller, Pichler | same four on the slides; the algorithmics decks are Chen's |
| weighting | not stated | 6 sheets x 5 points + 2 exams x 35 points, see note 00 |

The two retake readings on TUWEL disagree with each other as well as with
TISS. Both start no earlier than 13:30, so the 13:00 room booking is the
outer bound.
