# Sources — 191.125 Scientific Programming with Python

Register of every source used to write and verify `../notes` and
`../src`. The notes cite these as `[S<n>]`. Retrieval dates are the day
the page was fetched; TISS and library documentation change, so re-check before
the exam.

**Two rules specific to this course.**

1. *Version-pinned docs only.* This is a library course, and library behaviour
   changes between major versions. Every library citation points at the
   documentation build for the version **installed in the repo venv**
   ([S40](#s40--repo-environment-record-the-versions-everything-was-verified-against)),
   not at `latest`/`stable`, so a claim and the page backing it cannot drift
   apart. Where only a `stable` URL exists, the entry says which version
   `stable` was at retrieval.
2. *No TUWEL.* Every offering of this course puts its slides, exercise sheets
   and past papers in TUWEL, which needs a login. Nothing behind that login was
   fetched, and no link into it is followed, so TUWEL facts (exercises, Part
   1/Part 2 weighting) are unchecked; every note that mentions them says so.

**Vendoring policy.** Nothing in this directory is a third-party file. See
[`README.md`](README.md) for why — unusually, it is *not* for licence reasons.

---

## Course-authoritative

### S1 — TISS course page, 2026W (the semester being studied)

- Title: 191.125 Scientific Programming with Python, 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191125&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript)
- Access: public, no login
- Used for: scope (subject of course, learning outcomes), lecturer (Hunold,
  Sascha, E191 Institute of Computer Engineering), ECTS (2.0), format
  (presence), dates (Tue 11:00–13:00, 13.10.2026–01.12.2026, HS 6 RPL),
  registration windows, examination modalities ("Part 1 — successfully
  completing the exercises; Part 2 — written exam with multiple choice and
  programming exercises"), literature ("No lecture notes are available."),
  curricula. Diffed against [`../docs/tiss.md`](../docs/tiss.md): **no change**
  in any field.
- Re-read: **2026-09-27**, in a logged-in browser: no field changed. Facts used from
  it, as of that day: eight lectures Tue 11:00-13:00, HS 6 RPL, 13.10.2026 to
  01.12.2026; deregistration until 20.10.2026; Exam 1 Tue 19.01.2027
  13:00-15:00, HS 17 / EI 9, registration 06.12.2026 to 17.01.2027; Exam 2 Tue
  23.02.2027 13:00-15:00, Informatikhörsaal, registration 20.01.2027 to
  19.02.2027; TUWEL course available from 01.10.2026.

### S2 — TISS course page, 2025W (previous offering)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191125&semester=2025W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the year-on-year diff. Identical learning outcomes, subject list,
  teaching methods, examination modalities, lecturer and curricula; lecture
  period 14.10.2025–09.12.2025 (nine Tuesdays), registration 15.09.2025–
  09.10.2025, deregistration to 21.10.2025.

### S3 — TISS course page, 2024W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191125&semester=2024W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the diff, and for two facts that matter. (a) 2024W is the **first
  year the examination modalities say "multiple choice and programming
  exercises"** — 2021W–2023W say only "programming exercises". (b) The page
  carries three **exam-inspection** appointments (27.01.2025, 29.01.2025,
  03.03.2025), which is direct evidence that a real written paper is set and
  marked, not a formality. Lecture period 08.10.2024–03.12.2024.

### S4 — TISS course page, 2023W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191125&semester=2023W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the diff. Hybrid format, lecture period 10.10.2023–23.01.2024 (the
  **full** semester, unlike 2024W onwards), examination modalities "written exam
  with programming exercises" — no multiple choice. Curricula: CSE and Digital
  Skills only; Computer Engineering (033 535) is **not** yet listed.

### S5 — TISS course page, 2022W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191125&semester=2022W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the diff. Hybrid, LectureTube-recorded, 11.10.2022–24.01.2023.
  Examination modalities add the delivery mode: "written exam with programming
  exercises — mode: TUWEL quiz or Jupyter notebook — required infrastructure:
  Computer with Internet connection, Webcam".

### S6 — TISS course page, 2021W (earliest offering under this number)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191125&semester=2021W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the diff and the **shape of the teaching**. Fully online. The
  appointment list is not "a weekly lecture" but six named slots: a preliminary
  meeting, *three* live lectures (09.11., 14.12., 18.01.) and *two* "Live
  Session Assignment" slots (16.11., 07.12.). Same examination modalities as S5.
  CSE only in the curricula.

### S7 — TISS course page, 191.116 Scientific Programming with Python, 2019W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191116&semester=2019W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the **predecessor course number** — this is the "similarly named
  LVA" and VoWi links to both ([S9]). Same lecturer, same learning outcomes,
  same subject list, but 1.0 semester hours (not 2.0) at the same 2.0 ECTS, and
  different examination modalities: "completing a student project" + "exam (oral
  or written)". Offered 2019W and 2020W only; the number was retired and
  191.125 started in 2021W. It also has two exam-inspection appointments and a
  **"Course homepage" link** ([S8]) that the 191.125 pages no longer carry.

