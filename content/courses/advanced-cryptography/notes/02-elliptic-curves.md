# 02: Elliptic-curve cryptography

*TISS heading 2 [S2]. Boneh-Shoup ch. 15 (curves, Curve25519, pairings) and
sec. 16.1-16.3 (DL attacks, generic bound) [S4]; Hankerson-Menezes-Vanstone
[S20] (not free, cite only); Galbraith ch. 9 [S37]; curve parameters SEC 2
[S21]; X25519 RFC 7748 [S22]; Ed25519 RFC 8032 [S23]; strength table
SP 800-57 [S36]. Prerequisite: intro notes
[09](../../introduction-to-cryptography/notes/09-number-theory.md)
(cyclic groups, DL/CDH/DDH, the NIST table) and
[11](../../introduction-to-cryptography/notes/11-digital-signatures.md)
(DSA, Schnorr). Code: [`../src/py/ec_toy.py`](../src/py/ec_toy.py).*

Everything built on a prime-order group $\mathbb G$ in the prerequisite (DH,
ElGamal, Schnorr, DSA) works verbatim in an elliptic-curve group. The point of
this note is *why* that group: square-root-hard DL at 256 bits.

## Definitions

**Definition [S4 Def. 15.1].** For a prime $p>3$ an elliptic curve over
$\mathbb F_p$ is $E: y^2 = x^3+ax+b$ with $4a^3+27b^2\ne0$ (no repeated root).
$E(\mathbb F_p)$ is the set of solutions plus the point at infinity
$\mathcal O$.

**Group law [S4 sec. 15.2].** $\mathcal O$ is neutral, $-(x,y)=(x,-y)$. For
$P=(x_1,y_1)$, $Q=(x_2,y_2)$, $P\ne -Q$:
$$\lambda=\begin{cases}\dfrac{y_2-y_1}{x_2-x_1} & P\ne Q\ \text{(chord)}\\[2mm]
\dfrac{3x_1^2+a}{2y_1} & P=Q\ \text{(tangent)}\end{cases}\qquad
x_3=\lambda^2-x_1-x_2,\quad y_3=\lambda(x_1-x_3)-y_1 .$$
Geometric content: $P$, $Q$, $-(P+Q)$ are the three intersections of a line
with the cubic. Commutativity is visible; associativity is a theorem (proof
via the Picard group or by computer algebra; `test_group_axioms_on_toy_curve`
checks it numerically).

**Hasse [S4 sec. 15.2], [S37 Thm 9.10.7].** $\#E(\mathbb F_p)=p+1-t$ with
$|t|\le2\sqrt p$. Point counting is polynomial time (Schoof, SEA) [S4 Rem. 15.1].
Every point order divides $n_E=\#E(\mathbb F_p)$ (Lagrange); one works in a
subgroup of prime order $n$, $n_E = h\,n$ with **cofactor** $h$.

**Scalar multiplication.** $kP$ by double-and-add in $\le 2\log_2 k$ group
operations. The branch on each bit of $k$ leaks $k$ through timing; the
**Montgomery ladder** keeps $(R_0,R_1)$ with invariant $R_1-R_0=P$ and does
one addition and one doubling per bit whatever the bit is:
$$b_i=0:\ (R_0,R_1)\gets(2R_0,\,R_0+R_1),\qquad
b_i=1:\ (R_0,R_1)\gets(R_0+R_1,\,2R_1).$$
*Correctness.* If $R_0 = mP$, $R_1=(m+1)P$ then after the step $R_0=(2m+b_i)P$
and $R_1 = R_0+P$. Induction over the bits. $\square$

## Hardness: the ECDLP

Given $P$ of prime order $n$ and $Q=\alpha P$, find $\alpha$. Generic
algorithms (baby-step giant-step, Pollard rho) need $O(\sqrt n)$ operations,
and in the generic group model no algorithm does better: success
$\le((3T+2)^2/2+1)/n$ after $T$ queries [S4 Thm 16.3]. For well-chosen curves
nothing better than generic is known [S4 sec. 15.3]. Known weak classes
[S4 sec. 15.3]:

- **Smooth order.** Pohlig-Hellman reduces DL to the largest prime factor;
  require $n_E\in\{n, 4n, 8n\}$ with $n$ prime.
- **Anomalous curves** ($n_E=p$): DL in polynomial time.
- **Small embedding degree** $\tau$ ($n\mid p^\tau-1$): a pairing moves DL into
  $\mathbb F_{p^\tau}^*$ where index calculus works (MOV).

