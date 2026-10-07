# 02 The relational model and its formal foundations

> **Sourcing.** Codd 1970 [S9] for the model and its motivation; [S6] ch. 2
> for keys and constraints; [S10] ch. 3 for the formal set-up; NULL behaviour
> from [S21] (nulls.html) and the tests in `src/py/test_sql_lab.py`.

## Definitions

Let $D_1, \dots, D_n$ be sets (domains). A **relation** on them is a subset
$r \subseteq D_1 \times \dots \times D_n$ [S9]; $n$ is the **degree** (arity),
$|r|$ the **cardinality**. Attaching names:

| term | meaning |
|---|---|
| attribute | a name $A_i$ with domain $\mathrm{dom}(A_i)$; values are **atomic** (1NF) [S6] |
| relation schema | $R(A_1, \dots, A_n)$; write $\mathrm{attr}(R)$ for the attribute set |
| tuple | a function $t : \mathrm{attr}(R) \to \bigcup_i \mathrm{dom}(A_i)$ with $t(A_i) \in \mathrm{dom}(A_i)$; $t[X]$ is its restriction to $X \subseteq \mathrm{attr}(R)$ |
| relation (instance) | a **finite set** of tuples over $R$ |
| database schema / instance | a set of relation schemas / one instance per schema |

Consequences of "a relation is a set" that Codd lists explicitly [S9]: the
**order of rows is immaterial** and **all rows are distinct**; with named
attributes the order of columns is immaterial too. SQL tables break two of
these (duplicates, and `SELECT *` column order): note 06.

Codd's motivation was **data independence**: application programs must not
depend on how data is stored (order, indexes, access paths) [S9]. The
algebra and SQL are therefore defined on relations, never on pages or pointers;
notes 07-10 are the "how it is stored" half that the model hides.

### Keys and integrity constraints

For $K \subseteq \mathrm{attr}(R)$ and every legal instance $r$ of $R$:

$$K \text{ is a superkey} \iff \forall t_1, t_2 \in r:\ t_1[K] = t_2[K] \Rightarrow t_1 = t_2.$$

| constraint | statement |
|---|---|
| superkey | as above (e.g. $\{ID\}$ and $\{ID, name\}$ for `instructor`) [S6] |
| candidate key | a superkey none of whose proper subsets is a superkey (minimal) [S6] |
| primary key | the candidate key chosen as the main identifier; in SQL also NOT NULL (**entity integrity**) |
| foreign key | $R.X$ references $S.Y$ ($Y$ a key of $S$): for every $t \in r$, $t[X]$ is NULL or appears as $u[Y]$ for some $u \in s$ (**referential integrity**) [S6] |
| domain / CHECK | values lie in the domain; per-tuple predicates (`grade BETWEEN 1 AND 5`) |

Keys are a property of the **schema** (all legal instances), not of one
instance: a column that happens to be unique in today's data is not a key.

Counting superkeys: if $R$ has $n$ attributes and a single candidate key $K$
with $|K| = k$, the superkeys are exactly the supersets of $K$, so there are
$2^{n-k}$ of them.

### NULL

`NULL` marks a missing value (unknown or inapplicable). It is **not** part of
Codd's 1970 model [S9]; SQL adds it with a **three-valued logic** where a
comparison with NULL yields UNKNOWN (note 06). [S6] ch. 2 describes NULL as "a
member of every domain". Engines agree on the core but not on every corner: NULLs
are distinct in a UNIQUE column but not distinct for `SELECT DISTINCT` and
`UNION` in every engine SQLite surveyed [S21] (nulls.html).

## Worked example: keys of the lab schema

`sql_lab.SCHEMA` defines

$$\mathit{exam}(\underline{sid}, \underline{cid}, \underline{attempt}, grade),\quad
\mathit{course}(\underline{cid}, title, ects, pid),\quad \dots$$

- $\{sid, cid, attempt\}$ is the primary key of `exam`: a student may sit the
  same course several times, so $\{sid, cid\}$ is **not** a key.
  $n = 4$, $k = 3$: superkeys $2^{4-3} = 2$, namely $\{sid,cid,attempt\}$ and
  all four attributes.
- `course` has two candidate keys: $\{cid\}$ (primary) and $\{title\}$
  (declared `UNIQUE`). Superkeys: supersets of $\{cid\}$ ($2^3 = 8$) plus
  supersets of $\{title\}$ ($8$) minus supersets of both ($2^2 = 4$), i.e. 12.
- `exam.sid` references `student.sid`, `exam.cid` references `course.cid`.
  `course.pid` references `professor` and may be NULL (a course without a
  lecturer yet): a NULL foreign key satisfies referential integrity.
- `professor.boss` references `professor` itself (a recursive foreign key).

What the constraints buy is tested in `test_sql_lab.py::test_dml_demo`: a
`CHECK` violation, a dangling foreign key, a duplicate primary key and a NULL
name are all rejected; deleting a student cascades to its exams.

## Pitfalls

- "Relation" (a set of tuples) is not "relationship" (an ER construct).
- A key is minimal; a superkey need not be. "The primary key is the smallest
  key" is false: any candidate key may be chosen.
- Referential integrity says nothing about the referencing column being NOT
  NULL; add that separately if participation is total (note 03).
- Uniqueness in an instance does not prove a key; one counterexample row
  disproves it.
- NULL is not a value that equals itself: `NULL = NULL` is UNKNOWN
  (`test_sql_lab.py::test_three_valued_logic`).

## Exam-style questions

1. *True or false: the rows of a relation have a defined order.* **False** [S9].
2. *$R(A,B,C,D)$ has the single candidate key $\{A,B\}$. How many superkeys?*
   **4** ($2^{4-2}$): $AB, ABC, ABD, ABCD$.
3. *True or false: a foreign-key column may contain NULL even though the
   referenced column is a primary key.* **True**; NULL foreign keys satisfy
   referential integrity unless the column is declared NOT NULL.
4. *An instance of $R(A,B)$ has no two rows with equal $A$. Is $A$ a key?*
   **Not necessarily**: keys constrain all legal instances.
5. *Which of Codd's properties does a SQL table without a primary key violate?*
   **Distinctness of rows** (bags allow duplicates).

## Code

`src/py/sql_lab.py`: `sql_lab.SCHEMA` (keys, foreign keys, CHECK, NOT NULL,
UNIQUE), `sql_lab.dml_demo` (constraint violations). `src/py/relalg.py`:
`relalg.Relation` (set semantics; equality ignores column order).
