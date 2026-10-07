# 09 Large language models

A large language model (LLM) is a decoder-only transformer (note 06) with $10^8$-$10^{12}$ parameters trained by next-token prediction on $10^{11}$-$10^{13}$ tokens of text, then adapted to follow instructions. The pretrained weights are a general-purpose sequence prior; everything a project does with them is adaptation: prompting (no weight change), parameter-efficient fine-tuning (change $<1\%$ of the weights), retrieval augmentation (change the input), or full fine-tuning (rarely affordable). This note covers the data path (tokenisation), the training objectives and their metrics, scaling laws, fine-tuning and LoRA in detail, prompting and decoding, evaluation, RAG, and the practical constraints of doing any of this on an M3 Pro for the course project. The reference implementation `llm_finetune_sketch.py` reproduces the LoRA mechanics on a tiny model.

## Concepts

### Tokenisation

A token is the unit the model reads and predicts: an integer index into a vocabulary of size $V$, mapped to an embedding row $E_t\in\mathbb{R}^d$. Options: characters ($V\approx 10^2$, long sequences, no out-of-vocabulary problem, weak per-token semantics), words ($V\ge 10^5$, short sequences, OOV words and rare-word embeddings undertrained), subwords ($V\approx 3\cdot10^4$-$2.5\cdot10^5$: frequent words are one token, rare words split into pieces; the standard).

Byte-pair encoding (Sennrich et al. 2016; Gage 1994). Training:
1. Split the corpus into words (pre-tokenisation on whitespace/punctuation), represent each word as a sequence of characters (or bytes) plus an end-of-word marker; the initial vocabulary is the character set.
2. Count the frequency of every adjacent symbol pair over the corpus.
3. Merge the most frequent pair $(a, b)$ into a new symbol $ab$, add it to the vocabulary, record the merge rule.
4. Repeat 2-3 for a fixed number of merges ($V - |\text{chars}|$).

Encoding a new string applies the recorded merges in order. Example corpus with counts: `hug`$\times10$, `pug`$\times5$, `pun`$\times12$, `bun`$\times4$, `hugs`$\times5$. Pair counts: $(u,g) = 20$, $(p,u) = 17$, $(u,n) = 16$, $(h,u) = 15$, $(g,s) = 5$, $(b,u) = 4$. Merge 1: `ug`. New counts: $(u,n) = 16$, $(h,\text{ug}) = 15$, $(p,u) = 12$, $(p,\text{ug}) = 5$. Merge 2: `un`. Merge 3: `hug`. After three merges `hugs` encodes as `[hug, s]`, `bun` as `[b, un]`. Byte-level BPE (GPT-2) starts from 256 bytes so any string is encodable. WordPiece (BERT) chooses the merge maximising the likelihood gain $\frac{\text{count}(ab)}{\text{count}(a)\,\text{count}(b)}$ instead of raw count, and marks word-internal pieces with `##`. SentencePiece treats the input as a raw stream (whitespace is the symbol `▁`, no pre-tokeniser, language-independent) and implements BPE or the unigram model (Kudo 2018): start from a large candidate vocabulary, fit a unigram distribution $p(\text{token})$ by EM, prune tokens whose removal least reduces the corpus likelihood; encoding is the Viterbi segmentation maximising $\prod p(t_i)$.

Trade-offs: larger $V$ shortens sequences (cheaper attention, longer effective context) and gives rare pieces poor embeddings; the embedding and output matrices cost $2Vd$ parameters ($V = 128{,}000$, $d = 4096$: $1.05$ B). Special tokens: `<bos>`, `<eos>`, `<pad>`, `<unk>`, and chat-template markers (`<|user|>`, `<|assistant|>`) that instruction-tuned models were trained with; leaving them out silently degrades outputs. Why tokenisation matters: numbers are split inconsistently (`1234` may be `[123, 4]` while `1235` is `[12, 35]`), so digit-level arithmetic is not aligned to the model's units (models with single-digit tokenisation do arithmetic better); non-English and code text is tokenised into 2-4$\times$ more tokens per word than English by an English-heavy vocabulary, which costs context, money and accuracy; whitespace handling (`" hello"` vs `"hello"`) changes tokens, so prompts must be constructed the way the training data was.

### Pretraining objectives

Causal (autoregressive) LM. $p_\theta(x_{1:T}) = \prod_{t=1}^T p_\theta(x_t\mid x_{<t})$; loss = mean next-token cross-entropy $\mathcal L = -\frac1T\sum_t\log p_\theta(x_t\mid x_{<t})$, computed for all positions in parallel with a causal mask (teacher forcing). Metrics: perplexity $\mathrm{PPL} = \exp(\mathcal L)$ with $\mathcal L$ in nats, the effective branching factor (a uniform model over $V$ has $\mathrm{PPL} = V$); bits per token $= \mathcal L/\ln 2 = \log_2\mathrm{PPL}$; bits per character $= $ bits per token $\times$ tokens/character, the tokeniser-independent version (the reference code reports bits per character). Perplexities of models with different tokenisers are not comparable.

Masked LM (BERT, Devlin et al. 2019): replace 15% of tokens by `[MASK]` (80%), a random token (10%) or leave unchanged (10%), predict the originals from bidirectional context. Produces encoders for classification and retrieval, not generators; the pretrain/fine-tune mismatch (`[MASK]` never appears downstream) is the reason for the 80/10/10 rule.

