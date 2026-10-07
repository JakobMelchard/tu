# 07 Physical data organisation

> **Sourcing.** [S6] ch. 13 (records, slotted pages, file organisations,
> buffer replacement, columnar storage) and ch. 15 (cost measures, external
> sort); [S21] fileformat2.html (sqlite's b-tree page as a concrete slotted
> page); [S16] for the place of the storage layer in a DBMS. The heap/sorted
> cost table is derived here in a pure page-I/O model; numbers are from
> `python src/py/storage.py`.

## Model and definitions

The unit of transfer between disk and memory is the **page** (block), a few KiB.
[S6] ch. 15 measures cost by **block transfers** and **seeks**; below, as in most
exam arithmetic, only page I/Os are counted and CPU is ignored.

| term | definition |
|---|---|
| record | the bytes of one tuple; fixed-length (all fields fixed) or variable-length (strings, NULLs, several record types) [S6] |
| blocking factor | records per page, $\mathit{bf} = \lfloor (B - H)/R \rfloor$ for page size $B$, header $H$, record size $R$ (records not spanning pages) |
| file size | $b = \lceil n / \mathit{bf} \rceil$ pages for $n$ records |
| slotted page | header with a **slot directory** (offset, length per record) growing from the front, records packed from the back; free space in the middle [S6] |
| record id (rid) | (page number, slot number); stable while the record moves **inside** its page |
| heap file | records anywhere there is space; a **free-space map** finds pages with room [S6] |
| sequential (sorted) file | records ordered by a search key; overflow pages when full [S6] |
| hash file | page chosen by a hash of a key (note 08) |
| multitable clustering | rows of several relations that are joined often stored together [S6] |
| buffer manager | keeps pages in memory frames; **pinned** pages may not be evicted; replacement LRU, MRU, toss-immediate [S6] |
| column store | each attribute stored separately: good for scans of few columns, bad for fetching whole rows [S6] |

Why the slot directory: other structures (indexes) point to a record by rid. If
a record grows or the page is compacted, only the slot's offset changes; the
rid stays valid. Deleting a record sets its slot to empty rather than shifting
later slots. sqlite's b-tree page has the same layout: a cell-pointer array after
the page header and a cell content area growing from the end of the page [S21].

LRU is bad for the nested-loop join's inner relation: it is scanned repeatedly,
and LRU evicts exactly the page that will be needed next; MRU fits that pattern
[S6].

## Cost of the basic operations (derived)

$b$ pages, search key = ordering key of the sorted file, unique; binary search
reads $\lceil \log_2 b \rceil$ pages; a range query matches $k$ pages.

| operation | heap file | sorted file |
|---|---|---|
| full scan | $b$ | $b$ |
| equality on key | $b/2$ average, $b$ worst (stop at the hit) | $\lceil\log_2 b\rceil$ |
| equality on non-key | $b$ (all duplicates must be found) | $\lceil\log_2 b\rceil + $ matching pages $- 1$ |
| range on key | $b$ | $\lceil\log_2 b\rceil + k - 1$ |
| insert | 2 (read and write the last page, or a page with free space) | $\lceil\log_2 b\rceil + b$ (find the place, then read and write the half file that shifts) |
| delete (given rid) | 2 | as insert if records are kept packed; 2 with tombstones |

The sorted file buys fast search with expensive insertion; indexes (note 08)
buy both at the price of extra pages.

### Worked example

4096-byte pages with a 96-byte header, 100-byte records, $10^6$ records:

$$\mathit{bf} = \lfloor (4096 - 96)/100 \rfloor = 40,\qquad b = \lceil 10^6 / 40 \rceil = 25{,}000.$$

Equality search on the key: heap $12{,}500$ pages on average; sorted
$\lceil \log_2 25{,}000 \rceil = 15$. Range with 10 matching pages on a
1000-page file: heap 1000, sorted $10 + 10 - 1 = 19$
(`storage.file_costs(1000, match_pages=10)`).

## External merge sort

Sorting $b$ pages with $M$ buffer pages ([S6] ch. 15):

1. **Run generation**: read $M$ pages, sort in memory, write a run:
   $\lceil b/M \rceil$ runs of $M$ pages.
2. **Merge passes**: merge $M - 1$ runs at a time (one input page each, one
   output page), repeat until one run is left.

$$\text{passes} = 1 + \left\lceil \log_{M-1} \lceil b/M \rceil \right\rceil,
\qquad \text{I/O} = 2b \cdot \text{passes}.$$

[S6] does not count the final write (the result goes to the next operator):
$b\,(2\lceil\log_{M-1}(b/M)\rceil + 1)$.

Worked: $b = 1000$, $M = 5$: $200$ runs; merging 4 at a time gives
$200 \to 50 \to 13 \to 4 \to 1$, four merge passes, **5 passes** total,
$10{,}000$ page I/Os including the final write, $9{,}000$ in [S6]'s count.
`storage.external_sort` sorts 10,000 records this way and counts the same.
With $M = 32$: $32$ runs but only 31-way merges, so $32 \to 2 \to 1$: **3 passes**,
not 2 (practice item P12). [S6]'s own example: $M = 11$ and 90 runs: one pass
leaves 9 runs, a second finishes (`test_storage.py::test_silberschatz_merge_example`).

Two passes suffice iff $\lceil b/M \rceil \le M - 1$, i.e. roughly $b \le M^2$:
with 4 KiB pages and 100 MiB of buffer ($M = 25{,}600$) that is about 2.5 TiB.

## Pitfalls

- Records per page is a floor, pages per file a ceiling.
- A merge pass merges $M - 1$ runs, not $M$ (one frame is the output buffer).
- Pass counts include run generation; I/O counts may or may not include the
  final write: say which.
- A deleted record's slot is not reused by shifting; rids elsewhere must stay valid.
- Heap-file equality search on a non-key cannot stop at the first hit.

## Exam-style questions

1. *8 KiB pages, no header, 200-byte records, 50,000 records: pages?* $\mathit{bf} = 40$ (8192/200 = 40.96), $b = 1250$.
2. *External sort of 10,000 pages with 11 buffers: passes?* 910 runs; 10-way merges: $910 \to 91 \to 10 \to 1$: **4 passes**.
3. *True or false: in a slotted page, compaction changes the record ids.* **False**: only offsets in the slot directory change.
4. *True or false: equality search on the key costs $\lceil\log_2 b\rceil$ page reads in a heap file.* **False**: $b/2$ on average; that cost belongs to a sorted file.
5. *Which replacement policy suits the repeatedly scanned inner relation of a nested-loop join?* **MRU** [S6].

## Code

`src/py/storage.py`: `storage.blocking_factor`, `storage.pages`,
`storage.SlottedPage` (insert, delete, compact, slot reuse),
`storage.file_costs`, `storage.external_sort`, `storage.sort_passes`,
`storage.sort_cost_silberschatz`. Tests: random insert/delete keeps every rid
readable; the simulated sort matches the closed forms for five $(b, M)$ pairs.
