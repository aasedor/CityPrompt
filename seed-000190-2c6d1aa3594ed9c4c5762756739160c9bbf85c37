#!/usr/bin/env bash
set -e

echo "=== 3D Platform — Render Startup ==="

PORT="${PORT:-8000}"

# --- Run DB setup (extensions + migrations + admin seeding) in background ---
# This lets uvicorn start immediately so health checks pass on cold start.
(
    SYNC_URL="${DATABASE_URL}"
    SYNC_URL="${SYNC_URL/postgres:\/\//postgresql:\/\/}"
    SYNC_URL="${SYNC_URL/postgresql+asyncpg:\/\//postgresql:\/\/}"

    echo "[bg] Enabling PostGIS and uuid-ossp extensions..."
    python -c "
import sqlalchemy
engine = sqlalchemy.create_engine('${SYNC_URL}')
with engine.connect() as conn:
    conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS postgis'))
    conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"'))
    conn.commit()
print('[bg] Extensions enabled.')
" || echo "[bg] WARNING: Extension creation failed"

    echo "[bg] Running Alembic migrations..."
    alembic upgrade head || echo "[bg] WARNING: Migrations failed"

    echo "[bg] Ensuring admin users..."
    python -m scripts.ensure_admins || echo "[bg] WARNING: Admin seeding skipped"

    echo "[bg] DB setup complete."
) &

# --- Start uvicorn immediately ---
echo "Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips="*"
