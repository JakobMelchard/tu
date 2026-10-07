"""Runs the worked past papers in ../exercises and checks their answers.

Each solution.py carries its own check() with the exact numbers; the tests
below run it and add the structural assertions (verdicts consistent with greedy
sets, conventions differing by exactly 2m, and so on).

The papers themselves are not reproduced -- see ../exercises/README.md.  Each
solution module exposes solve() returning a dict; the assertions below are what
the paper asked for, and where a transcript records a specific outcome the test
pins that outcome.
"""
import importlib.util
import os

import numpy as np
import pytest

EX = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exercises"))
PAPERS = ("2019-10-18", "2020-06-25", "2020-09-09", "2022-06-30", "2026-01-27")


def load(folder):
    path = os.path.join(EX, folder, "solution.py")
    spec = importlib.util.spec_from_file_location(f"ex_{folder.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def papers():
    return {f: load(f) for f in PAPERS}


def test_every_paper_runs(papers):
    for name, mod in papers.items():
        assert isinstance(mod.solve(), dict), name


@pytest.mark.parametrize("folder", PAPERS)
def test_every_paper_passes_its_own_check(papers, folder):
    """Each solution.py asserts its numeric answers in check(); run it here too."""
    mod = papers[folder]
    doc = mod.__doc__
    assert "Questions answered" in doc and "[S11]" in doc, folder   # states question and source
    mod.check(mod.solve())


# ------------------------------------------------------- E19b, 18.10.2019
def test_2019_10_18(papers):
    r = papers["2019-10-18"].solve()

    a = r["4"]      # two concentric rings
    assert a["perceptron_train_accuracy"] < 0.75          # one hyperplane cannot enclose a ring
    assert a["svm_rbf_train_accuracy"] == 1.0
    assert a["svm_poly2_train_accuracy"] == 1.0
    assert a["knn1_train_accuracy"] == 1.0
    assert a["tree_train_accuracy"] == 1.0

    b = r["5"]      # AdaBoost on -1, +1, -1
    assert b["initial_weights"] == [pytest.approx(1 / 3)] * 3      # the graded answer [S12]
    assert b["best_stump_error"] == pytest.approx(1 / 3)
    assert b["alpha"] == pytest.approx(0.5 * np.log(2))
    assert max(b["weights_after_round_1"]) == pytest.approx(0.5)
    assert sum(b["weights_after_round_1"]) == pytest.approx(1.0)
    assert b["upweighted_index"] in b["misclassified"]

    c = r["6"]      # support vectors of four points
    assert c["support_vectors"] == [1, 2]
    assert c["boundary_slope"] == pytest.approx(-1.0)
    assert c["all_correct"]

    d = r["7"]      # 3-NN then naive Bayes without Laplace
    assert d["knn_predictions"] == ["A", "B", "B"]
    assert d["nb_predictions"] == ["A", "B", "B"]
    assert d["precision_B"] == 1.0 and d["recall_B"] == 1.0
    # without Laplace every wrong class is vetoed by a zero factor
    assert any(0.0 in row.values() for row in d["nb_likelihoods"])


# ------------------------------------------------------- E20b, 25.06.2020
def test_2020_06_25(papers):
    r = papers["2020-06-25"].solve()

    a = r["17"]     # LOOCV
    assert a["1nn_training_error"] == 0.0                 # resubstitution, the T/F item
    assert a["1nn"]["error_rate"] > 0.0                   # but LOOCV is not free
    assert a["3nn"]["error_rate"] < a["1nn"]["error_rate"]
    assert a["1nn"]["accuracy"] == pytest.approx(1 - a["1nn"]["error_rate"])

    b = r["18"]     # 1R, the transcript's own finding
    assert b["chosen_attribute"] == "age"
    assert b["training_errors"] == min(b["error_table"].values())
    assert b["accuracy"] == 1.0 and b["precision_yes"] == 1.0 and b["recall_yes"] == 1.0
    assert b["zero_r_accuracy"] < b["accuracy"]           # 1R beats the 0R baseline

    c = r["13"]     # AdaBoost weights
    assert c["initial_weight"] == pytest.approx(1 / 3)
    assert c["epsilon"] == pytest.approx(1 / 3)
    assert max(c["weights"]) == pytest.approx(0.5)

    d = r["15_16"]
    assert len(d["hyperparameter_optimisation"]) >= 3
    assert len(d["linear_regression_coefficients"]) == 2

    assert r["tf"]["Boosting is easily parallelisable"] is False
    assert r["tf"]["Random forests use bootstrapping"] is True


# ------------------------------------------------------- E20c, 09.09.2020
def test_2020_09_09(papers):
    r = papers["2020-09-09"].solve()

    a = r["18_19"]
    assert a["output_size"] == 3                          # floor((7-3)/2) + 1
    assert np.array(a["conv"]).shape == (3, 3)
    assert np.array(a["max_pool"]).shape == (3, 3)
    assert a["output_size_stride_1"] == 5
    assert a["output_size_same_padding"] == 7
    assert a["conv"][0][0] == pytest.approx(a["top_left_conv_by_hand"])
    assert a["max_pool"][0][0] == pytest.approx(a["top_left_pool_by_hand"])

    b = r["20"]
    assert 0.0 <= b["recall_yes"] <= 1.0
    assert all(v > 0 for row in b["likelihoods"] for v in row.values())   # Laplace works
    assert b["zero_likelihoods_without_laplace"] > 0                     # and is needed

    assert r["knn"]["monotone_in_k"]
    assert r["tf"]["Convolution and max pooling are important for recurrent networks"] is False
    assert r["tf"]["Kernels can only be used with SVMs"] is False


# ------------------------------------------------------- E22b, 30.06.2022
def test_2022_06_30(papers):
    r = papers["2022-06-30"].solve()

    a = r["1"]
    assert [row["t"] for row in a["trace"]] == [1, 2, 3, 4, 5]
    assert a["trace"][0]["verdict"] == "tie"              # all arms tie at Q = 0
    assert a["definitely_random"] == [2, 4, 5]
    assert sorted(a["definitely_random"] + a["possibly_random"]) == [1, 2, 3, 4, 5]

    b = r["2"]
    # at w = 0 the residual is the target itself
    assert b["residual_at_w0"] == [12.0, 9.0, 11.0, 15.0, 7.0]
    # the two loss conventions differ by exactly 2m = 10
    assert b["ratio"] == pytest.approx(10.0)
    assert b["w1_rss"] == pytest.approx(10 * b["w1_mean"])
    # the intercept update is 2*alpha*sum(y) under the RSS convention
    assert b["w_after_one_step_rss"][0] == pytest.approx(2 * 0.5 * sum(b["residual_at_w0"]))

    assert r["2b"]["diverges"]                            # alpha = 0.5 on unscaled features


# ------------------------------------------------------- E26a, 27.01.2026
def test_2026_01_27(papers):
    r = papers["2026-01-27"].solve()

    a = r["s2q1"]
    assert a["predictions"] == [7.0, 7.0, 4.0, 10.0]
    assert a["mae"] == pytest.approx(1.5)
    assert a["mse"] == pytest.approx(2.5)                 # the distractor
    assert a["mae"] != a["mse"]

    b = r["s2q2"]
    assert b["trace"][0]["verdict"] == "tie"
    assert b["definitely_random"] == [2, 3, 6]
    for row in b["trace"]:
        # the verdict is consistent with the greedy set recorded for that step
        assert (row["verdict"] == "definite") == (row["action"] not in row["greedy"])

    c = r["s2q3"]
    assert c["chosen"] == "outlook"
    assert c["error_table"]["outlook"] == 0
    assert c["training_accuracy"] == 1.0
    assert min(c["error_table"].values()) == c["error_table"][c["chosen"]]

    d = r["s2q4"]
    assert d["prediction_without_laplace"] == "+"
    assert min(d["likelihoods_without_laplace"].values()) == 0.0    # zero-frequency problem
    assert all(v > 0 for v in d["likelihoods_with_laplace"].values())
    assert sum(d["priors"].values()) == pytest.approx(1.0)

    s3 = r["s3"]
    cnn = s3["Which of these are well-known CNN architectures?"]
    assert [k for k, v in cnn.items() if v] == ["LeNet", "ResNet"]
    conv_q = s3["An output of a convolutional layer is larger when ..."]
    assert [k for k, v in conv_q.items() if v] == ["padding increases", "stride decreases"]
    voting = s3["Which classification methods use majority voting?"]
    assert [k for k, v in voting.items() if v] == ["k-NN", "random forests"]

    # and the padding/stride claim is verified, not recalled
    chk = r["s3_check"]
    assert chk["more_padding"] > chk["base"] > chk["less_padding"]
    assert chk["smaller_stride"] > chk["base"] > chk["larger_stride"]

    assert r["s1"]["The first model in gradient boosting is a zero rule model"] is True
    assert r["s1"]["Gradient boosting for classification always starts with the one-rule model"] is False
