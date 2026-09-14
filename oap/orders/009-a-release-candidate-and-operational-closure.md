# OAP WORK ORDER 009-a — RELEASE CANDIDATE AND OPERATIONAL CLOSURE

Strategic work order 009-a, final. All live facts below were independently
verified by the strategic agent on 2026-09-14 (Europe/Ljubljana) via
authenticated gh, remote git, read-only host probes, and repository
inspection. No VERIFY/DRAFT markers remain.

## Objective

Turn the accepted Local Coding implementation (Objectives 000–008, all merged)
into a truthful, reproducible deployment candidate, in one coherent PR:

1. reconcile all current-facing documentation with merged software truth;
2. close release-artifact/packaging with an explicit supported-artifact policy
   and mechanically proven artifact contents;
3. provide one primary supported deployment path (systemd user service on the
   local host, repository venv) with a complete operator contract;
4. exercise all deployment mechanics in a disposable environment against fake
   loopback upstreams only;
5. produce a content-free release/deployment provenance manifest;
6. prepare — without executing — the exact final live-cutover/rollback runbook.

This objective performs no protected-service mutation, no live cutover, and no
release publication. On acceptance, the only remaining work toward production
must be the real protected cutover/release act itself, under separate
human-authorized order.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective: `009` (first unused; verified 2026-09-14: `oap/orders/` contains objectives 000..008 (through 008-b); 009 is unused).
- Round: `009-a`; mode: `CREATE_NEW_PR`.
- Required base/default branch: `main` at 1a913bf3520e7570042774ef7c8ca5153da7a671 (verified 2026-09-14 via `git rev-parse origin/main` after fetch).
- Verified remote state at order time: no open PRs (`gh pr list --state open` returned `[]`, verified 2026-09-14).
- Verified last merge: PR #10 (objective 008) merged 2026-09-13T22:02:12Z; merge commit 1a913bf3520e7570042774ef7c8ca5153da7a671 = main.
- Verified CI on base: GitHub Actions run 34785566603 on 1a913bf3520e7570042774ef7c8ca5153da7a671: status completed, conclusion success (2026-09-13T22:02:14Z); required jobs `test` and `gateway-contract` both green.
- Required branch: `oap/009-release-candidate-and-operational-closure`.
- Create exactly one non-draft PR. Never merge; never enable auto-merge.

## Strategic context and independently verified current state

Merged and accepted (one PR per numeric objective, PR #1–#10):

- 000–004: adapter foundation, observation, compiler/cache, working-set
  injection, real-Codex E2E + security/observability/operations hardening.
- 005: SLAIF Gateway integration, merged/accepted under its documented
  composed closure (signed-identity adapter contract, cross-repository real
  Codex acceptance, protected-acceptance matrix, cutover-closure evidence).
- 006: signed-request replay hardening.
- 007: current cross-repository Gateway contract CI.
- 008: durable acceptance evidence and fail-closed safe-evidence export.

The original roadmap meanings formerly associated with numeric 006/007/008
(e.g. "SME package") are historical planning prose, not live objective
identifiers. This objective 009 implements the original milestone
"reproducible SME package and honest release evidence" as a milestone name.

Verified peer/facts at order time:

- Gateway peer: ulfe-lmi/slaif-api-gateway @ 65666f5886832034c52211fdd7604046557e6ada; verified 2026-09-14 as the gateway repository's current default-branch main (remote commit exists, merged 2026-09-13T02:05:49Z, PR #301) (local fixture
  `tests/fixtures/gateway/current_peer_authority.json` pins the same commit;
  module contract versions: local-coding-v1 module_version 2 (replay_mode process_local_inclusive_horizon_fail_closed), codex-0.149-responses-v1 module_version 4).
