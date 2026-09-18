#!/usr/bin/env bash
# M0-01 helper: poll an HTTP health endpoint until 200 or timeout.
# Usage: check-shell-http.sh <name> <url> [timeout_seconds]
set -euo pipefail
NAME="${1:?usage: check-shell-http.sh <name> <url> [timeout]}"
URL="${2:?usage: check-shell-http.sh <name> <url> [timeout]}"
TIMEOUT="${3:-30}"

echo "waiting for ${NAME} at ${URL} (timeout ${TIMEOUT}s)..."
for i in $(seq 1 "${TIMEOUT}"); do
  if curl -fsS "${URL}" >/tmp/nerveops-health-"${NAME}".json 2>/dev/null; then
    echo "${NAME}: healthy"
    cat /tmp/nerveops-health-"${NAME}".json
    echo ""
    exit 0
  fi
  sleep 1
done
echo "${NAME}: FAILED to become healthy at ${URL}" >&2
exit 1
