# OAP Work Order — 004-a

## Objective

Add a bounded real-Codex E2E harness for the explicitly enabled local adapter
and prove, using Codex CLI 0.149.0 against a disposable repository, that a long
synthetic `AGENTS.md`, referenced dependency, ordinary local file tools, cache
reuse, and sentinel governance work through the candidate adapter. This round
does not claim forced compaction, vision, production, gateway, or cutover
readiness.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-a`
- PR mode: `CREATE_NEW_PR`
- Existing objective PR: N/A
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head branch: `oap/004-real-codex-governed-e2e`
- Required action: exactly one new non-draft PR; coding never merges.

Post-merge state verified before activation:

```text
objective 003 PR #5: MERGED
main: 7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161
open PRs: none
```

## Verified runtime

```text
host/user: hinton1 / janezp
Codex CLI: 0.149.0 at /synology/homes/janezp/.local/bin/codex
vLLM: PID 26020 upstream on 127.0.0.1:18020, health/models HTTP 200
model: qwen3.8-27b
current image capacity: zero images
candidate adapter port: 127.0.0.1:18031, currently free
```

## Bounded scope

### A. Isolated real-Codex launcher

Add a repo-owned Python helper/test support that creates a disposable temporary
Git repository and temporary `CODEX_HOME`. Generate only that temporary Codex
config with a custom OpenAI-compatible provider pointing to
`http://127.0.0.1:18031/v1`, model `qwen3.8-27b`, response wire API, and
protected `QWEN3090_API_KEY` environment reference.

Hard requirements:

- never modify `~/.codex`, active profiles, auth files, hooks, or either OAP
  agent route;
- do not copy auth tokens into the repository or temporary config;
- run `codex exec` from the disposable repo with `workspace-write`, approvals
  never, JSON events, and an output-last-message file;
- serialize runs and impose explicit process/output/time bounds;
- retain raw Codex events only in memory or temporary files during the run;
- emit only sanitized facts: CLI version/exit/status, duration, event types and
  counts, tool-call count/names, final sentinel pass/fail, adapter metrics, and
  fixed failure reasons;
- delete temporary repository/config/events/last-message state after evidence
  extraction.

### B. Disposable governed fixture

Generate a synthetic repository with:

- long multi-section `AGENTS.md` containing a unique sentinel rule near the end;
- one referenced P1 text dependency;
- no customer/production data;
- deterministic synthetic tokens designed for pass/fail detection.

Prompt only asks Codex to inspect governance, read the referenced file with its
ordinary local tool, and return the exact synthetic acknowledgment required by
the sentinel. Do not instruct it to reveal source contents.

### C. Candidate adapter E2E run

Start one repo-owned adapter on loopback 18031 using explicit global/route
constitution enablement and static synthetic identity. Run up to three bounded
attempts only to accommodate transient CLI/model failures; stop on success.
Evidence must prove:

1. actual Codex CLI invoked the adapter, not a direct active profile;
2. at least one ordinary local file/tool call occurred;
3. adapter observed exactly one root and acquired the referenced dependency;
4. first run performed root/dependency compilation;
5. a second actual Codex invocation on the same fixture reused persistent cache
   without additional compiler calls;
6. final response satisfied the sentinel;
7. SSE/non-stream behavior, tools, errors/disconnect, and image policy tests
   remain green;
8. zero-image vision case remains truthfully `SKIPPED`/`BLOCKED`.

### D. Documentation/completeness

Document the isolated launcher, safety boundary, sanitized evidence, and
limitations. Update `oap/COMPLETENESS.md` from objective-004 15% to 35% and
overall branch readiness from ~74% to ~78%. Remaining objective-004 gaps are
actual forced/equivalent long-session compaction, vision-capable E2E, security
hardening review, and systemd candidate proof. Do not claim production/multi-user
readiness.

## Explicit non-goals

No forced compaction claim; no image/vision E2E; no active profile/cutover; no
gateway integration; no systemd installation; no raw payload logging; no client
filesystem access by adapter; no multi-user/production claim; no rewrite of OAP
history. Do not change protected vLLM, model, keys, network, firewall, VPN, or
systemd.

## Acceptance criteria

1. Isolated Codex home/config is used and active Codex configuration/profile
   hashes are unchanged.
2. Actual Codex 0.149.0 completes through candidate adapter with ordinary tool
   use and sentinel compliance.
3. Adapter metrics prove one-root observation, dependency acquisition,
   compilation, then persistent cache reuse with zero new compiler calls.
4. Raw Codex output/source/sentinel fixture content is not committed, logged, or
   reported; only approved sanitized facts are retained.
5. All existing fake-upstream behavior remains preserved.
6. Documentation/completeness are honest and explicit about remaining 004 gaps.
7. All required local gates and final-head GitHub CI pass.

## Required verification

Run exact statuses for lock/frozen sync/Ruff/format/mypy/full pytest/live suite/
build/compileall/shell syntax/diff check. Add focused helper tests for temporary
fixture/config generation and sanitized event parsing using canned events; real
Codex execution is local evidence, not GitHub CI. Perform secret/raw-content
scan, scoped diff audit, active Codex config/profile hash before/after, and
protected-host before/after snapshot. Wait for final report-head CI.

## Publication contract

Create exactly one PR titled
`[OAP 004] Add real Codex governed tool E2E`. Commit intended paths plus exact
order/active. Record implementation head after all non-report work is remote.
Atomically publish exactly one immutable
`oap/reports/004-a-real-codex-governed-tool-e2e.md`; SELF must be sole final
commit, parent equals implementation head, change only that report, and be
remote PR head before response `OK`. Label all evidence exactly; never rewrite
prior artifacts.
