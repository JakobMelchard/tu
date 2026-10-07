"""Generative models on 8x8 synthetic images: a VAE trained on its ELBO, the GAN objective
evaluated (optimal discriminator, JS identity, saturating vs non-saturating loss), and the
DDPM forward process in closed form.

Note 06 (generative models). ELBO and reparameterisation after Kingma & Welling [S27];
GAN value function and D* after Goodfellow et al. [S28]; q(x_t | x_0) after Ho et al. [S29].
Derivations are in ws2026/applied-deep-learning/notes/05-autoencoders-generative.md; this
module makes them checkable on data small enough for a CPU test.
"""
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn


def make_bars(n, seed=0, size=8):
    """Binary size x size images: one horizontal bar with p = 0.5, one vertical bar with
    p = 0.5, at least one of the two. Flattened to [n, size^2] float32."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n, size, size), np.float32)
    kind = rng.integers(1, 4, n)                         # 1 = h, 2 = v, 3 = both
    for i in range(n):
        if kind[i] & 1:
            X[i, rng.integers(size), :] = 1
        if kind[i] & 2:
            X[i, :, rng.integers(size)] = 1
    return torch.from_numpy(X.reshape(n, -1))


# ---------------------------------------------------------------- VAE
def kl_gauss(mu, logvar):
    """KL(N(mu, diag e^logvar) || N(0, I)) = 1/2 sum (mu^2 + sigma^2 - log sigma^2 - 1), per row."""
    return 0.5 * (mu ** 2 + logvar.exp() - logvar - 1).sum(-1)


def kl_monte_carlo(mu, logvar, n=200_000, seed=0):
    """E_q[log q(z) - log p(z)] by sampling: the closed form must agree (test)."""
    g = torch.Generator().manual_seed(seed)
    std = (0.5 * logvar).exp()
    z = mu + std * torch.randn(n, *mu.shape, generator=g, dtype=mu.dtype)
    log_q = (-0.5 * ((z - mu) / std) ** 2 - torch.log(std) - 0.5 * np.log(2 * np.pi)).sum(-1)
    log_p = (-0.5 * z ** 2 - 0.5 * np.log(2 * np.pi)).sum(-1)
    return (log_q - log_p).mean(0)


class VAE(nn.Module):
    def __init__(self, d=64, hidden=64, latent=2):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(d, hidden), nn.ReLU(), nn.Linear(hidden, 2 * latent))
        self.dec = nn.Sequential(nn.Linear(latent, hidden), nn.ReLU(), nn.Linear(hidden, d))

    def encode(self, x):
        mu, logvar = self.enc(x).chunk(2, -1)
        return mu, logvar.clamp(-10, 10)

    def reparameterize(self, mu, logvar):
        return mu + (0.5 * logvar).exp() * torch.randn_like(mu)    # z = mu + sigma * eps

    def forward(self, x):
        mu, logvar = self.encode(x)
        return self.dec(self.reparameterize(mu, logvar)), mu, logvar


def neg_elbo(logits, x, mu, logvar, beta=1.0):
    """-ELBO per example, batch mean: Bernoulli reconstruction (BCE summed over pixels) + beta KL."""
    rec = F.binary_cross_entropy_with_logits(logits, x, reduction="none").sum(-1)
    return (rec + beta * kl_gauss(mu, logvar)).mean()


def train_vae(steps=400, seed=0, n=2000, lr=3e-3, batch=128, beta=1.0):
    torch.manual_seed(seed)
    X, model = make_bars(n, seed), VAE()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    g, hist = torch.Generator().manual_seed(seed), []
    for _ in range(steps):
        x = X[torch.randint(0, n, (batch,), generator=g)]
        logits, mu, logvar = model(x)
        loss = neg_elbo(logits, x, mu, logvar, beta)
        opt.zero_grad()
        loss.backward()
        opt.step()
        hist.append(loss.item())
    return model, hist


# ---------------------------------------------------------------- GAN objective
def gan_value(d_real, d_fake):
    """V(D, G) = E_data log D(x) + E_z log(1 - D(G(z))), from discriminator probabilities."""
    return float(np.mean(np.log(d_real)) + np.mean(np.log1p(-d_fake)))


def gauss_pdf(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))


def optimal_discriminator(x, pd, pg):
    """D*(x) = p_data(x) / (p_data(x) + p_g(x)) for fixed G [S28]."""
    a, b = pd(x), pg(x)
    return a / (a + b)


def js_divergence_1d(pd, pg, lo=-20, hi=20, n=200_001):
    x = np.linspace(lo, hi, n)
    a, b = pd(x), pg(x)
    m = 0.5 * (a + b)
    kl = lambda p: np.trapezoid(np.where(p > 0, p * np.log(np.where(p > 0, p, 1) / m), 0), x)
    return 0.5 * kl(a) + 0.5 * kl(b)


def value_at_optimal_d(pd, pg, lo=-20, hi=20, n=200_001):
    """V(D*, G) by quadrature; equals -log 4 + 2 JS(p_data || p_g) (test)."""
    x = np.linspace(lo, hi, n)
    d = optimal_discriminator(x, pd, pg)
    f = pd(x) * np.log(np.clip(d, 1e-300, 1)) + pg(x) * np.log(np.clip(1 - d, 1e-300, 1))
    return float(np.trapezoid(f, x))


def generator_loss_grads(a):
    """d/da of the two generator losses at discriminator logit a (D = sigmoid(a)):
    saturating  log(1 - D):  -sigmoid(a)        -> 0 when D rejects the sample (a << 0)
    non-saturating -log D:   -(1 - sigmoid(a))  -> -1 there: the useful signal."""
    t = torch.tensor(a, dtype=torch.float64, requires_grad=True)
    (g1,) = torch.autograd.grad(F.logsigmoid(-t).sum(), t)          # log(1 - sigmoid(a))
    (g2,) = torch.autograd.grad((-F.logsigmoid(t)).sum(), t)
    return g1.numpy(), g2.numpy()


def gan_steps(steps=20, seed=0, latent=4, batch=64):
    """A few alternating updates of small MLPs on bars; returns (d_loss, g_loss) per step.
    Not a trained GAN: enough to see the two losses move against each other."""
    torch.manual_seed(seed)
    X = make_bars(512, seed)
    G = nn.Sequential(nn.Linear(latent, 64), nn.ReLU(), nn.Linear(64, 64))
    D = nn.Sequential(nn.Linear(64, 64), nn.LeakyReLU(0.2), nn.Linear(64, 1))
    oG, oD = (torch.optim.Adam(m.parameters(), 2e-3, betas=(0.5, 0.999)) for m in (G, D))
    hist = []
    for _ in range(steps):
        x, z = X[torch.randint(0, 512, (batch,))], torch.randn(batch, latent)
        fake = torch.sigmoid(G(z))
        ones, zeros = torch.ones(batch, 1), torch.zeros(batch, 1)
        d_loss = (F.binary_cross_entropy_with_logits(D(x), ones)
                  + F.binary_cross_entropy_with_logits(D(fake.detach()), zeros))
        oD.zero_grad()
        d_loss.backward()
        oD.step()
        g_loss = F.binary_cross_entropy_with_logits(D(fake), ones)      # non-saturating
        oG.zero_grad()
        g_loss.backward()
        oG.step()
        hist.append((d_loss.item(), g_loss.item()))
    return hist


# ---------------------------------------------------------------- diffusion forward process
def alpha_bar(T=1000, beta1=1e-4, betaT=0.02):
    """Linear beta schedule; alpha_bar_t = prod_{s<=t} (1 - beta_s) [S29]."""
    return np.cumprod(1 - np.linspace(beta1, betaT, T))


def q_sample(x0, t, abar, rng):
    """x_t = sqrt(abar_t) x0 + sqrt(1 - abar_t) eps: any step in one shot (t is 1-based)."""
    a = abar[t - 1]
    return np.sqrt(a) * x0 + np.sqrt(1 - a) * rng.normal(size=np.shape(x0))


def q_iterate(x0, t, T=1000, beta1=1e-4, betaT=0.02, rng=None):
    """The same by running the chain x_t = sqrt(1 - beta_t) x_{t-1} + sqrt(beta_t) eps."""
    betas = np.linspace(beta1, betaT, T)
    x = np.array(x0, float)
    for s in range(t):
        x = np.sqrt(1 - betas[s]) * x + np.sqrt(betas[s]) * rng.normal(size=x.shape)
    return x


if __name__ == "__main__":
    mu, lv = torch.tensor([0.0, 1.0, -0.5]), torch.tensor([0.0, 0.0, np.log(0.25)])
    print(f"KL closed form {kl_gauss(mu, lv).item():.4f} (ADL note 05 worked example: 0.943)")
    model, hist = train_vae()
    print(f"VAE on 8x8 bars, latent 2: -ELBO {np.mean(hist[:20]):.2f} -> {np.mean(hist[-20:]):.2f} nats/image")
    pd, pg = (lambda x: gauss_pdf(x, 0, 1)), (lambda x: gauss_pdf(x, 2, 1))
    v, js = value_at_optimal_d(pd, pg), js_divergence_1d(pd, pg)
    print(f"p_data N(0,1), p_g N(2,1): V(D*,G) = {v:.4f}, -log4 + 2 JS = {-np.log(4) + 2 * js:.4f}")
    print(f"  at p_g = p_data: V = {value_at_optimal_d(pd, pd):.4f} = -log 4 = {-np.log(4):.4f}")
    g1, g2 = generator_loss_grads([-6.0, 0.0])
    print(f"generator gradient at D = sigmoid(-6) = {1 / (1 + np.exp(6)):.4f}: saturating {g1[0]:.4f}, "
          f"non-saturating {g2[0]:.4f}")
    h = gan_steps()
    print(f"20 GAN steps on bars: D loss {h[0][0]:.3f} -> {h[-1][0]:.3f}, G loss {h[0][1]:.3f} -> {h[-1][1]:.3f}")
    ab = alpha_bar()
    print(f"DDPM linear schedule: alpha_bar at t = 1, 250, 500, 1000: {ab[0]:.4f}, {ab[249]:.4f}, "
          f"{ab[499]:.4f}, {ab[-1]:.2e}")
