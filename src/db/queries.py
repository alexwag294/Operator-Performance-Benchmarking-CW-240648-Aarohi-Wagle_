"""
queries.py
----------
All read queries against the operator_reliability table.

SECURITY: every query here uses a parameterized placeholder (`?`) with
values passed as a separate tuple, never Python string
formatting/concatenation. This prevents SQL injection - see the
security section in the project README for a worked example of why
this matters.
"""

import sqlite3


def get_operator_by_name(conn: sqlite3.Connection, agency_name: str) -> list[tuple]:
    """Look up a single operator's reliability data by name."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM operator_reliability WHERE agency_name = ?",
        (agency_name,),
    )
    return cursor.fetchall()


def get_operators_by_tier(conn: sqlite3.Connection, performance_tier: str) -> list[tuple]:
    """Return all operators in a given performance tier (e.g. 'Most Reliable')."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT agency_name, avg_headway_sec, headway_stddev_sec "
        "FROM operator_reliability WHERE performance_tier = ? "
        "ORDER BY headway_stddev_sec",
        (performance_tier,),
    )
    return cursor.fetchall()


def get_top_n_most_reliable(conn: sqlite3.Connection, n: int) -> list[tuple]:
    """Return the n operators with the lowest headway variance (most consistent)."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT agency_name, headway_stddev_sec FROM operator_reliability "
        "ORDER BY headway_stddev_sec ASC LIMIT ?",
        (n,),
    )
    return cursor.fetchall()
