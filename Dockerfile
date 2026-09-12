FROM python:3.12-slim

WORKDIR /app

# curl is needed for the HEALTHCHECK below - python:3.12-slim doesn't include it by default
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (separate layer -> Docker caches this
# unless requirements.txt changes, speeding up rebuilds during dev)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Seed the database at image build time so the container is ready
# to serve immediately (fine for SQLite/demo use; for MySQL/Postgres
# in production you'd run migrations separately, not bake data into the image)
RUN python -m database.seed_data

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
