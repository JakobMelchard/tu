# B02 PSPACE, EXPTIME and the hierarchy theorems

Above NP sit the classes defined by polynomial space and exponential time. Space behaves very differently from time: nondeterminism costs only a square (Savitch), so PSPACE = NPSPACE and the natural complete problem, TQBF, is a game rather than a search. The hierarchy theorems are the only unconditional separations we have; they prove $\mathrm P \ne \mathrm{EXPTIME}$ and $\mathrm{NL} \ne \mathrm{PSPACE}$ by diagonalisation, which pins down where the unknown strict inclusions in $\mathrm L \subseteq \mathrm{NL} \subseteq \mathrm P \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXPTIME}$ must hide. References: Papadimitriou ch. 7.2-7.3 (space, Savitch, hierarchy theorems), ch. 19 (PSPACE-completeness, QBF, games), ch. 17 (polynomial hierarchy) [S26]; Savitch [S56]. **The polynomial hierarchy is not on the 192.043 subject list** [S1] but it is on the list of the co-taught 192.219 [S5] and is a named topic of Pichler's own complexity course [S7, S14], so it is treated here. Exam 1 material.

## Definitions

- $\mathrm{PSPACE} = \bigcup_k \mathrm{SPACE}(n^k)$, $\mathrm{NPSPACE} = \bigcup_k \mathrm{NSPACE}(n^k)$. Space of a multi-tape TM = cells used on the work tapes (for sublinear space the input tape is read-only and not counted, B03).
- $\mathrm{EXPTIME} = \bigcup_k \mathrm{DTIME}(2^{n^k})$, $\mathrm{NEXPTIME} = \bigcup_k \mathrm{NTIME}(2^{n^k})$, $\mathrm{EXPSPACE}$ analogously. ($\mathrm E = \mathrm{DTIME}(2^{O(n)})$ is a different, smaller class; it is not closed under polynomial reductions.)
- A function $f$ is **space-constructible** (time-constructible) if some TM computes $1^n \mapsto f(n)$ in binary using $O(f(n))$ space (time). All the usual functions ($\log n$, $n^k$, $2^n$) are.
- **Configuration graph** $G_{M,x}$ of a machine $M$ on input $x$: vertices = configurations, edge $C \to C'$ iff $C \vdash C'$. With space $s(n) \ge \log n$ there are at most $|Q| \cdot n \cdot s(n) \cdot |\Gamma|^{s(n)} = 2^{O(s(n))}$ configurations.
- **QBF / TQBF.** A fully quantified Boolean formula $\Phi = Q_1 x_1 Q_2 x_2 \cdots Q_n x_n\, \varphi(x_1, \dots, x_n)$, $Q_i \in \{\exists, \forall\}$, $\varphi$ quantifier-free. TQBF = the set of true such formulas. SAT is the special case with only $\exists$; TAUTOLOGY (coNP-complete) has only $\forall$.
- **Polynomial hierarchy.** $\Sigma_k^p$: languages $\{x : \exists y_1 \forall y_2 \cdots Q_k y_k\ V(x, y_1, \dots, y_k) = 1\}$ with $|y_i| \le \mathrm{poly}(|x|)$ and polynomial-time $V$; $\Pi_k^p = \mathrm{co}\Sigma_k^p$. $\Sigma_1^p = \mathrm{NP}$, $\Pi_1^p = \mathrm{coNP}$, $\Sigma_0^p = \mathrm P$, $\mathrm{PH} = \bigcup_k \Sigma_k^p$. Equivalent oracle definition $\Sigma_{k+1}^p = \mathrm{NP}^{\Sigma_k^p}$.

## Results

**Basic inclusions.** For $f(n) \ge \log n$ constructible:
$$\mathrm{DTIME}(f) \subseteq \mathrm{SPACE}(f) \subseteq \mathrm{NSPACE}(f) \subseteq \mathrm{DTIME}\big(2^{O(f)}\big).$$
The first: one cell per step. The last: build the configuration graph ($2^{O(f)}$ vertices) and run BFS from the start configuration to the accepting one. Consequences: $\mathrm{NP} \subseteq \mathrm{PSPACE}$ (simulate all branches of an NTM one after the other, reusing space; equivalently, $\mathrm{NTIME}(f) \subseteq \mathrm{SPACE}(f)$) and $\mathrm{PSPACE} \subseteq \mathrm{EXPTIME}$.

