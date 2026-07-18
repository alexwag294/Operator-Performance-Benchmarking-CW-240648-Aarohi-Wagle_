
import sqlite3

import pandas as pd
import pytest

from src.db.queries import get_operator_by_name, get_top_n_most_reliable


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE operator_reliability (
            agency_name TEXT PRIMARY KEY,
            avg_headway_sec REAL,
            headway_stddev_sec REAL,
            cluster INTEGER,
            performance_tier TEXT
        )
        """
    )
    df = pd.DataFrame(
        {
            "agency_name": ["Operator A", "Operator B"],
            "avg_headway_sec": [150.0, 900.0],
            "headway_stddev_sec": [400.0, 2000.0],
            "cluster": [0, 1],
            "performance_tier": ["Most Reliable", "Least Consistent"],
        }
    )
    df.to_sql("operator_reliability", connection, if_exists="append", index=False)
    yield connection
    connection.close()


def test_get_operator_by_name_returns_correct_row(conn):
    result = get_operator_by_name(conn, "Operator A")
    assert len(result) == 1
    assert result[0][0] == "Operator A"


def test_get_operator_by_name_is_parameterized_safe(conn):
    # A classic SQL-injection payload should simply not match anything,
    # rather than executing as SQL - proving the query is parameterized.
    malicious_input = "Operator A' OR '1'='1"
    result = get_operator_by_name(conn, malicious_input)
    assert result == []


def test_get_top_n_most_reliable_orders_correctly(conn):
    result = get_top_n_most_reliable(conn, 1)
    assert result[0][0] == "Operator A"  # lower stddev = more reliable
