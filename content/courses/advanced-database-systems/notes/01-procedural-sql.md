# 01 Procedural SQL: PL/pgSQL functions, procedures, cursors, triggers

> **Sourcing.** PostgreSQL 18 manual, ch. 41 PL/pgSQL [S10] (sections 41.5.3,
> 41.6.8, 41.7, 41.10 vendored in `../refs/vendor/`), trigger
> overview and CREATE TRIGGER [S12]; topic list from the 2026 block-1 notes and
> the VoWi exam report [S2], [S3]. **PostgreSQL is not installed here: the PL/pgSQL
> below is traced by hand against the manual, not executed.** Trigger semantics
> are executed in SQLite by `triggers.py`.

## Definitions

- **Procedural extension of SQL**: a language running *inside* the DBMS with
  variables, loops, branches and error handling around embedded SQL. PL/pgSQL
  (PostgreSQL), PL/SQL (Oracle), T-SQL (SQL Server). Gain: fewer client/server
  round trips, logic next to the data, access control via `EXECUTE` rights, triggers.
- **Block**: `[<<label>>] [DECLARE decls] BEGIN stmts [EXCEPTION handlers] END [label];`
  Blocks nest. `DO $$ ... $$;` runs an anonymous block once; `$$` is dollar quoting
  (a string literal without escaping `'`).
- **Function** (`CREATE FUNCTION f(...) RETURNS t LANGUAGE plpgsql AS $$...$$`):
  called inside a query (`SELECT f(3)`), returns a value, a row, or a set
  (`RETURNS SETOF t` / `RETURNS TABLE(...)` with `RETURN NEXT` / `RETURN QUERY`).
  Cannot `COMMIT`.
- **Procedure** (`CREATE PROCEDURE`, invoked with `CALL`): no return value (OUT
  parameters instead); may `COMMIT`/`ROLLBACK` when called from top level [S10 41.8].
- **Parameter modes**: `IN` (default), `OUT` (result column), `INOUT` (both).
- **Variables**: `x integer := 0;`, `r emp%ROWTYPE;` (row of a table), `v emp.salary%TYPE;`
  (type of a column), `rec RECORD;` (shape fixed at assignment). Inner blocks shadow
  outer names; reach the outer one as `outer_label.x`.

## SELECT INTO and FOUND [S10 41.5.3]

```sql
SELECT salary INTO v FROM emp WHERE name = n;          -- 0 rows: v := NULL; >1 rows: first row
SELECT salary INTO STRICT v FROM emp WHERE name = n;   -- 0 rows: NO_DATA_FOUND, >1: TOO_MANY_ROWS
IF NOT FOUND THEN ... END IF;                          -- FOUND: did the last statement hit a row?
```

"First row" is arbitrary without `ORDER BY`. This is a common MC trap: non-strict
`SELECT INTO` never raises on 0 or many rows.

## Errors and the rollback-to-block rule [S10 41.6.8]

When a handler catches an error, **local variables keep the values they had at
the error, but every database change made inside the block is rolled back**
(the block runs as a subtransaction). Worked example, `t` has one row `(1, 10)`:

```sql
DO $$
DECLARE x int := 0;
BEGIN
  UPDATE t SET v = 99 WHERE id = 1;        -- outer block: survives
  BEGIN
    x := x + 1;
    UPDATE t SET v = 0 WHERE id = 1;       -- inner block: rolled back
    x := x / 0;                            -- division_by_zero
  EXCEPTION WHEN division_by_zero THEN
    RAISE NOTICE 'x = %', x;               -- prints x = 1
  END;
END $$;
-- afterwards: t = (1, 99)
```

Propagation: an error not matched by any `WHEN` in the current block leaves the
block (its changes rolled back) and is re-raised in the enclosing block; if no
block handles it, the whole statement (and the surrounding transaction) fails.
`WHEN OTHERS` catches everything except query cancellation. Handlers are
checked top to bottom; the first match wins. `RAISE EXCEPTION 'msg %', v;`
raises; `RAISE NOTICE` only logs.

## Control structures [S10 41.6]

```sql
IF a > 0 THEN ... ELSIF a = 0 THEN ... ELSE ... END IF;
LOOP  EXIT WHEN i > 10;  i := i + 1;  END LOOP;
WHILE i < 10 LOOP ... END LOOP;
FOR i IN 1..10 BY 2 LOOP ... END LOOP;          -- i = 1,3,5,7,9; REVERSE 10..1 counts down
FOR r IN SELECT * FROM emp ORDER BY id LOOP ... END LOOP;   -- implicit cursor
CONTINUE WHEN r.salary IS NULL;   EXIT outer_label;          -- labelled loops
```

## Cursors [S10 41.7]

A **cursor** is a handle on a query result that is read row by row instead of
materialised at once. Lifecycle: declare, `OPEN`, `FETCH ... INTO`, test `FOUND`,
`CLOSE`. All cursor variables have type `refcursor`.

```sql
DECLARE
  c CURSOR FOR SELECT id, salary FROM emp ORDER BY id;   -- bound cursor
  r RECORD; total numeric := 0;
BEGIN
  OPEN c;
  LOOP
    FETCH c INTO r;
    EXIT WHEN NOT FOUND;
    total := total + r.salary;
    IF r.salary < 1000 THEN
      UPDATE emp SET salary = salary * 1.1 WHERE CURRENT OF c;   -- the row just fetched
    END IF;
  END LOOP;
  CLOSE c;
END;
```

