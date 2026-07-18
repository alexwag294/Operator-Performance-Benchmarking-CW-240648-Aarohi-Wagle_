"""
headway.py
----------
Computes headway (time gap between consecutive buses at the same stop)
and aggregates it into a per-operator reliability metric: lower
variance in headway means a more consistent, predictable service.

This exists because BODS disruption records could not be reliably
joined to individual operators (see docs/architecture.md), so
service consistency derived from the timetable itself is used as the
reliability proxy instead.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, lag, stddev
from pyspark.sql.window import Window


def compute_headways(stop_times_named: DataFrame) -> DataFrame:
    """
    For each (operator, stop), order stops by arrival time and compute
    the gap (headway) between consecutive arrivals.
    """
    window_spec = Window.partitionBy("agency_name", "stop_id").orderBy(
        "arrival_seconds"
    )

    return stop_times_named.withColumn(
        "prev_arrival", lag("arrival_seconds").over(window_spec)
    ).withColumn("headway_seconds", col("arrival_seconds") - col("prev_arrival"))


def aggregate_operator_reliability(headway_df: DataFrame) -> DataFrame:
    """
    Aggregate headway data into one row per operator: average headway
    and headway standard deviation (the reliability metric used for
    clustering).
    """
    return (
        headway_df.filter(col("headway_seconds").isNotNull())
        .groupBy("agency_name")
        .agg(
            avg("headway_seconds").alias("avg_headway_sec"),
            stddev("headway_seconds").alias("headway_stddev_sec"),
        )
        .orderBy("headway_stddev_sec")
    )
