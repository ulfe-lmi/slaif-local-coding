# OAP Coding-Agent Report — 014-b

## Work order
- Identifier: `014-b` (numeric objective `014`, round `014-b`)
- Order path: `oap/orders/014-b-reject-rc3-close-qualification-gaps-and-qualify-private-rc4.md`
- PR mode: AMENDED_EXISTING_PR (PR #19 only; created in round 014-a, amended this round)

## Status
COMPLETE

## Executive summary
RC3 (round 014-a) was rejected as a release candidate for five independently
verified defects (publication preceded a successful aggregate security gate;
internally inconsistent record schema; argv privacy exposure of the smoke
prompt and private upstream URL; unenforced execution bounds; manually
asserted compatibility facts). Its published identity, scoped smoke evidence
(ledger 002), and 014-a report are preserved immutable. This round closed all
five defects (qualification harness v2; schema/record repair with
manifest-verified evidence binding; RC3→RC4 reconciliation), froze a new
source, re-ran a fresh genuine Codex 0.149.0 qualification (testing ledger
003, PASS), passed every prepublication gate including the separate
aggregate CodeQL policy check, and published the collision-safe private
candidate `0.1.0-rc4` — exactly two tag aliases to one digest — only after
the gates succeeded. Final-head CI (five jobs + two CodeQL workflow
analyses + the aggregate CodeQL policy check) is fully green, `docker-
published` pulled the actual image by digest and passed all 13
qualification phases, and the evidence-bound RC4 record/handoff and
rc-published provenance manifest are committed. No benchmark, no final
public release, no cutover, no merge.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #19 <https://github.com/ulfe-lmi/slaif-local-coding/pull/19> — OPEN, non-draft
  (title/body updated to the final RC4 outcome this round)
- Base: `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`
- Head branch: `oap/014-real-codex-compatibility-rc3` (not renamed, not recreated,
  not force-pushed)
- Starting remote SHA (014-a report SELF): `2cc49e60405d87b16e8271cd129374077dd46323`
- Implementation head SHA: 014e0d188eac6d5063ceff629a0fc97ab5d7f02e
- Report publication commit: SELF
- Implementation commits pushed before report (oldest → newest, all remote):
  - `f503e7d092d5ced85391fe2fd66d977f9f7ad347` — WS-A: qualification harness v2
    (stdin prompt, secret-free argv, disposable Codex home, live byte caps,
    explicit ceilings; CodeQL alert #10 real fix)
  - `e8ec35bc817aae94b5ce275aed47695d9bf41c21` — WS-B + WS-C.1: RC record
    evidence binding, companion schema identity v3, RC3→RC4 reconciliation,
    RC3 archive
  - `c48f9456ba8f44339aedbe6688aa8cd6db7a8994` — source: objective-field
    assertion follows the 014-b provenance rebind (source A)
  - `601a7f9fae19869ad8e09f10fa994550368fd87c` — S4: provenance manifest v5
    re-bound to A (derived metadata only; image source commit)
  - `fad9d239694afba8794ece8aa19642f63caf3f79` — WS-D: testing ledger 003
    (real Codex RC4 qualification, PASS)
  - `f0cd2c79aa7521dcd5710a0fb7e1beb2d25b4292` — source: bind the
    state-conditional qualification-label gate to the generator constants
    (RC3→RC4 identity residue found during this round's post-publication
    local verification; the only source change after S4)
  - `014e0d188eac6d5063ceff629a0fc97ab5d7f02e` — WS-C.6: record published RC4
    (post-publication metadata only: record, handoff, rc-published manifest
    re-bound to `f0cd2c79…`) — implementation head
- New PR this round: NO; amended existing PR #19: YES; merge performed: NO

## Changes and files
- `scripts/real_codex_rc_qualification.py` (+ pure tests): harness v2 — fixed
  synthetic prompt delivered over stdin (Codex 0.149 documented stdin mode);
  no prompt substring in any process argv; private backend URL supplied only
  through a mode-0600 disposable file reference read into a protected
  environment (never argv, never `-c` config arguments); provider/catalog
  settings in the disposable Codex home/config; live stdout/stderr byte
  ceiling (1 MiB) that terminates the session and records only a sanitized
  failure class; explicit tested ceilings (adapter requests ≤ 64, compiler
  calls ≤ 4, tool interactions ≤ 8, attempts ≤ 2, per-attempt 600 s, total
  5400 s, arm count 4) with content-free bounded counting; CodeQL
  `py/clear-text-storage-sensitive-data` alert #10 resolved by writing only
  the environment-variable name (never the credential value) into generated
  Codex configuration; disposable state removed with absence proof.
- `packaging/rc_artifact_record.schema.json`: `$id` and `properties.schema`
  consistently `slaif-rc-record-v3`; docs/comments that called the active
  record v2 corrected (archived historical v2 files byte-identical).
- `scripts/rc_artifact_record.py`: compatibility section now DERIVED from one
  manifest-verified closed-schema facts file (ledger MANIFEST.sha256 closed-
  set verification; exact client identity; overall + per-arm PASS;
  no-Gateway topology; wheel equal to the candidate manifest wheel;
  protected state unchanged; disposable state removed; DIRECT contextual
  result); tamper/missing/mismatch/BLOCKED fail closed; no manual verdict
  CLI assertions; deterministic handoff rendering from the validated record.
- `scripts/release_provenance_manifest.py`, `scripts/release_registry_publish.py`,
  `.github/workflows/release-image.yml`, `.github/workflows/ci.yml`,
  `scripts/docker_qualification_ci.py`, `scripts/operator_session_ci.py`,
  provenance generator constants: RC3→RC4 candidate identity reconciled
  (publisher accepts exactly `0.1.0-rc4`; final/stable denylist unchanged).
- `packaging/releases/0.1.0-rc3/`: byte-identical archive of the RC3
  record/handoff/manifest (RC1/RC2 convention).
- `docs/HISTORY.md`, `docs/RC-HANDOFF.md`, `docs/RELEASE-ARTIFACT-POLICY.md`:
  RC3 non-acceptance documented (smoke passed; publication preceded a
  successful aggregate security gate; schema/harness defects found in later
  review) and RC4 identity recorded.
- `oap/evidence/testing-ledger/003/`: sanitized closed-schema RC4
  qualification facts + README + closed-set MANIFEST.sha256 (content-free).
- `tests/`: focused privacy/bounds/cleanup/ceiling tests; companion
  schema/record consistency regression; evidence-binding tamper classes;
  state-conditional qualification-label gate bound to generator constants
  (final source commit).
- `packaging/rc_record.json` (slaif-rc-record-v3), `packaging/rc_handoff.md`,
  `packaging/release_provenance_manifest.json`: post-publication metadata
  (record + rendered handoff first committed; manifest re-bound in
  rc_published state).

## Acceptance evidence
### Criterion 1 — exact diff/commit/PR identity; no second PR
- PR #19 is the only PR for objective 014 (014-a created it; 014-b amended
  it). Branch head advanced strictly: `2cc49e6…` → `f503e7d…` → `e8ec35b…` →
  `c48f9456…` → `601a7f9…` → `fad9d23…` → `f0cd2c7…` → `014e0d1…`; remote
  verified via `git ls-remote` after each push. No force-push, no rename.
### Criterion 2 — ledger/archive byte-identity (001, 002, RC1, RC2, RC3)
- Ledgers 001/002 + RC1/RC2: 14/14 files byte-identical to the 014-a SELF
  `2cc49e6…` (re-verified this round): PASSED.
- RC3 archive: `rc_record.json` sha256 `45a6ce5d7666afda2d8b5352701190a70d08d08496cb2380f3ee7f01c15e6492`,
  `rc_handoff.md` `28a21d26e18cfbbd470ab83b786acbda4b768f17e105b3b9623991686cabf4a8`,
  `release_provenance_manifest.json` `2cc28c9d1fbefb2dd6e8cf3561628296d1ce28a2cc79f640e84474e7649bc6d5`
  — byte-identical to the RC3 record set as it stood at publication
  (pre-archive identity): PASSED.
- Ledger 003 MANIFEST.sha256 closed-set verified (covers exactly the ledger
  directory, manifest self-exempt; both listed hashes match): PASSED.
- RC3 registry identity untouched: `0.1.0-rc3` and
  `sha-307a929ffb30f4ea41c8be4e8a5ea25802e25142` still resolve to
  `sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436`
  (read-only authenticated registry check at publication time; RC3 tags
  never rewritten by the RC4 publisher, which verified RC4 aliases absent
  first).
### Criterion 3 — focused image-policy / namespace-tool regressions green
- Focused set (image policy, full-app namespace-tool envelope, real-Codex
  qualification harness, RC record, provenance manifest, source-input
  binding, docker qualification record gate, docs consistency):
  224 passed, 0 failed locally at the implementation head; included in the
  final-head CI `test` job (1421 passed). PASSED.
### Criterion 4 — companion RC schema/record consistency + tamper tests
- `test_rc_record.py` companion-schema regression + closed-key/value-class
  gates + tamper classes (digest flip, tag drift, wheel drift, extra key,
  missing compatibility, wrong schema, BLOCKED facts, drifted working
  tree): all pass locally and in final-head CI. PASSED.
### Criterion 5 — reproducibility, artifact inspection, noneditable smoke
- Clean `git archive` builds of `f0cd2c79…` on CPython 3.12.3
  (`/usr/bin/python3.12`) and 3.12.14 (`~/.local/bin/python3.12`):
  wheel byte-identical across both = `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
  (= W4, = in-image wheel), sdist byte-identical across both =
  `5bfcd702f3496c418b7f03fa0d2ef262dd8a6c4b8375c37d2e90042e13014d2b`
  (465903 bytes; differs from the S4-era sdist only in the one test file).
  The W4 == RC3-wheel equality is because this round changed no wheel input
  (`src/` untouched) — documented in the manifest limitations, HISTORY, and
  ledger 003. `source_input_map.py --ab f0cd2c79… 014e0d18…` →
  "input-map A/B binding OK … (126 input files)"; `--ref f0cd2c79…` →
  "input-map ref OK". CI `uv build` + `artifact_policy_check.py --inspect`
  + fresh-venv noneditable install smoke passed in the final-head `test`
  job. PASSED.
### Criterion 6 — fresh exact-S4 prepublication CI + aggregate CodeQL before the release workflow
- Prepublication gate at exact S4 `601a7f9fae19869ad8e09f10fa994550368fd87c`
  (CI run 36395023328, 2026-09-28): all 8 check runs SUCCESS — test
  108839260268 @ 08:04:42Z; docker 108839260048 @ 08:04:14Z;
  operator-session 108839260271 @ 08:03:43Z; gateway-contract
  108839260295 @ 08:02:55Z; docker-published 108839260304 @ 08:02:55Z
  (pre-publication mode: explicit NOT RUN, exit 0); Analyze (python)
  108839250710 @ 08:03:40Z; Analyze (actions) 108839250945 @ 08:03:41Z;
  aggregate GitHub Advanced Security `CodeQL` 108839519183 @ 08:03:36Z.
  No pending/failed/cancelled/missing check; 0 open branch alerts at the
  time. Publication run 36395861883 started 08:11:15Z — after every gate
  above completed SUCCESS. PASSED.
### Criterion 7 — authenticated absent-before / present-after RC4 tags
- Publication run 36395861883 (release-image.yml workflow_dispatch from
  exact S4; success 08:12:03Z; check run `build-and-publish`
  108841969887 SUCCESS @ 08:12:02Z): in-workflow wheel
  `897ef605…` == committed manifest wheel (W4); log line
  `registry before: sha-601a7f9f… = verified absent; 0.1.0-rc4 = verified
  absent` @ 08:11:43.548Z (authenticated strict, rechecked immediately
  before each write); publish began 08:11:45.152Z; source alias resolved
  @ 08:11:55.889Z; log line `registry after: sha-601a7f9f… = present at
  sha256:a4f2014c…; 0.1.0-rc4 = present at sha256:a4f2014c…` @
  08:12:00.337Z. Exactly the two aliases, one digest
  D4 = `sha256:a4f2014c7dae1e21f965f35e09b3c877c89c18bc7c8cdc0dddf7cea117584f7f`.
  PASSED.
### Criterion 8 — actual pulled D4 Docker qualification + all ordinary final-head jobs
- Final-head CI run 36398453378 at `014e0d18…` (2026-09-28): five ordinary
  jobs SUCCESS — test 108850333428 @ 08:39:26Z; docker 108850333832 @
  08:38:55Z; docker-published 108850333749 @ 08:38:29Z; gateway-contract
  108850333885 @ 08:37:36Z; operator-session 108850333756 @ 08:38:22Z —
  plus Analyze (actions) 108850334929 @ 08:38:04Z, Analyze (python)
  108850335182 @ 08:38:34Z, and the separate aggregate `CodeQL` policy
  check 108850515243 @ 08:37:57Z, all SUCCESS; 0 open code-scanning alerts
  repository-wide. `docker-published` ran in RC-published mode: pulled
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:a4f2014c…` by digest, pulled
  both tags and asserted each resolves to D4 (image `.Id` + RepoDigests +
  authenticated strict registry lookups), verified the full OCI label set
  against the committed manifest (incl. qualification label
  `rc-candidate-0.1.0-rc4; private; not final release`), then passed all
  13 qualification phases with summary PASSED: verify_wheel_binding (W4,
  manifest rc_published), compose_rendered_validation (no secret values),
  pull_preexistence_no_build (digest form, no build), fake_upstream_start,
  adapter_stack_up (healthy), in_image_provenance (non-editable, lock
  closure 18/17 pinned, W4), bridge_positive_signed (chat/chat-stream/
  models/tool-roundtrip 200 with sentinel match), bridge_negative_contract
  (401/403/409), config_time_rejection, fail_closed_readiness (readyz 503),
  image_content_scan (6484 files, 0 forbidden matches), hardening_and_labels,
  teardown_absence_proof (containers/listeners absent on 18031/18033/18034).
  PASSED.
### Criterion 9 — final-head CodeQL workflow + aggregate policy, no open alert
- Final head: `Analyze (actions)` 108850334929 SUCCESS, `Analyze (python)`
  108850335182 SUCCESS, aggregate `CodeQL` 108850515243 SUCCESS — recorded
  as separate facts; workflow analysis success is NOT claimed as a
  substitute for the aggregate policy check (the 014-a false claim is not
  repeated). Open code-scanning alerts at the final head: 0. PASSED.
### Criterion 10 — genuine corrected-harness VISION/CACHE/BOTH PASS + DIRECT
- Testing ledger 003 (`oap/evidence/testing-ledger/003/`, schema
  `slaif-real-codex-rc-qualification-v2`, created 2026-09-28T08:07:11Z,
  overall PASS): retained Codex CLI 0.149.0 standalone
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`;
  topology `disposable-codex-home;loopback-adapter;port-18031;
  existing-backend;gateway-ingress-disabled`; VISION PASS (2×200 adapter
  requests, 0×500/422, 0 upstream failures, 0 compiler calls, 1 bounded
  tool interaction, sentinel present), CACHE PASS (2×200, compiler call 1 +
  cache entry 1), BOTH PASS (2×200, compiler call 1 + cache entry 1),
  DIRECT PASS contextual (0 adapter requests — direct-to-backend control);
  1 attempt per arm; every ceiling enforced (arms 4 ≤ 4, tools 1/arm ≤ 8,
  adapter ≤ 64, compiler ≤ 4, output cap 1 MiB, per-attempt 600 s, total
  5400 s); tested wheel binding equal to W4; protected state 13 files
  checked / 0 changed, units `qwen-serving-vision.service` active +
  `qwen-serving.service` inactive, ports 18020:1 / 18031:0; disposable
  state removed. Sanitized, content-free, MANIFEST.sha256-bound. PASSED.
### Criterion 11 — protected fixture unchanged; loopback 18031 absent
- Ledger 003 before/after within the WS-D run: 13 protected files / 0
  changed. Post-round read-only recheck (this report): all 13 files present
  with pre-existing mtimes (most recent 2026-09-28 06:04:10 +0200, predating
  this round's activity); units active/inactive as before; the vllm process
  is the same long-lived fixture PID 23961 (uptime 21 d 15 h — the fixture
  recorded since 2026-09-06 in the 013-n report, i.e. no restart this
  round); listeners: 18020 → 1 (vllm), 18031 → 0. PASSED.
### Criterion 12 — private visibility; no benchmark; no Gateway mutation; no cutover; no final release
- Unauthenticated GHCR manifest probe: `unauthorized` (private package
  access denied) — re-probed this round. The final-head docker-published
  baseline used the job's ephemeral `packages:read` token (read-only).
  No benchmark task ran (no benchmark repository access). No Gateway
  mutation. No protected-host cutover. No final/stable tag, no GitHub
  Release. Record carries `final_public_release: false`,
  `cutover_performed: false`, `private_registry_auth_required: true`.
  PASSED.

## Verification
- `uv run --frozen python -m pytest tests/ -q` (local, implementation head): PASSED — 1422 passed, 26 skipped, 0 failed. (CI `test` job at the same tree: 1421 passed, 27 skipped — the single delta is `test_target_semantic_preflight_failure_precedes_protected_selection`, gated on a host-pinned rehearsal path present only on this machine; honestly SKIPPED on the CI runner, not a weakened gate.)
- `uv run --frozen ruff check .`: PASSED — all checks passed.
- `uv run --frozen ruff format --check .`: PASSED — 410 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues found in 81 source files.
- Focused set (image policy, namespace-tool envelope, qualification harness, RC record, provenance manifest, source-input binding, docker qualification gate, docs consistency): PASSED — 224 passed, 0 failed.
- `uv build --out-dir … --python /usr/bin/python3.12` and `--python ~/.local/bin/python3.12` from clean `git archive f0cd2c79…` trees: PASSED — wheel byte-identical (= W4) and sdist byte-identical across both interpreters.
- `uv run --frozen python scripts/source_input_map.py --ab f0cd2c79… 014e0d18… --manifest packaging/release_provenance_manifest.json`: PASSED — A/B binding OK (126 input files); `--ref f0cd2c79…`: PASSED.
- Byte-identity checks (ledger 001/002, RC1/RC2 vs `2cc49e6…`; RC3 archive hashes; ledger 003 closed-set manifest): PASSED (see Criterion 2).
- Registry probes: unauthenticated GHCR → `unauthorized` (private denial): PASSED; authenticated before/after evidence from publication run logs (Criterion 7).
- Protected host read-only recheck (files/units/PID/ports): PASSED (Criterion 11).

## Live model/service evidence
- Bounded authenticated use of the existing protected Qwen/vLLM vision
  fixture (loopback 127.0.0.1:18020) occurred only inside the WS-D
  qualification run through the disposable 18031 adapter, per ledger 003:
  VISION/CACHE/BOTH adapter 2×200, 0×500/422, 0 upstream failures per arm;
  no credential or private URL printed, logged, or committed.
- Fixture unchanged: same vllm PID 23961 (no restart), units
  active/invariant, 18020 single listener, 18031 absent at round end.

## GitHub CI / required checks
- Implementation head `014e0d18…` (run 36398453378, 2026-09-28): test
  108850333428 SUCCESS @ 08:39:26Z; docker 108850333832 SUCCESS @
  08:38:55Z; docker-published 108850333749 SUCCESS @ 08:38:29Z (13/13
  phases against pulled D4); gateway-contract 108850333885 SUCCESS @
  08:37:36Z; operator-session 108850333756 SUCCESS @ 08:38:22Z;
  Analyze (actions) 108850334929 SUCCESS @ 08:38:04Z; Analyze (python)
  108850335182 SUCCESS @ 08:38:34Z; aggregate CodeQL 108850515243 SUCCESS @
  08:37:57Z. Open alerts: 0.
- Prepublication gate at S4 (run 36395023328): all 8 check runs SUCCESS
  (Criterion 6).
- Transient note (truthful): intermediate source commit `f0cd2c79…` had
  CI run 36398000065 FAILURE in the `test` job only
  (`test_real_repo_source_inputs_bound_to_committed_source` — working tree
  carried the corrected input map while that commit still recorded the
  pre-fix manifest map). This is inherent to the two-commit
  source-fix-then-rebind sequence (same pattern as `e8ec35b…`→
  `c48f9456…` earlier this round) and was resolved by the manifest rebind
  at the final head; the final head is the order's gate target
  (WS-C.7) and is fully green.
- All required checks green at drafting: YES. The report-only push may
  trigger new checks on the report commit; strategy verifies those
  independently (per protocol §8).

## Local setup/dependencies
- Repo-owned `uv` venv, `uv run --frozen` everywhere (lock
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`).
- Clean builds used two existing CPython 3.12 patch versions (3.12.3
  system, 3.12.14 user-local) in fresh `mktemp -d` directories; no `rm -rf`,
  no new dependencies, no host Docker, no sudo.