### S8 — Course homepage for 191.116, 2019W (Research Group Parallel Computing), via the Internet Archive

- URL (archived): <http://web.archive.org/web/20221209223114/https://par.tuwien.ac.at/teaching/2019w/191.116.html>
- Original URL: `https://par.tuwien.ac.at/teaching/2019w/191.116.html` — now dead;
  `par.tuwien.ac.at` redirects to the institute's TU Wien page ([S10]) and the
  whole `/teaching/` tree is gone.
- Retrieved: 2026-09-22
- Access: public
- Used for: the only public page the lecturer ever hosted for this course. It
  gives a **preliminary lecture plan of eight lectures** for a 2.0 ECTS course
  and states, in full, the answer to "where is the material?": *"All material
  will be published on TUWEL"*. Eight lecture slots is also exactly what the
  2026W period gives (13.10.–01.12., eight Tuesdays), which is why
  [`../notes/README.md`](../notes/README.md) maps ten notes onto eight sessions
  rather than pretending there is a week per note.
- Checked and **not found** in the Wayback Machine: `.../2021w/191.125.html`,
  `.../2022w/191.125.html`, `.../2023w/191.125.html`, `.../2024w/191.125.html`,
  `par.tuwien.ac.at/teaching/`, `par.tuwien.ac.at/~hunold/`. There is no
  archived course homepage for 191.125 at all.

### S9 — VoWi, *TU Wien:Scientific Programming with Python VU (Hunold)*

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Scientific_Programming_with_Python_VU_(Hunold)>
- Retrieved: 2026-09-22 (browser; VoWi is behind a proof-of-work bot gate)
- Access: public
- Used for: **establishing that VoWi has nothing.** The page exists but is a
  stub: *Inhalt, Ablauf, Vorkenntnisse, Vortrag, Übungen, Prüfung/Benotung,
  Zeitaufwand, Unterlagen, Tipps, Kritik* all read "noch offen", and
  "Diese Seite hat noch keine Anhänge" — **no attachments, no past papers, no
  reported grading scheme**. What it does give: the course is also a compulsory
  subject in the *Bachelorstudium Technische Informatik* module "Einführung in
  die Programmierung", it links both TISS numbers (191125 and 191116, hence
  [S7]), "Letzte Abhaltung 2025W", and a Mattermost channel
  `scientific-programming-with-python`.
- Also searched on VoWi, full text, namespaces 0/100/102: **"Hunold"** → one hit
  (this page). There is no second VoWi page for this lecture under another
  number or the German title.

### S10 — Sascha Hunold, personal and institutional pages

- URLs: <https://hunoldscience.net/> · <https://informatics.tuwien.ac.at/people/sascha-hunold>
  · <https://www.tuwien.at/en/inf/par> (E191-04 Research Group Parallel Computing)
- Retrieved: 2026-09-22
- Access: public
- Used for: lecturer identity (Associate Professor, Research Unit of Parallel
  Computing, E191-04) and for confirming that **no teaching material is hosted
  outside TUWEL**: `hunoldscience.net` carries research, publications and
  programme-committee work, and for teaching only a pointer to the TISS course
  list. His research area (MPI, collective communication, performance
  portability, shared-memory programming) is why note 08 is worth more attention
  than a 2 ECTS Python course would otherwise justify.

---

## Primary language and library documentation

All of these are the upstream projects' own reference documentation: the primary
source for a library's semantics. Licences are given because they decide what
could be quoted or vendored.

### S11 — Python 3.12 documentation

- URLs: <https://docs.python.org/3.12/reference/datamodel.html> ·
  <https://docs.python.org/3.12/library/ctypes.html> ·
  <https://docs.python.org/3.12/library/multiprocessing.html> ·
  <https://docs.python.org/3.12/library/concurrent.futures.html> ·
  <https://docs.python.org/3.12/library/timeit.html> ·
  <https://docs.python.org/3.12/library/profile.html> ·
  <https://docs.python.org/3.12/library/tracemalloc.html> ·
  <https://docs.python.org/3.12/library/dataclasses.html> ·
  <https://docs.python.org/3.12/library/functools.html> ·
  <https://docs.python.org/3.12/library/subprocess.html>
- Version: 3.12 — the interpreter in the repo venv is 3.12.13 [S40]
- Retrieved: 2026-09-22
- Access: public. Licence: PSF License Agreement (redistributable with notice)
- Used for: note 01 throughout (data model, mutability, LEGB, generators,
  closures, decorators, dataclasses, context managers), note 08 (start methods,
  `Pool`, `concurrent.futures`, `shared_memory`), note 09 (ctypes,
  subprocess), note 10 (timeit, cProfile/pstats, tracemalloc).

