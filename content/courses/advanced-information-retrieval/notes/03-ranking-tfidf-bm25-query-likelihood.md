# 03 Crash course II: ranking with TF-IDF, BM25 and query likelihood

Three unsupervised scoring functions over the statistics of note 02. BM25 is the
baseline every neural model in this course is compared against, and the first
stage every re-ranker sits on [S6 sl. 41-75, S23].

## Definitions

Notation: $tf_{t,d}$ occurrences of $t$ in $d$; $df_t$ documents containing $t$; $N$ documents; $dl_d$ length of $d$; $avgdl$ mean length; $cf_t=\sum_d tf_{t,d}$; $|C|=\sum_d dl_d$.

1. **TF-IDF** (lecture form) [S6 sl. 54]: $\displaystyle \mathrm{TFIDF}(q,d)=\sum_{t\in q\cap d}\log(1+tf_{t,d})\cdot\log\frac{N}{df_t}$.
2. **BM25** (lecture form, Robertson and Zaragoza 2009) [S6 sl. 68, S23 eq. 3.15]:
$$\mathrm{BM25}(q,d)=\sum_{t\in q\cap d}\frac{tf_{t,d}}{k_1\bigl((1-b)+b\,\frac{dl_d}{avgdl}\bigr)+tf_{t,d}}\;\log\frac{N-df_t+0.5}{df_t+0.5}.$$
   Many implementations multiply by $(k_1+1)$ (rank-equivalent, makes the tf part 1 at $tf=1$, $dl=avgdl$) [S6 sl. 70]. Typical $1.2\le k_1\le2$, $0.5\le b\le0.8$ [S6 sl. 72].
3. **RSJ weight** with relevance information ($R$ known relevant, $r$ of them contain $t$, $n=df_t$) [S23 eq. 3.2]:
$$w^{RSJ}_t=\log\frac{(r+0.5)(N-R-n+r+0.5)}{(n-r+0.5)(R-r+0.5)};\qquad R=r=0\ \Rightarrow\ \log\frac{N-n+0.5}{n+0.5}.$$
4. **Query likelihood (QL)**: rank by $\log p(q\mid\theta_d)=\sum_{t\in q}\log p(t\mid\theta_d)$, a unigram language model per document, smoothed with the collection model $p(t\mid C)=cf_t/|C|$ [S24]:
   - Jelinek-Mercer: $p_\lambda(t\mid d)=(1-\lambda)\frac{tf_{t,d}}{dl_d}+\lambda\,p(t\mid C)$.
   - Dirichlet: $p_\mu(t\mid d)=\dfrac{tf_{t,d}+\mu\,p(t\mid C)}{dl_d+\mu}$ (a Bayesian posterior mean with a Dirichlet prior of mass $\mu$ centred on the collection model).

## Results

**BM25 from the eliteness model** [S23 §3.4]. BIM (binary independence) gives the presence weight $w^{RSJ}$. Modelling $tf$ as a mixture of two Poissons (elite vs non-elite documents for $t$) gives a weight that increases in $tf$, saturates, and tends to $w^{RSJ}$ as $tf\to\infty$ [S23 eq. 3.8-3.9]. BM25 replaces the unwieldy exact form by the simplest function with those properties, $\frac{tf}{k_1+tf}\,w^{RSJ}$ [S23 eq. 3.10-3.11], then normalises $tf$ by length, $tf'=tf/B$ with $B=(1-b)+b\,dl/avgdl$ [S23 eq. 3.12-3.13]:
$$\frac{tf'}{k_1+tf'}=\frac{tf}{k_1B+tf}.$$
Limits: $k_1=0$ gives the binary model $\sum_{t\in q\cap d} w_t$; $k_1\to\infty$ gives $tf$ linear; $b=0$ no length normalisation, $b=1$ full (relative frequency) [S6 sl. 72].

**Negative idf.** $\log\frac{N-df+0.5}{df+0.5}<0$ iff $df>N/2$: a term in more than half of the documents lowers the score of documents containing it. Lucene uses $\log\bigl(1+\frac{N-df+0.5}{df+0.5}\bigr)\ge0$.

**Dirichlet QL is TF-IDF-like.** Split the sum into terms present and absent in $d$:
$$\log p(q\mid d)=\sum_{t\in q\cap d}\log\frac{tf_{t,d}+\mu p(t\mid C)}{\mu p(t\mid C)}+\sum_{t\in q}\log\frac{\mu\,p(t\mid C)}{dl_d+\mu}
=\sum_{t\in q\cap d}\log\Bigl(1+\frac{tf_{t,d}}{\mu\,p(t\mid C)}\Bigr)+|q|\log\frac{\mu}{dl_d+\mu}+\underbrace{\sum_{t\in q}\log p(t\mid C)}_{\text{same for all }d}.$$
The first term grows with $tf$ and with rarity ($1/p(t\mid C)$ acts as idf); the second is a document-length prior. Only matching postings need to be touched.

## Worked examples

