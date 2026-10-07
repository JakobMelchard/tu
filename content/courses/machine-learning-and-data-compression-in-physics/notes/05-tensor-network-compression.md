# 05 Tensor-network compression: MPS / tensor trains

Note 02 compresses matrices. A tensor with $d$ indices has $d-1$ ways to be cut
into a matrix; a tensor train (TT, in physics: matrix product state, MPS)
truncates all of them in sequence. Wallerberger's recent work compresses
Green's functions this way ("quantics" tensor trains [S16, S32, S34]).

Code: [`../src/py/tt_svd.py`](../src/py/tt_svd.py).

## 1 Definitions [S24, S25, S26]

- **Tensor** $T_{s_1\dots s_d}$, $s_k\in\{1..n_k\}$; $\prod_kn_k$ numbers.
- **Tensor train / MPS**: $T_{s_1\dots s_d}=G_1[s_1]G_2[s_2]\cdots G_d[s_d]$ with
  $G_k[s_k]\in\mathbb R^{r_{k-1}\times r_k}$, $r_0=r_d=1$. **Bond dimensions** $r_k$
  ($\chi$ in physics). Parameters $\sum_kr_{k-1}n_kr_k$ (`tt_num_params`).
- **Unfolding** $T^{\langle k\rangle}\in\mathbb R^{(n_1\cdots n_k)\times(n_{k+1}\cdots n_d)}$.
  Any TT has $r_k\ge\operatorname{rank}T^{\langle k\rangle}$, and TT-SVD attains equality [S26].
- **Left-orthogonal core**: $\sum_{s,a}G_k[s]_{ab}G_k[s]_{ab'}=\delta_{bb'}$
  (reshaped $(r_{k-1}n_k)\times r_k$ matrix with orthonormal columns).
- **Schmidt values** of a state $\psi$ at cut $k$: singular values $\lambda_\alpha$ of
  $\psi^{\langle k\rangle}$; entanglement entropy $S_k=-\sum_\alpha\lambda_\alpha^2\ln\lambda_\alpha^2$
  (normalised $\psi$) (`schmidt_values`, `entanglement_entropy`).

## 2 TT-SVD and its error [S26]

Algorithm (`tt_svd`): $C\leftarrow T$ reshaped $1\times\prod n$. For $k=1..d-1$:
reshape $C$ to $(r_{k-1}n_k)\times(\text{rest})$, SVD $C=U\Sigma V^T$, keep $r_k$
columns, $G_k=U_{:,1..r_k}$ (left-orthogonal), $C\leftarrow\Sigma_{r_k}V_{r_k}^T$. Last core $=C$.

**Error identity.** Let $\varepsilon_k$ be the Frobenius norm discarded at cut $k$.
Then $\lVert T-\tilde T\rVert_F^2=\sum_k\varepsilon_k^2$.
*Proof.* At step $k$, $C=U_rS_rV_r^T+E_k$ with $E_k=U_\perp S_\perp V_\perp^T$.
Everything later is built from $S_rV_r^T$ and multiplied from the left by the
left-orthogonal prefix $Q_{\le k}$, whose columns are orthogonal to the prefix
times $U_\perp$. So $T-\tilde T=\sum_kQ_{<k}E_k+\dots$ is a sum of mutually orthogonal
pieces, each isometrically embedded: norms add in squares. $\square$

Hence choosing per-cut tolerance $\delta=\varepsilon\lVert T\rVert_F/\sqrt{d-1}$ guarantees
$\lVert T-\tilde T\rVert_F\le\varepsilon\lVert T\rVert_F$ (Oseledets' bound $\sqrt{d-1}\,\delta$ [S26];
`rel_eps`). And at every single cut, Eckart-Young gives the lower bound
$\lVert T-\tilde T\rVert_F\ge(\sum_{\alpha>\chi}\lambda^{(k)2}_\alpha)^{1/2}$: TT-SVD is at most
a factor $\sqrt{d-1}$ from optimal. Both tested in
`test_error_equals_root_sum_of_discarded_weights`.

## 3 When is a tensor TT-compressible?

**Quantum states.** $\chi$ at cut $k$ must be at least the Schmidt rank; to
discard weight $\epsilon^2$ one keeps the $\lambda_\alpha$ with tail $\le\epsilon^2$. A rough
count: $\chi\gtrsim e^{S_k}$.

- Ground states of gapped 1D local Hamiltonians: **area law**, $S_k$ bounded
  in $n$, $\chi$ independent of $n$ [S24, S25].
- Critical 1D ground states: $S$ grows like $\log n$ with a prefactor set by the
  central charge [S25], so $\chi$ grows polynomially in $n$.
- Random states: $S$ near maximal (Page), $\chi$ exponential in $n$: no compression.

