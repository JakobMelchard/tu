# Notes: 188.980 Advanced Information Retrieval

Preparation for **2027S** (the 2027S TISS page is not published; everything
course-specific is the 2026S pattern [S1]). Ordered by the ECTS breakdown on
TISS: introduction, 3 crash-course IR, 3 NLP, 5 neural IR, special topics [S2].
Each topic note has definitions, a worked numeric example, pitfalls, five
exam-style questions with answers, and pointers into [`../src/py`](../src/README.md).
Every claim is cited `[S<n>]` against [`../refs/SOURCES.md`](../refs/SOURCES.md);
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md) maps the public
2022 lectures onto these notes.

**Start with [00](00-exam-focus.md)**: the course is **not in the QIST curriculum** on TISS (free elective only), and that must be decided before registering.

| # | Note | One line |
|---|---|---|
| **00** | [**Exam focus**](00-exam-focus.md) | **Read first.** Status 2026-09-28, curriculum warning, assessment eras 2019-2026 (take-home paper exam, true/false with a paper, CLEF-lab exercise), past-question themes, January 2027 checklist. |
| 01 | [Introduction](01-introduction.md) | Relevance, ad hoc retrieval, first stage vs re-ranking, why re-ranking exists (cost arithmetic on MS MARCO), course map. |
| 02 | [Inverted index and preprocessing](02-indexing-and-preprocessing.md) | Tokenisation, stop words, stemming, postings, linear merges, TAAT vs DAAT, Zipf and Heaps, gap + variable-byte compression. |
| 03 | [Ranking: TF-IDF, BM25, query likelihood](03-ranking-tfidf-bm25-query-likelihood.md) | Lecture formulas, BM25 from the eliteness model, negative idf, Dirichlet QL as TF-IDF, hand-computed scores, vocabulary mismatch measured. |
| 04 | [Evaluation and test collections](04-evaluation-and-test-collections.md) | Cranfield, sparse vs dense qrels, pooling, kappa, P/R/MRR/MAP/nDCG with the lecture's example, paired $t$ vs randomisation test, Bonferroni. |
| 05 | [Tokenisation and subwords](05-tokenisation-and-subwords.md) | Word vocabularies and OOV, fastText n-grams, WordPiece greedy encoding, why low-frequency terms matter more in IR (cross-links ADL 09 for BPE). |
| 06 | [Word embeddings](06-word-embeddings.md) | Skip-gram softmax and negative-sampling gradients derived, one SGNS step by hand, GloVe, analogies and their caveat, query expansion and topic shift. |
| 07 | [Sequence models](07-sequence-models.md) | 1D CNNs as n-gram encoders, pooling with masks, LSTM cell path, encoder-decoder attention by hand (cross-links ADL 02, 03, 06). |
| 08 | [Learning to rank](08-learning-to-rank.md) | Point/pair/listwise, hinge and RankNet gradients, LambdaRank weight by hand, negative sampling and how it breaks, loss vs metric. |
| 09 | [Neural re-ranking: KNRM, Conv-KNRM](09-neural-reranking-kernel-pooling.md) | Match matrix, kernel pooling by hand, $\log$ vs $\log(1+\cdot)$, masking, results on the planted collection (MRR 0.577 to 0.708/0.751). |
| 10 | [Transformer re-ranking](10-transformer-reranking.md) | BERT_CAT, mono-duo, long documents, PreTTR, TK, the efficiency design-space table, 110 M parameters and 35 TFLOPs per query derived, why pre-training matters (from-scratch 0.312). |
| 11 | [Dense retrieval vs late interaction](11-dense-retrieval-and-late-interaction.md) | Bi-encoders, in-batch negatives and gradient, ANCE, IVF, LSH collision law derived, HNSW/PQ, ColBERT MaxSim, index sizes, BEIR. |
| 12 | [Efficiency and distillation](12-efficiency-and-distillation.md) | Efficiency axes, time budgets, KD with temperature, Margin-MSE and its shift invariance, TAS-B, dual supervision. |
| 13 | [Evaluation campaigns](13-evaluation-campaigns.md) | TREC, MS MARCO, TREC DL, CLEF labs (LongEval, BioASQ), run files, pool bias simulated, bpref, Kendall $\tau$, practical campaign advice. |
| 14 | [Domain-specific IR](14-domain-specific-ir.md) | Medical (systematic reviews, TREC-COVID), legal (case law, eDiscovery), domain LMs, recall-oriented evaluation arithmetic. |
| 15 | [Extractive QA](15-extractive-qa.md) | Span prediction with BERT, loss, constrained decoding by hand, EM/F1, open-domain QA. |

Suggested order before March 2027: 00, then 02-04 (the crash course, with the
Hofstätter lectures 1-3 [S6-S8]), 05-07, then 08-12 (the exercise), 13 before
the campaign starts, 14-15 last.

**Related material in this repo, deliberately not duplicated:**
- [`introduction-to-information-retrieval`](../../introduction-to-information-retrieval/index.md): 194.166, the basics course. Notes 02-04 are the crash-course subset.
- [`cse/ws2026/applied-deep-learning/notes/06-transformers.md`](../../applied-deep-learning/notes/06-transformers.md) and [`09-llms.md`](../../applied-deep-learning/notes/09-llms.md): attention, transformer blocks, BPE, RAG; [`02-cnns.md`](../../applied-deep-learning/notes/02-cnns.md), [`03-rnns.md`](../../applied-deep-learning/notes/03-rnns.md).

Changes: `CHANGELOG.md`.
