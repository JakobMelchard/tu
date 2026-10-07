# 04 Deep reinforcement learning

Reinforcement learning (RL) is sequential decision making: an agent observes a state, picks an action, receives a scalar reward, and the environment moves to a new state. There is no labelled target per step; the learning signal is the discounted sum of future rewards, which is delayed, noisy and depends on the agent's own behaviour. Deep RL replaces the tabular policy or value function by a neural network so that large or continuous state spaces become tractable. The two dominant families are policy gradient (REINFORCE, actor-critic, PPO) and value-based methods (DQN and its variants); both are sample-hungry and fragile compared to supervised learning, so the project should budget for careful evaluation and reward design.

## Concepts

### MDP, policy, return

A Markov decision process is the tuple $(S, A, P, R, \gamma)$: state set $S$, action set $A$, transition kernel $P(s' \mid s, a)$, reward function $R(s, a, s')$ (or $r_t$ as a random variable), discount $\gamma \in [0, 1)$. Markov property: $P(s_{t+1} \mid s_t, a_t, s_{t-1}, \dots) = P(s_{t+1} \mid s_t, a_t)$.

A (stochastic) policy is $\pi(a \mid s)$; a parametrised policy is $\pi_\theta$. An episode (trajectory) is $\tau = (s_0, a_0, r_0, s_1, a_1, r_1, \dots, s_T)$ with $s_0 \sim \rho_0$, $a_t \sim \pi(\cdot \mid s_t)$, $s_{t+1} \sim P(\cdot \mid s_t, a_t)$.

The return from step $t$ is
$$G_t = \sum_{k=0}^{T-t-1} \gamma^k r_{t+k} = r_t + \gamma G_{t+1}.$$
The recursion is what makes returns computable in one backward pass over an episode. The objective is $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[G_0]$.

### Value functions and Bellman equations

State value and action value under $\pi$:
$$V^\pi(s) = \mathbb{E}_\pi[G_t \mid s_t = s], \qquad Q^\pi(s, a) = \mathbb{E}_\pi[G_t \mid s_t = s, a_t = a].$$
They are related by $V^\pi(s) = \sum_a \pi(a \mid s) Q^\pi(s, a)$.

Bellman expectation equations (from $G_t = r_t + \gamma G_{t+1}$ and the Markov property):
$$V^\pi(s) = \sum_a \pi(a \mid s) \sum_{s'} P(s' \mid s, a)\,[R(s, a, s') + \gamma V^\pi(s')],$$
$$Q^\pi(s, a) = \sum_{s'} P(s' \mid s, a)\,[R(s, a, s') + \gamma \sum_{a'} \pi(a' \mid s') Q^\pi(s', a')].$$

Bellman optimality equations, for the optimal $V^* = \max_\pi V^\pi$, $Q^* = \max_\pi Q^\pi$:
$$V^*(s) = \max_a \sum_{s'} P(s' \mid s, a)\,[R + \gamma V^*(s')], \qquad Q^*(s, a) = \sum_{s'} P(s' \mid s, a)\,[R + \gamma \max_{a'} Q^*(s', a')].$$
The optimal policy is greedy w.r.t. $Q^*$: $\pi^*(s) = \arg\max_a Q^*(s, a)$. The Bellman optimality operator is a $\gamma$-contraction in the sup norm, so value iteration converges in the tabular case; with function approximation this guarantee is lost (see deadly triad below).

### Policy gradient theorem and REINFORCE

Write $p_\theta(\tau) = \rho_0(s_0) \prod_t \pi_\theta(a_t \mid s_t) P(s_{t+1} \mid s_t, a_t)$ and $G(\tau) = G_0$. Log-derivative trick: $\nabla_\theta p_\theta = p_\theta \nabla_\theta \log p_\theta$. Then
$$\nabla_\theta J = \nabla_\theta \int p_\theta(\tau) G(\tau)\,d\tau = \int p_\theta(\tau) \nabla_\theta \log p_\theta(\tau) G(\tau)\,d\tau = \mathbb{E}_\tau\!\left[ \nabla_\theta \log p_\theta(\tau)\, G(\tau) \right].$$
Since $\rho_0$ and $P$ do not depend on $\theta$, $\nabla_\theta \log p_\theta(\tau) = \sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)$. The environment dynamics drop out; no model of $P$ is needed.

