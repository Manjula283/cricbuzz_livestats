"""
services/analytics_service.py

Executes the 25 SQL practice queries (sql/queries.py) against the
database and returns results as a list of dicts (ready for
pandas.DataFrame / st.dataframe in the Streamlit Analytics page).
"""
import logging

from database.db_connection import get_db_cursor
from sql.queries import QUERIES
from utils.exceptions import DBError

logger = logging.getLogger(__name__)


def run_query(question_number: int) -> list[dict]:
    """
    Runs one of the 25 practice queries by its number (1-25).
    Raises DBError with a clear message if the query fails or the
    question number doesn't exist.
    """
    if question_number not in QUERIES:
        raise DBError(f"No query defined for question {question_number}.")

    try:
        with get_db_cursor() as cursor:
            cursor.execute(QUERIES[question_number])
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Query {question_number} failed: {e}")
        raise DBError(f"Query {question_number} failed: {e}")


def list_available_questions() -> list[int]:
    return sorted(QUERIES.keys())
