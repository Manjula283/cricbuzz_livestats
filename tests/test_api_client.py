"""
tests/test_api_client.py

Tests the API client and parser using MOCKED HTTP responses -
no real network call to Cricbuzz/RapidAPI is made. This is the
correct way to test third-party API integrations: fast, reliable,
runs in CI without secrets, and doesn't burn your rate limit.
"""
import pytest
import requests
from unittest.mock import MagicMock, patch

from api.cricbuzz_client import CricbuzzClient
from api.response_parser import parse_live_matches
from utils.exceptions import APIError


def _mock_response(status_code=200, json_data=None, raise_json_error=False):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    if raise_json_error:
        mock_resp.json.side_effect = ValueError("Invalid JSON")
    else:
        mock_resp.json.return_value = json_data or {}
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_resp)
    else:
        mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_successful_live_matches_call():
    client = CricbuzzClient()
    with patch.object(client.session, "get", return_value=_mock_response(200, {"typeMatches": []})):
        result = client.get_live_matches()
    assert result == {"typeMatches": []}


def test_401_raises_clean_api_error():
    client = CricbuzzClient()
    with patch.object(client.session, "get", return_value=_mock_response(401)):
        with pytest.raises(APIError, match="Invalid or missing"):
            client.get_live_matches()


def test_429_raises_rate_limit_error():
    client = CricbuzzClient()
    with patch.object(client.session, "get", return_value=_mock_response(429)):
        with pytest.raises(APIError, match="rate limit"):
            client.get_live_matches()


def test_timeout_raises_api_error():
    client = CricbuzzClient()
    with patch.object(client.session, "get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(APIError, match="timed out"):
            client.get_live_matches()


def test_connection_error_raises_api_error():
    client = CricbuzzClient()
    with patch.object(client.session, "get", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(APIError, match="Could not connect"):
            client.get_live_matches()


def test_malformed_json_raises_api_error():
    client = CricbuzzClient()
    with patch.object(client.session, "get", return_value=_mock_response(200, raise_json_error=True)):
        with pytest.raises(APIError, match="malformed JSON"):
            client.get_live_matches()


def test_parser_handles_missing_score_gracefully():
    """A match with no matchScore yet (upcoming fixture) must not crash the parser."""
    raw = {
        "typeMatches": [{
            "seriesMatches": [{
                "seriesAdWrapper": {
                    "seriesId": 1, "seriesName": "Test Series",
                    "matches": [{
                        "matchInfo": {
                            "matchId": 1, "matchDesc": "1st ODI", "matchFormat": "ODI",
                            "team1": {"teamName": "India"}, "team2": {"teamName": "Australia"},
                            "venueInfo": {"ground": "Test Venue", "city": "Test City"},
                            "status": "Match not started",
                        },
                        "matchScore": {},
                    }],
                }
            }]
        }]
    }
    result = parse_live_matches(raw)
    assert len(result) == 1
    assert result[0]["team1_score"] == "Yet to bat"
