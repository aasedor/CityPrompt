#!/usr/bin/env bash
# Generate a modular LEGO building family from a real SiteForge archetype.
#   ./scripts/generate-archetype-family.sh --archetype-id nordic_timber_midrise [--floors 6] ...
# All arguments are passed straight through to tools/archetype_compiler/generate_family.py.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND="$REPO_ROOT/frontend"

command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || {
  echo "FAILED: Python not found. Install Python 3.11+." >&2; exit 1; }
PYTHON="$(command -v python3 || command -v python)"

command -v npm >/dev/null 2>&1 || { echo "FAILED: Node.js/npm not found. Install Node 18+." >&2; exit 1; }

if [ ! -d "$FRONTEND/node_modules/.bin" ]; then
  echo "Installing frontend dependencies (first run only)..."
  (cd "$FRONTEND" && npm install)
fi

exec "$PYTHON" "$REPO_ROOT/tools/archetype_compiler/generate_family.py" "$@"