Span corruption (T5, Raffel et al. 2020): mask contiguous spans (mean length 3, 15% of tokens), replace each by a sentinel `<X>`, `<Y>`, and train an encoder-decoder to output `<X> span1 <Y> span2`. Prefix LM: a decoder-only model with bidirectional attention over a prefix (the input) and causal attention over the continuation (the target); a middle ground used in UL2 and PaLM ablations. Causal LM won at scale because every token is a training signal (vs 15%), it needs no special tokens at inference, and generation is the training task.

### Scaling laws and compute

Training FLOPs $C\approx 6ND$ for $N$ parameters and $D$ tokens (forward $2N$, backward $4N$ per token). Kaplan et al. (2020) fit $\mathcal L(N, D)$ as power laws and recommended growing $N$ faster than $D$. Hoffmann et al. (2022, Chinchilla) refit with $\mathcal L(N,D) = E + A N^{-\alpha} + B D^{-\beta}$ ($\alpha\approx 0.34$, $\beta\approx 0.28$) and found the compute-optimal allocation scales $N$ and $D$ equally, with $D_{\text{opt}}\approx 20N$ tokens: a 70 B model should see $1.4$ T tokens, and GPT-3 (175 B, 300 B tokens) was undertrained. Since inference cost is proportional to $N$ alone, deployed models are deliberately overtrained beyond $20N$ (LLaMA-3 8B on 15 T tokens $= 1900N$) to get a small model with the loss of a larger one. Consequences for a project: pretraining is out of scope (even a 125 M model needs $2.5$ B tokens and $\approx 2\cdot10^{18}$ FLOPs); the question is always which pretrained model to adapt.

### The GPT-style decoder stack

Token embedding plus positional information (learned absolute in GPT-2, rotary RoPE in LLaMA/Mistral), $L$ pre-LayerNorm (or RMSNorm) blocks of causal multi-head self-attention and a position-wise MLP (GELU or SwiGLU, width $4d$ or $\frac83 d$), a final norm and an output projection to $V$ logits, often tied to the input embedding; see note 06 for attention, masking and the KV cache. Parameter count $\approx 12Ld^2 + 2Vd$ (LLaMA-2-7B: $L = 32$, $d = 4096$, $V = 32{,}000$: $6.4 + 0.26 = 6.7$ B). Inference cost per generated token is $\approx 2N$ FLOPs plus attention over the cache, $O(T d L)$; memory for the KV cache is $2\cdot L\cdot T\cdot d\cdot 2$ bytes in bf16 ($7$ B model, $T = 4096$: $2$ GB per sequence).

### Fine-tuning

Full fine-tuning updates all $N$ parameters. Memory in mixed precision with Adam: bf16 weights (2 B) + fp32 master weights (4 B) + bf16 gradients (2 B) + fp32 Adam $m, v$ (8 B) $= 16$ bytes/parameter, plus activations ($\propto B\cdot T\cdot d\cdot L$, reducible by gradient checkpointing). A 7 B model needs $112$ GB before activations, a 1 B model $16$ GB. Full fine-tuning on small data also erases pretrained abilities (catastrophic forgetting) and produces a full copy per task.

Instruction tuning / supervised fine-tuning (SFT): continue the causal-LM loss on (prompt, response) pairs with the loss masked to the response tokens; $10^3$-$10^5$ examples turn a base model into an assistant that follows the prompt format (Wei et al. 2022, FLAN; Ouyang et al. 2022). RLHF (Ouyang et al. 2022): collect human rankings of responses, train a reward model $r_\phi(x, y)$ on pairwise preferences with the Bradley-Terry loss $-\log\sigma(r(x, y_w) - r(x, y_l))$, then optimise the policy with PPO on $r_\phi(x,y) - \beta\,\mathrm{KL}(\pi_\theta\|\pi_{\text{ref}})$, the KL term keeping the model near the SFT model. DPO (Rafailov et al. 2023) eliminates the reward model and RL loop: the optimal policy of the KL-regularised objective satisfies $r(x,y) = \beta\log\frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \text{const}$, so the preference loss becomes a supervised objective on the policy directly,

$$
\mathcal L_{\text{DPO}} = -\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\Big),
$$

one forward pass through $\pi_\theta$ and the frozen $\pi_{\text{ref}}$ per pair. Both are compatible with LoRA.

### Parameter-efficient fine-tuning: LoRA (Hu et al. 2021 [S77])

Hypothesis: the weight update $\Delta W$ needed for a downstream task has low intrinsic rank. Freeze $W_0\in\mathbb{R}^{d\times k}$ and add a trainable rank-$r$ factorisation:

$$
h = W_0 x + \Delta W x = W_0 x + \frac{\alpha}{r}\,B A x,\qquad A\in\mathbb{R}^{r\times k},\ B\in\mathbb{R}^{d\times r},\ r\ll\min(d,k).
$$

