# 04 Functional dependencies and normal forms

> **Sourcing.** [S6] ch. 7 for closure, canonical cover, the normal forms, 3NF
> synthesis and BCNF decomposition; [S10] Thm. 8.2.11 (Armstrong's axioms are
> sound and complete), ch. 8.4 (chase), Def. 11.2.1 and 11.2.11 (BCNF, 3NF);
> the synthesis algorithm goes back to Bernstein [S12] (not read). Every number
> below is printed by `python src/py/fd.py` or asserted in `test_fd.py`.

## Definitions

$R$ a schema, $X, Y \subseteq \mathrm{attr}(R)$. The **functional dependency**
$X \to Y$ holds in an instance $r$ iff

$$\forall t_1, t_2 \in r:\quad t_1[X] = t_2[X] \;\Rightarrow\; t_1[Y] = t_2[Y].$$

It is **trivial** if $Y \subseteq X$. $F \models X \to Y$ ($F$ implies it) iff
every instance satisfying $F$ satisfies $X \to Y$; $F^+$ is the set of all
implied FDs.

**Armstrong's axioms** ([S10] FD1-FD3, sound and complete, Thm. 8.2.11):
reflexivity ($Y \subseteq X \Rightarrow X \to Y$), augmentation
($X \to Y \Rightarrow XZ \to YZ$), transitivity ($X \to Y, Y \to Z \Rightarrow
X \to Z$). Derived: union, decomposition ($X \to YZ \Rightarrow X \to Y$),
pseudo-transitivity.

**Attribute closure** $X^+ = \{A : F \models X \to A\}$, computed by the fixpoint

$$X^{(0)} = X,\qquad X^{(i+1)} = X^{(i)} \cup \bigcup\{\,W : V \to W \in F,\ V \subseteq X^{(i)}\,\}.$$

Then $F \models X \to Y \iff Y \subseteq X^+$, and $X$ is a **superkey** iff
$X^+ = \mathrm{attr}(R)$. This one algorithm answers every implication, key and
normal-form question below.

**Finding all candidate keys.** An attribute on no right-hand side is in
**every** key (nothing derives it); one on right-hand sides only is in **no**
key. Start from the first set, add attributes from the "both sides" set in order
of size, stop extending a set once it is a superkey (`fd.candidate_keys`).

**Minimal (canonical) cover** $G \equiv F$ with (1) singleton right sides,
(2) no extraneous left attribute ($A$ in $X$ is extraneous in $X \to B$ if
$B \in (X \setminus A)^+$), (3) no redundant FD ($G \setminus \{f\} \models f$).
Not unique; its size is.

### Normal forms

A **prime** attribute belongs to some candidate key.

| NF | condition for every nontrivial $X \to A$ in $F^+$ ($A$ a single attribute) |
|---|---|
| 1NF | domains atomic (assumed throughout) |
| 2NF | no non-prime $A$ depends on a **proper subset** of a candidate key |
| 3NF | $X$ is a superkey **or** $A$ is prime ([S10] Def. 11.2.11) |
| BCNF | $X$ is a superkey ([S10] Def. 11.2.1) |

$\text{BCNF} \subsetneq 3\text{NF} \subsetneq 2\text{NF} \subsetneq 1\text{NF}$.
It suffices to check the FDs of $F$ (split to single right sides) rather than
all of $F^+$ [S6].

### Decompositions

$\{R_1, \dots, R_k\}$ with $\bigcup R_i = R$ is

- **lossless** iff $\pi_{R_1}(r) \bowtie \dots \bowtie \pi_{R_k}(r) = r$ for every
  legal $r$. For $k = 2$: iff $R_1 \cap R_2 \to R_1$ or $R_1 \cap R_2 \to R_2$
  [S6]. In general: the **chase** [S10] ch. 8.4 (`fd.is_lossless`).
- **dependency preserving** iff $(\bigcup_i F|_{R_i})^+ = F^+$. Test without
  projecting: for each $X \to Y \in F$, grow $Z := X$ by
  $Z := Z \cup ((Z \cap R_i)^+ \cap R_i)$ until stable; preserved iff $Y \subseteq Z$
  (`fd.preserves`).

| algorithm | result | lossless | dep. preserving |
|---|---|---|---|
| **3NF synthesis**: minimal cover; one schema $X \cup \{A \mid X \to A\}$ per left side $X$; add a candidate key if no schema contains one; drop schemas contained in others | 3NF | yes | **yes** |
| **BCNF decomposition**: while some $R_i$ has a violation $X \to Y$, replace it by $X^+ \cap R_i$ and $X \cup (R_i \setminus X^+)$ | BCNF | yes | **not always** |

## Worked example 1 (the `fd.py` demo)

$R = ABCDE$, $F = \{A \to B,\ B \to C,\ CD \to E,\ E \to A\}$.

1. Closures: $A^+ = ABC$; $CD^+$: $CD \to E$ gives $CDE$, $E \to A$ gives $ACDE$,
   $A \to B$ gives $ABCDE$. So $CD$ is a superkey.
