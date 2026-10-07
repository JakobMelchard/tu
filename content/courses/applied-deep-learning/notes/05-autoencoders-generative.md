# 05 Autoencoders, VAE, GAN and diffusion

Generative models learn a distribution $p_\theta(x)$ over data from samples alone, without labels. An autoencoder is the simplest deterministic version: compress $x$ through a bottleneck and reconstruct it, which yields a representation but no sampling procedure. The variational autoencoder (VAE) turns the bottleneck into a latent variable model with a tractable lower bound on the likelihood; the generative adversarial network (GAN) sidesteps likelihood entirely and trains the generator against a classifier; diffusion models learn to invert a fixed Gaussian noising process and currently give the best sample quality at the highest sampling cost. Which family to use in the project depends on whether the goal is a representation, a likelihood, or samples.

## Concepts

### Autoencoder

Encoder $f_\phi: \mathbb{R}^D \to \mathbb{R}^m$, decoder $g_\theta: \mathbb{R}^m \to \mathbb{R}^D$, $m < D$ (undercomplete). Objective: $\min_{\phi, \theta} \mathbb{E}_x \|x - g_\theta(f_\phi(x))\|^2$ (or BCE per pixel for data in $[0, 1]$). The bottleneck forces the code $z = f_\phi(x)$ to keep only what is needed to reconstruct; there is no constraint on the distribution of $z$, so decoding a random $z$ gives garbage (Goodfellow ch. 14 [S15]).

Linear case: with $f(x) = Wx$, $g(z) = W'z$ and squared loss, the optimum spans the same subspace as the top-$m$ principal components (Baldi & Hornik 1989); the columns of $W'$ need not be orthonormal or ordered, but $g \circ f$ equals the PCA projector. A nonlinear AE is a nonlinear generalisation of PCA.

Denoising AE (Vincent et al. 2008): corrupt the input, $\tilde x \sim C(\tilde x \mid x)$ (Gaussian noise or masking), train $g(f(\tilde x)) \approx x$. Prevents the identity solution for overcomplete codes and makes the learned reconstruction field $g(f(\tilde x)) - \tilde x$ point towards the data manifold, proportional to $\nabla_x \log p(x)$ for small Gaussian noise (Alain & Bengio 2014). This is the same object that diffusion models learn.

Sparse AE: add $\lambda \sum_j |z_j|$ or a KL penalty on the mean activation $\bar\rho_j$ towards a small target $\rho$, $\sum_j \mathrm{KL}(\rho \| \bar\rho_j)$, so that few code units are active per input (Goodfellow ch. 14.2.1 [S15]).

### VAE: latent variable model and ELBO

Model: $z \sim p(z) = \mathcal N(0, I)$, $x \sim p_\theta(x \mid z)$ (a decoder network outputs the parameters of a Bernoulli or Gaussian). Marginal likelihood
$$p_\theta(x) = \int p_\theta(x \mid z)\, p(z)\, dz$$
is intractable for a neural decoder, and so is the posterior $p_\theta(z \mid x)$. Introduce an encoder $q_\phi(z \mid x) = \mathcal N(\mu_\phi(x), \mathrm{diag}\,\sigma^2_\phi(x))$ and bound the log-likelihood (Kingma & Welling 2014 [S56]; Goodfellow ch. 20.10.3 [S15]):
$$\log p_\theta(x) = \log \int q_\phi(z \mid x) \frac{p_\theta(x \mid z) p(z)}{q_\phi(z \mid x)} dz \ge \mathbb{E}_{q_\phi(z \mid x)}\!\left[ \log \frac{p_\theta(x \mid z) p(z)}{q_\phi(z \mid x)} \right] \quad \text{(Jensen)}$$
$$= \mathbb{E}_{q_\phi(z \mid x)}[\log p_\theta(x \mid z)] - \mathrm{KL}\big(q_\phi(z \mid x)\,\|\,p(z)\big) =: \mathcal L(\theta, \phi; x).$$
The gap is exactly $\mathrm{KL}(q_\phi(z \mid x) \| p_\theta(z \mid x))$, since $\log p_\theta(x) = \mathcal L + \mathrm{KL}(q_\phi \| p_\theta(\cdot \mid x))$. Maximising the ELBO therefore fits the decoder and pushes $q_\phi$ towards the true posterior simultaneously. The first term is a reconstruction log-likelihood; the second is a regulariser that keeps the aggregate of posteriors close to the prior so that decoding $z \sim p(z)$ produces data.

