# 08: Ring/module-LWE, ML-KEM and ML-DSA, and the quantum threat

*TISS heading 5, second half ("quantum-secure public-key schemes") [S2].
Peikert [S6] sec. 4.4 (ring-LWE, module generalisation), 5.2.4, 5.6.2;
FIPS 203 ML-KEM [S16] sec. 3-8; FIPS 204 ML-DSA [S17] sec. 3-4 and Alg. 7;
the Kyber and Dilithium papers [S39, S40]; Fujisaki-Okamoto analysis [S41];
Shor [S34], Proos-Zalka [S35], Boneh-Shoup sec. 16.5 [S4]. Code:
[`../src/py/lwe_toy.py`](../src/py/lwe_toy.py) (Kyber-shaped toy KEM).*

## Why structure

Plain LWE needs a public matrix $A\in\mathbb Z_q^{m\times n}$: $\tilde O(n^2)$
bits [S6 sec. 5.2.1]. Replacing $\mathbb Z_q$ by the ring
$$R_q=\mathbb Z_q[X]/(X^N+1),\qquad N\text{ a power of 2},$$
makes one ring element stand for an $N\times N$ **negacyclic** block
($X\cdot$ shifts coefficients and negates the one that wraps around), so
keys shrink by a factor $N$.

**Ring-LWE [S6 sec. 4.4].** Samples $(a,\ a\cdot s+e)\in R_q^2$ with $a$
uniform, $s,e$ short. Hardness: at least as hard as quantumly solving
SVP$_\gamma$ on **ideal lattices** in $R$ in the worst case,
$\gamma=\mathrm{poly}(n)/\alpha$ [S6 Thm 4.4.3].

**Module-LWE.** Secret $\mathbf s\in R_q^k$, samples
$(\mathbf a,\langle\mathbf a,\mathbf s\rangle+e)\in R_q^k\times R_q$; $k=1$ is
ring-LWE, $N=1$ is plain LWE. Hardness from worst-case problems on module
lattices [S6 sec. 4.4.3]. Both NIST standards use it with $N=256$ and tune
security by $k$ alone [S16 sec. 3.2], [S17 sec. 3.2].

**Arithmetic.** $q=3329=2^8\cdot13+1$ for ML-KEM [S16 sec. 2.3], and
$q=8380417=2^{23}-2^{13}+1$ for ML-DSA [S17]: both have the roots of unity
needed for the number-theoretic transform (NTT), an FFT over $\mathbb Z_q$
that makes multiplication in $R_q$ quasi-linear. The toy code uses schoolbook
negacyclic convolution.

## ML-KEM (Kyber) [S16], [S39]

**K-PKE** (FIPS 203 sec. 5, ignoring encodings; $\chi_\eta$ the centred
binomial distribution, sum of $\eta$ coin flips minus $\eta$ coin flips):

- **KeyGen:** $A\in R_q^{k\times k}$ expanded from a seed $\rho$;
  $\mathbf s,\mathbf e\gets\chi_{\eta_1}^k$; $\mathbf t=A\mathbf s+\mathbf e$.
  $ek=(\mathbf t,\rho)$, $dk=\mathbf s$.
- **Encrypt**$(m\in\{0,1\}^{256};\ r)$: from coins $r$, $\mathbf y\gets
  \chi_{\eta_1}^k$, $\mathbf e_1\gets\chi_{\eta_2}^k$, $e_2\gets\chi_{\eta_2}$;
  $$\mathbf u=A^{\!\top}\mathbf y+\mathbf e_1,\qquad v=\mathbf t^{\!\top}\mathbf y+e_2+\lceil q/2\rfloor m;$$
  output $c=(\mathrm{Compress}_{d_u}(\mathbf u),\mathrm{Compress}_{d_v}(v))$.
- **Decrypt:** $w=v'-\mathbf s^{\!\top}\mathbf u'$, $m=\mathrm{Compress}_1(w)$.

*Correctness.* $w=\mathbf e^{\!\top}\mathbf y-\mathbf s^{\!\top}\mathbf e_1+e_2+\lceil q/2\rfloor m
+(\text{compression errors})$: every term except the message is a product or
sum of short polynomials. Decryption is right whenever each coefficient of the
noise is below $q/4$; FIPS 203 bounds the failure probability
(Table 1 below).

*CPA security.* Two MLWE hops: $(A,\mathbf t)$ is pseudorandom; then
$(\mathbf u,v)$ is an MLWE sample under secret $\mathbf y$ plus a message
offset. Same shape as Regev and as ElGamal (note 07; intro note 10).

**Compression [S16 eq. (4.7)-(4.8)].**
$\mathrm{Compress}_d(x)=\lceil(2^d/q)x\rfloor\bmod2^d$,
$\mathrm{Decompress}_d(y)=\lceil(q/2^d)y\rfloor$. Decompress-then-compress is
the identity [S16 sec. 4.2.1]; compress-then-decompress moves $x$ by at most
$\lceil q/2^{d+1}\rfloor$ (checked for all $x$ and $d$ by
`test_compress_decompress_fips203_properties`). Dropping low bits is extra
noise that the parameters absorb, and it halves ciphertexts.

