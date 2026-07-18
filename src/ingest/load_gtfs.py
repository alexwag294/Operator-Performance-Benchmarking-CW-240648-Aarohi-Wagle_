"""
load_gtfs.py
------------
Loads the four BODS GTFS timetable files (stop_times, trips, routes,
agency) as PySpark DataFrames. This is the entry point for the
"Data Collection & Ingestion" stage of the pipeline.
"""

from pyspark.sql import DataFrame, SparkSession

from src.config import resolve_path


def load_gtfs_tables(spark: SparkSession, config: dict) -> dict[str, DataFrame]:
    """
    Load stop_times, trips, routes, and agency GTFS files into PySpark
    DataFrames.

    Returns a dict of {table_name: DataFrame} so callers can access
    each table by name, e.g. tables["stop_times"].
    """
    gtfs_dir = resolve_path(config["data"]["gtfs_dir"])

    file_names = {
        "stop_times": "stop_times.txt",
        "trips": "trips.txt",
        "routes": "routes.txt",
        "agency": "agency.txt",
    }

    tables: dict[str, DataFrame] = {}
    for table_name, file_name in file_names.items():
        file_path = str(gtfs_dir / file_name)
        tables[table_name] = spark.read.csv(file_path, header=True, inferSchema=True)

    return tables


def repartition_and_cache(df: DataFrame, config: dict) -> DataFrame:
    """
    Repartition the (typically large) stop_times DataFrame to the
    configured partition count and cache it in memory, since it is
    reused across multiple downstream operations (joins, aggregations).
    """
    n_partitions = config["spark"]["repartition_count"]
    df = df.repartition(n_partitions)
    df.cache()
    df.count()  # force the cache to actually materialise
    return df
