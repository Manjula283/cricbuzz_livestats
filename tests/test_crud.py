"""
tests/test_crud.py
Integration tests: CRUD service against the real (isolated test) database.
"""
import pytest

from services.crud_service import (
    create_player, get_player, update_player, delete_player,
    create_match, get_match, delete_match,
)
from utils.exceptions import DBError


def test_player_create_read_update_delete_cycle():
    player_id = create_player({
        "full_name": "Pytest Player", "country": "India", "playing_role": "Bowler",
    })
    assert player_id is not None

    fetched = get_player(player_id)
    assert fetched["full_name"] == "Pytest Player"

    updated = update_player(player_id, {
        "full_name": "Pytest Player", "country": "India", "playing_role": "All-rounder",
    })
    assert updated is True
    assert get_player(player_id)["playing_role"] == "All-rounder"

    deleted = delete_player(player_id)
    assert deleted is True
    assert get_player(player_id) is None


def test_delete_player_with_dependent_records_is_blocked():
    """Player 1 has batting/bowling records from the seed - deleting must fail safely."""
    with pytest.raises(DBError):
        delete_player(1)


def test_update_nonexistent_player_returns_false():
    result = update_player(999999, {
        "full_name": "Ghost", "country": "Nowhere", "playing_role": "Batsman",
    })
    assert result is False


def test_match_create_read_delete_cycle():
    match_id = create_match({
        "team1_id": 1, "team2_id": 2, "venue_id": 1,
        "match_date": "2024-06-15", "match_format": "T20I",
        "match_description": "Pytest match",
    })
    assert match_id is not None

    fetched = get_match(match_id)
    assert fetched["team1"] == "India"

    assert delete_match(match_id) is True
    assert get_match(match_id) is None
