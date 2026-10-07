"""Tiny character-level decoder-only transformer on a generated corpus.

Corpus: lines like "12+7=19\n". The model learns next-character prediction
with causal masking; scaled dot-product attention and multi-head attention are
written out (no nn.MultiheadAttention) to expose the arithmetic:
    Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k) + mask) V.
`generate` completes a prefix greedily, e.g. "23+45=" -> "68".
"""

from __future__ import annotations

import math

import torch
from torch import nn
from torch.nn import functional as F

from common import Timer, count_params, get_device, loss_decreased, seed_all, train_loop

VOCAB = "0123456789+-=\n"  # 14 symbols; "\n" ends a line and doubles as padding
STOI = {ch: i for i, ch in enumerate(VOCAB)}
PAD = STOI["\n"]


def make_corpus(n_lines: int = 2000, seed: int = 0, op: str = "add", max_operand: int = 99) -> list[str]:
    gen = torch.Generator().manual_seed(seed)
    a = torch.randint(0, max_operand + 1, (n_lines,), generator=gen)
    b = torch.randint(0, max_operand + 1, (n_lines,), generator=gen)
    if op == "add":
        return [f"{x}+{y}={x + y}\n" for x, y in zip(a.tolist(), b.tolist())]
    return [f"{max(x, y)}-{min(x, y)}={abs(x - y)}\n" for x, y in zip(a.tolist(), b.tolist())]  # non-negative


def encode(lines: list[str], max_len: int) -> torch.Tensor:
    """[n, max_len] int tensor, right-padded with PAD."""
    out = torch.full((len(lines), max_len), PAD, dtype=torch.long)
    for i, line in enumerate(lines):
        ids = [STOI[c] for c in line[:max_len]]
        out[i, : len(ids)] = torch.tensor(ids)
    return out


def causal_mask(T: int, device: torch.device | None = None) -> torch.Tensor:
    """[T, T] additive mask: 0 on and below the diagonal, -inf above (no peeking at the future)."""
    return torch.triu(torch.full((T, T), float("-inf"), device=device), diagonal=1)


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.0):
        super().__init__()
        assert d_model % n_heads == 0
        self.h, self.d_k = n_heads, d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model)  # one matmul for Q, K, V of all heads
        self.out = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        B, T, d = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.d_k).unbind(dim=2)  # each [B, T, h, d_k]
        q, k, v = (t.transpose(1, 2) for t in (q, k, v))  # [B, h, T, d_k]
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d_k) + mask  # [B, h, T, T]
        attn = self.drop(scores.softmax(dim=-1))
        y = (attn @ v).transpose(1, 2).reshape(B, T, d)  # concat heads
        return self.out(y)


class Block(nn.Module):
    """Pre-LN transformer block: x + MHA(LN(x)); x + FFN(LN(x))."""

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.0):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d_model), nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = nn.Sequential(nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Linear(4 * d_model, d_model),
                                 nn.Dropout(dropout))

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x), mask)
        return x + self.ffn(self.ln2(x))


class CharTransformer(nn.Module):
    def __init__(self, vocab: int = len(VOCAB), d_model: int = 64, n_heads: int = 4, n_layers: int = 2,
                 max_len: int = 12, dropout: float = 0.0):
        super().__init__()
        self.tok = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(max_len, d_model)  # learned absolute positions
        self.blocks = nn.ModuleList([Block(d_model, n_heads, dropout) for _ in range(n_layers)])
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab, bias=False)
        self.max_len = max_len

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        """idx [B, T] -> logits [B, T, vocab]."""
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        mask = causal_mask(T, idx.device)
        for block in self.blocks:
            x = block(x, mask)
        return self.head(self.ln(x))


def lm_loss(model: nn.Module, batch: torch.Tensor) -> torch.Tensor:
    """Next-token cross-entropy: input = tokens[:-1], target = tokens[1:]."""
    logits = model(batch[:, :-1])
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), batch[:, 1:].reshape(-1))


@torch.no_grad()
def generate(model: nn.Module, prefix: str, max_new: int = 4) -> str:
    model.eval()
    device = next(model.parameters()).device
    idx = torch.tensor([[STOI[c] for c in prefix]], device=device)
    for _ in range(max_new):
        nxt = model(idx[:, -model.max_len :])[0, -1].argmax()  # greedy decoding
        if nxt.item() == PAD:
            break
        idx = torch.cat([idx, nxt.view(1, 1)], dim=1)
    model.train()
    return "".join(VOCAB[i] for i in idx[0].tolist())


@torch.no_grad()
def bits_per_char(model: nn.Module, data: torch.Tensor) -> float:
    model.eval()
    bpc = lm_loss(model, data).item() / math.log(2)
    model.train()
    return bpc


def run(steps: int = 500, batch: int = 64, n_lines: int = 3000, max_len: int = 10, device: torch.device | None = None,
        seed: int = 0, log_every: int = 0, **model_kw) -> dict:
    device = device or get_device()
    gen = seed_all(seed)
    data = encode(make_corpus(n_lines, seed), max_len).to(device)
    test = encode(make_corpus(500, seed + 1), max_len).to(device)
    model = CharTransformer(max_len=max_len, **model_kw).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=0.01)
    warmup = max(1, steps // 10)
    sched = torch.optim.lr_scheduler.LambdaLR(  # linear warmup, then cosine decay to zero
        opt, lambda s: min(1.0, (s + 1) / warmup) * 0.5 * (1 + math.cos(math.pi * min(1.0, s / steps))))

    def step_fn() -> torch.Tensor:
        return lm_loss(model, data[torch.randint(0, n_lines, (batch,), generator=gen).to(device)])

    with Timer() as t:
        losses = train_loop(step_fn, opt, steps, log_every=log_every, scheduler=sched, clip_grad=1.0)
    return {"losses": losses, "bits_per_char": bits_per_char(model, test), "sample": generate(model, "23+45="),
            "model": model, "seconds": t.seconds}


if __name__ == "__main__":
    print(f"params {count_params(CharTransformer())}, causal mask 4x4:\n{causal_mask(4)}")
    out = run(steps=1500, log_every=300)
    print(f"test bits/char {out['bits_per_char']:.3f}, {out['seconds']:.1f}s, loss decreased {loss_decreased(out['losses'])}")
    for p in ("23+45=", "7+8=", "99+1="):
        print(f"  {p!r} -> {generate(out['model'], p)!r}")
