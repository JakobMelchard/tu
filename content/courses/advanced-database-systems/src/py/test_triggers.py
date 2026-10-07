import triggers as tr


def test_before_row_trigger_skips_only_that_row():
    conn = tr.make_db()
    assert tr.withdraw_all(conn, 80) == {1: 20, 2: 50, 3: 420}
    # the skipped row fires no AFTER trigger
    assert conn.execute("SELECT id, old, new FROM audit").fetchall() == [(1, 100, 20), (3, 500, 420)]


def test_after_row_trigger_fires_per_row():
    conn = tr.make_db()
    conn.execute("UPDATE account SET balance = balance + 1")
    assert conn.execute("SELECT count(*) FROM audit").fetchone()[0] == 3


def test_abort_rolls_back_the_whole_statement():
    conn = tr.make_db()
    msg = tr.insert_batch(conn, [(4, "dan", 10), (5, None, 10)])
    assert msg.startswith("aborted") and "owner" in msg
    assert conn.execute("SELECT count(*) FROM account").fetchone()[0] == 3
    assert tr.insert_batch(conn, [(4, "dan", 10)]) == "ok"


def test_instead_of_trigger_on_view():
    conn = tr.make_db()
    conn.execute("INSERT INTO rich VALUES (6, 'eve', 20)")
    assert conn.execute("SELECT * FROM account WHERE id = 6").fetchone() == (6, "eve", 1000)
