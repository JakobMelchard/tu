# 00 Exam focus: what is assessed, and what to decide first

Built from the 2026S TISS record [S1, S2], the public 2019-2022 course material
of Sebastian Hofstätter [S4, S5, S17], the 2023 exercise template [S18], a
student's collection of remembered exam questions [S19], student repositories
from 2025S [S21] and one unverified search snippet of the VoWi page [S20].
Nothing from TUWEL. Read 2026-09-28.

## 0. Status as of 2026-09-28

| what | state | source |
|---|---|---|
| TISS 2027S page | **not published**. Every fact below is the 2026S pattern | [S1] |
| **Curriculum** | TISS lists **066 645 Data Science** and **066 926 Business Informatics** only. **066 558 QIST is not listed**: counts for QIST **only as a free elective** | [S1] |
| Format 2026S | VU 2.0 h, 3 ECTS, online, flipped classroom: YouTube recordings (45-60 min), PDF slides with captions, TUWEL + GitHub, online office hours | [S1, S2] |
| Slot 2026S | Mon 14:00-16:00, Informatikhörsaal, 09.03-29.06.2026 ("Lecture"), despite the online format | [S1] |
| Registration 2026S | 31.01.2026 00:00 - 22.03.2026 23:59, deregistration until the same time | [S1] |
| Assessment 2026S | "Exercises for solving practical challenges and exam"; exam **with two dates**; mode "immanent" | [S1, S2] |
| Flag | **"Attendance Required!"** on the TISS page | [S1] |
| Exercises 2026S | participation in an **international evaluation campaign with a competitive leaderboard**; neural IR in **PyTorch**; critical assessment of papers | [S1] |
| Lecturers 2026S | Knees, Arzt, Lasy, Iklodi, Rauber (E194) | [S1] |
| Preceding | 188.977 Grundlagen des IR, 194.166 Introduction to IR (notes in [`introduction-to-information-retrieval`](../../introduction-to-information-retrieval/index.md)); basics only "briefly refreshed" | [S1, S2] |
| TUWEL | not accessed: every TUWEL-side detail is unknown | - |


## 1. Decide the curriculum question before registering

The course is not in the QIST catalogue on TISS [S1]. Registration makes the
grade appear on the transcript; whether it counts toward 066 558 depends on the
free-elective quota, not on the course. Before 31 January 2027 (the 2026S window
opened 31.01):

1. Check the 2027S TISS page's curricula list again; if 066 558 appears, the question is gone.
2. Otherwise count the free-elective ECTS still open in the QIST degree. 3 ECTS for 75 h of work [S2] is a poor rate if the slot is not free.
3. If it is only for interest: the full 2021/2022 lecture series is public [S4, S16] and costs no registration.

## 2. Assessment shape: exercises dominate

TISS gives only one sentence [S1] but the workload split is explicit [S2]:

| part | hours | share |
|---|---|---|
| lectures and background reading (intro, 3 crash-course IR, 3 NLP, 5 neural IR, special topics) | 25 | 33 % |
| **exercises** | **45** | **60 %** |
| exam including preparation | 5 | 7 % |

The only published point split is from 2022 [S5 sl. 29]: exercise 1 (annotation)
10 % (min 50 %), exercise 2 (neural IR) 50 % (min 50 %), exam 40 % (min 30 %),
total $\ge 50\,\%$; grades $\ge 88/75/63/50$ for 1/2/3/4 (TUWEL defaults). Treat
this as a prior, not as the 2027S rule.

## 3. How the course changed, era by era

| era | lecturers | exercises | exam | source |
|---|---|---|---|---|
| 2019 | Hofstätter et al. | neural re-ranking | written, **open questions** (compare MatchPyramid and KNRM; PR curve of an ideal re-ranker; why low-frequency terms hurt IR) | [S19] |
| 2021-2022 | Hofstätter, Althammer | ex. 1: 500 FiRA relevance annotations; ex. 2 in groups of 4 on GitHub Classroom: KNRM + TK re-ranking from scratch, extractive QA with HuggingFace | **24 h take-home, open book**: read a paper, answer easier and harder questions; two dates; via TUWEL Test | [S5 sl. 23-29, S17] |
| 2023 | (template in `tuwien-information-retrieval`) | ex. 2: judgement aggregation 20, KNRM + TK 40, extractive QA 30, report 10 points | reported as short statements to judge true/false on lecture content | [S18, S19] |
| 2024 | Rauber (VoWi page title) | not public | true/false and fill-in on lectures **plus questions on one paper** (Rahmani et al. 2024, synthetic test collections) | [S19, S53] |
| 2025S | Rauber et al. | group participation in a **CLEF 2025 lab** (LongEval SciRetrieval, BioASQ 13b): a BM25 pipeline, a representation-learning (dense) pipeline, a neural re-ranking pipeline, runs submitted to the official leaderboard | **unverified** (search snippet of VoWi): printed, machine-graded, true/false only with **points deducted for wrong answers**; 12 lecture questions (24 points) and 16 questions (16 points) on a paper released 48 h before | [S20, S21] |
| 2026S | Knees, Arzt, Lasy, Iklodi, Rauber | "international evaluation campaign with a competitive leaderboard", PyTorch | "exam (2 dates offered)" | [S1, S2] |

