"""
interpret.py
------------
Turns raw numeric cluster IDs (0, 1, 2...) into human-readable
performance tiers (e.g. "Most Reliable"), based on each cluster's
average headway_stddev - the cluster with the lowest variance is
labelled most reliable, the highest is labelled least consistent.
"""

import pandas as pd


def label_clusters(operator_reliability_pd: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds a `performance_tier` column, derived from each cluster's mean
    headway_stddev_sec (lower = more reliable).
    """
    df = operator_reliability_pd.copy()

    cluster_order = (
        df.groupby("cluster")["headway_stddev_sec"]
        .mean()
        .sort_values()
        .index.tolist()
    )

    labels_config = config["ml"]["cluster_labels"]
    tier_names = [
        labels_config["most_reliable"],
        labels_config["moderate"],
        labels_config["least_consistent"],
    ]

    # Map however many clusters actually exist (may be < 3) to tier names,
    # from most reliable (lowest stddev) to least (highest stddev).
    tier_map = {
        cluster_id: tier_names[i] if i < len(tier_names) else f"Tier {i}"
        for i, cluster_id in enumerate(cluster_order)
    }

    df["performance_tier"] = df["cluster"].map(tier_map)
    return df