Initialisation: $A\sim\mathcal N(0, \sigma^2)$ (Kaiming-uniform in the reference implementations), $B = 0$, so $\Delta W = 0$ at step 0 and the model starts exactly at the pretrained function; gradients flow to $A$ through $B$ only after $B$ moves, and to $B$ immediately since $Ax\ne0$. The scale $\alpha/r$ keeps the effective learning rate of $\Delta W$ roughly constant when $r$ is changed ($\alpha$ fixed, e.g. $\alpha = 2r$ or $\alpha = 16$); rsLoRA argues for $\alpha/\sqrt r$. Rank $r\in[4, 64]$; performance saturates early because the task update really is low-rank; $r = 8$ is a common default. Which matrices: the paper adapts $W_q$ and $W_v$ only; adapting all linear layers (q, k, v, o, MLP up/gate/down) at smaller $r$ is generally better for the same budget (Dettmers et al. 2023). Parameter count per adapted matrix $r(d + k)$ instead of $dk$: for $d = k = 4096$, $r = 16$: $131{,}072$ vs $16.8$ M, a factor $128$. Optimiser state and gradients exist only for $A, B$, so memory drops from $16$ bytes/param to $2$ bytes/param (frozen bf16 weights) plus $16$ bytes per adapter parameter; activations are unchanged. Merging at inference: $W = W_0 + \frac{\alpha}{r}BA$ once, then the adapted model has the same cost as the base (no extra latency); keep adapters separate to serve many tasks from one base. QLoRA (Dettmers et al. 2023): store $W_0$ in 4-bit NormalFloat with double quantisation, dequantise on the fly for the matmul, keep $A, B$ in bf16 and use paged optimisers; a 65 B model fine-tunes on one 48 GB GPU with quality matching bf16 LoRA.

Other PEFT methods, one line each: adapters (Houlsby et al. 2019) insert small bottleneck MLPs $W_{\text{up}}\,\sigma(W_{\text{down}}h) + h$ after attention and MLP sub-layers, adding inference latency; prefix tuning (Li & Liang 2021) prepends trainable key/value vectors to every attention layer, leaving weights untouched; prompt tuning (Lester et al. 2021) prepends trainable embedding vectors to the input only, works at scale ($>10$ B) and is weak on small models; (IA)$^3$ scales activations with learned vectors; BitFit trains biases only.

### Prompting and decoding

Zero-shot: the task is described in the prompt; few-shot / in-context learning (Brown et al. 2020): $k$ input-output examples in the prompt, no weight change, the model infers the task from the pattern; sensitive to example order, format and label balance. Chain-of-thought (Wei et al. 2022 [S79]): ask for intermediate reasoning steps ("let's think step by step", or few-shot examples with reasoning); improves multi-step arithmetic and logic for large models, because the generated tokens act as working memory. **Tree-of-thought** (Yao et al. 2023 [S79]), a named chapter of Lecture 13 [S4], generalises the chain into a search: generate several candidate next steps, score them with the model itself, and explore the promising branches with BFS or DFS, backtracking when a branch is judged hopeless. It costs many more forward passes and pays off only where a single greedy chain is likely to go wrong early. System prompt: a fixed preamble with role and constraints, given its own chat-template slot in instruction-tuned models. Prompt engineering is a hyperparameter search over strings; report the exact prompt with the results.

Decoding from the logits $z\in\mathbb{R}^V$ at each step: greedy $\arg\max_t z_t$ (deterministic, repetitive); temperature $T$: sample from $\mathrm{softmax}(z/T)$, $T\to0$ is greedy, $T = 1$ is the model's distribution, $T > 1$ flattens; top-$k$: sample from the $k$ most probable tokens renormalised; top-$p$ (nucleus, Holtzman et al. 2020): sample from the smallest set whose cumulative probability $\ge p$; beam search keeps the $b$ highest-probability partial sequences (used in translation, produces bland or repetitive text in open-ended generation); repetition penalties; constrained decoding (grammar, JSON). Why temperature matters for evaluation: at $T > 0$ the output is a random variable, so a single run is one sample of the metric; report the mean over $n$ samples or use $T = 0$ for reproducibility, and state $T$, top-$p$ and the seed; pass@$k$ metrics for code explicitly assume sampling at $T\approx 0.8$; comparing a greedy baseline against a sampled model is not a fair comparison.

### Evaluation

Perplexity measures the pretraining objective on held-out text, cheap and continuous, but it does not measure task performance, is tokeniser-dependent, and improves with memorised data. Task metrics: accuracy on multiple-choice benchmarks (MMLU: 57 subjects, 4 choices, 5-shot; ARC, HellaSwag, GSM8K for arithmetic word problems, HumanEval for code with pass@$k$, BIG-bench); exact match and F1 for extractive QA; BLEU/ROUGE $n$-gram overlap for generation (weakly correlated with quality); semantic similarity via an embedding model or BERTScore. Contamination: benchmark test sets are on the web and in pretraining corpora, so scores inflate; check $n$-gram overlap of test items with the training data, prefer benchmarks released after the model's cutoff, and never fine-tune on data that overlaps the test set (for a project: deduplicate by hashing normalised questions across splits). LLM-as-judge (Zheng et al. 2023): a strong model scores or compares outputs; correlates with human preference around $80\%$ but has biases: position bias (prefers the first answer, mitigate by swapping), verbosity bias (prefers longer), self-enhancement (prefers its own style), and it cannot verify facts; use pairwise comparisons with swapped order, a rubric, and spot-check against human labels. Human evaluation is the reference: define a rubric, at least two annotators, report inter-annotator agreement (Cohen's $\kappa$). Exact match is right for closed-form answers (numbers, labels) and wrong for free text; semantic metrics are the reverse.

### Retrieval-augmented generation (RAG)

