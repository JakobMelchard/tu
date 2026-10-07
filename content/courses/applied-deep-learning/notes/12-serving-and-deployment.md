# 12 Serving, optimising and deployment

A trained checkpoint is not a deliverable. Lecture 12 [S4] opens with the point and assignment 3 enforces it: **the demo application is worth 10 of the 50 points**, the same as the report and the same as each earlier assignment [S14]. What the sheet asks for is a thing a stranger can run — a command-line tool, a Docker container, or (its own recommendation) a small web app that runs your model in the browser. This note is the path from `best.pt` to that, plus the three optimisations the lecture spends its second half on: **number formats**, **quantisation** and **pruning**.

The scheduling trap: this is one of the *last* lectures of the semester, after assignment 2 is due [S4, S5]. If you only watch it when it is released you will be building the demo in the last three weeks with no slack. The previous years' recordings are online [S6, S7]; watch it in November.

Every number in this note was produced by running `src/py/deploy_optimize.py` and `src/py/pruning.py`, not quoted.

## Concepts

### The serving ladder

Lecture 12's own progression, from "a simple way to serve a model" upwards:

1. **Load the model inside the request handler.** One Flask/FastAPI route, `torch.load` at import, `model.eval()`, `with torch.no_grad()`. Works, and is where to start. Fails under concurrency: the model is loaded once but the GIL and the single-sample forward pass make throughput terrible, and a second worker doubles the memory.
2. **Separate the model server from the application.** Batch incoming requests over a short window (say 10 ms), run one forward pass, scatter the results. A batch of 16 costs barely more than a batch of 1 on a GPU, so this is the single biggest throughput lever. TensorFlow Serving and TorchServe do this for you and also give versioned model endpoints, so a new model is a directory drop rather than a redeploy.
3. **Container.** The model server plus its exact dependency set in a Docker image. This is what makes "it runs on my machine" reproducible, and it is what the assignment sheet names as the step above a bare CLI tool [S14].
4. **Hosted.** Streamlit, Gradio and Hugging Face Spaces each turn a Python function into a web UI with a public URL and no infrastructure. Gradio in particular is about fifteen lines for an image-in/label-out demo. All three are named in [S14]; for a 3-ECTS project they are the right level of effort.
5. **In the browser.** No server at all: ship the weights as a static file and run inference in the visitor's browser tab with ONNX Runtime Web or TensorFlow.js. Lecture 12 gives this eleven minutes and [S14] recommends it. It is free to host (GitHub Pages), has no cold start, and the data never leaves the machine — but it caps you at models of roughly tens of MB and at WASM/WebGPU speed.

Whatever you pick: **the weights are fetched at runtime from a GitHub release, never committed** [S13].

### ONNX

ONNX is an interchange format: a serialised computation graph with a versioned operator set (*opset*), plus initialisers for the weights. `torch.onnx.export` traces or scripts your model into it; ONNX Runtime executes it on CPU, CUDA, CoreML, WebAssembly or WebGPU. The reason it matters for the project is that it is the bridge out of Python — the same `.onnx` file runs in a browser, on a phone, and in a C++ service.

The failure modes are all about tracing. A traced graph is one control-flow path, so `if x.shape[0] > 1:` is baked in at whatever the example input made it; loops over a Python list are unrolled; an unsupported op fails the export or silently becomes something else. Mark the batch (and sequence) dimension as dynamic with `dynamic_axes`, then **verify numerically**: run the same input through PyTorch and through ONNX Runtime and assert the outputs agree to about `1e-5`. An export that loads but computes something else is the expensive bug here.

### Number formats

Read from `torch.finfo` [S96] by `deploy_optimize.float_formats()`:

| format | bytes | max | smallest normal | eps | mantissa bits | ~decimal digits |
|---|---|---|---|---|---|---|
| fp32 | 4 | $3.403\cdot10^{38}$ | $1.175\cdot10^{-38}$ | $1.192\cdot10^{-7}$ | 23 | 6.9 |
| fp16 | 2 | $6.550\cdot10^{4}$ | $6.104\cdot10^{-5}$ | $9.766\cdot10^{-4}$ | 10 | 3.0 |
| bf16 | 2 | $3.390\cdot10^{38}$ | $1.175\cdot10^{-38}$ | $7.812\cdot10^{-3}$ | 7 | 2.1 |
| int8 | 1 | $127$ | $-128$ | — | — | 256 levels |