Causality: the action $a_t$ cannot influence rewards $r_k$ for $k < t$, and $\mathbb{E}[\nabla_\theta \log \pi_\theta(a_t \mid s_t)\, r_k] = 0$ for $k < t$ (same argument as the baseline below, applied per reward). Dropping those terms gives the REINFORCE estimator (Williams 1992 [S16, ch. 13]):
$$\nabla_\theta J = \mathbb{E}\!\left[ \sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\, G_t \right].$$
Implementation: sample one or more episodes, compute $G_t$ backwards, minimise the surrogate loss $L = -\sum_t \log \pi_\theta(a_t \mid s_t)\, G_t$ (stop-gradient on $G_t$) with a standard optimiser. The estimator is unbiased but high-variance because $G_t$ sums many random rewards.

### Baselines and variance reduction

For any function $b(s_t)$ of the state only,
$$\mathbb{E}_{a_t \sim \pi_\theta(\cdot \mid s_t)}\!\left[ \nabla_\theta \log \pi_\theta(a_t \mid s_t)\, b(s_t) \right] = b(s_t) \sum_a \nabla_\theta \pi_\theta(a \mid s_t) = b(s_t)\, \nabla_\theta \sum_a \pi_\theta(a \mid s_t) = b(s_t)\, \nabla_\theta 1 = 0.$$
So $\sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\,(G_t - b(s_t))$ is still unbiased, and a good $b$ (ideally close to $V^\pi(s_t)$) reduces variance. A baseline that depends on $a_t$ would break the argument (the sum over $a$ no longer factors).

Return normalisation: the cheapest baseline is the batch mean, $\hat G_t = (G_t - \bar G) / (\sigma_G + \epsilon)$. Dividing by the standard deviation is a heuristic that also sets the effective learning rate; it changes the gradient by a positive scalar and does not affect the direction in expectation for the batch mean part, but the per-batch scale factor is a mild bias that is accepted in practice.

### Actor-critic, advantage, GAE

Replace $G_t$ by a learned estimate to trade variance for bias. With a critic $V_\phi(s)$, the advantage $A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$ is estimated as the one-step TD error $\delta_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$ (low variance, biased by critic error) or as the Monte-Carlo $G_t - V_\phi(s_t)$ (unbiased, high variance). Generalised advantage estimation (Schulman et al. 2016 [S52]) interpolates: $\hat A_t^{\mathrm{GAE}(\gamma, \lambda)} = \sum_{l \ge 0} (\gamma \lambda)^l \delta_{t+l}$, with $\lambda = 0$ giving TD and $\lambda = 1$ giving Monte-Carlo minus baseline; $\lambda \approx 0.95$ is the usual default. The actor loss is $-\sum_t \log \pi_\theta(a_t \mid s_t)\, \hat A_t$, the critic loss is $\sum_t (V_\phi(s_t) - \hat G_t)^2$, both updated from the same rollouts.

Entropy bonus: add $-\beta\, \mathcal H[\pi_\theta(\cdot \mid s_t)] = \beta \sum_a \pi_\theta(a \mid s_t) \log \pi_\theta(a \mid s_t)$ to the loss ($\beta \sim 10^{-2}$) to discourage premature collapse to a deterministic policy. This is the policy-gradient form of exploration.

### PPO

Proximal policy optimisation (Schulman et al. 2017 [S52]) reuses one batch of rollouts for several gradient epochs while limiting how far the policy moves. With the probability ratio $\rho_t(\theta) = \pi_\theta(a_t \mid s_t) / \pi_{\theta_{\mathrm{old}}}(a_t \mid s_t)$, the clipped objective is
$$L^{\mathrm{CLIP}}(\theta) = \mathbb{E}_t\!\left[ \min\!\big( \rho_t \hat A_t,\ \mathrm{clip}(\rho_t, 1 - \epsilon, 1 + \epsilon)\, \hat A_t \big) \right], \qquad \epsilon = 0.2.$$
The $\min$ makes the objective a pessimistic bound: for $\hat A_t > 0$ the incentive to increase $\rho_t$ stops at $1 + \epsilon$; for $\hat A_t < 0$ the incentive to decrease it stops at $1 - \epsilon$. Total loss $= -L^{\mathrm{CLIP}} + c_1 (V_\phi - \hat G)^2 - c_2 \mathcal H$. Typical settings: GAE $\lambda = 0.95$, $\gamma = 0.99$, 4 to 10 epochs per batch, minibatches of 64, Adam $3 \times 10^{-4}$, gradient clipping 0.5. PPO is the default choice if the project uses RL: it is on-policy, works for discrete and continuous actions, and is robust to hyperparameters relative to DQN or DDPG.

