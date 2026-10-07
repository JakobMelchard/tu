# 11 Practice set — 24 executable MC items and 16 programming problems

Code: `../src/exercises/`, tests in each directory.

Sources: this note is the write-up of the **substitute-source pass**. The
practice material is adapted from Aalto's *Python for Scientific Computing*
[S41], the *Scientific Python Lectures* [S39] and Software Carpentry's
*Programming with Python* [S42] — all CC BY 4.0 — or is ours [S43]. Verified
against the versions in [`../refs/SOURCES.md`](../refs/SOURCES.md) §S40, last on
2026-09-27 (PuLP 4.0.0).

> **None of this is a past paper.** 191.125 publishes no script, no exercise
> sheet and no past paper: TISS's literature field says *"No lecture notes are
> available."* in all seven offerings 2019W–2026W [S1]–[S7], the lecturer's one
> course homepage is dead and said *"All material will be published on TUWEL"*
> [S8], and the VoWi page is an empty stub [S9]. TUWEL needs a login and was not
> touched. Read [`00-exam-focus.md`](00-exam-focus.md) first; nothing here
> contradicts it.
>
> **Every item below carries its provenance.** A problem tagged [S41] is
> *adapted from Aalto*, restated in our own words — it is not a TU Wien
> question, and no reader should be able to mistake it for one.

## 1. Where the material comes from, and why these three

No single free course covers this course's eight-item TISS subject list. Three
were needed, and they were picked so their gaps do not overlap:

| source | licence | covers, of the TISS list | directory |
|---|---|---|---|
| **Aalto, *Python for Scientific Computing*** [S41] | CC BY 4.0 (repo `LICENSE`) | NumPy/SciPy, data processing, **parallel processing**, Jupyter | `../src/exercises/aalto-python-for-scicomp-2025/` |
| ***Scientific Python Lectures*** 2024.1 [S39] | CC BY 4.0 (`LICENSE.md`) | **optimisation**, **interfaces** (to C), advanced NumPy | `../src/exercises/scientific-python-lectures-2024/` |
| **Software Carpentry, *Programming with Python*** [S42] | CC BY 4.0 material, MIT code | the **language**, **code testing** | `../src/exercises/software-carpentry-python-2026/` |
| **the MC bank** [S43] | ours | all eight | `../src/exercises/` |

Sundnes [S38] is the fourth CC BY 4.0 text the repo holds. It is an excellent
companion for the first TISS item and nothing else — it stops where note 02
starts — so it is recommended reading rather than a source of exercises here.

**Nothing is vendored, and no problem statement is copied.** Each task was
restated and reimplemented; datasets that would have needed downloading were
replaced by seeded generators. The per-directory `README.md` files give the
licence, the retrieval date, what the source covers that TISS also covers, and
what it covers that this course does not.

## 2. The 24 multiple-choice items — and why they are executable

TISS has said since 2024W that Part 2 is a *"written exam with multiple choice
and programming exercises"* [S3]. Multiple choice about library behaviour is the
one exam format whose correct answer can be **produced by running the code**, so
it is: each item in [`../src/exercises/mc_items.py`](../src/exercises/mc_items.py)
has a `check` callable in `mc_checks.py` that executes the behaviour in the repo
venv and derives the letter. `test_mc_bank.py` runs all 24, and the helpers
require **exactly one** of the four options to match — a question with two
defensible answers fails the suite instead of misleading you.

Re-run on 2026-09-27 after the venv was re-created (PuLP 3.3.2 → 4.0.0, every
other version unchanged [S40]): **all 24 answers unchanged**. No item touches
PuLP; the three optimisation items O1–O3 are about `scipy.optimize`, whose
version did not move. The PuLP change is in note [07](07-optimisation.md) §7.

Print them with

```sh
cd src/exercises                  # from the course folder
uv run python mc_bank.py        # questions only
uv run python mc_bank.py -a     # with answers and reasons
```

Three per TISS subject item:

