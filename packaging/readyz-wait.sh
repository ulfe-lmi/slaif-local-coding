#!/usr/bin/env bash
# Bounded readiness polling for the loopback SLAIF Local Coding candidate.
#
# Usage: readyz-wait.sh [BASE_URL] [TIMEOUT_SECONDS]
#   BASE_URL        default http://127.0.0.1:18031 (loopback only)
#   TIMEOUT_SECONDS default 30
#
# Exits 0 once /readyz returns 200, exits 1 (fail closed) when the bounded
# wait elapses or the endpoint is unreachable. No retries beyond the bounded
# wait; no secrets are read, printed, or logged.
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:18031}"
TIMEOUT_SECONDS="${2:-30}"

case "$BASE_URL" in
  http://127.0.0.1:* | http://localhost:* | http://[::1]:*) ;;
  *)
    echo "readyz-wait: refusing non-loopback base URL (fail closed)" >&2
    exit 1
    ;;
esac

deadline=$((SECONDS + TIMEOUT_SECONDS))
while (( SECONDS < deadline )); do
  status="$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 \
    "${BASE_URL}/readyz" 2>/dev/null || true)"
  if [[ "$status" == "200" ]]; then
    echo "readyz: ready (${BASE_URL})"
    exit 0
  fi
  sleep 0.5
done

echo "readyz: not ready within ${TIMEOUT_SECONDS}s (${BASE_URL}) — fail closed" >&2
exit 1
