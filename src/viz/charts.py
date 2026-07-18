"""
charts.py
---------
Shared matplotlib charting functions for EDA and results. All figures
are saved into the configured output directory (docs/figures by
default) so they can be embedded directly in the report.

Note: PySpark DataFrames are converted to pandas only at this final
plotting step (via .toPandas()/.sample() upstream), never for
large-scale processing - see docs/architecture.md for the
PySpark-vs-pandas justification.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import resolve_path


def _save(fig, filename: str, config: dict) -> None:
    output_dir = resolve_path(config["output"]["figures_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / filename, bbox_inches="tight")


def plot_trips_by_hour(trips_by_hour_pd: pd.DataFrame, config: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(trips_by_hour_pd["hour_of_day"], trips_by_hour_pd["count"])
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Number of scheduled stops")
    ax.set_title("Service volume by hour of day")
    _save(fig, "eda_trips_by_hour.png", config)
    plt.close(fig)


def plot_headway_distribution(headway_sample_pd: pd.DataFrame, config: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(headway_sample_pd["headway_seconds"], bins=40)
    ax.set_xlabel("Headway (seconds)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of headways between consecutive buses")
    _save(fig, "eda_headway_distribution.png", config)
    plt.close(fig)


def plot_operator_clusters(operator_reliability_pd: pd.DataFrame, config: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    for tier, group in operator_reliability_pd.groupby("performance_tier"):
        ax.scatter(group["avg_headway_sec"], group["headway_stddev_sec"], label=tier)
    ax.set_xlabel("Average headway (seconds)")
    ax.set_ylabel("Headway standard deviation (seconds)")
    ax.set_title("Operator performance clusters")
    ax.legend()
    _save(fig, "operator_clusters.png", config)
    plt.close(fig)
