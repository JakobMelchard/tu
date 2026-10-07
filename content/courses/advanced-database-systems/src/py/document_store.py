"""A JSON document store with a MongoDB-style find() and aggregation pipeline,
note 09. Semantics follow the MongoDB manual [S34] for the subset implemented:

  filters   {"field": value}, dotted paths "a.b", operators $eq $ne $gt $gte
            $lt $lte $in $nin $exists, $and / $or; a filter on an array field
            matches if ANY element matches (MongoDB's array semantics)
  stages    $match $project $addFields $unwind $group $sort $limit $skip
            $lookup $count
  $group    _id: "$field" | {name: "$field", ...} | None;
            accumulators $sum $avg $min $max $push $addToSet $first $last
  exprs     "$field", literals, {"$multiply": [...]}, {"$add": [...]},
            {"$size": "$arr"}

Not MongoDB: no indexes, no types beyond Python's, no update operators.
Run: python document_store.py
"""
from __future__ import annotations

import copy
from collections import defaultdict

MISSING = object()


def get_path(doc, path: str):
    """Resolve 'a.b.c'. Through an array, collect the values of all elements."""
    cur = doc
    for part in path.split("."):
        if isinstance(cur, list):
            vals = [get_path(x, part) for x in cur if isinstance(x, dict)]
            cur = [v for v in vals if v is not MISSING]
        elif isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return MISSING
    return cur


CMP = {"$eq": lambda a, b: a == b, "$ne": lambda a, b: a != b,
       "$gt": lambda a, b: a is not None and a > b, "$gte": lambda a, b: a is not None and a >= b,
       "$lt": lambda a, b: a is not None and a < b, "$lte": lambda a, b: a is not None and a <= b,
       "$in": lambda a, b: a in b, "$nin": lambda a, b: a not in b}


def _cond_holds(value, cond) -> bool:
    if isinstance(cond, dict) and cond and all(k.startswith("$") for k in cond):
        for op, arg in cond.items():
            if op == "$exists":
                if (value is not MISSING) != arg:
                    return False
            elif op == "$ne" or op == "$nin":
                vals = value if isinstance(value, list) else [value]
                if not all(CMP[op](v, arg) for v in vals):
                    return False
            elif not _any(value, lambda v: CMP[op](v, arg)):
                return False
        return True
    return _any(value, lambda v: v == cond) or value == cond


def _any(value, pred) -> bool:
    if value is MISSING:
        return False
    if isinstance(value, list):
        return any(pred(v) for v in value)
    try:
        return pred(value)
    except TypeError:
        return False


def matches(doc, flt: dict) -> bool:
    for key, cond in flt.items():
        if key == "$and":
            if not all(matches(doc, f) for f in cond):
                return False
        elif key == "$or":
            if not any(matches(doc, f) for f in cond):
                return False
        elif not _cond_holds(get_path(doc, key), cond):
            return False
    return True


def evaluate(expr, doc):
    if isinstance(expr, str) and expr.startswith("$"):
        v = get_path(doc, expr[1:])
        return None if v is MISSING else v
    if isinstance(expr, dict) and len(expr) == 1:
        (op, arg), = expr.items()
        if op == "$multiply":
            out = 1
            for a in arg:
                out *= evaluate(a, doc)
            return out
        if op == "$add":
            return sum(evaluate(a, doc) for a in arg)
        if op == "$size":
            return len(evaluate(arg, doc))
    if isinstance(expr, dict):
        return {k: evaluate(v, doc) for k, v in expr.items()}
    return expr


def _group(docs, spec):
    idspec = spec["_id"]
    groups: dict = {}
    order = []
    for d in docs:
        key = evaluate(idspec, d)
        hk = repr(key)
        if hk not in groups:
            groups[hk] = (key, defaultdict(list))
            order.append(hk)
        for field, acc in spec.items():
            if field != "_id":
                (op, e), = acc.items()
                groups[hk][1][field].append(evaluate(e, d))
    out = []
    for hk in order:
        key, cols = groups[hk]
        row = {"_id": key}
        for field, acc in spec.items():
            if field == "_id":
                continue
            op = next(iter(acc))
            vs = cols[field]
            nums = [v for v in vs if isinstance(v, (int, float))]
            row[field] = {"$sum": lambda: sum(nums),
                          "$avg": lambda: sum(nums) / len(nums) if nums else None,
                          "$min": lambda: min(v for v in vs if v is not None),
                          "$max": lambda: max(v for v in vs if v is not None),
                          "$push": lambda: list(vs),
                          "$addToSet": lambda: list({repr(v): v for v in vs}.values()),
                          "$first": lambda: vs[0], "$last": lambda: vs[-1]}[op]()
        out.append(row)
    return out


