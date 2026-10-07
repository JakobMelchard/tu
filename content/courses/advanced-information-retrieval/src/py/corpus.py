"""Synthetic test collection with planted relevance, shared by every module.

Notes 02-04 and 08-13. No download: a few hundred documents are generated from
a fixed seed so that the ground truth is known exactly.

Generative story (one topic = one "information need family"):
- each topic t owns `terms_per_topic` content words ("concepts") and, for each
  concept, an alias: a synonym that queries use but documents rarely contain.
  The alias is the planted vocabulary mismatch that lexical models cannot
  bridge and learned embeddings can [S12 sl. 43-47, S51].
- a document of topic t emphasises a *facet* of 3 of its topic's concepts;
  concept tokens are drawn from the facet with probability `facet_bias`.
- a query is made from a source document: two concepts of its facet, each
  written as the alias with probability `p_alias` (MS MARCO style: queries are
  sampled so that at least one relevant passage exists [S44]).
- graded relevance: 0 other topic, 1 same topic, 2 one queried concept in the
  facet, 3 both. Binary relevance (MRR, MAP) is grade 3, like the sparse
  MS MARCO labels [S7 sl. 10].
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

STOPWORDS = ("the", "of", "and", "a", "to", "in", "is", "for", "on", "with")
_CONS = "bdfgklmnprstvz"
_VOWS = "aeiou"


def pseudo_words(n: int, rng: np.random.Generator, taken: set[str]) -> list[str]:
    """n distinct pronounceable lowercase words (2-3 CV syllables), none in `taken`."""
    out: list[str] = []
    while len(out) < n:
        k = rng.integers(2, 4)
        w = "".join(rng.choice(list(_CONS)) + rng.choice(list(_VOWS)) for _ in range(k))
        if w not in taken:
            taken.add(w)
            out.append(w)
    return out


@dataclass
class Collection:
    docs: dict[str, str]                      # doc id -> text
    queries: dict[str, str]                   # query id -> text
    qrels: dict[str, dict[str, int]]          # query id -> doc id -> grade (>0 only)
    doc_topic: dict[str, int]
    doc_facet: dict[str, frozenset[int]]
    query_topic: dict[str, int]
    query_concepts: dict[str, tuple[int, int]]
    terms: list[list[str]]                    # terms[t][j]
    aliases: list[list[str]]                  # aliases[t][j], synonym of terms[t][j]
    background: list[str] = field(default_factory=list)

    def binary_qrels(self, min_grade: int = 3) -> dict[str, set[str]]:
        return {q: {d for d, g in r.items() if g >= min_grade} for q, r in self.qrels.items()}

    def split_queries(self, n_test: int, seed: int = 0) -> tuple[list[str], list[str]]:
        qids = sorted(self.queries)
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(qids))
        test = sorted(qids[i] for i in perm[:n_test])
        train = sorted(qids[i] for i in perm[n_test:])
        return train, test


def make_collection(n_topics: int = 20, docs_per_topic: int = 15, terms_per_topic: int = 8,
                    queries_per_topic: int = 12, n_background: int = 200, facet_size: int = 3,
                    facet_bias: float = 0.8, p_alias: float = 0.5, seed: int = 0) -> Collection:
    rng = np.random.default_rng(seed)
    taken = set(STOPWORDS)
    terms = [pseudo_words(terms_per_topic, rng, taken) for _ in range(n_topics)]
    aliases = [pseudo_words(terms_per_topic, rng, taken) for _ in range(n_topics)]
    background = pseudo_words(n_background, rng, taken)
    # Zipf-like background and stopword distributions: p(rank r) ~ 1/r
    zb = 1.0 / np.arange(1, n_background + 1); zb /= zb.sum()
    zs = 1.0 / np.arange(1, len(STOPWORDS) + 1); zs /= zs.sum()

    docs, doc_topic, doc_facet = {}, {}, {}
    for t in range(n_topics):
        for i in range(docs_per_topic):
            did = f"d{t:02d}{i:02d}"
            facet = rng.choice(terms_per_topic, size=facet_size, replace=False)
            toks = []
            for _ in range(int(rng.integers(40, 81))):
                u = rng.random()
                if u < 0.35:
                    toks.append(STOPWORDS[rng.choice(len(STOPWORDS), p=zs)])
                elif u < 0.60:
                    toks.append(background[rng.choice(n_background, p=zb)])
                elif u < 0.85:
                    j = rng.choice(facet) if rng.random() < facet_bias else rng.integers(terms_per_topic)
                    toks.append(terms[t][j])
                elif u < 0.90:                      # aliases occur, but not facet-specifically
                    toks.append(aliases[t][rng.integers(terms_per_topic)])
                else:                               # off-topic noise
                    o = (t + 1 + rng.integers(n_topics - 1)) % n_topics
                    toks.append(terms[o][rng.integers(terms_per_topic)])
            docs[did] = _render(toks, rng)
            doc_topic[did] = t
            doc_facet[did] = frozenset(int(j) for j in facet)

    queries, qrels, query_topic, query_concepts = {}, {}, {}, {}
    by_topic = {t: [d for d in docs if doc_topic[d] == t] for t in range(n_topics)}
    for t in range(n_topics):
        for k in range(queries_per_topic):
            qid = f"q{t:02d}{k:02d}"
            src = by_topic[t][rng.integers(docs_per_topic)]
            j1, j2 = sorted(int(j) for j in rng.choice(sorted(doc_facet[src]), size=2, replace=False))
            words = [aliases[t][j] if rng.random() < p_alias else terms[t][j] for j in (j1, j2)]
            queries[qid] = " ".join(words)
            query_topic[qid] = t
            query_concepts[qid] = (j1, j2)
            qrels[qid] = {d: 1 + len({j1, j2} & doc_facet[d]) for d in by_topic[t]}
    return Collection(docs, queries, qrels, doc_topic, doc_facet, query_topic,
                      query_concepts, terms, aliases, background)


def _render(tokens: list[str], rng: np.random.Generator) -> str:
    """Join tokens into 'sentences' with capitals and full stops (exercises the tokeniser)."""
    out, start = [], True
    for tok in tokens:
        out.append(tok.capitalize() if start else tok)
        start = rng.random() < 0.08
        if start:
            out[-1] += "."
    return " ".join(out) + "."


if __name__ == "__main__":
    c = make_collection()
    lens = [len(t.split()) for t in c.docs.values()]
    rel = c.binary_qrels()
    print(f"{len(c.docs)} docs, mean length {np.mean(lens):.1f}; {len(c.queries)} queries")
    print(f"relevant (grade 3) per query: mean {np.mean([len(v) for v in rel.values()]):.2f}")
    q = "q0000"
    print(f"{q}: '{c.queries[q]}' concepts {c.query_concepts[q]}; aliases of topic 0: {c.aliases[0][:4]}")
    print("d0000:", c.docs["d0000"][:160], "...")