### DQN

Q-learning (Watkins 1989) is off-policy TD control: it regresses $Q(s, a)$ towards the one-step bootstrapped target of the optimality equation. With a network $Q(s, a; \theta)$ the loss per transition $(s, a, r, s', d)$ ($d$ = terminal flag) is
$$L(\theta) = \big( y - Q(s, a; \theta) \big)^2, \qquad y = r + \gamma (1 - d) \max_{a'} Q(s', a'; \theta^-),$$
with the gradient taken only through $Q(s, a; \theta)$, not through $y$. Deep Q-network (Mnih et al. 2015 [S51]) adds two stabilisers:

- Experience replay: store transitions in a ring buffer ($10^5$ to $10^6$), sample uniform minibatches. Breaks temporal correlation between consecutive samples and reuses each transition many times.
- Target network: $\theta^-$ is a frozen copy of $\theta$, updated every $C$ steps (hard, $C \sim 10^3$ to $10^4$) or by Polyak averaging $\theta^- \leftarrow \tau \theta + (1 - \tau)\theta^-$, $\tau \sim 0.005$. Keeps the regression target fixed for a while so the update is closer to supervised regression.

Double DQN (van Hasselt et al. 2016): $\max_{a'} Q(s', a'; \theta^-)$ uses the same network to choose and to evaluate the action, so noise in $Q$ produces an upward bias ($\mathbb{E}[\max_a X_a] \ge \max_a \mathbb{E}[X_a]$). Decouple: $y = r + \gamma Q(s', \arg\max_{a'} Q(s', a'; \theta); \theta^-)$.

Deadly triad (Sutton & Barto 2018, ch. 11 [S16]): function approximation + bootstrapping + off-policy training can diverge, because the TD update is not the gradient of any fixed objective (the target moves with $\theta$) and the sampling distribution is not the one the Bellman operator contracts under. DQN has all three; replay and target networks make divergence rare but not impossible. Symptoms: Q-values growing without bound, sudden performance collapse.

### Exploration

- $\epsilon$-greedy: with probability $\epsilon$ take a uniform random action, else $\arg\max_a Q$. Anneal $\epsilon$ from 1.0 to 0.05 over the first 10% of training. Simple, undirected, standard for DQN.
- Softmax / Boltzmann: $\pi(a \mid s) \propto \exp(Q(s, a) / \tau)$; temperature $\tau \to 0$ is greedy, $\tau \to \infty$ uniform. Directed by value differences, but sensitive to the scale of $Q$.
- Entropy regularisation: the entropy bonus above (A2C, PPO, SAC) keeps the stochastic policy from collapsing; the policy itself is the exploration mechanism.
- Optimism / UCB: prefer actions with high uncertainty, $a = \arg\max_a [Q(s, a) + c \sqrt{\log t / N(s, a)}]$ in bandits; deep analogues are count-based bonuses, random network distillation and bootstrapped ensembles. Needed when rewards are very sparse.

### Reward design and discount

- Sparse reward (only at the goal) is the honest specification but gives no gradient until the agent stumbles on the goal by chance; success probability under a random policy decays exponentially with the horizon. Dense reward (distance to goal, per-step progress) speeds learning but encodes the designer's guess.
- Potential-based shaping (Ng, Harada & Russell 1999 [S54]): replacing $R$ by $R'(s, a, s') = R(s, a, s') + \gamma \Phi(s') - \Phi(s)$ for any $\Phi: S \to \mathbb{R}$ leaves the set of optimal policies unchanged, since the shaping terms telescope: $\sum_t \gamma^t (\gamma \Phi(s_{t+1}) - \Phi(s_t)) = -\Phi(s_0) + \lim \gamma^{T} \Phi(s_T)$, a constant per start state. Non-potential shaping (e.g. a bonus for picking up a key) can create loops the agent exploits.
- Reward hacking: the agent maximises the stated reward, not the intended behaviour (circling a bonus item, exploiting a simulator bug). Log the actual behaviour, not only the return curve.
- Per-step penalty (e.g. $-0.01$) encourages short episodes and acts as a weak dense signal; combined with a large terminal reward it keeps the return positive for good episodes and negative for time-outs.
- Discount: $\gamma$ sets the effective horizon $\approx 1 / (1 - \gamma)$; $\gamma = 0.98$ looks 50 steps ahead, $\gamma = 0.99$ 100 steps. Too small: the agent ignores distant goals. Too large: returns have high variance and value targets become large. Choose $\gamma$ from the length of the causal chain between decision and consequence, not as a free hyperparameter.

### Practical

- Episode length limits: always cap $T_{\max}$ (`max_steps`), otherwise a policy that never terminates stalls data collection. Truncation is not termination: bootstrapping $V(s_{T_{\max}})$ is still valid at a truncated state and wrong at a true terminal.
- Gymnasium API (Towers et al. 2023 [S95]): `obs, info = env.reset(seed=s)`; `obs, reward, terminated, truncated, info = env.step(action)`. `terminated` = the MDP ended (goal, death), `truncated` = time limit hit. Use `done = terminated or truncated` for episode bookkeeping and `terminated` alone for masking the bootstrap target. `env.action_space`, `env.observation_space` describe shapes.
- Evaluation: train and evaluation seeds must differ; evaluate the greedy or mean policy over many episodes (100 or more) and report mean and standard error of the return plus success rate; run at least 3 to 5 training seeds and plot the median with quartiles, since RL variance across seeds is large (Henderson et al. 2018 [S93]).
- Vectorised environments ($N$ copies stepped in lock step) are the main throughput lever for on-policy methods; the rollout tensor is then `[N, T_rollout, ...]`.

## Architecture sketch

`GridWorld(size=5, max_steps=30)`: cells $(i, j)$, start $(0, 0)$ top-left, goal $(4, 4)$ bottom-right, one pit cell; actions {up, down, left, right}; reward $-0.01$ per step, $+1$ at goal, $-1$ at pit, both terminal; state is the one-hot position of length $25$.

```
episode loop (REINFORCE):

  s_0 one-hot [25]
     |
     v
  PolicyNet: Linear(25, 64) -> tanh -> Linear(64, 4) -> log-softmax  ->  log pi(.|s) [4]
     |  sample a_t ~ Categorical(pi)
     v
  env.step(a_t) -> (s_{t+1} [25], r_t, done)          repeated until done or t = max_steps
     |
     v
  rewards [T]  --discounted_returns(gamma)-->  G [T]   (backward pass G_t = r_t + gamma G_{t+1})
     |
     v
  normalise G -> (G - mean) / (std + 1e-8)
     |
     v
  loss = -sum_t log pi(a_t | s_t) * G_t   ->  backward  ->  Adam step
```

Batched version stacks the $T$ states of one episode into `[T, 25]`, one forward pass gives `[T, 4]` log-probabilities, gather the taken actions to `[T]`.

Parameter count of `PolicyNet`: $25 \cdot 64 + 64 + 64 \cdot 4 + 4 = 1600 + 64 + 256 + 4 = 1924$.

Worked example, discounted returns with $\gamma = 0.9$ for the reward sequence $r = (-0.01, -0.01, -0.01, +1)$ (three steps then the goal):

- $G_3 = 1$
- $G_2 = -0.01 + 0.9 \cdot 1 = 0.89$
- $G_1 = -0.01 + 0.9 \cdot 0.89 = 0.791$
- $G_0 = -0.01 + 0.9 \cdot 0.791 = 0.7019$

With the pit instead, $r = (-0.01, -0.01, -1)$: $G_2 = -1$, $G_1 = -0.91$, $G_0 = -0.829$. A time-out after 30 steps of $-0.01$: $G_0 = -0.01 \cdot (1 - 0.9^{30}) / (1 - 0.9) \approx -0.0958$. The ordering pit $<$ time-out $<$ goal is what the per-step penalty plus terminal rewards are designed to produce; note the time-out is only mildly worse than a fast pit, which is fine because the pit is also terminal.

## Pitfalls

- Return curve flat at the time-out value for hundreds of episodes -> sparse reward, random policy never reaches the goal -> shrink the grid, add a potential-based shaping term $\Phi(s) = -\mathrm{dist}(s, \mathrm{goal})$, or increase exploration (entropy bonus, higher initial temperature).
- Policy collapses to one action early (entropy near 0, success rate 0) -> learning rate too high or returns not normalised, so one lucky episode dominates -> normalise returns, lower lr to $10^{-3}$ or below, add an entropy bonus.
- Loss decreases but return does not -> the surrogate $-\sum \log \pi\, G$ is not a performance measure; its value depends on the policy's own entropy -> monitor the moving-average return and success rate, treat the surrogate only as a gradient source.
- Gradient through the returns -> `G` computed from tensors that carry `requires_grad` (e.g. when a critic value is subtracted) -> `.detach()` the advantage before multiplying with the log-probability.
- DQN Q-values explode, return collapses after initially improving -> deadly triad, target network updated too often or lr too high -> larger target update interval, Huber loss instead of MSE, gradient clipping, Double DQN.
- Agent looks good in training logs, bad in evaluation -> training return includes $\epsilon$-greedy or stochastic exploration, evaluation uses the greedy policy, or training seeds were reused -> evaluate greedy policy on held-out seeds, many episodes, several training seeds.
- Bootstrapping at a truncated state treated as terminal -> $V(s_{T_{\max}})$ multiplied by $(1 - d)$ with $d = 1$ -> mask only on `terminated`, not on `truncated`.
- Reward hacking: high return, wrong behaviour -> reward proxy exploited (e.g. a shaping bonus that can be collected repeatedly) -> render or log trajectories, restrict shaping to potential-based form, check for loops.
- Wildly different results across runs -> RL variance across seeds is intrinsic -> never report a single seed; report median and quartiles of 5 seeds and fix `seed_all(seed)` for reproducibility.
- Slow wall-clock training on the M3 -> tiny networks and per-step Python overhead dominate; `mps` adds kernel-launch latency for small tensors -> run small RL models on `cpu`, batch episodes, or vectorise environments.

## Questions

1. Derive the REINFORCE gradient from $J(\theta) = \mathbb{E}_{\tau \sim p_\theta}[G(\tau)]$ and explain why the transition model $P$ does not appear.

<details><summary>Answer</summary>
$\nabla_\theta J = \int \nabla_\theta p_\theta(\tau) G(\tau) d\tau = \int p_\theta(\tau) \nabla_\theta \log p_\theta(\tau) G(\tau) d\tau = \mathbb{E}[\nabla_\theta \log p_\theta(\tau) G(\tau)]$ by the log-derivative trick. $\log p_\theta(\tau) = \log \rho_0(s_0) + \sum_t [\log \pi_\theta(a_t \mid s_t) + \log P(s_{t+1} \mid s_t, a_t)]$; only the policy terms depend on $\theta$, so $\nabla_\theta \log p_\theta(\tau) = \sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)$. Replacing $G(\tau)$ by $G_t$ per term uses that past rewards are uncorrelated with the current score function in expectation.
</details>

2. Show that subtracting a state-dependent baseline $b(s_t)$ leaves the policy gradient estimator unbiased. Why does an action-dependent baseline fail?

<details><summary>Answer</summary>
$\mathbb{E}_{a \sim \pi_\theta(\cdot \mid s)}[\nabla_\theta \log \pi_\theta(a \mid s) b(s)] = b(s) \sum_a \pi_\theta(a \mid s) \nabla_\theta \log \pi_\theta(a \mid s) = b(s) \sum_a \nabla_\theta \pi_\theta(a \mid s) = b(s) \nabla_\theta \sum_a \pi_\theta(a \mid s) = b(s) \nabla_\theta 1 = 0$. With $b(s, a)$ the factor cannot be pulled out of the sum, so $\sum_a b(s, a) \nabla_\theta \pi_\theta(a \mid s) \ne 0$ in general.
</details>

3. Write the DQN target and explain the role of the target network and of experience replay. What does Double DQN change and why?

<details><summary>Answer</summary>
$y = r + \gamma (1 - d) \max_{a'} Q(s', a'; \theta^-)$, loss $(y - Q(s, a; \theta))^2$, no gradient through $y$. The target network $\theta^-$ is a delayed copy so the regression target does not move with every update (otherwise the same weights chase themselves and can diverge). Replay stores transitions and samples them uniformly, breaking the strong correlation of consecutive frames and reusing data. Double DQN uses $\arg\max$ from the online network and evaluates it with the target network, removing the maximisation bias $\mathbb{E}[\max_a X_a] \ge \max_a \mathbb{E}[X_a]$ that arises when the same noisy estimate selects and scores the action.
</details>

4. State the deadly triad and explain in one sentence each why each element contributes to instability.

<details><summary>Answer</summary>
Function approximation: updates to one state's value change other states' values, so the Bellman backup is no longer a per-state contraction. Bootstrapping: targets depend on the current (wrong) estimates, so errors propagate. Off-policy data: the states are sampled from a distribution different from the one under which the projected Bellman operator is a contraction, so the fixed-point argument fails. Any two are fine; all three together admit divergence (Sutton & Barto 2018, ch. 11 [S16]).
</details>

5. Prove that potential-based reward shaping $R' = R + \gamma \Phi(s') - \Phi(s)$ does not change the optimal policy.

<details><summary>Answer</summary>
Along any trajectory, $\sum_{t} \gamma^t [\gamma \Phi(s_{t+1}) - \Phi(s_t)] = \sum_t \gamma^{t+1} \Phi(s_{t+1}) - \sum_t \gamma^t \Phi(s_t) = -\Phi(s_0) + \gamma^{T} \Phi(s_T)$ (telescoping; the last term is 0 with a terminal convention $\Phi(\text{terminal}) = 0$ or vanishes as $T \to \infty$). So $G'_0 = G_0 - \Phi(s_0)$ for every trajectory from $s_0$: returns of all policies shift by the same state-dependent constant, $Q'^\pi(s, a) = Q^\pi(s, a) - \Phi(s)$, and the $\arg\max_a$ is unchanged. Ng, Harada & Russell 1999 [S54] show this form is also necessary for invariance over all transition models.
</details>

6. Compute $G_0$ with $\gamma = 0.5$ for $r = (0, 0, 0, 8)$, and explain what changes if $\gamma = 0.99$.

<details><summary>Answer</summary>
$G_0 = 0 + 0.5 \cdot 0 + 0.25 \cdot 0 + 0.125 \cdot 8 = 1$. With $\gamma = 0.99$, $G_0 = 0.99^3 \cdot 8 \approx 7.76$. A small $\gamma$ shrinks distant rewards exponentially (effective horizon $1 / (1 - \gamma) = 2$ steps here), so an agent with $\gamma = 0.5$ would barely distinguish reaching the reward at step 3 from never reaching it; $\gamma = 0.99$ keeps the signal but makes the return variance across long episodes larger.
</details>

7. In the PPO clipped objective, what happens to the gradient of a sample with $\hat A_t > 0$ once $\rho_t > 1 + \epsilon$, and why is this the intended behaviour?

<details><summary>Answer</summary>
For $\hat A_t > 0$, $\min(\rho_t \hat A_t, \mathrm{clip}(\rho_t) \hat A_t) = (1 + \epsilon) \hat A_t$ once $\rho_t > 1 + \epsilon$, which is constant in $\theta$: the gradient is zero. The sample can no longer push the policy further towards $a_t$. This implements a trust region without a KL constraint: the policy is allowed to move at most a factor $1 \pm \epsilon$ in probability per update on any sample, so several epochs on the same batch stay close to $\pi_{\theta_{\mathrm{old}}}$ where the advantage estimates are valid.
</details>

8. Project question: you want to train an agent on a small custom Gymnasium environment for phase 2 of the course project. Which algorithm, reward and evaluation protocol would you choose, and what would you report in phase 3?

<details><summary>Answer</summary>
PPO with GAE ($\gamma = 0.99$, $\lambda = 0.95$, $\epsilon = 0.2$, entropy coefficient 0.01), vectorised environments, on CPU for a tiny policy. Reward: the true sparse objective plus a potential-based shaping term if learning does not start; a small per-step penalty and a `max_steps` truncation with correct bootstrap masking. Evaluation: fixed evaluation seeds disjoint from training seeds, 100 or more episodes with the mean (deterministic) policy, 5 training seeds, report median return and interquartile range plus success rate. Phase 3 compares against a documented baseline (random policy, a hand-coded heuristic, and published PPO/DQN numbers if the environment is standard) and states the compute budget.
</details>

## Code

`src/py/rl_reinforce.py`: `GridWorld(size=5, max_steps=30)` (inline environment: start top-left, goal bottom-right, one pit; reward $-0.01$ per step, $+1$ goal, $-1$ pit; state = one-hot position), `PolicyNet`, `discounted_returns(rewards, gamma)` (backward recursion $G_t = r_t + \gamma G_{t+1}$), `run_episode(env, policy)`, `run(episodes=400, gamma=0.98, entropy_coef=0.01, exploring_starts=True, device=None, seed=0)` returning `{"losses", "returns", "success_rate", "greedy_reaches_goal", "greedy_steps"}`. Two of the tricks above are needed even on a 5x5 grid: without exploring starts (random initial cell during training) or an entropy bonus, REINFORCE from the corner finds the $+1$ so rarely that it converges to bumping into a wall for $-0.3$ (better than the pit) on most seeds; evaluation is always greedy from the top-left corner (optimal path 8 steps). `"losses"` is the negative moving average of the episode return, so that "loss decreases" means "return increases". Uses `common.get_device()`, `common.seed_all(seed)`. Running `python src/py/rl_reinforce.py` from the repo root with `.venv/bin/python` trains for a few seconds and prints the success rate. `test_rl_reinforce.py` calls `run` with a small episode budget and asserts `common.loss_decreased(losses)`: the mean of the last 10% of `losses` is below the mean of the first 10%.

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016): ch. 5.10 (learning as optimisation, brief RL context), ch. 8 (optimisation, used for the policy updates). RL itself is not covered in Goodfellow; use Sutton & Barto.
- Sutton, R. S. & Barto, A. G., *Reinforcement Learning: An Introduction*, 2nd ed. (2018) [S16]: ch. 3 (MDPs, Bellman equations), ch. 6 (TD, Q-learning), ch. 11 (deadly triad), ch. 13 (policy gradient, REINFORCE with baseline, actor-critic).
- Williams, R. J. (1992). Simple statistical gradient-following algorithms for connectionist reinforcement learning. REINFORCE.
- Mnih, V. et al. (2015) [S51]. Human-level control through deep reinforcement learning. DQN. **Lecture 6's reference 11** [S4].
- van Hasselt, H., Guez, A., Silver, D. (2016). Deep reinforcement learning with double Q-learning.
- Schulman, J. et al. (2016) [S52]. High-dimensional continuous control using generalized advantage estimation. GAE.
- Schulman, J. et al. (2017) [S52]. Proximal policy optimization algorithms. PPO.
- Mnih, V. et al. (2016). Asynchronous methods for deep reinforcement learning. A3C, entropy bonus.
- Ng, A. Y., Harada, D., Russell, S. (1999) [S54]. Policy invariance under reward transformations: theory and application to reward shaping.
- Henderson, P. et al. (2018) [S93]. Deep reinforcement learning that matters. Seeds and evaluation.
- Towers, M. et al. (2023) [S95]. Gymnasium. API reference for `reset` / `step`.
- **Lecture 6** [S4], *Deep Reinforcement Learning*, is the lecture this note covers. Its own first reference is **Amini & Soleimany, MIT 6.S191** [S17], whose framing (classes of learning problems; key concepts; quality/value/policy functions; Q-function to the policy) is the lecture's structure. It also spends 14 minutes on **reward shaping, auxiliary tasks and hindsight experience replay** [S53] and works Karpathy's *Pong from pixels* [S55] as its running example.
