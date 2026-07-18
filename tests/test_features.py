"""
Tests for src/ml/interpret.py (cluster -> performance tier labeling)
and src/ml/features.py (feature matrix construction).
"""

import pandas as pd

from src.ml.features import build_feature_matrix
from src.ml.interpret import label_clusters

_TEST_CONFIG = {
    "ml": {
        "cluster_labels": {
            "most_reliable": "Most Reliable",
            "moderate": "Moderate",
            "least_consistent": "Least Consistent",
        }
    }
}


def test_label_clusters_orders_by_stddev():
    df = pd.DataFrame(
        {
            "agency_name": ["A", "B", "C"],
            "avg_headway_sec": [100, 500, 2000],
            "headway_stddev_sec": [50, 400, 3000],
            "cluster": [0, 1, 2],
        }
    )

    labelled = label_clusters(df, _TEST_CONFIG)

    # Cluster 0 has the lowest stddev, so it should be "Most Reliable"
    assert labelled.loc[labelled["cluster"] == 0, "performance_tier"].iloc[0] == "Most Reliable"
    # Cluster 2 has the highest stddev, so it should be "Least Consistent"
    assert labelled.loc[labelled["cluster"] == 2, "performance_tier"].iloc[0] == "Least Consistent"


def test_build_feature_matrix_drops_nulls_and_scales():
    df = pd.DataFrame(
        {
            "agency_name": ["A", "B", "C"],
            "avg_headway_sec": [100, 500, None],
            "headway_stddev_sec": [50, 400, 300],
        }
    )

    features_scaled, scaler = build_feature_matrix(df)

    # The row with a null avg_headway_sec should have been dropped
    assert features_scaled.shape[0] == 2
    assert features_scaled.shape[1] == 2
