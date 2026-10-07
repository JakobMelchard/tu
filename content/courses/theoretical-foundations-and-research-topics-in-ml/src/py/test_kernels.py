import numpy as np

from kernels import (centre_gram, feature_distance, gram_matrix, is_psd,
                     laplacian_kernel, linear_kernel, poly2_feature_map,
                     kernel_rademacher_bound, kernel_rademacher_mc,
                     polynomial_kernel, rbf_kernel, representer_demo, sigmoid_kernel)


def test_standard_kernels_are_psd():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(25, 4))
    for k, kw in ((linear_kernel, {}), (polynomial_kernel, {"degree": 3}),
                  (rbf_kernel, {"gamma": 0.7}), (laplacian_kernel, {"gamma": 0.5})):
        assert is_psd(gram_matrix(k, X, **kw))


def test_sigmoid_kernel_not_psd():
    rng = np.random.default_rng(1)
    bad = 0
    for _ in range(20):
        X = rng.normal(size=(8, 2)) * 2
        bad += not is_psd(gram_matrix(sigmoid_kernel, X))
    assert bad > 0


def test_kernels_match_sklearn():
    from sklearn.metrics.pairwise import laplacian_kernel as skl, linear_kernel as sklin
    from sklearn.metrics.pairwise import polynomial_kernel as skp, rbf_kernel as skr
    rng = np.random.default_rng(2)
    X = rng.normal(size=(10, 3)); Y = rng.normal(size=(7, 3))
    assert np.allclose(rbf_kernel(X, Y, 0.3), skr(X, Y, gamma=0.3))
    assert np.allclose(polynomial_kernel(X, Y, 3, 1.0), skp(X, Y, degree=3, gamma=1.0, coef0=1.0))
    assert np.allclose(laplacian_kernel(X, Y, 0.4), skl(X, Y, gamma=0.4))
    assert np.allclose(linear_kernel(X, Y), sklin(X, Y))


def test_explicit_quadratic_feature_map():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(9, 3))
    Phi = poly2_feature_map(X, c=2.0)
    assert Phi.shape == (9, 1 + 3 + 3 + 3)
    assert np.allclose(Phi @ Phi.T, polynomial_kernel(X, X, 2, 2.0))


def test_feature_distance_and_centring():
    rng = np.random.default_rng(4)
    X = rng.normal(size=(5, 2))
    k = lambda a, b: rbf_kernel(a, b, 1.0)
    assert abs(feature_distance(k, X[0], X[0])) < 1e-12
    assert 0 < feature_distance(k, X[0], X[1]) <= 2 + 1e-12
    Kc = centre_gram(gram_matrix(k, X))
    assert np.allclose(Kc.sum(axis=0), 0) and is_psd(Kc)


def test_representer_theorem():
    rng = np.random.default_rng(5)
    X = rng.normal(size=(7, 2))
    y = rng.normal(size=7)
    wp, wd, alpha, orth = representer_demo(X, y, 0.05)
    assert np.allclose(wp, wd, atol=1e-8)
    assert orth < 1e-8
    assert len(alpha) == 7 and wp.shape == (6,)


def test_kernel_rademacher_closed_form_and_bound():
    rng = np.random.default_rng(6)
    # K = c I: sigma^T K sigma = c n for every sigma, so R_S = B sqrt(c n)/n equals the bound.
    K = 2.0 * np.eye(9)
    assert abs(kernel_rademacher_mc(K, 1.5, 10, rng) - 1.5 * np.sqrt(18) / 9) < 1e-12
    assert abs(kernel_rademacher_bound(K, 1.5) - 1.5 * np.sqrt(18) / 9) < 1e-12
    # linear kernel: must agree with the linear-class formula of note 05 (same sigma draws)
    X = rng.normal(size=(30, 4))
    r1 = kernel_rademacher_mc(linear_kernel(X, X), 2.0, 3000, np.random.default_rng(0))
    sigma = np.random.default_rng(0).choice([-1.0, 1.0], size=(3000, 30))
    assert abs(r1 - 2.0 * np.mean(np.linalg.norm(sigma @ X, axis=1)) / 30) < 1e-10
    # RBF: bound = B/sqrt(n) since k(x,x) = 1, and R_S <= bound
    K = rbf_kernel(X, X, 0.5)
    assert abs(kernel_rademacher_bound(K, 1.0) - 1 / np.sqrt(30)) < 1e-12
    assert kernel_rademacher_mc(K, 1.0, 3000, rng) <= kernel_rademacher_bound(K, 1.0)
