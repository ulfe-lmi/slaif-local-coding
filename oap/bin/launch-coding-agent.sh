#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DEFAULT_REPO=$(cd -- "$SCRIPT_DIR/../.." && pwd)
STRATEGIC_HOME=${OAP_STRATEGIC_HOME:-/synology/homes/janezp/codex-supervision/slaif-local-coding}
RUNTIME_ENV=${OAP_RUNTIME_ENV:-$STRATEGIC_HOME/runtime.env}
[[ -f "$RUNTIME_ENV" ]] || { echo "Missing runtime env: $RUNTIME_ENV" >&2; exit 1; }
# shellcheck disable=SC1090
source "$RUNTIME_ENV"

REPO_ROOT=${OAP_REPO_ROOT:-$DEFAULT_REPO}
STRATEGIC_HOME=${OAP_STRATEGIC_HOME:-$STRATEGIC_HOME}
CODEX_BIN=${CODEX_BIN:-codex}
CODING_CODEX_PROFILE=${CODING_CODEX_PROFILE:-qwen38-vision}
CONTROL_FIFO="$STRATEGIC_HOME/control.fifo"
RESPONSE_FIFO="$STRATEGIC_HOME/response.fifo"

[[ "${OAP_ACK_LIVE_HOST_RISK:-NO}" == "YES" ]] || {
  echo "Refusing full-access Codex on live model host." >&2
  echo "Review AGENTS.md protected-host law, then set OAP_ACK_LIVE_HOST_RISK=YES in $RUNTIME_ENV." >&2
  exit 1
}
[[ -d "$REPO_ROOT/.git" ]] || { echo "Not a Git checkout: $REPO_ROOT" >&2; exit 1; }
[[ -p "$CONTROL_FIFO" && -p "$RESPONSE_FIFO" ]] || { echo "OAP FIFOs missing/invalid; run bootstrap." >&2; exit 1; }

cd "$REPO_ROOT"

echo "Coding OAP loop ready; profile=$CODING_CODEX_PROFILE; waiting on $CONTROL_FIFO" >&2
while true; do
  "$REPO_ROOT/oap/bin/oap_fifo.py" wait --fifo "$CONTROL_FIFO"
  "$REPO_ROOT/oap/bin/check_state.py" \
    --repo-root "$REPO_ROOT" --strategic-home "$STRATEGIC_HOME" >/dev/null

  PROMPT=$(cat <<PROMPT_EOF
You are the OAP coding Codex. The external wrapper has already consumed one exact
strategic FIFO OK. Work in $REPO_ROOT. Read AGENTS.md,
OAP-COMMUNICATION-coding-agent.md, ARCHITECTURE-for-agents.md, SECURITY.md,
TESTING.md, oap/active, and the one exact matching order. Reconcile GitHub before
mutation. Execute only that order. Obey the protected live-host boundary: discover and preserve the current Codex
vision provider path; no pre-existing image proxy is assumed. Never alter
protected model/Codex/network state unless the active order explicitly authorizes
it. Create/amend the
correct PR, never merge. Publish the immutable report as the final report-only
SELF commit, verify it remotely, then send exactly two bytes OK with:

$REPO_ROOT/oap/bin/oap_fifo.py send --fifo $RESPONSE_FIFO

Do not ask the human or strategic agent to perform routine terminal/setup work.
If blocked or failed, publish truthful evidence and signal according to protocol.
PROMPT_EOF
)

  set +e
  "$CODEX_BIN" exec --profile "$CODING_CODEX_PROFILE" \
    --dangerously-bypass-approvals-and-sandbox "$PROMPT"
  rc=$?
  set -e
  if [[ "$rc" -ne 0 ]]; then
    echo "Coding Codex exited with status $rc before wrapper could confirm a completed round." >&2
    echo "The wrapper will stop; strategy must recover from OAP/GitHub truth." >&2
    exit "$rc"
  fi
  echo "Coding Codex process ended; returning to control FIFO wait." >&2
done
