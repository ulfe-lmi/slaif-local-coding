# OAP Work Order — 004-g

## Objective

Amend objective-004 PR #6 to identify the exact boundary causing Codex CLI
0.149.0 `workspace-write` command execution to fail on hinton1 and, only if a
Codex-supported OS-enforced sandbox path can be made to work without weakening
policy, restore one successful ordinary dependency read through the candidate
adapter. Do not use danger-full-access or claim governance/sentinel completion
unless a successful completed read crosses the API boundary.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-g`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-f` SELF:
  `3c932e5176408d0925fa7a9981a6e3060a5ca611`
- Prior implementation SHA:
  `620770d65e237d7f8020485ecf89ee1e8d489f1e`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; implementation/report-head `test`
  checks SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Independently verified blocker and strategic basis

`004-f` proved the generated dependency is a regular private non-symlink file
that the same user can read byte-identically. Both fresh Codex attempts instead
returned command exit 1 with the same bounded diagnostic hash/class
`sandbox_denied`; neither completed a read, exposed observed dependency bytes,
or supported governance-derived sentinel attribution. Objective 004 remains
35% complete.

Current official Codex documentation states that `workspace-write` is the
intended unattended local mode and that `codex sandbox` runs a command under the
same policies Codex uses internally:

- `https://learn.chatgpt.com/docs/developer-commands?surface=cli`
- `https://learn.chatgpt.com/docs/agent-approvals-security`

The installed CLI exposes `codex sandbox`, `codex exec --sandbox
workspace-write`, profile/config overrides, and a working-directory selector.
This round must use those supported interfaces to distinguish sandbox bootstrap
or host capability failure from an E2E invocation/config/event-shape defect.

## Bounded scope

### A. Direct sandbox-policy preflight

Add a disposable, no-model preflight using the installed `codex sandbox`
helper against a synthetic private repository/file under the same temporary
root style as the E2E fixture. Run a minimal read-only command under the resolved
`workspace-write` policy and record only:

- CLI version and fixed platform/kernel capability labels needed to interpret
  sandbox availability;
- process exit/status, timeout, bounded byte lengths/hashes, and fixed first-line
  diagnostic class/subclass;
- whether working directory and target are inside the disposable repository;
- resolved sandbox mode/profile/feature labels without raw config, paths, or
  credentials.

Do not retain or report raw stdout/stderr, source, command output, private paths,
environment values, tokens, or credentials. The preflight must not call the
model, candidate adapter, or protected upstream.

### B. Boundary classification

Compare the direct helper result with the nested `codex exec` command lifecycle
and classify exactly one of:

```text
workspace_sandbox_available
host_sandbox_bootstrap_unsupported
workspace_root_resolution_mismatch
invocation_config_precedence_error
command_event_schema_mismatch
unresolved_with_fixed_evidence
```

Tests must prove deterministic mapping and raw-text non-retention. Do not infer
file permission failure after the already-passing same-user control.

### C. Safe remediation and one fresh governed proof

If the direct helper succeeds, correct only the E2E launcher/config/parser defect
established by evidence. Final governed execution must retain:

- `workspace-write` OS-enforced sandboxing;
- approvals `never`/no interactive escalation;
- disposable `CODEX_HOME` and repository;
- explicit local candidate provider on 18031;
- no active profile/config mutation;
- the governance-only token boundary and all prior lifecycle/provenance gates.

Run at most two fresh actual Codex invocations total in this round: one after the
evidence-based correction and, only if needed, one identical confirmation or one
documented supported invocation variant. No retry loop.

If `codex sandbox` itself cannot execute the minimal read on this host, do not
switch to `danger-full-access`, bypass sandboxing, loosen file modes, mutate the
host/kernel, or claim success. Publish `BLOCKED|PARTIAL` with the fixed
classification and evidence needed for a later human/architecture decision.
`read-only` may be used only as a non-model diagnostic comparison; it does not
satisfy the final workspace-write Codex E2E contract.

### D. Outcome, tests, and documentation

If a workspace-write Codex command completes, require exactly one intended
dependency read, zero failed commands, observed-byte hash/length provenance,
cache stored-source equality against observed bytes, and the dependency-derived
sentinel. Only that full result may raise objective 004 from 35% to 40% and the
branch total from ~78% to ~79%.

Otherwise leave completeness unchanged and document the exact fixed blocker.
Add focused tests for preflight command construction, timeout/output bounds,
classification, privacy, invocation precedence, and success/failure gating.

## Explicit non-goals

No danger-full-access, bypass-sandbox flag, approval weakening, host/kernel/
container modification, protected Qwen/vLLM/model/key/network/firewall/VPN/
systemd/profile mutation, forced compaction, vision, gateway, production,
multi-user, or cutover claim. No rewrite of prior OAP artifacts. No raw
diagnostic persistence or broad host troubleshooting.

## Acceptance criteria

1. A no-model `codex sandbox` preflight truthfully establishes whether the same
   workspace policy can read the disposable dependency on this host.
2. The failure boundary receives one deterministic fixed classification with
   bounded privacy-preserving evidence.
3. Any remediation is evidence-based and retains `workspace-write`, approvals
   never, disposable state, and all protected-host constraints.
4. At most two fresh actual Codex invocations run; success requires the complete
   lifecycle/provenance/cache/sentinel gate, while failure leaves completeness
   unchanged.
5. Focused tests cover command construction, bounds, classifier mapping,
   invocation/config precedence, privacy, and final gating.
6. Documentation and completeness claims match actual results.
7. All exact local gates and final implementation/report-head CI pass.

## Required verification

Record exact statuses for lock check, frozen sync, Ruff check/format, mypy, full
pytest, build, compileall, shell syntax, and diff check. Run focused sandbox-
preflight/E2E tests. Include secret/raw-content and private-path scans, scoped
diff audit, current-head GitHub checks, and protected-host before/after snapshot.
The seven opt-in live-suite skips remain skips; the specifically authorized
fresh Codex runs are separate required evidence. Wait for final report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, host sandbox/kernel configuration, or
active Codex profiles. A runtime service-log append caused by bounded calls is
not an authorized configuration mutation and must not be edited/restored.

## Local authority

Coding owns safe repo-local dependencies, temporary fixtures, diagnostics, and
test execution. Do not recruit the human or strategy as terminal operator. Any
required host sandbox/kernel change is outside this order and must be reported,
not performed.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-g-workspace-sandbox-compatibility.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.