2. Keys. Every attribute appears on a right side except $D$, so $D$ is in every
   key; $D^+ = D$. Try $D$ plus one attribute: $AD^+ = ABCDE$, $BD^+ = BCD \to$
   $CD \to E \to A$: all; $CD$, $DE$ likewise. Keys: $\{AD, BD, CD, DE\}$ (four).
3. Minimal cover: $F$ itself (single right sides, no extraneous attribute: $C^+ = C$,
   $D^+ = D$; no FD redundant).
4. Every attribute is prime, so every FD passes the 3NF test: **3NF**. $A \to B$
   has a non-superkey left side: **not BCNF**.
5. 3NF synthesis: $AB, BC, CDE, AE$; $CDE$ contains the key $CD$, so no key
   schema is added. Lossless and dependency preserving (the code checks both).
6. BCNF decomposition: split on $A \to B$: $A^+ \cap R = ABC$ and $ADE$. In $ABC$
   ($A \to B$, $B \to C$), $B \to C$ violates: $BC$, $AB$. In $ADE$ the projected
   FDs are $E \to A$, $AD \to E$; $E \to A$ violates: $AE$, $DE$.
   Result $BC, AB, AE, DE$: lossless, but **$CD \to E$ is lost** ($C$, $D$, $E$
   never share a schema; `fd.preserves` returns False).

## Worked example 2: anomalies and repair

$\mathit{exam}(s, n, c, t, g)$ = (student id, student name, course id, course
title, grade) with $s \to n$, $c \to t$, $sc \to g$. Key: $sc$ (neither $s$ nor
$c$ is derivable). $s \to n$ is a partial dependency of the non-prime $n$: only
**1NF**. The anomalies this causes:

- update: renaming a course touches every exam row of it;
- insertion: a course without exams cannot be stored (the key would contain NULL);
- deletion: deleting the last exam of a student deletes the student's name.

Synthesis and BCNF decomposition agree here: $\{sn, ct, scg\}$.

## Worked example 3: the chase

$R = ABC$, $F = \{A \to B\}$. Decomposition $\{AB, BC\}$: rows $(a, a, b_1)$ and
$(b_2, a, a)$ (row $i$ has distinguished $a$ on $R_i$'s attributes). The only FD
has left side $A$, and the rows disagree on $A$: nothing changes, no all-$a$ row:
**lossy**. Decomposition $\{AB, AC\}$: rows $(a, a, b_1)$, $(a, b_2, a)$ agree on
$A$, so $A \to B$ equates $b_2 := a$; row 2 becomes $(a, a, a)$: **lossless**.
Binary shortcut: $AB \cap AC = A$, $A \to AB$. Yes.

## Pitfalls

- A 3NF test must check primality against **all** candidate keys, not just the primary key.
- BCNF can be impossible to reach while preserving dependencies:
  $R = ABC$, $F = \{AB \to C, C \to B\}$ is 3NF, keys $AB$, $AC$; its only BCNF
  split $\{BC, AC\}$ loses $AB \to C$ (`test_fd.py::test_bcnf_can_lose_dependency`).
- Lossless is about joins of projections, not about losing rows: a lossy
  decomposition produces **extra** (spurious) tuples.
- "Every two-attribute schema is in BCNF" is true; "every schema with a single
  key is in BCNF" is false (transitive dependencies).
- Minimal covers are not unique; the number of schemas from synthesis can differ
  between covers.
- Projecting $F$ onto $R_i$ means $F^+$ restricted to $R_i$, not the FDs of $F$
  that happen to fit (`fd.project`).

## Exam-style questions

1. *$R(ABCD)$, $F = \{AB \to C, B \to D\}$. Highest normal form?* **1NF**: key
   $AB$, and $B \to D$ is a partial dependency of the non-prime $D$.
2. *$R(ABCDE)$, $F = \{AB \to C, A \to D, D \to E, E \to A\}$. Candidate keys and
   NF?* Keys **$AB$, $BD$, $BE$**; every non-prime ($C$) depends only on keys and
   $A, D, E$ are prime: **3NF**, not BCNF ($A \to D$).
3. *Minimal cover of $\{A \to BC, B \to C, AB \to C, A \to B\}$?* **$\{A \to B, B \to C\}$**.
4. *True or false: the decomposition $\{AB, BC\}$ of $R(ABC)$ with $F = \{A \to B\}$ is lossless.*
   **False** ($AB \cap BC = B$ determines neither side).
5. *True or false: 3NF synthesis always yields a dependency-preserving
   decomposition, BCNF decomposition always a lossless one.* **Both true** [S6].

## Code

`src/py/fd.py`: `fd.closure`, `fd.implies`, `fd.candidate_keys`,
`fd.prime_attributes`, `fd.minimal_cover`, `fd.project`, `fd.is_2nf`,
`fd.is_3nf`, `fd.is_bcnf`, `fd.normal_form`, `fd.synthesize_3nf`,
`fd.bcnf_decompose`, `fd.is_lossless` (chase), `fd.preserves`. Tests compare
keys with a brute-force search over all subsets, check minimal covers for
equivalence and minimality on random FD sets, and check the chase against the
binary criterion on 300 random decompositions.
