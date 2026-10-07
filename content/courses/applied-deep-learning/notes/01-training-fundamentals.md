# 01 Training fundamentals

Training a neural network means minimising an empirical risk over parameters $\theta$ by stochastic gradient methods, where the gradient is computed by reverse-mode automatic differentiation (backprop). Everything else in this note (optimiser variants, learning-rate schedules, initialisation, normalisation, dropout, augmentation) exists to make that minimisation converge fast and to make the minimiser generalise from the training set to unseen data. These pieces are shared by every later topic (CNNs, RNNs, transformers, GANs, ...), so the project's training loop in `src/py/common.py` is written once and reused. The diagnostics section is what you actually look at when a run misbehaves.

## Concepts

### Empirical risk and loss functions

Dataset $\{(x_i, y_i)\}_{i=1}^N$ i.i.d. from $p_{data}$. True risk $R(\theta) = \mathbb E_{(x,y)\sim p_{data}}[\ell(f_\theta(x), y)]$ is unknown; we minimise the empirical risk
$$\hat R(\theta) = \frac1N \sum_{i=1}^N \ell(f_\theta(x_i), y_i), \qquad \nabla_\theta \hat R \approx \frac1B \sum_{i \in \mathcal B} \nabla_\theta \ell_i$$
where a *minibatch* $\mathcal B$ of size $B$ gives an unbiased gradient estimate with variance $\propto 1/B$. One pass over the data is an *epoch*, one minibatch update a *step*. Generalisation gap $= R - \hat R$ is what regularisation controls (Goodfellow ch. 5.2, 8.1 [S15]).

Losses are negative log-likelihoods of an output distribution (Goodfellow 6.2 [S15]):

- MSE, $\ell = \frac12 \|\hat y - y\|^2$: Gaussian likelihood with fixed variance; $\partial \ell / \partial \hat y = \hat y - y$. Regression. Sensitive to outliers (Huber/L1 alternatives).
- Softmax cross-entropy: logits $z \in \mathbb R^K$, $p_k = e^{z_k} / \sum_j e^{z_j}$, one-hot target $y$ with class $c$:
  $$\ell = -\sum_k y_k \log p_k = -z_c + \log \sum_j e^{z_j}, \qquad \frac{\partial \ell}{\partial z_k} = \frac{e^{z_k}}{\sum_j e^{z_j}} - y_k = p_k - y_k.$$
  The derivation is one line: $\partial_{z_k} \log\sum_j e^{z_j} = p_k$. The gradient is bounded in $[-1, 1]$ per logit and does not saturate the way MSE-on-softmax does (Goodfellow 6.2.2.3 [S15]). Numerically, $\log\sum_j e^{z_j} = m + \log\sum_j e^{z_j - m}$ with $m = \max_j z_j$; PyTorch `nn.CrossEntropyLoss` takes raw logits and does `log_softmax` + `nll_loss` in one fused, stable op. Never put a softmax layer before it.
- Binary cross-entropy: $\ell = -[y \log\sigma(z) + (1-y)\log(1-\sigma(z))]$, $\partial \ell/\partial z = \sigma(z) - y$. Use `nn.BCEWithLogitsLoss` (stable), not `Sigmoid` + `BCELoss`. Multi-label = $K$ independent BCEs.
- Label smoothing (Szegedy et al. 2016): replace $y$ by $y^{ls} = (1-\epsilon) y + \epsilon / K$. Gradient becomes $p_k - y^{ls}_k$, which vanishes at $p_c = 1 - \epsilon + \epsilon/K < 1$: the logit gap cannot grow without bound, weights stay smaller, calibration improves. $\epsilon = 0.1$ typical. `nn.CrossEntropyLoss(label_smoothing=0.1)`.

### Backprop as reverse-mode automatic differentiation

A forward pass builds a directed acyclic *computational graph*: nodes are ops, edges are tensors, leaves are inputs and parameters, the root is the scalar loss $L$. Reverse-mode AD computes the adjoint $\bar v := \partial L / \partial v$ for every node by walking the graph in reverse topological order: for a node $v = f(u)$,
$$\bar u \mathrel{+}= J_f(u)^\top \bar v \qquad \text{(vector-Jacobian product, VJP)}.$$
This is the chain rule in Jacobian form, $\partial L / \partial u = (\partial v/\partial u)^\top \partial L/\partial v$, accumulated ($+=$) because $u$ may feed several nodes. The Jacobian is never materialised; each op implements its VJP directly. For $Y = X W$ ($X \in \mathbb R^{B\times n}$, $W \in \mathbb R^{n \times m}$): $\bar X = \bar Y W^\top$, $\bar W = X^\top \bar Y$. For elementwise $\phi$: $\bar u = \phi'(u) \odot \bar v$.