Pipeline (Lewis et al. 2020 [S80]): (1) chunk the documents into passages of 200-500 tokens with overlap, keeping metadata (source, page); (2) embed each chunk with a bi-encoder (a BERT-style encoder producing one vector per passage, trained contrastively so that question and relevant passage are close; e.g. `all-MiniLM`, `bge`, `e5`) into $\mathbb{R}^{384..1024}$; (3) store in a vector index, cosine similarity $= \frac{q^\top p}{\|q\|\|p\|}$ (dot product after $\ell_2$ normalisation), exact search with FAISS `IndexFlatIP` up to $10^6$ vectors, approximate (HNSW, IVF) beyond; (4) at query time embed the question, retrieve the top-$k$ ($k = 3$-$10$) chunks, optionally rerank with a cross-encoder (joint encoding of query and passage, more accurate, $k$ forward passes); (5) stuff the chunks into the prompt with instructions to answer only from them and to cite chunk IDs; (6) generate. Hybrid retrieval adds BM25 keyword scores for exact terms (IDs, names). Failure modes: retrieval miss (the answer is in the corpus but the chunk is not in the top-$k$; wrong chunking, embedding mismatch between question and passage style, missing keywords); lost in the middle (Liu et al. 2023: models use information at the start and end of a long context much better than in the middle, so put the best chunk first or last); context overflow; conflicting or outdated chunks; the model answering from parametric memory and ignoring the context. Evaluation splits into retrieval (recall@$k$ / MRR against gold passages) and generation (answer correctness against gold answers; faithfulness = fraction of answer claims supported by the retrieved context, judged by an LLM or humans; context precision). RAG reduces hallucination on knowledge questions and allows updates without retraining; it does not teach the model new skills or formats, which is what fine-tuning is for.

### Multimodality and contrastive learning: CLIP

Lecture 13 [S4] closes with multiple modalities, and the mechanism is contrastive pretraining. CLIP (Radford et al. 2021 [S78]) trains an image encoder and a text encoder jointly on 400M (image, caption) pairs from the web. For a batch of $N$ pairs it computes all $N^2$ cosine similarities between image embeddings $I_i$ and text embeddings $T_j$, scales them by a learned temperature, and applies cross-entropy **in both directions** so that the $N$ true pairs are the diagonal:
$$\mathcal L = \tfrac12\Big[\mathrm{CE}\big(\mathrm{sim}(I, T)/\tau,\ \mathrm{diag}\big) + \mathrm{CE}\big(\mathrm{sim}(T, I)/\tau,\ \mathrm{diag}\big)\Big].$$
The other $N-1$ captions in the batch are the negatives, which is why contrastive methods want large batches — the task gets harder, and more informative, as $N$ grows.

What it buys is a **shared embedding space**, and with it zero-shot classification: embed the class names as prompts ("a photo of a {class}"), embed the image, take the nearest. No classifier head, no fine-tuning, no labelled data for the target classes. For a project this is often the strongest baseline you can build in an afternoon, and it is the retrieval backbone for text-to-image models.

### Tool use, agents and the Model Context Protocol

Added for the 2025 edition of the lecture [S4, S6]. A model with a tool interface emits a structured call (a function name and JSON arguments) instead of an answer; the runtime executes it and returns the result as another message, and the loop repeats. This turns a next-token predictor into something that can search, compute and act — and moves the failure surface from "wrong facts" to "wrong actions", which is a different and larger problem.

The **Model Context Protocol** [S81] standardises the connection between a model runtime and those tools and data sources, so that a tool server written once works with any client that speaks the protocol — the usual argument for a standard, applied to the $M \times N$ integration problem.

### Adversarial prompting, AI slop and model collapse

Three failure modes Lecture 13 treats as first-class [S4]:

- **Adversarial prompting / prompt injection.** Instructions that arrive in the *data* (a web page, a document, a tool result) and that the model follows as if they came from the user. Alignment training is a mitigation, not a fix. **KROP** (Martin et al. 2024 [S83]) shows one family of bypasses: the harmful instruction is not written out but assembled by the model from knowledge it already has ("the capital of France" instead of "Paris"), so surface-level filters see nothing. The structural lesson is the one that matters for anything you build: **content retrieved by the model is data, never instructions**, and a system that cannot maintain that boundary cannot be made safe by prompt wording.
- **Model collapse.** Shumailov et al. 2024 [S82]: training generation after generation on the previous generation's output makes the learned distribution progressively lose its tails, converging to a low-variance caricature of the original. The mechanism is sampling error compounding — each generation's finite sample under-represents rare events, and the next model fits that. This is a real constraint on synthetic data (fine in moderation, mixed with real data; not fine as a closed loop) and the technical content behind "AI slop".
- **Hallucination**, below, which is the per-output version of the same underlying fact: the objective rewards plausibility, not truth.

### Hallucination and calibration

Hallucination: fluent output not supported by the input or by facts. Causes: the objective rewards plausible continuations, not truth; missing knowledge; sampling; sycophancy after RLHF; long contexts. Mitigations: RAG with citations, lower temperature, asking for abstention, self-consistency (sample $n$ answers and vote), verification against tools. Calibration: a model is calibrated if among predictions with confidence $p$ a fraction $p$ is correct; measure with reliability diagrams and expected calibration error $\mathrm{ECE} = \sum_b \frac{|B_b|}{n}|\mathrm{acc}(B_b) - \mathrm{conf}(B_b)|$ over confidence bins. Base models are reasonably calibrated on multiple-choice token probabilities; RLHF degrades this (OpenAI 2023 GPT-4 report), and verbalised confidences ("I am 90% sure") are poorly calibrated; temperature scaling on the logits repairs token-level calibration on a validation set.

