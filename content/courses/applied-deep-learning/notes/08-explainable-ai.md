# 08 Explainable AI

Explainable AI (XAI) is the set of methods that answer "which parts of the input, or which learned concepts, drove this prediction" for a model whose computation is too large to read. The main practical use in a project is debugging: a classifier at 98% test accuracy that attends to the background, a watermark or a text tag is exploiting a shortcut (Clever Hans effect) and will fail on deployment data; an attribution map exposes this. Secondary uses are trust and communication with domain experts and regulation (GDPR right to explanation, EU AI Act transparency duties for high-risk systems). This note covers gradient-based attributions (saliency, integrated gradients, Grad-CAM), perturbation methods (occlusion, LIME, SHAP), why attention is not an explanation, concept-based and counterfactual methods, and, most importantly, how to test whether an explanation method says anything about the model at all.

## Concepts

### Taxonomy

- Intrinsic (the model is interpretable by construction: linear models, small trees, prototype networks, attention with constraints) vs post-hoc (a separate procedure explains a trained black box; everything below).
- Local (explain one prediction $f(x)$) vs global (explain the model: which features matter on average, which concepts a neuron encodes).
- Model-specific (needs gradients or internal activations: saliency, IG, Grad-CAM, DeepSHAP) vs model-agnostic (only queries $f$: occlusion, LIME, KernelSHAP, counterfactual search).

Notation: classifier $f:\mathbb{R}^d\to\mathbb{R}^C$, class score $f_c(x)$ (logit, not softmax probability, unless stated), attribution $a\in\mathbb{R}^d$ with $a_i$ = contribution of input feature $i$ (pixel, token, tabular column).

### Gradient-based attributions

Vanilla saliency (Simonyan, Vedaldi, Zisserman 2014): $a_i = |\partial f_c(x)/\partial x_i|$, the first-order Taylor coefficient of $f_c$ around $x$; for images take the max over colour channels. One backward pass. Problems: the gradient of a ReLU network is piecewise constant and changes abruptly with $x$, so the map is noisy and high-frequency; it measures local sensitivity, not contribution (a saturated feature has zero gradient but may have driven the decision); for a linear model $f = w^\top x$ it returns $|w_i|$ regardless of $x$.

Gradient $\times$ input: $a_i = x_i\,\partial f_c/\partial x_i$. For a linear model this gives $w_i x_i$, the actual contribution of feature $i$, and $\sum_i a_i = f(x)$ (exact for a bias-free ReLU network at the same activation pattern, since $f$ is locally linear and homogeneous). Sign is meaningful (for/against class $c$).

SmoothGrad (Smilkov et al. 2017): $\hat a(x) = \frac{1}{n}\sum_{k=1}^n a(x + \epsilon_k)$, $\epsilon_k\sim\mathcal N(0,\sigma^2 I)$, $n\approx 50$, $\sigma\approx 10$-$20\%$ of the input range. Averages out the high-frequency noise of the gradient; cost $n$ backward passes. Applicable on top of any gradient method.

Integrated gradients (Sundararajan, Taly, Yan 2017). Choose a baseline $x'$ (an input that "means absence", $f(x')\approx 0$) and integrate the gradient along the straight path from $x'$ to $x$:

