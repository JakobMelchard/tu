# src/exercises - substitute practice material

**360.242 publishes no exercise sheet and no past paper.** TISS says *"No lecture
notes are available."* in every offering from 2019W to 2026W [S1] [S2] [S3], and
the VoWi page is empty - 0 Materialien [S4]. See
[`../../notes/00-exam-focus.md`](../../notes/00-exam-focus.md).

So there is nothing here that came from this course. Every directory is
**another course's or another author's material**, and every one of them says so
in its first paragraph. The rule this directory is built on:

> Never present another institution's material as 360.242's. Provenance -
> institution, course, year, licence, URL, retrieval date - is in each
> `README.md` and repeated in the header of each solution file.

| directory | source | licence | TISS topics [S1] |
|---|---|---|---|
| `tuwien-introsc-2025/` | J. Schöberl, *Introduction to Scientific Computing*, TU Wien E101 [S8] [S9] | LGPL-2.1 / MIT | 1, 2, 7, (8, 10) |
| [`utaustin-theartofhpc-2022/`](utaustin-theartofhpc-2022/README.md) | V. Eijkhout, *The Art of HPC* vol. 1, UT Austin / TACC [S43] | CC BY 4.0 | 1, 2, (4, 5, 7, 8) |
| [`cornell-cs5220-2015/`](cornell-cs5220-2015/README.md) | D. Bindel, CS 5220 *Applications of Parallel Computers*, Cornell, Fall 2015, HW3 [S44] | MIT | 2, 7, 8 |

`tuwien-introsc-2025/` comes first on purpose:
Schöberl is **one of the five 2026W lecturers of 360.242** [S1] [S10], so his own
exercises outrank any external substitute.

**Nothing is vendored.** Two of the three licences would permit it; the exercise
texts are restated in our words and cited to chapter and section instead, so
that no reader can mistake a restatement for the original or the original for a
360.242 question.

The problems these directories feed into are collected in
[`../../notes/11-practice-set.md`](../../notes/11-practice-set.md), which also
records the TISS topics for which **no** good free practice material was found.

## Run everything

```sh
# from the course folder
uv run pytest src -q     # src/py plus every exercise directory
make -C src/exercises/tuwien-introsc-2025 test
```
