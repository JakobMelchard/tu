import sqlite3

import pytest

import relalg as ra
import sql_lab


@pytest.fixture()
def con():
    c = sql_lab.connect()
    c.execute(sql_lab.VIEW)
    return c


@pytest.mark.parametrize("ex", sql_lab.EXERCISES, ids=lambda e: e[0])
def test_exercise(con, ex):
    _, _, sql, expected = ex
    got = sql_lab.run(con, sql)
    if "ORDER BY" in sql.upper():
        assert got == expected
    else:
        assert sorted(got, key=repr) == sorted(expected, key=repr)


def test_dml_demo():
    out = sql_lab.dml_demo()
    assert out["raised"] == [("Hofer", 7700), ("Novak", 7150), ("Wagner", 5280)]
    assert out["exam_rows_after_delete"] == 12          # Eve's one exam row cascaded
    assert out["check"].startswith("CHECK")
    assert out["fk"].startswith("FOREIGN KEY")
    assert out["pk"].startswith("UNIQUE")               # sqlite reports a PK clash as UNIQUE
    assert out["not_null"].startswith("NOT NULL")
    assert out["dke_lecturer"] is None                  # ON DELETE SET NULL
    assert out["delete_boss"].startswith("FOREIGN KEY")  # boss column has no ON DELETE action


def test_division_matches_algebra(con):
    passed = ra.from_sql(con, "SELECT DISTINCT sid, cid FROM exam WHERE grade <= 4", ("sid", "cid"))
    ada = ra.project(ra.select(passed, lambda t: t["sid"] == 101), ("cid",))
    sids = ra.division(passed, ada)
    names = {n for (n,) in sql_lab.run(con, f"SELECT name FROM student WHERE sid IN "
                                            f"({','.join(str(s) for (s,) in sids.rows)})")}
    assert names == {"Ada", "Cyd"}


def test_three_valued_logic(con):
    one = lambda e: con.execute(f"SELECT {e}").fetchone()[0]
    assert one("NULL = NULL") is None                   # UNKNOWN, not TRUE
    assert one("NULL IS NULL") == 1
    assert one("NULL AND 0") == 0 and one("NULL AND 1") is None
    assert one("NULL OR 1") == 1 and one("NULL OR 0") is None
    assert one("NOT NULL") is None
    assert one("1 IN (1, NULL)") == 1 and one("2 IN (1, NULL)") is None
    assert one("2 NOT IN (1, NULL)") is None            # the E7a trap in one line
    assert one("COALESCE(NULL, 7)") == 7


def test_not_in_fixed_by_filtering_nulls(con):
    got = sql_lab.run(con, "SELECT COUNT(*) FROM student WHERE program NOT IN "
                           "(SELECT program FROM student WHERE semester = 6 AND program IS NOT NULL)")
    assert got == [(6,)]            # subquery empty; x NOT IN (empty) is TRUE even for x NULL
    one = lambda e: con.execute(f"SELECT {e}").fetchone()[0]
    assert one("NULL NOT IN (SELECT 1 WHERE 0)") == 1 and one("NULL IN (SELECT 1 WHERE 0)") == 0


def test_aggregates_ignore_null_but_group_by_groups_it(con):
    assert sql_lab.run(con, "SELECT COUNT(*), COUNT(program), COUNT(DISTINCT program) FROM student") == [(6, 5, 2)]
    groups = sql_lab.run(con, "SELECT program, COUNT(*) FROM student GROUP BY program ORDER BY program")
    assert groups == [(None, 1), ("CSE", 2), ("INF", 3)]   # NULLs form one group; sqlite sorts NULL first
    assert sql_lab.run(con, "SELECT SUM(grade), MAX(grade) FROM exam WHERE cid = 'SEM'") == [(None, None)]
    assert sql_lab.run(con, "SELECT COUNT(*) FROM exam WHERE cid = 'SEM'") == [(0,)]


def test_all_vs_max_on_empty_subquery(con):
    with pytest.raises(sqlite3.OperationalError):       # sqlite has no quantified comparison
        con.execute("SELECT name FROM professor WHERE salary > ALL (SELECT salary FROM professor)")
    # > ALL (empty) is TRUE in standard SQL; > (SELECT MAX(...)) over empty is NULL -> no rows
    got = sql_lab.run(con, "SELECT COUNT(*) FROM professor WHERE salary > "
                           "(SELECT MAX(salary) FROM professor WHERE dept = 'NONE')")
    assert got == [(0,)]
    rewrite = sql_lab.run(con, "SELECT COUNT(*) FROM professor p WHERE NOT EXISTS (SELECT * FROM professor q "
                               "WHERE q.dept = 'NONE' AND q.salary >= p.salary)")
    assert rewrite == [(6,)]                             # the faithful rewrite of > ALL


def test_foreign_keys_off_by_default_in_sqlite():
    c = sqlite3.connect(":memory:")
    c.executescript(sql_lab.SCHEMA.replace("PRAGMA foreign_keys = ON;", ""))
    c.execute("INSERT INTO exam VALUES (999, 'NOPE', 1, 2)")           # accepted: no enforcement
    assert c.execute("PRAGMA foreign_keys").fetchone() == (0,)


def test_view_is_not_materialised(con):
    before = sql_lab.run(con, "SELECT COUNT(*) FROM best")[0][0]
    con.execute("INSERT INTO exam VALUES (106, 'DM', 1, 4)")
    assert sql_lab.run(con, "SELECT COUNT(*) FROM best")[0][0] == before + 1


def test_union_vs_union_all(con):
    all_ = sql_lab.run(con, "SELECT COUNT(*) FROM (SELECT cid FROM exam UNION ALL SELECT cid FROM course)")
    dist = sql_lab.run(con, "SELECT COUNT(*) FROM (SELECT cid FROM exam UNION SELECT cid FROM course)")
    assert all_ == [(19,)] and dist == [(6,)]


def test_index_changes_plan():
    plans = sql_lab.index_demo()
    assert plans["cid = 'DBS', no index"] == ["SCAN exam"]
    assert plans["cid = 'DBS', index on cid"] == ["SEARCH exam USING INDEX ix_exam_cid (cid=?)"]
    assert plans["sid = 101 (leftmost PK column)"][0].startswith("SEARCH exam USING INDEX")
    assert plans["attempt = 2 (not a PK prefix)"] == ["SCAN exam"]
    join = plans["join, filter on e.cid"]
    assert join[0].startswith("SEARCH e USING INDEX ix_exam_cid") and "PRIMARY KEY" in join[1]


def test_exam_question_count_avg():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE t (a)")
    c.executemany("INSERT INTO t VALUES (?)", [(1,), (2,), (None,)])
    assert c.execute("SELECT COUNT(*), COUNT(a), AVG(a) FROM t").fetchone() == (3, 2, 1.5)
    c.execute("CREATE TABLE g (x CHECK (x BETWEEN 1 AND 5))")
    c.execute("INSERT INTO g VALUES (NULL)")                 # UNKNOWN is not FALSE: accepted
    with pytest.raises(sqlite3.IntegrityError):
        c.execute("INSERT INTO g VALUES (6)")
