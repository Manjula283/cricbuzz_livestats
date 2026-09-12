"""
pages/3_Top_Player_Stats.py

Career leaderboards using the v_player_batting_summary view (Phase 8)
and the players table. Read-only page, calls database via a small
local query function (kept simple since this is pure reporting,
not CRUD — no need to route through crud_service.py for reads-only
aggregate views).
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from database.db_connection import get_db_cursor
from utils.db_guard import require_database_ready

st.set_page_config(page_title="Top Player Stats", page_icon="📊", layout="wide")
st.title("📊 Top Player Stats")

require_database_ready()


@st.cache_data(ttl=300)
def get_batting_leaderboard(country_filter: str = None) -> list[dict]:
    query = "SELECT * FROM v_player_batting_summary"
    params = ()
    if country_filter and country_filter != "All":
        query += " WHERE country = ?"
        params = (country_filter,)
    query += " ORDER BY total_runs DESC"

    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


@st.cache_data(ttl=300)
def get_countries() -> list[str]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT DISTINCT country FROM players ORDER BY country")
        return [row["country"] for row in cursor.fetchall()]


country_options = ["All"] + get_countries()
selected_country = st.selectbox("Filter by country", country_options)

leaderboard = get_batting_leaderboard(selected_country)

if not leaderboard:
    st.info("No player data available yet — run the seed script first.")
else:
    df = pd.DataFrame(leaderboard)

    col1, col2, col3 = st.columns(3)
    with col1:
        top_scorer = df.iloc[0]
        st.metric("Top Run Scorer", top_scorer["full_name"], f"{top_scorer['total_runs']} runs")
    with col2:
        best_avg = df.sort_values("avg_runs_per_innings", ascending=False).iloc[0]
        st.metric("Best Average", best_avg["full_name"], f"{best_avg['avg_runs_per_innings']}")
    with col3:
        best_sr = df.sort_values("strike_rate", ascending=False).iloc[0]
        st.metric("Best Strike Rate", best_sr["full_name"], f"{best_sr['strike_rate']}")

    st.divider()
    st.markdown("#### Full Leaderboard")
    st.dataframe(
        df.rename(columns={
            "full_name": "Player", "country": "Country",
            "matches_played": "Matches", "total_runs": "Runs",
            "highest_score": "HS", "avg_runs_per_innings": "Avg",
            "strike_rate": "SR",
        }),
        width='stretch', hide_index=True,
    )

    st.divider()
    st.markdown("#### Top 10 by Total Runs")
    chart_df = df.head(10).set_index("full_name")["total_runs"]
    st.bar_chart(chart_df)

    st.divider()
    st.markdown("#### Player Archetypes: Average vs Strike Rate")
    st.caption(
        "Two players can have identical total runs but very different playing "
        "styles. This scatter reveals that — bottom-right = high average, "
        "low strike rate ('anchor'); top-left = low average, high strike rate "
        "('finisher'); top-right = both high ('complete batter')."
    )
    scatter_fig = px.scatter(
        df, x="strike_rate", y="avg_runs_per_innings",
        size="total_runs", color="country", hover_name="full_name",
        labels={"strike_rate": "Strike Rate", "avg_runs_per_innings": "Batting Average"},
    )
    st.plotly_chart(scatter_fig, width='stretch')