### S12 — NumPy 2.5 reference documentation

- URLs: <https://numpy.org/doc/2.5/reference/arrays.ndarray.html> ·
  <https://numpy.org/doc/2.5/user/basics.broadcasting.html> ·
  <https://numpy.org/doc/2.5/user/basics.indexing.html> ·
  <https://numpy.org/doc/2.5/reference/ufuncs.html> ·
  <https://numpy.org/doc/2.5/reference/generated/numpy.einsum.html> ·
  <https://numpy.org/doc/2.5/reference/routines.linalg.html> ·
  <https://numpy.org/doc/2.5/reference/random/generator.html> ·
  <https://numpy.org/doc/2.5/reference/routines.testing.html> ·
  <https://numpy.org/doc/2.5/numpy_2_0_migration_guide.html>
- Version: 2.5 — installed 2.5.3 [S40]
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-3-Clause (code), docs CC-BY-like/BSD terms
- Used for: all of note 02, the numpy parts of notes 05, 08 and 10.

### S13 — NEP 50, *Promotion rules for Python scalars*

- URL: <https://numpy.org/neps/nep-0050-scalar-promotion.html>
- Retrieved: 2026-09-22
- Access: public
- Used for: note 02 §2, the rule that in NumPy ≥ 2 a Python scalar is "weak" and
  does not upcast the array (`float32 array + 1.0 → float32`), and that
  integer overflow in *scalar* arithmetic now emits a `RuntimeWarning` while the
  array case still wraps silently. Verified in the venv, see
  [`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py).

### S14 — NEP 19, *Random number generator policy*

- URL: <https://numpy.org/neps/nep-0019-rng-policy.html>
- Retrieved: 2026-09-22
- Access: public
- Used for: note 02 §9 and note 06 §3 — the stream of a `Generator` is *not*
  guaranteed identical across NumPy releases, which is why the reproducibility
  claim in the notes is version-qualified.

### S15 — SciPy 1.18.0 reference documentation

- URLs: <https://docs.scipy.org/doc/scipy-1.18.0/reference/index.html> ·
  `.../generated/scipy.integrate.solve_ivp.html` ·
  `.../generated/scipy.integrate.quad.html` ·
  `.../generated/scipy.interpolate.interp1d.html` ·
  `.../tutorial/interpolate/1D.html` ·
  `.../reference/sparse.html` · `.../reference/fft.html` ·
  `.../generated/scipy.optimize.minimize.html` ·
  `.../generated/scipy.optimize.least_squares.html` ·
  `.../generated/scipy.optimize.linprog.html` ·
  `.../generated/scipy.optimize.milp.html`
- Version: the 1.18.0 build; installed SciPy is 1.18.1 [S40], which has no
  separate documentation build. Micro releases do not change the documented API.
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-3-Clause
- Used for: all of note 03 and note 07 §2–§6. In particular the `interp1d` page
  carries the notice *"This class is considered legacy and will no longer
  receive updates"*, which corrected note 03.

### S16 — pandas 3.0 documentation and *What's new in 3.0.0*

- URLs: <https://pandas.pydata.org/pandas-docs/version/3.0/whatsnew/v3.0.0.html> ·
  <https://pandas.pydata.org/pandas-docs/version/3.0/user_guide/copy_on_write.html> ·
  <https://pandas.pydata.org/pandas-docs/version/3.0/user_guide/indexing.html> ·
  <https://pandas.pydata.org/pandas-docs/version/3.0/user_guide/groupby.html> ·
  <https://pandas.pydata.org/pandas-docs/version/3.0/user_guide/text.html>
- Version: 3.0 — installed 3.0.6 [S40]
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-3-Clause
- Used for: note 04 §7. Three claims corrected from it: Copy-on-Write is on
  permanently and cannot be disabled; **`SettingWithCopyWarning` is removed**
  and chained assignment now raises a `ChainedAssignmentError` warning; and
  string columns default to the dedicated `str` dtype, not `object`.

### S17 — Matplotlib 3.11.2 documentation

- URLs: <https://matplotlib.org/3.11.2/users/explain/figure/api_interfaces.html> ·
  <https://matplotlib.org/3.11.2/users/explain/quick_start.html> ·
  <https://matplotlib.org/3.11.2/users/explain/axes/constrainedlayout_guide.html> ·
  <https://matplotlib.org/3.11.2/users/explain/colors/colormaps.html> ·
  <https://matplotlib.org/3.11.2/api/_as_gen/matplotlib.pyplot.subplots.html>
- Version: 3.11.2 — the installed version [S40]
- Retrieved: 2026-09-22
- Access: public. Licence: Matplotlib licence (PSF-based, BSD-compatible)
- Used for: note 04 §1–§6. The *API interfaces* page is the source for the
  Figure → Axes → Axis hierarchy and for preferring the object-oriented
  interface; the layout guide is the source for `layout="constrained"` being the
  current spelling.

### S18 — pytest documentation

- URLs: <https://docs.pytest.org/en/stable/how-to/fixtures.html> ·
  <https://docs.pytest.org/en/stable/how-to/parametrize.html> ·
  <https://docs.pytest.org/en/stable/reference/reference.html> ·
  <https://docs.pytest.org/en/stable/how-to/skipping.html>
- Version: `stable` was 9.x at retrieval; installed pytest is 9.1.1 [S40].
  pytest does not publish a per-minor documentation tree, so `stable` is the
  best available pin.
- Retrieved: 2026-09-22
- Access: public. Licence: MIT
- Used for: note 05 §2–§4 (collection rules, `approx` default `rel=1e-6`,
  fixture scopes, `parametrize`, markers, `xfail(strict=True)`).

### S19 — `numpy.testing` reference

- URL: <https://numpy.org/doc/2.5/reference/generated/numpy.testing.assert_allclose.html>
- Retrieved: 2026-09-22
- Access: public
- Used for: note 05 §5 — `rtol=1e-7`, `atol=0` defaults and the
  $|a-d| \le \text{atol} + \text{rtol}\,|d|$ criterion. Signature defaults
  re-checked in the venv.

### S20 — IPython documentation: built-in magic commands

- URL: <https://ipython.readthedocs.io/en/stable/interactive/magics.html>
- Version: `stable`; installed IPython 9.17.1 [S40]
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-3-Clause
- Used for: the magic table in note 06 §2.

### S21 — Jupyter messaging protocol and `nbformat`

- URLs: <https://jupyter-client.readthedocs.io/en/stable/messaging.html> ·
  <https://nbformat.readthedocs.io/en/latest/format_description.html>
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-3-Clause
- Used for: note 06 §1 — kernel/frontend split, ZeroMQ message types
  (`execute_request`, `execute_result`, `stream`, `display_data`, `error`),
  and the nbformat 4 cell/output JSON schema.

### S22 — `nbconvert` documentation

- URL: <https://nbconvert.readthedocs.io/en/latest/usage.html>
- Retrieved: 2026-09-22
- Access: public
- Used for: note 06 §5 — export targets and `--execute`.

### S23 — PuLP documentation

- URL: <https://coin-or.github.io/pulp/>
- Version: installed PuLP is **4.0.0** since 2026-09-27; 3.3.2 on 2026-09-22 [S40]
- Retrieved: 2026-09-22 (online docs, then for 3.3). The 4.0 facts come from
  the installed wheel's README (`pulp-4.0.0.dist-info/METADATA`, which links
  the migration guide
  <https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html>) and from
  execution in the venv; the online docs were not re-fetched.
- Access: public. Licence: MIT
- Used for: note 07 §7. **This is where the version pin earned its keep, twice.**
  On 2026-09-22 PuLP 3.3 emitted `DeprecationWarning`s for three idioms the note
  originally taught: `LpVariable(name, …)` constructed directly,
  `LpProblem.constraints` used as a dict, and `PULP_CBC_CMD`. On 2026-09-27
  PuLP 4.0.0 had removed all three (`TypeError`, `TypeError`,
  `AttributeError`), plus `LpStatus`/`prob.status` (`solve()` returns an
  `LpSolveStats`) and the bundled CBC binary.

### S24 — HiGHS

- URL: <https://highs.dev/>
- Retrieved: 2026-09-22
- Access: public. Licence: MIT
- Used for: note 07 §6, the solver behind `scipy.optimize.linprog`'s default
  `method="highs"` and behind `milp`; and since 2026-09-27 note 07 §7, where it
  solves the PuLP models because PuLP 4.0 ships no solver (`solve_pulp`).

### S25 — COIN-OR CBC

- URL: <https://github.com/coin-or/Cbc>
- Retrieved: 2026-09-22
- Access: public. Licence: EPL-2.0
- Used for: note 07 §7, the branch-and-cut solver PuLP shells out to through
  `COIN_CMD`. Bundled with PuLP up to 3.x; since PuLP 4.0 a separate install
  (`pulp[cbc]`, i.e. the `cbcbox` wheel, or `cbc` on `PATH`), absent here.

### S26 — PEP 703 (free-threaded CPython) and PEP 734 (sub-interpreters)

- URLs: <https://peps.python.org/pep-0703/> · <https://peps.python.org/pep-0734/>
- Retrieved: 2026-09-22
- Access: public
- Used for: note 08 §1 — the two routes around the GIL, and the fact that they
  are opt-in and not what this course examines.

### S27 — cffi documentation

- URL: <https://cffi.readthedocs.io/en/stable/overview.html>
- Version: `stable`; installed cffi 2.1.1 [S40]
- Retrieved: 2026-09-22
- Access: public. Licence: MIT
- Used for: note 09 §4 — ABI vs API mode.

### S28 — `numpy.f2py` user guide

- URL: <https://numpy.org/doc/2.5/f2py/index.html>
- Retrieved: 2026-09-22
- Access: public
- Used for: note 09 §6 — `-c -m`, `intent(in|out|inout)`, the Meson build
  requirement, column-major argument passing.

### S29 — pybind11 documentation

- URL: <https://pybind11.readthedocs.io/en/stable/>
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-3-Clause
- Used for: note 09 §7.

### S30 — PythonCall.jl / juliacall documentation

- URL: <https://juliapy.github.io/PythonCall.jl/stable/>
- Retrieved: 2026-09-22
- Access: public. Licence: MIT
- Used for: note 09 §8 — the current Julia bridge, zero-copy array sharing and
  the column-major/transpose consequence.

### S31 — Numba documentation

- URL: <https://numba.readthedocs.io/en/stable/user/5minguide.html>
- Retrieved: 2026-09-22
- Access: public. Licence: BSD-2-Clause
- Used for: note 09 §9 and note 10 §6. **Not installed** in the repo venv [S40],
  so every numba claim in the notes is documentation-only and marked as such.

### S32 — Cython documentation

- URL: <https://cython.readthedocs.io/en/latest/src/quickstart/cythonize.html>
- Retrieved: 2026-09-22
- Access: public. Licence: Apache-2.0
- Used for: note 10 §6. Also not installed.

### S33 — Hypothesis documentation

- URL: <https://hypothesis.readthedocs.io/en/latest/>
- Retrieved: 2026-09-22
- Access: public. Licence: MPL-2.0
- Used for: note 05 §6. Not installed; the note's property-based example is
  written as a seeded loop instead.

### S34 — uv documentation

- URL: <https://docs.astral.sh/uv/>
- Retrieved: 2026-09-22
- Access: public. Licence: MIT/Apache-2.0
- Used for: note 01 §10 and note 06 §3 — `uv venv`, `uv sync`, `uv.lock` as the
  fact-vs-intent distinction against `pyproject.toml`.

---

## Primary sources for the algorithms and results the notes state

### S35 — Amdahl, *Validity of the single processor approach to achieving large scale computing capabilities* (1967)

- Author: Gene M. Amdahl. AFIPS '67 (Spring), pp. 483–485.
- DOI: <https://doi.org/10.1145/1465482.1465560>
- Retrieved (metadata): 2026-09-22 via Crossref
- Access: **ACM Digital Library, paywalled. Licence: ACM copyright — cite only,
  not vendored.**
- Used for: note 08 §7, the speedup law $S(n) = 1/\big((1-p) + p/n\big)$.

### S36 — Gustafson, *Reevaluating Amdahl's law* (1988)

- Author: John L. Gustafson. *Communications of the ACM* **31**(5), 532–533.
- DOI: <https://doi.org/10.1145/42411.42415>
- Retrieved (metadata): 2026-09-22 via Crossref
- Access: **ACM copyright — cite only.**
- Used for: note 08 §7, scaled (weak-scaling) speedup $S = (1-p) + pn$.

### S37 — Dormand & Prince, *A family of embedded Runge–Kutta formulae* (1980)

- Authors: J. R. Dormand, P. J. Prince. *J. Comput. Appl. Math.* **6**(1), 19–26.
- DOI: <https://doi.org/10.1016/0771-050X(80)90013-3>
- Retrieved (metadata): 2026-09-22 via Crossref
- Access: **Elsevier, paywalled — cite only.**
- Used for: note 03, the method behind `solve_ivp(method="RK45")`; SciPy's own
  page [S15] names this paper as its reference.

---

## Free, redistributable textbooks on the course's topic

Both are genuinely CC BY 4.0. Neither is named by TISS — **TISS names no
literature at all** [S1] — so they are supplements, not the syllabus.

### S38 — Sundnes, *Introduction to Scientific Programming with Python* (2020) ★

- Author: Joakim Sundnes, Simula Research Laboratory.
  Simula SpringerBriefs on Computing, vol. 6. Springer Cham, 1st edition, 2020.
  XIV + 148 pages. Softcover ISBN 978-3-030-50355-0, eBook ISBN 978-3-030-50356-7.
- DOI: <https://doi.org/10.1007/978-3-030-50356-7>
- PDF: <https://link.springer.com/content/pdf/10.1007/978-3-030-50356-7.pdf> (1.8 MB)
- Retrieved: 2026-09-22
- Access: **Open access. Licence: Creative Commons Attribution 4.0
  International (CC BY 4.0)**, stated per chapter: "This chapter is licensed
  under the terms of the Creative Commons Attribution 4.0 International
  License". Redistributable with attribution — see [`README.md`](README.md) for
  why it is nonetheless not vendored.
- Used for: an independent cross-check of note 01's ordering and of what
  "scientific programming with Python" means as a course. Chapters: Getting
  Started; Computing with Formulas; Loops and Lists; Functions and Branching;
  User Input and Error Handling; Arrays and Plotting; Dictionaries and Strings;
  Classes; Object-Oriented Programming. It is an *introductory* book: it stops
  where note 02 starts, and covers nothing in notes 05–10.

### S39 — *Scientific Python Lectures* (formerly *Scipy Lecture Notes*) ★

- Editors: the Scientific Python developers (Varoquaux, Gouillart, Vahtras,
  Haenel et al.). Release 2024.1 (tagged 2024-04-26) is the latest tagged PDF;
  the live HTML build was 2025.2 development at retrieval.
- URLs: <https://lectures.scientific-python.org/> ·
  <https://github.com/scipy-lectures/scientific-python-lectures> ·
  PDF <https://github.com/scipy-lectures/scientific-python-lectures/releases/download/2024.1/ScientificPythonLectures.pdf>
  (18 MB)
- Retrieved: 2026-09-22
- Access: **Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)**,
  stated in `LICENSE.md`: "All code and material is licensed under a Creative
  Commons Attribution 4.0 International License (CC-by)".
- Used for: the single best free match to this course's *subject list*. Its
  table of contents is almost the TISS list: the Python language, NumPy,
  Matplotlib, SciPy, advanced NumPy, debugging, optimizing code, sparse arrays,
  mathematical optimization, **interfacing with C**, statistics. Used as a
  cross-check on notes 02, 03, 04, 07, 09 and 10, and as the recommended
  companion text in [`../notes/README.md`](../notes/README.md).

---

## Environment

### S40 — Repo environment record: the versions everything was verified against

- URL: none, this is a local measurement, not a document.
- Access: local; reproduce it with
  `uv run pytest src/py/test_doc_examples.py` from this course folder.
- Command: `.venv/bin/python -c "import importlib.metadata as m; ..."` run at
  the repo root on **2026-09-27**, after the venv was re-created with
  `uv sync`. First recorded 2026-09-22.
- Result:

  | package | 2026-09-22 | **2026-09-27** | | package | 2026-09-22 | **2026-09-27** |
  |---|---|---|---|---|---|---|
  | CPython | 3.12.13 | 3.12.13 | | pytest | 9.1.1 | 9.1.1 |
  | NumPy | 2.5.3 | 2.5.3 | | IPython | 9.17.1 | 9.17.1 |
  | SciPy | 1.18.1 | 1.18.1 | | jupyter-core | 5.9.1 | 5.9.1 |
  | pandas | 3.0.6 | 3.0.6 | | notebook | 7.6.3 | 7.6.3 |
  | Matplotlib | 3.11.2 | 3.11.2 | | nbconvert | 7.17.1 | 7.17.1 |
  | PuLP | 3.3.2 | **4.0.0** | | cffi | 2.1.1 | 2.1.1 |
  | SymPy | 1.14.0 | 1.14.0 | | joblib | 1.6.0 | 1.6.0 |

  Also recorded on 2026-09-27: nbclient 0.11.0, ipykernel 7.3.0, threadpoolctl
  3.7.0 (a scikit-learn dependency; listed as not installed on 2026-09-22), C
  compiler `cc` = Apple clang 21.0.0, arm64. NumPy and SciPy report Apple
  Accelerate as BLAS/LAPACK, and `threadpoolctl.threadpool_info()` is empty.

  **Why PuLP moved:** `pyproject.toml` lists `pulp` with no bound and `uv.lock`
  is git-ignored in this repo, so `uv sync` resolved the newest release.

  **Not installed**, therefore only described, never demonstrated: numba,
  Cython, hypothesis, pytest-cov, line_profiler, juliacall, numexpr, py-spy,
  memory_profiler; and **no solver PuLP can call** (no `cbcbox`, `highspy` or
  `cbc`/`highs`/`glpsol` on `PATH`; `pulp.listSolvers(onlyAvailable=True)` is
  `[]`).
- Used for: pinning every library citation above, and for
  [`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py), which
  asserts the major.minor of NumPy, SciPy, pandas, Matplotlib, pytest, PuLP and
  IPython and fails loudly if any of them changes the behaviour a note states.