Closed-form KL for $q = \mathcal N(\mu, \mathrm{diag}\,\sigma^2)$ and $p = \mathcal N(0, I)$ in $m$ dimensions:
$$\mathrm{KL}(q \| p) = \frac12 \sum_{j=1}^m \left( \mu_j^2 + \sigma_j^2 - \log \sigma_j^2 - 1 \right).$$
Derivation per dimension: $\mathrm{KL} = \mathbb{E}_q[\log q - \log p] = \mathbb{E}_q[-\tfrac12 \log(2\pi\sigma^2) - \tfrac{(z - \mu)^2}{2\sigma^2} + \tfrac12 \log 2\pi + \tfrac{z^2}{2}] = -\tfrac12 \log \sigma^2 - \tfrac12 + \tfrac12(\mu^2 + \sigma^2)$, using $\mathbb{E}_q[(z - \mu)^2] = \sigma^2$ and $\mathbb{E}_q[z^2] = \mu^2 + \sigma^2$. Networks output $\log \sigma^2$ (`logvar`) so $\sigma^2 = \exp(\mathrm{logvar}) > 0$ without a constraint. Each term is $\ge 0$ with equality at $\mu = 0$, $\sigma^2 = 1$.

### Reparameterisation trick

The reconstruction term needs $\nabla_\phi \mathbb{E}_{z \sim q_\phi(z \mid x)}[\log p_\theta(x \mid z)]$. Sampling $z$ from a distribution whose parameters depend on $\phi$ is not differentiable; the score-function estimator (as in REINFORCE) exists but has high variance. Instead write the sample as a deterministic function of $\phi$ and parameter-free noise:
$$z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \qquad \epsilon \sim \mathcal N(0, I).$$
Then $\mathbb{E}_{q_\phi}[h(z)] = \mathbb{E}_\epsilon[h(\mu + \sigma \odot \epsilon)]$ and the gradient passes through $\mu, \sigma$ by ordinary backpropagation; one sample of $\epsilon$ per data point suffices in practice. The trick works for any location-scale family and for any distribution with a differentiable inverse CDF; it does not work for discrete latents (use Gumbel-softmax or VQ-VAE there).

Training loss per example (minimised): $-\mathcal L = \mathrm{BCE}(\hat x, x) + \beta\, \mathrm{KL}$, with BCE summed over pixels.

### beta-VAE, posterior collapse, blurry samples

- $\beta$-VAE (Higgins et al. 2017 [S57]): weight the KL by $\beta > 1$. Stronger pressure towards the factorised prior gives more disentangled latents at the cost of reconstruction; $\beta < 1$ does the reverse. The relative scale of the reconstruction sum (grows with $D$) and the KL (grows with $m$) means $\beta = 1$ is already a strong regulariser for small images.
- Posterior collapse: $q_\phi(z \mid x) \approx p(z)$ for all $x$, KL $\to 0$, the decoder ignores $z$. Occurs when the decoder is powerful enough (autoregressive, or large relative to the data) to model $x$ without $z$, or when the KL dominates early. Fixes: KL warm-up (anneal $\beta$ from 0 to 1 over the first epochs), free bits (do not penalise KL below a threshold per dimension), a weaker decoder.
- Blurry samples: with a Gaussian or factorised Bernoulli likelihood, the decoder outputs the conditional mean of all $x$ that map to a neighbourhood of $z$; the optimum under a per-pixel loss is an average, so edges smear. The model is not wrong about the likelihood; the likelihood is a poor perceptual metric. Remedies: perceptual losses, hierarchical latents, or a different family (GAN, diffusion).

### GAN: minimax objective and optimal discriminator