- Protected host (read-only): hinton1, read-only 2026-09-14: user unit qwen-serving-vision.service active (running) since Sun 2026-09-06 18:57:26 CEST, main PID 23961 (vllm, model qwen3.8-27b), listener 0.0.0.0:18020, GET /health = 200; port 18021 absent; port 18031 absent (no dev adapter running).
- Coding vision profile: ~/.codex/qwen-neumann.config.toml present, mode 0600, mtime 2026-09-13 11:59 local (unchanged).
- Packaging state at base: current dist/slaif_local_coding-0.1.0-py3-none-any.whl: 26 entries, only slaif_local_coding/ and slaif_local_coding-0.1.0.dist-info/ (incl. LICENSE/NOTICE under licenses/) — verified clean; current dist/slaif_local_coding-0.1.0.tar.gz: 404 entries, incl. 290 oap/ entries (orders/reports/active/evidence/bin), scripts/, docs/, .github/, and untracked placeholder files Local/clean/unchanged; pyproject.toml defines no explicit sdist policy (hatchling default) — confirmed not an accepted release artifact.
- Existing deployment assets at base: `packaging/slaif-local-coding.service.example`
  (hardened user-unit example, external 0600 EnvironmentFile, loopback-only),
  `config/adapter.example.toml` (loopback 18031 candidate config),
  `tests/test_packaging.py` (static unit/config contract tests).
- Residual coding-repo working-tree state (not committed; not part of any PR):
  uncommitted local edit to `oap/runtime.env.example` (strategic runtime
  profile values); untracked empty placeholder files `Local`, `clean`,
  `unchanged` at repository root. Coding must preserve these without
  committing or deleting them, and the build policy must ensure the
  placeholders can never enter any artifact.

## Bounded scope (workstreams A–F)

A. Current-state documentation truth reconciliation.
B. Release artifact / packaging closure.
C. Reproducible appliance / operator closure (one supported path).
D. Disposable operational qualification (fake upstream only).
E. Release provenance manifest + final live-cutover plan (prepare only).
F. Regression / CI gates.

## Explicit non-goals

- No mutation, stop, restart, or reconfiguration of the protected Qwen
  service: `qwen-serving`/`qwen-serving-vision.service`, port 18020,
  model/checkpoint/patches/venv/launch flags, systemd production units,
  API-key files, firewall/VPN/network bindings, or active Codex profiles.
- No live cutover, no Gateway implementation/deployment change, no real key
  provisioning, no public binding, no TLS, no tag creation, no artifact
  publication to any registry, no release-state change.
- No OCI/Compose or any second deployment system; systemd local-host user
  service is the single supported path for this objective.
- No model weights, no model download, no Qwen/protected-model inference,
  no benchmark/capacity/soak/model-quality work.
- No Gateway/Responses protocol refactor or other elegance refactor of the
  proven implementation.
- No rewrite or edit of immutable OAP orders/reports (`oap/orders/`,
  `oap/reports/`); their content may be referenced, never altered.
- No broad protected-acceptance rerun; Objectives 005–008 evidence remains
  accepted as-is.
- No multi-user, production-certification, compliance, or
  frontier-equivalence claims.

## A. Current-state documentation truth reconciliation

A1. Independently reconcile at least these files against merged remote truth
and this order: `README.md`, `oap/COMPLETENESS.md`,
`ARCHITECTURE-for-agents.md`, `ARCHITECTURE.md`,
`docs/IMPLEMENTATION-ROADMAP.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`,
`docs/ADAPTER-CONFIGURATION.md`, `SECURITY.md`, `TESTING.md`.

A2. Every current-facing statement must truthfully distinguish, with exact
merged-PR/SHA evidence, at least these states:
`implemented and merged`; `real-E2E accepted`; `continuously
Gateway-contract tested`; `packaged`; `deployment-qualified (disposable
environment only)`; `cutover not performed`; `not released`. No document may
present the original planned meanings of numeric 006–008 as live objective
identifiers. Original product milestones may be preserved as milestone names
only, explicitly separated from the OAP numeric history.