---

## Substitute practice sources

Added by the **substitute-source pass of 2026-09-22**, which had one job the
verification pass could not do: this course publishes no exercise sheet and no
past paper, so there is nothing to practise on. These are free, licence-clear
teaching materials **for the same subject from elsewhere**, condensed into
`../src/exercises/` and written up in
[`../notes/11-practice-set.md`](../notes/11-practice-set.md).

**They are not this course's material and must never be read as such.** Every
directory under `src/exercises/` names the institution, course, year and licence
it is adapted from in its first lines, and every task was restated in our own
words and reimplemented — nothing is copied, nothing is vendored. Where a source
relied on a downloaded dataset, generated data replaced it, because this repo's
tests do no network I/O.

Two of the four were already registered above and are reused here rather than
renumbered: **[S38] Sundnes** (introductory Python, CC BY 4.0) and **[S39]
Scientific Python Lectures** (CC BY 4.0), the latter as
`src/exercises/scientific-python-lectures-2024/`.

### S41 — Aalto University, *Python for Scientific Computing* ★

- Institution: Aalto University, Aalto Scientific Computing (with CodeRefinery
  and the Nordic e-Infrastructure Collaboration). No course code: it is a
  recurring three-day workshop, not a credited course.
- Authors: the 2020 redesign names Radovan Bast, Richard Darst, Anne Fouilloux,
  Thor Wikfeldt; originally designed by Janne Blomqvist.