Generator $G_\theta: z \mapsto x$, $z \sim p(z)$, induced distribution $p_g$. Discriminator $D_\psi: x \mapsto [0, 1]$. Value function (Goodfellow et al. 2014 [S58]; Goodfellow ch. 20.10.4 [S15]):
$$\min_G \max_D V(D, G) = \mathbb{E}_{x \sim p_d}[\log D(x)] + \mathbb{E}_{z \sim p(z)}[\log(1 - D(G(z)))].$$
For fixed $G$, maximise pointwise: $V = \int [p_d(x) \log D(x) + p_g(x) \log(1 - D(x))] dx$; $\partial / \partial D$ of the integrand $= p_d / D - p_g / (1 - D) = 0$ gives
$$D^*(x) = \frac{p_d(x)}{p_d(x) + p_g(x)}.$$
Substituting back,
$$V(D^*, G) = \mathbb{E}_{p_d}\!\left[\log \frac{p_d}{p_d + p_g}\right] + \mathbb{E}_{p_g}\!\left[\log \frac{p_g}{p_d + p_g}\right] = -\log 4 + 2\, \mathrm{JS}(p_d \| p_g),$$
using $\mathrm{JS}(p \| q) = \tfrac12 \mathrm{KL}(p \| \tfrac{p + q}{2}) + \tfrac12 \mathrm{KL}(q \| \tfrac{p + q}{2})$. The minimum over $G$ is at $p_g = p_d$ with value $-\log 4$ and $D^* = 1/2$ everywhere. So, at discriminator optimality, the generator minimises a JS divergence. JS saturates when the supports of $p_d$ and $p_g$ do not overlap (early training, low-dimensional manifolds in high-dimensional space): the gradient to $G$ vanishes.

Non-saturating generator loss: the minimax generator loss $\log(1 - D(G(z)))$ has small gradient when $D$ confidently rejects samples ($D(G(z)) \approx 0$). Use instead
$$L_G = -\mathbb{E}_z[\log D(G(z))],$$
which has the same fixed point but a large gradient exactly when the generator is bad. This is what practical GANs (and `gan_toy.py`) train. The discriminator loss is binary cross-entropy with labels 1 for data, 0 for samples.

### GAN failure modes, WGAN, conditional GAN

- Mode collapse: $G$ maps many $z$ to a few outputs that currently fool $D$; $D$ then learns to reject those, $G$ jumps to other modes, and the pair oscillates without covering the distribution. Detect by measuring coverage (in the toy: the fraction of the 8 ring modes that receive samples), not by the losses.
- Training instabilities: the two losses are not a single objective, so their values do not decrease monotonically and do not measure progress; simultaneous gradient descent on a minimax game can cycle. Practical stabilisers: Adam with $\beta_1 = 0.5$ or $0$, spectral normalisation of $D$ (Miyato et al. 2018), label smoothing on real labels (0.9), balanced $D$/$G$ step ratios, small learning rates ($2 \times 10^{-4}$).
- WGAN (Arjovsky et al. 2017 [S59]): replace JS by the Wasserstein-1 distance $W(p_d, p_g) = \sup_{\|f\|_L \le 1} \mathbb{E}_{p_d}[f] - \mathbb{E}_{p_g}[f]$ (Kantorovich-Rubinstein duality). $W$ is continuous and has useful gradients even for disjoint supports, and the critic loss correlates with sample quality. The critic $f$ must be 1-Lipschitz; weight clipping was the first (crude) enforcement, the gradient penalty $\lambda\, \mathbb{E}_{\hat x}[(\|\nabla_{\hat x} f(\hat x)\|_2 - 1)^2]$ on interpolates $\hat x$ between real and generated points (Gulrajani et al. 2017, WGAN-GP, $\lambda = 10$ [S59]) is the standard one.
- Conditional GAN (Mirza & Osindero 2014): feed a label $y$ to both $G(z, y)$ and $D(x, y)$; the game becomes $\min_G \max_D \mathbb{E}[\log D(x, y)] + \mathbb{E}[\log(1 - D(G(z, y), y))]$. Enables class-conditional generation and image-to-image translation (pix2pix, Isola et al. 2017).

### Diffusion models (DDPM)