The structure behind the table, which is what to remember rather than the digits: a float is sign + exponent + mantissa; the **exponent field sets the range**, the **mantissa sets the precision**. fp32 and fp16 both have 2 bytes' worth of difference spent almost entirely on the exponent: fp32 has 8 exponent bits, fp16 has 5. **bf16 is fp32 with 16 mantissa bits chopped off** — same 8-bit exponent, so the same $3.4\cdot10^{38}$ ceiling and the same $1.2\cdot10^{-38}$ floor, but only 8 significant bits. So:

- **bf16 is less precise than fp16 and much harder to break.** fp16 overflows at 65504, which activations and especially gradients reach, so fp16 training needs *loss scaling* (multiply the loss by ~$2^{15}$ before backward, divide the gradients after) to move small gradients into fp16's representable range. bf16 needs none of that [S85]. On Apple Silicon and modern NVIDIA hardware, use bf16 and stop thinking about it.
- Mixed precision means **weights and the optimiser state stay fp32**; only the forward and backward activations are in the narrow type. Memory saving is on activations, which is where it is needed (note 01: activations, not parameters, limit batch size).

### Post-training int8 quantisation

Map a real interval onto the 256 integers. The **affine** scheme [S87]:
$$q = \mathrm{round}(x/s) + z, \qquad \hat x = (q - z)\, s .$$
Requiring the endpoints $[x_{\min}, x_{\max}]$ to map onto $[q_{\min}, q_{\max}] = [-128, 127]$ gives
$$s = \frac{x_{\max} - x_{\min}}{q_{\max} - q_{\min}}, \qquad z = q_{\min} - \mathrm{round}(x_{\min}/s).$$
$z$ is rounded to an integer on purpose: it makes real zero exactly representable, which matters because zero padding must quantise to exactly zero or every padded convolution acquires a bias. **Symmetric** quantisation fixes $z = 0$ and $s = \max|x| / 127$: half the levels are wasted on a one-sided tensor, but the arithmetic drops a term, so weights are usually symmetric and activations asymmetric.

Error analysis. Rounding to the nearest of a grid of spacing $s$ bounds the error by $s/2$, and for a smooth distribution the error is close to uniform on $[-s/2, s/2]$, so its RMS is $s/\sqrt{12}$. Measured on 4096 samples of $\mathcal N(0, 0.1^2)$ (`deploy_optimize.quantization_error`):

| | scale $s$ | zero point | max error | bound $s/2$ | RMS error | $s/\sqrt{12}$ | SNR |
|---|---|---|---|---|---|---|---|
| symmetric | $3.230\cdot10^{-3}$ | 0 | $1.615\cdot10^{-3}$ | $1.615\cdot10^{-3}$ | $9.381\cdot10^{-4}$ | $9.323\cdot10^{-4}$ | 40.5 dB |
| asymmetric | $3.214\cdot10^{-3}$ | $-1$ | $1.606\cdot10^{-3}$ | $1.607\cdot10^{-3}$ | $9.316\cdot10^{-4}$ | $9.277\cdot10^{-4}$ | 40.6 dB |

The max error sits exactly on the bound and the RMS within 1 % of the uniform prediction, which is the check that the implementation is right. The quantised integers agree with `torch.quantize_per_tensor` on 100 % of entries.

**Where it breaks: outliers.** The scale is set by the largest magnitude in the tensor, so one extreme weight costs every other weight resolution. Adding a single value of $5.0$ to that same $\sigma = 0.1$ tensor drops the SNR from **40.5 dB to 21.0 dB** — a factor of 9 in error, from one entry out of 4096. This is exactly why per-tensor int8 fails on large language models, whose activations have systematic outlier channels, and why the working recipes are per-*channel* scales, a clipped calibration range (choose $s$ to minimise KL or MSE rather than to cover the max), or keeping the outlier channels in fp16.

### Pruning, and what it actually buys

**Magnitude pruning**: set the smallest weights to zero and retrain the rest. *Global* (one threshold over all layers) beats per-layer, because layers differ in how much they need.

On the toy in `deploy_optimize.py` — a 3-layer MLP on a 20-input, 3-class problem — **95 % of the weights can be removed with no loss of test accuracy** (0.886 dense, 0.916 pruned). That is a statement about the network being far larger than the task needs, which is the normal situation and the reason pruning works at all.

