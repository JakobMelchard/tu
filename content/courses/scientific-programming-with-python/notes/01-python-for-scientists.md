# 01 Python for scientists

Code: [`../src/py/python_basics.py`](../src/py/python_basics.py), tests in `test_python_basics.py`.

Sources: the CPython 3.12 language reference and library docs [S11]; uv [S34];
cross-checked against Sundnes, *Introduction to Scientific Programming with
Python* (CC BY 4.0) [S38]. **Verified against CPython 3.12.13** [S40], last re-run 2026-09-27; the
register is [`../refs/SOURCES.md`](../refs/SOURCES.md).

## 1. The data model: everything is an object, names are bindings

A Python variable is a *name* bound to an *object*; objects have identity (`id`), type and value [S11]. Assignment never copies; it binds another name to the same object. `is` compares identity, `==` calls `__eq__`.

```python
a = [1, 2, 3]
b = a            # same object
b.append(4)      # a is [1, 2, 3, 4] too
c = a[:]         # shallow copy: new list, same element objects
```

**Mutable** objects (list, dict, set, bytearray, most user classes, numpy arrays) can change in place; **immutable** ones (int, float, str, tuple, frozenset, bytes) cannot, so any "modification" creates a new object. Hashability follows: dict keys and set members must be immutable (technically: define `__hash__` consistent with `__eq__`). A tuple containing a list is not hashable.

Two consequences examined constantly:

- `x = x + [4]` rebinds `x` to a new list; `x += [4]` calls `list.__iadd__` and mutates the existing list, so every alias sees it. For immutables `+=` always rebinds. (`rebinding_vs_mutation`)
- Default arguments are evaluated **once**, at `def` time. `def f(x, acc=[])` shares one list across calls (`append_bad`). The idiom is `acc=None` and create inside.

Function arguments are passed by *object reference* ("call by sharing"): the callee gets the same object; reassigning the parameter does nothing to the caller, mutating it does.

Scoping is LEGB (local, enclosing, global, builtin), decided at compile time [S11]: any assignment to a name anywhere in a function makes it local for the whole function, so `x += 1` in a nested function raises `UnboundLocalError` unless you declare `nonlocal x` (or `global x`).

## 2. Comprehensions

`[f(x) for x in it if p(x)]` builds a list eagerly; `{k: v for ...}` a dict; `{x for ...}` a set; `(f(x) for x in it)` is a **generator expression**, lazy and single-pass. Nested clauses read left to right like nested `for` loops. Comprehensions have their own scope (the loop variable does not leak). `primes_below` is a set-comprehension sieve; `transpose` uses `zip(*rows)`, the standard unzip idiom.

## 3. Iterators and generators

The **iterator protocol**: `iter(obj)` calls `obj.__iter__()`, which returns an iterator; `next(it)` calls `it.__next__()` until it raises `StopIteration`. A `for` loop is sugar for exactly this. An *iterable* is anything with `__iter__` (list, range, file, dict); an *iterator* is additionally consumed by `next` and is exhausted afterwards. `Countdown` implements it by hand.

A **generator function** contains `yield`; calling it runs nothing and returns a generator object whose frame is paused at each `yield` and resumed by `next`. State lives in local variables, memory is O(1), and it can be infinite (`fibonacci`). Generators compose into pipelines (`running_mean(filter(..., map(...)))`) where nothing is materialised until consumed. `yield from` delegates to a sub-generator; `send()` pushes values in (coroutine style); a `return` inside a generator ends it (`StopIteration.value`).

Pitfall: a generator can be iterated **once**. `list(g)` twice gives `[]` the second time. `zip`, `map`, `filter`, `dict.items()` views and file objects are also single-pass or live views.

## 4. Closures and late binding

A nested function captures variables of the enclosing scope by *reference to the cell*, not by value. Reading needs nothing; rebinding needs `nonlocal` (`make_counter`). Because lookup happens at call time, `[lambda: i for i in range(3)]` yields `2, 2, 2` (`late_binding_bad`); the fix is to freeze the value with a default argument `lambda i=i: i` or `functools.partial`.

