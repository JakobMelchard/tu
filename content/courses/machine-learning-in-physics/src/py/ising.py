"""2D Ising model: Metropolis data, order parameter, Binder cumulant, PCA and classifiers.

Note 10 (exercise domain "recognising magnetic phases in the Ising model").
  H = -J sum_<ij> s_i s_j, J = 1, k_B = 1, periodic L x L lattice [S20].
  Onsager: T_c = 2 / ln(1 + sqrt 2) = 2.26919 [S18].
  Metropolis, checkerboard: sites of one colour have no neighbours of the same colour,
  so all of them can be updated at once; accept a flip with min(1, exp(-beta dE)),
  dE = 2 s_i h_i, h_i = sum of the four neighbours.
  Binder cumulant U_L = 1 - <m^4> / (3 <m^2>^2): 2/3 in the ordered phase, 0 for a
  Gaussian m (disordered), curves for different L cross near T_c [S19].
  Unsupervised: PC1 of the configurations is the uniform vector, its score is L^2 m / L
  up to sign [S16]. Supervised: train ordered (T < 2) vs disordered (T > 2.5), skip the
  critical region, read T_c off where p(ordered) = 1/2 [S15, S6 sec. VII.C.1].
Mehta et al.'s dataset is 16 temperatures x 10^4 samples at L = 40 [S6 app. A]; the
defaults here are smaller (L = 16) so the tests run in seconds.
"""
from __future__ import annotations

import numpy as np

TC = 2.0 / np.log(1.0 + np.sqrt(2.0))


def neighbour_sum(S):
    return (np.roll(S, 1, -1) + np.roll(S, -1, -1) + np.roll(S, 1, -2) + np.roll(S, -1, -2))


def energy_per_site(S):
    """E/N for a batch (..., L, L): each bond counted once via right and down neighbours."""
    e = -(S * np.roll(S, -1, -1) + S * np.roll(S, -1, -2)).sum((-1, -2))
    return e / (S.shape[-1] * S.shape[-2])


def magnetisation(S):
    return S.mean((-1, -2))


def metropolis(L, temps, n_samples=25, chains=8, n_therm=500, n_between=10, seed=0,
               start="cold"):
    """Returns spins (n_T, chains * n_samples, L, L) as int8, one row block per T."""
    rng = np.random.default_rng(seed)
    temps = np.asarray(temps, float)
    C = temps.size * chains
    beta = np.repeat(1.0 / temps, chains)[:, None, None]
    S = np.ones((C, L, L)) if start == "cold" else rng.choice([-1.0, 1.0], size=(C, L, L))
    ii, jj = np.indices((L, L))
    masks = [((ii + jj) % 2 == c) for c in (0, 1)]

    def sweep():
        for m in masks:
            dE = 2.0 * S * neighbour_sum(S)
            flip = (rng.random(S.shape) < np.exp(-beta * dE)) & m
            S[flip] *= -1.0

    for _ in range(n_therm):
        sweep()
    out = np.empty((n_samples, C, L, L), dtype=np.int8)
    for k in range(n_samples):
        for _ in range(n_between):
            sweep()
        out[k] = S
    # (n_samples, T*chains, L, L) -> (T, chains * n_samples, L, L)
    out = out.reshape(n_samples, temps.size, chains, L, L).transpose(1, 2, 0, 3, 4)
    return out.reshape(temps.size, chains * n_samples, L, L)


def exact_small(L, T):
    """Exact <E>/N, <|m|>, <m^2> by enumerating all 2^(L^2) states (L <= 4)."""
    n = L * L
    idx = np.arange(2**n, dtype=np.int64)
    bits = ((idx[:, None] >> np.arange(n)) & 1).astype(np.int8)
    S = (2 * bits - 1).reshape(-1, L, L).astype(float)
    e = energy_per_site(S)
    m = magnetisation(S)
    w = np.exp(-(e - e.min()) * n / T)
    Z = w.sum()
    return float((w * e).sum() / Z), float((w * np.abs(m)).sum() / Z), float((w * m**2).sum() / Z)


def binder(m):
    m2 = np.mean(m**2)
    return float(1.0 - np.mean(m**4) / (3.0 * m2**2))


def random_global_flip(spins, seed=0):
    """Apply the Z2 symmetry s -> -s to a random half of the samples."""
    rng = np.random.default_rng(seed)
    sign = rng.choice([-1, 1], size=spins.shape[:2]).astype(np.int8)
    return spins * sign[..., None, None]


def dataset(L=16, temps=None, seed=0, **kw):
    temps = np.round(np.arange(1.0, 3.55, 0.1), 2) if temps is None else np.asarray(temps)
    spins = random_global_flip(metropolis(L, temps, seed=seed, **kw), seed + 1)
    X = spins.reshape(-1, L * L).astype(float)
    T = np.repeat(temps, spins.shape[1])
    return temps, spins, X, T


