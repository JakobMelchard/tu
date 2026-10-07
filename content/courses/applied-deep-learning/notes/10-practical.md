# 10 Practical deep learning in PyTorch

Everything in notes 01-09 is a few hundred lines of maths; what decides whether a project succeeds in 45 h is the engineering around it. This note collects the PyTorch idioms, the Apple-Silicon specifics, and the discipline (logging, seeding, checkpointing, profiling, debugging in a fixed order) that turn a model definition into an experiment whose numbers can be trusted and reproduced. Nothing here is theory; all of it is the difference between "loss went down once" and a result that survives a second seed. The reference training loop lives in `src/py/common.py` and the project skeleton in `src/project_template/train.py`.

## Concepts

### PyTorch idioms

- **Tensor**: an $n$-dimensional array with a `dtype`, a `device`, a memory layout (strides), and optionally an autograd history. **Batch**: leading dimension $B$ of independent samples processed together; the loss is a mean over it. **Layout**: which axis means what, e.g. images `[B, C, H, W]`, sequences `[B, T, F]` (batch-first) or `[T, B, F]`; PyTorch does not know the semantics, only the shape.
- `nn.Module`: parameters are registered in `__init__` (anything assigned as `nn.Parameter` or as a sub-module), computation is `forward(x)`. Call the module, never `forward` directly (hooks, autocast). `nn.Sequential(*layers)` for pure chains; write a class as soon as there is a skip connection or two inputs.
- `Dataset` (`__len__`, `__getitem__(i)` returning one sample) + `DataLoader(ds, batch_size, shuffle, num_workers, collate_fn, pin_memory, drop_last)`. `collate_fn` turns a list of samples into a batch; the default stacks equal-shape tensors, write your own for padding variable-length sequences. `num_workers>0` forks worker processes; on macOS this uses `spawn`, so the script body must be under `if __name__ == "__main__":`.
- `model.train()` / `model.eval()` toggle `Dropout` and `BatchNorm` behaviour; they do not touch gradients. `torch.no_grad()` disables graph building; `torch.inference_mode()` additionally skips version counters and view tracking (faster, but the resulting tensors cannot later enter autograd).
- Step: `optimizer.zero_grad(set_to_none=True)` (sets `.grad = None` instead of filling zeros: saves a kernel and memory) $\to$ `loss = ...` $\to$ `loss.backward()` $\to$ `optimizer.step()` $\to$ `scheduler.step()`.
- Device: `model.to(device)` once; every batch `x.to(device, non_blocking=True)`. Parameters and inputs must live on the same device; the error otherwise is explicit.
- `state_dict()`: an `OrderedDict` name $\to$ tensor of all parameters and buffers (BN running stats). `load_state_dict` matches by name, so renaming a submodule breaks old checkpoints; `strict=False` to load partially.
- `torch.compile(model)` traces the forward into fused kernels; 1.2-2x on CUDA for static shapes, first call is slow, MPS support is partial in 2.14. Try last, not first.
- Broadcasting: trailing dimensions are aligned right-to-left, a size-1 axis stretches. `[B,1] - [1,B]` gives `[B,B]`; this is the classic source of silent wrong losses. `torch.einsum("btd,bsd->bts", q, k)` documents the contraction and avoids `transpose`/`bmm` bookkeeping.
- In-place ops (`x.add_(1)`, `x[:, 0] = 0`, `relu(inplace=True)`) modify a tensor that autograd may have saved for backward; the error is "one of the variables needed for gradient computation has been modified by an inplace operation". Out-of-place is the default; in-place only on tensors that are not inputs to a saved op.

### Device selection

```python
def get_device():
    if torch.backends.mps.is_available(): return torch.device("mps")
    if torch.cuda.is_available():         return torch.device("cuda")
    return torch.device("cpu")
```
MPS (Metal Performance Shaders) on the M3 Pro: unified memory (the GPU sees the whole RAM, so "out of memory" is rarer but swapping is silent), no `float64` (`.double()` raises; keep everything fp32/bf16), a few ops not implemented (the error names the op; `PYTORCH_ENABLE_MPS_FALLBACK=1` runs that op on CPU with a copy, slow but correct), `torch.mps.synchronize()` before timing, `torch.mps.manual_seed`. CUDA equivalents: `torch.cuda.synchronize()`, `torch.cuda.manual_seed_all`, `torch.cuda.max_memory_allocated()`. Small models ($<10^6$ parameters, batch $<64$) are often faster on CPU than MPS because kernel launch overhead dominates; measure both once.

