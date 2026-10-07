from corpus import make_collection


def test_planted_relevance_is_consistent():
    c = make_collection(seed=0)
    assert len(c.docs) == 300 and len(c.queries) == 240
    rel = c.binary_qrels()
    for q, (j1, j2) in c.query_concepts.items():
        assert rel[q], q                                      # the source document is always relevant
        t = c.query_topic[q]
        for d, g in c.qrels[q].items():
            assert c.doc_topic[d] == t and g == 1 + len({j1, j2} & c.doc_facet[d])
        words = c.queries[q].split()
        assert all(w in (c.terms[t][j], c.aliases[t][j]) for w, j in zip(words, (j1, j2)))


def test_deterministic_and_split_disjoint():
    a, b = make_collection(seed=7), make_collection(seed=7)
    assert a.docs == b.docs and a.queries == b.queries
    tr, te = a.split_queries(40)
    assert len(te) == 40 and not set(tr) & set(te) and len(tr) + len(te) == len(a.queries)