Two stable facts across eras: **a paper is part of the exam** since 2021 (take-home
reading, later a paper released before a sit-down exam), and **the exercise is a
full retrieval pipeline evaluated on real data** (MS MARCO subset until 2023, a
CLEF lab in 2025S).

## 4. What the public exam material says

[S19] is a student's reconstruction, not official. Paraphrased themes of the
remembered items, grouped by the note that answers them:

| theme | example of what was asked (paraphrased) | note |
|---|---|---|
| metric definitions | what the "M" in MAP averages over; MRR looks only at the first relevant; which metrics are reported at small vs large cutoffs | [04](04-evaluation-and-test-collections.md) |
| test collections | pools should come from many diverse systems; significance is a property of a system comparison, not of a collection; inter-annotator agreement measures label quality, not collection quality | [04](04-evaluation-and-test-collections.md), [13](13-evaluation-campaigns.md) |
| representations | word2vec learns one vector per word (unigram); 1D CNNs build n-gram representations; BERT contextualises tokens | [06](06-word-embeddings.md), [07](07-sequence-models.md), [10](10-transformer-reranking.md) |
| architectures | match BERT_CAT, TK, ColBERT, BERT_DOT to "most effective", "memory hungry", "work moved to indexing", "transformer + kernel pooling" | [10](10-transformer-reranking.md), [11](11-dense-retrieval-and-late-interaction.md), [12](12-efficiency-and-distillation.md) |
| the paper | Cranfield paradigm, which TREC setting, correlation of system rankings (Kendall $\tau$), biases of LLM-generated test data | [13](13-evaluation-campaigns.md) |

Consequences:

- **Exact definitions win.** A true/false item on "the cutoff for MRR" is lost by a fuzzy memory. Every note ends with five exam-style questions for this reason.
- **Negative marking (if it holds in 2027S) makes guessing expensive.** With $+1$ for right and $-1$ for wrong on a true/false item, answering at confidence $p$ has expected value $2p-1$: skip below $p=0.5$, answer above. Check the rule in the first session.
- **Trade-off tables** (effectiveness, query latency, index size, what is precomputed) are the preferred multi-choice format. Note 12 has the table.
- **The paper portion rewards reading speed in IR vocabulary**: pooling, qrels, runs, nDCG@10, Kendall $\tau$ between system rankings, significance tests. Note 13 is the glossary for it.

## 5. Weighting of the notes for the exam

By where past questions fell [S19] and the ECTS split [S2]: evaluation and test
collections (04, 13) and the neural architectures (09-12) carry most exam items;
01-03 and 05-07 are prerequisites that appear as single true/false statements;
14 and 15 appear via the exercise more than the exam.

## 6. What to check in January 2027

| check | why | where |
|---|---|---|
| 2027S TISS page published | all facts above are 2026S | TISS |
| curricula list: is 066 558 added? | decides §1 | TISS "Curricula" |
| registration window | 2026S: 31.01-22.03; expect late January 2027 | TISS |
| weekly slot and whether "Attendance Required!" is real | 2026S slot was Mon 14:00-16:00 [S1] | TISS dates, first session |
| exam dates, format, negative marking, the paper | §3 shows three formats in five years | TISS exam list; TUWEL |
| which evaluation campaign (CLEF lab? TREC track?), group size, compute | the exercise is 60 % of the hours | TUWEL, campaign site [S54, S56, S57] |
| lecturer set | 2026S changed to Knees et al.; content may shift from Hofstätter's slides | TISS |


## 7. Preparation plan before March 2027

1. Watch or read Hofstätter's lectures 1-3 (crash course) against notes 02-04 [S6-S8]; run `src/py/bm25.py`, `metrics.py`.
2. Lectures 4-6 against notes 05-07 and the ADL notes on CNNs, RNNs, transformers (cross-linked there).
3. Lectures 7, 8, 10 against notes 08-12; run `knrm.py`, `dense_retrieval.py`. These are the exercise.
4. Note 13 and `evaluation_campaign.py` before the campaign starts: run-file format, pooling, what the leaderboard measures.
5. Pick one TREC DL overview [S45] and one CLEF lab overview and read them as an exam paper would be read.

## Questions

**Q:** Why can this course not be booked as a QIST elective module course, and what follows?
**A:** TISS lists only 066 645 and 066 926 in its curricula [S1]; for 066 558 it can only be a free elective, so it competes for the free-elective ECTS; decide before registration.

**Q:** What fraction of the workload is exercises, and what did the 2022 grading make of it?
**A:** 45 of 75 h, 60 % [S2]; in 2022 the exercises were 60 % of the grade (10 + 50) with per-part minimums, the exam 40 % with a 30 % minimum [S5 sl. 29].

**Q:** Under a $\pm1$ true/false scheme, when should you answer?
**A:** Expected score $p\cdot1+(1-p)(-1)=2p-1>0 \iff p>1/2$. Answer when more likely right than wrong; the variance argument only matters near $p=1/2$.

**Q:** What was the 2025S exercise, as far as public evidence shows?
**A:** Group participation in a CLEF 2025 lab (LongEval SciRetrieval or BioASQ 13b) with three pipelines, lexical BM25, dense representation learning, neural re-ranking, submitted to the official leaderboard [S21]. Student repositories only, so not the full task text.


## Code

None for this note. The reference implementations are indexed in [`../src/README.md`](../src/README.md).