### Experiment tracking

Log per run: full config (every hyperparameter), git commit hash and dirty flag, seed, device, PyTorch version; per step: loss, LR, gradient norm (`torch.nn.utils.clip_grad_norm_` returns it), throughput (samples/s), wall time; per epoch: validation metrics, best-so-far. Tools: `torch.utils.tensorboard.SummaryWriter` (`add_scalar(tag, value, step)`, local, no account), Weights & Biases (hosted, config diffing, sweeps), MLflow (self-hosted), or a CSV written with `csv.DictWriter` plus a 20-line matplotlib script; the last is enough for a 3-ECTS project and never breaks. Config pattern: one `config.yaml` $\to$ `dataclass`:

```python
@dataclass
class Config:
    lr: float = 3e-4; batch_size: int = 64; steps: int = 5000; seed: int = 0
cfg = Config(**yaml.safe_load(open("config.yaml")))
```
Override from the CLI (`--lr 1e-3`), dump the resolved config next to the checkpoints. A run is identified by its directory `runs/<date>_<name>/`.

### Reproducibility

`seed_all(seed)` sets `random.seed`, `np.random.seed`, `torch.manual_seed` (covers CUDA and MPS), and the `DataLoader(generator=torch.Generator().manual_seed(seed))` plus `worker_init_fn` for workers. `torch.use_deterministic_algorithms(True)` raises on nondeterministic kernels (on CUDA also needs `CUBLAS_WORKSPACE_CONFIG=:4096:8`; `torch.backends.cudnn.benchmark=False`). Nondeterminism sources: cuDNN autotuner picking different convolution algorithms, floating-point atomics in scatter/index ops (summation order changes), MPS kernels (largely undocumented), data-loader worker scheduling, `torch.compile`. Even bit-exact seeds do not make the *conclusion* reproducible: the variance across seeds is the noise floor of any comparison. Report $\bar m \pm s$ over $n \ge 3$ seeds with $s$ the sample standard deviation; two methods whose intervals overlap are not distinguished by that experiment.

### Checkpoints

Save a dict: `{"model": model.state_dict(), "optimizer": opt.state_dict(), "scheduler": sched.state_dict(), "step": step, "rng": {"torch": torch.get_rng_state(), "np": np.random.get_state(), "py": random.getstate()}, "config": asdict(cfg), "best_metric": best}`. `torch.save(ckpt, path)`; `torch.load(path, map_location=device, weights_only=True)` (`weights_only=True` is the default since 2.6 and refuses arbitrary pickles; store only tensors, numbers, strings, dicts). Keep `last.pt` (overwritten every $k$ steps, for resuming) and `best.pt` (overwritten when the validation metric improves, for evaluation). Resuming: load all four, set `step`, restore RNG, continue; the LR schedule and Adam moments are part of the state, otherwise resumption changes the trajectory.

### Mixed precision

`with torch.autocast(device_type="cuda", dtype=torch.bfloat16):` runs matmuls and convolutions in the low dtype and keeps reductions (softmax, norms, losses) in fp32. bf16 has the fp32 exponent range (8 bits) with 7 mantissa bits, so no scaling is needed; fp16 has a 5-bit exponent, gradients below $6\cdot10^{-8}$ underflow, hence `GradScaler`: multiply the loss by $s$, unscale gradients before `step`, halve $s$ on inf/nan, double it every 2000 clean steps. Benefit comes from tensor cores (CUDA, 2-3x throughput, half the activation memory). On MPS `autocast` exists with fp16/bf16 but speedups are small; the memory halving still applies. Master weights stay fp32 in both variants; the optimizer step is fp32.

### Profiling