| TISS subject item | items | what they test |
|---|---|---|
| Introduction to the Python programming language | L1–L3 | mutable default argument; late-binding closures; `t[1] += [3]` on a tuple (raises **and** mutates) |
| The SciPy and NumPy ecosystem | N1–N3 | `arange` step vs `linspace` count; `np.sort`'s default `axis=-1`; `solve_ivp(...).y` is `(states, times)` |
| Data processing and plotting (Matplotlib) | D1–D3 | `plt.subplots(1, 3)` squeezes to shape `(3,)`; `transform` is one row per *input row*; `ax.plot` returns a **list** |
| Code testing | T1–T3 | `approx` defaults to `rel=1e-6`; comparing against zero needs an explicit `abs`; `pytest.raises` matches subclasses |
| Reproducible … with IPython/Jupyter | J1–J3 | `%%timeit` is the only one of four that is also a cell magic; `outputs` is the code-cell-only nbformat key; nbconvert's `--to` targets |
| Introduction to solving optimization problems | O1–O3 | Newton-CG refuses without `jac`; SLSQP `ineq` means `fun(x) ≥ 0`; `linprog` **minimises** |
| Parallel processing in Python | P1–P3 | `map` returns a list, `imap` an iterator; a lambda cannot be pickled to a worker; processes do not share the parent's globals |
| Interfaces to other programming languages | I1–I3 | ctypes without `restype` returns a wrong *number*, not an error; `a.T` is F-contiguous for free; `capture_output` gives bytes |

These are **ours**. No public paper for this course, this lecturer or the
predecessor number 191.116 exists to model them on [S9].

## 3. Sixteen programming problems, two per TISS subject item

Part 2's programming half is written **on paper**, in a lecture hall, with no
interpreter — the TUWEL-quiz mode of 2021W/2022W was dropped in 2023W [S4]–[S6].
So do these with a pen first and only then check them. Argument *names* and
*order* are what you lose marks on.

Each problem says what a full answer must contain and where the worked version
is. The tag is the provenance: **[ours]**, or the source it is adapted from.

### Introduction to the Python programming language

1. **[ours]** Write a generator `running_mean(values)` that yields the mean of
   everything seen so far, in one pass and without storing the input. State what
   it yields for an empty iterable. — *Must contain:* `yield` inside a loop, a
   running count and sum, no list. See [`../src/py/python_basics.py`](../src/py/python_basics.py).
2. **[S42]** Explain, in four lines, what `t = (1, [2]); t[1] += [3]` does, in
   what order, and what `t` is afterwards. — *Must contain:* `list.__iadd__`
   mutates in place and succeeds; the store back into the tuple is what raises;
   both happen. MC item L3; [`swc_exercises.exception_clause_order`](../src/exercises/software-carpentry-python-2026/swc_exercises.py)
   is the neighbouring idea.

### The SciPy and NumPy ecosystem

3. **[ours]** Given `P` of shape `(n, 3)`, write the full pairwise distance
   matrix without a Python loop, and say how large the temporary is. — *Must
   contain:* `P[:, None, :] - P[None, :, :]`, `np.linalg.norm(..., axis=-1)`,
   and the observation that the temporary is `n²·3·8` bytes.
4. **[S41]** Normalise each row of an `(m, n)` array to sum to 1. Say what
   happens without `keepdims=True` and when it happens to work anyway. — *Must
   contain:* `a / a.sum(axis=1, keepdims=True)`; without `keepdims` the `(m,)`
   result right-aligns against the *last* axis, so it raises for `m != n` and —
   worse — succeeds for a square array while normalising the wrong way. See [`aalto_exercises.reduce_along_axis`](../src/exercises/aalto-python-for-scicomp-2025/aalto_exercises.py).

### Data processing and plotting (Matplotlib)

5. **[S41]** From a DataFrame with columns `station` and `value`, draw mean ± sd
   per station as an error-bar chart using the object-oriented interface. — *Must
   contain:* `df.groupby("station")["value"].agg(["mean", "std"])`,
   `fig, ax = plt.subplots(layout="constrained")`, `ax.errorbar(..., yerr=...)`,
   axis labels. See [`aalto_exercises.group_statistics`](../src/exercises/aalto-python-for-scicomp-2025/aalto_exercises.py)
   and [`../src/py/plotting.py`](../src/py/plotting.py).
6. **[ours]** Plot $f(x,y) = \sin r / r$, $r = \sqrt{x^2+y^2}$, as a 3-D surface.
   — *Must contain:* `np.meshgrid`, `fig.add_subplot(projection="3d")`,
   `ax.plot_surface(X, Y, Z)`. A learning outcome names 3-D plotting explicitly
   [S1], so this is the one plotting idiom worth memorising letter-perfect.

### Code testing

