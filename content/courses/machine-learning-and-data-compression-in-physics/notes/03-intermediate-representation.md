# 03 The intermediate representation (IR) for Green's functions

The IR is note 02 applied to the kernel that maps a spectral function to an
imaginary-time propagator. Its authors include Wallerberger [S10, S12, S13], and
it is the most likely technical core of a project with him. This note derives the
kernel, its singular value expansion (SVE), why it compresses, and sparse sampling.

Code: [`../src/py/ir_toy.py`](../src/py/ir_toy.py). Production code: sparse-ir [S14].

## 1 The kernel

Fermionic $G(\tau)=-\langle T_\tau c(\tau)c^\dagger(0)\rangle$, $0<\tau<\beta$.
Lehmann, $Z=\sum_m e^{-\beta E_m}$, $c(\tau)=e^{\tau H}ce^{-\tau H}$:
$$G(\tau)=-\frac1Z\sum_{mn}e^{-\beta E_m}e^{-\tau(E_n-E_m)}\lvert\langle m|c|n\rangle\rvert^2 .$$
Spectral function $\rho(\omega)=\frac1Z\sum_{mn}\lvert\langle m|c|n\rangle\rvert^2(e^{-\beta E_m}+e^{-\beta E_n})\,\delta(\omega-E_n+E_m)$.
On the support, $e^{-\beta E_m}/(e^{-\beta E_m}+e^{-\beta E_n})=1/(1+e^{-\beta\omega})$, hence
$$G(\tau)=-\int d\omega\,K(\tau,\omega)\rho(\omega),\qquad K(\tau,\omega)=\frac{e^{-\tau\omega}}{1+e^{-\beta\omega}},$$
the **logistic kernel**, sparse-ir eq. (3) with the $+$ sign [S13]. Evaluate it as
$e^{(\beta-\tau)\omega}/(1+e^{\beta\omega})$ for $\omega<0$ to avoid overflow
(`logistic_kernel`). Sum rule: $K(0,\omega)+K(\beta,\omega)=1\Rightarrow G(0^+)+G(\beta^-)=-\int\rho$.

**Matsubara.** $\nu_n=(2n+1)\pi/\beta$, $e^{i\nu_n\beta}=-1$:
$$\int_0^\beta d\tau\,e^{i\nu_n\tau}K(\tau,\omega)=\frac{e^{(i\nu_n-\omega)\beta}-1}{(i\nu_n-\omega)(1+e^{-\beta\omega})}=\frac{1}{\omega-i\nu_n},$$
so $G(i\nu_n)=\int d\omega\,\rho(\omega)/(i\nu_n-\omega)$ as it must. Used in `IRBasis.uhat`.

**Single pole** $\rho=\delta(\omega-\epsilon)$: $G(\tau)=-e^{-\tau\epsilon}/(1+e^{-\beta\epsilon})$,
$G(i\nu)=1/(i\nu-\epsilon)$. The closed form every test checks against (`single_pole`).

## 2 Singular value expansion

