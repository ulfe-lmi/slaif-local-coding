# OAP Work Order — 004-x

## Objective

Amend objective-004 PR #6 to record strategic acceptance of 004-w security/
observability hardening and prove the packaged Local Coding candidate under an
isolated, temporary user-systemd lifecycle on loopback port 18031, including
safe environment handling, health/readiness, bounded text/tool/stream smoke,
journal privacy, clean stop, and rollback. Never alter the protected Qwen unit,
port 18020, or active Codex profiles.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-x`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-w` SELF:
  `5f5606ded4cbe6679299fec5ba63e402fadd45f6`
- Prior implementation SHA:
  `36a2bdbaccdcfd8eb28e2a5e2deaafedda1d1c7a`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Strategically accepted prerequisite

004-w's complete findings matrix, production diff, negative tests, packaging,
privacy scans, protected-state evidence, report-only relationship, and final CI
are accepted. Update `oap/COMPLETENESS.md` at the start of this round from
objective 004 `40%` / branch `~79%` to objective 004 `60%` / branch `~83%`,
crediting the accepted security/observability hardening. Preserve remaining
compaction, vision, and systemd gaps until their own evidence is accepted.

## Authorized temporary systemd scope

This order explicitly authorizes only a disposable **user-systemd candidate**
for this repository on `127.0.0.1:18031`. It does not authorize installation,
enablement, replacement, restart, edit, link, drop-in, daemon reload, or other
mutation of `qwen-serving`, its unit, port 18020, model files/venv/launch flags,
network/firewall/VPN, keys, gateway, or Codex profiles.

Prefer a uniquely named transient user unit created with `systemd-run --user`,
or an equivalently isolated private user-manager mechanism, so no persistent
unit file is installed. If the packaged example must be rendered/linked to prove
it, use a unique temporary file outside protected paths, link only that candidate,
and remove the link/file after stop. Record exact rollback. Never overwrite or
reuse an existing unit name.

## A. Static packaging and hardening validation

Review `packaging/slaif-local-coding.service.example`, CLI/config docs, repo
venv assumptions, and current production settings. Require:

- Python 3.12/repo venv and immutable explicit config path;
- service runs as the current unprivileged user, loopback 18031 only;
- secret supplied by protected mode-0600 environment-file reference, never
  inline unit `Environment=` or argv;
- working directory, restart/timeout/kill behavior, and graceful SIGTERM;
- `NoNewPrivileges`, private temp, filesystem/home protection, safe umask,
  bounded file descriptors/tasks/memory where compatible;
- only required address families and no public bind;
- stdout/stderr journal behavior contains no raw payload/credential/private URL;
- no model loading/duplicate vLLM and no dependency on gateway/cutover.

Run `systemd-analyze verify` or the applicable user-unit verifier. Fix only
concrete packaging/docs defects and add focused static tests where durable.

## B. Protected-state preflight

Before candidate mutation, record sanitized:

- protected Qwen unit active/substate/PID/start time, unit/start-script/config
  hashes, listener 18020, bounded authenticated health/models;
- ports 18021/18031 absent;
- candidate unit name absent;
- active Codex config/profile hashes;
- repo/venv/config revisions and clean intended worktree state.

Refuse to proceed on name/port collision or changed protected prerequisite.

## C. Temporary candidate lifecycle

Create a private temporary config/cache/environment boundary. Start one unique
user-systemd candidate using current PR code on 18031. Record unit identity and
safe property values without exposing full environment/credentials/private
URLs.

Require:

1. unit reaches `active/running`, correct unprivileged UID, expected executable/
   working-directory hashes, and only loopback 18031 listener;
2. `/healthz` and `/readyz` return 200 with truthful fixed component states;
3. `/metrics` obeys configured private enablement and exposes fixed bounded
   labels only;
4. bounded authenticated model passthrough, one text response, one ordinary
   function-tool response, and one SSE response complete through the candidate;
5. no full SSE buffering regression, no raw tool/model/body data in journal,
   and no secret/canary/private URL in journal or `systemctl show` output;
6. no duplicate model process and protected service state remains unchanged.

Use synthetic canaries transiently and report only absence booleans/counts, not
values. Maximum candidate model calls: three (text/tool/stream). No vision,
compaction, governed Codex, retry loop, soak, gateway, or cutover.

## D. Stop and rollback proof

Stop the candidate through systemd and require graceful exit within configured
timeout. Verify:

- unit inactive and no child/orphan process;
- port 18031 absent;
- transient/linked unit, temporary config/env/cache, and caller-owned synthetic
  state removed; no unsafe broad deletion;
- user manager has no enabled/persistent candidate artifact or failed unit
  residue;
- protected Qwen unit/listener/hashes/PID/start time and Codex profiles match
  preflight;
- 18020 health/models still pass.

If startup/lifecycle fails due a direct packaging defect, implement the smallest
unit/config/docs/test fix and rerun the complete candidate lifecycle once. Do
not repair systemd/host policy or protected services.

## Acceptance criteria

1. Completeness records accepted hardening at objective 004 60% / branch ~83%
   before systemd credit.
2. Packaged unit validates statically and satisfies the required unprivileged,
   private, bounded hardening properties without secret-in-unit exposure.
3. One temporary user-systemd candidate on 18031 passes unit, health/readiness,
   metrics, text/tool/SSE, journal privacy, and resource/process checks.
4. Stop/rollback removes every candidate artifact/listener/process and preserves
   protected Qwen/Codex state exactly.
5. No public bind, gateway/cutover, model/service/profile mutation, raw leakage,
   or unrelated implementation change occurs.
6. Focused/full local gates and final implementation/report-head CI pass.

## Required verification

Record lock/frozen sync, Ruff check/format, mypy, focused packaging/config/app/
security tests, full pytest, build, wheel/sdist contents, systemd unit verify,
compileall, shell syntax, diff check; accepted-hardening completeness update;
pre/post protected snapshot; sanitized unit properties; exact candidate
health/readiness/metrics/text/tool/SSE statuses; model-call count; journal/
systemctl secret/raw-canary scans; process/listener/resource facts; cleanup and
rollback; dependency/scoped diff; and current GitHub checks. Wait for final
report-head CI.

## Completeness and remaining gaps

Coding leaves systemd credit pending strategic review. On complete candidate
success, strategy may raise objective 004 from 60% to 80% and branch readiness
from ~83% to ~87%. Remaining gaps are actual Codex compaction and vision-capable
E2E. No production/systemd-install/cutover readiness claim follows from a
temporary candidate proof.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable `oap/reports/004-x-systemd-candidate-proof.md`;
SELF must be the sole final commit, its first parent must equal the
implementation head, it must change only that report, and it must be remote PR
head before response FIFO `OK`.
