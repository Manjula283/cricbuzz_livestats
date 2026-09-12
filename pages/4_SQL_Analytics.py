"""
pages/4_SQL_Analytics.py

The core graded deliverable: all 25 SQL practice queries, selectable
by question number, executed live via services/analytics_service.py
and shown as a table. Also shows the raw SQL for transparency/learning.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from services.analytics_service import run_query, list_available_questions
from sql.queries import QUERIES
from utils.exceptions import DBError
from utils.db_guard import require_database_ready

st.set_page_config(page_title="SQL Analytics", page_icon="🧮", layout="wide")
st.title("🧮 SQL Queries & Analytics")

require_database_ready()

QUESTION_TITLES = {
    1: "Players from India", 2: "Matches in last 30 days", 3: "Top 10 ODI run scorers",
    4: "Venues with capacity > 50,000", 5: "Match wins per team", 6: "Players per role",
    7: "Highest score per format", 8: "Series started in 2024",
    9: "All-rounders: 1000+ runs & 50+ wickets", 10: "Last 20 completed matches",
    11: "Cross-format player comparison", 12: "Home vs away performance",
    13: "Batting partnerships >= 100 runs", 14: "Bowling economy by venue",
    15: "Performance in close matches", 16: "Yearly batting trend since 2020",
    17: "Toss win -> match win advantage", 18: "Most economical limited-overs bowlers",
    19: "Batting consistency (std dev)", 20: "Format-wise stats, 20+ matches",
    21: "Weighted performance ranking", 22: "Head-to-head team analysis",
    23: "Recent form (last 10 innings)", 24: "Best partnership pairs",
    25: "Quarterly performance trajectory",
}

question_numbers = list_available_questions()
selected = st.selectbox(
    "Choose a SQL practice question",
    question_numbers,
    format_func=lambda n: f"Q{n} — {QUESTION_TITLES.get(n, '')}",
)

with st.expander("Show SQL query"):
    st.code(QUERIES[selected].strip(), language="sql")

if st.button("▶️ Run Query", type="primary"):
    try:
        results = run_query(selected)
        if not results:
            st.warning(
                "Query ran successfully but returned 0 rows. For some advanced "
                "questions (9, 20, 22, 24, 25) this is expected with the current "
                "seed dataset size — the thresholds in those questions need more "
                "historical data than our synthetic seed provides."
            )
        else:
            df = pd.DataFrame(results)
            st.success(f"{len(df)} rows returned.")
            st.dataframe(df, width='stretch', hide_index=True)

            # Q21 naturally forms a player x format grid - a heatmap shows
            # at a glance who's strong in which format, which a flat table
            # of ~68 rows makes hard to scan.
            if selected == 21:
                st.divider()
                st.markdown("#### Heatmap: Weighted Score by Player x Format")
                pivot = df.pivot_table(
                    index="full_name", columns="match_format",
                    values="total_weighted_score", aggfunc="first",
                )
                heatmap_fig = px.imshow(
                    pivot, aspect="auto", color_continuous_scale="YlOrRd",
                    labels={"color": "Weighted Score"},
                )
                st.plotly_chart(heatmap_fig, width='stretch')
    except DBError as e:
        st.error(f"Query failed: {e}")