A3. Known stale statements to correct (non-exhaustive; find all others):
README "Current status: objectives 000–004 … objectives 005–006 remain
separate milestones"; `oap/COMPLETENESS.md` "~91% readiness" table with 005 at
5% and 006 at 20% under original planned semantics;
`docs/IMPLEMENTATION-ROADMAP.md` presenting planned 005/006 meanings as live
identifiers; `ARCHITECTURE-for-agents.md` "Planned objective boundaries" and
"005 gateway+cutover; 006 SME package/release"; `ARCHITECTURE.md` objective
boundary list; "current" gateway-pin/cutover-preparation statements in
`docs/SLAIF-GATEWAY-INTEGRATION.md`, `SECURITY.md`, `TESTING.md` that predate
Objectives 006–008.

A4. Documentation changes must not add claims beyond accepted evidence. After
this objective is accepted, the truthful position is: functional integration
accepted; security hardening accepted; current Gateway CI accepted; durable
evidence accepted; clean reproducible package accepted; disposable
install/upgrade/rollback accepted; truthful docs current; cutover NOT
performed; NOT released.

A5. Do not edit `oap/orders/`, `oap/reports/`, or any accepted evidence
artifact while reconciling docs.

## B. Release artifact / packaging closure

B1. Declare an explicit supported-artifact policy, documented in the repo
(naming the policy location is yours; it must be linked from README and the
deployment doc). Directive: the wheel is the single supported distributable
for deployment; the sdist is a developer-only source archive, not a supported
release artifact. Whichever design is implemented, the policy must be
deliberate and documented, not an accidental backend default.

B2. Implement explicit Hatch build include/exclude policy for both targets
(`[tool.hatch.build]` and sdist target), replacing default behavior. No
artifact (wheel or sdist) may contain: `oap/orders`, `oap/reports`,
`oap/active`, `oap/evidence`, `oap/bin`, orchestration transcripts, strategic
or coding runtime state (e.g. `runtime.env`), temporary/placeholder files
(including untracked `Local`, `clean`, `unchanged`), caches/venvs
(`__pycache__`, `.venv`, `*.pyc`), host-specific artifacts (paths under
`/synology`, hostnames), credentials or key material, or model weights.
Preserve the verified-clean wheel property (runtime package plus metadata and
license files only).

B3. Prove artifact contents mechanically: a deterministic, machine-executable
policy check (script and/or pytest gate) that builds or inspects both
artifacts and fails on any forbidden entry or missing required entry (e.g.
runtime package present, license notices present). The check must be part of
local gates and CI (see F).

B4. Install the built release candidate into a fresh, empty, disposable
Python environment (venv, not an editable checkout) using only the built
wheel, and prove: package imports, the `slaif-local-coding` console entry
point resolves and runs (`--help`/version behavior), and runtime source
provenance (installed file location is inside the disposable environment, not
the repository checkout; entry point script and module paths recorded as
evidence).

B5. If the sdist is retained as developer-only, prove it is not publishable by
accident: the policy check must assert the sdist contents against the same
forbidden set, and the docs must state that only the wheel is the supported
deployment artifact. (Clean-sdist alternative: if you instead make the sdist
fully clean, the same mechanical proof applies and the policy doc must say so.)

B6. Do not add model weights, vendor the Gateway, or add hidden
hosted/account-bound components. Any new dependency, if unavoidable, must be
documented, locked in `uv.lock`, and justified in the report.

## C. Reproducible appliance / operator closure

C1. Establish exactly one primary supported deployment path: systemd user
service on the local host running the adapter from a repository-owned
environment, based on and superseding `packaging/slaif-local-coding.service.example`
and `config/adapter.example.toml` where needed. Justify from current source
review that this remains the intended path; do not add OCI/Compose.

C2. Provide the minimum complete, reviewable asset set (templates + one
canonical operator/deployment document linked from README):
  - service/unit template (evolved from the existing example; keep
    loopback-only networking, hardening directives, external EnvironmentFile);
  - protected environment/config-file contract (mode-0600 env file holding
    credential values by env name only; mode-0600/0640 config file; no
    secrets in unit, argv, or documentation);
  - explicit runtime user/path/permissions assumptions;
  - startup/readiness ordering (dependencies, post-start readiness polling of
    `/readyz` with a bounded wait and fail-closed operator guidance);
  - cache/state directories and permissions (default protected cache
    0700 dir / 0600 files; XDG fallback; explicit cache purge/rebuild);
  - logging/privacy behavior (journal output; no raw prompts/source/images/
    tool output/bodies in logs; sanitized errors);
  - start/stop/restart/status commands (exact operator commands);
  - upgrade procedure: backup previous configuration (exact backup path,
    mode, and contents) → install/replace exact new artifact → restart →
    verify readiness + contract smoke → confirm or roll back;
  - rollback procedure: mechanical restore of the exact previous artifact and
    configuration from the backup, with post-rollback verification;
  - uninstall/disable procedure removing only package-owned files/units while
    preserving external model, Gateway, and explicitly retained configuration.

