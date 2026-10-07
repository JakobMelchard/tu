"""ER schema -> relational schema, and relational schema -> SQL DDL (notes 01, 03).

Mapping rules of [S6] ch. 6, one per construct:
  strong entity E(key, attrs)      table E, PK = key
  multivalued attribute m of E     table E_m(key of E, m), PK both, FK -> E, cascade
  weak entity W of owner O         table W(key of O, partial key, attrs), PK = both,
                                   FK -> O ON DELETE CASCADE (existence dependency)
  1:N relationship R (E1 1, E2 N)  FK to E1 in E2's table (+ R's attributes);
                                   NOT NULL iff E2 participates totally
  1:1 relationship                 FK on the side with total participation, UNIQUE
  N:M or n-ary relationship        own table, PK = the keys of the N-sides,
                                   FK to each participant
  ISA (sub of super)               table per subclass: PK = super's key, FK -> super
                                   (the other two strategies are discussed in note 03)
Composite attributes are assumed flattened before mapping.
"""
import sqlite3


def transform(er):
    ents, rels = er["entities"], er.get("relationships", {})
    tables = {}

    def key_of(e):
        spec = ents[e]
        if spec.get("owner"):
            return key_of(spec["owner"]) + spec["key"]
        if spec.get("isa"):
            return key_of(spec["isa"])
        return spec["key"]

    def prefixed(e):
        return [f"{e.lower()}_{k}" for k in key_of(e)]

    for e, spec in ents.items():
        t = {"cols": [], "pk": [], "fks": [], "unique": [], "not_null": []}
        if spec.get("owner"):
            own = prefixed(spec["owner"])
            t["cols"] = own + spec["key"]
            t["pk"] = own + spec["key"]
            t["fks"].append((own, spec["owner"], "CASCADE"))
        elif spec.get("isa"):
            t["cols"], t["pk"] = list(key_of(e)), list(key_of(e))
            t["fks"].append((key_of(e), spec["isa"], "CASCADE"))
        else:
            t["cols"], t["pk"] = list(spec["key"]), list(spec["key"])
        t["cols"] += spec.get("attrs", [])
        tables[e] = t
        for m in spec.get("multi", []):
            tables[f"{e}_{m}"] = {"cols": key_of(e) + [m], "pk": key_of(e) + [m],
                                  "fks": [(key_of(e), e, "CASCADE")], "unique": [], "not_null": []}

    for r, spec in rels.items():
        ends = spec["ends"]                          # [(entity, "1" | "N", total?)]
        ones = [x for x in ends if x[1] == "1"]
        if len(ends) == 2 and len(ones) >= 1:
            if len(ones) == 2:                       # 1:1: FK on the total side
                (a, _, ta), (b, _, tb) = ends
                host, ref, total = (a, b, ta) if ta or not tb else (b, a, tb)
            else:
                ref = ones[0][0]
                host, _, total = next(x for x in ends if x[1] == "N")
            fk = [f"{r}_{c}" for c in key_of(ref)]
            t = tables[host]
            t["cols"] += fk + spec.get("attrs", [])
            t["fks"].append((fk, ref, "SET NULL" if not total else "RESTRICT"))
            if total:
                t["not_null"] += fk
            if len(ones) == 2:
                t["unique"].append(fk)
        else:                                        # N:M or n-ary
            cols, pk, fks = [], [], []
            for e, card, _ in ends:
                c = prefixed(e)
                cols += c
                fks.append((c, e, "CASCADE"))
                if card == "N" or all(x[1] == "1" for x in ends):
                    pk += c
            tables[r] = {"cols": cols + spec.get("attrs", []), "pk": pk, "fks": fks,
                         "unique": [], "not_null": []}
    return tables


def ddl(tables, key_cols_of=None):
    """CREATE TABLE statements; referenced columns are the target's primary key."""
    order, out = _dependency_order(tables), []
    for name in order:
        t = tables[name]
        lines = [f"  {c}{' NOT NULL' if c in t['not_null'] else ''}" for c in t["cols"]]
        lines.append(f"  PRIMARY KEY ({', '.join(t['pk'])})")
        for u in t["unique"]:
            lines.append(f"  UNIQUE ({', '.join(u)})")
        for cols, ref, action in t["fks"]:
            lines.append(f"  FOREIGN KEY ({', '.join(cols)}) REFERENCES {ref} "
                         f"({', '.join(tables[ref]['pk'])}) ON DELETE {action}")
        out.append(f"CREATE TABLE {name} (\n" + ",\n".join(lines) + "\n);")
    return "\n".join(out)


def _dependency_order(tables):
    done, order = set(), []

    def visit(n):
        if n in done:
            return
        done.add(n)
        for _, ref, _ in tables[n]["fks"]:
            if ref != n:
                visit(ref)
        order.append(n)
    for n in tables:
        visit(n)
    return order


def university():
    return {
        "entities": {
            "Professor": {"key": ["pid"], "attrs": ["name", "rank"]},
            "Student": {"key": ["sid"], "attrs": ["name", "semester"], "multi": ["email"]},
            "Course": {"key": ["cid"], "attrs": ["title", "ects"]},
            "Room": {"key": ["rid"], "attrs": ["seats"]},
            "Section": {"key": ["sno"], "owner": "Course", "attrs": ["weekday"]},
            "Tutor": {"isa": "Student", "attrs": ["hours"]},
        },
        "relationships": {
            "teaches": {"ends": [("Professor", "1", False), ("Course", "N", True)]},
            "attends": {"ends": [("Student", "N", False), ("Course", "N", False)], "attrs": ["grade"]},
            "office": {"ends": [("Professor", "1", True), ("Room", "1", False)]},
            "leads": {"ends": [("Tutor", "1", False), ("Section", "N", False)]},
        },
    }


if __name__ == "__main__":
    tables = transform(university())
    for name, t in tables.items():
        print(f"{name}({', '.join(c + ('*' if c in t['pk'] else '') for c in t['cols'])})")
    sql = ddl(tables)
    con = sqlite3.connect(":memory:")
    con.executescript(sql)
    print(f"{len(tables)} tables, DDL accepted by sqlite {sqlite3.sqlite_version}")
