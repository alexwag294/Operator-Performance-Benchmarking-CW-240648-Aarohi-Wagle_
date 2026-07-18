"""
train_models.py
---------------
Trains KMeans clustering across multiple values of k (the assignment's
"compare at least 3 models or configurations" requirement) and returns
the fitted models plus their labels, ready for evaluation.
"""

from sklearn.cluster import KMeans


def train_kmeans_configs(features_scaled, config: dict) -> dict:
    """
    Fit a KMeans model for each k in config["ml"]["k_values"].

    Returns {k: {"model": fitted_model, "labels": cluster_labels}}
    """
    k_values = config["ml"]["k_values"]
    random_state = config["ml"]["random_state"]
    n_init = config["ml"]["n_init"]

    results = {}
    for k in k_values:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=n_init)
        labels = model.fit_predict(features_scaled)
        results[k] = {"model": model, "labels": labels}

    return results
