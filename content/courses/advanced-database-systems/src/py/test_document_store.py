import sqlite3

import pandas as pd

import document_store as ds


def lines_df():
    rows = [(o["_id"], o["customer"], o["status"], it["sku"], it["qty"], it["price"])
            for o in ds.ORDERS for it in o["items"]]
    return pd.DataFrame(rows, columns=["oid", "customer", "status", "sku", "qty", "price"])


def test_revenue_by_sku_against_pandas():
    df = lines_df().query("status == 'paid'").assign(rev=lambda d: d.qty * d.price)
    ref = df.groupby("sku").agg(revenue=("rev", "sum"), units=("qty", "sum")).reset_index()
    ref = ref.sort_values(["revenue", "sku"], ascending=[False, True])
    got = ds.make_db()["orders"].aggregate(ds.REVENUE_BY_SKU)
    assert [(r["_id"], r["revenue"], r["units"]) for r in got] == \
        [tuple(x) for x in ref.itertuples(index=False)]


def test_lookup_against_sql_join():
    conn = sqlite3.connect(":memory:")
    lines_df().to_sql("line", conn)
    pd.DataFrame(ds.CUSTOMERS).rename(columns={"_id": "name"}).to_sql("customer", conn)
    ref = conn.execute("""SELECT c.city, SUM(l.qty * l.price) FROM line l
                          JOIN customer c ON c.name = l.customer
                          WHERE l.status = 'paid' GROUP BY c.city ORDER BY c.city""").fetchall()
    got = ds.make_db()["orders"].aggregate(ds.REVENUE_BY_CITY)
    assert [(r["_id"], r["revenue"]) for r in got] == ref


def test_find_array_semantics():
    orders = ds.make_db()["orders"]
    ids = lambda f: [d["_id"] for d in orders.find(f)]
    assert ids({"items.sku": "ink"}) == [1, 4]              # any element matches
    assert ids({"items.sku": {"$ne": "pen"}}) == [3, 4]     # no element equals
    assert ids({"items.qty": {"$gte": 3}}) == [1, 2]
    assert ids({"$or": [{"customer": "bob"}, {"status": "open"}]}) == [2, 3]
    assert ids({"customer": {"$in": ["ann", "cid"]}, "status": "paid"}) == [1, 4]
    assert ids({"coupon": {"$exists": False}}) == [1, 2, 3, 4]


def test_projection_group_count_unwind():
    db = ds.make_db()
    assert db["orders"].find({"_id": 2}, {"customer": 1, "_id": 0}) == [{"customer": "bob"}]
    per_customer = db["orders"].aggregate([
        {"$group": {"_id": "$customer", "n": {"$sum": 1}, "ids": {"$push": "$_id"}}},
        {"$sort": {"_id": 1}}])
    assert per_customer == [{"_id": "ann", "n": 2, "ids": [1, 3]},
                            {"_id": "bob", "n": 1, "ids": [2]},
                            {"_id": "cid", "n": 1, "ids": [4]}]
    db["orders"].insert_many([{"_id": 5, "customer": "dan", "status": "open", "items": []}])
    n_lines = db["orders"].aggregate([{"$unwind": "$items"}, {"$count": "n"}])
    assert n_lines == [{"n": 6}]                            # empty array: document dropped
    sizes = db["orders"].aggregate([{"$addFields": {"k": {"$size": "$items"}}},
                                    {"$match": {"k": {"$gt": 1}}}, {"$project": {"k": 1}}])
    assert sizes == [{"_id": 1, "k": 2}, {"_id": 4, "k": 2}]
