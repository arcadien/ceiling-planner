#!/usr/bin/env bash
# Launch the Ceiling Planner web app.
#
# Usage: ./run.sh [PORT] [HOST]
#   PORT  port to serve on   (default 8000)
#   HOST  host to bind to    (default 127.0.0.1)
#
# Syncs dependencies with uv, then starts the FastAPI app with autoreload.
set -euo pipefail

PORT="${1:-8000}"
HOST="${2:-127.0.0.1}"

cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' is required but not found. Install it from https://docs.astral.sh/uv/" >&2
  exit 1
fi

echo "Syncing dependencies..."
uv sync --extra dev

echo "Ceiling Planner running at http://${HOST}:${PORT}  (Ctrl+C to stop)"
exec uv run uvicorn ceiling_planner.api.app:app --host "${HOST}" --port "${PORT}" --reload
