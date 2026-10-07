"""Worked solution: exam of 27.01.2026 (label E26a, 2025W main date).

Source of the questions: [S11] VoWi `Exam 2026-01-27`.  Described in our own
words in README.md; the paper is not reproduced.  **This is the most recent
184.702 paper and the closest model for 2026W**: 75 minutes, three question
groups, entirely single/multiple choice, in three sections
  1) 13 true/false        +2 / -1
  2) 4 calculations       +3 / -1.5
  3) multiple-correct MC  +2 only if every correct box is ticked, else 0.

All four of section 2's calculations are worked here.

Questions answered (numbers asserted in `check()`):
  S2 Q1  MAE of yhat = 3 + 2 F1 + F2 on four rows: residuals 2, -1, 1, -2,
         MAE = 1.5 (MSE = 2.5 is the distractor).
  S2 Q2  bandit trace, actions 1, 2, 3, 3, 3, 1, 3, 3: definitely random at
         t = 2, 3, 6.
  S2 Q3  1R: errors temperature 3, humidity 2, outlook 0, so 1R takes outlook.
  S2 Q4  naive Bayes without Laplace: P(+) = 4/7, factors (1, 1/4, 1/4) for +
         and (0, 1/3, 2/3) for -, likelihoods 1/28 vs 0, predict +; with the
         course's Laplace variant [S14]: 16/175 vs 9/224, still +.
  S3     the four multiple-correct lists, with the padding/stride claim
         verified from O = floor((I - K + 2P)/S) + 1 on I = 16, K = 3.

Run:  ../../../../../.venv/bin/python solution.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py")))

from bayes import CategoricalNB                                   # noqa: E402
from conv import output_size                                      # noqa: E402
from metrics import mae, mse                                      # noqa: E402
from bandits import bandit_random_action_analysis                 # noqa: E402
from rules import OneR                                            # noqa: E402


# --- Section 2, question 1: MAE of the model yhat = 3 + 2*F1 + F2 ---------------
REG_FEATURES = np.array([[1.0, 2.0], [2.0, 0.0], [0.0, 1.0], [3.0, 1.0]])
REG_TARGET = np.array([9.0, 6.0, 5.0, 8.0])


def section2_q1_mae():
    """"Calculate the MAE for the regression model 3 + 2*F1 + F2."

    Pure arithmetic; the exam offers options such as 2.5 / 2 / 1.5 / none of the
    above (E25b), so the only risk is an arithmetic slip or reporting MSE.
    """
    pred = 3 + 2 * REG_FEATURES[:, 0] + REG_FEATURES[:, 1]
    return dict(predictions=pred.tolist(),
                residuals=(REG_TARGET - pred).tolist(),
                mae=mae(REG_TARGET, pred),
                mse=mse(REG_TARGET, pred),
                note="MAE averages |residual| (1.5 here); MSE averages its square (2.5) -- "
                     "and 2.5 is exactly the kind of number that appears as a distractor")


# --- Section 2, question 2: the k-armed bandit ----------------------------------
BANDIT_ACTIONS_1BASED = [1, 2, 3, 3, 3, 1, 3, 3]
BANDIT_REWARDS = [1.0, 2.0, 5.0, 4.0, 3.0, 0.0, 6.0, 2.0]


def section2_q2_bandit():
    actions = [a - 1 for a in BANDIT_ACTIONS_1BASED]
    trace = bandit_random_action_analysis(actions, BANDIT_REWARDS, k=3)
    return dict(
        trace=[dict(t=s["t"], action=s["action"] + 1, reward=s["reward"],
                    q_before=[round(float(v), 4) for v in s["q_before"]],
                    greedy=[a + 1 for a in s["greedy"]], verdict=s["verdict"])
               for s in trace],
        definitely_random=[s["t"] for s in trace if s["verdict"] == "definite"],
    )


# --- Section 2, question 3: which feature does 1R take? -------------------------
ONER_TABLE = np.array([
    ["hot",  "high",   "sunny"],
    ["hot",  "high",   "rain"],
    ["mild", "normal", "sunny"],
    ["cool", "normal", "sunny"],
    ["cool", "high",   "rain"],
    ["mild", "high",   "rain"],
    ["hot",  "normal", "sunny"],
    ["cool", "normal", "rain"],
], dtype=object)
ONER_TARGET = np.array(["+", "-", "+", "+", "-", "-", "+", "-"])
ONER_NAMES = ["temperature", "humidity", "outlook"]


def section2_q3_one_rule():
    """"One example to decide which feature 1R takes."

    Show the per-attribute error count; the attribute with the fewest training
    errors wins.  Here `outlook` separates the classes perfectly, so 1R picks it.
    """
    model = OneR().fit(ONER_TABLE, ONER_TARGET)
    return dict(
        error_table={ONER_NAMES[r["attribute"]]: r["errors"] for r in model.rule_table_},
        accuracy_table={ONER_NAMES[r["attribute"]]: round(r["accuracy"], 4)
                        for r in model.rule_table_},
        chosen=ONER_NAMES[model.attribute_],
        rules={str(k): str(v) for k, v in model.rules_.items()},
        training_accuracy=float(np.mean(model.predict(ONER_TABLE) == ONER_TARGET)),
    )


# --- Section 2, question 4: naive Bayes without Laplace correction --------------
NB_TABLE = np.array([
    ["yes", "high",   "young"],
    ["yes", "low",    "old"],
    ["no",  "high",   "young"],
    ["no",  "low",    "young"],
    ["yes", "medium", "old"],
    ["no",  "medium", "old"],
    ["yes", "high",   "old"],
], dtype=object)
NB_TARGET = np.array(["+", "+", "-", "-", "+", "-", "+"])
NB_NEW = np.array(["yes", "medium", "young"], dtype=object)


def section2_q4_naive_bayes():
    """"Calculate naive Bayes to predict +/- for an additional row **without**
    Laplace correction."  Seven training rows, as in E25b and E26a."""
    raw = CategoricalNB(course_laplace=False).fit(NB_TABLE, NB_TARGET)
    smoothed = CategoricalNB(course_laplace=True).fit(NB_TABLE, NB_TARGET)
    factors = {str(c): [round(raw.conditional(c, j, NB_NEW[j]), 6) for j in range(3)]
               for c in raw.classes_}
    return dict(
        priors={str(c): round(raw.prior_[c], 6) for c in raw.classes_},
        conditional_factors=factors,
        likelihoods_without_laplace={str(k): float(v) for k, v in raw.likelihoods(NB_NEW).items()},
        posteriors_without_laplace={str(c): round(float(p), 6) for c, p in
                                    zip(raw.classes_, raw.predict_proba([NB_NEW])[0])},
        prediction_without_laplace=str(raw.predict([NB_NEW])[0]),
        likelihoods_with_laplace={str(k): float(v) for k, v in smoothed.likelihoods(NB_NEW).items()},
        prediction_with_laplace=str(smoothed.predict([NB_NEW])[0]),
    )


