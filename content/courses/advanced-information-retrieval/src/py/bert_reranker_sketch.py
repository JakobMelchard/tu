"""A tiny BERT-shaped transformer encoder used as a cross-encoder re-ranker (BERT_CAT / monoBERT).

Note 10. No pretrained weights: this is the architecture and the training
step, not a reproduction of BERT's effectiveness (which comes from
pre-training on billions of tokens [S32]). Lecture [S11 sl. 7-20, S13 sl. 8-14];
monoBERT [S35]; general transformer derivations in the ADL notes
(`cse/ws2026/applied-deep-learning/notes/06-transformers.md`).

Input  [CLS] q_1..q_n [SEP] d_1..d_m [SEP], segment ids 0 / 1, learned positions.
Encoder: L post-LN blocks x <- LN(x + MHA(x)), x <- LN(x + FFN(x)) (BERT order).
Score  s(q, d) = w^T h_[CLS] + b.  Cost: every (q, d) pair is a full forward
pass over n + m + 3 tokens, O(L (n+m)^2 d) attention per candidate, nothing
can be precomputed; this is what ColBERT, PreTTR, TK and bi-encoders trade away.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

PAD, OOV, CLS, SEP = 0, 1, 2, 3


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d: int, h: int):
        super().__init__()
        assert d % h == 0
        self.h, self.dk = h, d // h
        self.qkv = nn.Linear(d, 3 * d)
        self.o = nn.Linear(d, d)
        self.last_attn: torch.Tensor | None = None

    def forward(self, x: torch.Tensor, key_pad: torch.Tensor) -> torch.Tensor:
        """x (B, T, d); key_pad (B, T) True where the key is padding."""
        B, T, d = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.dk).permute(2, 0, 3, 1, 4)   # 3 x (B, h, T, dk)
        scores = q @ k.transpose(-1, -2) / math.sqrt(self.dk)                          # (B, h, T, T)
        scores = scores.masked_fill(key_pad[:, None, None, :], float("-inf"))
        a = scores.softmax(-1)
        self.last_attn = a.detach()
        return self.o((a @ v).transpose(1, 2).reshape(B, T, d))


class Block(nn.Module):
    def __init__(self, d: int, h: int, d_ff: int, dropout: float = 0.0):
        super().__init__()
        self.att, self.ln1, self.ln2 = MultiHeadSelfAttention(d, h), nn.LayerNorm(d), nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d, d_ff), nn.GELU(), nn.Linear(d_ff, d))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, key_pad):
        x = self.ln1(x + self.drop(self.att(x, key_pad)))
        return self.ln2(x + self.drop(self.ff(x)))


class TinyCrossEncoder(nn.Module):
    def __init__(self, vocab_size: int, d: int = 32, h: int = 4, layers: int = 2, d_ff: int = 64,
                 max_len: int = 128, use_pos: bool = True, dropout: float = 0.0):
        super().__init__()
        self.tok = nn.Embedding(vocab_size, d, padding_idx=PAD)
        self.pos = nn.Embedding(max_len, d)
        self.seg = nn.Embedding(2, d)
        self.ln = nn.LayerNorm(d)
        self.blocks = nn.ModuleList(Block(d, h, d_ff, dropout) for _ in range(layers))
        self.head = nn.Linear(d, 1)
        self.use_pos, self.max_len = use_pos, max_len

    def forward(self, ids: torch.Tensor, seg: torch.Tensor) -> torch.Tensor:
        pad = ids == PAD
        x = self.tok(ids) + self.seg(seg)
        if self.use_pos:
            x = x + self.pos(torch.arange(ids.shape[1], device=ids.device))[None]
        x = self.ln(x)
        for b in self.blocks:
            x = b(x, pad)
        return self.head(x[:, 0]).squeeze(-1)                                         # [CLS] pooling


def param_count_formula(V: int, d: int, h: int, layers: int, d_ff: int, max_len: int) -> int:
    """Embeddings (V + max_len + 2) d, embedding LN 2d; per block: attention 4d^2 + 4d,
    FFN 2 d d_ff + d_ff + d, two LNs 4d; head d + 1. Independent of h."""
    per_block = (4 * d * d + 4 * d) + (2 * d * d_ff + d_ff + d) + 4 * d
    return (V + max_len + 2) * d + 2 * d + layers * per_block + d + 1


def build_pairs(q_ids: list[list[int]], d_ids: list[list[int]], max_len: int = 128):
    """Concatenate [CLS] q [SEP] d [SEP], truncate the *document* to fit, pad to the batch maximum."""
    rows, segs = [], []
    for q, d in zip(q_ids, d_ids):
        d = d[: max_len - len(q) - 3]
        rows.append([CLS] + q + [SEP] + d + [SEP])
        segs.append([0] * (len(q) + 2) + [1] * (len(d) + 1))
    T = max(map(len, rows))
    ids = torch.tensor([r + [PAD] * (T - len(r)) for r in rows])
    seg = torch.tensor([s + [0] * (T - len(s)) for s in segs])
    return ids, seg


def train_step(model: nn.Module, opt: torch.optim.Optimizer, pos, neg, margin: float = 1.0) -> float:
    """One pairwise step: pos / neg are (ids, seg) of the same queries with a relevant / non-relevant doc."""
    model.train()
    loss = F.relu(margin - model(*pos) + model(*neg)).mean()
    opt.zero_grad()
    loss.backward()
    opt.step()
    return loss.item()


def best_span(start: torch.Tensor, end: torch.Tensor, max_len: int = 15) -> tuple[int, int, float]:
    """Extractive QA decoding [S11 sl. 29-31, S47]: argmax over i <= j < i + max_len of start_i + end_j
    (log-space), computed with a running maximum over the start logits, O(n max_len)."""
    best = (0, 0, float("-inf"))
    for j in range(len(end)):
        lo = max(0, j - max_len + 1)
        i = lo + int(torch.argmax(start[lo:j + 1]))
        s = float(start[i] + end[j])
        if s > best[2]:
            best = (i, j, s)
    return best


def rerank_experiment(steps: int = 400, depth: int = 30, n_test: int = 60, seed: int = 0):
    """Train from scratch on the planted collection, re-rank BM25 top-depth of held-out queries."""
    import numpy as np

    from bm25 import BM25
    from corpus import make_collection
    from inverted_index import InvertedIndex
    from knrm import candidates, evaluate, make_triples

    torch.manual_seed(seed)
    c = make_collection(seed=seed, queries_per_topic=40)
    ix = InvertedIndex(c.docs)
    train_q, test_q = c.split_queries(n_test, seed)
    cand = candidates(BM25(ix), c.queries, depth)
    stoi = {w: i + 4 for i, w in enumerate(sorted(ix.postings))}
    enc = lambda text: [stoi.get(t, OOV) for t in ix.analyze(text)]
    model = TinyCrossEncoder(len(stoi) + 4)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    rng = np.random.default_rng(seed)
    triples = make_triples(c, cand, train_q, 8000, rng)
    hist = []
    for _ in range(steps):
        b = [triples[i] for i in rng.integers(len(triples), size=32)]
        qs = [enc(c.queries[x[0]]) for x in b]
        hist.append(train_step(model, opt, build_pairs(qs, [enc(c.docs[x[1]]) for x in b]),
                               build_pairs(qs, [enc(c.docs[x[2]]) for x in b])))
    model.eval()
    run = {}
    with torch.no_grad():
        for q in test_q:
            docs = cand[q]
            s = model(*build_pairs([enc(c.queries[q])] * len(docs), [enc(c.docs[d]) for d in docs]))
            run[q] = [docs[i] for i in torch.argsort(-s, stable=True).tolist()]
    return evaluate({q: cand[q] for q in test_q}, c), evaluate(run, c), hist


if __name__ == "__main__":
    import time

    m = TinyCrossEncoder(1000)
    n = sum(p.numel() for p in m.parameters())
    print(f"TinyCrossEncoder(V=1000, d=32, h=4, L=2): {n} parameters, formula {param_count_formula(1000, 32, 4, 2, 64, 128)}")
    print(f"BERT-base by the same formula (V=30522, d=768, L=12, d_ff=3072, 512 positions): "
          f"{param_count_formula(30522, 768, 12, 12, 3072, 512) / 1e6:.1f} M (+ pooler 0.6 M = 110 M)")
    t0 = time.time()
    (b_mrr, b_nd), (m_mrr, m_nd), hist = rerank_experiment()
    print(f"trained from scratch in {time.time() - t0:.1f} s, loss {sum(hist[:20]) / 20:.3f} -> {sum(hist[-20:]) / 20:.3f}")
    print(f"BM25 top-30 of 60 held-out queries: BM25 MRR@10 {b_mrr:.3f} nDCG@10 {b_nd:.3f} | "
          f"cross-encoder MRR@10 {m_mrr:.3f} nDCG@10 {m_nd:.3f}")
