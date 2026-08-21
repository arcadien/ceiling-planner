#!/usr/bin/env bash
# Run the Ceiling Planner locally and auto-update from origin.
#
# Usage: ./dev.sh [PORT] [HOST] [INTERVAL_SECONDS]
#   PORT      port to serve on        (default 8000)
#   HOST      host to bind to         (default 127.0.0.1)
#   INTERVAL  seconds between checks   (default 15)
#
# Polls origin for new commits on the current branch and fast-forwards the working
# tree; uvicorn --reload then restarts the server on the changed files. HTML/schema
# changes are picked up on the next browser refresh (the page is read per request).
set -euo pipefail

PORT="${1:-8000}"
HOST="${2:-127.0.0.1}"
INTERVAL="${3:-15}"

cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' is required but not found. Install it from https://docs.astral.sh/uv/" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"

auto_update() {
  while true; do
    sleep "$INTERVAL"
    git fetch --quiet origin "$BRANCH" 2>/dev/null || continue
    local before after
    before="$(git rev-parse HEAD)"
    after="$(git rev-parse "origin/${BRANCH}" 2>/dev/null || echo "$before")"
    [ "$before" = "$after" ] && continue
    if git merge --ff-only "origin/${BRANCH}" >/dev/null 2>&1; then
      echo "↻ updated to $(git rev-parse --short HEAD) — server reloads on .py changes; refresh the browser for UI changes"
      if git diff --name-only "$before" HEAD | grep -qE 'pyproject\.toml|uv\.lock'; then
        echo "  dependencies changed — syncing..."
        uv sync --extra dev >/dev/null 2>&1 || true
      fi
    else
      echo "⚠ local commits diverge from origin/${BRANCH}; skipping auto-update (resolve manually)" >&2
    fi
  done
}

echo "Syncing dependencies..."
uv sync --extra dev

auto_update &
UPDATER_PID=$!
trap 'kill "$UPDATER_PID" 2>/dev/null || true' EXIT

echo "Ceiling Planner (auto-updating from origin/${BRANCH}, every ${INTERVAL}s) at http://${HOST}:${PORT}"
echo "Ctrl+C to stop."
exec uv run uvicorn ceiling_planner.api.app:app --host "${HOST}" --port "${PORT}" --reload