Cost: one reverse pass costs a small constant times the forward pass (about $2$-$3\times$ FLOPs) and yields $\partial L/\partial\theta$ for *all* $n$ parameters at once. Forward-mode (JVP) would need $n$ passes. Memory: all intermediate activations must be stored until the backward pass, $O(\text{depth} \times \text{activation size})$; this, not the parameters, is what limits batch size on a GPU (gradient checkpointing trades recomputation for memory). Goodfellow 6.5 [S15]; Baydin et al. 2018 [S21].

PyTorch autograd: tensors with `requires_grad=True` (parameters via `nn.Parameter`) record every op in `grad_fn`; `loss.backward()` runs the reverse pass and *accumulates* into `.grad` (hence `optimizer.zero_grad()` each step); `with torch.no_grad():` disables recording for evaluation/inference (no graph, no memory); `.detach()` cuts the graph at one tensor (used in truncated BPTT, target networks, GAN discriminator steps). `.item()` on a scalar copies to CPU and syncs the device; do it once per step for logging, not inside the graph.

### Optimisers

Let $g_t = \nabla_\theta \hat R_{\mathcal B_t}(\theta_t)$, learning rate $\eta$. Goodfellow ch. 8.3-8.5 [S15].

- SGD: $\theta_{t+1} = \theta_t - \eta g_t$. Converges for convex $L$-smooth objectives with $\eta < 2/L$; noise floor $\propto \eta \sigma^2 / B$.
- Momentum (Polyak 1964): $v_{t+1} = \mu v_t + g_t$, $\theta_{t+1} = \theta_t - \eta v_{t+1}$. Steady-state step for constant gradient: $\eta g / (1-\mu)$, i.e. $\mu = 0.9$ is a $10\times$ effective LR along consistent directions and averages out oscillations across ravines.
- Nesterov (Sutskever et al. 2013): gradient evaluated at the look-ahead point $\theta_t - \eta\mu v_t$; slightly better damping. `SGD(momentum=0.9, nesterov=True)`.
- RMSProp (Hinton 2012): $s_{t+1} = \rho s_t + (1-\rho) g_t^2$, $\theta_{t+1} = \theta_t - \eta\, g_t / (\sqrt{s_{t+1}} + \epsilon)$ (elementwise). Per-coordinate step size normalised by recent gradient magnitude.
- Adam (Kingma & Ba 2015 [S22]): momentum on the first moment plus RMSProp on the second, with bias correction:
  $$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \quad v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2, \quad \hat m_t = \frac{m_t}{1-\beta_1^t}, \quad \hat v_t = \frac{v_t}{1-\beta_2^t}, \quad \theta_{t+1} = \theta_t - \eta\, \frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon}.$$
  Bias correction: with $m_0 = 0$, $m_t = (1-\beta_1)\sum_{i=1}^t \beta_1^{t-i} g_i$, so for stationary $g$, $\mathbb E[m_t] = (1-\beta_1^t)\,\mathbb E[g]$; dividing by $1 - \beta_1^t$ removes the zero-init bias (same for $v_t$ with $\beta_2$). Without it the first step is $\eta\, m_1/\sqrt{v_1} = \eta\,(0.1 g_1)/(\sqrt{10^{-3}}\,|g_1|) = \eta/\sqrt{0.1} \approx 3.16\,\eta$ instead of $\eta$, i.e. **about $3\times$ too large, and it stays inflated for the $\sim 1/(1-\beta_2) = 1000$ steps it takes $\beta_2^t$ to decay** (the factor is computed in `test_shape_formulas.py::test_adam_bias_correction_factor`; question 3 below derives it). Defaults $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$, $\eta = 10^{-3}$. The update magnitude per coordinate is roughly bounded by $\eta$, independent of gradient scale (invariant to rescaling the loss).
