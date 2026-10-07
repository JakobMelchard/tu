# 09 Neural IR II: neural re-ranking from scratch (MatchPyramid, KNRM, Conv-KNRM)

The first generation of IR-specific neural rankers, trained from scratch on
MS MARCO: an interaction matrix between query and document word vectors,
followed by a way to summarise it into a score. No longer state of the art, but
fast, small, and the model the exercise implemented from 2020 to at least 2023
[S12 sl. 4, S17, S18].

## Definitions

Query tokens $q_{1:n}$, document tokens $d_{1:m}$, embeddings $\mathbf q_i,\mathbf d_j\in\mathbb R^{e}$.

1. **Match matrix** $M_{ij}=\cos(\mathbf q_i,\mathbf d_j)$, $M\in[-1,1]^{n\times m}$ [S12 sl. 23-25].
2. **MatchPyramid** [S65]: treat $M$ as an image; 2D convolutions and dynamic pooling, then an MLP [S12 sl. 26-27].
3. **KNRM** [S33, S12 sl. 29-33]: $K$ RBF kernels with centres $\mu_k$ and widths $\sigma_k$,
$$K_k(M_i)=\sum_{j=1}^m\exp\Bigl(-\frac{(M_{ij}-\mu_k)^2}{2\sigma_k^2}\Bigr),\qquad \phi_k=\sum_{i=1}^n\log K_k(M_i),\qquad s=\mathbf w^\top\boldsymbol\phi+b.$$
   Standard kernels: $\mu=1$, $\sigma=10^{-3}$ (exact match) and $\mu\in\{0.9,0.7,\dots,-0.9\}$, $\sigma=0.1$: 11 kernels.
4. **Soft-TF**: $K_k(M_i)$ counts how many document tokens match query token $i$ at similarity level $\approx\mu_k$. The exact-match kernel is (almost) $tf_{q_i,d}$.
5. **Conv-KNRM** [S34, S12 sl. 37-40]: 1D CNNs of widths $h=1..H$ produce n-gram embeddings for query and document; all $H^2$ cross-matches ($h_q$-grams vs $h_d$-grams) are kernel-pooled; $K H^2$ features feed the linear layer.

## Results

**KNRM is a learned, soft BM25 skeleton.** With only the exact-match kernel and $\log$: $\phi=\sum_i\log tf_{q_i,d}$: a log-tf, conjunctive score. The other kernels add "soft tf" at lower similarity levels, and training tunes the embeddings so that the right words land in the right kernels ("kernel-guided embedding") [S33]. Parameters besides embeddings: $K+1$ (plus nothing else): very fast [S12 sl. 29].

**Why $\log$ then sum over query terms.** $\sum_i\log K_k(M_i)=\log\prod_iK_k(M_i)$: each query term must be matched for a high score (AND-like), unlike $\sum_i K_k(M_i)$ (OR-like). It also dampens tf like $\log(1+tf)$ in TF-IDF.

**Implementation details matter** [S12 sl. 35-36]. Two open-source KNRM variants differ only in $\log(1+\text{soft-TF})$ vs $\log(\text{soft-TF})$. On the lecture's MS MARCO setup the first did not learn (best MRR@10 0.186, same as BM25), the second did (0.221). Their explanation: with $\log(\text{soft-TF})$ a single exact occurrence contributes $\log1=0$, so single occurrences are ignored as noise (a regulariser), while zero occurrences give a large negative ($\log10^{-10}$, clamped).

**Padding must be masked after the kernel.** A padded position has $M_{ij}=0$ after cosine with a zero vector, and $\exp(-(0-\mu_k)^2/2\sigma_k^2)$ is not 0 ($e^{-0.5}=0.61$ for the $\mu=\pm0.1$ kernels): without the mask, longer padding raises the soft-TF [S18 hints]. `kernel_pooling` multiplies by the document mask inside the sum and by the query mask before summing over $i$.

## Worked examples

**Kernel pooling by hand** (`test_kernel_pooling_hand_computed`). One query token, similarities to three document tokens $(1.0,0.9,0.0)$.
- Exact kernel ($\mu=1,\sigma=10^{-3}$): $e^0+e^{-0.01/2\cdot10^{-6}}+\dots=1$; $\log1=0$.
- $\mu=0.9,\sigma=0.1$: $e^{-0.01/0.02}+e^0+e^{-0.81/0.02}=0.6065+1+2.6\cdot10^{-18}=1.6065$; $\log=0.474$.
- With the $0.01$ scaling of the reference code: $\boldsymbol\phi=(0,\,0.00474)$.