**Saturation flips a ranking** [S6 sl. 71]. Query `machine learning`, $\log_2(N/df)$: learning 7, machine 10. doc1: learning 1024, machine 1; doc2: learning 16, machine 8; $dl=avgdl$.
- TF-IDF with $1+\log_2 tf$: doc1 $11\cdot7+1\cdot10=87$, doc2 $5\cdot7+4\cdot10=75$: doc1 wins on one hammered term.
- BM25, $k_1=2$, $(k_1+1)$ form: $\frac{3\cdot1024}{2+1024}=2.99$, $\frac{3\cdot1}{3}=1$, $\frac{3\cdot16}{18}=2.67$, $\frac{3\cdot8}{10}=2.4$: doc1 $30.96$, doc2 $42.67$: doc2 wins, covering both terms.

**BM25 by hand** (`test_bm25_hand_computed`). Five documents: d1 `apple banana apple` (3), d2 `banana cherry` (2), d3 `cherry cherry cherry date` (4), d4 `date elder fig` (3), d5 `fig grape apple banana` (4); $N=5$, $avgdl=16/5=3.2$. Query `apple cherry`, $k_1=1.2$, $b=0.75$. $df=2$ for both, $idf=\ln\frac{3.5}{2.5}=0.33647$.
- d1: $K=1.2(0.25+0.75\cdot3/3.2)=1.14375$, $\frac{2}{1.14375+2}\cdot0.33647=0.21406$.
- d3: $K=1.2(0.25+0.75\cdot4/3.2)=1.425$, $\frac{3}{4.425}\cdot0.33647=0.22812$.
- d2 ($tf=1$, $dl=2$): $0.18066$; d5 ($tf=1$, $dl=4$): $0.13875$. Ranking d3, d1, d2, d5.

**Dirichlet QL**, $\mu=2$: $p(\text{apple}\mid C)=3/16$, $p(\text{cherry}\mid C)=4/16$. d1: $\frac{2+0.375}{5}=0.475$, $\frac{0+0.5}{5}=0.1$, $\log$-likelihood $-3.047$. d3: $\frac{0.375}{6}=0.0625$, $\frac{3.5}{6}=0.5833$, $-3.312$. Now d1 beats d3: with small $\mu$ QL is closer to "cover every query term" than BM25 with these parameters.

**On the planted collection** (`bm25.py` demo, 240 queries, MRR@10 / nDCG@10): TF-IDF 0.635 / 0.820, BM25 0.610 / 0.814, BM25 $b=0$ 0.623 / 0.811, QL Dirichlet $\mu=100$ 0.592 / 0.811. The 54 queries written only in aliases: BM25 MRR@10 **0.333**: vocabulary mismatch, which no parameter fixes.

## Pitfalls

- **Log bases and tf variants differ between slides.** Sl. 54 uses $\log(1+tf)$, the example on sl. 71 uses $1+\log tf$ (Stanford CS276). Say which one you use.
- **BM25 without $(k_1+1)$** has maximum 1 per term; with it, $k_1+1$. Same ranking, different score scale.
- Negative idf for $df>N/2$ is real in the lecture's formula; on small or topical collections it bites.
- Parameters are collection-specific; defaults are not "BM25", they are one BM25.
- QL with $\mu\to0$ (maximum likelihood) gives $-\infty$ to any document missing a query term. Smoothing is not optional.
- Repeated query terms count repeatedly in all three models (query term frequency). Deduplicating the query changes the model.

## Questions

**Q:** Write down BM25 and explain the role of $k_1$ and $b$.
**A:** Definition 2. $k_1$ controls tf saturation ($0$: binary, $\infty$: linear); $b$ controls length normalisation ($0$: none, $1$: full relative frequency).

**Q:** Why does BM25 saturate term frequency, and where does the functional form come from?
**A:** Under the eliteness (2-Poisson) model the evidence from more occurrences has diminishing returns and approaches the presence weight $w^{RSJ}$; $tf/(k_1+tf)$ is the simplest increasing, saturating function with that limit [S23 §3.4].

**Q:** When is the BM25 idf negative, and how does Lucene avoid it?
**A:** When $df_t>N/2$. Lucene uses $\log(1+\frac{N-df+0.5}{df+0.5})$.

**Q:** Show that Dirichlet-smoothed QL contains an idf-like and a length-normalisation component.
**A:** The rewriting above: $\log(1+tf/(\mu p(t\mid C)))$ grows as $p(t\mid C)$ shrinks (idf); $|q|\log\frac{\mu}{dl+\mu}$ penalises long documents; the rest is constant per query.

**Q:** Compute the BM25 tf component for $tf=3$, $dl=4$, $avgdl=3.2$, $k_1=1.2$, $b=0.75$.
**A:** $K=1.2\,(0.25+0.9375)=1.425$; $3/(1.425+3)=0.678$.

## Code

[`../src/py/bm25.py`](../src/py/bm25.py):
- `bm25_tf(tf, dl, avgdl, k1, b, plus_one)`, `idf_rsj0(N, df)`, `rsj_weight(N, n, R, r)`.
- `BM25(index, k1, b, plus_one, lucene_idf)`: `scores`, `rank`.
- `QueryLikelihood(index, mu, lam)`: `scores` (full log-likelihood), `scores_sparse` (the rank-equivalent form above, tested equal up to a query constant).
- `lecture_example()`: reproduces 87 / 75 vs 31 / 42.7.