- AdamW (Loshchilov & Hutter 2019 [S23]): L2 penalty $\frac\lambda2\|\theta\|^2$ in the loss gives $g_t + \lambda\theta$, which Adam then divides by $\sqrt{\hat v_t}$, so coordinates with large gradient history are barely decayed. Decoupled weight decay applies the shrinkage outside the adaptive step:
  $$\theta_{t+1} = \theta_t - \eta\Big(\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon} + \lambda \theta_t\Big).$$
  `torch.optim.AdamW(weight_decay=0.01)` (note: `Adam(weight_decay=...)` is the coupled L2 version). Exclude biases and norm affine parameters from decay via parameter groups.

Rule of thumb: AdamW $\eta \in [10^{-4}, 3\cdot 10^{-3}]$ works out of the box for almost everything; SGD+momentum with a tuned schedule still wins on ImageNet-style CNNs by a little.

### Learning-rate schedules

- Step: $\eta_t = \eta_0 \gamma^{\lfloor t / s \rfloor}$ (`StepLR`, `MultiStepLR`).
- Cosine annealing (Loshchilov & Hutter 2017, SGDR [S24]): $\eta_t = \eta_{min} + \frac12(\eta_0 - \eta_{min})(1 + \cos(\pi t/T))$; smooth decay to $\approx 0$ at the last step $T$ (`CosineAnnealingLR(T_max=steps)`). Optionally with warm restarts.
- Linear warmup: $\eta_t = \eta_0\, t/T_w$ for $t < T_w$ (typically $T_w \approx 1$-$5\%$ of steps), then any decay. `LinearLR` chained with `SequentialLR`, or `OneCycleLR`.
- One-cycle (Smith 2018): warm up to $\eta_{max}$ over the first $\sim 30\%$, anneal to $\approx 0$; momentum cycled inversely. Allows a larger $\eta_{max}$ than constant LR.
- Reduce-on-plateau: multiply $\eta$ by `factor` when the validation metric has not improved for `patience` epochs (`ReduceLROnPlateau`, call `scheduler.step(val_loss)`).

Why warmup helps Adam: $\hat v_t$ after few steps is an average of few samples; its variance is large, and coordinates that happened to see small gradients get a huge $1/\sqrt{\hat v_t}$ and take destructive steps in the sharp early loss landscape (Liu et al. 2020, RAdam analysis). Keeping $\eta$ small until $\hat v$ has seen $\sim 1/(1-\beta_2) = 1000$ samples avoids this. Essential for transformers and large batches, harmless elsewhere. Ordering: `optimizer.step()` then `scheduler.step()`.

### Initialisation

Linear layer $y = W x$, $W \in \mathbb R^{n_{out}\times n_{in}}$, entries i.i.d. with mean 0 and variance $\sigma^2$, inputs i.i.d. with mean 0 and variance $q$. Then $\mathrm{Var}(y_j) = n_{in} \sigma^2 q$. Backward: $\bar x = W^\top \bar y$ gives $\mathrm{Var}(\bar x_i) = n_{out}\sigma^2 \mathrm{Var}(\bar y)$. Over $L$ layers the forward variance scales as $(n_{in}\sigma^2)^L$: exponential blow-up or vanishing unless the factor is $1$.

- Xavier/Glorot (Glorot & Bengio 2010 [S26]): compromise between $\sigma^2 = 1/n_{in}$ (forward) and $1/n_{out}$ (backward): $\sigma^2 = 2/(n_{in} + n_{out})$; uniform version $U(\pm\sqrt{6/(n_{in}+n_{out})})$. Derived for linear/tanh (tanh is linear near 0).
- Kaiming/He (He et al. 2015 [S27]): ReLU zeroes half the pre-activations; for symmetric $z$, $\mathbb E[\mathrm{relu}(z)^2] = \frac12 \mathbb E[z^2]$, so each layer halves the variance and the correction is $\sigma^2 = 2/n_{in}$ (`kaiming_normal_(mode="fan_in", nonlinearity="relu")`). For a conv, $n_{in} = k^2 C_{in}$.
- Zero (or any constant) init fails by symmetry: every unit in a layer computes the same output and receives the same gradient, so they stay identical forever and the layer has effective width 1. With ReLU and $W = 0$ the gradient is also exactly zero. Biases may be zero. Random init breaks the symmetry; the scale sets whether signal survives depth.
- PyTorch defaults: `nn.Linear`/`nn.Conv2d` use `kaiming_uniform_(a=sqrt(5))`, i.e. $U(\pm 1/\sqrt{n_{in}})$, variance $1/(3 n_{in})$, smaller than He. Fine with BatchNorm; for deep plain ReLU nets set He init explicitly. Goodfellow 8.4 [S15].

### Batch normalisation

