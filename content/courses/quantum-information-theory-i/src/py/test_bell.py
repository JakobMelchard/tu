import numpy as np
import pytest

from bell import (cabello_check, chsh_operator, chsh_value, hemisphere_value, horodecki_max_chsh,
                  local_bound, max_chsh_numeric, noncontextual_assignments, pentagram,
                  square_contexts, tsirelson_identity_error, werner)
from states import BELL, dm, random_pure


def test_local_bound_is_two():
    assert local_bound() == 2


def test_tsirelson_bound_attained_by_singlet():
    z, x = np.array([0, 0, 1.0]), np.array([1.0, 0, 0])
    v = chsh_value(dm(BELL["psi-"]), z, x, -(z + x) / np.sqrt(2), -(z - x) / np.sqrt(2))
    assert v == pytest.approx(2 * np.sqrt(2))


def test_operator_norm_never_exceeds_tsirelson():
    rng = np.random.default_rng(0)
    for _ in range(300):
        B = chsh_operator(*[rng.normal(size=3) for _ in range(4)])
        assert np.abs(np.linalg.eigvalsh(B)).max() <= 2 * np.sqrt(2) + 1e-12
    assert tsirelson_identity_error(rng) < 1e-12


def test_numeric_optimum_matches_horodecki_and_tsirelson():
    rng = np.random.default_rng(1)
    assert max_chsh_numeric(dm(BELL["phi+"]), rng, restarts=6) == pytest.approx(2 * np.sqrt(2), abs=1e-6)
    psi = random_pure(4, rng)
    assert max_chsh_numeric(dm(psi), rng, restarts=8) == pytest.approx(horodecki_max_chsh(dm(psi)), abs=1e-5)


def test_pure_entangled_states_violate_gisin():
    # |psi> = cos t|00> + sin t|11>: max CHSH = 2 sqrt(1 + sin^2 2t) > 2 for t not in {0, pi/2}
    for t in (0.1, 0.4, np.pi / 4):
        psi = np.array([np.cos(t), 0, 0, np.sin(t)])
        assert horodecki_max_chsh(dm(psi)) == pytest.approx(2 * np.sqrt(1 + np.sin(2 * t) ** 2))


def test_werner_threshold_one_over_sqrt2():
    assert horodecki_max_chsh(werner(1 / np.sqrt(2))) == pytest.approx(2)
    assert horodecki_max_chsh(werner(0.5)) < 2   # entangled (p > 1/3) but no CHSH violation
    assert horodecki_max_chsh(werner(0.8)) > 2


def test_peres_mermin_square():
    ctx = square_contexts()
    assert sorted(s for _, s in ctx) == [-1, 1, 1, 1, 1, 1]
    assert noncontextual_assignments([(i, j) for i in range(3) for j in range(3)], ctx) == 0


def test_mermin_pentagram():
    ops, lines = pentagram()
    assert all(commute for _, _, commute in lines)
    assert [s for _, s, _ in lines].count(-1) == 1
    assert all(sum(k in l for l, _, _ in lines) == 2 for k in ops)  # every observable on two lines
    assert noncontextual_assignments(list(ops), [(l, s) for l, s, _ in lines]) == 0


def test_cabello_18_vector_kochen_specker():
    orth, n, incidences, colourings = cabello_check()
    assert orth and n == 18 and incidences == {2} and colourings == 0


def test_qubit_admits_noncontextual_model():
    rng = np.random.default_rng(2)
    for _ in range(500):
        n = rng.normal(size=3)
        assert hemisphere_value(n) + hemisphere_value(-n) == 1
