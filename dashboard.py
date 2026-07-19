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

st.set_page_config(
    page_title="Operator Performance Benchmarking",
    layout="wide",
    page_icon="🚌",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #E8F4FD;
    }
    section[data-testid="stSidebar"] {
        background-color: #D0E8FA;
    }
    span[data-baseweb="tag"] {
        background-color: #7FCDCD !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #D0E8FA;
    }
    div[data-testid="stMetricLabel"] {
        color: #4A5A6A;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #1E88E5;
    }

    /* Headings */
    h1 {
        color: #0D3B66;
        font-weight: 700;
    }
    h2, h3 {
        color: #14507A;
    }

    /* Dataframe container */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    /* Sidebar header */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2 {
        color: #0D3B66;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🚌 Operator Performance Benchmarking")
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
st.sidebar.header("🔍 Select an operator")
operator_names = sorted(df["agency_name"].unique())
selected_operator = st.sidebar.selectbox("Operator", operator_names)

st.sidebar.divider()
st.sidebar.caption(f"Total operators tracked: **{len(operator_names)}**")

selected_row = df[df["agency_name"] == selected_operator].iloc[0]

# --- Main: selected operator's stats ---
st.subheader(f"📊 {selected_operator}")
col1, col2, col3 = st.columns(3)
col1.metric("Performance tier", selected_row["performance_tier"])
col2.metric("Avg headway (sec)", f"{selected_row['avg_headway_sec']:.0f}")
col3.metric("Headway std dev (sec)", f"{selected_row['headway_stddev_sec']:.0f}")

st.divider()

# --- Comparison chart: all operators, coloured by tier ---
st.subheader("📈 How this operator compares to all others")

tier_colors = {
    tier: color
    for tier, color in zip(
        sorted(df["performance_tier"].unique()),
        ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"],
    )
}

fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor("#E8F4FD")
ax.set_facecolor("#FFFFFF")

for tier, group in df.groupby("performance_tier"):
    ax.scatter(
        group["avg_headway_sec"],
        group["headway_stddev_sec"],
        label=tier,
        alpha=0.75,
        color=tier_colors[tier],
        edgecolor="white",
        linewidth=0.5,
        s=70,
    )

ax.scatter(
    selected_row["avg_headway_sec"],
    selected_row["headway_stddev_sec"],
    color="#FFC300",
    s=260,
    marker="*",
    edgecolor="black",
    linewidth=0.8,
    label=f"Selected: {selected_operator}",
    zorder=5,
)

ax.set_xlabel("Average headway (seconds)")
ax.set_ylabel("Headway standard deviation (seconds)")
ax.grid(True, linestyle="--", alpha=0.3)
ax.legend(frameon=False)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
st.pyplot(fig)

st.divider()

# --- Full table, filterable by tier ---
st.subheader("📋 All operators")
tier_filter = st.multiselect(
    "Filter by performance tier",
    options=sorted(df["performance_tier"].unique()),
    default=sorted(df["performance_tier"].unique()),
)
st.dataframe(
    df[df["performance_tier"].isin(tier_filter)].sort_values("headway_stddev_sec"),
    width="stretch",
)