Forward process: fix a variance schedule $\beta_1 < \dots < \beta_T$ (e.g. linear $10^{-4}$ to $0.02$, $T = 1000$) and define the Markov chain
$$q(x_t \mid x_{t-1}) = \mathcal N\!\left(\sqrt{1 - \beta_t}\, x_{t-1},\ \beta_t I\right).$$
With $\alpha_t = 1 - \beta_t$ and $\bar\alpha_t = \prod_{s \le t} \alpha_s$, composing Gaussians gives the closed form
$$q(x_t \mid x_0) = \mathcal N\!\left(\sqrt{\bar\alpha_t}\, x_0,\ (1 - \bar\alpha_t) I\right), \qquad x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon,\ \epsilon \sim \mathcal N(0, I).$$
Proof by induction: $x_t = \sqrt{\alpha_t} x_{t-1} + \sqrt{\beta_t} \epsilon_t$; the variance of the sum of the independent noise terms is $\alpha_t (1 - \bar\alpha_{t-1}) + \beta_t = 1 - \bar\alpha_t$. For $\bar\alpha_T \approx 0$, $x_T$ is pure noise. The scaling $\sqrt{1 - \beta_t}$ keeps the total variance at 1 (variance-preserving).

Reverse process: a network $\epsilon_\theta(x_t, t)$ (a U-Net with a time embedding) predicts the noise that was added. Ho et al. (2020) [S61] show that the variational bound on $\log p(x_0)$, after reparameterising the true posterior mean $\tilde\mu_t(x_t, x_0)$ in terms of $\epsilon$, reduces up to weights to the simple loss
$$L_{\mathrm{simple}} = \mathbb{E}_{t \sim U\{1..T\},\ x_0,\ \epsilon}\!\left[ \|\epsilon - \epsilon_\theta(\sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon,\ t)\|^2 \right].$$
Training: sample a data point, a random $t$, noise $\epsilon$; one forward and backward pass per step. This is a denoising autoencoder trained at all noise levels, and $-\epsilon_\theta / \sqrt{1 - \bar\alpha_t}$ estimates the score $\nabla_{x_t} \log q(x_t)$ (Song & Ermon 2019).

Sampling: start from $x_T \sim \mathcal N(0, I)$ and iterate for $t = T, \dots, 1$
$$x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left( x_t - \frac{\beta_t}{\sqrt{1 - \bar\alpha_t}}\, \epsilon_\theta(x_t, t) \right) + \sigma_t z,\quad z \sim \mathcal N(0, I),\ \sigma_t^2 = \beta_t.$$
Cost: $T$ network evaluations per sample (1000 for DDPM), versus one for a GAN or VAE decoder. DDIM (Song et al. 2021) gives a deterministic sampler that works with 20 to 50 steps; distillation reduces further. Latent diffusion (Rombach et al. 2022, Stable Diffusion) runs the diffusion in the latent space of a pretrained autoencoder ($64 \times 64 \times 4$ instead of $512 \times 512 \times 3$), which cuts the cost of every step by roughly two orders of magnitude and is the standard for image generation.

### Evaluating generative models

- Log-likelihood: VAEs give a lower bound, diffusion models a bound or exact likelihood via the ODE formulation, GANs nothing. Likelihood is comparable across models only for the same data representation (discretised pixels, bits per dimension) and correlates weakly with sample quality: a model can put high likelihood on data and produce poor samples (Theis et al. 2016).
- FID (Heusel et al. 2017): embed real and generated images with an Inception-v3 pool layer, fit Gaussians $(\mu_r, \Sigma_r)$, $(\mu_g, \Sigma_g)$, report $\|\mu_r - \mu_g\|^2 + \mathrm{tr}(\Sigma_r + \Sigma_g - 2(\Sigma_r \Sigma_g)^{1/2})$ (Frechet distance between the two Gaussians). Lower is better; needs 10k or more samples; biased by sample size; measures both fidelity and diversity in one number, so it cannot distinguish a blurry-but-diverse model from a sharp-but-collapsed one.
- Precision / recall for distributions (Sajjadi et al. 2018; Kynkaanniemi et al. 2019): precision = fraction of generated samples that lie within the support (k-NN manifold) of real features; recall = fraction of real samples covered by the generated manifold. Mode collapse shows as low recall with high precision; blur as low precision. For the 2D toy, the analogue is the mode coverage count and the mean distance to the nearest mode.