What it buys is size, not speed. Unstructured sparsity leaves a dense tensor full of zeros; a dense matmul kernel multiplies them anyway. The compressed download shrinks (a sparse format stores only the survivors), the FLOPs do not. **Structured** pruning — removing whole channels, heads or blocks — changes the tensor shapes and therefore does speed up any kernel, at a worse accuracy-per-parameter ratio.

Combined with int8, `quantize_model_weights` on the pruned model gives **22.3 KiB fp32 → 5.6 KiB int8, 4.0×** (4× minus a scale and zero point per tensor), of which 80 % of the bytes are zeros that a sparse format would also remove.

### The lottery ticket hypothesis — and a negative result

Frankle & Carbin [S84]: a dense network contains a sparse subnetwork which, **trained from the original initialisation**, matches the dense network. The claimed sharpness is that the *initialisation* is part of the ticket: rewind the survivors to their initial values and it works; redraw them and it does not.

`deploy_optimize.lottery_ticket_sweep` runs exactly that comparison at 80 % sparsity over 5 seeds:

| | test accuracy |
|---|---|
| dense | $0.885 \pm 0.013$ |
| pruned, weights **rewound** to init | $0.889 \pm 0.032$ |
| pruned, weights **reinitialised** | $0.896 \pm 0.025$ |
| rewind − reinit | $-0.007 \pm 0.008$ (standard error $0.004$) |

**This does not reproduce the effect**, and the difference is 1.9 standard errors in the *opposite* direction. That is a fact about this experiment, not about the paper: [S84] reports the effect for heavily over-parameterised vision networks under *iterative* pruning over many rounds, and this is one-shot pruning of a small MLP on a nearly linear problem — where, as the 95 % result above shows, there is no capacity pressure for a ticket to matter at all.

It is kept in the notes because it is the honest outcome and because it is the pitfall assignment 2 warns about from the other side: **a single seed would have "shown" whichever ordering it happened to draw** — at 50 % sparsity reinit wins by 0.014, at 80 % rewind wins by 0.003. Report $n \ge 3$ seeds with a spread, or report nothing.

### Throughput, batch size, warmup

- **Data loading is the usual bottleneck, not the GPU.** Symptom: GPU utilisation oscillating between 0 and 100 %. Fixes in order: `num_workers > 0`, `pin_memory=True`, `persistent_workers=True`, `prefetch_factor`, decode-once-cache-tensors for small datasets, and doing augmentation on the GPU.
- **Larger batches** improve hardware utilisation and reduce gradient variance, which lets you raise the learning rate — the **linear scaling rule**: multiply the LR by the same factor as the batch size [S86]. It stops working at very large batches, where the gradient is already nearly exact and further averaging buys nothing.
- **Warmup** exists because the linear rule's target LR is unstable in the first steps. [S86] ramps linearly over the first few epochs; note 01 gives the Adam-specific reason (the second-moment estimate is built from too few samples early on).
- **Inference warmup** is a different thing with the same name: the first forward pass after loading pays for lazy kernel compilation, autotuning and memory-pool allocation, so benchmarking without discarding the first few iterations reports a number several times too slow.

### Publishing the dataset: FAIR

If the project is *Bring your own data*, publishing the dataset earns a bonus point [S12], and Lecture 12 gives the standard for it: **FAIR** [S89] — Findable (a persistent identifier and rich metadata; a Zenodo DOI is the cheap route), Accessible (retrievable by that identifier over an open protocol, with metadata surviving even if the data is withdrawn), Interoperable (a formal, shared vocabulary; standard file formats), Reusable (a **clear licence**, provenance, and domain-relevant standards). The licence is the one people forget and the one that decides whether the dataset is usable at all — see the data card in note 11 [S90].

## Architecture sketch

The path from checkpoint to demo, and where each optimisation applies:

