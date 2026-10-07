# 08 Autoencoders

TISS topic 8, "Autoencoders" [S2]. **No autoencoder lecture exists in the public
2021-2023 video channel and no 2021S exercise uses one** [S5, S11]: the topic was
added later, so its depth and exercise are unverified. Texts: [S6 sec. XVII.C]
(variational autoencoders), [S7 ch. 10] (PCA, the linear case), [S28, S35, S36].
Neither the CSE ML notes nor the other textbooks named on TISS treat
autoencoders in depth; this note is self-contained.

## Definitions

- **Autoencoder (AE):** encoder $z=E_\phi(x)\in\mathbb R^r$, decoder
  $\hat x=D_\psi(z)$, trained to minimise reconstruction error
  $\frac1N\sum_n\|x_n-D_\psi(E_\phi(x_n))\|^2$. $r<\dim x$ (**undercomplete**,
  bottleneck) forces compression. $z$ is the **latent** representation.
- **Linear AE:** $E(x)=Ax$, $D(z)=Bz$, $A\in\mathbb R^{r\times d}$, $B\in\mathbb R^{d\times r}$.
- **Denoising AE (DAE)** [S36]: input $\tilde x=x+\xi$, target $x$.
- **Variational AE (VAE)** [S6 sec. XVII.C]: stochastic encoder $q_\phi(z|x)$,
  prior $p(z)=\mathcal N(0,\mathbb 1)$, trained on the ELBO
  $\mathbb E_q\log p_\psi(x|z)-\mathrm{KL}(q_\phi(z|x)\|p(z))$; a generative model.

## Derivations

**Linear AE = PCA subspace** [S28]. With centred $X$, the loss is
$\|X-XA^TB^T\|_F^2$; the product $M=B A$ has rank $\le r$. By Eckart-Young
(note 07) the minimum over all rank-$r$ matrices is attained at $XM=X_r$, i.e.
$M=V_rV_r^T$, the projector on the top-$r$ principal subspace; minimum value
$\sum_{k\ge r}s_k^2$. Every $(A,B)$ with $BA=V_rV_r^T$ is optimal:
$B=V_rG$, $A=G^{-1}V_r^T$ for any invertible $G$. Consequences:

- the AE recovers the **subspace**, not the ordered orthonormal axes;
- Baldi-Hornik: all other critical points are saddles, so GD finds the global
  minimum generically [S28].

With a sigmoid on the code but linear decoder the conclusion is similar for small
signals; genuine gains need non-linear encoder **and** decoder.

**Why non-linear helps.** Data on a curved $r$-dimensional manifold need more
than $r$ linear components. A $3/4$ circular arc in $\mathbb R^6$ is intrinsically
1D: PCA needs $r=2$, a non-linear AE $r=1$ (the arc is homeomorphic to an
interval; a *full* circle is not, and cannot be encoded continuously in $r=1$:
topology limits AEs).

**Denoising AE learns the projection onto the data.** For small Gaussian noise
$\xi\sim\mathcal N(0,\sigma^2\mathbb 1)$, the optimal $D(E(\tilde x))$ is
$\mathbb E[x|\tilde x]\approx\tilde x+\sigma^2\nabla\log p(\tilde x)$ (Tweedie): it
moves inputs toward high density, i.e. back onto the manifold. Noise also
prevents the identity map in overcomplete AEs.

**VAE loss, one line.** $\log p(x)\ge\mathbb E_{q(z|x)}\log p(x|z)-\mathrm{KL}(q\|p)$
(Jensen, as in EM of note 06). Gaussian $q=\mathcal N(\mu,\mathrm{diag}\,s^2)$:
$\mathrm{KL}=\frac12\sum_j(\mu_j^2+s_j^2-1-\log s_j^2)$; sample
$z=\mu+s\odot\varepsilon$ (reparametrisation) to backpropagate through the sampling.

**Physics uses.** Latent variable as an order parameter (AE on Ising
configurations: $r=1$ latent tracks $m$, like PC1; Mehta et al. use a VAE on Ising
[S6 sec. XVII.D.3]); anomaly detection in collider data via reconstruction
error (train on background, flag events that reconstruct badly); compression of
many-body data (138.129).

## Worked example (`src/py/autoencoder.py`)

- **Linear AE by GD** (numpy, 5D data with stds $(3,2,1,0.3,0.1)$, $r=2$):
  MSE $1.1569$ = Eckart-Young optimum $1.1569$; sine of the largest principal
  angle to the PCA subspace $4\times10^{-5}$. The PCA axes expressed in the decoder
  basis form a rotation $\begin{pmatrix}0.65&-0.76\\0.78&0.64\end{pmatrix}$, not the identity.
- **Arc in $\mathbb R^6$** (600 points, noise 0.02): PCA $r=1$ MSE $0.307$,
  PCA $r=2$ $0.0015$; torch AE ($6\text{-}32\text{-}32\text{-}1\text{-}32\text{-}32\text{-}6$, tanh, Adam, 2500 steps)
  $r=1$: $0.0022$.
- **Denoising** (same architecture, noise $\sigma=0.15$ on inputs): MSE to the clean
  data $0.135\to0.023$.

## Pitfalls

- Overcomplete ($r\ge d$) plain AE learns the identity; needs a bottleneck, noise
  or a sparsity penalty.
- Reconstruction error on training data says nothing about the latent space
  being meaningful (disentangled, smooth).
- Latent coordinates are defined up to reparametrisation: do not read physics
  into the scale or sign of $z$ without calibration.
- Linear AE trained by GD converges slowly along small-variance directions
  (condition number, note 01).
- An AE is not a generative model: decoding random $z$ gives garbage; that is
  what the VAE's KL term fixes.

## Test-style questions

**Q1.** Show that the optimal linear AE spans the top-$r$ principal subspace.
**A.** $XA^TB^T$ has rank $\le r$; Eckart-Young gives the best rank-$r$
approximation $X_r=XV_rV_r^T$; so $(BA)^T=V_rV_r^T$ on the row space. Any
invertible $G$ mixes the axes without changing the loss.

**Q2.** What does a linear AE not give you that PCA does?
**A.** Ordered, orthonormal axes and the explained variance per axis.

**Q3.** Why can a non-linear AE with $r=1$ reconstruct a circular arc but not a full circle?
**A.** The encoder-decoder composition would restrict to a continuous injective map
from the circle to $\mathbb R$ on the data, which does not exist (a circle is not
homeomorphic to a subset of $\mathbb R$); an arc is.

**Q4.** What does a denoising AE learn in the small-noise limit?
**A.** $\hat x(\tilde x)\approx\tilde x+\sigma^2\nabla_x\log p(\tilde x)$: a step up
the data density, projecting onto the data manifold.

**Q5.** How would you use an AE to find anomalous LHC events?
**A.** Train on (mostly) background; reconstruction error is small for
background-like events and large for events unlike the training data. Threshold
the error; evaluate with a ROC curve on labelled simulation (note 10).

## Code

`src/py/autoencoder.py`: `linear_ae_numpy` (untied linear AE, full-batch GD),
`curve_data` (arc in $\mathbb R^d$), `AE` (torch MLP encoder/decoder), `train_ae`
(Adam; `noise>0` = denoising), `pca_reconstruction_mse`. Tests: subspace distance
$<10^{-3}$, AE MSE $<0.1\times$ PCA($r=1$), denoising error $<0.4\times$ input
noise. `clustering_pca.subspace_distance` computes principal angles.
