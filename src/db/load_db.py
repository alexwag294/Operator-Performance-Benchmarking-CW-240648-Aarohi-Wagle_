"""
load_db.py
----------
Creates the SQLite database (applying schema.sql) and loads the
operator reliability results into it. No credentials are used, since
SQLite connects directly to a local file rather than a server.
"""

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import resolve_path

_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection(config: dict) -> sqlite3.Connection:
    """Open (creating if needed) the SQLite database file configured in settings.yaml."""
    db_path = resolve_path(config["database"]["path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def apply_schema(conn: sqlite3.Connection) -> None:
    """Create the operator_reliability table if it doesn't already exist."""
    with open(_SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()


def load_operator_reliability(
    conn: sqlite3.Connection, df: pd.DataFrame, config: dict
) -> None:
    """Write the operator reliability + cluster results into SQLite."""
    table_name = config["database"]["table_name"]
    df.to_sql(table_name, conn, if_exists="replace", index=False)