```
best.pt (fp32)                                             22.3 KiB
   |
   |  model.eval(); torch.no_grad()             <- forgetting this is bug #1
   v
optional: magnitude prune -> retrain             80-95 % zeros, same accuracy
   |
   |  optional: int8 quantise (per-channel)      4.0x smaller, ~40 dB SNR
   v
torch.onnx.export(model, example, "m.onnx",      <- verify numerically vs torch
                  dynamic_axes={"x": {0: "batch"}})
   |
   +---> ONNX Runtime (CPU / CoreML)  ---> FastAPI + batching ---> Docker ---> a URL
   |
   +---> ONNX Runtime Web / TF.js     ---> static page on GitHub Pages
   |                                       weights fetched from a GH release
   +---> Gradio / Streamlit           ---> Hugging Face Space        <- fastest route
```

**Worked example: does the model fit in a browser tab?** A ResNet-18 has $11.7\cdot10^6$ parameters. fp32: $11.7\cdot10^6 \times 4 = 46.8$ MB, too much for a page anyone will wait for. int8: $11.7$ MB, plus per-channel scales — acceptable over a fast link, marginal on mobile. Prune to 80 % sparsity first and store sparsely: roughly $0.2 \times 11.7 = 2.3$ MB of values plus indices, call it 4–5 MB. Or: use a MobileNetV3-Small backbone ($2.5\cdot10^6$ parameters, $2.5$ MB at int8) and accept a few points of accuracy. The arithmetic is $\text{bytes} = \text{params} \times \text{bytes per param}$ and it decides the architecture, so do it in assignment 1, not in January.

**Worked example: the quantisation grid.** A weight tensor with $x_{\max} = 0.41$, $x_{\min} = -0.41$, symmetric: $s = 0.41/127 = 3.23\cdot10^{-3}$. A weight of $0.0500$ becomes $\mathrm{round}(0.05/0.00323) = \mathrm{round}(15.48) = 15$, dequantised $15 \times 0.00323 = 0.04845$ — an error of $1.55\cdot10^{-3}$, inside the $s/2 = 1.615\cdot10^{-3}$ bound. Now suppose one weight is $5.0$: $s$ becomes $5.0/127 = 0.0394$, and that same $0.0500$ becomes $\mathrm{round}(1.27) = 1 \to 0.0394$, error $1.06\cdot10^{-2}$, seven times worse. One number moved the whole grid.

## Pitfalls

- Demo works locally, 500s in the container $\to$ the model file was in `.gitignore` or fetched from a path that does not exist in the image $\to$ fetch weights from a release URL at startup and fail loudly if the checksum does not match.
- Inference results differ from the evaluation script $\to$ `model.eval()` missing (dropout on, BN using batch statistics) or a different preprocessing path in the serving code $\to$ one preprocessing function, imported by both; a test that asserts train-time and serve-time preprocessing agree on a fixed input.
- ONNX export succeeds, outputs are wrong $\to$ Python control flow or a shape was traced as a constant $\to$ `dynamic_axes`, and a numerical comparison against PyTorch on 3 inputs of different batch sizes as a test.
- int8 model's accuracy collapses although the weight error looked tiny $\to$ per-tensor scale set by an outlier, or the *activations* were calibrated on unrepresentative data $\to$ per-channel weight scales, calibrate activations on a few hundred real training samples, and compare accuracy fp32 vs int8 on the validation split before shipping.
- fp16 training produces NaN in the first epoch, bf16 does not $\to$ fp16 overflows at 65504 $\to$ bf16, or fp16 plus a gradient scaler.
- "The GPU is only 30 % utilised" $\to$ the data loader, not the model $\to$ `num_workers`, `pin_memory`, and time one epoch with the model replaced by `lambda x: x.sum()` to measure the loader alone.
- Benchmarked latency is 5x worse than in production $\to$ the first iterations paid for kernel compilation and allocation $\to$ discard the first 10 iterations, then report a median and a p95 over at least 100.
- Pruned to 90 % and the inference time did not change $\to$ unstructured sparsity in a dense kernel $\to$ expect a smaller download, not a faster model; use structured pruning or a sparse runtime if latency is the goal.
- Demo runs, but only on your laptop's GPU $\to$ the grader has neither your GPU nor your CUDA $\to$ the demo must run on CPU, or in the browser; test it with `CUDA_VISIBLE_DEVICES=""`.
- Presentation demo fails live $\to$ network, dependency or cold start $\to$ [S14] says record a screencast and embed it; in a four-minute slot a live demo is not worth the risk.

## Questions

There is no written exam in this course (see [`00-exam-focus.md`](00-exam-focus.md)). These are the questions worth being able to answer about your own project, because they are what a grader looking at the demo and the report will ask.

