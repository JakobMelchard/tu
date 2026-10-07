# 06 Transformers

The transformer (Vaswani et al. 2017 [S62]) is a sequence model built entirely from attention and position-wise feed-forward layers, with no recurrence and no convolution. Every token can read from every other token in one layer, so the path length between any two positions is $O(1)$ instead of $O(T)$ as in an RNN, and the whole sequence is processed in parallel on the accelerator. The price is $O(T^2)$ compute and memory in attention and the need to inject position information explicitly. The same block, stacked, is the backbone of BERT, GPT, T5, ViT and every current LLM, so the details below (shapes, masking, normalisation placement, training schedule) transfer directly to the project.

## Concepts

### Tokens, embeddings, the `[B, T, d]` layout

A token is the unit of the input sequence after tokenisation: a character, a byte, a subword (BPE, WordPiece), a word, or an image patch. Tokenisation maps raw input to integer ids in $\{0, \dots, V - 1\}$, $V$ = vocabulary size. A batch is $B$ sequences processed together; sequences are padded (or truncated) to a common length $T$ and a padding mask records which positions are real.

Embedding: a lookup table $E \in \mathbb{R}^{V \times d}$ maps ids `[B, T]` to vectors `[B, T, d]`; $d$ (`d_model`) is the width of the residual stream. Every layer maps `[B, T, d] -> [B, T, d]`, which is what makes the blocks stackable. The output head is a linear map $d \to V$ (often tied to $E^\top$) followed by softmax over $V$.

### Scaled dot-product attention

Given queries $Q \in \mathbb{R}^{T \times d_k}$, keys $K \in \mathbb{R}^{T \times d_k}$, values $V \in \mathbb{R}^{T \times d_v}$,
$$\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\!\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V,$$
with softmax applied row-wise. Row $i$ of the output is a convex combination of value rows weighted by how well query $i$ matches each key $j$. Shapes: $QK^\top$ is `[T, T]`, the result is `[T, d_v]`; batched with heads the score tensor is `[B, h, T, T]`.

Why $\sqrt{d_k}$: if the components of $q, k \in \mathbb{R}^{d_k}$ are independent with zero mean and unit variance, then $q \cdot k = \sum_{i=1}^{d_k} q_i k_i$ has mean 0 and variance $\sum_i \mathrm{Var}(q_i k_i) = \sum_i \mathbb{E}[q_i^2] \mathbb{E}[k_i^2] = d_k$. Without scaling, logits grow as $\sqrt{d_k}$ in standard deviation, the softmax saturates towards one-hot, and its gradient $\partial \mathrm{softmax}_i / \partial z_j = p_i(\delta_{ij} - p_j)$ vanishes. Dividing by $\sqrt{d_k}$ restores unit variance of the logits at initialisation.

Self-attention: $Q = X W_Q$, $K = X W_K$, $V = X W_V$ from the same $X \in \mathbb{R}^{T \times d}$. Cross-attention: queries from one sequence (decoder), keys and values from another (encoder output).

### Multi-head attention

Split $d$ into $h$ heads with $d_k = d_v = d / h$. For head $i$: $W_Q^i, W_K^i, W_V^i \in \mathbb{R}^{d \times d_k}$, $\mathrm{head}_i = \mathrm{Attention}(X W_Q^i, X W_K^i, X W_V^i) \in \mathbb{R}^{T \times d_k}$. Concatenate along the feature axis to `[T, d]` and apply the output projection $W_O \in \mathbb{R}^{d \times d}$:
$$\mathrm{MHA}(X) = \mathrm{Concat}(\mathrm{head}_1, \dots, \mathrm{head}_h)\, W_O.$$
Implementation: one `Linear(d, 3d)` produces $Q, K, V$ for all heads at once, `[B, T, 3d]` is reshaped to `[B, T, 3, h, d_k]` and permuted to three `[B, h, T, d_k]` tensors; the score matmul is `[B, h, T, d_k] x [B, h, d_k, T] -> [B, h, T, T]`.

Parameter count: $W_Q, W_K, W_V$ together are $d \times 3d$, $W_O$ is $d \times d$, total $4d^2$ (plus $4d$ biases if used). Independent of $h$: heads reorganise the same parameters into $h$ parallel lower-rank attention maps, which lets different heads attend to different relations (position, syntax, copying) at no parameter cost.