**The FO transform with implicit rejection** [S16 Alg. 17-18], [S41]:
$$\mathsf{Encaps}(ek):\ m\gets\{0,1\}^{256},\ (K,r)=G(m\,\|\,H(ek)),\ c=\mathrm{Enc}(ek,m;r).$$
$$\mathsf{Decaps}(dk,c):\ m'=\mathrm{Dec}(c),\ (K',r')=G(m'\|h),\
c'=\mathrm{Enc}(ek,m';r');\ \text{return }K'\text{ if }c'=c\text{ else }J(z\,\|\,c).$$
Re-encryption with derandomised coins makes every accepted ciphertext
honestly generated, so a decapsulation oracle is useless: IND-CPA of K-PKE
becomes IND-CCA2 of the KEM in the (quantum) ROM [S41]. On failure a
pseudorandom key $J(z\|c)$ is returned, never an error, so the rejection is
invisible.

| [S16 Tables 1-3] | $k$ | $\eta_1$ | $\eta_2$ | $d_u$ | $d_v$ | $|ek|$ | $|c|$ | decaps failure | category |
|---|---|---|---|---|---|---|---|---|---|
| ML-KEM-512 | 2 | 3 | 2 | 10 | 4 | 800 B | 768 B | $2^{-138.8}$ | 1 |
| ML-KEM-768 | 3 | 2 | 2 | 10 | 4 | 1184 B | 1088 B | $2^{-164.8}$ | 3 |
| ML-KEM-1024 | 4 | 2 | 2 | 11 | 5 | 1568 B | 1568 B | $2^{-174.8}$ | 5 |

$N=256$, $q=3329$ throughout; shared key 32 bytes. NIST recommends ML-KEM-768
as the default [S16 sec. 8]. Categories are defined relative to breaking a
block cipher or hash of a given size in any realistic model of computation,
not as "bits of security" [S16 sec. 8].

## ML-DSA (Dilithium) [S17], [S40]

"A Schnorr-like signature" [S17 sec. 3.3]. Public $A\in R_q^{k\times\ell}$,
secret short $(\mathbf s_1,\mathbf s_2)$, $\mathbf t=A\mathbf s_1+\mathbf
s_2$ (only the high bits $\mathbf t_1$ are published, $d=13$ bits dropped).

- **Commit:** short $\mathbf y$ (coefficients below $\gamma_1$),
  $\mathbf w=A\mathbf y$, $\mathbf w_1=\mathrm{HighBits}(\mathbf w)$.
- **Challenge:** $c=\mathrm{SampleInBall}(H(\mu\|\mathbf w_1))$, a polynomial
  with $\tau$ coefficients $\pm1$, rest 0.
- **Response:** $\mathbf z=\mathbf y+c\,\mathbf s_1$.
- **Abort** and restart if $\|\mathbf z\|_\infty\ge\gamma_1-\beta$ or
  $\|\mathrm{LowBits}(\mathbf w-c\mathbf s_2)\|_\infty\ge\gamma_2-\beta$,
  $\beta=\tau\eta$ [S17 Alg. 7, line 23].
- **Verify:** recompute $\mathbf w_1$ from $A\mathbf z-c\,\mathbf t_1 2^d$
  with a hint $\mathbf h$, check the hash and $\|\mathbf z\|_\infty<\gamma_1-\beta$.

*Why abort ("Fiat-Shamir with aborts").* Without it $\mathbf z=\mathbf y+c\mathbf s_1$
is biased in the direction of $\mathbf s_1$ and signatures leak the key
[S17 sec. 3.3]. Rejection makes the distribution of $\mathbf z$ independent of
$\mathbf s_1$: the lattice analogue of HVZK (note 03). Security:
SUF-CMA from MLWE and SelfTargetMSIS [S17 sec. 3.1-3.2].

| [S17 Tables 1-2] | $(k,\ell)$ | $\eta$ | $\tau$ | $\gamma_1$ | $\gamma_2$ | exp. repetitions | $|pk|$ | $|\sigma|$ | category |
|---|---|---|---|---|---|---|---|---|---|
| ML-DSA-44 | (4,4) | 2 | 39 | $2^{17}$ | $(q-1)/88$ | 4.25 | 1312 B | 2420 B | 2 |
| ML-DSA-65 | (6,5) | 4 | 49 | $2^{19}$ | $(q-1)/32$ | 5.1 | 1952 B | 3309 B | 3 |
| ML-DSA-87 | (8,7) | 2 | 60 | $2^{19}$ | $(q-1)/32$ | 3.85 | 2592 B | 4627 B | 5 |

Compare: an Ed25519 signature is 64 bytes and its public key 32 [S23].