Restrict $\omega\in[-\omega_{\max},\omega_{\max}]$. $K$ is continuous on a
compact rectangle, so it is a Hilbert-Schmidt operator
$L^2[-\omega_{\max},\omega_{\max}]\to L^2[0,\beta]$ and has an SVE [S10, S13]
$$K(\tau,\omega)=\sum_{l\ge0}U_l(\tau)S_lV_l(\omega),\quad \int_0^\beta U_lU_{l'}=\int V_lV_{l'}=\delta_{ll'},\quad S_0>S_1>\dots>0 .$$

Properties (all tested):

- **One parameter.** With $x=2\tau/\beta-1$, $y=\omega/\omega_{\max}$ the kernel
  becomes $e^{-\Lambda y(x+1)/2}/(1+e^{-\Lambda y})$, $\Lambda=\beta\omega_{\max}$;
  the measure gives $S_l=\sqrt{\beta\omega_{\max}/2}\,s_l(\Lambda)$ [S13]. Ratios
  $S_l/S_0$ depend on $\Lambda$ only.
- **Parity.** $K(\beta-\tau,-\omega)=K(\tau,\omega)\Rightarrow U_l(\beta-\tau)=(-1)^lU_l(\tau)$,
  $V_l(-\omega)=(-1)^lV_l(\omega)$. Hence $\hat U_l(i\nu)$ is purely imaginary for
  even $l$ and purely real for odd $l$ (`test_uhat_is_fourier_transform_of_u`).
- **Oscillation.** $U_l$ has $l$ roots, like orthogonal polynomials (checked
  numerically: `tau_sampling_points` finds exactly $L$ roots of $U_L$).
- **Exponential decay** of $S_l$, and a basis size $L(\varepsilon)$ with
  $S_L/S_0<\varepsilon$ that grows only logarithmically with $\Lambda$ [S13].

## 3 The IR and why it compresses

Insert the SVE into the spectral representation:
$$G(\tau)=\sum_lG_lU_l(\tau),\qquad G_l=-S_l\rho_l,\quad \rho_l=\int d\omega\,V_l(\omega)\rho(\omega).$$
$\lvert\rho_l\rvert\le\lVert\rho\rVert_2$ (Cauchy-Schwarz), and for a normalised
positive $\rho$ also $\lvert\rho_l\rvert\le\sup\lvert V_l\rvert$. Truncation after $L$ terms:
$$\Big\lVert G-\sum_{l<L}G_lU_l\Big\rVert_2^2=\sum_{l\ge L}S_l^2\rho_l^2\le S_L^2\lVert\rho\rVert_2^2 .$$
So **$L$ is fixed by the kernel and $\varepsilon$, not by $\rho$**: the basis is
model-independent [S10]. The compression is the information the kernel destroys:
directions $V_l$ with $S_l<\varepsilon S_0$ of $\rho$ are invisible in $G$ at
precision $\varepsilon$. The same fact makes analytic continuation ill-posed (note 06).

Counting: $L(\Lambda=1,10,100,1000)=6,12,26,43$ at $\varepsilon=10^{-8}$ (`basis_size_vs_lambda`).
Ten times $\Lambda$ costs $\sim15$ more coefficients.

**Particle-hole symmetry.** $\rho(-\omega)=\rho(\omega)$ and $V_l$ of parity
$(-1)^l$ give $\rho_l=0$ for odd $l$: half the coefficients vanish.

## 4 Discretised SVE (what `IRBasis` does)

Composite Gauss-Legendre rules $(\tau_i,w_i)$, $(\omega_j,w_j')$, panels refined
geometrically towards $\tau=0,\beta$ (scale $1/\omega_{\max}$) and $\omega=0$
(scale $1/\beta$). Then
$$A_{ij}=\sqrt{w_i}\,K(\tau_i,\omega_j)\sqrt{w_j'}=\sum_l\hat U_{il}S_l\hat V_{jl},\qquad U_l(\tau_i)\approx\hat U_{il}/\sqrt{w_i}.$$
Off the nodes use the Nyström extension
$U_l(\tau)=S_l^{-1}\sum_jK(\tau,\omega_j)\sqrt{w_j'}\hat V_{jl}$ and the same with
$1/(\omega_j-i\nu)$ for $\hat U_l(i\nu)$. Roundoff in $U_l$ is
$\sim\epsilon_{\rm mach}S_0/S_l$, so double precision limits the toy to
$\varepsilon\approx10^{-8}$. sparse-ir reaches $10^{-15}$ with piecewise Legendre
bases and extended-precision arithmetic [S13] (Wallerberger's `libxprec` [S7]); its
predecessor irbasis shipped a precomputed database of bases for fixed $\Lambda$ [S11].

## 5 Sparse sampling

Store $L$ coefficients, but compute with values. Pick $L$ times $\bar\tau_k$,
$F_{kl}=U_l(\bar\tau_k)$; then $G(\bar\tau_k)=\sum_lF_{kl}G_l$ and the fit is
$G_l=F^{+}G(\bar\tau)$. The choice of points sets $\operatorname{cond}F$:

| rule | $\operatorname{cond}F$ ($\Lambda=100$, $L=26$) |
|---|---|
| roots of $U_L$ (`tau_sampling_points("roots")`) | 5.3 |
| extrema of $U_{L-1}$, end points moved inwards [S13] (`"extrema"`) | 7.3 |
| $L$ equally spaced $\tau$ | $2.3\times10^{9}$ |

Li et al. [S12] use midpoints of the roots of $U_{L-1}$ and $0,\beta$; all three
good rules interleave with the roots, as Gauss points do for polynomials.
Matsubara: take the $n$ at the sign changes of the non-vanishing part of
$\hat U_L(i\nu_n)$ and mirror $n\to-n-1$ (28 frequencies, max $\lvert n\rvert=127$,
$\operatorname{cond}=15.5$). sparse-ir adds four frequencies for conditioning and
solves via a stored SVD of $F$ instead of a pseudoinverse (backward stability) [S13].

**Workflow in a diagrammatic code** (the sparse-ir README example is second-order
perturbation theory [S14]): $G_l\to G(\bar\tau_k)$; form $\Sigma(\bar\tau_k)=U^2G(\bar\tau_k)^2G(\beta-\bar\tau_k)$
pointwise; fit $\Sigma_l$; evaluate $\Sigma(i\bar\nu_n)$; Dyson
$G^{-1}=G_0^{-1}-\Sigma$ at the $\bar\nu_n$; fit $G_l$; iterate. Every step is
$O(L^2)$ instead of $O(N_\tau)$ or $O(N_\nu)$ with $N\sim10^4$.

## 6 Worked example (`python ir_toy.py`, $\beta=\omega_{\max}=10$)

- $L=26$ at $\varepsilon=10^{-8}$; $S_l/S_0$ at $l=0,5,\dots,25$:
  $1,\ 1.3\times10^{-1},\ 5.7\times10^{-3},\ 1.4\times10^{-4},\ 1.9\times10^{-6},\ 1.6\times10^{-8}$.
- Single pole $\epsilon=0.7$ from 26 sampled times: max error of $G(\tau)$ on 1001
  points $6.2\times10^{-9}$. A uniform grid with linear interpolation needs
  $32768$ points for the same error (`uniform_grid_points_needed`).
- The same pole from 28 Matsubara values: max error over 4000 frequencies
  $9.6\times10^{-10}$; the fitted $G_l$ equal the $\tau$-projection to $10^{-7}$.
- Two symmetric Gaussians at $\pm1.5$: $\lvert G_l\rvert$ for $l=0,4,8,\dots$:
  $0.39,\ 9.2\times10^{-2},\ 7.6\times10^{-3},\ 1.1\times10^{-4},\ 5.9\times10^{-6},\ 7.5\times10^{-8},\ 1.1\times10^{-9}$;
  odd $l$: $<4\times10^{-16}$.

## 7 Pitfalls

- $\omega_{\max}$ smaller than the spectral support: $G$ is then not in the span
  and the error bound is void. Check $\lvert G_l\rvert$ still decays at $l\approx L$.
- Noisy input (QMC): $G_l$ stop decaying at the noise level. Truncate there, not
  at $\varepsilon$; fitting beyond it amplifies noise by $S_0/S_l$ in $\rho_l$.
- Sign and statistics conventions: bosonic propagators need the bosonic
  frequencies and, in sparse-ir, the logistic kernel is used for both [S13].
- Fitting with $F^{-1}$ when $F$ is not square (Matsubara): least squares.
- Comparing basis functions across codes: signs are conventions (`IRBasis` fixes
  $\hat U_{0l}>0$).
- Double-precision SVE: the last basis functions are accurate only to
  $\epsilon_{\rm mach}S_0/S_l$; do not push $\varepsilon$ below $10^{-10}$ in the toy.

## 8 Questions

1. **Derive the logistic kernel from the Lehmann representation.** Above:
   weight $e^{-\beta E_m}$ over $e^{-\beta E_m}+e^{-\beta E_n}$ equals
   $1/(1+e^{-\beta\omega})$ with $\omega=E_n-E_m$, leaving $e^{-\tau\omega}$.
2. **Why is the IR basis size nearly independent of the physics?** $G_l=-S_l\rho_l$
   with $\rho_l$ bounded for any admissible $\rho$; truncation error $\le S_L\lVert\rho\rVert$,
   so $L$ is set by $\Lambda$ and $\varepsilon$ only.
3. **What does parity buy?** $U_l(\beta-\tau)=(-1)^lU_l(\tau)$ from
   $K(\beta-\tau,-\omega)=K(\tau,\omega)$; $\hat U_l$ purely real or imaginary;
   particle-hole symmetric $\rho$ has only even $\rho_l$; the SVE block-diagonalises [S13].
4. **Why not sample $G$ at $L$ equally spaced times?** $U_l$ oscillate faster near
   $\tau=0,\beta$ (scale $1/\omega_{\max}$); uniform points under-resolve the ends and
   $\operatorname{cond}F=2.3\times10^9$ vs $5$ for roots of $U_L$.
5. **How would you check an IR code?** Single pole in closed form in both $\tau$
   and $i\nu$; orthonormality on an independent quadrature; parity; $L(\Lambda)$
   logarithmic; if installed, $S_l/S_0$ against sparse-ir (`test_against_sparse_ir_if_installed`).

## Code

`logistic_kernel`, `composite_gauss`, `matsubara`, `IRBasis` (`u`, `v`, `uhat`,
`tau_sampling_points`, `matsubara_sampling_points`, `fit`, `project`),
`single_pole`, `rho_coefficients`, `basis_size_vs_lambda`,
`uniform_grid_points_needed` in [`ir_toy.py`](../src/py/ir_toy.py); tests in
[`test_ir_toy.py`](../src/py/test_ir_toy.py). Next step for real work:
`pip install sparse-ir`, then `FiniteTempBasis('F', beta, wmax, eps)`,
`TauSampling`, `MatsubaraSampling` [S14].
