"""Tests for python_basics.py (note 01): data model, closures, generators, classes."""
import math

import pytest

import python_basics as pb


def test_mutable_default_is_shared():
    pb.append_bad.__defaults__[0].clear()
    assert pb.append_bad(1) == [1]
    assert pb.append_bad(2) == [1, 2]
    assert pb.append_good(1) == [1] and pb.append_good(2) == [2]


def test_rebinding_vs_mutation():
    assert pb.rebinding_vs_mutation() == ([1, 2, 3], [1, 2, 3, 4])


def test_comprehensions():
    assert pb.primes_below(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert pb.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_iterators_and_generators():
    assert list(pb.Countdown(3)) == [3, 2, 1]
    it = iter(pb.Countdown(1)); next(it)
    with pytest.raises(StopIteration):
        next(it)
    assert pb.take(8, pb.fibonacci()) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(pb.running_mean([2, 4, 6])) == [2, 3, 4]


def test_closures():
    c = pb.make_counter()
    assert [c(), c(), c()] == [1, 2, 3]
    assert pb.late_binding_bad() == [2, 2, 2]
    assert pb.late_binding_good() == [0, 1, 2]


def test_decorators():
    @pb.timed
    def f(x):
        "doc"
        return x * 2
    assert f(3) == 6 and f.__name__ == "f" and f.__doc__ == "doc"
    assert f.last_seconds >= 0
    assert pb.fib(50) == 12586269025 and (50,) in pb.fib.cache
    calls = []
    @pb.repeat(3)
    def g():
        calls.append(1)
    g()
    assert len(calls) == 3


def test_vector_class():
    v = pb.Vector(3, 4)
    assert abs(v) == 5 and v + v == pb.Vector(6, 8) and 2 * v == v * 2
    assert math.isclose(pb.Vector.polar(1, math.pi / 2).angle, math.pi / 2)
    with pytest.raises(AttributeError):        # __slots__: no new attributes
        v.z = 1


def test_dataclass():
    a, b = pb.Measurement(0.0, 1.0, ("x",)), pb.Measurement(0.0, 1.0, ("y",))
    assert a == b                       # tags has compare=False
    assert a < pb.Measurement(1.0, 0.0)
    assert hash(a) == hash(b)
    with pytest.raises(Exception):      # FrozenInstanceError
        a.value = 2.0


def test_exceptions():
    assert math.isclose(pb.newton_sqrt(2.0), math.sqrt(2.0), rel_tol=1e-12)
    with pytest.raises(ValueError):
        pb.newton_sqrt(-1)
    with pytest.raises(pb.ConvergenceError) as info:
        pb.newton_sqrt(2.0, tol=0.0, max_iter=3)
    assert info.value.iterations == 3
    assert isinstance(info.value, RuntimeError)
    assert pb.parse_float_or_default("x", 1.5) == 1.5


def test_context_managers():
    with pb.Timer() as t:
        pass
    assert t.seconds >= 0

    class Cfg:
        level = 1
    with pytest.raises(KeyError):
        with pb.temporarily(Cfg, "level", 5):
            assert Cfg.level == 5
            raise KeyError
    assert Cfg.level == 1               # restored despite the exception
