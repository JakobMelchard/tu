"""Tokeniser, positional inverted index, boolean / phrase / ranked retrieval.

Note 02 (indexing, preprocessing) and note 03 (TF-IDF). Follows the crash
course [S6 sl. 8-22, 47-55] and Manning et al. [S22 ch. 1-2, 5, 6].

- `tokenize`: case folding, split on non-alphanumerics, optional stop-word
  removal and a light suffix-stripping stemmer (Porter step 1a/1b flavour).
- `InvertedIndex`: term -> postings list [(doc, tf, positions)] sorted by doc
  number, plus df, document lengths and avgdl (the statistics BM25 needs).
- boolean retrieval by linear merges (`intersect`, `union`, `difference`) and a
  recursive-descent parser for AND / OR / NOT / parentheses.
- phrase queries by positional intersection.
- ranked retrieval: term-at-a-time accumulators (`score_taat`) and
  document-at-a-time with a size-k heap (`topk_daat`), both with the lecture's
  TF-IDF $\\sum_t \\log(1+tf_{t,d})\\log(|D|/df_t)$ [S6 sl. 54].
- postings compression: gap encoding + variable-byte codes [S22 §5.3].
"""
from __future__ import annotations

import heapq
import math
import re
from collections import defaultdict

from corpus import STOPWORDS

_TOKEN = re.compile(r"[a-z0-9]+")


def light_stem(w: str) -> str:
    """Crude affix chopping: sses->ss, ies->i, s->'' (not ss), ing/ed if a vowel remains."""
    if w.endswith("sses"):
        return w[:-2]
    if w.endswith("ies"):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    for suf in ("ing", "ed"):
        if w.endswith(suf) and re.search(r"[aeiou]", w[: -len(suf)]) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def tokenize(text: str, stopwords: tuple[str, ...] | None = STOPWORDS, stem: bool = False) -> list[str]:
    toks = _TOKEN.findall(text.lower())
    if stopwords:
        sw = set(stopwords)
        toks = [t for t in toks if t not in sw]
    return [light_stem(t) for t in toks] if stem else toks


class InvertedIndex:
    def __init__(self, docs: dict[str, str], stopwords=STOPWORDS, stem: bool = False):
        self.stopwords, self.stem = stopwords, stem
        self.doc_ids = list(docs)                      # doc number -> external id
        self.postings: dict[str, list[tuple[int, int, list[int]]]] = {}
        tmp: dict[str, dict[int, list[int]]] = defaultdict(dict)
        self.doc_len = []
        for n, did in enumerate(self.doc_ids):
            toks = self.analyze(docs[did])
            self.doc_len.append(len(toks))
            for pos, t in enumerate(toks):
                tmp[t].setdefault(n, []).append(pos)
        for t, per_doc in tmp.items():                 # docs were added in order: already sorted
            self.postings[t] = [(n, len(p), p) for n, p in per_doc.items()]
        self.N = len(self.doc_ids)
        self.avgdl = sum(self.doc_len) / self.N

    def analyze(self, text: str) -> list[str]:
        """Same pipeline for documents and queries, otherwise terms never match [S6 sl. 10]."""
        return tokenize(text, self.stopwords, self.stem)

    def df(self, t: str) -> int:
        return len(self.postings.get(t, ()))

    def docs_of(self, t: str) -> list[int]:
        return [n for n, _, _ in self.postings.get(t, ())]

    def tf(self, t: str, n: int) -> int:
        for m, f, _ in self.postings.get(t, ()):
            if m == n:
                return f
        return 0

    # ---------- boolean retrieval ----------
    def boolean(self, query: str) -> list[str]:
        """Evaluate e.g. 'a AND (b OR NOT c)'; NOT binds tighter than AND, AND tighter than OR."""
        toks = re.findall(r"\(|\)|[A-Za-z0-9]+", query)
        pos = 0

        def peek():
            return toks[pos] if pos < len(toks) else None

        def eat():
            nonlocal pos
            pos += 1
            return toks[pos - 1]

        def expr():
            left = term()
            while peek() == "OR":
                eat()
                left = union(left, term())
            return left

        def term():
            left = factor()
            while peek() == "AND":
                eat()
                left = intersect(left, factor())
            return left

        def factor():
            tok = eat()
            if tok == "NOT":
                return difference(list(range(self.N)), factor())
            if tok == "(":
                r = expr()
                eat()                                   # ')'
                return r
            a = self.analyze(tok)
            return self.docs_of(a[0]) if a else []

        return [self.doc_ids[n] for n in expr()]

    def phrase(self, text: str) -> list[str]:
        """Documents containing the analysed terms at consecutive positions."""
        terms = self.analyze(text)
        if not terms:
            return []
        cand = self.docs_of(terms[0])
        for t in terms[1:]:
            cand = intersect(cand, self.docs_of(t))
        out = []
        for n in cand:
            starts = set(self._positions(terms[0], n))
            for k, t in enumerate(terms[1:], 1):
                starts &= {p - k for p in self._positions(t, n)}
            if starts:
                out.append(self.doc_ids[n])
        return out

    def _positions(self, t: str, n: int) -> list[int]:
        for m, _, p in self.postings[t]:
            if m == n:
                return p
        return []

    # ---------- ranked retrieval ----------
    def tfidf_weight(self, t: str, tf: int) -> float:
        return math.log(1 + tf) * math.log(self.N / self.df(t))

    def score_taat(self, query: str) -> dict[str, float]:
        """Term-at-a-time: one accumulator per document touched by any query term."""
        acc: dict[int, float] = defaultdict(float)
        for t in self.analyze(query):
            for n, f, _ in self.postings.get(t, ()):
                acc[n] += self.tfidf_weight(t, f)
        return {self.doc_ids[n]: s for n, s in acc.items()}

    def topk_daat(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        """Document-at-a-time: advance a cursor per term to the smallest doc number, min-heap of size k."""
        terms = [t for t in self.analyze(query) if t in self.postings]
        cur = {t: 0 for t in terms}
        heap: list[tuple[float, int]] = []
        while True:
            live = [self.postings[t][cur[t]][0] for t in terms if cur[t] < len(self.postings[t])]
            if not live:
                break
            n = min(live)
            s = 0.0
            for t in terms:
                if cur[t] < len(self.postings[t]) and self.postings[t][cur[t]][0] == n:
                    s += self.tfidf_weight(t, self.postings[t][cur[t]][1])
                    cur[t] += 1
            if len(heap) < k:
                heapq.heappush(heap, (s, -n))
            elif (s, -n) > heap[0]:
                heapq.heapreplace(heap, (s, -n))
        return [(self.doc_ids[-m], s) for s, m in sorted(heap, reverse=True)]


def intersect(a: list[int], b: list[int]) -> list[int]:
    """Linear merge of two sorted postings lists, O(|a|+|b|) [S22 fig. 1.6]."""
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def union(a: list[int], b: list[int]) -> list[int]:
    i = j = 0
    out = []
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and a[i] < b[j]):
            out.append(a[i]); i += 1
        elif i == len(a) or b[j] < a[i]:
            out.append(b[j]); j += 1
        else:
            out.append(a[i]); i += 1; j += 1
    return out


