# 06 SQL: queries, definition, manipulation

> **Sourcing.** [S6] ch. 3-4 (query semantics, NULL and three-valued logic,
> aggregation, subqueries, views, constraints); [S21] nulls.html (engines
> disagree on NULL corners); [S22] functions-comparison and queries-order
> (PostgreSQL behaviour). Every query result quoted here is asserted in
> `src/py/test_sql_lab.py` against sqlite 3.53.1. Which DBMS the 184.686 SQL
> exam uses is **not public** (note 00).

## Semantics of one query block

```sql
SELECT [DISTINCT] e1, ..., ek      -- 5. project (bag!), compute expressions
FROM   r1, ..., rm                 -- 1. Cartesian product of the inputs
WHERE  p                           -- 2. keep rows where p is TRUE (not UNKNOWN)
GROUP  BY g1, ..., gj              -- 3. partition into groups
HAVING q                           -- 4. keep groups where q is TRUE
ORDER  BY ...                      -- 6. sort (only here is order defined)
```

In algebra with bag semantics:
$\pi^{\text{bag}}_{e}\big(\sigma_q(\gamma_{g;\,\text{aggs}}(\sigma_p(r_1 \times \dots \times r_m)))\big)$.
Consequences: a `SELECT` alias is not visible in `WHERE`; aggregates cannot
appear in `WHERE` (it runs before grouping) [S6]; with `GROUP BY`, every
non-aggregated `SELECT` column must be a grouping column [S6].

**Bags.** Tables and results may contain duplicates. `DISTINCT`, `UNION`,
`INTERSECT`, `EXCEPT` remove them; `UNION ALL` keeps them (in the lab database
19 vs 6 rows, `test_sql_lab.py::test_union_vs_union_all`).

### Joins

| form | result |
|---|---|
| `r JOIN s ON c` | $\sigma_c(r \times s)$ |
| `r NATURAL JOIN s`, `JOIN s USING (a)` | equate the common/listed columns, keep one copy |
| `r LEFT [OUTER] JOIN s ON c` | inner join plus unmatched `r` rows padded with NULL |
| `RIGHT`, `FULL` | symmetric; `FULL` pads both sides |
| `r CROSS JOIN s` | $r \times s$ |

A condition on the **right** table of a left join belongs in `ON`; in `WHERE` it
discards the padded rows and silently turns the outer join into an inner join.

### NULL and three-valued logic

Any comparison with NULL is UNKNOWN [S6]. The connectives ([S6] ch. 3):

| $p$ | $q$ | $p \land q$ | $p \lor q$ | $\lnot p$ |
|---|---|---|---|---|
| T | U | U | T | F |
| F | U | F | U | T |
| U | U | U | U | U |

`WHERE` and `HAVING` keep only TRUE. Tested one-liners (`test_three_valued_logic`):
`NULL = NULL` is NULL; `NULL IS NULL` is 1; `2 IN (1, NULL)` is NULL; hence
`2 NOT IN (1, NULL)` is NULL, never TRUE. `x IS DISTINCT FROM y` is the
NULL-safe inequality (`NULL IS DISTINCT FROM NULL` is false) [S22].

Aggregates **ignore NULLs**, except `COUNT(*)`, which counts rows; over an
empty input `COUNT` is 0 and `SUM`, `AVG`, `MAX` are NULL. `GROUP BY` puts all
NULLs into **one** group; `DISTINCT` and `UNION` treat NULLs as equal while a
`UNIQUE` column admits several NULLs [S21].

### Nested queries

| form | meaning |
|---|---|
| `x IN (Q)` | $\exists y \in Q: x = y$ (3VL: UNKNOWN if no match but $Q$ has a NULL) |
| `EXISTS (Q)` | $Q \ne \emptyset$; never UNKNOWN |
| `x > ALL (Q)` | $\forall y \in Q: x > y$; TRUE if $Q = \emptyset$ |
| `x > ANY (Q)` / `SOME` | $\exists y \in Q: x > y$ |
| scalar `(Q)` | one value; NULL if $Q$ is empty, error if $Q$ has more rows |

A subquery is **correlated** if it refers to the outer row; it is (logically)
re-evaluated per outer row. `NOT EXISTS` with correlation is the SQL form of
$\forall$ and of division (note 05).

### DDL and DML

```sql
CREATE TABLE exam (
  sid INTEGER REFERENCES student(sid) ON DELETE CASCADE,
  cid TEXT REFERENCES course(cid),
  attempt INTEGER NOT NULL CHECK (attempt >= 1),
  grade INTEGER CHECK (grade BETWEEN 1 AND 5),       -- NULL passes a CHECK
  PRIMARY KEY (sid, cid, attempt));
INSERT INTO exam VALUES (101, 'DM', 1, 1);
UPDATE professor SET salary = salary * 11 / 10 WHERE pid IN (SELECT pid FROM course WHERE ects = 6);
DELETE FROM student WHERE sid = 105;                 -- cascades to exam
```

