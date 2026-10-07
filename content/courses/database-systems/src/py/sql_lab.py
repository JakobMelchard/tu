"""SQL lab: an in-memory sqlite3 university database and exam-style exercises
with asserted results (notes 06 and 13).

The 2026S SQL exam is computer-assisted in the Informatiklabor [S1]; which DBMS
it uses is not stated in any public source read for this pass.  sqlite3 is used
here because it ships with Python; every query below is also valid PostgreSQL
except where an EXERCISE says otherwise.  Differences that bite (no ALL/ANY,
foreign keys off by default, integer division) are asserted in the tests.

Schema (keys underlined in note 06):
  professor(pid, name, dept, salary, boss -> professor)
  student(sid, name, semester, program)            program may be NULL
  course(cid, title, ects, pid -> professor)       pid NULL = no lecturer yet
  prereq(cid -> course, pre -> course)
  exam(sid -> student, cid -> course, attempt, grade)   grade 1..5, 5 = fail,
                                                        NULL = not graded yet
"""
import sqlite3

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE professor (
  pid    INTEGER PRIMARY KEY,
  name   TEXT NOT NULL,
  dept   TEXT NOT NULL,
  salary INTEGER NOT NULL CHECK (salary > 0),
  boss   INTEGER REFERENCES professor(pid));
CREATE TABLE student (
  sid      INTEGER PRIMARY KEY,
  name     TEXT NOT NULL,
  semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 20),
  program  TEXT);
CREATE TABLE course (
  cid   TEXT PRIMARY KEY,
  title TEXT NOT NULL UNIQUE,
  ects  REAL NOT NULL CHECK (ects > 0),
  pid   INTEGER REFERENCES professor(pid) ON DELETE SET NULL);
CREATE TABLE prereq (
  cid TEXT REFERENCES course(cid) ON DELETE CASCADE,
  pre TEXT REFERENCES course(cid) ON DELETE CASCADE,
  PRIMARY KEY (cid, pre));
CREATE TABLE exam (
  sid     INTEGER REFERENCES student(sid) ON DELETE CASCADE,
  cid     TEXT REFERENCES course(cid),
  attempt INTEGER NOT NULL CHECK (attempt >= 1),
  grade   INTEGER CHECK (grade BETWEEN 1 AND 5),
  PRIMARY KEY (sid, cid, attempt));