Order of suspicion: data loading $\to$ host-device copies $\to$ small kernels $\to$ the model. Test 1: time one epoch with the model replaced by `x.sum()`; if that is not $\ll$ the full epoch, the loader is the bottleneck (increase `num_workers`, pre-decode to tensors, cache to `.npy`). Test 2: `time.perf_counter()` around forward and backward with `torch.mps.synchronize()`/`torch.cuda.synchronize()` before each reading (kernels are asynchronous, unsynchronised timings measure launch, not execution). `torch.utils.benchmark.Timer(stmt, globals).blocked_autorange()` for micro-benchmarks with warm-up; `torch.profiler.profile(activities=[CPU, CUDA])` with `key_averages().table(sort_by="self_cuda_time_total")` for kernel-level tables. Memory: `torch.cuda.max_memory_allocated()`, `torch.mps.current_allocated_memory()` and `driver_allocated_memory()`. Gradient accumulation: call `backward()` on `loss / k` for $k$ micro-batches, `step()` once; equals batch $kB$ except for BatchNorm statistics. Gradient checkpointing (`torch.utils.checkpoint.checkpoint(block, x)`): drop activations of a block in forward, recompute in backward; memory $O(\sqrt L)$ instead of $O(L)$ for $L$ layers at $\approx 30\%$ extra compute (Chen et al. 2016).

### Common bugs

| symptom | cause | fix |
|---|---|---|
| loss decreases then explodes, grad norm grows each step | `zero_grad` missing, gradients accumulate | `zero_grad(set_to_none=True)` at loop start |
| val accuracy far below train, or fluctuates with batch size | `model.eval()` missing: dropout on, BN uses batch stats | `eval()` + `no_grad()` in the eval function, `train()` after |
| loss stuck near $\log C$ though model is large | softmax applied before `CrossEntropyLoss` (expects logits) | remove the softmax; use `log_softmax` + `NLLLoss` only as a pair |
| RNN learns nothing, shapes look right | `[B,T,F]` fed to a module expecting `[T,B,F]` (`batch_first=False` default) | pass `batch_first=True` or transpose once, assert shapes |
| loss ok in value but never converges, `loss.shape` non-scalar or huge | `pred [B,1]` minus `target [B]` broadcasts to `[B,B]` | `target.view_as(pred)` or `squeeze(-1)`; assert `pred.shape == target.shape` |
| val metric too good, collapses on test | leakage: normalisation fitted on all data, duplicates across splits, augmentation before splitting | split first, fit statistics on train only, dedup by hash |
| loss NaN after a few steps | LR too high, fp16 overflow, log of zero | lower LR 3-10x, `clip_grad_norm_`, `eps` in logs, bf16 |
| loss decreases by $10^{-4}$ per epoch | LR too low or wrong parameter group | LR range test: increase LR geometrically until divergence, use 1/3 of that |
| train loss has periodic structure, poor generalisation | `shuffle=False`, sorted dataset | `shuffle=True` for train, never for val |
| accuracy $\approx 1/C$ exactly | labels 1-based, or off by one after `argmax` | labels in $\{0,\dots,C-1\}$, check `y.min(), y.max()` |
| "view size is not compatible with input tensor's size and stride" | `view` on a non-contiguous tensor (after `transpose`/`permute`) | `reshape` or `.contiguous().view` |
| GPU utilisation low, `.item()` in the inner loop | each `.item()` synchronises device and host | accumulate loss tensors, call `.item()` once per `log_every` |
| memory grows every step | storing `loss` (with graph) in a list | `loss.detach()` or `.item()` for logging |
| accuracy always 0 | integer division `correct / total` with tensors of dtype long in old code, or `//` | `.float()` / `.item()` before dividing |
| pretrained model gives $\approx$ random outputs | input normalised with own statistics instead of the model's (ImageNet mean/std) | use the transform shipped with the weights |
| `DataLoader` with `num_workers>0` hangs or re-imports the script on macOS | spawn start method re-executes the module | put the entry point under `if __name__ == "__main__":` |

### Capacity, effective capacity and the Bayes error

Lecture 5 [S4] is Goodfellow chapter 11 [S15] with a library tour attached, and these three ideas are its spine. They are worth stating precisely because they are what tells you *which* thing to fix when a run disappoints.

**Representational capacity** is the set of functions the architecture can express at all — a linear model cannot express XOR no matter how it is trained. **Effective capacity** is the subset the *optimiser actually reaches* from a given initialisation in a given budget, and it is always smaller: a 100-layer plain net can represent everything a 10-layer one can, and SGD will not find it (note 02). Every regulariser, every schedule and every architectural trick in these notes moves effective capacity, not representational capacity. So:

- **Train loss high** $\Rightarrow$ underfitting $\Rightarrow$ capacity problem: bigger model, longer training, better optimisation, less regularisation.
- **Train loss low, val loss high** $\Rightarrow$ overfitting $\Rightarrow$ more data, more augmentation, more regularisation, smaller model.
- **Both low and still not good enough** $\Rightarrow$ you are near the noise floor.

That floor is the **Bayes error**: the loss of the best possible predictor given the inputs, i.e. the irreducible part that comes from the labels genuinely not being a function of the inputs — sensor noise, ambiguous images, disagreeing annotators, genuinely random outcomes. No model beats it. Two consequences for the project:

1. **Estimate it before you set a target.** Human performance on the same inputs is the usual proxy; a cheaper one is to relabel 100 random validation items yourself and measure your disagreement with the stored labels. If that disagreement is 8 %, an accuracy target of 97 % is not ambitious, it is impossible, and the assignment-2 sheet asks you to commit to "a reasonable target value" [S13].
2. **A result at the Bayes error is a complete result.** "The model reaches 0.91, human agreement on this data is 0.92, so the remaining error is label noise" is a stronger report than chasing another point, and it is exactly the kind of insight [S14] asks the report to contain.

**Coverage** is the third term: the fraction of inputs on which the system chooses to answer. Letting a model abstain when its confidence is below a threshold trades coverage for accuracy, and the accuracy-vs-coverage curve is often the honest way to report a system that must not be wrong (medical triage, moderation) — 99 % accuracy at 60 % coverage can be far more useful than 93 % at 100 %.

### Hyperparameter search

Lecture 5's own ordering [S4]. Tune by hand first: the **learning rate is the single most important hyperparameter** and is worth more attention than everything else combined; find the largest one that does not diverge, then everything else.

For automated search, **random search beats grid search** (Bergstra & Bengio 2012 [S94]) and the argument is geometric, not empirical: with $k$ hyperparameters of which only $k' < k$ actually matter, a grid of $n$ points per axis spends $n^k$ trials but tries only $n$ distinct values of each important parameter, because every other axis' variation is wasted. Random search with the same budget tries a distinct value of *every* parameter in *every* trial. Since which parameters matter is unknown in advance and usually $k'$ is 2 or 3, random wins. Then: log-uniform sampling for scale parameters (LR, weight decay), uniform for bounded ones; Bayesian optimisation or Hyperband/ASHA once trials are expensive enough to be worth modelling (Feurer & Hutter 2019 [S94]); and successive halving — start many short runs, kill the worst — which is the highest-value trick on a fixed laptop budget. `optuna` implements ASHA and TPE in a few lines.

**Report the search, not just the winner** [S13]: the grid or distribution, the number of trials, the budget per trial, and the selection metric. A hyperparameter chosen on the test set is test tuning (note 11).

### Debugging in order (Karpathy 2019 [S19], "A Recipe for Training Neural Networks")

1. Fix the seed, disable augmentation, `num_workers=0`.
2. Inspect data: plot 16 inputs with labels straight from the `DataLoader` (after augmentation), check class counts, dtype, value range.
3. Trivial baselines: majority class, mean prediction; note their metric values.
4. Loss at initialisation: for $C$ classes with uniform predictions $\mathcal L = \log C$ ($\log 10 = 2.303$); for MSE the variance of the targets. Deviation means wrong scaling or wrong loss.
5. Overfit one batch: one fixed batch of 8-32 samples, train until loss $\approx 0$ / accuracy 100%. Failure means the model, loss, or optimizer is broken, not the data. Under-fitting it is the single most informative test.
6. Widen: full data, small model, no regularisation; verify train loss decreases and val loss tracks it; then add capacity, then regularisation.
7. Gradient checks: `grad_norm` per layer (zeros at the bottom of a deep network mean vanishing gradients or a `detach` in the wrong place), `torch.autograd.gradcheck` for custom ops in fp64 on CPU.
8. Only now tune hyperparameters, one at a time, from a working baseline.

## Architecture sketch