# --- Section 3: the multiple-correct lists (all-or-nothing marking) -------------
def section3_lists():
    """The four lists E26a asked for, with the answers [S11, S12, S26] support."""
    return {
        "Which of these are well-known CNN architectures?":
            {"LeNet": True, "LSTM": False, "ResNet": True,
             "Reception": False, "TeNet": False, "None of the above": False},
        "An output of a convolutional layer is larger when ...":
            {"padding decreases": False, "padding increases": True,
             "stride decreases": True, "stride increases": False},
        "What helps with vanishing gradients?":
            {"gradient clipping": True, "ReLU activations": True,
             "He/Xavier initialisation": True, "batch normalisation": True,
             "residual connections": True, "a larger learning rate": False},
        "Which classification methods use majority voting?":
            {"k-NN": True, "decision trees": False, "Bayesian networks": False,
             "random forests": True,
             "an ensemble that outputs the most confident model's prediction": False,
             "all of the above": False, "none of the above": False},
    }


def section1_true_false():
    """The section-1 item the transcript remembers, plus the neighbours it names."""
    return {
        "The first model in gradient boosting is a zero rule model": True,
        "Gradient boosting for classification always starts with the one-rule model": False,
        "Random forests are a boosting ensemble technique": False,
        "In AdaBoost the weights are uniformly initialised": True,
    }


