🏏 Cricbuzz LiveStats | Real-Time Cricket Insights & SQL Analytics

A real-time cricket analytics dashboard built with Python, Streamlit, SQLite, REST API integration, Pandas, and Plotly.

The application combines live cricket match data from the Cricbuzz REST API with a local SQL database to provide live scores, player statistics, SQL-based analytics, and CRUD operations through an interactive Streamlit interface.

🚀 Live Demo

Cricbuzz LiveStats:
https://cricbuzz-livestats-manjula283.streamlit.app/

📌 Project Overview

Cricbuzz LiveStats is an end-to-end cricket analytics project that demonstrates how API data, SQL databases, Python data processing, and interactive visualization can be combined into a single analytics application.

The project provides:

🔴 Live cricket match information

🏏 Player performance statistics

📊 Interactive player visualizations

🧮 25 SQL analytics queries

🛠️ CRUD operations for players and matches

🗄️ SQLite database management

🔌 REST API integration

🧪 Automated testing with 61 tests

❤️ Database and API health checks

🎯 Project Objectives

- Retrieve real-time cricket match information through a REST API
- Store and manage cricket data using a relational database
- Perform SQL analysis from beginner to advanced level
- Analyze player batting and performance statistics
- Create interactive visualizations using Plotly
- Implement Create, Read, Update, and Delete operations
- Build a user-friendly analytics dashboard using Streamlit
- Apply modular software architecture and testing practices

🛠️ Tech Stack

| Area | Tools / Technologies |
|---|---|
| Programming Language | Python 3.11 |
| Web Framework | Streamlit |
| Database | SQLite |
| API | Cricbuzz REST API via RapidAPI |
| Data Analysis | Pandas |
| Visualization | Plotly |
| SQL | SQLite SQL |
| Testing | Pytest |
| Configuration | Environment Variables |
| Version Control | Git & GitHub |

✨ Features

🔴 Live Matches

Displays live cricket match information retrieved from the Cricbuzz REST API.

Features include:
- Live match status
- Teams and scores
- Match information
- Real-time API data retrieval
- 60-second caching to reduce unnecessary API requests

📊 Top Player Stats

Provides player performance insights from the project database.

Includes:
- Top run scorers
- Best batting average
- Best strike rate
- Country-based filtering
- Top 10 player performance visualization
- Player archetype analysis

The player archetype visualization compares:

Batting Average vs Strike Rate

to help identify different player performance patterns.

🧮 SQL Analytics

The project contains 25 SQL practice and analytics queries, ranging from beginner to advanced SQL concepts.

Examples include:
- Filtering and sorting
- Aggregations
- GROUP BY
- JOINs
- Subqueries
- Window functions
- Ranking
- Player performance analysis
- Statistical analysis

The SQL Analytics page allows users to select and execute predefined queries directly from the Streamlit application.

🛠️ CRUD Operations

The application provides database management functionality for cricket data.

**Players**
- Add new player
- View existing players
- Update player information
- Delete player records

**Matches**
- Add match records
- View match records
- Update match information
- Delete match records

🏠 Home Dashboard

The home page provides an overview of the application and displays database/API health information.

It includes:
- Number of players in the database
- Number of matches tracked
- Cricbuzz API configuration status
- Navigation to all application modules

📈 Key Analytics

The dashboard provides analysis across multiple areas:

🏏 Player Performance
- Total runs
- Batting average
- Strike rate
- Player rankings
- Country-based comparison

🔴 Match Analysis
- Live match status
- Team scores
- Match tracking
- API-based match updates

🧮 SQL Analysis
- Aggregations
- Grouping
- Joins
- Subqueries
- Window functions
- Ranking-based analysis

🗄️ Database Management
- Player records
- Match records
- CRUD operations
- SQL views
- Database indexes

💡 Business / Analytical Questions

The project can be used to answer questions such as:

- Who are the top run scorers?
- Which players have the highest batting average?
- Which players have the highest strike rate?
- How do player performances differ by country?
- Which players show a combination of high average and high strike rate?
- How many matches are currently being tracked?
- How can cricket data be filtered and ranked using SQL?
- How can player and match records be created, updated, and deleted?

🗄️ Database Design

The default application uses SQLite as the database.

The database contains:
- 7 tables
- 2 SQL views
- 5 indexes

The project also includes configuration support for MySQL and PostgreSQL, although those database backends have not been tested against a real server in this project.

🔌 API Integration

The application integrates with the Cricbuzz REST API through RapidAPI to retrieve live cricket information.

The API layer is separated from the application logic using:
- `cricbuzz_client.py` — API communication
- `response_parser.py` — API response processing

The API key is stored as an environment variable rather than directly in the source code.

