"""
database/seed_data.py

Populates the database with a realistic SYNTHETIC dataset so that
all 25 SQL practice questions have enough data to answer meaningfully.
This is separate from live API data (which only covers current/recent
matches) — this seed represents "historical" data for analytics practice.

random.seed(42) makes this reproducible: re-running gives identical data.
"""
import random
from datetime import date, timedelta

from database.db_connection import get_db_cursor, initialize_database

random.seed(42)

TEAMS = [
    ("India", "India"), ("Australia", "Australia"), ("England", "England"),
    ("New Zealand", "New Zealand"), ("Pakistan", "Pakistan"),
    ("South Africa", "South Africa"), ("Sri Lanka", "Sri Lanka"),
    ("West Indies", "West Indies"),
]

VENUES = [
    ("Wankhede Stadium", "Mumbai", "India", 33000),
    ("Melbourne Cricket Ground", "Melbourne", "Australia", 100000),
    ("Lord's", "London", "England", 30000),
    ("Eden Park", "Auckland", "New Zealand", 50000),
    ("Gaddafi Stadium", "Lahore", "Pakistan", 27000),
    ("Newlands", "Cape Town", "South Africa", 25000),
]

FIRST_NAMES = ["Rohit", "Virat", "Steve", "Joe", "Kane", "Babar", "Quinton", "Angelo",
               "Jasprit", "Pat", "James", "Trent", "Shaheen", "Kagiso", "Lasith", "Jason",
               "Shubman", "David", "Ben", "Tom", "Rassie", "Wanindu", "Mohammed", "Mitchell"]
LAST_NAMES = ["Sharma", "Kohli", "Smith", "Root", "Williamson", "Azam", "de Kock", "Mathews",
              "Bumrah", "Cummins", "Anderson", "Boult", "Afridi", "Rabada", "Malinga", "Holder",
              "Gill", "Warner", "Stokes", "Latham", "van der Dussen", "Hasaranga", "Shami", "Starc"]

ROLES = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
FORMATS = ["Test", "ODI", "T20I"]

# Explicit index-aligned country list (matches FIRST_NAMES/LAST_NAMES order)
# so seeded players look realistic instead of randomly mismatched.
PLAYER_COUNTRIES = [
    "India", "India", "Australia", "England", "New Zealand", "Pakistan",
    "South Africa", "Sri Lanka", "India", "Australia", "England", "New Zealand",
    "Pakistan", "South Africa", "Sri Lanka", "West Indies", "India", "Australia",
    "England", "New Zealand", "South Africa", "Sri Lanka", "India", "Australia",
]


def seed_teams(cursor):
    cursor.executemany(
        "INSERT INTO teams (team_name, country) VALUES (?, ?)", TEAMS
    )
    return {name: idx + 1 for idx, (name, _) in enumerate(TEAMS)}  # name -> team_id


def seed_venues(cursor):
    cursor.executemany(
        "INSERT INTO venues (venue_name, city, country, capacity) VALUES (?, ?, ?, ?)",
        VENUES,
    )


def seed_players(cursor, n=24):
    players = []
    for i in range(n):
        full_name = f"{FIRST_NAMES[i]} {LAST_NAMES[i]}"
        country = PLAYER_COUNTRIES[i]
        role = ROLES[i % len(ROLES)]
        players.append((full_name, country, role, "Right-hand bat", "Right-arm fast"))
    cursor.executemany(
        "INSERT INTO players (full_name, country, playing_role, batting_style, bowling_style) "
        "VALUES (?, ?, ?, ?, ?)",
        players,
    )


def seed_series(cursor):
    series = [
        ("Border-Gavaskar Trophy 2023", "Australia", "Test", "2023-02-09", 4),
        ("World Cup 2023", "India", "ODI", "2023-10-05", 10),
        ("T20I Tri-Series 2024", "South Africa", "T20I", "2024-01-15", 6),
    ]
    cursor.executemany(
        "INSERT INTO series (series_name, host_country, match_type, start_date, total_matches) "
        "VALUES (?, ?, ?, ?, ?)",
        series,
    )


def seed_matches_and_performances(cursor, n_matches=20):
    """Generates matches + batting/bowling/fielding rows for each match."""
    team_ids = list(range(1, len(TEAMS) + 1))
    venue_ids = list(range(1, len(VENUES) + 1))
    player_ids = list(range(1, 25))
    series_ids = [1, 2, 3]
    base_date = date(2023, 1, 1)

    for match_num in range(1, n_matches + 1):
        team1, team2 = random.sample(team_ids, 2)
        venue = random.choice(venue_ids)
        series = random.choice(series_ids)
        match_format = random.choice(FORMATS)
        match_date = base_date + timedelta(days=match_num * 9)
        toss_winner = random.choice([team1, team2])
        toss_decision = random.choice(["bat", "bowl"])
        winner = random.choice([team1, team2, None])  # None simulates draw/no-result
        victory_type = random.choice(["runs", "wickets"]) if winner else None
        victory_margin = random.randint(5, 150) if winner else None

        cursor.execute(
            """INSERT INTO matches
               (series_id, team1_id, team2_id, venue_id, match_date, match_format,
                match_description, toss_winner_id, toss_decision, winner_team_id,
                victory_margin, victory_type, match_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed')""",
            (series, team1, team2, venue, match_date.isoformat(), match_format,
             f"Match {match_num}", toss_winner, toss_decision, winner,
             victory_margin, victory_type),
        )
        match_id = cursor.lastrowid

        # Batting performances: pick 6 players per team per innings (simplified)
        for innings, team in enumerate([team1, team2], start=1):
            team_players = random.sample(player_ids, 6)
            for pos, pid in enumerate(team_players, start=1):
                runs = max(0, int(random.gauss(35, 25)))
                balls = max(1, runs + random.randint(-10, 30))
                cursor.execute(
                    """INSERT INTO batting_performances
                       (match_id, player_id, team_id, innings_number, batting_position,
                        runs_scored, balls_faced, fours, sixes, is_out)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (match_id, pid, team, innings, pos, runs, balls,
                     runs // 10, runs // 25, random.choice([0, 1])),
                )

        # Bowling performances: pick 4 bowlers per team per innings
        for innings, team in enumerate([team1, team2], start=1):
            bowlers = random.sample(player_ids, 4)
            for pid in bowlers:
                overs = round(random.uniform(2, 10), 1)
                runs_conceded = random.randint(15, 60)
                wickets = random.randint(0, 4)
                cursor.execute(
                    """INSERT INTO bowling_performances
                       (match_id, player_id, team_id, innings_number, overs_bowled,
                        runs_conceded, wickets_taken)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (match_id, pid, team, innings, overs, runs_conceded, wickets),
                )

        # Fielding performances: 3 random players get catches/stumpings
        for pid in random.sample(player_ids, 3):
            cursor.execute(
                """INSERT INTO fielding_performances
                   (match_id, player_id, catches, stumpings, run_outs)
                   VALUES (?, ?, ?, ?, ?)""",
                (match_id, pid, random.randint(0, 3), random.randint(0, 1), random.randint(0, 1)),
            )


def run_seed():
    initialize_database()
    with get_db_cursor(commit=True) as cursor:
        seed_teams(cursor)
        seed_venues(cursor)
        seed_players(cursor)
        seed_series(cursor)
        seed_matches_and_performances(cursor)
    print("Database seeded successfully.")


if __name__ == "__main__":
    run_seed()
