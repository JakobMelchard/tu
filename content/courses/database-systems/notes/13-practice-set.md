# 13 Practice set

> **What this is.** Our own practice material, not 184.686's: no past paper or
> exercise sheet of the course was publicly readable on 2026-09-28 ([S4] 403,
> [S5] bot check). Part A imitates the **written multiple-choice exam** [S1]
> with independent true/false statements; every answer is **computed** by the
> reference code (`python src/py/practice.py`) and pinned by
> `src/py/test_practice.py`. Part B imitates the **computer-assisted SQL exam**
> [S1]: sixteen exercises on the lab database of note 06 with the exact
> expected rows, asserted by `src/py/test_sql_lab.py`. How the real MC exam
> scores wrong ticks is unknown (note 00).

How to use: answer on paper first, then compare; for part B type the query
into `sqlite3` (or PostgreSQL) on the database from `sql_lab.connect` before
looking at the solution.

## Part A: multiple-choice items

**P1.** R(ABCDE), F = {A->B, B->C, CD->E, E->A}.

a. AD is a candidate key
b. R has exactly three candidate keys
c. R is in 3NF
d. R is in BCNF

**P2.** R(ABCD), F = {AB->C, C->D, D->A}.

a. BD is a candidate key
b. every attribute is prime
c. R is in BCNF
d. {C}+ = {A, C, D}

**P3.** F = {A->BC, B->C, AB->C, A->B}.

a. {A->B, B->C} is a minimal cover of F
b. AB->C has an extraneous attribute
c. F implies C->A

**P4.** R(ABC), F = {A->B}.

a. {AB, AC} is lossless
b. {AB, BC} is lossless
c. {AB, AC} preserves F
d. R is in 2NF

**P5.** R(ABC), F = {AB->C, C->B}.

a. the BCNF decomposition {AC, BC} loses AB->C
b. R is in 3NF

**P6.** Relations R(a, b), T(a, b) with |R| = m, |T| = k; S(b) non-empty with |S| = n.

a. |R union T| <= m + k
b. |R - T| >= m - k
c. |pi_a(R)| <= m
d. |R / S| <= m / n
e. |R join S| <= m
f. pi_a(R - T) = pi_a(R) - pi_a(T) always

