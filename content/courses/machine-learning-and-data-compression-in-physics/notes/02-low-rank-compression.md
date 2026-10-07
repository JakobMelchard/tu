# 02 Data compression as low-rank approximation

Every compression method in notes 03-05 is a variation of one statement: keep the
leading singular directions, drop the rest, and the error is the discarded
singular weight. This note is that statement with proofs, the PCA special case,
the randomised algorithm that makes it cheap, and how to choose the rank.

Code: [`../src/py/lowrank.py`](../src/py/lowrank.py).

## 1 Definitions

- **SVD.** $A\in\mathbb R^{m\times n}$, $A=U\Sigma V^T=\sum_{j}s_j u_j v_j^T$,
  $s_1\ge s_2\ge\dots\ge0$, $U^TU=V^TV=I$.
- **Rank-$k$ truncation.** $A_k=\sum_{j\le k}s_ju_jv_j^T$. Storage $k(m+n+1)$
  numbers instead of $mn$: compression ratio $\rho_k=k(m+n+1)/(mn)$ (`compression_ratio`).
- **Norms.** $\lVert A\rVert_2=s_1$, $\lVert A\rVert_F^2=\sum_j s_j^2$. Report
  relative errors $\lVert A-A_k\rVert/\lVert A\rVert$ and say which norm.
- **Unitarily invariant norm.** $\lVert QAR\rVert=\lVert A\rVert$ for orthogonal
  $Q,R$; depends on $A$ only through its singular values.

## 2 Eckart-Young-Mirsky [S19]

**Theorem.** For every $B$ with $\operatorname{rank}B\le k$:
$\lVert A-B\rVert_2\ge s_{k+1}$ and $\lVert A-B\rVert_F^2\ge\sum_{j>k}s_j^2$,
with equality at $B=A_k$.

*Proof (spectral).* $\dim\ker B\ge n-k$ and $\dim\operatorname{span}\{v_1..v_{k+1}\}=k+1$,
so they share a unit vector $x=\sum_{j\le k+1}c_jv_j$. Then
$\lVert(A-B)x\rVert=\lVert Ax\rVert=(\sum_{j\le k+1}c_j^2s_j^2)^{1/2}\ge s_{k+1}$.

*Proof (Frobenius).* Weyl: $s_{i+j-1}(X+Y)\le s_i(X)+s_j(Y)$. Put $X=A-B$,
$Y=B$, $j=k+1$: $s_{k+1}(B)=0$, so $s_{i+k}(A)\le s_i(A-B)$. Square and sum over $i$:
$\lVert A-B\rVert_F^2\ge\sum_i s_{i+k}(A)^2$. $\square$

Consequence: **the singular value spectrum is the complete answer** to "how
compressible is $A$ linearly". `eckart_young_error(s, k)` gives the error from
$s$ alone; `rank_for_tolerance(s, eps)` the smallest $k$ reaching a relative
Frobenius tolerance.

## 3 PCA is the SVD of centred data

Data $X\in\mathbb R^{n\times d}$ (rows = samples), $\mu=\frac1n\sum_i x_i$,
$X_c=X-\mathbf 1\mu^T=U\Sigma V^T$. Sample covariance
$$C=\frac{X_c^TX_c}{n-1}=V\frac{\Sigma^2}{n-1}V^T .$$
Principal axes = columns of $V$, variances $\lambda_j=s_j^2/(n-1)$. Encoding
$z=V_k^T(x-\mu)\in\mathbb R^k$, decoding $\hat x=\mu+V_kz$. By Eckart-Young
applied to $X_c$, this is the best rank-$k$ **affine** reconstruction:
$$\sum_i\lVert x_i-\hat x_i\rVert^2=\sum_{j>k}s_j^2=(n-1)\sum_{j>k}\lambda_j .$$
Explained variance ratio $\sum_{j\le k}\lambda_j/\sum_j\lambda_j$ (`pca`).
PCA is also the linear autoencoder's optimum (note 04).

## 4 Randomised SVD [S18]

Cost of a dense SVD: $O(mn\min(m,n))$. If only $k\ll\min(m,n)$ directions are
needed, find the range first:

1. $\Omega\in\mathbb R^{n\times(k+p)}$ Gaussian, $Y=A\Omega$ (`range_finder`).
2. Optional $q$ power iterations $Y\leftarrow A(A^TY)$, QR after each product
   (otherwise roundoff kills the small directions). Replaces $s_j$ by
   $s_j^{2q+1}$: helps when the spectrum decays slowly.
3. $Q=\operatorname{orth}(Y)$, $B=Q^TA\in\mathbb R^{(k+p)\times n}$, $B=\tilde U\Sigma V^T$,
   $U=Q\tilde U$ (`randomized_svd`).

Cost $O(mn(k+p))$ plus $O(q)$ further passes over $A$. Error guarantee for
$q=0$, $k,p\ge2$ [S18 Thm 10.5]:
$$\mathbb E\lVert A-QQ^TA\rVert_F\le\Big(1+\frac{k}{p-1}\Big)^{1/2}\Big(\sum_{j>k}s_j^2\Big)^{1/2}.$$
With $p=10$ the factor is $\le1.5$ for $k\le 11$: near-optimal at a fraction of the cost.
Tested literally in `test_range_finder_obeys_halko_martinsson_tropp_thm_10_5`.

## 5 Error vs rank: three regimes

**Analytic kernel.** If $f(x,y)$ is analytic in $x$ in a Bernstein ellipse with
parameter $r>1$, the degree-$k$ Chebyshev interpolant in $x$ has error $O(r^{-k})$,
and it is a sum of $k+1$ separable terms $T_j(x)g_j(y)$. So
$s_{k+2}\le\lVert f-f_k\rVert=O(r^{-k})$: **exponential decay**. This is why the
IR basis (note 03) and quantics tensor trains (note 05) exist.

