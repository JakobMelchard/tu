"""BM25 and query likelihood with Dirichlet / Jelinek-Mercer smoothing.

Note 03. BM25 in the lecture's form [S6 sl. 68], which is Robertson &
Zaragoza's eq. (3.15) with the RSJ weight replaced by the no-relevance idf
[S23 eq. 3.2, 3.12-3.15]:

$$\\mathrm{BM25}(q,d)=\\sum_{t\\in q\\cap d}\\frac{tf_{t,d}}{k_1\\bigl((1-b)+b\\,dl_d/avgdl\\bigr)+tf_{t,d}}
\\log\\frac{N-df_t+0.5}{df_t+0.5}.$$

`plus_one=True` multiplies by $(k_1+1)$ (rank-equivalent, makes tf = 1 score 1
at dl = avgdl [S6 sl. 70]). Query likelihood: $\\sum_{t\\in q}\\log p(t\\mid\\theta_d)$
with $p_\\mu(t\\mid d)=(tf_{t,d}+\\mu p(t\\mid C))/(dl_d+\\mu)$ [S24].
"""
from __future__ import annotations

import math

import numpy as np

from inverted_index import InvertedIndex


def bm25_tf(tf: float, dl: float, avgdl: float, k1: float = 1.2, b: float = 0.75, plus_one: bool = False) -> float:
    """Saturating tf component; tends to 1 (or k1+1) as tf -> infinity."""
    norm = k1 * ((1 - b) + b * dl / avgdl)
    return tf * ((k1 + 1) if plus_one else 1.0) / (norm + tf)


def idf_rsj0(N: int, df: int) -> float:
    """RSJ weight with no relevance information; negative when df > N/2 [S23 §3.3]."""
    return math.log((N - df + 0.5) / (df + 0.5))


def rsj_weight(N: int, n: int, R: int, r: int) -> float:
    """Robertson/Sparck Jones weight [S23 eq. 3.2]: n docs contain t, R known relevant, r of them contain t."""
    return math.log(((r + 0.5) * (N - R - n + r + 0.5)) / ((n - r + 0.5) * (R - r + 0.5)))


class BM25:
    def __init__(self, index: InvertedIndex, k1: float = 1.2, b: float = 0.75,
                 plus_one: bool = False, lucene_idf: bool = False):
        self.ix, self.k1, self.b, self.plus_one, self.lucene_idf = index, k1, b, plus_one, lucene_idf

    def idf(self, t: str) -> float:
        df = self.ix.df(t)
        if self.lucene_idf:                       # log(1 + ...) is always >= 0
            return math.log(1 + (self.ix.N - df + 0.5) / (df + 0.5))
        return idf_rsj0(self.ix.N, df)

    def scores(self, query: str) -> dict[str, float]:
        acc: dict[int, float] = {}
        for t in self.ix.analyze(query):          # repeated query terms count repeatedly
            if t not in self.ix.postings:
                continue
            w = self.idf(t)
            for n, tf, _ in self.ix.postings[t]:
                acc[n] = acc.get(n, 0.0) + w * bm25_tf(tf, self.ix.doc_len[n], self.ix.avgdl,
                                                        self.k1, self.b, self.plus_one)
        return {self.ix.doc_ids[n]: s for n, s in acc.items()}

    def rank(self, query: str, k: int = 1000) -> list[tuple[str, float]]:
        return sorted(self.scores(query).items(), key=lambda x: (-x[1], x[0]))[:k]


