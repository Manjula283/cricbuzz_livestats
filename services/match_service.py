"""
services/match_service.py

Orchestration layer for match data: ties together the API client,
the response parser, and the database — so Streamlit pages only ever
call simple functions like get_live_matches() without knowing HOW
the data was fetched or stored.
"""
import logging
import sqlite3

from api.cricbuzz_client import CricbuzzClient
from api.response_parser import parse_live_matches
from database.db_connection import get_db_cursor
from utils.exceptions import APIError

logger = logging.getLogger(__name__)


def get_or_create_team(cursor, team_name: str, country: str = None) -> int:
    """
    Looks up a team by name; inserts it if it doesn't exist yet.
    Returns the team_id either way. This is the standard "get-or-create"
    pattern for reconciling external API data with our own primary keys.

    team_name has a UNIQUE constraint, so if two calls race (e.g. the
    same team appears twice in one batch, or Streamlit reruns overlap),
    the INSERT can fail even though the SELECT found nothing a moment
    earlier. We catch that and re-SELECT instead of crashing.
    """
    cursor.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
    row = cursor.fetchone()
    if row:
        return row["team_id"]

    try:
        cursor.execute(
            "INSERT INTO teams (team_name, country) VALUES (?, ?)",
            (team_name, country or team_name),
        )
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Someone else inserted this team name between our SELECT and INSERT.
        cursor.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
        row = cursor.fetchone()
        if row:
            return row["team_id"]
        raise  # genuinely unexpected — re-raise so it's not silently swallowed


def get_or_create_venue(cursor, venue_name: str, city: str = "") -> int:
    """
    Same get-or-create pattern as teams. venue_name has no UNIQUE
    constraint in the current schema, so this can't hit the same
    race today — but the guard is here in case that changes later.
    """
    cursor.execute("SELECT venue_id FROM venues WHERE venue_name = ?", (venue_name,))
    row = cursor.fetchone()
    if row:
        return row["venue_id"]

    try:
        cursor.execute(
            "INSERT INTO venues (venue_name, city, country, capacity) VALUES (?, ?, ?, ?)",
            (venue_name, city, "", None),
        )
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute("SELECT venue_id FROM venues WHERE venue_name = ?", (venue_name,))
        row = cursor.fetchone()
        if row:
            return row["venue_id"]
        raise


def save_live_matches(parsed_matches: list[dict]) -> int:
    """
    Saves parsed live matches into the matches table.
    Deduplicates on (team1_id, team2_id, match_description) so repeated
    polling of the live endpoint doesn't create duplicate rows every
    refresh. Returns count of NEW matches inserted (existing ones are
    skipped).
    """
    inserted_count = 0
    with get_db_cursor(commit=True) as cursor:
        for m in parsed_matches:
            team1_id = get_or_create_team(cursor, m["team1"])
            team2_id = get_or_create_team(cursor, m["team2"])
            venue_id = get_or_create_venue(cursor, m["venue"], m.get("city", ""))

            # Dedup check: has this fixture already been stored?
            cursor.execute(
                """SELECT match_id FROM matches
                   WHERE team1_id = ? AND team2_id = ? AND match_description = ?""",
                (team1_id, team2_id, m["match_desc"]),
            )
            if cursor.fetchone():
                continue  # already stored, skip

            cursor.execute(
                """INSERT INTO matches
                   (team1_id, team2_id, venue_id, match_date, match_format,
                    match_description, match_status)
                   VALUES (?, ?, ?, date('now'), ?, ?, 'live')""",
                (team1_id, team2_id, venue_id, m["match_format"], m["match_desc"]),
            )
            inserted_count += 1

    logger.info(f"Saved {inserted_count} new live matches to DB.")
    return inserted_count


def get_live_matches() -> list[dict]:
    """
    The ONE function Streamlit pages should call. Fetches from API,
    parses, saves a snapshot to DB, and returns clean data for display.
    Gracefully returns an empty list (with a logged error) if the API
    call fails, instead of crashing the page.
    """
    try:
        client = CricbuzzClient()
        raw = client.get_live_matches()
        parsed = parse_live_matches(raw)
        save_live_matches(parsed)
        return parsed
    except APIError as e:
        logger.error(f"Failed to fetch live matches: {e}")
        return []