- URLs: <https://aaltoscicomp.github.io/python-for-scicomp/> ·
  repository <https://github.com/AaltoSciComp/python-for-scicomp> ·
  exercise index <https://aaltoscicomp.github.io/python-for-scicomp/exercises/>
- Version: the `master` build; most recent commit **2025-11-27**. The site has
  no tagged releases; its footer reads "© Copyright 2020-2024, The contributors."
- Retrieved: 2026-09-22
- Access: public, no login.
- **Licence: the repository's `LICENSE` file reads, in full, "Creative Commons
  Attribution 4.0".** That is a licence *statement*, not the licence text, so
  GitHub's detector reports `NOASSERTION`. Redistribution with attribution is
  clearly intended; nothing is vendored here in any case.
- **Why it is comparable.** Its chapter list is the closest thing to this
  course's TISS subject list that a *taught* free course offers: Introduction to
  Python, Jupyter, NumPy and Advanced NumPy, Pandas, Plotting with Matplotlib,
  Working with Data, Scripts, Profiling, SciPy, Parallel programming, Dependency
  management. Five of the eight TISS subject items are covered, including
  **Parallel programming** (GIL, `multiprocessing.Pool`, `mpi4py`, Dask), which
  note 08 weights highly and which almost no introductory Python course teaches
  at all. Its audience — early-career researchers who already know basic Python
  syntax — is the same audience TISS describes.
