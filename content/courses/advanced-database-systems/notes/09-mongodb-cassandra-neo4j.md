# 09 MongoDB, Cassandra, Neo4j: query languages and data modelling

> **Sourcing.** MongoDB manual [S34] (aggregation pipeline, data modelling,
> atomicity, replication, write concern, sharding); Cassandra docs [S35] (data
> modelling, Dynamo-style architecture and consistency levels); Neo4j docs [S36]
> (Cypher manual, graph database intro). Exam shapes (denormalise a relational
> schema into documents and argue pros and cons; evaluate Cypher on a given
> graph) from the 2020 exam [S6] and the block-3 cheat sheet [S5]. The MongoDB
> subset runs in `document_store.py`; **Cassandra and Neo4j are not installed:
> CQL and Cypher below are traced by hand** (the Cypher answers were
> cross-checked with networkx).

## MongoDB

**Terms**: database > **collection** (like a table, no fixed schema) > **document**
(like a row; BSON = binary JSON, nested objects and arrays); `_id` is the primary key.
Writes are atomic **per document**; `updateMany` is atomic per document, not as a
whole; multi-document transactions exist but cost more [S34].

### Queries (`document_store.Collection.find`)

```js
db.orders.find({ "items.sku": "ink" })                 // dotted path into an array: ANY element
db.orders.find({ "items.qty": { $gt: 5 } })
db.orders.find({ customer: { $in: ["ann", "cid"] }, status: "paid" })   // implicit AND
db.orders.find({ $or: [{ customer: "bob" }, { status: "open" }] })
db.orders.find({ _id: 2 }, { customer: 1, _id: 0 })   // projection
```

On the sample orders (1: ann paid pen x3 @2, ink x1 @7; 2: bob paid pen x10 @2;
3: ann open pad x2 @4; 4: cid paid ink x2 @7, pad x1 @4): `items.sku = ink` gives
1, 4; `items.qty > 5` gives 2; `items.sku $ne pen` gives 3, 4 (**no** element may equal).

### Aggregation pipeline [S34]

A pipeline is a list of **stages**; each consumes the previous stage's documents.

```js
db.orders.aggregate([
  { $match: { status: "paid" } },                        // WHERE
  { $unwind: "$items" },                                  // one document per array element
  { $group: { _id: "$items.sku",                          // GROUP BY
              revenue: { $sum: { $multiply: ["$items.qty", "$items.price"] } },
              units:   { $sum: "$items.qty" } } },
  { $sort: { revenue: -1 } }                              // ORDER BY
])
// { _id: "pen", revenue: 26, units: 13 }, { _id: "ink", revenue: 21, units: 3 }, { _id: "pad", revenue: 4, units: 1 }
```

SQL equivalent over a normalised `line(order_id, sku, qty, price)`:
`SELECT sku, SUM(qty*price), SUM(qty) FROM orders o JOIN line l ... WHERE status='paid' GROUP BY sku ORDER BY 2 DESC`.
`$lookup {from, localField, foreignField, as}` is a **left outer join** that puts
matches into an array; `$unwind` of an empty array drops the document (unless
`preserveNullAndEmptyArrays`). Revenue by city via `$lookup` on customers:
Graz 20, Wien 31 (`document_store.REVENUE_BY_CITY`, checked against SQLite).

### Data modelling: embed or reference

| relationship | typical choice (cheat sheet [S5]) |
|---|---|
| 1 : few (address of a user) | embed in the parent |
| 1 : many, bounded (order lines) | embed, or array of references in the parent |
| 1 : huge (log lines of a host) | reference the parent from the child |
| m : n | two collections with reference arrays, or a link collection as in SQL |

**Denormalisation** (copying data into the documents that read it), in the
setting of the 2020 exam [S6]: store `movie.title, genre` inside each `watched` document.
Pro: "most watched genre" reads one collection, no join. Con: changing a movie's
genre must rewrite every `watched` document of that movie, and not atomically.
Rule: denormalise data that is read often and changed rarely.

**Replication**: a replica set has one **primary** (takes all writes, records
them in the **oplog**) and secondaries that replay it; if the primary fails an
eligible secondary is **elected** [S34]. **Write concern** `w: "majority"`
acknowledges after a majority of voting members wrote durably; read concern
`"majority"` reads only majority-committed data. **Sharding**: the collection is
split by a **shard key**, hashed (even spread, range queries go everywhere) or
ranged (range queries hit few shards, risk of hot spots); clients talk to the
`mongos` router; each shard is a replica set [S34].

## Cassandra

**Query-driven modelling** [S35]: no joins, so design one table per query and
duplicate data between tables (denormalise). Primary key = **partition key**
(hashed onto the ring, decides the node) + **clustering columns** (sort order
inside a partition).

