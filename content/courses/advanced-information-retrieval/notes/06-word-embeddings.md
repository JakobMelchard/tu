# 06 NLP II: word embeddings (word2vec, GloVe) with the skip-gram derivation

Dense word vectors trained on raw text so that words in similar contexts get
similar vectors (distributional hypothesis). They were the input layer of every
pre-BERT neural ranker, including the exercise's KNRM, which used GloVe
[S9, S17, S18].

## Definitions

1. **One-hot** $e_w\in\{0,1\}^{|V|}$: orthogonal, no similarity. **Embedding** $E\in\mathbb R^{|V|\times d}$, $v_w=E^\top e_w$, $d\approx 100$-$300$.
2. **word2vec** [S29]: CBOW predicts the centre word from the averaged context; **skip-gram** predicts each context word from the centre word, window $\pm m$ [S9 sl. 13-14].
3. Skip-gram model: two matrices, centre ("input") vectors $v_w$ and context ("output") vectors $u_w$,
$$p(o\mid c)=\frac{\exp(u_o^\top v_c)}{\sum_{w\in V}\exp(u_w^\top v_c)},\qquad J=-\frac1T\sum_{t}\sum_{-m\le j\le m,\,j\neq0}\log p(w_{t+j}\mid w_t).$$
4. **Negative sampling (SGNS)** [S30]: replace the softmax by $K$ logistic "real vs noise" tasks,
$$\ell(c,o)=-\log\sigma(u_o^\top v_c)-\sum_{k=1}^K\log\sigma(-u_{n_k}^\top v_c),\qquad n_k\sim P_n(w)\propto \mathrm{count}(w)^{3/4}.$$
5. **Subsampling** of frequent words: drop an occurrence of $w$ with probability $1-\sqrt{t/f(w)}$ ($f$ relative frequency, $t\approx10^{-5}$) [S30].
6. **GloVe** [S31]: weighted least squares on the log co-occurrence matrix $X$,
$$J=\sum_{i,j:X_{ij}>0}f(X_{ij})\bigl(w_i^\top\tilde w_j+b_i+\tilde b_j-\log X_{ij}\bigr)^2,\qquad f(x)=\min\bigl(1,(x/x_{\max})^{\alpha}\bigr),\ \alpha=\tfrac34,\ x_{\max}=100.$$
7. **Analogy (3CosAdd)**: $a:b::c:?$ answered by $\arg\max_{x\notin\{a,b,c\}}\cos(x,\,b-a+c)$ [S9 sl. 18].

## Derivations

**Full softmax gradient.** With $p_w=p(w\mid c)$:
$$\frac{\partial(-\log p(o\mid c))}{\partial v_c}=-u_o+\sum_w p_w u_w=\mathbb E_{w\sim p(\cdot\mid c)}[u_w]-u_o,\qquad \frac{\partial}{\partial u_w}=(p_w-\mathbb 1[w=o])\,v_c.$$
"Observed minus expected": the update pulls $v_c$ towards the true context and away from the model's current average. Cost $O(|V|d)$ per pair: infeasible for $|V|=10^6$, hence negative sampling (or hierarchical softmax).

**SGNS gradient.** Using $\frac{d}{dx}\log\sigma(x)=1-\sigma(x)$ and $\frac{d}{dx}\log\sigma(-x)=-\sigma(x)$:
$$\frac{\partial\ell}{\partial v_c}=(\sigma(u_o^\top v_c)-1)\,u_o+\sum_k\sigma(u_{n_k}^\top v_c)\,u_{n_k},\quad
\frac{\partial\ell}{\partial u_o}=(\sigma(u_o^\top v_c)-1)\,v_c,\quad
\frac{\partial\ell}{\partial u_{n_k}}=\sigma(u_{n_k}^\top v_c)\,v_c.$$
Cost $O(Kd)$. The $3/4$ power flattens the noise distribution: a word 16 times more frequent is sampled only $16^{3/4}=8$ times more often (`test_noise_distribution_is_unigram_to_three_quarters`).

**Why analogies can work.** If a word's context distribution is (approximately) a product of factors, e.g. role and gender, then its vector is (approximately) a sum of factor directions, and $v_{\text{queen}}\approx v_{\text{king}}-v_{\text{man}}+v_{\text{woman}}$. `word2vec_toy.make_analogy_corpus` plants exactly this structure; with it the analogy accuracy is 1.00 over 132 role pairs. Real corpora only approximately factorise; analogies are fragile across runs [S9 sl. 18].

