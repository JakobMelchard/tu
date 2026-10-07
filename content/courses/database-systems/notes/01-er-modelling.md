# 01 ER modelling

> **Sourcing.** Definitions and notation from [S6] ch. 6 (Silberschatz et al.
> slides); the model itself is Chen's [S11]. The course's own ER notation is
> unknown (no public slides, [S4]); check the first exercise sheet for which
> cardinality convention it uses before learning one by heart.

## Definitions

| term | definition |
|---|---|
| entity | a distinguishable object of the domain (a student, a course) |
| entity set (type) | the set of all entities of one kind; drawn as a rectangle |
| attribute | a function from an entity set to a domain; **simple** or **composite** (`address` = street, city), **single-** or **multivalued** (`phone_numbers`), stored or **derived** (`age` from `date_of_birth`) [S6] |
| key | a set of attributes whose values identify an entity uniquely; the chosen one is underlined |
| relationship set | a mathematical relation $R \subseteq E_1 \times \dots \times E_n$ among entity sets; **degree** $n$ (binary, ternary); may carry attributes (`grade` on `attends`) |
| role | the name of an entity set's function in a relationship; needed when an entity set occurs twice (`prereq(course, course)`) |
| cardinality ratio | for binary $R \subseteq A \times B$: **1:1**, **1:N**, **N:M**; "A is 1 in 1:N" means each $b$ relates to at most one $a$ |
| participation | **total**: every entity of the set takes part in at least one relationship (double line); otherwise **partial** [S6] |
| (min, max) | an interval $l..h$ on the line between $E$ and $R$: each $e \in E$ takes part in between $l$ and $h$ relationships of $R$; $l = 1$ is total participation, $h = 1$ means at most one, $h = *$ unbounded [S6] |
| weak entity set | has no key of its own; identified by the key of an **owner** (identifying) entity set plus a **discriminator** (partial key, dashed underline); participates totally in the identifying relationship [S6] |
| specialisation / generalisation (ISA) | subclasses inherit the superclass's attributes and key; **disjoint** vs **overlapping**, **total** vs **partial** (partial is the default) [S6] |
| aggregation | treat a relationship as an entity so that another relationship can involve it [S6] |

### Two cardinality notations point in opposite directions

Chen-style 1:N between `Professor` and `Course` for `teaches` writes **1 next to
Professor**, **N next to Course**: a course has one professor, a professor N
courses. The $(\min,\max)$ notation writes at each entity how often **that
entity** participates: `Professor (0,*)`, `Course (1,1)`. Same fact, the numbers
sit at the opposite ends. Silberschatz's arrow notation adds a third convention:
an arrow **into** the entity set that is "one" [S6].

$$\text{Chen: } \text{Prof} \overset{1}{\text{---}} \langle\text{teaches}\rangle \overset{N}{\text{---}} \text{Course}
\qquad
\text{(min,max): } \text{Prof} \overset{(0,*)}{\text{---}} \langle\text{teaches}\rangle \overset{(1,1)}{\text{---}} \text{Course}$$

## Worked example: a small university

Requirements, and the modelling decision each forces:

| requirement | ER construct |
|---|---|
| professors have id, name, rank | entity `Professor(pid, name, rank)` |
| students have id, name, semester, **several e-mail addresses** | entity `Student(sid, ...)`, multivalued `email` |
| every course is taught by exactly one professor; professors teach any number | `teaches`: Professor 1 : N Course, Course **total** |
| students attend any number of courses and get a grade per course | `attends`: Student N : M Course, attribute `grade` on the relationship |
| every professor has exactly one office; a room is an office of at most one professor | `office`: Professor 1 : 1 Room, Professor total |
| courses are split into sections numbered 1, 2, ... **within** the course | weak entity `Section`, discriminator `sno`, owner `Course` |
| some students are tutors with a weekly hours figure; a tutor leads sections | `Tutor` ISA `Student` (partial), `leads`: Tutor 1 : N Section |

Why `grade` is on `attends` and not on `Student` or `Course`: it is a function of
the pair (student, course), not of either entity alone. Putting it on the N side
of a 1:N relationship is allowed (it is then determined by that entity), but
here the relationship is N:M.

Why `Section` is weak: "Section 2" means nothing without the course; the key
of a section is $(\mathit{cid}, \mathit{sno})$. Deleting a course must delete
its sections (existence dependency), which note 03 turns into
`ON DELETE CASCADE`.

The model is `er.university()`; `python src/py/er.py` prints the eight
relation schemas note 03 derives from it.

### Ternary is not three binaries

`examines(Professor, Student, Course)` records which professor examined which
student in which course. Replacing it by `P-S`, `S-C`, `P-C` loses information:
from $(p_1, s_1)$, $(s_1, c_1)$, $(p_1, c_1)$ you cannot tell whether $p_1$
examined $s_1$ **in** $c_1$ or in another course that both happen to share.
Formally, the ternary relation is not always the join of its three binary
projections (that is exactly a lossy decomposition, note 04). [S6] also allows
at most one arrow out of a ternary relationship, because two arrows have two
incompatible readings.

## Pitfalls

- Reading $(\min,\max)$ with Chen's 1:N convention, or the reverse. Always ask:
  "for **one** entity on this side, how many relationships?"
- A relationship set is a **set**: the same pair $(s, c)$ occurs at most once.
  Two attempts at the same exam need an attribute in the key (weak entity
  `Attempt`) or an entity, not a second relationship instance.
- Modelling a relationship as an attribute holding a foreign key (`Course.pid`)
  in the ER diagram. Foreign keys belong to the relational schema, not to ER.
- A weak entity's discriminator is not a key; its full key includes the owner's key.
- Total participation of `Course` in `teaches` is a constraint on `Course`, not
  on `Professor`.
- Derived attributes (age) are drawn but not stored.

## Exam-style questions

1. *True or false: in a 1:N relationship from Professor (1) to Course (N), a
   course can have two professors.* **False.** Each course relates to at most
   one professor; a professor can relate to many courses.
2. *In (min,max) notation, `Student (1,1) --- advisor --- Instructor (0,*)`.
   Which is true: (a) every student has exactly one advisor, (b) every
   instructor advises at least one student?* **(a) true, (b) false**
   (min 0 at Instructor) [S6].
3. *True or false: a weak entity set always participates totally in its
   identifying relationship.* **True** [S6]: without its owner it has no key.
4. *Is a ternary relationship always replaceable by the three binary
   relationships between its participants without loss?* **No**; see the
   `examines` example.
5. *A generalisation `Person` into `Student` and `Employee` where a person can be
   both and need not be either: which constraints?* **Overlapping, partial.**

## Code

`src/py/er.py`: `er.university` (the example as data), `er.transform` (ER to
relations, note 03), `er.ddl` (SQL DDL). `src/py/test_er.py` loads the DDL into
sqlite and checks that total participation, 1:1, weak-entity cascade, N:M key
and ISA behave as modelled.
