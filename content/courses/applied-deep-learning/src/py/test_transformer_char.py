import torch

from common import loss_decreased
from transformer_char import VOCAB, CharTransformer, causal_mask, encode, make_corpus, run


def test_mask_and_shapes():
    m = causal_mask(3)
    assert m[0, 1] == float("-inf") and m[1, 0] == 0 and m[2, 2] == 0
    ids = encode(make_corpus(5, seed=0), 10)
    logits = CharTransformer(max_len=10)(ids)
    assert logits.shape == (5, 10, len(VOCAB))
    # causality: changing the last token must not change earlier logits
    ids2 = ids.clone()
    ids2[:, -1] = (ids2[:, -1] + 1) % len(VOCAB)
    model = CharTransformer(max_len=10)
    assert torch.allclose(model(ids)[:, :-1], model(ids2)[:, :-1], atol=1e-5)


def test_lm_trains():
    out = run(steps=120, n_lines=1000)
    assert loss_decreased(out["losses"])
    assert out["bits_per_char"] < 3.0 and out["sample"].startswith("23+45=")
