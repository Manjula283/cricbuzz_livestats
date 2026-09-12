"""
services/crud_service.py

Professional CRUD operations for players and matches.

Every WRITE operation (Create/Update/Delete):
  1. validates input first (fail fast, before touching the DB)
  2. runs inside get_db_cursor(commit=True) -> auto commit/rollback
  3. catches sqlite3.IntegrityError to turn cryptic FK/constraint
     errors into human-readable messages

READ operations use commit=False (default) since they don't modify data.
"""
import logging
import sqlite3

from database.db_connection import get_db_cursor
from utils.validators import validate_player_data, validate_match_data, validate_id
from utils.exceptions import DBError, ValidationError

logger = logging.getLogger(__name__)


# ============================================================
# PLAYERS
# ============================================================

def create_player(data: dict) -> int:
    """Returns the new player_id."""
    validate_player_data(data)
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO players (full_name, country, playing_role,
                                         batting_style, bowling_style)
                   VALUES (?, ?, ?, ?, ?)""",
                (data["full_name"].strip(), data["country"].strip(),
                 data.get("playing_role"), data.get("batting_style"),
                 data.get("bowling_style")),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise DBError(f"Could not create player: {e}")


def get_player(player_id: int) -> dict | None:
    validate_id(player_id, "player_id")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_players(country: str = None) -> list[dict]:
    """Optional country filter — used by Streamlit CRUD page's search box."""
    with get_db_cursor() as cursor:
        if country:
            cursor.execute("SELECT * FROM players WHERE country = ? ORDER BY full_name", (country,))
        else:
            cursor.execute("SELECT * FROM players ORDER BY full_name")
        return [dict(row) for row in cursor.fetchall()]


def update_player(player_id: int, data: dict) -> bool:
    """Returns True if a row was actually updated, False if player_id didn't exist."""
    validate_id(player_id, "player_id")
    validate_player_data(data)

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """UPDATE players
                   SET full_name = ?, country = ?, playing_role = ?,
                       batting_style = ?, bowling_style = ?
                   WHERE player_id = ?""",
                (data["full_name"].strip(), data["country"].strip(),
                 data.get("playing_role"), data.get("batting_style"),
                 data.get("bowling_style"), player_id),
            )
            return cursor.rowcount > 0
    except sqlite3.IntegrityError as e:
        raise DBError(f"Could not update player {player_id}: {e}")


def delete_player(player_id: int) -> bool:
    """
    Deletes a player. Will fail with a clear DBError if the player has
    existing batting/bowling/fielding records (FK constraint) — this is
    intentional: silently cascading deletes on career stats is dangerous.
    """
    validate_id(player_id, "player_id")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        raise DBError(
            f"Cannot delete player {player_id}: they have existing match "
            f"performance records. Delete those first, or consider this a "
            f"data-integrity safeguard rather than a bug."
        )


# ============================================================
# MATCHES
# ============================================================

def create_match(data: dict) -> int:
    validate_match_data(data)
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO matches
                   (series_id, team1_id, team2_id, venue_id, match_date,
                    match_format, match_description, toss_winner_id,
                    toss_decision, winner_team_id, victory_margin,
                    victory_type, match_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data.get("series_id"), data["team1_id"], data["team2_id"],
                 data.get("venue_id"), data.get("match_date"), data.get("match_format"),
                 data.get("match_description"), data.get("toss_winner_id"),
                 data.get("toss_decision"), data.get("winner_team_id"),
                 data.get("victory_margin"), data.get("victory_type"),
                 data.get("match_status", "completed")),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise DBError(f"Could not create match: {e}")


def get_match(match_id: int) -> dict | None:
    validate_id(match_id, "match_id")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM v_match_summary WHERE match_id = ?", (match_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_matches(match_format: str = None) -> list[dict]:
    with get_db_cursor() as cursor:
        if match_format:
            cursor.execute(
                "SELECT * FROM v_match_summary WHERE match_format = ? ORDER BY match_date DESC",
                (match_format,),
            )
        else:
            cursor.execute("SELECT * FROM v_match_summary ORDER BY match_date DESC")
        return [dict(row) for row in cursor.fetchall()]


def update_match(match_id: int, data: dict) -> bool:
    validate_id(match_id, "match_id")
    validate_match_data(data)
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """UPDATE matches
                   SET team1_id = ?, team2_id = ?, venue_id = ?, match_date = ?,
                       match_format = ?, match_description = ?, winner_team_id = ?,
                       victory_margin = ?, victory_type = ?
                   WHERE match_id = ?""",
                (data["team1_id"], data["team2_id"], data.get("venue_id"),
                 data.get("match_date"), data.get("match_format"),
                 data.get("match_description"), data.get("winner_team_id"),
                 data.get("victory_margin"), data.get("victory_type"), match_id),
            )
            return cursor.rowcount > 0
    except sqlite3.IntegrityError as e:
        raise DBError(f"Could not update match {match_id}: {e}")


def delete_match(match_id: int) -> bool:
    validate_id(match_id, "match_id")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        raise DBError(
            f"Cannot delete match {match_id}: it has existing batting/bowling "
            f"performance records tied to it. Delete those first."
        )