### Practical for the project

Hugging Face API sketch:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
tok = AutoTokenizer.from_pretrained(name)                       # BPE/SentencePiece + chat template
model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.bfloat16).to(device)
cfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
                 target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM")
model = get_peft_model(model, cfg); model.print_trainable_parameters()
batch = tok(texts, return_tensors="pt", padding=True).to(device)
loss = model(**batch, labels=batch["input_ids"]).loss             # shifts labels internally
# ... optimiser over model.parameters() (only adapters require grad); model.merge_and_unload() at the end
```

Model sizes for an M3 Pro (18 or 36 GB unified memory, `mps` backend): bf16 weights cost $2$ bytes/param, so inference with a 3 B model takes $6$ GB and a 7-8 B model $14$-$16$ GB (only on the 36 GB machine, slow); LoRA training in bf16 fits for $\le 1$-$3$ B parameters with sequence length $\le 512$ and batch $\le 8$, with gradient checkpointing; 4-bit loading via `bitsandbytes` targets CUDA and does not run on MPS, so quantised training on Apple silicon means MLX (`mlx-lm` with `--train` LoRA) or GGUF for inference only. Candidates: Qwen2.5-0.5B/1.5B/3B, Llama-3.2-1B/3B, SmolLM2, Gemma-2-2B (check each licence: Llama and Gemma have use restrictions, Qwen and SmolLM are Apache-2.0; a course report must state the licence). Context length: training at 512-1024 tokens is enough for most tasks; attention cost grows quadratically and the KV cache linearly with length. Data leakage: instruction-tuned checkpoints may have seen public benchmarks, so build a test set from data that cannot be in pretraining (own annotations, post-cutoff sources) and deduplicate train/test by normalised text hash. Budget: a LoRA run of a 1 B model on $10^4$ examples for 3 epochs is a few hours on the M3 Pro; plan the 45 h of programming time accordingly and cache tokenised data.

## Architecture sketch

`TinyLM` is `CharTransformer` from note 06: $d = 64$, $4$ heads, $2$ blocks, MLP width $256$, character vocabulary $V$ (digits, `+`, `-`, `=`, padding), `max_len = 10`. The attention module has one fused `qkv = nn.Linear(64, 192)` and `out = nn.Linear(64, 64)`; the MLP `ffn` has `Linear(64, 256)` and `Linear(256, 64)`. Every one of these four linears per block is wrapped in `LoRALinear(base, r=4, alpha=8)`; embeddings, LayerNorms and the output head stay frozen and unwrapped.

```
tokens [B, T] int64, T <= 10
  -> tok_emb [V, 64] + pos_emb [10, 64]                            -> x [B, T, 64]   (frozen)
  -> block x2 (pre-LN):
       LN -> qkv = LoRALinear(64 -> 192) -> split q, k, v [B, T, 4, 16]
       causal MHA (4 heads x 16) -> out = LoRALinear(64 -> 64)     -> [B, T, 64]  (+ residual)
       LN -> ffn: LoRALinear(64 -> 256), GELU, LoRALinear(256 -> 64) -> [B, T, 64]  (+ residual)
  -> LN -> head [64, V]                                            -> logits [B, T, V]  (frozen)
  cross_entropy(logits[:, :-1].reshape(-1, V), tokens[:, 1:].reshape(-1))

LoRALinear(base=nn.Linear(k -> d), r=4, alpha=8), input x [B, T, k]:
   x --- base.weight W0 [d, k], bias  (requires_grad=False) ---> W0 x         [B, T, d] --+
    \                                                                                     (+) -> h [B, T, d]
     +-- A [r, k] = [4, k]  N(0, 1/r) trainable --> A x [B, T, 4]                          |
                        --> B [d, r] = [d, 4]  zeros trainable --> B A x [B, T, d] * (alpha / r = 2) --+
   backward: dL/dB = (alpha/r) (dL/dh)^T (A x),  dL/dA = (alpha/r) B^T (dL/dh)^T x,  dL/dW0 not computed
   merge_lora: W0 <- W0 + (alpha/r) B A, drop A, B; forward cost back to one matmul
