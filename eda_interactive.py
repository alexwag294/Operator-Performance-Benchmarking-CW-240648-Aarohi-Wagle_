# %%
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EDA_Interactive") \
    .master("local[*]") \
    .getOrCreate()

print(spark.version)

stop_times_sdf = spark.read.csv(
    r"C:\Users\Acer\operator_performance\data\itm_west_midlands_gtfs\stop_times.txt",
    header=True, inferSchema=True
)
trips_sdf = spark.read.csv(
    r"C:\Users\Acer\operator_performance\data\itm_west_midlands_gtfs\trips.txt",
    header=True, inferSchema=True
)
routes_sdf = spark.read.csv(
    r"C:\Users\Acer\operator_performance\data\itm_west_midlands_gtfs\routes.txt",
    header=True, inferSchema=True
)
agency_sdf = spark.read.csv(
    r"C:\Users\Acer\operator_performance\data\itm_west_midlands_gtfs\agency.txt",
    header=True, inferSchema=True
)
stop_times_sdf = stop_times_sdf.repartition(4)
stop_times_sdf.cache()
stop_times_sdf.count()

# %%
from pyspark.sql.functions import broadcast, col, floor

stop_times_with_route = stop_times_sdf.join(
    trips_sdf.select("trip_id", "route_id"), on="trip_id", how="left"
)
stop_times_full = stop_times_with_route.join(
    broadcast(routes_sdf.select("route_id", "agency_id")), on="route_id", how="left"
)
stop_times_named = stop_times_full.join(
    broadcast(agency_sdf.select("agency_id", "agency_name")), on="agency_id", how="left"
)

stop_times_named = stop_times_named.withColumn(
    "arrival_seconds",
    (col("arrival_time").substr(1, 2).cast("int") * 3600)
    + (col("arrival_time").substr(4, 2).cast("int") * 60)
    + (col("arrival_time").substr(7, 2).cast("int"))
)
stop_times_named = stop_times_named.withColumn(
    "hour_of_day", (floor(col("arrival_seconds") / 3600) % 24)
)

print("Ready:", stop_times_named.count())

# %%
import matplotlib.pyplot as plt

trips_by_hour_pd = stop_times_named.groupBy("hour_of_day").count().orderBy("hour_of_day").toPandas()

plt.figure(figsize=(8,5))
plt.bar(trips_by_hour_pd["hour_of_day"], trips_by_hour_pd["count"])
plt.xlabel("Hour of day")
plt.ylabel("Number of scheduled stops")
plt.title("Service volume by hour of day")
plt.show()

# %%
from pyspark.sql.window import Window
from pyspark.sql.functions import lag

window_spec = Window.partitionBy("agency_name", "stop_id").orderBy("arrival_seconds")
headway_df = stop_times_named.withColumn(
    "prev_arrival", lag("arrival_seconds").over(window_spec)
).withColumn("headway_seconds", col("arrival_seconds") - col("prev_arrival"))

headway_sample = headway_df.filter(col("headway_seconds").between(0, 7200)) \
    .sample(fraction=0.01, seed=42).toPandas()

plt.figure(figsize=(8,5))
plt.hist(headway_sample["headway_seconds"], bins=40)
plt.xlabel("Headway (seconds)")
plt.ylabel("Frequency")
plt.title("Distribution of headways between consecutive buses")
plt.show()

# %%
top_routes = trips_sdf.groupBy("route_id").count() \
    .join(routes_sdf.select("route_id", "route_short_name", "agency_id"), on="route_id") \
    .join(agency_sdf.select("agency_id", "agency_name"), on="agency_id") \
    .orderBy("count", ascending=False).limit(10).toPandas()

plt.figure(figsize=(8,5))
plt.barh(top_routes["route_short_name"] + " (" + top_routes["agency_name"] + ")", top_routes["count"])
plt.xlabel("Number of trips")
plt.title("Top 10 most frequent routes")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# %%
stops_per_trip = stop_times_sdf.groupBy("trip_id").count().sample(fraction=0.05, seed=42).toPandas()

plt.figure(figsize=(8,5))
plt.hist(stops_per_trip["count"], bins=30)
plt.xlabel("Number of stops per trip")
plt.ylabel("Frequency")
plt.title("Distribution of trip length (stops)")
plt.show()