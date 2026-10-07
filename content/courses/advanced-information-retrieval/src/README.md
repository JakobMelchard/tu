# Reference implementations

Python only: the course's exercises are in Python and PyTorch [S1, S17]. numpy
first, torch for the neural models, scipy/scikit-learn only as cross-checks in
tests. **No downloads, no network**: every module builds its data from a fixed
seed, mostly the planted collection of `corpus.py` (300 documents, 240 queries,
graded qrels, and query-side aliases as planted vocabulary mismatch). All
torch code runs on the CPU.

From the course folder, with the repo's Python environment:

```
python -m pytest src -q           # 62 tests, about 8 s
python src/py/knrm.py             # any module: runs its demo
```

Every module docstring names its note and sources.

| Module | Note | Implements | Demo prints (seed 0) | Test anchors |
|---|---|---|---|---|
| `py/corpus.py` | all | `make_collection`: topics, facets, graded qrels 0-3, aliases; `binary_qrels`, `split_queries` | 300 docs, 240 queries, 2.42 grade-3 docs per query | qrels consistent with facets; determinism |
| `py/inverted_index.py` | 02, 03 | `tokenize`, `light_stem`, `InvertedIndex` (positional), boolean parser, `phrase`, TF-IDF `score_taat` / `topk_daat`, `intersect`/`union`/`difference`, `vbyte_encode`/`decode` | 519 terms; boolean counts; top-5; 72 vs 18 bytes | set algebra; parser vs brute force; TF-IDF by hand and vs a scikit-learn count matrix; IIR vbyte bytes |
| `py/bm25.py` | 03 | `bm25_tf`, `idf_rsj0`, `rsj_weight`, `BM25`, `QueryLikelihood` (Dirichlet, JM, sparse form), `lecture_example` | 87/75 vs 30.96/42.67; MRR@10 and nDCG@10 of five rankers; alias-only queries MRR 0.333 | hand-computed 0.214058 / 0.228117; limits $k_1=0$, $b=0$; negative idf; QL by hand; sparse = full up to a constant |
| `py/metrics.py` | 04 | P@k, R@k, RR, AP, DCG/nDCG (linear or $2^x-1$), paired $t$, randomisation test, Bonferroni, Kendall $\tau$ | slide systems A/B/C; $t=2.449$, $p=0.0917$ vs randomisation 0.25 | lecture numbers 0.83/0.17/0.58 and 0.69/0.14/0.66; scikit-learn AP and nDCG; `scipy.stats.ttest_rel`; exact enumeration |
| `py/word2vec_toy.py` | 06 | analogy corpus, `Vocab.noise` ($^{3/4}$), `skipgram_pairs`, `sgns_loss_grads`, `train_sgns`, `most_similar`, `analogy`, `analogy_accuracy` | loss 3.07 to 2.13; king - man + woman = queen; accuracy 1.00 over 132 pairs | finite-difference gradients; accuracy $\ge0.9$; topic coherence on the IR collection |
| `py/knrm.py` | 08, 09 | `kernel_pooling`, `KNRM` (`log` / `log1p`), `ConvKNRM`, `Encoder`, BM25 candidates, `make_triples`, `train` (margin loss), `rerank`, `experiment` | BM25 top-30 MRR@10 0.577 to 0.708 (`log`), 0.751 (`log1p`), 0.707 (Conv-KNRM); about 2 s per KNRM run | kernel values by hand; padding invariance; **MRR gain over BM25 > 0.05 asserted** |
| `py/bert_reranker_sketch.py` | 10, 15 | `MultiHeadSelfAttention`, `Block`, `TinyCrossEncoder`, `build_pairs`, `param_count_formula`, `train_step`, `rerank_experiment`, `best_span` | 53,345 parameters = formula; BERT-base 108.9 M + pooler; from scratch MRR@10 0.312 (below BM25: no pre-training) | equals `torch.nn.MultiheadAttention`; padding and permutation invariance; loss reduction; span decoding vs brute force |
| `py/dense_retrieval.py` | 11, 12 | `BiEncoder`, `in_batch_loss`, `margin_mse`, `brute_force`, `kmeans`, `IVFIndex`, `LSHIndex`, `ann_recall`, `dense_experiment` | recall@20 BM25 0.825, untrained 0.433, trained 0.979; IVF and LSH recall vs fraction scanned | loss = manual cross-entropy; IVF all lists = exact; LSH $1-\theta/\pi$; Margin-MSE shift invariance; trained > BM25 |
| `py/evaluation_campaign.py` | 13, 04 | `simulate`, `pool`, `pooled_qrels`, `bpref`, `map_score`, `leaderboard`, `leave_one_out` | pooled leaderboard; novel run rank 3 to 7; $\tau=1$ among contributors; paired $t$ of the top two | union-of-top-$k$; P@k exact for contributors; pool bias $\ge3$ ranks; bpref by hand |

Timings above were measured on 2026-09-28 on a heavily loaded machine (load average near 100); expect them to be lower.

What is deliberately not here: pretrained BERT/HuggingFace models, MS MARCO or any
real collection (downloads), GPU code. The course's exercise supplies those; the
modules here reproduce the mechanisms and the arithmetic.
