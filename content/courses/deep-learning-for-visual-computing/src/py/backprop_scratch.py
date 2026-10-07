"""Backpropagation from scratch in numpy: a scalar computational graph, a 2-layer MLP,
and a 2-D convolution and max pool with their backward passes.

Note 03 (feedforward nets and backprop), note 04 (conv layer backward). Derivations in
the note; gradients are checked against torch.autograd and central differences in
test_backprop_scratch.py [S11 ch. 6.5].
"""
import numpy as np


# ---------------------------------------------------------------- scalar graph (exam style)
class Node:
    """A node of a scalar computational graph: op in {'input', 'add', 'mul', 'max'}."""

    def __init__(self, op, *parents, value=None, name=""):
        self.op, self.parents, self.value, self.name = op, parents, value, name
        self.grad = 0.0            # "cached" d(top)/d(this node)
        self.local = []            # local gradient d(this)/d(parent), one per parent

    def forward(self):
        if self.op == "input":
            return self.value
        v = [p.forward() for p in self.parents]
        if self.op == "add":
            self.value, self.local = v[0] + v[1], [1.0, 1.0]
        elif self.op == "mul":
            self.value, self.local = v[0] * v[1], [v[1], v[0]]          # swap the inputs
        elif self.op == "max":
            self.value = max(v)
            self.local = [1.0, 0.0] if v[0] >= v[1] else [0.0, 1.0]     # route to the winner
        return self.value


def backward(top):
    """Reverse-mode sweep. Accumulates d(top)/d(node) into node.grad for every node.

    Topological order by DFS; each node pushes grad * local gradient to its parents
    (the sum over paths of the multivariate chain rule, computed once per edge).
    """
    order, seen = [], set()

    def visit(n):
        if id(n) not in seen:
            seen.add(id(n))
            for p in n.parents:
                visit(p)
            order.append(n)
    visit(top)
    for n in order:
        n.grad = 0.0
    top.grad = 1.0
    for n in reversed(order):
        for p, lg in zip(n.parents, n.local):
            p.grad += n.grad * lg
    return order


def exam_graph(x1, x2, x3, x4):
    """f = (x1 * x2 + x3) * max(x2, x4): all three gate types, x2 used twice. (ours)"""
    a = [Node("input", value=float(v), name=f"x{i + 1}") for i, v in enumerate((x1, x2, x3, x4))]
    m = Node("mul", a[0], a[1], name="m")
    s = Node("add", m, a[2], name="s")
    mx = Node("max", a[1], a[3], name="mx")
    f = Node("mul", s, mx, name="f")
    f.forward()
    backward(f)
    return f, a


# ---------------------------------------------------------------- 2-layer MLP
def init_mlp(d_in, d_hidden, n_classes, rng):
    """He initialisation for the ReLU layer, Xavier-like for the output layer [S19]."""
    return {"W1": rng.normal(0, np.sqrt(2 / d_in), (d_in, d_hidden)), "b1": np.zeros(d_hidden),
            "W2": rng.normal(0, np.sqrt(1 / d_hidden), (d_hidden, n_classes)), "b2": np.zeros(n_classes)}


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)           # shift for stability; softmax is shift-invariant
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def mlp_forward(P, X):
    z1 = X @ P["W1"] + P["b1"]
    h = np.maximum(z1, 0)
    z2 = h @ P["W2"] + P["b2"]
    return z2, (X, z1, h)


def mlp_loss_and_grads(P, X, y):
    """Mean cross-entropy and its gradients. With p = softmax(z2), Y one-hot, n rows:
    dL/dz2 = (p - Y)/n;  dW2 = h^T dz2;  db2 = sum dz2;  dh = dz2 W2^T;
    dz1 = dh * 1[z1 > 0];  dW1 = X^T dz1;  db1 = sum dz1."""
    z2, (X, z1, h) = mlp_forward(P, X)
    n = X.shape[0]
    p = softmax(z2)
    loss = -np.log(p[np.arange(n), y]).mean()
    dz2 = p.copy()
    dz2[np.arange(n), y] -= 1
    dz2 /= n
    dh = dz2 @ P["W2"].T
    dz1 = dh * (z1 > 0)
    grads = {"W2": h.T @ dz2, "b2": dz2.sum(0), "W1": X.T @ dz1, "b1": dz1.sum(0)}
    return loss, grads


def train_mlp(X, y, d_hidden=32, lr=0.5, steps=300, seed=0):
    rng = np.random.default_rng(seed)
    P = init_mlp(X.shape[1], d_hidden, int(y.max()) + 1, rng)
    losses = []
    for _ in range(steps):
        loss, g = mlp_loss_and_grads(P, X, y)
        for k in P:
            P[k] -= lr * g[k]
        losses.append(loss)
    return P, losses


