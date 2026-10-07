# Practice set — substitute material, with provenance on every item

191.125 publishes **no script, no exercise sheet and no past paper**. TISS's
literature field says "No lecture notes are available." in all seven offerings
2019W–2026W, the one course homepage the lecturer ever had is dead and said
*"All material will be published on TUWEL"*, and the VoWi page is an empty stub
— [`../../notes/00-exam-focus.md`](../../notes/00-exam-focus.md) and
[`../../refs/SOURCES.md`](../../refs/SOURCES.md) [S1]–[S9]. TUWEL needs a login
and was not touched.

This directory is what fills that gap. **The one rule: nothing here is this
course's material, and nothing pretends to be.** Every file names the
institution, the course, the year and the licence it is adapted from, or says
that it is ours.

## Layout

```
exercises/
  mc_bank.py      framework: the Item type, and pick/pick_true, which insist
  mc_checks.py    the executable half: one function per item, each RUNS the
                  behaviour and derives the correct letter
  mc_items.py     the 24 questions.  OURS — no past paper exists to copy
  test_mc_bank.py runs every item against the installed libraries

  aalto-python-for-scicomp-2025/       [S41]  CC BY 4.0   6 tasks
  scientific-python-lectures-2024/     [S39]  CC BY 4.0   6 tasks
  software-carpentry-python-2026/      [S42]  CC BY 4.0 (+ MIT code)  5 tasks
```

Each source directory has its own `README.md` giving the licence, **what it
covers that the TISS subject list also covers**, and what it covers that this
course does not. Read that before the code.

## The idea worth the effort: multiple choice you can execute

TISS has said since 2024W that Part 2 is a *"written exam with multiple choice
and programming exercises"* [S3]. Multiple choice about library behaviour is the
one exam format that can be **checked by running it** — so it is, here. Each
item in `mc_items.py` carries a `check` callable that executes the behaviour in
the repo venv and *derives* the letter of the answer; `test_mc_bank.py` runs all
24. Two things follow:

1. A stated answer cannot be wrong unless a library changes — and then the
   suite fails instead of the reader.
2. The **distractors** are checked too. `pick` and `pick_true` require exactly
   one of the four options to match, so a question with two defensible answers
   is a test failure, not a trap.

This extends [`../py/test_doc_examples.py`](../py/test_doc_examples.py) from
"one test per version-sensitive claim in the notes" to "one test per exam
question". Versions are pinned in [`../../refs/SOURCES.md`](../../refs/SOURCES.md)
§S40.

## Vendored vs cited

**Nothing is vendored.** All three sources are CC BY 4.0 and could legally be
copied. None is, for the reason [`../../refs/README.md`](../../refs/README.md)
already gives for the library documentation: two of the three are living sites
with no tagged release, so a copy would be a fork of something that moves. Every
task was **restated in our own words and reimplemented**, and every dataset that
would have had to be downloaded was replaced by a seeded generator — this repo's
tests do no network I/O.

## Run it

```sh
uv run pytest src -q          # from the course folder

cd src/exercises
uv run python mc_bank.py        # the 24 questions
uv run python mc_bank.py -a     # ... with answers
```

The condensed write-up, with the programming problems that go with these, is
[`../../notes/11-practice-set.md`](../../notes/11-practice-set.md).