```
CRICBUZZ_API_KEY=your_rapidapi_key_here
```

API endpoints may require verification or adjustment depending on the current RapidAPI Cricbuzz provider configuration.

🧪 Testing

The project includes automated tests using Pytest.

Current test suite:
- 61 tests

Testing covers application functionality such as services, validation, database-related behavior, and API-related components.

Run the test suite with:

```
pytest
```

📁 Project Structure

```
cricbuzz_livestats/
│
├── app.py
├── config.py
├── requirements.txt
├── Dockerfile
├── Procfile
├── .env.example
│
├── .streamlit/
│   └── config.toml
│
├── database/
│   ├── db_connection.py
│   ├── schema.sql
│   └── seed_data.py
│
├── api/
│   ├── cricbuzz_client.py
│   └── response_parser.py
│
├── services/
│   ├── match_service.py
│   ├── crud_service.py
│   └── analytics_service.py
│
├── sql/
│   └── queries.py
│
├── pages/
│   ├── 2_Live_Matches.py
│   ├── 3_Top_Player_Stats.py
│   ├── 4_SQL_Analytics.py
│   └── 5_CRUD_Operations.py
│
├── utils/
│   ├── validators.py
│   ├── exceptions.py
│   ├── logger.py
│   └── db_guard.py
│
├── tests/
│   └── ...
│
├── Screenshots/
│   ├── home.png
│   ├── live_matches.png
│   ├── top_player_stats.png
│   ├── top_player_runs_chart.png
│   ├── top_player_archetype.png
│   ├── sql_analytics.png
│   └── crud_operations.png
│
└── README.md
```

⚙️ How to Run Locally

**1. Clone the repository**
```
git clone <your-repository-url>
cd cricbuzz_livestats
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Configure the API key**

Create a `.env` file based on `.env.example`.
```
CRICBUZZ_API_KEY=your_rapidapi_key_here
```

**4. Initialize the database**
```
python -m database.seed_data
```

**5. Start the Streamlit application**
```
streamlit run app.py
```

**6. Open the application**

Streamlit will provide the local application address in the terminal.

🧭 Application Navigation

The application contains the following main sections:

| Page | Purpose |
|---|---|
| 🏠 Home | Project overview and system health |
| 🔴 Live Matches | Live cricket match information |
| 📊 Top Player Stats | Player performance analysis |
| 🧮 SQL Analytics | SQL query execution and analytics |
| 🛠️ CRUD Operations | Player and match database management |

📊 SQL Concepts Demonstrated

The SQL analytics section demonstrates concepts including:
- SELECT
- WHERE
- ORDER BY
- GROUP BY
- HAVING
- Aggregate functions
- INNER JOIN
- LEFT JOIN
- Subqueries
- Common analytical patterns
- Window functions
- Ranking
- Views

The queries progress from basic SQL operations to more advanced analytical queries.

🔐 Configuration & Security

Sensitive configuration values are stored using environment variables.

The API key should not be hard-coded in Python files or committed to GitHub.

Use:

`.env`

for local secrets and keep the actual API key private.

A template is provided through:

`.env.example`

⚠️ Known Limitations

- Five of the 25 SQL queries may return zero rows with the default seed dataset because the seeded data does not satisfy the required conditions or scale for those queries.
- The current live API integration depends on the availability and configuration of the Cricbuzz provider on RapidAPI.
- MySQL and PostgreSQL configuration exists, but those database backends were not tested against a live server as part of this project.
- Historical match backfilling is not currently implemented.
- The application does not currently provide role-based authentication.

🚀 Future Enhancements

Possible future improvements include:
- 🔐 User authentication and role-based access
- 📚 Historical cricket data backfilling
- ⚡ Push-based live score updates
- 🤖 Machine learning based match-outcome analysis
- 📈 Additional player performance metrics
- ☁️ Production database integration
- 📱 Improved mobile responsiveness
- 📊 More advanced cricket analytics

📌 Project Highlights

- Built an end-to-end cricket analytics application using Python and Streamlit
- Integrated a REST API for live cricket data
- Designed and used a relational SQLite database
- Implemented 25 SQL analytics queries
- Added CRUD functionality for player and match records
- Created interactive charts using Plotly
- Used Pandas for data processing
- Implemented API/data caching for live-match requests
- Added automated testing with 61 tests
- Organized the application using separate API, database, service, SQL, utility, and page layers
- Deployed the application using Streamlit

👩‍💻 Author

Manjula

Electronics & Communication Engineering | Data Analytics | Python | SQL | Power BI

🔗 Project

Live application:
https://cricbuzz-livestats-manjula283.streamlit.app/

📄 License

This project is intended for learning, portfolio, and demonstration purposes.