def difference(a: list[int], b: list[int]) -> list[int]:
    """a AND NOT b."""
    bs = set(b)
    return [x for x in a if x not in bs]


def vbyte_encode(docs: list[int]) -> bytes:
    """Gaps between sorted doc numbers, 7 payload bits per byte, high bit marks the last byte."""
    out, prev = bytearray(), 0
    for d in docs:
        gap, prev = d - prev, d
        chunk = [gap & 0x7F]
        gap >>= 7
        while gap:
            chunk.append(gap & 0x7F)
            gap >>= 7
        chunk.reverse()
        chunk[-1] |= 0x80
        out.extend(chunk)
    return bytes(out)


def vbyte_decode(data: bytes) -> list[int]:
    out, n, prev = [], 0, 0
    for byte in data:
        n = (n << 7) | (byte & 0x7F)
        if byte & 0x80:
            prev += n
            out.append(prev)
            n = 0
    return out


if __name__ == "__main__":
    from corpus import make_collection

    c = make_collection()
    idx = InvertedIndex(c.docs)
    print(f"N={idx.N}, vocabulary {len(idx.postings)}, avgdl {idx.avgdl:.1f}")
    t0, t1 = c.terms[0][0], c.terms[0][1]
    print(f"df({t0})={idx.df(t0)}, df({t1})={idx.df(t1)}")
    print(f"'{t0} AND {t1}': {len(idx.boolean(f'{t0} AND {t1}'))} docs; "
          f"'{t0} AND NOT {t1}': {len(idx.boolean(f'{t0} AND NOT {t1}'))} docs")
    q = c.queries["q0001"]
    print(f"query '{q}': top-5 TF-IDF (DAAT):", [(d, round(s, 2)) for d, s in idx.topk_daat(q, 5)])
    print("relevant (grade 3):", sorted(c.binary_qrels()["q0001"]))
    p = idx.postings[t0]
    raw = 4 * len(p)
    enc = vbyte_encode([n for n, _, _ in p])
    print(f"postings of '{t0}': {len(p)} docs, {raw} bytes as int32 vs {len(enc)} bytes vbyte-gap")
