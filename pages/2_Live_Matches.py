"""
pages/2_Live_Matches.py

Displays live/recent matches by calling the Cricbuzz API through
services/match_service.py. Never calls the API client or DB directly.
"""
import streamlit as st
import pandas as pd

from services.match_service import get_live_matches
from utils.db_guard import require_database_ready

st.set_page_config(page_title="Live Matches", page_icon="🔴", layout="wide")
st.title("🔴 Live Matches")

require_database_ready()

st.caption(
    "Fetches live match data from the Cricbuzz API and saves a snapshot "
    "to the database. Cached for 60 seconds to respect API rate limits."
)


@st.cache_data(ttl=60)
def fetch_live_matches_cached():
    return get_live_matches()


col_a, col_b = st.columns([1, 5])
with col_a:
    if st.button("🔄 Refresh now"):
        fetch_live_matches_cached.clear()

matches = fetch_live_matches_cached()

if not matches:
    st.info(
        "No live match data available right now. This could mean:\n"
        "- No matches are currently live/recent\n"
        "- The `CRICBUZZ_API_KEY` isn't configured in `.env`\n"
        "- The API rate limit was hit — try again shortly"
    )
else:
    for m in matches:
        with st.container(border=True):
            c1, c2 = st.columns([3, 2])
            with c1:
                st.subheader(f"{m['team1']} vs {m['team2']}")
                st.caption(f"{m['series_name']} — {m['match_desc']} ({m['match_format']})")
                st.text(f"📍 {m['venue']}, {m['city']}")
            with c2:
                st.metric(m['team1'], m['team1_score'])
                st.metric(m['team2'], m['team2_score'])
            st.markdown(f"**Status:** {m['status']}")

    st.divider()
    st.markdown("#### All matches (table view)")
    df = pd.DataFrame(matches)[
        ["team1", "team2", "match_desc", "match_format", "venue", "status"]
    ]
    st.dataframe(df, width='stretch', hide_index=True)