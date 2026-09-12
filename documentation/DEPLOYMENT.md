# Deployment Guide — Cricbuzz LiveStats

⚠️ Honest disclaimer: Docker isn't available in the environment these files
were built in, so the Dockerfile below is written correctly and checked
carefully, but NOT verified with an actual `docker build`. Please run
`docker build -t cricbuzz-livestats .` yourself and let me know if anything
breaks — happy to debug from the actual error.

All other steps (requirements.txt install, Streamlit config, app startup)
WERE verified directly in a real environment during this project.

---

## Option 1: Streamlit Community Cloud (easiest, free, recommended for this project)

1. Push your project to a public (or Cloud-connected private) GitHub repo.
2. Go to https://share.streamlit.io -> "New app".
3. Select your repo, branch, and set the main file path to `app.py`.
4. Under "Advanced settings" -> "Secrets", add your API key in TOML format:
   ```toml
   CRICBUZZ_API_KEY = "your_real_key"
   ```
   Then in `config.py`, prefer `st.secrets` over `os.getenv` when deployed
   (Streamlit Cloud injects secrets as `st.secrets`, not environment variables,
   unless you access them via `os.environ` after Streamlit loads secrets.toml
   into the environment - check current Streamlit docs, as this detail can change).
5. **Important for this project:** Streamlit Cloud's filesystem is ephemeral
   and the DB isn't seeded automatically. Add this near the top of `app.py`
   (or use `require_database_ready()` and seed once via the in-browser
   terminal Streamlit Cloud provides under "Manage app" -> Terminal).
6. Click Deploy. You get a public `*.streamlit.app` URL.

**Best for:** this exact project — zero cost, zero infra knowledge needed, matches your SQLite-first design.

---

## Option 2: Render

1. Push to GitHub.
2. New "Web Service" on Render, connect your repo.
3. Build command: `pip install -r requirements.txt && python -m database.seed_data`
4. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add `CRICBUZZ_API_KEY` under Environment Variables.
6. Render's free tier disks are ephemeral on redeploy — same caveat as Streamlit Cloud; the build command re-seeding handles this.

---

## Option 3: Railway

1. Push to GitHub, then "New Project" -> "Deploy from GitHub repo" on Railway.
2. Railway auto-detects Python; add a `Procfile` (included in this project):
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Add `CRICBUZZ_API_KEY` as a variable in the Railway dashboard.
4. Add a one-off "Deploy Hook" or run `python -m database.seed_data` via
   Railway's shell after first deploy to seed the DB.

---

## Option 4: Azure (App Service)

1. Install Azure CLI, then:
   ```
   az webapp up --runtime PYTHON:3.12 --sku B1 --name cricbuzz-livestats
   ```
2. Set the startup command in Azure Portal -> Configuration -> Startup Command:
   ```
   streamlit run app.py --server.port=8000 --server.address=0.0.0.0
   ```
3. Add `CRICBUZZ_API_KEY` under Configuration -> Application settings.
4. Azure App Service's filesystem persists across restarts (unlike the
   free tiers above) if you use a persistent storage mount — otherwise
   same ephemeral caveat applies.

---

## Option 5: AWS (Elastic Beanstalk, simplest AWS path for this app)

1. Install the EB CLI: `pip install awsebcli`
2. `eb init -p python-3.12 cricbuzz-livestats`
3. `eb create cricbuzz-livestats-env`
4. Set environment variables: `eb setenv CRICBUZZ_API_KEY=your_key`
5. Add a `Procfile` (same as Railway's) since EB uses it to know the start command.
6. `eb deploy`

For anything beyond a portfolio demo, RDS (managed MySQL/Postgres) instead of
SQLite-on-disk would be the correct production choice here — this is exactly
where the `DB_TYPE` switch in `config.py` earns its keep.

---

## Option 6: Docker (self-host anywhere, or push to any container platform)

```bash
docker build -t cricbuzz-livestats .
docker run -p 8501:8501 --env-file .env cricbuzz-livestats
```
Then visit http://localhost:8501

To push to a registry for cloud deployment (e.g., AWS ECS, Google Cloud Run):
```bash
docker tag cricbuzz-livestats your-registry/cricbuzz-livestats:latest
docker push your-registry/cricbuzz-livestats:latest
```

---

## Recommendation for THIS project

Given your 14-day timeline and SQLite-first design: **Streamlit Community
Cloud** is the right call — it's free, matches your database choice, and
takes ~10 minutes to set up. Save Docker/AWS/Azure for when you outgrow
SQLite or want the DevOps practice for your resume.
