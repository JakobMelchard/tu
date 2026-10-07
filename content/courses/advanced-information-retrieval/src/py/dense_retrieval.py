"""Dense retrieval: a bi-encoder trained with in-batch negatives, exact and approximate NN search.

Note 11. BERT_DOT / DPR [S15 sl. 9-16, S37]; in-batch negatives [S37 §3.2];
FAISS-style IVF [S43]; random-hyperplane LSH for cosine similarity.

Bi-encoder: q = f(query), p = f(passage), s(q, p) = q^T p. Passages are encoded
once, offline; a query costs one encoder pass plus a nearest-neighbour search.
In-batch negatives: for B (q_i, p_i+) pairs, S = Q P^T / tau and
L = -(1/B) sum_i log softmax(S_i)_i, i.e. every other positive in the batch is
a negative for q_i: B^2 scores for the price of 2B encoder passes.

The encoder here is deliberately small (embedding bag + linear map); the
structure (siamese towers, pooling, dot product, contrastive loss, index) is
what DPR and TAS-B share, the capacity is not.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

PAD, OOV = 0, 1


class BiEncoder(nn.Module):
    def __init__(self, vocab_size: int, dim: int = 32, out: int = 32, normalise: bool = True):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, dim, padding_idx=PAD)
        self.proj = nn.Linear(dim, out)
        self.normalise = normalise

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        m = (ids != PAD).float()[..., None]
        pooled = (self.emb(ids) * m).sum(1) / m.sum(1).clamp(min=1)       # masked mean pooling
        v = self.proj(pooled)
        return F.normalize(v, dim=-1) if self.normalise else v


def in_batch_loss(q: torch.Tensor, p: torch.Tensor, tau: float = 0.05) -> torch.Tensor:
    """q (B, d), p (B + extra, d): row i's positive is p[i]; all other rows are negatives."""
    S = q @ p.T / tau
    return F.cross_entropy(S, torch.arange(len(q)))


def margin_mse(s_pos: torch.Tensor, s_neg: torch.Tensor, t_pos: torch.Tensor, t_neg: torch.Tensor) -> torch.Tensor:
    """Margin-MSE distillation [S40]: match the student's margin to the teacher's,
    MSE((s+ - s-), (t+ - t-)). Invariant to a per-pair shift of either model's scores, so a
    cross-encoder teacher can train a dot-product student whose score scale differs [S15 sl. 25]."""
    return F.mse_loss(s_pos - s_neg, t_pos - t_neg)


# ---------------- nearest-neighbour search ----------------
def brute_force(Q: np.ndarray, X: np.ndarray, k: int) -> np.ndarray:
    """Exact maximum inner product search, (nq, k) indices sorted by score."""
    S = Q @ X.T
    idx = np.argpartition(-S, k - 1, axis=1)[:, :k]
    order = np.argsort(-np.take_along_axis(S, idx, 1), axis=1, kind="stable")
    return np.take_along_axis(idx, order, 1)


