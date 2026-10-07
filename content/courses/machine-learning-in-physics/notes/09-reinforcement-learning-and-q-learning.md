# 09 Reinforcement learning and Q-learning

TISS topic 9, "Reinforcement learning, Q learning" [S2]; videos Learning 7 and
"Temporal Distance Learning" (2022 guest lectures, Huber), Reinforcement 1-2
(2023: basics, learning paradigms and Q-learning); exercise 12 CartPole with a
Q-table [S5, S11]. Text: Sutton and Barto [S24] (recommended in the video
descriptions), Watkins and Dayan [S25]. Bandits, Monte Carlo control:
[CSE note 14](../../machine-learning/notes/14-reinforcement-learning.md).

## Definitions

- **Markov decision process (MDP):** states $\mathcal S$, actions $\mathcal A$,
  transition kernel $P(s'|s,a)$, reward $r(s,a,s')$, discount $\gamma\in[0,1)$.
  **Markov:** $P$ depends only on the current $(s,a)$, not on the history.
- **Observation vs state:** the agent sees $o=O(s)$; if $o$ does not determine the
  future distribution (e.g. CartPole without velocities) the problem is a POMDP.
- **Policy** $\pi(a|s)$; **return** $G_t=\sum_{k\ge0}\gamma^kr_{t+k+1}$.
- **Value functions:** $V^\pi(s)=\mathbb E_\pi[G_t|s_t=s]$,
  $Q^\pi(s,a)=\mathbb E_\pi[G_t|s_t=s,a_t=a]$; optimal $Q^*=\max_\pi Q^\pi$,
  greedy policy $\pi^*(s)=\arg\max_aQ^*(s,a)$.
- **$\varepsilon$-greedy:** random action with probability $\varepsilon$, else greedy.
- **On-/off-policy:** learning about the policy being run (SARSA) vs about another
  one, here the greedy policy (Q-learning).

## Derivations

**Bellman equations.** Split off the first reward: $G_t=r_{t+1}+\gamma G_{t+1}$, so