**Planted collection** (`knrm.py` demo; BM25 top-30 of 60 held-out queries; 740 training queries; CPU):

| model | train time | MRR@10 | nDCG@10 |
|---|---|---|---|
| BM25 (candidate order) | - | 0.577 | 0.811 |
| KNRM, $\log$ (paper) | 1.8 s | **0.708** | 0.758 |
| KNRM, $\log(1+\cdot)$ | 1.2 s | **0.751** | **0.834** |
| Conv-KNRM ($h\le2$), $\log$ | 6.9 s | 0.707 | 0.757 |

Read it carefully:
- Both KNRMs beat BM25 on MRR by learning the planted aliases (query-side synonyms): the soft-match kernels do what exact matching cannot.
- On this toy data the ordering of the two variants is the **reverse** of the lecture's MS MARCO result. The toy's queries have two terms and the relevant documents repeat facet terms several times, so "ignore single occurrences" is not the useful regulariser here. The lesson that transfers is the lecture's: tiny implementation choices change results, so report them.
- The `log` KNRM's nDCG@10 falls below BM25's: binary triples treat grade-2 documents as negatives (note 08).
- Conv-KNRM gains nothing: the toy has no multi-word concepts to match. It is included for the architecture, not for the number.
- With 12 queries per topic (180 training queries) instead of 40, the gain is not reliable (positive for one of three seeds tried, negative for two): each alias occurs in about one training query, and unseen aliases are OOV (note 05). Neural rankers need training data at MS MARCO scale [S44].

## Pitfalls

- Missing masks (both query and document side) silently change scores with batch composition: `test_padding_mask_is_applied_after_the_kernel`.
- The $\sigma=10^{-3}$ exact kernel needs embeddings to be normalised: cosine, not dot product.
- Frozen pretrained embeddings (GloVe in the exercise) vs fine-tuned embeddings: KNRM's effect comes largely from tuning them [S33].
- Low-frequency terms: a word vocabulary with a count cut-off removes rare query terms; fastText-style composition helps [S12 sl. 43-47, S51].
- KNRM has no notion of term importance (idf) except through embeddings and no length normalisation: long documents collect more soft matches. TK adds document-length-enhanced kernel pooling for this reason [S36].

## Questions

**Q:** Write down KNRM and explain what a kernel counts.
**A:** Definition 3. Kernel $k$ counts, per query term, the document terms whose cosine similarity is near $\mu_k$ (soft-TF); $\log$ and a sum over query terms give one feature per kernel; a linear layer scores.

**Q:** What is the role of the exact-match kernel, and why is its $\sigma$ so small?
**A:** It reproduces term frequency of exact matches (cosine 1), the strongest lexical signal; $\sigma=10^{-3}$ keeps near-synonyms out of it so the model can weight exact and soft matches separately.

**Q:** Why must the padding mask be applied after the kernel, not to $M$?
**A:** Padding gives $M_{ij}=0$, and the RBF of 0 is non-zero for kernels near 0; masking $M$ would still let those positions add soft-TF. Multiply the kernel values by the document mask before summing over $j$.

**Q:** Compare MatchPyramid and KNRM.
**A:** Both start from the query-document match matrix. MatchPyramid learns local match patterns with 2D CNNs and pooling (more parameters, slower); KNRM summarises it with fixed RBF kernels into $K$ soft-TF features (very few parameters, fastest), with similar effectiveness in the lecture's comparison [S12 sl. 26-29, S19].

**Q:** What does Conv-KNRM add, and at what cost?
**A:** n-gram embeddings via 1D CNNs and cross-matching of all n-gram widths, so "convolutional neural networks" can match "deep learning"; $H^2$ match matrices instead of one, i.e. $H^2$ times the kernel-pooling work [S34].

## Code

[`../src/py/knrm.py`](../src/py/knrm.py): `kernels`, `kernel_pooling(M, d_mask, q_mask, mu, sigma, log1p)`, `KNRM(vocab_size, dim, n_kernels, log1p)`, `ConvKNRM(..., max_n)`, `Encoder`, `candidates`, `make_triples`, `train`, `rerank`, `evaluate`, `experiment(model_cls, depth, n_test, steps, seed, queries_per_topic, **kw)`. Tests: kernel values by hand, padding invariance, shapes, and **MRR improvement over BM25 asserted** for both variants (`test_knrm_improves_mrr_over_bm25`, `test_knrm_log1p_variant_improves_mrr_and_ndcg`).
