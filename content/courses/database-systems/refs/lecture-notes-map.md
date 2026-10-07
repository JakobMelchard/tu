# Topic map: TISS subject list → sources → notes → code

184.686 publishes no lecture notes ("No lecture notes", [S1]) and its slides
were not publicly readable on 2026-09-28 ([S4] HTTP 403). The structural index
is therefore the TISS "Subject of course" list [S2], one row per item in TISS
order; the notes are numbered in this order. When the 2027S slides appear,
add a slide column and re-order if the lecture order differs.

| TISS subject item [S2] | primary sources | note | code (`../src/py/`) |
|---|---|---|---|
| fundamentals of database design, conceptual modelling with ER diagrams | [S6] ch. 6, [S11] | [01](../notes/01-er-modelling.md) | `er.py` |
| the relational data model and its formal foundations | [S9], [S6] ch. 2, [S10] ch. 3 | [02](../notes/02-relational-model.md) | `relalg.py`, `sql_lab.py` |
| transformation of conceptual models into relational schemas | [S6] ch. 6 (reduction to schemas) | [03](../notes/03-er-to-relational.md) | `er.py` |
| functional dependencies and normal forms | [S6] ch. 7, [S10] ch. 8, 11, [S12] | [04](../notes/04-fds-and-normal-forms.md) | `fd.py` |
| relational algebra, relational calculus, SQL | [S6] ch. 2-4, [S10] ch. 4-5 | [05](../notes/05-relational-algebra-and-calculus.md), [06](../notes/06-sql.md) | `relalg.py`, `sql_lab.py` |
| definition and manipulation of data and schemas | [S6] ch. 3-4, [S21], [S22] | [06](../notes/06-sql.md) | `sql_lab.py` |
| fundamentals of physical data organisation | [S6] ch. 13, 15, [S16], [S21] fileformat2 | [07](../notes/07-physical-organisation.md) | `storage.py` |
| index structures and their use for efficient query processing | [S6] ch. 14, [S13], [S15], [S21] eqp, queryplanner | [08](../notes/08-index-structures.md) | `bplustree.py`, `hashing.py`, `sql_lab.py` |
| basic join algorithms and their role in query execution | [S6] ch. 15 | [09](../notes/09-join-algorithms.md) | `joins.py` |
| query optimisation, execution of simple plans | [S6] ch. 16, [S14] | [10](../notes/10-query-optimisation.md) | `optimizer.py` |
| transaction concepts and models | [S6] ch. 17, [S19] | [11](../notes/11-transactions-and-concurrency.md) | `transactions.py` |
| error handling and recovery | [S6] ch. 19, [S20], [S21] atomiccommit | [12](../notes/12-recovery.md) | `transactions.py`, `recovery.py` |
| mechanisms for multi-user synchronisation | [S6] ch. 18, [S17], [S19], [S22] | [11](../notes/11-transactions-and-concurrency.md) | `locking.py`, `transactions.py` |

Plus [00](../notes/00-exam-focus.md) (format, not a topic) and
[13](../notes/13-practice-set.md) (MC items and SQL lab exercises, all topics).

## Learning outcomes → notes

The nine learning outcomes [S2] are mapped in
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) ("How to weight the notes").

## Where the sources disagree or are silent

- **B-tree occupancy conventions.** [S6] counts pointers per node ($n$);
  degree-$k$ conventions (entries between $k$ and $2k$) are common in German
  texts such as [S7] (not checked). The course's convention is unknown; note 08
  shows how to convert.
- **Cardinality notation.** Chen-style 1:N, $(\min,\max)$ and [S6]'s arrows put
  the numbers at opposite ends of the relationship (note 01). Which one the
  course uses is unknown.
- **External sort cost.** [S6] omits the final write, many exercises include it
  (note 07 gives both).
- **Relational calculus.** Moved out of [S6]'s main chapters in the 7th ed.;
  note 05 follows [S10]. The course's calculus notation (TRC with range
  declarations, or DRC) is unknown.
- **Block nested-loop formula.** An image in [S6]'s PDF; derived in note 09.
- **NULL ordering and quantified comparisons.** sqlite and PostgreSQL differ
  (note 06): matters only if the SQL exam's DBMS is not the one practised on.
- **Exam dates.** The 2026S page lists 2027 dates labelled "1. Test", "2. Test"
  and a repeat [S1]; which component each belongs to is not stated anywhere
  public.