## 5. Decorators

A decorator is a callable that takes a function and returns a function; `@deco` above `def f` is exactly `f = deco(f)`. The returned wrapper usually takes `*args, **kwargs` and is wrapped with `functools.wraps(fn)` so `__name__`, `__doc__`, `__wrapped__` survive (introspection, pytest, pickling). A decorator *with arguments* is a function returning a decorator (`repeat(3)`). Standard-library decorators to know: `functools.lru_cache` / `cache` (memoisation; only for pure functions with hashable args), `functools.wraps`, `property`, `staticmethod`, `classmethod`, `dataclass`, `contextlib.contextmanager`. `memoize` in the code shows what `lru_cache` does; `fib(80)` becomes linear instead of exponential.

## 6. Classes and dataclasses

Operators dispatch to dunder methods: `a + b` tries `a.__add__(b)`, then `b.__radd__(a)`; `2 * v` needs `__rmul__` on `Vector`. `__repr__` is for developers (unambiguous, ideally evaluable), `__str__` for users. `__eq__` without `__hash__` makes instances unhashable. `__slots__` replaces the per-instance `__dict__` with fixed slots: less memory, faster attribute access, no dynamic attributes.

`@property` turns a method into a computed attribute; `@classmethod` receives the class (alternative constructors like `Vector.polar`); `@staticmethod` receives nothing.

`@dataclass` generates `__init__`, `__repr__`, `__eq__` from the annotated fields; `order=True` adds comparisons in field order; `frozen=True` forbids assignment and makes instances hashable; `field(default_factory=list)` for mutable defaults; `field(compare=False)` excludes a field from `__eq__`/ordering (`Measurement`). `slots=True` (3.10+) combines both worlds; the full parameter list in 3.12 is `init, repr, eq, order, unsafe_hash, frozen, match_args, kw_only, slots, weakref_slot` [S11]. `typing.NamedTuple` is the tuple-based alternative.

## 7. Typing

Annotations are metadata, not enforced at run time; `mypy`/`pyright` check them statically. Modern syntax: `list[int]`, `dict[str, float]`, `int | None`, `Callable[[float], float]`, `Iterable[T]`, `TypeVar`, `Protocol` for structural typing, `numpy.typing.NDArray[np.float64]`. `from __future__ import annotations` makes annotations lazy strings (forward references, cheaper). In scientific code the payoff is documentation and IDE help; the cost is near zero.

## 8. Exceptions

`try / except Type as e / else / finally`: `else` runs when no exception occurred, `finally` always. Catch specific exceptions, not bare `except:` (it also swallows `KeyboardInterrupt`). Define domain exceptions by subclassing (`ConvergenceError(RuntimeError)`) and attach data; `raise ... from e` chains causes. EAFP ("easier to ask forgiveness") is idiomatic: `try: float(s) except ValueError` instead of pre-validating. numpy floating errors are *not* exceptions by default (`1/0.` in an array gives `inf` and a warning); `np.errstate(divide="raise")` converts them.

## 9. Context managers

`with cm as x:` calls `cm.__enter__()`, binds the result to `x`, and guarantees `cm.__exit__(type, value, tb)` runs even if the block raises; returning `True` from `__exit__` suppresses the exception. `contextlib.contextmanager` builds one from a generator: code before `yield` is enter, after is exit (put it in `finally`). Use cases: files, locks, timers (`Timer`), temporary settings (`temporarily`, like `np.errstate`, `np.printoptions`, `plt.rc_context`), `tempfile.TemporaryDirectory`, `contextlib.suppress`, `ExitStack` for a dynamic number of managers.

## 10. Packaging and environments with uv

