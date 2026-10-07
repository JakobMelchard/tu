# 00 Project focus: what 138.129 is and what is graded

**Read first.** 138.129 is not a lecture. It is a 250 h research project,
supervised one-to-one or in a small group by an E138 lecturer, and graded on one
written artefact: the protocol [S1, S2]. There is nothing to memorise; there is a
topic to agree, a question to answer and a report to write.

## 0 Status 2026-09-28

- **2027W page not published.** Everything below is the 2026W page [S1] and API
  record [S2]; the course has run every semester since 2022W and a 2027S tab
  already exists [S1, S3].
- **Mandatory, QIST 3rd semester** (066 558) [S1].
- **No dates, no TISS registration** ("Not necessary") [S1]: the project exists
  once a lecturer agrees to supervise it.
- **TUWEL:** nothing here depends on TUWEL; nothing was read from it.
- **Prerequisite (recommended):** 138.128 Machine Learning in Physics, notes in
  [`../../../ss2027/machine-learning-in-physics/`](../../machine-learning-in-physics/index.md) [S4].


## 1 Course facts [S1, S2]

| field | value |
|---|---|
| Type | PR (project), 8.0 h, **10.0 ECTS = 250 h** |
| Institute | E138 Solid State Physics |
| Lecturers | Tomczak, Jan Martin; Wallerberger, Markus |
| Mode | immanent; "Protocol" |
| Teaching method | "Interactive course"; hybrid |
| Language | "if required in English" |
| Registration | not necessary; contact the lecturers |
| Curricula | 066 558 QIST: **mandatory, 3rd semester**; 033 261, 066 460, 066 461 mandatory elective |
| Subject | ML as a tool for data analysis and prognosis; project work applying ML in physics and developing tools "e.g. for the compression of data or in optimization problems, pattern recognition, and the prediction of observables" [S2] |
| Literature | none listed; "We recommend taking the course 138.128" |

The learning-outcomes field ("comprehend the materials presented in the lecture
... actively communicate the contents") is generic text [S2]; it names no project
deliverable. The only assessment fact is **"Examination modalities: Protocol"**.

## 2 How the grade is formed

What TISS says: mode immanent, examination modality "Protocol" [S1, S2]. That is all.
What follows from it:

- The protocol is the only graded artefact on record. Treat it as the whole grade.
- "Immanent" formally means continuous assessment; the supervisor sees the work
  during the semester, so the weekly progress is probably not irrelevant. Ask.
- No presentation, oral or code review is mentioned. Ask whether any of these
  is expected (note 08, section 5).

## 3 The lecturers (as of 2026-09-28)

- **Markus Wallerberger**, E138 [S5], in the Computational Materials Science unit
  (Held; DMFT, GW+DMFT, vertex methods [S35]). Senior scientist; lead author of the
  sparse-ir library and paper [S13, S14], co-author of the IR, sparse-sampling and
  quantics tensor-train papers [S12, S15, S16, S32, S34]; teaches 138.128 [S4, S6]
  (Best Lecture 2023 per his page [S6]); maintains w2dynamics and `libxprec` [S7].
  His GitHub profile read "on leave until September 2026" [S7].
- **Jan M. Tomczak** [S8, S9]. Senior Lecturer at King's College London since
  January 2023, Privatdozent at TU Wien since 2019; correlated materials,
  realistic simulations, projects RECORD, BandITT, LinReTraCe [S9]. No ML paper of
  his was found (and beware: **Jakub** M. Tomczak is a different, ML, researcher).

**Inference, not a source:** Wallerberger is the likely supervisor, and the
compression themes of notes 02-05 are his research. Verify both.

## 4 What a 250 h protocol-graded project looks like

250 h is roughly 6 full weeks, or 16 h/week over a 15-week semester next to other
courses. A realistic split:

| block | h | output |
|---|---|---|
| topic, reading, agreement | 30 | one-page project plan (note 01) |
| reproduce a baseline from the literature | 40 | e.g. IR compression of a known $G$, validated |
| main experiments | 100 | the results section |
| validation and error analysis | 30 | tests, seeds, binning, convergence |
| writing the protocol | 40 | the graded artefact (note 08) |
| meetings | 10 | biweekly, with a written log |

The deliverable is a question answered with numbers, error bars and a baseline,
not a tool or a trained model.

## 5 Timeline from 138.128 to the topic agreement

| when | what | source |
|---|---|---|
| 03.03.2027 | 138.128 introduction, FAV HS 1 | [S4] |
| 07.03.-14.03.2027 12:00 | 138.128 registration | [S4] |
| 05.03.-25.06.2027 | 138.128 lectures (Fri 12-14); tests 05.05. and 23.06.2027 | [S4] |
| during 138.128 | note which lecture topics interest you; Wallerberger lectures it: ask in a Q&A after class whether he takes 138.129 students in 2027W | suggestion |
| **end of June 2027** | after the second test: first e-mail to the lecturers (draft in note 01) with 2-3 candidate topics | suggestion |
| July-August 2027 | read [S13] and one topic paper; run sparse-ir [S14] or the `../src` toys on the topic's object | suggestion |
| **September 2027** | topic meeting: question, scope, deliverables, meeting cadence, protocol format, deadline | brief |
| October 2027 | 2027W starts (winter semester formally 1 Oct - end of Feb; verify in the TU Wien calendar) | assumption |
| Oct 2027 - Jan 2028 | project (note 01 milestones) | suggestion |
| by end of 2027W | protocol submitted; confirm the deadline at the topic meeting | ask |

Fallback: the course also runs in summer semesters [S1, S3]; if the topic slips,
2028S is possible, at the cost of the 3rd-semester slot.

## 6 What to verify when the 2027W page appears

- [ ] Page published; lecturers still Tomczak and Wallerberger (Tomczak is in London).
- [ ] Registration still "Not necessary"; no kick-off date (the IFP elective kick-off
      noted on 138.128 was for summer [S4]).
- [ ] Examination still "Protocol"; any presentation or oral added.
- [ ] Mode (hybrid / presence), language.
- [ ] 066 558 still lists it as mandatory, 3rd semester.
- [ ] Any literature, TUWEL course (access pending), or group page with topics.
- [ ] Wallerberger's availability (leave status) [S7].

## 7 Questions

1. **What is the only assessment fact TISS gives, and what does it imply for how
   you spend the 250 h?** "Protocol" [S2]; the report must stand alone, so reserve
   about 40 h for writing and build the validation and error analysis that the report
   will show from the start.
2. **Do you register in TISS?** No: "Not necessary" [S1]. You contact the lecturers and
   agree a topic; the grade appears once the protocol is accepted (confirm the
   administrative step with them).
3. **Why start contacting the lecturers in June rather than October?** No dates and
   no registration mean no automatic slot; a September agreement leaves the whole
   winter semester for 250 h, and summer reading makes the first meeting concrete.
4. **Who is the likely supervisor and why?** Wallerberger: E138, teaches 138.128, and
   the compression themes (IR, sparse sampling, quantics TT) are his papers [S13, S16];
   Tomczak has been at King's College London since 2023 [S8]. Inference; verify.
5. **What distinguishes a gradable result from a demo?** A precise question, a
   baseline, uncertainties from independent repetitions, validation against a known
   limit, and a discussion of what failed (notes 01, 08).