```sql
CREATE TABLE readings_by_sensor_day (
  sensor_id text, day date, ts timestamp, value double,
  PRIMARY KEY ((sensor_id, day), ts)            -- partition (sensor_id, day), cluster ts
) WITH CLUSTERING ORDER BY (ts DESC);

SELECT ts, value FROM readings_by_sensor_day
 WHERE sensor_id = 's1' AND day = '2028-04-16' AND ts > '2028-04-16 12:00';   -- one partition, a slice
SELECT * FROM readings_by_sensor_day WHERE value > 30;   -- rejected without ALLOW FILTERING
```

Rules: equality on **all** partition-key columns; ranges only on clustering
columns, left to right. Composite partition keys bound partition size (one
partition per sensor *per day*).

**Tunable consistency** [S35]: per request `ONE`, `TWO`, `QUORUM` (majority of
the replication factor), `ALL`, `LOCAL_QUORUM`...; `QUORUM` writes + `QUORUM`
reads satisfy $R + W > N$. Storage is an LSM tree (note 08).

## Neo4j and Cypher [S36]

**Property graph**: nodes with **labels** and properties; relationships with one
**type**, a direction and properties. Cypher describes patterns in ASCII art:
`(n:Label {key: value})`, `-[:TYPE]->`, `<-[:TYPE]-`, `-[:TYPE]-` (either
direction), `-[:TYPE*1..3]->` (1 to 3 hops), `p = shortestPath((a)-[*]->(b))`.

Graph: ann->bob, bob->cid, ann->cid, cid->dan, dan->ann, all `:FOLLOWS`, nodes `:Person {name}`.

```cypher
// people followed by someone ann follows, but not by ann herself
MATCH (a:Person {name: 'ann'})-[:FOLLOWS]->()-[:FOLLOWS]->(f)
WHERE f <> a AND NOT (a)-[:FOLLOWS]->(f)
RETURN DISTINCT f.name                                  // dan  (cid is excluded: ann follows cid)

MATCH (a:Person {name: 'ann'})-[:FOLLOWS*1..2]->(x) RETURN DISTINCT x.name   // bob, cid, dan

MATCH p = shortestPath((:Person {name: 'ann'})-[:FOLLOWS*]->(:Person {name: 'dan'}))
RETURN [n IN nodes(p) | n.name], length(p)              // [ann, cid, dan], 2

MATCH (p:Person)<-[:FOLLOWS]-(f) RETURN p.name, count(f) AS followers
                                                        // ann 1, bob 1, cid 2, dan 1
```

Writing: `CREATE (:Person {name: 'eve'})`, `MERGE` (create if the pattern is
missing), `MATCH ... SET p.age = 23`, `MATCH ... DETACH DELETE p` (a node with
relationships cannot be deleted without `DETACH`). Aggregates: `count`, `sum`,
`avg`, `collect` (to a list). Within one `MATCH`, a relationship is not
traversed twice in the same path (default match mode) [S36].

**Relational to graph**: table -> label, row -> node, column -> property,
foreign key or link table -> relationship [S5].

## Pitfalls

- Mongo filter on an array field matches if **any** element matches; `$ne` requires **no** element to match.
- `$unwind` multiplies documents; count after it counts elements, not orders.
- Cassandra: a query not starting with the full partition key is either rejected or a cluster-wide scan.
- Cypher patterns are directed unless written `-[]-`; `count(f)` groups by the other returned expressions.
- Denormalisation is not the same as embedding an m:n relationship; the 2020 solution key penalised calling the latter a denormalisation [S6].

## Exam-style questions

1. *Collection `users {name, emails: [..]}`. Query "users having an email ending in @tuwien.ac.at"?* `db.users.find({emails: {$regex: "@tuwien\\.ac\\.at$"}})`: the regex is applied to each array element.
2. *Give a Cassandra table for "latest 10 orders of a customer".* `PRIMARY KEY ((customer_id), order_ts, order_id) WITH CLUSTERING ORDER BY (order_ts DESC)`; `SELECT ... WHERE customer_id = ? LIMIT 10`.
3. *On the graph above, `MATCH (x)-[:FOLLOWS]->(y)-[:FOLLOWS]->(x) RETURN x.name`?* Empty: no pair follows each other.
4. *Pipeline to count paid orders per customer, most first?* `[{$match: {status: "paid"}}, {$group: {_id: "$customer", n: {$sum: 1}}}, {$sort: {n: -1}}]` gives ann 1, bob 1, cid 1.
5. *Name one query that profits and one update that suffers from embedding customer city into every order.* Revenue by city reads orders only; a customer moving city rewrites all their orders.

## Code

- `document_store.Collection` (`find`, `aggregate`, `insert_many`), `document_store.Database`, `document_store.matches`, `document_store.evaluate`, pipelines `document_store.REVENUE_BY_SKU` and `document_store.REVENUE_BY_CITY`; tests compare with pandas and SQLite.