def kmeans(X: np.ndarray, n: int, iters: int = 20, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng(0)
    C = X[rng.choice(len(X), n, replace=False)].copy()
    for _ in range(iters):
        a = np.argmax(X @ C.T - 0.5 * (C**2).sum(1), 1)                # nearest centroid in L2
        for j in range(n):
            if np.any(a == j):
                C[j] = X[a == j].mean(0)
    return C


class IVFIndex:
    """Inverted file: k-means coarse quantiser, one list per centroid; search the nprobe closest lists."""

    def __init__(self, X: np.ndarray, nlist: int = 32, rng=None):
        self.X = X
        self.C = kmeans(X, nlist, rng=rng)
        assign = np.argmax(X @ self.C.T - 0.5 * (self.C**2).sum(1), 1)
        self.lists = [np.flatnonzero(assign == j) for j in range(nlist)]

    def search(self, Q: np.ndarray, k: int, nprobe: int = 4) -> tuple[np.ndarray, float]:
        """Returns top-k indices and the mean fraction of the collection scored (the work done)."""
        out, work = [], 0
        probe = np.argsort(-(Q @ self.C.T - 0.5 * (self.C**2).sum(1)), 1)[:, :nprobe]
        for q, lists in zip(Q, probe):
            cand = np.concatenate([self.lists[j] for j in lists])
            work += len(cand)
            s = self.X[cand] @ q
            top = cand[np.argsort(-s, kind="stable")[:k]]
            out.append(np.pad(top, (0, k - len(top)), constant_values=-1))
        return np.array(out), work / (len(Q) * len(self.X))


class LSHIndex:
    """Random-hyperplane LSH: P[h(x) = h(y)] per bit = 1 - angle(x, y)/pi; n_tables tables of n_bits bits."""

    def __init__(self, X: np.ndarray, n_bits: int = 8, n_tables: int = 8, rng=None):
        rng = rng or np.random.default_rng(0)
        self.X = X
        self.H = rng.normal(size=(n_tables, n_bits, X.shape[1]))
        self.w = 1 << np.arange(n_bits)
        self.tables = []
        for H in self.H:
            codes = ((X @ H.T) > 0) @ self.w
            table: dict[int, list[int]] = {}
            for i, c in enumerate(codes):
                table.setdefault(int(c), []).append(i)
            self.tables.append(table)

    def search(self, Q: np.ndarray, k: int) -> tuple[np.ndarray, float]:
        out, work = [], 0
        for q in Q:
            cand = set()
            for H, table in zip(self.H, self.tables):
                cand.update(table.get(int(((H @ q) > 0) @ self.w), ()))
            cand = np.fromiter(cand, int) if cand else np.zeros(0, int)
            work += len(cand)
            top = cand[np.argsort(-(self.X[cand] @ q), kind="stable")[:k]]
            out.append(np.pad(top, (0, k - len(top)), constant_values=-1))
        return np.array(out), work / (len(Q) * len(self.X))


def ann_recall(approx: np.ndarray, exact: np.ndarray) -> float:
    """Fraction of the exact top-k found by the approximate search (recall@k of the index, not of relevance)."""
    return float(np.mean([len(set(a) & set(e)) / len(e) for a, e in zip(approx, exact)]))


# ---------------- training on the planted collection ----------------
def encode_texts(model: BiEncoder, stoi: dict[str, int], analyze, texts: list[str]) -> np.ndarray:
    ids = [[stoi.get(t, OOV) for t in analyze(x)] or [OOV] for x in texts]
    L = max(map(len, ids))
    with torch.no_grad():
        return model(torch.tensor([i + [PAD] * (L - len(i)) for i in ids])).numpy()


def dense_experiment(steps: int = 400, batch: int = 64, n_test: int = 60, k: int = 20, seed: int = 0):
    """Returns recall@k on held-out queries for: BM25, untrained bi-encoder, trained bi-encoder."""
    from bm25 import BM25
    from corpus import make_collection
    from inverted_index import InvertedIndex
    from metrics import recall_at_k

    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    c = make_collection(seed=seed, queries_per_topic=40)
    ix = InvertedIndex(c.docs)
    rel = c.binary_qrels()
    train_q, test_q = c.split_queries(n_test, seed)
    stoi = {w: i + 2 for i, w in enumerate(sorted(ix.postings))}
    model = BiEncoder(len(stoi) + 2)
    doc_ids = list(c.docs)

    def recall(m):
        D = encode_texts(m, stoi, ix.analyze, [c.docs[d] for d in doc_ids])
        Qv = encode_texts(m, stoi, ix.analyze, [c.queries[q] for q in test_q])
        top = brute_force(Qv, D, k)
        return float(np.mean([recall_at_k([doc_ids[i] for i in t], rel[q], k) for q, t in zip(test_q, top)]))

    r_untrained = recall(model)
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    pairs = [(q, d) for q in train_q for d in sorted(rel[q])]
    hist = []
    for _ in range(steps):
        b = [pairs[i] for i in rng.choice(len(pairs), batch, replace=False)]
        qv = model(_pad([[stoi.get(t, OOV) for t in ix.analyze(c.queries[q])] for q, _ in b]))
        pv = model(_pad([[stoi.get(t, OOV) for t in ix.analyze(c.docs[d])] for _, d in b]))
        loss = in_batch_loss(qv, pv)
        opt.zero_grad()
        loss.backward()
        opt.step()
        hist.append(loss.item())
    bm = BM25(ix)
    r_bm25 = float(np.mean([recall_at_k([d for d, _ in bm.rank(c.queries[q], k)], rel[q], k) for q in test_q]))
    return r_bm25, r_untrained, recall(model), hist


def _pad(ids: list[list[int]]) -> torch.Tensor:
    ids = [i or [OOV] for i in ids]
    L = max(map(len, ids))
    return torch.tensor([i + [PAD] * (L - len(i)) for i in ids])


if __name__ == "__main__":
    import time

    t0 = time.time()
    r_bm, r_0, r_1, hist = dense_experiment()
    print(f"bi-encoder trained in {time.time() - t0:.1f} s, in-batch loss {np.mean(hist[:20]):.2f} -> {np.mean(hist[-20:]):.2f}")
    print(f"recall@20 on 60 held-out queries: BM25 {r_bm:.3f}, untrained bi-encoder {r_0:.3f}, trained {r_1:.3f}")
    rng = np.random.default_rng(0)
    centres = rng.normal(size=(50, 32))
    X = centres[rng.integers(50, size=20000)] + 0.35 * rng.normal(size=(20000, 32))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    Q = X[rng.choice(20000, 200, replace=False)] + 0.05 * rng.normal(size=(200, 32))
    exact = brute_force(Q, X, 10)
    ivf = IVFIndex(X, nlist=64, rng=rng)
    for nprobe in (1, 4, 16):
        a, w = ivf.search(Q, 10, nprobe)
        print(f"IVF nlist 64 nprobe {nprobe:2d}: recall@10 {ann_recall(a, exact):.3f}, scored {100 * w:.1f} % of vectors")
    for tables in (4, 16):
        a, w = LSHIndex(X, n_bits=10, n_tables=tables, rng=rng).search(Q, 10)
        print(f"LSH 10 bits x {tables:2d} tables: recall@10 {ann_recall(a, exact):.3f}, scored {100 * w:.1f} % of vectors")
