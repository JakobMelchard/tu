# 02 Trigonometric interpolation and the FFT

[S4] §1.9: **marked (CSE)**, so it is in this course and not in the Visual
Computing variant, and no public past paper covers it ([00](00-exam-focus.md)).
Still part of chapter 1: it is interpolation, with $e^{ijx}$ in place of $x^j$.
The DFT is the change of basis; the FFT is the observation that the basis-change
matrix factors. Implementation: `src/py/fft.py`, `src/cpp/fft.cpp`.

Convention throughout [S4 §1.9]: $i=\sqrt{-1}$ is the imaginary unit, never an
index; vector indices start at $0$.

## 1. Trigonometric interpolation [S4 §1.9.1]

A classical trigonometric polynomial is
$$p(x)=a_0+\sum_{j=1}^m a_j\cos(jx)+b_j\sin(jx)=\sum_{j=-m}^{m}c_je^{ijx},$$
with $c_j=\tfrac12(a_j-ib_j)$ for $j\ge1$, $c_j=\tfrac12(a_j+ib_j)$ for $j<0$,
$c_0=a_0$ [S4 (1.32)–(1.34)]. It is $2\pi$-periodic, so the knots are taken in
$[0,2\pi)$. Interpolation problem: given $2m+1$ knots and values, find the
$a_j,b_j$ with $p(x_k)=y_k$ [S4 (1.33)].

**Simplification** [S4 §1.9.1]. Multiplying by $e^{imx}$ turns the two-sided sum
into a one-sided one, so it suffices to solve, for $n$ knots,
$$\text{find } p(x)=\sum_{j=0}^{n-1}c_je^{ijx}\ \text{ with } p(x_j)=y_j \qquad\text{[S4 Def. 1.40, (1.36)]}.$$
**Unique solvability** [S4 Thm 1.43]: with $z_j=e^{ix_j}$ the system matrix is
the Vandermonde matrix in the $z_j$, whose determinant $\prod_{j<k}(z_k-z_j)$ is
non-zero because the $z_j$ are distinct.

Why anyone cares [S4 Rem. 1.39]: the continuous Fourier series
$f(x)=\sum_j f_je^{ixj}$, $f_j=\tfrac1{2\pi}\int_0^{2\pi}f(x)e^{-ixj}dx$ needs
integrals; instead sample $f$, interpolate trigonometrically, and read off the
coefficients of $p$ as approximations to the $f_j$.

## 2. The DFT matrix [S4 §1.9.1, Def. 1.44–1.46]

Take the **uniform** knots $x_j=2\pi j/n$, $j=0..n-1$ [S4 (1.37)], and set
$$\omega_n:=e^{-2\pi i/n},\qquad V_n:=\big(\omega_n^{jk}\big)_{j,k=0}^{n-1},\qquad \omega_n^n=1,\ \ \omega_n^j=e^{-ix_j}.$$
**Theorem** [S4 Thm 1.45]: $\tfrac1{\sqrt n}V_n$ is symmetric and **unitary**,
$\big(\tfrac1{\sqrt n}V_n\big)^{-1}=\tfrac1{\sqrt n}\overline{V_n}$, and the
interpolation coefficients are $c=\tfrac1n\overline{V_n}\,y$, i.e.
$c_k=\tfrac1n\sum_{j}\omega_n^{-jk}y_j$. Proof: the columns of
$\tfrac1{\sqrt n}V_n$ are orthonormal: the diagonal entries are $1$ and the
off-diagonal ones are geometric sums $\tfrac1n\frac{1-(\omega_n^{n})^{l-k}}{1-\omega_n^{l-k}}=0$.

$$F_n:\ \mathbb C^n\to\mathbb C^n,\quad y\mapsto V_ny \qquad\text{(DFT of length }n)\quad\text{[S4 Def. 1.46]},$$
$$F_n^{-1}y=\tfrac1n\overline{V_n}\,y=\tfrac1n\overline{F_n(\bar y)}\qquad\text{[S4 Rem. 1.47]},$$
so the IDFT is the DFT with a conjugation and a $1/n$: no separate algorithm
needed. Componentwise this is the familiar pair
$$X_k=\sum_{j=0}^{n-1}x_j\,\omega_n^{jk},\qquad x_j=\frac1n\sum_{k=0}^{n-1}X_k\,\omega_n^{-jk},$$
which is exactly `numpy.fft.fft` / `ifft` [S20]: same sign, same placement of
the $1/n$. (Some texts put $1/\sqrt n$ on both sides; ours does not.)

