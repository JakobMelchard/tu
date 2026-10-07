# 06: Secure multi-party computation II: OT, GMW, Yao

*TISS heading 4, second half [S2]. Lindell survey [S7] sec. 3, 4.5;
Lindell-Pinkas [S13] (the complete description and proof of Yao) sec. 3-4;
Yao [S12] and Goldreich-Micali-Wigderson [S11] (cite only); Boneh-Shoup sec.
11.6 (OT from Diffie-Hellman) and 23.3 (garbled circuits) [S4]. Code:
[`../src/py/garbled_circuit_toy.py`](../src/py/garbled_circuit_toy.py).*

With $t\ge n/2$, in particular two parties, secret sharing with an honest
majority is unavailable. The tools are **oblivious transfer** and either
**XOR-sharing with OT per AND gate (GMW)** or **garbled circuits (Yao)**.
Security is computational and without fairness [S7 sec. 3].

## Oblivious transfer

**Functionality [S13 sec. 3.2].** 1-out-of-2 OT:
$((m_0,m_1),\sigma)\mapsto(\bot,\ m_\sigma)$. The sender learns nothing about
$\sigma$, the receiver nothing about $m_{1-\sigma}$. 1-out-of-$n$ likewise.

**OT from trapdoor permutations, semi-honest [S13 Protocol 1].**

1. $S$ picks a trapdoor permutation $(f,f^{-1})$, sends $f$.
2. $R$ picks $v_\sigma$, sets $w_\sigma=f(v_\sigma)$, and samples $w_{1-\sigma}$
   **directly** from the domain (without a preimage); sends $(w_0,w_1)$.
3. $S$ sends $b_j=B(f^{-1}(w_j))\oplus m_j$, $B$ a hard-core bit.
4. $R$ outputs $B(v_\sigma)\oplus b_\sigma$.

$S$ sees two uniform elements (receiver privacy, perfect). A semi-honest $R$
does not know $f^{-1}(w_{1-\sigma})$, and $B$ of it is pseudorandom (sender
privacy). A *malicious* $R$ would sample both with preimages: semi-honest only.

**OT from Diffie-Hellman in the ROM [S4 sec. 11.6.1]** (1-out-of-$n$, the one
in the code). $\mathbb G=\langle g\rangle$ of order $q$, hash $H$.

1. $S$: $\beta\gets\mathbb Z_q$, sends $v=g^\beta$.
2. $R$ (choice $i$): $\alpha\gets\mathbb Z_q$, sends $u=g^\alpha v^{-i}$.
3. $S$: for each $j$, $u_j=uv^j$, $k_j=H(v,u_j^\beta)$, sends $c_j=E_{k_j}(m_j)$.
4. $R$: $k=H(v,v^\alpha)$, decrypts $c_i$.

*Correctness:* $u_i=g^\alpha$, so $u_i^\beta=g^{\alpha\beta}=v^\alpha$.
*Receiver privacy:* $g^\alpha$ is uniform and independent of $i$, so $u$ is.
*Sender privacy (sketch):* learning two keys means querying $H$ at
$(v,(uv^{j_1})^\beta)$ and $(v,(uv^{j_2})^\beta)$; dividing gives
$v^{\beta(j_1-j_2)}$, hence $g^{\beta^2}$ from $g^\beta$, equivalent to CDH
[S4 sec. 11.6.1]. Caveat in [S4]: not secure as is under concurrent composition.

## GMW (XOR sharing) [S11], [S7 sec. 4.5]

Each bit $v$ is shared $v=v_1\oplus v_2$.

- **Input:** the owner picks a random $r$ and hands out $(v\oplus r, r)$.
- **XOR, NOT:** local ($v_1\oplus w_1$, $v_2\oplus w_2$; one party flips).
- **AND** $c=(a_1\oplus a_2)(b_1\oplus b_2)$: $P_1$ picks $r$, offers the
  4-entry table $T[u,v]=r\oplus\big((a_1\oplus u)(b_1\oplus v)\big)$ in a
  1-out-of-4 OT; $P_2$ selects $(u,v)=(a_2,b_2)$. Shares: $c_1=r$,
  $c_2=T[a_2,b_2]$.
- **Output:** exchange output shares.

*Correctness:* $c_1\oplus c_2=(a_1\oplus a_2)(b_1\oplus b_2)$ by construction.
*Privacy:* $P_1$'s view of each AND is its own $r$ plus the OT, which hides
$(a_2,b_2)$; $P_2$ gets $r\oplus(\dots)$ with $r$ uniform, a uniform bit. A
simulator outputs uniform bits for every received share. Rounds grow with
the **AND-depth**; XOR is free.

## Yao's garbled circuits [S12], [S13 sec. 4], [S4 sec. 23.3]

**Garbling** (by $P_1$). For each wire $w$ two random labels
$k_w^0,k_w^1\in\{0,1\}^\kappa$. For a gate $g$ with inputs $a,b$, output $c$,
the table has one row per $(\alpha,\beta)$:
$$\mathrm{Enc}_{k_a^\alpha}\big(\mathrm{Enc}_{k_b^\beta}(k_c^{g(\alpha,\beta)})\big),$$
randomly permuted. Output wires get a decoding table $k^0\mapsto0$, $k^1\mapsto1$.