```
config.yaml --> Config dataclass --> seed_all(cfg.seed), device = get_device()
      |
      v
Dataset --> DataLoader(batch=B, shuffle, num_workers, collate_fn)   x:[B,...]  y:[B]
      |
      v
model = Net(cfg).to(device)          count_params(model)
opt   = AdamW(model.parameters(), lr) ; sched = CosineAnnealingLR(opt, steps)
      |
      v
for step in range(steps):                                   # train_loop
    x, y = next(batch); x, y = x.to(device), y.to(device)
    opt.zero_grad(set_to_none=True)
    with autocast(dtype=bf16): loss = criterion(model(x), y)  # scalar []
    loss.backward(); gn = clip_grad_norm_(model.parameters(), 1.0)
    opt.step(); sched.step()
    if step % log_every == 0: log(step, loss.item(), lr, gn, samples/s)
    if step % eval_every == 0: metric = evaluate(model, val_loader)   # eval(), no_grad()
                               save last.pt; if metric > best: save best.pt
      |
      v
evaluate(best.pt, test_loader) exactly once --> report
```

`common.train_loop(step_fn, optimizer, steps, log_every=0, scheduler=None) -> list[float]`: `step_fn()` draws a batch, runs forward, and returns the loss tensor; the loop does `zero_grad`, `backward`, `step`, optional `scheduler.step()`, prints every `log_every` steps, and returns the per-step losses as floats.

**Worked example: memory for 10M parameters under Adam with bf16 autocast.** Per parameter: fp32 master weight 4 B, fp32 gradient 4 B, Adam $m$ and $v$ 4 + 4 B $\Rightarrow$ 16 B. $10^7 \cdot 16\,\text{B} = 160\,\text{MB}$ static. Autocast adds a transient bf16 copy of each weight used in a matmul: $10^7 \cdot 2\,\text{B} = 20\,\text{MB}$. Activations dominate and scale with $B$: a 12-layer transformer with $d=512$, $T=256$, $B=32$ stores per layer roughly $B T \cdot (8d + 2 h T)$ values (residual, QKV, attention scores $[B,h,T,T]$, MLP $4d$) $\approx 32\cdot256\cdot(4096 + 2\cdot8\cdot256) = 67\cdot10^6$ values $\to$ 134 MB in bf16 per layer, 1.6 GB for 12 layers. Total $\approx 1.8$ GB, so the model state is not the problem; the batch is. Halving $B$ or checkpointing halves the activation term; the optimizer term is untouched.

## Pitfalls

- Loss curve looks perfect, metric on test is random $\to$ evaluation ran in `train()` mode or on un-normalised inputs $\to$ one `evaluate()` function that sets `eval()`, `no_grad()`, uses the same transform as training minus augmentation.
- Two runs with the same seed differ $\to$ nondeterministic kernels (cuDNN, atomics, MPS) or worker ordering $\to$ accept it; report mean $\pm$ std over seeds instead of chasing bit-exactness.
- Training takes 10x longer than the FLOP count suggests $\to$ data loader or `.item()` synchronisation $\to$ time with the model replaced by `x.sum()`, then with `num_workers` 0/2/4, remove per-step `.item()`.
- Resumed run diverges from the uninterrupted one $\to$ optimizer/scheduler state not restored, LR restarted at the warm-up value $\to$ save and load all four state dicts plus `step`.
- Checkpoint fails to load after a refactor $\to$ `state_dict` keys are attribute paths $\to$ keep module names stable or write a key-remapping function; load with `strict=False` only deliberately.
- fp16 run has loss NaN at step 3 $\to$ gradient overflow without `GradScaler` $\to$ use bf16 on hardware that supports it, else `GradScaler`.
- `torch.compile` errors or is slower $\to$ dynamic shapes (variable $T$), MPS backend, tiny model $\to$ pad to fixed shapes or skip compilation; it is an optimisation, not a requirement.
- MPS run silently slow $\to$ `PYTORCH_ENABLE_MPS_FALLBACK=1` routing an op through CPU each step $\to$ run once without the fallback to see which op is missing, replace it (e.g. `float64` $\to$ `float32`, unsupported `scatter_reduce` $\to$ dense equivalent).
- Metric computed per batch and averaged $\to$ wrong for non-decomposable metrics (F1, AUC) and for unequal last batch $\to$ accumulate predictions and targets, compute once per epoch.

