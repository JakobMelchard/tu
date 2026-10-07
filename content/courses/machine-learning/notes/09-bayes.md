# 09 Naive Bayes and Bayesian networks

> Lecture units 6 and 7 [S18]. Exam weight ●●● — [S10]: “there’s always one [naive Bayes calculation] in each exam”. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## Bayes classifiers

Bayes' rule for classification: $p(c \mid x) = \frac{p(x \mid c)\,p(c)}{p(x)}$, decision $\hat c = \operatorname{argmax}_c p(x \mid c)p(c)$ (the denominator is constant in $c$). The **Bayes optimal classifier** uses the true $p(x \mid c)$; its error is the irreducible lower bound. A generative model estimates $p(x \mid c)$ and $p(c)$ from data.

## Naive Bayes

Assume features conditionally independent given the class: $p(x \mid c) = \prod_j p(x_j \mid c)$. Then
$$\hat c = \operatorname{argmax}_c \Big[\log p(c) + \sum_j \log p(x_j \mid c)\Big]$$
(work in logs to avoid underflow). Parameters per class and feature instead of a joint over all features: $O(Kd)$ instead of $O(K\cdot|\mathcal X|^d)$.

- **Gaussian NB** (continuous): $p(x_j \mid c) = \mathcal N(x_j; \mu_{cj}, \sigma_{cj}^2)$, MLE = class-wise mean and variance; add `var_smoothing` $\epsilon$ to the variances. With shared variances the boundary is linear; with class-specific variances quadratic.
- **Multinomial NB** (counts, text): $p(x \mid c) \propto \prod_j \theta_{cj}^{x_j}$, $\hat\theta_{cj} = \frac{N_{cj} + \alpha}{N_c + \alpha d}$ with **Laplace / additive smoothing** $\alpha$ (a word never seen in class $c$ would otherwise give $p = 0$ and veto the class). $\alpha = 1$ Laplace, $\alpha < 1$ Lidstone.
- **Bernoulli NB** (binary presence): $p(x \mid c) = \prod_j \theta_{cj}^{x_j}(1 - \theta_{cj})^{1 - x_j}$; absence is informative, unlike multinomial.
- **Categorical NB**: a table per feature and class.

Properties: trains in one pass, works with tiny data and huge $d$, robust to irrelevant features, but its probabilities are over-confident (dependent features are counted several times) and it cannot model feature interactions (XOR). Despite the wrong independence assumption the *argmax* is often right (Domingos & Pazzani 1997). Zero-frequency problem → smoothing. Continuous features may need discretisation or a better density. It is an **eager** learner, not a lazy one — it estimates the probability tables at training time, and the exam asks this (E21d, answer **false** to "naive Bayes is a lazy learner") [S12].

### The course's convention for a hand calculation — use this in the exam

[S14] works a complete example and its arithmetic differs from
scikit-learn's in two ways. Follow it, because the graded answer depends on it.

1. **Likelihood, then normalise.** For each class $C$ compute
   $\text{Likelihood}(C \mid E) = P(C)\prod_j P(F_j = v_j \mid C)$ with
   $P(C)$ = the class's share of the training rows, then
   $P(C\mid E) = \text{Likelihood}(C\mid E)\,/\,\sum_{C'}\text{Likelihood}(C'\mid E)$.
   Predict the largest.
