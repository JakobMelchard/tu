"""Pretrain a tiny causal LM, then fine-tune it with LoRA adapters (Hu et al. 2021).

Stage 1: pretrain `TinyLM` (= CharTransformer) on corpus A, addition lines "12+7=19".
Stage 2: freeze every weight, wrap each nn.Linear inside the attention and MLP
         blocks in `LoRALinear`:  y = W x + (alpha / r) * B A x,  A ~ N(0, 1/r),
         B = 0 at init (so the model starts unchanged); train only A, B on
         corpus B, subtraction lines "19-7=12".
`merge_lora` folds W + (alpha/r) B A back into a plain nn.Linear for inference.
"""

from __future__ import annotations

import math

import torch
from torch import nn

from common import Timer, count_params, get_device, loss_decreased, seed_all, train_loop
from transformer_char import CharTransformer, bits_per_char, encode, generate, lm_loss, make_corpus

TinyLM = CharTransformer


class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r: int = 4, alpha: float = 8.0):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad_(False)
        self.A = nn.Parameter(torch.randn(r, base.in_features) / math.sqrt(r))  # [r, k]
        self.B = nn.Parameter(torch.zeros(base.out_features, r))  # [d, r], zero => no change at init
        self.scale = alpha / r

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base(x) + self.scale * (x @ self.A.T @ self.B.T)

    def merged(self) -> nn.Linear:
        lin = nn.Linear(self.base.in_features, self.base.out_features, bias=self.base.bias is not None)
        with torch.no_grad():
            lin.weight.copy_(self.base.weight + self.scale * self.B @ self.A)
            if self.base.bias is not None:
                lin.bias.copy_(self.base.bias)
        return lin


def add_lora(model: nn.Module, r: int = 4, alpha: float = 8.0, targets: tuple[str, ...] = ("qkv", "out", "ffn")) -> int:
    """Freeze the model and replace every nn.Linear whose qualified name contains a target. Returns #replaced."""
    for p in model.parameters():
        p.requires_grad_(False)
    n = 0
    for name, module in list(model.named_modules()):
        for child_name, child in list(module.named_children()):
            full = f"{name}.{child_name}" if name else child_name
            if isinstance(child, nn.Linear) and any(t in full for t in targets):
                setattr(module, child_name, LoRALinear(child, r, alpha))
                n += 1
    return n


def merge_lora(model: nn.Module) -> nn.Module:
    """Replace every LoRALinear by the merged plain nn.Linear (in place)."""
    for name, module in list(model.named_modules()):
        for child_name, child in list(module.named_children()):
            if isinstance(child, LoRALinear):
                setattr(module, child_name, child.merged().to(child.B.device))
    return model


def _fit(model: nn.Module, data: torch.Tensor, steps: int, lr: float, batch: int, gen: torch.Generator,
         log_every: int) -> list[float]:
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)

    def step_fn() -> torch.Tensor:
        return lm_loss(model, data[torch.randint(0, len(data), (batch,), generator=gen).to(data.device)])

    return train_loop(step_fn, opt, steps, log_every=log_every, scheduler=sched, clip_grad=1.0)


def run(pretrain_steps: int = 300, finetune_steps: int = 300, r: int = 4, alpha: float = 8.0, batch: int = 64,
        n_lines: int = 3000, max_len: int = 10, device: torch.device | None = None, seed: int = 0,
        log_every: int = 0) -> dict:
    device = device or get_device()
    gen = seed_all(seed)
    add = encode(make_corpus(n_lines, seed, "add"), max_len).to(device)
    sub = encode(make_corpus(n_lines, seed + 1, "sub"), max_len).to(device)
    sub_test = encode(make_corpus(500, seed + 2, "sub"), max_len).to(device)
    model = TinyLM(max_len=max_len).to(device)
    total = count_params(model)
    with Timer() as t:
        pre = _fit(model, add, pretrain_steps, 3e-3, batch, gen, log_every)
        bpc_before = bits_per_char(model, sub_test)
        n_wrapped = add_lora(model, r, alpha)
        model.to(device)
        trainable = count_params(model, trainable_only=True)
        fine = _fit(model, sub, finetune_steps, 1e-2, batch, gen, log_every)  # adapters tolerate a larger LR
        bpc_after = bits_per_char(model, sub_test)
        merge_lora(model)
        bpc_merged = bits_per_char(model, sub_test)
    return {"losses": fine, "pretrain_losses": pre, "trainable_fraction": trainable / total, "n_wrapped": n_wrapped,
            "finetune_bpc": bpc_after, "bpc_before_finetune": bpc_before, "bpc_merged": bpc_merged,
            "model": model, "seconds": t.seconds}


if __name__ == "__main__":
    out = run(pretrain_steps=1200, finetune_steps=600, log_every=300)
    print(f"LoRA wrapped {out['n_wrapped']} linears; trainable fraction {out['trainable_fraction']:.3%}")
    print(f"subtraction bits/char: before fine-tune {out['bpc_before_finetune']:.3f}, after {out['finetune_bpc']:.3f}, "
          f"after merge {out['bpc_merged']:.3f}; {out['seconds']:.1f}s, loss decreased {loss_decreased(out['losses'])}")
    for p in ("50-20=", "99-1=", "12+7="):
        print(f"  {p!r} -> {generate(out['model'], p)!r}")
    print("  (the last one probes forgetting: addition was only seen in pretraining)")
