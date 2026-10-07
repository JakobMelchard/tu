import torch

from bert_reranker_sketch import (CLS, PAD, SEP, MultiHeadSelfAttention, TinyCrossEncoder, best_span, build_pairs,
                                  param_count_formula, train_step)


def test_build_pairs_layout_segments_truncation():
    ids, seg = build_pairs([[10, 11], [12]], [[20, 21, 22], list(range(30, 60))], max_len=16)
    assert ids.shape == (2, 16)
    assert ids[0].tolist()[:8] == [CLS, 10, 11, SEP, 20, 21, 22, SEP] and ids[0, 8:].eq(PAD).all()
    assert seg[0].tolist()[:8] == [0, 0, 0, 0, 1, 1, 1, 1]
    assert ids[1].tolist()[-1] == SEP and (ids[1] != PAD).sum() == 16          # doc truncated to fit


def test_shapes_and_parameter_count():
    m = TinyCrossEncoder(500, d=32, h=4, layers=3, d_ff=48, max_len=64)
    ids, seg = build_pairs([[5, 6]] * 7, [[7, 8, 9]] * 7)
    assert m(ids, seg).shape == (7,)
    assert sum(p.numel() for p in m.parameters()) == param_count_formula(500, 32, 4, 3, 48, 64)
    # heads do not change the parameter count
    assert param_count_formula(500, 32, 1, 3, 48, 64) == param_count_formula(500, 32, 8, 3, 48, 64)


def test_attention_rows_are_distributions_and_ignore_padding():
    torch.manual_seed(0)
    att = MultiHeadSelfAttention(16, 4)
    x = torch.randn(2, 5, 16)
    pad = torch.tensor([[False] * 5, [False, False, False, True, True]])
    att(x, pad)
    a = att.last_attn
    assert torch.allclose(a.sum(-1), torch.ones(2, 4, 5))
    assert a[1, :, :, 3:].abs().max() == 0


def test_matches_torch_multihead_attention():
    torch.manual_seed(0)
    d, h = 16, 4
    ours, ref = MultiHeadSelfAttention(d, h), torch.nn.MultiheadAttention(d, h, batch_first=True)
    with torch.no_grad():
        ref.in_proj_weight.copy_(ours.qkv.weight)
        ref.in_proj_bias.copy_(ours.qkv.bias)
        ref.out_proj.weight.copy_(ours.o.weight)
        ref.out_proj.bias.copy_(ours.o.bias)
    x = torch.randn(3, 6, d)
    pad = torch.zeros(3, 6, dtype=torch.bool)
    pad[2, 4:] = True
    out_ref, _ = ref(x, x, x, key_padding_mask=pad)
    assert torch.allclose(ours(x, pad), out_ref, atol=1e-5)


def test_padding_invariance():
    torch.manual_seed(0)
    m = TinyCrossEncoder(100).eval()
    ids, seg = build_pairs([[5, 6]], [[7, 8, 9]])
    ids2 = torch.cat([ids, torch.zeros(1, 4, dtype=torch.long)], 1)
    seg2 = torch.cat([seg, torch.zeros(1, 4, dtype=torch.long)], 1)
    assert torch.allclose(m(ids, seg), m(ids2, seg2), atol=1e-5)


def test_without_positions_the_encoder_sees_a_bag_of_words():
    torch.manual_seed(0)
    m = TinyCrossEncoder(100, use_pos=False).eval()
    a = build_pairs([[5, 6]], [[7, 8, 9, 10]])
    b = build_pairs([[5, 6]], [[10, 9, 7, 8]])
    assert torch.allclose(m(*a), m(*b), atol=1e-5)
    mp = TinyCrossEncoder(100, use_pos=True).eval()
    assert not torch.allclose(mp(*a), mp(*b), atol=1e-5)


def test_training_steps_reduce_pairwise_loss_on_a_fixed_batch():
    torch.manual_seed(0)
    m = TinyCrossEncoder(60)
    opt = torch.optim.Adam(m.parameters(), lr=3e-3)
    qs = [[4, 5], [6, 7], [8, 9], [10, 11]]
    pos = build_pairs(qs, [[4, 5, 20, 21], [6, 7, 22], [8, 23, 9], [24, 10, 11]])      # contain the query terms
    neg = build_pairs(qs, [[30, 31, 32], [33, 34], [35, 36, 37, 38], [39, 40]])
    losses = [train_step(m, opt, pos, neg) for _ in range(30)]
    assert losses[-1] < 0.2 * losses[0]


def test_best_span_matches_brute_force():
    torch.manual_seed(1)
    for _ in range(20):
        st, en = torch.randn(30), torch.randn(30)
        ref = max(((i, j, float(st[i] + en[j])) for i in range(30) for j in range(i, min(30, i + 5))), key=lambda x: x[2])
        i, j, s = best_span(st, en, max_len=5)
        assert (i, j) == ref[:2] and abs(s - ref[2]) < 1e-6