7. **[S42]** Write the pytest tests for `range_overlap(ranges)` **before** the
   function, then the function. Name the case that decides the design. — *Must
   contain:* the touching case `[(0, 1), (1, 2)]`, which has no interval of
   positive width and must give `None`. See
   [`test_swc_exercises.py`](../src/exercises/software-carpentry-python-2026/test_swc_exercises.py).
8. **[ours]** Write a parametrised test comparing a numerical routine against a
   closed form, and explain in one line why
   `np.testing.assert_allclose(x, 0)` fails for any nonzero `x`. — *Must
   contain:* `@pytest.mark.parametrize("a,b", [...])`, and `atol=0` by default,
   so the criterion $|a-d| \le \text{atol} + \text{rtol}|d|$ is $\le 0$ against
   zero. MC items T1–T2; note [05](05-testing.md) §5.

### Reproducible and interactive data processing with IPython/Jupyter

9. **[ours]** Write the first cell of a notebook that someone else must be able
   to re-run in a year. — *Must contain:* the library versions recorded in the
   output, one `rng = np.random.default_rng(seed)` passed onward rather than
   `np.random.seed`, and no reliance on execution order. See
   [`../src/notebooks/tour.ipynb`](../src/notebooks/tour.ipynb) and note [06](06-reproducibility-jupyter.md).
10. **[ours]** Give the command that re-executes a notebook top to bottom and
    writes the executed copy elsewhere, and say what `--to script` produces. —
    *Must contain:* `jupyter nbconvert --to notebook --execute nb.ipynb --output out.ipynb`;
    `--to script` gives a `.py`. MC item J3.

### Introduction to solving optimization problems (e.g. SciPy, PuLP)

11. **[ours]** A workshop makes two products. Each unit of P1 needs 2 machine
    hours and 1 labour hour; P2 needs 1 and 3. There are 100 machine hours and
    200 labour hours; profits are 40 and 50. Formulate the LP in standard form
    and write both the `linprog` and the PuLP calls. — *Must contain:* the
    objective **negated** for `linprog` because it minimises, `A_ub @ x <= b_ub`,
    `bounds=[(0, None)] * 2`, and for PuLP `LpMaximize` with
    `prob.add_variable(...)`. Worked both ways in
    [`optimisation.workshop_lp`](../src/py/optimisation.py): $(P_1, P_2) = (20, 60)$,
    profit 3800. Under PuLP 4 the solve needs a solver PuLP can find; this venv has
    none, so `solve_pulp` hands the model to SciPy's HiGHS (note [07](07-optimisation.md) §7).
    MC item O3. *No free source teaches LP — this problem is ours (see §4).*
12. **[S39]** Minimise $(x-3)^2 + (y-2)^2$ subject to $x + y \le 2$ and
    $x, y \ge 0$ with SLSQP. Write the constraint. — *Must contain:*
    `{"type": "ineq", "fun": lambda v: 2 - v[0] - v[1]}` — `ineq` is satisfied
    where the function is **≥ 0** — plus `bounds`. Answer `(1.5, 0.5)`, $f=4.5$.
    See [`spl_exercises.constrained_box`](../src/exercises/scientific-python-lectures-2024/spl_exercises.py);
    MC item O2.

### Parallel processing in Python

13. **[S41]** Turn a serial Monte Carlo estimate of $\pi$ into one that runs on
    `w` processes and gives the *same* answer every time. — *Must contain:*
    `np.random.SeedSequence(seed).spawn(w)` for independent streams, a top-level
    worker function (a lambda cannot be pickled — MC item P2),
    `with mp.Pool(w) as pool: pool.map(...)`, and the
    `if __name__ == "__main__":` guard that `spawn` requires. See
    [`aalto_exercises.pi_parallel`](../src/exercises/aalto-python-for-scicomp-2025/aalto_exercises.py)
    and [`../src/py/parallel.py`](../src/py/parallel.py).
14. **[ours]** A program spends 10 % of its time in code that cannot be
    parallelised. Give the speedup on 4 and on infinitely many cores, and say
    what Gustafson changes. — *Must contain:* $S(n) = 1/((1-p) + p/n)$ giving
    $S(4) = 3.08$ and $S(\infty) = 10$; Gustafson holds the *time* fixed instead
    of the problem size, so $S = (1-p) + pn$ grows without bound [S35], [S36].
    Note [08](08-parallel-processing.md) §7.

### Interfaces to other programming languages (e.g. Julia)

