# 03 From ER diagrams to relational schemas

> **Sourcing.** Mapping rules and the two ISA methods of [S6] ch. 6; the
> single-table ISA variant is common practice and marked (unsourced). The
> worked example is `er.transform(er.university())`, loaded into sqlite by
> `src/py/test_er.py`.

## The rules

Notation: $\mathrm{key}(E)$ is the primary key of entity set $E$; underline = primary key.

| construct | relation(s) | constraints |
|---|---|---|
| strong entity $E(\underline{k}, a_1, \dots)$ | $E(\underline{k}, a_1, \dots)$; composite attributes flattened [S6] | PK $k$ |
| multivalued attribute $m$ of $E$ | $E\_m(\underline{\mathrm{key}(E), m})$ [S6] | FK to $E$, `ON DELETE CASCADE` |
| weak entity $W$, owner $O$, discriminator $d$ | $W(\underline{\mathrm{key}(O), d}, \dots)$; the identifying relationship needs **no** table of its own [S6] | FK to $O$, `ON DELETE CASCADE` |
| N:M relationship $R$ between $A$, $B$ (attributes $x$) | $R(\underline{\mathrm{key}(A), \mathrm{key}(B)}, x)$ [S6] | FKs to $A$ and $B$ |
| 1:N relationship ($A$ one, $B$ many) | add $\mathrm{key}(A)$ (and $R$'s attributes) to $B$'s relation [S6] | FK; NOT NULL iff $B$'s participation is total |
| 1:1 relationship | add the other key on either side, preferably the side with total participation [S6] | FK, **UNIQUE**, NOT NULL if total |
| n-ary relationship | own relation with all participants' keys | PK = keys of the "many" sides |
| ISA method 1 | superclass relation + one relation per subclass with $\mathrm{key}(\text{super})$ and local attributes [S6] | subclass PK is also FK to super |
| ISA method 2 | one relation per subclass with **all** inherited + local attributes [S6] | no super table (works if the specialisation is total) |
| ISA single table | one relation with every attribute + a type column; subclass attributes nullable (unsourced) | CHECKs tie attributes to the type |

Why these and not others:

- **1:N into the N side.** Each $b$ has at most one $a$, so $\mathrm{key}(A)$ is
  functionally determined by $\mathrm{key}(B)$ and fits in $B$'s row. Putting it
  on the one side would need a multivalued attribute. If $B$'s participation is
  partial the column is sometimes NULL; [S6] notes this and the alternative is a
  separate relation $R(\underline{\mathrm{key}(B)}, \mathrm{key}(A))$.
- **N:M needs its own relation.** Neither key determines the other; the pair is
  the key.
- **1:1 needs UNIQUE.** Without it the schema would allow 1:N.
- **Weak entity key.** The discriminator alone repeats across owners.

ISA trade-offs: method 1 answers "all persons" with one table and "all data of a
tutor" with a join; method 2 answers "all persons" with a union and stores an
overlapping entity twice (redundancy, [S6] slide "Method 2" drawback); the
single table needs no join but many NULLs.

## Worked example: the university of note 01

`python src/py/er.py` prints (asterisk = primary key column):

```
Professor(pid*, name, rank, office_rid)
Student(sid*, name, semester)
Student_email(sid*, email*)
Course(cid*, title, ects, teaches_pid)
Room(rid*, seats)
Section(course_cid*, sno*, weekday, leads_sid)
Tutor(sid*, hours)
attends(student_sid*, course_cid*, grade)
```

Line by line:

- `office` (1:1, Professor total) became `Professor.office_rid NOT NULL UNIQUE`
  referencing `Room`. Room is partial, so putting the key on the Room side
  would force NULLs.
- `teaches` (1:N, Course total) became `Course.teaches_pid NOT NULL`, and the
  DDL uses `ON DELETE RESTRICT`: a professor who still teaches cannot vanish.
- `leads` (1:N, Section partial) became `Section.leads_sid`, nullable, with
  `ON DELETE SET NULL`.
- `attends` (N:M, attribute `grade`) became its own relation with key
  $(\mathit{student\_sid}, \mathit{course\_cid})$.
- `Section` (weak) got key $(\mathit{course\_cid}, \mathit{sno})$ and
  `ON DELETE CASCADE` to `Course`; no `sec_course` table [S6].
- `Tutor` (ISA, method 1) has key `sid`, which is also a foreign key to `Student`.

Six entity sets, four relationships and one multivalued attribute became eight
relations: `teaches`, `office` and `leads` were absorbed as foreign keys. The
generated DDL for one of them (`er.ddl`, column lines joined):

```sql
CREATE TABLE Professor (
  pid, name, rank,
  office_rid NOT NULL,
  PRIMARY KEY (pid),
  UNIQUE (office_rid),
  FOREIGN KEY (office_rid) REFERENCES Room (rid) ON DELETE RESTRICT
);
```

What the tests check against sqlite (`test_er.py`): a course without lecturer
is rejected; a second professor in room 1 is rejected; a second `attends` row
for the same pair is rejected; a `Tutor` that is not a `Student` is rejected;
deleting a course deletes its sections; deleting a tutor's student row cascades
to `Tutor` and nulls `Section.leads_sid`.

### What the relational schema cannot express

Some ER constraints survive only as application logic or triggers:

- total participation of the **one** side of 1:N (every professor teaches at
  least one course): a NOT NULL column cannot say "at least one row elsewhere";
- disjointness and totality of a specialisation under method 1;
- $(\min,\max)$ bounds other than 0, 1, $*$ (e.g. at most 3 courses).

## Pitfalls

- Putting the foreign key of a 1:N relationship on the one side.
- Forgetting `UNIQUE` for 1:1, or NOT NULL for total participation on the many side.
- Giving a weak entity's table only the discriminator as key.
- Creating a table for the identifying relationship of a weak entity (redundant [S6]).
- Using a reserved word as a table name: `Group` failed in sqlite while this
  note was written (renamed `Section`).

## Exam-style questions

1. *Student N:M Course with attribute `grade`. Minimum number of relations?*
   **3** (`Student`, `Course`, `attends` with the grade).
2. *True or false: a 1:N relationship with partial participation on the N side
   can be mapped into the N side's relation.* **True**, at the price of NULLs;
   a separate relation avoids them [S6].
3. *Weak entity `Room(number)` owned by `Building(bid)`: primary key of `Room`?*
   **$(bid, number)$.**
4. *True or false: mapping a 1:1 relationship by a foreign key without UNIQUE
   still enforces 1:1.* **False**: it allows 1:N.
5. *ISA with overlapping subclasses `Student`, `Employee` of `Person`; which method
   stores a person who is both twice?* **Method 2** (all attributes per subclass).

## Code

`src/py/er.py`: `er.transform` (the rules above), `er.ddl` (DDL with PK,
UNIQUE, NOT NULL, FK and ON DELETE actions, in dependency order),
`er.university`. Tests in `src/py/test_er.py`.