Consequences of unitarity: **Parseval** $\sum_j|x_j|^2=\tfrac1n\sum_k|X_k|^2$;
$\kappa_2(F_n/\sqrt n)=1$, so the DFT is perfectly conditioned and the FFT is
backward stable with relative error $O(u\log n)$ *([S12]; [S4] does not discuss
FFT round-off)*.

Reading a spectrum: sampling at $t_j=j\Delta t$ over $T=n\Delta t$, bin $k$ is
frequency $k/T$ up to the Nyquist frequency $1/(2\Delta t)$, and bins $k>n/2$ are
the negative frequencies $k-n$. A real signal has $X_{n-k}=\overline{X_k}$.

## 3. The FFT [S4 §1.9.2]: decimation in frequency

Naively $V_ny$ costs $O(n^2)$. Let $n=2m$ and $\omega=e^{\pm2\pi i/n}$,
$\xi=\omega^2$. Splitting the *output* index by parity [S4 Lem. 1.48]:
$$\alpha_{2\ell}=\sum_{j=0}^{m-1}g_j\,\xi^{j\ell},\quad g_j:=y_j+y_{j+m},\qquad
\alpha_{2\ell+1}=\sum_{j=0}^{m-1}h_j\,\xi^{j\ell},\quad h_j:=(y_j-y_{j+m})\,\omega^{j}.$$
So one length-$n$ DFT becomes two length-$m$ DFTs plus $O(n)$ work
[S4 Alg. 3]:

```
FFT(n, y):
    if n == 1: return y
    w := exp(-2*pi*i/n);  m := n/2
    g[j] := y[j] + y[j+m]                 for j = 0..m-1
    h[j] := (y[j] - y[j+m]) * w**j        for j = 0..m-1
    (yhat[0], yhat[2], ..., yhat[n-2]) := FFT(m, g)
    (yhat[1], yhat[3], ..., yhat[n-1]) := FFT(m, h)
```

IFFT is the same with $\omega=e^{+2\pi i/n}$ and a factor $\tfrac12$ on both $g$
and $h$ [S4 Alg. 4]: the $n$ halvings supply the $1/n$ of [S4 Rem. 1.47].

**Cost** [S4 §1.9.2]: $A(n)\le2A(n/2)+Cn$, unrolled $p=\log_2n$ times gives
$A(n)\le nA(1)+Cn\log_2 n = O(n\log n)$. For $n=2^{20}$ that is $2\cdot10^7$
against $10^{12}$ operations. [S4 Ex. 1.49] times MATLAB's FFT against a naive
DFT on $f(t)=3\sin(100\pi t)+\sin(240\pi t)$ and sees exactly $O(N\log N)$.

**This is decimation in frequency** (Sande–Tukey): the *input* is untouched and
the *output* comes out in bit-reversed order. The mirror-image variant
(decimation in time, Cooley–Tukey) splits the input by parity,
$$X_k=E_k+\omega_n^kO_k,\qquad X_{k+n/2}=E_k-\omega_n^kO_k,$$
with $E,O$ the DFTs of the even- and odd-indexed samples; it needs the **input**
bit-reversed and is what the in-place loop below (and `fft.cpp`) implements. Both
are $\tfrac n2\log_2n$ complex multiplications and $n\log_2n$ additions; [S4]
presents only the DIF form, so know that one for the exam.

*Bit reversal:* for $n=8$ the leaf order is $(0,4,2,6,1,5,3,7)$. In place:

```
X <- x[bitrev]
for s = 2, 4, ..., n:
    w_s = exp(-2*pi*i/s)
    for start = 0, s, 2s, ...:
        w = 1
        for k = 0 .. s/2-1:
            u = X[start+k];  v = w * X[start+k+s/2]
            X[start+k] = u + v;  X[start+k+s/2] = u - v
            w *= w_s
```

