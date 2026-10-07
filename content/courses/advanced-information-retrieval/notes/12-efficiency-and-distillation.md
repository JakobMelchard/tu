# 12 Neural IR V: efficiency and knowledge distillation

Effectiveness is bought with latency, memory and index size. Knowledge
distillation (KD) moves effectiveness from a slow teacher (BERT_CAT, ensembles)
into an efficient student (TK, ColBERT, BERT_DOT) without changing the
student's cost [S15 sl. 19-34, S40, S41].

## Definitions

1. **Efficiency axes**: query latency (ms per query, at batch size 1), throughput, index size (GB), indexing time, training cost (GPU hours), and hardware (GPU vs CPU serving) [S13 sl. 27, S15 sl. 17].
2. **Time budget** [S36]: a fixed latency per query (e.g. 200 ms); a model's effectiveness is judged at the candidate depth it can afford within the budget.
3. **Knowledge distillation** [S69]: train a student on a teacher's outputs. Classification form: $\mathcal L=\mathrm{CE}(y,\ p_s)+\lambda\,T^2\,\mathrm{KL}\bigl(p_t^{(T)}\,\|\,p_s^{(T)}\bigr)$ with $p^{(T)}=\mathrm{softmax}(z/T)$; a temperature $T>1$ exposes the teacher's "dark knowledge" in the non-maximal classes.
4. **Supervision levels** [S15 sl. 21]: output scores only (architecture-independent, teacher ensembles easy) vs intermediate activations/attention (more signal, locks the student to the teacher's architecture). DistilBERT distils during pre-training: 40 % smaller, 60 % faster, 97 % of BERT's language understanding [S68].
5. **Margin-MSE** [S40, S15 sl. 25]: for a triple $(q,p^+,p^-)$,
$$\mathcal L=\mathrm{MSE}\bigl(M_s(q,p^+)-M_s(q,p^-),\ M_t(q,p^+)-M_t(q,p^-)\bigr).$$
6. **TAS / TAS-Balanced** [S41, S15 sl. 30-31]: cluster training queries once; each batch samples queries from one cluster (harder in-batch negatives, no extra cost); TAS-B additionally samples positive-negative pairs balanced across margin bins, down-sampling easy large-margin pairs. Trained with dual supervision: a pairwise Margin-MSE teacher and an in-batch teacher (ColBERT) [S15 sl. 28].

## Results

**Why margins and not scores.** Different architectures produce scores in different ranges (BERT_CAT logits vs dot products of normalised vectors) [S15 sl. 24, S40]. Ranking only needs differences. Margin-MSE is invariant to adding any constant to both of a model's scores for a query: $(s^++c)-(s^-+c)=s^+-s^-$. So the student is free in its scale and offset; only the teacher's margins are matched. It also turns a binary label into a graded one: the teacher says *how much* better $p^+$ is, and teacher scores can be precomputed once for all training triples [S15 sl. 25].

**Why distillation fixes sparse labels.** MS MARCO has about one labelled relevant per query, and many "negatives" are unlabelled relevant passages [S15 sl. 20]. A teacher that scores a false negative high produces a small or negative target margin, so the student is not pushed to rank it low.

**Reported gains.** Margin-MSE from a BERT_CAT ensemble significantly improves TK, ColBERT, PreTT and BERT_DOT re-ranking effectiveness at unchanged efficiency [S40]. TAS-B trains a 6-layer dense retriever on one consumer GPU in under 48 h, 64 ms per query, and beats BM25 by 44 % and a plainly trained dense retriever by 19 % nDCG@10 on TREC DL [S41].

**Where the work is done.** Moving computation from query time to indexing time (PreTTR, ColBERT, BERT_DOT) trades storage for latency; making the query-time model smaller (TK, distilled students) trades effectiveness, which distillation buys back. Past exams asked to match architectures to these properties (note 10 table) [S19].

## Worked examples

**Margin-MSE.** Teacher scores $8.1$ and $5.3$ (margin $2.8$); student $0.92$ and $0.88$ (margin $0.04$). $\mathcal L=(0.04-2.8)^2=7.62$. The student scores are small because it is a normalised dot product: MSE on raw scores would demand an impossible scale, the margin does not. `test_margin_mse_shift_invariance`: margins $(1,-0.2)$ for both models give loss 0 whatever the offsets.

**Temperature.** Teacher logits $(4,2,0)$: $T=1$ gives $(0.867,0.117,0.016)$, nearly one-hot; $T=4$ gives $(0.506,0.307,0.186)$: the ranking among the non-top classes becomes visible to the student. The $T^2$ factor keeps gradient magnitudes comparable across $T$ [S69].

**Time budget.** At 1 ms per candidate for BERT_CAT and 0.05 ms for a TK-sized model (illustrative numbers), a 200 ms budget allows re-ranking 200 vs 4000 candidates. If BM25 recall@200 is well below recall@4000, the fast model can be more effective within the budget: TK's result [S36].

## Pitfalls

- "Efficient" without a measurement setup means nothing: state batch size, hardware, candidate depth, and whether encoding the passages is counted.
- A distilled student cannot exceed the teacher in general; it closes part of the gap. Ensembled teachers help [S15 sl. 21].
- Distillation with intermediate-layer losses constrains architectures; Margin-MSE uses only output scores and works across architectures [S40].
- Balanced sampling (TAS-B) changes the training distribution; it is not "more data".
- Latency at batch size 1 and throughput at large batch are different numbers; GPU brute force looks great in throughput and memory-bound in latency [S15 sl. 15].

## Questions

**Q:** Define Margin-MSE and state the property that makes it suitable for cross-architecture distillation.
**A:** MSE between student and teacher score margins $s^+-s^-$ and $t^+-t^-$; it is invariant to per-query shifts of either model's scores, so score ranges need not match [S40].

**Q:** What is knowledge distillation, and what does the temperature do?
**A:** Training a small student on a large teacher's outputs; softmax with $T>1$ spreads the teacher's distribution so the relative probabilities of wrong classes carry information; scale the KD term by $T^2$ [S69].

**Q:** What is Topic Aware Sampling, and why does it help in-batch negatives?
**A:** Queries are clustered once; a batch draws queries from one cluster, so the other passages in the batch are topically related and hence harder negatives, at no extra training cost [S41].

**Q:** Name three efficiency measures and one architecture that optimises each.
**A:** Query latency (BERT_DOT with ANN search; TK within a budget), index size (BERT_DOT single vector; ColBERTv2/ColBERTer compression), training cost (TAS-B: one consumer GPU, under 48 h) [S39, S41, S52].

**Q:** Why do sparse labels make distillation especially useful in IR?
**A:** With about one labelled relevant per query, many sampled negatives are unlabelled relevant; a teacher's graded margins soften these false negatives and add fine-grained information missing from binary labels [S15 sl. 20].

## Code

- [`../src/py/dense_retrieval.py`](../src/py/dense_retrieval.py): `margin_mse(s_pos, s_neg, t_pos, t_neg)`, tested for shift invariance.
- [`../src/py/knrm.py`](../src/py/knrm.py): an efficient student-sized model (trains in about 2 s on a CPU); `experiment` exposes candidate depth, the knob a time budget turns.
- [`../src/py/bert_reranker_sketch.py`](../src/py/bert_reranker_sketch.py): `param_count_formula` for size comparisons.
