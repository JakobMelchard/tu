# 06 Generative models for image synthesis

> TISS item 5 [S1, S3]. Catalogue weight: GANs only (concept, training loop,
> conditional GAN, colourisation, paired vs unpaired, cycle consistency) in
> 2020 and 2022S [S7, S8]; VAE and diffusion are in the TISS subject line but
> not in any public catalogue. Papers [S27-S29]; Goodfellow ch. 14, 20 [S11];
> Drori ch. 9-10 [S12].
> **Derivations live in [ADL 05](../../applied-deep-learning/notes/05-autoencoders-generative.md)**:
> ELBO via Jensen and its gap, the Gaussian KL, reparameterisation, $D^*$ and
> the JS identity, WGAN, the DDPM closed form and loss, FID. This note states
> the results, adds the image-to-image material the catalogue asks for, and
> checks the formulas numerically.

## Definitions and results

**Generative model.** Learns $p_\theta(x)$ (or a sampler for it) from
unlabelled images. Uses: synthesis, augmentation, image-to-image translation,
anomaly detection (a model of normal data scores deviations [S8]).

**Autoencoder.** $x \to z = f_\phi(x) \to \hat x = g_\theta(z)$, trained on
$\|x - \hat x\|$; the bottleneck forces a compressed code. No distribution on
$z$, so decoding random codes gives garbage.

**VAE** [S27]. Prior $p(z) = \mathcal N(0, I)$, decoder $p_\theta(x\mid z)$,
encoder $q_\phi(z\mid x) = \mathcal N(\mu, \mathrm{diag}\,\sigma^2)$. Maximise
$$ \mathcal L = \mathbb E_{q_\phi}[\log p_\theta(x\mid z)] - \mathrm{KL}(q_\phi(z\mid x)\,\|\,p(z)) \le \log p_\theta(x), $$
gap $= \mathrm{KL}(q_\phi(z\mid x)\,\|\,p_\theta(z\mid x))$;
$\mathrm{KL} = \tfrac12\sum_j(\mu_j^2 + \sigma_j^2 - \log\sigma_j^2 - 1)$;
sample $z = \mu + \sigma\odot\epsilon$ to backpropagate. Per-pixel likelihoods
make samples blurry (the decoder predicts a conditional mean).

**GAN** [S28]. Generator $G: z\mapsto x$, discriminator
$D: x\mapsto[0,1]$ (any image classifier). Two-player game
$$ \min_G\max_D V = \mathbb E_{p_d}\log D(x) + \mathbb E_{z}\log(1 - D(G(z))). $$
For fixed $G$: $D^* = p_d/(p_d + p_g)$ and $V(D^*, G) = -\log 4 + 2\,\mathrm{JS}(p_d\|p_g)$,
minimised iff $p_g = p_d$, where $D^* \equiv \tfrac12$. **Latent vectors**
$z \sim \mathcal N(0,I)$ are the source of variation; moving in $z$ moves along
the image manifold.

**Training loop** [S7, S8] (per iteration): sample real $x$ and noise $z$;
update $D$ on $-\log D(x) - \log(1 - D(G(z)))$ with $G(z)$ detached; sample
$z$ again, update $G$ on the **non-saturating** loss $-\log D(G(z))$. Ideal
outcome: $p_g = p_d$, $D = \tfrac12$ everywhere. In practice training is
stopped by sample quality, not by the losses.

**Why the non-saturating loss.** With $D = \sigma(a)$:
$\partial_a\log(1 - \sigma(a)) = -\sigma(a)$, which vanishes exactly when $D$
confidently rejects the fake ($a \ll 0$), i.e. early in training;
$\partial_a(-\log\sigma(a)) = -(1 - \sigma(a)) \approx -1$ there.

**Instabilities.** (i) Vanishing generator gradient when $D$ wins (JS
saturates at $\log 2$ for disjoint supports). (ii) **Mode collapse**: $G$
covers a few modes that currently fool $D$, then hops. (iii) Oscillation:
simultaneous gradient steps on a min-max game cycle instead of converging.
(iv) Losses are not a progress measure. Remedies: non-saturating loss,
Adam with $\beta_1 = 0.5$, spectral norm or gradient penalty (WGAN-GP), label
smoothing, balanced update ratio; see ADL 05.

**Conditional GAN** [S28 Mirza & Osindero 1411.1784]. Feed a condition $y$ to both: $G(z, y)$,
$D(x, y)$. Choose $y$ to pick the class, vary $z$ for variety.

**Image-to-image translation.** *Paired* (pix2pix, [S28 Isola 1611.07004]):
training pairs $(a, b)$ exist, e.g. grayscale/colour, edges/photo. $G$ is a
U-Net conditioned on $a$; $D$ judges pairs $(a, b)$ patch-wise; loss
adversarial $+ \lambda\|G(a) - b\|_1$. *Unpaired* (CycleGAN,
[S28 Zhu 1703.10593]): two domains without correspondence, e.g. horses and
zebras, photos and paintings. Two generators $F: A\to B$, $G: B\to A$, two
discriminators, plus **cycle consistency**
$\|G(F(a)) - a\|_1 + \|F(G(b)) - b\|_1$: a translation must be invertible,
which rules out mapping every input to one plausible output.

