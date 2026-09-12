"""
tests/test_db_connection.py
Unit tests for the centralized DB connection layer.
"""
from database.db_connection import get_db_cursor, is_database_ready


def test_database_is_ready_after_seeding():
    assert is_database_ready() is True


def test_get_db_cursor_returns_dict_like_rows():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM teams LIMIT 1")
        row = cursor.fetchone()
    assert row["team_name"] is not None  # Row behaves like a dict, not a plain tuple


def test_transaction_rolls_back_on_error():
    """A failed write inside the context manager must not leave a partial row behind."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as cnt FROM teams")
        count_before = cursor.fetchone()["cnt"]

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO teams (team_name, country) VALUES ('Rollback Test', 'X')")
            cursor.execute("INSERT INTO teams (team_name, country) VALUES ('Rollback Test', 'X')")
            # second insert violates the UNIQUE constraint on team_name -> should roll back BOTH
    except Exception:
        pass

    with get_db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as cnt FROM teams")
        count_after = cursor.fetchone()["cnt"]

    assert count_after == count_before  # proves rollback undid the first insert too


def test_foreign_keys_are_enforced():
    """SQLite doesn't enforce FKs by default - confirms our PRAGMA actually took effect."""
    import sqlite3
    import pytest as pt

    with pt.raises(sqlite3.IntegrityError):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO matches (team1_id, team2_id, match_date) VALUES (9999, 9998, '2024-01-01')"
            )
