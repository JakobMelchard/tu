"""Recursive Common Table Expressions (CTEs) in SQLite, note 03.

A CTE is a named subquery introduced by WITH. WITH RECURSIVE allows the
subquery to refer to itself: a non-recursive (base) term, then UNION or
UNION ALL, then a recursive term that reads the rows produced so far.

Evaluation (PostgreSQL 18 docs 7.8.2 [S9]; SQLite lang_with 3.3 [S13]):
  working := base term (UNION: duplicates removed); result := working
  while working not empty:
      new := recursive term evaluated on `working` only
      UNION: drop rows of `new` already in result (and within new)
      result += new; working := new
This is semi-naive evaluation of a linear recursive rule (note 04):
each round joins only the rows that were new in the previous round.

Run: python recursive_cte.py
"""
from __future__ import annotations

import sqlite3

# weighted digraph with a cycle c -> b -> d -> e -> c
EDGES = [("a", "b", 4), ("a", "c", 1), ("c", "b", 2), ("b", "d", 1),
         ("c", "d", 5), ("d", "e", 3), ("e", "c", 1)]

# bill of materials: assembly contains qty x part
CONTAINS = [("bike", "wheel", 2), ("bike", "frame", 1),
            ("wheel", "spoke", 32), ("wheel", "rim", 1), ("wheel", "hub", 1),
            ("wheel", "bolt", 2), ("frame", "tube", 3), ("frame", "bolt", 4),
            ("hub", "bearing", 2)]

# par(child, parent): a -> {b, c}; b -> {d, e}; c -> {f}; d -> {g}; f -> {h}
PAR = [("b", "a"), ("c", "a"), ("d", "b"), ("e", "b"), ("f", "c"),
       ("g", "d"), ("h", "f")]


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE edge(src TEXT, dst TEXT, w INTEGER);
        CREATE TABLE contains(assembly TEXT, part TEXT, qty INTEGER);
        CREATE TABLE par(child TEXT, parent TEXT);
    """)
    conn.executemany("INSERT INTO edge VALUES (?,?,?)", EDGES)
    conn.executemany("INSERT INTO contains VALUES (?,?,?)", CONTAINS)
    conn.executemany("INSERT INTO par VALUES (?,?)", PAR)
    return conn


TC_SQL = """
WITH RECURSIVE tc(x, y) AS (
    SELECT src, dst FROM edge
  UNION
    SELECT tc.x, e.dst FROM tc JOIN edge e ON e.src = tc.y
)
SELECT x, y FROM tc ORDER BY x, y
"""


def transitive_closure(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    """All (x, y) with a non-empty path x -> y. UNION makes it terminate on cycles."""
    return set(conn.execute(TC_SQL).fetchall())


SP_SQL = """
WITH RECURSIVE sp(node, dist, path) AS (
    SELECT :src, 0, ',' || :src || ','
  UNION ALL
    SELECT e.dst, sp.dist + e.w, sp.path || e.dst || ','
    FROM sp JOIN edge e ON e.src = sp.node
    WHERE instr(sp.path, ',' || e.dst || ',') = 0      -- simple paths only
)
SELECT node, dist, path FROM (
    SELECT node, dist, path,
           ROW_NUMBER() OVER (PARTITION BY node ORDER BY dist, path) AS rn
    FROM sp)