Hence the key-size asymmetry of the NIST table [S36 Table 2]:

| security (bits) | symmetric | RSA / finite-field DH | EC group order |
|---|---|---|---|
| 128 | AES-128 | 3072 | 256-383 |
| 192 | AES-192 | 7680 | 384-511 |
| 256 | AES-256 | 15360 | 512+ |

## Named curves and models

- **secp256r1 (P-256)** $y^2=x^3-3x+b$, prime order, $b$ derived from an
  unexplained seed; **secp256k1** $y^2=x^3+7$ over
  $p=2^{256}-2^{32}-977$, prime order, no unexplained constant [S4 sec.
  15.3.1], [S21 sec. 2.4.1]. `test_secp256k1_...` checks $nG=\mathcal O$ and
  agreement with the `cryptography` package.
- **Montgomery form** $Bv^2=u^3+Au^2+u$: $\#E$ divisible by 4, and $x$-only
  arithmetic suffices for the ladder [S4 sec. 15.2.1].
- **Curve25519** $v^2=u^3+486662u^2+u$ over $p=2^{255}-19$, order $8\ell$,
  $\ell = 2^{252}+\texttt{0x14def9de...5cf5d3ed}$, base point $u=9$
  [S22 sec. 4.1]; designed for a fast ladder and **twist security**: points
  with $u\in\mathbb F_p$ off the curve lie on the twist, whose order is also
  nearly prime, so $x$-only code need not validate inputs [S4 sec. 15.3.2-3].
- **Twisted Edwards** $-x^2+y^2=1+dx^2y^2$ (edwards25519, birational to
  Curve25519 [S22]): one **complete** addition formula, no special cases
  [S4 sec. 15.2.1].

## Protocols

**ECDH.** $A=aG$, $B=bG$, key $abG$ (use a KDF on it). **X25519** [S22 sec.
5-6]: clamp the scalar to $2^{254}+8k$, $0\le k<2^{251}$. Multiple of 8: a
small-order component of the peer's point is killed (the product is $\mathcal O$,
hence the optional all-zero check). Top bit fixed: the ladder always runs 255
steps.

**ECDSA** [S4 sec. 19.3]. Key $d$, $Q=dG$, group order $n$.
$$r = x(kG)\bmod n,\qquad s = k^{-1}(H(m)+rd)\bmod n .$$
Verify: $w=s^{-1}$, $X=H(m)w\,G+rw\,Q$, accept iff $x(X)\equiv r$.
*Correctness:* $X = w(H(m)+rd)G = w\,s\,k\,G = kG$. **Nonce reuse:** two
signatures with the same $k$ share $r$, and
$s_1-s_2=k^{-1}(H(m_1)-H(m_2))$ gives $k$, then $d=(s_1k-H(m_1))/r$
(`ecdsa_nonce_reuse`).

**Schnorr / EdDSA.** $R=kG$, $e=H(R,P,m)$, $s=k+ed$; verify $sG=R+eP$
(the note-03 Sigma protocol plus Fiat-Shamir). **Ed25519** [S23 sec. 5.1]
derandomises: $r=H(\text{prefix}\,\|\,m)$ from the secret key's hash,
$S=r+H(R\|A\|m)\,a \bmod \ell$, and verifies cofactored,
$[8][S]B=[8]R+[8][k]A$. Deterministic nonces remove the nonce-reuse failure
mode; `test_ed25519_against_cryptography` checks byte-identical signatures.

## Pairings (one section)

A **pairing** is $e:\mathbb G_1\times\mathbb G_2\to\mathbb G_T$, all of prime
order $n$, with (i) bilinearity $e(aP,bQ)=e(P,Q)^{ab}$, (ii) non-degeneracy
$e(P,Q)\ne1$ for generators, (iii) efficient computability [S4 sec. 15.4].
Realised by Weil/Tate pairings on curves with small embedding degree
[S37 ch. 26]. Consequences:

- **DDH is easy** in $\mathbb G$ if $e:\mathbb G\times\mathbb G\to\mathbb G_T$
  exists: test $e(aP,bP)\stackrel?=e(P,cP)$. CDH may still be hard ("gap"
  groups).
- **MOV:** $e(P,\cdot)$ maps ECDL into $\mathbb G_T\subset\mathbb F_{p^\tau}^*$,
  so pairing curves need $p^\tau$ large enough for index calculus.
