"""
config.py
Centralized configuration. This is the ONLY file that should read
environment variables directly. Every other module receives config
as function arguments or imports these constants.
"""
import os
from pathlib import Path

# Load .env if python-dotenv is installed (optional, done at import time)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional in dev; env vars can be set directly too

BASE_DIR = Path(__file__).resolve().parent

# --- Database config ---
# DB_TYPE lets us swap SQLite -> MySQL/Postgres later without touching
# any other file, per the "database-agnostic" requirement.
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # sqlite | mysql | postgres
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "data" / "cricbuzz.db"))

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "cricbuzz_livestats"),
}

# --- API config ---
CRICBUZZ_API_KEY = os.getenv("CRICBUZZ_API_KEY", "")
CRICBUZZ_API_HOST = os.getenv("CRICBUZZ_API_HOST", "cricbuzz-cricket.p.rapidapi.com")