class Collection:
    def __init__(self, name: str, db: "Database"):
        self.name, self.db, self.docs = name, db, []

    def insert_many(self, docs) -> None:
        for d in docs:
            d = copy.deepcopy(d)
            d.setdefault("_id", len(self.docs) + 1)
            self.docs.append(d)

    def find(self, flt: dict | None = None, projection: dict | None = None) -> list[dict]:
        out = [d for d in self.docs if matches(d, flt or {})]
        return [self._project(d, projection) for d in out] if projection else out

    @staticmethod
    def _project(d, spec):
        if all(v in (0, False) for v in spec.values()):
            return {k: v for k, v in d.items() if k not in spec}
        out = {"_id": d["_id"]} if spec.get("_id", 1) else {}
        for k, v in spec.items():
            if k != "_id" and v not in (0, False):
                val = evaluate(v if not isinstance(v, (bool, int)) else "$" + k, d)
                out[k] = val
        return out

    def aggregate(self, pipeline: list[dict]) -> list[dict]:
        docs = copy.deepcopy(self.docs)
        for stage in pipeline:
            (op, arg), = stage.items()
            if op == "$match":
                docs = [d for d in docs if matches(d, arg)]
            elif op == "$project":
                docs = [self._project(d, arg) for d in docs]
            elif op == "$addFields":
                docs = [{**d, **{k: evaluate(e, d) for k, e in arg.items()}} for d in docs]
            elif op == "$unwind":                    # one output doc per array element
                f = arg.lstrip("$")
                docs = [{**d, f: x} for d in docs for x in (d.get(f) or [])]
            elif op == "$group":
                docs = _group(docs, arg)
            elif op == "$sort":                      # stable sorts, last key first
                for k, direction in reversed(list(arg.items())):
                    docs.sort(key=lambda d: (get_path(d, k) is MISSING, get_path(d, k)),
                              reverse=direction < 0)
            elif op == "$limit":
                docs = docs[:arg]
            elif op == "$skip":
                docs = docs[arg:]
            elif op == "$count":
                docs = [{arg: len(docs)}]
            elif op == "$lookup":                    # left outer join into an array
                other = self.db[arg["from"]].docs
                docs = [{**d, arg["as"]: [copy.deepcopy(o) for o in other
                                          if _any(get_path(o, arg["foreignField"]),
                                                  lambda v: v == get_path(d, arg["localField"]))]}
                        for d in docs]
            else:
                raise ValueError(f"unsupported stage {op}")
        return docs


class Database(dict):
    def __missing__(self, name):
        self[name] = Collection(name, self)
        return self[name]


ORDERS = [
    {"_id": 1, "customer": "ann", "status": "paid",
     "items": [{"sku": "pen", "qty": 3, "price": 2}, {"sku": "ink", "qty": 1, "price": 7}]},
    {"_id": 2, "customer": "bob", "status": "paid", "items": [{"sku": "pen", "qty": 10, "price": 2}]},
    {"_id": 3, "customer": "ann", "status": "open", "items": [{"sku": "pad", "qty": 2, "price": 4}]},
    {"_id": 4, "customer": "cid", "status": "paid",
     "items": [{"sku": "ink", "qty": 2, "price": 7}, {"sku": "pad", "qty": 1, "price": 4}]},
]
CUSTOMERS = [{"_id": "ann", "city": "Wien"}, {"_id": "bob", "city": "Graz"},
             {"_id": "cid", "city": "Wien"}]

REVENUE_BY_SKU = [
    {"$match": {"status": "paid"}},
    {"$unwind": "$items"},
    {"$group": {"_id": "$items.sku",
                "revenue": {"$sum": {"$multiply": ["$items.qty", "$items.price"]}},
                "units": {"$sum": "$items.qty"}}},
    {"$sort": {"revenue": -1, "_id": 1}},
]
REVENUE_BY_CITY = [
    {"$match": {"status": "paid"}},
    {"$lookup": {"from": "customers", "localField": "customer",
                 "foreignField": "_id", "as": "cust"}},
    {"$unwind": "$cust"}, {"$unwind": "$items"},
    {"$group": {"_id": "$cust.city",
                "revenue": {"$sum": {"$multiply": ["$items.qty", "$items.price"]}}}},
    {"$sort": {"_id": 1}},
]


def make_db() -> Database:
    db = Database()
    db["orders"].insert_many(ORDERS)
    db["customers"].insert_many(CUSTOMERS)
    return db


def demo() -> None:
    db = make_db()
    print("find items.sku = 'ink':", [d["_id"] for d in db["orders"].find({"items.sku": "ink"})])
    print("find items.qty > 5:    ", [d["_id"] for d in db["orders"].find({"items.qty": {"$gt": 5}})])
    print("revenue by sku:")
    for row in db["orders"].aggregate(REVENUE_BY_SKU):
        print("   ", row)
    print("revenue by city ($lookup):", db["orders"].aggregate(REVENUE_BY_CITY))


if __name__ == "__main__":
    demo()
