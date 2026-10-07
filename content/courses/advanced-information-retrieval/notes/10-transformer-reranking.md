# 10 Neural IR III: transformer re-ranking (BERT_CAT and its efficient relatives)

Concatenate query and passage, run a pre-trained transformer, read a score off
`[CLS]`: this roughly doubled MS MARCO effectiveness and "opened a new era" of IR
[S13 sl. 8-11, S35, S48]. Its cost motivated every efficient architecture in
notes 11-12.

**Not repeated here:** self-attention, multi-head attention, positional
encodings, the block structure, pre-training objectives and parameter-count
derivations are in
[`cse/ws2026/applied-deep-learning/notes/06-transformers.md`](../../applied-deep-learning/notes/06-transformers.md)
and [`09-llms.md`](../../applied-deep-learning/notes/09-llms.md). This note starts from "BERT is a stack of encoder blocks".

## Definitions

1. **BERT** [S32]: a transformer encoder pre-trained with masked language modelling on large text; input `[CLS] A [SEP] B [SEP]` with token, segment and learned position embeddings; BERT-base $L=12$, $d=768$, 12 heads, about 110 M parameters; at most 512 positions [S11 sl. 15-20, S13 sl. 13].
2. **BERT_CAT** (monoBERT, "vanilla BERT") [S13 sl. 8, S35]: $s(q,p)=\mathbf w^\top\,\mathrm{BERT}(\texttt{[CLS]}\,q\,\texttt{[SEP]}\,p\,\texttt{[SEP]})_{\texttt{[CLS]}}+b$. Full query-passage cross-attention in every layer; one forward pass per candidate.
3. **Mono-duo** [S13 sl. 12, S70]: mono $s(q,p)$ on the top 1000, then duo $s(q,p_1,p_2)$ ("is $p_1$ more relevant than $p_2$") on pairs of the top 50, on the order of $50^2$ passes, aggregated per passage.
4. **Long documents** [S13 sl. 13]: truncate to $512-|q|-3$ tokens (works well on MS MARCO documents), or slide a window over the document and take the maximum window score (also yields a snippet).
5. **PreTTR** [S66, S13 sl. 18-19]: run the first $b$ layers on query and passage **separately** (passage part precomputed at index time), concatenate and run layers $b+1..L$ jointly at query time.
6. **TK** (Transformer-Kernel) [S36, S13 sl. 22-26]: word embeddings, at most 3 small transformer layers contextualising query and document separately, then KNRM-style kernel pooling with document-length normalisation. Designed for a time budget (e.g. 200 ms per query): a faster model can re-rank more candidates.
7. **ColBERT** (late interaction): separate encoders, token-level MaxSim; see note 11 [S38, S13 sl. 20-21].

## Results

**Effectiveness jump.** MS MARCO passage MRR@10 from 0.194 (BM25) to 0.385 (ALBERT-large BERT_CAT); documents 0.252 to 0.384 [S13 sl. 11]. monoBERT's first submission beat the previous leaderboard top by 27 % relative MRR@10 [S35]. The gains come from pre-training, not from the architecture alone (see the from-scratch experiment below).

**Cost of BERT_CAT.** Per candidate a full pass over $T=|q|+|p|+3$ tokens. Dense-layer work $\approx2\cdot P_{\text{layers}}\cdot T$ FLOPs, attention scores $\approx 4LT^2d$. Nothing depends on the passage alone, so nothing can be precomputed: the lecture measured about 2 s of GPU time per query for 250 candidates [S13 sl. 14].

**The efficiency design space** (what is computed when):

| model | query-passage interaction | precomputed at index time | query-time work |
|---|---|---|---|
| BERT_CAT | all layers, all tokens | nothing | $k$ full passes |
| PreTTR | layers $b+1..L$ | first $b$ layers per passage token | $k$ partial passes |
| TK | kernel pooling after separate shallow encoders | nothing (shallow, fast) | $k$ cheap passes |
| ColBERT | MaxSim over token vectors | all passage token vectors | 1 query pass + $k\cdot|q|\cdot|p|$ dot products |
| BERT_DOT | one dot product | one vector per passage | 1 query pass + NN search |

