# 05 Relational algebra and relational calculus

> **Sourcing.** Operators from [S6] ch. 2 ("six basic operators"); calculus,
> domain independence and the equivalence theorem from [S10] ch. 4-5
> (Def. 5.3.7, Lemma 5.3.8, Thm. 5.4.6). The relational calculus is not in the
> main chapters of [S6] 7th ed., so check the course's own notation when the
> slides appear. Results below are computed by `relalg.py` and cross-checked
> against sqlite in `test_relalg.py`.

## Algebra: operators

Relations are sets; every operator maps relations to a relation.

| operator | definition | schema of result |
|---|---|---|
| selection $\sigma_\theta(R)$ | $\{t \in R : \theta(t)\}$ | $R$ |
| projection $\pi_X(R)$ | $\{t[X] : t \in R\}$ (duplicates vanish) | $X$ |
| union, difference $R \cup S$, $R - S$ | set operations; $R$, $S$ **union-compatible** (same attributes, compatible domains) | $R$ |
| Cartesian product $R \times S$ | $\{rs : r \in R, s \in S\}$; attribute names disjoint | $R \cup S$ |
| rename $\rho_{S(B_1..B_n)}(R)$ | same tuples, new names | renamed |

These six are the **basic** operators [S6]. Everything else is derived:

$$R \cap S = R - (R - S),\qquad R \bowtie_\theta S = \sigma_\theta(R \times S),$$
$$R \bowtie S = \pi_{\mathrm{attr}(R) \cup \mathrm{attr}(S)}\big(\sigma_{R.C = S.C\ \forall C \in \mathrm{attr}(R) \cap \mathrm{attr}(S)}(R \times S)\big),$$
$$R \ltimes S = \pi_{\mathrm{attr}(R)}(R \bowtie S),\qquad R \mathbin{\bar\ltimes} S = R - (R \ltimes S).$$

**Division.** With $\mathrm{attr}(S) \subset \mathrm{attr}(R)$ and
$X = \mathrm{attr}(R) \setminus \mathrm{attr}(S)$,
$R \div S = \{x : \forall s \in S.\ (x, s) \in R\}$ ("the $x$ paired with every $s$"). Derivation:
$\pi_X(R) \times S$ are all candidate pairs; minus $R$ leaves the missing pairs;
their $X$-values are the disqualified candidates:

$$R \div S = \pi_X(R) - \pi_X\big((\pi_X(R) \times S) - R\big).$$

If $S = \emptyset$, nothing is missing and $R \div S = \pi_X(R)$.

**Extended** (not in the pure algebra): outer joins (pad dangling tuples with
NULL), grouping/aggregation $\gamma_{G;\,f(A)}(R)$.

Size bounds with $|R| = m$, $|T| = k$, $|S| = n > 0$ (the first four, and
$|R \bowtie S| \le m$ for $\mathrm{attr}(S) \subseteq \mathrm{attr}(R)$, are
checked on random instances in `practice.py`, item P6):

$$|R \cup T| \le m + k,\quad |R - T| \ge m - k,\quad |\pi_X(R)| \le m,\quad |R \div S| \le m/n,\quad |R \bowtie S| \le m \cdot n.$$

## Calculus

**Tuple relational calculus (TRC):** $\{t \mid \varphi(t)\}$, $t$ a tuple
variable, $\varphi$ built from $t \in R$, comparisons $t.A \,\theta\, u.B$ or
$t.A \,\theta\, c$, $\land, \lor, \lnot$, $\exists u \in R$, $\forall u \in R$.
**Domain relational calculus (DRC):** $\{\langle x_1, \dots, x_k\rangle \mid \varphi\}$,
variables range over domain values, atoms $R(x_1, \dots, x_n)$.

**Safety.** $\{x \mid \lnot R(x)\}$ depends on what the variable ranges over.
A query is **domain independent** if its answer is the same for every domain
containing the active domain (the values in the database and the query)
[S10] Def. 5.3.7; then evaluating over the active domain gives the answer
(Lemma 5.3.8). Domain independence is undecidable ([S10] section 6.3), so languages use a
syntactic sufficient condition (safe-range formulas).

**Codd's theorem** in the form of [S10] Thm. 5.4.6: the safe-range calculus
and the relational algebra express exactly the same queries. Practical reading:
any algebra expression can be written in safe calculus and vice versa; $\forall$
becomes a double negation, which is division in the algebra and a double
`NOT EXISTS` in SQL (note 06).