## Architecture sketch

VAE on `cnn_shapes.make_shapes(n, size=16)` (16x16 grey images of circles, squares, triangles), latent $m = 8$:

```
x [B, 1, 16, 16]
  -> conv3x3(16), stride 2, ReLU   -> [B, 16, 8, 8]
  -> conv3x3(32), stride 2, ReLU   -> [B, 32, 4, 4]
  -> flatten                       -> [B, 512]
  -> Linear(512, 8)  = mu          -> [B, 8]
  -> Linear(512, 8)  = logvar      -> [B, 8]
z = mu + exp(0.5 * logvar) * eps,  eps ~ N(0, I)   -> [B, 8]
  -> Linear(8, 512), ReLU, reshape -> [B, 32, 4, 4]
  -> convT 4x4(16), stride 2, ReLU -> [B, 16, 8, 8]
  -> convT 4x4(1),  stride 2       -> [B, 1, 16, 16]  (logits)
loss = BCE_with_logits(x_hat, x).sum over pixels + beta * KL(mu, logvar)
```

`AE(latent=8)` is the same without the `logvar` head and the KL term: `z = Linear(512, 8)`.

GAN on `make_ring(n, seed)` (2D points from 8 Gaussians centred on a ring of radius 2, std 0.05):

```
z [B, 2] ~ N(0, I)
  -> Linear(2, 128), ReLU -> Linear(128, 128), ReLU -> Linear(128, 2)   = G(z) [B, 2]

x [B, 2] (real or G(z))
  -> Linear(2, 128), LeakyReLU(0.2) -> Linear(128, 128), LeakyReLU -> Linear(128, 1)   = D logits [B, 1]

per step:  L_D = BCE(D(x_real), 1) + BCE(D(G(z).detach()), 0)   -> step D
           L_G = BCE(D(G(z)), 1)  (= -log D(G(z)), non-saturating) -> step G
```

Worked example, KL term for $m = 3$ with $\mu = (0, 1, -0.5)$ and $\mathrm{logvar} = (0, 0, \log 0.25)$, i.e. $\sigma^2 = (1, 1, 0.25)$:

- $j = 1$: $\mu^2 + \sigma^2 - \log \sigma^2 - 1 = 0 + 1 - 0 - 1 = 0$ (matches the prior exactly).
- $j = 2$: $1 + 1 - 0 - 1 = 1$.
- $j = 3$: $0.25 + 0.25 - \log 0.25 - 1 = 0.5 + 1.3863 - 1 = 0.8863$.

$\mathrm{KL} = \tfrac12 (0 + 1 + 0.8863) = 0.943$ nats. Note that the third dimension is penalised for being too narrow ($\sigma^2 = 0.25$): $-\log \sigma^2$ grows as $\sigma \to 0$, which is what prevents the encoder from becoming deterministic. For reference, a per-pixel BCE of 0.1 on $16 \times 16 = 256$ pixels gives a reconstruction term of 25.6, so KL of order 1 to 10 per example is the expected regime at $\beta = 1$.

## Pitfalls

