"""KNRM and Conv-KNRM kernel-pooling re-rankers in torch, trained on the planted collection.

Note 09 (model), note 08 (pairwise training). Xiong et al. [S33], Dai et al. [S34],
lecture [S12 sl. 11-16, 29-40]; the exercise asked for exactly this model on
MS MARCO with BM25 top-k candidates [S17, S18].

Per query-document pair (query tokens i, document tokens j):
  M_ij = cos(q_i, d_j)                                    match matrix
  K_k(M_i) = sum_j exp(-(M_ij - mu_k)^2 / (2 sigma_k^2))   soft-TF of kernel k
  phi_k = sum_i log K_k(M_i)                              log, then sum over query
  s = w^T phi + b
11 kernels: mu = 1 (sigma 1e-3, exact match) and mu = 0.9, 0.7, ..., -0.9 (sigma 0.1).

The re-ranking workflow: BM25 retrieves top-`depth` candidates, KNRM re-scores
them; training uses triples (q, d+, d-) with d- sampled from BM25 candidates
and the margin loss max(0, 1 - s+ + s-) [S12 sl. 15].
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from bm25 import BM25
from corpus import Collection, make_collection
from inverted_index import InvertedIndex
from metrics import mean_metric, ndcg_at_k, reciprocal_rank

PAD, OOV = 0, 1


def kernels(n: int = 11) -> tuple[torch.Tensor, torch.Tensor]:
    mu = [1.0] + [0.9 - 0.2 * i for i in range(n - 1)]
    sigma = [1e-3] + [0.1] * (n - 1)
    return torch.tensor(mu), torch.tensor(sigma)


def kernel_pooling(M: torch.Tensor, d_mask: torch.Tensor, q_mask: torch.Tensor,
                   mu: torch.Tensor, sigma: torch.Tensor, log1p: bool = False) -> torch.Tensor:
    """M (B, Lq, Ld) -> phi (B, K). Masks are 1 for real tokens, 0 for padding.
    Padding must be masked *after* the kernel: exp(-(0 - mu)^2/...) is not 0 [S18 hints]."""
    Kv = torch.exp(-((M.unsqueeze(-1) - mu) ** 2) / (2 * sigma**2)) * d_mask[:, None, :, None]
    soft_tf = Kv.sum(2)                                               # (B, Lq, K)
    lg = torch.log1p(soft_tf) if log1p else torch.log(soft_tf.clamp(min=1e-10))
    return (lg * 0.01 * q_mask[:, :, None]).sum(1)                    # scale as in [S12 sl. 35-36] code


class KNRM(nn.Module):
    def __init__(self, vocab_size: int, dim: int = 32, n_kernels: int = 11, log1p: bool = False):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, dim, padding_idx=PAD)
        mu, sigma = kernels(n_kernels)
        self.register_buffer("mu", mu)
        self.register_buffer("sigma", sigma)
        self.out = nn.Linear(n_kernels, 1)
        self.log1p = log1p

    def match_matrix(self, q: torch.Tensor, d: torch.Tensor) -> torch.Tensor:
        qe = F.normalize(self.emb(q), dim=-1, eps=1e-8)
        de = F.normalize(self.emb(d), dim=-1, eps=1e-8)
        return qe @ de.transpose(1, 2)

    def forward(self, q: torch.Tensor, d: torch.Tensor) -> torch.Tensor:
        phi = kernel_pooling(self.match_matrix(q, d), (d != PAD).float(), (q != PAD).float(),
                             self.mu, self.sigma, self.log1p)
        return self.out(phi).squeeze(-1)


class ConvKNRM(KNRM):
    """n-gram embeddings by 1D convolutions (h = 1..max_n), cross-matched: (max_n)^2 match matrices,
    each kernel-pooled, concatenated -> linear [S34]."""

    def __init__(self, vocab_size: int, dim: int = 32, n_kernels: int = 11, max_n: int = 2):
        super().__init__(vocab_size, dim, n_kernels)
        self.convs = nn.ModuleList(nn.Conv1d(dim, dim, h, padding=0) for h in range(1, max_n + 1))
        self.out = nn.Linear(n_kernels * max_n**2, 1)

    def ngrams(self, x: torch.Tensor) -> list[tuple[torch.Tensor, torch.Tensor]]:
        e = self.emb(x).transpose(1, 2)                                 # (B, dim, L)
        m = (x != PAD).float()
        out = []
        for h, conv in enumerate(self.convs, 1):
            g = F.relu(conv(e)).transpose(1, 2)                         # (B, L-h+1, dim)
            gm = m.unfold(1, h, 1).min(-1).values if h > 1 else m      # n-gram real iff all tokens real
            out.append((F.normalize(g, dim=-1, eps=1e-8), gm))
        return out

    def forward(self, q: torch.Tensor, d: torch.Tensor) -> torch.Tensor:
        feats = []
        for qe, qm in self.ngrams(q):
            for de, dm in self.ngrams(d):
                feats.append(kernel_pooling(qe @ de.transpose(1, 2), dm, qm, self.mu, self.sigma))
        return self.out(torch.cat(feats, -1)).squeeze(-1)


class Encoder:
    """Token ids with the same analyzer as the index; 0 pad, 1 OOV (unseen at training time)."""

    def __init__(self, index: InvertedIndex, extra: list[str] = ()):
        words = sorted(set(index.postings) | set(extra))
        self.index = index
        self.stoi = {w: i + 2 for i, w in enumerate(words)}

    def __len__(self):
        return len(self.stoi) + 2

    def batch(self, texts: list[str], max_len: int = 100) -> torch.Tensor:
        ids = [[self.stoi.get(t, OOV) for t in self.index.analyze(x)][:max_len] or [OOV] for x in texts]
        L = max(len(i) for i in ids)
        return torch.tensor([i + [PAD] * (L - len(i)) for i in ids])


def candidates(bm: BM25, queries: dict[str, str], depth: int) -> dict[str, list[str]]:
    return {q: [d for d, _ in bm.rank(t, depth)] for q, t in queries.items()}


def make_triples(c: Collection, cand: dict[str, list[str]], qids: list[str], n: int,
                 rng: np.random.Generator) -> list[tuple[str, str, str]]:
    """(query, relevant doc, BM25-candidate non-relevant doc); a random doc if the candidates hold none."""
    rel = c.binary_qrels()
    all_docs = list(c.docs)
    out = []
    while len(out) < n:
        q = qids[rng.integers(len(qids))]
        pos = sorted(rel[q])[rng.integers(len(rel[q]))]
        negs = [d for d in cand[q] if d not in rel[q]] or all_docs
        out.append((q, pos, negs[rng.integers(len(negs))]))
    return out


def train(model: nn.Module, enc: Encoder, c: Collection, triples, steps: int = 300, batch: int = 32,
          lr: float = 1e-2, seed: int = 0) -> list[float]:
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MarginRankingLoss(margin=1.0)
    rng = np.random.default_rng(seed)
    hist = []
    model.train()
    for _ in range(steps):
        b = [triples[i] for i in rng.integers(len(triples), size=batch)]
        q = enc.batch([c.queries[x[0]] for x in b])
        sp = model(q, enc.batch([c.docs[x[1]] for x in b]))
        sn = model(q, enc.batch([c.docs[x[2]] for x in b]))
        loss = loss_fn(sp, sn, torch.ones_like(sp))                    # max(0, 1 - (s+ - s-))
        opt.zero_grad()
        loss.backward()
        opt.step()
        hist.append(loss.item())
    return hist


@torch.no_grad()
def rerank(model: nn.Module, enc: Encoder, c: Collection, cand: dict[str, list[str]]) -> dict[str, list[str]]:
    model.eval()
    out = {}
    for q, docs in cand.items():
        s = model(enc.batch([c.queries[q]] * len(docs)), enc.batch([c.docs[d] for d in docs]))
        out[q] = [docs[i] for i in torch.argsort(-s, stable=True).tolist()]
    return out


def evaluate(run: dict[str, list[str]], c: Collection) -> tuple[float, float]:
    rel = c.binary_qrels()
    return (mean_metric(lambda q: reciprocal_rank(run[q], rel[q], 10), run),
            mean_metric(lambda q: ndcg_at_k(run[q], c.qrels[q], 10), run))


def experiment(model_cls=KNRM, depth: int = 30, n_test: int = 60, steps: int = 300, seed: int = 0,
               queries_per_topic: int = 40, **kw):
    """BM25 top-depth -> model re-ranking on held-out queries.
    Returns (bm25 (MRR@10, nDCG@10), model (MRR@10, nDCG@10), loss history).
    40 queries per topic (740 training queries) so that most aliases occur in several training
    queries: with 12 per topic an alias is seen about once and the gain does not generalise."""
    torch.manual_seed(seed)
    c = make_collection(seed=seed, queries_per_topic=queries_per_topic)
    ix = InvertedIndex(c.docs)
    bm = BM25(ix)
    train_q, test_q = c.split_queries(n_test, seed)
    cand = candidates(bm, c.queries, depth)
    enc = Encoder(ix, extra=[w for q in train_q for w in ix.analyze(c.queries[q])])
    model = model_cls(len(enc), **kw)
    triples = make_triples(c, cand, train_q, 8000, np.random.default_rng(seed))
    hist = train(model, enc, c, triples, steps=steps, seed=seed)
    test_cand = {q: cand[q] for q in test_q}
    return evaluate(test_cand, c), evaluate(rerank(model, enc, c, test_cand), c), hist


if __name__ == "__main__":
    import time

    for name, cls, kw in [("KNRM log", KNRM, {}), ("KNRM log1p", KNRM, {"log1p": True}),
                          ("Conv-KNRM", ConvKNRM, {"steps": 200})]:
        t0 = time.time()
        (b_mrr, b_nd), (m_mrr, m_nd), hist = experiment(cls, **kw)
        print(f"{name:10s} {time.time() - t0:4.1f} s, loss {np.mean(hist[:20]):.3f} -> {np.mean(hist[-20:]):.3f} | "
              f"60 test queries, BM25 top-30: BM25 MRR@10 {b_mrr:.3f} nDCG@10 {b_nd:.3f} -> "
              f"MRR@10 {m_mrr:.3f} nDCG@10 {m_nd:.3f}")
