"""
tests/test_pages.py

UI-level tests using streamlit.testing.v1.AppTest - the correct tool
for testing Streamlit pages (simulates a real session, unlike running
a page as a bare script, which silently no-ops st.stop()).
"""
from streamlit.testing.v1 import AppTest


def test_home_page_loads_without_exception():
    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception


def test_home_page_shows_database_metrics():
    at = AppTest.from_file("../app.py")
    at.run()
    metric_labels = [m.label for m in at.metric]
    assert "Players in Database" in metric_labels
    assert "Matches Tracked" in metric_labels


def test_top_player_stats_page_loads():
    at = AppTest.from_file("../pages/3_Top_Player_Stats.py")
    at.run(timeout=15)  # Plotly scatter rendering needs more than the 3s default
    assert not at.exception


def test_sql_analytics_page_loads_and_lists_questions():
    at = AppTest.from_file("../pages/4_SQL_Analytics.py")
    at.run()
    assert not at.exception
    assert len(at.selectbox) >= 1  # the question picker is present


def test_crud_page_loads_with_tabs():
    at = AppTest.from_file("../pages/5_CRUD_Operations.py")
    at.run()
    assert not at.exception
    assert len(at.tabs) == 2  # Players tab + Matches tab
