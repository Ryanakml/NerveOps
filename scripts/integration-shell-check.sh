#!/usr/bin/env bash
# M0-01 integration-test wiring (stable interface; #4 owns deterministic harness).
# Boots every shell locally, verifies operability probes, then stops cleanly.
# No database, Redis, model, or domain behavior required.
# Usage: bash scripts/integration-shell-check.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

PASS=0
FAIL=0
PIDS=""

pass() { echo "PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL: $1" >&2; FAIL=$((FAIL+1)); }

cleanup() {
  if [ -n "${PIDS}" ]; then
    # shellcheck disable=SC2086
    kill ${PIDS} 2>/dev/null || true
    sleep 2
    # shellcheck disable=SC2086
    kill -9 ${PIDS} 2>/dev/null || true
  fi
}
trap cleanup EXIT

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing required command: $1" >&2; exit 2; }; }
need curl
need python3

echo "=== M0-01 shell integration check (no infra) ==="

# --- Python shells: CLI checks (no servers needed) ---
echo "--- runtime-worker --check/--once ---"
if (cd apps/runtime-worker && python3 -m worker.main --check >/tmp/nw-rw-check.json && cat /tmp/nw-rw-check.json && echo "" && python3 -m worker.main --once >/tmp/nw-rw-once.json); then
  pass "runtime-worker --check/--once"
else
  fail "runtime-worker --check/--once"
fi

echo "--- celery-worker --check ---"
if (cd apps/celery-worker && python3 -m app.check --check >/tmp/nw-cw-check.json && cat /tmp/nw-cw-check.json && echo ""); then
  pass "celery-worker --check"
else
  fail "celery-worker --check"
fi

# --- runtime-api: boot uvicorn, poll /health + /ready ---
echo "--- runtime-api boot ---"
if python3 -c "import fastapi, uvicorn" 2>/dev/null; then
  (cd apps/runtime-api && RUNTIME_API_PORT=8000 python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >/tmp/nw-runtime-api.log 2>&1 & echo $! >/tmp/nw-runtime-api.pid)
  RUNTIME_PID=$(cat /tmp/nw-runtime-api.pid)
  PIDS="${PIDS} ${RUNTIME_PID}"
  if bash scripts/check-shell-http.sh runtime-api http://127.0.0.1:8000/health 30; then
    pass "runtime-api /health"
  else
    fail "runtime-api /health"
  fi
  if curl -fsS http://127.0.0.1:8000/ready >/tmp/nw-runtime-ready.json && cat /tmp/nw-runtime-ready.json && echo ""; then
    pass "runtime-api /ready"
  else
    fail "runtime-api /ready"
  fi
else
  echo "SKIP: runtime-api boot (fastapi/uvicorn not installed; run pip install -r apps/runtime-api/requirements.txt)"
fi

# --- Node shells: only if dependencies are installed ---
if [ -d "apps/control-plane/node_modules" ]; then
  echo "--- control-plane boot ---"
  (cd apps/control-plane && CONTROL_PLANE_PORT=3001 npm run start --silent >/tmp/nw-control.log 2>&1 & echo $! >/tmp/nw-control.pid)
  CONTROL_PID=$(cat /tmp/nw-control.pid)
  PIDS="${PIDS} ${CONTROL_PID}"
  if bash scripts/check-shell-http.sh control-plane http://127.0.0.1:3001/health 45; then
    pass "control-plane /health"
  else
    fail "control-plane /health"
    echo "--- control-plane log tail ---"
    tail -n 100 /tmp/nw-control.log || true
  fi
else
  echo "SKIP: control-plane boot (node_modules missing; run npm install)"
fi

if [ -d "apps/web/node_modules" ]; then
  echo "--- web boot ---"
  # Web requires a production build for `next start`; fall back to build if needed.
  if [ ! -d "apps/web/.next" ]; then
    echo "web .next missing; running next build..."
    (cd apps/web && npm run build --silent)
  fi
  (cd apps/web && npm run start --silent >/tmp/nw-web.log 2>&1 & echo $! >/tmp/nw-web.pid)
  WEB_PID=$(cat /tmp/nw-web.pid)
  PIDS="${PIDS} ${WEB_PID}"
  if bash scripts/check-shell-http.sh web http://127.0.0.1:3100/api/health 60; then
    pass "web /api/health"
  else
    fail "web /api/health"
    echo "--- web log tail ---"
    tail -n 100 /tmp/nw-web.log || true
  fi
  if curl -fsS http://127.0.0.1:3100/api/ready >/tmp/nw-web-ready.json && cat /tmp/nw-web-ready.json && echo ""; then
    pass "web /api/ready"
  else
    fail "web /api/ready"
  fi
else
  echo "SKIP: web boot (node_modules missing; run npm install)"
fi

echo "=== result: ${PASS} passed, ${FAIL} failed ==="
[ "${FAIL}" -eq 0 ]
