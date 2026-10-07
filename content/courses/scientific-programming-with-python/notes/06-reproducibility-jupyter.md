# 06 Reproducible and interactive data processing with IPython/Jupyter

Notebook: [`../src/notebooks/tour.ipynb`](../src/notebooks/tour.ipynb); run `uv run jupyter nbconvert --to notebook --execute src/notebooks/tour.ipynb --output /tmp/tour_out.ipynb`.

Sources: IPython's built-in magics reference [S20], the Jupyter messaging
protocol and `nbformat` format description [S21], `nbconvert` [S22], NEP 19
[S14], uv [S34]. **Verified against IPython 9.17.1, jupyter-core 5.9.1,
notebook 7.6.3 and nbconvert 7.17.1** [S40], last re-run 2026-09-27.

This is the note the course's own teaching method points at: TISS says the
teaching methods are "programming exercises" and *"small software projects using
Jupyter notebooks"* [S1].

## 1. Architecture: kernels, frontends, the .ipynb file

**IPython** is an enhanced interactive Python shell: tab completion, object introspection (`obj?` docstring, `obj??` source, `dir`, `%pdoc`), history (`_`, `__`, `Out[3]`, `In`), shell escapes (`!ls`, `files = !ls *.csv`), and **magics**. **Jupyter** separates the *frontend* (Notebook, JupyterLab, VS Code, console) from the *kernel* (the process that executes code). They talk over ZeroMQ sockets with JSON messages (`execute_request`, `execute_result`, `stream`, `display_data`, `error`) defined by the Jupyter messaging protocol [S21]; the kernel spec (`jupyter kernelspec list`) tells the frontend how to start a kernel, which is how one JupyterLab drives Python, Julia (IJulia), R (IRkernel) or a second venv (`python -m ipykernel install --user --name cse`).

A notebook is a **JSON file** (`nbformat` 4) with a list of cells (`markdown`, `code`, `raw`), each code cell carrying `source`, `execution_count` and `outputs` (streams, `text/plain`, `image/png` as base64, `text/html`, errors) [S21]. Outputs are stored *in the file*, so a notebook is both code and a document, and can be large and unreadable in `git diff` (`nbstripout`, `nbdime` help). The kernel keeps all state (variables, imports) in memory between cells; the file does not know in which order cells were executed, only the `execution_count` numbers hint at it.

## 2. Magics

Line magics `%x args` act on one line, cell magics `%%x` on a whole cell; both are IPython syntax, not Python (a `.py` script fails on them, `get_ipython().run_line_magic` is the underlying call) [S20]. The ones to know:

| Magic | Does |
|---|---|
| `%time stmt` / `%%time` | wall and CPU time of one run |
| `%timeit stmt` / `%%timeit` | best of many runs (autorange, `-n`, `-r`), the right tool for micro-benchmarks |
| `%prun f()` / `%%prun` | cProfile; `%lprun -f f f()` line profiler (extension), `%memit` (memory_profiler) |
| `%matplotlib inline` / `widget` | render figures as PNG into the notebook / interactive widget |
| `%run script.py` | run a script in the kernel namespace (`-i` share variables) |
| `%load_ext autoreload` + `%autoreload 2` | re-import edited modules automatically |
| `%who`, `%whos`, `%who_ls type` | list variables |
| `%debug`, `%pdb` | post-mortem debugger after an exception |
| `%env`, `%cd`, `%pwd`, `%ls` | shell-like |
| `%%writefile f.py`, `%load f.py` | write/load cell content |
| `%%bash`, `%%script julia` | run the cell in another interpreter |
| `%lsmagic`, `%quickref` | list and cheat sheet |

`tour.ipynb` uses `%time`, `%timeit`, `%%time`, `%who_ls`, `%matplotlib inline`.

## 3. Reproducibility

Reproducible means: the same inputs, code and environment give the same outputs, on another machine and a year later. The layers:

1. **Seeds.** Every source of randomness gets an explicit seed: `rng = np.random.default_rng(2026)` passed into functions; `random.Random(seed)`; `torch.manual_seed`; scipy `random_state=rng`. Avoid global state (`np.random.seed`) that any imported library can advance. For parallel work spawn child seeds (`SeedSequence.spawn`, note 08). Seeded does not mean bit-identical across numpy versions or BLAS builds (summation order, SIMD width): report tolerances, not equality, across platforms. This is policy, not accident — NEP 19 [S14] explicitly declines to guarantee a `Generator`'s stream across releases, reserving stream compatibility for the legacy `RandomState` only. Pin the version in the lock file if bit-identical output matters.
2. **Floating point.** Results depend on operation order: `a.sum()` (pairwise) $\neq$ `np.cumsum(a)[-1]` (sequential) in the last bits; multithreaded BLAS reductions can differ run to run; `math.fsum` is the correctly rounded reference. Set `OMP_NUM_THREADS=1` for bitwise repeatability if it matters.
3. **Environment pinning.** Record Python and package versions (`importlib.metadata.version`, `pip freeze`, `uv pip freeze`, `conda env export`), and better, use a **lock file** (`uv.lock` from `uv sync` [S34], `requirements.txt` with `==` and `--hash`, `conda-lock`) so a rebuild resolves to identical wheels. `pyproject.toml` states intent (ranges), the lock file states fact (exact versions). Containers (Docker) freeze the OS layer too. These notes practise it: [S40] is the recorded environment they were written against, and [`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py) fails if it drifts. It did: this repo's `pyproject.toml` lists `pulp` with no bound and its `uv.lock` is git-ignored, so re-creating the venv on 2026-09-27 resolved PuLP 4.0.0 instead of 3.3.2, a major version that removed the API note 07 used. Intent without a committed lock file is not a pin.
4. **Data and provenance.** Keep raw data immutable, derived data regenerable by scripts; hash inputs; record git commit (`git rev-parse HEAD`) and parameters next to outputs; save arrays with `np.save`/`np.savez`, tables as CSV/Parquet, metadata as JSON.
5. **Execution order.** "Restart kernel and run all" is the only way to know a notebook is in a valid state; `nbconvert --execute` does exactly this from the command line and fails on the first error, so it works as a test (CI). [`../src/notebooks/test_tour.py`](../src/notebooks/test_tour.py) does the same inside pytest with `nbclient` and also checks that the execution counts run 1, 2, 3, ... top to bottom.

## 4. Notebook hygiene

- Keep notebooks short and linear: imports and config at the top, one idea per cell, markdown headings, no hidden state (a cell that only works if another was run twice).
- Move stable functions into a module (`src/py/*.py`), import them, and test them with pytest; the notebook becomes a narrative that calls tested code. `%autoreload 2` makes the loop comfortable.
- Do not `import *`, do not shadow builtins, do not rely on `Out[n]`.
- Long computations: run once, `np.save` the result, load in a separate cell; or move to a script run with `nohup`/a job scheduler.
- Clear outputs before committing (`jupyter nbconvert --clear-output --inplace`, `nbstripout`), unless the outputs are the deliverable (then commit the executed copy separately or export to HTML/PDF).
- Print an environment record at the end (versions, seed, date) as in the tour notebook.
- Use `pathlib.Path` and paths relative to the notebook or a configured root; never hard-code an absolute path into your home directory.

## 5. nbconvert and friends

`jupyter nbconvert --to html|pdf|slides|script|markdown|notebook tour.ipynb` [S22]; `--execute` runs it first (`--ExecutePreprocessor.timeout=600`), `--output` names the file, `--no-input` hides code for reports, `--to script` extracts a `.py`. `papermill` parametrises and executes notebooks (inject a parameters cell) for batch runs; `jupytext` pairs a notebook with a plain `.py`/`.md` file that diffs cleanly; `nbval` and `nbmake` run notebooks as pytest tests; `voila` turns one into a dashboard; `jupyter-book` builds documentation.

## 6. When not to use notebooks

- Anything that must run unattended (pipelines, cron jobs, HPC batch): scripts with argparse, or a package with a CLI.
- Code that needs tests, review and reuse: modules. Notebooks cannot be imported cleanly, are hard to diff, and encourage global state.
- Long-running or memory-heavy computations: a crashed kernel loses everything; scripts checkpoint to disk.
- Parallel code with `multiprocessing` on macOS/Windows: the `spawn` start method must import worker functions from a file, so functions defined in notebook cells fail to pickle (put them in a module).
- Anything where execution-order bugs are dangerous (production analysis): use notebooks for exploration and reporting, scripts for the pipeline.

Rule of thumb: explore in a notebook, then promote every reused function to a module with a test; the notebook shrinks to a story with plots.

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md).

1. In Jupyter, where do the variables of a notebook live?
   (a) in the `.ipynb` file (b) in the browser tab (c) in the kernel process, until it is restarted (d) in the Jupyter server
   **c.** The file stores source and outputs only; state is in the kernel's memory.

2. `%%timeit` differs from `%time` in that it
   (a) measures a whole cell and repeats it many times, reporting mean and standard deviation (b) measures CPU time only (c) is plain Python syntax (d) profiles by line
   **a.** `%time` runs once; `timeit` autoranges the loop count and repeats, disabling GC.

3. Two runs of a seeded simulation give results differing in the 15th digit on two different machines. The most likely cause is
   (a) the seed was ignored (b) different BLAS/SIMD summation order in floating-point reductions (c) a bug in numpy's Generator (d) Jupyter caching
   **b.** Floating-point addition is not associative; a seed fixes the random inputs, not the reduction order.

4. Which action guarantees a notebook's outputs correspond to a top-to-bottom execution of its current code?
   (a) Save (b) Run the last cell (c) Restart kernel and run all (or `nbconvert --execute`) (d) Clear outputs
   **c.**

5. `uv.lock` (or a pinned requirements file) is needed in addition to `pyproject.toml` because
   (a) pyproject cannot list dependencies (b) pyproject states version *ranges*; the lock file records the exact resolved versions so the environment can be rebuilt identically (c) uv ignores pyproject (d) the lock file contains the source code
   **b.**