### Causal masking

A decoder predicting token $t + 1$ from tokens $\le t$ must not see the future. Add a mask $M \in \mathbb{R}^{T \times T}$ with $M_{ij} = 0$ for $j \le i$ and $-\infty$ for $j > i$ to the logits before softmax:
$$\mathrm{softmax}\!\left( \frac{Q K^\top}{\sqrt{d_k}} + M \right).$$
$\exp(-\infty) = 0$, so masked positions receive exactly zero weight and the row still normalises over the allowed positions. In code: `torch.triu(torch.full((T, T), -inf), diagonal=1)` and `scores.masked_fill(mask, -inf)`; use a large negative finite value under fp16 to avoid `inf - inf = nan`. Padding masks work the same way on the key axis. With causal masking, one forward pass of a `[B, T]` batch yields $T$ training targets (next-token prediction at every position), which is why decoder-only training is so data-efficient per pass.

### Positional encoding

Attention is permutation-equivariant: permuting the rows of $X$ permutes the output rows identically, so without position information the model is a bag of tokens. Options:

- Sinusoidal (Vaswani et al. 2017 [S62]): for position $p$ and dimension pair $2i, 2i + 1$,
$$PE(p, 2i) = \sin\!\left(\frac{p}{10000^{2i/d}}\right), \qquad PE(p, 2i + 1) = \cos\!\left(\frac{p}{10000^{2i/d}}\right),$$
added to the token embedding. Each pair $(\sin \omega_i p, \cos \omega_i p)$ is a rotation by angle $\omega_i p$, so for any fixed offset $k$,
$$\begin{pmatrix} \sin \omega_i (p + k) \\ \cos \omega_i (p + k) \end{pmatrix} = \begin{pmatrix} \cos \omega_i k & \sin \omega_i k \\ -\sin \omega_i k & \cos \omega_i k \end{pmatrix} \begin{pmatrix} \sin \omega_i p \\ \cos \omega_i p \end{pmatrix},$$
a linear map that depends on $k$ only. A single linear layer can therefore express "attend to position $p + k$", and the encoding extrapolates to unseen lengths (in principle). Wavelengths range from $2\pi$ to $10000 \cdot 2\pi$, giving both fine and coarse position resolution.
- Learned absolute positions: a second embedding table $P \in \mathbb{R}^{T_{\max} \times d}$, $X = E[\mathrm{ids}] + P[0 : T]$. Simple and used in BERT, GPT-2 and `transformer_char.py`; cannot be evaluated beyond $T_{\max}$.
- RoPE (Su et al. 2021): rotate $q$ and $k$ (not $v$) by position-dependent angles in each 2D subspace before the dot product, so that $q_p \cdot k_{p'}$ depends on $p - p'$ only: relative position enters the attention score directly. Used in LLaMA and most current LLMs; extends to longer contexts with frequency scaling.

### The transformer block

One block, input $X \in \mathbb{R}^{T \times d}$, pre-LN form (Xiong et al. 2020):
$$X' = X + \mathrm{MHA}(\mathrm{LN}(X)), \qquad Y = X' + \mathrm{FFN}(\mathrm{LN}(X')),$$
$$\mathrm{FFN}(x) = W_2\, \mathrm{GELU}(W_1 x + b_1) + b_2, \qquad W_1 \in \mathbb{R}^{4d \times d},\ W_2 \in \mathbb{R}^{d \times 4d}.$$
Post-LN (original paper) is $X' = \mathrm{LN}(X + \mathrm{MHA}(X))$, $Y = \mathrm{LN}(X' + \mathrm{FFN}(X'))$. Pre-LN keeps an unnormalised residual path from the embedding to the output, so gradient norms are roughly uniform across layers at initialisation and training works without warmup tricks; post-LN gives slightly better final quality in some settings but needs warmup and is unstable when deep. Use pre-LN unless replicating a post-LN paper. A final LN is applied after the last block in pre-LN models.

Residual connections make each block a perturbation of the identity, so depth composes; LayerNorm normalises over the feature axis $d$ per token (not over the batch), which is batch-size independent and works for variable-length sequences (Ba et al. 2016 [S30]). The FFN is applied identically and independently at every position (a 1x1 convolution over $T$); it holds most of the parameters and, in trained LLMs, most of the memorised facts.

Parameter count per block: attention $4d^2$, FFN $2 \cdot 4d \cdot d = 8d^2$, total $12d^2$; biases and the two LayerNorms add $O(d)$: $4d$ (attention biases) $+ 5d$ (FFN biases: $4d + d$) $+ 4d$ (two LN, each $\gamma, \beta$) $= 13d$. GPT-3 175B: $d = 12288$, 96 layers, $12 \cdot 12288^2 \cdot 96 \approx 1.74 \times 10^{11}$ (Brown et al. 2020).

### Encoder, decoder, encoder-decoder

- Encoder-only (BERT, Devlin et al. 2019): bidirectional self-attention (no causal mask), trained with masked language modelling (predict 15% masked tokens) and used for classification, tagging, retrieval embeddings. A `[CLS]` token's final state summarises the sequence.
- Decoder-only (GPT, Radford et al. 2018; Brown et al. 2020): causal self-attention, trained by next-token prediction $\sum_t -\log p(x_{t+1} \mid x_{\le t})$; used for generation and, via prompting, for everything else. This is `CharTransformer`.
- Encoder-decoder (original transformer; T5, Raffel et al. 2020): the encoder reads the source bidirectionally; each decoder block has causal self-attention, then cross-attention with $Q$ from the decoder stream and $K, V$ from the encoder output, then the FFN. Natural for translation and any input-to-output mapping where the input is fully available. Cross-attention adds another $4d^2$ per decoder block.

### Complexity and the KV cache

Per block, with $T$ tokens and width $d$:

- Attention scores and weighted sum: $QK^\top$ and $PV$ are each $O(T^2 d)$ FLOPs, and the score matrix is $O(h T^2)$ memory per sequence (the `[B, h, T, T]` tensor, stored for backward unless flash attention recomputes it).
- Projections $Q, K, V, O$ and the FFN: $O(T d^2)$, FFN dominating ($8 T d^2$ multiply-adds).

Attention dominates when $T > d$ (long context); the FFN dominates when $T < d$ (short sequences, wide models). For $d = 64$, $T = 8$ in the toy the FFN is 99% of the FLOPs. FlashAttention (Dao et al. 2022) computes exact attention in tiles without materialising the $T \times T$ matrix, making memory $O(T)$ while FLOPs stay $O(T^2 d)$.

KV cache at inference: autoregressive generation produces one token per forward pass. Recomputing $K, V$ for all previous tokens each step costs $O(T^2)$ per token, $O(T^3)$ per sequence. Caching the per-layer $K, V$ tensors `[B, h, T, d_k]` and computing only the new query's row makes each step $O(T)$ in attention. Cache size is $2 \cdot L \cdot h \cdot d_k \cdot T$ values per sequence $= 2 L d T$; for a 7B model ($L = 32$, $d = 4096$) at $T = 4096$ in fp16 that is $2 \cdot 32 \cdot 4096 \cdot 4096 \cdot 2$ bytes $\approx 2.1$ GB per sequence, which is why serving is memory-bound.

### Training recipe

- Schedule: linear warmup over the first 1 to 5% of steps (attention logits and Adam second moments are unreliable at the start), then cosine decay to 10% of peak (Loshchilov & Hutter 2017) or the original inverse-square-root $\mathrm{lr} = d^{-1/2} \min(s^{-1/2}, s \cdot w^{-3/2})$ (Vaswani et al. 2017). Peak lr $3 \times 10^{-4}$ to $10^{-3}$ for small models, lower for larger.
- Optimiser: AdamW (Loshchilov & Hutter 2019) with $\beta = (0.9, 0.95)$, weight decay 0.1 applied to weight matrices only; LayerNorm parameters, biases and often embeddings are excluded (two parameter groups). Decay on norms would pull $\gamma \to 0$ and shrink activations.
- Label smoothing $\epsilon = 0.1$: target $(1 - \epsilon)$ on the true class, $\epsilon / V$ elsewhere; regularises the logits and improves BLEU in translation (Szegedy et al. 2016; Vaswani et al. 2017); usually off for language modelling where perplexity is the metric.
- Gradient clipping at global norm 1.0: `clip_grad_norm_(params, 1.0)` after backward, before the step; prevents the occasional loss spike from destroying the run.
- Dropout 0.1 on attention weights (after softmax), on the residual branches (after MHA and FFN before adding), and on the embedding sum; 0 for large models with enough data.
- Mixed precision: `torch.autocast` in bf16 (or fp16 with a `GradScaler`); keeps master weights in fp32. Softmax and LayerNorm run in fp32 under autocast. On Apple `mps`, fp16 autocast works, bf16 support depends on the PyTorch version; test on a few steps.
- Gradient accumulation: accumulate $k$ micro-batches before `optimizer.step()` to reach an effective batch of $k B$ when memory is limited; divide the loss by $k$; equivalent to the large batch for AdamW. Transformer training likes large token batches ($10^5$ to $10^6$ tokens per step).
- Tokenisation for the project: character-level (as in `transformer_char.py`) is trivial to implement, has a tiny $V$, no unknown tokens, and is appropriate for arithmetic and small synthetic corpora, but sequences are 4 to 5 times longer than with subwords, which costs $T^2$ in attention. Byte-pair encoding (Sennrich et al. 2016) merges frequent pairs to a vocabulary of $8$k to $50$k and is the choice for natural text; use `tokenizers` or `sentencepiece` rather than writing BPE from scratch, and freeze the vocabulary before phase 2.

### Set prediction: DETR and the bipartite matching loss

Do not skip this because it looks like a detection detail. **Lecture 8 spends 25 of its 62 minutes here** — object detection with transformers, DETR, the bipartite matching loss and object queries — which is more time than it gives positional encoding and cross-attention together [S4].

The problem is structural, not visual. A detector must output a *set*: the objects in an image have no canonical order, but a network emits an ordered list of slots. A naive per-slot loss punishes a model that finds the right objects in the wrong slots, so classical detectors avoid the issue with anchors, a hand-designed assignment rule, and non-maximum suppression to delete the duplicates that rule produces.

DETR (Carion et al. 2020 [S63]) removes all three. A CNN backbone produces features, a transformer encoder contextualises them, and a decoder attends from $N$ learned **object queries** — $N$ fixed and larger than any plausible object count, 100 in the paper — each emitting one (class, box). At training time the loss first solves for the cheapest one-to-one matching between the $N$ predictions and the $M \le N$ ground-truth objects:
$$\hat\sigma = \arg\min_{\sigma} \sum_{i=1}^{M} \mathcal C\big(\hat p_{\sigma(i)}, \hat b_{\sigma(i)};\ c_i, b_i\big), \qquad
\mathcal C = -\hat p_{\sigma(i)}(c_i) + \lambda_{L1}\|\hat b_{\sigma(i)} - b_i\|_1 + \lambda_{giou}\big(1 - \mathrm{GIoU}\big),$$
with $\lambda_{L1} = 5$, $\lambda_{giou} = 2$. Note the class term is a **probability, not a log-probability**, deliberately, so that it is on the same scale as the box terms. This is an assignment problem and is solved **exactly** in $O(N^3)$ by the Hungarian algorithm (`scipy.optimize.linear_sum_assignment`). Greedy matching — repeatedly take the cheapest remaining pair — is *not* equivalent; on random $5\times3$ cost matrices it is strictly worse about a quarter of the time (measured in `src/py/set_prediction.py`).

The loss is then applied along $\hat\sigma$: cross-entropy over all $N$ slots, where unmatched slots get the special **"no object"** class (down-weighted $0.1$, since it dominates), plus L1 and GIoU box losses on the matched slots only. Because the matching is one-to-one, **two predictions can never both claim one object** — duplicate suppression is a property of the loss, so there is no NMS.

**Why GIoU and not IoU.** IoU is exactly zero for *every* pair of disjoint boxes, so it is flat and gives no gradient telling a badly placed box which way to move. Generalised IoU subtracts the share of the smallest enclosing box $C$ that neither occupies:
$$\mathrm{GIoU}(A, B) = \mathrm{IoU}(A,B) - \frac{|C \setminus (A \cup B)|}{|C|} \in [-1, 1],$$
which keeps decreasing towards $-1$ as the boxes separate. Measured in `set_prediction.py`: two unit squares that merely touch give IoU $0$, GIoU $0$; eight units apart they give IoU $0$, GIoU $-0.8$ — and the gradient of IoU w.r.t. the box is exactly zero while GIoU's is not. L1 alone is not enough either, because its scale depends on box size.

The price of the design: DETR converges slowly (500 epochs in the paper) because the queries have to specialise, and it is weak on small objects. Deformable DETR and DINO fix both. But the set-prediction idea is the transferable part — the same matching loss is used wherever a model must emit an unordered collection.

`src/py/set_prediction.py` implements GIoU, the matching cost, the Hungarian and greedy matchers, the full criterion, and a small query-based set predictor; the tests check the matcher against exhaustive enumeration and the loss against permutation invariance of the slots.

### Vision transformer

ViT (Dosovitskiy et al. 2021 [S64]) and the hierarchical Swin Transformer (Liu et al. 2021 [S64]) are the two Lecture 8 names under *architecture variations* [S4].

ViT (Dosovitskiy et al. 2021) splits an image `[3, H, W]` into $N = (H / p)(W / p)$ non-overlapping patches of size $p \times p$ ($p = 16$ on 224x224 gives 196 patches), flattens each to $3p^2$ values and projects linearly to $d$: the patches are the tokens. A learned `[CLS]` token is prepended (giving $T = N + 1$), learned 1D position embeddings are added, a standard pre-LN encoder is applied, and the final `[CLS]` state goes to a classification head. ViT has no convolutional inductive bias (locality, translation equivariance), so it underperforms CNNs on small datasets and overtakes them with 10M or more images or with strong augmentation and distillation (DeiT, Touvron et al. 2021). For the project on a small image dataset, a CNN or a pretrained ViT fine-tuned on the target is the safer choice; a ViT from scratch is not.

## Architecture sketch

`CharTransformer(vocab, d_model=64, n_heads=4, n_layers=2, max_len)` on lines like `"12+7=19"`, vocabulary of digits, `+`, `=`, newline and padding ($V = 14$), shown for `T = 8`, `d = 64`, `h = 4`, `d_k = 16`:

```
ids [B, 8]  (int64)
  -> token embedding E[V, 64]       -> [B, 8, 64]
  +  position embedding P[max_len, 64][:8]  -> [B, 8, 64]
  -> dropout

  block x 2:
    LN                              -> [B, 8, 64]
    Linear(64, 192) -> split Q,K,V  -> 3 x [B, 8, 64] -> reshape/permute -> 3 x [B, 4, 8, 16]
    scores = Q K^T / sqrt(16)       -> [B, 4, 8, 8]
    + causal_mask(8)  (upper triangle -inf)
    softmax over last axis, dropout -> [B, 4, 8, 8]
    @ V                             -> [B, 4, 8, 16] -> permute/reshape -> [B, 8, 64]
    Linear(64, 64) (W_O), dropout   -> [B, 8, 64]
    residual add                    -> [B, 8, 64]
    LN -> Linear(64, 256) -> GELU -> Linear(256, 64) -> dropout -> residual add  -> [B, 8, 64]

  final LN                          -> [B, 8, 64]
  -> Linear(64, V) logits           -> [B, 8, 14]

loss = cross_entropy(logits[:, :-1].reshape(-1, V), ids[:, 1:].reshape(-1))   (next-char prediction)
bits_per_char = loss / ln 2
generate(model, prefix, max_new): feed prefix, take argmax (or sample) of the last logit row, append, repeat
```

Worked example 1, parameters of one block at $d = 64$:

- Attention: $W_{QKV}$: $64 \cdot 192 + 192 = 12480$; $W_O$: $64 \cdot 64 + 64 = 4160$; sum $16640$ ($4d^2 = 16384$ plus $4d = 256$ biases).
- FFN: $W_1$: $64 \cdot 256 + 256 = 16640$; $W_2$: $256 \cdot 64 + 64 = 16448$; sum $33088$ ($8d^2 = 32768$ plus $5d = 320$).
- Two LayerNorms: $2 \cdot 2 \cdot 64 = 256$.
- Block total $= 16640 + 33088 + 256 = 49984 \approx 12 d^2 + 13 d = 49152 + 832$.

Whole model: embeddings $14 \cdot 64 = 896$, positions $\mathrm{max\_len} \cdot 64$ (e.g. $16 \cdot 64 = 1024$), 2 blocks $99\,968$, final LN $128$, head $64 \cdot 14 = 896$ (`transformer_char.py` builds the head with `bias=False`, so there is no $+14$): **$102\,912$**, confirmed by `common.count_params(model)` and asserted in `test_shape_formulas.py::test_note_06_worked_examples`.

Worked example 2, attention memory for $T = 1024$: the score tensor is `[B, h, T, T]`. For $h = 4$, $B = 1$: $4 \cdot 1024^2 = 4.19$M floats $= 16.8$ MB $= 16.0$ MiB in fp32, per layer, kept for backward (plus the same for the softmax output). For a GPT-2-small configuration ($h = 12$, $L = 12$, $B = 8$): $8 \cdot 12 \cdot 1024^2 \cdot 12 = 1.2 \times 10^9$ floats $= 4.83$ GB $= 4.5$ GiB in fp32, half that in bf16, before activations of the FFN, which is why FlashAttention matters at this scale. Doubling $T$ to 2048 quadruples this; the FFN activation memory only doubles.

## Pitfalls

- Loss stuck at $\ln V$ (2.64 nats for $V = 14$) from the start -> model predicts the unigram distribution; positional embedding missing, or the causal mask is applied after softmax instead of before -> add positions, `masked_fill` the logits with $-\infty$ before softmax.
- Training loss falls to near zero, generated strings are wrong -> the mask leaks the future (mask built with `diagonal=0` masks the diagonal, or the mask is on the wrong axis), so the model copies the target -> assert `mask[i, j]` is $-\infty$ iff $j > i$; check that shifting inputs by one still works.
- NaN loss after a few hundred steps -> fp16 overflow in the attention logits or `-inf` rows in a fully padded query -> use bf16 or fp32, mask with $-10^4$ under fp16, ensure no row is entirely masked.
- Loss spikes and never recovers -> lr too high without warmup, Adam second-moment estimates unreliable early -> linear warmup 500 to 2000 steps, gradient clipping at 1.0, lower peak lr.
- Quality degrades when generating beyond the training length -> learned absolute positions have no entries past `max_len`, or attention has never seen those distances -> train with `max_len` covering the longest generation, or use RoPE with length extrapolation.
- `generate` produces the same token repeatedly -> greedy decoding on a small model finds a fixed point -> sample with temperature 0.8 to 1.0 or top-k, and verify on the training prefix `"12+7="`.
- Weight decay applied to LayerNorm and biases -> activations shrink, loss plateaus higher -> two parameter groups, decay only 2D weight tensors.
- Slow training on `mps` for the tiny model -> many small kernels; `[B, 8, 64]` tensors do not saturate the GPU -> increase $B$ to 256 or more, or run on `cpu` and compare with `common.Timer`.
- Reported bits per character not comparable across tokenisers -> BPE tokens carry more bits each -> convert to bits per byte or per character of the raw text before comparing models in phase 3.
- Attention heads all look identical after training -> initialisation symmetric or lr too low to break it; or evaluating with dropout still active -> check `model.eval()` at evaluation, use the default per-head random init.

## Questions

1. Show that the unscaled dot product $q \cdot k$ of two vectors with i.i.d. zero-mean unit-variance components has variance $d_k$, and explain the consequence for softmax gradients.

<details><summary>Answer</summary>
$q \cdot k = \sum_{i=1}^{d_k} q_i k_i$. Each product has mean $\mathbb{E}[q_i]\mathbb{E}[k_i] = 0$ and variance $\mathbb{E}[q_i^2]\mathbb{E}[k_i^2] = 1$; the terms are independent, so the variance of the sum is $d_k$. Logits with standard deviation $\sqrt{d_k}$ push the softmax towards one-hot; its Jacobian $p_i(\delta_{ij} - p_j)$ is then near zero and gradients to $Q, K$ vanish. Dividing by $\sqrt{d_k}$ gives unit-variance logits at initialisation.
</details>

2. Count the parameters of multi-head attention and of the FFN in one block with width $d$ and show the total is about $12d^2$. Why does the head count not appear?

<details><summary>Answer</summary>
$W_Q, W_K, W_V \in \mathbb{R}^{d \times d}$ (as concatenations of $h$ blocks $d \times d/h$) and $W_O \in \mathbb{R}^{d \times d}$: $4d^2$. FFN with hidden $4d$: $W_1 \in \mathbb{R}^{4d \times d}$, $W_2 \in \mathbb{R}^{d \times 4d}$: $8d^2$. Total $12d^2 + O(d)$ for biases and LayerNorm. The heads partition the same $d$ output columns of $W_Q, W_K, W_V$ into $h$ groups, so their number changes how the projections are used, not how many parameters they have.
</details>

3. Prove that sinusoidal encodings satisfy $PE(p + k) = R_k\, PE(p)$ with $R_k$ independent of $p$.

<details><summary>Answer</summary>
For each frequency $\omega_i = 10000^{-2i/d}$ the pair $(\sin \omega_i p, \cos \omega_i p)$ is a unit vector at angle $\omega_i p$. The angle-addition formulas give $\sin \omega_i(p + k) = \sin \omega_i p \cos \omega_i k + \cos \omega_i p \sin \omega_i k$ and $\cos \omega_i (p + k) = \cos \omega_i p \cos \omega_i k - \sin \omega_i p \sin \omega_i k$, i.e. a 2x2 rotation by $\omega_i k$ applied to the pair. Stacking the $d/2$ rotations gives a block-diagonal $R_k$ that depends only on $k$. Hence a linear layer can compute "the encoding $k$ positions away", which is the mechanism by which attention can learn relative offsets from absolute encodings.
</details>

4. Compare the FLOPs of attention and FFN per block for $T = 512$, $d = 768$ and for $T = 8192$, $d = 768$.

<details><summary>Answer</summary>
Attention core: $2 T^2 d$ multiply-adds ($QK^\top$ and $PV$). FFN: $8 T d^2$. Ratio attention/FFN $= 2T^2 d / 8Td^2 = T / 4d$. For $T = 512$, $d = 768$: $512 / 3072 \approx 0.17$, FFN dominates. For $T = 8192$: $8192 / 3072 \approx 2.7$, attention dominates. The crossover is $T = 4d = 3072$. Memory tells a different story: the score tensor $h T^2$ per layer is already large at $T = 512$ relative to the $T \cdot 4d$ FFN activations when $h T > 4d$.
</details>

5. Explain what the KV cache stores, why it makes generation $O(T)$ per token, and estimate its size for $L = 2$, $d = 64$, $T = 16$ in fp32.

<details><summary>Answer</summary>
For each layer it stores the key and value tensors of all previous positions, `[B, h, t, d_k]` each. A new token needs its own $q$ against all cached $k$ (one row of scores, $O(t d)$) and the weighted sum of cached $v$, instead of recomputing $K, V$ for all $t$ tokens ($O(t d^2)$) and the full $t \times t$ score matrix. Size $= 2 L d T$ values $= 2 \cdot 2 \cdot 64 \cdot 16 = 4096$ floats $= 16$ KB per sequence; for a 7B model at $T = 4096$ it is gigabytes, so batch size at serving time is bounded by the cache.
</details>

6. Pre-LN vs post-LN: write both block equations and state one advantage of each.

<details><summary>Answer</summary>
Pre-LN: $X' = X + \mathrm{MHA}(\mathrm{LN}(X))$, $Y = X' + \mathrm{FFN}(\mathrm{LN}(X'))$. Post-LN: $X' = \mathrm{LN}(X + \mathrm{MHA}(X))$, $Y = \mathrm{LN}(X' + \mathrm{FFN}(X'))$. Pre-LN keeps a clean identity path, so gradients at initialisation have similar magnitude at every depth and training is stable with little or no warmup (Xiong et al. 2020); post-LN normalises the full residual stream, which constrains activation scale and can reach slightly better final loss for shallow models, but the gradient at early layers scales badly with depth and needs warmup and small lr.
</details>

7. Derive why the causal-mask value must be $-\infty$ (or a very large negative number) and not $0$.

<details><summary>Answer</summary>
Softmax weights are $p_j = \exp(z_j) / \sum_l \exp(z_l)$. Setting a future logit to $0$ gives it weight $\exp(0) / \sum_l \exp(z_l) > 0$, so the future token still contributes to the output and to the normaliser, and the model can learn to exploit it (training loss drops, generation fails). Setting it to $-\infty$ gives $\exp(-\infty) = 0$: zero weight and no contribution to the denominator, so the row is a proper distribution over positions $\le i$. Multiplying the weights by a 0/1 mask after softmax is also wrong unless renormalised, and the gradient through the masked entries would still be nonzero. Under fp16, $-\infty$ minus $-\infty$ in the max-subtraction step can give NaN, hence $-10^4$ instead.
</details>

8. Project question: you plan a decoder-only transformer for a small text corpus (5 MB) in phase 2. Give the configuration, tokeniser, training schedule and what you would measure in phase 3.

<details><summary>Answer</summary>
Configuration: pre-LN decoder, $d = 256$, $h = 8$, $L = 6$, FFN $4d$, learned or RoPE positions, $T = 256$, dropout 0.1, tied embedding and output head: about $5$M parameters, trainable in minutes per epoch on the M3 Pro. Tokeniser: BPE with $V \approx 4$k trained on the corpus (character-level is acceptable if the text is code-like or very small); freeze it before training. Schedule: AdamW $\beta = (0.9, 0.95)$, wd 0.1 on matrices only, peak lr $6 \times 10^{-4}$, warmup 500 steps, cosine to 10%, clip 1.0, batch of $2^{15}$ tokens via accumulation, bf16 if supported on `mps`, early stopping on validation loss. Phase 3: report validation bits per byte against a Kneser-Ney n-gram baseline and a published small model on the same data, samples with fixed seeds, and an ablation (no positions, post-LN, no warmup) to show which choices mattered.
</details>

## Code

`src/py/transformer_char.py`: `make_corpus(n_lines, seed)` generates lines like `"12+7=19"` (addition of small integers); `CharTransformer(vocab, d_model=64, n_heads=4, n_layers=2, max_len)` is decoder-only with learned positional embeddings; `MultiHeadAttention` is written out (no `nn.MultiheadAttention`), using `causal_mask(T)`; `generate(model, prefix, max_new)` produces continuations autoregressively; `run(steps=500, device=None, seed=0)` returns `{"losses", "bits_per_char", "sample"}`. `python src/py/transformer_char.py` trains a few seconds and prints `bits_per_char` and a generated `sample` for an addition prefix. `test_transformer_char.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)`. `common.count_params(model)` gives the parameter count to check against the worked example.

## References

- **Lecture 8** [S4], *Transformers*: why transformers, input embedding and positional encoding, attention, implementing attention, masked attention, cross-attention, the final layers, architecture variations, **transformers for object detection, DETR, bipartite matching loss, object queries** (25 of 62 minutes), advances in transformers.
- Carion et al. 2020 [S63], *End-to-end object detection with transformers* (DETR). Rezatofighi et al. 2019, *Generalized intersection over union*.

- Goodfellow, Bengio, Courville, *Deep Learning* (2016): ch. 10.12 (attention, brief), ch. 12.4.5 (neural machine translation with attention), ch. 8.7.1 (batch and layer normalisation context). Transformers postdate the book; use the papers.
- Vaswani, A. et al. (2017). Attention is all you need.
- Bahdanau, D., Cho, K., Bengio, Y. (2015). Neural machine translation by jointly learning to align and translate. Additive attention.
- Ba, J. L., Kiros, J. R., Hinton, G. E. (2016). Layer normalization.
- Xiong, R. et al. (2020). On layer normalization in the transformer architecture. Pre-LN.
- Devlin, J. et al. (2019). BERT. Encoder-only, masked LM.
- Radford, A. et al. (2018, 2019). Improving language understanding by generative pre-training; Language models are unsupervised multitask learners. GPT, GPT-2.
- Brown, T. et al. (2020). Language models are few-shot learners. GPT-3.
- Raffel, C. et al. (2020). Exploring the limits of transfer learning with a unified text-to-text transformer. T5.
- Su, J. et al. (2021). RoFormer: enhanced transformer with rotary position embedding. RoPE.
- Dao, T. et al. (2022). FlashAttention.
- Loshchilov, I. & Hutter, F. (2017). SGDR: stochastic gradient descent with warm restarts (cosine schedule); (2019). Decoupled weight decay regularization (AdamW).
- Szegedy, C. et al. (2016). Rethinking the Inception architecture. Label smoothing.
- Sennrich, R., Haddow, B., Birch, A. (2016). Neural machine translation of rare words with subword units. BPE.
- Dosovitskiy, A. et al. (2021). An image is worth 16x16 words. ViT.
- Touvron, H. et al. (2021). Training data-efficient image transformers and distillation through attention. DeiT.
- Karpathy, A. (2022). nanoGPT / minGPT. Reference for the written-out multi-head attention in `transformer_char.py`.
