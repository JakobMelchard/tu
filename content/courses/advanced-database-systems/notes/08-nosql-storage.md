# 08 NoSQL data models and storage: partitioning, LSM trees, column stores

> **Sourcing.** Data-model topics and emphasis from the block-3 cheat sheet
> [S5] and the 2020 exam [S6]; consistent hashing: Karger et al. [S32] and
> Dynamo [S24 4.2]; LSM trees: O'Neil et al. [S33], Bigtable [S25 2, 5.3-5.4],
> Cassandra storage engine [S35]; column-store compression: Abadi, Madden,
> Ferreira [S40]. Code: `nosql.py`.

## Why NoSQL

Relational strengths: a formal model, one standard query language, ACID
transactions, integration of many applications on one schema. Pain points at
web scale: a fixed schema, nested or graph-shaped data split over many tables
and re-joined, sparse attributes (many NULLs), and scaling *out* on commodity
nodes. NoSQL systems give up some of: joins, schemas, multi-item transactions,
strong consistency, in exchange for horizontal scaling and availability [S5].

## Four data models

**Aggregate**: a unit of data read and written together (an order with its lines).
Key-value, document and wide-column stores are aggregate-oriented; graph stores are not.

| model | the value is | queried by | examples | fits |
|---|---|---|---|---|
| key-value | opaque bytes; only the application knows the structure | key only (get/put/delete) | Riak, Dynamo, Redis | sessions, carts, caches |
| document | a nested JSON/BSON document the DBMS understands | key, any field, secondary indexes, aggregation | MongoDB, CouchDB | catalogues, content, logs |
| wide-column | rows of column families; sparse, versioned cells | row key (range), column family | Bigtable, HBase, Cassandra | time series, huge sparse tables |
| graph | nodes and relationships, both with properties | traversals, pattern matching | Neo4j | social networks, recommendations, ownership chains |

Same data, four shapes (a user and her orders):

```
KV:        "user:17"  -> 0x7b2261...                       (a blob)
document:  {_id: 17, name: "Ann", orders: [{id: 1, total: 13}, {id: 3, total: 8}]}
wide-col:  row "17" | info:name="Ann" | orders:1=13 | orders:3=8       (qualifiers are data)
graph:     (:User {id: 17, name: "Ann"})-[:PLACED]->(:Order {id: 1, total: 13})
```

## Partitioning with consistent hashing [S32], [S24 4.2]

**Partitioning** (sharding) assigns each key to a node. With $\text{hash}(k) \bmod m$
nearly every key moves when $m$ changes. **Consistent hashing** maps nodes and keys
onto a ring $[0, 2^{32})$; a key belongs to the first node clockwise. Adding a node
moves only the keys between it and its predecessor: an expected fraction $1/(m+1)$.
**Virtual nodes** (each physical node at many ring positions) even out the load
and spread a failed node's keys over many successors. Replicas: the key's
**preference list** = the next $N$ distinct physical nodes clockwise.

Worked (`nosql.demo`, 2 000 keys, 64 virtual nodes each): going from 4 to 5
nodes moves **0.18** of the keys with the ring (ideal $1/5 = 0.2$) and **0.79**
with mod-hashing (ideal $4/5$); every moved key moves *to the new node*
(`test_ring_moves_few_keys_on_join`).

## LSM trees [S33], [S25 5.3-5.4]

A **log-structured merge tree** turns random writes into sequential ones.

- **Write**: append to a commit log (durability), insert into the in-memory
  **memtable** (sorted). When full, flush it as an immutable sorted file, an **SSTable** (sorted string table).
- **Delete**: write a **tombstone** (a deletion marker); older SSTables still hold the key.
- **Read**: memtable, then SSTables newest to oldest; the first hit wins. A
  per-SSTable **Bloom filter** (bit array, $k$ hash functions; no false negatives,
  false-positive rate $\approx (1 - e^{-kn/m})^k$) skips files without the key.