- VAE KL goes to exactly 0 within the first epochs and reconstructions become the dataset mean -> posterior collapse, KL dominates early -> warm up $\beta$ from 0 to 1 over the first 20% of steps, or use free bits.
- Reconstruction loss plateaus high and samples from the prior are all similar -> latent too small or decoder too weak for the variation in the data -> increase `latent`, add decoder capacity, check the reconstruction term is summed (not averaged) over pixels relative to the KL.
- NaN in the VAE loss -> `exp(logvar)` overflow or BCE on probabilities outside $[0, 1]$ -> use `BCEWithLogits` on logits, clamp `logvar` to $[-10, 10]$.
- Gradients from the KL flow but reconstructions do not improve -> `reparameterize` uses `torch.randn` outside the graph correctly but $z$ was sampled with `.detach()` or via `torch.normal(mu, std)` (non-differentiable path) -> `z = mu + std * torch.randn_like(std)`.
- GAN losses look reasonable ($L_D \approx 1.39$, $L_G \approx 0.69$) but samples cover 1 to 2 of the 8 modes -> mode collapse; the losses are uninformative -> track `mode_distance` and mode coverage, lower learning rate, use Adam $\beta_1 = 0.5$, add spectral norm or switch to WGAN-GP.
- $L_D \to 0$, $L_G$ explodes, samples stop changing -> discriminator wins, saturated sigmoid, no gradient to $G$ -> reduce $D$ capacity or lr, label smoothing, non-saturating loss (already), or WGAN-GP.
- Generator gradient flows into the discriminator update -> `D(G(z))` without `.detach()` in $L_D$ -> detach generated samples in the discriminator step, or use separate optimisers and `zero_grad` correctly.
- Diffusion samples are noise after training -> time embedding missing or $\bar\alpha_t$ computed with the wrong index (off by one between training and sampling schedules) -> unit-test that $\bar\alpha$ arrays match and that $t$ passed to the network is the same $t$ used to noise.
- FID numbers not comparable to the paper -> different sample count, resolution, or Inception weights -> use the reference implementation (pytorch-fid or torch-fidelity), 50k samples, state the protocol.
- Training a VAE on `mps` is slower than on CPU for 16x16 images -> kernel-launch overhead dominates for tiny tensors -> benchmark both with `common.Timer`, pick the faster device.

## Questions

1. Derive the ELBO from $\log p_\theta(x)$ and identify the gap.

<details><summary>Answer</summary>
$\log p_\theta(x) = \log \int q_\phi(z \mid x) \frac{p_\theta(x, z)}{q_\phi(z \mid x)} dz \ge \mathbb{E}_{q_\phi}[\log p_\theta(x, z) - \log q_\phi(z \mid x)]$ by Jensen (log is concave). Splitting $p_\theta(x, z) = p_\theta(x \mid z) p(z)$ gives $\mathbb{E}_{q_\phi}[\log p_\theta(x \mid z)] - \mathrm{KL}(q_\phi(z \mid x) \| p(z))$. Exact identity: $\log p_\theta(x) = \mathcal L + \mathrm{KL}(q_\phi(z \mid x) \| p_\theta(z \mid x))$, so the gap is the KL between the approximate and the true posterior, zero iff $q_\phi$ is exact.
</details>

2. Derive the closed-form KL between $\mathcal N(\mu, \sigma^2)$ and $\mathcal N(0, 1)$ and state at which values it vanishes.

<details><summary>Answer</summary>
$\mathrm{KL} = \mathbb{E}_q[\log q(z) - \log p(z)] = \mathbb{E}_q[-\tfrac12 \log \sigma^2 - \tfrac{(z - \mu)^2}{2\sigma^2} + \tfrac{z^2}{2}]$ (the $\log 2\pi$ terms cancel). $\mathbb{E}_q[(z - \mu)^2] = \sigma^2$, $\mathbb{E}_q[z^2] = \mu^2 + \sigma^2$, so $\mathrm{KL} = \tfrac12(\mu^2 + \sigma^2 - \log \sigma^2 - 1)$. Zero iff $\mu = 0$ and $\sigma^2 = 1$; $x - \log x - 1 \ge 0$ with equality at $x = 1$ makes each term nonnegative.
</details>

3. Why is the reparameterisation trick needed, and why does it not apply to a categorical latent?

<details><summary>Answer</summary>
The reconstruction term is an expectation over $z \sim q_\phi(z \mid x)$; the sampling operation has no derivative w.r.t. $\phi$, so backpropagation cannot reach the encoder. Writing $z = \mu_\phi + \sigma_\phi \odot \epsilon$ with $\epsilon \sim \mathcal N(0, I)$ moves the randomness to a parameter-free input; $z$ is then a differentiable function of $\phi$ and Monte-Carlo gradients have low variance. A categorical sample is a discrete function of the parameters (argmax of perturbed logits), whose derivative is zero almost everywhere; one uses the score-function estimator, straight-through, or the Gumbel-softmax relaxation instead.
</details>

4. Compute the optimal discriminator for fixed $G$ and show that the generator then minimises a JS divergence. What practical problem does this cause?

