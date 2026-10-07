# Sources: 188.980 Advanced Information Retrieval

Register of every source used for [`../notes`](../notes/README.md) and
[`../src`](../src/README.md). The notes cite `[S<n>]`, with a locator where one
exists: `[S7 sl. 20]` is printed slide number 20 of lecture 2 (the number in the
slide's corner, not the PDF page; animation steps are dropped in the PDFs, so the
two differ), `[S23 eq. 3.15]` an equation number, `[S37 §3.2]` a section.
All retrieved **2026-09-28** unless stated otherwise.

**Nothing is vendored.** No source here is permissively licensed (see "Licence"
per entry); `fetch-sources.sh` downloads the open ones into the git-ignored
`cite-only/`. See [`README.md`](README.md).

**Licence correction.** The task brief described the Hofstätter slides as
"CC BY-SA 4.0". That could not be confirmed: the repository's only licence is
**GPL-3.0** (GitHub API `license.spdx_id`, and the `LICENSE` file), and neither
the slide PDFs nor the README carries a Creative Commons notice (text of all 11
PDFs searched). Treated as GPL-3.0, cite-only.

## Course records

| id | what | where | notes |
|---|---|---|---|
| S1 | TISS page 188.980, **2026S** (2027S not published) | [`../docs/tiss.md`](../docs/tiss.md), <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=188980&semester=2026S> | transcribed 2026-09-28; format, ECTS split, lecturers, Mon 14-16 slot, registration 31.01-22.03.2026, curricula (no 066 558), "Attendance Required!" |
| S2 | TISS API record 2026S | `../docs/tiss-api.md` | learning outcomes, ECTS breakdown (intro, 3 crash-course IR, 3 NLP, 5 neural IR, special topics; 25 h / 45 h / 5 h) |
| S3 | semester schedule `ss2027/_schedule/dates.json`, entries 188.980 and 141.320 | source repo, not published | the 2027S slot of 141.320 (Mon 13:00-16:00) |

## Public course material, Hofstätter era (2019-2022)

Repository <https://github.com/sebastian-hofstaetter/teaching>, folder
`advanced-information-retrieval/`. **Licence: GPL-3.0** (repo-wide; no CC notice
found). Last push 2023-06-12. Lecturers 2022: Hofstätter, Althammer [S5 sl. 2].
Slides downloaded 2026-09-28; sha256 of each PDF in `fetch-sources.sh`.

| id | file | used for |
|---|---|---|
| S4 | repo `README.md` | lecture list 0-10, YouTube links, exercise links, "Best Distance Learning Award 2021" |
| S5 | Lecture 0, *Course Introduction* (2022) | syllabus sl. 14; exercises sl. 23-27; **online exam sl. 28**; **grading sl. 29** |
| S6 | Lecture 1, *Crash Course: Fundamentals* | inverted index sl. 8-22; TF-IDF sl. 49-55; BM25 sl. 67-73; BM25F sl. 73-75 |
| S7 | Lecture 2, *Crash Course: Evaluation* | judgements sl. 9-10; metrics and cutoffs sl. 14; MRR sl. 16-18; MAP sl. 19-20; nDCG sl. 22-27; significance sl. 29-30; non-determinism sl. 31 |
| S8 | Lecture 3, *Crash Course: Test Collections* | MS MARCO, TREC-DL, crowdsourcing, majority voting, kappa, pooling, pool bias, FiRA, biases (slides cited by title) |
| S9 | Lecture 4, *Word Representation Learning* | word2vec, fastText, analogies, query expansion, topic shifting, retrofitting |
| S10 | Lecture 5, *Sequence Modelling in NLP* | 1D CNN, pooling, RNN/LSTM, encoder-decoder, attention, beam search |
| S11 | Lecture 6, *Transformer and BERT Pre-training* | self-attention, MLM, BERT input/workflow, HuggingFace, **extractive QA** |
| S12 | Lecture 7, *Introduction to Neural Re-Ranking* | workflow sl. 7-16 (loss functions sl. 15), MatchPyramid sl. 26-27, **KNRM sl. 29-36**, Conv-KNRM sl. 37-40, low-frequency terms sl. 43-47 |
| S13 | Lecture 8, *Transformer Contextualized Re-Ranking* | BERT_CAT sl. 8-11, mono-duo sl. 12, long documents sl. 13, inefficiency sl. 14, PreTTR sl. 18-19, ColBERT sl. 20-21, TK sl. 22-26, comparison sl. 27, TKL/IDCM sl. 34-40 |
| S14 | Lecture 9, *Domain Specific Applications* (guest lecture Althammer) | medical and legal IR, campaigns, BERT-PLI |
| S15 | Lecture 10, *Dense Retrieval and Knowledge Distillation* | BERT_DOT sl. 9-11, in-batch negatives / ANCE sl. 12-13, NN search sl. 14-17, KD sl. 19-24, **Margin-MSE sl. 25**, TAS-B sl. 30-34, BEIR sl. 36-38 |
| S16 | YouTube playlist *Advanced Information Retrieval* | <https://www.youtube.com/playlist?list=PLSg1mducmHTPZPDoal4m59pPxxsceXF-y> | reachable (HTTP 200); not watched, the slides and transcripts cover it |
| S17 | `neural-ir-exercise-2022/Assignment.md` (also 2020, 2021) | exercise 2: KNRM/TK re-ranking + extractive QA, FiRA data |

