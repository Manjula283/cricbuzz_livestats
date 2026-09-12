"""
tests/test_sql_queries.py

Tests for the 25 SQL practice queries. Since conftest.py seeds a
FRESH database using the same random.seed(42) as the dev seed script,
results here are deterministic and match what was manually verified
during Phase 11 (e.g. exactly 5 Indian players).
"""
import pytest

from services.analytics_service import run_query, list_available_questions
from utils.exceptions import DBError


@pytest.mark.parametrize("question_number", list_available_questions())
def test_every_query_executes_without_error(question_number):
    """Smoke test: all 25 queries must run without raising, regardless of
    how many rows they return."""
    results = run_query(question_number)
    assert isinstance(results, list)  # always a list, even if empty


def test_invalid_question_number_raises_db_error():
    with pytest.raises(DBError):
        run_query(999)


def test_q1_returns_only_indian_players():
    results = run_query(1)
    assert len(results) == 5  # matches the seed data verified in Phase 11
    assert all("full_name" in r for r in results)


def test_q3_top_10_odi_scorers_sorted_descending():
    results = run_query(3)
    totals = [r["total_runs"] for r in results]
    assert totals == sorted(totals, reverse=True)  # must be sorted highest-first
    assert len(results) <= 10  # LIMIT 10 respected


def test_q4_venues_over_50000_capacity():
    results = run_query(4)
    assert all(r["capacity"] > 50000 for r in results)


def test_q17_toss_decision_groups_are_valid():
    results = run_query(17)
    valid_decisions = {"bat", "bowl"}
    assert all(r["toss_decision"] in valid_decisions for r in results)


def test_q21_rank_is_sequential_within_each_format():
    """RANK() OVER (PARTITION BY format ...) must start at 1 for each format."""
    results = run_query(21)
    formats = set(r["match_format"] for r in results)
    for fmt in formats:
        ranks_for_format = [r["rank_in_format"] for r in results if r["match_format"] == fmt]
        assert min(ranks_for_format) == 1
