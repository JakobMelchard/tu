# 15 AutoML, metalearning and the no-free-lunch theorem

> Lecture unit 13 [S18]. Exam weight ●●● — added in the 2026-09-22 source pass; Rice's framework, landmarking and the no-free-lunch theorem are asked by name in six papers [S11]. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## What it is

Lecture unit 13 [S18]: **learning how to choose and configure learning
algorithms**. TISS names "Model Selection" in the subject line [S1]; the exam
archive shows what the course means by it, and it is not just grid search —
it is Rice's framework, landmarking, and the no-free-lunch theorem, all asked by
name and repeatedly [S11, S12].

Three questions, in order of generality:

1. Given this data set, **which algorithm** should I use? → algorithm selection,
   Rice's framework, metalearning.
2. Given this algorithm, **which hyperparameters**? → hyperparameter
   optimisation.
3. Can both be automated end to end? → **AutoML**.

## The no-free-lunch theorem

**Statement** [S31]: averaged over *all* possible target functions (or all
problem instances drawn uniformly), every learning algorithm has the same
expected off-training-set error. Superior performance on one class of problems
is exactly paid for by inferior performance on another.

**The implication the course wants** (asked in E20c, E21a, E21b, E21c) [S12]:

> There is no single algorithm that is best on every problem. Any claim that
> algorithm A beats algorithm B is a claim about a *restricted* set of problems,
> so you must say which set — and you must actually run the experiment.

It is also the reason the algorithm-selection framework below needs an
assumption before it can work at all:

- **OCWA**, open classification world assumption: models are *not* comparable
  across problems; nothing learned on one data set transfers.
- **CCWA**, closed classification world assumption: models *are* comparable,
  because we trust our experiments to reflect generalisation [S18].
  Metalearning only makes sense under CCWA.

A practical corollary the exam likes: a good portfolio of base learners should
have **different inductive biases** and represent **different model classes**,
and should be small but with good coverage [S12].

## Rice's framework

[S30], asked by name in E19b, E21b and E21c.

Four spaces and two mappings:

| space | contents |
|---|---|
| $P$ | **problem space** — all data sets; we only ever see a subset $P' \subset P$ |
| $F$ | **feature space** — the meta-features $f(x)$ extracted from a data set $x$ |
| $A$ | **algorithm space** — the candidate learners |
| $Y$ | **performance space** — the metric values $y(a(x))$ |

$$x \in P \;\xrightarrow{\;f\;}\; f(x) \in F \;\xrightarrow{\;S\;}\; a \in A
\;\xrightarrow{\;y\;}\; y(a(x)) \in Y$$

The task is to find the **selection mapping** $S(f(x))$ that maximises
$\|y(a(x))\|$. In machine-learning terms: train a *meta-model* whose inputs are
meta-features of a data set and whose output is the best algorithm (or the
predicted performance of each algorithm).

**Issues to consider when applying it** — the exact wording of E21b [S12]:

- you must assume **CCWA**;
- the **computational cost** of extracting meta-features and of running the
  selection mapping must be smaller than just trying the algorithms;
- the algorithm portfolio should be **small with good coverage**, which is hard;
- the **no-free-lunch theorem** limits how general any selection mapping can be;
- base learners should have **different biases**.

**Can it be used for hyperparameter optimisation?** The expected answer
(E19b) [S12]: not directly — it selects an *algorithm*, not a configuration —
but if you treat "which algorithm" as one more hyperparameter (the CASH problem:
combined algorithm selection and hyperparameter optimisation), the two collapse
into one search and the framework applies.

## Metalearning features

"Which features are used in metalearning? What are landmarking features?" is one
of the most-repeated questions in the archive (E18a, E21b, E21d, E22a)
[S11, S12]. The four families [S12, S32]:

| family | what it is | examples |
|---|---|---|
| **statistical / information-theoretic** | computed **directly from the data set** | number of attributes, number of classes, number of instances, ratio of examples to attributes, average class entropy, class imbalance, degree of correlation between features and target, signal-to-noise ratio, skewness, kurtosis |
| **model-based** | properties of a **hypothesis induced** on the problem — an indirect characterisation | for a decision tree: number of nodes, maximum depth, tree imbalance, nodes per feature; for kNN: the chosen $k$ and distance function; for an SVM: kernel and degree |
| **landmarking** | the **performance of simple, fast learners** on the data set [S32] | accuracy of 1R, 1-NN, naive Bayes, a decision stump, a linear discriminant |
| **learning-curve** | shape of performance vs training-set size | slope, plateau level, sample size at which it saturates |

