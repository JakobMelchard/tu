# 04 Information reconciliation and privacy amplification

Fourth TISS topic: "information reconciliation and privacy amplification (theorems and their applications)" [S2]. After sifting and parameter estimation Alice holds $X\in\{0,1\}^n$, Bob $Y$ with $\Pr[X_i\ne Y_i]\approx e$, Eve $E$. Reconciliation makes Bob's string equal to $X$ at a public cost of $\mathrm{leak_{EC}}+t$ bits; privacy amplification compresses $X$ to $\ell$ bits that are $\varepsilon$-close to uniform given everything Eve has. The key length formula at the end is the one every security proof fills in.

## Definitions

1. **One-way reconciliation.** Alice sends $C=\mathrm{synd}(X)\in\{0,1\}^r$; Bob computes $\hat X=\mathrm{corr}(Y,C)$. $\mathrm{leak_{EC}}=r$ [S5 §3.2].
2. **Verification.** Alice sends $H_{\rm ec}(X)$, $t$ bits, $H_{\rm ec}$ from a two-universal family; Bob aborts if $H_{\rm ec}(\hat X)\ne H_{\rm ec}(X)$. Then $\Pr[K_A\ne K_B\wedge\text{pass}]\le2^{-t}=\varepsilon_{\rm cor}$ [S5 Thm 2].
3. **Efficiency.** $f=\mathrm{leak_{EC}}/(n\,h(e))\ge1$; the Slepian-Wolf limit for a binary symmetric channel is $nh(e)$ [S3 §III.B; S9 Eq. (1)].
4. **BINARY.** Given a block with differing parity, Alice announces the parity of the first half; recurse into the half that differs. Finds one error with $\lceil\log_2k\rceil$ parities.
5. **Cascade** [S22]. Pass 1: blocks of size $k_1\approx0.73/e$, compare parities, BINARY on odd blocks. Pass $j$: random permutation, block size doubled. **Cascade step:** a bit corrected in pass $j$ flips the parity of the block containing it in every earlier pass, which was even; those blocks become odd and BINARY finds a second error there, and so on. Two-way and interactive.
6. **Syndrome codes.** Linear code with parity-check matrix $H\in\mathbb F_2^{r\times n}$: Alice sends $HX$; Bob looks for the most likely error pattern $\mathbf e$ with $H\mathbf e=HX\oplus HY$. Hamming(7,4): $r=3$ per 7 bits, corrects one error per block. **LDPC** codes: sparse $H$, decoded by belief propagation using $Y$ as side information; rate-adapted LDPC reaches $f\approx1.1$ [S39], the value used in [S5 Fig. 7].
7. **Two-universal family** [S4 Def. 5.4.1, S23]. $\mathcal F=\{f:\mathcal X\to\{0,1\}^\ell\}$ with $\Pr_f[f(x)=f(x')]\le2^{-\ell}$ for all $x\ne x'$.
8. **Toeplitz hashing.** Seed $s\in\{0,1\}^{n+\ell-1}$, $T_{ij}=s_{i-j+n-1}$ (constant diagonals), $f_s(x)=Tx\bmod2$. Seed length $n+\ell-1$ instead of $n\ell$ for a random matrix; $O(n\log n)$ by FFT.

## Results

**Proposition 4.1 (Toeplitz is two-universal).** For $z=x\oplus x'\ne0$, $Tz$ is uniform on $\{0,1\}^\ell$.

*Proof.* Let $j$ be the smallest index with $z_j=1$ and $d_i=i-j+n-1$. Row $i$ is $(Tz)_i=s_{d_i}\oplus\bigoplus_{k>j}z_ks_{i-k+n-1}$, so it involves seed bits of index $\le d_i$ only, and rows $<i$ involve indices $\le d_{i-1}<d_i$. Conditioned on all seed bits of index $<d_i$ (which fix rows $<i$ and the rest of row $i$), $(Tz)_i=s_{d_i}\oplus\text{const}$ is uniform. By the chain rule of probability $Tz$ is uniform, so $\Pr[Tz=0]=2^{-\ell}$. ∎ Checked by exhaustive enumeration of all seeds in `collision_probability`.

**Theorem 4.2 (leftover hash lemma)** [S4 Thm 5.5.1, Cor. 5.6.1; S12]. $\rho_{XE}$ cq, $F$ uniform from a two-universal family into $\{0,1\}^\ell$:
$$\tfrac12\bigl\|\rho_{F(X)FE}-\tau_\ell\otimes\rho_{FE}\bigr\|_1\le\varepsilon+\tfrac12\,2^{-\frac12(H^\varepsilon_{\min}(X|E)-\ell)}.$$
([S4] states it for the unhalved $L_1$ norm: $2\varepsilon+2^{-\frac12(H^\varepsilon_{\min}-\ell)}$.) The seed $F$ may be public.

*Proof sketch, classical $E$, $\varepsilon=0$.* For a distribution $P$ on $2^\ell$ values, Cauchy-Schwarz gives $\|P-U\|_1\le\sqrt{2^\ell\|P-U\|_2^2}=\sqrt{2^\ell\,\mathrm{Coll}(P)-1}$, $\mathrm{Coll}(P)=\sum_zP(z)^2$. Two-universality: $\mathbb E_f\,\mathrm{Coll}(P_{f(X)})=\Pr[f(X)=f(X')]\le\mathrm{Coll}(P_X)+2^{-\ell}$ ($X'$ an independent copy). Jensen:
$$\mathbb E_f\|P_{f(X)}-U\|_1\le\sqrt{2^\ell\,\mathrm{Coll}(P_X)}\le\sqrt{2^{\ell-H_{\min}(X)}},$$
using $\mathrm{Coll}(P)\le\max_xP(x)$. Condition on $E=e$ and average with Jensen once more; $\sum_eP(e)2^{-H_{\min}(X|E=e)}=2^{-H_{\min}(X|E)}$ gives the conditional version. The quantum case replaces $\|\cdot\|_2$ by a weighted Hilbert-Schmidt norm relative to $\sigma_E$ [S4 Lemma 5.2.3, Thm 5.5.1]; smoothing adds $\varepsilon$ by the triangle inequality [S4 Cor. 5.6.1]. ∎

**Theorem 4.3 (composable key length).** Chain rule (note 03) for the public $r+t$ bits, then Thm 4.2 with target $\varepsilon_{\rm pa}$:
$$\boxed{\ell=\Bigl\lfloor H^\varepsilon_{\min}(X|E)-\mathrm{leak_{EC}}-t-2\log_2\frac1{2\varepsilon_{\rm pa}}\Bigr\rfloor}$$
Total security $\varepsilon_{\rm cor}+\varepsilon_{\rm sec}$ with $\varepsilon_{\rm cor}=2^{-t}$. Filling in $H^\varepsilon_{\min}(X|E)\ge n(1-h(\delta+\nu))$ from the uncertainty relation and the sampling bound gives exactly [S5 Eq. (58)] (note 05).

**Proposition 4.4 (you cannot extract more than $H_{\min}$).** If $X$ takes at most $2^k$ values and $\ell>k$, the output has support $\le2^k$ and $\frac12\|P_{f(X)}-U\|_1\ge1-2^{k-\ell}$ for every $f$.

**Reconciliation in a one-way proof.** Cascade is two-way; to use it in a one-way framework give Eve the error positions (count all parities of both sides) or encrypt the EC messages [S3 §III.B]. Bob also learns the exact number of errors during EC, which can replace a separate estimate [S3 §III.B].

## Worked example

**Cascade toy** (`reconciliation.demo`, $n=2\times10^4$, 4 passes):

| $e$ | errors | left | leaked parities | $nh(e)$ | $f$ |
|---|---|---|---|---|---|
| 0.01 | 212 | 0 | 1886 | 1616 | 1.17 |
| 0.02 | 382 | 0 | 3108 | 2829 | 1.10 |
| 0.05 | 982 | 0 | 6658 | 5728 | 1.16 |
| 0.08 | 1530 | 0 | 9449 | 8044 | 1.18 |

Block sizes $k_1=0.73/e$: 36 at 2 %, 14 at 5 %. Hamming(7,4) at 1 % on 7000 bits: 76 errors down to 15 (blocks with two errors fail) while leaking 3000 bits $\gg nh(e)=566$. Fixed short codes are wasteful at low QBER.

**Leftover hash lemma, exact** (`privacy_amplification.demo`: $X$ uniform on $2^8$ of the $2^{12}$ strings, 300 random Toeplitz seeds):

| $\ell$ | exact $\mathbb E_f$ distance | bound $\frac12 2^{-(8-\ell)/2}$ |
|---|---|---|
| 2 | 0.042 | 0.063 |
| 4 | 0.094 | 0.125 |
| 6 | 0.187 | 0.250 |
| 8 | 0.367 | 0.500 |
| 10 | 0.777 | $\ge1-2^{-2}=0.75$ by Prop. 4.4 |

Eve knowing 4 of 10 uniform bits, $\ell=3$: distance 0.039, bound $\frac122^{-(6-3)/2}=0.177$.

**Key length.** $n=10^6$, $e=2\%$, $H^\varepsilon_{\min}\ge n(1-h(0.025))=8.31\times10^5$, $\mathrm{leak_{EC}}=1.16\,nh(0.02)=1.64\times10^5$, $t=37$, $\varepsilon_{\rm pa}=3\times10^{-11}$: $\ell=667\,163$ (`key_length`). Asymptotic $n(1-2h(0.02))=717\,119$. The security terms $t+2\log_2(1/(2\varepsilon_{\rm pa}))=37+68$ cost only 105 bits; the loss is in $\nu$ and $f$.

## Pitfalls

- $2\log(1/\varepsilon)$, not $\log(1/\varepsilon)$: halving $\varepsilon$ costs 2 bits. And with the trace-distance ($\frac12\|\cdot\|_1$) convention there is an extra $+2$ from the $\frac12$ in front.
- The hash seed can be public but must be independent of $X$ and chosen *after* Eve's attack on the quantum states.
- Leakage counts every public bit correlated with $X$: syndrome, verification hash, Cascade parities of both parties (or error positions).
- Shannon entropy is the wrong quantity for PA: $H(X|E)$ large with $H_{\min}(X|E)$ small (one likely value) gives no key. Only the i.i.d. limit (AEP) turns $H_{\min}$ into $H$.
- The verification hash protects correctness, not secrecy; it costs $t$ bits of entropy (it is in Thm 4.3).
- Cascade's $f$ depends on $e$ and on the block schedule; quote the $f$ you actually achieve, not the Shannon limit.

## Questions

1. *Why is the leakage at least $nh(e)$?* Bob needs $H(X|Y)=nh(e)$ bits of information to recover $X$ (Slepian-Wolf converse); any one-way message that lets him decode must carry that much.
2. *Prove that the Toeplitz family is two-universal.* Prop. 4.1: triangular structure, each row introduces a fresh uniform seed bit.
3. *State the leftover hash lemma and sketch the proof.* Thm 4.2: collision probability plus two-universality plus Cauchy-Schwarz and Jensen.
4. *Derive the key length formula from LHL and the chain rule.* Thm 4.3: $H^\varepsilon_{\min}(X|EC)\ge H^\varepsilon_{\min}(X|E)-r-t$; set $\frac12 2^{-(H-r-t-\ell)/2}=\varepsilon_{\rm pa}$ and solve for $\ell$.
5. *With $n=10^5$, $e=3\%$, $f=1.2$, $t=40$, $\varepsilon_{\rm pa}=10^{-10}$ and $H^\varepsilon_{\min}=n(1-h(0.04))$, how long is the key?* $h(0.04)=0.24229$, $h(0.03)=0.19439$: $75\,770.8-23\,327.0-40-2\log_2(5\times10^9)=75\,770.8-23\,327.0-40-64.4$, floor $=52\,339$ bits (`key_length`).

## Code

`src/py/reconciliation.py`: `binary`, `cascade(a, b, e_est, rng, passes, k1)`, `hamming_reconcile`, `verify_hash`, `shannon_leak`, `efficiency`, `bsc`. `src/py/privacy_amplification.py`: `toeplitz`, `toeplitz_hash`, `collision_probability`, `lhl_bound`, `key_length`, `distance_flat_source`, `distance_with_prefix_leak`. Tests: `test_reconciliation.py`, `test_privacy_amplification.py` (exact two-universality, bound holds exactly, $\ell>H_{\min}$ fails).

## References

[S3 §III.B], [S4 §5.2-5.6], [S5 §3.2, Thm 2, Eq. (58)], [S12], [S22], [S23], [S39].
