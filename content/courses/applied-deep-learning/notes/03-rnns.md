# 03 RNNs, LSTM and GRU

A recurrent neural network processes a sequence one step at a time, carrying a hidden state $h_t$ that summarises everything seen so far; the same weights are applied at every step, which is parameter sharing along time exactly as a convolution shares along space. Training unrolls the recurrence into a deep feedforward graph and backpropagates through it, and the depth-in-time is where the vanishing/exploding gradient problem originates. LSTM and GRU fix the vanishing part with gated additive state updates and were the standard sequence models until attention-based encoder-decoders became transformers. In the project they remain the right tool for short sequences, small data, streaming inputs, and anything where a per-step state is the natural formulation.

## Concepts

### Sequence data and tensor layout

A sequence is $x_1, \dots, x_T$ with $x_t \in \mathbb R^F$ ($F$ features per step; for text, a token id embedded to $F$ dims). A batch of $B$ sequences is a 3-D tensor. PyTorch offers two layouts: `[B, T, F]` with `batch_first=True` (natural for data loading and indexing) and `[T, B, F]` (the default, because the time loop then slices a contiguous `[B, F]` matrix per step). Both `nn.RNN/LSTM/GRU` return `output` (hidden states of the last layer at every step, `[B, T, D H]` in batch-first) and `h_n` (final state of every layer, `[L D, B, H]`, *never* batch-first), where $L$ = layers, $D \in \{1, 2\}$ = directions. Sequences in a batch must have the same $T$; unequal lengths are handled by padding and packing below. Time complexity of one forward pass is $O(T (H^2 + HF))$ per sequence and strictly sequential in $t$, so it cannot be parallelised over $T$ on the GPU (the main practical reason transformers replaced RNNs for long inputs).

### Vanilla RNN

Elman 1990, Goodfellow 10.2 [S15]:
$$h_t = \tanh(W_h h_{t-1} + W_x x_t + b), \qquad \hat y_t = W_y h_t + c,$$
$h_0 = 0$ (or learned). Parameters of the recurrent part: $W_h \in \mathbb R^{H\times H}$, $W_x \in \mathbb R^{H \times F}$, $b \in \mathbb R^H$, total $H(H + F) + H$. `nn.RNN` keeps two bias vectors ($b_{ih}, b_{hh}$), so $H(H + F) + 2H$. The output at step $t$ depends on $x_{\le t}$ only (causal). The recurrence is a nonlinear dynamical system; with a finite-precision state it is Turing complete in principle (Siegelmann & Sontag 1995) but in practice its memory is limited by the gradient argument below.

### Backprop through time