C3. No secret may appear in any unit file, argv, example, template, or
document. Extend the static artifact tests to assert this across all new
packaging assets.

C4. Do not install, enable, or alter the actual protected service or any
persistent system/user unit of this host in this objective. Any unit used for
qualification must be transient/unique-named and fully removed with proof (see
D).

## D. Disposable operational qualification

D1. Exercise the deployment mechanics in a disposable environment (empty
prefix/venv + temporary state directories), using only fake/mock loopback
upstreams (reuse existing fake-upstream test support where adequate). No
package step, install step, or qualification step may reach any
model/provider/network endpoint beyond deliberately local fake services and
the routine package index for dependency installation; specifically never
port 18020, the protected vLLM, any Gateway, or any real provider.

D2. Verify port 18031 is free before and after; the disposable candidate
binds only loopback:18031; no listener of the candidate may remain after the
round (prove with socket inspection).

D3. Prove, from the built artifact and the deployment assets:
  - fresh install into an empty disposable prefix/environment (wheel only);
  - valid config creation from the documented template (no manual editing
    beyond documented placeholder substitution);
  - candidate starts on 127.0.0.1:18031 and reaches ready;
  - `/healthz`, `/readyz`, and private `/metrics` behave as documented;
  - representative Responses and Chat streaming requests plus ordinary
    function-tool forwarding work against the fake upstream (SSE event order,
    tool call/result envelopes, usage preserved);
  - stop/restart is clean (no orphan process, no partial state corruption);
  - an upgrade using the supported procedure preserves only intended
    configuration/state (exact before/after inventory diff of config/state/
    cache treatment; derived cache is disposable);
  - rollback restores the previous artifact and configuration mechanically;
  - a failed upgrade/start (injected at a defined point) leaves a recoverable
    previous configuration, from which the service starts again.

D4. Use systemd verification if safely available (e.g. `systemd-analyze
verify` and/or a unique transient `systemd-run --user --collect` unit on
18031). Absence of a utility or host limitation is not a blocker: validate
the same unit contract deterministically another way (extended static
contract tests plus direct venv-execution lifecycle proof) and record exactly
what was and was not proven.

D5. No broad protected-acceptance rerun; Objectives 005–008 remain accepted.

D6. Complete cleanup: every disposable prefix, venv, temporary unit, state
directory, and process removed; record absence proof.

## E. Release provenance and final cutover plan (prepare only)

E1. Produce a content-free machine-readable release/deployment provenance
manifest for the candidate (schema-versioned) containing exactly this class of
facts: local Git SHA; current approved Gateway peer SHA; Local/Gateway module
contract versions (local-coding-v1 / codex-0.149-responses-v1 and their
versions); Python runtime and package version; lockfile and build-input
hashes; release artifact SHA-256 and size; configuration/template hashes;
accepted reference compatibility versions where already public contract facts
(model name `qwen3.8-27b`, vLLM OpenAI-compatible `/v1` interface, Codex
0.149.0 wire fixtures); exact limitations and deployment status
(deployment-qualified disposable only; cutover not performed; not released).

E2. The manifest and its generator must exclude, by construction and by test:
host paths, credentials, provider keys, private identifiers, prompts, model
output, and raw acceptance payloads. Durable acceptance evidence
(`oap/evidence/`) stays separate from the runtime/package artifact and the
manifest.

E3. Add a test that regenerates/validates the manifest against the actual
build inputs and fails on drift or forbidden content.

