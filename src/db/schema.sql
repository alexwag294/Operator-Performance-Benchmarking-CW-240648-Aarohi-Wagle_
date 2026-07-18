-- Schema for the Operator Performance Benchmarking database.
-- One row per bus operator, storing the reliability metrics used
-- for clustering plus the resulting performance tier.

CREATE TABLE IF NOT EXISTS operator_reliability (
    agency_name          TEXT PRIMARY KEY,
    avg_headway_sec      REAL NOT NULL,
    headway_stddev_sec   REAL NOT NULL,
    cluster              INTEGER,
    performance_tier     TEXT
);