## Questions

1. Why does `optimizer.zero_grad(set_to_none=True)` save memory and time compared with zeroing?
<details><summary>Answer</summary>
Zeroing writes a full tensor of zeros for every parameter each step (one kernel per tensor, memory bandwidth). Setting `.grad = None` frees the gradient tensor; the next `backward` allocates it fresh with `=` instead of `+=`, skipping the read of the old zeros. Numerically identical except that code reading `.grad` before `backward` must handle `None`.
</details>

2. Derive the initial cross-entropy loss of a 10-class classifier with zero-initialised final layer and explain what a value of 5.2 at step 0 tells you.
<details><summary>Answer</summary>
Zero logits give softmax $p_c = 1/10$ for all $c$; $\mathcal L = -\log p_{y} = \log 10 = 2.303$. A value of 5.2 means the logits are far from zero at init: the final layer is not small (wrong init or a large bias), the inputs are not normalised so activations are huge, or a softmax/log was applied twice. Fix before training; a network that starts confidently wrong wastes the first epochs unlearning it.
</details>

3. A model with 50M parameters trained with AdamW in fp32 reports 2.1 GB peak memory at batch 16; what is the split, and what changes when you switch to bf16 autocast?
<details><summary>Answer</summary>
Weights 200 MB, gradients 200 MB, Adam moments 400 MB: 800 MB static. Remaining 1.3 GB is activations, workspace, and fragmentation. bf16 autocast does not touch the 800 MB (master weights and optimizer state stay fp32) but roughly halves activations (stored in bf16) and adds a transient 100 MB bf16 weight copy: expect $\approx 800 + 650 + 100 = 1.55$ GB, i.e. the batch can grow to about 24-28, not 32.
</details>

4. Your validation accuracy jumps between 71% and 84% from epoch to epoch while the training loss decreases smoothly. List three causes in order of likelihood and the test for each.
<details><summary>Answer</summary>
(i) Validation set too small: with $n=200$ the binomial std of accuracy at $p=0.8$ is $\sqrt{0.8\cdot0.2/200}=2.8\%$, so $\pm 6\%$ swings are noise; test: compute the std, enlarge val. (ii) BatchNorm in `train()` mode during evaluation with small batches; test: call `model.eval()` and check the variance disappears. (iii) LR too high causing the weights to oscillate around a minimum; test: plot training loss at step resolution, not epoch, and try LR/3.
</details>

5. Why is reporting one seed's test accuracy of 91.3% against a paper's 90.8% not evidence of improvement, and what would you report instead?
<details><summary>Answer</summary>
Seed-to-seed variance on typical small datasets is 0.5-2 percentage points, larger than the claimed gap; a single number has no error bar. Report mean $\pm$ sample std over $n\ge3$ seeds for both the reproduction of the baseline and the new method, on the same split and preprocessing, and state whether the gap exceeds roughly $2s/\sqrt n$. With 3 seeds at $s=0.8$ the resolvable difference is $\approx 0.9$ points, so 0.5 is not resolved.
</details>

6. In the project you have 2 h of M3 Pro time per experiment. Describe how you decide whether the data loader or the model is the bottleneck, and what you do in each case.
<details><summary>Answer</summary>
Measure three throughputs over 50 batches with `torch.mps.synchronize()` before each reading: (a) loader only (iterate, `x.sum()`), (b) loader + forward under `no_grad`, (c) full step. If (a) is within 2x of (c), the loader dominates: pre-decode images to a uint8 tensor on disk, use `num_workers=4` under `__main__` guard, move augmentation to the GPU or drop it. If (c) $\gg$ (b) $\gg$ (a), the model dominates: bf16 autocast, smaller image size, fewer layers, or a frozen pretrained backbone with cached features so only the head is trained.
</details>

7. `train_loop` returns per-step losses; the test asserts the mean of the last 10% is below the mean of the first 10%. Give a case where this passes but the model is wrong, and a case where it fails but the model is right.
<details><summary>Answer</summary>
Passes but wrong: a `[B,B]` broadcast loss still decreases as the model learns to predict the global mean; or the model memorises a single unshuffled batch. Fails but right: a GAN's discriminator loss (adversarial, non-monotone, which is why `gan_toy` reports mode distance instead), or an LR warm-up longer than the step budget so the loss barely moves. The test detects "optimisation is doing something", not correctness; the overfit-one-batch check and a held-out metric are needed for the latter.
</details>