E4. Produce the exact final live-cutover/rollback runbook as documentation
(canonical location your choice; linked from the deployment doc and README):
current live configuration capture → install exact Local artifact → start
candidate privately (18031) → verify candidate → configure/pin Gateway route
→ representative real Codex text/tool/vision smoke → verify no unintended
direct-vLLM bypass → rollback proof → deliberate final switch. Mark each step
with its authority class: `CODING-SAFE` vs `HUMAN-AUTHORIZED
(protected/live/release)`. The runbook must make the eventual final operation
small and mechanical, with explicit preconditions (this objective accepted and
merged) and explicit rollback triggers. Do not execute any step. Do not mutate
the protected Qwen service, Gateway deployment, Codex profiles,
firewall/VPN/network, systemd production state, public binding, or release
state in this objective.

## F. Regression / CI gates

F1. Keep the current production behavior and current Gateway contract intact.
The `gateway-contract` job must continue running against the exact pinned
peer ulfe-lmi/slaif-api-gateway @ 65666f5886832034c52211fdd7604046557e6ada; verified 2026-09-14 as the gateway repository's current default-branch main (remote commit exists, merged 2026-09-13T02:05:49Z, PR #301) (fixture `tests/fixtures/gateway/current_peer_authority.json`
unchanged unless remote Gateway main moved since order time; at order time it
has not — do not re-pin silently).

F2. The `test` job (or a clearly named job in the same workflow) must run, in
addition to the existing gates: Ruff check; Ruff format check; mypy; complete
ordinary local pytest; `uv build`; `python -m compileall`; `bash -n` shell
validation; plus new: wheel and sdist/release-artifact content policy
inspection (B3) and the fresh-artifact install smoke (B4) on the CI runner.

F3. All CI green on the PR head before the report is published: no failed,
cancelled, pending, or missing required checks.

F4. Do not refactor the proven Codex/Gateway protocol implementation. No
runtime behavior change beyond packaging/deployment/docs unless required to
satisfy an acceptance criterion (any such change must be called out in the
report with rationale).

## Security / privacy / secrets / resource / protected-host constraints

- Protected host access for this order is READ-ONLY plus bounded disposable
  candidate service on verified-free 127.0.0.1:18031 and disposable local
  files. No mutation of 18020, `qwen-serving*` units/files, model/venv/
  patches, API keys, firewall/VPN/network, or active Codex profiles.
- No raw prompts, source, images, tool output, request/response bodies,
  credentials, or private URLs may be committed, logged, or placed in any
  artifact, report, or manifest.
- Disposable candidate traffic uses synthetic fixtures only.
- Record protected-host state (unit state, PID, 18020 listener, 18031/18021
  absence) before and after the round; any discrepancy is a report-blocking
  finding.

## Local authority

Coding owns all safe routine setup: repository-local venvs/tools, disposable
prefixes, fake services, transient uniquely-named user units (if used), and
their complete removal. The human and strategic agent are not terminal
operators or log couriers.

## GitHub publication and immutable report contract

1. Start exactly from `origin/main` at 1a913bf3520e7570042774ef7c8ca5153da7a671 (verified 2026-09-14 via `git rev-parse origin/main` after fetch); create branch
   `oap/009-release-candidate-and-operational-closure`.
2. Implement, test, push all non-report work, create exactly one non-draft PR
   before the report; never merge.
3. Inspect and repair in-scope CI until green.
4. Capture the literal 40-hex implementation head SHA.
5. Publish exactly one immutable report at
   `oap/reports/009-a-release-candidate-and-operational-closure.md` containing
   `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`.
6. The report commit changes only that report; its first parent equals the
   literal implementation SHA; it is the remote PR head before the exact
   response FIFO `OK`.
7. The report must contain, per workstream A–F: exact commands, sanitized
   evidence, artifact hashes, the disposable install/upgrade/rollback
   evidence, before/after protected-host facts, CI check states observed, and
   an explicit limitations section. An intermediate in-scope failure is work
   to fix inside this round, not a stopping point, unless a genuine
   protected/live/release authority boundary is reached — in which case report
   exactly what is blocked and why.