Ioffe & Szegedy 2015 [S28]. For each feature (each channel in a conv net, statistics over $B \times H \times W$), per minibatch:
$$\mu_B = \frac1B \sum_i x_i, \quad \sigma_B^2 = \frac1B \sum_i (x_i - \mu_B)^2, \quad \hat x_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat x_i + \beta,$$
with learned $\gamma, \beta$ per feature. Train mode uses batch statistics (and backprop goes through $\mu_B, \sigma_B$, coupling the examples of a batch). Running averages $\mu_{run} \leftarrow (1-m)\mu_{run} + m\,\mu_B$ ($m = 0.1$ in PyTorch, unbiased variance) are stored as buffers and used in eval mode, so inference is a fixed affine map per feature (can be folded into the preceding conv). Consequences:

- Scale invariance $\mathrm{BN}(a W x) = \mathrm{BN}(W x)$: the layer before BN needs no bias (`bias=False`), and weight decay on $W$ acts by shrinking $\|W\|$, which raises the effective learning rate rather than regularising directly.
- Allows $\sim 10\times$ larger LR, reduces sensitivity to init, adds noise (mild regulariser). The original "internal covariate shift" explanation is not the mechanism; smoothing of the loss landscape is (Santurkar et al. 2018 [S29]).
- Batch-size interaction: $B < 16$ gives noisy statistics and a train/eval mismatch; $B = 1$ is degenerate ($\sigma_B = 0$). Fix: GroupNorm (Wu & He 2018) or freeze BN in eval mode when fine-tuning with tiny batches.
- Layer norm (Ba et al. 2016 [S30]) normalises over the feature dimension of each example separately: no batch dependence, identical train/eval behaviour, works for $B = 1$ and for variable-length sequences. Standard in RNNs and transformers; BN standard in CNNs.

### Dropout

Srivastava et al. 2014 [S31]. Training: $\tilde h = m \odot h$ with $m_i \sim \mathrm{Bernoulli}(1-p)$ i.i.d. per unit per example. Inverted dropout divides by the keep probability, $\tilde h = m \odot h / (1-p)$, so $\mathbb E[\tilde h] = h$ and the test-time forward pass is the identity (no rescaling needed). `nn.Dropout(p)` is inverted; it is active in `model.train()` and a no-op in `model.eval()`, exactly like BN switches statistics. Interpretation: trains an exponential ensemble of $2^n$ weight-sharing subnetworks; the test network approximates the geometric-mean ensemble (exact for a single softmax layer, Goodfellow 7.12). Typical $p = 0.5$ for wide FC layers, $0.1$-$0.3$ elsewhere; rarely combined with BN in conv stacks (variance shift); in RNNs only on non-recurrent connections (or the same mask at every step, Gal & Ghahramani 2016).

### Data augmentation as prior knowledge

A transformation $T$ with $p(y \mid T x) = p(y \mid x)$ (flip, small translation, noise, colour jitter for natural images) encodes an invariance the model would otherwise have to learn from data; applying random $T$ at training time is equivalent to enlarging the dataset with correctly labelled examples, i.e. a regulariser that reduces variance without adding bias, provided the invariance really holds (a vertical flip is wrong for digits, a horizontal flip is wrong for text). Apply on the training split only, resample every epoch, transform the label consistently for structured targets (masks, boxes, keypoints). Goodfellow 7.4 [S15].

Lecture 9 [S4] devotes chapters to the non-image modalities, which matter because the course's project topics include audio and text [S12]:

- **Images**: geometric (crop, flip, small rotation), photometric (brightness, contrast, colour jitter), and occlusion-style — **cutout** (DeVries & Taylor 2017 [S33]) masks out a random square, which forces the model to use the whole object rather than one discriminative patch; random erasing and CutMix are variants.
- **Audio**: waveform-level (time stretch, pitch shift, added background noise, room impulse responses) and spectrogram-level. **SpecAugment** (Park et al. 2019 [S36]) is the standard one and is deliberately crude: on the log-mel spectrogram it applies time warping, masks a block of consecutive **frequency** channels, and masks a block of consecutive **time** steps. It costs nothing (no re-synthesis) and was worth several points of word error rate on LibriSpeech.
- **Text**: **EDA** (Wei & Zou 2019 [S37]) — synonym replacement, random insertion, random swap, random deletion, each applied to a small fraction of tokens. It helps most on small datasets and can hurt when the label depends on exact wording (negation, sentiment with "not"). Back-translation is the stronger and more expensive option.

