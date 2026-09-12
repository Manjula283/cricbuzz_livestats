"""
utils/validators.py

Validation functions for CRUD input. Each function either returns
silently (valid) or raises ValidationError with a human-readable
message that can be shown directly in a Streamlit form.

Kept separate from crud_service.py so validation rules can be reused
(tests, future API layer) without duplicating logic.
"""
from datetime import datetime

from utils.exceptions import ValidationError

VALID_ROLES = {"Batsman", "Bowler", "All-rounder", "Wicket-keeper"}
VALID_FORMATS = {"Test", "ODI", "T20I"}


def validate_player_data(data: dict) -> None:
    """
    Expected keys: full_name, country, playing_role,
                   batting_style (optional), bowling_style (optional)
    """
    if not data.get("full_name", "").strip():
        raise ValidationError("Player full name is required.")

    if len(data["full_name"].strip()) > 100:
        raise ValidationError("Player full name must be under 100 characters.")

    if not data.get("country", "").strip():
        raise ValidationError("Player country is required.")

    role = data.get("playing_role")
    if role and role not in VALID_ROLES:
        raise ValidationError(
            f"Invalid playing role '{role}'. Must be one of: {', '.join(VALID_ROLES)}"
        )


def validate_match_data(data: dict) -> None:
    """
    Expected keys: team1_id, team2_id, venue_id, match_date, match_format
    """
    if not data.get("team1_id") or not data.get("team2_id"):
        raise ValidationError("Both team1_id and team2_id are required.")

    if data["team1_id"] == data["team2_id"]:
        raise ValidationError("team1 and team2 cannot be the same team.")

    match_format = data.get("match_format")
    if match_format and match_format not in VALID_FORMATS:
        raise ValidationError(
            f"Invalid match format '{match_format}'. Must be one of: {', '.join(VALID_FORMATS)}"
        )

    match_date = data.get("match_date")
    if match_date:
        try:
            datetime.strptime(match_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("match_date must be in YYYY-MM-DD format.")


def validate_id(value, field_name: str = "id") -> None:
    """Generic positive-integer ID validator, used before UPDATE/DELETE."""
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(f"Invalid {field_name}: must be a positive integer.")