- **Where it does not reach.** No optimisation chapter (a TISS subject item *and*
  a learning outcome) and no testing chapter, which is why [S39] and [S42] are
  here too. Xarray, Vega-Altair, Web APIs, Binder and packaging are outside the
  TISS list and were not used.
- Used for: `../src/exercises/aalto-python-for-scicomp-2025/`
  — six tasks covering views vs copies, `*` vs `@` and reduction axes, `out=`,
  pandas `agg` vs `transform`, `quad` and sparse storage, and a seeded parallel
  Monte Carlo with the `cpu_count`-is-not-your-allocation point.

### S42 — Software Carpentry, *Programming with Python* ★

- Organisation: The Carpentries (Software Carpentry). Lesson repository
  `swcarpentry/python-novice-inflammation`.
- URLs: <https://swcarpentry.github.io/python-novice-inflammation/> ·
  repository <https://github.com/swcarpentry/python-novice-inflammation> ·
  licence page <https://swcarpentry.github.io/python-novice-inflammation/LICENSE.html>
- Version: the published build; the lesson is continuously maintained and has no
  release tags. Most recent commit at retrieval: 2026-09-22.
- Retrieved: 2026-09-22
- Access: public, no login.
- **Licence: instructional material CC BY 4.0; example programs and software
  MIT. Copyright (c) The Carpentries.** Quoted from the licence page: all
  Carpentries instructional material "is made available under the Creative
  Commons Attribution license", and the example programs "are made available
  under the OSI-approved MIT license".