**Noise.** For $A+N$, $N_{ij}\sim\mathcal N(0,\sigma^2)$ i.i.d., the largest
singular value of $N$ is $\approx\sigma(\sqrt m+\sqrt n)$ (random-matrix edge,
checked in `test_noise_edge_threshold_is_near_optimal_denoiser`). Directions of $A$
with $s_j$ below that edge are not recoverable; directions of $A+N$ below it are
noise. Rule: keep $s_j>\sigma(\sqrt m+\sqrt n)$ (`noise_threshold_rank`).

**Random / volume-law data.** Flat spectrum, no useful compression (the random
state in note 05).

## 6 Worked example (`python lowrank.py`)

$A_{ij}=1/(1+25(x_i-y_j)^2)$ on $300\times200$ equispaced points in $[-1,1]^2$
(poles at $x-y=\pm i/5$: analytic, but close to the real axis, so $r$ is modest).

| $k$ | rel. error, clean | rel. error, $+10^{-3}$ noise | randomised ($q=2$) | $\rho_k$ |
|---|---|---|---|---|
| 4 | $3.1\times10^{-1}$ | $3.1\times10^{-1}$ | $3.1\times10^{-1}$ | 0.033 |
| 16 | $8.6\times10^{-3}$ | $8.9\times10^{-3}$ | $8.6\times10^{-3}$ | 0.134 |
| 32 | $7.1\times10^{-5}$ | $2.2\times10^{-3}$ | $7.1\times10^{-5}$ | 0.267 |
| 48 | $5.8\times10^{-7}$ | $1.9\times10^{-3}$ | $5.8\times10^{-7}$ | 0.401 |

Clean: $\approx$ one decade per 8 ranks; $k=47$ for $10^{-6}$. Noisy: floor at the
noise level. Denoising, i.e. truncating $A+N$ and comparing with the **clean** $A$:
error $5.2\times10^{-2}$ ($k=10$), $1.38\times10^{-3}$ ($k=24$),
$1.28\times10^{-3}$ ($k=28$, the noise-edge threshold $\sigma(\sqrt{300}+\sqrt{200})=0.031$),
$1.77\times10^{-3}$ ($k=48$). The optimum is a bias-variance trade-off, and the
threshold finds it without knowing $A$.

## 7 Pitfalls

- PCA without centring: the first "component" is then the mean.
- Mixed units across features: PCA of unscaled data ranks by variance in
  whatever units you chose. Standardise, or justify not doing so.
- Quoting explained variance on noisy data as if it were signal; use the noise
  edge or a held-out reconstruction error.
- Comparing singular vectors across runs: signs (and rotations inside degenerate
  subspaces) are arbitrary. Compare subspaces ($\lVert P_1-P_2\rVert$), not vectors.
- Randomised SVD with $q=0$ on a slowly decaying spectrum: the bound holds only in
  expectation and the constant multiplies a large tail. Use $q=1$-$2$.
- Counting storage in numbers but ignoring precision: $k$ float64 vectors vs raw
  1-bit spins is not a fair ratio (note 04 counts bits).

## 8 Questions

1. **State Eckart-Young for both norms and say why one theorem covers every
   unitarily invariant norm.** $\min_{\operatorname{rank}B\le k}\lVert A-B\rVert$
   is attained at $A_k$ with error $s_{k+1}$ (2-norm) and $(\sum_{j>k}s_j^2)^{1/2}$
   (Frobenius). Mirsky: such norms are symmetric gauge functions of the singular
   values, and $s_{i+k}(A)\le s_i(A-B)$ (Weyl) makes the tail minimal entrywise.
2. **Why are PCA reconstruction error and discarded eigenvalues the same thing?**
   Reconstruction error $=\lVert X_c-X_cV_kV_k^T\rVert_F^2=\sum_{j>k}s_j^2=(n-1)\sum_{j>k}\lambda_j$.
3. **What do power iterations buy in randomised SVD, and what do they cost?**
   Spectrum $s_j\to s_j^{2q+1}$, so the tail relative to $s_k$ shrinks and the
   range finder captures the top-$k$ space more reliably; each iteration costs two
   more passes over $A$ and needs re-orthonormalisation for stability.
4. **Why does a smooth kernel have exponentially decaying singular values?**
   Polynomial interpolation of degree $k$ in one variable gives a separable rank-$(k+1)$
   approximation with error $O(r^{-k})$ for analyticity in a Bernstein ellipse of
   parameter $r$; Eckart-Young bounds $s_{k+2}$ by that error.
5. **You compress noisy data with a truncated SVD. How do you choose $k$?**
   Keep the singular values above the noise edge $\sigma(\sqrt m+\sqrt n)$ (for
   i.i.d. noise of known $\sigma$) or minimise a held-out error; larger $k$ keeps
   fitted noise, smaller $k$ adds bias. In the example the threshold $k=28$
   is at the minimum of the true error.

## Code

`truncate`, `reconstruct`, `eckart_young_error`, `rank_for_tolerance`,
`error_curve`, `noise_threshold_rank`, `compression_ratio`, `pca`, `pca_encode`,
`pca_reconstruct`, `range_finder`, `randomized_svd`, `smooth_kernel_matrix` in
[`lowrank.py`](../src/py/lowrank.py); tests in
[`test_lowrank.py`](../src/py/test_lowrank.py) (sklearn `PCA` cross-check,
Eckart-Young equalities, HMT Thm 10.5, denoising optimum).
