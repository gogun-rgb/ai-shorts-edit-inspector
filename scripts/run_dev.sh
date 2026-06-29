#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v ffmpeg >/dev/null || { echo "ffmpeg is missing"; exit 1; }
command -v ffprobe >/dev/null || { echo "ffprobe is missing"; exit 1; }

if [ ! -x "$ROOT/backend/.venv/bin/python" ]; then
  echo "Backend virtual environment not found."
  echo "Run:"
  echo "  cd \"$ROOT/backend\""
  echo "  python3.11 -m venv .venv"
  echo "  . .venv/bin/activate"
  echo "  python -m pip install -r requirements-dev.txt"
  exit 1
fi

trap 'kill 0' EXIT
(cd "$ROOT/backend" && .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
(cd "$ROOT/frontend" && npm run dev -- --host 127.0.0.1 --port 5173) &
wait

