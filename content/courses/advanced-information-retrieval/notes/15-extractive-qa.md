# 15 Special topics III: extractive question answering

Given a question and a passage, select the span of the passage that answers it.
Combined with a retriever it becomes open-domain QA ("retrieve and read"). It
was part 2 of the exercise in 2021-2023 (HuggingFace model on FiRA/MS MARCO
pairs) [S11 sl. 27-32, S17, S18].

## Definitions

1. **Extractive QA**: output one or more spans $[i,j]$ of the passage (start and end token) [S11 sl. 29]. **Generative QA** writes new text: more natural, more room for errors and bias.
2. **Datasets**: SQuAD (crowd-written questions on Wikipedia paragraphs, more than 100k) [S47]; Natural Questions (Google search queries on Wikipedia) [S11 sl. 30].
3. **BERT reader** [S11 sl. 31, S32]: input `[CLS] q [SEP] p [SEP]`; final token vectors $h_t$; learned vectors $S,E\in\mathbb R^d$; $P_{\text{start}}(t)=\mathrm{softmax}_t(S^\top h_t)$, $P_{\text{end}}(t)=\mathrm{softmax}_t(E^\top h_t)$ over passage positions.
4. **Training loss**: cross-entropy of the gold start plus cross-entropy of the gold end, $\mathcal L=-\log P_{\text{start}}(i^*)-\log P_{\text{end}}(j^*)$; optionally a "no answer" prediction for the passage (SQuAD 2.0) [S11 sl. 31].
5. **Decoding**: $\arg\max_{i\le j<i+L_{\max}}\bigl(S^\top h_i+E^\top h_j\bigr)$ (log-space sum of start and end scores), $O(nL_{\max})$ with a running maximum.
6. **Metrics**: exact match (EM) after normalisation (lower-case, strip punctuation and articles), and token-level F1 between prediction and gold answer, maximised over gold answers [S47].
7. **Open-domain QA**: retrieve candidate passages from a collection, then read; can be separate systems or trained jointly; DPR was introduced as the retriever for this [S11 sl. 32, S37].

## Results

**Independence of start and end.** The model predicts start and end with separate softmaxes; the joint span score $S^\top h_i+E^\top h_j$ assumes they are independent given the encoding. The contextual encoder has already mixed question and passage, which is why this crude factorisation works. The constraints $i\le j$ and $j-i<L_{\max}$ are imposed only at decoding.

**Why retrieval quality bounds QA.** In retrieve-and-read, the reader cannot answer from a passage it never sees: end-to-end accuracy $\le$ retriever recall@$k$ times reader accuracy on answer-bearing passages. DPR's gains in top-20 retrieval accuracy (9-19 points over BM25) carried over to end-to-end QA [S37].

**FiRA text selections** [S8 'FiRA', S18]: the course's own annotations include both a relevance grade and the selected answer text per (query, passage) pair, so the exercise could evaluate re-ranking (grades) and extractive QA (spans) on the same data.

## Worked examples

**Span decoding** (`best_span`). Passage scores for 5 tokens: start $(1.0,\,3.0,\,0.5,\,0.2,\,0.1)$, end $(0.1,\,0.2,\,2.5,\,0.4,\,2.8)$, $L_{\max}=2$ (span of at most 2 tokens). Candidates $(i,j)$ with $j-i\le1$: $(1,2)$: $3.0+2.5=5.5$; $(3,4)$: $0.2+2.8=3.0$; $(2,2)$: $3.0$; $(1,1)$: $3.2$. Best $(1,2)$, although the single best end is token 4: the start at 1 is too far from it. With $L_{\max}=4$: $(1,4)$ scores $3.0+2.8=5.8$ and wins.

**EM and F1.** Gold `kola nut tree`, prediction `kola nut`: EM 0. Precision $2/2=1$, recall $2/3$, $F1=\frac{2\cdot1\cdot\frac23}{1+\frac23}=0.8$.

## Pitfalls

- Token positions are in subword units: map back to character offsets through the tokenizer's offset mapping, or the extracted string is wrong at word boundaries.
- Passages longer than the model's limit are split into overlapping windows (stride); the same answer can appear in two windows; take the best-scoring span over windows.
- Start and end must lie in the passage segment, not in the question or on `[SEP]`; mask other positions before the softmax or at decoding.
- Unanswerable questions: without a no-answer option (SQuAD 2.0 style [S11 sl. 31]) the reader always returns some span.
- Evaluating on only the gold passage (the SQuAD setting) overstates open-domain performance [S11 sl. 32].

## Questions

**Q:** How does a BERT model predict an answer span, and how is it trained?
**A:** Two learned vectors score every passage token as start and as end via softmax over positions; the loss is the sum of the cross-entropies of the gold start and end [S11 sl. 31, S32].

**Q:** Why is decoding restricted to $i\le j<i+L_{\max}$, and how is it computed efficiently?
**A:** Independent start/end predictions can produce invalid or implausibly long spans; for each end $j$, take the best start in the window $[j-L_{\max}+1,j]$: $O(nL_{\max})$.

**Q:** Define EM and F1 for extractive QA.
**A:** EM: 1 if the normalised prediction equals a normalised gold answer. F1: harmonic mean of token precision and recall between prediction and gold, maximised over gold answers [S47].

**Q:** What is open-domain QA, and what bounds its accuracy?
**A:** Retrieve passages from a large collection, then extract the answer; bounded by the retriever's recall of answer-bearing passages at the depth the reader sees [S11 sl. 32, S37].

**Q:** Extractive vs generative QA: one advantage of each.
**A:** Extractive: the answer is verbatim from a source (verifiable, no invented facts). Generative: can combine information and phrase naturally, at a higher risk of errors and bias [S11 sl. 29].

## Code

[`../src/py/bert_reranker_sketch.py`](../src/py/bert_reranker_sketch.py): `best_span(start, end, max_len)`, tested against brute force over all valid spans. The encoder in the same file (`TinyCrossEncoder`, `build_pairs`) has the reader's input layout; a real reader uses a pretrained HuggingFace model, which is out of scope for network-free tests.
