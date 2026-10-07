import sqlite3

import pytest

import er


@pytest.fixture()
def con():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    c.executescript(er.ddl(er.transform(er.university())))
    c.execute("INSERT INTO Room VALUES (1, 30), (2, 60)")
    c.execute("INSERT INTO Professor VALUES (10, 'Hofer', 'full', 1)")
    c.execute("INSERT INTO Course VALUES ('DBS', 'Databases', 6, 10)")
    c.execute("INSERT INTO Student VALUES (100, 'Ada', 2), (101, 'Bob', 4)")
    return c


def test_table_shapes():
    t = er.transform(er.university())
    assert set(t) == {"Professor", "Student", "Student_email", "Course", "Room", "Section", "Tutor", "attends"}
    assert t["attends"]["pk"] == ["student_sid", "course_cid"] and "grade" in t["attends"]["cols"]
    assert t["Section"]["pk"] == ["course_cid", "sno"]            # owner key + partial key
    assert t["Course"]["not_null"] == ["teaches_pid"]            # total participation
    assert t["Professor"]["unique"] == [["office_rid"]]           # 1:1
    assert t["Tutor"]["pk"] == ["sid"] and t["Tutor"]["fks"][0][1] == "Student"


def test_weak_entity_cascades(con):
    con.execute("INSERT INTO Section VALUES ('DBS', 1, 'Wed', NULL), ('DBS', 2, 'Thu', NULL)")
    con.execute("DELETE FROM Course WHERE cid = 'DBS'")
    assert con.execute("SELECT COUNT(*) FROM Section").fetchone() == (0,)


def test_total_participation_and_one_to_one(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO Course VALUES ('ALG', 'Algorithms', 6, NULL)")   # needs a lecturer
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO Professor VALUES (11, 'Lang', 'assoc', 1)")      # room 1 taken
    con.execute("INSERT INTO Professor VALUES (11, 'Lang', 'assoc', 2)")


def test_many_to_many_and_isa(con):
    con.execute("INSERT INTO attends VALUES (100, 'DBS', 1), (101, 'DBS', NULL)")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO attends VALUES (100, 'DBS', 2)")                # one row per pair
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO Tutor VALUES (999, 10)")                        # must be a Student
    con.execute("INSERT INTO Tutor VALUES (100, 10)")
    con.execute("INSERT INTO Section VALUES ('DBS', 1, 'Wed', 100)")
    con.execute("DELETE FROM Student WHERE sid = 100")                           # cascades to Tutor
    assert con.execute("SELECT leads_sid FROM Section").fetchone() == (None,)    # SET NULL
    assert con.execute("SELECT COUNT(*) FROM attends").fetchone() == (1,)


def test_multivalued_attribute(con):
    con.execute("INSERT INTO Student_email VALUES (100, 'a@x'), (100, 'b@x')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO Student_email VALUES (100, 'a@x')")
