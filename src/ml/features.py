"""
features.py
-----------
Builds the feature matrix used for clustering operators into
performance tiers, and scales it (KMeans is distance-based, so
features must be on comparable scales).
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = ["avg_headway_sec", "headway_stddev_sec"]


def build_feature_matrix(operator_reliability_pd: pd.DataFrame):
    """
    Returns (features_scaled, scaler) where features_scaled is a numpy
    array ready for KMeans, and scaler is kept so new data could be
    transformed consistently if needed later.
    """
    features = operator_reliability_pd[FEATURE_COLUMNS].dropna()
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    return features_scaled, scaler
