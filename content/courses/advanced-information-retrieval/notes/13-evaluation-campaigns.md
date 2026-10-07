# 13 Special topics I: evaluation campaigns (TREC, MS MARCO, CLEF) and leaderboards

An evaluation campaign fixes a task, a collection and a deadline; participants
submit runs; the organisers pool, judge and publish a comparison. Since at
least 2025S the course's exercise **is** participation in one, with a
leaderboard [S1, S21], and the exam's paper portion is written in this
vocabulary [S19, S53].

## Definitions

1. **TREC** (Text REtrieval Conference, organised by NIST, annual) [S54]: tracks (ad hoc, web, deep learning, COVID, ...); topics with title, description and narrative; participants submit up to a fixed number of runs; NIST pools and judges; results in an overview paper [S7 sl. 9].
2. **Run file** (TREC format): one line per retrieved document, `qid Q0 docid rank score run_tag`; qrels: `qid 0 docid grade`.
3. **Reusable test collection**: judgements good enough to evaluate systems that did not contribute to the pool (depends on pool depth and diversity).
4. **MS MARCO** [S44, S55]: 1,010,916 real Bing questions; 8,841,823 passages from 3,563,535 documents; about one judged relevant passage per query (sparse) for more than 500k training queries; a public leaderboard that became very popular (more than 100 entries) and fuelled the neural shift [S8 'MS MARCO', 'Importance of MS MARCO'].
5. **TREC Deep Learning track** (2019-) [S45, S46]: MS MARCO corpora, a few dozen test queries judged densely by pooling (43 in 2019, 54 in 2020 [S8 'TREC Deep Learning Track']); 2019: 15 groups, 75 runs, deep learning runs significantly outperformed traditional ones [S45].
6. **CLEF labs**: the European counterpart; the 2025S exercise used LongEval (Sci-Retrieval on the CORE collection, click-model qrels) and BioASQ Task 13b (biomedical semantic QA over PubMed) [S21, S56, S57].
7. **Leave-one-run-out test** [S27]: remove one run's unique pool contributions, re-evaluate that run; the drop measures how much the collection favours contributors.
8. **bpref** [S28]: $\frac1R\sum_{r}\bigl(1-\frac{\min(|\{n\text{ judged non-rel above }r\}|,\,R)}{R}\bigr)$ over retrieved relevant $r$; ignores unjudged documents, so it is robust to incomplete judgements.
9. **Kendall's $\tau$** between two system orderings: $\tau=\frac{C-D}{\binom{n}{2}}$ ($C$ concordant, $D$ discordant pairs).

## Results

**MS MARCO's limitations** [S8 'Limitations of MS MARCO']: the passage corpus was built from the top-10 Bing passages of sampled queries (possibly easier than a web-scale index); question-style queries; English only; sparse judgements miss many relevant passages (mitigated by the large query count).

**Sparse vs dense labels agree, but not at the top.** TREC DL 2020 found a clear correlation between system orderings under MS MARCO's sparse labels and TREC's dense ones; small differences between top systems cannot be resolved with about 50 queries: "continue to use the sparse labels if we do not overclaim small differences" [S8 'TREC-DL 2020: Sparse vs. Dense Judgements', S46].

**What a campaign is for.** The goal is not the top score but robust, widely usable techniques; campaign design choices (training data, pooling, query selection, leaderboard rules) can encourage or discourage that and create internal and external validity problems [S71].

**Synthetic test collections.** LLM-generated queries and judgements can yield collections that rank systems reliably (high $\tau$ against human-built ones), with a measurable risk of bias towards LLM-based systems [S53]; this was the 2024 exam paper [S19].

## Worked examples

**Pool bias, simulated** (`evaluation_campaign.py`, 3000 documents, 50 queries, 20 relevant per query of which 40 % lexically mismatched; 10 lexical runs contribute to a depth-20 pool; one "novel" run does not):

