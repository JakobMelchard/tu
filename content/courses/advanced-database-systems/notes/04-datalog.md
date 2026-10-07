# 04 Datalog: syntax, semantics, evaluation, stratified negation

> **Sourcing.** Abiteboul, Hull, Vianu, *Foundations of Databases* [S7]:
> ch. 12 (syntax, model/fixpoint/proof semantics), 13.1 (semi-naive), 15.2
> (stratified negation); Green, Huang, Loo, Zhou [S8]; the 2026 block-1 topic
> list (naive "INFER" loop, semi-naive, negation, stratification, safety) from
> [S3] and the VoWi SS26 report [S2]. All programs run in `datalog.py`.

## Definitions

- **Term**: a variable (`X`, upper case) or a constant (`a`, `42`, `'Ann'`).
- **Atom**: $p(t_1, \ldots, t_k)$, predicate $p$ of arity $k$. **Literal**: an atom
  or a negated atom `not p(...)`, or a comparison `X < Y`.
- **Rule**: $H \leftarrow B_1, \ldots, B_n$ written `H :- B1, ..., Bn.` (the comma is AND).
  **Fact**: a rule with empty body and no variables, `edge(a, b).`
- **EDB** (extensional database): predicates given as stored facts (tables).
  **IDB** (intensional): predicates defined by rules (views). IDB predicates appear in heads.
- **Safety (range restriction)**: every variable of the head, of a negated atom
  and of a comparison occurs in a **positive** relational atom of the body.
  Guarantees finite answers drawn from the active domain (the constants occurring in the input).
- **Recursive** predicate: depends on itself in the dependency graph. A rule is
  **linear** if at most one body atom is recursive (mutually recursive with the head).

## Datalog vs SQL, side by side

| Datalog | SQL |
|---|---|
| `q(N, T) :- student(M, N), exam(M, C, G), course(C, T), G <= 2.` | `SELECT s.name, c.title FROM student s, exam e, course c WHERE s.id = e.id AND e.course = c.id AND e.grade <= 2` |
| two rules with the same head | `UNION` |
| recursive rule | `WITH RECURSIVE` |
| `not p(X)` | `NOT EXISTS` / `EXCEPT` |
| set semantics always | bag semantics unless `DISTINCT`/`UNION` |

