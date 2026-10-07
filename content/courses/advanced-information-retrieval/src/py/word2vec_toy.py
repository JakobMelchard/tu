"""Skip-gram with negative sampling (SGNS) in numpy on a synthetic corpus.

Note 06. Mikolov et al. [S28, S29]; lecture [S9 sl. 12-19].

For a (centre c, context o) pair and K negatives n_1..n_K drawn from the
unigram distribution raised to 3/4, the loss is
$$\\ell=-\\log\\sigma(u_o^\\top v_c)-\\sum_k\\log\\sigma(-u_{n_k}^\\top v_c),$$
with gradients (using $\\sigma'(x)=\\sigma(x)(1-\\sigma(x))$, $\\partial_x\\log\\sigma(x)=1-\\sigma(x)$)
$$\\partial_{v_c}\\ell=(\\sigma(u_o^\\top v_c)-1)u_o+\\sum_k\\sigma(u_{n_k}^\\top v_c)u_{n_k},\\quad
\\partial_{u_o}\\ell=(\\sigma(u_o^\\top v_c)-1)v_c,\\quad \\partial_{u_{n_k}}\\ell=\\sigma(u_{n_k}^\\top v_c)v_c.$$

The corpus is generated from two latent factors, a *role* (royalty, acting,
family, ...) and a *gender*, so that the analogy king - man + woman = queen has
a planted answer: each word's contexts are the union of its role's contexts and
its gender's contexts, which is exactly the additive structure analogies need.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

PAIRS = [("man", "woman"), ("king", "queen"), ("prince", "princess"), ("actor", "actress"),
         ("waiter", "waitress"), ("uncle", "aunt"), ("father", "mother"), ("brother", "sister"),
         ("boy", "girl"), ("husband", "wife"), ("monk", "nun"), ("wizard", "witch")]
ROLE_CTX = [("person", "adult", "human"), ("crown", "throne", "reign"), ("castle", "heir", "royal"),
            ("film", "stage", "role"), ("restaurant", "table", "menu"), ("relative", "visit", "gift"),
            ("parent", "child", "home"), ("sibling", "younger", "older"), ("young", "school", "play"),
            ("marriage", "spouse", "wedding"), ("monastery", "prayer", "vow"), ("magic", "spell", "wand")]
GENDER_CTX = [("he", "his", "him"), ("she", "her", "hers")]
FILLER = ("the", "a", "and", "of", "was", "is")


def make_analogy_corpus(n_sentences: int = 6000, seed: int = 0) -> list[list[str]]:
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_sentences):
        r, g = rng.integers(len(PAIRS)), rng.integers(2)
        toks = [PAIRS[r][g]]
        toks += [ROLE_CTX[r][i] for i in rng.integers(3, size=2)]
        toks += [GENDER_CTX[g][i] for i in rng.integers(3, size=2)]
        toks += [FILLER[i] for i in rng.integers(len(FILLER), size=rng.integers(0, 3))]
        rng.shuffle(toks)
        out.append(toks)
    return out


class Vocab:
    def __init__(self, sentences: list[list[str]], min_count: int = 1):
        cnt = Counter(t for s in sentences for t in s)
        self.itos = sorted((w for w, c in cnt.items() if c >= min_count), key=lambda w: (-cnt[w], w))
        self.stoi = {w: i for i, w in enumerate(self.itos)}
        self.counts = np.array([cnt[w] for w in self.itos], float)

    def __len__(self):
        return len(self.itos)

    def noise(self, power: float = 0.75) -> np.ndarray:
        p = self.counts**power
        return p / p.sum()


def skipgram_pairs(sentences: list[list[str]], vocab: Vocab, window: int = 2) -> np.ndarray:
    """All (centre, context) index pairs with |offset| <= window."""
    pairs = []
    for s in sentences:
        ids = [vocab.stoi[t] for t in s if t in vocab.stoi]
        for i, c in enumerate(ids):
            for j in range(max(0, i - window), min(len(ids), i + window + 1)):
                if j != i:
                    pairs.append((c, ids[j]))
    return np.array(pairs, dtype=np.int64)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def sgns_loss_grads(V: np.ndarray, U: np.ndarray, c: np.ndarray, o: np.ndarray, neg: np.ndarray):
    """Batch loss (mean) and gradients w.r.t. the rows involved.
    V: centre ('input') vectors, U: context ('output') vectors; c, o: (B,), neg: (B, K)."""
    vc, uo, un = V[c], U[o], U[neg]                      # (B,d), (B,d), (B,K,d)
    sp = sigmoid(np.einsum("bd,bd->b", uo, vc))          # sigma(u_o . v_c)
    sn = sigmoid(np.einsum("bkd,bd->bk", un, vc))        # sigma(u_n . v_c)
    loss = -np.log(sp + 1e-12) - np.log(1 - sn + 1e-12).sum(1)
    g_vc = (sp - 1)[:, None] * uo + np.einsum("bk,bkd->bd", sn, un)
    g_uo = (sp - 1)[:, None] * vc
    g_un = sn[:, :, None] * vc[:, None, :]
    return loss.mean(), g_vc, g_uo, g_un


def train_sgns(sentences, dim: int = 16, window: int = 2, k_neg: int = 5, epochs: int = 5,
               lr: float = 0.05, batch: int = 256, seed: int = 0):
    rng = np.random.default_rng(seed)
    vocab = Vocab(sentences)
    pairs = skipgram_pairs(sentences, vocab, window)
    V = (rng.random((len(vocab), dim)) - 0.5) / dim      # word2vec init: small V, zero U
    U = np.zeros((len(vocab), dim))
    noise = vocab.noise()
    steps, step, history = epochs * int(np.ceil(len(pairs) / batch)), 0, []
    for _ in range(epochs):
        perm = rng.permutation(len(pairs))
        for s in range(0, len(pairs), batch):
            b = pairs[perm[s:s + batch]]
            neg = rng.choice(len(vocab), size=(len(b), k_neg), p=noise)
            loss, g_vc, g_uo, g_un = sgns_loss_grads(V, U, b[:, 0], b[:, 1], neg)
            a = lr * (1 - step / steps) + 1e-4           # linear decay, as in word2vec
            np.add.at(V, b[:, 0], -a * g_vc)             # add.at: repeated indices accumulate
            np.add.at(U, b[:, 1], -a * g_uo)
            np.add.at(U, neg.ravel(), -a * g_un.reshape(-1, dim))
            history.append(loss)
            step += 1
    return vocab, V, U, np.array(history)


def normalise(E: np.ndarray) -> np.ndarray:
    return E / np.linalg.norm(E, axis=1, keepdims=True)


def most_similar(E: np.ndarray, vocab: Vocab, word: str, k: int = 5, exclude=()) -> list[tuple[str, float]]:
    En = normalise(E)
    sims = En @ En[vocab.stoi[word]]
    order = [i for i in np.argsort(-sims) if vocab.itos[i] not in {word, *exclude}]
    return [(vocab.itos[i], float(sims[i])) for i in order[:k]]


def analogy(E: np.ndarray, vocab: Vocab, a: str, b: str, c: str) -> str:
    """a : b :: c : ?  answered by argmax cos(x, v_b - v_a + v_c), query words excluded (3CosAdd)."""
    En = normalise(E)
    t = En[vocab.stoi[b]] - En[vocab.stoi[a]] + En[vocab.stoi[c]]
    sims = En @ (t / np.linalg.norm(t))
    for w in (a, b, c):
        sims[vocab.stoi[w]] = -np.inf
    return vocab.itos[int(np.argmax(sims))]


def analogy_accuracy(E: np.ndarray, vocab: Vocab) -> float:
    """Over all ordered pairs of roles (r1, r2): m1 : f1 :: m2 : f2 ?"""
    hits = total = 0
    for m1, f1 in PAIRS:
        for m2, f2 in PAIRS:
            if m1 != m2:
                hits += analogy(E, vocab, m1, f1, m2) == f2
                total += 1
    return hits / total


if __name__ == "__main__":
    sents = make_analogy_corpus()
    vocab, V, U, hist = train_sgns(sents)
    print(f"{len(sents)} sentences, vocabulary {len(vocab)}, loss {hist[:50].mean():.3f} -> {hist[-50:].mean():.3f}")
    print("nearest to 'king':", [(w, round(s, 2)) for w, s in most_similar(V, vocab, "king")])
    print("king - man + woman =", analogy(V, vocab, "man", "woman", "king"))
    print("actor - man + woman =", analogy(V, vocab, "man", "woman", "actor"))
    print(f"analogy accuracy over {len(PAIRS) * (len(PAIRS) - 1)} ordered role pairs: V {analogy_accuracy(V, vocab):.2f}, "
          f"V+U {analogy_accuracy(V + U, vocab):.2f}")