- Disposable qualification state (Codex home, config, URL file ref,
  temp dirs) created 0600 and removed with absence proof; no durable
  docs/config changes beyond the order's scope.

## Documentation
- Updated in-round: `docs/HISTORY.md` (RC3 non-acceptance + RC4 record),
  `docs/RC-HANDOFF.md` (record v3 + RC4 identity),
  `docs/RELEASE-ARTIFACT-POLICY.md` (RC4 identity), manifest limitations
  and tag convention (published state), order 014-b scope in the
  qualification harness docstrings. Consistency enforced by the
  `docs_consistency_check.py` gate in the final-head `test` job (green).

## Safety/scope confirmations
- Unrelated files: none touched; pre-existing human/unrelated work
  preserved; zero-byte untracked `Local`/`clean`/`unchanged` preserved
  untracked.
- Secrets/raw content: none committed, printed, or logged; registry
  evidence is digest/tag-level only; qualification facts are
  content-free (counts, hashes, verdicts, timings).
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO (read-only checks before/after; same long-lived vllm PID
  23961).
- Required tests skipped/not run: only honest environment skips (SLAIF_
  GATEWAY_ROOT, SLAIF_LIVE_TEST, SLAIF_VISION_ACCEPTANCE, host-pinned
  rehearsal path) — identical skip law to prior rounds; no scope
  deviation.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: NO.
