"""
app.py — Home page / Streamlit entry point.

Streamlit's multipage convention: this file IS the first page shown.
Additional pages live in pages/ and appear in the sidebar automatically,
ordered by their filename prefix (2_, 3_, 4_, 5_...).
"""
import streamlit as st

import config
from utils.logger import setup_logging
from utils.db_guard import require_database_ready
from services.crud_service import get_all_players, get_all_matches

setup_logging()

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)

st.title("🏏 Cricbuzz LiveStats")
st.markdown("### Real-Time Cricket Insights & SQL-Based Analytics")

st.markdown("""
This dashboard combines **live Cricbuzz API data** with a **SQL database**
to deliver cricket analytics, player stats, and 25 practice SQL queries —
all in one interactive app.
""")

st.divider()

require_database_ready()

# --- Quick stats row (proves DB connectivity on the landing page) ---
col1, col2, col3 = st.columns(3)

with col1:
    player_count = len(get_all_players())
    st.metric("Players in Database", player_count)

with col2:
    match_count = len(get_all_matches())
    st.metric("Matches Tracked", match_count)

with col3:
    api_status = "✅ Configured" if config.CRICBUZZ_API_KEY else "⚠️ Not set"
    st.metric("Cricbuzz API Key", api_status)

st.divider()

st.markdown("""
#### Navigate using the sidebar:
- 🔴 **Live Matches** — real-time scores fetched from the Cricbuzz API
- 📊 **Top Player Stats** — leaderboards and career summaries
- 🧮 **SQL Analytics** — all 25 practice SQL queries, run live against the DB
- 🛠️ **CRUD Operations** — add, update, or remove player and match records

#### Built with
Python · SQLite · Streamlit · Cricbuzz REST API · pandas · Plotly
""")

if not config.CRICBUZZ_API_KEY:
    st.warning(
        "No `CRICBUZZ_API_KEY` found in your `.env` file. The Live Matches page "
        "will show a friendly error until you add one — everything else (DB-backed "
        "pages) works without it."
    )
