# 02 Crash course I: inverted index and text preprocessing

The inverted index maps each term to the list of documents containing it, with
the statistics a scoring model needs, so that a query touches only the postings
of its terms instead of every document [S6 sl. 8-22, S22 ch. 1-2, 5]. The
course only refreshes this (it is the core of 194.166, notes in
[`introduction-to-information-retrieval`](../../introduction-to-information-retrieval/index.md)); what it
expects is the vocabulary and the cost arguments.

## Definitions

1. **Token**: an occurrence of a character sequence after splitting. **Type**: a distinct token string. **Term**: a normalised type that is indexed.
2. **Tokenisation**: split on whitespace and punctuation (baseline; breaks `U.S.A` into `U, S, A` and `25.9.2018` into three numbers [S6 sl. 13]).
3. **Normalisation**: case folding, removing diacritics, mapping variants to one term.
4. **Stop words**: very frequent function words (`the, of, and`); removing them shrinks postings; phrase queries ("to be or not to be") then fail.
5. **Stemming**: heuristic suffix chopping (`automate, automatic, automation` $\to$ `automat`); **lemmatisation**: map inflections to the dictionary form (`am, are, is` $\to$ `be`), needs morphology [S6 sl. 16]. Both raise recall and can lower precision (`university`, `universe` $\to$ `univers` in Porter).
6. **Dictionary**: the set of terms, with $df_t$ and a pointer to the postings (hash table or B-tree; B-trees support prefix/wildcard queries) [S6 sl. 27-29].
7. **Postings list** of $t$: sorted document ids $d$ with $tf_{t,d}$ and optionally positions. Also stored: $dl_d$, $avgdl$, $N$ [S6 sl. 8].
8. **Boolean retrieval**: AND/OR/NOT over postings as set operations; result is unranked.
9. **Positional index**: postings carry token positions; enables phrase and proximity queries.

## Results

**Linear merge.** Two sorted postings lists of lengths $x,y$ intersect in $O(x+y)$ with two pointers (advance the smaller id) [S22 fig. 1.6]. For a conjunction of $m$ terms, process in order of increasing $df$: the intermediate result never exceeds the rarest list, so the cost is $\le \sum_i df_{t_i}$ and usually close to $m\cdot\min_i df_{t_i}$ with skip pointers.

**Term-at-a-time (TAAT)** keeps one accumulator per touched document and adds one term's contribution at a time; memory $O(|\bigcup \text{postings}|)$. **Document-at-a-time (DAAT)** advances one cursor per term to the smallest current document id, scores that document completely and keeps a size-$k$ min-heap; memory $O(k+m)$, which is why engines prefer it (and why WAND/MaxScore-style skipping can prune documents that cannot enter the heap).

**Zipf and Heaps** [S22 §5.1]. Collection frequency of the $i$-th most frequent term $cf_i\propto 1/i$: a few terms hold most tokens (stop words), most terms are rare (the long tail that hurts neural models, note 05). Vocabulary size grows as $M=kT^b$ with $T$ tokens, typically $30\le k\le100$, $b\approx0.5$: the dictionary never stops growing.

**Gap + variable-byte compression** [S22 §5.3]. Store differences of consecutive document ids (small for frequent terms), each in 7-bit groups, high bit set on the last byte.

## Worked example

Documents after lower-casing, removing the module's stop list (`the of and a to in is for on with`) and the light stemmer:

| id | text | terms |
|---|---|---|
| a | This is a sample document, full of infos. | thi, sample, document, full, info |
| b | Sample documents and more samples. | sample, document, more, sample |
| c | Nothing to see here: full stop. | noth, see, here, full, stop |

(`this` $\to$ `thi` is not a bug of the toy stemmer: Porter's step 1a also strips the final `s`.)
Postings: `sample` $\to$ a:1, b:2; `document` $\to$ a:1, b:1; `full` $\to$ a:1, c:1.
`sample AND full` $=\{a,b\}\cap\{a,c\}=\{a\}$; `sample AND NOT full` $=\{b\}$.

Variable byte for document ids $824, 829, 215406$: gaps $824, 5, 214577$.
$824=6\cdot128+56$: bytes `00000110 10111000`; $5$: `10000101`;
$214577=13\cdot128^2+12\cdot128+49$: `00001101 00001100 10110001`. Six bytes instead of twelve as 32-bit integers [S22 table 5.4]; reproduced by `test_vbyte_roundtrip_and_known_bytes`.

On the planted collection (`inverted_index.py` demo): 300 documents, 519 terms, a postings list of 18 documents takes 18 bytes gap-encoded vs 72 as `int32`.

## Pitfalls

- **Query and documents must go through the same analyzer** [S6 sl. 10]. A stemmed index with an unstemmed query silently loses matches. `InvertedIndex.analyze` is used for both.
- Stemmers conflate unrelated words and miss irregular forms; for neural models, the subword tokeniser replaces the stemmer and both should not be stacked blindly.
- `NOT t` alone is the complement over all $N$ documents: expensive. Always evaluate it as `a AND NOT t`.
- Stop-word removal changes $dl_d$ and so BM25's length normalisation; keep it consistent between index and statistics.
- Positions are needed for phrases; a non-positional index answers `"new york"` with documents containing both words anywhere (test `test_phrase_query`).

## Questions

**Q:** Which statistics does an inverted index store, and which scoring model needs which?
**A:** Per term $df_t$ and postings with $tf_{t,d}$ (positions optional); per document $dl_d$; global $N$ and $avgdl$. TF-IDF needs $tf, df, N$; BM25 additionally $dl_d$ and $avgdl$; query likelihood additionally collection frequencies $cf_t$ and $\sum_d dl_d$ [S6 sl. 8].

**Q:** Why process a conjunctive query in order of increasing document frequency?
**A:** Every intermediate result is a subset of the rarest list, so the merge work stays near the shortest list; starting with the most frequent term makes the first intersection as large as possible.

**Q:** Compare TAAT and DAAT scoring.
**A:** TAAT: one pass per term, an accumulator per candidate document, simple, memory grows with the union of postings. DAAT: all lists in parallel by document id, each document scored once, a size-$k$ heap, constant memory in the collection size; enables dynamic pruning.

**Q:** Stemming vs lemmatisation: definitions and one failure mode each.
**A:** Stemming chops suffixes by rule (over-conflation: `universe`/`university`); lemmatisation maps to the dictionary lemma using morphology and part of speech (needs a lexicon; fails on unknown words, costs more).

**Q:** Encode the gaps $5$ and $130$ in variable-byte code.
**A:** $5$: `10000101`. $130=1\cdot128+2$: `00000001 10000010`.

## Code

[`../src/py/inverted_index.py`](../src/py/inverted_index.py):
- `tokenize(text, stopwords, stem)`, `light_stem(word)`: the analyzer.
- `InvertedIndex(docs)`: `postings`, `df`, `tf`, `doc_len`, `avgdl`; `boolean("a AND (b OR NOT c)")` (recursive descent, NOT > AND > OR); `phrase("new york")`.
- `intersect`, `union`, `difference`: linear merges, tested against Python sets.
- `score_taat(query)`, `topk_daat(query, k)`: the lecture's TF-IDF [S6 sl. 54], both strategies, tested equal and against a scikit-learn count matrix.
- `vbyte_encode`, `vbyte_decode`: gap + variable-byte compression.
