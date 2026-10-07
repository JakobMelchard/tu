# A01 Asymptotics and recurrences

An *algorithm* is a finite, unambiguous procedure that maps every input of a problem to a correct output. To compare algorithms we need a measure of cost that does not depend on the machine, the compiler or the constants of the day. That measure is the *asymptotic growth of the worst-case running time as a function of the input size*. This note fixes the vocabulary ($O$, $\Omega$, $\Theta$, $o$, $\omega$), explains why "polynomial time" is the working definition of "efficient", and gives the standard tools for solving the recurrences that describe recursive algorithms (substitution, recursion tree, master theorem), plus the idea of amortised analysis. Reference: Kleinberg & Tardos (KT) chapter 2, sections 2.1 to 2.4; recurrences in KT 5.1 to 5.2; amortisation in KT 4.6. References: Kleinberg & Tardos ch. 2 [S25]; the syllabus bullet "Basic running time analysis: O-notation, asymptotic order of growth" [S1, S5] (new in 2025W [S2, S3]). Exam 1 material.

## Definitions

**Input size.** The number of bits (or, more coarsely, the number of "elementary items": integers, vertices, edges) needed to write down the input. We write $n$ for it, or several parameters ($n$ vertices, $m$ edges; $n$ items, weight bound $W$). The choice matters: an integer $W$ takes $\log_2 W$ bits, not $W$ (see A05, pseudo-polynomial).

**Running time.** Count of elementary steps (arithmetic on machine words, comparisons, memory access, pointer following) executed on an input. Each step costs $O(1)$; this is the *word-RAM* model. The **worst-case running time** is
$$T(n) = \max_{\text{inputs } x \text{ of size } n} \text{steps}(x).$$
Worst case is the default because it gives a guarantee and is usually tractable to analyse. Average-case needs a distribution over inputs; amortised (below) is a worst case over *sequences* of operations.

**Big-O family.** Let $f, g : \mathbb{N} \to \mathbb{R}_{\ge 0}$.

- $f = O(g)$ (asymptotic upper bound): $\exists\, c > 0,\ n_0$ such that $f(n) \le c\, g(n)$ for all $n \ge n_0$.
- $f = \Omega(g)$ (asymptotic lower bound): $\exists\, c > 0,\ n_0$ with $f(n) \ge c\, g(n)$ for all $n \ge n_0$.
- $f = \Theta(g)$ (tight bound): $f = O(g)$ and $f = \Omega(g)$; equivalently $c_1 g(n) \le f(n) \le c_2 g(n)$ eventually.
- $f = o(g)$ (strictly smaller): $\forall\, c > 0\ \exists\, n_0 : f(n) \le c\, g(n)$ for $n \ge n_0$; if $g > 0$ eventually, this is $\lim f/g = 0$.
- $f = \omega(g)$ (strictly larger): $\forall\, c > 0\ \exists\, n_0 : f(n) \ge c\, g(n)$; equivalently $g = o(f)$, or $\lim f/g = \infty$.

The notation $f = O(g)$ is really $f \in O(g)$, the set of functions bounded by $g$ up to constants. It is asymmetric: never write $O(g) = f$. The letters are read: "$f$ is at most $g$", "at least $g$", "exactly $g$", "negligible against $g$", "dominates $g$".

**Limit test.** If $L = \lim_{n\to\infty} f(n)/g(n)$ exists in $[0, \infty]$: $L = 0 \Rightarrow f = o(g)$; $0 < L < \infty \Rightarrow f = \Theta(g)$; $L = \infty \Rightarrow f = \omega(g)$. The converse fails: $f(n) = (2 + (-1)^n) n$ is $\Theta(n)$ although the limit does not exist.

**Polynomial time.** An algorithm runs in polynomial time if $T(n) = O(n^d)$ for some constant $d$. The class of problems solvable in polynomial time is $\mathrm{P}$ (see B01).

**Recurrence.** An equation expressing $T(n)$ in terms of $T$ at smaller arguments, e.g. $T(n) = 2T(n/2) + cn$, $T(1) = c$. It arises from a recursive algorithm: $a$ subproblems of size $n/b$ plus $f(n)$ work to split and combine. Floors and ceilings ($T(\lfloor n/2 \rfloor)$) do not change the asymptotic answer for the recurrences in this note; we drop them.

