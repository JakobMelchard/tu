# 10 Query optimisation

> **Sourcing.** [S6] ch. 16 (equivalence rules, statistics, size estimation,
> number of join orders, dynamic programming, left-deep trees); Selinger et al.
> [S14] (selectivity factors of Table 1, interesting orders, DP, deferring
> Cartesian products); [S16] for the optimiser's place in a DBMS. The cost model
> $C_{out}$ is our simplification; all numbers come from `python src/py/optimizer.py`.

## From SQL to a plan

SQL text is parsed into a relational-algebra tree; **logical optimisation**
rewrites it with equivalence rules; **physical optimisation** picks access
paths (scan or index, note 08), join algorithms (note 09) and a join order by
estimated cost [S6]. The optimiser never sees data, only **statistics**: $n_r$
tuples, $b_r$ pages, $V(A, r)$ distinct values, min/max, histograms [S6].

## Equivalence rules (the ones exams use) [S6]

1. $\sigma_{\theta_1 \land \theta_2}(E) = \sigma_{\theta_1}(\sigma_{\theta_2}(E))$ (cascade; so selections commute).
2. $\pi_{L_1}(\pi_{L_2}(E)) = \pi_{L_1}(E)$ for $L_1 \subseteq L_2$.
3. $\sigma_\theta(E_1 \times E_2) = E_1 \bowtie_\theta E_2$.
4. $E_1 \bowtie E_2 = E_2 \bowtie E_1$; $(E_1 \bowtie E_2) \bowtie E_3 = E_1 \bowtie (E_2 \bowtie E_3)$ (natural/theta joins with care about which attributes a condition uses).
5. $\sigma_{\theta}(E_1 \bowtie E_2) = \sigma_\theta(E_1) \bowtie E_2$ if $\theta$ mentions only $E_1$'s attributes (**selection pushdown**).
6. $\pi_L(E_1 \bowtie_\theta E_2) = \pi_{L_1}(E_1) \bowtie_\theta \pi_{L_2}(E_2)$ where $L_i$ = the attributes of $L$ and $\theta$ in $E_i$ (**projection pushdown**; project the join columns away only after the join).
7. $\sigma_\theta(E_1 \cup E_2) = \sigma_\theta E_1 \cup \sigma_\theta E_2$, same for $-$ and $\cap$; $\pi$ distributes over $\cup$ but not over $-$ (note 05).

Heuristics that follow: push selections and projections as far down as they go,
replace $\sigma(\times)$ by joins, join the most restrictive pairs first, avoid
Cartesian products.

## Estimation

| expression | estimate | source |
|---|---|---|
| $\sigma_{A = c}(r)$ | $n_r / V(A, r)$; 1 if $A$ is a key | [S6] |
| $\sigma_{A > c}(r)$ | $n_r \cdot \frac{\max - c}{\max - \min}$ (uniform) | [S6], [S14] |
| no statistics | $A = c$: $1/10$; open range: $1/3$; `BETWEEN`: $1/4$; `IN` list: $k \cdot$ (equality factor), at most $1/2$ | [S14] Table 1 |
| $\theta_1 \land \theta_2$ | $s_1 s_2$ (independence) | [S6] |
| $\theta_1 \lor \theta_2$ | $1 - (1 - s_1)(1 - s_2)$ | [S6] |
| $\lnot\theta$ | $1 - s$ | [S6] |
| $r \bowtie_A s$ | $\dfrac{n_r\, n_s}{\max(V(A,r), V(A,s))}$ | [S6] |
| $r \bowtie s$, $A$ a foreign key in $s$ referencing $r$ | exactly $n_s$ | [S6] |

The join formula follows from containment of value sets: every one of the
$\min(V)$ values on the smaller side finds partners; each value carries
$n_r/V(A,r)$ and $n_s/V(A,s)$ tuples, so
$\min(V) \cdot \frac{n_r}{V_r}\frac{n_s}{V_s} = \frac{n_r n_s}{\max(V_r, V_s)}$.
[S6]'s example: `student` $\bowtie$ `takes`, $5000 \cdot 10{,}000 / \max(5000, 2500) = 10{,}000$,
equal to the foreign-key answer. `test_optimizer.py` checks the foreign-key case
exactly and a uniform random case within 10 % against sqlite counts.

Selinger's comment on the defaults: 1/3 has "no significance ... other than"
being less selective than equality and below 1/2 [S14].

## Plan space and dynamic programming

Number of join trees over $n$ relations [S6]:

$$\text{left-deep: } n!,\qquad \text{bushy: } \frac{(2(n-1))!}{(n-1)!}$$