- **Compaction**: merge SSTables (a $k$-way merge of sorted runs, linear time),
  keep the newest version of each key, drop shadowed versions, and drop
  tombstones once no older file can hold the key (full merge).
- Trade-off vs a B-tree: cheap writes, reads touch several files (read
  amplification), data rewritten by compactions (write amplification).

Worked (`nosql.demo`, memtable limit 3): puts `a b c | a b d | e f g | a h`,
delete `b`: four SSTables, the newest `{a:9, b:TOMBSTONE, h:10}`. `get(a) = 9`
from the newest file, `get(b) = None` because the tombstone shadows `b:4` and
`b:1`; both reads stop at the newest file (2 probes in total). Full compaction
leaves one run `a:9 c:2 d:5 e:6 f:7 g:8 h:10`.

## Bigtable's wide-column model [S25 2]

"A sparse, distributed, persistent multi-dimensional sorted map":
$(\text{row}: \text{string}, \text{column}: \text{string}, \text{time}: \text{int64}) \to \text{string}$.
Rows are sorted by key and split into **tablets** (row ranges, the unit of
distribution); columns are `family:qualifier`, families declared up front,
qualifiers arbitrary; each cell keeps several timestamped versions. Row key
design matters: reversed URLs `com.cnn.www` keep one site's pages adjacent.

## Column stores and compression [S40], [S5]

A **column store** keeps each column as its own array (tuple $i$ = position $i$
in every column). Analytics read few columns of many rows: less I/O, and a column
holds similar values, so it compresses well. Schemes (`nosql.rle`,
`nosql.dictionary_encode`, `nosql.bitmap_encode`) on `AT AT AT DE DE CH CH CH CH`:

| scheme | encoding | good when |
|---|---|---|
| run-length (RLE) | `(AT,3) (DE,2) (CH,4)` | sorted or clustered column; worse than nothing on alternating values |
| dictionary | dict `[AT, CH, DE]`, codes `0 0 0 2 2 1 1 1 1` | few distinct wide values (strings) |
| bitmap | `AT:111000000`, `CH:000001111`, `DE:000110000` | very few distinct values; predicates become bit operations |

Operators can work **on compressed data**: `SUM` over an RLE column is
$\sum \text{value} \times \text{run length}$ [S40]. **Late materialisation**: filter
on individual columns by position lists, build output tuples only at the end.
Updates are expensive on compressed columns: buffer them in a write store and merge.

## Pitfalls

- A key-value store cannot filter on a field inside the value; a document store can.
- Consistent hashing without virtual nodes gives very uneven partitions for small $m$.
- In an LSM tree, a delete *adds* data until compaction.
- A Bloom filter answers "definitely not" or "maybe", never "definitely yes".
- Wide-column is not the same as a column store: Cassandra keeps a partition's rows together, sorted by clustering key [S35]; a column store keeps each column apart [S40].

## Exam-style questions

1. *True or false: in a key-value store values cannot be nested.* False: the value may be anything, including nested JSON; the store just does not interpret it.
2. *Ring with 10 nodes (many virtual nodes); an 11th joins. Fraction of keys that move, and where to?* About $1/11$, all to the new node.
3. *LSM: `put(x,1)`, flush, `delete(x)`, flush, `put(x,2)`. What does `get(x)` return, and after a full compaction what remains?* 2 (memtable wins); `x:2` only.
4. *Which compression for a sorted `date` column? For a `country` column with 30 values in random order?* RLE; dictionary (or bitmap).
5. *Why do graph databases handle a 5-hop friends-of-friends query better than SQL joins?* Relationships are stored natively with their nodes (the cheat sheet [S5]: "as pointers"), so each hop follows stored connections instead of joining the whole edge table again [S36].

## Code

- `nosql.ConsistentHashRing` (`owner`, `preference_list`, `add`, `remove`), `nosql.moved_fraction`, `nosql.LSMTree` (`put`, `delete`, `get`, `flush`, `compact`, `probes`), `nosql.Bloom`, `nosql.rle`, `nosql.dictionary_encode`, `nosql.bitmap_encode`.
