"""
Tests for src/ml/evaluate.py and src/ml/train_models.py, using a tiny
synthetic dataset with an obvious 2-cluster structure so the expected
result is easy to reason about.
"""

import numpy as np

from src.ml.evaluate import evaluate_configs
from src.ml.train_models import train_kmeans_configs

_TEST_CONFIG = {"ml": {"k_values": [2, 3], "random_state": 42, "n_init": 10}}


def test_train_and_evaluate_configs_returns_expected_shape():
    # Two obviously separated clusters of points
    features = np.array(
        [[0, 0], [0, 1], [1, 0], [10, 10], [10, 11], [11, 10]], dtype=float
    )

    trained = train_kmeans_configs(features, _TEST_CONFIG)
    assert set(trained.keys()) == {2, 3}

    results_df = evaluate_configs(features, trained)
    assert len(results_df) == 2
    assert set(results_df.columns) == {"k", "silhouette_score", "wcss"}

    # k=2 should score very well on this obviously 2-cluster dataset
    sil_k2 = results_df.loc[results_df["k"] == 2, "silhouette_score"].iloc[0]
    assert sil_k2 > 0.8