# ---------------------------------------------------------------- convolution
def conv2d_forward(x, w, b, stride=1, pad=0):
    """Cross-correlation, x [N,C,H,W], w [F,C,k,k], b [F] -> y [N,F,Ho,Wo] (im2col-free loops
    over kernel offsets: each offset is one strided slice times a C x F matrix)."""
    N, C, H, W = x.shape
    F, _, k, _ = w.shape
    xp = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)))
    Ho, Wo = (H + 2 * pad - k) // stride + 1, (W + 2 * pad - k) // stride + 1
    y = np.zeros((N, F, Ho, Wo)) + b[None, :, None, None]
    for u in range(k):
        for v in range(k):
            patch = xp[:, :, u:u + stride * Ho:stride, v:v + stride * Wo:stride]   # [N,C,Ho,Wo]
            y += np.einsum("nchw,fc->nfhw", patch, w[:, :, u, v])
    return y, (x, w, stride, pad)


def conv2d_backward(dy, cache):
    """dL/dx, dL/dw, dL/db for conv2d_forward. For each kernel offset (u, v):
    dw[:, :, u, v] = sum_{n,h,w} dy[n,f,h,w] x_pad[n,c,u+s h, v+s w]   (correlate input with dy)
    dx_pad[n,c,u+s h, v+s w] += sum_f dy[n,f,h,w] w[f,c,u,v]           (scatter dy back = transposed conv)
    db = sum over n, h, w of dy."""
    x, w, s, pad = cache
    N, C, H, W = x.shape
    F, _, k, _ = w.shape
    Ho, Wo = dy.shape[2], dy.shape[3]
    xp = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)))
    dxp = np.zeros_like(xp)
    dw = np.zeros_like(w)
    for u in range(k):
        for v in range(k):
            patch = xp[:, :, u:u + s * Ho:s, v:v + s * Wo:s]
            dw[:, :, u, v] = np.einsum("nfhw,nchw->fc", dy, patch)
            dxp[:, :, u:u + s * Ho:s, v:v + s * Wo:s] += np.einsum("nfhw,fc->nchw", dy, w[:, :, u, v])
    dx = dxp[:, :, pad:pad + H, pad:pad + W]
    return dx, dw, dy.sum(axis=(0, 2, 3))


def maxpool_forward(x, k=2):
    """Non-overlapping k x k max pool (H, W divisible by k)."""
    N, C, H, W = x.shape
    xr = x.reshape(N, C, H // k, k, W // k, k)
    y = xr.max(axis=(3, 5))
    return y, (x, k)


def maxpool_backward(dy, cache):
    """Route each output gradient to the argmax of its window (ties: first max only)."""
    x, k = cache
    N, C, H, W = x.shape
    xr = x.reshape(N, C, H // k, k, W // k, k).transpose(0, 1, 2, 4, 3, 5).reshape(N, C, H // k, W // k, k * k)
    idx = xr.argmax(-1)
    mask = np.zeros_like(xr)
    np.put_along_axis(mask, idx[..., None], 1.0, axis=-1)
    dx = mask * dy[..., None]
    return dx.reshape(N, C, H // k, W // k, k, k).transpose(0, 1, 2, 4, 3, 5).reshape(N, C, H, W)


def numerical_grad(f, x, eps=1e-6):
    """Central differences, O(eps^2) truncation error."""
    g = np.zeros_like(x)
    it = np.nditer(x, flags=["multi_index"])
    for _ in it:
        i = it.multi_index
        old = x[i]
        x[i] = old + eps
        fp = f()
        x[i] = old - eps
        fm = f()
        x[i] = old
        g[i] = (fp - fm) / (2 * eps)
    return g


if __name__ == "__main__":
    f, xs = exam_graph(3, 4, 5, 6)     # digits "3456" inserted right to left, as in [S6, S9]
    print(f"f = (x1*x2 + x3) * max(x2, x4) at (3, 4, 5, 6): f = {f.value}")
    print("  df/dx:", {n.name: n.grad for n in xs})
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 2))
    y = (X[:, 0] * X[:, 1] > 0).astype(int)                     # XOR: not linearly separable
    P, losses = train_mlp(X, y)
    acc = (mlp_forward(P, X)[0].argmax(1) == y).mean()
    print(f"2-layer MLP on XOR: loss {losses[0]:.3f} -> {losses[-1]:.3f}, train acc {acc:.2f}")
    x = rng.normal(size=(1, 2, 5, 5))
    w = rng.normal(size=(3, 2, 3, 3))
    yv, cache = conv2d_forward(x, w, np.zeros(3), stride=2, pad=1)
    dx, dw, db = conv2d_backward(np.ones_like(yv), cache)
    print("conv 2x5x5 -> 3 maps, k3 s2 p1: out", yv.shape[1:], "dx", dx.shape[1:], "dw", dw.shape)