**Functions on a grid (quantics).** Sample $f$ at $x_j=j/2^R$, write
$j=\sum_kb_k2^{R-1-k}$ and treat $f(x(b_0..b_{R-1}))$ as a $(2,\dots,2)$ tensor
(`quantics`). Then
- $e^{ax}=\prod_ke^{ab_k2^{-k-1}}$: rank 1.
- $\sin(ax+c)$: $\sin(\alpha+\beta)=\sin\alpha\cos\beta+\cos\alpha\sin\beta$ splits every cut into 2 terms: rank $\le2$.
- degree-$p$ polynomial: $(u+v)^p$ binomial: rank $\le p+1$.
- A function with structure on many scales (a narrow Gaussian, a Green's function
  with $\beta\omega_{\max}\gg1$) has modest ranks where a uniform grid would need $2^R$ points.
  This is the multiscale ansatz of [S16]; tensor cross interpolation builds the TT from
  at most $O(R\chi^2)$ function evaluations and $O(R\chi^3)$ time, never forming
  the $2^R$ tensor [S32].

## 4 Worked example (`python tt_svd.py`)

Transverse-field Ising chain $H=-\sum Z_iZ_{i+1}-g\sum X_i$, $n=12$ (4096
amplitudes), ground state by Lanczos (`tfim_ground_state`); relative error vs
maximal bond dimension $\chi$:

| $\chi$ | $g=0.5$ | $g=1$ (critical) | random state | parameters |
|---|---|---|---|---|
| 1 | 0.99 | 0.79 | 1.00 | 24 |
| 2 | $4.7\times10^{-2}$ | $7.2\times10^{-2}$ | 0.99 | 88 |
| 4 | $6.5\times10^{-4}$ | $2.4\times10^{-3}$ | 0.97 | 296 |
| 8 | $6.8\times10^{-6}$ | $3.0\times10^{-5}$ | 0.90 | 936 |
| 16 | $6.5\times10^{-10}$ | $6.8\times10^{-9}$ | 0.72 | 2728 |

Half-chain entropy: 0.696 ($g=0.5$), 0.397 ($g=1$), 3.656 (random; Page value
$\approx6\ln2-\tfrac12=3.659$). Note $g=0.5$: the finite-chain ground state is the
symmetric cat $(\lvert\Uparrow\rangle+\lvert\Downarrow\rangle)/\sqrt2$ dressed by
fluctuations, $S\approx\ln2$, so $\chi=1$ fails and $\chi=2$ is already good.

Quantics, $R=16$ (65536 points), tolerance $10^{-10}$: $e^{-3x}$ ranks all 1
(32 parameters); $\sin(10\pi x)$ ranks $\le2$ (114); $x^3-x$ ranks $\le4$ (342);
Gaussian of width 0.01 ranks $\le10$ (854 parameters).

## 5 Pitfalls

- TT-SVD needs the full tensor: exponential memory. It is a reference and a test
  oracle; for large $d$ use DMRG / variational MPS [S25] or TCI [S32].
- Index order matters: ranks depend on which indices are neighbours (bit order in
  quantics: most significant first; interleaving of several variables [S16]).
- Degenerate ground states (symmetry-broken phases on finite systems): Lanczos
  returns some vector in the degenerate space; its entanglement depends on which.
- Relative vs absolute tolerance, and per-cut vs global: state which.
- Counting parameters without counting what the downstream operation costs:
  contracting two TTs costs $O(d\,n\,\chi^3)$.

## 6 Questions

1. **Why is the TT-SVD error exactly the root-sum-square of the per-cut
   discarded weights?** The discarded pieces are multiplied by left-orthogonal
   prefixes and are orthogonal to everything kept afterwards; orthogonal errors add
   in squares.
2. **Give a lower bound on the error of any TT with bond dimension $\chi$.**
   At every cut the TT is a rank-$\chi$ matrix, so by Eckart-Young the error is at
   least $(\sum_{\alpha>\chi}\lambda_\alpha^{(k)2})^{1/2}$ for every $k$.
3. **Why does the area law make MPS efficient, and why does a random state not
   compress?** Bounded $S_k$ means the Schmidt spectrum decays fast enough that a
   fixed $\chi$ captures it independent of $n$; a random state has an almost flat
   Schmidt spectrum of size $2^{n/2}$.
4. **Show that $e^{ax}$ and $\sin(ax)$ on a $2^R$ quantics grid have TT ranks 1 and 2.**
   $x=\sum_kb_k2^{-k-1}$: the exponential factorises over bits; $\sin$ of a sum of
   two partial sums is a sum of two products.
5. **When would you prefer the IR (note 03) over a quantics TT for a Green's function,
   and vice versa?** IR: one variable, known kernel, $O(\log\Lambda)$ coefficients with
   a priori error; quantics TT: several variables (two-particle, momentum
   dependence), no kernel needed, exploits scale separation [S16, S34].

## Code

`tt_svd`, `tt_to_full`, `tt_ranks`, `tt_num_params`, `schmidt_values`,
`entanglement_entropy`, `tfim_ground_state`, `ghz`, `random_state`, `quantics`,
`error_vs_bond_dimension` in [`tt_svd.py`](../src/py/tt_svd.py); tests in
[`test_tt_svd.py`](../src/py/test_tt_svd.py).