"""

DATA = {
    "professor": [(1, "Hofer", "DBAI", 7000, None), (2, "Lang", "DBAI", 5200, 1),
                  (3, "Mayr", "DBAI", 5400, 2), (4, "Novak", "ALGO", 6500, None),
                  (5, "Wagner", "ALGO", 4800, 4), (6, "Berger", "THEO", 5000, None)],
    "student": [(101, "Ada", 2, "INF"), (102, "Bob", 4, "INF"), (103, "Cyd", 2, "CSE"),
                (104, "Dan", 6, None), (105, "Eve", 1, "CSE"), (106, "Fay", 3, "INF")],
    "course": [("DBS", "Database Systems", 6.0, 1), ("DM", "Data Modelling", 3.0, 2),
               ("ALG", "Algorithms", 6.0, 4), ("TCS", "Theoretical CS", 6.0, 5),
               ("DKE", "Knowledge Engineering", 3.0, 3), ("SEM", "Seminar", 3.0, None)],
    "prereq": [("DBS", "DM"), ("DKE", "DBS"), ("DKE", "ALG"), ("TCS", "ALG")],
    "exam": [(101, "DM", 1, 1), (101, "DBS", 1, 2), (101, "ALG", 1, 5), (101, "ALG", 2, 3),
             (102, "DM", 1, 3), (102, "DBS", 1, 5), (102, "DBS", 2, None),
             (103, "DM", 1, 2), (103, "ALG", 1, 1), (103, "TCS", 1, 2), (103, "DBS", 1, 1),
             (104, "DBS", 1, 4), (105, "DM", 1, 5)],
}


def connect():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA)
    for table in ("professor", "student", "course", "prereq", "exam"):   # FK order
        rows = DATA[table]
        con.executemany(f"INSERT INTO {table} VALUES ({', '.join('?' * len(rows[0]))})", rows)
    con.commit()
    return con


# (id, task, sql, expected rows; compared in order when the SQL has ORDER BY)
EXERCISES = [
    ("E1", "Names of students in semester 2, alphabetically.",
     "SELECT name FROM student WHERE semester = 2 ORDER BY name",
     [("Ada",), ("Cyd",)]),
    ("E2", "Every course with its lecturer's name; courses without lecturer too.",
     "SELECT c.cid, c.title, p.name FROM course c LEFT JOIN professor p ON p.pid = c.pid ORDER BY c.cid",
     [("ALG", "Algorithms", "Novak"), ("DBS", "Database Systems", "Hofer"),
      ("DKE", "Knowledge Engineering", "Mayr"), ("DM", "Data Modelling", "Lang"),
      ("SEM", "Seminar", None), ("TCS", "Theoretical CS", "Wagner")]),
    ("E3", "Names of students who passed DBS (grade 1-4 in some attempt).",
     "SELECT DISTINCT s.name FROM student s JOIN exam e ON e.sid = s.sid "
     "WHERE e.cid = 'DBS' AND e.grade <= 4 ORDER BY s.name",
     [("Ada",), ("Cyd",), ("Dan",)]),
    ("E4", "Per student: number of passed courses and passed ECTS, students with none included.",
     "SELECT s.name, COUNT(p.cid) AS n, COALESCE(SUM(c.ects), 0) AS ects FROM student s "
     "LEFT JOIN (SELECT DISTINCT sid, cid FROM exam WHERE grade <= 4) p ON p.sid = s.sid "
     "LEFT JOIN course c ON c.cid = p.cid GROUP BY s.sid, s.name ORDER BY ects DESC, s.name",
     [("Cyd", 4, 21.0), ("Ada", 3, 15.0), ("Dan", 1, 6.0), ("Bob", 1, 3.0), ("Eve", 0, 0), ("Fay", 0, 0)]),
    ("E5", "Average grade per course over graded attempts, courses with at least two graded attempts.",
     "SELECT cid, AVG(grade), COUNT(grade) FROM exam GROUP BY cid HAVING COUNT(grade) >= 2 ORDER BY cid",
     [("ALG", 3.0, 3), ("DBS", 3.0, 4), ("DM", 2.75, 4)]),
    ("E6", "Students who passed every course that Ada (101) passed (division).",
     "SELECT s.name FROM student s WHERE NOT EXISTS ("
     " SELECT * FROM exam a WHERE a.sid = 101 AND a.grade <= 4 AND NOT EXISTS ("
     "  SELECT * FROM exam e WHERE e.sid = s.sid AND e.cid = a.cid AND e.grade <= 4)) ORDER BY s.name",
     [("Ada",), ("Cyd",)]),
    ("E7a", "Students whose program differs from every program of 6th-semester students: NOT IN.",
     "SELECT name FROM student WHERE program NOT IN "
     "(SELECT program FROM student WHERE semester = 6) ORDER BY name",
     []),
    ("E7b", "Same question with NOT EXISTS (NULL = x is UNKNOWN, so no row blocks).",
     "SELECT name FROM student s WHERE NOT EXISTS (SELECT * FROM student t "
     "WHERE t.semester = 6 AND t.program = s.program) ORDER BY name",
     [("Ada",), ("Bob",), ("Cyd",), ("Dan",), ("Eve",), ("Fay",)]),
    ("E8", "Professors who earn more than their boss (self-join).",
     "SELECT p.name FROM professor p JOIN professor b ON b.pid = p.boss WHERE p.salary > b.salary",
     [("Mayr",)]),
    ("E9", "All direct and indirect prerequisites of DKE (recursive CTE).",
     "WITH RECURSIVE req(c) AS (SELECT pre FROM prereq WHERE cid = 'DKE' "
     "UNION SELECT p.pre FROM prereq p JOIN req r ON p.cid = r.c) SELECT c FROM req ORDER BY c",
     [("ALG",), ("DBS",), ("DM",)]),
    ("E10", "Rank students by passed ECTS (ties share a rank; window function).",
     "SELECT name, RANK() OVER (ORDER BY ects DESC) FROM (SELECT s.name, COALESCE(SUM(c.ects), 0) AS ects "
     "FROM student s LEFT JOIN (SELECT DISTINCT sid, cid FROM exam WHERE grade <= 4) p ON p.sid = s.sid "
     "LEFT JOIN course c ON c.cid = p.cid GROUP BY s.sid) ORDER BY 2, name",
     [("Cyd", 1), ("Ada", 2), ("Dan", 3), ("Bob", 4), ("Eve", 5), ("Fay", 5)]),
    ("E11", "Professors who teach no course.",
     "SELECT name FROM professor p WHERE NOT EXISTS (SELECT * FROM course c WHERE c.pid = p.pid)",
     [("Berger",)]),
    ("E12", "Professors earning more than every ALGO professor (> ALL; sqlite needs MAX).",
     "SELECT name FROM professor WHERE salary > (SELECT MAX(salary) FROM professor WHERE dept = 'ALGO')",
     [("Hofer",)]),
    ("E14", "Via a view of best passing grades: per course, students passed and best grade.",
     "SELECT cid, COUNT(*), MIN(grade) FROM best GROUP BY cid ORDER BY cid",
     [("ALG", 2, 1), ("DBS", 3, 1), ("DM", 3, 1), ("TCS", 1, 2)]),
    ("E15", "COUNT(*), COUNT(grade), COUNT(DISTINCT sid), rounded AVG(grade), SUM(grade)/COUNT(*) on exam.",
     "SELECT COUNT(*), COUNT(grade), COUNT(DISTINCT sid), ROUND(AVG(grade), 2), SUM(grade) / COUNT(*) FROM exam",
     [(13, 12, 5, 2.83, 2)]),
    ("E16", "Failed attempts never (yet) followed by a pass: student name and course (EXCEPT).",
     "SELECT s.name, f.cid FROM (SELECT sid, cid FROM exam WHERE grade = 5 EXCEPT "
     "SELECT sid, cid FROM exam WHERE grade <= 4) f JOIN student s ON s.sid = f.sid ORDER BY s.name",
     [("Bob", "DBS"), ("Eve", "DM")]),
]

VIEW = ("CREATE VIEW best AS SELECT sid, cid, MIN(grade) AS grade FROM exam "
        "WHERE grade <= 4 GROUP BY sid, cid")


def run(con, sql):
    return con.execute(sql).fetchall()


def dml_demo():
    """E13: DDL/DML and constraint behaviour; returns what happened, step by step."""
    con = connect()
    out = {}
    con.execute("UPDATE professor SET salary = salary * 11 / 10 "
                "WHERE pid IN (SELECT pid FROM course WHERE ects = 6)")
    out["raised"] = run(con, "SELECT name, salary FROM professor WHERE pid IN (1, 4, 5) ORDER BY pid")
    con.execute("DELETE FROM student WHERE sid = 105")                     # cascades to exam
    out["exam_rows_after_delete"] = run(con, "SELECT COUNT(*) FROM exam")[0][0]
    for key, stmt in (("check", "INSERT INTO exam VALUES (101, 'TCS', 1, 6)"),
                      ("fk", "INSERT INTO exam VALUES (999, 'DBS', 1, 2)"),
                      ("pk", "INSERT INTO exam VALUES (101, 'DM', 1, 2)"),
                      ("not_null", "INSERT INTO student VALUES (107, NULL, 1, 'INF')")):
        try:
            con.execute(stmt)
            out[key] = "accepted"
        except sqlite3.IntegrityError as e:
            out[key] = str(e).split(":")[0]
    con.execute("DELETE FROM professor WHERE pid = 3")                     # ON DELETE SET NULL
    out["dke_lecturer"] = run(con, "SELECT pid FROM course WHERE cid = 'DKE'")[0][0]
    try:
        con.execute("DELETE FROM professor WHERE pid = 1")                 # Lang's boss; course DBS
        out["delete_boss"] = "accepted"
    except sqlite3.IntegrityError as e:
        out["delete_boss"] = str(e).split(":")[0]
    return out


def query_plan(con, sql):
    """sqlite's EXPLAIN QUERY PLAN detail strings: 'SCAN t' = full scan, 'SEARCH t USING
    INDEX i (a=?)' = index lookup ([S21] eqp.html)."""
    return [row[3] for row in con.execute("EXPLAIN QUERY PLAN " + sql)]