`FOR r IN c LOOP` opens, fetches and closes automatically. `SCROLL` allows
`FETCH PRIOR / ABSOLUTE n`; `MOVE` repositions without reading. A function may
`RETURN` a `refcursor` so the client fetches lazily. Unbound form:
`c refcursor; OPEN c FOR SELECT ...;`.

## Triggers [S10 41.10], [S12]

A **trigger** binds a *trigger function* (`RETURNS trigger`, no declared arguments,
extra ones in `TG_ARGV`) to an event on a table or view:

```sql
CREATE TRIGGER name {BEFORE | AFTER | INSTEAD OF} {INSERT | UPDATE [OF col] | DELETE | TRUNCATE}
  ON tbl [REFERENCING NEW TABLE AS nt] FOR EACH {ROW | STATEMENT} [WHEN (cond)]
  EXECUTE FUNCTION f();
```

Variables: `NEW` (INSERT/UPDATE rows), `OLD` (UPDATE/DELETE rows), both NULL in
statement-level triggers; `TG_OP` ('INSERT'...), `TG_WHEN`, `TG_LEVEL`, `TG_TABLE_NAME`.

| kind | fires | return value |
|---|---|---|
| BEFORE ROW | once per affected row, before it is written | `NULL`: **skip this row** (no later triggers, no change for it); `NEW` (possibly modified): store that row; for DELETE return `OLD` to proceed |
| AFTER ROW | once per affected row, after the statement's rows are changed | ignored |
| BEFORE/AFTER STATEMENT | **once per statement, even if 0 rows are affected** | ignored |
| INSTEAD OF (views only, row level only) | instead of the DML on the view | `NULL`: "did nothing" (row not counted); `NEW`/`OLD`: done |

Any trigger can still abort the statement by raising an error. Several triggers
on the same event fire in **alphabetical order of their names** [S12]. A trigger
that modifies its own table can fire itself (cascade); guard with `WHEN` or
`pg_trigger_depth()`.

### Worked example: derived column plus audit

```sql
CREATE FUNCTION keep_total() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.qty < 0 THEN RETURN NULL; END IF;         -- silently skip bad rows
  NEW.total := NEW.qty * NEW.price;                 -- modify the row being written
  RETURN NEW;
END $$;
CREATE TRIGGER t1 BEFORE INSERT OR UPDATE ON line FOR EACH ROW EXECUTE FUNCTION keep_total();

CREATE FUNCTION log_it() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO audit VALUES (TG_OP, now());
  RETURN NULL;                                      -- ignored: AFTER trigger
END $$;
CREATE TRIGGER t2 AFTER INSERT ON line FOR EACH STATEMENT EXECUTE FUNCTION log_it();

INSERT INTO line(qty, price) VALUES (2, 5), (-1, 3), (4, 1);
-- line: (2,5,10), (4,1,4)    the (-1,3) row was skipped by t1
-- audit: one row ('INSERT'), because t2 is statement level
```

`triggers.py` runs the SQLite analogue: `withdraw_all` shows the BEFORE-row skip
(`RAISE(IGNORE)`) leaving the other rows updated and firing no AFTER trigger for
the skipped row; `insert_batch` shows an abort rolling back the whole
multi-row statement; the `rich` view shows INSTEAD OF.

## Pitfalls

- Non-`STRICT` `SELECT INTO` with no row gives NULL, not an error.
- A caught exception undoes the *block's* DB changes but not its variable assignments.
- `RETURN NULL` means "skip" only in BEFORE ROW (and INSTEAD OF) triggers; in AFTER triggers it is irrelevant.
- Statement-level triggers fire for UPDATEs that match no row.
- `NEW` is NULL in DELETE triggers and in statement triggers; referencing it there gives NULLs, not errors.
- INSTEAD OF exists only for views; BEFORE/AFTER on views only at statement level.
- Functions cannot commit; procedures can (from top level `CALL`).

## Exam-style questions

1. *`SELECT x INTO v FROM t WHERE false;` in a function without `STRICT`: what happens?*
   `v` becomes NULL, `FOUND` is false, no error.
2. *A BEFORE UPDATE FOR EACH ROW trigger returns NULL for 2 of 5 matched rows. How many rows are updated, and how often does an AFTER UPDATE FOR EACH ROW trigger fire?*
   3 and 3; skipped rows fire no later triggers (`triggers.py`, test `test_before_row_trigger_skips_only_that_row`).
3. *`DELETE FROM t WHERE false;` with an AFTER DELETE FOR EACH STATEMENT trigger and a FOR EACH ROW trigger: which fire?*
   The statement trigger once; the row trigger never.
4. *In the rollback example above, change the handler to `WHEN no_data_found`. Final state?*
   The error is not caught in the inner block, propagates out of the outer block, the DO statement fails and the outer UPDATE is undone too: `t = (1, 10)`.
5. *Why would a DBA expose a procedure instead of granting UPDATE on a table?*
   Access control: users may execute the procedure (with its checks) without direct table rights; plus fewer round trips.

## Code

- `triggers.py`: `make_db`, `withdraw_all`, `insert_batch`; header maps PostgreSQL trigger return values to SQLite's `RAISE(IGNORE)` / `RAISE(ABORT)`.
