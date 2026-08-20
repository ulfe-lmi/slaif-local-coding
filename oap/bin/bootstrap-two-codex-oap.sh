#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: bootstrap-two-codex-oap.sh [--refresh-strategic-files]

Creates the separate strategic workspace and exact control/response FIFOs.
It does not activate an order or start either Codex agent.
USAGE
}

REFRESH=0
case "${1:-}" in
  "") ;;
  --refresh-strategic-files) REFRESH=1 ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DEFAULT_REPO=$(cd -- "$SCRIPT_DIR/../.." && pwd)
REPO_ROOT=${OAP_REPO_ROOT:-$DEFAULT_REPO}
STRATEGIC_HOME=${OAP_STRATEGIC_HOME:-/synology/homes/janezp/codex-supervision/slaif-local-coding}
SOURCE_DIR="$REPO_ROOT/oap/strategic-instructions"

[[ -d "$REPO_ROOT/.git" ]] || { echo "Not a Git checkout: $REPO_ROOT" >&2; exit 1; }
[[ -d "$SOURCE_DIR" ]] || { echo "Missing strategic source: $SOURCE_DIR" >&2; exit 1; }

mkdir -p "$STRATEGIC_HOME" "$STRATEGIC_HOME/drafts" "$STRATEGIC_HOME/workorders"
chmod 700 "$STRATEGIC_HOME" "$STRATEGIC_HOME/drafts" "$STRATEGIC_HOME/workorders"

for name in AGENTS.md OAP-COMMUNICATION-strategic.md strategic_model_init_material.md ARCHITECTURE-for-agents.md INITIAL-ROADMAP.md; do
  src="$SOURCE_DIR/$name"
  dst="$STRATEGIC_HOME/$name"
  [[ -f "$src" ]] || { echo "Missing strategic file: $src" >&2; exit 1; }
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst" && [[ "$REFRESH" -ne 1 ]]; then
    echo "Refusing to overwrite changed strategic file: $dst" >&2
    echo "Review it, then rerun with --refresh-strategic-files if replacement is intended." >&2
    exit 1
  fi
  install -m 600 "$src" "$dst"
done

for src in "$SOURCE_DIR"/initial-orders/*.md; do
  [[ -e "$src" ]] || continue
  dst="$STRATEGIC_HOME/drafts/$(basename "$src")"
  if [[ ! -e "$dst" ]]; then
    install -m 600 "$src" "$dst"
  elif ! cmp -s "$src" "$dst"; then
    echo "Preserving modified strategic draft: $dst" >&2
  fi
done

for fifo in "$STRATEGIC_HOME/control.fifo" "$STRATEGIC_HOME/response.fifo"; do
  if [[ -e "$fifo" && ! -p "$fifo" ]]; then
    echo "Path exists but is not FIFO: $fifo" >&2
    exit 1
  fi
  [[ -p "$fifo" ]] || mkfifo -m 600 "$fifo"
  chmod 600 "$fifo"
done

if [[ ! -e "$STRATEGIC_HOME/runtime.env" ]]; then
  cat > "$STRATEGIC_HOME/runtime.env" <<RUNTIME_ENV
OAP_REPO_ROOT=$REPO_ROOT
OAP_STRATEGIC_HOME=$STRATEGIC_HOME
CODEX_BIN=codex
CODING_CODEX_PROFILE=
STRATEGIC_CODEX_PROFILE=
OAP_ACK_LIVE_HOST_RISK=NO
RUNTIME_ENV
  chmod 600 "$STRATEGIC_HOME/runtime.env"
fi

cat > "$STRATEGIC_HOME/RUNTIME.md" <<RUNTIME_MD
# OAP runtime facts

\`REPO_ROOT=$REPO_ROOT\`  
\`STRATEGIC_HOME=$STRATEGIC_HOME\`  
\`CONTROL_FIFO=$STRATEGIC_HOME/control.fifo\`  
\`RESPONSE_FIFO=$STRATEGIC_HOME/response.fifo\`

The coding loop consumes control \`OK\` before starting each fresh coding Codex.
Strategic publishes order+active atomically, sends control \`OK\`, waits response
\`OK\`, then independently reviews GitHub and alone decides/merges.

Protected live development state: vLLM historically uses 18020; candidate adapter
uses 18031. No port-18021 image proxy is assumed. Verify the actual coding Codex
profile/provider endpoint and all listeners live; do not infer from this file.
RUNTIME_MD
chmod 600 "$STRATEGIC_HOME/RUNTIME.md"

if [[ ! -e "$STRATEGIC_HOME/workorders/EXECUTION_TIMINGS.md" ]]; then
  cat > "$STRATEGIC_HOME/workorders/EXECUTION_TIMINGS.md" <<'TIMINGS'
# OAP execution timings

| Objective | Activated | PR opened | Merged/closed | Rounds | Notes |
|---|---|---|---|---|---|
TIMINGS
  chmod 600 "$STRATEGIC_HOME/workorders/EXECUTION_TIMINGS.md"
fi

mkdir -p "$REPO_ROOT/oap/orders" "$REPO_ROOT/oap/reports"

cat <<EOF2
OAP bootstrap complete.

1. Edit: $STRATEGIC_HOME/runtime.env
2. Set OAP_ACK_LIVE_HOST_RISK=YES only after reviewing protected-host rules.
3. Terminal A: $REPO_ROOT/oap/bin/launch-coding-agent.sh
4. Terminal B: $REPO_ROOT/oap/bin/launch-strategic-agent.sh

No order is active. The strategic Codex must verify live GitHub/host state,
finalize a draft, publish it with publish_order.py, then send exact control OK.
EOF2
