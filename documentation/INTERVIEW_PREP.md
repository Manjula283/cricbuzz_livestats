# Interview Preparation — Cricbuzz LiveStats

50 questions across Python, SQL, Streamlit, API design, System Design, and
Project Viva — grounded in decisions actually made in this project, not
generic textbook answers.

---

## Python (10)

**1. Why use a context manager (`@contextmanager`) for database access instead of opening/closing connections manually?**
It guarantees cleanup (commit/rollback + close) even when an exception occurs mid-transaction, via the `try/finally` inside the generator. Manual open/close code is easy to get wrong when an exception skips your `close()` call.

**2. What's the difference between `except Exception` and catching specific exceptions like `sqlite3.IntegrityError`?**
Specific exceptions let you handle known failure modes precisely (e.g., convert an FK violation into a friendly message) while still letting unexpected errors propagate and get logged/investigated. Catching bare `Exception` everywhere hides bugs.

**3. Why does `NULLIF(x, 0)` matter when computing an average in Python-adjacent SQL code?**
It converts a zero denominator to `NULL` before division, so the query returns `NULL` instead of crashing with a divide-by-zero error — cleaner than wrapping every average calculation in Python-side try/except.

**4. Explain the `get_or_create` pattern used in `match_service.py`.**
When reconciling external data (API team/venue names) with internal primary keys, you look up by a natural key (name); if found, return its ID, otherwise insert and return the new ID. This avoids duplicate rows when the same entity appears across multiple API calls.

**5. Why use dataclasses/typed models instead of passing raw dicts everywhere?**
Typed models catch column-name typos at development time (via IDE/type checker) rather than at runtime; this project uses dicts (via `sqlite3.Row`) for simplicity, but `models/` was scaffolded for exactly this reason.

**6. What does `@st.cache_data(ttl=60)` actually do, and why is TTL necessary here?**
It memoizes a function's return value for 60 seconds; without it, Streamlit's rerun-on-every-interaction model would hit the Cricbuzz API on every single widget click, burning rate-limit quota fast.

**7. Why does `cricbuzz_client.py` centralize all HTTP calls through one `_get()` method?**
Single place for retry logic, auth headers, and error translation — every public method (`get_live_matches`, `get_player_batting_stats`, etc.) automatically inherits consistent error handling without duplicating try/except blocks.

**8. What's the risk of `response.json()` without a try/except?**
If the API returns non-JSON (e.g., an HTML error page during an outage), `.json()` raises `ValueError`/`JSONDecodeError` uncaught — crashes the whole request chain instead of degrading gracefully.

**9. Why validate input in a separate `validators.py` rather than inline in each CRUD function?**
Reusability (same rules apply whether the caller is a Streamlit form, a test, or a future API layer) and testability (pure functions with no DB dependency, fast unit tests).

**10. Explain Python's logical query evaluation order and why it matters for `WHERE` vs `SELECT`.**
SQL executes roughly `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`, even though you *write* `SELECT` first. This is why you can't reference a `SELECT`-list alias in a `WHERE` clause (it doesn't exist yet at that stage) but you can in `ORDER BY`.

---

## SQL (12)

**11. Why does the batting average formula divide by dismissals, not innings played?**
Cricket convention: a "not out" innings isn't a completed dismissal, so it's excluded from the average's denominator — using total innings would understate a player's true average.

**12. Explain the self-join used for partnership calculation (Q13/Q24).**
Joining `batting_performances` to itself on `match_id + innings_number`, with `bp2.batting_position = bp1.batting_position + 1`, pairs each batter with the one who batted immediately after them in the same innings — modeling a "partnership" without a dedicated table.

**13. Why use a CTE instead of a subquery for the all-rounder query (Q9)?**
Readability and reusability — naming `batting_totals` and `bowling_totals` as CTEs makes the final join self-documenting, versus nesting two subqueries inline, which gets hard to read past 2 levels.

**14. What does `RANK() OVER (PARTITION BY match_format ORDER BY total_weighted_score DESC)` do, and how does it differ from `ROW_NUMBER()`?**
`RANK()` assigns the same rank to ties (with a gap after), while `ROW_NUMBER()` always gives distinct sequential numbers even for ties. Q21 uses `RANK()` because two players tying on weighted score should show the same rank.

**15. Why does SQLite need `SQRT(AVG(x²) - AVG(x)²)` instead of `STDDEV()`?**
SQLite has no built-in standard deviation function. This is the population variance formula (E[X²] − E[X]²) under a square root — computed manually using only `AVG()`, which SQLite does support.

