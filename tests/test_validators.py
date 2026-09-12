"""
tests/test_validators.py
Pure unit tests for validation logic - no database needed.
"""
import pytest

from utils.validators import validate_player_data, validate_match_data, validate_id
from utils.exceptions import ValidationError


def test_valid_player_passes():
    validate_player_data({"full_name": "Test Player", "country": "India", "playing_role": "Batsman"})
    # no exception = pass


def test_empty_player_name_rejected():
    with pytest.raises(ValidationError):
        validate_player_data({"full_name": "", "country": "India"})


def test_missing_country_rejected():
    with pytest.raises(ValidationError):
        validate_player_data({"full_name": "Test Player", "country": ""})


def test_invalid_playing_role_rejected():
    with pytest.raises(ValidationError):
        validate_player_data({"full_name": "Test", "country": "India", "playing_role": "Superhero"})


def test_same_team_match_rejected():
    with pytest.raises(ValidationError):
        validate_match_data({"team1_id": 1, "team2_id": 1})


def test_invalid_match_format_rejected():
    with pytest.raises(ValidationError):
        validate_match_data({"team1_id": 1, "team2_id": 2, "match_format": "T99"})


def test_invalid_date_format_rejected():
    with pytest.raises(ValidationError):
        validate_match_data({"team1_id": 1, "team2_id": 2, "match_date": "15-06-2024"})


def test_valid_match_passes():
    validate_match_data({"team1_id": 1, "team2_id": 2, "match_format": "ODI", "match_date": "2024-06-15"})


def test_negative_id_rejected():
    with pytest.raises(ValidationError):
        validate_id(-1, "player_id")


def test_non_integer_id_rejected():
    with pytest.raises(ValidationError):
        validate_id("abc", "player_id")
