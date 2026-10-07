"""Trigger semantics, executed in SQLite as a stand-in for PostgreSQL, note 01.

PostgreSQL is not installed here, so PL/pgSQL itself cannot be run. SQLite's
triggers share the semantics the exam asks about, with a different syntax
(SQLite CREATE TRIGGER [S15]; PostgreSQL 41.10 [S10], CREATE TRIGGER [S12]):

  PostgreSQL (PL/pgSQL trigger function)       SQLite (trigger body)
  BEFORE ... FOR EACH ROW, RETURN NULL         BEFORE, SELECT RAISE(IGNORE)
    -> this row's operation is skipped           -> same, statement continues
  BEFORE ... RETURN NEW (possibly modified)    no equivalent: SQLite cannot modify
                                                 NEW; use an AFTER UPDATE instead
  RAISE EXCEPTION '...'                        SELECT RAISE(ABORT, '...')
    -> the whole statement fails                 -> same, statement rolled back
  AFTER ... FOR EACH ROW (return ignored)      AFTER (SQLite has only row triggers)
  AFTER ... FOR EACH STATEMENT                 not supported by SQLite
  INSTEAD OF ... on a view                     INSTEAD OF on a view

Run: python triggers.py
"""
from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE account(id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER);
CREATE TABLE audit(seq INTEGER PRIMARY KEY, id INTEGER, old INTEGER, new INTEGER);

-- BEFORE row trigger that silently skips the row (PostgreSQL: RETURN NULL)
CREATE TRIGGER no_overdraft BEFORE UPDATE OF balance ON account
FOR EACH ROW WHEN NEW.balance < 0
BEGIN SELECT RAISE(IGNORE); END;

-- BEFORE row trigger that aborts the statement (PostgreSQL: RAISE EXCEPTION)
CREATE TRIGGER owner_required BEFORE INSERT ON account
FOR EACH ROW WHEN NEW.owner IS NULL
BEGIN SELECT RAISE(ABORT, 'owner must not be null'); END;

-- AFTER row trigger: fires once per changed row, sees OLD and NEW
CREATE TRIGGER log_change AFTER UPDATE OF balance ON account
FOR EACH ROW
BEGIN INSERT INTO audit(id, old, new) VALUES (OLD.id, OLD.balance, NEW.balance); END;

-- a view and an INSTEAD OF trigger that makes it insertable
CREATE VIEW rich AS SELECT id, owner, balance FROM account WHERE balance >= 1000;
CREATE TRIGGER rich_insert INSTEAD OF INSERT ON rich
FOR EACH ROW
BEGIN INSERT INTO account(id, owner, balance) VALUES (NEW.id, NEW.owner, max(NEW.balance, 1000)); END;
"""


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", isolation_level=None)   # autocommit
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO account VALUES (?,?,?)",
                     [(1, "ann", 100), (2, "bob", 50), (3, "cid", 500)])
    return conn


def balances(conn) -> dict[int, int]:
    return dict(conn.execute("SELECT id, balance FROM account ORDER BY id"))


def withdraw_all(conn, amount: int) -> dict[int, int]:
    """One UPDATE statement over three rows; the row that would go negative is skipped."""
    conn.execute("UPDATE account SET balance = balance - ?", (amount,))
    return balances(conn)


def insert_batch(conn, rows) -> str:
    """Multi-row INSERT; one bad row aborts the whole statement."""
    try:
        conn.execute("INSERT INTO account VALUES " + ",".join("(?,?,?)" for _ in rows),
                     [x for r in rows for x in r])
        return "ok"
    except sqlite3.IntegrityError as e:           # RAISE(ABORT) surfaces as a constraint error
        return f"aborted: {e}"


def demo() -> None:
    conn = make_db()
    print("start        ", balances(conn))
    print("withdraw 80  ", withdraw_all(conn, 80), "(bob skipped by BEFORE trigger)")
    print("audit rows   ", conn.execute("SELECT id, old, new FROM audit").fetchall())
    print("bad batch    ", insert_batch(conn, [(4, "dan", 10), (5, None, 10)]),
          "| rows now:", conn.execute("SELECT count(*) FROM account").fetchone()[0])
    conn.execute("INSERT INTO rich VALUES (6, 'eve', 20)")
    print("via view     ", conn.execute("SELECT * FROM account WHERE id = 6").fetchone(),
          "| visible in view:", conn.execute("SELECT count(*) FROM rich").fetchone()[0])


if __name__ == "__main__":
    demo()
