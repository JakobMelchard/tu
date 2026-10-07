# 14 Reinforcement learning: bandits, MDPs and tabular Monte Carlo

> Lecture unit 11 [S18]. Exam weight ●●● — added in the 2026-09-22 source pass; a bandit calculation is in the calculation section of every paper since 2022 [S11]. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## What it is

Lecture unit 11 [S18]. The third learning paradigm beside supervised and
unsupervised: an **agent** interacts with an **environment**, observes a
**state**, takes an **action**, receives a **reward**, and learns a **policy**
that maximises long-run reward. No labelled examples — only a scalar reward
signal, possibly delayed [S21 ch. 1].

The course teaches the first half of Sutton & Barto [S21] — the book Musliu
lectures from [S10, S17] — and stops at **tabular** methods: small enough
state–action spaces that $Q$ can be stored as a table. No function
approximation, no deep RL.

**This is not optional material.** A $k$-armed bandit calculation has appeared
in the calculation section of *every* paper since 2022 (E22b, E24a, E25b, E26a),
and RL true/false items appear alongside it [S11, S12].

## The $k$-armed bandit

One state, $k$ actions, each with an unknown stationary reward distribution.
The **value** of action $a$ is $q_*(a) \doteq \mathbb E[R_t \mid A_t = a]$; the
estimate after $t-1$ steps is the **sample average**
$$Q_t(a) = \frac{\sum_{i<t} R_i\,\mathbb 1[A_i = a]}{\sum_{i<t}\mathbb 1[A_i = a]} .$$

Computed **incrementally**, so nothing but $Q$ and $N$ is stored [S21 §2.4]:
$$Q_{n+1} = Q_n + \frac{1}{n}\big[R_n - Q_n\big],\qquad\text{i.e.}\qquad
\text{new} \leftarrow \text{old} + \text{step}\cdot[\text{target} - \text{old}].$$

That update form — *old estimate + step size × error* — is the shape of every
algorithm in this chapter.

**Non-stationary rewards**: replace $1/n$ by a constant $\alpha \in (0,1]$
[S21 §2.5]:
$$Q_{n+1} = Q_n + \alpha[R_n - Q_n] = (1-\alpha)^n Q_1 + \sum_{i=1}^n \alpha(1-\alpha)^{n-i}R_i,$$
an exponentially weighted average that never stops tracking. (Weights sum to 1;
this is why it is a *weighted average* and not just a decay.)

### Exploration vs exploitation

Acting greedily, $A_t = \arg\max_a Q_t(a)$, **exploits**; anything else
**explores**. The three schemes the course names [S21 §2.3, §2.6, §2.7]:

| scheme | rule | note |
|---|---|---|
| **$\varepsilon$-greedy** | with probability $1-\varepsilon$ take $\arg\max_a Q_t(a)$, otherwise a uniformly random action | the one the exam uses; in the limit every action is sampled infinitely often, so $Q \to q_*$ |
| **optimistic initial values** | set $Q_1(a)$ far above any plausible reward | every action disappoints, so early steps explore by themselves; works only for stationary problems |
| **upper confidence bound** | $A_t = \arg\max_a\big[Q_t(a) + c\sqrt{\ln t / N_t(a)}\big]$ | prefers actions that are either good or under-tried; $c$ sets the exploration strength |

### The exam's bandit question

"Given the actions taken and the rewards received over 8 time steps, in which
steps **was** a random (exploratory) action definitely taken, and in which
**could** it have been?" (E22b, E25b, E26a) [S11].

The procedure: start $Q(a) = 0$, $N(a) = 0$ for all $a$; at each step, *before*
applying the reward, compute $\arg\max_a Q_t(a)$, then

- the chosen action is **not** a (co-)maximiser → it was **definitely random**;
- the chosen action **is** the unique maximiser → **possibly random** (greedy and
  exploratory choices coincide, so you cannot tell);
- several actions tie for the maximum → **possibly random**, whichever was
  taken, since $\varepsilon$-greedy breaks ties arbitrarily.

Then update $N(A) \mathrel{+}= 1$ and $Q(A) \mathrel{+}= \frac{1}{N(A)}[R - Q(A)]$.
Note that all-zero initial estimates make step 1 a tie among all $k$ actions:
step 1 is never "definitely random".

## Markov decision processes

Beyond one state: the reward depends on the state too [S21 ch. 3]. The dynamics
are one function,
$$p(s', r \mid s, a) \doteq \Pr[S_t = s', R_t = r \mid S_{t-1} = s, A_{t-1} = a],
\qquad \sum_{s'}\sum_r p(s',r\mid s,a) = 1 .$$
The **Markov property** is exactly this: the next state and reward depend on the
present state and action only, not on the history.

