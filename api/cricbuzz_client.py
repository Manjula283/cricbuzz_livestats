"""
api/cricbuzz_client.py

Thin, defensive wrapper around the Cricbuzz REST API (via RapidAPI).
Responsibilities of this module ONLY:
  - authentication headers
  - HTTP call + retry/backoff
  - raising clean custom exceptions on failure
It does NOT parse/flatten JSON (that's response_parser.py) and does NOT
know about the database (that's services/match_service.py).
"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config
from utils.exceptions import APIError

logger = logging.getLogger(__name__)

BASE_URL = f"https://{config.CRICBUZZ_API_HOST}"


def _build_session() -> requests.Session:
    """
    Builds a requests.Session with automatic retry on transient failures.

    total=3            -> retry up to 3 times
    backoff_factor=1    -> wait 1s, 2s, 4s between retries (exponential)
    status_forcelist    -> only retry on these specific HTTP codes
                           (429 = rate limited, 500/502/503/504 = server-side issues)
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.headers.update({
        "x-rapidapi-key": config.CRICBUZZ_API_KEY,
        "x-rapidapi-host": config.CRICBUZZ_API_HOST,
    })
    return session


class CricbuzzClient:
    """
    Usage:
        client = CricbuzzClient()
        data = client.get_live_matches()
    """

    def __init__(self):
        if not config.CRICBUZZ_API_KEY:
            logger.warning("CRICBUZZ_API_KEY is empty — API calls will fail with 401/403.")
        self.session = _build_session()

    def _get(self, endpoint: str, params: dict = None, timeout: int = 10) -> dict:
        """
        Central GET method. Every public method below routes through here
        so error handling only needs to live in ONE place.
        """
        url = f"{BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()  # raises HTTPError for 4xx/5xx
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {url}")
            raise APIError(f"Cricbuzz API timed out for endpoint: {endpoint}")

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling {url}")
            raise APIError(f"Could not connect to Cricbuzz API for endpoint: {endpoint}")

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            logger.error(f"HTTP {status} error calling {url}: {e}")
            if status == 401 or status == 403:
                raise APIError("Invalid or missing Cricbuzz API key.")
            elif status == 429:
                raise APIError("Cricbuzz API rate limit exceeded. Try again later.")
            else:
                raise APIError(f"Cricbuzz API returned HTTP {status} for endpoint: {endpoint}")

        except ValueError as e:
            # response.json() raises ValueError if body isn't valid JSON
            logger.error(f"Invalid JSON from {url}: {e}")
            raise APIError(f"Cricbuzz API returned malformed JSON for endpoint: {endpoint}")

    # --- Public endpoint methods ---

    def get_live_matches(self) -> dict:
        return self._get("/matches/v1/live")

    def get_recent_matches(self) -> dict:
        return self._get("/matches/v1/recent")

    def get_upcoming_matches(self) -> dict:
        return self._get("/matches/v1/upcoming")

    def get_match_scorecard(self, match_id: int) -> dict:
        return self._get(f"/mcenter/v1/{match_id}/scard")

    def search_player(self, name: str) -> dict:
        return self._get("/stats/v1/player/search", params={"plrN": name})

    def get_player_batting_stats(self, player_id: int) -> dict:
        return self._get(f"/stats/v1/player/{player_id}/batting")

    def get_icc_rankings(self, category: str = "batsmen") -> dict:
        # category: "batsmen" | "bowlers" | "allrounders"
        return self._get(f"/stats/v1/rankings/{category}")