### Adversarial examples and adversarial training

A trained network can be moved across a decision boundary by a perturbation far below the level a human would notice. The **fast gradient sign method** (Goodfellow, Shlens & Szegedy 2015 [S34]) is one step in the direction that most increases the loss, clipped to an $\ell_\infty$ ball:
$$x_{adv} = x + \epsilon\,\mathrm{sign}\big(\nabla_x \ell(f_\theta(x), y)\big).$$
The sign is the point: it uses the full budget $\epsilon$ in every coordinate, so the perturbation has $\ell_\infty$ norm exactly $\epsilon$ and $\ell_2$ norm $\epsilon\sqrt D$ — which is large in aggregate even when each pixel moves imperceptibly. Their explanation is that networks are *too linear*, not too nonlinear: a locally linear model with weights $w$ suffers a logit change $\epsilon\|w\|_1$, which grows with dimension. Iterated versions (PGD) are stronger; the **one-pixel attack** (Su et al. 2017 [S35]) shows the opposite extreme, changing a single pixel by a large amount and still flipping many CIFAR predictions.

**Adversarial training** adds $x_{adv}$ to each minibatch (or trains on $\max_{\|\delta\|\le\epsilon} \ell(f(x+\delta), y)$). It buys robustness within the threat model it trains against and usually costs a little clean accuracy; it is not a general defence. For the project the practical takeaway is diagnostic rather than defensive: if a few-$\epsilon$ perturbation destroys your accuracy, the model is keying on fragile, non-semantic features, which is worth a sentence in the report and cross-references to note 08 on explanations.

### Stochastic weight averaging

SWA (Izmailov et al. 2018 [S32]): after the model has converged, continue training with a constant or cyclic learning rate and average the weights visited, $\theta_{SWA} = \frac1n\sum_i \theta_i$. SGD with a high LR bounces around the rim of a wide flat basin rather than settling in it; averaging the iterates lands nearer the centre, which generalises better than any single iterate. It costs one extra copy of the weights and nothing else. One catch: the averaged weights have never had BatchNorm statistics computed for them, so you must do one extra pass over the training data with `torch.optim.swa_utils.update_bn` before evaluating. `AveragedModel` and `SWALR` implement it.

Exponential moving averages of the weights (EMA) are the same idea with a decay, and are standard in generative models (note 05) for the same reason.

### Overfitting diagnostics

- Splits: train (fit $\theta$), validation (choose hyperparameters, early stopping, model selection), test (touched once, at the end). Split by *group* when examples are correlated (same subject, same time window), otherwise the validation score is optimistic.
- Learning curves: plot train and validation loss (and the metric) against steps. Both high and close: underfitting (high bias) -> bigger model, longer training, higher LR. Train low and val high: overfitting (high variance) -> more data/augmentation, weight decay, dropout, smaller model, early stopping. For squared loss, $\mathbb E[(\hat f(x) - y)^2] = \mathrm{Bias}^2 + \mathrm{Var} + \sigma^2_{noise}$ (Goodfellow 5.4.4 [S15]).
- Early stopping: keep the checkpoint with the best validation metric; for a linear model with quadratic loss it is equivalent to L2 regularisation with $\lambda \propto 1/(\eta \tau)$ (Goodfellow 7.8 [S15]).
- "Loss goes down but accuracy does not": (i) *validation* loss rises while validation accuracy is flat or still rising: the network is becoming overconfident on the examples it gets wrong (log-loss is unbounded per example) while the argmax on the rest is unchanged; a calibration problem, fix with label smoothing/weight decay/early stopping on the metric, not the loss. (ii) *Training* loss decreases from $\ln K$ but accuracy stays at chance: the model is only learning the class prior (shrinking logits toward the marginal), inputs carry no usable signal for it yet: check the label pipeline (shuffled labels, wrong `y` dtype, off-by-one classes), input normalisation, LR (too high: loss plateaus just below $\ln K$).
- Gradient norm clipping (Pascanu et al. 2013 [S47]): $g \leftarrow g \cdot \min(1, c/\|g\|_2)$, `torch.nn.utils.clip_grad_norm_(model.parameters(), c)` after `backward()` and before `step()` (`train_loop(..., clip_grad=c)`). Keeps the direction, bounds the step; needed for RNNs and transformers; logging $\|g\|$ per step is the cheapest diagnostic for instability (spikes precede NaN).

