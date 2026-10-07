# 04 Autoencoders and learned compression

Nonlinear generalisation of note 02: learn the encoder and decoder instead of
taking singular vectors. The honest summary of the experiments below: a
nonlinear autoencoder wins when the data lie on a curved low-dimensional manifold,
and loses to PCA on small, noisy, symmetric data such as Ising snapshots.

Code: [`../src/py/autoencoder_compression.py`](../src/py/autoencoder_compression.py),
data from [`../src/py/ising_snapshots.py`](../src/py/ising_snapshots.py).

## 1 Definitions

- **Autoencoder (AE).** Encoder $f_\phi:\mathbb R^d\to\mathbb R^k$, decoder
  $g_\theta:\mathbb R^k\to\mathbb R^d$, trained on
  $D(\phi,\theta)=\frac1n\sum_i\lVert x_i-g_\theta(f_\phi(x_i))\rVert^2$. $k<d$ is the **bottleneck**.
- **Distortion** $D=\mathbb E\,d(X,\hat X)$; here $d$ = squared error per component (MSE).
- **Rate** $R$: bits per sample (or per spin) needed to transmit the code. A real
  latent has no finite rate; rate exists only after quantisation or with noise (VAE).
- **Rate-distortion function** $R(D)=\min_{p(\hat x|x):\,\mathbb Ed\le D}I(X;\hat X)$ [S36].

## 2 Rate-distortion, the reference curve

**Scalar uniform quantiser**, step $\Delta$: for a smooth density the error is
approximately uniform on $[-\Delta/2,\Delta/2]$, so
$\mathrm{MSE}=\int_{-\Delta/2}^{\Delta/2}e^2\,de/\Delta=\Delta^2/12$. One more bit halves
$\Delta$: $-6.02$ dB per bit (`quantise`; tested: MSE $=\Delta^2/12$ within 20 %).

**Gaussian source** $X\sim\mathcal N(0,\sigma^2)$: $R(D)=\tfrac12\log_2(\sigma^2/D)$
for $D<\sigma^2$ [S36]. **Gaussian vector** with covariance eigenvalues $\lambda_j$:
reverse water-filling, $D_j=\min(\vartheta,\lambda_j)$,
$R=\sum_j\tfrac12\log_2(\lambda_j/D_j)$ [S36]. Directions with $\lambda_j<\vartheta$
get zero bits. So for Gaussian data **PCA + per-component quantisation is optimal**
(transform coding); a learned transform can only win on non-Gaussian data.
Ballé et al. train encoder, quantiser proxy and decoder end to end on $R+\lambda D$ [S33].

## 3 Linear AE = PCA [S31]

Centred data $X_c$, linear maps $W_e\in\mathbb R^{d\times k}$, $W_d\in\mathbb R^{k\times d}$.
$$\min_{W_e,W_d}\lVert X_c-X_cW_eW_d\rVert_F^2 .$$
$M=W_eW_d$ has rank $\le k$ and $X_cM$ has rank $\le k$, so by Eckart-Young
(note 02) the minimum is $\sum_{j>k}s_j^2$, reached at $X_cM=U_k\Sigma_kV_k^T$,
i.e. $M=V_kV_k^T$ (on the row space). Every factorisation $W_e=V_kG$,
$W_d=G^{-1}V_k^T$, $G\in GL(k)$, is optimal: **the AE finds the PCA subspace, not
the principal axes**. Baldi and Hornik: all other critical points are saddles, so
gradient descent reaches it [S31]. `test_linear_autoencoder_reaches_pca`: linear
AE training MSE within 3 % of PCA, never below it.

## 4 Nonlinear AE and the VAE

A tanh MLP AE ($d\to64\to k\to64\to d$, `MLPAE`) can represent curved manifolds.
It can also memorise: nothing in $D$ penalises using the $k$ reals to index the
training set. Test error, not training error, is the measure.

**VAE** [S21]. Encoder outputs $q_\phi(z|x)=\mathcal N(\mu(x),\operatorname{diag}\sigma^2(x))$,
prior $p(z)=\mathcal N(0,I)$, decoder $p_\theta(x|z)=\mathcal N(g_\theta(z),s^2I)$. Jensen:
$$\log p(x)\ge\mathbb E_{q}\log p_\theta(x|z)-\mathrm{KL}(q_\phi(z|x)\,\Vert\,p(z))
=-\frac{\mathbb E_q\lVert x-g_\theta(z)\rVert^2}{2s^2}-\mathrm{KL}+\text{const}.$$
Gaussian KL in closed form: $\mathrm{KL}=\tfrac12\sum_j(\mu_j^2+\sigma_j^2-1-\log\sigma_j^2)$.
Gradients through the sampling by **reparameterisation** $z=\mu+\sigma\odot\xi$, $\xi\sim\mathcal N(0,I)$.

**Rate interpretation.** $\mathbb E_x\mathrm{KL}(q(z|x)\Vert p(z))=I(X;Z)+\mathrm{KL}(q(z)\Vert p(z))\ge I(X;Z)$,
with $q(z)=\mathbb E_xq(z|x)$. So the KL term is an upper bound on the rate in nats,
the reconstruction term is the distortion, and the $\beta$-VAE loss
$D/(2s^2)+\beta\,\mathrm{KL}$ traces an $R$-$D$ curve as $\beta$ varies (`VAE`, `vae_kl_per_spin`).

## 5 Worked examples (`python autoencoder_compression.py`)