**The trap**: "Model-based features used for metalearning are extracted directly
from the data set" — **false**; that describes the statistical family. And
"'Number of attributes of data set' is *not* a model-based feature" — **true**
[S12]. Both have been asked.

**Landmarking**, defined properly [S32]: use a *learning mechanism itself* as
the measuring instrument. Each learner performs well on a characteristic class
of tasks, so how well a cheap learner does on a data set says something about
the data set's nature — a linear discriminant landmarker scoring high says the
problem is close to linearly separable. The **landmark learner** is the
meta-model that maps landmarker scores to an algorithm choice.

## Hyperparameter optimisation

The objective is the cross-validated loss as a function of the configuration
$\boldsymbol\lambda \in \boldsymbol\Lambda = \Lambda_1\times\cdots\times\Lambda_n$:
$$f(\boldsymbol\lambda) = \frac1k\sum_{i=1}^k L\big(A_{\boldsymbol\lambda},\,
D^{(i)}_{\text{train}},\, D^{(i)}_{\text{valid}}\big).$$
It is a black box: no gradient, expensive to evaluate, mixed discrete and
continuous, and noisy. **Name three methods** (E20b, E21b, E21c) [S12]:

- **Grid search** — the Cartesian product of candidate values. Exhaustive,
  reproducible, exponential in the number of hyperparameters, and it wastes the
  budget re-testing the same value of the important hyperparameter.
- **Random search** — sample configurations from distributions. At a fixed
  budget it tries $B$ *distinct* values of every hyperparameter instead of
  $B^{1/n}$, which matters because usually only one or two hyperparameters
  matter [S37]. Can be stopped at any time.
- **Bayesian optimisation / SMBO** — fit a probabilistic surrogate (Gaussian
  process, random forest, or a tree-structured Parzen estimator) to the
  observed $(\boldsymbol\lambda, f)$ pairs and evaluate next where an
  acquisition function such as expected improvement is largest. Sample-efficient;
  this is what real AutoML systems use.
- Also named in the lecture: successive halving / Hyperband (allocate a small
  budget to many configurations, keep the best fraction, repeat), evolutionary
  search, and local search / simulated annealing [S18, S12].

**The examined true/false**: "Usually state-of-the-art AutoML systems use grid
search to find the best hyperparameters" — **false** (E21b, E21c, E23c)
[S12, S18, S37]. Note that [S12] gives two different reasons in two places
("can be outperformed by randomised search", "uses simulated annealing more");
the defensible one is [S37]'s: grid search is exhaustive and budget-inefficient,
and sequential model-based optimisation dominates it in practice.

## AutoML systems

"Describe two AutoML systems" (E21b) [S12]. The ones in the lecture's orbit:

- **Auto-WEKA** — CASH over WEKA's learners and their hyperparameters, solved
  with SMAC (sequential model-based algorithm configuration, a random-forest
  surrogate). The WEKA lineage of this course [S22] makes it the natural first
  example.
- **auto-sklearn** — CASH over scikit-learn pipelines, with two additions:
  **metalearning warm-starting** (meta-features of the new data set retrieve
  configurations that worked on similar data sets — Rice's framework in
  production) and **ensemble construction** from the models evaluated during the
  search.
- **TPOT** — genetic programming over whole scikit-learn pipelines.
- **SMAC** itself is an algorithm *configurator* rather than a full AutoML
  system, but it is the optimiser inside the other two; Kletzander, the lecturer
  added for 2026W, works in exactly this area [S9].

## Worked example

A portfolio of four learners and a new data set. Landmarkers first:

| landmarker | accuracy |
|---|---|
| 0R (majority class) | 0.62 |
| 1R (one attribute) | 0.64 |
| 1-NN | 0.91 |
| naive Bayes | 0.68 |

Reading: 1R barely beats 0R, so no single attribute carries the signal; naive
Bayes is also weak, so the class-conditional independence assumption fails; 1-NN
is strong, so the decision boundary is local and probably non-linear with
interacting features. The meta-model should propose kNN, an RBF SVM or a tree
ensemble — not a linear model, not naive Bayes. Statistical meta-features
($n = 1200$, $d = 8$, ratio 150, 2 classes, class entropy 0.96) confirm there is
enough data per dimension for a flexible model.