def index_demo():
    """How an index changes the plan (note 08): returns {label: plan}."""
    con = connect()
    q = "SELECT * FROM exam WHERE cid = 'DBS'"
    out = {"cid = 'DBS', no index": query_plan(con, q)}
    con.execute("CREATE INDEX ix_exam_cid ON exam(cid)")
    out["cid = 'DBS', index on cid"] = query_plan(con, q)
    out["sid = 101 (leftmost PK column)"] = query_plan(con, "SELECT * FROM exam WHERE sid = 101")
    out["attempt = 2 (not a PK prefix)"] = query_plan(con, "SELECT * FROM exam WHERE attempt = 2")
    out["join, filter on e.cid"] = query_plan(
        con, "SELECT s.name FROM student s JOIN exam e ON e.sid = s.sid WHERE e.cid = 'DBS'")
    return out


def main():
    con = connect()
    con.execute(VIEW)
    for ex_id, task, sql, expected in EXERCISES:
        got = run(con, sql)
        ok = got == expected if "ORDER BY" in sql.upper() else sorted(got, key=repr) == sorted(expected, key=repr)
        print(f"{ex_id:4} {'ok ' if ok else 'BAD'} {task}")
        print(f"     {got}")
    print("E13 ", dml_demo())
    for label, plan in index_demo().items():
        print(f"plan {label:32} {plan}")


if __name__ == "__main__":
    main()
