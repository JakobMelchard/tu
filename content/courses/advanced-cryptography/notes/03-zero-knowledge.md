# 03: Zero knowledge I: Sigma protocols and commitments

*TISS heading 3, first half [S2]. Boneh-Shoup ch. 19 (Def. 19.3-19.5, Thm
19.1, 19.14, 19.18-19.21, Lemma 19.2) and sec. 20.1-20.3 (Thm 20.1-20.3) [S4];
Goldwasser-Micali-Rackoff [S45] (cite only); Fiat-Shamir [S9]; Schnorr [S10]
(cite only); Cramer-Damgard-Schoenmakers OR-proofs [S29] (cite only);
Pedersen [S30] (cite only); weak Fiat-Shamir [S33]. Prerequisite: Schnorr
identification and Fiat-Shamir signatures in intro note
[11](../../introduction-to-cryptography/notes/11-digital-signatures.md).
Code: [`../src/py/sigma_protocols.py`](../src/py/sigma_protocols.py),
[`../src/py/commitments.py`](../src/py/commitments.py).*

## Interactive proofs

An **effective relation** $R\subseteq\mathcal X\times\mathcal Y$: $(x,y)\in R$
means "$x$ is a witness for statement $y$", checkable efficiently
[S4 Def. 19.2]. $L_R=\{y:\exists x\,(x,y)\in R\}$. A proof system is a pair of
interactive algorithms $(P(x,y), V(y))$ ending in accept/reject.

- **Completeness:** $(x,y)\in R\Rightarrow V$ accepts (w.p. 1).
- **Soundness:** for $y\notin L_R$ every $P^*$ makes $V$ accept w.p.
  $\le\varepsilon$. *Argument* if only efficient $P^*$ are covered.
- **Knowledge soundness:** an **extractor** that rewinds any $P^*$ convincing
  with probability $\varepsilon$ outputs a witness with probability
  $\mathrm{poly}(\varepsilon)$. Needed whenever every $y$ has a witness
  (every $y\in\mathbb G$ has a discrete log: plain soundness is then vacuous).
- **Zero knowledge [S45]:** for every efficient $V^*$ a simulator $\mathrm{Sim}(y)$
  outputs transcripts indistinguishable from real ones (perfect, statistical,
  computational). **HVZK:** only for the honest $V$.

## Sigma protocols

**Definition [S4 Def. 19.3-19.5].** Three moves: $P$ sends a commitment $t$,
$V$ sends a uniform challenge $c\in\mathcal C$, $P$ answers $s$; $V$ decides
from $(y,t,c,s)$. Properties:

- **Special soundness:** from two accepting $(t,c,s)$, $(t,c',s')$ with $c\ne c'$
  an efficient extractor computes a witness.
- **Special HVZK:** an efficient $\mathrm{Sim}(y,c)$ outputs $(t,s)$ such that
  $(t,c,s)$ has the real distribution, for every fixed $c$.

**Schnorr** for $R=\{(x,y): y=g^x\}$ in $\mathbb G=\langle g\rangle$, $|\mathbb G|=q$:
$$t=g^r,\quad c\gets\mathbb Z_q,\quad s=r+cx,\qquad\text{accept iff } g^s=t\,y^c.$$

*Completeness:* $g^{r+cx}=g^r(g^x)^c$.

