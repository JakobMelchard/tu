# 09 — Number theory for cryptography

*Lectures 10 and 11 [S8]. Katz-Lindell sec. 9.1.2 (modular arithmetic), 9.1.3
(groups), and sec. 10-11 at the level of quoted running times [S10]. Key-length
guidance is NIST SP 800-57 Part 1 Rev. 5 [S27]. Code:
[`../src/py/numtheory.py`](../src/py/numtheory.py).*

Public-key cryptography rests on algebra in finite groups and on problems
believed hard there. This note is the toolbox: the group theory you need, the
algorithms (all in `numtheory.py`), and the hardness assumptions (DLP, CDH, DDH,
RSA/factoring) that notes 10-11 build on. A physicist can read the group theory
fast; the payoff is knowing *exactly which* problem each scheme reduces to.

## Groups and $\mathbb{Z}_N^*$

A **group** $(G,\cdot)$: closed associative operation, identity, inverses. Finite
abelian groups are all we use. Two families:

- $(\mathbb{Z}_N, +)$: integers mod $N$ under addition, order $N$.
- $(\mathbb{Z}_N^*, \cdot)$: integers in $[1,N)$ **coprime to $N$**, under
  multiplication mod $N$. Its order is $\varphi(N)$ (Euler's totient).

$a$ is invertible mod $N$ iff $\gcd(a,N)=1$; the inverse comes from the extended
Euclidean algorithm, since $ax+Ny=1 \Rightarrow ax\equiv 1$. Code: `egcd`,
`modinv`.

**Euler's totient:** $\varphi(N)=N\prod_{p\mid N}(1-\tfrac1p)$. For primes
$\varphi(p)=p-1$; for $N=pq$ (RSA), $\varphi(N)=(p-1)(q-1)$. Code: `euler_phi`,
`factorize`.

## Fermat, Euler, and fast exponentiation

**Euler's theorem:** if $\gcd(a,N)=1$ then $a^{\varphi(N)}\equiv 1\pmod N$.
**Fermat (special case):** $a^{p-1}\equiv 1\pmod p$ for prime $p\nmid a$.
Consequences: exponents live mod $\varphi(N)$ (this is why RSA sets
$d=e^{-1}\bmod\varphi(N)$), and $a^{-1}\equiv a^{\varphi(N)-1}$.

Modular exponentiation by **square-and-multiply** costs $O(\log e)$
multiplications — the reason public-key crypto is feasible at all. Code:
`modexp` (handles negative exponents via `modinv`).

## Chinese Remainder Theorem

For pairwise coprime $m_1,\dots,m_k$ with product $M$,
$$\mathbb{Z}_M \cong \mathbb{Z}_{m_1}\times\cdots\times\mathbb{Z}_{m_k},$$
an isomorphism of rings: computing mod $M$ = computing in each coordinate
independently. Uses: **fast RSA decryption** (work mod $p$ and mod $q$, then
recombine — $\approx 4\times$ faster, `rsa.decrypt_crt`); Hastad's broadcast
attack (note 10); reconstructing a value from residues. Code: `crt`.

## Cyclic groups, generators, discrete log

$G$ is **cyclic** if some $g$ (a **generator**) has $\{g^0,g^1,\dots,g^{|G|-1}\}=G$;
then the **order** of $g$ is $|G|$. Facts:
- $\mathbb{Z}_p^*$ is cyclic of order $p-1$ for prime $p$ (so generators, i.e.
  *primitive roots*, exist). Code: `find_generator`, `is_generator`, `order`.
- The order of any element divides the group order (Lagrange). $g$ is a generator
  of $\mathbb{Z}_p^*$ iff $g^{(p-1)/q}\ne 1$ for every prime $q\mid p-1$ — the
  test `is_generator` uses, needing only the factorisation of $p-1$.
- **Safe primes** $p=2q+1$ ($q$ prime): $\mathbb{Z}_p^*$ has a unique subgroup of
  large prime order $q$; working there gives clean, prime-order groups for
  DH/ElGamal/Schnorr (avoids small-subgroup attacks). Code: `gen_safe_prime`,
  `subgroup_generator`.

**Discrete logarithm problem (DLP):** given $g$ and $h=g^x$ in $G$, find $x$.

> **The group matters, not the notation.** DLP is *easy* in $(\mathbb Z_p,+)$
> [S12]: there "exponentiation" $x\mapsto x\cdot g$ is multiplication, so the
> logarithm is $x = h\cdot g^{-1} \bmod p$, one extended-Euclid call. Hardness is
> a property of the group, and the additive group of a field is the wrong one.

**(Named only — K&L sec. 10 is on the "what we did not cover" list [S8]; lecture
11 quotes the running times and moves on.)**

- **Baby-step giant-step (BSGS):** write $x=im+j$ with $m=\lceil\sqrt n\rceil$;
  tabulate baby steps $g^j$, then match giant steps $h\cdot g^{-im}$. Time and
  memory $O(\sqrt n)$. Code: `bsgs` (recovers a 17-bit log instantly in the demo).
- **Pollard's rho:** same $O(\sqrt n)$ time, $O(1)$ memory. For a prime-order
  group of $n$-bit order, $\approx 2^{n/2}$ [S8].
- **Pohlig-Hellman:** if $n=|G|$ has only small prime factors, solve DLP per
  prime-power factor via CRT — *cheap*. Hence the insistence on **prime-order**
  subgroups: $n=q$ prime makes Pohlig-Hellman useless and forces the full
  $O(\sqrt q)$ cost.
- **Number field sieve** in (subgroups of) $\mathbb Z_p^*$: sub-exponential,
  $2^{O(\ell^{1/3}(\log \ell)^{2/3})}$ for an $\ell$-bit $p$ [S8]. This is why
  $\mathbb Z_p^*$ needs a 3072-bit $p$ where an elliptic curve needs 256 bits:
  the curve has no sub-exponential attack, so only the generic $\approx 2^{n/2}$
  applies.

## Primality testing and prime generation

Key generation needs large random primes. **Miller-Rabin** (`miller_rabin`):
write $n-1=2^s d$ with $d$ odd; a random base $a$ is a *witness* to compositeness
unless $a^d\equiv 1$ or $a^{2^r d}\equiv -1$ for some $r<s$. A composite passes
one round with probability $\le 1/4$, so $t$ rounds give error $\le 4^{-t}$.
Cross-checked against `sympy.isprime` over thousands of $n$ including the
Carmichael numbers 561, 1105, 1729 (`test_numtheory.py::test_miller_rabin_vs_sympy`).
`gen_prime` samples odd candidates with the top bit set until one passes; by the
prime number theorem a random $b$-bit integer is prime with probability about
$1/\ln(2^b)$, an odd one with twice that, so about $\ln(2^b)/2\approx 0.35\,b$
tries on average (about 355 for $b=1024$).

## Hardness assumptions (the foundations of notes 10-11)

Fix a cyclic group $G=\langle g\rangle$ of prime order $q$.

- **Discrete Log (DLP):** given $g^x$, find $x$.
- **Computational Diffie-Hellman (CDH):** given $g^x, g^y$, compute $g^{xy}$.
- **Decisional Diffie-Hellman (DDH):** distinguish $(g^x,g^y,g^{xy})$ from
  $(g^x,g^y,g^z)$ with $z$ random.

**Relations, and get the direction right.** As *algorithms*, a DLP solver gives
a CDH solver (recover $x$ from $g^x$, then raise $g^y$ to it), and a CDH solver
gives a DDH distinguisher (compute $g^{xy}$ and compare). So

$$\text{DLP easy} \Rightarrow \text{CDH easy} \Rightarrow \text{DDH easy},$$

and contrapositively, as *assumptions*,

$$\boxed{\text{DDH hard} \Rightarrow \text{CDH hard} \Rightarrow \text{DLP hard}.}$$

DDH is therefore the **strongest** assumption of the three and DLP the weakest.
The 2024W final asks exactly this: *"if CDH holds in $\mathbb G$, then the
discrete logarithm assumption holds in $\mathbb G$"* — **true** [S16].

The implications are strict in at least one direction: DDH is **false** in
$\mathbb{Z}_p^*$ itself, because the Legendre symbol is computable and leaks
whether $g^{xy}$ is a square, while CDH there is still believed hard. That is
why we work in the prime-order subgroup, where DDH is believed to hold.

- **RSA assumption:** given $(N,e)$ and $y=x^e\bmod N$ with $N=pq$, find $x$.
  It **implies** the hardness of **factoring** $N$ (a factoring algorithm gives
  $\varphi(N)$, hence $d$, hence $x$), so RSA hard $\Rightarrow$ factoring hard;
  the converse is not known, so the RSA assumption is the stronger one.
- **Factoring:** given $N=pq$, find $p,q$. Best classical: General Number Field
  Sieve, sub-exponential $\exp(O((\log N)^{1/3}(\log\log N)^{2/3}))$. Lecture 11
  makes the point with the **factorisation records** [S8]: 330 bits in 1991, 512
  in 1999, 768 in 2009, 795 in 2019, 829 in 2020. The curve is shallow, which is
  what lets us pick a modulus size and expect it to last.

## Choosing parameters: the NIST table

Symmetric parameters are read off directly — an $n$-bit block-cipher key gives
$\approx 2^n$ security, an $n$-bit hash $\approx 2^{n/2}$ collision security.
Public-key parameters are not, because the attacks are sub-exponential. The
comparison NIST publishes, quoted slide-for-slide in lecture 11 [S8, S27]:

| security strength | symmetric | FFC: DSA, DH ($L$ = $p$, $N$ = order) | IFC: RSA ($k$ = $\lvert N\rvert$) | ECC ($f$ = order) |
|---|---|---|---|---|
| 112 | 3TDEA | 2048 / 224 | 2048 | 224-255 |
| **128** | **AES-128** | **3072 / 256** | **3072** | **256-383** |
| 192 | AES-192 | 7680 / 384 | 7680 | 384-511 |
| 256 | AES-256 | 15360 / 512 | 15360 | 512+ |

Two exam items live in this table. *"NIST recommends longer keys for private-key
than for public-key schemes"* — **false**, spectacularly so: 128 bits against
3072 [S12]. *"For the same security level, the RSA modulus should be longer than
the order of an elliptic-curve group"* — **true**, 3072 against 256 [S16].

The reason for the two public-key columns differing is the previous section: the
number field sieve attacks $\mathbb Z_p^*$ and factoring sub-exponentially, and
nothing sub-exponential is known for a well-chosen curve.

**Quantum caveat (background).** Shor's algorithm solves DLP and factoring in
polynomial time on a large quantum computer, which breaks every assumption in
this section — but not AES or SHA-2, which lose at most a square root to Grover.
That asymmetry is why post-quantum cryptography is about replacing the
*public-key* layer. Lecture 13a lists post-quantum cryptography as a master-course
topic, explicitly not covered here [S8]; it is in these notes because the course
is on the QIST list, not because it is examinable.

## Elliptic curves (idea)

Points on $y^2=x^3+ax+b$ over a finite field, plus a point at infinity, form an
abelian group under the "chord-and-tangent" addition law. The DLP there (**ECDLP**)
has *no known sub-exponential* attack, so a $\approx 256$-bit curve matches the
security of a $\approx 3072$-bit $\mathbb{Z}_p^*$ — smaller keys, faster ops. DH,
ElGamal, and DSA all transplant to EC groups (ECDH, ECDSA, note 11). We treat EC
as "a group where DLP is especially hard"; the group law itself is not examined
in code here.

## Worked example

*Find the order of $2$ in $\mathbb{Z}_{23}^*$ and decide if $2$ is a generator.*
$|\mathbb{Z}_{23}^*|=22=2\cdot 11$. Divisors: $1,2,11,22$. Compute
$2^{11}\bmod 23$: $2^{11}=2048=23\cdot 89+1$, so $2^{11}\equiv 1$. Thus the order
divides $11$; it is not $1$, so $\mathrm{ord}(2)=11\ne 22$ — **not** a generator.
Meanwhile $5^{11}\equiv -1$ and $5^2=25\equiv 2\ne1$, so $\mathrm{ord}(5)=22$: $5$
*is* a generator. Matches `numtheory.order(2,23)=11`, `find_generator(23)=5`,
and `sympy.primitive_root(23)=5`.

## Pitfalls

- **Compute mod the group order for exponents, mod $N$ for the base.** Exponents
  live mod $\varphi(N)$ (or $q$), not mod $N$.
- **Inverses need coprimality** — `modinv` raises otherwise; RSA keygen must check
  $\gcd(e,\varphi(N))=1$.
- **Use prime-order subgroups** (safe primes). Composite, smooth order $\Rightarrow$
  Pohlig-Hellman/small-subgroup attacks.
- **DDH fails in $\mathbb{Z}_p^*$** (quadratic-residue bit leaks); restrict to the
  order-$q$ subgroup.
- **Miller-Rabin is probabilistic** — use enough rounds; a single round is not a
  proof of primality.

## Exam-style questions

**Q1** *(F23 4a [S12]).* Compute $[2^{63}\bmod 11]$. By Fermat
$2^{10}\equiv 1$, so the exponent reduces mod $\varphi(11)=10$:
$63 = 6\cdot 10 + 3$, giving $2^{63}\equiv 2^3 = \mathbf 8$. (Here
$\mathrm{ord}(2)=10$ anyway: $2^2=4$, $2^5=32\equiv 10$. Reducing mod
$\varphi(N)$ is always valid for $\gcd(a,N)=1$; reducing mod the order is
valid too and sometimes shorter.)

**Q2** *(F24 1k [S16]).* True or false: $[3^{1000000}\bmod 22]=3$. — **False.**
$\gcd(3,22)=1$ and $\varphi(22)=\varphi(2)\varphi(11)=10$, so the exponent may
be reduced mod 10, giving $3^{0}=1$. The order confirms it:
$3^5 = 243 = 11\cdot 22+1$, so $\mathrm{ord}(3)=5$ and $5\mid 10^6$. Either way
the answer is $\mathbf 1$. The trap is that "$3^{1000000}$, and $10^6$ ends in
lots of zeros, so it's $3^0$-ish, so it's 3" is a plausible-sounding non-argument.

**Q3** *(F23 1i / F24 1e / F20 2b [S12, S16, S15]).* Is $(\mathbb Z,\cdot)$ a
group? Is $\mathbb Z_7^*$ cyclic? Is $(\{0,1\}^2,\oplus)$ a group, and is it
cyclic? — $(\mathbb Z,\cdot)$: **no**, only $\pm1$ have inverses.
$\mathbb Z_7^*$: **yes** — $\mathbb Z_p^*$ is cyclic for every prime $p$, and
here $3$ is a generator ($3,2,6,4,5,1$). $(\{0,1\}^2,\oplus)$: **a group**
(associative, identity $00$, every element its own inverse) but **not cyclic** —
it has order 4 and every non-identity element has order 2, so no single element
generates. It is the Klein four-group, $\mathbb Z_2\times\mathbb Z_2$.

**Q4** *(F23 1j [S12]).* For $N,e$ with $\gcd(e,\varphi(N))=1$, is
$x\mapsto[x^e\bmod N]$ a permutation of $\mathbb Z_N^*$? — **Yes.** Coprimality
gives $d$ with $ed\equiv 1 \pmod{\varphi(N)}$, so $x\mapsto x^d$ inverts it:
$x^{ed}=x^{1+t\varphi(N)}=x$ by Euler. A map on a finite set with a two-sided
inverse is a bijection. This is exactly why RSA decryption works, and the exam
asks it in the abstract. `test_rsa.py::test_rsa_is_a_permutation_of_the_unit_group`.

**Q5** *(F23 1k [S12]).* Is the discrete logarithm problem hard in
$(\mathbb Z_p,+)$ for prime $p$? — **No.** In additive notation "$g^x$" is
$x\cdot g \bmod p$, so recovering $x$ from $h = xg$ is $x = h g^{-1}\bmod p$, one
extended-Euclid call. Hardness is a property of the group; $\mathbb Z_p^*$ and
elliptic curves are believed hard, $(\mathbb Z_p,+)$ is trivially not.

**Q6** *(F23 1l / F24 1b [S12, S16]).* Does NIST recommend longer keys for
symmetric or for public-key schemes at the same security level? — **Public-key,
by an order of magnitude.** 128-bit security is AES-128, RSA-3072, a 3072-bit
$\mathbb Z_p^*$ with a 256-bit subgroup, or a 256-bit curve [S27]. The reason is
that factoring and $\mathbb Z_p^*$-DLog have sub-exponential algorithms while
brute-forcing a block cipher does not, and curves sit in between because only the
generic $\approx 2^{n/2}$ attacks apply.

**Q7** *(F24 1g [S16]).* If the CDH assumption holds in $\mathbb G$, does the
discrete-logarithm assumption hold in $\mathbb G$? — **Yes.** A DLog solver
yields a CDH solver (extract $x$ from $g^x$, output $(g^y)^x$), so if DLog were
easy CDH would be easy. Contrapositive: CDH hard $\Rightarrow$ DLog hard. The
same argument one step further gives DDH hard $\Rightarrow$ CDH hard, so DDH is
the strongest of the three assumptions.

**Q8** *(ours — the past papers do not examine prime-order subgroups directly,
though every scheme in notes 10-11 depends on them.)* Why insist that the
Diffie-Hellman group have prime order? — Three reasons. (i) Pohlig-Hellman
reduces DLog to the prime-power factors of the order, so a smooth order is
cheap to attack; prime order forces the full $O(\sqrt q)$. (ii) DDH is false in
$\mathbb Z_p^*$ because the Legendre symbol leaks a bit, and true only in the
prime-order subgroup — and ElGamal's proof needs DDH, not CDH (note 10).
(iii) Every non-identity element generates, so there are no small subgroups to
confine a peer's key into. RFC 3526's 2048-bit group is a safe prime $p=2q+1$
for exactly this reason [S26], and
`test_standard_vectors.py::test_rfc3526_group14_is_a_safe_prime_with_generator_2`
checks it.

## Code

`src/py/numtheory.py`: `egcd`, `modinv`, `modexp`, `crt`, `miller_rabin`,
`gen_prime`, `gen_safe_prime`, `factorize`, `euler_phi`, `order`, `order_mod`,
`is_generator`, `find_generator`, `subgroup_generator`, `bsgs`.
`src/py/dh.py`: `MODP2048` (RFC 3526 group 14 [S26]). Tests:
`test_numtheory.py::test_order_mod_matches_sympy_and_the_exam_items` (F24 1k,
F23 4a), `test_numtheory.py::test_miller_rabin_vs_sympy`,
`test_standard_vectors.py::test_rfc3526_group14_is_a_safe_prime_with_generator_2`.