**Theorem (Savitch 1970 [S56]).** For space-constructible $s(n) \ge \log n$: $\mathrm{NSPACE}(s) \subseteq \mathrm{SPACE}(s^2)$.
*Proof.* Let $N$ use space $s$; its configuration graph has $\le 2^{c\, s(n)} =: 2^{K}$ vertices, and $x$ is accepted iff the accepting configuration $C_{acc}$ (made unique by erasing the tape before accepting) is reachable from $C_0$ by a path of length $\le 2^K$. Define
$$\mathrm{REACH}(C, C', k) = \big[\text{there is a path } C \to C' \text{ of length} \le 2^k\big], \qquad \mathrm{REACH}(C, C', k) = \bigvee_{C''} \big[\mathrm{REACH}(C, C'', k-1) \wedge \mathrm{REACH}(C'', C', k-1)\big],$$
with base case $k = 0$: $C = C'$ or $C \vdash C'$ (checked directly). Evaluate recursively, **enumerating** the middle configurations $C''$ (space $K$ bits for the counter). Recursion depth $K$; each stack frame stores $(C, C', C'', k)$: $O(K)$ bits. Total space $O(K^2) = O(s(n)^2)$. The time is $2^{O(K^2)} = n^{O(\log n)}$ for $s = \log n$; Savitch trades time for space. $\square$

Corollaries: $\mathrm{PSPACE} = \mathrm{NPSPACE}$ (square of a polynomial is a polynomial); $\mathrm{NL} \subseteq \mathrm{SPACE}(\log^2 n)$ (B03). Contrast: nobody knows whether $\mathrm{NTIME}(f) \subseteq \mathrm{DTIME}(f^2)$; the analogue of Savitch for time would give $\mathrm P = \mathrm{NP}$.

**Theorem (Stockmeyer-Meyer).** TQBF is PSPACE-complete (under polynomial-time reductions).
*Membership.* Evaluate recursively: $\mathrm{eval}(Q_1 x_1 \cdots)$ tries $x_1 = 0$ then $x_1 = 1$, combining with OR ($\exists$) or AND ($\forall$), reusing the space of the first branch for the second. Depth $n$, each frame $O(1)$ bits plus the current partial assignment: $O(n)$ space, plus $O(|\varphi|)$ to evaluate the matrix. Time $2^n$: polynomial space, exponential time.
*Hardness (sketch).* Let $L \in \mathrm{SPACE}(p(n))$ via $M$. As in Cook-Levin encode a configuration $C$ by $O(p(n))$ Boolean variables; a formula $\varphi_0(C, C')$ of polynomial size expresses "$C = C'$ or $C \vdash C'$". Savitch's recursion written as a formula, $\varphi_k(C, C') = \exists C''\, [\varphi_{k-1}(C, C'') \wedge \varphi_{k-1}(C'', C')]$, doubles in size at every level and $k = O(p(n))$, so the size would be exponential. The fix is a universal quantifier that lets **one** copy of $\varphi_{k-1}$ serve both conjuncts:
$$\varphi_k(C, C') = \exists C''\ \forall D_1 \forall D_2\ \Big[\big((D_1, D_2) = (C, C'') \vee (D_1, D_2) = (C'', C')\big) \to \varphi_{k-1}(D_1, D_2)\Big].$$
Each level adds $O(p(n))$ variables and $O(p(n))$ symbols; with $k = O(p(n))$ levels the formula has size $O(p(n)^2)$ and is built in polynomial time. $x \in L$ iff $\varphi_{K}(C_0, C_{acc})$ is true. (Convert to prenex form by pulling the quantifiers out; this is where the alternation $\exists \forall \exists \forall \cdots$ comes from.) $\square$