Unroll the recurrence for $T$ steps into a feedforward graph with shared weights and total loss $L = \sum_t L_t$. The gradient w.r.t. the shared $W_h$ is the sum over all steps of the local gradients, and the gradient of $L_t$ w.r.t. an earlier state is a product of Jacobians:
$$\frac{\partial L_t}{\partial h_k} = \frac{\partial L_t}{\partial h_t} \prod_{i = k+1}^{t} \frac{\partial h_i}{\partial h_{i-1}}, \qquad \frac{\partial h_i}{\partial h_{i-1}} = \mathrm{diag}\big(1 - h_i^2\big)\, W_h,$$
using $\tanh'(z) = 1 - \tanh^2(z)$ (in the row-vector convention $W_h$ appears as $W_h^\top$). Norm bound (Pascanu et al. 2013 [S47]):
$$\Big\|\frac{\partial h_i}{\partial h_{i-1}}\Big\|_2 \le \|\mathrm{diag}(\tanh')\|_2\, \|W_h\|_2 \le \gamma\, \sigma_{max}(W_h), \quad \gamma = \max \tanh' = 1,$$
so $\|\partial L_t / \partial h_k\| \le \|\partial L_t/\partial h_t\|\, (\gamma\,\sigma_{max}(W_h))^{t-k}$. If $\sigma_{max}(W_h) < 1/\gamma$ the gradient from step $t$ to step $k$ decays exponentially in $t - k$: *vanishing*, long-range dependencies contribute nothing to the update and are not learned. If $\sigma_{max} > 1$ and the units are not saturated, the product can grow exponentially: *exploding*, visible as loss spikes and NaN. For sigmoid units $\gamma = 1/4$, which makes vanishing the default. Saturation ($|h| \to 1$) kills $\tanh'$ and also vanishes the gradient. The same analysis applied to $\prod_l J_l$ of a deep feedforward net is why ResNets add the identity term (note 02). Memory of BPTT: all $T$ hidden states are kept for the backward pass, $O(T B H)$.

Truncated BPTT: process a long sequence in chunks of $k$ steps, carry $h$ into the next chunk but `detach()` it so the graph ends at the chunk boundary. Cost $O(k)$ per update instead of $O(T)$, but the gradient is biased: dependencies longer than $k$ steps receive no gradient at all. Gradient clipping, $g \leftarrow g\, \min(1, c / \|g\|)$, fixes exploding gradients (bounded step, direction kept) but does nothing against vanishing; use it always with RNNs (`clip_grad` in `train_loop`).

### LSTM

Hochreiter & Schmidhuber 1997 [S46], forget gate Gers et al. 2000. With $[h_{t-1}, x_t]$ the concatenation and $\sigma$ the logistic function:
$$\begin{aligned}
f_t &= \sigma(W_f [h_{t-1}, x_t] + b_f) && \text{forget gate: what to erase from } c_{t-1}\\
i_t &= \sigma(W_i [h_{t-1}, x_t] + b_i) && \text{input gate: what to write}\\
\tilde c_t &= \tanh(W_c [h_{t-1}, x_t] + b_c) && \text{candidate content}\\
c_t &= f_t \odot c_{t-1} + i_t \odot \tilde c_t && \text{cell state, additive update}\\
o_t &= \sigma(W_o [h_{t-1}, x_t] + b_o) && \text{output gate: what to expose}\\
h_t &= o_t \odot \tanh(c_t)
\end{aligned}$$
Why it carries gradient: $\partial c_t / \partial c_{t-1} = \mathrm{diag}(f_t) + (\text{terms via } h_{t-1})$. Along the cell path the Jacobian product is $\prod_i \mathrm{diag}(f_i)$, no weight matrix and no $\tanh'$ factor; with $f_i \approx 1$ the gradient passes $t - k$ steps essentially unchanged (the "constant error carousel"). The network learns *when* to forget instead of forgetting by default. Practical: initialise $b_f$ to 1-2 so gates start open (Jozefowicz et al. 2015); PyTorch `nn.LSTM` initialises all biases uniformly, set `bias_hh[H:2H]` manually if long memory is needed from the start. Parameters: four gate blocks, each $H(H + F) + H$, total $4\,(H(H+F) + H)$; `nn.LSTM` with its two bias vectors: $4\,(H(H+F) + 2H)$, stored as `weight_ih [4H, F]`, `weight_hh [4H, H]`, `bias_ih [4H]`, `bias_hh [4H]` in gate order $i, f, g(=\tilde c), o$. Goodfellow 10.10.1 [S15].

### GRU

Cho et al. 2014 [S50]:
$$\begin{aligned}
z_t &= \sigma(W_z [h_{t-1}, x_t] + b_z) && \text{update gate}\\
r_t &= \sigma(W_r [h_{t-1}, x_t] + b_r) && \text{reset gate}\\
\tilde h_t &= \tanh(W_h [r_t \odot h_{t-1}, x_t] + b_h) && \text{candidate}\\
h_t &= (1 - z_t) \odot h_{t-1} + z_t \odot \tilde h_t
\end{aligned}$$
One state instead of $(h, c)$; the update gate plays both forget and input gate roles (tied: $f = 1 - z$, $i = z$), the reset gate lets the candidate ignore the past. $\partial h_t / \partial h_{t-1}$ contains $\mathrm{diag}(1 - z_t)$, the same additive-path argument. Three gate blocks: $3\,(H(H+F) + H)$ parameters ($3\,(H(H+F) + 2H)$ in `nn.GRU`), i.e. $25\%$ fewer than an LSTM at equal $H$, similar accuracy on most tasks (Chung et al. 2014); LSTM is slightly better at counting and very long memory.

### Bidirectional and stacked RNNs

Bidirectional (Schuster & Paliwal 1997): one RNN reads $x_1 \to x_T$, a second reads $x_T \to x_1$, outputs are concatenated $[\overrightarrow h_t; \overleftarrow h_t] \in \mathbb R^{2H}$. Every position then sees the whole sequence; only valid when the full input is available before predicting (tagging, encoders), never for autoregressive generation or online processing. `bidirectional=True` doubles the output width and the parameters. Stacked (`num_layers=L`): layer $l$ takes the output sequence of layer $l - 1$ as input; `dropout=p` applies between layers only, not across time. Two or three layers is the usual maximum; deeper needs residual connections. Goodfellow 10.3, 10.5 [S15].

### Sequence task taxonomy

- Many-to-one: sequence in, one output (classification, regression); read $h_T$ (or the state at the true last step under padding), or mean/max-pool the outputs, then a linear head. The adding problem below is this.
- One-to-many: one input, sequence out (image captioning: CNN features as $h_0$, tokens generated step by step).
- Many-to-many aligned: an output per step with the same length (POS tagging, per-frame labelling); loss summed over steps.
- Many-to-many unaligned, seq2seq (Sutskever et al. 2014): encoder RNN compresses $x_{1:T}$ into $c = h_T^{enc}$, decoder RNN generates $y_{1:T'}$ conditioned on $c$ and its own previous output. The single vector $c$ is a bottleneck for long inputs. Attention (Bahdanau et al. 2015 [S49]) replaces it by a per-step context $c_t = \sum_s \alpha_{ts} h^{enc}_s$ with $\alpha_{ts} = \mathrm{softmax}_s(\mathrm{score}(s_{t-1}, h^{enc}_s))$: the decoder looks back at all encoder states with learned soft alignment. Removing the recurrences and keeping only attention (with positional encodings) gives the transformer (Vaswani et al. 2017 [S62]), covered in the next note.

### Teacher forcing, exposure bias, scheduled sampling

Autoregressive models factorise $p(y_{1:T'} \mid x) = \prod_t p(y_t \mid y_{<t}, x)$. Teacher forcing (Williams & Zipser 1989) trains by feeding the *ground truth* $y_{t-1}$ as the decoder input at step $t$, so the loss is the exact negative log-likelihood, every step is conditioned on correct history, and all steps can be computed in one pass. At inference the model is free-running: it feeds its own sampled or argmax $\hat y_{t-1}$. The mismatch is exposure bias: the model never saw its own mistakes during training, so an early error puts it in an unfamiliar state and errors compound over the sequence. Scheduled sampling (Bengio et al. 2015): at each step use the ground truth with probability $\epsilon_i$ and the model's own prediction otherwise, annealing $\epsilon_i$ from 1 toward a floor over training; it reduces the mismatch but is no longer a consistent likelihood objective (Huszár 2015). Other remedies: beam search at decode time, sequence-level losses, or simply more data. Goodfellow 10.2.1 [S15].

### CTC: training on unaligned sequences

Lecture 4 [S4] gives this its own chapter, and it is the loss behind the lecturer's own optical-music-recognition work [S9]. The problem it solves: you have an audio clip and its transcription, or a line image and its text, and you know *what* was said but not *when*. A per-step loss needs a frame-level alignment that you do not have and that is expensive to annotate.

Connectionist temporal classification (Graves et al. 2006 [S48]) removes the need for one. The network emits, per frame $t$, a distribution $y_t$ over the alphabet plus one extra symbol, the **blank** $\varnothing$. A *path* $\pi$ is one symbol per frame. Paths are mapped many-to-one onto label sequences by

$$\mathcal B: \text{squash repeated symbols, then delete blanks},$$

so $a\,a\,\varnothing\,a\,b \mapsto a\,a\,b$ (the blank keeps the two $a$s apart) while $a\,a\,a\,\varnothing\,b \mapsto a\,b$. The blank is what makes the map able to emit repeated labels at all, and it doubles as "nothing happening here". CTC then maximises the total probability of *every* path that produces the label:
$$p(l \mid x) = \sum_{\pi \in \mathcal B^{-1}(l)} \prod_{t=1}^T y_t(\pi_t), \qquad \mathcal L = -\log p(l \mid x).$$

The sum has up to $|A|^T$ terms, so it is computed by dynamic programming over the **extended label** $l' = (\varnothing, l_1, \varnothing, l_2, \dots, l_L, \varnothing)$ of length $S = 2L+1$ — the states a path can occupy. With $\alpha_t(s)$ the total probability of all length-$t$ prefixes ending in state $s$:
$$\alpha_1(1) = y_1(\varnothing), \quad \alpha_1(2) = y_1(l_1), \quad \alpha_1(s>2) = 0,$$
$$\alpha_t(s) = y_t(l'_s)\Big[\alpha_{t-1}(s) + \alpha_{t-1}(s-1) + \mathbb 1[\,l'_s \ne \varnothing \ \wedge\ l'_s \ne l'_{s-2}\,]\;\alpha_{t-1}(s-2)\Big],$$
$$p(l \mid x) = \alpha_T(S) + \alpha_T(S-1).$$

The three terms are the three legal moves: stay, advance one state, or **skip a blank**. The skip is forbidden when $l'_s = l'_{s-2}$, because that blank is the one separating two identical labels and deleting it would merge them. Cost $O(TS)$ instead of $O(|A|^T)$. Implement it in log space with `logsumexp`; the products underflow within a few dozen frames otherwise.

Consequences worth knowing:

- **$T \ge L + (\text{number of adjacent repeats in } l)$**, otherwise $p(l\mid x) = 0$ and the loss is $+\infty$. A CNN front end that downsamples time by 8 can silently make some training targets impossible; `zero_infinity=True` hides this rather than fixing it.
- **CTC assumes conditional independence of the per-frame outputs given $x$.** It therefore has no language model of its own, which is why CTC systems are usually decoded with an external one.
- **Greedy (best-path) decoding — argmax per frame, then $\mathcal B$ — is not the most likely label sequence.** The label's probability is a sum over many paths, so a label with no single dominant path can beat the argmax path's label. `ctc_loss.py` has a three-frame example where every frame's argmax is the blank, yet the empty label has probability $0.4^3 = 0.064$ while the label $[1]$ has $0.243$ — nearly four times more. Prefix beam search, which merges paths as it goes, fixes this.
- The alignment is a by-product: $\arg\max_s \alpha_t(s)\beta_t(s)$ gives one, and CTC's tend to be **peaky** — the model emits each label in one frame and blanks elsewhere.

`src/py/ctc_loss.py` implements the recursion and checks it three ways: against `torch.nn.CTCLoss`, against brute-force enumeration of every path for small $T$, and against two hand-computable cases.

### Padding, packing, masking

Variable-length sequences in one batch: pad to $T_{max}$ with zeros (`torch.nn.utils.rnn.pad_sequence(seqs, batch_first=True)`) and keep a `lengths` tensor. A plain RNN over padded input keeps updating $h$ on the pad steps, so `h_n` is wrong for shorter sequences; for a many-to-one head gather `output[torch.arange(B), lengths - 1]` instead of `output[:, -1]`. Cleaner: `pack_padded_sequence(x, lengths.cpu(), batch_first=True, enforce_sorted=False)` produces a `PackedSequence` that the RNN unrolls only over the valid steps, so `h_n` is the state at each sequence's true end and the backward direction of a bidirectional RNN starts at the true end rather than at pads; `pad_packed_sequence` restores `[B, T, H]`. For per-step losses mask the pads: `CrossEntropyLoss(ignore_index=PAD)` for tokens, or `(loss * mask).sum() / mask.sum()` for regression. In attention models the same information is a key-padding mask.

### The adding problem

Hochreiter & Schmidhuber 1997 [S46] (task 5). Each step has two inputs, $x_t = (v_t, m_t)$ with $v_t \sim U[0, 1]$ and a marker $m_t \in \{0, 1\}$ that is 1 at exactly two positions; the target is $y = \sum_t m_t v_t$, the sum of the two marked values, a many-to-one regression. Solving it requires storing a value when its marker appears and holding it across an arbitrary number of irrelevant steps, i.e. a long-range dependency with no local cue. Baseline: $y$ is the sum of two independent uniforms (triangular on $[0, 2]$, mean 1, variance $2/12 = 1/6$); predicting the constant 1 gives MSE $1/6 \approx 0.167$ and MAE $\mathbb E|y - 1| = 2\int_0^1 (1 - s)\, s\, ds = 1/3$. A model has learned something only when its MAE is well below $0.33$. A plain RNN solves $T \approx 10$-$20$ and fails around $T \gtrsim 50$-$100$; an LSTM solves $T = 1000$ in the original paper. `grad_norm_through_time` makes the mechanism visible: for the plain RNN, $\|\partial L / \partial h_t\|$ decays geometrically as $t$ moves away from $T$; for the LSTM it stays flat.

## Architecture sketch

`SeqModel(cell="lstm", hidden=32)` on `make_adding` data, many-to-one, $F = 2$, $H = 32$:

```
X [B, T, 2]  (batch_first; X[:, :, 0] = value, X[:, :, 1] = marker)
  -> nn.LSTM(2, 32, batch_first=True)
       output [B, T, 32]   h_n [1, B, 32]   c_n [1, B, 32]
  -> h_n[-1]  (or output[:, -1])           -> [B, 32]
  -> nn.Linear(32, 1) -> squeeze(-1)       -> y_hat [B]
  -> MSE(y_hat, y [B])                     -> loss []
step t inside the cell:
  [h_{t-1}, x_t] [B, 34] -> W [128, 34] + b -> gates [B, 4*32] -> split i, f, g, o [B, 32] each
  c_t = f*c_{t-1} + i*tanh(g)   h_t = o*tanh(c_t)
```

Worked example, parameter count for $F = 2$, $H = 32$. One gate block: $H(H + F) + H = 32\cdot34 + 32 = 1{,}120$. LSTM: $4 \cdot 1{,}120 = 4{,}480$; with PyTorch's second bias vector, $4\,(1{,}088 + 64) = 4{,}608$ (check: `weight_ih` $128\times2 = 256$, `weight_hh` $128\times32 = 4{,}096$, `bias_ih` $128$, `bias_hh` $128$). Head: $32 + 1 = 33$. Total `count_params(SeqModel("lstm"))` $= 4{,}641$. GRU: $3\cdot 1{,}152 + 33 = 3{,}489$; RNN: $1{,}152 + 33 = 1{,}185$. Per-step cost is dominated by `weight_hh`: $128 \times 32$ MACs per example, $O(H^2)$, so doubling $H$ quadruples the recurrent compute. Loss sanity value: an untrained model outputs $\approx 0$, so the initial MSE is $\mathbb E[y^2] = \mathrm{Var} + 1 = 7/6 \approx 1.17$; the constant-1 predictor reaches $0.167$; a solved model reaches $< 0.01$.

## Pitfalls

- Loss plateaus at $\approx 0.167$ (MSE) / $0.33$ (MAE) on the adding problem -> the model predicts the mean; the recurrence is not carrying the marked values (vanishing gradient, $T$ too long for the cell) -> switch `cell="rnn"` to `"lstm"`/`"gru"`, open the forget gate bias, shorten $T$ to confirm.
- Loss spikes and NaN after a few hundred steps -> exploding gradient through time -> `clip_grad=1.0` in `train_loop`, lower LR; check with `grad_norm_through_time`.
- `h_n` looks wrong for short sequences in a padded batch -> the RNN kept running over pads -> `pack_padded_sequence`, or gather at `lengths - 1`.
- Shape error `input.size(-1) must be equal to input_size` -> `[T, B, F]` passed to a `batch_first=True` module or vice versa -> pick one layout and assert `X.shape[-1] == F` before the module.
- `h_n` shape `[1, B, H]` fed into `Linear` and the batch dimension disappears -> `h_n` is never batch-first -> use `h_n[-1]` (`[B, H]`) or `output[:, -1]`.
- Bidirectional LSTM performs perfectly on validation but is useless in the deployed streaming setting -> the backward direction reads the future -> unidirectional model for online use; bidirectional only for offline encoders.
- Model trained with teacher forcing generates fluent starts that degrade into repetition -> exposure bias -> scheduled sampling or beam search, and evaluate with free-running decoding during training, not only teacher-forced loss.
- Training is slow on `mps`/GPU despite a tiny model -> $T$ sequential kernel launches per step, the RNN cannot parallelise over time -> larger batch (parallel over $B$), fewer but wider layers, cuDNN-style fused `nn.LSTM` rather than a hand-written cell loop; for long $T$ consider a 1-D CNN or transformer.
- `.detach()` forgotten in truncated BPTT -> the graph grows across chunks, memory climbs until OOM and backward gets slower every chunk -> `h = h.detach()` (both `h` and `c` for LSTM) at each chunk boundary.

## Questions

1. Derive $\partial h_t / \partial h_{t-1}$ for the tanh RNN and give a sufficient condition for vanishing gradients.
<details><summary>Answer</summary>
$h_t = \tanh(a_t)$, $a_t = W_h h_{t-1} + W_x x_t + b$, so $\partial h_t/\partial h_{t-1} = \mathrm{diag}(1 - h_t^2)\, W_h$. Then $\|\partial h_t/\partial h_{t-1}\|_2 \le \|\mathrm{diag}(1 - h_t^2)\|_2 \|W_h\|_2 \le 1\cdot\sigma_{max}(W_h)$, and the product over $t - k$ steps is bounded by $\sigma_{max}(W_h)^{t-k}$. If $\sigma_{max}(W_h) < 1$ (for sigmoid: $< 4$) the gradient of any loss term w.r.t. states $t - k$ steps earlier decays at least geometrically (Pascanu et al. 2013 [S47]). Saturated units make it worse since $1 - h^2 \to 0$.
</details>

2. Why does the LSTM cell state avoid this? Write the relevant Jacobian.
<details><summary>Answer</summary>
$c_t = f_t \odot c_{t-1} + i_t \odot \tilde c_t$ gives $\partial c_t/\partial c_{t-1} = \mathrm{diag}(f_t)$ plus indirect terms through $h_{t-1} = o_{t-1}\odot\tanh(c_{t-1})$. The direct path multiplies by gate values only, elementwise, with no weight matrix and no activation derivative; if the network sets $f \approx 1$ the product $\prod_i \mathrm{diag}(f_i) \approx I$ for any distance, so gradient and information persist. Vanishing becomes a learned decision (close the gate) rather than a consequence of the architecture. Exploding is still possible through the other paths, hence clipping.
</details>

3. Count the parameters of `nn.GRU(input_size=16, hidden_size=64)` and of the equivalent `nn.LSTM`.
<details><summary>Answer</summary>
Per gate block with PyTorch's two biases: $H(H + F) + 2H = 64\cdot 80 + 128 = 5{,}248$. GRU: $3 \cdot 5{,}248 = 15{,}744$. LSTM: $4 \cdot 5{,}248 = 20{,}992$. Textbook counts with one bias: $3\cdot5{,}184 = 15{,}552$ and $4\cdot 5{,}184 = 20{,}736$. Note the $H^2$ term dominates: $F$ barely matters once $H \gg F$.
</details>

4. What does teacher forcing optimise, what is exposure bias, and how would you detect it in the project?
<details><summary>Answer</summary>
Teacher forcing optimises the exact conditional log-likelihood $\sum_t \log p(y_t \mid y_{<t}^{true}, x)$, feeding ground-truth history. At test time the history is the model's own outputs, a distribution it never trained on; errors compound (exposure bias). Detect it by comparing the teacher-forced validation loss (looks fine) with a free-running metric on the same data (e.g. exact-match or edit distance of generated sequences); a large gap between the two, growing with sequence length, is the signature. Mitigate with scheduled sampling, beam search, or shorter generation horizons.
</details>

5. Explain what `pack_padded_sequence` changes compared to running the RNN on the padded tensor, and when you can skip it.
<details><summary>Answer</summary>
Packing reorders the batch by length and stores, for each time step, only the sequences still active, so the RNN performs no computation on pad positions: `h_n` is the state at each sequence's true last step, the backward direction of a bidirectional RNN starts at the true end, and no pad values leak into the state. On the padded tensor the RNN keeps updating through pads, corrupting `h_n` for short sequences. It can be skipped when all sequences have equal length (the adding problem), when you only use per-step outputs with a loss mask and a unidirectional model, or when you gather `output` at `lengths - 1` yourself.
</details>

6. You must classify 20 000 variable-length sensor recordings ($T$ between 50 and 5 000, $F = 6$) on an M3 Pro within the course's compute budget. Which model and training setup, and what is your fallback?
<details><summary>Answer</summary>
Start with a 1-2 layer GRU/LSTM, $H = 64$-$128$, bidirectional (offline classification), packed batches sorted into length buckets to reduce padding, AdamW $10^{-3}$, gradient clipping at 1, mean-pooled outputs plus $h_n$ into the head, and downsample or window the 5 000-step recordings (the recurrence is sequential and $T = 5000$ is slow and hard to train). Fallback: a 1-D CNN with dilations or a small transformer with a length cap, which parallelise over $T$; compare all on the same split with learning curves and the same seed. Check first that a non-sequential baseline (summary statistics + logistic regression) does not already solve the task.
</details>

7. A plain RNN reaches MAE 0.05 on the adding problem at $T = 12$ but 0.33 at $T = 100$; an LSTM reaches 0.05 at both. Explain with the gradient-norm curve you would plot.
<details><summary>Answer</summary>
Plot $\|\partial L/\partial h_t\|$ against $t$ (`grad_norm_through_time`). For the RNN the norm falls geometrically with $T - t$, by a factor $\approx \gamma\sigma_{max}(W_h)$ per step; at $T = 12$ the marked positions still receive usable gradient, at $T = 100$ a marker at $t = 5$ contributes essentially zero, so the model cannot learn to store its value and regresses to the mean (MAE $1/3$). For the LSTM the curve is nearly flat because the cell path multiplies by forget gates near 1, so both marked values get gradient regardless of position.
</details>

8. Why did attention-based seq2seq lead to the transformer? Name the two RNN limitations it removes and the one thing it must add.
<details><summary>Answer</summary>
Attention already gives the decoder direct access to every encoder state, so the fixed-size context bottleneck is gone; the remaining recurrences (i) are sequential in $T$, preventing parallel training on GPUs, and (ii) still route long-range information through $O(T)$ multiplicative steps with the gradient problems above. Replacing them with self-attention makes every position reachable in $O(1)$ steps and the whole layer parallel in $T$; the price is that the model no longer knows positions, so positional encodings must be added, and attention costs $O(T^2)$ (Vaswani et al. 2017 [S62]).
</details>

## Code

`src/py/rnn_sequence.py`: `make_adding(n, T=12, seed=0)` -> `X [n,T,2]` (value in $[0,1]$, marker 0/1 with exactly two 1s), `y [n]` = sum of the two marked values; `SeqModel(cell="lstm"|"gru"|"rnn", hidden=32)` many-to-one regression; `run(steps=400, cell="lstm", T=12, device=None, seed=0)` -> `{"losses", "mae"}`; `grad_norm_through_time(model, X, y)` returns the per-timestep gradient norms of the loss w.r.t. the hidden states, which shows the vanishing gradient for `cell="rnn"` versus the flat curve for the LSTM (the `__main__` also probes untrained cells at $T=60$, where the ratio $\|\partial L/\partial h_0\| / \|\partial L/\partial h_{59}\|$ is orders of magnitude smaller for the tanh RNN). `python src/py/rnn_sequence.py` trains for a few seconds and prints the MAE (compare against the constant-predictor baseline $1/3$). `src/py/test_rnn_sequence.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)`. Training uses `common.train_loop` with `clip_grad` set.

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016) [S15]: ch. 10 (sequence modelling: 10.2 RNNs and teacher forcing, 10.2.2 BPTT, 10.3 bidirectional, 10.4 encoder-decoder, 10.7 long-term dependencies, 10.10 LSTM and GRU, 10.11 clipping, 10.12 attention).
- Elman 1990, finding structure in time. Werbos 1990, BPTT. Williams & Zipser 1989, teacher forcing. Bengio, Simard, Frasconi 1994, learning long-term dependencies is difficult. Pascanu, Mikolov, Bengio 2013 [S47], on the difficulty of training RNNs (clipping, spectral-norm argument).
- Hochreiter & Schmidhuber 1997 [S46], LSTM (adding problem, task 5). Gers, Schmidhuber, Cummins 2000, forget gate. Jozefowicz et al. 2015, empirical exploration of recurrent architectures (forget bias). Cho et al. 2014 [S50], GRU / encoder-decoder. Chung et al. 2014, empirical evaluation of gated RNNs. Schuster & Paliwal 1997, bidirectional RNNs. Gal & Ghahramani 2016, dropout in RNNs.
- Sutskever, Vinyals, Le 2014, seq2seq. Bahdanau, Cho, Bengio 2015 [S49], attention. Bengio et al. 2015, scheduled sampling. Huszár 2015, critique of scheduled sampling. Vaswani et al. 2017 [S62], transformer.
- Graves, Fernández, Gomez & Schmidhuber 2006 [S48], *Connectionist temporal classification: labelling unsegmented sequence data with recurrent neural networks*, ICML. Hannun 2017, *Sequence modeling with CTC*, Distill — the explainer on **Lecture 4's own reading list** [S4].
- **Lecture 4** [S4] is the lecture this note covers; its chapter list (modelling sequences with CNNs, memory, unfolding, parameter sharing, BPTT, vanishing/exploding gradients, clipping, RNN variations, teacher forcing, vector-to-sequence, bidirectional, encoder-decoder, LSTM/GRU, short-term prediction, CNN+RNN for OCR, **CTC**, translation with attention, "should you still use RNNs?") is the order of this note.