- **BLS signatures** [S4 sec. 15.5.1]: $\sigma=sk\cdot H(m)$, verify
  $e(\sigma,g_2)=e(H(m),pk)$ with $pk = sk\cdot g_2$; aggregation by adding
  signatures (with care, [S4 sec. 15.5.3]).
- **Groth16** verification is one pairing-product equation (note 04).

## Worked example

$E: y^2=x^3+2x+2$ over $\mathbb F_{17}$; $\#E=19$ (prime, inside Hasse's
$18\pm8.2$), $G=(5,1)$.

- $2G$: $\lambda=(3\cdot25+2)/(2\cdot1)=77\cdot2^{-1}=9\cdot9=13$;
  $x_3=169-10\equiv6$, $y_3=13(5-6)-1\equiv3$. So $2G=(6,3)$.
- Multiples: $3G=(10,6)$, $7G=(0,6)$, $10G=(7,11)$, $11G=(13,10)$, $18G=(5,16)=-G$, $19G=\mathcal O$.
- **ECDH** $a=3$, $b=10$: $A=(10,6)$, $B=(7,11)$, shared $30G=11G=(13,10)$.
- **Schnorr** $d=3$, $k=7$, pretend $e=11$: $R=(0,6)$,
  $s=7+33\equiv2 \pmod{19}$; check $2G=(6,3)$ and $R+eP=7G+33G=40G=2G$. ✓

(Reproduce with `Curve(17, 2, 2)`; the module's own toy curve is
$y^2=x^3+x+14$ over $\mathbb F_{1009}$, prime order 1013.)

## Pitfalls

- **Invalid-curve points.** Weierstrass formulas never use $b$; an attacker's
  point on another curve (with smooth order) passes through the arithmetic.
  Check $P\in E$ and $nP=\mathcal O$ unless the design is twist-secure.
- **Cofactor.** On Curve25519/edwards25519 multiply by 8 or clamp; otherwise
  small-subgroup components leak bits of the key.
- **Nonces.** Reused, biased or leaked ECDSA nonces reveal $d$ (reuse: one
  line; bias: lattice attacks). Use RFC 6979 or EdDSA-style derivation.
- **Timing.** Double-and-add and affine inversions are not constant time.
  So is everything in `ec_toy.py`.
- **"256-bit curve = 256-bit security"** is wrong: generic DL costs
  $\sqrt n$, so 128 bits [S36].

## Exam-style questions

1. *Compute $2P$ for $P=(3,1)$ on $y^2=x^3+2x+2$ over $\mathbb F_{17}$.*
   $P=4G$; $\lambda=(27+2)/2=29\cdot9\equiv 12\cdot 9 = 108\equiv6$;
   $x_3=36-6=30\equiv13$, $y_3=6(3-13)-1=-61\equiv7$: $2P=(13,7)=8G$. ✓
2. *Why must $n_E$ have a large prime factor, and why is prime order not
   enough (name a second condition)?* Pohlig-Hellman; also embedding degree
   large (MOV) and $n_E\ne p$ (anomalous).
3. *Prove correctness of ECDSA verification and derive the key from two
   signatures with the same nonce.* See above.
4. *Why does X25519 clamp scalars to a multiple of 8, and why is the top bit
   fixed?* Cofactor 8: kills small-order components; fixed bit length makes
   the ladder's step count independent of the key.
5. *Given a symmetric pairing on $\mathbb G$, show DDH is easy but argue why
   BLS signatures can still be secure.* Test $e(aP,bP)=e(P,cP)$. BLS forgery
   means computing $sk\cdot H(m)$ from $pk=sk\cdot g$ and $H(m)$: a CDH
   instance, which the pairing does not solve.

## Code

`ec_toy.py`: `Curve.add/mul/ladder/points/order`, `keygen`, `ecdh`,
`schnorr_sign/verify`, `ecdsa_sign/verify`, `ecdsa_nonce_reuse`, secp256k1
constants, `x25519` (RFC 7748 sec. 5), `ed25519_public/sign/verify`
(RFC 8032 sec. 5.1). Tests reproduce RFC 7748 sec. 5.2/6.1 and RFC 8032
sec. 7.1 vectors, read from the vendored RFCs, and cross-check with
`cryptography` (X25519, Ed25519, SECP256K1).