**Games.** TQBF is a two-player game: $\exists$ chooses the odd variables, $\forall$ the even ones, $\exists$ wins iff $\varphi$ becomes true; TQBF asks whether $\exists$ has a winning strategy. Generalised versions of Geography, Hex, Go (with polynomial move bound), Reversi and STRIPS planning with a polynomial plan bound are PSPACE-complete (Papadimitriou 19.2). Games with exponentially long plays (chess, Go with ko rules, on $n \times n$ boards) are EXPTIME-complete. Rule of thumb: alternating quantifiers over polynomially many rounds $\Rightarrow$ PSPACE.

**Theorem (time hierarchy, Hartmanis-Stearns).** If $f, g$ are time-constructible and $f(n) \log f(n) = o(g(n))$, then $\mathrm{DTIME}(f) \subsetneq \mathrm{DTIME}(g)$.
*Proof (diagonalisation).* Define $D$: on input $w = \langle M \rangle 10^k$ (a machine description followed by padding), simulate $M$ on $w$ for $g(|w|)$ steps using a universal TM with a step counter; if $M$ halts and **rejects** within the budget, $D$ accepts, otherwise (accepts or times out) $D$ rejects. The universal simulation of $t$ steps of a fixed machine costs $O(t \log t)$ (the $\log$ factor comes from keeping the counter and the multi-tape encoding; Papadimitriou Thm 2.2), and computing $g(|w|)$ is affordable by constructibility, so $L(D) \in \mathrm{DTIME}(g)$. Suppose $L(D) \in \mathrm{DTIME}(f)$, decided by some $M^*$ running in time $c f(n)$. Choose the padding $k$ so large that the simulation of $M^*$ on $w = \langle M^* \rangle 10^k$ finishes within $g(|w|)$ steps, possible because $c' f(n) \log f(n) < g(n)$ for large $n$. Then $D$ accepts $w$ iff $M^*$ rejects $w$ iff $w \notin L(D)$. Contradiction. $\square$
The padding is what makes "for large $n$" usable: the constant in $M^*$'s running time is unknown, but there are infinitely many encodings of $M^*$ of increasing length.

**Theorem (space hierarchy).** For space-constructible $f, g$ with $f = o(g)$, $g \ge \log n$: $\mathrm{SPACE}(f) \subsetneq \mathrm{SPACE}(g)$. Same proof; space simulation has only constant overhead, hence no $\log$ factor. Nondeterministic versions: $\mathrm{NTIME}(f) \subsetneq \mathrm{NTIME}(g)$ for $f(n+1) = o(g(n))$ (Cook, Seiferas-Fischer-Meyer; the proof is harder because "reject if the simulation accepts" does not work nondeterministically), $\mathrm{NSPACE}(f) \subsetneq \mathrm{NSPACE}(g)$ via Immerman-Szelepcsényi (B03).

**Consequences.**
- $\mathrm P \subsetneq \mathrm{EXPTIME}$: $\mathrm P \subseteq \mathrm{DTIME}(2^n)$, and $2^n \log 2^n = n 2^n = o(2^{n^2})$, so $\mathrm{DTIME}(2^n) \subsetneq \mathrm{DTIME}(2^{n^2}) \subseteq \mathrm{EXPTIME}$. Likewise $\mathrm{NP} \subsetneq \mathrm{NEXPTIME}$, $\mathrm{PSPACE} \subsetneq \mathrm{EXPSPACE}$.
- $\mathrm L \subsetneq \mathrm{PSPACE}$: $\log n = o(n)$.
- $\mathrm{NL} \subsetneq \mathrm{PSPACE}$: Savitch gives $\mathrm{NL} \subseteq \mathrm{SPACE}(\log^2 n)$ and $\log^2 n = o(n)$.
- Hence in $\mathrm L \subseteq \mathrm{NL} \subseteq \mathrm P \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXPTIME} \subseteq \mathrm{NEXPTIME}$ at least one of $\mathrm{NL} \subseteq \mathrm P \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE}$ is strict and at least one of $\mathrm P \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXPTIME}$ is strict, but no individual one is known to be. Also $\mathrm P = \mathrm{NP} \Rightarrow \mathrm{EXPTIME} = \mathrm{NEXPTIME}$ (padding argument: pad the input to length $2^{n^k}$).

