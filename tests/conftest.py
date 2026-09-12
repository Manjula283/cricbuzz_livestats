"""
tests/conftest.py

Session-wide fixture: points config.SQLITE_DB_PATH at a temporary file
and seeds it once, so the test suite never touches your real
data/cricbuzz.db (dev data stays untouched, tests are reproducible
and isolated from each other's side effects across runs).
"""
import pytest

import config


@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data") / "test_cricbuzz.db"
    config.SQLITE_DB_PATH = str(db_path)

    from database.seed_data import run_seed
    run_seed()

    yield db_path
