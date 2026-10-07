# 01 Introduction: the retrieval problem and the neural pipeline

Information retrieval (IR) ranks items of an unstructured collection by their
relevance to an information need expressed as a query [S6 sl. 3-6, S22 ch. 1].
This course takes the classical machinery (inverted index, BM25, test
collections) as given in three "crash-course" lectures and spends the rest on
learned representations and neural ranking [S1, S2, S5 sl. 14]. This note fixes
vocabulary and the architecture that every later note plugs into.

## Definitions

1. **Collection** $D$: a set of documents (web pages, passages, abstracts). $|D|=N$.
2. **Information need**: what the user wants to know. **Query** $q$: its (lossy) expression as text, typically 2-10 words.
3. **Relevance**: a judgement $rel(q,d)$, binary $\{0,1\}$ or graded (TREC: 0 irrelevant, 1 relevant, 2 highly relevant, 3 perfectly relevant [S7 sl. 23]). Topical relevance is what test collections label; users also care about novelty, credibility, effort.
4. **Ad hoc retrieval**: a new query against a fixed collection, output a ranked list $\pi_q$ of the top $k$ documents.
5. **Ranking model / scoring function** $s(q,d)\in\mathbb R$; the ranking is $\pi_q=\operatorname{argsort}_d(-s(q,d))$. Only the order matters, so any strictly increasing transform of $s$ is the same model.
6. **First-stage retrieval** (candidate generation): cheap $s$ over all of $D$ via an index: BM25 over an inverted index, or a dense retriever over a vector index.
7. **Re-ranking**: an expensive $s$ applied to the top $k_1$ (e.g. 100-1000) candidates only [S12 sl. 7].
8. **Offline evaluation**: fixed collection, queries and judgements (a *test collection*); **online**: user behaviour, A/B tests [S7 sl. 3-4].
9. **Vocabulary mismatch**: relevant documents that use different words than the query ("car" vs "automobile"). Exact-match models score them 0; this is the main motivation for learned representations.

## The two-stage pipeline and its cost

$$\underbrace{D \xrightarrow{\ \text{index, }O(\text{postings})\ } \text{top-}k_1}_{\text{first stage}}\ \xrightarrow{\ k_1\text{ forward passes}\ }\ \underbrace{\text{top-}k_2}_{\text{re-ranked}}$$

Cost per query: first stage $\approx$ sum of postings-list lengths of the query
terms (sparse) or one encoder pass plus a nearest-neighbour search (dense);
re-ranking $k_1\times$ one model pass. Effectiveness is bounded by the first
stage's **recall@$k_1$**: a relevant document not in the candidates can never be
re-ranked up.

Desired properties of a neural IR model [S12 sl. 5]: effective, efficient
(latency and memory), and robust to the long tail of rare terms [S51].

## Worked example: why re-ranking exists

MS MARCO passage has $N=8{,}841{,}823$ passages [S44]. Suppose a cross-encoder
costs $t=1$ ms per (query, passage) pair on a GPU (an assumption of the right
order for BERT-base at 200 tokens; the lecture measured roughly 2 s per query
for 250 candidates, i.e. 8 ms per pair, including overheads [S13 sl. 14]).

- Scoring the whole collection: $8.84\times10^6\times1\text{ ms}=8840$ s $\approx 2.5$ h per query.
- Re-ranking BM25's top $k_1=1000$: $1$ s. Top 100: $0.1$ s.
- So the re-ranker is only feasible on candidates, and the choice of $k_1$ trades recall for latency. Note 12 formalises this as a time budget [S36].

## The course map

| block (TISS ECTS split [S2]) | lecture (2022 numbering [S4]) | note |
|---|---|---|
| introduction | 0 | 00, 01 |
| crash course IR ×3 | 1 fundamentals, 2 evaluation, 3 test collections | 02, 03, 04 |
| NLP ×3 | 4 word representations, 5 sequence modelling, 6 transformer and BERT | 05, 06, 07 (+ ADL 06) |
| neural IR ×5 | 7 neural re-ranking, 8 transformer re-ranking, 10 dense retrieval and distillation | 08, 09, 10, 11, 12 |
| special topics | 3 (campaigns), 9 domain-specific, 6 (extractive QA) | 13, 14, 15 |

## Pitfalls

- "Relevant" in a test collection means *judged* relevant. Unjudged is usually scored as non-relevant [S7 sl. 7]; note 04 and note 13 show when that biases results.
- A re-ranker's gain is measured on the first stage's candidates. Comparing a re-ranker on BM25 top-100 with a dense retriever on the full collection compares pipelines, not models.
- Scores from different models are not comparable in scale; only rankings are (this is why Margin-MSE exists, note 12).
- The query is not the information need: "jaguar" has several needs. Test collections resolve this by writing a narrative per topic (TREC) or by sampling real queries with one judged answer (MS MARCO) [S8, S44].

## Questions

**Q:** What is the difference between first-stage retrieval and re-ranking, and what bounds the effectiveness of the pipeline?
**A:** First stage scores all of $D$ cheaply via an index; re-ranking applies an expensive model to the top $k_1$. The pipeline cannot exceed the first stage's recall@$k_1$.

**Q:** Why is a strictly increasing transform of a scoring function the same ranking model?
**A:** Ranking uses only the order of $s(q,\cdot)$ for a fixed $q$; $g$ strictly increasing preserves every pairwise order. It is not the same if scores are compared across queries or combined with other scores.

**Q:** Give the cost of cross-encoding the full MS MARCO passage collection at 1 ms per pair, and of re-ranking the top 1000.
**A:** $8.84\times10^6$ ms $\approx 2.5$ h vs 1 s per query.

**Q:** What is vocabulary mismatch and which model families address it?
**A:** Relevant documents that share no terms with the query; exact-match models (TF-IDF, BM25, QL) give them no credit. Learned embeddings (soft matching in KNRM, dense retrieval) and query/document expansion address it.

**Q:** Name the TREC graded relevance scale.
**A:** 3 perfectly relevant, 2 highly relevant, 1 relevant, 0 irrelevant [S7 sl. 23].

## Code

- [`../src/py/corpus.py`](../src/py/corpus.py): `make_collection` builds the planted test collection used by every module: topics, facets, graded qrels, and aliases as planted vocabulary mismatch.
- [`../src/py/knrm.py`](../src/py/knrm.py): `experiment` is the full two-stage pipeline (BM25 top-30, then KNRM).