**Amortised cost.** For a sequence of $k$ operations on a data structure, the amortised cost per operation is $(\text{total worst-case cost of the sequence})/k$. Individual operations may be expensive as long as the total stays small.

## Results

### Properties of $O$

1. **Transitivity.** $f = O(g),\ g = O(h) \Rightarrow f = O(h)$. Proof: $f \le c_1 g \le c_1 c_2 h$ for $n \ge \max(n_1, n_2)$. Same for $\Omega, \Theta, o, \omega$.
2. **Sums.** $f_1 = O(g_1),\ f_2 = O(g_2) \Rightarrow f_1 + f_2 = O(g_1 + g_2) = O(\max(g_1, g_2))$. In particular $f = O(g)$ implies $f + g = \Theta(g)$: a lower-order term is absorbed. Proof: $f_1 + f_2 \le c_1 g_1 + c_2 g_2 \le (c_1 + c_2)\max(g_1, g_2)$.
3. **Products.** $f_1 = O(g_1),\ f_2 = O(g_2) \Rightarrow f_1 f_2 = O(g_1 g_2)$, constant $c_1 c_2$.
4. **Constants.** $c f = \Theta(f)$ for constant $c > 0$; $O(1)$ means bounded.
5. **Reflexivity / symmetry.** $f = \Theta(f)$; $f = \Theta(g) \iff g = \Theta(f)$; $f = O(g) \iff g = \Omega(f)$.
6. **Polynomials.** If $p(n) = \sum_{i=0}^d a_i n^i$ with $a_d > 0$, then $p = \Theta(n^d)$. Proof: $p(n) \le (\sum |a_i|) n^d$, and $p(n) \ge a_d n^d - (\sum_{i<d} |a_i|) n^{d-1} \ge \tfrac{1}{2} a_d n^d$ for $n \ge 2 \sum_{i<d}|a_i| / a_d$.

### Growth hierarchy

For constants $a, b > 0$, $\epsilon > 0$, $r > 1$:
$$1 \prec \log\log n \prec \log^a n \prec n^{\epsilon} \prec n \prec n \log n \prec n^{b} \ (b > 1) \prec r^{n} \prec n! \prec n^n,$$
where $f \prec g$ means $f = o(g)$.

