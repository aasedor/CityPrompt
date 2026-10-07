#!/usr/bin/env bash
set -euo pipefail

# Migrations must finish successfully before the API accepts student work.
# Never interpolate a database URL into shell/Python source text.
# Render can run this once in its pre-deploy step. Preserve inline migrations
# for existing installations; a typo must never silently skip them.
case "${RUN_DATABASE_MIGRATIONS:-true}" in
    true) python -m scripts.prepare_database ;;
    false) ;;
    *) printf '%s\n' 'RUN_DATABASE_MIGRATIONS must be true or false' >&2; exit 1 ;;
esac

# Administrative bootstrap is explicit, without default passwords or promotions.
if [[ -n "${BOOTSTRAP_ADMIN_EMAIL:-}" || -n "${BOOTSTRAP_ADMIN_PASSWORD:-}" ]]; then
    python -m scripts.ensure_admins
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" \
    --proxy-headers --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-127.0.0.1}" \
    --no-access-log