**Ising snapshots**, $12\times12$, 12 temperatures in $[1.5,3.5]$, 900 train / 300 test.
PCA: first explained-variance ratio 0.434, then 0.024, 0.023, ...;
$\operatorname{corr}(\text{PC}_1,m)=1.000$ on the test set: the first component is the
magnetisation [S22].

| $k$ | PCA test MSE | linear AE | MLP AE test | MLP AE train | wrong spins PCA / MLP |
|---|---|---|---|---|---|
| 1 | 0.562 | 0.562 | 0.577 | 0.565 | 0.222 / 0.229 |
| 2 | 0.541 | 0.539 | 0.588 | 0.511 | 0.211 / 0.226 |
| 4 | 0.498 | 0.499 | 0.622 | 0.371 | 0.186 / 0.213 |
| 8 | 0.436 | 0.438 | 0.613 | 0.261 | 0.155 / 0.194 |

The MLP memorises (train $\ll$ test) and never beats PCA. Why PCA is hard to beat
at $k=1$: by translation invariance $\mathbb E[s_i\,|\,m]=m$, so the best decoder
given $m$ is the uniform field $m$, which is what PCA's $k=1$ reconstruction is; its
MSE is $1-m^2$ per spin. High-$T$ snapshots are incompressible noise
($1-m^2\approx1$) and dominate the average.

**Single-pole Green's functions** $G(\tau;\epsilon)=-K(\tau,\epsilon)$, 64 points,
$\epsilon\sim U[-5,5]$: a one-parameter curve in $\mathbb R^{64}$ (`pole_dataset`).

| model, $k$ | test MSE |
|---|---|
| PCA 1 / 2 / 3 / 4 / 5 / 6 | $1.3\times10^{-2}$ / $3.3\times10^{-3}$ / $1.1\times10^{-3}$ / $2.3\times10^{-4}$ / $5.6\times10^{-5}$ / $1.1\times10^{-5}$ |
| MLP AE 1 | $1.2\times10^{-4}$ |

The AE with one latent matches PCA with four to five. PCA's decay is exponential
for the reason of note 03: the family is spanned by the smooth kernel.

**Rate.** $k=2$ MLP AE, latents quantised: 1, 2, 4, 8 bits per latent give
0.014, 0.028, 0.056, 0.111 bits/spin at MSE 0.70, 0.63, 0.59, 0.59 (raw data: 1 bit/spin
lossless). **VAE** $k=2$, $\beta=0.1,1,10$: rate 0.144, 0.042, 0.020 nats/spin, MSE
0.61, 0.58, 0.56. Distortion does not rise with $\beta$ here: the extra rate at small
$\beta$ is spent on training-set noise.

## 6 Pitfalls

- Reporting training reconstruction error. Always a held-out set; show both.
- "Compressed to $k$ numbers" without saying how many bits: $k$ float32 latents
  are $32k$ bits. Quantise and count.
- MSE on $\pm1$ spins with a tanh output: fine for comparison with PCA, but the
  likelihood-correct loss for binary data is cross-entropy (Wetzel uses it [S22]).
- Comparing AE and PCA with different preprocessing (centring, scaling) or $k$.
- Non-reproducible training: fix seeds, re-initialise, report spread over seeds.
- VAE posterior collapse: a strong decoder can ignore $z$ (KL $\to0$). Check the
  KL per latent dimension.
- Symmetry: an AE does not know $s\to-s$; augment with flipped samples (note 07)
  or build it in.

## 7 Questions

1. **Show that a linear autoencoder cannot beat PCA and that it finds the same
   subspace.** $X_cW_eW_d$ has rank $\le k$; Eckart-Young bounds the error by
   $\sum_{j>k}s_j^2$, attained iff $W_eW_d$ projects onto $\operatorname{span}(v_1..v_k)$;
   the factorisation is unique only up to $G\in GL(k)$.
2. **Why is the bottleneck dimension not a rate?** A real number carries unbounded
   information; only quantisation (bits) or noise (VAE: KL bounds $I(X;Z)$) makes the
   rate finite and comparable to $R(D)$.
3. **Derive the uniform-quantiser MSE and the 6 dB/bit rule.** Error uniform on
   $[-\Delta/2,\Delta/2]$, variance $\Delta^2/12$; $b\to b+1$ halves $\Delta$, MSE$/4$,
   $10\log_{10}4=6.02$ dB.
4. **For which data can a nonlinear AE beat PCA at equal $k$, and why does it fail
   on Ising snapshots?** Data on a curved $k$-dimensional manifold (single-pole
   $G$: $10^{-4}$ vs $10^{-2}$). Ising: the conditional mean given $m$ is linear in
   $m$, the rest is thermal noise, and with $10^3$ samples the MLP memorises.
5. **Write the $\beta$-VAE loss and interpret each term in rate-distortion language.**
   $\mathbb E\lVert x-g(z)\rVert^2/(2s^2)+\beta\,\mathbb E\,\mathrm{KL}(q(z|x)\Vert p(z))$:
   distortion plus $\beta$ times an upper bound on $I(X;Z)$ in nats; $\beta$ is the
   Lagrange multiplier selecting a point on the $R$-$D$ curve.

## Code

`ising_dataset`, `pole_dataset`, `LinearAE`, `MLPAE`, `VAE`, `train`,
`ae_encode`, `ae_decode`, `vae_kl_per_spin`, `mse`, `spin_error_rate`,
`quantise`, `compare`, `compare_poles` in
[`autoencoder_compression.py`](../src/py/autoencoder_compression.py); tests in
[`test_autoencoder_compression.py`](../src/py/test_autoencoder_compression.py).
