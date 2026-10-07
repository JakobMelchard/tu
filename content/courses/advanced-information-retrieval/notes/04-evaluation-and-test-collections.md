# 04 Crash course III: evaluation with test collections

Offline evaluation compares systems on a fixed **test collection**: documents,
queries (topics) and relevance judgements (qrels). This is the Cranfield
paradigm, and every leaderboard in the course, including the one in the
exercise, runs on it [S7, S8, S22 ch. 8]. Past exams asked about exactly these
definitions [S19].

## Definitions

1. **Qrels**: judged $(q,d,rel)$ triples. **Run**: a system's ranked list per query (TREC format `qid Q0 docid rank score tag`).
2. **Sparse judgements**: about one judged relevant per query, many queries (MS MARCO train/dev: noisy, cheap). **Dense judgements**: 100+ judged per query, few queries (TREC: 50+, better 200+) [S7 sl. 10].
3. **Pooling**: judge only the union of the top-$k$ ("pool depth") of many diverse runs; unjudged documents are treated as non-relevant [S8 'Pooling in IR', 'Pooling Process'].
4. **Pool bias**: a later system retrieving relevant but unjudged documents is under-scored [S8 'Pool Bias'].
5. **Inter-annotator agreement**, Cohen's $\kappa=\dfrac{p_o-p_e}{1-p_e}$ ($p_o$ observed agreement, $p_e$ agreement expected by chance from the marginals); Fleiss' $\kappa$ for more than two annotators. Rough reading: $\ge0.8$ strong, $0.6$-$0.79$ moderate, $0.4$-$0.59$ weak, and task-dependent [S8 'Evaluate Annotation Quality'].
6. Metrics for query $q$ with ranking $d_1,d_2,\dots$, binary $r_i=rel(q,d_i)$, $R_q$ = number of relevant documents of $q$:
   - $P@k=\frac1k\sum_{i\le k}r_i$, $\ R@k=\frac1{R_q}\sum_{i\le k}r_i$.
   - $RR=1/\text{rank of the first relevant}$ (0 if none within the cutoff); $MRR=\frac1{|Q|}\sum_q RR_q$ [S7 sl. 16].
   - $AP=\frac1{R_q}\sum_{i}P@i\cdot r_i$ (relevant documents never retrieved contribute 0); $MAP=\frac1{|Q|}\sum_qAP_q$. The "M" is the mean over **queries** [S7 sl. 19].
   - $DCG@k=\sum_{i\le k}\frac{g(rel_i)}{\log_2(i+1)}$, lecture gain $g(x)=x$; common alternative $g(x)=2^x-1$ [S25]. $nDCG@k=DCG@k/IDCG@k$, IDCG from all judged grades of $q$ sorted descending [S7 sl. 24-25].
7. **Cutoffs**: MAP and recall at 100 or 1000; P, MRR, nDCG at 5, 10, 20 [S7 sl. 14].

## Results

**AP is the area under the (uninterpolated) precision-recall curve.** Recall jumps by $1/R_q$ exactly at relevant ranks, where precision is $P@i$; the Riemann sum is $\sum_i P@i\cdot\frac{r_i}{R_q}$.

**Discounts compared.** MRR's weight $1/i$ vs nDCG's $1/\log_2(i+1)$: at rank 3, $0.33$ vs $0.5$; at rank 10, $0.1$ vs $0.29$. nDCG discounts less steeply [S7 sl. 26].

**Paired significance tests** [S7 sl. 29-30, S26]. Per-query differences $\delta_q=m_A(q)-m_B(q)$, $H_0$: $\mathbb E\delta=0$.
- Paired $t$: $t=\bar\delta/(s_\delta/\sqrt n)$, $n-1$ degrees of freedom, relies on the CLT for $\bar\delta$.
- Randomisation (permutation) test: under $H_0$ the labels A/B are exchangeable per query, so flip each $\delta_q$'s sign at random; $p=P(|\overline{\pm\delta}|\ge|\bar\delta|)$. Exact by enumeration for small $n$, no distributional assumption. Smucker et al. recommend it (with $t$ as a close second) over sign and Wilcoxon tests for IR [S26].
- **Multiple comparisons**: $m$ tests at level $\alpha$ give $P(\text{some false positive})\le m\alpha$; Bonferroni tests each at $\alpha/m$ [S7 sl. 30].
- At least 50 queries for the tests to be meaningful [S7 sl. 30]; neural models also vary with the random seed: report mean over seeds or fix seeds [S7 sl. 31].

## Worked examples

**The lecture's three systems** [S7 sl. 18, 20, 27]. Two relevant documents: $x$ (grade 3) and $y$ (grade 1). A ranks $y,\cdot,x$; B ranks $\cdot,\cdot,y$; C ranks $\cdot,x,y$.