**Worked example**, $n=4$, $y=(1,2,3,4)$, $\omega_4=-i$. DIF: $m=2$,
$g=(1+3,\,2+4)=(4,6)$, $h=\big((1-3)\omega^0,(2-4)\omega^1\big)=(-2,\,2i)$.
$F_2(g)=(10,-2)\to\hat y_0=10,\hat y_2=-2$; $F_2(h)=(-2+2i,\,-2-2i)\to
\hat y_1=-2+2i,\hat y_3=-2-2i$. Check against the definition:
$X_1=1+2(-i)+3(-1)+4(i)=-2+2i$ ✓.

## 4. Properties of the DFT and fast convolution [S4 §1.9.3–1.9.4]

A sequence $f=(f_j)_{j\in\mathbb Z}$ is $n$-**periodic** if $f_{j+n}=f_j$;
$\mathbb C^n_{\mathrm{per}}$ denotes these [S4 Def. 1.50]. The **convolution** of
$f,g\in\mathbb C^n_{\mathrm{per}}$ is
$$(f*g)_k=\sum_{j=0}^{n-1}f_{k-j}\,g_j .$$
**Convolution theorem** [S4 Thm 1.52]: $\widehat{f*g}=\hat f\cdot\hat g$
componentwise. Naive cost $O(n^2)$ [S4 Ex. 1.55]; with three FFTs it is
$O(n\log n)$.

Finite (non-periodic) sequences are handled by zero-padding to
$n\ge L_1+L_2-1$ [S4 Ex. 1.56]; too little padding wraps the tail around
(circular aliasing). Applications named in [S4]:

- **Polynomial multiplication** [S4 Ex. 1.57]: coefficients of $\pi_1\pi_2$ are
  the convolution of the coefficient vectors. Example:
  $(1,2,3)*(4,5,6,7)=(4,13,28,34,32,21)$, padded to $n=8$.
- **Multiplying numbers with many digits** [S4 Ex. 1.58].
- **Circulant systems** [S4 Ex. 1.59]: a circulant $C$ is diagonalised by the
  DFT, so $Cx=b$ costs $O(n\log n)$: $x=F^{-1}\big(\hat b/\hat c\big)$.
- **Periodic differential equations** [S4 Ex. 1.60], where the discretisation
  matrix is circulant. Differentiation becomes multiplication by $ik$.

Also useful, not in [S4]: correlation is $\overline{\hat f}\cdot\hat g$; a
streaming filter uses overlap-add.

## 5. Real signals

Half a real spectrum is redundant ($X_{n-k}=\overline{X_k}$), so a complex FFT
wastes a factor 2.

**Two real transforms in one complex one.** With $z=x+iy$, $Z=F_n(z)$:
$$X_k=\tfrac12\big(Z_k+\overline{Z_{n-k}}\big),\qquad Y_k=\tfrac1{2i}\big(Z_k-\overline{Z_{n-k}}\big).$$
**A length-$n$ real transform from a length-$n/2$ complex one.** Pack
$z_j=x_{2j}+ix_{2j+1}$, split $Z$ as above into $E=F(x_{\mathrm{even}})$,
$O=F(x_{\mathrm{odd}})$, then one butterfly stage $X_k=E_k+\omega_n^kO_k$ for
$k=0..n/2$. This is `numpy.fft.rfft`, output length $n/2+1$ [S20].
*(Neither is in [S4]; both are standard and both are implemented.)*

## Pitfalls

- Length not a power of two: the radix-2 code must refuse (ours does). Zero
  padding *changes the spectrum*: fine for convolution, misleading for spectral
  estimation.
- Mixing the two decimations. [S4 Alg. 3] combines $y_j\pm y_{j+m}$ (halves of
  the input, output bit-reversed); the in-place loop combines even/odd samples
  (input bit-reversed). Writing the $\omega^j$ twiddle on the wrong branch gives
  a permuted, plausible-looking, wrong answer.
- Forgetting the $\tfrac12$ per level in [S4 Alg. 4], or applying $1/n$ twice.
- Circular vs linear convolution: pad to at least $L_1+L_2-1$.
- Bin $k$ is frequency $k/T$, not $k$; bins above $n/2$ are negative frequencies.
- Leakage: a tone that does not complete a whole number of periods in $T$ smears
  over many bins.