## Worked example: "passed every 6-ECTS course"

`relalg.sample_db()`: $S(\mathit{sid}, \mathit{name}, \mathit{sem})$ with five
students (Eve, sid 5, has passed nothing), $C(\mathit{cid}, \mathit{title}, \mathit{ects})$
with DB (6), AL (3), TH (6), $P(\mathit{sid}, \mathit{cid})$ = passed.

Algebra:

$$\mathit{Six} = \pi_{cid}(\sigma_{ects = 6}(C)) = \{DB, TH\},\qquad
P \div \mathit{Six} = \{1, 2\}.$$

By the formula: $\pi_{sid}(P) = \{1,2,3,4\}$; $\pi_{sid}(P) \times \mathit{Six}$
has 8 pairs; minus $P$ leaves $(3,DB), (3,TH), (4,TH)$; their sids $\{3, 4\}$;
$\{1,2,3,4\} - \{3,4\} = \{1, 2\}$.

TRC: $\{t \mid \exists p \in P\,(p.sid = t.sid) \land \forall c \in \mathit{Six}\ \exists q \in P\,(q.sid = t.sid \land q.cid = c.cid)\}$
with $t$ over $\pi_{sid}(P)$.

DRC: $\{\langle x\rangle \mid \exists y\, P(x, y) \land \forall c\,(\mathit{Six}(c) \Rightarrow P(x, c))\}$.

SQL (double negation: no 6-ECTS course that $x$ has not passed):

```sql
SELECT DISTINCT sid FROM P p WHERE NOT EXISTS (
  SELECT * FROM six c WHERE NOT EXISTS (
    SELECT * FROM P q WHERE q.sid = p.sid AND q.cid = c.cid));
```

All four give $\{1, 2\}$ (`python src/py/relalg.py`; the test
`test_relalg.py::test_division_three_ways` also adds a `GROUP BY ... HAVING
count(DISTINCT) =` formulation and repeats it on 25 random databases).

Other results of the demo: students with no pass $= \pi_{name}(S \mathbin{\bar\ltimes} P) = \{\text{Eve}\}$;
$S$ left-outer-join $P$ has 8 rows (Eve padded with NULL).

## Pitfalls

- $\pi$ removes duplicates; SQL `SELECT` does not (note 06).
- Natural join of relations with no common attribute is the Cartesian product;
  with all attributes common it is the intersection.
- $\pi$ distributes over $\cup$ but **not** over $-$: $R = \{(1,1),(1,2)\}$,
  $T = \{(1,1)\}$ gives $\pi_a(R - T) = \{1\}$ but $\pi_a R - \pi_a T = \emptyset$
  (`test_relalg.py::test_projection_difference_counterexample`).
- $\forall$ over an empty range is true: $R \div \emptyset = \pi_X(R)$.
- Selection pushdown past a join is valid only if $\theta$ mentions attributes of one side.
- In TRC/DRC, a negated atom must be guarded by a positive one, or the query is unsafe.

## Exam-style questions

1. *True or false: $R \cap S$ can be expressed with $-$ alone.* **True**: $R - (R - S)$.
2. *$|R| = 6$, $|S| = 3$, $\mathrm{attr}(S) \subset \mathrm{attr}(R)$. Maximum $|R \div S|$?* **2**.
3. *True or false: $\sigma_{A=1}(R \bowtie S) = \sigma_{A=1}(R) \bowtie S$ when $A$ is an attribute of $R$ only.* **True**.
4. *Is $\{x \mid \lnot \mathit{Passed}(x, \text{'DB'})\}$ domain independent?* **No**: adding an unused
   value to the domain adds it to the answer (`test_relalg.py::test_unsafe_query_depends_on_domain`).
5. *True or false: every relational-algebra query can be written in the safe relational calculus.* **True** [S10] Thm. 5.4.6.

## Code

`src/py/relalg.py`: `relalg.Relation`, `relalg.select`, `relalg.project`,
`relalg.rename`, `relalg.union`, `relalg.difference`, `relalg.intersect`,
`relalg.product`, `relalg.natural_join`, `relalg.theta_join`,
`relalg.semijoin`, `relalg.antijoin`, `relalg.division`,
`relalg.left_outer_join`, `relalg.group_count`, `relalg.trc`, `relalg.drc`,
`relalg.to_sqlite`. `test_relalg.py` compares each operator with the equivalent
SQL on 25 random databases.