15. **[S39]** A C library exports `double vec_dot(const double *a, const double
    *b, size_t n)`. Write the ctypes declaration and the call with two NumPy
    arrays, and say what happens if you skip the declaration. — *Must contain:*
    `ndpointer(np.float64, ndim=1, flags="C_CONTIGUOUS")` for the arrays,
    `ctypes.c_size_t` for `n`, `restype = ctypes.c_double`; without `restype`
    ctypes assumes `int` and returns a wrong number **without raising**. See
    [`spl_exercises.undeclared_vs_declared`](../src/exercises/scientific-python-lectures-2024/spl_exercises.py)
    and [`../src/py/interfaces.py`](../src/py/interfaces.py); MC item I1.
16. **[ours]** You must pass a $(m, n)$ NumPy matrix to a Julia or Fortran
    routine that expects column-major storage. Give the zero-copy way and the
    copying way, and say which one changes the logical array. — *Must contain:*
    `a.T` only swaps strides, shares memory and is already F-contiguous but is
    the *transpose*; `np.asfortranarray(a)` copies and keeps the same logical
    array. See [`spl_exercises.column_major_handoff`](../src/exercises/scientific-python-lectures-2024/spl_exercises.py);
    MC item I2.

## 4. TISS topics with no good free practice material

Stated rather than padded around, as the brief for this pass required.

- **Linear and integer programming (PuLP).** TISS names PuLP by name, and *none*
  of the three sources teaches it: the Scientific Python Lectures' optimisation
  chapter is continuous only — no `linprog`, no `milp`, no LP formulation — and
  Aalto has no optimisation chapter at all. PuLP's own documentation [S23] is
  MIT-licensed reference with case studies, not graded exercises. **Problem 11
  is therefore ours**, and so is everything LP in
  [`../src/py/optimisation.py`](../src/py/optimisation.py). This is the largest
  remaining gap, and it sits on a topic TISS lists *and* makes a learning
  outcome.
- **Julia ↔ Python.** TISS's subject item says "*e.g. Julia*". No free
  CC-licensed exercise set for it was found; [S39] ch. 2.8 teaches C, SWIG and
  Cython, and PythonCall.jl's documentation [S30] is reference with no problems.
  Problem 15 exercises the transferable part (declared signatures, memory
  layout) and note [09](09-interfaces.md) §8 stays documentation-only. Julia is
  **not installed** in the repo venv, so nothing about it is demonstrated.
- **Jupyter as a *workflow*.** The three executable facts in the MC bank
  (J1–J3) are all that a pytest suite can check. Out-of-order execution,
  kernel-restart discipline and notebook review are habits, not assertions;
  Aalto's Jupyter and Binder chapters teach them but have nothing to test.
  Problems 9–10 are ours for that reason.
- **3-D plotting.** A learning outcome names it [S1]; neither Aalto nor Software
  Carpentry goes past 2-D. Problem 6 is ours.
- **pytest proper.** Software Carpentry's testing is `assert` and hand-written
  TDD — no fixtures, `parametrize`, `approx` or markers. That half of "Code
  testing" rests on pytest's own documentation [S18] and note
  [05](05-testing.md), which is a primary source and needs no substitute.

## 5. How to use this in the last week

1. **Print the MC bank without answers** and do all 24 cold. Anything you get
   wrong is a note to re-read, not a fact to memorise — the tag in the table in
   §2 says which note.
2. **Write problems 1–16 by hand**, then run the linked module and diff your
   version against it. The paper exam has no interpreter and no completion; the
   gap between "I recognise this" and "I can write `minimize(f, x0, jac=g,
   constraints=[{"type": "ineq", "fun": c}])` correctly" is the whole exercise.
3. **Run the suite once** — `uv run pytest src -q` from the course folder.
   If it fails, a library moved and something in these notes is now wrong; the
   failing test names the claim.
4. **Do not treat any of this as the exam.** The one thing actually known about
   the paper is its format [S1], [S3]. The TUWEL course opens on 01.10.2026 [S1]
   and presumably states the point split and the duration, which would supersede
   the guesses in [`00-exam-focus.md`](00-exam-focus.md) §"What would change this
   page". **Caveat:** TUWEL was not read for these notes.

## Exam-style questions

The 24 multiple-choice items of §2 are this note's exam-style questions, and
they are **ours** — see §2. The programming problems of §3 are tagged
individually: **[ours]**, or adapted from [S39], [S41] or [S42] with the source
named. None of them is a past paper's, because no past paper for this course is
public [S9].