## Architecture sketch

Two-layer MLP classifier, batch $B$, input dim $D$, hidden $H$, classes $K$:

```
x  [B, D] --(W1 [D, H], b1 [H])--> z1 [B, H] --ReLU--> h [B, H] --(W2 [H, K], b2 [K])--> z [B, K]
z  [B, K], y [B] (int64 class ids) --softmax + cross-entropy, mean over B--> L  []

backward (adjoints, same shapes as the forward tensors):
  dz  = (softmax(z) - onehot(y)) / B      [B, K]
  dW2 = h^T dz                            [H, K]      db2 = sum_B dz     [K]
  dh  = dz W2^T                           [B, H]
  dz1 = dh * 1[z1 > 0]                    [B, H]
  dW1 = x^T dz1                           [D, H]      db1 = sum_B dz1    [H]
```

The four lines of a PyTorch training step (`step_fn` in `train_loop` wraps the middle two):

```python
optimizer.zero_grad()                 # .grad accumulates, so clear it
loss = loss_fn(model(x), y)           # forward, builds the graph
loss.backward()                       # reverse-mode AD, fills .grad
optimizer.step()                      # theta <- theta - eta * f(.grad)
```

Worked example. $D = 784$, $H = 128$, $K = 10$: parameters $784\cdot128 + 128 + 128\cdot10 + 10 = 101{,}770$. Loss at a random init that outputs near-uniform probabilities: $-\log(1/10) = \ln 10 = 2.303$; a training loss starting far above this means the logits are too large at init (wrong scale). Cross-entropy for one example with logits $z = (2, 0, -1)$ and $y = 0$: $e^z = (7.389, 1, 0.368)$, sum $8.757$, $p = (0.844, 0.114, 0.042)$, $\ell = -\ln 0.844 = 0.170$, $\partial\ell/\partial z = p - y = (-0.156, 0.114, 0.042)$ (sums to 0, as it must, since softmax is shift-invariant).

## Pitfalls

- Loss constant at exactly $\ln K$ from step 0 -> gradient is zero or never reaches the parameters -> check `requires_grad`, that `optimizer` was built from `model.parameters()` after the model was moved to the device, and that `zero_grad`/`backward`/`step` all run.
- Loss decreases per epoch but jumps at each epoch boundary -> `.grad` never cleared, or the data loader is not reshuffled -> `optimizer.zero_grad()` every step, `shuffle=True`.
- NaN after a few hundred steps -> LR too high for Adam without warmup, or an unstable loss (`log(softmax)` by hand, `BCELoss` on sigmoids) -> use the `*WithLogits` / `CrossEntropyLoss` fused versions, add warmup, clip gradient norm, log $\|g\|$.
- Validation accuracy much worse than training accuracy even at epoch 1 -> `model.eval()` missing (dropout active, BN using batch statistics of a batch of 1) or validation data normalised with different statistics -> same preprocessing for both, `model.eval()` + `torch.no_grad()` in the eval loop, `model.train()` afterwards.
- Training works on CPU but is slower on `mps` -> tiny model and many small kernel launches, or `.item()` syncs in the inner loop -> batch larger, log every `log_every` steps only; keep the CPU path as a fallback (`get_device()`).
- Same script gives different numbers per run -> unseeded RNGs (Python, NumPy, torch, the device) and nondeterministic kernels -> `seed_all(seed)` at the top, and compare loss *curves*, not single values, since some ops remain nondeterministic on GPU/MPS.
- Weight decay "does nothing" with Adam -> coupled L2 is normalised away by $\sqrt{\hat v}$ -> `AdamW`, and exclude biases and norm parameters from the decay group.
- Cosine schedule with the wrong `T_max` -> LR goes to 0 at a third of training, or never decays -> set `T_max` to the total number of *steps* if you call `scheduler.step()` per step, epochs if per epoch; plot the LR once.
- Overfits a 100-sample subset fine, but not the full set -> capacity is fine, the data pipeline for the full set differs (augmentation too strong, label misalignment after shuffling `X` and `y` separately) -> augment only train, shuffle indices once and index both tensors with them.

## Questions

