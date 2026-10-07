# 11 Neural IR IV: dense retrieval (bi-encoders, DPR, ANN search) vs late interaction (ColBERT)

Encode queries and passages **independently** into vectors, precompute the
passage side, and retrieve by nearest-neighbour search: a learned first stage
that can find passages sharing no word with the query [S15 sl. 3-18, S37].
Late interaction keeps one vector per token instead of one per passage [S38].

## Definitions

1. **Bi-encoder / BERT_DOT** [S15 sl. 9-10]: $s(q,p)=\eta(q)^\top\eta(p)$ with $\eta$ a transformer and `[CLS]` (or mean) pooling; cosine variants normalise. Passages are encoded at indexing time; a query costs one encoder pass plus a search. DPR uses two separate BERT-base encoders and `[CLS]` [S37].
2. **In-batch negatives** [S15 sl. 12, S37 §3.2]: a batch of $B$ pairs $(q_i,p_i^+)$; score matrix $S=QP^\top/\tau$; loss $\mathcal L=-\frac1B\sum_i\log\frac{e^{S_{ii}}}{\sum_je^{S_{ij}}}$. Every other positive is a negative: $B^2$ scores for $2B$ encoder passes. Extra hard negatives (e.g. one BM25 negative per query) are appended as additional columns.
3. **ANCE** [S42, S15 sl. 13]: negatives retrieved from an ANN index of the model being trained, refreshed periodically (multiple GPU hours per refresh on MS MARCO).
4. **Exact NN (MIPS)**: $\arg\text{top}_k\,Xq$; on a GPU, 9 M vectors of 768 dimensions take about 70 ms per query, on a CPU about 1 s [S15 sl. 15].
5. **IVF** (inverted file, FAISS [S43]): k-means into $n_{list}$ cells; at query time scan only the $n_{probe}$ cells with the nearest centroids.
6. **LSH for cosine**: $h_r(x)=\mathrm{sign}(r^\top x)$, $r\sim\mathcal N(0,I)$; $k$ bits per table, $L$ tables; candidates = union of the query's buckets, then exact re-scoring.
7. **HNSW** [S67]: hierarchical proximity graphs, greedy search from the top layer, logarithmic scaling. **PQ**: product quantisation compresses vectors to codes, search in the compressed domain [S43].
8. **ColBERT** [S38, S13 sl. 20-21]: $\hat q_{1:n}=\mathrm{BERT}(\texttt{[CLS]};q)$, $\hat p_{1:m}=\mathrm{BERT}(\texttt{[CLS]};p)$ (both optionally reduced by a linear layer), $s=\sum_{i=1}^n\max_{j}\hat q_i^\top\hat p_j$ ("MaxSim"). Passage token vectors are precomputed.

## Results

