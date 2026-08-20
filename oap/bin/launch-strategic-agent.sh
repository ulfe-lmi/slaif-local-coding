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
STRATEGIC_CODEX_PROFILE=${STRATEGIC_CODEX_PROFILE:-}

[[ "${OAP_ACK_LIVE_HOST_RISK:-NO}" == "YES" ]] || {
  echo "Refusing full-access strategic Codex on live model host." >&2
  echo "Review strategic/live-host rules, then set OAP_ACK_LIVE_HOST_RISK=YES in $RUNTIME_ENV." >&2
  exit 1
}
[[ -d "$REPO_ROOT/.git" ]] || { echo "Not a Git checkout: $REPO_ROOT" >&2; exit 1; }
[[ -p "$STRATEGIC_HOME/control.fifo" && -p "$STRATEGIC_HOME/response.fifo" ]] || {
  echo "OAP FIFOs missing/invalid; run bootstrap." >&2; exit 1;
}

cd "$STRATEGIC_HOME"
PROMPT=$(cat <<PROMPT_EOF
You are the OAP strategic Codex for $REPO_ROOT, running from the separate
strategic workspace $STRATEGIC_HOME. Read AGENTS.md,
strategic_model_init_material.md, OAP-COMMUNICATION-strategic.md,
ARCHITECTURE-for-agents.md, INITIAL-ROADMAP.md, and RUNTIME.md completely.
Then inspect the coding repository constitution/protocol and independently query
GitHub/live host facts. Do not execute the seed draft until every VERIFY marker
and DRAFT marker has been replaced in a strategic-workspace copy. Publish a
final order atomically with:

python $REPO_ROOT/oap/bin/publish_order.py --repo-root $REPO_ROOT \
  --source <final-order-path> --id <NNN-L>

Then signal exactly:

python $REPO_ROOT/oap/bin/oap_fifo.py send \
  --fifo $STRATEGIC_HOME/control.fifo

Wait for coding response with the matching wait command. Read the immutable
report and independently verify the exact GitHub PR, commits, SELF parent, diff,
checks, security, protected live-host state, and all acceptance criteria. Only
you may merge, and only when fully satisfied and all required checks are green.
Never become routine implementer. Keep the human informed with concise evidence,
risk, and decision summaries.
PROMPT_EOF
)

args=("$CODEX_BIN")
if [[ -n "$STRATEGIC_CODEX_PROFILE" ]]; then
  args+=(--profile "$STRATEGIC_CODEX_PROFILE")
fi
args+=(--dangerously-bypass-approvals-and-sandbox "$PROMPT")
exec "${args[@]}"
