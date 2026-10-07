import numpy as np
import pytest

from word2vec_toy import (PAIRS, Vocab, analogy, analogy_accuracy, make_analogy_corpus, most_similar,
                          sgns_loss_grads, skipgram_pairs, train_sgns)


def test_skipgram_pairs_window():
    v = Vocab([["a", "b", "c", "d"]])
    pairs = {(v.itos[c], v.itos[o]) for c, o in skipgram_pairs([["a", "b", "c", "d"]], v, window=1)}
    assert pairs == {("a", "b"), ("b", "a"), ("b", "c"), ("c", "b"), ("c", "d"), ("d", "c")}
    assert len(skipgram_pairs([["a", "b", "c", "d"]], v, window=2)) == 2 + 3 + 3 + 2


def test_noise_distribution_is_unigram_to_three_quarters():
    v = Vocab([["x"] * 16 + ["y"]])
    p = v.noise()
    assert p[v.stoi["x"]] / p[v.stoi["y"]] == pytest.approx(16**0.75)   # = 8, not 16


def test_sgns_gradients_finite_differences():
    rng = np.random.default_rng(0)
    V, U = rng.normal(size=(7, 4)), rng.normal(size=(7, 4))
    c, o, neg = np.array([1]), np.array([2]), np.array([[3, 4, 5]])
    _, g_vc, g_uo, g_un = sgns_loss_grads(V, U, c, o, neg)
    eps = 1e-6

    def num(M, row):
        g = np.zeros(4)
        for j in range(4):
            Mp, Mm = M.copy(), M.copy()
            Mp[row, j] += eps; Mm[row, j] -= eps
            args = (Mp, U) if M is V else (V, Mp)
            g[j] = (sgns_loss_grads(*args, c, o, neg)[0] - sgns_loss_grads(*((Mm, U) if M is V else (V, Mm)), c, o, neg)[0]) / (2 * eps)
        return g

    assert np.allclose(g_vc[0], num(V, 1), atol=1e-6)
    assert np.allclose(g_uo[0], num(U, 2), atol=1e-6)
    for k, row in enumerate([3, 4, 5]):
        assert np.allclose(g_un[0, k], num(U, row), atol=1e-6)


def test_training_reduces_loss_and_solves_analogies():
    vocab, V, U, hist = train_sgns(make_analogy_corpus(seed=1), seed=1)
    assert hist[-50:].mean() < hist[:50].mean() - 0.5
    assert analogy(V, vocab, "man", "woman", "king") == "queen"
    assert analogy_accuracy(V, vocab) >= 0.9
    # the female counterpart is among the nearest *person* words
    persons = {w for p in PAIRS for w in p}
    near = [w for w, _ in most_similar(V, vocab, "prince", k=30) if w in persons]
    assert near[0] in {"princess", "king"}


def test_topic_coherence_on_ir_collection():
    """Terms of the same topic co-occur, so their embeddings end up close."""
    from corpus import make_collection
    from inverted_index import tokenize

    c = make_collection()
    sents = [tokenize(t) for t in c.docs.values()]
    vocab, V, _, _ = train_sgns(sents, dim=24, window=3, epochs=4, seed=0)
    hits = 0
    for t in range(10):
        w = c.terms[t][0]
        near = [x for x, _ in most_similar(V, vocab, w, k=5)]
        hits += sum(x in c.terms[t] or x in c.aliases[t] for x in near)
    assert hits / 50 > 0.7