- **Why it is comparable.** One episode is the reason it is here: episode 10,
  *Defensive Programming* — assertions, pre- and post-conditions, invariants and
  test-driven development, written as **exercises**. "Code testing" is its own
  item on the TISS subject list, and **neither [S41] nor [S39] has a testing
  chapter**; this is the only free CC-licensed treatment found that is exercises
  rather than API reference. Episodes 1, 4, 5, 7, 8 and 9 cover TISS's
  "Introduction to the Python programming language", and episode 2 introduces
  NumPy's axis reductions on tabular data.
- **Where it does not reach.** It is a novice lesson: four episodes on lists,
  loops and conditionals that note 01 assumes, and its testing is `assert` and
  hand-written TDD, not pytest — no fixtures, no `parametrize`, no `approx`.
  That half of the TISS item stays with pytest's own documentation [S18] and
  note 05. Five of the eight TISS items are absent entirely (SciPy,
  optimisation, parallelism, interfaces, Jupyter).
- Used for: `../src/exercises/software-carpentry-python-2026/`
  — five tasks covering per-axis summaries on generated data, assertions as pre-
  and post-conditions, a test-first `range_overlap` including the touching-ranges
  case, the `try/except/else/finally` order and the exception hierarchy, and the
  fact that `python -O` deletes every `assert`.

