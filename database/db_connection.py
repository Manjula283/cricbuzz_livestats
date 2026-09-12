"""
database/db_connection.py

Single centralized place for all database connections.
No other file in the project should call sqlite3.connect() or
mysql.connector.connect() directly — everyone goes through here.

This is what makes the app "database-agnostic": swapping DB_TYPE
in config.py is enough to point the whole app at a different engine.
"""
import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def get_connection():
    """
    Returns a raw DB connection based on config.DB_TYPE.
    Callers are responsible for closing it, OR (preferred) use
    get_db_cursor() context manager below instead of calling this directly.
    """
    if config.DB_TYPE == "sqlite":
        # Ensure the data/ folder exists before connecting
        Path(config.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(config.SQLITE_DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")   # SQLite needs this explicitly
        conn.row_factory = sqlite3.Row              # rows behave like dicts
        return conn

    elif config.DB_TYPE == "mysql":
        import mysql.connector
        return mysql.connector.connect(**config.MYSQL_CONFIG)

    elif config.DB_TYPE == "postgres":
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(
            host=config.MYSQL_CONFIG["host"],
            user=config.MYSQL_CONFIG["user"],
            password=config.MYSQL_CONFIG["password"],
            dbname=config.MYSQL_CONFIG["database"],
        )
        return conn

    else:
        raise ValueError(f"Unsupported DB_TYPE: {config.DB_TYPE}")


@contextmanager
def get_db_cursor(commit: bool = False):
    """
    Context manager for safe DB access with automatic commit/rollback
    and guaranteed connection closing — even if an exception occurs.

    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO players (...) VALUES (...)", params)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error, rolled back: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def initialize_database(schema_path: str = None):
    """
    Runs schema.sql against the configured database.
    Safe to call multiple times (schema.sql uses IF NOT EXISTS).
    """
    if schema_path is None:
        schema_path = str(Path(__file__).parent / "schema.sql")

    with open(schema_path, "r") as f:
        schema_script = f.read()

    conn = get_connection()
    try:
        conn.executescript(schema_script)   # sqlite3-specific: runs multi-statement SQL
        conn.commit()
        logger.info("Database schema initialized successfully.")
    finally:
        conn.close()


def is_database_ready() -> bool:
    """
    Checks whether the core schema actually exists yet.
    Used by Streamlit pages to show a friendly setup message instead
    of crashing with a raw 'no such table' traceback on first run.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='players'"
            )
            return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        return False
