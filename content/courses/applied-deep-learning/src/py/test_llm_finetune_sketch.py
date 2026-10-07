import torch

from common import loss_decreased
from llm_finetune_sketch import LoRALinear, TinyLM, add_lora, merge_lora, run


def test_lora_merge_is_exact():
    torch.manual_seed(0)
    base = torch.nn.Linear(6, 5)
    lora = LoRALinear(base, r=2, alpha=4)
    x = torch.randn(3, 6)
    assert torch.allclose(lora(x), base(x))  # B = 0 at init: identical to the base
    torch.nn.init.normal_(lora.B)
    assert torch.allclose(lora(x), lora.merged()(x), atol=1e-5)


def test_only_adapters_train():
    model = TinyLM(max_len=10)
    n = add_lora(model, r=4)
    assert n == 8  # 2 layers x (qkv, out, ffn.0, ffn.2)
    trainable = {name for name, p in model.named_parameters() if p.requires_grad}
    assert trainable and all(name.endswith((".A", ".B")) for name in trainable)
    merge_lora(model)
    assert not any(isinstance(m, LoRALinear) for m in model.modules())


def test_finetune_decreases_loss():
    out = run(pretrain_steps=80, finetune_steps=80, n_lines=1000)
    assert loss_decreased(out["losses"]) and loss_decreased(out["pretrain_losses"])
    assert 0 < out["trainable_fraction"] < 0.2
    assert abs(out["finetune_bpc"] - out["bpc_merged"]) < 1e-3