def check_conv_claim():
    """Verify the section-3 padding/stride claim numerically rather than by memory."""
    base = output_size(16, 3, stride=2, padding=1)
    return dict(
        base=base,
        more_padding=output_size(16, 3, stride=2, padding=2),
        less_padding=output_size(16, 3, stride=2, padding=0),
        smaller_stride=output_size(16, 3, stride=1, padding=1),
        larger_stride=output_size(16, 3, stride=4, padding=1),
    )


def solve():
    return {
        "s1": section1_true_false(),
        "s2q1": section2_q1_mae(),
        "s2q2": section2_q2_bandit(),
        "s2q3": section2_q3_one_rule(),
        "s2q4": section2_q4_naive_bayes(),
        "s3": section3_lists(),
        "s3_check": check_conv_claim(),
    }


def check(r):
    """Assert the numeric answers listed in the module docstring."""
    q1 = r["s2q1"]
    assert q1["residuals"] == [2.0, -1.0, 1.0, -2.0]
    assert np.isclose(q1["mae"], 1.5) and np.isclose(q1["mse"], 2.5)

    assert r["s2q2"]["definitely_random"] == [2, 3, 6]

    q3 = r["s2q3"]
    assert q3["error_table"] == {"temperature": 3, "humidity": 2, "outlook": 0}
    assert q3["chosen"] == "outlook"

    q4 = r["s2q4"]
    assert np.isclose(q4["priors"]["+"], 4 / 7, atol=1e-6)
    assert np.allclose(q4["conditional_factors"]["+"], [1, 1 / 4, 1 / 4], atol=1e-6)
    assert np.allclose(q4["conditional_factors"]["-"], [0, 1 / 3, 2 / 3], atol=1e-6)
    assert np.isclose(q4["likelihoods_without_laplace"]["+"], 1 / 28)
    assert q4["likelihoods_without_laplace"]["-"] == 0.0
    assert np.isclose(q4["likelihoods_with_laplace"]["+"], 16 / 175)
    assert np.isclose(q4["likelihoods_with_laplace"]["-"], 9 / 224)
    assert q4["prediction_without_laplace"] == q4["prediction_with_laplace"] == "+"

    assert r["s3_check"] == dict(base=8, more_padding=9, less_padding=7,
                                 smaller_stride=16, larger_stride=4)


if __name__ == "__main__":
    import json
    r = solve()
    print("--- section 2, q1: MAE of yhat = 3 + 2*F1 + F2 ---")
    print(json.dumps(r["s2q1"], indent=2, default=float))
    print("\n--- section 2, q2: k-armed bandit ---")
    print(" t  A_t  R_t   Q before             greedy     verdict")
    for row in r["s2q2"]["trace"]:
        print("%2d  %3d  %4.0f   %-20s %-10s %s"
              % (row["t"], row["action"], row["reward"], row["q_before"],
                 row["greedy"], row["verdict"]))
    print("definitely random:", r["s2q2"]["definitely_random"])
    print("\n--- section 2, q3: which feature does 1R take? ---")
    print(json.dumps(r["s2q3"], indent=2, default=float))
    print("\n--- section 2, q4: naive Bayes without Laplace ---")
    print(json.dumps(r["s2q4"], indent=2, default=float))
    print("\n--- section 3 lists (all-or-nothing marking) ---")
    for question, options in r["s3"].items():
        print(" ", question)
        for option, correct in options.items():
            print("    [%s] %s" % ("x" if correct else " ", option))
    print("\n  output-size check:", r["s3_check"])
    check(r)
    print("\ncheck(): all asserted answers hold")