def pca_tc(temps, X, T):
    """PC1 via SVD; T_c(L) estimate = peak of the variance of |PC1 score| per temperature."""
    Xc = X - X.mean(0)
    _, s, VT = np.linalg.svd(Xc, full_matrices=False)
    score = Xc @ VT[0] / np.sqrt(X.shape[1])          # = sqrt(N) m up to sign and centring
    chi = np.array([np.var(np.abs(score[T == t])) for t in temps])
    evr = s**2 / np.sum(s**2)
    return dict(pc1=VT[0], score=score, chi=chi, tc=float(temps[np.argmax(chi)]), evr=evr)


def supervised_tc(temps, X, T, seed=0):
    """Ordered (T < 2) vs disordered (T > 2.5): three classifiers, T_c from p = 1/2."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier

    rng = np.random.default_rng(seed)
    train_mask = (T < 2.0) | (T > 2.5)
    y = (T < 2.0).astype(int)
    idx = np.flatnonzero(train_mask)
    rng.shuffle(idx)
    tr, te = idx[: len(idx) * 2 // 3], idx[len(idx) * 2 // 3:]
    m = X.mean(1, keepdims=True)
    e = np.array([energy_per_site(x.reshape(int(np.sqrt(X.shape[1])), -1)) for x in X])[:, None]
    feats = {"logistic, raw spins": X,
             "logistic, (|m|, m^2, E/N)": np.hstack([np.abs(m), m**2, e]),
             "MLP 16 hidden, raw spins": X}
    res = {}
    for name, F in feats.items():
        if name.startswith("MLP"):
            clf = MLPClassifier((16,), max_iter=500, random_state=seed)
        else:
            clf = LogisticRegression(C=1.0, max_iter=2000)
        clf.fit(F[tr], y[tr])
        acc = float(clf.score(F[te], y[te]))
        p = np.array([clf.predict_proba(F[T == t])[:, 1].mean() for t in temps])
        # linear interpolation of the first downward crossing of p = 1/2
        k = int(np.argmax(p < 0.5)) if np.any(p < 0.5) else len(p) - 1
        tc = float(temps[k - 1] + (p[k - 1] - 0.5) / (p[k - 1] - p[k]) * (temps[k] - temps[k - 1])) \
            if k > 0 else float(temps[0])
        res[name] = dict(acc=acc, p=p, tc=tc)
    return res


def binder_crossing(Ls=(8, 16), temps=None, seed=0):
    temps = np.round(np.arange(2.0, 2.61, 0.05), 2) if temps is None else temps
    U = {}
    for L in Ls:
        spins = metropolis(L, temps, n_samples=100, chains=16, n_therm=1000, n_between=5,
                           seed=seed + L)
        U[L] = np.array([binder(magnetisation(spins[i].astype(float))) for i in range(len(temps))])
    d = U[Ls[1]] - U[Ls[0]]
    k = int(np.argmax(d < 0)) if np.any(d < 0) else len(d) - 1
    tc = float(temps[k - 1] + d[k - 1] / (d[k - 1] - d[k]) * (temps[k] - temps[k - 1])) \
        if k > 0 else float(temps[0])
    return temps, U, tc


def _demo() -> None:
    e, am, m2 = exact_small(4, 2.5)
    sp = metropolis(4, [2.5], n_samples=400, chains=50, n_therm=200, n_between=5, seed=3)[0]
    sp = sp.astype(float)
    print(f"L = 4, T = 2.5: exact <E>/N = {e:.4f}, <|m|> = {am:.4f}; Metropolis "
          f"{energy_per_site(sp).mean():.4f}, {np.abs(magnetisation(sp)).mean():.4f}")
    temps, spins, X, T = dataset()
    m = np.abs(X.mean(1))
    print(f"L = 16, {len(temps)} temperatures x {spins.shape[1]} samples; Onsager T_c = {TC:.4f}")
    for t in [1.5, 2.0, 2.3, 2.6, 3.0]:
        print(f"  T = {t}: <|m|> = {m[np.isclose(T, t)].mean():.3f}")
    r = pca_tc(temps, X, T)
    print(f"PCA: explained variance ratio PC1 {r['evr'][0]:.3f}, PC2 {r['evr'][1]:.3f}; "
          f"PC1 uniformity |<pc1, 1/L>| = {abs(r['pc1'].sum()) / 16:.3f}; "
          f"corr(|score|, |m|) = {np.corrcoef(np.abs(r['score']), m)[0, 1]:.4f}")
    print(f"PCA susceptibility peak T_c(L=16) ~ {r['tc']:.2f}")
    for name, v in supervised_tc(temps, X, T).items():
        print(f"{name:28s}: test accuracy {v['acc']:.3f}, p = 1/2 at T = {v['tc']:.3f}")
    ts, U, tc = binder_crossing()
    print(f"Binder U_8 vs U_16 crossing at T = {tc:.3f}; U_16(2.0) = {U[16][0]:.3f}, "
          f"U_16(2.6) = {U[16][-1]:.3f}")


if __name__ == "__main__":
    _demo()
