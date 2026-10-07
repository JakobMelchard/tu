# Lecture map: public AIR lectures (2021/2022) onto these notes and the code

The only public lecture series of this course is Hofstätter's 2021/2022 one
[S4]: 11 lectures, slides (GPL-3.0 repository), YouTube recordings [S16] and
corrected transcripts. The 2026S lecturers' material is in TUWEL and not
public; TISS's 2026S ECTS breakdown (intro, 3 crash-course IR, 3 NLP, 5 neural
IR, special topics [S2]) matches this series' structure, so it is the best
public proxy. Slide numbers are the printed ones.

| lecture [S4] | slides | content | note | code |
|---|---|---|---|---|
| 0 Introduction 2022 [S5] | 14-16 | syllabus: crash course, representation learning, neural IR | [01](../notes/01-introduction.md) | - |
| | 23-29 | exercises, online exam, grading 2022 | [00](../notes/00-exam-focus.md) | - |
| 1 Crash course: fundamentals [S6] | 8-22 | inverted index, tokenisation, stemming, query types | [02](../notes/02-indexing-and-preprocessing.md) | `inverted_index.py` |
| | 27-29 | dictionary data structures | 02 | - |
| | 41-55 | relevance, TF, DF, IDF, TF-IDF | [03](../notes/03-ranking-tfidf-bm25-query-likelihood.md) | `InvertedIndex.score_taat`, `topk_daat` |
| | 67-75 | BM25, saturation, example, hyperparameters, BM25F | 03 | `bm25.py` `BM25`, `lecture_example` |
| 2 Crash course: evaluation [S7] | 3-13 | offline/online, test collections, judgement types | [04](../notes/04-evaluation-and-test-collections.md) | - |
| | 14-27 | MRR, MAP, graded labels, nDCG, worked examples | 04 | `metrics.py` (tests reproduce sl. 18, 20, 27) |
| | 29-31 | significance, multiple testing, non-determinism | 04 | `paired_t_test`, `randomisation_test`, `bonferroni` |
| 3 Crash course: test collections [S8] | 'MS MARCO' to 'TREC-DL 2020' | MS MARCO, its limits, TREC DL, sparse vs dense | [13](../notes/13-evaluation-campaigns.md) | - |
| | 'Creating IR Test Collections' to 'Evaluate Annotation Quality' | task design, crowdsourcing, majority voting, kappa | 04 | - |
| | 'Pooling in IR' to 'Annotating for Recall' | pooling, pool bias, recall | 04, 13 | `evaluation_campaign.py` |
| | 'FiRA' to end | FiRA, biases in data and models | 13, 15 | - |
| 4 Word representation learning [S9] | 9-19 | embeddings, word2vec, fastText, similarity, analogies | [06](../notes/06-word-embeddings.md), [05](../notes/05-tokenisation-and-subwords.md) | `word2vec_toy.py` |
| | 21-28 | limitations, query expansion, topic shift, retrofitting | 06 | - |
| 5 Sequence modelling [S10] | 5-17 | 1D CNN, pooling, character embeddings | [07](../notes/07-sequence-models.md) | `knrm.ConvKNRM` |
| | 18-40 | RNN, LSTM, encoder-decoder, beam search, attention, pointer-generator | 07 (+ ADL 03) | - |
| 6 Transformer and BERT [S11] | 4-26 | self-attention, MLM, BERT input and workflow, HuggingFace | [10](../notes/10-transformer-reranking.md) (+ ADL 06) | `bert_reranker_sketch.py` |
| | 27-32 | extractive QA, datasets, training, open-domain QA | [15](../notes/15-extractive-qa.md) | `best_span` |
| 7 Introduction to neural re-ranking [S12] | 3-18 | workflow, training triples, batches, negatives, losses, evaluation | [08](../notes/08-learning-to-rank.md) | `knrm.make_triples`, `train` |
| | 19-28 | encoding layer, match matrix, cosine, MatchPyramid | [09](../notes/09-neural-reranking-kernel-pooling.md) | `KNRM.match_matrix` |
| | 29-40 | KNRM, kernels, implementation details, Conv-KNRM | 09 | `kernel_pooling`, `KNRM`, `ConvKNRM` |
| | 43-47 | low-frequency terms, vocabulary, fastText | 05, 09 | `Encoder` (OOV) |
| 8 Transformer contextualised re-ranking [S13] | 5-14 | BERT_CAT, effectiveness, mono-duo, long documents, inefficiency | 10 | `TinyCrossEncoder` |
| | 15-27 | PreTTR, ColBERT, TK, comparing models | 10, [11](../notes/11-dense-retrieval-and-late-interaction.md), [12](../notes/12-efficiency-and-distillation.md) | `param_count_formula` |
| | 28-41 | TK analysis, TK-Sparse, TKL, IDCM | 10, 12 | - |
| 9 Domain-specific applications [S14] | 3-31 | medical and legal IR, campaigns, challenges, BERT-PLI | [14](../notes/14-domain-specific-ir.md) | - |
| 10 Dense retrieval and knowledge distillation [S15] | 3-18 | BERT_DOT, in-batch negatives, ANCE, NN search, production | 11 | `dense_retrieval.py` |
| | 19-34 | KD, DistilBERT, Margin-MSE, dual supervision, TAS-B | 12 | `margin_mse` |
| | 35-43 | BEIR zero-shot, lexical matching, where BM25 wins | 11, 14 | - |

**Exercises** [S17, S18] map onto notes 08, 09, 13, 15 and the modules `knrm.py`
(KNRM re-ranking with BM25 candidates and early stopping on validation MRR),
`evaluation_campaign.py` (judgement aggregation and qrels), `bert_reranker_sketch.best_span`
(extractive QA decoding). The 2025S exercise (a CLEF lab with BM25, dense and
re-ranking pipelines [S21]) maps onto `bm25.py`, `dense_retrieval.py`, `knrm.py`.
