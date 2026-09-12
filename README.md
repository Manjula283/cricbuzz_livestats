# 🏏 Cricbuzz LiveStats

Real-Time Cricket Insights & SQL-Based Analytics — a Streamlit dashboard combining
live Cricbuzz API data with a SQL database for cricket analytics, player stats,
and 25 practice SQL queries.

## Features

- 🔴 **Live Matches** — real-time scores from the Cricbuzz REST API (RapidAPI)
- 📊 **Top Player Stats** — batting leaderboards, career summaries, archetype scatter plot
- 🧮 **SQL Analytics** — all 25 practice SQL queries (beginner → advanced), run live
- 🛠️ **CRUD Operations** — add/update/delete players and matches via forms
- 🏠 **Home** — project overview and live DB/API health check

## Tech Stack

Python · Streamlit · SQLite · Cricbuzz REST API · pandas · Plotly

*(MySQL/PostgreSQL are supported via a config switch but not tested in this build — see "Database Setup Details" below.)*

## Project Structure

```
cricbuzz_livestats/
├── app.py                    # Home page / entry point
├── config.py                 # Centralized configuration (reads .env)
├── requirements.txt
├── Dockerfile / Procfile     # Deployment
├── .streamlit/config.toml    # Streamlit theme/server config
│
├── database/
│   ├── db_connection.py      # Single connection point, transactions
│   ├── schema.sql            # Table definitions, views, indexes
│   └── seed_data.py          # Synthetic dataset for SQL practice
│
├── api/
│   ├── cricbuzz_client.py    # API auth, retry, error handling
│   └── response_parser.py    # Flattens nested API JSON
│
├── services/                 # Business logic layer (pages call ONLY these)
│   ├── match_service.py
│   ├── crud_service.py
│   └── analytics_service.py
│
├── sql/
│   └── queries.py            # All 25 practice SQL queries
│
├── pages/                    # Streamlit multipage app
│   ├── 2_Live_Matches.py
│   ├── 3_Top_Player_Stats.py
│   ├── 4_SQL_Analytics.py
│   └── 5_CRUD_Operations.py
│
├── utils/
│   ├── validators.py         # Input validation
│   ├── exceptions.py         # Custom exception classes
│   ├── logger.py             # Centralized logging config
│   └── db_guard.py           # Friendly "DB not seeded" page guard
│
├── tests/                    # 61 pytest tests (unit/integration/API/UI)
└── documentation/
    ├── DEPLOYMENT.md
    └── screenshots/
```

## Setup Instructions

### 1. Clone and install dependencies
```bash
git clone <your-repo-url>
cd cricbuzz_livestats
pip install -r requirements.txt
```

### 2. Configure your API key
```bash
cp .env.example .env
```
Edit `.env` and add your Cricbuzz API key:
```
CRICBUZZ_API_KEY=your_rapidapi_key_here
```

**Getting a key:** Sign up at [RapidAPI](https://rapidapi.com), subscribe to
the "Cricbuzz Cricket" API (free tier available), and copy your key from
the dashboard.

### 3. Initialize and seed the database
```bash
python -m database.seed_data
```
This creates `data/cricbuzz.db` with the schema and a synthetic dataset
(8 teams, 24 players, 20 matches, 500+ performance records) so the SQL
Analytics page has data to query immediately.

### 4. Run the app
```bash
streamlit run app.py
```
Visit `http://localhost:8501`

### 5. (Optional) Run the test suite
```bash
pip install pytest
python -m pytest tests/ -v
```

## Database Setup Details

- **Default:** SQLite, zero-config, file-based (`data/cricbuzz.db`) — this
  is the only database actually run and verified in this project (all 61
  tests, all 25 SQL queries, all 5 pages tested against SQLite).
- **To switch to MySQL/PostgreSQL:** set `DB_TYPE=mysql` (or `postgres`) in
  `.env` and fill in the corresponding credentials — `database/db_connection.py`
  has the connection logic for both, but **it has not been tested against a
  real MySQL or PostgreSQL server**. The code should work since it follows
  the same connection interface, but treat it as unverified until you've
  run it yourself.
- **Schema:** 7 tables (teams, venues, players, series, matches,
  batting/bowling/fielding_performances), 2 views (match summary, player
  batting summary), 5 indexes tuned to the actual query patterns in
  `sql/queries.py`.

## Known Limitations

- **5 of the 25 SQL queries return 0 rows against the default seed data**
  (Q9, Q20, Q22, Q24, Q25) — their thresholds (1000+ career runs, 20+
  matches, etc.) need more historical data than the 20-match synthetic
  seed provides. The query logic itself is verified correct (tested with
  lower thresholds during development); this is a data-scale limitation,
  not a bug.
- The Cricbuzz API endpoint paths in `api/cricbuzz_client.py` are based on
  the well-known "Cricbuzz Cricket" RapidAPI structure — verify against
  your own RapidAPI dashboard if endpoints have changed since.

## Future Improvements

- Authentication/role-based access for CRUD operations
- Automated historical data backfill from the API (beyond live/recent matches)
- Real-time push updates instead of polling
- ML-based match outcome prediction

## Screenshots

*(Add screenshots of each page here before submission — see `documentation/screenshots/`)*

- `home.png`
- `live_matches.png`
- `top_player_stats.png`
- `sql_analytics.png`
- `crud_operations.png`

## License

Educational project — built as a mentor-guided learning exercise.
