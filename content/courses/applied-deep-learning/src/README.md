# Reference implementations: 194.077 Applied Deep Learning

Python only (the course is PyTorch-based). Everything runs in the repo venv (`uv sync` at the repo root, which holds `pyproject.toml`); nothing is downloaded, every dataset is generated in the script. From this course folder:

```
uv run pytest src/py -q      # 54 tests, about 14 s
cd src/py && uv run python cnn_shapes.py   # any module: a few seconds of training, prints a metric
```

Device: `common.get_device()` picks `mps` on Apple Silicon, else `cuda`, else `cpu`. The RNN and RL examples default to CPU because their per-step Python loops are kernel-launch-bound on MPS.

## py/

| Module | Topic (note) | What it trains | Printed metric |
|---|---|---|---|
| `common.py` | 01, 10 | `get_device`, `seed_all`, `train_loop(step_fn, optimizer, steps, log_every, scheduler, clip_grad)`, `Timer`, `loss_decreased`, `count_params`, `moving_average` | |
| `cnn_shapes.py` | 02 | conv-BN-ReLU CNN on generated circle/square/triangle images, AdamW + one-cycle, flip augmentation | test accuracy, receptive field |
| `rnn_sequence.py` | 03 | RNN / GRU / LSTM cells unrolled by hand on the adding problem; `grad_norm_through_time` | test MAE, gradient norm per time step |
| `rl_reinforce.py` | 04 | REINFORCE with baseline and entropy bonus on an inline 5x5 gridworld | success rate, greedy path length |
| `autoencoder_vae.py` | 05 | AE and VAE (closed-form KL, reparameterisation) on 16x16 shapes | pixel error, KL |
| `gan_toy.py` | 05 | non-saturating GAN on 8 Gaussians on a ring | mode distance, modes covered |
| `transformer_char.py` | 06 | decoder-only char transformer (attention written out) on generated `"12+7=19"` lines | bits/char, greedy completions |
| `gnn_gcn.py` | 07 | dense GCN vs feature-only MLP on a stochastic block model, 10 % labels | test accuracy on unlabelled nodes |
| `xai_saliency.py` | 08 | saliency, integrated gradients (completeness check), Grad-CAM on the shape CNN | attribution mass on the shape |
| `llm_finetune_sketch.py` | 09 | pretrain tiny LM on addition, freeze, LoRA adapters fine-tuned on subtraction, merge | trainable fraction, bits/char before/after |
| `shape_formulas.py` | 02, 03, 06 | nothing — it *verifies*: conv/transposed-conv output size, parameter counts for conv/RNN/LSTM/GRU/attention/transformer blocks, receptive field, attention memory, each checked against torch over a sweep | number of checks, then the tables printed from the verified formulas |
| `ctc_loss.py` | 03 | the CTC forward algorithm in log space, from scratch; then a frame classifier trained with it on unaligned targets | agreement with `torch.nn.CTCLoss` and with brute force; greedy-decode exact match |
| `set_prediction.py` | 06 | GIoU, the DETR matching cost, Hungarian vs greedy vs brute-force matching, the set criterion, and a query-based toy detector | matching optimality, mean IoU of matched boxes |
| `deploy_optimize.py` | 12 | affine int8 quantisation from scratch; float formats read out of `torch.finfo` | float-format table, quantisation SNR against its analytic bound |
| `pruning.py` | 12 | global magnitude pruning and the lottery-ticket rewind-vs-reinit comparison over seeds | sparsity vs accuracy, rewind − reinit ± standard error |

Every module exposes `run(steps=..., device=None, seed=0) -> dict` with a `"losses"` list and a metric. `test_<module>.py` calls `run` with a small step budget, asserts `common.loss_decreased(losses)` (mean of the last 10 % below the mean of the first 10 %; for the GAN the series is the mode distance), and cross-checks one formula against torch (conv output size, KL vs `torch.distributions`, GCN normalisation, IG on a linear model, LoRA merge, causal mask).

### Reference results reproduced

The highest-value tests are the ones that reproduce a number someone else published or that an independent method computes:

| test | reproduces |
|---|---|
| `test_ctc_loss.py::test_matches_torch_ctc_loss` | `torch.nn.CTCLoss`, the reference implementation of Graves et al. 2006 [S48] — exact agreement to `1e-4` on three configurations |
| `test_ctc_loss.py::test_matches_brute_force_enumeration` | exhaustive enumeration of all $C^T$ paths and the collapse rule, i.e. CTC's *definition* rather than another implementation of its dynamic program |
| `test_ctc_loss.py::test_closed_forms` | two hand-computable cases, including the three paths of $l=[1]$ over two frames |
| `test_set_prediction.py::test_hungarian_is_optimal_and_greedy_is_not` | exhaustive enumeration of every injection, over 100 random cost matrices; greedy loses on more than 10 of them |
| `test_set_prediction.py::test_iou_and_giou_axioms` | the defining properties of GIoU: $1$ for identical boxes, $\to -1$ as boxes separate, and equal to IoU when the enclosing box is the union |
| `test_deploy_optimize.py::test_quantisation_matches_torch` | `torch.quantize_per_tensor` on every entry of three tensors spanning four orders of magnitude |
| `test_deploy_optimize.py::test_quantisation_error_respects_the_half_step_bound` | the analytic $s/2$ bound and the $s/\sqrt{12}$ uniform-error RMS |
| `test_deploy_optimize.py::test_float_format_facts` | `torch.finfo` — the float-format table in note 12 is generated, never typed |
| `test_shape_formulas.py` (10 tests) | every worked number in notes 02, 03 and 06, plus 936 conv configurations and a *measured* receptive field (gradient support, not a recomputation of the same recursion) |

`test_pruning.py::test_lottery_ticket_runs_and_is_reported_honestly` is the opposite case and is deliberate: the lottery-ticket effect [S84] does **not** reproduce on this toy, and the test pins that so an apparent future "reproduction" is noticed. See [`../notes/12-serving-and-deployment.md`](../notes/12-serving-and-deployment.md).

Source ids `[S<n>]` resolve in [`../refs/SOURCES.md`](../refs/SOURCES.md).

## project_template/

Copy-and-fill skeleton for the graded project: `README.md` (per-assignment checklist and dates), `config.yaml`, `data/`, `models/`, `train.py` (config -> data -> model -> loop with CSV log, best/last checkpoints, resume, optional bf16 autocast), `evaluate.py` (test split once, majority baseline, confusion matrix, worst errors), `report/outline.md`, `presentation/outline.md`. Runs as is on synthetic data:

```
cd src/project_template
uv run python train.py --steps 200 --experiment smoke
uv run python evaluate.py --checkpoint models/checkpoints/smoke/best.pt
```
