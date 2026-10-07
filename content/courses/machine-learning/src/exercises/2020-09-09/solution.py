"""Worked solution: exam of 09.09.2020 (label E20c, 2019W/2020S re-take).

Source of the questions: [S11] VoWi `Exam 2020-09-09`.  Described in our own
words in README.md; the paper is not reproduced.  This is the paper that
introduced the convolution and max-pooling calculations that have been in every
paper since.

Questions answered (numbers asserted in `check()`):
  Ex. 18/19  7x7 input, 3x3 window, stride 2: output 3x3 since
             floor((7 - 3)/2) + 1 = 3.  Convolution with the vertical-edge
             filter gives [[1,-7,7],[-2,-5,9],[0,-2,2]]; max pooling gives
             [[5,9,9],[7,9,9],[3,4,6]].  Cross-checked against
             scipy.signal.correlate2d and a direct loop over the windows.
  Ex. 20     naive Bayes with the course's Laplace variant [S14]: predictions
             no, yes, no, yes; recall(yes) = 2/3, precision(yes) = 1,
             F1 = 0.8; without smoothing 3 class likelihoods are zero.
  kNN        training error grows with k (0, 0.13, 0.155 for k = 1, 5, 25),
             which is how the three boundary pictures are ordered.
  T/F        eleven recalled items, answered as [S12] marks them.

Run:  ../../../../../.venv/bin/python solution.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py")))

from bayes import CategoricalNB                         # noqa: E402
from conv import conv2d, max_pool2d, output_size        # noqa: E402
from knn import KNNClassifier                           # noqa: E402
from metrics import precision_recall_f1                 # noqa: E402


# --- Exercises 18 and 19: max pooling and convolution, 7x7 input, 3x3, stride 2 -
INPUT_7x7 = np.array([
    [1, 2, 0, 3, 1, 0, 2],
    [0, 5, 2, 1, 0, 8, 1],
    [3, 0, 1, 2, 9, 1, 0],
    [1, 2, 7, 0, 1, 2, 3],
    [2, 1, 0, 4, 3, 0, 1],
    [0, 3, 2, 1, 0, 6, 2],
    [1, 0, 1, 3, 2, 1, 0],
], dtype=float)

FILTER_3x3 = np.array([
    [1.0, 0.0, -1.0],
    [1.0, 0.0, -1.0],
    [1.0, 0.0, -1.0],
])


def exercises_18_19_conv_and_pool():
    """Both questions are answered by O = floor((I - K + 2P)/S) + 1 = 3.

    The exam gives six candidate 3x3 arrays and asks which is the right output,
    so the marks are for getting the arithmetic right, not for the concept.
    """
    o = output_size(7, 3, stride=2)
    conv = conv2d(INPUT_7x7, FILTER_3x3, stride=2)
    pooled = max_pool2d(INPUT_7x7, size=3, stride=2)
    return dict(
        output_size=o,
        conv=conv.tolist(),
        max_pool=pooled.tolist(),
        # the same input with stride 1 and with 'same' padding, for contrast
        output_size_stride_1=output_size(7, 3, stride=1),
        output_size_same_padding=output_size(7, 3, stride=1, padding=1),
        top_left_conv_by_hand=float(np.sum(INPUT_7x7[:3, :3] * FILTER_3x3)),
        top_left_pool_by_hand=float(np.max(INPUT_7x7[:3, :3])),
    )


# --- Exercise 20: naive Bayes recall, **with** Laplace correction ---------------
TRAIN = np.array([
    ["sunny",    "hot",  "high",   "weak"],
    ["sunny",    "hot",  "high",   "strong"],
    ["overcast", "hot",  "high",   "weak"],
    ["rain",     "mild", "high",   "weak"],
    ["rain",     "cool", "normal", "weak"],
    ["rain",     "cool", "normal", "strong"],
    ["overcast", "cool", "normal", "strong"],
    ["sunny",    "mild", "high",   "weak"],
], dtype=object)
PLAY = np.array(["no", "no", "yes", "yes", "yes", "no", "yes", "no"])

TEST = np.array([
    ["sunny",    "cool", "normal", "weak"],
    ["rain",     "mild", "normal", "weak"],
    ["sunny",    "mild", "high",   "strong"],
    ["overcast", "mild", "high",   "strong"],
], dtype=object)
PLAY_TEST = np.array(["yes", "yes", "no", "yes"])


def exercise_20_naive_bayes_recall():
    """Classify the test rows with naive Bayes *with* Laplace correction and
    report the recall, using the course's convention (+1 top and bottom) [S14]."""
    nb = CategoricalNB(course_laplace=True).fit(TRAIN, PLAY)
    pred = nb.predict(TEST)
    p, r, f = precision_recall_f1(PLAY_TEST, pred, average="binary", pos_label="yes")

    # without smoothing, an unseen (value, class) pair zeroes the whole product
    raw = CategoricalNB(course_laplace=False).fit(TRAIN, PLAY)
    zeros = sum(1 for row in TEST for v in raw.likelihoods(row).values() if v == 0.0)

    return dict(
        predictions=[str(v) for v in pred],
        likelihoods=[{str(k): float(val) for k, val in nb.likelihoods(row).items()}
                     for row in TEST],
        recall_yes=r,
        precision_yes=p,
        f1_yes=f,
        zero_likelihoods_without_laplace=zeros,
    )


