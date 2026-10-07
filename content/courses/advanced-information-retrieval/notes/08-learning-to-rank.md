# 08 Neural IR I: learning to rank, pairwise losses, the training workflow

Every neural ranker in notes 09-12 is trained the same way: score
(query, document) pairs, compare scores of documents with different labels,
evaluate the sorted list [S12 sl. 7-16]. This note is that shared machinery.

## Definitions

1. **Learning to rank (LTR)**: learn $s_\theta(q,d)$ from labelled data so that sorting by $s_\theta$ maximises a ranking metric. Classic LTR uses hand-made features (BM25 score, clicks, recency, source quality) with regression, SVMs or trees; text-based neural models are "another signal" of this kind [S12 sl. 3].
2. **Pointwise**: regress or classify each $(q,d)$ label independently, e.g. binary cross-entropy on relevant vs non-relevant (monoBERT [S35]).
3. **Pairwise**: learn from pairs $d^+\succ d^-$ of the same query:
   - margin (hinge) loss $\ell=\max(0,\ m-s^++s^-)$, $m=1$; `torch.nn.MarginRankingLoss` [S12 sl. 15];
   - RankNet [S49]: $P(d_i\succ d_j)=\sigma(s_i-s_j)$, cross-entropy against the target; for a known preference $\ell=-\log\sigma(s_i-s_j)=\log(1+e^{-(s_i-s_j)})$ [S12 sl. 15].
4. **Listwise**: a loss over the whole candidate list, e.g. softmax cross-entropy $-\log\frac{e^{s^+}}{\sum_j e^{s_j}}$ (the in-batch loss of note 11 is this, over a batch).
5. **LambdaRank** [S72, not retrieved]: use RankNet's pair gradient scaled by the metric change of swapping the pair, $\lambda_{ij}=-\sigma(-(s_i-s_j))\,|\Delta\mathrm{nDCG}_{ij}|$.
6. **Training triple** $(q,d^+,d^-)$: two forward passes per triple, one loss; batches mix queries (typical batch 16-128 triples) [S12 sl. 11-12].
7. **Negative sampling**: collections label (few) relevant documents only. Standard recipe: run BM25, take the top 1000 per training query, sample from those not labelled relevant [S12 sl. 13].
8. **Re-ranking evaluation**: score each candidate tuple, sort, compute MRR@10 etc. per query [S12 sl. 16].

## Results

**RankNet gradient.** With $z=s_i-s_j$ and $d_i\succ d_j$: $\partial\ell/\partial s_i=-(1-\sigma(z))=-\sigma(-z)$, $\partial\ell/\partial s_j=+\sigma(-z)$. Well-ordered pairs with a large margin contribute almost nothing; badly ordered pairs contribute up to 1. The hinge loss has gradient exactly 0 once $s^+-s^-\ge m$: training stops caring about easy pairs.

**Why pairwise and not pointwise.** Ranking depends only on score differences within a query. Pointwise losses spend capacity on calibrating absolute scores across queries (an easy query's non-relevant document may deserve a higher score than a hard query's relevant one). Pairwise losses are invariant to per-query shifts.

**Why the metric is not the loss.** MRR, AP, nDCG are piecewise constant in the scores (they change only when two documents swap), so their gradient is 0 almost everywhere. Pairwise and listwise losses are smooth surrogates; LambdaRank reweights the surrogate by the metric's sensitivity. Consequence: "you cannot really compare training loss and IR evaluation metric"; monitor the metric on validation queries, and use the loss only to see that training is not broken [S12 sl. 16].

**Negatives decide what is learned.**
- BM25 negatives have lexical overlap with the query, so the model must learn more than term matching; a bit of label noise is tolerable [S12 sl. 13].
- **False negatives break training.** Sampling non-clicked results from click logs as negatives (many are relevant) made training fail on TripClick, while BM25 negatives worked [S12 sl. 14].
- Graded labels are lost by binary triples: a grade-2 document sampled as a negative for a grade-3 positive is taught as "irrelevant". In the planted collection this shows up as a higher MRR (grade 3 on top) with a lower graded nDCG for the `log` KNRM (note 09).

