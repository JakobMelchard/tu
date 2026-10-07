# Exercises — substitutes, and nothing that pretends to be otherwise

In the other courses in this repo, `src/exercises/<term>-<n>/` holds a worked
solution to a **real past exercise sheet or exam paper** of *that* course.

**191.030 has none, and still has none.** The course is new in 2026W [S1]: TISS
has no 2025W or 2024W offering [S2], VoWi has no page for it or for its
lecturer [S7], and Tobias Fiebig — who took the chair on 1 March 2026 [S5] — has
no public teaching material of his own [S5], [S33]. TISS states outright that no
lecture notes are available [S1]. Nothing has been withheld here; there is
nothing to withhold.

What changed is that the gap is now filled with **substitute material from
elsewhere, labelled as such**. The directory names say whose it is:

| directory | source | licence | what it gives |
|---|---|---|---|
| `mit-6.02-2012/` | MIT 6.02 *Introduction to EECS II*, Fall 2012, OCW [S34] | CC BY-NC-SA 4.0 | routing and reliable-transport problems **with MIT's published solutions** — the only external answer key in this tree |
| `uclouvain-cnp3-2019/` | *Computer Networking: Principles, Protocols and Practice*, O. Bonaventure, UCLouvain [S35] | CC BY-SA 3.0 | bridging, **inter-domain routing policy** (path vector) and addressing exercises; no published solutions |

Both are **cited, not vendored**: no PDF and no `.rst` file is committed, no
sentence of either author's prose is copied, every problem is restated in our
own words, and each directory's `README.md` gives institution, course, year,
URL, retrieval date, licence, the overlap with 191.030's TISS topic list, and
the scope differences in both directions. The reasoning for citing rather than
vendoring is in those READMEs.

> **Read the rule once.** A Berkeley — or Cambridge, Massachusetts — problem set
> is not a TU Wien past paper, and nothing in this directory may be mistaken for
> one. Every item carries its provenance on the first line.

The condensed practice set that pulls both sources together, adds problems of
our own for the topics neither covers, and tags every problem with its origin
is [`../../notes/12-substitute-practice-set.md`](../../notes/12-substitute-practice-set.md).

## When the real sheets appear

The five exercises will be released during the semester, after lectures 7, 9,
16, 19 and 22 [S1], which
[`../../notes/00-exam-focus.md`](../../notes/00-exam-focus.md) works out to
roughly 09.11.2026, 16.11.2026, 07.12.2026, 11.01.2027 and 18.01.2027. Where
they will be published is open: TISS links no TUWEL course for 191.030
(re-read 2026-09-27). Wherever they appear, **course material is not ours to
copy**: describe each task in your own words in `<term>-<n>/README.md` and put
your own solution beside it, as the other courses do. Do not paste the sheet.

## What else stands in for a past paper

1. **[`../py/test_rfc_vectors.py`](../py/test_rfc_vectors.py)** — 20 tests (plus
   the RFC-figure tests in `test_tcp_fsm.py`, `test_dns.py`, `test_subnet.py`
   and `test_telnet_client_sketch.py`), each
   naming an RFC and a section and reproducing a number that RFC *prints*. That
   is the same discipline as reproducing a lecturer's worked example: it
   validates the source reading and the implementation at once. For the
   constants this course is likely to ask about (OSPF's appendices, RFC 4271
   §10, RFC 6298's rounding rule) it is arguably better than a past paper,
   because a standard does not misremember.
2. **[`../../notes/11-exercise-playbook.md`](../../notes/11-exercise-playbook.md)**
   — the procedure for each of the three task types TISS named ("describing
   packet traces received", "deriving a topology based on provided
   information", "describe TCP behavior given a specific scenario" [S1];
   stated on TISS until 2026-09-2x, removed by 2026-09-27), with
   the tools in [`../sh/tools_cheatsheet.sh`](../sh/tools_cheatsheet.sh) and the
   simulators in [`../py/tcp_sim.py`](../py/tcp_sim.py),
   [`../py/tcp_fsm.py`](../py/tcp_fsm.py),
   [`../py/subnet.py`](../py/subnet.py),
   [`../py/linkstate.py`](../py/linkstate.py) to generate your own instances.

Source labels refer to [`../../refs/SOURCES.md`](../../refs/SOURCES.md).
