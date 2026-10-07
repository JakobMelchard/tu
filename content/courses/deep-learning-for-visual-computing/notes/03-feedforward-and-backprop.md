# 03 Feedforward networks and backpropagation

> TISS item 3 [S1, S3]. Catalogue weight: MLP definition and sketch, activation
> functions, backprop steps and gate patterns in every edition; **the hand
> backprop on a graph filled with your Matrikelnummer** in 2017 and SS21
> [S6, S9]. Books: Goodfellow ch. 6 (§6.5 backprop) [S11]; Drori ch. 2 [S12].
> Background already written: [ADL 01, backprop as reverse-mode AD](../../applied-deep-learning/notes/01-training-fundamentals.md),
> [ML 11 neural networks](../../machine-learning/notes/11-neural-networks.md).
> New here: the matrix derivation in the course's two-layer form and the
> convolution backward pass.

## Definitions

**Feedforward network.** A directed acyclic graph of units; information flows
input to output, no cycles. Input units hold $x$; hidden units compute
$h = g(w^\top a + b)$ from the previous layer's activations $a$; output units
produce scores. **MLP**: fully connected layers, $a^{(l)} = g(W^{(l)} a^{(l-1)} + b^{(l)})$.
A unit is a linear function followed by a fixed non-linearity; without $g$
the whole stack collapses to one linear map.

**Activation functions.** sigmoid $\sigma(z) = 1/(1+e^{-z})$,
$\sigma' = \sigma(1-\sigma) \le 1/4$; tanh, $\tanh' = 1-\tanh^2 \le 1$;
**ReLU** $\max(0,z)$, derivative $1[z>0]$; leaky ReLU $\max(\alpha z, z)$;
GELU $z\Phi(z)$. ReLU is the default for vision [S7, S15]: no saturation for
$z > 0$ (gradient 1, so products over depth do not vanish), cheap, sparse
activations. Dead units ($z < 0$ for all inputs) are its failure mode.

**Computational graph.** Nodes are operations, edges carry values. The
derivative of the output $f$ with respect to a node is the sum over all
paths of the product of local derivatives (multivariate chain rule).

**Backpropagation** = reverse-mode differentiation of that graph. Forward
pass: compute and cache every node value. Backward pass, in reverse
topological order, at every node $n$ with upstream gradient
$\bar n = \partial f/\partial n$: multiply by the local gradient of each input
edge and **add** into that input's $\bar{\cdot}$. Each edge is visited once,
so the full gradient costs a small constant times one forward pass. The
"naive" alternatives [S7, S8]: expanding the chain rule per parameter and per
path (repeats shared sub-products; exponential in depth for branching graphs),
or finite differences ($2P$ forward passes for $P$ parameters, plus
truncation error).

**Gate patterns** [S7, S8]:

| gate | forward | backward to the inputs |
|---|---|---|
| $x + y$ | sum | **distributes** $\bar f$ unchanged to both |
| $x \cdot y$ | product | **swaps**: $\bar x = y\bar f$, $\bar y = x\bar f$ |
| $\max(x, y)$ | max | **routes** $\bar f$ to the larger input, 0 to the other |
| fan-out (a value used twice) | copy | **sums** the two upstream gradients |

## Derivation: two-layer MLP with softmax cross-entropy

Batch rows, $X \in \mathbb R^{n\times d}$, one-hot $Y \in \mathbb R^{n\times K}$:
$$ Z_1 = XW_1 + \mathbf 1 b_1^\top,\quad H = \mathrm{ReLU}(Z_1),\quad
   Z_2 = HW_2 + \mathbf 1 b_2^\top,\quad P = \mathrm{softmax}(Z_2),\quad
   L = -\tfrac1n \textstyle\sum_{ik} Y_{ik}\log P_{ik}. $$
Backward, each step one local derivative (shapes force the transposes):
$$ \bar Z_2 = \tfrac1n(P - Y),\quad \bar W_2 = H^\top \bar Z_2,\quad
   \bar b_2 = \bar Z_2^\top\mathbf 1,\quad \bar H = \bar Z_2 W_2^\top, $$
$$ \bar Z_1 = \bar H \odot 1[Z_1 > 0],\quad \bar W_1 = X^\top \bar Z_1,\quad
   \bar b_1 = \bar Z_1^\top \mathbf 1. $$
The first line uses $\partial L/\partial z = p - u$ (note 02). A linear layer
$Z = AW$ always gives $\bar W = A^\top \bar Z$ and $\bar A = \bar Z W^\top$;
an elementwise $g$ gives $\bar Z = \bar A \odot g'(Z)$. That is all of MLP
backprop.

## Derivation: convolution layer backward

Forward (correlation, stride $s$, padded input $x$, $F$ filters, $C$ channels):
$$ y[f,i,j] = b_f + \sum_{c,u,v} w[f,c,u,v]\; x[c,\, si+u,\, sj+v]. $$
With $\delta = \partial L/\partial y$, differentiate the sum term by term:
$$ \frac{\partial L}{\partial w[f,c,u,v]} = \sum_{i,j}\delta[f,i,j]\,x[c,si+u,sj+v]
   \quad\text{(correlate the input with } \delta\text{)}, $$
