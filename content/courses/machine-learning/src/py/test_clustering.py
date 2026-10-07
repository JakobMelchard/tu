import numpy as np
import pytest
from sklearn import cluster as skc, metrics as skm
from sklearn.datasets import make_blobs, make_moons

import clustering as cl

X, y = make_blobs(200, centers=4, cluster_std=0.8, random_state=2)
Xm, ym = make_moons(200, noise=0.08, random_state=0)


def test_kmeans_inertia_close_to_sklearn():
    ours = cl.KMeans(4, n_init=5, rng=0).fit(X)
    theirs = skc.KMeans(4, n_init=5, random_state=0).fit(X)
    assert abs(ours.inertia_ - theirs.inertia_) / theirs.inertia_ < 0.02
    assert skm.adjusted_rand_score(ours.labels_, theirs.labels_) > 0.95
    assert np.array_equal(ours.predict(X), ours.labels_)


@pytest.mark.parametrize("linkage", ["single", "complete", "average", "ward"])
def test_agglomerative_matches_sklearn(linkage):
    ours = cl.Agglomerative(4, linkage).fit(X)
    theirs = skc.AgglomerativeClustering(4, linkage=linkage).fit(X)
    assert skm.adjusted_rand_score(ours.labels_, theirs.labels_) > 0.95


def test_dbscan_matches_sklearn_exactly():
    ours = cl.DBSCAN(0.2, 5).fit(Xm)
    theirs = skc.DBSCAN(eps=0.2, min_samples=5).fit(Xm)
    assert np.array_equal(ours.labels_ == -1, theirs.labels_ == -1)
    m = ours.labels_ != -1
    assert skm.adjusted_rand_score(ours.labels_[m], theirs.labels_[m]) == pytest.approx(1.0)
    assert ours.labels_.max() == 1


def test_evaluation_metrics_match_sklearn():
    lab = cl.KMeans(4, rng=0).fit(X).labels_
    assert cl.silhouette_score(X, lab) == pytest.approx(skm.silhouette_score(X, lab))
    assert cl.davies_bouldin(X, lab) == pytest.approx(skm.davies_bouldin_score(X, lab))
    assert cl.adjusted_rand_index(y, lab) == pytest.approx(skm.adjusted_rand_score(y, lab))
    assert cl.normalized_mutual_info(y, lab) == pytest.approx(skm.normalized_mutual_info_score(y, lab))
    assert cl.purity(lab, y) > 0.95