2. **Laplace correction adds 1 to the numerator *and 1* to the denominator**:
   $$P(F_j = v \mid C) = \frac{\#\{F_j = v,\ C\} + 1}{\#\{C\} + 1},$$
   not the textbook $\frac{N_{cj} + \alpha}{N_c + \alpha\,|\text{values}(F_j)|}$.
   The **class prior is not smoothed** [S14]. The course's variant is not a
   proper Dirichlet posterior — the smoothed probabilities of one attribute no
   longer sum to 1 — but it is what the marking scheme uses.

   **[S14]'s own worked number is wrong, and the fix matters.** On its four-row
   table with the new sample `(False, Medium, True)` the sheet prints
   $\tfrac{2+1}{2+1}\cdot\tfrac{0+1}{2+1}\cdot\tfrac{0+1}{2+1}\cdot\tfrac24 = 0.05555$
   for class A — but the first factor is $P(F_1 = \text{True}\mid A)$, taken
   from the generic formula line above it, whereas the sample has
   $F_1 = \text{False}$, for which the factor is $\tfrac{0+1}{2+1} = \tfrac13$.
   The correct likelihood is $\tfrac13\cdot\tfrac13\cdot\tfrac13\cdot\tfrac24 = 0.01852$
   against $0.148$ for class B, so the prediction is **B** with
   $P(B\mid E) = 0.889$. `../src/py/bayes.py` (`CategoricalNB(course_laplace=True)`)
   reproduces both numbers and `test_bayes.py` pins them: $0.05555$ is the
   likelihood of `(True, Medium, True)`.
3. **Whether to smooth at all is stated in the question.** "The Laplace
   corrector must be used when using naive Bayes" is **false**: it *can* be
   used, and is needed when the zero-frequency problem arises (E21b) [S12].
   E26a says explicitly "without Laplace correction"; E20c asks for recall
   *with* it.
4. **Numeric attributes**: mean and standard deviation **per class**, then
   $f(x) = \frac{1}{\sqrt{2\pi}\sigma}e^{-(x-\mu)^2/2\sigma^2}$ in place of the
   frequency [S14]. Hence the true/false item "if naive Bayes is applied on a
   data set that contains also numeric attributes then a probability density
   function must always be used" — **true**; and its inverse "a density function
   is used when only nominal attributes are present" — **false** [S12].
5. **Missing values**: during training the row is left out of the frequency
   count for that attribute–class pair (and out of the mean and standard
   deviation for numeric attributes); at classification time the attribute is
   simply omitted from the product [S12]. That is the answer to "explain how to
   deal with missing values and the zero-frequency problem in NB" (E21b, E21d).

## Bayesian networks

A DAG over random variables $X_1, \dots, X_n$ plus a **conditional probability table (CPT)** $P(X_i \mid \text{Pa}(X_i))$ per node, encoding
$$P(X_1, \dots, X_n) = \prod_i P(X_i \mid \text{Pa}(X_i)).$$
Local Markov property: each node is independent of its non-descendants given its parents. Parameter count: a node with $k$ values and parents with $k_1, \dots, k_m$ values needs $(k - 1)\prod k_j$ numbers; the full joint needs $\prod_i k_i - 1$. Naive Bayes is the BN "class → every feature".

**Three canonical structures** (for path $X - Z - Y$):
- chain $X \to Z \to Y$: blocked iff $Z$ observed;
- fork (common cause) $X \leftarrow Z \to Y$: blocked iff $Z$ observed;
- collider (common effect) $X \to Z \leftarrow Y$: blocked iff **neither** $Z$ nor any descendant of $Z$ is observed. Observing a collider creates dependence: **explaining away** (if the alarm rang and there was an earthquake, a burglary becomes less likely).

**d-separation**: $X \perp Y \mid Z$ holds in every distribution factorising over the DAG iff every undirected path from $X$ to $Y$ is blocked by $Z$ (one of the three rules above at some node of the path). Equivalent algorithmic test (`bayesnet.BayesianNetwork.d_separated`): take the ancestral subgraph of $X \cup Y \cup Z$, **moralise** (connect co-parents, drop directions), delete $Z$; $X$ and $Y$ are d-separated iff disconnected. The **Markov blanket** (parents, children, children's other parents) d-separates a node from everything else.

**Inference**: $P(Q \mid e) = \alpha \sum_{h} P(Q, e, h)$ over the hidden variables $h$. **Enumeration** expands the product in topological order and sums out hidden variables; exponential in the number of hidden variables but exact. **Variable elimination** caches factors (sum-product); polynomial on trees / polytrees, exponential in the treewidth in general (exact inference is #P-hard). Approximate: rejection sampling, likelihood weighting, Gibbs sampling / MCMC.

**Parameter learning** (complete data, known structure): MLE $\hat P(x \mid \text{pa}) = \frac{N(x, \text{pa})}{N(\text{pa})}$, smoothed $\frac{N(x, \text{pa}) + \alpha}{N(\text{pa}) + \alpha k}$ (Dirichlet prior). Incomplete data: EM. Structure learning: score-based (BIC, BDeu with greedy hill-climbing) or constraint-based (PC algorithm from conditional-independence tests).

### Building a network — the course's own recipe

"Describe a local-search algorithm for Bayesian network creation" is asked in
**five** papers (E20c, E21c, E21d, E22a, and as "how can you learn the structure
of a BN?" in E21b) [S11]. The expected answer [S14, S12]:

- **Who builds it.** Human experts, learning from data, or both — and the
  division of labour the course states is that **experts are better at the
  structure, computers at the probabilities** [S12].
- **Case A, structure known** → estimate each conditional probability by
  counting, $P(J\mid A) = \frac{\#\{A = \text{true} \wedge J = \text{true}\}}{\#\{A = \text{true}\}}$,
  with Laplace correction [S14].
- **Case B, structure unknown** → *"find a network that is a good fit to the
  data and has low complexity"*, i.e. maximise
  $$\log P(D \mid M) - \alpha\,\#M,$$
  where $\#M$ is the number of parameters and $\alpha$ says how much complexity
  reduction matters [S14]. Brute force over DAGs is super-exponential, so use a
  heuristic **local search**:
  1. construct an initial network;
  2. score the current network (with its probabilities learned);
  3. generate the **neighbourhood** by small changes — **add an arc, remove an
     arc, reverse an arc**;
  4. take the best neighbour as the new current network;
  5. repeat until a stopping criterion.
  Hill climbing, simulated annealing and tabu search are the named variants
  [S12].

Two traps follow from this: **"d-separation is used in neighbourhood search when
building a BN"** is **false** — the neighbourhood operators are add/remove/
reverse-arc, not d-separation (E19b) — and **"Bayesian optimisation is used for
constructing Bayesian networks"** is **false** too: Bayesian *optimisation* is a
hyperparameter-search method (note 15), unrelated despite the name (E19b) [S12].
Finally, **"learning the structure is simpler than learning the probabilities"**
is **false**: the structure is a combinatorial search, the probabilities are
counting (E20c, E21a, E21b) [S12].

## Hidden Markov models *(historical — E17a and E17b only)*

An HMM is a Markov chain over **hidden** states $S$ with parameters
$\lambda = (A, B, \pi)$: transition matrix $A_{ij} = P(S_{t+1} = j \mid S_t = i)$,
emission matrix $B_{jk} = P(O_t = k \mid S_t = j)$, and initial distribution
$\pi$. Only the observations $O$ are seen. Rabiner's **three problems** [S38],
which is what the exam asked for [S43]:

1. **Evaluation** — what is $P(O \mid \lambda)$? Solved by the forward
   algorithm, $O(N^2T)$.
2. **Decoding** — which hidden state sequence most likely produced $O$? Solved
   by Viterbi.
3. **Learning** — how do we adjust $A$, $B$, $\pi$ to maximise
   $P(O\mid\lambda)$? Solved by Baum–Welch (an EM algorithm).

*(Scope note: no paper after 2017 mentions HMMs [S11], and neither the formula
sheet [S13] nor the how-tos [S14] cover them. Kept because they are cheap to
learn and the 2017 papers are still on VoWi. No implementation in `src/`.)*

## Worked example

Alarm network (AIMA [S25]): $P(B) = 0.001$, $P(E) = 0.002$, $P(A \mid B, E)$: $0.95, 0.94, 0.29, 0.001$ for $(b,e), (b,\neg e), (\neg b, e), (\neg b, \neg e)$; $P(J \mid A) = 0.9$, $P(J \mid \neg A) = 0.05$; $P(M \mid A) = 0.7$, $P(M \mid \neg A) = 0.01$.

Joint of one full assignment: $P(j, m, a, \neg b, \neg e) = 0.9 \cdot 0.7 \cdot 0.001 \cdot 0.999 \cdot 0.998 = 0.000628$.

Query $P(B \mid j, m) = \alpha\, P(B) \sum_e P(e) \sum_a P(a \mid B, e) P(j \mid a) P(m \mid a)$:
$P(b, j, m) = 0.001 \cdot [0.002(0.95 \cdot 0.63 + 0.05 \cdot 0.0005) + 0.998(0.94 \cdot 0.63 + 0.06 \cdot 0.0005)] = 0.001 \cdot 0.5923 = 0.000592$;
$P(\neg b, j, m) = 0.999 \cdot [0.002(0.29 \cdot 0.63 + 0.71 \cdot 0.0005) + 0.998(0.001 \cdot 0.63 + 0.999 \cdot 0.0005)] = 0.999 \cdot 0.001493 = 0.001492$;
normalise: $P(b \mid j, m) = 0.000592 / 0.002084 = 0.284$. (`bayesnet.py` `__main__` prints 0.2842.)

Independences: $B \perp E$ (collider $A$ unobserved), $B \not\perp E \mid A$, $B \not\perp E \mid J$ (descendant of the collider), $J \perp M \mid A$ (fork), $B \perp J \mid A$ (chain).

Naive Bayes, text: classes spam/ham with priors 0.4/0.6, vocabulary {free, meeting, now}; smoothed counts give $\theta_{\text{spam}} = (0.5, 0.1, 0.4)$, $\theta_{\text{ham}} = (0.1, 0.6, 0.3)$. Message "free now now": spam $\propto 0.4 \cdot 0.5 \cdot 0.4^2 = 0.032$, ham $\propto 0.6 \cdot 0.1 \cdot 0.3^2 = 0.0054$ → spam with posterior $0.032 / 0.0374 = 0.86$.

## Pitfalls

- No smoothing: a single unseen feature value zeroes a class.
- Trusting NB probabilities (use them for ranking, not as calibrated risk).
- Gaussian NB on skewed or bounded features: transform first.
- Confusing "$X$ and $Y$ independent" with "d-separated given nothing" when there is a collider on the path: observing the collider's descendant re-opens the path.
- A BN encodes independences, not causality, unless built with causal semantics; arrows can be reversed in equivalent DAGs (same v-structures).
- Enumeration re-computes shared sub-sums; do not claim it is polynomial.

## Exam-style questions

1. **Write the naive Bayes decision rule for a document with word counts $x$ and explain the role of $\alpha$.** $\hat c = \operatorname{argmax}_c[\log p(c) + \sum_j x_j \log\theta_{cj}]$ with $\theta_{cj} = (N_{cj} + \alpha)/(N_c + \alpha d)$; $\alpha$ prevents zero probabilities for unseen words and acts as a Dirichlet prior (pseudo-counts).
2. **State the factorisation of a BN and count parameters for the alarm network vs the full joint.** $P = P(B)P(E)P(A \mid B,E)P(J \mid A)P(M \mid A)$: $1 + 1 + 4 + 2 + 2 = 10$ parameters; the full joint of five binary variables needs $2^5 - 1 = 31$.
3. **Define d-separation and decide $X \perp Y \mid Z$ for $X \to W \leftarrow Y$, $W \to Z$.** Every path from $X$ to $Y$ must be blocked. The only path $X \to W \leftarrow Y$ has a collider $W$; given $\emptyset$ it is blocked ($X \perp Y$); given $Z$ (a descendant of $W$) it is open, so $X \not\perp Y \mid Z$.
4. **Explain "explaining away" with the alarm example.** $B$ and $E$ are marginally independent, but once $A = \text{true}$ is observed, learning $E = \text{true}$ explains the alarm and lowers $P(B \mid a, e)$ below $P(B \mid a)$: two causes compete for one observed effect.
5. **Describe inference by enumeration for $P(B \mid j, m)$ and its complexity; name a better exact method.** *(modelled on E17a.)* Expand $P(B, j, m) = \sum_e\sum_a P(B)P(e)P(a \mid B, e)P(j \mid a)P(m \mid a)$, evaluate in topological order, normalise. $O(2^{h})$ for $h$ hidden binary variables (with repeated sub-computations). Variable elimination stores intermediate factors and is polynomial on polytrees.
6. **Describe a local-search algorithm for creating a Bayesian network.** *(modelled on E20c, E21c, E21d, E22a — asked four times.)* Objective: maximise $\log P(D\mid M) - \alpha\,\#M$, a fit-minus-complexity score. Start from an initial network; score it with its probabilities learned by counting; build the neighbourhood by adding, removing or reversing a single arc; move to the best neighbour; repeat until no improvement or a budget is spent. Hill climbing, simulated annealing or tabu search; brute force is infeasible because the number of DAGs is super-exponential.
7. **Why can a general Bayesian network give better results than naive Bayes?** *(E21b.)* Naive Bayes forces every attribute to be conditionally independent of every other given the class. Real attributes are usually dependent, and naive Bayes then double-counts the shared evidence, giving over-confident and sometimes wrong posteriors. A general network encodes only the independences that actually hold, at the price of having to learn the structure.
8. **What is the chain rule and how is it used in Bayesian networks?** *(E21c.)* The chain rule of probability writes a joint distribution as a product of conditionals, $P(X_1,\ldots,X_n) = \prod_i P(X_i \mid X_1,\ldots,X_{i-1})$. In a BN the conditional independences let each term drop to $P(X_i \mid \text{Pa}(X_i))$, so the joint needs only the CPTs of directly connected variables — which is exactly the parameter saving in question 2. "The chain rule simplifies the calculation of probabilities in BNs" is **true** [S12].
9. **What is a hidden Markov model and what are its three problems?** *(modelled on E17a, E17b — historical.)* A Markov chain over hidden states with transition matrix $A$, emission matrix $B$ and initial distribution $\pi$, of which only the emissions are observed. The three problems: **evaluation** ($P(O\mid\lambda)$, forward algorithm), **decoding** (most likely state sequence, Viterbi), **learning** (fit $A, B, \pi$ to maximise $P(O\mid\lambda)$, Baum–Welch) [S38].

## Code

`src/py/bayes.py` — the classifiers: `GaussianNB`, `MultinomialNB(alpha)`,
`BernoulliNB`, **`CategoricalNB(course_laplace=…)`**, the course's
hand-calculation convention of [S14], whose `likelihoods()` returns the
un-normalised per-class products so the numbers can be checked against a worked
exam answer.

`src/py/bayesnet.py` — the networks: `BayesianNetwork(nodes, parents, cpt)` with
`joint`, `enumeration_ask`, `d_separated` (moralised ancestral graph),
`markov_blanket`, `fit_cpts(data, alpha)`, `sample`, `alarm_network()`; and the
structure search of the section above — **`score_structure`**
($\log P(D\mid M) - \alpha\,\#M$), **`neighbourhood`** (add / remove / reverse
one arc, acyclic only) and **`hill_climb_structure`**.

Tests (`test_bayes.py`, `test_bayesnet.py`): NB against sklearn, **[S14]'s
worked example reproduced to $0.05555$ — and shown to belong to a different
sample than the sheet states**, enumeration against the brute-force joint,
d-separation on the six textbook cases, CPT recovery from samples, and hill
climbing from the empty network landing within 1 % of the generating
structure's score.