- Active/order edited: NO (order + `oap/active` committed byte-exact in
  the round's activation commit, untouched since).
- Report commit report-only: YES (single path
  `oap/reports/014-b-reject-rc3-close-qualification-gaps-and-qualify-private-rc4.md`).

## Known limitations/blockers
- `docker-published` at the S4 head ran in pre-publication mode (explicit
  NOT RUN); the actual D4 qualification happened at the final head as the
  order requires (Criterion 8). Both facts are reported separately.
- The sdist recorded for RC4 (`5bfcd702…`) was rebuilt from the post-fix
  source `f0cd2c79…`; it is a developer-only artifact — the published
  image/wheel identities (D4/W4, built from S4) are unchanged and
  independently bound in the record (`image_source_commit` = S4,
  `workflow_head_sha` = S4, run 36395861883).
- Single RTX 3090 fixture evidence is fixture-scoped, not generic
  production equivalence; no multi-user/production/compliance claim.
- No unresolved blockers.

## Recommended strategic follow-up
- Strategy may independently verify: the report-head checks (the report
  push triggers a fresh run on the report commit), PR #19 state, the RC4
  identity (D4/tags/W4/S4/run), and the private-registry facts; then alone
  decide acceptance, merge, and any next order (e.g. benchmark on the
  separate VM by pulling D4 by digest — the handoff enables that without a
  rebuild — or a separately authorized final release). Factual only;
  strategy decides.

BENCHMARK_READY