$$ \frac{\partial L}{\partial x[c,p,q]} = \sum_{f}\sum_{\substack{i,j,u,v:\\ si+u=p,\ sj+v=q}}\delta[f,i,j]\,w[f,c,u,v]
   \quad\text{(scatter } \delta \text{ back through } w\text{)}, \qquad
   \frac{\partial L}{\partial b_f} = \sum_{i,j}\delta[f,i,j]. $$
For $s = 1$ the input gradient is a *full* convolution of $\delta$ with $w$,
i.e. a correlation of the zero-padded $\delta$ with the flipped kernel. For
general $s$ it is exactly the **transposed convolution** with the same
$k, s, p$: the linear adjoint of the forward map, which is why transposed
convolution is the upsampling layer of decoders (notes 04, 05). Weight sharing
shows up as the sum over positions $(i,j)$ in $\partial L/\partial w$. A max
pool routes each $\delta$ to its window's argmax.

## Worked examples

**Graph by hand** (the Matrikelnummer format, our graph). Digits 3456 go right
to left into $x_4, x_3, x_2, x_1$: $x = (3, 4, 5, 6)$ and
$f = (x_1x_2 + x_3)\max(x_2, x_4)$.
Forward: $m = 12$, $s = 17$, $\max = 6$, $f = 102$.
Backward: $\bar f = 1$; product node: $\bar s = 6$, $\overline{\max} = 17$;
sum: $\bar m = 6$, $\bar x_3 = 6$; product: $\bar x_1 = x_2\bar m = 24$,
$\bar x_2 \mathrel{+}= x_1\bar m = 18$; max routes to $x_4 = 6 > 4$:
$\bar x_4 = 17$, nothing more to $x_2$. Result $\nabla f = (24, 18, 6, 17)$.

**1-D convolution backward.** $x = (1,2,3,4)$, $w = (1,-1)$, valid
correlation $y = (x_0 - x_1, x_1 - x_2, x_2 - x_3) = (-1,-1,-1)$. Upstream
$\delta = (1, 0, 2)$. $\bar w_0 = \sum_i \delta_i x_i = 7$,
$\bar w_1 = \sum_i \delta_i x_{i+1} = 10$; $\bar x = (\delta_0 w_0,\ \delta_1 w_0 + \delta_0 w_1,\
\delta_2 w_0 + \delta_1 w_1,\ \delta_2 w_1) = (1, -1, 2, -2)$. Check by
linearity: $L = \delta^\top y = (x_0 - x_1) + 2(x_2 - x_3)$.

## Pitfalls

- Overwriting instead of accumulating gradients at a fan-out (the $x_2$ above).
- Taking the max gate's gradient to both inputs.
- Forgetting the $1/n$ of a mean loss in $\bar Z_2$, or the ReLU mask in $\bar Z_1$.
- "Dropped units / ReLU zeros still receive gradient": they do not; the mask is 0.
- Believing the input gradient of a strided conv is a strided conv: it is the transposed conv.
- Stating that a single hidden layer "cannot extract high-level features" (it
  can approximate anything, but needs exponentially many units where depth
  composes features; the catalogue's point is parameter efficiency and
  locality, note 04).

## Exam-style questions

1. **Define a feedforward network and an MLP; what does a hidden unit compute?**
   *(17, 20, 22)* A DAG of units; an MLP is fully connected layers;
   $h = g(w^\top a + b)$, an affine map followed by a non-linearity.
2. **Draw an MLP for binary classification of 3-D inputs with one hidden layer
   of four units; count parameters.** *(22)* $3\to4\to1$ (sigmoid output) or
   $\to 2$ (softmax): $3\cdot4 + 4 + 4\cdot1 + 1 = 21$ (or 26 with two outputs).
3. **Purpose of backprop, difference to the naive algorithm, steps at a node,
   and the gradient patterns of $+$, $\cdot$, $\max$.** *(20, 22)* See the
   definitions and table: one reverse sweep reusing cached values, cost of the
   order of one forward pass, versus per-parameter recomputation.
4. **Compute all partial derivatives of $f = (x_1x_2 + x_3)\max(x_2,x_4)$ at
   $(3,4,5,6)$ and mark values and local gradients.** *(format of 17, 21)*
   $(24, 18, 6, 17)$ as worked above; `exam_graph(3, 4, 5, 6)` prints it.
5. **Derive $\partial L/\partial w$ and $\partial L/\partial x$ for a stride-1
   convolution; why does a conv layer's gradient involve a sum over
   positions?** *(ours)* As derived: correlation of input with $\delta$ for the
   weights, full convolution of $\delta$ with $w$ for the input; the same
   weight is used at every position (sharing), so its gradient sums the
   contributions of all positions.

## Code

- `src/py/backprop_scratch.py`: `Node`, `backward`, `exam_graph` (the graph
  above), `init_mlp`, `mlp_forward`, `mlp_loss_and_grads` (the derivation
  line by line), `train_mlp`, `numerical_grad`, `conv2d_forward`,
  `conv2d_backward`, `maxpool_forward`, `maxpool_backward`.
- Tests: every gradient against `torch.autograd` and central differences; the
  input gradient of a stride-2 conv equals `F.conv_transpose2d`.