## Worked examples

**RankNet.** $s_i=2$, $s_j=1$, $d_i\succ d_j$: $P=\sigma(1)=0.731$, $\ell=0.313$, $\partial\ell/\partial s_i=-0.269$, $\partial\ell/\partial s_j=+0.269$. Hinge with $m=1$: $\max(0,1-1)=0$, gradient 0.

**LambdaRank weight.** A query with judged grades $\{3,2,0,0\}$, $IDCG=3+2/\log_23=4.262$ (linear gain). The current list has a grade-0 document at rank 1 and the grade-3 document at rank 4. Swapping them changes DCG by $(3-0)\bigl(\frac1{\log_22}-\frac1{\log_25}\bigr)=3(1-0.431)=1.708$, so $|\Delta\mathrm{nDCG}|=0.401$: this pair's RankNet gradient is multiplied by 0.401, while a swap between ranks 9 and 10 would get a factor near 0.

**Training on the planted collection** (`knrm.experiment`, 300 steps of 32 triples, BM25 negatives from the top 30): margin loss $0.986\to0.147$ in 1.8 s on a CPU, while test MRR@10 moves $0.577\to0.708$. The loss says training works; only the metric says how well.

## Pitfalls

- Negatives from the same query only. Negatives from other queries are "easy" and teach topic detection, not ranking (in-batch negatives in dense retrieval are this, deliberately, note 11).
- Sampling negatives from far down the BM25 list (rank 900) vs near the top (rank 5) are different curricula; say which.
- Training on sparse labels (one relevant per query, MS MARCO) means many unlabelled relevant documents are in the negative pool: accept the noise, or denoise with a teacher (note 12).
- Early stopping on validation MRR, not on training loss [S17, S18].
- A re-ranker is evaluated with the first stage fixed. Changing the candidate depth changes the result; the lecture uses the "re-ranking threshold" (depth sweep) as a diagnostic [S12 sl. 44].

## Questions

**Q:** Contrast pointwise, pairwise and listwise LTR.
**A:** Pointwise: loss per $(q,d)$ label, needs calibrated scores. Pairwise: loss per preference pair of one query, invariant to per-query shifts (hinge, RankNet). Listwise: loss over the whole ranked list or its softmax (ListNet-style cross-entropy, LambdaRank's metric-weighted gradients).

**Q:** Derive the RankNet gradient for a pair with $d_i\succ d_j$.
**A:** $\ell=\log(1+e^{-z})$, $z=s_i-s_j$; $\partial\ell/\partial s_i=-\frac{e^{-z}}{1+e^{-z}}=-\sigma(-z)$, $\partial\ell/\partial s_j=\sigma(-z)$.

**Q:** Why can we not train directly on nDCG?
**A:** It is piecewise constant in the scores: zero gradient almost everywhere, undefined at ties. Use a smooth surrogate (pairwise or listwise), optionally reweighted by $|\Delta\mathrm{nDCG}|$ (LambdaRank).

**Q:** How are non-relevant training documents usually obtained, and how can this go wrong?
**A:** Sample from BM25's top 1000 for the training query, excluding labelled relevant ones. It fails when the sampled negatives are often actually relevant, e.g. non-clicked results from click logs [S12 sl. 13-14].

**Q:** Why is the training loss a poor progress indicator for a re-ranker?
**A:** The loss is on sampled triples, the metric on full candidate lists; the loss can keep falling (memorising training queries) while validation MRR stalls or drops, so select models on validation MRR [S12 sl. 16].

## Code

- [`../src/py/knrm.py`](../src/py/knrm.py): `make_triples` (BM25-candidate negatives), `train` (Adam, `MarginRankingLoss`), `rerank`, `evaluate`.
- [`../src/py/bert_reranker_sketch.py`](../src/py/bert_reranker_sketch.py): `train_step` (the hinge loss written out).
- [`../src/py/dense_retrieval.py`](../src/py/dense_retrieval.py): `in_batch_loss` (listwise over the batch).