- Believing the FFT is less accurate than the direct DFT. It is *more* accurate,
  $O(u\log n)$ against $O(un)$ [S12].

## Exam-style questions

No public past paper reaches this chapter (it is CSE-only, [00](00-exam-focus.md)),
so these are ours, written against [S4] §1.9 in the style of the true/false and
"derive and state the cost" items that the rest of the papers use.

1. *State the trigonometric interpolation problem and prove it is uniquely
   solvable.*
   Find $p(x)=\sum_{j=0}^{n-1}c_je^{ijx}$ with $p(x_j)=y_j$ for distinct
   $x_j\in[0,2\pi)$; with $z_j=e^{ix_j}$ this is a Vandermonde system in the
   distinct $z_j$, $\det=\prod_{j<k}(z_k-z_j)\ne0$ [S4 Thm 1.43].
2. *Show that $\tfrac1{\sqrt n}V_n$ is unitary and deduce the inversion formula.*
   Column inner products: $1$ on the diagonal, and for $k\ne l$ a geometric sum
   $\tfrac1n\frac{1-(\omega_n^n)^{l-k}}{1-\omega_n^{l-k}}=0$ since $\omega_n^n=1$.
   Hence $V_n^{-1}=\tfrac1n\overline{V_n}$ and $c=\tfrac1n\overline{V_n}y$
   [S4 Thm 1.45].
3. *Derive the splitting of [S4 Lem. 1.48] and the $O(n\log n)$ count.*
   $\alpha_{2\ell}$ uses $\omega^{2\ell j}$ and $\omega^{n\ell}=1$, giving
   $g_j=y_j+y_{j+m}$; $\alpha_{2\ell+1}$ picks up the extra $\omega^j$, giving
   $h_j=(y_j-y_{j+m})\omega^j$. Then $A(n)\le2A(n/2)+Cn$, and unrolling
   $p=\log_2n$ times gives $A(n)\le nA(1)+Cpn$.
4. *Compute the DFT of $(1,0,-1,0)$.*
   $X_k=1-(-i)^{2k}=1-(-1)^k$: $(0,2,0,2)$.
5. *How do you multiply two degree-1000 polynomials in $O(n\log n)$, and why does
   the padding length matter?*
   Coefficients convolve; pad both to $n\ge2001$, a power of two ($2048$), then
   $F^{-1}(\hat a\cdot\hat b)$ [S4 Ex. 1.56, 1.57]. With $n<L_1+L_2-1$ the DFT
   computes the *periodic* convolution and the tail wraps onto the head.
6. *Why is the trapezoidal rule the right quadrature for a smooth periodic
   integrand, and what does that have to do with this chapter?*
   The composite trapezoidal rule on $n$ uniform points **is** the $0$-th DFT
   coefficient of the samples; it integrates every $e^{ijx}$ with $j\not\equiv0$
   exactly, so it is exact on trigonometric polynomials of degree $<n$ and
   converges exponentially for analytic periodic $f$ [S4 §2.5, Ex. 2.20]. See
   note [03](03-numerical-integration.md).

## Implementation

`src/py/fft.py`: `dft` ($O(n^2)$ reference), `fft_recursive` (decimation in
time), **`fft_dif`** (decimation in frequency, [S4 Alg. 3]), **`ifft_dif`**
([S4 Alg. 4]), `bit_reverse_permutation`, `fft_iterative`, `ifft`, `convolve`,
`fft_two_real`, `rfft`, `next_pow2`, **`trig_interp_coeffs`** / **`trig_interp_eval`**
([S4 (1.36)]), **`solve_circulant`** ([S4 Ex. 1.59]).

Tests `test_fft.py`: against `numpy.fft.fft/ifft/rfft`, `np.convolve`,
`scipy.signal.fftconvolve`; Parseval; a single-bin tone; DIF against DIT;
`trig_interp_eval` reproducing the data at the knots; the
$(1,2,3)*(4,5,6,7)=(4,13,28,34,32,21)$ example of [S4 Ex. 1.57]; a circulant
solve against `numpy.linalg.solve`; and the unitarity of
$V_n/\sqrt n$ [S4 Thm 1.45].

`src/cpp/fft.cpp`: in-place iterative radix-2 on `std::complex<double>`,
inverse, convolution, checks against the $O(n^2)$ DFT.
