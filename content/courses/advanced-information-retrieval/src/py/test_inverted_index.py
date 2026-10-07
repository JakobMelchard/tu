import math

import numpy as np
import pytest

from corpus import make_collection
from inverted_index import (InvertedIndex, difference, intersect, light_stem, tokenize,
                            union, vbyte_decode, vbyte_encode)

DOCS = {
    "a": "This is a sample document, full of infos.",
    "b": "Sample documents and more samples.",
    "c": "Nothing to see here: full stop.",
}


def test_tokenize_case_folding_punctuation_stopwords():
    assert tokenize("This is a sample document - full of infos.") == ["this", "sample", "document", "full", "infos"]
    assert tokenize("U.S.A 25.9.2018", stopwords=None) == ["u", "s", "a", "25", "9", "2018"]  # [S6 sl. 13]


def test_light_stem():
    assert [light_stem(w) for w in ["infos", "classes", "ponies", "walked", "running", "sing", "glass"]] == \
        ["info", "class", "poni", "walk", "runn", "sing", "glass"]


def test_index_statistics():
    idx = InvertedIndex(DOCS, stem=True)
    assert idx.N == 3
    assert idx.df("sampl") == 0 and idx.df("sample") == 2         # 'samples' -> 'sample'
    assert idx.tf("sample", 1) == 2 and idx.tf("document", 1) == 1
    assert idx.doc_len == [5, 4, 5]                                # stop words removed
    assert idx.avgdl == pytest.approx(14 / 3)


def test_merges_against_python_sets():
    rng = np.random.default_rng(1)
    for _ in range(50):
        a = sorted(set(rng.integers(0, 60, 25).tolist()))
        b = sorted(set(rng.integers(0, 60, 25).tolist()))
        assert intersect(a, b) == sorted(set(a) & set(b))
        assert union(a, b) == sorted(set(a) | set(b))
        assert difference(a, b) == sorted(set(a) - set(b))


def test_boolean_parser_against_brute_force():
    c = make_collection(seed=3)
    idx = InvertedIndex(c.docs)
    sets = {d: set(idx.analyze(t)) for d, t in c.docs.items()}
    x, y, z = c.terms[0][0], c.terms[0][1], c.terms[1][0]
    cases = {
        f"{x} AND {y}": lambda s: x in s and y in s,
        f"{x} OR {z}": lambda s: x in s or z in s,
        f"{x} AND NOT {y}": lambda s: x in s and y not in s,
        f"({x} OR {z}) AND NOT ({y} OR {c.terms[1][1]})": lambda s: (x in s or z in s) and not (y in s or c.terms[1][1] in s),
        f"NOT {x} AND {y} OR {z}": lambda s: ((x not in s) and y in s) or z in s,
    }
    for q, pred in cases.items():
        assert sorted(idx.boolean(q)) == sorted(d for d, s in sets.items() if pred(s)), q


def test_phrase_query():
    idx = InvertedIndex({"1": "new york city", "2": "york new city", "3": "the new big york"}, stopwords=None)
    assert idx.phrase("new york") == ["1"]
    assert idx.phrase("york city") == ["1"]
    assert idx.phrase("new") == ["1", "2", "3"]


def test_tfidf_hand_computed():
    idx = InvertedIndex(DOCS, stem=True)
    s = idx.score_taat("sample full")
    # doc b: 'sample' tf 2, df 2 -> log(3) log(3/2); doc a: sample tf1 + full tf1 (df 2)
    assert s["b"] == pytest.approx(math.log(3) * math.log(1.5))
    assert s["a"] == pytest.approx(2 * math.log(2) * math.log(1.5))
    assert s["c"] == pytest.approx(math.log(2) * math.log(1.5))


def test_daat_equals_taat_topk():
    """Same top-k scores; ties may be broken differently, so compare the score multiset."""
    c = make_collection(seed=5)
    idx = InvertedIndex(c.docs)
    for q in list(c.queries.values())[:40]:
        taat = sorted(idx.score_taat(q).values(), reverse=True)[:10]
        daat = [s for _, s in idx.topk_daat(q, 10)]
        assert daat == pytest.approx(taat)


def test_tfidf_cross_check_with_sklearn():
    """sklearn with sublinear_tf=False computes tf*(ln(N/df)+1); rebuild our variant from its matrix."""
    from sklearn.feature_extraction.text import CountVectorizer

    c = make_collection(seed=2)
    idx = InvertedIndex(c.docs, stopwords=None)
    cv = CountVectorizer(token_pattern=r"[a-z0-9]+")
    X = cv.fit_transform(list(c.docs.values())).toarray()
    df = (X > 0).sum(0)
    W = np.log1p(X) * np.log(len(c.docs) / df)
    for qid in list(c.queries)[:20]:
        q = c.queries[qid]
        cols = [cv.vocabulary_[t] for t in idx.analyze(q) if t in cv.vocabulary_]
        ref = W[:, cols].sum(1)
        ours = idx.score_taat(q)
        for n, did in enumerate(c.docs):
            assert ours.get(did, 0.0) == pytest.approx(ref[n])


def test_vbyte_roundtrip_and_known_bytes():
    assert vbyte_encode([824, 829, 215406]) == bytes([0x06, 0xB8, 0x85, 0x0D, 0x0C, 0xB1])  # [S22 table 5.4]
    rng = np.random.default_rng(0)
    docs = sorted(set(rng.integers(0, 10**6, 500).tolist()))
    assert vbyte_decode(vbyte_encode(docs)) == docs
