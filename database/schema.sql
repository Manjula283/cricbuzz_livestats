-- =====================================================
-- Cricbuzz LiveStats — Database Schema
-- Target: SQLite (dev). Kept ANSI-SQL-close for portability
-- to MySQL/PostgreSQL with minor type tweaks.
-- =====================================================

CREATE TABLE IF NOT EXISTS teams (
    team_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name   VARCHAR(100) NOT NULL UNIQUE,
    country     VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name  VARCHAR(150) NOT NULL,
    city        VARCHAR(100),
    country     VARCHAR(100),
    capacity    INTEGER
);

CREATE TABLE IF NOT EXISTS players (
    player_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     VARCHAR(100) NOT NULL,
    country       VARCHAR(100) NOT NULL,
    playing_role  VARCHAR(50) CHECK (playing_role IN ('Batsman','Bowler','All-rounder','Wicket-keeper')),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS series (
    series_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name   VARCHAR(150) NOT NULL,
    host_country  VARCHAR(100),
    match_type    VARCHAR(20) CHECK (match_type IN ('Test','ODI','T20I')),
    start_date    DATE,
    total_matches INTEGER
);

CREATE TABLE IF NOT EXISTS matches (
    match_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id         INTEGER REFERENCES series(series_id),
    team1_id          INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id          INTEGER NOT NULL REFERENCES teams(team_id),
    venue_id          INTEGER REFERENCES venues(venue_id),
    match_date        DATE NOT NULL,
    match_format      VARCHAR(20) CHECK (match_format IN ('Test','ODI','T20I')),
    match_description VARCHAR(200),
    toss_winner_id    INTEGER REFERENCES teams(team_id),
    toss_decision     VARCHAR(10) CHECK (toss_decision IN ('bat','bowl')),
    winner_team_id    INTEGER REFERENCES teams(team_id),
    victory_margin    INTEGER,
    victory_type      VARCHAR(10) CHECK (victory_type IN ('runs','wickets')),
    match_status      VARCHAR(20) DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS batting_performances (
    batting_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id         INTEGER NOT NULL REFERENCES matches(match_id),
    player_id        INTEGER NOT NULL REFERENCES players(player_id),
    team_id          INTEGER NOT NULL REFERENCES teams(team_id),
    innings_number   INTEGER NOT NULL,
    batting_position INTEGER,
    runs_scored      INTEGER DEFAULT 0 CHECK (runs_scored >= 0),
    balls_faced      INTEGER DEFAULT 0,
    fours            INTEGER DEFAULT 0,
    sixes            INTEGER DEFAULT 0,
    is_out           BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS bowling_performances (
    bowling_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER NOT NULL REFERENCES matches(match_id),
    player_id       INTEGER NOT NULL REFERENCES players(player_id),
    team_id         INTEGER NOT NULL REFERENCES teams(team_id),
    innings_number  INTEGER NOT NULL,
    overs_bowled    REAL CHECK (overs_bowled >= 0),
    runs_conceded   INTEGER DEFAULT 0,
    wickets_taken   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fielding_performances (
    fielding_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id     INTEGER NOT NULL REFERENCES matches(match_id),
    player_id    INTEGER NOT NULL REFERENCES players(player_id),
    catches      INTEGER DEFAULT 0,
    stumpings    INTEGER DEFAULT 0,
    run_outs     INTEGER DEFAULT 0
);

-- =====================================================
-- Indexes (tied to actual query patterns from the 25 SQL Qs)
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_format ON matches(match_format);
CREATE INDEX IF NOT EXISTS idx_batting_match_innings ON batting_performances(match_id, innings_number, batting_position);
CREATE INDEX IF NOT EXISTS idx_batting_player ON batting_performances(player_id);
CREATE INDEX IF NOT EXISTS idx_bowling_player_match ON bowling_performances(player_id, match_id);

-- =====================================================
-- Views (reusable "pre-joined" shortcuts — used by Streamlit pages
-- for quick reads without repeating the same JOIN everywhere)
-- =====================================================

-- View 1: Match summary with team/venue names resolved (no raw FK ids)
CREATE VIEW IF NOT EXISTS v_match_summary AS
SELECT
    m.match_id,
    m.match_description,
    t1.team_name AS team1,
    t2.team_name AS team2,
    v.venue_name,
    v.city,
    m.match_date,
    m.match_format,
    w.team_name AS winner,
    m.victory_margin,
    m.victory_type
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
LEFT JOIN venues v ON m.venue_id = v.venue_id
LEFT JOIN teams w ON m.winner_team_id = w.team_id;

-- View 2: Player career batting summary (aggregated)
CREATE VIEW IF NOT EXISTS v_player_batting_summary AS
SELECT
    p.player_id,
    p.full_name,
    p.country,
    COUNT(DISTINCT bp.match_id) AS matches_played,
    SUM(bp.runs_scored) AS total_runs,
    MAX(bp.runs_scored) AS highest_score,
    ROUND(AVG(bp.runs_scored), 2) AS avg_runs_per_innings,
    ROUND(SUM(bp.runs_scored) * 100.0 / NULLIF(SUM(bp.balls_faced), 0), 2) AS strike_rate
FROM players p
JOIN batting_performances bp ON p.player_id = bp.player_id
GROUP BY p.player_id, p.full_name, p.country;