**coNP and PH.** $\mathrm{coNP} \subseteq \mathrm{PSPACE}$ (PSPACE is closed under complement: deterministic). $\Sigma_k^p \subseteq \mathrm{PSPACE}$ for every $k$: a $\Sigma_k$ statement is a QBF with $k$ blocks of quantifiers, evaluated in polynomial space, so $\mathrm{PH} \subseteq \mathrm{PSPACE}$. $\mathrm{PH} = \mathrm{PSPACE}$ would make TQBF complete for some $\Sigma_k^p$ and collapse PH to that level, so it is believed $\mathrm{PH} \subsetneq \mathrm{PSPACE}$. $\mathrm P = \mathrm{NP} \Rightarrow \mathrm{PH} = \mathrm P$ (induction on $k$ using the oracle characterisation); $\mathrm{NP} = \mathrm{coNP} \Rightarrow \mathrm{PH} = \mathrm{NP}$. Complete problems: $\Sigma_k$-SAT = TQBF restricted to $k$ alternations, $\exists \forall \cdots$. Used in B04 (Karp-Lipton), B05 (BPP $\subseteq \Sigma_2^p$), B06 (Toda-type statements).

## Worked example

*Savitch's space bound with numbers.* An NL machine on inputs of length $n = 2^{10} = 1024$ with work tape of $\log_2 n = 10$ bits, $|Q| = 16$ states, binary work alphabet: configurations $\le 16 \cdot 1024 \cdot 10 \cdot 2^{10} \approx 1.7 \cdot 10^8 < 2^{28}$, so $K = 28$. REACH recursion depth 28, each frame three configuration names of 28 bits plus $k$: about $90$ bits; total stack $\approx 28 \cdot 90 \approx 2500$ bits $= O(\log^2 n)$, versus $2^{28}$ bits for a visited-set in BFS. Time: at depth $j$ there are $2^{28}$ choices of $C''$ and two recursive calls: $(2 \cdot 2^{28})^{28} \approx 2^{812}$ steps in the worst case.

*TQBF by hand.* $\Phi = \exists x \forall y \exists z\ (x \vee y)(\neg y \vee z)(\neg x \vee \neg z)$.
- $x = 1$: $y = 0$ needs $z$ with $(\neg 0 \vee z) = 1$ and $\neg z = 1$: $z = 0$ works. $y = 1$ needs $z = 1$ from the second clause but $\neg z = 1$ from the third: no $z$. So $\forall y$ fails for $x = 1$.
- $x = 0$: $y = 0$ falsifies $(x \vee y)$. Fails.
$\Phi$ is false. The recursion visited 2 (for $x$) $\times$ 2 ($y$) $\times$ 2 ($z$) leaves at most, storing only the current path $(x, y, z)$: 3 bits of stack. Swapping quantifiers changes the answer: $\forall y \exists x \exists z$ of the same matrix is true ($y = 0$: $x = 1, z = 0$; $y = 1$: $x = 0, z = 1$).

*Hierarchy theorem applied.* $\mathrm{DTIME}(n^2) \subsetneq \mathrm{DTIME}(n^3)$ because $n^2 \log n^2 = 2 n^2 \log n = o(n^3)$. But the theorem says nothing about $\mathrm{DTIME}(n^2)$ vs $\mathrm{DTIME}(n^2 \log n)$; a finer simulation is needed there.

## Pitfalls

