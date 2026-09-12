"""
utils/db_guard.py

A small reusable guard for Streamlit pages: call this at the top of
any page that reads from the database. If the schema hasn't been
initialized/seeded yet, it shows a friendly instructional message
and stops the page cleanly (st.stop()) instead of letting a raw
sqlite3.OperationalError traceback reach the user.
"""
import streamlit as st

from database.db_connection import is_database_ready


def require_database_ready() -> None:
    if not is_database_ready():
        st.error("Database not initialized yet.")
        st.info(
            "Run this once from your project's root folder, then refresh this page:\n\n"
            "```\npython -m database.seed_data\n```"
        )
        st.stop()  # halts execution of the rest of this page's script