WHERE rn = 1 ORDER BY node
"""


def shortest_paths(conn: sqlite3.Connection, src: str) -> dict[str, tuple[int, str]]:
    """Single-source shortest paths by enumerating simple paths.

    UNION ALL + growing `dist` would never reach a fixpoint on a cycle; the
    path-string check is the hand-written version of PostgreSQL's CYCLE clause.
    Exponential in general: fine for exam-sized graphs, not for real ones.
    """
    rows = conn.execute(SP_SQL, {"src": src}).fetchall()
    return {n: (d, p.strip(",")) for n, d, p in rows}


BOM_SQL = """
WITH RECURSIVE need(part, qty) AS (
    SELECT part, qty FROM contains WHERE assembly = :root
  {op}
    SELECT c.part, need.qty * c.qty
    FROM need JOIN contains c ON c.assembly = need.part
)
SELECT part, SUM(qty) FROM need
WHERE part NOT IN (SELECT assembly FROM contains)       -- leaves = base parts
GROUP BY part ORDER BY part
"""


def bill_of_materials(conn: sqlite3.Connection, root: str,
                      op: str = "UNION ALL") -> dict[str, int]:
    """Base parts needed for one `root`. op='UNION' shows the dedup pitfall."""
    assert op in ("UNION", "UNION ALL")
    return dict(conn.execute(BOM_SQL.format(op=op), {"root": root}).fetchall())


SG_SQL = """
WITH RECURSIVE sg(x, y) AS (
    SELECT p1.child, p2.child FROM par p1 JOIN par p2 ON p1.parent = p2.parent
  UNION
    SELECT p1.child, p2.child
    FROM sg JOIN par p1 ON p1.parent = sg.x JOIN par p2 ON p2.parent = sg.y
)
SELECT x, y FROM sg
"""


def same_generation(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    """sg(X,Y) :- par(X,P), par(Y,P).  sg(X,Y) :- par(X,P), sg(P,Q), par(Y,Q)."""
    return set(conn.execute(SG_SQL).fetchall())


def depth_counter_rows(conn: sqlite3.Connection, limit: int) -> int:
    """UNION does NOT save you when a column keeps growing: every (x, y, depth)
    row is new, so the fixpoint is never reached on a cyclic graph. The outer
    LIMIT stops SQLite after `limit` rows (SQLite doc 3.3 [S13]); the count
    equals the limit, i.e. without it the query would run forever."""
    sql = """
    WITH RECURSIVE r(x, y, depth) AS (
        SELECT src, dst, 1 FROM edge
      UNION
        SELECT r.x, e.dst, r.depth + 1 FROM r JOIN edge e ON e.src = r.y
    )
    SELECT count(*) FROM (SELECT * FROM r LIMIT :lim)
    """
    return conn.execute(sql, {"lim": limit}).fetchone()[0]


def working_table_trace(edges, union: bool = True, max_rounds: int = 50):
    """Pure-Python replay of the PostgreSQL WITH RECURSIVE algorithm for the
    transitive-closure query. Returns (result, [working table per round])."""
    pairs = [(s, d) for s, d, *_ in edges]
    working = list(dict.fromkeys(pairs)) if union else list(pairs)
    result = list(working)
    seen = set(result)
    rounds = [list(working)]
    while working and len(rounds) < max_rounds:
        new = [(x, d) for (x, y) in working for (s, d) in pairs if s == y]
        if union:
            new = [t for t in dict.fromkeys(new) if t not in seen]
            seen.update(new)
        result += new
        working = new
        if working:
            rounds.append(list(working))
    return result, rounds


def demo() -> None:
    conn = make_db()
    print(TC_SQL.strip())
    tc = transitive_closure(conn)
    print(f"-> {len(tc)} pairs; from a: {sorted(y for x, y in tc if x == 'a')}")
    _, rounds = working_table_trace(EDGES)
    for i, w in enumerate(rounds):
        print(f"   round {i}: {len(w)} new rows {sorted(w)}")
    print("\nshortest paths from a:")
    for node, (d, p) in shortest_paths(conn, "a").items():
        print(f"   {node}: {d:2d} via {p}")
    print("\nbill of materials for one bike:")
    good, bad = bill_of_materials(conn, "bike"), bill_of_materials(conn, "bike", "UNION")
    for part in good:
        flag = "" if good[part] == bad[part] else f"   <- UNION gives {bad[part]}"
        print(f"   {part:8s} {good[part]:3d}{flag}")
    print(f"\nsame generation: {len(same_generation(conn))} pairs")
    print(f"UNION with a growing depth column: LIMIT 100 reached "
          f"({depth_counter_rows(conn, 100)} rows) -> non-terminating without it")


if __name__ == "__main__":
    demo()