## After 2022

| id | what | licence / status | used for |
|---|---|---|---|
| S18 | <https://github.com/tuwien-information-retrieval/air-23-template> `assignment_2.md` (2023) | no licence file: cite only | exercise 2 in 2023: judgement aggregation 20, KNRM+TK 40, extractive QA 30, report 10 points; KNRM ~0.19 MRR@10 on the subset |
| S19 | <https://github.com/sueszli/tu-wien-data-science-summaries>, folder `air - advanced information retrieval 188.980/exams.md` and `summary.md` | AGPL-3.0; **student-compiled recollections** ("most of these are from mattermost"), not official | shape of past exam questions 2019, 2022, 2023, 2024 (paraphrased, never copied) |
| S20 | VoWi pages *TU Wien:Advanced Information Retrieval VU (Rauber)*, its subpage *Sueszli's summary + altprüfungen*, and *(Knees)* | **not read**: the wiki answered with an Anubis bot-protection page; only a search-engine result snippet was seen | 2025S exam description from that snippet, marked **unverified** everywhere it is used |
| S21 | student repos <https://github.com/mtiessler/188.980_Advanced_Information_Retrieval_Project> (LongEval 2025 SciRetrieval, CLEF) and <https://github.com/sagii814/TU_AIR_S2025> (BioASQ Task 13b) | no licence: README read only | the 2025S exercise shape: group participation in a CLEF lab with a BM25, a representation-learning and a neural re-ranking pipeline, submitted to the official leaderboard |

## Textbook and classic IR papers

