"""
dashboard.py
------------
Streamlit dashboard for exploring operator performance results.
Reads from the project's SQLite database (via src.db) and its
configured settings (via src.config), consistent with the rest of
this modular pipeline - no hardcoded paths.

Run from the project root with:
    streamlit run dashboard.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.config import load_config
from src.db.load_db import get_connection

st.set_page_config(page_title="Operator Performance Benchmarking", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #E8F4FD;
    }
    section[data-testid="stSidebar"] {
        background-color: #D0E8FA;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Operator Performance Benchmarking")
st.caption("West Midlands bus operators, ranked by service consistency (headway variance)")


@st.cache_data
def load_data():
    config = load_config()
    conn = get_connection(config)
    table_name = config["database"]["table_name"]
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)  # noqa: S608 - table name from trusted config, not user input
    conn.close()
    return df


df = load_data()

if df.empty:
    st.warning(
        "No data found in the database yet. Run `python main.py` first to "
        "populate it, then reload this dashboard."
    )
    st.stop()

# --- Sidebar: operator picker ---
st.sidebar.header("Select an operator")
operator_names = sorted(df["agency_name"].unique())
selected_operator = st.sidebar.selectbox("Operator", operator_names)

selected_row = df[df["agency_name"] == selected_operator].iloc[0]

# --- Main: selected operator's stats ---
col1, col2, col3 = st.columns(3)
col1.metric("Performance tier", selected_row["performance_tier"])
col2.metric("Avg headway (sec)", f"{selected_row['avg_headway_sec']:.0f}")
col3.metric("Headway std dev (sec)", f"{selected_row['headway_stddev_sec']:.0f}")

st.divider()

# --- Comparison chart: all operators, coloured by tier ---
st.subheader("How this operator compares to all others")

fig, ax = plt.subplots(figsize=(9, 6))
for tier, group in df.groupby("performance_tier"):
    ax.scatter(group["avg_headway_sec"], group["headway_stddev_sec"], label=tier, alpha=0.7)

ax.scatter(
    selected_row["avg_headway_sec"],
    selected_row["headway_stddev_sec"],
    color="black",
    s=200,
    marker="*",
    label=f"Selected: {selected_operator}",
)

ax.set_xlabel("Average headway (seconds)")
ax.set_ylabel("Headway standard deviation (seconds)")
ax.legend()
st.pyplot(fig)

st.divider()

# --- Full table, filterable by tier ---
st.subheader("All operators")
tier_filter = st.multiselect(
    "Filter by performance tier",
    options=sorted(df["performance_tier"].unique()),
    default=sorted(df["performance_tier"].unique()),
)
st.dataframe(
    df[df["performance_tier"].isin(tier_filter)].sort_values("headway_stddev_sec"),
    use_container_width=True,
)