Referential actions: `ON DELETE/UPDATE {NO ACTION | RESTRICT | CASCADE | SET NULL | SET DEFAULT}`.
A `CHECK` rejects only FALSE, so a NULL passes. **Views** are stored queries,
recomputed on use (a new exam row shows up in the view at once,
`test_view_is_not_materialised`); materialised views store the result and must
be maintained [S6]. Most systems allow updates only through simple views: one
base table, plain columns, no aggregates, `DISTINCT`, `GROUP BY` or `HAVING` [S6].
Recursive queries: `WITH RECURSIVE` (E9 below).

## The lab database

`sql_lab.SCHEMA`: `professor(pid, name, dept, salary, boss)`,
`student(sid, name, semester, program)`, `course(cid, title, ects, pid)`,
`prereq(cid, pre)`, `exam(sid, cid, attempt, grade)`; grade 5 = fail, NULL =
not graded yet. Sixteen exercises, `sql_lab.EXERCISES`, full text and expected
rows in note 13. The ones that teach something:

| id | point | result |
|---|---|---|
| E2 | `LEFT JOIN` keeps the course without lecturer | `('SEM', 'Seminar', None)` among 6 rows |
| E4 | `COUNT(p.cid)` counts 0 for padded rows; `COUNT(*)` would say 1 | Eve 0, Fay 0 |
| E5 | `AVG` over graded attempts only; `HAVING COUNT(grade) >= 2` | DBS avg 3.0 over 4 graded of 5 rows |
| E6 | division by double `NOT EXISTS` | Ada, Cyd |
| E7a/E7b | `NOT IN` against a subquery containing NULL returns **nothing**; `NOT EXISTS` returns everyone | 0 vs 6 rows |
| E8 | self-join on `boss` | Mayr |
| E9 | transitive prerequisites by `WITH RECURSIVE` | ALG, DBS, DM |
| E10 | `RANK()` window: ties share a rank, the next rank skips | Eve 5, Fay 5 |
| E12 | `> ALL` rewritten as `> (SELECT MAX ...)` in sqlite | Hofer |
| E15 | `COUNT(*)` 13, `COUNT(grade)` 12, `SUM/COUNT(*)` integer division 2 | |
| E16 | `EXCEPT` for "failed and never passed" | Bob DBS, Eve DM |

### Where sqlite and PostgreSQL differ (tested or documented)

| point | sqlite (tested) | PostgreSQL |
|---|---|---|
| `x > ALL (subquery)` | syntax error | supported |
| foreign keys | **off** unless `PRAGMA foreign_keys = ON` (`test_foreign_keys_off_by_default_in_sqlite`) | always on |
| NULL in `ORDER BY ... ASC` | first | last: NULL sorts as larger than any value by default [S22] |
| `5 / 2` on integers | 2 | 2 (integer division too; use `5.0 / 2`) (unverified here) |
| primary-key violation message | "UNIQUE constraint failed" | "duplicate key value violates unique constraint" (unverified here) |

## Pitfalls

- `NOT IN (subquery)` where the subquery can yield NULL: always empty (E7a).
  Use `NOT EXISTS` or filter `IS NOT NULL`.
- `> ALL` is not `> MAX` on an empty subquery: `ALL` over $\emptyset$ is TRUE,
  `> NULL` is UNKNOWN (`test_all_vs_max_on_empty_subquery`).
- `COUNT(col)` vs `COUNT(*)` after an outer join (E4).
- `WHERE right.col = ...` after a `LEFT JOIN` makes it an inner join.
- `= NULL` instead of `IS NULL`.
- `SELECT name, COUNT(*) ... GROUP BY sid`: `name` is not a grouping column;
  sqlite accepts it anyway; the SQL standard rejects it unless `name` is
  functionally dependent on the grouping columns (PostgreSQL behaviour not
  checked in this pass).
- Forgetting `DISTINCT` when joining a 1:N path (E3 would list Ada twice
  without it if she had passed DBS twice).

## Exam-style questions

1. *True or false: `SELECT * FROM t WHERE a = NULL` returns the rows with NULL in `a`.* **False**: none.
2. *`t(a)` contains 1, 2, NULL. Value of `SELECT COUNT(*), COUNT(a), AVG(a) FROM t`?* **3, 2, 1.5**
   (`test_sql_lab.py::test_exam_question_count_avg`).
3. *True or false: `x NOT IN (SELECT y FROM s)` and `NOT EXISTS (SELECT * FROM s WHERE s.y = x)` are equivalent.*
   **False** when `s.y` or `x` can be NULL (E7a vs E7b).
4. *A `CHECK (grade BETWEEN 1 AND 5)` column receives NULL. Accepted?* **Yes**: the check is UNKNOWN, not FALSE.
5. *Which clause filters groups: `WHERE` or `HAVING`?* **`HAVING`**; `WHERE` filters rows before grouping [S6].

## Code

`src/py/sql_lab.py`: `sql_lab.SCHEMA`, `sql_lab.DATA`, `sql_lab.connect`,
`sql_lab.EXERCISES`, `sql_lab.VIEW`, `sql_lab.dml_demo` (E13: UPDATE with
subquery, cascading DELETE, CHECK/FK/PK/NOT NULL violations, SET NULL,
RESTRICT), `sql_lab.query_plan`, `sql_lab.index_demo` (note 08).
`src/py/test_sql_lab.py`: every exercise plus the NULL and dialect tests named above.
