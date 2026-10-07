import math

import pytest

from bm25 import BM25, QueryLikelihood, bm25_tf, idf_rsj0, lecture_example, rsj_weight
from corpus import make_collection
from inverted_index import InvertedIndex

# 5 documents, no stop words involved; N = 5, avgdl = 16/5 = 3.2
DOCS = {
    "d1": "apple banana apple",
    "d2": "banana cherry",
    "d3": "cherry cherry cherry date",
    "d4": "date elder fig",
    "d5": "fig grape apple banana",
}


@pytest.fixture
def ix():
    return InvertedIndex(DOCS, stopwords=None)


def test_lecture_example_numbers():                    # [S6 sl. 71]: 87, 75 vs 31, 42.7
    t1, t2, b1, b2 = lecture_example()
    assert (t1, t2) == (87.0, 75.0)
    assert b1 == pytest.approx(31, abs=0.1) and b2 == pytest.approx(42.7, abs=0.05)
    assert b2 > b1 and t1 > t2                            # saturation flips the ranking


def test_bm25_hand_computed(ix):
    # query 'apple cherry', k1 = 1.2, b = 0.75. df(apple) = 2, df(cherry) = 2, N = 5
    idf = math.log((5 - 2 + 0.5) / (2 + 0.5))           # ln 1.4 = 0.33647
    assert idf == pytest.approx(0.336472, abs=1e-6)
    K = lambda dl: 1.2 * (0.25 + 0.75 * dl / 3.2)
    d1 = 2 / (K(3) + 2) * idf                            # apple tf 2, dl 3
    d3 = 3 / (K(4) + 3) * idf                            # cherry tf 3, dl 4
    s = BM25(ix).scores("apple cherry")
    assert s["d1"] == pytest.approx(d1) and s["d3"] == pytest.approx(d3)
    assert s["d1"] == pytest.approx(0.214058, abs=1e-6) and s["d3"] == pytest.approx(0.228117, abs=1e-6)
    assert "d4" not in s


def test_bm25_limits(ix):
    # k1 = 0: binary model, score = sum of idf of matched terms [S6 sl. 72]
    s = BM25(ix, k1=0.0).scores("apple cherry")
    assert s["d1"] == pytest.approx(idf_rsj0(5, 2)) and s["d3"] == pytest.approx(idf_rsj0(5, 2))
    # tf -> infinity: tf component -> 1, or k1+1 with plus_one
    assert bm25_tf(1e9, 3, 3) == pytest.approx(1.0) and bm25_tf(1e9, 3, 3, plus_one=True) == pytest.approx(2.2)
    # b = 0: no length normalisation
    assert bm25_tf(2, 100, 3, b=0) == bm25_tf(2, 1, 3, b=0)
    # plus_one is rank-equivalent
    r1 = [d for d, _ in BM25(ix).rank("apple banana cherry")]
    r2 = [d for d, _ in BM25(ix, plus_one=True).rank("apple banana cherry")]
    assert r1 == r2


def test_negative_idf_and_lucene_floor():
    assert idf_rsj0(3, 2) < 0                             # df > N/2
    ix3 = InvertedIndex({"a": "x y", "b": "x z", "c": "w"}, stopwords=None)
    assert BM25(ix3).scores("x")["a"] < 0
    assert BM25(ix3, lucene_idf=True).scores("x")["a"] > 0


def test_rsj_weight_reduces_to_idf_without_relevance_info():
    assert rsj_weight(N=100, n=10, R=0, r=0) == pytest.approx(idf_rsj0(100, 10))
    assert rsj_weight(100, 10, 5, 4) > rsj_weight(100, 10, 5, 1)


def test_query_likelihood_dirichlet_hand_computed(ix):
    ql = QueryLikelihood(ix, mu=2.0)
    # p_C(apple) = 3/16, p_C(cherry) = 4/16; d1: dl 3, apple tf 2, cherry tf 0
    p_apple = (2 + 2 * 3 / 16) / (3 + 2)
    p_cherry = (0 + 2 * 4 / 16) / (3 + 2)
    assert ql.scores("apple cherry")["d1"] == pytest.approx(math.log(p_apple) + math.log(p_cherry))


def test_query_likelihood_sparse_form_is_rank_equivalent():
    c = make_collection(seed=4)
    ix = InvertedIndex(c.docs)
    ql = QueryLikelihood(ix, mu=50)
    for q in list(c.queries.values())[:15]:
        full, sparse = ql.scores(q), ql.scores_sparse(q)
        diffs = {round(full[d] - sparse[d], 9) for d in full}   # differ by a query-only constant
        assert len(diffs) == 1


def test_jelinek_mercer_and_dirichlet_limits(ix):
    # lambda -> 1: every document gets the collection model -> equal scores
    s = QueryLikelihood(ix, lam=1.0).scores("apple cherry")
    assert len({round(v, 12) for v in s.values()}) == 1
    # mu -> 0: maximum likelihood; a document missing a query term scores -inf (log 0 guarded)
    ql = QueryLikelihood(ix, mu=1e-9)
    assert ql.p_term("apple", 0) == pytest.approx(2 / 3)


def test_vocabulary_mismatch_on_planted_collection():
    """Queries written in document vocabulary vs only in aliases: the lexical model collapses."""
    from metrics import mean_metric, reciprocal_rank

    c = make_collection()
    ix = InvertedIndex(c.docs)
    rel = c.binary_qrels()
    bm = BM25(ix)
    alias = set(sum(c.aliases, []))
    only_alias = [q for q in c.queries if all(w in alias for w in c.queries[q].split())]
    no_alias = [q for q in c.queries if not any(w in alias for w in c.queries[q].split())]
    mrr = lambda qs: mean_metric(lambda q: reciprocal_rank([d for d, _ in bm.rank(c.queries[q], 10)], rel[q]), qs)
    assert len(only_alias) > 30 and len(no_alias) > 30
    assert mrr(no_alias) > 0.8
    assert mrr(only_alias) < mrr(no_alias) - 0.4
