# 02 Non-recursive CTEs and window functions

> **Sourcing.** PostgreSQL 18 manual 7.8 WITH queries [S9] and 9.22 window
> functions [S11] (both vendored), SQLite window functions [S14]; CTE usage as
> taught in 2026 per [S3]. Window functions are not in the reported 2026 block-1
> topic list [S2], [S3]: they are here because recursive-query answers often need
> them (shortest path with `ROW_NUMBER`, note 03) and because 184.686 may not
> cover them. Every query and result below is executed by `window_functions.py`.

## Common Table Expressions

A **CTE** is a named subquery defined in a `WITH` clause and visible to the rest
of the statement:

```sql
WITH best AS (SELECT course, MAX(points) AS top FROM exam GROUP BY course),
     who  AS (SELECT e.* FROM exam e JOIN best b
              ON b.course = e.course AND b.top = e.points)   -- may use `best`
SELECT * FROM who ORDER BY course;
```

- Several CTEs are separated by commas; each may use the ones before it.
- **Materialisation** [S9 7.8.3]: a CTE is normally evaluated once per statement.
  A non-recursive CTE without side effects (a `SELECT` with no volatile functions)
  that the main query references **once** is folded into it, so the optimiser can
  push predicates inside; referenced twice it is materialised. Override with
  `AS MATERIALIZED` / `AS NOT MATERIALIZED`.
- **Data-modifying CTEs** (PostgreSQL): `WITH moved AS (DELETE FROM a WHERE ... RETURNING *) INSERT INTO b SELECT * FROM moved;`
  All sub-statements see the same snapshot; without `RETURNING` the deleted rows are gone.
- A CTE vs a **view**: a view is stored in the catalog and reusable across
  statements; a CTE lives for one statement. A **temporary table** lives for the
  session and can be indexed.

### Universal quantification ("for all") with NOT EXISTS

"Students enrolled in **all** db-group courses" = students for whom **no** such
course is missing:

```sql
WITH req AS (SELECT course FROM courses WHERE grp = 'db'),
     missing AS (SELECT s.id, r.course FROM students s CROSS JOIN req r
                 WHERE NOT EXISTS (SELECT 1 FROM enrolled e
                                   WHERE e.id = s.id AND e.course = r.course))
SELECT s.id FROM students s
WHERE NOT EXISTS (SELECT 1 FROM missing m WHERE m.id = s.id);
```

Relational algebra: $\pi_{id}(S) - \pi_{id}\big((\pi_{id}(S) \times R) - E\big)$,
which is division $E \div R$ when every student appears in $E$.

## Window functions

A **window function** returns one value *per row*, computed over a set of rows
related to it, without collapsing rows as `GROUP BY` does:

$$f(\ldots)\ \texttt{OVER}\ (\texttt{PARTITION BY}\ p\ \ \texttt{ORDER BY}\ o\ \ \textit{frame})$$

- **Partition**: rows with equal `p`; computed independently.
- **Peers**: rows of a partition with equal `o` values.
- **Frame**: the rows `f` sees. `ROWS` counts rows, `RANGE` works on `o` values
  (peers enter together), `GROUPS` counts peer groups.
- **Default frame with `ORDER BY`**: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`,
  i.e. up to and **including all peers** of the current row. Without `ORDER BY`:
  the whole partition [S14], [S11].
- Ranking: `ROW_NUMBER` (1,2,3,4), `RANK` (ties share, then a gap: 1,2,2,4),
  `DENSE_RANK` (no gap: 1,2,2,3), `NTILE(k)` (bucket number), `PERCENT_RANK`, `CUME_DIST`.
  Offsets: `LAG(x, k, default)`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`.
  Any aggregate (`SUM`, `AVG`, `COUNT`) can be used with `OVER`.
- Evaluation order: `FROM/WHERE/GROUP BY/HAVING`, then windows, then `ORDER BY/LIMIT`.
  So a window value cannot be filtered in `WHERE` of the same query: wrap it in a subquery.