*Special soundness:* $g^s=ty^c$ and $g^{s'}=ty^{c'}$ give
$g^{s-s'}=y^{c-c'}$, so $x=(s-s')/(c-c')\bmod q$ ($q$ prime, $c\ne c'$). $\square$

*Special HVZK:* $\mathrm{Sim}(y,c)$: $s\gets\mathbb Z_q$, $t=g^sy^{-c}$. For
fixed $c$, the real map $r\mapsto(g^r, r+cx)$ and the simulated map
$s\mapsto(g^sy^{-c},s)$ are both bijections from $\mathbb Z_q$ onto
$\{(t,s): g^s=ty^c\}$; uniform $r$ and uniform $s$ give the same uniform
distribution on that set. $\square$ (`test_hvzk_exact_distribution`
enumerates all $q^2$ transcripts for $q=11$.)

**From special soundness to knowledge soundness.** If $P^*$ succeeds with
probability $\varepsilon$, run it, then rewind to after $t$ with a fresh $c'$.
The rewinding lemma [S4 Lemma 19.2] gives two accepting transcripts with
$c\ne c'$ w.p. $\ge\varepsilon^2-\varepsilon/|\mathcal C|$, hence a witness.
Consequences: Schnorr identification is secure if DL is hard, with
$\varepsilon\le 1/N+\sqrt{\varepsilon'}$ [S4 Thm 19.1]; for a false statement
the acceptance probability is $\le 1/|\mathcal C|$ [S4 Thm 20.1].

**HVZK is not ZK.** A malicious verifier choosing $c=H(t)$ gets a transcript
it could not simulate without rewinding. With $|\mathcal C|$ polynomial one
can simulate by guessing $c$ and rewinding (expected $|\mathcal C|$ tries);
with $|\mathcal C|=q$ Schnorr is not known to be ZK. Special HVZK still
implies **witness indistinguishability** [S4 Thm 19.21], which is what OR-proofs
need.

## Fiat-Shamir [S9], [S4 sec. 19.6, 20.3.3]

Replace $c$ by $c=H(y,t,\text{msg})$. The result is a non-interactive proof
$(t,s)$ (or a signature on msg). In the ROM: sound with loss $Q_{ro}+1$
[S4 Thm 20.2] and zero-knowledge, the simulator programming
$H(y,t,\cdot):=c$ at a simulated $(t,c,s)$ [S4 Thm 20.3].

**The statement must be hashed.** "Weak" Fiat-Shamir $c=H(t,\text{msg})$ lets
a cheater pick $y$ after $c$: fix any $t$, compute $c=H(t)$, pick $s$, set
$y=(g^st^{-1})^{1/c}$. Then $g^s=ty^c$ holds, yet the cheater knows no
$\log_g y$ (it would need $\log_g t$). Harmless for signatures with fixed
$pk$, fatal for proofs about adversarially chosen statements [S33], [S4 Ex.
19.12, 20.13] (`weak_fs_forge`).

## Commitments

$\mathsf{Com}(m;r)\to C$, opened by revealing $(m,r)$.
**Hiding:** $C$ reveals nothing about $m$. **Binding:** no efficient
adversary opens $C$ two ways. Not both can be information-theoretic: if every
$C$ had openings to all $m$ (perfect hiding) an unbounded adversary finds them.

**Pedersen [S30].** Public $g,h\in\mathbb G$ with $\log_g h$ unknown.
$C=g^mh^r$, $r\gets\mathbb Z_q$.

- *Perfectly hiding:* for fixed $m$, $r\mapsto g^mh^r$ is a bijection
  $\mathbb Z_q\to\mathbb G$ ($h\ne1$), so $C$ is uniform independently of $m$.
  (`test_pedersen_perfectly_hiding_exact`.)
- *Computationally binding under DL:* two openings $g^{m}h^{r}=g^{m'}h^{r'}$
  with $m\ne m'$ give $\log_g h=(m-m')/(r'-r)$. A binding adversary is a DL
  solver: $\mathsf{Adv}^{\mathrm{bind}}\le\mathsf{Adv}^{\mathrm{dl}}$ (tight).
- *Trapdoor:* whoever knows $\tau=\log_gh$ opens $C$ to any $m'$ with
  $r'=r+(m-m')/\tau$. Generating $h$ by hashing to the group avoids this.
- *Homomorphic:* $\mathsf{Com}(m_1;r_1)\,\mathsf{Com}(m_2;r_2)=\mathsf{Com}(m_1+m_2;r_1+r_2)$.

**Hash commitment** $C=H(r\|m)$: hiding in the ROM, binding by collision
resistance; the dual trade-off.

## Composition: AND and OR [S4 sec. 19.7], [S29]

**AND** for $y_0,y_1$: run both with the same challenge.

**OR** for $R_{\vee}=\{((x,b),(y_0,y_1)): y_b=g^x\}$: the prover knowing
$x=\log y_b$

1. simulates branch $1-b$: $(t_{1-b},c_{1-b},s_{1-b})\gets\mathrm{Sim}(y_{1-b})$;
2. commits honestly in branch $b$: $t_b=g^r$; sends $(t_0,t_1)$;
3. on challenge $c$ sets $c_b=c-c_{1-b}$, $s_b=r+c_bx$; sends
   $(c_0,c_1,s_0,s_1)$.

$V$ checks $c_0+c_1=c$ and both Schnorr equations. *Special soundness:*
two accepting answers to $c\ne c'$ with the same $(t_0,t_1)$ have
$c_0+c_1\ne c_0'+c_1'$, so some branch $i$ has $c_i\ne c_i'$ and yields
$\log y_i$. *Special HVZK:* simulate both branches with $c_0$ random and
$c_1=c-c_0$. *WI:* for fixed $c$ the transcript is uniform on accepting
transcripts with $c_0+c_1=c$ whichever $b$ was used
(`test_or_proof_witness_indistinguishable_exact`).

## Worked example

$\mathbb G\subset\mathbb Z_{23}^*$, $q=11$, $g=4$ (groups.TINY); secret
$x=7$, $y=4^7\bmod23=8$.

- Honest run: $r=5$, $t=4^5=12$; $c=3$, $s=5+21\equiv4$. Check
  $g^s=4^4=3$ and $ty^c=12\cdot8^3=12\cdot6=72\equiv3$. ✓
- Rewind with $c'=8$: $s'=5+56\equiv6$. Extract
  $(4-6)(3-8)^{-1}=(-2)(-5)^{-1}=2\cdot5^{-1}=2\cdot9\equiv7=x$. ✓
- Simulate $c=4$, $s=9$: $t=4^9\cdot8^{-4}=13\cdot2^{-1}=13\cdot12\equiv18$;
  check $ty^c=18\cdot2\equiv13=g^9$. ✓
- Pedersen with $h=4^6=2$ (trapdoor $\tau=6$): $\mathsf{Com}(3;2)=64\cdot4\equiv3$.
  Equivocate to $m'=5$: $r'=2+(3-5)\cdot6^{-1}=2-2\cdot2\equiv9$; check
  $4^5\cdot2^9=12\cdot6\equiv3$. ✓

## Pitfalls

- **Soundness vs knowledge.** "Schnorr is sound" is empty (every $y$ has a
  log); state knowledge soundness.
- **Small challenge space.** Soundness error $1/|\mathcal C|$; $\mathcal C=\{0,1\}$
  needs $\lambda$ repetitions.
- **Reused $r$** leaks $x$ exactly like the extractor (intro note 11).
- **Weak Fiat-Shamir** (statement not hashed).
- **Pedersen generators with known relation** (anyone who knows $\log_g h$
  breaks binding); and Pedersen is *not* binding against unbounded adversaries.

## Exam-style questions

1. *Give the Chaum-Pedersen protocol for $\{(x,(u,v,w)): v=g^x, w=u^x\}$ and
   its extractor.* $t_1=g^r$, $t_2=u^r$, $s=r+cx$; check $g^s=t_1v^c$ and
   $u^s=t_2w^c$; extractor as Schnorr [S4 sec. 19.5.2] (`cp_prove`).
2. *Show the OR-proof is special sound.* Above.
3. *A prover convinces the Schnorr verifier w.p. $\varepsilon=2^{-40}$ with
   $|\mathcal C|=2^{256}$. Does that break DL?* Rewinding extracts w.p.
   $\ge\varepsilon^2-\varepsilon/N\approx2^{-80}$: a DL algorithm with twice
   the running time and success $2^{-80}$. The square is the price of
   rewinding; the conclusion is loose but still contradicts a
   $2^{-128}$-hard group.
4. *Why can Pedersen not be perfectly binding, and what breaks if $h=g^2$
   is public?* Perfect hiding means every $C$ has an opening for every $m$;
   with $h=g^2$ open $\mathsf{Com}(m;r)$ as $(m+2,\,r-1)$.
5. *Fiat-Shamir without the message in the hash: what goes wrong for
   signatures?* $c=H(t)$ does not depend on $m$: one signature $(t,s)$
   verifies for every message. Existential forgery.

## Code

`sigma_protocols.py`: `schnorr_commit/respond/check/run`, `schnorr_simulate`,
`schnorr_extract`, `fs_prove/fs_verify` (strong and weak), `weak_fs_forge`,
`cp_prove/cp_check`, `or_prove/or_check/or_extract`, `or_fs_prove/verify`.
`commitments.py`: `pedersen_commit/open`, `pedersen_equivocate`,
`pedersen_dlog_from_double_opening`, `hash_commit`. The groups are in
`groups.py` (TINY $q=11$, TOY $q=1019$, MEDIUM 128-bit).