- A **module** is a `.py` file, a **package** a directory with `__init__.py` (or a namespace package without). `import x` searches `sys.path` (script directory first, then site-packages). `python -m pkg.mod` runs a module with the package context; `if __name__ == "__main__":` separates script behaviour from import behaviour.
- A **virtual environment** is a directory with its own `python` symlink and `site-packages`, isolating dependencies per project. `uv venv --python 3.12 .venv` creates one; `.venv/bin/python` uses it without "activation".
- `pyproject.toml` declares the project (`[project] dependencies = [...]`, build backend); `uv sync` resolves and installs into `.venv` and writes `uv.lock`, a *lock file* pinning exact versions and hashes for reproducibility [S34]. `uv pip install numpy` for ad-hoc installs, `uv run script.py` to run inside the env, `uv add scipy` to add a dependency. Speed comes from Rust, a global cache and hard links.
- Semantic versioning constraints: `numpy>=2,<3`. Pin exact versions in the lock file, ranges in `pyproject.toml`.
- This repo: `pyproject.toml` at the repo root, env `.venv` there (created with `uv sync`); run `uv run pytest src` from the course folder.

## Pitfalls checklist

1. Mutable default arguments; `+=` on a shared list; shallow vs deep copy (`copy.deepcopy`).
2. Integer division: `/` is always float, `//` floors (towards $-\infty$, so `-7 // 2 == -4`), `%` has the sign of the divisor.
3. `0.1 + 0.2 != 0.3`: compare floats with `math.isclose` / `pytest.approx`; `round` is banker's rounding (`round(2.5) == 2`).
4. Chained comparisons `0 < x < 1` work; `is` for `None` (and `True`/`False`) only, never for numbers or strings. The reason is not "small-int caching" alone: CPython caches `-5..256` as singletons *and* shares equal constants inside one code object, so at module scope `a = 257; b = 257; a is b` is **True** in CPython 3.12, and so is `257 is 257` — while the same comparison across two separately compiled units is False. Nothing here is guaranteed by the language, which is why CPython 3.12 emits `SyntaxWarning: "is" with 'int' literal` when you write it [S11]. Verified in the venv; see `test_identity_comparison_is_not_a_value_test`.
5. Late binding in closures; generators are single-pass; modifying a list while iterating over it skips elements.
6. `sorted()` returns a new list, `list.sort()` returns `None`.
7. Strings are immutable: build with `"".join(parts)` or f-strings, not `+=` in a loop.

## Exam-style questions

**All five are ours.** No public past paper exists for this course — see
[`00-exam-focus.md`](00-exam-focus.md). They are written in the multiple-choice
style the 2024W-onwards examination modalities imply [S3].

1. What does `f()` return on the third call, given `def f(x=[]): x.append(1); return len(x)`?
   (a) 1 (b) 2 (c) 3 (d) TypeError
   **c.** The default list is created once and grows with every call.

2. After `a = [1, 2]; b = a; a = a + [3]`, what is `b`?
   (a) `[1, 2]` (b) `[1, 2, 3]` (c) `[3]` (d) error
   **a.** `a + [3]` creates a new list and rebinds `a`; `b` still names the old one. With `a += [3]` the answer would be (b).

3. Which statement about generators is true?
   (a) Calling a generator function runs its body to the first `yield`. (b) A generator can be iterated any number of times. (c) `next()` on an exhausted generator raises `StopIteration`. (d) Generators must be finite.
   **c.** Calling only creates the object; nothing runs until `next`. They are single-pass and may be infinite.

4. `fs = [lambda: i for i in range(3)]; [f() for f in fs]` gives
   (a) `[0, 1, 2]` (b) `[2, 2, 2]` (c) `[0, 0, 0]` (d) NameError
   **b.** `i` is looked up when each lambda is called, after the loop finished with `i == 2`.

5. Which is true of `@dataclass(frozen=True)`?
   (a) Instances are hashable and attribute assignment raises. (b) Fields cannot have defaults. (c) `__eq__` is not generated. (d) Only `__init__` is generated.
   **a.** frozen forbids assignment (FrozenInstanceError) and, together with the generated `__eq__`, makes instances hashable.