- **Return** with discount $\gamma \in [0,1]$:
  $G_t \doteq \sum_{k\ge0}\gamma^k R_{t+k+1}$. $\gamma < 1$ keeps $G_t$ finite in
  continuing tasks and expresses a preference for sooner rewards.
- **Policy** $\pi(a\mid s)$ = probability of taking $a$ in $s$.
- **State-value** $v_\pi(s) \doteq \mathbb E_\pi[G_t \mid S_t = s]$ and
  **action-value** $q_\pi(s,a) \doteq \mathbb E_\pi[G_t\mid S_t=s, A_t=a]$.
- **Bellman equation** for $v_\pi$ — the recursion that makes everything
  computable [S21 §3.5]:
  $$v_\pi(s) = \sum_a \pi(a\mid s)\sum_{s',r} p(s',r\mid s,a)\big[r + \gamma\,v_\pi(s')\big].$$
- **Optimality**: $v_*(s) = \max_\pi v_\pi(s)$,
  $q_*(s,a) = \mathbb E[R_{t+1} + \gamma\,v_*(S_{t+1})\mid S_t=s, A_t=a]$; a
  greedy policy with respect to $v_*$ is optimal.

Dynamic programming (policy iteration, value iteration) solves this when $p$ is
known. Monte Carlo and temporal-difference methods learn it when $p$ is **not**
known — which is the realistic case and what the course covers.

## Monte Carlo methods

Learn from **complete episodes** of experience; no model of the environment is
needed [S21 ch. 5].

**First-visit MC prediction** estimates $v_\pi$: generate an episode under
$\pi$; walk it backwards accumulating $G \leftarrow \gamma G + R_{t+1}$; the
*first* time a state is visited in the episode, append $G$ to that state's
return list and set $V(s)$ to the average of the list. Converges to $v_\pi$ as
the number of visits grows (law of large numbers).

**MC control with exploring starts** improves the policy: keep
$Q(s,a)$ as the average return after $(s,a)$, and after each episode set
$\pi(s) \leftarrow \arg\max_a Q(s,a)$. Policy and value improve each other
(generalised policy iteration). "Exploring starts" means every $(s,a)$ pair has
a non-zero chance of beginning an episode — the alternative is an
$\varepsilon$-soft policy.

**The examined property**: because the target is the *return of a whole
episode*, **value estimates and the policy change only when an episode
completes** — asked verbatim in E22a, answer **true** [S12]. That is exactly
what distinguishes MC from temporal-difference methods, which bootstrap and
update every step:
$V(S_t) \leftarrow V(S_t) + \alpha[R_{t+1} + \gamma V(S_{t+1}) - V(S_t)]$.

## Worked example

A 4-armed bandit, $\varepsilon$-greedy, sample averages, $Q_1 = 0$. The trace
(this is the shape E22b and E25b print):

| $t$ | $A_t$ | $R_t$ | $Q$ before the step | greedy set | verdict |
|---|---|---|---|---|---|
| 1 | 1 | $+1$ | $(0,0,0,0)$ | all four tie | possibly random |
| 2 | 2 | $-1$ | $(1,0,0,0)$ | $\{1\}$ | **definitely random** |
| 3 | 2 | $+3$ | $(1,-1,0,0)$ | $\{1\}$ | **definitely random** |
| 4 | 1 | $+1$ | $(1,1,0,0)$ | $\{1,2\}$ | possibly random |
| 5 | 3 | $0$ | $(1,1,0,0)$ | $\{1,2\}$ | **definitely random** |
| 6 | 1 | $-2$ | $(1,1,0,0)$ | $\{1,2\}$ | possibly random |

Updates: after $t=2$, $Q(2) = 0 + \frac11(-1-0) = -1$; after $t=3$,
$N(2) = 2$ so $Q(2) = -1 + \frac12(3 - (-1)) = 1$; after $t=4$,
$N(1) = 2$, $Q(1) = 1 + \frac12(1-1) = 1$; after $t=6$, $N(1) = 3$,
$Q(1) = 1 + \frac13(-2-1) = 0$. Three steps were definitely exploratory.
`../src/py/bandits.py` `__main__` prints this table; `../src/exercises/2022-06-30/`
works the paper's version.

**Constant $\alpha$ vs sample average.** Rewards $1, 1, 1, 10$ for one action.
Sample average: $1, 1, 1, 3.25$. With $\alpha = 0.5$ from $Q_1 = 0$:
$0.5, 0.75, 0.875, 5.44$. The constant step forgets the early evidence and
tracks the change; that is the point.

## Pitfalls

- Updating $Q$ *before* deciding whether the action was greedy. The comparison
  uses the estimates as they stood at the start of the step.
- Forgetting that all-zero initial estimates make the first step a tie.
- Calling a greedy-looking action "not random": $\varepsilon$-greedy picks the
  greedy action with probability $1 - \varepsilon + \varepsilon/k$, so it is
  *possibly* random. The paper asks for "definitely" versus "possibly" for
  precisely this reason.
- Using $1/n$ on a non-stationary problem, or a constant $\alpha$ when you want
  convergence: $\sum\alpha_n = \infty$ and $\sum\alpha_n^2 < \infty$ is the
  condition for convergence, which $1/n$ satisfies and a constant does not
  [S21 §2.7].
- Confusing $v_\pi$ (a state) with $q_\pi$ (a state–action pair).
- Claiming Monte Carlo updates every step. It does not — that is TD.
- Treating $\gamma$ as a hyperparameter of the *algorithm* when it is part of
  the *problem definition* (what the agent is asked to maximise).

## Exam-style questions

1. **Given a table of $(A_t, R_t)$ for eight steps of $\varepsilon$-greedy with
   sample averaging, in which steps was a random action definitely taken?**
   *(modelled on E22b, E25b, E26a.)* Maintain $Q$ and $N$, initialised to 0;
   before each step take $\arg\max Q$; a chosen action outside the argmax set is
   definitely exploratory, anything else is only possibly so. Then apply
   $Q(A) \mathrel{+}= \frac1{N(A)}[R - Q(A)]$.
2. **"For the Monte Carlo method in reinforcement learning, value estimates and
   policies are changed only on the completion of an episode." True or false?**
   *(E22a.)* **True** — the MC target is the realised return $G_t$ of the whole
   episode, so nothing can be updated until the episode ends. TD methods update
   every step by bootstrapping off $V(S_{t+1})$.
3. **"$k$-armed bandits choose the next action based on the expected future
   reward." True or false?** *(E23a.)* **True**: the greedy component maximises
   the current estimate $Q_t(a)$ of the expected reward; the objective is the
   expected total reward over the horizon.
4. **Explain $\varepsilon$-greedy selection and why pure greedy fails.**
   *(E22a, E23c.)* Pure greedy locks onto whichever arm looked best early and
   never revisits the others, so a genuinely better arm whose first sample was
   unlucky is never found. $\varepsilon$-greedy takes a uniformly random action
   with probability $\varepsilon$, which guarantees every action is sampled
   infinitely often and $Q \to q_*$, at the cost of $\varepsilon$ of the steps
   being spent on known-inferior actions.
5. **Write the incremental update for a sample average and say what changes for
   a non-stationary problem.** *(ours — the archive asks for the trace, not the
   formula.)* $Q_{n+1} = Q_n + \frac1n[R_n - Q_n]$; for non-stationary rewards
   use a constant $\alpha$, giving
   $Q_{n+1} = (1-\alpha)^nQ_1 + \sum_i\alpha(1-\alpha)^{n-i}R_i$ — an
   exponentially weighted average that keeps tracking.
6. **State the Bellman equation for $v_\pi$ and identify each factor.**
   *(ours — beyond what any public 184.702 paper asks, but it is the definition
   the MDP section rests on.)*
   $v_\pi(s) = \sum_a\pi(a\mid s)\sum_{s',r}p(s',r\mid s,a)[r + \gamma v_\pi(s')]$:
   probability of the action, probability of the resulting (state, reward), the
   immediate reward plus the discounted value of where you land.

## Code

Split along the chapter boundary of [S21]:

`src/py/bandits.py` — chapter 2, and the examined calculation:

- `sample_average_update`, `constant_step_update`, `greedy_set`,
  `epsilon_greedy`, `ucb_select`;
- **`bandit_random_action_analysis(actions, rewards, k)`** — the exam
  calculation: returns per step the $Q$ table before the step, the greedy set,
  and `definite` / `tie` / `greedy`; `definitely_random_steps` is the one-line
  answer;
- `Bandit` (stationary and non-stationary testbeds) and `run_bandit`, a full
  $\varepsilon$-greedy / optimistic / UCB comparison over many runs.

`src/py/rl.py` — chapters 3, 5 and 6: `GridWorld`,
`first_visit_mc_prediction`, `mc_control_es` (with exploring starts),
`td0_prediction` for the MC-vs-TD contrast.

`src/exercises/2022-06-30/` works E22b's bandit and gradient-descent questions.