| id | reference | access |
|---|---|---|
| S22 | C. D. Manning, P. Raghavan, H. Schütze, *Introduction to Information Retrieval*, CUP 2008 | free online, <https://nlp.stanford.edu/IR-book/> (PDF HTTP 200); personal use, cite only |
| S23 | S. Robertson, H. Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*, FnTIR 3(4), 2009, doi:10.1561/1500000019 | author PDF <https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf>; equation numbers read from it (3.2 RSJ, 3.12 B, 3.13 tf', 3.15 BM25) |
| S24 | C. Zhai, J. Lafferty, *A study of smoothing methods for language models applied to ad hoc IR*, SIGIR 2001, doi:10.1145/383952.384019 | DOI verified via Crossref; paywalled, not read |
| S25 | K. Järvelin, J. Kekäläinen, *Cumulated gain-based evaluation of IR techniques*, TOIS 20(4) 2002, doi:10.1145/582415.582418 | DOI verified; not read |
| S26 | M. Smucker, J. Allan, B. Carterette, *A comparison of statistical significance tests for IR evaluation*, CIKM 2007, doi:10.1145/1321440.1321528 | DOI verified; not read |
| S27 | J. Zobel, *How reliable are the results of large-scale IR experiments?*, SIGIR 1998, doi:10.1145/290941.291014 | DOI verified; not read |
| S28 | C. Buckley, E. Voorhees, *Retrieval evaluation with incomplete information*, SIGIR 2004, doi:10.1145/1008992.1009000 | DOI verified; not read (bpref definition as commonly stated; our implementation's tie-breaking is ours) |
| S49 | C. Burges et al., *Learning to rank using gradient descent* (RankNet), ICML 2005, doi:10.1145/1102351.1102363 | DOI verified; not read |
| S72 | C. Burges, *From RankNet to LambdaRank to LambdaMART: An Overview*, MSR-TR-2010-82 | URL returned HTTP 403 to curl; **not retrieved** |

## Representation learning and neural IR papers (arXiv ids verified via the arXiv API)

| id | reference | id / URL |
|---|---|---|
| S29 | Mikolov et al., *Efficient Estimation of Word Representations in Vector Space*, 2013 | arXiv:1301.3781 |
| S30 | Mikolov et al., *Distributed Representations of Words and Phrases and their Compositionality*, 2013 | arXiv:1310.4546 |
| S31 | Pennington, Socher, Manning, *GloVe*, EMNLP 2014 | <https://nlp.stanford.edu/pubs/glove.pdf> |
| S32 | Devlin et al., *BERT*, 2018 | arXiv:1810.04805 |
| S33 | Xiong et al., *End-to-End Neural Ad-hoc Ranking with Kernel Pooling* (KNRM), SIGIR 2017 | arXiv:1706.06613, doi:10.1145/3077136.3080809 |
| S34 | Dai et al., *Convolutional Neural Networks for Soft-Matching N-Grams in Ad-hoc Search* (Conv-KNRM), WSDM 2018 | doi:10.1145/3159652.3159659, author PDF <http://www.cs.cmu.edu/~zhuyund/papers/WSDM_2018_Dai.pdf> |
| S35 | Nogueira, Cho, *Passage Re-ranking with BERT*, 2019 | arXiv:1901.04085 |
| S36 | Hofstätter et al., *Interpretable & Time-Budget-Constrained Contextualization for Re-Ranking* (TK), ECAI 2020 | arXiv:2002.01854 |
| S37 | Karpukhin et al., *Dense Passage Retrieval for Open-Domain QA* (DPR), EMNLP 2020 | arXiv:2004.04906 |
| S38 | Khattab, Zaharia, *ColBERT*, SIGIR 2020 | arXiv:2004.12832 |
| S39 | Santhanam et al., *ColBERTv2*, 2021 | arXiv:2112.01488 |
| S40 | Hofstätter et al., *Cross-Architecture Knowledge Distillation* (Margin-MSE), 2020 | arXiv:2010.02666 |
| S41 | Hofstätter et al., *Balanced Topic Aware Sampling* (TAS-B), SIGIR 2021 | arXiv:2104.06967 |
| S42 | Xiong et al., *ANCE*, ICLR 2021 | arXiv:2007.00808 |
| S43 | Johnson, Douze, Jégou, *Billion-scale similarity search with GPUs* (FAISS) | arXiv:1702.08734 |
| S44 | Bajaj et al., *MS MARCO*, 2016 (v3) | arXiv:1611.09268 (abstract: 1,010,916 questions, 8,841,823 passages from 3,563,535 documents) |
| S45 | Craswell et al., *Overview of the TREC 2019 Deep Learning Track* | arXiv:2003.07820 (abstract: 43 test queries per task, 8.8 M passages, 15 groups, 75 runs) |
| S46 | Craswell et al., *Overview of the TREC 2020 Deep Learning Track* | arXiv:2102.07662 |
| S47 | Rajpurkar et al., *SQuAD: 100,000+ Questions*, 2016 | arXiv:1606.05250 |
| S48 | Lin, Nogueira, Yates, *Pretrained Transformers for Text Ranking: BERT and Beyond* | arXiv:2010.06467 |
| S50 | Sennrich, Haddow, Birch, *Neural Machine Translation of Rare Words with Subword Units* (BPE) | arXiv:1508.07909 |
| S51 | Hofstätter et al., *On the Effect of Low-Frequency Terms on Neural-IR Models*, SIGIR 2019 | arXiv:1904.12683 |
| S52 | Hofstätter et al., *ColBERTer*, 2022 | arXiv:2203.13088 |
| S53 | Rahmani et al., *Synthetic Test Collections for Retrieval Evaluation*, SIGIR 2024 | arXiv:2405.07767 (the 2024 exam paper according to [S19]) |
| S58 | Thakur et al., *BEIR*, 2021 | arXiv:2104.08663 |
| S59 | Bojanowski et al., *Enriching Word Vectors with Subword Information* (fastText) | arXiv:1607.04606 |
| S60 | Kudo, Richardson, *SentencePiece* | arXiv:1808.06226 |
| S61 | Wu et al., *Google's Neural Machine Translation System* (WordPiece) | arXiv:1609.08144 |
| S62 | Kim, *Convolutional Neural Networks for Sentence Classification*, 2014 | arXiv:1408.5882 |
| S63 | Bahdanau, Cho, Bengio, *Neural MT by Jointly Learning to Align and Translate* | arXiv:1409.0473 |
| S64 | Vaswani et al., *Attention Is All You Need* | arXiv:1706.03762 |
| S65 | Pang et al., *Text Matching as Image Recognition* (MatchPyramid) | arXiv:1602.06359 |
| S66 | MacAvaney et al., *Efficient Document Re-Ranking for Transformers by Precomputing Term Representations* (PreTTR) | arXiv:2004.14255 |
| S67 | Malkov, Yashunin, *HNSW* | arXiv:1603.09320 |
| S68 | Sanh et al., *DistilBERT* | arXiv:1910.01108 |
| S69 | Hinton, Vinyals, Dean, *Distilling the Knowledge in a Neural Network* | arXiv:1503.02531 |
| S70 | Nogueira et al., *Multi-Stage Document Ranking with BERT* (monoBERT/duoBERT) | arXiv:1910.14424 |
| S71 | Craswell et al., *MS MARCO: Benchmarking Ranking Models in the Large-Data Regime*, SIGIR 2021 | arXiv:2105.04021 |

## Evaluation campaign homepages (HTTP 200 on 2026-09-28)

| id | site |
|---|---|
| S54 | TREC, <https://trec.nist.gov/> |
| S55 | MS MARCO, <https://microsoft.github.io/msmarco/> |
| S56 | CLEF LongEval, <https://clef-longeval.github.io/> |
| S57 | BioASQ, <https://www.bioasq.org/> |

## Deliberately not used

- **TUWEL**: login required, and off limits for this repo. Every TUWEL-hosted item (current slides, exercise sheets, exam dates, forum) is unknown.
- **VoWi page bodies** [S20]: blocked by bot protection; not circumvented.
- `github.com/tuwien-information-retrieval/air-24-template-public`: a student's AGPL copy of the 2023 template with Docker tooling; adds nothing to [S18].
- Levy & Goldberg (2014) on SGNS as implicit PMI factorisation: could not be verified from a stable URL on 2026-09-28, so the claim is not made.