Non-recursive Datalog with (safe, stratified) negation expresses exactly the
relational algebra (Codd's theorem, strengthened) [S3], [S7 ch. 5, 15]. Transitive
closure is not expressible in relational algebra; recursion is what Datalog adds.

## Semantics: three views that agree for positive programs [S7 ch. 12]

1. **Model-theoretic**: the answer is the **minimal model**: the smallest set of
   facts containing the EDB and closed under all rules.
2. **Fixpoint**: the **immediate consequence operator**
   $T_P(I) = \{ H\theta \mid (H \leftarrow B_1..B_n) \in P,\ B_i\theta \in I \ \forall i\}$
   is monotone; the answer is its **least fixpoint** containing the EDB,
   reached by $I_0 = \text{EDB},\ I_{k+1} = I_k \cup T_P(I_k)$.
3. **Proof-theoretic**: the facts derivable by finitely many rule applications.

Termination: no function symbols, so only constants of the input occur and
$I_k$ is bounded by $|\text{adom}|^{\text{max arity}}$: polynomial in the data.

## Naive vs semi-naive evaluation

**Naive** ("INFER" in [S3]): recompute $T_P$ on everything each round until nothing changes.

**Semi-naive** [S7 13.1]: in round $k+1$ only instantiations using at least one
fact that was **new in round $k$** can produce anything new. For a rule with
recursive body atoms $R_1, \ldots, R_m$ evaluate $m$ delta versions, the $i$-th
reading $\Delta R_i$ in position $i$:

$$\Delta p^{(k+1)} = \Big(\bigcup_{i} \text{body with } R_i := \Delta R_i^{(k)}\Big) \setminus p^{(k)}.$$

For linear rules this is one delta version per rule: exactly what SQL's working
table does (note 03).

### Worked example: ancestors [`datalog.ANCESTOR`]

```
parent(alice, carol). parent(bob, carol). parent(eve, alice).
parent(dave, bob).    parent(frank, eve).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

| round | new `ancestor` facts |
|---|---|
| 1 | (alice,carol) (bob,carol) (eve,alice) (dave,bob) (frank,eve) |
| 2 | (eve,carol) (dave,carol) (frank,alice) |
| 3 | (frank,carol) |
| 4 | none: fixpoint |

9 facts. Work (successful rule instantiations): naive **31**, semi-naive **9**,
one per fact. On the 7-edge cyclic graph of note 03 transitive closure costs
115 vs 35 (`test_seminaive_does_less_work`).

**Nonlinear** `path(X,Y) :- path(X,Z), path(Z,Y).` doubles the covered path
length each round: a 16-edge chain needs 6 rounds instead of 17
(`test_nonlinear_needs_fewer_rounds_on_a_chain`), but each round joins two big
relations. SQL cannot express it (linear recursion only, note 03).

## Negation and stratification [S7 15.2]

`not p(X)` is **non-monotone**: adding facts can remove answers, so $T_P$ is no
longer monotone and a least fixpoint need not exist. Stratified semantics:

- **Dependency graph**: node per predicate; edge $q \to p$ if $q$ occurs in the body
  of a rule with head $p$; the edge is **negative** if $q$ occurs negated.
- The program is **stratified** iff no cycle contains a negative edge.
- **Strata**: numbers $s(p)$ with $s(p) \ge s(q)$ for positive and $s(p) > s(q)$
  for negative edges. Evaluate stratum 0 to its fixpoint, then stratum 1 (all
  predicates it negates are now complete), and so on. Every stratification gives
  the same result.

### Worked example

```
u(X, Y) :- r(X, Z), r(Z, Y).
v(X, Y) :- s(X, Z), s(Z, Y), not u(X, Y).
w(X, Y) :- u(X, Y), not v(X, Y).
```

Negative edges $u \to v$, $v \to w$; no cycles. Strata: {u} (with EDB r, s),
{v}, {w} (`test_stratification_example`).

Not stratified: `p(X) :- q(X), not r(X).  r(X) :- q(X), not p(X).` (cycle
p -> r -> p through negation), and the game rule `win(X) :- move(X, Y), not win(Y).`
(negative self-loop). `datalog.stratify` raises for both.

Unreachable pairs (stratified, [`datalog.STRATIFIED`]):

```
reach(X, Y) :- edge(X, Y).
reach(X, Y) :- edge(X, Z), reach(Z, Y).
unreachable(X, Y) :- node(X), node(Y), X != Y, not reach(X, Y).
```

`node(X), node(Y)` makes the rule safe: `not reach(X, Y)` alone binds nothing.

## Pitfalls

- A variable only in a negated atom or a comparison: unsafe (`big(X) :- X > 3.`).
- Stratification is about the **predicate** graph, not about the data.
- Semi-naive must still join the delta with the **full** other relations.
- Naive and semi-naive need the same number of rounds; semi-naive saves work per round.
- Datalog is set-based: duplicate derivations never create duplicate facts (unlike `UNION ALL`).

## Exam-style questions

1. *Is `p(X) :- q(X, Y), not r(Y, Z).` safe?* No: `Z` appears only under negation.
2. *Program `a :- not b.  b :- not c.  c :- d.` Stratified? Strata?* Yes: $s(c) = 0$ (with d), $s(b) = 1$, $s(a) = 2$.
3. *Edges a->b, b->c, c->d. Semi-naive TC with the linear rule: new facts per round?* 3, 2, 1, then 0.
4. *Why do naive and semi-naive give the same result?* A fact derivable in round $k+1$ but not in round $k$ needs at least one body fact that was new in round $k$; semi-naive enumerates exactly those instantiations (plus harmless repeats).
5. *Translate `anc(X,Y) :- par(X,Y). anc(X,Y) :- par(X,Z), anc(Z,Y).` to SQL.* `WITH RECURSIVE anc(x, y) AS (SELECT child, parent FROM par UNION SELECT p.child, a.y FROM par p JOIN anc a ON p.parent = a.x) SELECT * FROM anc;` (with `par(X, Y)` read as X's parent is Y).

## Code

- `datalog.parse`, `datalog.check_safety`, `datalog.stratify`, `datalog.evaluate` (`method="naive"` or `"seminaive"`, returns `Stats` with rounds, derivations and the per-round trace), `datalog.fire` (one rule, optional delta position).
- Tests compare transitive closure and same generation with `recursive_cte` (SQLite) for both methods and for the nonlinear rule.