## The quantum threat

**Shor [S34], [S4 sec. 16.5].** A quantum computer finds the period of a
function in time polynomial in the logarithm of the period. Factoring reduces
to the period of $x\mapsto g^x\bmod N$; discrete log in **any** group to the
periods of $(a,b)\mapsto g^ah^b$. So RSA, finite-field DH and ECDLP all fall;
for elliptic curves the circuit was worked out by Proos and Zalka [S35]. What
makes it work: an efficiently computable function on an **abelian** group
whose hidden period/subgroup encodes the secret.

**LWE:** no comparable structure is known to be exploitable; the best known
quantum algorithms for GapSVP/SIVP offer only generic speed-ups over classical
ones [S6 sec. 4.2.2]. Hence "post-quantum" is a statement about known
algorithms, not a proof. Generic quantum search (Grover) square-roots
brute-force costs, which is why NIST's categories are pegged to AES and SHA
key-search/collision costs [S16 sec. 8]; SP 800-57 states that its strength
table will change once quantum computing is practical [S36].

## Worked example

- $\mathrm{Compress}_4(1000)=\lceil16000/3329\rfloor=\lceil4.81\rfloor=5$;
  $\mathrm{Decompress}_4(5)=\lceil16645/16\rfloor=1040$: error 40, below
  $\lceil3329/32\rfloor=104$.
- $\mathrm{Compress}_1$ maps $[833,2496]$ to 1 and the rest to 0;
  $\mathrm{Decompress}_1(1)=1665$. A message bit survives any noise of
  absolute value below $q/4\approx832$.
- Negacyclic product in $\mathbb Z_{17}[X]/(X^4+1)$:
  $(1+2X+3X^3)(2+X^2+X^3)$: plain product coefficients
  $(2,4,1,9,2,3,3)$; fold $X^4=-1$: $(2-2,\,4-3,\,1-3,\,9)=(0,1,15,9)$.
- Toy KEM ($N=16$, $k=2$, $\eta_1=3$, $\eta_2=2$, $d_u=10$, $d_v=4$,
  $q=3329$): keys agree in every test run; changing one ciphertext
  coefficient returns the implicit-rejection key.

## Pitfalls

- **Explicit rejection** (returning an error) or non-constant-time comparison
  of $c$ and $c'$ turns decapsulation into a plaintext-checking oracle.
- **Unchecked encapsulation keys:** FIPS 203 requires input checking of $ek$
  (the "modulus check": decoded coefficients must re-encode to the same bytes) [S16 sec. 7.2].
- **ML-DSA without the abort** leaks $\mathbf s_1$ statistically; aborts must
  not leak through timing of *which* check failed (**background**).
- **Parameters from asymptotics:** worst-case theorems (note 07) do not
  produce $k,\eta$; attack estimates do [S16 sec. 8].
- **"Quantum-safe" includes the symmetric parts:** hashes and XOFs inside
  ML-KEM/ML-DSA must also resist Grover-type speed-ups.

## Exam-style questions

1. *Show that multiplication by $X$ in $R_q$ is the negacyclic shift and
   write the $4\times4$ matrix of $a=1+2X+3X^3$ for $N=4$.* Columns
   $a,Xa,X^2a,X^3a$: $(1,2,0,3)$, $(-3,1,2,0)$, $(0,-3,1,2)$, $(-2,0,-3,1)$.
2. *Derive the ML-KEM decryption noise term.* $\mathbf e^{\!\top}\mathbf
   y-\mathbf s^{\!\top}\mathbf e_1+e_2$ plus compression errors of
   $\mathbf u$ (times $\mathbf s$) and of $v$.
3. *Why does FO need derandomised encryption and implicit rejection?* The
   decapsulator must recompute $c$ exactly to detect malformed ciphertexts;
   an explicit error would be an oracle.
4. *In ML-DSA, why is $\mathbf z$ rejected when $\|\mathbf z\|_\infty\ge
   \gamma_1-\beta$?* $\|c\mathbf s_1\|_\infty\le\tau\eta=\beta$; accepted
   $\mathbf z$ then lie in a box that every $\mathbf y+c\mathbf s_1$ covers
   uniformly, so $\mathbf z$ does not depend on $\mathbf s_1$.
5. *Why does Shor break ECDLP but no known quantum algorithm breaks LWE?*
   Abelian hidden-period structure vs none known for lattices; [S6] reports
   only generic quantum speed-ups.

## Code

`lwe_toy.py`: `compress`, `decompress`, `polymul` (negacyclic), `cbd`,
`pke_keygen/encrypt/decrypt` (K-PKE shape), `kem_keygen/encaps/decaps` (FO
with implicit rejection). Not ML-KEM: $N=16$, no NTT, no FIPS encodings,
no test vectors; `test_lwe_toy.py` checks correctness, the FIPS 203
compression properties and negacyclic multiplication against `sympy`.
