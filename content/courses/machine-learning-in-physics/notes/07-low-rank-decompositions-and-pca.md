# 07 Low-rank decompositions and principal component analysis

TISS topic 7, "Low-rank decompositions, principal component analysis" [S2]; 2021S
videos Low-rank 1-3 (truncated SVD, PCA, tensor networks); exercise 11 "Low-rank
approximations in the Ising model" [S5, S11]. Texts: [S7 sec. 4.6, ch. 10],
[S8 sec. 14.5], [S6 sec. XII.B], [S9 sec. 12.2]. The SVD itself: note 03.
t-SNE/MDS and the ML-side PCA summary:
[CSE note 12](../../machine-learning/notes/12-unsupervised.md).

## Definitions

- **Truncated SVD:** $X_r=\sum_{k<r}s_ku_kv_k^T$.
- **PCA:** centre $\tilde X=X-\mathbf 1\bar x^T$, sample covariance
  $C=\tilde X^T\tilde X/(N-1)$. **Principal axes** $w_k$ = eigenvectors of $C$ =
  right singular vectors $v_k$ of $\tilde X$; **scores** (projections)
  $\tilde XW_r=U_rS_r$; **explained variance** $\lambda_k=s_k^2/(N-1)$; **ratio**
  $\lambda_k/\sum_j\lambda_j$.
- **Reconstruction:** $\hat x=\bar x+W_rW_r^T(x-\bar x)$.

## Derivations

**Maximum variance.** Find unit $w$ maximising the variance of $\tilde Xw$:
$\max_w w^TCw$ s.t. $w^Tw=1$. Lagrangian $w^TCw-\lambda(w^Tw-1)$, stationarity
$Cw=\lambda w$, objective value $\lambda$: take the top eigenvector. The $k$-th
axis maximises variance orthogonal to the first $k-1$ (Rayleigh quotient,
Courant-Fischer) [S7 sec. 10.2].

**Minimum reconstruction error.** For orthonormal $W\in\mathbb R^{K\times r}$,
$\sum_n\|\tilde x_n-WW^T\tilde x_n\|^2=\mathrm{tr}(\tilde X^T\tilde X)-\mathrm{tr}(W^T\tilde X^T\tilde XW)$,
so minimising error = maximising projected variance: same solution [S7 sec. 10.3].

**Eckart-Young** [S29, S7 sec. 4.6]. For any $B$ with $\mathrm{rank}\,B\le r$,

$$\|X-B\|_F^2\ge\|X-X_r\|_F^2=\sum_{k\ge r}s_k^2,\qquad\|X-B\|_2\ge s_r .$$

So the relative error of the best rank-$r$ approximation follows from the
singular values alone: $\epsilon_r=\sqrt{\sum_{k\ge r}s_k^2/\sum_ks_k^2}$
(exercise 11 asks exactly this [S5]).

**PCA via SVD, not via $C$.** $C=VS^2V^T/(N-1)$: forming $C$ squares the
condition number and costs $O(NK^2)$; the thin SVD of $\tilde X$ is stabler.
For $K\gg N$ use the $N\times N$ Gram matrix $\tilde X\tilde X^T=US^2U^T$ instead
[S7 sec. 10.5].

**Probabilistic view.** PPCA $x=Wz+\mu+\epsilon$, $z\sim\mathcal N(0,\mathbb 1)$,
$\epsilon\sim\mathcal N(0,\sigma^2\mathbb 1)$: the ML solution spans the top-$r$
principal subspace [S7 sec. 10.7]. Links PCA to GMMs (note 06) and to linear
autoencoders (note 08).

**Tensor networks (outlook, video Low-rank 3 [S11]).** A state or data tensor
$T_{i_1\dots i_n}$ reshaped into a matrix and truncated by SVD, repeatedly:
matrix product states. The same Eckart-Young error control is DMRG's truncation.
The follow-up course 138.129 PR continues with data compression
([ws2027 folder](../../machine-learning-and-data-compression-in-physics/index.md)).