1. Derive $\partial \ell / \partial z$ for softmax cross-entropy and explain why it is preferred over MSE on top of a softmax.
<details><summary>Answer</summary>
$\ell = -z_c + \log\sum_j e^{z_j}$; $\partial_{z_k}\ell = -\delta_{kc} + e^{z_k}/\sum_j e^{z_j} = p_k - y_k$. With MSE on $p$, the gradient carries a factor $\partial p/\partial z$ that is $\approx 0$ whenever the softmax is saturated, including when it is confidently wrong, so learning stalls; cross-entropy's gradient stays $O(1)$ as long as $p_c < 1$, and its log undoes the exponential of the softmax (Goodfellow 6.2.2.3).
</details>

2. Why does reverse-mode AD cost $O(1)$ forward passes for a gradient with $10^6$ parameters, and what is the price?
<details><summary>Answer</summary>
Reverse mode propagates one adjoint vector $\bar v = \partial L/\partial v$ per node from the scalar output back to all leaves; each op contributes one VJP whose cost is comparable to its forward cost, so total work is a constant factor of the forward pass regardless of the number of inputs. Forward mode propagates one tangent per *input* direction and would need $10^6$ passes. The price is memory: every intermediate activation needed by a VJP stays alive until the reverse pass reaches it, $O(\text{depth}\times\text{activation size})$.
</details>

3. Show that Adam's bias correction is exactly $1/(1-\beta^t)$ and estimate the damage of omitting it at $t = 1$ with $\beta_2 = 0.999$.
<details><summary>Answer</summary>
Unrolling $m_t = \beta m_{t-1} + (1-\beta) g_t$ with $m_0 = 0$ gives $m_t = (1-\beta)\sum_{i=1}^t \beta^{t-i} g_i$; for stationary $g$ with mean $\bar g$, $\mathbb E[m_t] = (1-\beta)\bar g \sum_{i=0}^{t-1}\beta^i = (1-\beta^t)\bar g$. At $t = 1$, $v_1 = 0.001\, g_1^2$, so $\sqrt{v_1} = 0.032\,|g_1|$ and the uncorrected step $\eta\, m_1/\sqrt{v_1} = \eta\cdot 0.1\,g_1 / (0.032|g_1|) \approx 3\eta$; with both corrections the step is $\eta\, g_1/|g_1| = \eta$. Without correction the early second-moment estimate is far too small and steps are inflated until $\beta_2^t$ decays, i.e. for $\sim 1000$ steps.
</details>

4. Derive the He initialisation variance for a ReLU network and explain what breaks if all weights start at zero.
<details><summary>Answer</summary>
For $y = Wx$ with i.i.d. zero-mean weights of variance $\sigma^2$ and inputs of variance $q$, $\mathrm{Var}(y_j) = n_{in}\sigma^2 q$. After ReLU, for symmetric $y$, $\mathbb E[\mathrm{relu}(y)^2] = \frac12\mathbb E[y^2]$, so the second moment passed to the next layer is $\frac12 n_{in}\sigma^2 q$; requiring it to equal $q$ gives $\sigma^2 = 2/n_{in}$. At $W = 0$ all units of a layer compute identical outputs and receive identical gradients (symmetry never broken), and with ReLU the hidden activations and thus all weight gradients are exactly zero, so nothing moves.
</details>

5. Batch norm: write the train-mode and eval-mode computations and explain why a model that trains well can evaluate at chance.
<details><summary>Answer</summary>
Train: $\hat x = (x - \mu_B)/\sqrt{\sigma_B^2 + \epsilon}$ with batch statistics, running buffers updated by EMA. Eval: $\hat x = (x - \mu_{run})/\sqrt{\sigma_{run}^2 + \epsilon}$. Chance-level eval happens when the running statistics do not match the data: too few training steps for the EMA (momentum 0.1, needs $\gtrsim 50$ steps), batches so small that $\sigma_B$ is noisy, or a train/eval preprocessing mismatch. Conversely forgetting `model.eval()` evaluates with the statistics of the evaluation batch, which for $B = 1$ maps every input to $\hat x = 0$.
</details>

6. Validation loss has been rising for 10 epochs but validation accuracy is still creeping up. Are you overfitting? What do you do in the project?
<details><summary>Answer</summary>
Partly: the model is getting more confident, and on the examples it misclassifies the per-example log-loss grows without bound, which dominates the mean loss although the argmax decisions (accuracy) still improve. Decision quality is not yet degrading. In the project: early-stop on the metric you report (accuracy/MAE), not on the loss; add label smoothing or weight decay to limit logit growth; report calibration if probabilities matter; and keep the best-metric checkpoint rather than the last.
</details>