class QueryLikelihood:
    """Unigram language model per document, smoothed with the collection model."""

    def __init__(self, index: InvertedIndex, mu: float = 100.0, lam: float | None = None):
        self.ix, self.mu, self.lam = index, mu, lam
        total = sum(index.doc_len)
        self.p_c = {t: sum(f for _, f, _ in p) / total for t, p in index.postings.items()}

    def p_term(self, t: str, n: int) -> float:
        tf, dl = self.ix.tf(t, n), self.ix.doc_len[n]
        if self.lam is not None:                  # Jelinek-Mercer
            return (1 - self.lam) * (tf / dl if dl else 0.0) + self.lam * self.p_c[t]
        return (tf + self.mu * self.p_c[t]) / (dl + self.mu)

    def scores(self, query: str) -> dict[str, float]:
        """Full log-likelihood over all documents; unseen-in-collection terms are dropped."""
        terms = [t for t in self.ix.analyze(query) if t in self.p_c]
        return {self.ix.doc_ids[n]: sum(math.log(self.p_term(t, n)) for t in terms) for n in range(self.ix.N)}

    def scores_sparse(self, query: str) -> dict[str, float]:
        """Rank-equivalent Dirichlet form touching only matching postings [S24]:
        sum_{t in q cap d} log(1 + tf/(mu p_C)) + |q| log(mu/(dl+mu))."""
        terms = [t for t in self.ix.analyze(query) if t in self.p_c]
        out = {did: len(terms) * math.log(self.mu / (self.ix.doc_len[n] + self.mu))
               for n, did in enumerate(self.ix.doc_ids)}
        for t in terms:
            for n, tf, _ in self.ix.postings[t]:
                out[self.ix.doc_ids[n]] += math.log(1 + tf / (self.mu * self.p_c[t]))
        return out

    def rank(self, query: str, k: int = 1000) -> list[tuple[str, float]]:
        return sorted(self.scores_sparse(query).items(), key=lambda x: (-x[1], x[0]))[:k]


def lecture_example(k1: float = 2.0) -> tuple[float, float, float, float]:
    """[S6 sl. 71]: query 'machine learning', idf(learning)=7, idf(machine)=10 (log2 |D|/df),
    doc1 learning 1024 machine 1, doc2 learning 16 machine 8, dl = avgdl.
    Returns (tfidf doc1, tfidf doc2, bm25 doc1, bm25 doc2): 87, 75, 31, 42.7 on the slide."""
    idf_l, idf_m = 7.0, 10.0
    tfidf = lambda tl, tm: (1 + math.log2(tl)) * idf_l + (1 + math.log2(tm)) * idf_m   # slide uses 1+log2 tf
    bm = lambda tl, tm: idf_l * bm25_tf(tl, 1, 1, k1, 0.0, True) + idf_m * bm25_tf(tm, 1, 1, k1, 0.0, True)
    return tfidf(1024, 1), tfidf(16, 8), bm(1024, 1), bm(16, 8)


def run_ranker(ranker, queries: dict[str, str], k: int = 100) -> dict[str, list[str]]:
    return {q: [d for d, _ in ranker.rank(text, k)] for q, text in queries.items()}


if __name__ == "__main__":
    from corpus import make_collection
    from metrics import mean_metric, ndcg_at_k, reciprocal_rank

    print("lecture example [S6 sl. 71] (tfidf d1, tfidf d2, bm25 d1, bm25 d2):",
          [round(x, 2) for x in lecture_example()])
    c = make_collection()
    ix = InvertedIndex(c.docs)
    rel = c.binary_qrels()

    class TFIDF:
        def rank(self, q, k):
            return sorted(ix.score_taat(q).items(), key=lambda x: (-x[1], x[0]))[:k]

    for name, r in [("TF-IDF", TFIDF()), ("BM25 k1=1.2 b=0.75", BM25(ix)), ("BM25 b=0", BM25(ix, b=0.0)),
                    ("QL Dirichlet mu=100", QueryLikelihood(ix, mu=100)), ("QL JM lambda=0.5", QueryLikelihood(ix, lam=0.5))]:
        run = run_ranker(r, c.queries)
        mrr = mean_metric(lambda q: reciprocal_rank(run[q], rel[q], 10), c.queries)
        nd = mean_metric(lambda q: ndcg_at_k(run[q], c.qrels[q], 10), c.queries)
        print(f"{name:22s} MRR@10 {mrr:.3f}  nDCG@10 {nd:.3f}")
    alias_q = [q for q in c.queries if all(w in sum(c.aliases, []) for w in c.queries[q].split())]
    run = run_ranker(BM25(ix), {q: c.queries[q] for q in alias_q})
    print(f"BM25 on the {len(alias_q)} queries written only in aliases: MRR@10 "
          f"{mean_metric(lambda q: reciprocal_rank(run[q], rel[q], 10), alias_q):.3f} (vocabulary mismatch)")
