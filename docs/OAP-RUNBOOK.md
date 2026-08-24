# Two-Codex OAP runbook

## Topology

```text
coding Codex cwd: /synology/homes/janezp/codex-work/slaif-local-coding
strategic Codex cwd: /synology/homes/janezp/codex-supervision/slaif-local-coding
control: strategic -> control.fifo -> coding
response: strategic <- response.fifo <- coding
wire payload: exact bytes OK, no newline
```

Coding gets one fresh Codex process per active round. Strategic remains the
long-lived control plane. GitHub is remote software truth; repository OAP files
are orchestration truth; FIFOs only wake/synchronize.

## Bootstrap once

```bash
cd /synology/homes/janezp/codex-work/slaif-local-coding
bash oap/bin/bootstrap-two-codex-oap.sh
```

Review strategic `runtime.env`, profile names, and protected-host law. Set
`OAP_ACK_LIVE_HOST_RISK=YES` only after deliberate review. Start coding launcher
first, then strategic launcher in separate terminals.

## Strategic activation

1. Read strategic constitution/protocol/architecture/roadmap.
2. Independently inspect GitHub and relevant live host state.
3. Edit a strategic-workspace draft; remove all draft/placeholders.
4. Dry run and publish:

```bash
python /synology/homes/janezp/codex-work/slaif-local-coding/oap/bin/publish_order.py \
  --repo-root /synology/homes/janezp/codex-work/slaif-local-coding \
  --source /absolute/final/order.md --id NNN-L --dry-run

python /synology/homes/janezp/codex-work/slaif-local-coding/oap/bin/publish_order.py \
  --repo-root /synology/homes/janezp/codex-work/slaif-local-coding \
  --source /absolute/final/order.md --id NNN-L
```

5. Send control and wait response:

```bash
python /synology/homes/janezp/codex-work/slaif-local-coding/oap/bin/oap_fifo.py send \
  --fifo /synology/homes/janezp/codex-supervision/slaif-local-coding/control.fifo

python /synology/homes/janezp/codex-work/slaif-local-coding/oap/bin/oap_fifo.py wait \
  --fifo /synology/homes/janezp/codex-supervision/slaif-local-coding/response.fifo
```

Both commands may block indefinitely by design.

## Coding round

The wrapper consumes control `OK`, validates local OAP state, and launches one
full-access coding Codex using `CODING_CODEX_PROFILE`. Coding reads exact active
order, implements, pushes, creates/amends PR, publishes final report-only SELF
commit, verifies remote state, writes response `OK`, then exits. Wrapper waits
for next control signal.

Coding never merges. `NNN-a` creates one PR; `NNN-b..z`, then `NNN-aa..zz`, amend it.

## Strategic review

After response:

- require active equals sent ID and one matching report;
- verify PR identity/base/head and literal implementation SHA;
- resolve SELF to report-containing remote head;
- verify SELF changes only report and first parent=implementation SHA;
- review diff against every objective round, constitution, architecture,
  security, tests, docs, protected-host law, and non-goals;
- verify every required current-head check successful;
- merge only if strategically satisfactory; verify remote main afterward;
- otherwise publish next same-PR letter or escalate/wait/abandon explicitly.

## Read-only state snapshot

```bash
python oap/bin/check_state.py \
  --repo-root /synology/homes/janezp/codex-work/slaif-local-coding \
  --strategic-home /synology/homes/janezp/codex-supervision/slaif-local-coding
```

## Recovery

- Control send blocked: coding launcher absent; order remains inert/durable.
- Response wait blocked: coding turn incomplete/crashed; do not merge/advance.
- Coding wrapper exited: inspect active/order/report/GitHub; restart only after
  understanding partial state.
- Published order but active write interrupted: `publish_order.py` may recover
  only when the existing matching target is byte-identical to source; otherwise
  preserve and inspect.
- Existing final report: never overwrite or replay; inspect its Git commit.
- Duplicate PR: preserve both, do not auto-close/merge; deliberate remediation.
- Strategic restart: reconstruct from active/order/report/GitHub, not memory.

## Protected host

Ordinary objectives use candidate port 18031. Never mutate port 18020,
qwen-serving/model/venv/patches/systemd, firewall/VPN/bindings/keys, or active
Codex profiles without a dedicated explicit rollback-proven order. Port 18021
is not presumed occupied; live reconnaissance decides whether it is free.

For an unchanged gateway with one shared service-Bearer credential, set
`[constitution.rehydration].enabled = false` unless the route is explicitly
single-user. This preserves current-request governance but disables zero-root
post-compaction rehydration; it does not provide trusted multi-user identity.

Objective-005-c ended `FAILED` during the disposable gateway rehearsal. The
standard text/SSE/one-image subset and teardown completed, but the pinned
gateway rejected the real Codex 0.149.0 tool envelope before accounting for
that request. Do not treat this as gateway Codex acceptance or retry live
diagnostics from the coding turn; review the immutable report and address the
gateway/tool-contract blocker through a new authorized order.

Objective-005-d recorded the resulting security-containment incident in
[the containment record](OBJECTIVE-005D-SECURITY-CONTAINMENT.md). Its bounded
no-model differential used four fresh disposable Codex homes and a loopback
fake Responses provider. The pinned gateway rejected every captured envelope
before reservation with `responses_hosted_tool_not_supported`; ordinary local
`function`/`custom` declarations remained while hosted `tool_search` and/or
`web_search` declarations remained. `--ignore-user-config`, supported feature
disables, and a disposable catalog-only variant did not produce configuration-
only compatibility. The corrected rehearsal driver now emits this preflight
and refuses Docker, PostgreSQL, gateway/adapter listeners, and Qwen work when
the gateway rejects it. Completeness and cutover status remain unchanged.
