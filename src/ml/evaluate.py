"""
evaluate.py
-----------
Evaluates each trained clustering configuration using Silhouette
Score and Within-Cluster Sum of Squares (WCSS), as required by the
brief's clustering evaluation criteria.

Also documents the algorithmic complexity of KMeans, since the brief
requires evaluating algorithmic complexity alongside accuracy: KMeans
has time complexity approximately O(n * k * i * d), where n is the
number of data points (operators here), k the number of clusters,
i the number of iterations to convergence, and d the number of
features. Because clustering is performed on a small, pre-aggregated
per-operator feature table (tens of rows) rather than the raw
multi-million-row stop_times data, all configurations converge almost
instantly regardless of k.
"""

import pandas as pd
from sklearn.metrics import silhouette_score


def evaluate_configs(features_scaled, trained_models: dict) -> pd.DataFrame:
    """
    Returns a DataFrame with one row per k, showing silhouette score
    and WCSS (inertia), for direct comparison of the >=3 configurations.
    """
    rows = []
    for k, result in trained_models.items():
        labels = result["labels"]
        model = result["model"]
        rows.append(
            {
                "k": k,
                "silhouette_score": silhouette_score(features_scaled, labels),
                "wcss": model.inertia_,
            }
        )
    return pd.DataFrame(rows)
