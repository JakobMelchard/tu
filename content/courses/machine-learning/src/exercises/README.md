# Worked past papers

**There are no public exercise sheets for the current course.** The three group
assignments live in TUWEL, which needs a login and is not ours to copy. One
older assignment sheet *is* public ([S15], Exercise 1, 2021S) and is digested in
[`../../notes/17-exercise-playbook.md`](../../notes/17-exercise-playbook.md)
rather than reproduced here, because it asks for a 15-page group report, not for
a calculation.

What *is* public and worth working is the **exam archive**: 19 transcribed
papers on VoWi [S11] plus two in a student repository [S18], digested in
[`../../notes/00-exam-focus.md`](../../notes/00-exam-focus.md). Five of them are
worked here.

| folder | date | label | term | why this one |
|---|---|---|---|---|
| `2019-10-18` | 18.10.2019 | E19b | 2018W re-take | the long-answer era: kNN + naive Bayes by hand, AdaBoost stumps, support vectors, decision boundaries |
| `2020-06-25` | 25.06.2020 | E20b | 2020S | **1R** with precision and accuracy, and **LOOCV** for 1-NN vs 3-NN |
| `2020-09-09` | 09.09.2020 | E20c | 2019W/2020S re-take | where **convolution and max pooling** first appear; naive Bayes **with** Laplace |
| `2022-06-30` | 30.06.2022 | E22b | 2022S | the format break: first all-MC paper, first **$k$-armed bandit**, one **gradient-descent step** |
| `2026-01-27` | 27.01.2026 | E26a | 2025W main | **the most recent paper and the closest model for 2026W** — all four section-2 calculations plus the section-3 lists |

Together they cover **all five recurring hand calculations**: naive Bayes, the
bandit trace, convolution/pooling, 1R, and a regression error or gradient step.

## Important caveat

Every one of these transcripts is a student's recollection, and **none of them
reproduces the paper's data tables**. So each `solution.py` works a table of the
*stated shape* — the right number of rows, the right attribute types, the right
question — with our own implementations from [`../py`](../README.md). The
**method** is what transfers; the numbers are ours. Where a transcript does
record a specific outcome (the 1/3 initial AdaBoost weights, 1R splitting on
`age` and scoring 1.0, the $3\times3$ output of a $7\times7$/$3\times3$/stride-2
operation), the solution reproduces that outcome and says so.

Nothing from the papers is copied: each folder's `README.md` describes what was
asked in our own words. The transcripts are student wiki text with no licence
[S11]; see [`../../refs/SOURCES.md`](../../refs/SOURCES.md).

## Running them

```sh
# from the course folder
uv run python src/exercises/2026-01-27/solution.py
```

Every `solution.py` states in its docstring the questions it answers, with the
source paper [S11] and the resulting numbers; exposes `solve()` returning a dict
of answers; and exposes `check(r)`, which asserts those numbers. `__main__`
prints the answers and then runs `check()`. `src/py/test_exercises.py` runs
`solve()` and `check()` for all five, so `pytest src` covers them.
