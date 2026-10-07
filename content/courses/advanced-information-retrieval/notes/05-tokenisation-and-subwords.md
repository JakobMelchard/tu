# 05 NLP I: tokenisation and subwords, seen from retrieval

Neural models need a finite vocabulary of units with a vector each. The choice
of unit (word, character n-gram, subword) decides what happens to the rare terms
that carry most of the relevance signal in IR [S9, S12 sl. 43-47, S51].

**Not repeated here:** BPE training step by step with a worked merge sequence,
SentencePiece and the unigram model, byte-level BPE and the LLM-side
consequences are in the ADL notes,
[`cse/ws2026/applied-deep-learning/notes/09-llms.md`](../../applied-deep-learning/notes/09-llms.md) §Tokenisation.
This note covers what is specific to retrieval.

## Definitions

1. **Word-level vocabulary** $V$: all types with count $\ge c_{\min}$; everything else maps to one `[UNK]`/OOV vector. Size $10^5$-$10^6$ for a web collection (Heaps' law, note 02).
2. **Character n-gram composition** (fastText [S59]): word $w$ with boundary markers `<w>` is represented by the sum of the vectors of its character n-grams ($3\le n\le6$) plus the word vector if known: $\mathbf v_w=\sum_{g\in G(w)}\mathbf z_g$. Unseen words get a vector from their n-grams [S9 sl. 16].
3. **Subword vocabulary** (BPE [S50], WordPiece [S61], SentencePiece [S60]): 30k-50k units; frequent words are one unit, rare words split. BERT uses a 30,000-token WordPiece vocabulary [S32]; word-internal pieces carry the prefix `##`.
4. **WordPiece encoding** (inference): per whitespace-separated word, greedy longest-match-first: take the longest prefix in $V$, then the longest `##`-prefixed continuation, and so on; if some remainder matches nothing, the **whole word** becomes `[UNK]`.
5. **Special tokens**: `[CLS]` (sequence summary position), `[SEP]` (segment boundary), `[PAD]`, `[MASK]` (pre-training) [S11 sl. 18].

## Results

**Why IR cares more than classification.** Rare terms have high idf: they are exactly the terms that identify the relevant document (names, codes, acronyms). A fixed word vocabulary removes them "as a concession to efficiency" and the neural model never sees them; unseen query terms are OOV at test time [S12 sl. 43]. Hofstätter et al. showed that covering all terms matters and that fastText's n-gram composition strongly improves effectiveness on queries with low-frequency terms (below about 10 occurrences) [S12 sl. 44-46, S51]. A classifier deciding the topic of a whole document can ignore a rare word; a ranker deciding *which* of 1000 on-topic documents answers the query cannot.

**Subwords remove OOV but not the problem.** A rare word split into 4 pieces has no vector of its own; its meaning must be composed by the contextual encoder. Dense retrievers compress the whole passage into one vector, so exact rare-term matches can get lost: the lecture's analysis asks "Can we retrieve unknown acronyms?" and finds cases where BM25 is still better [S15 sl. 40-42].

**Sequence length.** Subwords lengthen sequences (every split word costs extra positions); cross-encoders are capped at 512 positions for query + passage [S13 sl. 13], so tokenisation eats into how much of a document is seen.

## Worked example: greedy WordPiece is not optimal

$V=\{\texttt{un},\texttt{una},\texttt{\#\#afford},\texttt{\#\#able},\texttt{\#\#a},\texttt{\#\#ble}\}$. Word `unaffordable`.
1. Longest prefix in $V$: `una` (longer than `un`).
2. Remainder `ffordable`: no entry starts with `##f` $\Rightarrow$ the whole word is `[UNK]`.

Remove `una` from $V$: `un` + `##afford` + `##able`. A split existed all along; greedy longest-match cannot backtrack. (The unigram model's Viterbi segmentation, see the ADL note, would find it.)

fastText view of the same word, $n=3$: `<un, una, naf, aff, ffo, for, ord, rda, dab, abl, ble, le>` plus `<unaffordable>` if known: shares `aff, ffo, for, ord` with `afford`, so the vectors are close even if `unaffordable` was never seen.

## Pitfalls

- A tokenisation mismatch between index time and query time is silent; with HuggingFace models, always use the model's own tokenizer for both sides.
- Lower-casing: BERT-base-uncased lower-cases and strips accents; the cased model does not. Mixing them costs effectiveness without an error.
- Truncation to 512 tokens happens on the document side of `[CLS] q [SEP] d [SEP]`: long documents lose their tail (note 10, passage splitting).
- Counting "terms" for BM25 and "tokens" for BERT are different things; do not reuse BM25's document lengths as model input lengths.
- Stemming before a subword tokeniser throws away information the tokeniser would have used.

## Questions

**Q:** Why are low-frequency terms a bigger problem for neural IR than for text classification?
**A:** In IR rare terms carry the discriminative relevance signal (high idf) and appear in queries; a fixed vocabulary maps them to OOV, so the model cannot match them. Classification of a whole document's topic depends on many frequent words and tolerates losing a rare one [S12 sl. 43, S51].

**Q:** How does fastText produce a vector for an unseen word?
**A:** As the sum of learned character n-gram vectors ($3\le n\le6$ with boundary markers) of the word [S59].

**Q:** How does WordPiece encode a word, and what happens if a piece cannot be matched?
**A:** Greedy longest-match-first from the left, continuation pieces marked `##`; if a remainder has no match the entire word becomes `[UNK]`.

**Q:** Name BERT's special tokens and their role in a re-ranker input.
**A:** `[CLS]` first, its output vector is pooled for the score; `[SEP]` separates query and passage and ends the input; `[PAD]` fills to batch length and is masked in attention [S11 sl. 18, S13 sl. 8].

**Q:** Give one retrieval case where BM25 can beat a dense retriever and explain it via tokenisation.
**A:** Queries with rare exact identifiers or acronyms: BM25 matches the exact term with high idf; the dense model splits it into subwords and compresses the passage to one vector, losing the exact match [S15 sl. 40-42].

## Code

- [`../src/py/inverted_index.py`](../src/py/inverted_index.py): `tokenize`, the word-level analyzer the index, KNRM and the bi-encoder share.
- [`../src/py/knrm.py`](../src/py/knrm.py): `Encoder` maps unseen words to one `OOV` id: the fixed-vocabulary failure mode, visible when training queries are few (`experiment` docstring).