**In-batch loss gradient.** With $\pi_{ij}=\mathrm{softmax}_j(S_{ij})$: $\partial\mathcal L/\partial q_i=\frac1{B\tau}\bigl(\sum_j\pi_{ij}p_j-p_i\bigr)$. Like word2vec (note 06): pull towards the positive, push away from the model-weighted average of the negatives. Negatives that already score low get small $\pi_{ij}$ and contribute little: random in-batch negatives become too easy, hence hard negatives (BM25, ANCE, TAS-B's topic-clustered batches, note 12).

**Random-hyperplane collision probability.** For $x,y$ at angle $\theta$, project onto the plane they span: the random hyperplane's normal direction there is uniform on the circle, and it separates $x$ and $y$ iff it falls in one of two arcs of total angle $2\theta$ out of $2\pi$. So $P[h(x)=h(y)]=1-\theta/\pi$ (`test_lsh_collision_probability_and_recall` checks it to $\pm0.005$ over 200k hyperplanes). With $k$ bits ANDed and $L$ tables ORed: $P[\text{candidate}]=1-(1-(1-\theta/\pi)^k)^L$, an S-curve in $\theta$.

**Dense vs sparse.**
- In-domain with large training data, dense retrieval beats BM25 clearly: DPR +9 to 19 points top-20 accuracy on open-domain QA [S37]; TAS-B +44 % nDCG@10 over BM25 on TREC DL [S41].
- **Zero-shot** (BEIR, 18 datasets), BM25 is a robust baseline; dense models often underperform it, re-rankers and late interaction are best on average but expensive [S58, S15 sl. 36-38].
- Exact rare-term matches (acronyms, identifiers) remain a weak spot [S15 sl. 40-42]; hybrids combine BM25 and dense scores.

**Late interaction sits between.** ColBERT keeps token-level matching (more effective than one vector, close to BERT_CAT) while precomputing passages: two orders of magnitude faster than BERT re-rankers and four orders fewer FLOPs per query [S38]. The price is storage: one vector per token. ColBERTv2's residual compression cuts the footprint 6-10$\times$ [S39]; ColBERTer learns whole-word vectors and drops unneeded ones, up to 2.5$\times$ less storage [S52].

## Worked examples

**Index sizes for MS MARCO passage** ($N=8{,}841{,}823$ [S44]): single vector, 768 dimensions, fp32: $8.84\text{M}\cdot768\cdot4\text{ B}=27.2$ GB. Late interaction, assuming 70 tokens per passage and 128-dimensional fp16 vectors: $8.84\text{M}\cdot70\cdot128\cdot2\text{ B}=158$ GB, about $6\times$ more.

**LSH amplification.** $k=10$ bits, $L=16$ tables. A neighbour at $30°$: $p=1-\frac{1}{6}=0.833$, $p^{10}=0.162$, found with probability $1-(1-0.162)^{16}=0.940$. A non-neighbour at $60°$: $p=0.667$, $p^{10}=0.0173$, $1-(1-0.0173)^{16}=0.244$. Raising $k$ sharpens the curve, raising $L$ recovers recall.

**Planted collection** (`dense_retrieval.py` demo; bag-of-embeddings bi-encoder, 400 in-batch steps of 64 pairs, 1.8-3.7 s): recall@20 on 60 held-out queries: BM25 0.825, untrained encoder 0.433, **trained 0.979**: the dense model learned the aliases that BM25 cannot match. ANN on 20k clustered vectors: IVF (64 lists) recall@10 0.900 scanning 2.1 % of vectors with $n_{probe}=1$, 1.000 at 6.6 % with $n_{probe}=4$; LSH (10 bits) 0.729 with 4 tables (1.9 %), 0.988 with 16 (4.2 %).

## Pitfalls

- "Recall" of an ANN index is agreement with exact search, not relevance recall. Report both.
- Normalised vs unnormalised embeddings: maximum inner product and cosine rank differently unless norms are equal; IVF with L2 centroids assumes the metric you trained for.
- In-batch negatives from the same topic can be false negatives; TAS samples topically related queries per batch deliberately and relies on a teacher to handle this (note 12).
- Dense retrieval replaces the first stage; a re-ranker on top still helps and TAS-B lets it re-rank fewer passages [S41].
- The index must be rebuilt when the passage encoder changes: fine-tuning a dense retriever is not free at serving time [S15 sl. 8].

## Questions

**Q:** Why can a bi-encoder be used for first-stage retrieval but a cross-encoder cannot?
**A:** The bi-encoder's passage vectors do not depend on the query, so they are computed once and indexed for (approximate) nearest-neighbour search; the cross-encoder needs a joint pass per (query, passage) pair.

**Q:** Explain in-batch negatives and give the loss.
**A:** For a batch of $B$ query-positive pairs, each query uses the other $B-1$ positives as negatives; loss is the softmax cross-entropy on the diagonal of $QP^\top/\tau$. Cheap: $B^2$ comparisons for $2B$ encodings [S37].

**Q:** Derive the collision probability of random-hyperplane LSH.
**A:** A random hyperplane separates two vectors at angle $\theta$ with probability $\theta/\pi$ (uniform direction in their plane, separating arc $2\theta$ of $2\pi$); collision probability $1-\theta/\pi$ per bit.

**Q:** Write ColBERT's score and say what is precomputed.
**A:** $s=\sum_i\max_j\hat q_i^\top\hat p_j$; all passage token vectors $\hat p_j$ are computed at index time; at query time only the query is encoded and MaxSim computed [S38].

**Q:** In which setting does BM25 still beat dense retrievers, and why?
**A:** Zero-shot on new domains (BEIR) and queries with rare exact terms: dense models trained on MS MARCO transfer poorly and compress exact-match evidence into one vector [S58, S15 sl. 40-42].

## Code

[`../src/py/dense_retrieval.py`](../src/py/dense_retrieval.py): `BiEncoder` (masked mean pooling, projection, normalisation), `in_batch_loss(q, p, tau)`, `margin_mse` (note 12), `brute_force`, `kmeans`, `IVFIndex(X, nlist).search(Q, k, nprobe)`, `LSHIndex(X, n_bits, n_tables).search(Q, k)` (both return the fraction of vectors scored), `ann_recall`, `dense_experiment`. Tests: loss equals manual cross-entropy, IVF with all lists equals exact search, recall grows with $n_{probe}$ and $L$, LSH collision law, trained recall above untrained and above BM25.