1. Your model has $8.4\cdot10^6$ parameters. Give the download size in fp32, fp16 and int8, and say which of the three deployment routes each allows.
<details><summary>Answer</summary>
fp32 $8.4\cdot10^6\times4 = 33.6$ MB; fp16 $16.8$ MB; int8 $8.4$ MB plus per-channel scales (negligible). 33.6 MB is fine for a server or a container and painful in a browser; 16.8 MB is a borderline browser payload; 8.4 MB is comfortable, cacheable, and works on mobile. Note that these are *weights only* — the runtime (ONNX Runtime Web is a few MB of WASM) and the activations are extra.
</details>

2. Why does bf16 need no loss scaling when fp16 does, given that bf16 is the *less* precise format?
<details><summary>Answer</summary>
Loss scaling exists to fix *range*, not precision. fp16 has a 5-bit exponent: it overflows at 65504 and its smallest normal is $6.1\cdot10^{-5}$, so small gradients underflow to zero. Multiplying the loss by a large constant before `backward` shifts the gradients into the representable band, and the gradients are divided back before the optimiser step. bf16 keeps fp32's 8-bit exponent, hence the same $3.4\cdot10^{38}$ ceiling and $1.2\cdot10^{-38}$ floor, so nothing over- or underflows; it pays in mantissa bits (7 vs 10), which costs precision per value but is averaged away over a minibatch. [S85]
</details>

3. Derive the affine quantisation scale and zero point, and explain why $z$ is rounded to an integer.
<details><summary>Answer</summary>
Map $[x_{\min}, x_{\max}]$ affinely onto $[q_{\min}, q_{\max}]$: the slope is $s = (x_{\max}-x_{\min})/(q_{\max}-q_{\min})$ and the offset follows from $q_{\min} = x_{\min}/s + z$, i.e. $z = q_{\min} - x_{\min}/s$. Rounding $z$ to an integer means the real value $0$ maps to the exact integer $z$ and back to exactly $0$. That matters because zero-padding, masking and ReLU outputs produce exact zeros in quantity; if $0$ dequantised to a small nonzero, every padded convolution would pick up a systematic bias proportional to the amount of padding.
</details>

4. A single outlier weight costs 19.5 dB of SNR in the measurement above. Explain the mechanism and give two fixes.
<details><summary>Answer</summary>
Per-tensor symmetric quantisation sets $s = \max|x|/127$, so the step size is proportional to the largest magnitude in the tensor. An outlier 50× the typical magnitude makes $s$ 50× larger, and every ordinary weight is now rounded to a 50× coarser grid; the error power grows as $s^2$, hence roughly $20\log_{10}50 \approx 34$ dB of headroom lost, partly offset because the outlier also raises the signal power. Fixes: (i) per-channel scales, so the outlier only degrades its own channel; (ii) clip the calibration range — choose $s$ to minimise MSE or KL over the distribution rather than to cover the maximum, accepting saturation of the outlier; (iii) keep the outlier channels in fp16 and quantise the rest.
</details>

5. You prune to 90 % sparsity and the inference latency is unchanged. Is the pruning useless? What would have changed it?
<details><summary>Answer</summary>
Not useless: the *compressed* model is much smaller, which is what matters for a browser or mobile deployment, and a sparse storage format realises that. But a dense GEMM kernel does the same number of multiply-accumulates whether or not the operands are zero, so latency is unchanged. To change latency you need either structured pruning (remove whole channels, heads or layers, so the tensor shapes actually shrink), a runtime with sparse kernels and enough sparsity to beat their overhead (typically > 90 % and even then modest), or hardware with structured-sparsity support (e.g. 2:4).
</details>

6. Your lottery-ticket experiment gives rewind 0.889 and reinit 0.896. What can you claim?
<details><summary>Answer</summary>
Nothing about the hypothesis. Over 5 seeds the difference is $-0.007 \pm 0.008$, a standard error of $0.004$, i.e. 1.9 SE — and in the direction opposite to the hypothesis, so it is neither evidence for nor a refutation of [S84]. What you *can* say is that the experiment as run cannot detect the effect: the network tolerates 95 % sparsity with no accuracy cost, so it is far larger than the task needs and there is no capacity pressure for the initialisation to matter; and [S84]'s protocol is iterative pruning of large vision models, not one-shot pruning of an MLP. The honest report states the numbers, the spread, and that the setup differs from the paper's.
</details>