| | value |
|---|---|
| judged per query | 167 documents (5.6 % of the collection), 64 % of all relevant documents found |
| novel run, MAP with complete judgements | 0.270, **rank 3** |
| novel run, MAP with pooled judgements | 0.189, **rank 7** |
| novel run, bpref with pooled judgements | 0.517 (rank 1: unjudged documents are skipped, not counted wrong) |
| contributors, $\tau$(full MAP, pooled MAP) | 1.000 (their order is preserved) |
| contributors, pooled MAP vs full | inflated (e.g. best run 0.341 $\to$ 0.526: $R_q$ shrinks to the judged relevant) |
| leave-one-run-out MAP drop | mean 0.006, max 0.010 (small: contributors are similar) |

Lesson: the collection is fair to systems like its contributors and unfair to a new family. The leave-one-run-out test on contributors does **not** detect it, because they share blind spots. Pool depth and **diversity** matter [S8 'Pooling in IR'].

**Kendall $\tau$.** Full-judgement order A > B > C > D, pooled order A > C > B > D. Of $\binom42=6$ pairs one (B, C) is discordant: $\tau=(5-1)/6=0.667$.

## Practical notes for the course's campaign

- Read the lab overview of the previous year first: task, collection, qrels origin (human, click model, LLM), official metric and cutoff.
- Validate run files against the official format before the deadline; a wrong `Q0` column or duplicate documents per query can void a run.
- Keep a held-out split of the training queries; tune on it, never on the leaderboard (repeated submissions overfit the test queries).
- Report significance against the baseline over queries (note 04), and effect sizes, not only the leaderboard rank.
- The 2025S student projects used BM25 (with a parameter grid), dense retrieval (SciBERT, ColBERTv2 via RAGatouille, SentenceTransformers), and a BM25 + neural re-ranking hybrid, evaluated with `ir_measures` [S21]: the three pipelines of notes 03, 11 and 10.

## Pitfalls

- A leaderboard score is a point estimate on a query sample; two adjacent systems are often not significantly different.
- Pooled MAP of contributors is inflated relative to complete judgements; compare systems under the same qrels only.
- Click-model or LLM qrels are labels with their own biases, not ground truth [S53].
- Test-collection quality is not inter-annotator agreement [S19]; reusability is about pools.
- Unjudged documents: `trec_eval`-style metrics treat them as non-relevant; bpref and condensed-list metrics skip them. Know which you report.

## Questions

**Q:** Describe how TREC builds a test collection and why the result can be biased.
**A:** Participants submit runs; the top-$k$ of each run are pooled and judged by assessors; unjudged documents count as non-relevant. Systems that retrieve relevant documents outside the pool (new model families) are under-scored.

**Q:** What are MS MARCO's main limitations as a test collection?
**A:** Sparse labels (about one relevant per query), passages drawn from Bing's top-10 per query, question-style English queries only [S8].

**Q:** What did TREC DL find about sparse vs dense judgements?
**A:** System orderings correlate clearly, but small differences at the top cannot be resolved with ~50 queries; do not overclaim small differences under sparse labels [S8, S46].

**Q:** Compute Kendall's $\tau$ for orders A>B>C>D and B>A>D>C.
**A:** Discordant pairs (A,B) and (C,D): $\tau=(4-2)/6=0.333$.

**Q:** Why is bpref more robust than MAP to incomplete judgements?
**A:** It only counts judged non-relevant documents ranked above relevant ones and ignores unjudged documents, whereas MAP treats unjudged documents as non-relevant [S28].

## Code

[`../src/py/evaluation_campaign.py`](../src/py/evaluation_campaign.py): `simulate` (complete ground truth, lexical family + one novel run), `pool(runs, systems, depth)`, `pooled_qrels`, `bpref`, `map_score`, `leaderboard(camp, qrels, judged)`, `leave_one_out`, `rank_of`. Tests: pooling is the union of top-$k$; P@$k$ exact for contributors when $k\le$ depth; pool bias demoted the novel run by at least 3 places; including it in the pool removes the bias; bpref by hand. `metrics.kendall_tau`, `metrics.paired_t_test` for the leaderboard statistics.