```

Worked example: trainable fraction. Base weights per block: `qkv` $64\cdot192 = 12{,}288$, `out` $64\cdot64 = 4{,}096$, `ffn` $64\cdot256 + 256\cdot64 = 32{,}768$, total $49{,}152$ plus $576$ biases; two blocks $99{,}456$; plus token and position embeddings, head and LayerNorms roughly $3{,}000$ (depends on $V$), total $\approx 1.02\cdot10^5$ frozen parameters. LoRA with $r = 4$ on the four linears per block, $r(k + d)$ each: $4(64 + 192) + 4(64 + 64) + 4(64 + 256) + 4(256 + 64) = 1{,}024 + 512 + 1{,}280 + 1{,}280 = 4{,}096$ per block, $8{,}192$ in total, i.e. trainable fraction $8{,}192/(1.02\cdot10^5 + 8{,}192)\approx 7.4\%$ (the exact value is the `trainable_fraction` key of `run`; on `qkv` alone it drops to $2{,}048/1.04\cdot10^5\approx 2\%$). Small models have a large fraction because $r(d + k)/(dk)$ is $12.5\%$ at $d = k = 64$, $r = 4$, and $8.3\%$ for the fused `qkv` ($1{,}024/12{,}288$). For a 7 B LLaMA-style model ($L = 32$, $d = 4096$) with $r = 16$ on $W_q, W_v$: $32\times2\times16\,(4096 + 4096) = 8{,}388{,}608\approx 8.4$ M trainable parameters, $8.4\cdot10^6/6.7\cdot10^9\approx 0.125\%$; these replace $32\times 2\times 16.8$ M $= 1.07$ B weights ($0.78\%$ of them). Memory: full fine-tuning $6.7\cdot10^9\times16$ B $= 107$ GB; LoRA $6.7\cdot10^9\times 2$ B $+ 8.4\cdot10^6\times 16$ B $= 13.4$ GB $+ 0.13$ GB, plus activations; QLoRA $\approx 3.5$ GB $+ 0.13$ GB.

## Pitfalls

- Fine-tune loss starts far above the pretraining loss at step 0 -> $B$ was not zero-initialised (or $\alpha/r$ scaling omitted), so the adapter perturbs the pretrained function immediately -> initialise $B = 0$, check that `model(x)` before training equals the frozen model's output.
- Loss does not move during LoRA training -> all parameters frozen including $A, B$, or the optimiser was built before wrapping and holds no adapter parameters -> wrap first, then `optimizer = Adam([p for p in model.parameters() if p.requires_grad])`, assert `trainable_fraction > 0`.
- After fine-tuning on task B the model can no longer do task A -> catastrophic forgetting, stronger with full fine-tuning and high learning rates -> keep adapters small, mix in 5-10% of task-A data, lower the learning rate ($10^{-4}$ for LoRA, $10^{-5}$ for full), evaluate on both tasks.
- Instruction model produces garbage or ignores the instruction -> chat template and special tokens omitted, prompt tokenised differently from training -> use `tok.apply_chat_template(messages)`; never hand-concatenate role strings.
- Perplexity improved, downstream accuracy did not -> perplexity measures the LM objective on all tokens, including easy ones; the loss was not masked to response tokens in SFT -> set `labels = -100` on prompt tokens, evaluate the task metric on a held-out set, tune on it.
- Benchmark score of a public model is unexpectedly high on the project's test set -> contamination: the test items are on the web -> check $n$-gram overlap, build a private test set, report results on post-cutoff data.
- Generation quality varies run to run and the reported number cannot be reproduced -> sampling at $T > 0$ without a seed and $n = 1$ -> fix seed, report mean $\pm$ std over $n\ge5$ samples or use greedy decoding for the headline number, state $T$ and top-$p$.
- RAG answers confidently with the wrong document -> retrieval miss on paraphrased questions, chunk too large or too small, or the relevant chunk landed in the middle of the context -> measure recall@$k$ on a labelled question set separately from answer quality; tune chunk size; rerank; place the top chunk first.
- Out of memory on MPS when loading a 7 B model -> $14$ GB bf16 weights plus KV cache exceeds unified memory or the `mps` allocator's limit -> use a $\le 3$ B model, shorten the context, `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` only with care, or run 4-bit via MLX/llama.cpp for inference.
- Numbers in the fine-tuning data are tokenised inconsistently and arithmetic accuracy is at chance -> multi-digit tokens split by frequency, not by position -> add spaces between digits or reverse digit order in the data, or pick a model with single-digit tokenisation; evaluate exact match on held-out operands.

## Questions

1. Show that bits per token $= \log_2\mathrm{PPL}$ and compute the perplexity of a character model at $1.5$ bits per character on a corpus with $V = 16$ symbols; compare with the uniform model.

<details><summary>Answer</summary>
$\mathcal L$ (nats) $= \ln\mathrm{PPL}$, and bits per token $= \mathcal L/\ln2 = \ln\mathrm{PPL}/\ln 2 = \log_2\mathrm{PPL}$. At $1.5$ bits per character, $\mathrm{PPL} = 2^{1.5} = 2.83$: the model is as uncertain as a uniform choice among $2.83$ characters. The uniform model has $\log_2 16 = 4$ bits and $\mathrm{PPL} = 16$. For the arithmetic corpus (`12+7=19`) the operand digits are unpredictable ($\approx 3.3$ bits each) while the result digits are deterministic given the prefix ($0$ bits for a perfect model), so the achievable bpc is bounded below by the entropy of the operands divided by the line length.
</details>

2. Derive the gradients of the LoRA loss with respect to $A$ and $B$ and explain why training works even though $B = 0$ at initialisation.

<details><summary>Answer</summary>
With $h = W_0x + sBAx$, $s = \alpha/r$, and upstream gradient $g = \partial\mathcal L/\partial h\in\mathbb{R}^d$: $\partial\mathcal L/\partial B = s\, g\,(Ax)^\top\in\mathbb{R}^{d\times r}$, $\partial\mathcal L/\partial A = s\,B^\top g\,x^\top\in\mathbb{R}^{r\times k}$. At initialisation $B = 0$ gives $\partial\mathcal L/\partial A = 0$, but $\partial\mathcal L/\partial B = s\,g(Ax)^\top\ne0$ because $A$ is random and $Ax\ne0$. After the first update $B\ne0$ and $A$ receives gradient. The symmetric choice $A = 0$, $B$ random would work identically; $A = B = 0$ would be a stationary point and never move.
</details>

3. You have 36 GB of unified memory. Which of the following are feasible and why: (a) inference with an 8 B model in bf16, (b) full fine-tuning of a 1 B model with Adam in mixed precision, (c) LoRA on a 3 B model in bf16, (d) QLoRA on a 7 B model with `bitsandbytes`?

<details><summary>Answer</summary>
(a) $16$ GB weights plus KV cache: feasible, slow. (b) $16$ bytes/param $\times 10^9 = 16$ GB plus activations ($\approx$ a few GB at $T = 512$, batch 4 with checkpointing): feasible on 36 GB, marginal on 18 GB. (c) frozen weights $6$ GB, adapters negligible, activations a few GB: feasible and the recommended setting. (d) `bitsandbytes` 4-bit kernels require CUDA, so not on MPS; the equivalent on Apple silicon is MLX (`mlx_lm.lora` with a 4-bit quantised model), which fits in $\approx 5$ GB.
</details>

4. Explain the Chinchilla result and compute the compute-optimal token budget and FLOPs for a 1.5 B model. Why did LLaMA-3 train an 8 B model on 15 T tokens instead?

<details><summary>Answer</summary>
Hoffmann et al. (2022) fit $\mathcal L(N, D) = E + AN^{-\alpha} + BD^{-\beta}$ on 400 runs and minimised it under $C = 6ND$; the optimum scales $N\propto C^{0.5}$, $D\propto C^{0.5}$, giving $D\approx 20N$. For $N = 1.5\cdot10^9$: $D = 3\cdot10^{10}$ tokens, $C = 6\times1.5\cdot10^9\times3\cdot10^{10} = 2.7\cdot10^{20}$ FLOPs ($\approx 3$ days on 8 A100s at $40\%$ utilisation). Chinchilla optimality minimises training compute for a target loss; it ignores inference cost, which is $\propto N$ per token for the model's lifetime. Training a smaller model far past $20N$ tokens ($15$ T $\approx 1900N$) buys a cheaper model with the loss of a Chinchilla-optimal larger one, and the loss keeps decreasing slowly with $D$.
</details>

5. Design the evaluation for a project that fine-tunes a 1 B model to answer questions about a university's course regulations, with and without RAG. Which metrics, which splits, which decoding, which baselines?

<details><summary>Answer</summary>
Build a question set of $\ge 200$ items with gold answers and gold source passages, written by hand from the documents (not generated by the model under test), split into dev (for prompt and chunk-size tuning) and test (touched once). Metrics: retrieval recall@$k$ and MRR against gold passages; answer exact match for closed answers (dates, ECTS numbers) and an LLM-judge score with a rubric for free-text answers, validated on 50 items by human rating with reported agreement; faithfulness = fraction of answer sentences supported by the retrieved chunks; abstention rate on 30 unanswerable questions. Decoding: greedy for the headline table, plus $n = 5$ samples at $T = 0.7$ to report variance. Baselines: base model zero-shot without RAG, base model with RAG, LoRA-tuned model without RAG, LoRA-tuned with RAG, and a retrieval-only "return the top chunk" baseline. Check that no test question text appears in the fine-tuning data (hash-based dedup) and report the licence of the model and embedding model.
</details>

6. Why does a fine-tuning corpus of `19-7=12` lines transfer from a model pretrained on `12+7=19`, and what does the reference experiment's `finetune_bpc` measure? What would you compare it against?

<details><summary>Answer</summary>
Pretraining on addition teaches the tokeniser-free character model the format (digits, operator, `=`, line structure), digit embeddings, positional structure and carry-like manipulations; subtraction shares all but the operator semantics, so a low-rank update of attention and MLP projections suffices to redirect the computation. `finetune_bpc` is the bits per character of the adapted model on held-out subtraction lines (lower is better; the result digits should approach $0$ bits). Compare against (i) the frozen pretrained model on subtraction (should be near the operand entropy plus a penalty on the result digits), (ii) full fine-tuning of all weights with the same step budget (upper bound on adaptation, higher `trainable_fraction`), (iii) LoRA at $r = 1, 4, 16$ to see the rank at which quality saturates, and (iv) bpc on the original addition corpus after fine-tuning to measure forgetting.
</details>

7. Why is the attention-based transformer's raw KV cache size a constraint on context length, and how does it scale? Compute it for a 3 B model with $L = 28$, $d = 3072$ at $T = 8192$ in bf16, and name two techniques that reduce it.

<details><summary>Answer</summary>
Each generated token attends to the keys and values of all previous tokens in every layer, which are cached to avoid recomputation: size $2\times L\times T\times d\times$ bytes. For $L = 28$, $d = 3072$, $T = 8192$, $2$ bytes: $2\times28\times8192\times3072\times2 = 2.8$ GB per sequence, linear in $T$ and in batch size. Reductions: grouped-query / multi-query attention shares K and V across heads (LLaMA-3 uses 8 KV heads for 32 query heads, a factor 4), KV-cache quantisation to 8 or 4 bit, sliding-window attention (Mistral), and paged attention for memory management; none changes the $O(T^2)$ prefill compute.
</details>

8. Compare LoRA, prefix tuning and prompt tuning by where the trainable parameters sit, their inference overhead, and when you would pick each in the project.

<details><summary>Answer</summary>
LoRA: low-rank additive updates inside existing linear layers; zero overhead after merging; works across model sizes; the default for a task that needs new behaviour or a new output format. Prefix tuning: trainable key/value vectors prepended in every attention layer; overhead of $p$ extra positions in every attention computation, cannot be merged; useful when the base weights must stay bit-identical and multiple tasks are served with prefix swapping. Prompt tuning: trainable input embeddings only; the cheapest ($p\times d$ parameters), same $p$-token overhead, competitive only for models $\gtrsim 10$ B; on a 1-3 B project model it underperforms LoRA. For the course project on an M3 Pro with a $\le 3$ B model: LoRA (or QLoRA via MLX) on all linear layers with $r = 8$-$16$.
</details>

## Code

`src/py/llm_finetune_sketch.py`. `TinyLM` is the decoder-only character model of `transformer_char.py`. `run(pretrain_steps=300, finetune_steps=300, device=None, seed=0)` pretrains on corpus A from `make_corpus("add")` (lines like `"12+7=19"`), freezes all weights, wraps the attention and MLP `nn.Linear` layers in `LoRALinear(base, r=4, alpha=8)` ($Wx + \frac{\alpha}{r}BAx$, $B$ initialised to zero), fine-tunes only the adapters on corpus B from `make_corpus("sub")` (lines like `"19-7=12"`) with `common.train_loop`, calls `merge_lora(model)`, and returns `{"losses"` (fine-tune losses), `"pretrain_losses", "trainable_fraction", "finetune_bpc"}`. `python src/py/llm_finetune_sketch.py` prints the number of wrapped linears, the trainable fraction, the subtraction bits per character before and after fine-tuning (and after merging, which must match), and greedy completions of a few subtraction prefixes. `test_llm_finetune_sketch.py` calls `run` with small step budgets and asserts `common.loss_decreased(losses)` on the fine-tune losses (mean of the last 10% below the mean of the first 10%); `common.count_params(model, trainable_only=True)` over `count_params(model)` is how the fraction is computed.

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016), ch. 12.4 (natural language processing, n-gram and neural language models, word embeddings), ch. 10 (sequence modelling), ch. 5.7-5.8 (supervised/unsupervised learning, evaluation), ch. 8 (optimisation, memory of Adam).
- Sennrich, Haddow, Birch, "Neural Machine Translation of Rare Words with Subword Units", ACL 2016 (BPE); Kudo & Richardson, "SentencePiece", EMNLP 2018; Kudo, "Subword Regularization", ACL 2018 (unigram).
- Radford et al., "Language Models are Unsupervised Multitask Learners", 2019 (GPT-2); Brown et al., "Language Models are Few-Shot Learners", NeurIPS 2020 (GPT-3, in-context learning).
- Devlin et al., "BERT", NAACL 2019 [S65]; Raffel et al., "T5", JMLR 2020.
- Kaplan et al., "Scaling Laws for Neural Language Models", 2020; Hoffmann et al., "Training Compute-Optimal Large Language Models", NeurIPS 2022 (Chinchilla).
- Touvron et al., "LLaMA", 2023; Dubey et al., "The Llama 3 Herd of Models", 2024.
- Ouyang et al., "Training language models to follow instructions with human feedback", NeurIPS 2022 (RLHF); Rafailov et al., "Direct Preference Optimization", NeurIPS 2023.
- Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022 (arXiv 2021) [S77]; Dettmers et al., "QLoRA", NeurIPS 2023; Houlsby et al., ICML 2019 (adapters); Li & Liang, ACL 2021 (prefix tuning); Lester et al., EMNLP 2021 (prompt tuning).
- Wei et al., "Chain-of-Thought Prompting", NeurIPS 2022 [S79]; Yao et al., "Tree of Thoughts", NeurIPS 2023 [S79]; Holtzman et al., "The Curious Case of Neural Text Degeneration", ICLR 2020 (nucleus sampling).
- Hendrycks et al., "Measuring Massive Multitask Language Understanding", ICLR 2021 (MMLU); Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", NeurIPS 2023.
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020 [S80]; Karpukhin et al., "Dense Passage Retrieval", EMNLP 2020; Liu et al., "Lost in the Middle", TACL 2023; Johnson, Douze, Jégou, "Billion-scale similarity search with GPUs", 2017 (FAISS).
- Guo et al., "On Calibration of Modern Neural Networks", ICML 2017 (ECE, temperature scaling); Ji et al., "Survey of Hallucination in Natural Language Generation", ACM CS 2023.
- Wolf et al., "Transformers: State-of-the-Art Natural Language Processing", EMNLP 2020 (Hugging Face); Mangrulkar et al., PEFT library, 2022.
- Radford et al., "Learning Transferable Visual Models From Natural Language Supervision", ICML 2021 (CLIP) [S78] -- **Lecture 13's reference 26** [S4].
- Anthropic, "Introducing the Model Context Protocol", 2024 [S81]; Martin et al., "Knowledge Return Oriented Prompting (KROP)", 2024 [S83]; Shumailov et al., "AI models collapse when trained on recursively generated data", Nature 2024 [S82]. All three are chapters added to the 2025 edition of the lecture.
- **Lecture 13** [S4], *Large Language Models*, is the lecture this note covers: types of LLMs, how they are trained, self-supervision, contrastive learning, prompting and prompt engineering, zero-/few-shot, chain-of-thought, tree-of-thought, best practices, RAG, MCP, problems of LLMs, hallucinations, AI slop, adversarial prompting, KROP, multiple modalities and CLIP, trends and costs. The LLM lecture did not exist before the 2024 edition [S3, S7].