<details><summary>Answer</summary>
Maximise $p_d \log D + p_g \log(1 - D)$ pointwise: $D^* = p_d / (p_d + p_g)$. Substituting, $V(D^*, G) = \mathbb{E}_{p_d}[\log \frac{p_d}{p_d + p_g}] + \mathbb{E}_{p_g}[\log \frac{p_g}{p_d + p_g}] = -\log 4 + 2\,\mathrm{JS}(p_d \| p_g)$. JS is bounded ($\le \log 2$) and constant when supports are disjoint, so a near-optimal $D$ gives the generator zero gradient early in training; the non-saturating loss $-\log D(G(z))$ and the Wasserstein objective are responses to this.
</details>

5. Show that $q(x_t \mid x_0) = \mathcal N(\sqrt{\bar\alpha_t} x_0, (1 - \bar\alpha_t) I)$ follows from the one-step forward kernel, and explain why this matters for training cost.

<details><summary>Answer</summary>
Induction: assume $x_{t-1} = \sqrt{\bar\alpha_{t-1}} x_0 + \sqrt{1 - \bar\alpha_{t-1}}\, \epsilon'$. Then $x_t = \sqrt{\alpha_t} x_{t-1} + \sqrt{1 - \alpha_t}\, \epsilon_t = \sqrt{\bar\alpha_t} x_0 + [\sqrt{\alpha_t(1 - \bar\alpha_{t-1})}\, \epsilon' + \sqrt{1 - \alpha_t}\, \epsilon_t]$. The bracket is Gaussian with variance $\alpha_t - \bar\alpha_t + 1 - \alpha_t = 1 - \bar\alpha_t$. Because any $x_t$ can be produced from $x_0$ in one shot, training samples a random $t$ per example and never runs the chain, so one training step costs one network evaluation regardless of $T$.
</details>

6. A VAE and a GAN are trained on the same images. The VAE reports a test ELBO, the GAN reports FID. Can you rank them? What would you add?

<details><summary>Answer</summary>
No: ELBO is a likelihood bound in nats per image and FID is a feature-space distance; neither is computable for the other model without extra work (GAN likelihood is undefined, VAE FID is possible). Compute FID and precision/recall for both from the same number of samples at the same resolution, and additionally show reconstructions (VAE only) and nearest training neighbours of samples to detect memorisation. State that the VAE optimises a likelihood objective and the GAN a perceptual one, so the comparison is on sample quality only.
</details>

7. Project question: the project needs to generate plausible 64x64 images of a domain with about 5k training images on an M3 Pro. Which family and which safeguards?

<details><summary>Answer</summary>
A small conditional diffusion model (DDPM with a U-Net of 5 to 10 M parameters, latent size 64x64x3 directly, cosine schedule, $T = 1000$ for training, DDIM 50 steps for sampling) is the most reliable for quality; a WGAN-GP with spectral norm is faster to sample and to train if compute is the bottleneck; a VAE only if a latent representation is the goal. Safeguards: augmentation (flips, small crops) for 5k images, EMA of the weights for sampling, FID against a held-out split with a fixed protocol, precision/recall to detect collapse, nearest-neighbour check for memorisation, and a fixed seed set for qualitative grids across phases.
</details>

8. Explain posterior collapse and give two mechanisms that cause it and two fixes.

<details><summary>Answer</summary>
Collapse: $q_\phi(z \mid x) = p(z)$ for all $x$, KL $= 0$, decoder independent of $z$; the ELBO is then just the marginal decoder likelihood. Causes: (i) a decoder strong enough to model $p(x)$ without $z$ (autoregressive or overparametrised), so the KL cost of using $z$ is not repaid; (ii) early training where the reconstruction gradient through a random decoder is uninformative and the KL gradient dominates, driving $q$ to the prior before $z$ becomes useful. Fixes: KL annealing (warm-up), free bits or a KL floor, weakening the decoder (dropout on its input, limited receptive field), or $\beta < 1$.
</details>

## Code