- $\mathrm{PSPACE} = \mathrm{NPSPACE}$ is a theorem; $\mathrm P = \mathrm{NP}$ is open. The difference is that space can be reused and Savitch's recursion re-explores; time cannot be reused.
- Savitch squares the space: $\mathrm{NL} \subseteq \mathrm{SPACE}(\log^2 n)$, not $\mathrm L$. Whether $\mathrm L = \mathrm{NL}$ is open (B03).
- EXPTIME means $2^{\mathrm{poly}(n)}$, not $2^{O(n)}$. Brute force for SAT is $2^n \mathrm{poly}(n) \in \mathrm E \subseteq \mathrm{EXPTIME}$; brute force for TQBF is also $2^n \mathrm{poly}(n)$; both are in PSPACE anyway. EXPTIME-complete problems (succinct circuit versions, generalised chess) need exponential time unconditionally (since $\mathrm P \ne \mathrm{EXPTIME}$).
- The hierarchy theorems need constructible bounds; without them there are gaps (Borodin's gap theorem: some $f$ with $\mathrm{DTIME}(f) = \mathrm{DTIME}(2^f)$).
- The time hierarchy has the $\log$ factor: $\mathrm{DTIME}(n) \subsetneq \mathrm{DTIME}(n \log^2 n)$ follows, $\mathrm{DTIME}(n) \ne \mathrm{DTIME}(n \log n)$ does not follow from the theorem as stated.
- TQBF is NP-hard (SAT is a special case) and coNP-hard, but is not believed to be in NP: a certificate would have to be a strategy tree of exponential size.
- "$\mathrm{PSPACE} \subseteq \mathrm{EXPTIME}$" is proved by counting configurations, not by "polynomial space means the machine can only take polynomially many steps" (it can loop through $2^{\mathrm{poly}}$ configurations).
- The strict inclusions from the hierarchy theorems separate classes four steps apart in the chain; they do not tell you which step is strict.

## Exam-style questions

1. *Prove Savitch's theorem and derive $\mathrm{PSPACE} = \mathrm{NPSPACE}$.* REACH recursion with halving, depth $O(s)$, frame $O(s)$, total $O(s^2)$; $\mathrm{NSPACE}(n^k) \subseteq \mathrm{SPACE}(n^{2k})$.
2. *Show TQBF $\in$ PSPACE and explain why the naive hardness construction fails and how the $\forall$ trick repairs it.* Recursive evaluation in $O(n + |\varphi|)$ space; doubling formula is exponential; the universal quantifier over $(D_1, D_2)$ shares one copy of $\varphi_{k-1}$, giving size $O(p(n)^2)$.
3. *State the time hierarchy theorem and prove $\mathrm P \ne \mathrm{EXPTIME}$.* $f \log f = o(g)$ gives $\mathrm{DTIME}(f) \subsetneq \mathrm{DTIME}(g)$; apply with $f = 2^n$, $g = 2^{n^2}$, and $\mathrm P \subseteq \mathrm{DTIME}(2^n)$.
4. *Where does the $\log f$ factor in the time hierarchy theorem come from, and why is it absent in the space hierarchy theorem?* Universal simulation with a step counter costs $O(t \log t)$ time for $t$ steps; space simulation of a fixed machine costs only a constant factor.
5. *Which of $\mathrm{NL} \subseteq \mathrm P$, $\mathrm P \subseteq \mathrm{NP}$, $\mathrm{NP} \subseteq \mathrm{PSPACE}$ are known to be strict? What is known?* None individually; $\mathrm{NL} \ne \mathrm{PSPACE}$ (Savitch plus space hierarchy) shows at least one is strict.
6. *Why is $\mathrm{PH} \subseteq \mathrm{PSPACE}$, and what would $\mathrm{PH} = \mathrm{PSPACE}$ imply?* Each $\Sigma_k^p$ statement is a bounded-alternation QBF; equality would put TQBF in some $\Sigma_k^p$, and since every $\Sigma_j^p$ problem reduces to TQBF, PH would collapse to level $k$.

## Code

`src/py/complexity/reachability.py`: `savitch_reach(g, u, v, k, trace)` implements the REACH recursion on an explicit graph (the configuration graph of a machine would be generated on the fly); `test_savitch_recursion_depth_is_log` checks that a path of length 15 needs $k = 4$ levels and that $k = 3$ fails. The recursive TQBF evaluator is the same pattern as `decision_tree_depth` in `query_complexity.py` (B06): minimax over a tree, storing only the current path.
