"""Tests for bayes.py: the naive Bayes family, and the course's hand-calculation
convention for it [S14].  The Bayesian-network tests are in test_bayesnet.py.
"""
import numpy as np
import pytest
from sklearn import naive_bayes as sknb
from sklearn.datasets import make_classification

import bayes

X, y = make_classification(300, 6, n_informative=4, n_classes=3, random_state=0)


def test_gaussian_nb():
    ours, theirs = bayes.GaussianNB().fit(X, y), sknb.GaussianNB().fit(X, y)
    assert np.array_equal(ours.predict(X), theirs.predict(X))
    assert np.allclose(ours.predict_proba(X), theirs.predict_proba(X), atol=1e-6)


def test_multinomial_and_bernoulli_nb():
    rng = np.random.default_rng(0)
    Xc = rng.poisson(np.where(y[:, None] == np.arange(6)[None, :] % 3, 4, 1))
    assert np.array_equal(bayes.MultinomialNB(1.0).fit(Xc, y).predict(Xc), sknb.MultinomialNB(alpha=1.0).fit(Xc, y).predict(Xc))
    Xb = (Xc > 2).astype(int)
    assert np.array_equal(bayes.BernoulliNB(1.0).fit(Xb, y).predict(Xb), sknb.BernoulliNB(alpha=1.0).fit(Xb, y).predict(Xb))


# ------- the course's own hand-calculation convention for naive Bayes [S14] -------
# The four-row table of [S14] "How to Predict a Class with Naive Bayes".
S14_X = np.array([[True, "Small", False],
                  [False, "Medium", False],
                  [True, "Small", True],
                  [True, "Large", False]], dtype=object)
S14_Y = np.array(["A", "B", "B", "A"])


def test_s14_printed_number_is_reproduced_for_the_sample_it_actually_used():
    """[S14] prints Likelihood(A) = 3/3 * 1/3 * 1/3 * 2/4 = 0.05555.

    That first factor is P(F1 = True | A), carried over from the sheet's generic
    formula line -- so the printed number belongs to the sample (True, Medium,
    True), not to the (False, Medium, True) the sheet asks about.  We reproduce
    it exactly for the sample it really corresponds to.
    """
    nb = bayes.CategoricalNB(course_laplace=True).fit(S14_X, S14_Y)
    lik = nb.likelihoods(np.array([True, "Medium", True], dtype=object))
    assert lik["A"] == pytest.approx(3 / 3 * 1 / 3 * 1 / 3 * 2 / 4)
    assert lik["A"] == pytest.approx(0.055555, abs=1e-5)


def test_s14_example_with_the_sample_it_states():
    """With the stated sample (False, Medium, True) the answer is B, not A."""
    nb = bayes.CategoricalNB(course_laplace=True).fit(S14_X, S14_Y)
    new = np.array([False, "Medium", True], dtype=object)
    lik = nb.likelihoods(new)
    assert lik["A"] == pytest.approx(1 / 3 * 1 / 3 * 1 / 3 * 2 / 4)     # 0.018519
    assert lik["B"] == pytest.approx(2 / 3 * 2 / 3 * 2 / 3 * 2 / 4)     # 0.148148
    proba = dict(zip(nb.classes_, nb.predict_proba([new])[0]))
    assert proba["B"] == pytest.approx(0.888888, abs=1e-5)
    assert nb.predict([new])[0] == "B"


def test_course_laplace_adds_one_to_numerator_and_denominator():
    """P(F=v|C) = (count + 1) / (n_C + 1), and the prior stays unsmoothed [S14]."""
    nb = bayes.CategoricalNB(course_laplace=True).fit(S14_X, S14_Y)
    assert nb.conditional("A", 0, True) == pytest.approx(3 / 3)
    assert nb.conditional("A", 1, "Medium") == pytest.approx(1 / 3)
    assert nb.prior_["A"] == pytest.approx(0.5)
    # not a proper distribution: the smoothed values of one attribute overshoot 1
    total = sum(nb.conditional("A", 1, v) for v in nb.values_[1])
    assert total > 1.0


def test_textbook_laplace_is_a_proper_distribution():
    nb = bayes.CategoricalNB(textbook=True, alpha=1.0).fit(S14_X, S14_Y)
    for j in range(S14_X.shape[1]):
        for c in nb.classes_:
            total = sum(nb.conditional(c, j, v) for v in nb.values_[j])
            assert total == pytest.approx(1.0)


def test_zero_frequency_without_smoothing_vetoes_a_class():
    """The zero-frequency problem the exam asks about [S12]."""
    nb = bayes.CategoricalNB(course_laplace=False).fit(S14_X, S14_Y)
    lik = nb.likelihoods(np.array([False, "Medium", True], dtype=object))
    assert lik["A"] == 0.0          # A never has F1 = False -> the whole product dies
    assert lik["B"] > 0.0


def test_missing_values_are_skipped_not_imputed():
    """During training the row is left out of that attribute's count; at prediction
    time the attribute is dropped from the product [S12]."""
    nb = bayes.CategoricalNB(course_laplace=True).fit(S14_X, S14_Y)
    full = nb.likelihoods(np.array([True, "Small", False], dtype=object))
    partial = nb.likelihoods(np.array([True, None, False], dtype=object))
    for c in nb.classes_:
        assert partial[c] == pytest.approx(full[c] / nb.conditional(c, 1, "Small"))


def test_categorical_nb_agrees_with_sklearn_when_smoothing_matches():
    """With the textbook add-alpha rule our posteriors match sklearn's CategoricalNB."""
    rng2 = np.random.default_rng(3)
    Xc = rng2.integers(0, 3, (120, 4))
    yc = (Xc[:, 0] + Xc[:, 1] > 2).astype(int)
    ours = bayes.CategoricalNB(textbook=True, alpha=1.0).fit(Xc.astype(object), yc)
    ref = sknb.CategoricalNB(alpha=1.0, force_alpha=True).fit(Xc, yc)
    assert np.array_equal(ours.predict(Xc.astype(object)), ref.predict(Xc))
    assert np.allclose(ours.predict_proba(Xc.astype(object)), ref.predict_proba(Xc), atol=1e-8)