$n = 2..6$: left-deep 2, 6, 24, 120, 720; bushy 2, 12, 120, 1680, 30240
(`optimizer.count_bushy`, checked by enumeration for $n \le 5$).

**Dynamic programming** (System R [S14], [S6]): the best plan for a set $S$ of
relations is the cheapest combination of best plans for a split $S = L \cup R$:

$$\mathrm{best}(S) = \min_{L \subset S} \big[\mathrm{best}(L) + \mathrm{best}(S \setminus L) + \mathrm{cost}(S)\big].$$

Left-deep restricts $|S \setminus L| = 1$: $O(n\,2^n)$ work (derived). Bushy:
$O(3^n)$ [S6]. System R additionally keeps the best plan per **interesting
order** (a sort order useful to a later merge join, `GROUP BY` or `ORDER BY`),
and considers a Cartesian product only when no join predicate connects the next
relation [S14]. Principle of optimality: a subplan of an optimal plan is optimal
for its subset, provided the cost of combining does not depend on how the
parts were built (it does for sort orders: hence interesting orders).

**Cost model used here:** $C_{out}$ = the sum of the estimated sizes of all
intermediate results (the final result is the same for every plan and is not
counted). It ignores access paths on purpose, to isolate the effect of order.

## Worked example (`optimizer.example`)

Chain $R - S - T - U$; $|R| = 1000$ with a filter of selectivity 0.01 (10
tuples left), $|S| = 5000$, $|T| = 20{,}000$, $|U| = 100$ with a 0.01 filter (1 tuple).
$V$: $R.a = 100$, $S.a = 1000$, $S.b = 50$, $T.b = 5000$, $T.c = 200$, $U.c = 100$.

Intermediate sizes:
$|RS| = \frac{10 \cdot 5000}{1000} = 50$,
$|ST| = \frac{5000 \cdot 20000}{5000} = 20{,}000$,
$|TU| = \frac{20000 \cdot 1}{200} = 100$,
$|RST| = 200$, $|STU| = 100$, $|RSTU| = 1$.

| subset | best left-deep | $C_{out}$ | best bushy | $C_{out}$ |
|---|---|---|---|---|
| RS, ST, TU | the join | 50, 20000, 100 | same | same |
| RST | $(RS)T$ | $50 + 200 = 250$ | same | 250 |
| STU | $(TU)S$ | $100 + 100 = 200$ | same | 200 |
| RSTU | $((TU)S)R$ | **200** | $(RS)(TU)$ | **150** |

Naive order $((RS)T)U$ costs $50 + 200 = 250$. Bushy wins here because both ends
of the chain shrink independently. Allowing Cartesian products finds
$((R \times U) S) T$ with $C_{out} = 10 + 50 = 60$: a product of two tiny relations
is harmless, which is why "never a product" is a heuristic, not a law.
`test_optimizer.py` checks DP against exhaustive enumeration on 180 random
3-5 relation queries (chain, star, cycle; left-deep and bushy; with and without
products).

## Pitfalls

- Estimates assume uniformity and independence; correlated predicates
  (city = 'Wien' and zip = '1040') are badly underestimated.
- $\max(V)$ in the denominator, not $\min$.
- Counting orders: $n!$ is left-deep only; bushy trees are many more.
- Pushing a projection below a join must keep the join attributes.
- The cheapest plan for a subset is not always part of the cheapest plan overall
  when sort orders matter (interesting orders).

## Exam-style questions

1. *$n_r = 1000$, $n_s = 5000$, $V(A,r) = 100$, $V(A,s) = 1000$. Estimated $|r \bowtie_A s|$?* **5000**.
2. *No statistics, predicate `salary > 5000`: System R's selectivity?* **1/3** [S14].
3. *How many bushy join trees for 4 relations?* **120**; left-deep **24**.
4. *True or false: $\pi_A(E_1 - E_2) = \pi_A(E_1) - \pi_A(E_2)$ is a valid rewrite.* **False**.
5. *True or false: with independence, $s(\theta_1 \lor \theta_2) = s_1 + s_2$.* **False**: $s_1 + s_2 - s_1 s_2$.

## Code

`src/py/optimizer.py`: `optimizer.sel_eq`, `optimizer.sel_range`,
`optimizer.sel_and`, `optimizer.sel_or`, `optimizer.sel_not`,
`optimizer.SELINGER_DEFAULTS`, `optimizer.join_size`, `optimizer.Query`,
`optimizer.best_plan` (DP, left-deep or bushy, with or without products),
`optimizer.plan_cost`, `optimizer.brute_force`, `optimizer.all_trees`,
`optimizer.count_left_deep`, `optimizer.count_bushy`, `optimizer.example`.