### S43 — The executable multiple-choice bank (ours)

- URL: none — this is a local artefact, like [S40], not a document.
- Files: [`../src/exercises/mc_bank.py`](../src/exercises/mc_bank.py),
  `mc_checks.py`, `mc_items.py`, `test_mc_bank.py`.
- Written: 2026-09-22 (the substitute-source pass); re-derived on every test run.
- Licence: not applicable — written for this repo and adapted from nothing. It
  contains no text from [S38]–[S42] and none from any TU Wien source.
- Access: local. Reproduce with
  `uv run pytest src/exercises -q` from the course folder.
- **Provenance: entirely ours.** No past paper for 191.125, for this lecturer or
  for the predecessor number 191.116 is public [S1]–[S9], so there is nothing to
  model the questions on and nothing is adapted from [S38]–[S42] either.
- What it is: 24 multiple-choice items, three per TISS subject item, in the
  format TISS has described since 2024W [S3]. Each item's correct answer is
  **derived by executing the behaviour** against the pinned versions in [S40],
  and the helper functions require exactly one of the four options to match —
  so an item with two defensible answers fails the suite rather than misleading
  a reader. This extends the [`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py)
  pattern from claims in the notes to questions on a paper.
- Used for: [`../notes/11-practice-set.md`](../notes/11-practice-set.md) §2.

---

## What was looked for and does not exist

Recorded so the search is not repeated.

| looked for | where | result |
|---|---|---|
| Lecture slides, script or handouts | TISS literature field, all six offerings [S1]–[S6] | "No lecture notes are available." Every time. |
| A public course homepage for 191.125 | TISS external links; `par.tuwien.ac.at`; Wayback Machine | None has ever existed. Only 191.116/2019W had one [S8], and it says the material is in TUWEL. |
| Past exam papers | VoWi [S9], web search | None. The VoWi page has no attachments and every section is "noch offen". |
| The grading scheme (points, weights, pass mark) | TISS [S1], VoWi [S9] | Not published anywhere. TISS gives only "Part 1 exercises / Part 2 written exam". |
| Exercise sheets | — | In TUWEL only; not fetched. |
| Lecturer-hosted teaching material | `hunoldscience.net`, TU Wien profile, GitHub [S10] | None for this course. |
| Named literature | TISS [S1]–[S7] | The field says "No lecture notes are available" and names no book, in any year. |

Looked for again in the **substitute-source pass**, 2026-09-22:

| looked for | where | result |
|---|---|---|
| A single free course covering all eight TISS subject items | Aalto [S41], Scientific Python Lectures [S39], Software Carpentry [S42], Sundnes [S38] | None exists. Three sources were needed, and two items are still thin — see [`../notes/11-practice-set.md`](../notes/11-practice-set.md) §4. |
| Free CC-licensed exercises on **Julia ↔ Python** interop | the four above; PythonCall.jl docs [S30] | None. [S39] ch. 2.8 teaches C, not Julia; [S30] is reference documentation with no exercises. Note 09's Julia material stays documentation-only. |
| Free CC-licensed exercises on **linear programming / PuLP** | the four above; PuLP docs [S23] | None. [S39] ch. 2.7 is continuous optimisation only; [S41] has no optimisation chapter. PuLP's own case studies are MIT-licensed reference, not graded exercises. The LP/ILP practice in note 11 is **ours**. |
| Practice for **IPython/Jupyter** that a pytest suite can check | [S41] Jupyter and Dependency-management chapters | Partly. Notebook *workflow* is not testable without a kernel session; only the three executable facts in the MC bank [S43] survive as checkable items. |

The consequence for [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md):
there is **no past paper to model questions on**, and every exam-style question
in the notes is ours. The one thing that *is* sourced about the exam is its
format, and it changed in 2024W — see [S3].
