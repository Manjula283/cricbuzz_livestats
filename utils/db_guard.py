"""
utils/db_guard.py

A small reusable guard for Streamlit pages: call this at the top of
any page that reads from the database. If the schema hasn't been
initialized/seeded yet, it AUTOMATICALLY seeds it (with a visible
spinner) instead of just showing instructions.
"""
import streamlit as st

from database.db_connection import is_database_ready


def require_database_ready() -> None:
    if not is_database_ready():
        with st.spinner("First-time setup: initializing and seeding the database..."):
            from database.seed_data import run_seed
            run_seed()
        st.rerun()