## Worked example: one SGNS step

$v_c=(0.5,0.1)$, $u_o=(0.4,0.2)$, one negative $u_n=(-0.3,0.6)$, learning rate $0.1$.
- $u_o^\top v_c=0.22$, $\sigma=0.5548$; $u_n^\top v_c=-0.09$, $\sigma=0.4775$.
- $\ell=-\ln0.5548-\ln(1-0.4775)=0.5892+0.6493=1.2383$.
- $\nabla_{v_c}=(0.5548-1)(0.4,0.2)+0.4775(-0.3,0.6)=(-0.3213,\,0.1975)$.
- $\nabla_{u_o}=-0.4452\,(0.5,0.1)=(-0.2226,-0.0445)$; $\nabla_{u_n}=0.4775\,(0.5,0.1)=(0.2388,0.0478)$.
- After the step: $v_c=(0.5321,0.0803)$, $u_o=(0.4223,0.2045)$, $u_n=(-0.3239,0.5952)$; loss $1.2126$.

## Embeddings in IR

- **Query expansion**: add the nearest neighbours of each query term with their similarity as weight, into a translation-model style BM25 [S9 sl. 24].
- **Topic shifting**: neighbours in embedding space are *related*, not *equivalent*: "Austria" is close to "Germany", "Hungary"; expanding "hotels in Austria" retrieves German hotels [S9 sl. 25]. Retrofitting pulls vectors towards an external lexicon's synonyms [S9 sl. 26].
- **Limitations**: one vector per word (senses are averaged) and no word order ("not good" vs "not bad") [S9 sl. 21-22]. Contextual encoders (notes 07, 10) remove both.

## Pitfalls

- **Know whether the analogy search excludes the query words.** The famous king - man + woman = queen depends on it: popular library code silently drops $a,b,c$ from the candidates, and without that the nearest vector is often `king` itself [S9 sl. 19]. `analogy()` excludes them (the usual 3CosAdd convention), so its 1.00 accuracy is conditional on that choice.
- Which matrix is "the embedding": usually $V$ (centre); $V+U$ is also used. They differ: $V$ neighbours of `king` in the toy include its context words `reign, throne, crown` (words sharing contexts), not only `queen`.
- Cosine, not dot product, for similarity: frequent words have larger norms.
- In the update, repeated indices in a mini-batch must accumulate (`np.add.at`), not overwrite; a fancy-index `V[idx] -= g` silently drops duplicates.
- word2vec is a unigram model of words: it learns one vector per word, it does not build n-gram representations [S19]. That is what 1D CNNs are for (note 07).

## Questions

**Q:** Derive the gradient of the skip-gram negative-sampling loss with respect to $v_c$.
**A:** $\partial\ell/\partial v_c=(\sigma(u_o^\top v_c)-1)u_o+\sum_k\sigma(u_{n_k}^\top v_c)u_{n_k}$ from $\frac{d}{dx}\log\sigma(x)=1-\sigma(x)$.

**Q:** Why negative sampling, and why the $3/4$ power?
**A:** The softmax normaliser costs $O(|V|)$ per pair; $K$ logistic contrasts cost $O(K)$. The $3/4$ power samples rare words more often than their frequency, frequent words less, which empirically gives better vectors [S30].

**Q:** Contrast word2vec and GloVe.
**A:** word2vec is a predictive local-window objective trained by SGD over the corpus; GloVe fits $w_i^\top\tilde w_j+b_i+\tilde b_j\approx\log X_{ij}$ on global co-occurrence counts with a weighting $f$ that caps frequent pairs and ignores zeros.

**Q:** Why can word embeddings hurt as query expansion?
**A:** Topic shifting: neighbours share contexts but are not substitutes (neighbouring countries, antonyms); expansion adds documents about the neighbour [S9 sl. 25].

**Q:** What two limitations of static embeddings motivate contextual models?
**A:** One vector per word regardless of sense; no word order or local context within the representation [S9 sl. 21-22].

## Code

[`../src/py/word2vec_toy.py`](../src/py/word2vec_toy.py): `make_analogy_corpus` (role × gender grammar), `Vocab.noise` (unigram$^{3/4}$), `skipgram_pairs`, `sgns_loss_grads` (the gradients above, finite-difference tested), `train_sgns` (numpy, linear learning-rate decay, `np.add.at`), `most_similar`, `analogy`, `analogy_accuracy`. The test `test_topic_coherence_on_ir_collection` trains on the planted IR collection: nearest neighbours of a topic term are terms or aliases of the same topic.