**16. Why use `UNION ALL` (not `UNION`) to unpivot team1/team2 in the home/away query (Q12)?**
`UNION ALL` keeps duplicates (a match appearing once as team1's row and once as team2's row is *intentional* here — they represent different teams' perspectives, not actual duplicate data). Plain `UNION` would incorrectly deduplicate rows that happen to look identical.

**17. Why does the head-to-head query (Q22) use `MIN(team1_id, team2_id)` and `MAX(...)`?**
To normalize unordered pairs — India vs Australia and Australia vs India (across different matches where team1/team2 order varies) need to be grouped as the *same* pairing, not counted separately.

**18. What's the purpose of the `IF NOT EXISTS` clause in every `CREATE TABLE`/`CREATE VIEW` statement?**
Makes the schema script idempotent — safe to re-run without erroring if tables already exist, useful for repeated test-database setup and defensive deployment scripts.

**19. Why are `strike_rate` and `economy_rate` NOT stored as columns?**
They're derived values (`runs/balls*100`, `runs/overs`) that several of the 25 SQL questions explicitly ask you to calculate — storing them would make those questions trivial lookups instead of testing aggregation skills, and risks going stale if underlying data changes.

**20. Explain why `CASE WHEN ... THEN 1 ELSE 0 END` wrapped in `SUM()` is used repeatedly (centuries, dismissals, close-match wins).**
It's a conditional counting pattern — turns a per-row boolean condition into a per-group count via aggregation, without needing a separate `COUNT(*) ... WHERE` subquery for each condition.

**21. Why does the schema use `LEFT JOIN` for `winner_team_id` in `v_match_summary` but `JOIN` for `team1_id`/`team2_id`?**
`winner_team_id` is nullable (drawn/no-result matches have no winner); `team1_id`/`team2_id` are always populated (`NOT NULL` in the schema), so an inner `JOIN` is correct and slightly more efficient there.

**22. What indexes were added, and why those specific ones?**
`matches(match_date)`, `matches(match_format)`, `batting_performances(match_id, innings_number, batting_position)` (supports the partnership self-join), `batting_performances(player_id)`, `bowling_performances(player_id, match_id)` — each chosen to match an actual filter/join pattern in the 25 queries, not applied generically.

---

## Streamlit (8)

**23. Why does every Streamlit page rerun its entire script on each interaction?**
That's Streamlit's execution model — it's a "rerun from top" framework, not event-driven like traditional web frameworks. This is exactly why `@st.cache_data` matters: without it, every button click/selectbox change re-triggers every DB/API call in the script.

**24. Why is there no SQL or API code directly inside any `pages/*.py` file?**
Enforces the layered architecture — pages only call `services/`, making the UI layer swappable (could rebuild in Flask/FastAPI later) without touching business logic.

**25. What does `st.stop()` do, and what's the gotcha with testing it?**
Halts remaining script execution for the current rerun. The gotcha: it's a documented no-op outside a real Streamlit session (`ScriptRunContext`), so testing it by running a page as a bare Python script gives a false negative — you must use `streamlit.testing.v1.AppTest` instead.

**26. Why use `st.form()` for CRUD input instead of individual widgets?**
`st.form()` batches all inputs and only triggers a rerun on submit, rather than on every keystroke/selection change — better UX and fewer wasted reruns for multi-field input.

**27. Why does the CRUD delete function block deletion of a player with existing performance records instead of cascading?**
Deliberate data-integrity choice — silently deleting a player's entire career history because you deleted their profile is dangerous. Better to surface a clear error and let the user decide.

**28. What's Streamlit's multipage file convention, and how does file naming affect the sidebar?**
Files in `pages/` become additional pages automatically; the numeric prefix (`2_`, `3_`, etc.) controls sidebar ordering, and the rest of the filename (underscores become spaces) becomes the displayed page name.

**29. Why show `st.warning()` instead of `st.error()` when a SQL query returns 0 rows?**
0 rows isn't necessarily a failure — it can be a correct answer (e.g., "no players meet this threshold"). `st.error()` implies something broke; `st.warning()` correctly signals "ran fine, just nothing matched."

**30. How does `require_database_ready()` prevent a crash, and why was it needed?**
It checks `sqlite_master` for the `players` table before any page logic runs; if missing, it shows setup instructions and calls `st.stop()`. It was needed because a fresh clone without seeding previously crashed with a raw `sqlite3.OperationalError` traceback shown to the user.

---

## API Design (7)

**31. Why does `cricbuzz_client.py` use a `requests.Session` with a `Retry` adapter instead of bare `requests.get()`?**
Automatic retry with exponential backoff on transient failures (429, 500-504) without writing manual retry loops in every calling function.

**32. Why retry only on specific status codes (429, 500-504) and not all errors?**
Retrying a 401 (bad key) or 404 (wrong endpoint) wastes time and API calls — those won't succeed on retry. Only transient, potentially-resolving errors should be retried.

**33. Why does `response_parser.py` use `.get()` everywhere instead of direct dictionary indexing?**
Third-party API JSON isn't guaranteed to have every key on every response (e.g., an upcoming match has no `matchScore` yet). `.get()` with defaults prevents `KeyError` crashes on missing fields.

**34. What's the authentication mechanism for the Cricbuzz API, and why headers instead of query params?**
Header-based (`x-rapidapi-key`, `x-rapidapi-host`) — RapidAPI's standard approach. Headers keep credentials out of URLs, which can end up logged in server access logs or browser history.

**35. Why does `get_live_matches()` catch `APIError` and return an empty list instead of letting it propagate to the page?**
Graceful degradation — a failed live-data fetch shouldn't crash the whole dashboard; showing "no live matches available" is a better UX than an error page.

**36. Explain the dedup strategy for saving live match snapshots to the database.**
Before inserting, check for an existing row matching `(team1_id, team2_id, match_description)`; skip if found. This prevents duplicate rows every time the cached API call refreshes (every 60 seconds).

**37. Why is pagination not implemented for the Cricbuzz live/recent endpoints?**
Those specific endpoints return complete lists, not paginated results — implementing pagination handling would be speculative complexity for a feature the API doesn't require.

---

## System Design (8)

**38. Walk through the layered architecture of this project.**
Frontend (Streamlit pages) → Services (business logic/orchestration) → API layer + Database layer (data sources) → Utils/Config (cross-cutting). Each layer only calls the one directly below it; pages never touch SQL or `requests` directly.

**39. Why is the database designed to be "database-agnostic," and how is that achieved?**
So the project can start on SQLite (zero setup) and move to MySQL/PostgreSQL in production without rewriting the app — achieved via `config.DB_TYPE` branching in `db_connection.get_connection()`, and by avoiding vendor-specific SQL syntax where possible.

**40. Why separate `api/response_parser.py` from `api/cricbuzz_client.py`?**
Single Responsibility — the client's job is "make the HTTP call correctly," the parser's job is "make sense of what came back." If Cricbuzz changes their JSON structure, only the parser needs updating, not the retry/auth logic.

**41. How would you scale this project to handle millions of matches instead of 20?**
Move off SQLite to PostgreSQL/MySQL with connection pooling; add pagination to list views; consider caching aggregate queries (like leaderboards) in a materialized view or scheduled job rather than computing live on every page load; add read replicas if query load grows.

**42. What's the tradeoff between storing computed stats (like strike rate) vs. computing them on read?**
Storing: faster reads, but risk of staleness if underlying data changes without updating the derived value. Computing on read: always accurate, but more CPU per query. This project chose "compute on read" since it's analytics-focused and data volume is small.

**43. Why block cascading deletes instead of implementing them?**
A career record spanning years of matches shouldn't vanish because someone deleted a player profile by mistake — the FK constraint acts as an intentional safety net, not a limitation to work around.

**44. How does this design handle the fact that the live API only gives recent data, but the SQL questions need historical data?**
Two separate data-entry paths into the same schema: `seed_data.py` populates synthetic historical data for analytics practice, while `match_service.py` saves live API snapshots — both write to the same `matches`/`players` tables, so SQL queries work identically regardless of data origin.

**45. Why is validation done in the service layer rather than relying on database constraints alone?**
Database constraints (CHECK, NOT NULL) catch invalid data but produce cryptic errors and only fire at insert time. Service-layer validation fails fast with human-readable messages before any DB round-trip.

---

## Project Viva / General (5)

**46. What was the hardest part of this project, and how did you solve it?**
(Answer from your own experience — but structurally: the 25 SQL questions requiring window functions/CTEs the seed data couldn't always satisfy at realistic thresholds is a strong, honest answer — shows you understood the query logic was correct even when data volume limited results.)

**47. What would you do differently if you started over?**
A reasonable answer: generate a larger, more realistic seed dataset from the start (100+ matches spanning 3+ years) rather than 20 matches, since 5 of the 25 queries needed more data volume to return meaningful results.

**48. How did you ensure your code actually works, not just "looks right"?**
Ran everything against a real (seeded) SQLite database at every phase — not just written and assumed correct. Built a 61-test pytest suite covering unit, integration, mocked-API, and UI tests using `streamlit.testing.v1.AppTest`.

**49. Why did you choose SQLite over MySQL/PostgreSQL for this project?**
Zero setup for graders/reviewers (no separate DB server to install/configure), fast iteration during development, while keeping the code structured (`DB_TYPE` config switch) to move to a production database without a rewrite.

**50. What security practices did you follow?**
API keys and DB credentials loaded from `.env` (never hardcoded, never committed — enforced via `.gitignore`), parametrized SQL queries everywhere (no string-formatted SQL, preventing injection), input validation before any database write.
