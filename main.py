
from pyspark.sql import SparkSession

from src.config import load_config
from src.db.load_db import apply_schema, get_connection, load_operator_reliability
from src.ingest.load_gtfs import load_gtfs_tables, repartition_and_cache
from src.ingest.parse_disruptions import parse_disruptions
from src.ml.evaluate import evaluate_configs
from src.ml.features import build_feature_matrix
from src.ml.interpret import label_clusters
from src.ml.train_models import train_kmeans_configs
from src.process.clean_join import add_arrival_seconds, join_operator_info
from src.process.headway import aggregate_operator_reliability, compute_headways


def main():
    config = load_config()

    # --- Ingestion ---
    spark = (
        SparkSession.builder.appName(config["spark"]["app_name"])
        .master(config["spark"]["master"])
        .getOrCreate()
    )

    tables = load_gtfs_tables(spark, config)
    tables["stop_times"] = repartition_and_cache(tables["stop_times"], config)

    disruptions_df = parse_disruptions(config)
    print(f"Loaded {len(disruptions_df)} disruption records (used as context, see docs).")

    # --- Processing ---
    stop_times_named = join_operator_info(
        tables["stop_times"], tables["trips"], tables["routes"], tables["agency"]
    )
    stop_times_named = add_arrival_seconds(stop_times_named)

    headway_df = compute_headways(stop_times_named)
    operator_reliability = aggregate_operator_reliability(headway_df)
    operator_reliability_pd = operator_reliability.toPandas()

    # --- ML ---
    features_scaled, _ = build_feature_matrix(operator_reliability_pd)
    trained_models = train_kmeans_configs(features_scaled, config)
    evaluation_df = evaluate_configs(features_scaled, trained_models)
    print("Model comparison (silhouette score, WCSS) across configured k values:")
    print(evaluation_df)

    selected_k = config["ml"]["selected_k"]
    operator_reliability_pd["cluster"] = trained_models[selected_k]["labels"]
    operator_reliability_pd = label_clusters(operator_reliability_pd, config)

    # --- Storage ---
    conn = get_connection(config)
    apply_schema(conn)
    load_operator_reliability(conn, operator_reliability_pd, config)
    conn.close()

    print("Pipeline complete. Results stored in the configured SQLite database.")
    spark.stop()


if __name__ == "__main__":
    main()