| | RR | AP | DCG | nDCG |
|---|---|---|---|---|
| A | $1$ | $(1+\frac23)/2=0.833$ | $1+\frac{3}{\log_24}=2.5$ | $2.5/3.631=0.689$ |
| B | $\frac13$ | $\frac13/2=0.167$ | $\frac1{2}=0.5$ | $0.138$ |
| C | $\frac12$ | $(\frac12+\frac23)/2=0.583$ | $\frac3{\log_23}+\frac12=2.393$ | $0.659$ |

with $IDCG=3+1/\log_23=3.631$. Note A beats C on AP and nDCG despite placing the grade-3 document lower: A found a relevant document first.

**Significance with four queries.** $A=(0.5,0.6,0.7,0.4)$, $B=(0.4,0.5,0.5,0.4)$, $\delta=(0.1,0.1,0.2,0)$, $\bar\delta=0.1$, $s_\delta=\sqrt{0.02/3}=0.0816$, $t=0.1/(0.0816/2)=\sqrt6=2.449$, $p=0.092$ (3 df). The exact randomisation test: of $2^4=16$ sign patterns, 4 reach $|\bar\delta|\ge0.1$ (all $+$ or all $-$, times 2 for the zero difference), $p=0.25$. Same data, very different $p$: with $n=4$ the $t$-test's normality assumption carries the result.

**Cohen's $\kappa$.** 100 pairs; both say relevant 40, both non-relevant 30, A yes/B no 20, A no/B yes 10. $p_o=0.7$; marginals A yes 0.6, B yes 0.5, $p_e=0.6\cdot0.5+0.4\cdot0.5=0.5$; $\kappa=(0.7-0.5)/0.5=0.4$: weak, despite 70 % raw agreement.

## Pitfalls

- MAP's normaliser is $R_q$, **not** the number retrieved. A run retrieving one relevant document at rank 1 out of 10 relevant has AP 0.1, not 1.
- nDCG's ideal ranking uses **all** judged grades of the query, not only the retrieved ones. Otherwise a run retrieving only junk could score 1.
- Linear vs exponential gain changes nDCG values and can change system orders; evaluation tools differ in their default. State which one you report.
- Significance is a statement about a **comparison of two systems on a query sample**, not a property of a test collection [S19].
- Inter-annotator agreement measures **label quality**, not the quality or reusability of a test collection [S19]; reusability is about pool depth and diversity.
- Pooling from similar systems produces a pool that misses what a different family finds (note 13, `evaluation_campaign.py`).
- Training loss is not the evaluation metric; watch MRR@10 on validation, not the loss [S12 sl. 16].

## Questions

**Q:** Define MRR and MAP. Over what is the "M" taken?
**A:** Means over the query set of reciprocal rank and average precision. RR uses only the first relevant document; AP averages $P@i$ over relevant positions and divides by all relevant documents of the query.

**Q:** Why is nDCG normalised, and what is the ideal DCG?
**A:** DCG depends on how many and how relevant the judged documents of a query are, so raw DCG is not comparable across queries. IDCG is the DCG of all judged documents sorted by grade; nDCG $\in[0,1]$.

**Q:** Explain pooling and pool bias.
**A:** Judge only the union of the top-$k$ of many runs, treat the rest as non-relevant; cheap and nearly unbiased for contributing runs. A system that did not contribute and finds different relevant documents gets them counted as non-relevant, so it is under-scored.

**Q:** Why paired tests, and why correct for multiple comparisons?
**A:** Query difficulty varies far more than system differences; pairing removes the query effect. Testing many pairs at $\alpha$ inflates the family-wise false-positive rate up to $m\alpha$; Bonferroni divides $\alpha$ by $m$.

**Q:** At which cutoffs are recall and MAP typically reported, and at which nDCG and MRR?
**A:** Recall and MAP at 100 or 1000 (depth of the candidate list); MRR, P and nDCG at 5, 10 or 20 (what a user sees) [S7 sl. 14].

## Code

[`../src/py/metrics.py`](../src/py/metrics.py): `precision_at_k`, `recall_at_k`, `reciprocal_rank`, `average_precision`, `dcg`, `ndcg_at_k(ranking, grades, k, exp_gain)`, `paired_t_test` (hand, cross-checked with `scipy.stats.ttest_rel`), `randomisation_test` (checked against exact enumeration), `bonferroni`, `kendall_tau`. Tests reproduce the lecture's numbers above and scikit-learn's `average_precision_score` and `ndcg_score`.
[`../src/py/evaluation_campaign.py`](../src/py/evaluation_campaign.py): pooling and pool bias (note 13).