`src/py/autoencoder_vae.py`: data from `cnn_shapes.make_shapes(n, size=16)`; `AE(latent=8)`, `VAE(latent=8)` with `encode -> (mu, logvar)`, `reparameterize`, `decode`; `vae_loss(x_hat, x, mu, logvar, beta=1.0)` = BCE reconstruction + `beta` times the closed-form KL $\tfrac12 \sum (\mu^2 + \sigma^2 - \log\sigma^2 - 1)$; `run(steps=400, kind="vae"|"ae", device=None, seed=0)` returning `{"losses", "recon_error", "kl"}`. `python src/py/autoencoder_vae.py` trains a few seconds and prints the reconstruction error (and KL for the VAE). `test_autoencoder_vae.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)`.

`src/py/gan_toy.py`: `make_ring(n, seed)` (8 Gaussians on a ring); `Generator(noise=2)`, `Discriminator`; non-saturating GAN loss; `mode_distance(samples)` = mean distance of generated samples to the nearest of the 8 modes; `run(steps=600, device=None, seed=0)` returning `{"losses", "d_losses", "g_losses", "mode_distance"}`, where `"losses"` is `mode_distance` evaluated every 20 steps, because the adversarial losses `d_losses`, `g_losses` do not decrease monotonically. `python src/py/gan_toy.py` prints the final `mode_distance`. `test_gan_toy.py` asserts `common.loss_decreased(losses)` on the mode-distance series.

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016) [S15]: ch. 14 (autoencoders: undercomplete, sparse, denoising, relation to PCA), ch. 19 (approximate inference, ELBO), ch. 20.10.3 (VAE), ch. 20.10.4 (GAN).
- Kingma, D. P. & Welling, M. (2014) [S56]. Auto-encoding variational Bayes. VAE, reparameterisation.
- Rezende, D. J., Mohamed, S., Wierstra, D. (2014). Stochastic backpropagation and approximate inference in deep generative models.
- Higgins, I. et al. (2017) [S57]. beta-VAE: learning basic visual concepts with a constrained variational framework.
- Vincent, P. et al. (2008). Extracting and composing robust features with denoising autoencoders.
- Alain, G. & Bengio, Y. (2014). What regularized auto-encoders learn from the data-generating distribution.
- Baldi, P. & Hornik, K. (1989). Neural networks and principal component analysis.
- Goodfellow, I. et al. (2014) [S58]. Generative adversarial nets.
- Arjovsky, M., Chintala, S., Bottou, L. (2017) [S59]. Wasserstein GAN. Lecture 7 gives the Wasserstein distance its own chapter [S4].
- Gulrajani, I. et al. (2017) [S59]. Improved training of Wasserstein GANs. Gradient penalty.
- Miyato, T. et al. (2018). Spectral normalization for generative adversarial networks.
- Mirza, M. & Osindero, S. (2014). Conditional generative adversarial nets.
- Ho, J., Jain, A., Abbeel, P. (2020) [S61]. Denoising diffusion probabilistic models. Luo (2022) [S61], *Understanding diffusion models*, is **Lecture 7's reference 20** [S4].
- Song, Y. & Ermon, S. (2019). Generative modeling by estimating gradients of the data distribution.
- Song, J., Meng, C., Ermon, S. (2021). Denoising diffusion implicit models.
- Rombach, R. et al. (2022). High-resolution image synthesis with latent diffusion models.
- Heusel, M. et al. (2017). GANs trained by a two time-scale update rule converge to a local Nash equilibrium. FID.
- Sajjadi, M. et al. (2018). Assessing generative models via precision and recall; Kynkaanniemi, T. et al. (2019). Improved precision and recall metric.
- Theis, L., van den Oord, A., Bethge, M. (2016). A note on the evaluation of generative models. Salimans et al. (2016) [S60], improved techniques for training GANs, is Lecture 7's own source for evaluating them.
- **Lecture 7** [S4], *Autoencoders and Generative Adversarial Networks*, is the lecture this note covers. **Scope caveat:** the lecture gives diffusion 3.5 minutes of its 75 (one chapter, "Diffusion", at 49:48) whereas this note treats it at length. That is deliberate -- diffusion is a plausible project topic -- but do not infer from the note's length that the course weights it that way.
