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

# --- 2. Create base tables (idempotent) ---
echo "Running create_all for base tables..."
python -c "
from app.core.database import Base
from app.models import models  # register all models
import sqlalchemy
engine = sqlalchemy.create_engine('${SYNC_URL}')
Base.metadata.create_all(bind=engine)
print('Base tables ensured.')
"

# --- 3. Run Alembic migrations ---
echo "Running Alembic migrations..."
# Check if alembic_version table exists (i.e. not a fresh deploy)
HAS_ALEMBIC=$(python -c "
import sqlalchemy
engine = sqlalchemy.create_engine('${SYNC_URL}')
with engine.connect() as conn:
    result = conn.execute(sqlalchemy.text(
        \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')\"
    ))
    print(result.scalar())
")

if [ "$HAS_ALEMBIC" = "True" ]; then
    echo "Existing deployment detected — running alembic upgrade head..."
    alembic upgrade head
else
    echo "Fresh deployment detected — stamping alembic to head..."
    alembic stamp head
fi

# --- 4. Ensure admin users exist ---
echo "Ensuring admin users..."
python -m scripts.ensure_admins

# --- 5. Start uvicorn ---
PORT="${PORT:-8000}"
echo "Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips="*"