**Colourisation GAN** [S7]. Paired task: any colour dataset gives pairs by
converting to grayscale. $G$ = U-Net from $L$ (1 channel) to colour
(2 channels $ab$ in Lab, or 3 RGB), $D$ = a patch classifier on
(gray, colour) pairs, loss adversarial + $L_1$.

## Diffusion in one page

Forward process fixed: $q(x_t\mid x_{t-1}) = \mathcal N(\sqrt{1-\beta_t}\,x_{t-1}, \beta_t I)$,
$t = 1..T$. With $\bar\alpha_t = \prod_{s\le t}(1-\beta_s)$:
$$ x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1 - \bar\alpha_t}\,\epsilon,\qquad \epsilon\sim\mathcal N(0,I), $$
by induction (independent Gaussian noise variances add:
$\alpha_t(1 - \bar\alpha_{t-1}) + \beta_t = 1 - \bar\alpha_t$). A U-Net
$\epsilon_\theta(x_t, t)$ is trained on
$\mathbb E\|\epsilon - \epsilon_\theta(x_t, t)\|^2$ with random $t$ [S29]:
a denoising autoencoder at every noise level, one network evaluation per
training step. Sampling runs the learned reverse chain from
$x_T\sim\mathcal N(0,I)$: $T$ evaluations (1 000 in DDPM; far fewer with DDIM
or latent diffusion). Trade-off against GANs: stable, likelihood-based,
mode-covering training versus slow sampling.

## Worked examples (all printed by `vae_gan_toy.py`)

**KL term.** $\mu = (0, 1, -0.5)$, $\sigma^2 = (1, 1, 0.25)$:
$\tfrac12[(0) + (1) + (0.25 + 0.25 + 1.386 - 1)] = 0.943$ nats. Monte Carlo
with $2\cdot10^5$ samples agrees to $10^{-2}$.

**VAE on $8\times8$ bars** (latent 2, 400 Adam steps): $-$ELBO falls from
37.0 to 19.0 nats per image. The uniform-Bernoulli baseline is
$64\ln 2 = 44.4$ nats.

**$D^*$ and JS.** $p_d = \mathcal N(0,1)$, $p_g = \mathcal N(2,1)$: $D^*(1) = \tfrac12$
by symmetry; quadrature gives $V(D^*, G) = -0.7126$, so
$\mathrm{JS} = (-0.7126 + \ln 4)/2 = 0.337$ nats (of at most $\ln 2 = 0.693$).
At $p_g = p_d$: $V = -\ln 4 = -1.386$.

**Saturation.** $a = -6$, $D = 0.0025$: saturating gradient $-0.0025$,
non-saturating $-0.9975$: 400 times stronger.

**Noise schedule.** Linear $\beta$ from $10^{-4}$ to $0.02$, $T = 1000$:
$\bar\alpha_t = 0.9999, 0.524, 0.079, 4\cdot10^{-5}$ at $t = 1, 250, 500, 1000$.
Half the signal variance is gone by $t \approx 250$.

## Pitfalls

- "Train $D$ to convergence, then $G$" (student key [S7]): an optimal $D$
  starves $G$ of gradient; alternate single steps.
- Stopping a GAN when $D$ outputs $(0.5, 0.5)$: a collapsed $G$ with a weak $D$
  also does that.
- Forgetting `detach()` on fakes in the $D$ step.
- Calling CycleGAN's cycle loss "MAE on the images" without saying which
  images: it compares an input with its round trip.
- VAE KL summed over latents but reconstruction averaged over pixels: the KL
  then dominates and the posterior collapses.

## Exam-style questions

1. **Concept of a GAN, the two networks, how they interact, and latent
   vectors.** *(20, 22)* As above; $D$ is a binary classifier real vs fake,
   $G$ maps noise to images and is trained through $D$'s gradient.
2. **Training loop in pseudo-code and the ideal outcome.** *(22)* Alternating
   $D$ and $G$ steps with the non-saturating loss; $p_g = p_d$, $D \equiv \tfrac12$.
3. **Conditional vs unconditional GAN; sketch.** *(22)* $y$ enters both $G$ and
   $D$; pick the class with $y$, vary $z$.
4. **Paired vs unpaired translation, an example each, cycle consistency and
   why it helps.** *(22)* Grayscale to colour (paired); photo to painting
   (unpaired); round-trip $L_1$ penalty prevents content-free mappings.
5. **Derive $V(D^*, G)$ and explain why the GAN generator can stop learning.**
   *(ours)* $D^* = p_d/(p_d+p_g)$, $V = -\log4 + 2\,\mathrm{JS}$; JS is flat
   ($\log 2$) for disjoint supports and the saturating loss has gradient
   $-D \approx 0$ when fakes are rejected.

## Code

- `src/py/vae_gan_toy.py`: `make_bars`, `kl_gauss`, `kl_monte_carlo`, `VAE`
  (`encode`, `reparameterize`), `neg_elbo`, `train_vae`, `gan_value`,
  `gauss_pdf`, `optimal_discriminator`, `js_divergence_1d`,
  `value_at_optimal_d`, `generator_loss_grads`, `gan_steps`, `alpha_bar`,
  `q_sample`, `q_iterate`.
- `src/py/segmentation_losses.py`: `TinyUNet`, the generator shape of pix2pix.