$$Q^\pi(s,a)=\sum_{s'}P(s'|s,a)\big[r+\gamma\sum_{a'}\pi(a'|s')Q^\pi(s',a')\big],$$
$$Q^*(s,a)=\sum_{s'}P(s'|s,a)\big[r+\gamma\max_{a'}Q^*(s',a')\big]\quad\text{(optimality)}.$$

**Value iteration converges.** The Bellman optimality operator $\mathcal T$ is a
$\gamma$-contraction in the sup norm: $|\max_aQ_1-\max_aQ_2|\le\max_a|Q_1-Q_2|$, hence
$\|\mathcal TQ_1-\mathcal TQ_2\|_\infty\le\gamma\|Q_1-Q_2\|_\infty$. Banach: unique
fixed point $Q^*$, error $\propto\gamma^k$. Requires the model $P$.

**Q-learning** [S25]: model-free stochastic approximation of $\mathcal T$ from
samples $(s,a,r,s')$:

$$Q(s,a)\leftarrow(1-\eta)Q(s,a)+\eta\big[r+\gamma\max_{a'}Q(s',a')\big]$$

(the exercise-12 form [S5]). The bracket is an unbiased sample of $(\mathcal TQ)(s,a)$.
Converges to $Q^*$ with probability 1 if every $(s,a)$ is updated infinitely often
and the step sizes satisfy Robbins-Monro, $\sum_t\eta_t=\infty$,
$\sum_t\eta_t^2<\infty$ (e.g. $\eta=n(s,a)^{-\omega}$, $\tfrac12<\omega\le1$). The
behaviour policy only has to explore; $\max$ makes it off-policy.
**TD error** $\delta=r+\gamma\max_{a'}Q(s',a')-Q(s,a)$; SARSA replaces $\max$ by the
action actually taken next.

**Exploration.** Greedy from the start locks onto the first rewarding action;
$\varepsilon$-greedy with decaying $\varepsilon$ (exercise 12: $\varepsilon\leftarrow\max(0.01,0.97\varepsilon)$ per
episode [S5]) trades exploration for exploitation. Optimistic initial $Q$ also
explores.

**Horizon from discount.** Rewards beyond $\sim1/(1-\gamma)$ steps barely count:
$\gamma$ is a physical time scale of the agent, not a mere convergence device.

## Exercise 12: CartPole with a Q-table [S5]

Observation $(x,\dot x,\theta,\dot\theta)$; actions push left/right; reward $+1$
per step while $|\theta|<12^\circ$ and the cart is on the track (episode ends at
500). Continuous observations are **discretised**: $\theta\in[-0.42,0.42]$ into 6
bins, $\dot\theta$ into 3 bins (thresholds $\pm0.29$), index $3i+j$, so an
$18\times2$ table; $x,\dot x$ ignored. $\gamma=0.99$, $\eta$ and $\varepsilon$ decayed
per episode. Hand-coded warm-ups: push toward the lean (growing oscillation),
push on $\dot\theta$ (cart runs off). Needs `gymnasium` [S34], so not reproduced
here offline.

## Physics toy (`src/py/qlearning.py`)

Particle on 21 sites in a box, tilted double well
$V(u)=(u^2-1)^2-0.3u$, $u\in[-2,2]$: metastable minimum $x=5$ ($V=+0.3$), global
minimum $x=15$ ($V=-0.3$), barrier $x=10$ ($V=1$). Actions: kick $-1,0,+1$;
reward $-V(x')-0.05|a|$; optional slip (random kick with probability $p$).

- Value iteration: an agent started in the metastable well **stays** for
  $\gamma\le0.85$ and **crosses** for $\gamma\ge0.9$. Crossing costs about
  $\sum V$ over the barrier now and gains $0.6$ per step later; with horizon
  $1/(1-\gamma)$ too short it never pays: a discount-induced metastability.
- Q-learning, $\gamma=0.95$, 3000 episodes $\times$ 60 steps, exploring starts,
  $\varepsilon=0.5$, $\eta=n^{-0.6}$: $\max|Q-Q^*|=0.027$ ($|Q^*|$ up to 20),
  greedy policy identical to the optimal one: `>>>>>>>>>>>>>>>.<<<<<`
  (move right until $x=15$, stay, from the right wall move left).
- Slip $0.2$: $\max|Q-Q^*|=0.87$ (noisier targets, same budget), policy still optimal.

## Pitfalls

- Constant $\eta$ does not converge under stochastic transitions; decay it, but
  not too fast ($\omega=0.8$ in our toy left errors $\approx2$ at the same budget).
- States never visited keep their initial $Q$: check visit counts.
- Discretisation can break the Markov property (hidden continuous variables).
- Reward shaping changes the optimal policy unless it is potential-based.
- Evaluate the learned policy greedily ($\varepsilon=0$), not with exploration on.

## Test-style questions

**Q1.** Specify CartPole as an MDP and say whether it is Markovian with and without velocities.
**A.** $s=(x,\dot x,\theta,\dot\theta)$, $a\in\{\text{left},\text{right}\}$, $r=1$ per
surviving step; deterministic Newtonian dynamics, Markovian in the full state.
Observing only $(x,\theta)$ is not Markovian (velocity hidden); stack two
frames or use a recurrent policy.

**Q2.** One Q-learning update: $Q(s,a)=2$, $r=1$, $\gamma=0.9$, $\max_{a'}Q(s',a')=5$, $\eta=0.5$.
**A.** Target $1+4.5=5.5$; $Q\leftarrow0.5\cdot2+0.5\cdot5.5=3.75$.

**Q3.** Prove value iteration converges.
**A.** $\mathcal T$ is a $\gamma$-contraction in $\|\cdot\|_\infty$ (above);
Banach's fixed-point theorem gives a unique fixed point and geometric convergence.

**Q4.** Why is Q-learning off-policy, and why does that matter for exploration?
**A.** The target uses $\max_{a'}$, the greedy policy's value, regardless of the
action the behaviour policy takes next. So any sufficiently exploring behaviour
(even uniform random) learns $Q^*$.

**Q5.** In the double well, why does a small $\gamma$ keep the agent in the metastable minimum?
**A.** Leaving costs $\approx\sum_{\text{barrier}}V>0$ immediately; the gain
$\Delta V=0.6$ per step arrives after $\sim10$ steps and is weighted by
$\gamma^{10}/(1-\gamma)$. For $\gamma\le0.85$ the discounted gain is smaller than
the cost (value iteration: switch between $0.85$ and $0.9$).

## Code

`src/py/qlearning.py`: `DoubleWell` (MDP with `transitions`, `step`),
`value_iteration`, `epsilon_greedy`, `q_learning` (count-based step size,
exploring starts), `greedy_policy`, `rollout`. Tests: Bellman residual $<10^{-9}$,
discount-dependent policy, $\|Q-Q^*\|_\infty<0.1$ and identical policy, slip case.
