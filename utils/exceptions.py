"""
utils/exceptions.py
Custom exception classes so callers can catch specific, meaningful
errors instead of bare `except Exception`.
"""


class APIError(Exception):
    """Raised when the Cricbuzz API call fails for any reason
    (timeout, connection, bad status code, malformed JSON)."""
    pass


class DBError(Exception):
    """Raised for database-layer failures not already handled
    by db_connection's rollback logic."""
    pass


class ValidationError(Exception):
    """Raised when CRUD form input fails validation rules."""
    pass
