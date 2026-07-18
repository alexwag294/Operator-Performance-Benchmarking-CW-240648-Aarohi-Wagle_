# Architecture: Operator Performance Benchmarking

## Pipeline overview

```
BODS Timetables (GTFS)  +  BODS Disruptions (SIRI-SX)
            |
            v
    PySpark processing
    (join, repartition, cache, broadcast join)
            |
            v
    SQLite database
    (parameterised queries)
            |
            v
    ML clustering (KMeans)
    (3 configurations compared: k=2, 3, 4)
            |
            v
    Performance tiers
    (Most Reliable / Moderate / Least Consistent)
```

See `docs/architecture.png` for the visual diagram version.

## Module responsibilities

| Module | Responsibility |
|---|---|
| `src/ingest/load_gtfs.py` | Loads BODS GTFS timetable files as PySpark DataFrames |
| `src/ingest/parse_disruptions.py` | Parses BODS SIRI-SX disruptions XML into a pandas DataFrame |
| `src/process/clean_join.py` | Joins stop_times -> trips -> routes -> agency to attach operator info |
| `src/process/headway.py` | Computes per-operator headway consistency (the reliability metric) |
| `src/db/schema.sql`, `load_db.py`, `queries.py` | SQLite schema, loading, and parameterised queries |
| `src/ml/features.py` | Builds and scales the clustering feature matrix |
| `src/ml/train_models.py` | Trains KMeans across k=2, 3, 4 |
| `src/ml/evaluate.py` | Evaluates each configuration (silhouette score, WCSS) |
| `src/ml/interpret.py` | Labels numeric clusters as human-readable performance tiers |
| `src/viz/charts.py` | Generates and saves all EDA/results figures |

## Why PySpark vs pandas

PySpark is used for all large-scale operations on the raw GTFS data (5.4M rows): loading, joining, repartitioning, and aggregation, since pandas would need to load the entire dataset into a single machine's memory. Pandas is used only after data has been reduced to a small, already-aggregated result (e.g. the per-operator reliability summary), where the dataset comfortably fits in memory and pandas/scikit-learn's simpler API is more convenient for the final clustering and plotting steps.

## Data persistence strategy

The full cleaned/joined dataset is kept in Spark's in-memory cache during processing rather than written out in full. Only the small, aggregated per-operator summary is persisted, in SQLite (for structured querying) and CSV (for reporting). Where a physical export of the full cleaned dataset is needed, Parquet is used instead of CSV, since its columnar storage and schema preservation give better performance and compression at this scale.

## Known limitations

- **Disruption-operator linkage**: the vast majority of BODS disruption records (359 of 409 in the snapshot examined) do not specify a particular operator, and none used a code matching the GTFS `agency_id`/NOC scheme. This reflects a known inconsistency in how local authorities report BODS disruption data, not an error in this pipeline. As a result, disruptions are used as regional/national context in the EDA rather than joined to individual operators; reliability is instead derived from timetable-based headway consistency.
- **Headway variance as a reliability proxy**: this metric is influenced by scheduled service frequency as well as actual consistency - a low-frequency rural route will naturally show higher headway variance than a high-frequency urban one, even if both operators run exactly on schedule. This is a known confound, noted here for transparency and as a direction for future refinement (e.g. normalising variance by scheduled frequency).

## Security

All SQLite queries (`src/db/queries.py`) use parameterised placeholders (`?`) with values passed as a separate tuple, never Python string concatenation, to prevent SQL injection - see `tests/test_db.py::test_get_operator_by_name_is_parameterized_safe` for a test demonstrating this explicitly. No API keys or database credentials are hardcoded anywhere in this codebase; SQLite connects directly to a local file and requires no credentials.