- **Logs beat nothing polynomial:** $\log^a n = o(n^{\epsilon})$ for every $a$ and every $\epsilon > 0$. Proof: substitute $n = e^t$; $t^a / e^{\epsilon t} \to 0$ (exponential beats polynomial in $t$, by L'Hôpital $a$ times).
- **Polynomials lose to exponentials:** $n^b = o(r^n)$. Same substitution: $n^b / r^n = e^{b \ln n - n \ln r} \to 0$ since $\ln n = o(n)$.
- **Base of a log does not matter:** $\log_a n = \log_b n / \log_b a = \Theta(\log_b n)$. Base of an exponential does: $2^n = o(3^n)$.
- **$n!$:** Stirling gives $\log(n!) = n \log n - n + O(\log n) = \Theta(n \log n)$; hence $2^n = o(n!)$ and $n! = o(n^n)$.
- $\log n = o(n^{\epsilon})$ is the fact behind "sorting in $O(n \log n)$ is nearly linear".

**Why polynomial time is "efficient" (KT 2.1).** (i) Closure: composing polynomial-time steps (calling a polynomial-time subroutine polynomially many times) stays polynomial, because $n^{a} \cdot (n^{b})^{c}$ is a polynomial. (ii) Robustness: reasonable machine models (Turing machine, word-RAM, your laptop) simulate each other with polynomial overhead, so the class does not depend on the model. (iii) Scaling: doubling $n$ multiplies an $n^d$ time by $2^d$, whereas $2^n$ time squares. In practice a $2^n$ algorithm dies around $n \approx 40$–$60$; $n^3$ handles $n \approx 10^4$; $n \log n$ handles $10^8$. The definition is a convention, and $n^{100}$ is polynomial but useless; empirically, natural problems in P tend to have low-degree algorithms.

### Common running times (KT 2.4)

| Time | Typical source |
|---|---|
| $O(1)$ | array access, hash lookup |
| $O(\log n)$ | binary search, halving loops |
| $O(n)$ | one pass, BFS/DFS on $O(n)$ edges, merging two sorted lists |
| $O(n \log n)$ | sorting (merge sort), divide and conquer with linear merge |
| $O(n^2)$ | all pairs, nested loops, insertion sort |
| $O(n^3)$ | Floyd–Warshall (A05), naive matrix multiplication |
| $O(n^k)$ | enumerating $k$-subsets |
| $O(2^n)$ | enumerating all subsets |
| $O(n!)$ | enumerating all permutations |

### Solving recurrences

**Method 1: unrolling / substitution (guess and verify by induction).** Guess $T(n) \le c\, g(n)$, plug into the recurrence, check the inductive step, then choose $c$ large enough for the base.

Example $T(n) = 2T(n/2) + n$, $T(1) = 1$. Guess $T(n) \le c\, n \log_2 n$ for $n \ge 2$. Step: $T(n) \le 2 c (n/2) \log_2(n/2) + n = c n \log_2 n - c n + n \le c n \log_2 n$ for $c \ge 1$. Base $T(2) = 3 \le 2c$ with $c \ge 3/2$. So $T(n) = O(n \log n)$; the matching $\Omega$ follows from the same computation with $\ge$.

A trap: guessing $T(n) \le cn$ for the same recurrence gives $T(n) \le cn + n$, which is *not* $\le cn$; the induction fails, and correctly so, because $T(n) = \Theta(n \log n)$.

**Method 2: recursion tree.** Draw the tree of recursive calls. Level $i$ has $a^i$ nodes each of size $n/b^i$, contributing $a^i f(n/b^i)$. Depth is $\log_b n$. Sum the levels.

**Method 3: master theorem.** Let $a \ge 1$, $b > 1$, $f(n) \ge 0$, and
$$T(n) = a\,T(n/b) + f(n).$$
Define the *critical exponent* $d^* = \log_b a$, so that $n^{d^*}$ is the number of leaves of the recursion tree. Then:

1. If $f(n) = O(n^{d^* - \epsilon})$ for some $\epsilon > 0$: $T(n) = \Theta(n^{\log_b a})$. (Leaves dominate.)
2. If $f(n) = \Theta(n^{d^*})$: $T(n) = \Theta(n^{\log_b a} \log n)$. (All levels equal.)
3. If $f(n) = \Omega(n^{d^* + \epsilon})$ for some $\epsilon > 0$ **and** the regularity condition $a f(n/b) \le \kappa f(n)$ holds for some constant $\kappa < 1$ and large $n$: $T(n) = \Theta(f(n))$. (Root dominates.)

*Proof sketch via the recursion tree.* Level $i$ costs $a^i f(n/b^i)$ for $i = 0, \ldots, L = \log_b n$; the leaf level costs $a^{L} T(1) = \Theta(n^{\log_b a})$. So
$$T(n) = \Theta(n^{\log_b a}) + \sum_{i=0}^{L-1} a^i f(n/b^i).$$
Case 1: $a^i f(n/b^i) \le c\, a^i (n/b^i)^{d^* - \epsilon} = c\, n^{d^* - \epsilon} (a b^{\epsilon} / b^{d^*})^i = c\, n^{d^* - \epsilon} (b^{\epsilon})^i$ since $b^{d^*} = a$. The geometric sum is dominated by its last term $i = L$: $n^{d^* - \epsilon} b^{\epsilon L} = n^{d^* - \epsilon} n^{\epsilon} = n^{d^*}$. So the sum is $O(n^{d^*})$, and the leaves give $\Theta(n^{d^*})$. Case 2: each level costs $\Theta(a^i (n/b^i)^{d^*}) = \Theta(n^{d^*})$; there are $\Theta(\log n)$ levels. Case 3: regularity gives $a^i f(n/b^i) \le \kappa^i f(n)$, a decreasing geometric series bounded by $f(n)/(1-\kappa)$; the root term $f(n)$ is also a lower bound. The regularity condition is what makes the series geometric; for polynomial $f(n) = n^d$ with $d > d^*$ it holds automatically with $\kappa = a/b^d < 1$. It can fail for pathological $f$ (e.g. oscillating), and then case 3 is not applicable.

*Gaps.* If $f$ is bigger than $n^{d^*}$ but not polynomially bigger (e.g. $f = n^{d^*} \log n$), no case applies; use the recursion tree directly (example below).

**Extended form (KT-style).** For $T(n) = a T(n/b) + O(n^d)$: $T(n) = O(n^d)$ if $d > \log_b a$, $O(n^d \log n)$ if $d = \log_b a$, $O(n^{\log_b a})$ if $d < \log_b a$. This is the three cases specialised to polynomial $f$, the form that appears in most exams.

### Examples

- $T(n) = 2T(n/2) + n$ (merge sort, counting inversions, A04): $a = 2, b = 2, d^* = 1, f = n = \Theta(n^1)$, case 2: $\Theta(n \log n)$.
- $T(n) = T(n/2) + 1$ (binary search): $a = 1, b = 2, d^* = 0$, $f = 1 = \Theta(n^0)$, case 2: $\Theta(\log n)$.
- $T(n) = 7T(n/2) + n^2$ (Strassen, A04): $d^* = \log_2 7 \approx 2.807 > 2$, case 1: $\Theta(n^{\log_2 7})$.
- $T(n) = 8T(n/2) + n^2$ (naive block matrix multiplication): $d^* = 3$, case 1: $\Theta(n^3)$.
- $T(n) = 3T(n/2) + n$ (Karatsuba, A04): $d^* = \log_2 3 \approx 1.585 > 1$, case 1: $\Theta(n^{1.585})$.
- $T(n) = 4T(n/2) + n$ (naive 4-multiplication recursion): $d^* = 2$, case 1: $\Theta(n^2)$; no gain over the schoolbook method.
- $T(n) = 2T(n/2) + n^2$: $d^* = 1 < 2$, regularity $2 (n/2)^2 = n^2/2 \le \kappa n^2$ with $\kappa = 1/2$, case 3: $\Theta(n^2)$.
- $T(n) = T(n-1) + n$ (selection sort, no halving): not master-theorem form; unroll: $\sum_{k=1}^{n} k = \Theta(n^2)$.
- $T(n) = 2T(n/2) + n \log n$: $f = n \log n$ is between $n^{1}$ and $n^{1 + \epsilon}$, no case applies. Recursion tree: level $i$ has $2^i$ nodes of size $n/2^i$, cost $2^i (n/2^i) \log(n/2^i) = n (\log n - i)$. Sum over $i = 0..\log n$: $n \sum_{i=0}^{\log n} (\log n - i) = n \cdot \Theta(\log^2 n)$. So $T(n) = \Theta(n \log^2 n)$.

### Amortised analysis (KT 4.6, aggregate method)

**Binary counter.** Incrementing an $n$-bit counter flips $k+1$ bits when the low $k$ bits are $1$s; worst case $n$ flips. But over $k$ increments from zero, bit $j$ flips $\lfloor k/2^j \rfloor$ times, so total flips $\le k \sum_j 2^{-j} < 2k$: amortised $O(1)$ per increment.

**Dynamic array.** Doubling capacity when full costs $O(n)$ at a resize but $O(1)$ amortised per append: total copies over $n$ appends are $1 + 2 + 4 + \cdots + n < 2n$.

**Union-find** (A03): with union by rank and path compression, any sequence of $m$ operations on $n$ elements costs $O(m\, \alpha(n))$ where $\alpha$ is the inverse Ackermann function, $\alpha(n) \le 4$ for every $n$ smaller than the number of atoms in the universe. Practically $O(1)$ amortised; a single find may still take $O(\log n)$.

## Worked example

Solve $T(n) = 3T(n/4) + n \log n$ (arbitrary instance of case 3).

$a = 3$, $b = 4$, $d^* = \log_4 3 \approx 0.79$. $f(n) = n \log n = \Omega(n^{0.79 + 0.2})$, so polynomially larger. Regularity: $a f(n/b) = 3 (n/4) \log(n/4) \le \tfrac{3}{4} n \log n$, so $\kappa = 3/4$. Case 3: $T(n) = \Theta(n \log n)$.

Check with the recursion tree: level $i$ costs $3^i (n/4^i) \log(n/4^i) \le (3/4)^i n \log n$; the sum is $\le n \log n / (1 - 3/4) = 4 n \log n$. Leaves: $3^{\log_4 n} = n^{\log_4 3} = o(n \log n)$. Consistent.

Numerically, $T(1) = 1$, $n = 16$: $T(4) = 3 T(1) + 4 \cdot 2 = 11$; $T(16) = 3 \cdot 11 + 16 \cdot 4 = 97$; $4 \cdot 16 \cdot 4 = 256 \ge 97$, within the bound.

Now compare orders: which is bigger, $n^{\log_4 3}$ or $\sqrt{n}$? $\log_4 3 = \ln 3 / \ln 4 \approx 0.792 > 0.5$, so $\sqrt{n} = o(n^{\log_4 3})$. And $\log_2 n$ versus $n^{0.01}$: the log loses, $\log n = o(n^{0.01})$, but only past $n \approx 10^{300}$; asymptotics say nothing about small $n$.

## Pitfalls

- $O$ is an upper bound, not a tight one: "$T(n) = O(n^2)$" is true for merge sort. Say $\Theta$ when you mean tight. "Algorithm A is $O(n^2)$ and B is $O(n \log n)$, so B is faster" is invalid without lower bounds.
- $O(g)$ describes the *function* $T$, not the algorithm's best case. Worst-case $\Omega(n \log n)$ does not mean every input costs that much.
- Master theorem needs $f$ *polynomially* separated from $n^{\log_b a}$; $n \log n$ vs $n$ is not polynomial separation (case 2 does not apply either: $n \log n \ne \Theta(n)$).
- $\log_b a$, not $\log_a b$; $T(n) = 7T(n/2) + n^2$ has exponent $\log_2 7$.
- $2^{2n} = 4^n \ne O(2^n)$; $\log(n!) = \Theta(n \log n)$, not $\Theta(n)$; $(\log n)^2 \ne \log n^2 = 2 \log n$.
- Input size is in bits: an algorithm that loops $W$ times where $W$ is an input number is exponential in the input size $\log W$ (A05).
- The regularity condition is part of case 3; if you cite the theorem in a proof, state it.
- $f = O(g)$ and $g = O(f)$ both false is possible: $f = n$, $g = n^{1 + \sin n}$ oscillates; $O$ is a partial, not total, order.

## Exam-style questions

1. **State the definition of $f = O(g)$ and prove that $3n^2 + 100n + 7 = O(n^2)$.** For $n \ge 1$: $3n^2 + 100 n + 7 \le 3n^2 + 100 n^2 + 7 n^2 = 110 n^2$; take $c = 110$, $n_0 = 1$.

2. **Order by growth: $n \log n$, $2^{\sqrt{n}}$, $n^{1.5}$, $(\log n)^{10}$, $2^n$, $n!$.** $(\log n)^{10} \prec n \log n \prec n^{1.5} \prec 2^{\sqrt{n}} \prec 2^n \prec n!$. Justification for the middle: $\log(2^{\sqrt n}) = \sqrt{n} = \omega(1.5 \log n) = \omega(\log n^{1.5})$; and $\sqrt{n} = o(n)$.

3. **Solve $T(n) = 4T(n/2) + n^2$ and $T(n) = 4T(n/2) + n^3$.** Both have $d^* = 2$. First: case 2, $\Theta(n^2 \log n)$. Second: $n^3 = \Omega(n^{2+1})$, regularity $4 (n/2)^3 = n^3/2$, case 3, $\Theta(n^3)$.

4. **Why is the running time of a recursive algorithm with recurrence $T(n) = 2T(n-1) + 1$ not polynomial?** Unrolling gives $T(n) = 2^n T(0) + 2^n - 1 = \Theta(2^n)$: each level doubles the number of calls but reduces size by only 1, so the tree has depth $n$ and $2^n$ leaves. Halving ($T(n/2)$) gives depth $\log n$ instead; that difference is the whole point of divide and conquer.

5. **Explain in one paragraph what "amortised $O(1)$" means and why a dynamic array satisfies it.** Over any sequence of $k$ appends starting from empty, the total work is $O(k)$, even though single appends that trigger a resize cost $\Theta(\text{current size})$. Resizes happen at sizes $1, 2, 4, \ldots$ and copy $1 + 2 + \cdots + 2^{\lfloor \log k \rfloor} < 2k$ elements in total; the other appends cost $O(1)$ each.

## Code

`src/py/algorithmics/divide_conquer.py`: `master_theorem(a, b, d)` returns the case and the asymptotic order for $T(n) = aT(n/b) + \Theta(n^d)$; `merge_sort` is the running instance of $T(n) = 2T(n/2) + n$ and the tests time it against $n \log n$. Amortised union-find is `UnionFind` in `src/py/algorithmics/greedy.py`.
