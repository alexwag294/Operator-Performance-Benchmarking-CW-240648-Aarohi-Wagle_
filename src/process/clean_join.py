"""
clean_join.py
-------------
Joins the four GTFS tables together so every stop_times row ends up
tagged with its operator (agency_name). This is the core "Data
Storage & Processing" step: creating relationships between datasets.

Join chain:
    stop_times.trip_id  -> trips.trip_id   (gives trips.route_id)
    trips.route_id      -> routes.route_id (gives routes.agency_id)
    routes.agency_id    -> agency.agency_id (gives agency.agency_name)

A broadcast join is used for the small `routes` and `agency` tables
(1,169 and ~200 rows respectively) against the much larger stop_times
table (5.4M rows), since broadcasting the small side avoids an
expensive shuffle of the large DataFrame.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import broadcast


def join_operator_info(
    stop_times: DataFrame, trips: DataFrame, routes: DataFrame, agency: DataFrame
) -> DataFrame:
    """Return stop_times with route_id, agency_id, and agency_name attached."""
    with_route = stop_times.join(
        trips.select("trip_id", "route_id"), on="trip_id", how="left"
    )

    with_agency_id = with_route.join(
        broadcast(routes.select("route_id", "agency_id")),
        on="route_id",
        how="left",
    )

    with_agency_name = with_agency_id.join(
        broadcast(agency.select("agency_id", "agency_name")),
        on="agency_id",
        how="left",
    )

    return with_agency_name


def add_arrival_seconds(df: DataFrame) -> DataFrame:
    """
    Convert GTFS arrival_time (HH:MM:SS text, which can exceed 24:00:00
    for overnight services) into an integer number of seconds since
    midnight, so it can be used in arithmetic (e.g. headway calculation).
    """
    from pyspark.sql.functions import col

    return df.withColumn(
        "arrival_seconds",
        (col("arrival_time").substr(1, 2).cast("int") * 3600)
        + (col("arrival_time").substr(4, 2).cast("int") * 60)
        + (col("arrival_time").substr(7, 2).cast("int")),
    )