**P7.** In the sql_lab database (Dan's program is NULL, Dan is the only 6th-semester student).

a. E7a (NOT IN) returns no row
b. E7b (NOT EXISTS) returns all six students
c. COUNT(*) = COUNT(grade) on exam
d. AVG(grade) = SUM(grade) / COUNT(*) on exam

**P8.** B+ tree, n = 4 (at most 4 pointers), keys 10 20 5 6 12 30 7 17 3 25 27 8 inserted.

a. the tree has 3 levels
b. the root holds the single key 20
c. there are 5 leaves
d. a point search reads 3 nodes

**P9.** B+ tree with n = 100, 10^6 keys.

a. height <= 4 is guaranteed
b. height 3 is possible (3 levels hold at most 100 * 100 * 99 keys)

**P10.** Extendible hashing, bucket capacity 2, h(k) = k (low bits), keys 1 4 5 7 10 12 13.

a. global depth ends at 3
b. there are 5 distinct buckets
c. inserting 12 (after 1 4 5 7 10) doubled the directory

**P11.** b_r = 100, b_s = 400 pages, M = 12 buffer pages.

a. block NL join with r outer reads 4100 pages
b. block NL join with s outer is cheaper
c. hash join (no recursive partitioning) costs 1500
d. sort-merge on sorted inputs costs 500

**P12.** External merge sort of b = 1000 pages with M = 5 buffers.

a. it needs 5 passes including run generation
b. with M = 32 it needs 2 passes

**P13.** Estimation: n_r = 1000, n_s = 5000, V(A, r) = 100, V(A, s) = 1000.

a. |r join_A s| is estimated as 5000
b. System R guesses 1/3 for A > c without statistics
c. four relations have 24 left-deep join orders
d. four relations have 120 bushy join trees

**P14.** Schedule r1(A) w2(A) r2(B) w1(B) c1 c2.

a. it is conflict-serialisable
b. it is view-serialisable
c. it is recoverable

**P15.** Schedule w1(A) r2(A) c2 c1.

a. it is conflict-serialisable
b. it is recoverable

**P16.** Deadlock handling with timestamps TS(T1) < TS(T3).

a. wait-die: T3 requesting a lock T1 holds is rolled back
b. wound-wait: T1 requesting a lock T3 holds waits

**P17.** Snapshot isolation (first committer wins).

a. two concurrent increments of x both commit
b. write skew on a + b >= 1 is possible

**P18.** ARIES restart of the recovery.py demo (crash after LSN 8).

a. redo reapplies 3 records
b. undo writes 3 CLRs
c. page A ends with value 10

### Answer key (computed by `practice.answers`)

| item | answers | why |
|---|---|---|
| P1 | a T, b F, c T, d F | keys AD, BD, CD, DE (four); all attributes prime; A->B violates BCNF |
| P2 | a T, b T, c F, d T | keys AB, BC, BD; C->D violates BCNF |
| P3 | a T, b T, c F | A->C follows from A->B, B->C, so B is extraneous in AB->C; C+ = C |
| P4 | a T, b F, c T, d F | key AC; A->B is partial; AB cap BC = B determines neither side |
| P5 | a T, b T | keys AB, AC; C->B has a prime RHS; the split {AC, BC} is forced by C->B |
| P6 | a T, b T, c T, d T, e T, f F | f: R = {(1,1),(1,2)}, T = {(1,1)} |
| P7 | a T, b T, c F, d F | the subquery yields NULL; 13 rows, 12 grades; AVG divides by 12 |
| P8 | a T, b T, c T, d T | trace in note 08 |
| P9 | a T, b F | 3 levels hold at most 990,000 keys |
| P10 | a T, b T, c F | 12 splits {4, 10}, local depth 1 < G = 2 |
| P11 | a T, b F, c T, d T | 100 + 10 * 400 vs 400 + 40 * 100 |
| P12 | a T, b F | 32 runs need two 31-way merges: 3 passes |
| P13 | a T, b T, c T, d T | 1000 * 5000 / 1000; (2 * 3)! / 3! |
| P14 | a F, b F, c T | cycle 1->2->1; no blind writes, so VSR = CSR; nobody reads uncommitted data |
| P15 | a T, b F | T2 commits after reading from the uncommitted T1 |
| P16 | a T, b F | wound-wait: the older requester wounds the younger holder |
| P17 | a F, b T | first committer wins; the skew writes are disjoint |
| P18 | a T, b T, c T | see note 12 |

## Part B: SQL lab

**E1.** Names of students in semester 2, alphabetically.

```sql
SELECT name FROM student WHERE semester = 2 ORDER BY name;
```

Expected: `[('Ada',), ('Cyd',)]`

**E2.** Every course with its lecturer's name; courses without lecturer too.

```sql
SELECT c.cid, c.title, p.name FROM course c LEFT JOIN professor p ON p.pid = c.pid ORDER BY c.cid;
```

Expected: `[('ALG', 'Algorithms', 'Novak'), ('DBS', 'Database Systems', 'Hofer'), ('DKE', 'Knowledge Engineering', 'Mayr'), ('DM', 'Data Modelling', 'Lang'), ('SEM', 'Seminar', None), ('TCS', 'Theoretical CS', 'Wagner')]`

**E3.** Names of students who passed DBS (grade 1-4 in some attempt).

```sql
SELECT DISTINCT s.name FROM student s JOIN exam e ON e.sid = s.sid WHERE e.cid = 'DBS' AND e.grade <= 4 ORDER BY s.name;
```

Expected: `[('Ada',), ('Cyd',), ('Dan',)]`

**E4.** Per student: number of passed courses and passed ECTS, students with none included.

```sql
SELECT s.name, COUNT(p.cid) AS n, COALESCE(SUM(c.ects), 0) AS ects FROM student s LEFT JOIN (SELECT DISTINCT sid, cid FROM exam WHERE grade <= 4) p ON p.sid = s.sid LEFT JOIN course c ON c.cid = p.cid GROUP BY s.sid, s.name ORDER BY ects DESC, s.name;
```

Expected: `[('Cyd', 4, 21.0), ('Ada', 3, 15.0), ('Dan', 1, 6.0), ('Bob', 1, 3.0), ('Eve', 0, 0), ('Fay', 0, 0)]`

**E5.** Average grade per course over graded attempts, courses with at least two graded attempts.

```sql
SELECT cid, AVG(grade), COUNT(grade) FROM exam GROUP BY cid HAVING COUNT(grade) >= 2 ORDER BY cid;
```

Expected: `[('ALG', 3.0, 3), ('DBS', 3.0, 4), ('DM', 2.75, 4)]`

**E6.** Students who passed every course that Ada (101) passed (division).

```sql
SELECT s.name FROM student s WHERE NOT EXISTS ( SELECT * FROM exam a WHERE a.sid = 101 AND a.grade <= 4 AND NOT EXISTS ( SELECT * FROM exam e WHERE e.sid = s.sid AND e.cid = a.cid AND e.grade <= 4)) ORDER BY s.name;
```

Expected: `[('Ada',), ('Cyd',)]`

**E7a.** Students whose program differs from every program of 6th-semester students: NOT IN.

```sql
SELECT name FROM student WHERE program NOT IN (SELECT program FROM student WHERE semester = 6) ORDER BY name;
```

Expected: `[]`

**E7b.** Same question with NOT EXISTS (NULL = x is UNKNOWN, so no row blocks).

```sql
SELECT name FROM student s WHERE NOT EXISTS (SELECT * FROM student t WHERE t.semester = 6 AND t.program = s.program) ORDER BY name;
```

Expected: `[('Ada',), ('Bob',), ('Cyd',), ('Dan',), ('Eve',), ('Fay',)]`

**E8.** Professors who earn more than their boss (self-join).

```sql
SELECT p.name FROM professor p JOIN professor b ON b.pid = p.boss WHERE p.salary > b.salary;
```

Expected: `[('Mayr',)]`

**E9.** All direct and indirect prerequisites of DKE (recursive CTE).

```sql
WITH RECURSIVE req(c) AS (SELECT pre FROM prereq WHERE cid = 'DKE' UNION SELECT p.pre FROM prereq p JOIN req r ON p.cid = r.c) SELECT c FROM req ORDER BY c;
```

Expected: `[('ALG',), ('DBS',), ('DM',)]`

**E10.** Rank students by passed ECTS (ties share a rank; window function).

```sql
SELECT name, RANK() OVER (ORDER BY ects DESC) FROM (SELECT s.name, COALESCE(SUM(c.ects), 0) AS ects FROM student s LEFT JOIN (SELECT DISTINCT sid, cid FROM exam WHERE grade <= 4) p ON p.sid = s.sid LEFT JOIN course c ON c.cid = p.cid GROUP BY s.sid) ORDER BY 2, name;
```

Expected: `[('Cyd', 1), ('Ada', 2), ('Dan', 3), ('Bob', 4), ('Eve', 5), ('Fay', 5)]`

**E11.** Professors who teach no course.

```sql
SELECT name FROM professor p WHERE NOT EXISTS (SELECT * FROM course c WHERE c.pid = p.pid);
```

Expected: `[('Berger',)]`

**E12.** Professors earning more than every ALGO professor (> ALL; sqlite needs MAX).

```sql
SELECT name FROM professor WHERE salary > (SELECT MAX(salary) FROM professor WHERE dept = 'ALGO');
```

Expected: `[('Hofer',)]`

**E14.** Via a view of best passing grades: per course, students passed and best grade.

```sql
SELECT cid, COUNT(*), MIN(grade) FROM best GROUP BY cid ORDER BY cid;
```

Expected: `[('ALG', 2, 1), ('DBS', 3, 1), ('DM', 3, 1), ('TCS', 1, 2)]`

**E15.** COUNT(*), COUNT(grade), COUNT(DISTINCT sid), rounded AVG(grade), SUM(grade)/COUNT(*) on exam.

```sql
SELECT COUNT(*), COUNT(grade), COUNT(DISTINCT sid), ROUND(AVG(grade), 2), SUM(grade) / COUNT(*) FROM exam;
```

Expected: `[(13, 12, 5, 2.83, 2)]`

**E16.** Failed attempts never (yet) followed by a pass: student name and course (EXCEPT).

```sql
SELECT s.name, f.cid FROM (SELECT sid, cid FROM exam WHERE grade = 5 EXCEPT SELECT sid, cid FROM exam WHERE grade <= 4) f JOIN student s ON s.sid = f.sid ORDER BY s.name;
```

Expected: `[('Bob', 'DBS'), ('Eve', 'DM')]`

**E13 (DDL/DML).** On a fresh copy (`sql_lab.dml_demo`): raise by 10 % the
salary of every professor teaching a 6-ECTS course; delete student 105; try to
insert a grade 6, an exam of a non-existent student, a duplicate exam, a
student without name; delete professor 3, then professor 1.

Expected: salaries Hofer 7700, Novak 7150, Wagner 5280; 12 exam rows left
(Eve's exam cascaded); the four inserts fail with CHECK, FOREIGN KEY, UNIQUE
(the primary key) and NOT NULL errors; deleting Mayr sets `course.pid` of DKE
to NULL (`ON DELETE SET NULL`); deleting Hofer fails (FOREIGN KEY:
`professor.boss` of Lang has no `ON DELETE` action).
