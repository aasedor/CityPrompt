#!/usr/bin/env bash
set -e

echo "=== 3D Platform — Render Startup ==="

# --- 1. Enable PostGIS and uuid-ossp extensions ---
# Derive a sync (psycopg2) URL from DATABASE_URL
SYNC_URL="${DATABASE_URL}"
# Render gives postgres:// — psycopg2 needs postgresql://
SYNC_URL="${SYNC_URL/postgres:\/\//postgresql:\/\/}"
# Strip any +asyncpg driver suffix if present
SYNC_URL="${SYNC_URL/postgresql+asyncpg:\/\//postgresql:\/\/}"

echo "Enabling PostGIS and uuid-ossp extensions..."
python -c "
import sqlalchemy
engine = sqlalchemy.create_engine('${SYNC_URL}')
with engine.connect() as conn:
    conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS postgis'))
    conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"'))
    conn.commit()
print('Extensions enabled.')
"

# --- 2. Run Alembic migrations (handles all table creation) ---
echo "Running Alembic migrations..."
alembic upgrade head

# --- 4. Ensure admin users exist ---
echo "Ensuring admin users..."
python -m scripts.ensure_admins

# --- 5. Start uvicorn ---
PORT="${PORT:-8000}"
echo "Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips="*"