$$
\mathrm{IG}_i(x) = (x_i - x_i')\int_0^1 \frac{\partial f(x' + \alpha(x - x'))}{\partial x_i}\,d\alpha
\ \approx\ (x_i - x_i')\,\frac{1}{m}\sum_{k=1}^{m} \frac{\partial f\big(x' + \tfrac{k}{m}(x - x')\big)}{\partial x_i},
$$

with $m = 20$-$300$ steps (Riemann sum, midpoint or right endpoint). Completeness: by the fundamental theorem of calculus along the path $\gamma(\alpha) = x' + \alpha(x - x')$,

$$
\sum_i \mathrm{IG}_i(x) = \int_0^1 \nabla f(\gamma(\alpha))^\top \gamma'(\alpha)\,d\alpha = f(x) - f(x'),
$$

so the attributions sum to the change in output, and the Riemann error $|\sum_i \mathrm{IG}_i - (f(x) - f(x'))|$ is a built-in convergence check (`completeness_error` in the reference code; increase $m$ until it is a few percent of $|f(x)-f(x')|$). Axioms: sensitivity (if $x$ and $x'$ differ in one feature and $f$ differs, that feature gets non-zero attribution; vanilla gradient violates this at saturated ReLUs), implementation invariance (two networks computing the same function get the same attributions; methods that use internal activations, such as LRP or DeepLIFT, can violate it), linearity, symmetry-preservation. IG is the unique path method satisfying these plus symmetry with the straight-line path. Baseline choice matters because IG explains $f(x) - f(x')$: black image (attributes nothing to black pixels, since $x_i - x_i' = 0$), blurred copy of $x$ (explains the high-frequency content), uniform or Gaussian noise averaged over several draws (Expected Gradients), for text the all-`[PAD]` or all-zero embedding, for tabular data the training mean or a background sample set.

### Grad-CAM (Selvaraju et al. 2017 [S74])

Class activation map from the feature maps $A^k\in\mathbb{R}^{H\times W}$, $k = 1..K$, of a chosen convolutional layer:

$$
\alpha_k^c = \frac{1}{Z}\sum_{i,j}\frac{\partial y^c}{\partial A^k_{ij}},\qquad
L^c_{\text{Grad-CAM}} = \mathrm{ReLU}\Big(\sum_k \alpha_k^c A^k\Big)\in\mathbb{R}^{H\times W},\qquad Z = HW,
$$

then bilinearly upsample $L^c$ from $H\times W$ to the input resolution and overlay. The weight $\alpha_k^c$ is the global-average-pooled gradient, i.e. the importance of channel $k$ for class $c$; the ReLU keeps only regions that increase $y^c$. For a network ending in global average pooling followed by a linear layer with weights $W\in\mathbb{R}^{C\times K}$, $\partial y^c/\partial A^k_{ij} = W_{ck}/Z$ exactly, so $\alpha_k^c = W_{ck}/Z$ and Grad-CAM reduces to CAM (Zhou et al. 2016). Which layer: the last convolutional layer, the deepest one with spatial layout, trades semantic content (high) against resolution (low, e.g. $7\times7$ for a $224$ input in ResNet-50, $16\times16$ in the `ShapeCNN`); earlier layers give sharper but less class-specific maps. Guided Grad-CAM multiplies with guided backprop for pixel-level detail, but guided backprop fails the sanity checks below. Grad-CAM is coarse, class-discriminative and cheap (one forward, one backward), and is the default for CNN debugging.

PyTorch implementation: register a forward hook on the layer, `layer.register_forward_hook(lambda m, i, o: store["act"] = o)`, and a hook on the output tensor, `o.register_hook(lambda g: store["grad"] = g)` (or `register_full_backward_hook` on the module), run `model(x)[0, c].backward()`, then `alpha = grad.mean(dim=(2, 3), keepdim=True)`, `cam = relu((alpha * act).sum(1))`, `F.interpolate(cam[:, None], size=x.shape[-2:], mode="bilinear")`. Put the model in `eval()` so batch-norm uses running statistics and dropout is off; remove hooks afterwards.

### Perturbation methods

Occlusion (Zeiler & Fergus 2014): slide a grey/black/mean patch of size $p\times p$ (stride $s$) over the image and record $f_c(x_{\text{occluded}})$; attribution of a region = drop in score. Model-agnostic, faithful by construction (it measures what the model does when the evidence is removed), but $O((HW/s^2))$ forward passes and the result depends on patch size and fill value, and occluded images are off the data manifold.

LIME (Ribeiro, Singh, Guestrin 2016 [S71]): local linear surrogate. Represent $x$ by $d'$ interpretable binary components $z\in\{0,1\}^{d'}$ (superpixels present/absent, words present/absent). Sample $n\approx 1000$ masks $z_k$, compute $f_c(x_{z_k})$ with the absent components replaced by a fill value, weight each sample by a kernel $\pi(z_k) = \exp(-D(x, x_{z_k})^2/\sigma^2)$, and fit a sparse linear model $g(z) = w^\top z$ by weighted least squares with an $\ell_1$ penalty (or top-$K$ feature selection). $w_j$ is the attribution of component $j$. Explanations depend on the segmentation, the fill value, the kernel width and the random masks, so they are unstable across runs; the surrogate can be a poor fit if $f$ is strongly non-linear within the kernel width.

### SHAP (Lundberg & Lee 2017 [S73])

Shapley value (1953) from cooperative game theory: features are players, $v(S) = f(S)$ is the model output when only the features in $S\subseteq F$ are "present" (the others are marginalised out or set to a baseline), and the attribution of feature $i$ is its average marginal contribution over all orderings:

$$
\phi_i = \sum_{S\subseteq F\setminus\{i\}} \frac{|S|!\,(|F| - |S| - 1)!}{|F|!}\,\big[f(S\cup\{i\}) - f(S)\big].
$$

The weight is the probability that, in a uniformly random ordering of the $|F|$ features, exactly the set $S$ precedes $i$. Axioms that uniquely determine $\phi$: efficiency ($\sum_i\phi_i = f(F) - f(\emptyset)$, the same completeness as IG), symmetry (interchangeable features get equal $\phi$), dummy (a feature that never changes $f$ gets $0$), linearity. Cost: $2^{|F|}$ evaluations of $f$, infeasible beyond $|F|\approx 20$. Approximations: KernelSHAP = LIME with the specific kernel $\pi(z) \propto \frac{|F| - 1}{\binom{|F|}{|z|}|z|(|F| - |z|)}$ and no regularisation, whose weighted least-squares solution is the Shapley value (model-agnostic, $\sim 2|F| + 2048$ samples); DeepSHAP / DeepLIFT propagates contributions layer by layer with a "rescale rule" relative to the baseline activations, one backward-like pass, approximate for non-linear interactions; TreeSHAP is exact and polynomial for tree ensembles; sampling permutations. Connection to IG: the Aumann-Shapley value is the continuous extension of the Shapley value to games with fractional participation, obtained by integrating the gradient along the diagonal path from $x'$ to $x$; IG is exactly the Aumann-Shapley value with baseline $x'$ (Sundararajan et al. 2017, Sundararajan & Najmi 2020). The difference is what "absent" means: Shapley/KernelSHAP marginalise over a background distribution (interventional or observational), IG interpolates deterministically between two points.

### Attention is not explanation

Jain & Wallace (2019) tested attention weights in RNN classifiers as explanations and found (i) attention weights correlate weakly with gradient-based and leave-one-out feature importance, and (ii) for most instances one can find an alternative attention distribution, far from the learned one in Jensen-Shannon divergence, that yields the same prediction: the attention is not necessary for the output. Reasons: attention weights are over contextualised hidden states, not over inputs, so a large weight on position $t$ says nothing about which input tokens $h_t$ encodes; multi-head and multi-layer attention mixes further; the value vectors' norms matter as much as the weights (Kobayashi et al. 2020). Wiegreffe & Pinter (2019) reply that attention can be an explanation if it is tested as such (adversarial attention trained end-to-end is harder to find). Practical rule: treat attention maps as one diagnostic, validate against a perturbation method, and use attention rollout or gradient-weighted attention (Chefer et al. 2021) for transformers rather than raw last-layer weights.

### Concept-based methods and counterfactuals

TCAV (Kim et al. 2018): a global, concept-level method. Collect positive examples of a human concept (stripes, wheels) and random negatives, take activations at layer $l$, train a linear classifier; its normal vector $v_C^l$ is the concept activation vector. Directional derivative $S_{C,c,l}(x) = \nabla f_c(a^l(x))^\top v_C^l$ measures how much moving activations toward the concept raises class $c$; the TCAV score is the fraction of class-$c$ inputs with positive derivative, tested against random CAVs for significance. Answers "does the model use stripes for zebra", not "which pixels". Related: network dissection (Bau et al. 2017), concept bottleneck models (intrinsic).

Counterfactual explanations (Wachter et al. 2017): the smallest change to $x$ that flips the prediction, $x^* = \arg\min_{x'} d(x, x') + \lambda\,\ell(f(x'), y_{\text{target}})$, with $d$ sparse ($\ell_1$) and optionally constrained to plausible inputs (actionable features, data-manifold via a generative model). For images this is an adversarial example unless the change is restricted to a semantic direction (e.g. a generator's latent space); for tabular decisions (loan denied: "income $+3$k would flip it") it is the most user-facing explanation form. Distinguish from adversarial examples by the plausibility constraint and from prototypes/influence functions (which training points caused this decision, Koh & Liang 2017).

### Evaluating explanations

Sanity checks (Adebayo et al. 2018). Model randomisation: re-initialise the weights of the network layer by layer from the top (cascading) or one layer at a time and recompute the map; an explanation of the model must change when the model is destroyed. Data randomisation: train on permuted labels; the map should degrade. Result: vanilla gradient, gradient $\times$ input, Grad-CAM and IG pass; guided backprop and guided Grad-CAM produce nearly identical, edge-detector-like maps for a random network, so they reflect the input, not the model. Any new method should be run through both checks before use.

Deletion / insertion curves (Petsiuk et al. 2018, RISE). Sort pixels by attribution; deletion: progressively replace the top-attributed pixels with a baseline and record $f_c$; a good explanation makes the score drop fast (small area under the curve). Insertion: start from the baseline and add pixels in attribution order; the score should rise fast (large AUC). Model-agnostic, quantitative, but off-manifold inputs and the choice of baseline influence the numbers; compare methods on the same model and protocol only.

Pointing game / mass inside mask. When a ground-truth region is known (bounding box, segmentation, or the synthetic shape mask in the reference data), measure whether the argmax of the map lies inside it (pointing accuracy) or the fraction of attribution mass inside the region, $\sum_{i\in M}|a_i| / \sum_i |a_i|$ (`mass_inside`). This measures plausibility (agreement with the human notion of evidence), which is only equal to faithfulness if the model actually uses that region; a model relying on a shortcut correctly gets a low score, and the metric cannot tell the two cases apart without an additional deletion test.

### Limits

- Faithfulness vs plausibility: a faithful explanation describes what the model computes; a plausible one looks right to a human. Users prefer plausible maps, so methods drift toward producing them (edge detectors), which is precisely what the sanity checks catch.
- Saliency of a linear model: $|\partial f/\partial x_i| = |w_i|$ for every $x$, so vanilla saliency explains the model, not the instance; the instance-level contribution is $w_i x_i$. IG with $x' = 0$ gives $w_i x_i$ exactly; see the worked example.
- Adversarial manipulation: explanations can be attacked while keeping the prediction. Ghorbani et al. (2019) perturb $x$ imperceptibly to move the saliency map arbitrarily; Dombrowski et al. (2019) show that the map's fragility is governed by the curvature of the network (ReLU kinks), and softplus smoothing helps; Slack et al. (2020) build models that behave fairly on the LIME/SHAP perturbation distribution (off-manifold) and unfairly on real data, fooling both methods. Heo et al. (2019) fine-tune a model so that its maps point elsewhere at unchanged accuracy.
- Explanation of a wrong model: every method explains the model as it is. A faithful map of a shortcut learner shows the shortcut, which is the useful case; a faithful map of a model that is right for the wrong reason on this input, or wrong with high confidence, is equally clean-looking. Explanations verify neither correctness nor causality; they localise evidence. Aggregate over many inputs and combine with a held-out test on shifted data before drawing conclusions.
- Practical: attributions on logits and on softmax probabilities differ (softmax saturation kills gradients of confident predictions; attribute the logit or the log-probability); batch-norm in train mode and dropout make maps stochastic; input normalisation must be accounted for in the baseline; the completeness check should always be reported with IG.

## Architecture sketch

`ShapeCNN` from `cnn_shapes.py` (conv3x3(16)-BN-ReLU $\times 2$, maxpool, conv3x3(32)-BN-ReLU, global average pool, linear $32\to3$; `width=16`), input $x\in[0,1]^{1\times32\times32}$, three classes. The reference `run` attributes the logit $f_c$ (pre-softmax), not the probability.

```
saliency(model, x, target):
  x [1, 1, 32, 32] requires_grad
    -> conv3x3(16)-BN-ReLU -> [1, 16, 32, 32]
    -> conv3x3(16)-BN-ReLU -> [1, 16, 32, 32]
    -> maxpool2            -> [1, 16, 16, 16]
    -> conv3x3(32)-BN-ReLU -> [1, 32, 16, 16]   <- A^k for Grad-CAM (forward hook stores act,
    -> global avg pool     -> [1, 32]              act.register_hook stores dL/dA [1, 32, 16, 16])
    -> linear(32 -> 3)     -> [1, 3]  logits
  logits[0, target].backward()
  x.grad [1, 1, 32, 32] -> abs -> attribution [32, 32]

integrated_gradients(model, x, baseline, target, steps=32):
  alphas [32]                       (k/steps, k = 1..32)
  path = baseline + alphas[:,None,None,None] * (x - baseline)   -> [32, 1, 32, 32]  one batch
  model(path)[:, target].sum().backward()                        -> path.grad [32, 1, 32, 32]
  attr = (x - baseline) * path.grad.mean(0)                      -> [1, 1, 32, 32]
  completeness_error = | attr.sum() - (f(x) - f(baseline)) |     (scalar, should be << |f(x)-f(x')|)

Grad-CAM on the third conv block:
  alpha [1, 32, 1, 1] = grad.mean((2, 3))
  cam   [1, 16, 16]   = relu((alpha * act).sum(1))
  upsample bilinear   -> [1, 32, 32], normalise to [0, 1], overlay on x
```

Cost: saliency = 1 forward + 1 backward; IG with $m = 32$ = one batched forward/backward of 32 images; Grad-CAM = 1 forward + 1 backward with two hooks. With GAP + linear, Grad-CAM's $\alpha_k^c$ equals $W_{ck}/256$ exactly, so the map is the CAM $\mathrm{ReLU}(\sum_k W_{ck} A^k)$.

Worked example: IG for a 1-D linear model $f(x) = wx$. Gradient along the path $\gamma(\alpha) = x' + \alpha(x - x')$ is $f'(\gamma(\alpha)) = w$ for all $\alpha$, so

$$
\mathrm{IG}(x) = (x - x')\int_0^1 w\,d\alpha = w(x - x') = f(x) - f(x'),
$$

completeness holds with zero Riemann error for any $m$. With $w = 2$, $x = 3$, $x' = 0$: $\mathrm{IG} = 6 = f(3) - f(0)$; vanilla saliency gives $|w| = 2$ independent of $x$; gradient $\times$ input gives $6$ too, because it coincides with IG at $x' = 0$ for linear $f$. With $x' = 1$: $\mathrm{IG} = 2\cdot 2 = 4 = f(3) - f(1)$, showing that IG explains the difference to the baseline, not $f(x)$ itself. For a 2-D linear model $f(x) = w_1x_1 + w_2x_2$ the same computation gives $\mathrm{IG}_i = w_i(x_i - x_i')$ and $\mathrm{IG}_1 + \mathrm{IG}_2 = f(x) - f(x')$. For a ReLU network the gradient is piecewise constant along the path and the Riemann sum has error $O(1/m)$ from the kinks, which is what `completeness_error` measures.

## Pitfalls

- Saliency map is uniform speckle with no shape visible -> raw ReLU gradients are high-frequency; the map is the gradient of the softmax probability of a confident prediction (near zero everywhere) -> attribute the logit, use SmoothGrad ($n = 50$, $\sigma = 0.15$) or IG, visualise with a percentile clip (99th) rather than min-max.
- IG completeness error is 30% of $f(x) - f(x')$ -> too few Riemann steps for a network with many ReLU kinks along the path -> raise `steps` from 32 to 128-256 (batched, cheap), or use the trapezoid rule; report the error alongside the map.
- IG attributes nothing to the dark shape on a black background -> baseline $x' = 0$ equals $x$ at those pixels, so $(x_i - x_i') = 0$ -> use a blurred or noise baseline, or a mean-image baseline; average over several random baselines.
- Grad-CAM map is blank (all zeros) for the predicted class -> hook on the wrong tensor (after global average pool, no spatial layout) or the ReLU removed all negative-gradient evidence for a class whose logit is negative -> hook the last conv block's output, check `act.shape == [B, K, H, W]`, inspect the map before the ReLU when debugging.
- Grad-CAM maps look different between two calls on the same input -> model in `train()` mode: batch-norm uses batch statistics of a batch of size 1 and dropout is active -> `model.eval()` before explaining; `torch.no_grad()` must not be active during the backward pass.
- Attribution mass inside the ground-truth mask is high but deletion curve shows no score drop -> the map is plausible but not faithful (e.g. guided backprop acting as an edge detector) -> run the model-randomisation sanity check; switch to IG or Grad-CAM; always pair a plausibility metric with a deletion/insertion test.
- LIME explanations change substantially between runs -> few samples, wide kernel, unstable superpixel segmentation -> increase samples to 2000+, fix the segmentation seed, report explanation variance, or use KernelSHAP with its fixed kernel.
- KernelSHAP takes minutes per image -> $2^{|F|}$ coalitions on pixel features -> explain over $\le 50$ superpixels, cap `nsamples`, or use DeepSHAP / IG for differentiable models.
- Explanations were used to conclude the model "understands shapes" -> explanations localise evidence and cannot certify reasoning; the model may still use shape area or edge count -> test on distribution shifts (scaled, rotated, inverted-contrast shapes) and report accuracy there; explanations are supporting evidence only.
- Hooks accumulate across calls and memory grows -> `register_forward_hook` handles never removed, activations retained with graphs -> keep the handle and call `handle.remove()` in a `finally` block; detach stored tensors after the backward pass.

## Questions

1. Prove the completeness property of integrated gradients and explain why it fails for vanilla gradient $\times$ input on a ReLU network with biases.

<details><summary>Answer</summary>
Let $\gamma(\alpha) = x' + \alpha(x - x')$, $g(\alpha) = f(\gamma(\alpha))$. Then $g'(\alpha) = \nabla f(\gamma(\alpha))^\top(x - x') = \sum_i (x_i - x_i')\partial_i f(\gamma(\alpha))$, and $\int_0^1 g'(\alpha)d\alpha = g(1) - g(0) = f(x) - f(x')$. Swapping sum and integral gives $\sum_i \mathrm{IG}_i = f(x) - f(x')$. Gradient $\times$ input equals $\sum_i x_i\partial_i f(x) = \nabla f(x)^\top x$, which equals $f(x)$ only if $f$ is positively homogeneous of degree 1 on its current linear region, i.e. a bias-free ReLU network; with biases $f(x) = \nabla f(x)^\top x + b_{\text{eff}}(x)$ and the bias term is unattributed.
</details>

2. Show that Grad-CAM on a network ending in global average pooling followed by a linear layer is identical to CAM, and compute $\alpha_k^c$ for the `ShapeCNN`.

<details><summary>Answer</summary>
Let $A^k\in\mathbb{R}^{H\times W}$, $p_k = \frac{1}{HW}\sum_{ij}A^k_{ij}$, $y^c = \sum_k W_{ck}p_k + b_c$. Then $\partial y^c/\partial A^k_{ij} = W_{ck}/(HW)$ for all $i,j$, so $\alpha_k^c = \frac{1}{HW}\sum_{ij}W_{ck}/(HW) = W_{ck}/(HW)$, and $L^c = \mathrm{ReLU}(\sum_k W_{ck}A^k)/(HW)$, the CAM up to a positive constant. For the `ShapeCNN` with $H = W = 16$ after the maxpool: $\alpha_k^c = W_{ck}/256$. Grad-CAM's generality lies in networks with fully connected layers after the conv stack, where the gradient is not constant over positions.
</details>

3. A colleague reports that guided backprop gives the sharpest, most convincing maps for their CNN. What test do you ask for, and what result do you expect?

<details><summary>Answer</summary>
The model-randomisation sanity check (Adebayo et al. 2018): reinitialise the weights from the top layer downward and recompute the maps; also the data-randomisation check with permuted labels. Guided backprop maps are expected to stay nearly unchanged (rank correlation with the trained-model maps stays high), because guided backprop zeroes negative gradients at every ReLU and effectively reconstructs input edges regardless of the weights; it is therefore not an explanation of the model. Vanilla gradient, IG and Grad-CAM maps degrade under randomisation as required. Sharpness is a plausibility property, not a faithfulness one.
</details>

4. Derive the Shapley weights for $|F| = 3$ and compute $\phi_1$ for the game $f(\emptyset) = 0$, $f(\{1\}) = 2$, $f(\{2\}) = 1$, $f(\{3\}) = 0$, $f(\{1,2\}) = 5$, $f(\{1,3\}) = 2$, $f(\{2,3\}) = 1$, $f(\{1,2,3\}) = 6$.

<details><summary>Answer</summary>
Weights $\frac{|S|!(3 - |S| - 1)!}{3!}$: $|S| = 0$: $\frac{0!\,2!}{6} = \frac13$; $|S| = 1$: $\frac{1!\,1!}{6} = \frac16$; $|S| = 2$: $\frac{2!\,0!}{6} = \frac13$. For $i = 1$: $S = \emptyset$: $\frac13(2 - 0) = \frac23$; $S = \{2\}$: $\frac16(5 - 1) = \frac23$; $S = \{3\}$: $\frac16(2 - 0) = \frac13$; $S = \{2,3\}$: $\frac13(6 - 1) = \frac53$. Sum: $\phi_1 = \frac23 + \frac23 + \frac13 + \frac53 = \frac{10}{3}$. Similarly $\phi_2 = \frac13(1) + \frac16(5-2) + \frac16(1-0) + \frac13(6-2) = \frac13 + \frac12 + \frac16 + \frac43 = \frac{7}{3}$, $\phi_3 = \frac13(0) + \frac16(0) + \frac16(0) + \frac13(6 - 5) = \frac13$. Efficiency: $\frac{10}{3} + \frac73 + \frac13 = 6 = f(F) - f(\emptyset)$. Feature 3 gets non-zero credit only through the interaction in the grand coalition.
</details>

5. Explain the difference between "faithful" and "plausible" and give a metric for each, using the synthetic shape dataset where the shape mask is known.

<details><summary>Answer</summary>
Faithful: the explanation reflects the model's computation; metric: deletion curve, remove pixels in attribution order and measure how fast $f_c$ drops (AUC), or the model-randomisation check. Plausible: the explanation agrees with human evidence; metric: `mass_inside(attr, mask)`, fraction of attribution mass inside the shape mask, or the pointing game. On the shape data a model that classifies by the shape's bounding-box aspect ratio would give a faithful map concentrated at the corners of the shape with low mass inside the interior mask; a plausibility metric would call it wrong, a deletion curve would confirm it is right about the model. Report both and interpret disagreements as information about the model.
</details>

6. Your project classifier for X-ray images reaches 96% accuracy. Describe a complete XAI protocol to decide whether it uses a shortcut, and what you would do if it does.

<details><summary>Answer</summary>
(i) Grad-CAM on the last conv block for 100 correctly and 100 incorrectly classified test images; look for consistent mass outside the anatomy (corners, labels, markers). (ii) Quantify: if lung masks are available, compute mass-inside per image and its distribution per class and per source hospital. (iii) Faithfulness: deletion curves with a blurred baseline; occlusion of the suspected marker region and re-measure accuracy; if accuracy drops a lot, the shortcut is confirmed. (iv) Sanity check the attribution method itself once with model randomisation. (v) Counterfactual test: paste the marker onto images of the other class. If a shortcut is found: remove or mask the artefact in preprocessing, crop to the anatomy, re-split the data so that hospital/marker and label are not confounded, add augmentation that destroys the artefact, retrain and repeat the protocol; report the pre/post attribution statistics in the phase-3 assessment.
</details>

7. Why is the attention matrix of a transformer classifier a weak explanation, and what would you use instead for a token-level attribution?

<details><summary>Answer</summary>
Attention weights in layer $l$ distribute over hidden states that already mix all tokens from layers $< l$, so a large weight on position $t$ does not identify input token $t$; multi-head and residual paths bypass attention; the magnitude of the value vectors modulates the effective contribution; Jain & Wallace (2019) show alternative weight configurations with identical outputs and weak correlation with gradient and leave-one-out importances. Alternatives: IG on the input embeddings with a `[PAD]`/zero baseline (completeness-checked), attention rollout (multiply attention matrices with residual identity across layers), gradient-weighted attention (Chefer et al. 2021), or leave-one-token-out perturbation; validate against a deletion test on tokens.
</details>

8. Compare the cost and the faithfulness guarantees of saliency, IG ($m$ steps), Grad-CAM, occlusion (patch $p$, stride $s$ on an $H\times W$ image) and KernelSHAP with $n$ samples.

<details><summary>Answer</summary>
Saliency: 1 backward pass; a first-order local sensitivity, no completeness. IG: $m$ forward+backward passes (batched); completeness $\sum\mathrm{IG} = f(x) - f(x')$, sensitivity, implementation invariance; faithfulness relative to the baseline path only. Grad-CAM: 1 forward + 1 backward; no axiomatic guarantee, passes sanity checks, coarse resolution $H_l\times W_l$. Occlusion: $\lceil H/s\rceil\lceil W/s\rceil$ forward passes (e.g. $32\times32$ image, $p = 8$, $s = 4$: 49 passes); measures the actual effect of removal, so it is faithful to the model under the chosen fill, but off-manifold. KernelSHAP: $n$ forward passes on masked inputs plus a weighted least squares; converges to Shapley values (efficiency, symmetry, dummy, linearity) as $n\to 2^{|F|}$, so guarantees hold only approximately for the sample budget; requires a small number of features (superpixels).
</details>

## Code

`src/py/xai_saliency.py`. `run(steps=200, device=None, seed=0)` trains `cnn_shapes.ShapeCNN` briefly on `cnn_shapes.make_shapes` data with `common.train_loop`, then computes for held-out images `saliency(model, x, target)` $= |\partial f_c/\partial x|$, `integrated_gradients(model, x, baseline, target, steps=32)`, `completeness_error(model, x, baseline, target, attr)` $= |\sum_i \mathrm{IG}_i - (f(x) - f(x'))|$ and `mass_inside(attr, mask)` = fraction of attribution mass inside the shape; it returns `{"losses", "ig_completeness_error", "saliency_mass_inside", "ig_mass_inside"}`. `python src/py/xai_saliency.py` prints the completeness error and the mass-inside fractions for saliency, IG and `grad_cam(model, x, target)` next to the shape's area fraction (all three should exceed it; IG is the sharpest because it is weighted by $x - x'$, which is small on the background). `test_xai_saliency.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)` on the training losses.

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016), ch. 6.5 (back-propagation, the machinery behind every gradient attribution), ch. 9 (CNN feature maps), ch. 7.13 (adversarial training, related to explanation fragility).
- Simonyan, Vedaldi, Zisserman, "Deep Inside Convolutional Networks", ICLR workshop 2014 (saliency) [S70] -- **Lecture 10's reference 16** [S4].
- Smilkov et al., "SmoothGrad: removing noise by adding noise", 2017.
- Sundararajan, Taly, Yan, "Axiomatic Attribution for Deep Networks", ICML 2017 (integrated gradients) [S75]; Sundararajan & Najmi, "The Many Shapley Values for Model Explanation", ICML 2020.
- Selvaraju et al., "Grad-CAM", ICCV 2017; Zhou et al., "Learning Deep Features for Discriminative Localization", CVPR 2016 (CAM) [S74] -- CAM is also a chapter of Lecture 9 [S4].
- Zeiler & Fergus, "Visualizing and Understanding Convolutional Networks", ECCV 2014 (occlusion).
- Ribeiro, Singh, Guestrin, "Why Should I Trust You?", KDD 2016 (LIME) [S71] -- **Lecture 10's reference 6**.
- Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions", NeurIPS 2017 (SHAP) [S73]; Shrikumar et al., "Learning Important Features Through Propagating Activation Differences", ICML 2017 (DeepLIFT).
- Jain & Wallace, "Attention is not Explanation", NAACL 2019; Wiegreffe & Pinter, "Attention is not not Explanation", EMNLP 2019.
- Kim et al., "Interpretability Beyond Feature Attribution: TCAV", ICML 2018.
- Wachter, Mittelstadt, Russell, "Counterfactual Explanations without Opening the Black Box", 2017.
- Adebayo et al., "Sanity Checks for Saliency Maps", NeurIPS 2018.
- Petsiuk, Das, Saenko, "RISE", BMVC 2018 (deletion/insertion) [S72] -- **Lecture 10's reference 3**.
- Ghorbani, Abid, Zou, "Interpretation of Neural Networks is Fragile", AAAI 2019; Dombrowski et al., NeurIPS 2019; Slack et al., "Fooling LIME and SHAP", AIES 2020.
- Geirhos et al., "Shortcut Learning in Deep Neural Networks", Nature MI 2020 (Clever Hans).
- Arrieta et al., "Explainable Artificial Intelligence (XAI): concepts, taxonomies, opportunities and challenges", Information Fusion 2020 [S76], and Molnar, *Interpretable Machine Learning* [S76] -- **Lecture 10's references 2 and 1**, and the source of its taxonomy and of the interpretability-vs-explainability distinction it opens with.
- **Lecture 10** [S4], *Explainable AI*, is the lecture this note covers: why trust a model, the black-box problem, interpretability vs explainability, goals of XAI, explainability vs accuracy, taxonomy, saliency maps, LIME, RISE, XAI in reinforcement learning, quantized bottleneck insertions, understanding GANs (GAN dissection), SHAP. It moved from lecture 12 to lecture 10 between the 2024 and 2025 editions [S6].
