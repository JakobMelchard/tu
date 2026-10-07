# Substitute exercise sets

**192.043 has no public exercise sheet, and no past paper of its own** [S24].
Blocks A and B had no practice material at all, and Exam 1 (11 Dec) is entirely
A + B [S1]. These three folders close that gap with free, licence-clear teaching
material from elsewhere. **They are not this course's material.** Each README
opens with its institution, course code, year, licence and retrieval date, says
what it covers that this course's TISS list also covers, and says what it covers
that this course does not. The reasoning and the rejected candidates are in
[`../../refs/SOURCES.md`](../../refs/SOURCES.md) §Substitute sources.

| folder | source | licence | what it teaches |
|---|---|---|---|
| `mit-18.404j-2020` | [S59] MIT OCW 18.404J, Sipser, Fall 2020, sample final **with solutions** | CC BY-NC-SA 4.0 | the settled/open/false class inclusions, **NP-completeness with both directions of the correctness proof**, log-space reductions, BPP ⊆ PSPACE → B01–B03, B05 |
| `princeton-arora-barak-2007` | [S60] Arora & Barak, free draft — **cite-only, exercises are ours** | none (all rights reserved) | the polynomial hierarchy, Shannon's counting bound, P/poly and undecidable languages, Adleman, the Feynman path sum → B02, B04, B05, B06 |
| `mit-6.046j-2015` | [S61] MIT OCW 6.046J, Demaine/Devadas/Lynch, Spring 2015, final **with solutions** | CC BY-NC-SA 4.0 | recurrences, an exchange-argument greedy, MST traps, Floyd–Warshall's recursion, **one Edmonds–Karp iteration**, list scheduling → A01, A03–A07 |

The two MIT folders *adapt* CC BY-NC-SA 4.0 material, so **those two folders are
themselves CC BY-NC-SA 4.0**, and their READMEs say so. Nothing anywhere is
vendored and no question text is copied; every question is restated in our own
words. The Arora & Barak draft forbids reproduction outright, so its folder's
exercises are ones we wrote for theorems the book states.

They are run by [`../py/test_substitute_exercises.py`](../py/test_substitute_exercises.py),
which also pins the numbers MIT published — Edmonds–Karp reaching a flow of 26,
and the tight $2-\frac1m$ load-balancing family.

The practice set that pulls the three folders together is
[`../../notes/01-practice-set-substitute-sources.md`](../../notes/01-practice-set-substitute-sources.md).

## Running them

Each `solution.py` runs standalone and checks itself:

```sh
cd src/exercises        # from the course folder
for d in */; do ( cd "$d" && python solution.py ); done
```
