#!/usr/bin/env bash
set -euo pipefail

# Migrations must finish successfully before the API accepts student work.
# Never interpolate a database URL into shell/Python source text.
python -m scripts.prepare_database

# Administrative bootstrap is explicit, without default passwords or promotions.
if [[ -n "${BOOTSTRAP_ADMIN_EMAIL:-}" || -n "${BOOTSTRAP_ADMIN_PASSWORD:-}" ]]; then
    python -m scripts.ensure_admins
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" \
    --proxy-headers --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-127.0.0.1}"