Recollected exam item [S19]: match "most effective" (BERT_CAT), "transformer + kernel pooling" (TK), "large memory for stored token vectors" (ColBERT), "effort moved to indexing" (BERT_DOT).

## Worked examples

**Parameter count** (`param_count_formula`, embeddings $(V+P+2)d$, per layer $4d^2+4d$ attention, $2dd_{ff}+d_{ff}+d$ feed-forward, $4d$ layer norms): BERT-base with $V=30522$, $P=512$, $d=768$, $d_{ff}=3072$, $L=12$: $108.9$ M, plus the $d^2+d=0.59$ M pooler: $\approx110$ M [S32]. The tiny test model ($V=1000$, $d=32$, $L=2$): $53{,}345$, matching `sum(p.numel())` exactly.

**FLOPs per query.** Non-embedding parameters $12\cdot(4\cdot768^2+2\cdot768\cdot3072)\approx85$ M; $T=200$: $2\cdot85\text{M}\cdot200=34$ GFLOPs per pair (attention adds $4\cdot12\cdot200^2\cdot768\approx1.5$ GFLOPs). Re-ranking 1000 candidates: $\approx35$ TFLOPs per query. A BERT_DOT query costs one pass over $\sim10$ query tokens, $\approx1.7$ GFLOPs, plus the search.

**From scratch, no pre-training** (`bert_reranker_sketch.py` demo, 2-layer $d=32$ cross-encoder, 400 steps): MRR@10 **0.312** vs BM25's 0.577 on the same candidates; 1500 steps: 0.437 with training loss 0.14 (overfitting). KNRM on the same data: 0.708. Without pre-training, the transformer has no inductive bias for exact matching and far too little data: BERT_CAT's gains are bought by pre-training on billions of tokens [S32, S48].

## Pitfalls

- Truncation silently happens on the passage side; for long documents the relevant part may be cut (passage-level relevance, [S8 'Where is the passage-level relevance?']).
- `[CLS]` pooling assumes fine-tuning; the raw pre-trained `[CLS]` vector is not a relevance score.
- Comparing BERT_CAT to a first-stage retriever is a category error: it needs candidates.
- Transformers are permutation-equivariant without position embeddings (`test_without_positions_the_encoder_sees_a_bag_of_words`): word order enters only through them.
- Leaderboard-style mono-duo and ensembles are effectiveness upper bounds, not deployable systems [S13 sl. 12].

## Questions

**Q:** Describe BERT_CAT's input, output and training.
**A:** `[CLS] q [SEP] p [SEP]` with segment embeddings; a linear layer on the final `[CLS]` vector gives the score; fine-tuned on MS MARCO triples with a pointwise or pairwise loss [S13 sl. 8, S35].

**Q:** Why is BERT_CAT expensive at query time, and what exactly can PreTTR and ColBERT precompute?
**A:** All layers see query and passage jointly, so every candidate needs a full pass at query time. PreTTR precomputes the first $b$ layers of passage token vectors; ColBERT precomputes all final passage token vectors and only does MaxSim at query time.

**Q:** How does TK trade effectiveness for efficiency?
**A:** At most 3 shallow transformer layers contextualise query and document separately, followed by kernel pooling; under a fixed time budget it can re-rank more candidates than BERT and ends up more effective in that regime [S36].

**Q:** How are documents longer than 512 tokens handled?
**A:** Truncate (first passage), or score overlapping windows and aggregate, typically by the maximum [S13 sl. 13].

**Q:** Estimate the FLOPs of re-ranking 1000 candidates of 200 tokens with BERT-base.
**A:** $\approx2\cdot85\text{M}\cdot200\approx34$ GFLOPs per pair, $\approx35$ TFLOPs per query.

## Code

[`../src/py/bert_reranker_sketch.py`](../src/py/bert_reranker_sketch.py): `MultiHeadSelfAttention` (key-padding mask; equals `torch.nn.MultiheadAttention` with copied weights), `Block` (post-LN, GELU), `TinyCrossEncoder(vocab, d, h, layers, d_ff, max_len, use_pos)`, `build_pairs` (layout, segments, document-side truncation), `param_count_formula`, `train_step` (hinge), `rerank_experiment`. Tests: shapes, parameter count, attention rows, padding invariance, bag-of-words without positions, loss reduction on a fixed batch.
