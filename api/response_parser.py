"""
api/response_parser.py

Flattens Cricbuzz's deeply nested JSON responses into simple flat
dicts/lists that the rest of the app (services, Streamlit pages) can
use without knowing anything about the API's internal JSON structure.

Every field access uses .get() with a default — API responses are
never 100% guaranteed to contain every key (e.g. a match that hasn't
started yet won't have score data), so we must never assume a key exists.
"""
import logging

logger = logging.getLogger(__name__)


def parse_live_matches(raw_json: dict) -> list[dict]:
    """
    Input:  raw response from CricbuzzClient.get_live_matches()
    Output: list of flat dicts, one per match, e.g.:
        {
            "match_id": 12345,
            "series_id": 678,
            "series_name": "...",
            "match_desc": "1st ODI",
            "match_format": "ODI",
            "team1": "India",
            "team2": "Australia",
            "venue": "Wankhede Stadium",
            "city": "Mumbai",
            "status": "India won by 6 wickets",
            "team1_score": "289/7 (50)",
            "team2_score": "290/4 (48.2)",
        }
    """
    parsed_matches = []

    type_matches = raw_json.get("typeMatches", [])
    for type_match in type_matches:
        series_matches = type_match.get("seriesMatches", [])
        for series_match in series_matches:
            wrapper = series_match.get("seriesAdWrapper", {})
            series_id = wrapper.get("seriesId")
            series_name = wrapper.get("seriesName", "")
            matches = wrapper.get("matches", [])

            for match in matches:
                match_info = match.get("matchInfo", {})
                match_score = match.get("matchScore", {})

                team1_info = match_info.get("team1", {})
                team2_info = match_info.get("team2", {})
                venue_info = match_info.get("venueInfo", {})

                parsed_matches.append({
                    "match_id": match_info.get("matchId"),
                    "series_id": series_id,
                    "series_name": series_name,
                    "match_desc": match_info.get("matchDesc", ""),
                    "match_format": match_info.get("matchFormat", ""),
                    "start_date": match_info.get("startDate", ""),
                    "team1": team1_info.get("teamName", "Unknown"),
                    "team2": team2_info.get("teamName", "Unknown"),
                    "venue": venue_info.get("ground", "Unknown"),
                    "city": venue_info.get("city", ""),
                    "status": match_info.get("status", ""),
                    "team1_score": _extract_score(match_score, "team1Score"),
                    "team2_score": _extract_score(match_score, "team2Score"),
                })

    logger.info(f"Parsed {len(parsed_matches)} matches from API response.")
    return parsed_matches


def _extract_score(match_score: dict, team_key: str) -> str:
    """
    Score data is nested per-innings (inngs1, inngs2 for Tests).
    Defensively builds a human-readable string like '289/7 (50 ov)'.
    """
    team_score = match_score.get(team_key, {})
    if not team_score:
        return "Yet to bat"

    innings_summaries = []
    for innings_key, innings_data in team_score.items():
        runs = innings_data.get("runs", 0)
        wickets = innings_data.get("wickets", 0)
        overs = innings_data.get("overs", 0)
        innings_summaries.append(f"{runs}/{wickets} ({overs} ov)")

    return " & ".join(innings_summaries) if innings_summaries else "Yet to bat"