8. What is the difference between `torch.no_grad()` and `torch.inference_mode()`, and when would the latter be a mistake?
<details><summary>Answer</summary>
Both stop graph construction. `inference_mode` also disables version counters and view/base tracking, so tensors it creates are cheaper but cannot be used in a later autograd computation ("Inference tensors cannot be saved for backward"). Mistake: computing features of a frozen backbone under `inference_mode` and then feeding them into a trainable head inside the same graph; use `no_grad` (or `detach`) there, `inference_mode` only for pure evaluation.
</details>

## Code

`src/py/common.py`: `get_device()` (mps > cpu), `seed_all(seed)`, `train_loop(step_fn, optimizer, steps, log_every=0, scheduler=None, clip_grad=None)` returning the list of per-step losses (`step_fn` returns the loss tensor), `Timer` context manager (`with Timer() as t: ...; t.seconds`), `loss_decreased(losses, frac=0.1)`, `count_params(model, trainable_only=False)`. Every `src/py/<module>.py` uses `run(steps=..., device=None, seed=0) -> dict` with `"losses"` and a metric key; `python src/py/<module>.py` trains for a few seconds and prints the metric; `test_<module>.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)`, i.e. the mean of the last 10% of losses is below the mean of the first 10%.

`src/project_template/train.py`: the skeleton of the diagram above (config.yaml $\to$ dict $\to$ data $\to$ model $\to$ optimizer $\to$ epoch loop with logging to `log.csv`, `best.pt`/`last.pt` checkpoints that include optimizer, scheduler, step and config, and resume via `train.resume`; it is self-contained and does not import `common`), to be copied and filled for the project. Run from this course folder with `uv run python` (repo venv).

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016) [S15]: ch. 8 (optimization: minibatches, Adam, learning rates), **ch. 11 (practical methodology: baselines, metrics, hyperparameter search, debugging strategies -- this is Lecture 5, almost section for section)**, ch. 12.1 (large-scale implementations, GPUs, mixed precision).
- Karpathy, A. (2019) [S19]. *A Recipe for Training Neural Networks*. Blog post.
- Kingma, D. P. and Ba, J. (2015) [S22]. Adam: A Method for Stochastic Optimization. ICLR.
- Loshchilov, I. and Hutter, F. (2019) [S23]. Decoupled Weight Decay Regularization (AdamW). ICLR.
- Micikevicius, P. et al. (2018) [S85]. Mixed Precision Training. ICLR. **Lecture 12's reference 2** [S4]; see [`12-serving-and-deployment.md`](12-serving-and-deployment.md) for the format table.
- Chen, T. et al. (2016). Training Deep Nets with Sublinear Memory Cost (gradient checkpointing). arXiv:1604.06174.
- Ioffe, S. and Szegedy, C. (2015) [S28]. Batch Normalization. ICML (train/eval mode semantics).
- Paszke, A. et al. (2019). PyTorch: An Imperative Style, High-Performance Deep Learning Library. NeurIPS.
- PyTorch 2.14 docs [S96]: `torch.autocast`, `torch.profiler`, `torch.utils.data`, MPS backend notes.
- Bergstra & Bengio (2012) [S94], *Random search for hyper-parameter optimization*, JMLR; Feurer & Hutter (2019) [S94], *Hyperparameter optimization*, AutoML book ch. 1 -- **Lecture 5's references 4 and 5** [S4].
- Tan & Le (2020) [S44], *EfficientNet* -- Lecture 5's *efficiently scaling up a model*.
- **Lecture 5** [S4], *Libraries and Practical Aspects*, is the lecture this note covers: coverage, capacity, under/overfitting, effective capacity, scaling up, hyperparameters, train/val/test, the learning rate, selecting hyperparameters, automatic hyperparameter optimization, the Bayes error, design principles, performance metrics, obtaining a baseline, dataset size, debugging, and 14 minutes of library tour. **Lecture 12** [S4] continues it into serving and optimisation; that is [`12-serving-and-deployment.md`](12-serving-and-deployment.md).