7. Which demo-application route would you pick for (a) a 3 MB image classifier, (b) a 400 MB fine-tuned language model, (c) an RL agent in a simulated environment?
<details><summary>Answer</summary>
(a) In-browser with ONNX Runtime Web on a GitHub Pages site: no server, no cold start, no cost, and it matches [S14]'s own recommendation. (b) Too large for a browser; a Gradio app on a Hugging Face Space, or a Docker container with the weights fetched from a release — and quantise to int8 first, which takes 400 MB to 100 MB. (c) The interesting artefact is the *behaviour*, not a single inference, so a CLI or Gradio app that runs one episode and returns a rendered video or an animated GIF, with the environment bundled so it needs no GPU.
</details>

8. Your ONNX export runs and produces plausible but slightly different outputs from PyTorch. How do you localise the cause?
<details><summary>Answer</summary>
First quantify: max absolute difference over a batch. Below ~$10^{-5}$ it is floating-point reassociation and is fine. Above that, bisect the graph — export prefixes of the model and compare each output tensor, or register hooks and dump intermediate activations from PyTorch, then run the ONNX graph with those intermediates as outputs. The usual causes are a traced shape or control-flow branch baked in (test with a different batch size: if the difference appears only off the traced shape, that is it), a BatchNorm exported in training mode (`model.eval()` before export), and an op whose ONNX implementation differs at the edges (interpolation modes, `align_corners`, padding conventions).
</details>

## Code

`src/py/deploy_optimize.py`: `float_formats()` (range, epsilon and mantissa width of fp32/fp16/bf16/int8, read from `torch.finfo`); `quant_params(x, symmetric)` and `quantize`/`dequantize` (the affine scheme, agreeing with `torch.quantize_per_tensor` on every entry); `quantization_error(x)` (max and RMS error against the $s/2$ and $s/\sqrt{12}$ predictions, plus SNR); `quantize_model_weights(model)` (size before and after). `test_deploy_optimize.py` checks the format facts against `torch.finfo`, the quantiser against `torch.quantize_per_tensor`, and the error against its analytic bound.

`src/py/pruning.py`: `magnitude_masks(model, sparsity)` (global unstructured pruning), `apply_masks`, `sparsity_of`; `lottery_ticket(sparsity, steps, seed)` (dense → prune → rewind vs reinit) and `lottery_ticket_sweep(sparsity, seeds)` (the same over several seeds with mean, std and standard error). `test_pruning.py` pins the negative lottery-ticket result so that an apparent future "reproduction" is noticed rather than believed.

`python src/py/deploy_optimize.py` and `python src/py/pruning.py` print every table in this note.

`src/py/shape_formulas.py` gives the parameter-count helpers used for the download-size arithmetic above.

Nothing here writes an ONNX file: `onnx` and `onnxruntime` are not in the repo venv, and the conventions forbid downloads at test time. The export line is in the sketch above; run it in the project repository, not here.

## References

- **Lecture 12** [S4], *Serving, Optimizing, and Practical Aspects* — the chapter list this note follows.
- Micikevicius et al. (2018), *Mixed precision training of deep neural networks* [S85] — loss scaling, and why fp16 needs it.
- Jacob et al. (2018), *Quantization and training of neural networks for efficient integer-arithmetic-only inference* [S87] — the affine scheme, the exact-zero requirement, per-channel scales.
- Frankle & Carbin (2019), *The lottery ticket hypothesis* [S84]; Frankle et al. (2019), *Stabilizing the lottery ticket hypothesis* (rewinding to an early step rather than to init).
- Goyal et al. (2018), *Accurate, large minibatch SGD* [S86] — the linear scaling rule and gradual warmup.
- ONNX and ONNX Runtime [S88]. TensorFlow.js, Gradio, Streamlit, Hugging Face Spaces, Docker — all named in assignment 3 [S14].
- Wilkinson et al. (2016), *The FAIR guiding principles* [S89]; <https://www.go-fair.org/fair-principles/>.
- Goodfellow, Bengio, Courville [S15], ch. 12.1 (large-scale deep learning: quantisation, model compression, dynamic structure).
