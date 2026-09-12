"""
sql/queries.py

All 25 SQL practice queries, keyed by question number.
Each entry is the raw SQL string, executed via database/db_connection.py
by services/analytics_service.py and displayed in the Streamlit
"SQL Queries & Analytics" page.
"""

QUERIES = {

1: """
SELECT full_name, playing_role, batting_style, bowling_style
FROM players
WHERE country = 'India';
""",

2: """
SELECT
    m.match_description,
    t1.team_name AS team1,
    t2.team_name AS team2,
    v.venue_name,
    v.city,
    m.match_date
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.match_date >= DATE('now', '-30 days')
ORDER BY m.match_date DESC;
""",

3: """
SELECT
    p.full_name,
    SUM(bp.runs_scored) AS total_runs,
    ROUND(SUM(bp.runs_scored) * 1.0 /
          NULLIF(SUM(CASE WHEN bp.is_out = 1 THEN 1 ELSE 0 END), 0), 2) AS batting_average,
    SUM(CASE WHEN bp.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries
FROM batting_performances bp
JOIN players p ON bp.player_id = p.player_id
JOIN matches m ON bp.match_id = m.match_id
WHERE m.match_format = 'ODI'
GROUP BY p.player_id, p.full_name
ORDER BY total_runs DESC
LIMIT 10;
""",

4: """
SELECT venue_name, city, country, capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;
""",

5: """
SELECT t.team_name, COUNT(*) AS total_wins
FROM matches m
JOIN teams t ON m.winner_team_id = t.team_id
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;
""",

6: """
SELECT playing_role, COUNT(*) AS player_count
FROM players
GROUP BY playing_role
ORDER BY player_count DESC;
""",

7: """
SELECT m.match_format, MAX(bp.runs_scored) AS highest_score
FROM batting_performances bp
JOIN matches m ON bp.match_id = m.match_id
GROUP BY m.match_format;
""",

8: """
SELECT series_name, host_country, match_type, start_date, total_matches
FROM series
WHERE strftime('%Y', start_date) = '2024';
""",

9: """
WITH batting_totals AS (
    SELECT bp.player_id, m.match_format, SUM(bp.runs_scored) AS total_runs
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
    GROUP BY bp.player_id, m.match_format
),
bowling_totals AS (
    SELECT bw.player_id, m.match_format, SUM(bw.wickets_taken) AS total_wickets
    FROM bowling_performances bw
    JOIN matches m ON bw.match_id = m.match_id
    GROUP BY bw.player_id, m.match_format
)
SELECT p.full_name, bt.match_format, bt.total_runs, bwt.total_wickets
FROM players p
JOIN batting_totals bt ON p.player_id = bt.player_id
JOIN bowling_totals bwt ON bt.player_id = bwt.player_id AND bt.match_format = bwt.match_format
WHERE p.playing_role = 'All-rounder'
  AND bt.total_runs > 1000
  AND bwt.total_wickets > 50
ORDER BY bt.total_runs DESC;
""",

10: """
SELECT
    m.match_description,
    t1.team_name AS team1,
    t2.team_name AS team2,
    w.team_name AS winning_team,
    m.victory_margin,
    m.victory_type,
    v.venue_name
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
LEFT JOIN teams w ON m.winner_team_id = w.team_id
LEFT JOIN venues v ON m.venue_id = v.venue_id
WHERE m.match_status = 'completed'
ORDER BY m.match_date DESC
LIMIT 20;
""",

11: """
WITH format_runs AS (
    SELECT
        bp.player_id,
        SUM(CASE WHEN m.match_format = 'Test' THEN bp.runs_scored ELSE 0 END) AS test_runs,
        SUM(CASE WHEN m.match_format = 'ODI' THEN bp.runs_scored ELSE 0 END) AS odi_runs,
        SUM(CASE WHEN m.match_format = 'T20I' THEN bp.runs_scored ELSE 0 END) AS t20i_runs,
        COUNT(DISTINCT m.match_format) AS formats_played,
        SUM(bp.runs_scored) AS total_runs,
        SUM(CASE WHEN bp.is_out = 1 THEN 1 ELSE 0 END) AS dismissals
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
    GROUP BY bp.player_id
)
SELECT
    p.full_name, fr.test_runs, fr.odi_runs, fr.t20i_runs,
    ROUND(fr.total_runs * 1.0 / NULLIF(fr.dismissals, 0), 2) AS overall_batting_average
FROM format_runs fr
JOIN players p ON fr.player_id = p.player_id
WHERE fr.formats_played >= 2
ORDER BY fr.total_runs DESC;
""",

12: """
WITH team_matches AS (
    SELECT match_id, team1_id AS team_id, venue_id, winner_team_id FROM matches
    UNION ALL
    SELECT match_id, team2_id AS team_id, venue_id, winner_team_id FROM matches
),
team_venue AS (
    SELECT tm.match_id, tm.team_id, tm.winner_team_id,
           CASE WHEN t.country = v.country THEN 'Home' ELSE 'Away' END AS location_type
    FROM team_matches tm
    JOIN teams t ON tm.team_id = t.team_id
    JOIN venues v ON tm.venue_id = v.venue_id
)
SELECT
    t.team_name, tv.location_type,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN tv.winner_team_id = tv.team_id THEN 1 ELSE 0 END) AS wins
FROM team_venue tv
JOIN teams t ON tv.team_id = t.team_id
GROUP BY t.team_id, t.team_name, tv.location_type
ORDER BY t.team_name, tv.location_type;
""",

13: """
SELECT
    p1.full_name AS player1,
    p2.full_name AS player2,
    (bp1.runs_scored + bp2.runs_scored) AS partnership_runs,
    bp1.innings_number
FROM batting_performances bp1
JOIN batting_performances bp2
    ON bp1.match_id = bp2.match_id
    AND bp1.innings_number = bp2.innings_number
    AND bp2.batting_position = bp1.batting_position + 1
JOIN players p1 ON bp1.player_id = p1.player_id
JOIN players p2 ON bp2.player_id = p2.player_id
WHERE (bp1.runs_scored + bp2.runs_scored) >= 100
ORDER BY partnership_runs DESC;
""",

14: """
WITH qualifying_bowling AS (
    SELECT bw.*, m.venue_id
    FROM bowling_performances bw
    JOIN matches m ON bw.match_id = m.match_id
    WHERE bw.overs_bowled >= 4
)
SELECT
    p.full_name, v.venue_name,
    COUNT(DISTINCT qb.match_id) AS matches_played,
    SUM(qb.wickets_taken) AS total_wickets,
    ROUND(SUM(qb.runs_conceded) * 1.0 / NULLIF(SUM(qb.overs_bowled), 0), 2) AS avg_economy_rate
FROM qualifying_bowling qb
JOIN players p ON qb.player_id = p.player_id
JOIN venues v ON qb.venue_id = v.venue_id
GROUP BY qb.player_id, qb.venue_id
HAVING COUNT(DISTINCT qb.match_id) >= 3
ORDER BY total_wickets DESC;
""",

15: """
WITH close_matches AS (
    SELECT * FROM matches
    WHERE (victory_type = 'runs' AND victory_margin < 50)
       OR (victory_type = 'wickets' AND victory_margin < 5)
)
SELECT
    p.full_name,
    ROUND(AVG(bp.runs_scored), 2) AS avg_runs_in_close_matches,
    COUNT(DISTINCT bp.match_id) AS close_matches_played,
    SUM(CASE WHEN bp.team_id = cm.winner_team_id THEN 1 ELSE 0 END) AS close_matches_won_batting
FROM batting_performances bp
JOIN close_matches cm ON bp.match_id = cm.match_id
JOIN players p ON bp.player_id = p.player_id
GROUP BY p.player_id, p.full_name
ORDER BY close_matches_played DESC;
""",

16: """
WITH yearly AS (
    SELECT bp.player_id, strftime('%Y', m.match_date) AS year,
           bp.match_id, bp.runs_scored, bp.balls_faced
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
    WHERE m.match_date >= '2020-01-01'
)
SELECT
    p.full_name, y.year,
    COUNT(DISTINCT y.match_id) AS matches_played,
    ROUND(AVG(y.runs_scored), 2) AS avg_runs_per_match,
    ROUND(SUM(y.runs_scored) * 100.0 / NULLIF(SUM(y.balls_faced), 0), 2) AS avg_strike_rate
FROM yearly y
JOIN players p ON y.player_id = p.player_id
GROUP BY y.player_id, y.year
HAVING COUNT(DISTINCT y.match_id) >= 5
ORDER BY y.year, avg_runs_per_match DESC;
""",

17: """
SELECT
    m.toss_decision,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN m.toss_winner_id = m.winner_team_id THEN 1 ELSE 0 END) AS toss_winner_also_match_winner,
    ROUND(SUM(CASE WHEN m.toss_winner_id = m.winner_team_id THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct
FROM matches m
WHERE m.winner_team_id IS NOT NULL AND m.toss_decision IS NOT NULL
GROUP BY m.toss_decision;
""",

18: """
WITH limited_overs AS (
    SELECT bw.*, m.match_format
    FROM bowling_performances bw
    JOIN matches m ON bw.match_id = m.match_id
    WHERE m.match_format IN ('ODI', 'T20I')
)
SELECT
    p.full_name,
    COUNT(DISTINCT lo.match_id) AS matches_played,
    ROUND(SUM(lo.runs_conceded) * 1.0 / NULLIF(SUM(lo.overs_bowled), 0), 2) AS economy_rate,
    SUM(lo.wickets_taken) AS total_wickets
FROM limited_overs lo
JOIN players p ON lo.player_id = p.player_id
GROUP BY lo.player_id
HAVING COUNT(DISTINCT lo.match_id) >= 10
   AND (SUM(lo.overs_bowled) * 1.0 / COUNT(DISTINCT lo.match_id)) >= 2
ORDER BY economy_rate ASC;
""",

19: """
WITH filtered AS (
    SELECT bp.player_id, bp.runs_scored
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
    WHERE bp.balls_faced >= 10 AND m.match_date >= '2022-01-01'
)
SELECT
    p.full_name,
    ROUND(AVG(f.runs_scored), 2) AS avg_runs,
    ROUND(SQRT(AVG(f.runs_scored * f.runs_scored) - AVG(f.runs_scored) * AVG(f.runs_scored)), 2) AS stddev_runs
FROM filtered f
JOIN players p ON f.player_id = p.player_id
GROUP BY f.player_id
ORDER BY stddev_runs ASC;
""",

20: """
WITH per_format AS (
    SELECT bp.player_id, m.match_format,
           COUNT(DISTINCT bp.match_id) AS matches_in_format,
           SUM(bp.runs_scored) AS runs_in_format,
           SUM(CASE WHEN bp.is_out = 1 THEN 1 ELSE 0 END) AS dismissals_in_format
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
    GROUP BY bp.player_id, m.match_format
),
totals AS (
    SELECT player_id, SUM(matches_in_format) AS total_matches
    FROM per_format
    GROUP BY player_id
)
SELECT
    p.full_name, pf.match_format, pf.matches_in_format,
    ROUND(pf.runs_in_format * 1.0 / NULLIF(pf.dismissals_in_format, 0), 2) AS batting_avg_in_format
FROM per_format pf
JOIN totals t ON pf.player_id = t.player_id
JOIN players p ON pf.player_id = p.player_id
WHERE t.total_matches >= 20
ORDER BY p.full_name, pf.match_format;
""",

21: """
WITH batting_agg AS (
    SELECT bp.player_id, m.match_format,
           SUM(bp.runs_scored) AS runs_scored,
           ROUND(SUM(bp.runs_scored) * 1.0 / NULLIF(SUM(CASE WHEN bp.is_out = 1 THEN 1 ELSE 0 END), 0), 2) AS batting_average,
           ROUND(SUM(bp.runs_scored) * 100.0 / NULLIF(SUM(bp.balls_faced), 0), 2) AS strike_rate
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
    GROUP BY bp.player_id, m.match_format
),
bowling_agg AS (
    SELECT bw.player_id, m.match_format,
           SUM(bw.wickets_taken) AS wickets_taken,
           ROUND(SUM(bw.runs_conceded) * 1.0 / NULLIF(SUM(bw.wickets_taken), 0), 2) AS bowling_average,
           ROUND(SUM(bw.runs_conceded) * 1.0 / NULLIF(SUM(bw.overs_bowled), 0), 2) AS economy_rate
    FROM bowling_performances bw
    JOIN matches m ON bw.match_id = m.match_id
    GROUP BY bw.player_id, m.match_format
),
fielding_agg AS (
    SELECT fp.player_id, m.match_format,
           SUM(fp.catches) AS catches,
           SUM(fp.stumpings) AS stumpings
    FROM fielding_performances fp
    JOIN matches m ON fp.match_id = m.match_id
    GROUP BY fp.player_id, m.match_format
),
scored AS (
    SELECT
        p.player_id, p.full_name, ba.match_format,
        ROUND(
            COALESCE(ba.runs_scored, 0) * 0.01
            + COALESCE(ba.batting_average, 0) * 0.5
            + COALESCE(ba.strike_rate, 0) * 0.3
            + COALESCE(bwa.wickets_taken, 0) * 2
            + (50 - COALESCE(bwa.bowling_average, 50)) * 0.5
            + (6 - COALESCE(bwa.economy_rate, 6)) * 2
            + COALESCE(fa.catches, 0) * 3
            + COALESCE(fa.stumpings, 0) * 5
        , 2) AS total_weighted_score
    FROM batting_agg ba
    JOIN players p ON ba.player_id = p.player_id
    LEFT JOIN bowling_agg bwa ON ba.player_id = bwa.player_id AND ba.match_format = bwa.match_format
    LEFT JOIN fielding_agg fa ON ba.player_id = fa.player_id AND ba.match_format = fa.match_format
)
SELECT
    full_name, match_format, total_weighted_score,
    RANK() OVER (PARTITION BY match_format ORDER BY total_weighted_score DESC) AS rank_in_format
FROM scored
ORDER BY match_format, rank_in_format;
""",

22: """
WITH pairs AS (
    SELECT match_id,
           MIN(team1_id, team2_id) AS team_a,
           MAX(team1_id, team2_id) AS team_b,
           winner_team_id, victory_margin, match_date
    FROM matches
    WHERE match_date >= DATE('now', '-3 years')
)
SELECT
    ta.team_name AS team_a, tb.team_name AS team_b,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN p.winner_team_id = p.team_a THEN 1 ELSE 0 END) AS team_a_wins,
    SUM(CASE WHEN p.winner_team_id = p.team_b THEN 1 ELSE 0 END) AS team_b_wins,
    ROUND(AVG(CASE WHEN p.winner_team_id = p.team_a THEN p.victory_margin END), 2) AS avg_margin_team_a_wins,
    ROUND(AVG(CASE WHEN p.winner_team_id = p.team_b THEN p.victory_margin END), 2) AS avg_margin_team_b_wins,
    ROUND(SUM(CASE WHEN p.winner_team_id = p.team_a THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS team_a_win_pct,
    ROUND(SUM(CASE WHEN p.winner_team_id = p.team_b THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS team_b_win_pct
FROM pairs p
JOIN teams ta ON p.team_a = ta.team_id
JOIN teams tb ON p.team_b = tb.team_id
GROUP BY p.team_a, p.team_b
HAVING COUNT(*) >= 5
ORDER BY total_matches DESC;
""",

23: """
WITH ranked AS (
    SELECT bp.player_id, bp.runs_scored, bp.balls_faced, m.match_date,
           ROW_NUMBER() OVER (PARTITION BY bp.player_id ORDER BY m.match_date DESC) AS rn
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
),
last10 AS (
    SELECT * FROM ranked WHERE rn <= 10
)
SELECT
    p.full_name,
    ROUND(AVG(CASE WHEN rn <= 5 THEN runs_scored END), 2) AS avg_runs_last5,
    ROUND(AVG(runs_scored), 2) AS avg_runs_last10,
    ROUND(SUM(CASE WHEN rn <= 5 THEN runs_scored ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN rn <= 5 THEN balls_faced ELSE 0 END), 0), 2) AS strike_rate_last5,
    SUM(CASE WHEN runs_scored > 50 THEN 1 ELSE 0 END) AS scores_above_50,
    ROUND(SQRT(AVG(runs_scored * runs_scored) - AVG(runs_scored) * AVG(runs_scored)), 2) AS consistency_stddev
FROM last10 l
JOIN players p ON l.player_id = p.player_id
GROUP BY l.player_id
ORDER BY avg_runs_last10 DESC;
""",

24: """
WITH partnerships AS (
    SELECT bp1.player_id AS player1_id, bp2.player_id AS player2_id,
           (bp1.runs_scored + bp2.runs_scored) AS partnership_runs
    FROM batting_performances bp1
    JOIN batting_performances bp2
        ON bp1.match_id = bp2.match_id
        AND bp1.innings_number = bp2.innings_number
        AND bp2.batting_position = bp1.batting_position + 1
)
SELECT
    p1.full_name AS player1, p2.full_name AS player2,
    COUNT(*) AS total_partnerships,
    ROUND(AVG(partnership_runs), 2) AS avg_partnership_runs,
    SUM(CASE WHEN partnership_runs > 50 THEN 1 ELSE 0 END) AS partnerships_above_50,
    MAX(partnership_runs) AS highest_partnership,
    ROUND(SUM(CASE WHEN partnership_runs > 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate_pct
FROM partnerships pt
JOIN players p1 ON pt.player1_id = p1.player_id
JOIN players p2 ON pt.player2_id = p2.player_id
GROUP BY pt.player1_id, pt.player2_id
HAVING COUNT(*) >= 5
ORDER BY success_rate_pct DESC, avg_partnership_runs DESC;
""",

25: """
WITH quarterly AS (
    SELECT bp.player_id,
           strftime('%Y', m.match_date) || '-Q' ||
               ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
           bp.match_id, bp.runs_scored, bp.balls_faced
    FROM batting_performances bp
    JOIN matches m ON bp.match_id = m.match_id
),
quarterly_agg AS (
    SELECT player_id, quarter,
           COUNT(DISTINCT match_id) AS matches_in_quarter,
           ROUND(AVG(runs_scored), 2) AS avg_runs,
           ROUND(SUM(runs_scored) * 100.0 / NULLIF(SUM(balls_faced), 0), 2) AS avg_strike_rate
    FROM quarterly
    GROUP BY player_id, quarter
    HAVING COUNT(DISTINCT match_id) >= 3
),
with_trend AS (
    SELECT *,
           LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter) AS prev_quarter_avg_runs,
           avg_runs - LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter) AS qoq_change
    FROM quarterly_agg
),
qualifying_players AS (
    SELECT player_id, COUNT(*) AS total_qualifying_quarters
    FROM quarterly_agg
    GROUP BY player_id
    HAVING COUNT(*) >= 6
)
SELECT
    p.full_name, wt.quarter, wt.matches_in_quarter, wt.avg_runs, wt.avg_strike_rate,
    wt.qoq_change,
    CASE
        WHEN wt.qoq_change > 0 THEN 'Improving'
        WHEN wt.qoq_change < 0 THEN 'Declining'
        ELSE 'Stable'
    END AS quarter_trend
FROM with_trend wt
JOIN qualifying_players qp ON wt.player_id = qp.player_id
JOIN players p ON wt.player_id = p.player_id
ORDER BY p.full_name, wt.quarter;
""",

}