## Ising configurations: what PCA finds [S16, S5]

Flatten each $L\times L$ snapshot to $x\in\{\pm1\}^{L^2}$. Below $T_c$, samples are
$\approx\pm\mathbf 1$ plus sparse flipped spins, so $\tilde X$ is dominated by one
direction: $w_1\approx\mathbf 1/L$ and the score $=\sqrt{L^2}\,m$ (up to centring
and sign): **PC1 is the magnetisation.** Above $T_c$ spins are nearly independent,
$C\approx\mathbb 1$, and the spectrum is flat.

Randomness is information: ordered data compress (rank 1 suffices), disordered
data do not; the high-$T$ design matrix has the flattest spectrum, i.e. the most
information per sample.

## Worked examples

**3D cloud** (`clustering_pca._demo`): stds $(5,1,0.2)$ in a random rotation,
500 points. Explained variance ratio $(0.959,0.039,0.0015)$; $|\cos|$ between
PC1 and the generating axis $=1.0000$.

**Ising, $L=16$, 26 temperatures $\times$ 200 samples, random global flips**
(`ising._demo`):

- all temperatures pooled: PC1 explains $0.519$, PC2 $0.015$;
  $|\langle w_1,\mathbf 1/L\rangle|=1.000$; $\mathrm{corr}(|\text{score}|,|m|)=0.9999$.
- The variance of $|\text{score}|$ across samples peaks at $T\approx2.4$: a
  susceptibility, locating $T_c(L=16)$ above Onsager's $2.269$ (finite-size shift).

## Pitfalls

- Forgetting to centre: the first "component" is then the mean.
- Unscaled features: PCA ranks by variance, so units decide the answer.
- PCA is linear: a curved manifold needs more components than its dimension
  (note 08: an arc needs $r=2$).
- Sign and, for degenerate eigenvalues, rotation of the axes are arbitrary.
- Projecting new data onto old axes is legitimate; refitting PCA on the test set
  is not.
- Explained variance is not relevance for a downstream label.

## Test-style questions

**Q1.** Derive PCA as a variance maximisation and state the answer via the SVD.
**A.** $\max w^TCw$, $\|w\|=1$ $\Rightarrow Cw=\lambda w$; top eigenvector. With
$\tilde X=USV^T$: axes $v_k$, variances $s_k^2/(N-1)$, scores $u_ks_k$.

**Q2.** $C=\begin{pmatrix}2&1\\1&2\end{pmatrix}$. Principal axes and explained variance ratio?
**A.** Eigenvalues 3, 1; axes $(1,1)/\sqrt2$, $(1,-1)/\sqrt2$; ratio $3/4$, $1/4$.

**Q3.** Give the relative error of a rank-1 approximation from singular values only.
**A.** $\epsilon_1=\sqrt{\sum_{k\ge1}s_k^2}/\sqrt{\sum_ks_k^2}$ (Eckart-Young; Frobenius norm).

**Q4.** Why is PC1 of low-temperature Ising configurations the uniform vector,
and what is its score?
**A.** Configurations are $\approx\pm\mathbf 1$; the variance is concentrated along
$\mathbf 1$ (between the $\pm$ sectors and in $m$). Score $=\mathbf 1^T\tilde x/L=L\,m$
(up to centring): the order parameter, found without labels [S16].

**Q5.** Why do disordered configurations "not compress"?
**A.** Independent spins give $C\approx\mathbb 1$: all $s_k$ comparable, so every
truncation loses a fixed fraction of $\|X\|_F^2$. Information (entropy) per sample is maximal.

## Code

`src/py/clustering_pca.py`: `pca` (SVD; equals `sklearn.decomposition.PCA` up to
sign), `pca_eig`, `explained_variance_ratio`, `truncated_svd` (rank-$r$ and
Eckart-Young error), `subspace_distance`. `src/py/ising.py`: `pca_tc`.
