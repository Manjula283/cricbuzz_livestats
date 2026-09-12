"""
pages/5_CRUD_Operations.py

Form-based CRUD UI for players and matches, wired entirely through
services/crud_service.py. This page contains NO SQL — only form
handling and calls to already-validated, transactional service functions.
"""
import streamlit as st
import pandas as pd

from services.crud_service import (
    create_player, get_all_players, update_player, delete_player,
    create_match, get_all_matches, delete_match,
)
from utils.exceptions import ValidationError, DBError
from utils.db_guard import require_database_ready

st.set_page_config(page_title="CRUD Operations", page_icon="🛠️", layout="wide")
st.title("🛠️ CRUD Operations")

require_database_ready()

tab_players, tab_matches = st.tabs(["👤 Players", "🏟️ Matches"])

# ============================================================
# PLAYERS TAB
# ============================================================
with tab_players:
    st.markdown("#### Add a new player")
    with st.form("add_player_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full name")
            country = st.text_input("Country")
        with c2:
            playing_role = st.selectbox(
                "Playing role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
            )
            batting_style = st.text_input("Batting style", value="Right-hand bat")
        bowling_style = st.text_input("Bowling style", value="")

        submitted = st.form_submit_button("Add Player")
        if submitted:
            try:
                new_id = create_player({
                    "full_name": full_name, "country": country,
                    "playing_role": playing_role, "batting_style": batting_style,
                    "bowling_style": bowling_style,
                })
                st.success(f"Player added (ID {new_id}).")
                st.cache_data.clear()
            except ValidationError as e:
                st.error(f"Validation error: {e}")
            except DBError as e:
                st.error(f"Database error: {e}")

    st.divider()
    st.markdown("#### Existing players")

    players = get_all_players()
    if players:
        df = pd.DataFrame(players)
        st.dataframe(df, width='stretch', hide_index=True)

        st.markdown("#### Update or delete a player")
        player_map = {f"{p['full_name']} (ID {p['player_id']})": p for p in players}
        selected_label = st.selectbox("Select player", list(player_map.keys()))
        selected_player = player_map[selected_label]

        with st.form("edit_player_form"):
            e1, e2 = st.columns(2)
            with e1:
                edit_name = st.text_input("Full name", value=selected_player["full_name"])
                edit_country = st.text_input("Country", value=selected_player["country"])
            with e2:
                roles = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
                current_role_idx = roles.index(selected_player["playing_role"]) if selected_player["playing_role"] in roles else 0
                edit_role = st.selectbox("Playing role", roles, index=current_role_idx)
                edit_batting = st.text_input("Batting style", value=selected_player.get("batting_style") or "")

            col_update, col_delete = st.columns(2)
            with col_update:
                if st.form_submit_button("💾 Update"):
                    try:
                        update_player(selected_player["player_id"], {
                            "full_name": edit_name, "country": edit_country,
                            "playing_role": edit_role, "batting_style": edit_batting,
                            "bowling_style": selected_player.get("bowling_style"),
                        })
                        st.success("Player updated.")
                        st.rerun()
                    except (ValidationError, DBError) as e:
                        st.error(str(e))
            with col_delete:
                if st.form_submit_button("🗑️ Delete", type="secondary"):
                    try:
                        delete_player(selected_player["player_id"])
                        st.success("Player deleted.")
                        st.rerun()
                    except DBError as e:
                        st.error(str(e))
    else:
        st.info("No players in the database yet.")

# ============================================================
# MATCHES TAB
# ============================================================
with tab_matches:
    st.markdown("#### Add a new match")

    players_for_teams = get_all_players()  # reused just to check DB is reachable
    with st.form("add_match_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            team1_id = st.number_input("Team 1 ID", min_value=1, step=1)
            team2_id = st.number_input("Team 2 ID", min_value=1, step=1)
            venue_id = st.number_input("Venue ID", min_value=1, step=1)
        with c2:
            match_format = st.selectbox("Format", ["Test", "ODI", "T20I"])
            match_date = st.date_input("Match date")
            match_description = st.text_input("Match description")

        submitted_match = st.form_submit_button("Add Match")
        if submitted_match:
            try:
                new_match_id = create_match({
                    "team1_id": int(team1_id), "team2_id": int(team2_id),
                    "venue_id": int(venue_id), "match_format": match_format,
                    "match_date": match_date.isoformat(),
                    "match_description": match_description,
                    "match_status": "upcoming",
                })
                st.success(f"Match added (ID {new_match_id}).")
                st.cache_data.clear()
            except ValidationError as e:
                st.error(f"Validation error: {e}")
            except DBError as e:
                st.error(f"Database error: {e}")

    st.caption("Tip: check the Top Player Stats / SQL Analytics pages for valid team/venue IDs.")

    st.divider()
    st.markdown("#### Existing matches")
    matches = get_all_matches()
    if matches:
        df_m = pd.DataFrame(matches)
        st.dataframe(df_m, width='stretch', hide_index=True)

        match_map = {f"{m['team1']} vs {m['team2']} ({m['match_date']}) - ID {m['match_id']}": m for m in matches}
        selected_match_label = st.selectbox("Select match to delete", list(match_map.keys()))
        if st.button("🗑️ Delete selected match"):
            try:
                delete_match(match_map[selected_match_label]["match_id"])
                st.success("Match deleted.")
                st.rerun()
            except DBError as e:
                st.error(str(e))
    else:
        st.info("No matches in the database yet.")