### Worked example (table `exam`, `window_functions.EXPECTED["ranks"]`)

```sql
SELECT course, student, points,
       ROW_NUMBER() OVER (PARTITION BY course ORDER BY points DESC, student) AS rn,
       RANK()       OVER (PARTITION BY course ORDER BY points DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY course ORDER BY points DESC) AS drnk
FROM exam ORDER BY course, rn;
```

| course | student | points | rn | rnk | drnk |
|---|---|---|---|---|---|
| db | ann | 90 | 1 | 1 | 1 |
| db | bob | 85 | 2 | 2 | 2 |
| db | cid | 85 | 3 | 2 | 2 |
| db | dan | 70 | 4 | 4 | 3 |
| os | bob | 75 | 1 | 1 | 1 |
| os | eve | 75 | 2 | 1 | 1 |
| os | ann | 60 | 3 | 3 | 2 |
| os | fay | 50 | 4 | 4 | 3 |

Top-2 per course: `WHERE rnk <= 2` gives db: ann, bob, cid (3 rows, tie kept);
`WHERE rn <= 2` gives exactly 2 per course.

### RANGE vs ROWS (table `txn`, two rows on day 2)

```sql
SELECT id, day, amount,
       SUM(amount) OVER (ORDER BY day)                            AS range_sum,
       SUM(amount) OVER (ORDER BY day, id ROWS UNBOUNDED PRECEDING) AS rows_sum
FROM txn ORDER BY id;
```

| id | day | amount | range_sum | rows_sum |
|---|---|---|---|---|
| 1 | 1 | 10 | 10 | 10 |
| 2 | 2 | 20 | **35** | **30** |
| 3 | 2 | 5 | 35 | 35 |
| 4 | 3 | 30 | 65 | 65 |
| 5 | 4 | 0 | 65 | 65 |
| 6 | 5 | 15 | 80 | 80 |

Row 2's default frame already contains its peer row 3. Moving average of the
last three rows: `AVG(amount) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
gives 10, 15, 11.667, 18.333, 11.667, 15.

### The LAST_VALUE trap

`LAST_VALUE(points) OVER (PARTITION BY course ORDER BY points DESC)` returns
**the row's own points** (the frame ends at the last peer of the current row),
not the partition minimum. Add
`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` to get 70 (db) and 50 (os).

## Pitfalls

- Default frame includes peers: running totals jump on ties.
- `ROW_NUMBER` over ties is nondeterministic unless `ORDER BY` is made unique.
- Window results cannot be used in `WHERE`/`GROUP BY` of the same `SELECT`.
- `LAG` returns NULL on the first row unless a default is given.
- A materialised CTE is a temporary copy without indexes: `WITH w AS (SELECT * FROM big) SELECT ... FROM w a JOIN w b ...` cannot use `big`'s index; `NOT MATERIALIZED` can, at the price of computing `w` twice [S9 7.8.3].

## Exam-style questions

1. *Points 90, 85, 85, 70 in one partition, ordered descending: RANK and DENSE_RANK of 70?* 4 and 3.
2. *Values by day (1:10), (2:20), (2:5): `SUM(x) OVER (ORDER BY day)` on the first day-2 row?* 35, because the default `RANGE` frame includes the peer.
3. *Why does `SELECT ..., RANK() OVER (...) AS r FROM t WHERE r <= 3` fail?* `WHERE` is evaluated before windows and cannot see `r`; use a subquery or CTE.
4. *Express "customers who bought every product of category X" in SQL.* Double `NOT EXISTS` (or the `missing` CTE above): no product of X for which no purchase exists.
5. *A CTE is referenced twice in PostgreSQL 18. Is it inlined?* No: by default it is materialised once; only single-reference, side-effect-free, non-recursive CTEs are inlined [S9 7.8.3].

## Code

- `window_functions.QUERIES` and `window_functions.EXPECTED`: all queries above with hand-computed results; `test_window_functions.py` re-derives them with pandas (`rank(method="min"/"dense")`, `cumsum`, `rolling`).
