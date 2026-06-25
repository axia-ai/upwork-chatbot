#!/usr/bin/env bash
#
# One-command setup + run for the North Star support bot.
#
#   ./start.sh
#
# On first run it installs the backend and frontend dependencies, asks for your
# Anthropic API key (stored locally in backend/.env, never committed), then
# starts both servers and opens the app in your browser. Press Ctrl+C to stop.
#
# Works on macOS and Linux (and Git Bash / WSL on Windows).

set -euo pipefail
cd "$(dirname "$0")"

BACKEND_PORT=8000
FRONTEND_PORT=5173

info() { printf "\n\033[1;32m==>\033[0m %s\n" "$1"; }
die()  { printf "\n\033[1;31mError:\033[0m %s\n\n" "$1" >&2; exit 1; }

# 1. Prerequisites -----------------------------------------------------------
command -v python3 >/dev/null || die "Python 3 is required — install it from https://www.python.org/downloads/ and re-run."
command -v node    >/dev/null || die "Node.js is required — install it from https://nodejs.org/ and re-run."
command -v npm     >/dev/null || die "npm is required (it comes with Node.js)."

# 2. Anthropic API key -> backend/.env ---------------------------------------
if [ ! -f backend/.env ] || ! grep -q '^ANTHROPIC_API_KEY=.\+' backend/.env 2>/dev/null; then
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" > backend/.env
    info "Saved ANTHROPIC_API_KEY from your environment to backend/.env"
  else
    info "An Anthropic API key is needed. It is stored only in backend/.env and is never committed."
    printf "Paste your Anthropic API key and press Enter: "
    read -r KEY
    [ -n "$KEY" ] || die "No key entered."
    echo "ANTHROPIC_API_KEY=${KEY}" > backend/.env
    info "Saved to backend/.env"
  fi
fi

# 3. Backend dependencies ----------------------------------------------------
[ -d backend/.venv ] || python3 -m venv backend/.venv
if [ ! -x backend/.venv/bin/uvicorn ]; then
  info "Installing backend dependencies (first run can take a few minutes)…"
  backend/.venv/bin/pip install --quiet --upgrade pip
  backend/.venv/bin/pip install --quiet -r backend/requirements.txt
fi

# 4. Frontend dependencies ---------------------------------------------------
if [ ! -d frontend/node_modules ]; then
  info "Installing frontend dependencies…"
  ( cd frontend && npm install --silent )
fi

# 5. Start both servers; clean up on exit ------------------------------------
cleanup() {
  info "Stopping…"
  pkill -f "uvicorn app.main:app --port ${BACKEND_PORT}" 2>/dev/null || true
  pkill -f "vite.*--port ${FRONTEND_PORT}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

info "Starting backend on http://localhost:${BACKEND_PORT}"
( cd backend && exec .venv/bin/uvicorn app.main:app --port "$BACKEND_PORT" --log-level warning ) &

info "Starting frontend on http://localhost:${FRONTEND_PORT}"
( cd frontend && exec npm run dev -- --port "$FRONTEND_PORT" >/dev/null 2>&1 ) &

# 6. Wait until ready, then open the browser ---------------------------------
info "Waiting for the app to start…"
for _ in $(seq 1 60); do
  if curl -sf "http://localhost:${BACKEND_PORT}/health" >/dev/null 2>&1 \
     && curl -sf "http://localhost:${FRONTEND_PORT}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

URL="http://localhost:${FRONTEND_PORT}"
info "Ready — opening ${URL}"
if   command -v open     >/dev/null; then open "$URL" 2>/dev/null || true
elif command -v xdg-open >/dev/null; then xdg-open "$URL" 2>/dev/null || true
else info "Open ${URL} in your browser."
fi

info "Both servers are running. Press Ctrl+C to stop."
wait