# --- The kNN "which order do the k values have?" question ----------------------
def exercise_knn_boundary_smoothness():
    """Three kNN boundaries on the same data; put k1, k2, k3 in order.

    The usable heuristic: a larger k gives a smoother boundary and, as a trend,
    a higher training error.  Only the k = 1 end is exact (training error 0 when
    no two identical points disagree, since each point is its own neighbour);
    between two larger k the training error can dip, so rank the pictures by
    smoothness, not by a theorem.  On this data it happens to rise monotonically.
    """
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 2))
    y = (X[:, 0] + 0.5 * rng.normal(size=200) > 0).astype(int)
    errors = {}
    for k in (1, 5, 25):
        pred = KNNClassifier(k=k).fit(X, y).predict(X)
        errors[k] = float(np.mean(pred != y))
    return dict(training_error_by_k=errors,
                monotone_in_k=errors[1] <= errors[5] <= errors[25])


# --- The twelve true/false items the transcript recalls ------------------------
def true_false_block():
    """Answers as the course marks them [S12]."""
    return {
        "Softmax as an activation scales the output to 0..1": True,
        "Kernels can only be used with SVMs": False,
        "Boosting is easy to parallelise": False,
        "A good ML model has low bias and low variance": True,
        "Freezing layers means their weights are only updated during fine-tuning": False,
        "Leave-p-out CV is computationally expensive on large data sets": True,
        "There exists no BN where nodes become d-separated after one node is instantiated": False,
        "Lasso cannot be used for feature selection": False,
        "F1 is used with regression": False,
        "Naive Bayes uses a density function when only nominal attributes are present": False,
        "Convolution and max pooling are important for recurrent networks": False,
    }


def solve():
    return {
        "tf": true_false_block(),
        "knn": exercise_knn_boundary_smoothness(),
        "18_19": exercises_18_19_conv_and_pool(),
        "20": exercise_20_naive_bayes_recall(),
    }


def check(r):
    """Assert the numeric answers listed in the module docstring."""
    a = r["18_19"]
    conv = [[1, -7, 7], [-2, -5, 9], [0, -2, 2]]
    pool = [[5, 9, 9], [7, 9, 9], [3, 4, 6]]
    assert a["output_size"] == 3 and a["output_size_stride_1"] == 5 and a["output_size_same_padding"] == 7
    assert np.array_equal(a["conv"], conv) and np.array_equal(a["max_pool"], pool)
    # independent checks: scipy's cross-correlation subsampled at stride 2, and a plain loop
    from scipy.signal import correlate2d
    assert np.array_equal(correlate2d(INPUT_7x7, FILTER_3x3, mode="valid")[::2, ::2], conv)
    windows = [[INPUT_7x7[2 * i:2 * i + 3, 2 * j:2 * j + 3] for j in range(3)] for i in range(3)]
    assert np.array_equal([[w.max() for w in row] for row in windows], pool)

    b = r["20"]
    assert b["predictions"] == ["no", "yes", "no", "yes"]
    assert np.isclose(b["recall_yes"], 2 / 3) and b["precision_yes"] == 1.0 and np.isclose(b["f1_yes"], 0.8)
    assert np.isclose(b["likelihoods"][0]["yes"], 0.5 * 0.2 * 0.6 * 0.6 * 0.8)   # sunny|yes = (0+1)/(4+1)
    assert b["zero_likelihoods_without_laplace"] == 3

    k = r["knn"]["training_error_by_k"]
    assert (k[1], k[5], k[25]) == (0.0, 0.13, 0.155)


if __name__ == "__main__":
    import json
    r = solve()
    for key, value in r.items():
        print(f"--- exercise {key} ---")
        print(json.dumps(value, indent=2, default=float))
    check(r)
    print("\ncheck(): all asserted answers hold")