7. Which parameters should not receive weight decay and why? How is this expressed in PyTorch?
<details><summary>Answer</summary>
Biases and the affine parameters $\gamma, \beta$ of BN/LN: decaying them pulls the output distribution toward zero mean/unit scale for no regularisation benefit (they are $O(\text{width})$ parameters, not $O(\text{width}^2)$, so they do not drive overfitting), and for weights feeding a BN layer decay only changes the effective LR. Build two parameter groups: `AdamW([{"params": decay, "weight_decay": 0.01}, {"params": no_decay, "weight_decay": 0.0}], lr=...)`, selecting by `p.ndim < 2` for the no-decay group.
</details>

8. You have 2 000 labelled training examples and a training budget of a few minutes on an M3 Pro. List, in order, what you would try to reduce the train/val gap.
<details><summary>Answer</summary>
(1) Sanity: shuffle labels once and confirm the model then cannot learn (pipeline check). (2) Augmentation encoding the true invariances of the data. (3) Weight decay via AdamW and early stopping on the validation metric. (4) Transfer learning from a pretrained backbone if the domain allows (see note 02). (5) Smaller model or dropout on the head. (6) Only then more data or a different architecture. Each step: change one thing, compare learning curves under the same seed.
</details>

## Code

`src/py/common.py`: `get_device()` (mps if available, else cpu), `seed_all(seed)`, `train_loop(step_fn, optimizer, steps, log_every=0, scheduler=None, clip_grad=None)` returns the list of per-step losses (`step_fn` returns the loss tensor; the loop does `zero_grad`, `backward`, optional `clip_grad_norm_` to `clip_grad`, `step`, and `scheduler.step()` if given), `Timer` context manager, `loss_decreased(losses, frac=0.1)` (mean of the last 10% below the mean of the first 10%), `count_params(model, trainable_only=False)`.

Concrete full loop with AdamW and a one-cycle schedule (`OneCycleLR`: warmup then cosine decay): `src/py/cnn_shapes.py`, `run(steps=300, device=None, seed=0)` -> `{"losses", "accuracy", "model"}`. `python src/py/cnn_shapes.py` trains for a few seconds and prints the accuracy; `src/py/test_cnn_shapes.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)`. Run from this course folder with `uv run python` (repo venv).

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016) [S15]: ch. 5 (ML basics, bias-variance 5.4), ch. 6 (feedforward nets, losses 6.2, backprop 6.5), ch. 7 (regularisation: 7.4 augmentation, 7.8 early stopping, 7.12 dropout), ch. 8 (optimisation: 8.3-8.5 SGD/momentum/adaptive, 8.4 init, 8.7.1 batch norm).
- Rumelhart, Hinton, Williams 1986 [S20], backpropagation. Baydin et al. 2018 [S21], AD survey.
- Kingma & Ba 2015 [S22], Adam. Loshchilov & Hutter 2019 [S23], AdamW. Loshchilov & Hutter 2017 [S24], SGDR (cosine). Ruder 2016 [S25], optimiser survey. Smith 2018, one-cycle. Liu et al. 2020, RAdam (warmup analysis). Sutskever et al. 2013, Nesterov momentum in DL.
- Glorot & Bengio 2010 [S26], Xavier init. He et al. 2015 [S27], He init and PReLU.
- Ioffe & Szegedy 2015 [S28], batch norm. Santurkar et al. 2018 [S29], how BN helps. Ba et al. 2016 [S30], layer norm. Wu & He 2018, group norm.
- Srivastava et al. 2014 [S31], dropout. Gal & Ghahramani 2016, dropout in RNNs. Szegedy et al. 2016, label smoothing (Inception-v3). Pascanu et al. 2013 [S47], gradient clipping.
- **Lecture 2** [S4] (neural networks, optimisation, backpropagation) and **Lecture 9** [S4] (preprocessing, augmentation, regularisation, visualisation) are the two lectures this note covers; their own reading lists supplied [S25] Ruder's optimiser overview, [S28]/[S29] batch norm, [S31] dropout, [S32] SWA, [S33] cutout, [S34]/[S35] adversarial examples, [S36] SpecAugment and [S37] EDA.
- Izmailov et al. 2018 [S32], stochastic weight averaging. DeVries & Taylor 2017 [S33], cutout. Goodfellow, Shlens & Szegedy 2015 [S34], adversarial examples and FGSM. Su et al. 2017 [S35], one-pixel attack. Park et al. 2019 [S36], SpecAugment. Wei & Zou 2019 [S37], EDA.