Then hyperparameter search at a fixed budget of 16 CV evaluations: grid search
over (`n_neighbors`, `weights`, `p`) with $4\times2\times2 = 16$ points tests
only **4** distinct values of $k$, each 4 times; random search over
$k \in \{1,\dots,60\}$ with the same budget tests up to **16** (sampling with
repeats). Since $k$ is the only hyperparameter that moves the score much, random
search resolves the optimum up to 4 times more finely at the same cost [S37].
`model_selection.py`'s `__main__` runs this on a 300-point synthetic stand-in:
grid $k \in \{1, 20, 40, 60\}$, 4 distinct $k$, best $k = 1$ at CV accuracy
0.927; random, 13 distinct $k$, best $k = 5$ at 0.937
(`test_model_selection.py` pins the distinct-$k$ counts).

## Pitfalls

- Reporting the best search score as the generalisation estimate — it is a
  maximum over noisy estimates. Nested CV (note 04) is the fix.
- Claiming NFL means "all algorithms are equally good on my data". It says they
  tie *averaged over all problems*; real problems are not uniformly drawn, which
  is exactly why some algorithms work.
- Calling the number of attributes a model-based meta-feature.
- Calling a landmarker's *hyperparameters* the landmarking features — the
  landmarking feature is the landmarker's **performance**.
- Meta-feature extraction that costs more than running the portfolio.
- Forgetting that the choice of preprocessing is part of the configuration
  space; auto-sklearn and TPOT optimise whole pipelines for this reason.
- Grid search on a linear scale for parameters that act multiplicatively
  ($C$, $\gamma$, $\lambda$, learning rate).

## Exam-style questions

1. **Explain Rice's framework for algorithm selection. Can it be used for
   hyperparameter optimisation?** *(modelled on E19b, E21b.)* Problem space $P$,
   feature space $F$, algorithm space $A$, performance space $Y$; extract
   $f(x)$ from the data set, apply a selection mapping $S(f(x)) = a$, measure
   $y(a(x))$, and learn $S$ so that $\|y\|$ is maximised. Not directly usable
   for hyperparameters — it picks an algorithm, not a configuration — but if the
   algorithm identity is treated as a hyperparameter (CASH), the two become one
   search.
2. **Which features are used in metalearning? What are landmarking features?**
   *(E18a, E21b, E21d, E22a.)* Statistical/information-theoretic (number of
   attributes and classes, example-to-attribute ratio, average class entropy,
   feature–target correlation), model-based (properties of an induced
   hypothesis: tree depth, node count, imbalance), landmarking, and
   learning-curve features. Landmarking features are the **performances of
   simple fast learners** (1R, 1-NN, naive Bayes, a stump) on the data set: each
   learner excels on a characteristic class of tasks, so its score characterises
   the task.
3. **What are the implications of the no-free-lunch theorem?** *(E20c, E21a,
   E21b, E21c.)* Averaged over all problems every algorithm performs equally, so
   no learner is universally best; performance claims are always relative to a
   problem class; comparison requires the closed-classification-world assumption
   and an empirical experiment; and a useful portfolio needs learners with
   *different* biases.
4. **"State-of-the-art AutoML systems usually use grid search." True or false,
   and why?** *(E21b, E21c, E23c.)* **False.** Grid search is exhaustive and
   scales exponentially with the number of hyperparameters, and at a fixed
   budget it resolves each hyperparameter coarsely; random search already beats
   it [S37], and production systems use sequential model-based Bayesian
   optimisation (SMAC in Auto-WEKA and auto-sklearn, TPE in others).
5. **Describe at least three methods for hyperparameter optimisation.**
   *(E20b, E21b, E21c.)* Grid search, random search, Bayesian optimisation
   (SMBO); optionally successive halving/Hyperband and evolutionary search — with
   the trade-off of each.
6. **Describe two AutoML systems.** *(E21b.)* Auto-WEKA (CASH over WEKA
   learners, optimised by SMAC) and auto-sklearn (CASH over scikit-learn
   pipelines, warm-started by metalearning over meta-features of known data sets
   and finishing with an ensemble of the evaluated models).
7. **Why does metalearning need the closed-classification-world assumption?**
   *(ours — [S12] states the assumption, no paper asks why.)* The meta-model
   generalises from performance measured on past data sets to a new one. That is
   only a valid induction if the measurements are comparable across problems —
   CCWA. Under OCWA nothing transfers and NFL bites in full.

## Code

`src/py/model_selection.py`: `grid_search`, `random_search`, `nested_cv`,
`learning_curve`, `validation_curve`, `param_grid`. The metalearning material is
conceptual; the closest runnable thing is `src/py/rules.py`'s `ZeroR`/`OneR`,
which are two of the standard landmarkers, and `src/py/exercise_template.py`,
which compares eight learners with one CV protocol — a hand-rolled selection
mapping over a small portfolio.
