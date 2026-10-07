"""SQL window functions in SQLite, note 02.

A window function computes a value for each row from a set of related rows
(its *window frame*) without collapsing the rows as GROUP BY would:

    f(...) OVER (PARTITION BY p ORDER BY o [frame])

PARTITION BY splits rows into independent groups; ORDER BY orders rows inside
a partition; the frame selects which rows of the partition f sees. Default
frame when ORDER BY is present: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT
ROW, which includes the current row's *peers* (rows with equal ORDER BY
values) [S14 section 3], [S11]. Every query below has its expected rows in
EXPECTED, hand-computed, and test_window_functions.py re-derives them with pandas.

Run: python window_functions.py
"""
from __future__ import annotations

import sqlite3

EXAM = [("ann", "db", 90), ("bob", "db", 85), ("cid", "db", 85), ("dan", "db", 70),
        ("ann", "os", 60), ("bob", "os", 75), ("eve", "os", 75), ("fay", "os", 50)]
TXN = [(1, 1, 10), (2, 2, 20), (3, 2, 5), (4, 3, 30), (5, 4, 0), (6, 5, 15)]  # id, day, amount

QUERIES = {
    "ranks": """
        SELECT course, student, points,
               ROW_NUMBER() OVER (PARTITION BY course ORDER BY points DESC, student) AS rn,
               RANK()       OVER (PARTITION BY course ORDER BY points DESC) AS rnk,
               DENSE_RANK() OVER (PARTITION BY course ORDER BY points DESC) AS drnk
        FROM exam ORDER BY course, rn""",
    "diff_from_avg": """
        SELECT course, student, points - AVG(points) OVER (PARTITION BY course) AS delta
        FROM exam ORDER BY course, student""",
    "running_range_vs_rows": """
        SELECT id, day, amount,
               SUM(amount) OVER (ORDER BY day) AS range_sum,
               SUM(amount) OVER (ORDER BY day, id ROWS UNBOUNDED PRECEDING) AS rows_sum
        FROM txn ORDER BY id""",
    "moving_avg": """
        SELECT id, ROUND(AVG(amount) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING
                                           AND CURRENT ROW), 3) AS ma3
        FROM txn ORDER BY id""",
    "lag": """
        SELECT id, amount - LAG(amount) OVER (ORDER BY id) AS change,
               LEAD(amount, 1, -1) OVER (ORDER BY id) AS next_amount
        FROM txn ORDER BY id""",
    "last_value_pitfall": """
        SELECT course, student,
               LAST_VALUE(points) OVER (PARTITION BY course ORDER BY points DESC) AS default_frame,
               LAST_VALUE(points) OVER (PARTITION BY course ORDER BY points DESC
                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS full_frame
        FROM exam ORDER BY course, student""",
    "top2_rank": """
        SELECT course, student FROM (
            SELECT course, student, RANK() OVER (PARTITION BY course ORDER BY points DESC) AS r
            FROM exam) WHERE r <= 2 ORDER BY course, student""",
    "top2_row_number": """
        SELECT course, student FROM (
            SELECT course, student,
                   ROW_NUMBER() OVER (PARTITION BY course ORDER BY points DESC, student) AS r
            FROM exam) WHERE r <= 2 ORDER BY course, student""",
    "ntile": """
        SELECT student, course, NTILE(2) OVER (ORDER BY points DESC, student) AS half
        FROM exam ORDER BY points DESC, student""",
}

EXPECTED = {
    "ranks": [("db", "ann", 90, 1, 1, 1), ("db", "bob", 85, 2, 2, 2),
              ("db", "cid", 85, 3, 2, 2), ("db", "dan", 70, 4, 4, 3),
              ("os", "bob", 75, 1, 1, 1), ("os", "eve", 75, 2, 1, 1),
              ("os", "ann", 60, 3, 3, 2), ("os", "fay", 50, 4, 4, 3)],
    "diff_from_avg": [("db", "ann", 7.5), ("db", "bob", 2.5), ("db", "cid", 2.5),
                      ("db", "dan", -12.5), ("os", "ann", -5.0), ("os", "bob", 10.0),
                      ("os", "eve", 10.0), ("os", "fay", -15.0)],
    # day 2 has two rows: RANGE puts both peers in the frame at once
    "running_range_vs_rows": [(1, 1, 10, 10, 10), (2, 2, 20, 35, 30), (3, 2, 5, 35, 35),
                              (4, 3, 30, 65, 65), (5, 4, 0, 65, 65), (6, 5, 15, 80, 80)],
    "moving_avg": [(1, 10.0), (2, 15.0), (3, 11.667), (4, 18.333), (5, 11.667), (6, 15.0)],
    "lag": [(1, None, 20), (2, 10, 5), (3, -15, 30), (4, 25, 0), (5, -30, 15), (6, 15, -1)],
    # default frame stops at the current row's last peer -> the row's own points
    "last_value_pitfall": [("db", "ann", 90, 70), ("db", "bob", 85, 70), ("db", "cid", 85, 70),
                           ("db", "dan", 70, 70), ("os", "ann", 60, 50), ("os", "bob", 75, 50),
                           ("os", "eve", 75, 50), ("os", "fay", 50, 50)],
    "top2_rank": [("db", "ann"), ("db", "bob"), ("db", "cid"), ("os", "bob"), ("os", "eve")],
    "top2_row_number": [("db", "ann"), ("db", "bob"), ("os", "bob"), ("os", "eve")],
    "ntile": [("ann", "db", 1), ("bob", "db", 1), ("cid", "db", 1), ("bob", "os", 1),
              ("eve", "os", 2), ("dan", "db", 2), ("ann", "os", 2), ("fay", "os", 2)],
}


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE exam(student TEXT, course TEXT, points INTEGER)")
    conn.execute("CREATE TABLE txn(id INTEGER PRIMARY KEY, day INTEGER, amount INTEGER)")
    conn.executemany("INSERT INTO exam VALUES (?,?,?)", EXAM)
    conn.executemany("INSERT INTO txn VALUES (?,?,?)", TXN)
    return conn


def run(conn: sqlite3.Connection, name: str) -> list[tuple]:
    return conn.execute(QUERIES[name]).fetchall()


def demo() -> None:
    conn = make_db()
    for name in QUERIES:
        rows = run(conn, name)
        status = "ok" if rows == EXPECTED[name] else "MISMATCH"
        print(f"-- {name} [{status}]")
        for r in rows:
            print("   ", r)


if __name__ == "__main__":
    demo()