**Evaluation** (by $P_2$), holding one label per input wire: for each gate try
the rows; exactly one decrypts correctly. [S13] makes wrong rows detectable
by an **efficiently verifiable, elusive range** (here: a 16-byte zero tag);
practical schemes use point-and-permute bits instead (**background**).

**Protocol.** $P_1$ sends the garbled circuit and the labels of its own input
bits; $P_2$ obtains the labels of its input bits by **one OT per bit**; $P_2$
evaluates and decodes. Constant rounds, independent of depth.

**Theorem [S13 Thm 7].** If the OT is secure against semi-honest adversaries
and the encryption is CPA-secure with an elusive and efficiently verifiable
range, the protocol securely computes $f$ against static semi-honest
adversaries.

*Simulators (idea).* Corrupted $P_1$: its view is its own coins plus OT
transcripts; simulate with the OT sender simulator. Corrupted $P_2$: given
$y$ and $f(x,y)$, build a **fake** garbled circuit in which every row of
every gate encrypts the *same* output label, so evaluation always follows
one "active" path, and let the output table map that label to $f(x,y)$. The
evaluator can decrypt only the active row of each table; the other three rows
hide labels it never holds, so by CPA security (a hybrid over gates) fake and
real circuits are indistinguishable [S13 sec. 4.2, proof of Thm 7].

| | GMW | Yao |
|---|---|---|
| rounds | $O(\text{AND-depth})$ | constant |
| per AND gate | one 1-of-4 OT, bits | 4 ciphertexts of $\kappa$ bits |
| parties | $n$ (generalises directly) | 2 (multi-party via BMR, background) |
| roles | symmetric | garbler / evaluator |

## Malicious adversaries (orientation)

Semi-honest Yao is broken by a malicious garbler (garble a different
function). Remedies named in [S7 sec. 4.5]: cut-and-choose, SPDZ-style MACs,
TinyOT, MPC-in-the-head. GMW's compiler forces honest behaviour with
zero-knowledge proofs of correct computation (note 03) [S11]
(**background**).

## Worked example

**OT** in groups.TINY ($p=23$, $q=11$, $g=4$), receiver wants $i=1$ of 2:
$\beta=3$, $v=4^3=18$; $\alpha=2$, $u=4^2\cdot18^{-1}=16\cdot9\equiv6$.
Sender: $u_0=6$, $u_0^\beta=216\equiv9$; $u_1=6\cdot18\equiv16=g^\alpha$,
$u_1^\beta=16^3\equiv2$. Receiver: $v^\alpha=18^2\equiv2=u_1^\beta$: only key
1 matches. ✓

**GMW AND** of $a=1$ ($a_1=1,a_2=0$) and $b=1$ ($b_1=0,b_2=1$): $P_1$
picks $r=1$, table $T[u,v]=1\oplus(1\oplus u)v$:
$T[0,0]=1$, $T[0,1]=0$, $T[1,0]=1$, $T[1,1]=1$. $P_2$ selects $T[0,1]=0$.
Shares $(1,0)$, XOR $=1=a\wedge b$. ✓

**Millionaires, 2 bits:** $[x>y]=(x_1\bar y_1)\vee(\overline{x_1\oplus
y_1}\,x_0\bar y_0)$; `COMPARATOR` has 8 gates, and the demo prints all 16
input pairs for plain, Yao and GMW evaluation.

## Pitfalls

- **OT receiver privacy is not sender privacy.** The DH-OT hides $i$
  perfectly but protects $m_{1-i}$ only computationally and only in the ROM.
- **Reusing garbled circuits or labels** across two evaluations leaks: with
  both labels of a wire the evaluator can decrypt more rows.
- **Evaluator learns only the output label's meaning via the decoding
  table**; decoding tables for internal wires would leak intermediate values.
- **Semi-honest security says nothing about a garbler who garbles the wrong
  circuit.**
- **"MPC gives privacy" is relative to $f$**: the output itself may reveal
  inputs (the millionaires' output reveals an order).

## Exam-style questions

1. *Show GMW's AND sub-protocol is correct and that $P_2$'s share is a
   uniform bit.* Above.
2. *Why does the evaluator in Yao need exactly one label per wire, and what
   breaks if $P_1$ sends both labels of $P_2$'s input wires?* With both it
   evaluates on every $y'$ and learns $f(x,\cdot)$: not simulatable from
   $f(x,y)$.
3. *Describe the simulator for a corrupted evaluator.* Fake circuit with one
   active label per wire and the output table forced to $f(x,y)$; hybrid over
   gates with CPA security.
4. *In the DH-based OT, prove receiver privacy and show the receiver cannot
   learn two messages unless CDH is easy.* Above.
5. *Compare rounds and communication of GMW and Yao for a circuit of depth
   $d$ with $s$ AND gates.* GMW $O(d)$ rounds, $s$ OTs; Yao $O(1)$ rounds,
   $4s$ ciphertexts plus one OT per input bit of $P_2$.

## Code

`garbled_circuit_toy.py`: `ot_sender_1/2`, `ot_receiver_1/2`, `ot`
(1-out-of-$n$, [S4 sec. 11.6.1]); `garble`, `evaluate`, `yao`; `gmw_and`,
`gmw`; `COMPARATOR`, `eval_plain`. Tests run every input of the comparator
and of random 12-gate circuits through both protocols.
