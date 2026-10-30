# OAP Round Report — 017-s: local fixture preparation and Python rehearsal

Status: COMPLETE for the round scope (all ordered work executed and
verified; independent strategic review/acceptance pending; genuine
native, handoff-execution and v1 items remain NOT RUN by scope, as
listed below). Acceptance is never automatic from green CI.

Implementation head SHA: d51f4967bd8737575631b758819533da559c2520
Report publication commit: SELF

## Objective, PR, and reconciled state

- Order: `oap/orders/017-s-local-fixture-preparation-and-supervision.md`
  (63 lines); `oap/active` = `017-s\n` (5 bytes). Both committed in the
  first S implementation commit `9c8bdb8` and byte-unchanged through
  the implementation head (verified by path-scoped history at
  `d51f496`).
- PR #25 `https://github.com/ulfe-lmi/slaif-local-coding/pull/25`,
  branch `oap/017-cache-read-observation`, base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. AMEND_EXISTING_PR. No
  second PR, no merge, no auto-merge.
- R SELF `aaa35165f96d5d3413ea283f6a19817b5c3e6ce4` and sole
  implementation parent `2ce9dcd904126be8458ae9e8391cc2bc4cae9ada` at
  start; the single S control OK was consumed exactly once via the
  existing wait and never re-read or replayed.
- Commit chain this round: `9c8bdb8` (source+docs A1) -> `3b33a5d`
  (docs consistency A2) -> `305219b` (manifest B1; CI test FAILED,
  preserved) -> `eee8cee` (typing A3) -> `fc7647e` (manifest B2; CI
  test FAILED, preserved) -> `54ef177` (hermetic test premises A4)
  -> `2a9c44e` (manifest B3; all 10 checks SUCCESS — the rehearsal
  checkpoint) -> `b4fb5ef` (post-run docs A5) -> `d51f496` (manifest
  B4 = final implementation head; B4 changes ONLY the development
  provenance manifest; sole parent A5).
- Source A5 `b4fb5ef28874ae8c50979962ccaba2eff5af029f`; manifest B4 /
  implementation head `d51f4967bd8737575631b758819533da559c2520`;
  development manifest: 193 source inputs, objective `017-s`,
  `--verify` OK at the implementation head.
- `src/` unchanged across S (diff vs `2ce9dcd` empty); no
  frozen-publication-path change; wheel identity unchanged from P and
  R (`1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`,
  142,753 B); development sdist refreshed to
  `4cc93e2d267f3945202bc0b20e3aad940d18c659a5f52cdf18ac5be7b611a0ca`
  (842,826 B — carries all public test files including the new 017-s
  local suite; developer scripts remain deliberately sdist-excluded).
- The measured rehearsal source is the earlier implementation head
  `2a9c44e2ee327b965828bafdfcaf444abc3a581c` (source inputs
  `54ef177`); the post-rehearsal docs/manifest commits A5/B4 are NOT
  the measured source and are not relabeled as such.

## Scope delivered (16 paths, +7996/−166 vs R implementation head)

- `scripts/cache_native_fixture_local.py` (+3820): the repo-owned
  stdlib-only local preparer/supervisor — one long-lived non-Codex
  Python fixture owner (supervisor) behind the protected bounded
  prepare / observe / rehearse / finish / abort lifecycle (single RAM
  run context; one non-resettable 1800 s END anchor + one bounded
  600 s cleanup grace; cumulative non-resettable ledger; exact CID
  registered BEFORE start with image/build-intent/env-file
  registration; protected 0700 control root with 0600 socket/state
  files OUTSIDE the disposable work root; owner-side self-convergence
  on caller death; container termination by docker on the exact
  registered CID only — no host PID signalling); thin CLI driver and
  bounded control client (exact run-id binding, closed response
  records, absolute client budget, expired-anchor refusal before IO).
- Reuse, not copy: R's validated image/model/controller/exporter/
  stand-in, guarded executor, measured confinement, single run
  deadline and ledger, artifact acquisition and ownership helpers
  (`scripts/cache_native_fixture_ci.py` +484/−123 — the narrow shared
  helper extraction preserving all existing tests/security meanings
  and the R/P hosted-only entry guards; controller +84/−7; stand-in
  +220/−3 — observe dispatch and closed diagnostic seams). No general
  framework; the 3500-line CI runner was not copied.
- Section 2 verified local endpoint binding: read-only lstat of the
  documented default unix socket (must exist as a socket file; never
  connected) corroborated by the daemon-declared name equal to this
  host's hostname through the pinned bound executor; every run Docker
  child inherits a FROZEN once-per-owner environment with DOCKER_HOST
  pinned to that verified socket and the overriding context selection
  removed (stored currentContext or later HOME/DOCKER_CONFIG/
  DOCKER_CONTEXT drift cannot redirect a later action); explicit
  remote selection refuses before any mutation; no endpoint value is
  ever echoed.
- `tests/test_cache_native_fixture_local.py` (+2674): 49 tests —
  order-bound opt-in vs the production hosted-env guard (ambient
  GITHUB_ACTIONS refused at construction with no attempt recorded)
  plus an explicit hosted-refusal negative and one-attempt admission;
  the single-owner protected lifecycle through the real control
  client; variant-aware finish compositions (python-rehearsal /
  unobserved / external) with the retained summary bound to the
  decoded payload and cross-variant forgery negatives; the curated
  subject-facts closed contract; the section-2 endpoint binding;
  driver composition negatives (same-session refusal, startup wait
  timeout, capture-cap fault, final-wait expiry refusing before a
  blocking wait, held reader and read-error faults, valid baseline
  with real retained-evidence validation); public main refusals
  (missing state, expired anchor before IO). Fake
  Docker/socket/time/identity seams plus tiny exact-owned Python
  children only; no docker daemon, namespace or syscall probe; no
  secrets forwarded.
- `tests/test_cache_native_fixture_ci.py` (+42): shared-seam tests for
  the extracted guarded executor/env binding (hosted default
  behavior preserved).
- Docs: `docs/CACHE-OBSERVATION-CONTRACT.md` (+107/−9, section 11d
  with the measured rehearsal facts), `docs/CACHE-REWORK-LEDGER.md`
  (+82/−4), `TESTING.md` (+46/−5, local-suite paragraph; count 49),
  `ARCHITECTURE.md` (+27/−3), `ARCHITECTURE-for-agents.md` (+1/−1) and
  both mirrors byte-identical (root, `oap/strategic-instructions/`,
  strategic-local; verified by `cmp`). The compact map header states
  rounds 017-a through 017-r reports published with 017-s active and
  its measured Python-only rehearsal outcome — it does not preclaim
  S's own publication.
- `oap/active` (+1/−1: `017-r` -> `017-s`), the activated S order
  (+63, immutable), the immutable R report (+334, R's own
  publication carried in the diff), and the development manifest
  (+10/−9, B4).

## The ONE local rehearsal (single attempt; PASS)

- Command (order-bound opt-in; literal `017-s` + literal bound head,
  verified read-only against the bound repository):
  `scripts/cache_native_fixture_local.py rehearsal --order 017-s
  --bind-head 2a9c44e2ee327b965828bafdfcaf444abc3a581c` with fresh
  protected work/evidence roots under the 0700 root
  `/home/janezp/oap-017s-work/20261025T223626Z/`.
- Driver record: `{"status": "pass", "owner_exit": 0,
  "run_id": "c8fed899fcc64c0faf8115dac5880080", "evidence_sha256":
  "a48dda367ecd62022f4fd21d359547b8c101d02ada9d69cd906c682f8fbf9dce",
  "reason": null}`; exit 0; wall ~50 s.
- Evidence: `local-evidence.json`, schema
  `slaif-017s-local-evidence-v1`, 8,496 B, 0600 uid janezp under the
  0700 root; independently validated PASS by strategic against the
  current pure validator.
- Lifecycle: prepare measured the same reviewed confinement as R —
  subject 21002/21002 groups [21002] (own primary gid variant),
  1 GiB / CPU 1 / PIDs 96 / swap v2-swap-max, 68 mount records
  scanned with 5 masked /dev/null aliases (runc maskPaths) and four
  64 MiB writable-data mounts (`/dev/shm` 0777:0, `/run/slaif-ctl`
  0700:21001, `/run/slaif-subj` 0700:21002, `/tmp` 0777:21002 —
  256 MiB effective total), controller 21001:21001 PID 1,
  log-driver none, network none, keyring errno add_key/
  request_key/keyctl all 1; PTY attached with env handoff verified
  (0600 env file under 0700, exactly the two synthetic keys
  CODEX_HOME/SLAIF_SYNTHETIC_API_KEY, profile
  `early-beta.config.toml` sha256 `33204499...`, zero wire,
  diagnostic state unobserved at prepare). The exact CID
  `abec10b55bc5ff4053dcd5f59268077e186916cd16bf0703810a99c13cd5c6ac`
  was registered BEFORE start and bound across ALL phases — it
  remained alive through preparation, the diagnostic consume and
  quiesce/freeze/export, with its final absence verified only during
  terminal teardown (the phase `cleanup: absent-verified` labels in
  the record summarize that final teardown, not phase-time removals).
- Consume (Python stand-in under 21002, not native): 3 requests, 1
  admitted, 2 refused — the missing and wrong variants refused, the
  one valid diagnostic admitted; response `fixed-final-text-no-tools`
  with no issued calls.
- Finish: quiesce `closed-pass` (handlers/owned-subject/owned-tools/
  provider-sockets stopped, zero active connections, zero residual
  writers); controller ledger 5 requests (3 auth + 1 quiesce + 1
  export); retained capture 2,991 B, export sha256
  `751e17eb...`, revalidated and bound to the decoded payload
  (observed_at_position 0; observed_at_finish diagnostic/wire 3 /
  observed); export before teardown, publication after verified
  teardown.
- Teardown: container present-before true -> removal absent-verified;
  image removal absent-verified (image id
  `sha256:d02f5a43...`, identity-vs-CI honestly false — no
  byte-equivalence claim); descendants 1 -> 0; sentinel survived;
  owner converged without its backstop; env file removed
  (sha256 `1ed06f55...`); work+control roots destroyed on the pass
  path (evidence root retained).
- Ledger (host, non-resettable): api_requests 5 / api_attempts 5 /
  admitted 3 / refused 2 / healthz 1; docker_admissions 34 /
  docker_refusals 0; bytes_drained 23,763 / bytes_retained 23,763.
  The host ledger (5) and the controller ledger (5) and the consume
  requests (3) are distinct measured quantities, not one counter.
- Safety flags: `native_started: false`, `native_ready: false`,
  `codex_invoked: false`, `worker_stopped: false`,
  `deadline_expired: false`; attach plan `executed: false` with argv
  exactly `codex --yolo --profile early-beta` (inert; S never
  executes it, including help/version).
- Artifact (static preparation only): public Codex 0.164.0 musl,
  tag `rust-v0.164.0`, commit
  `6aaac694803004a63c6f393d153c96d22521a6b9`, archive
  sha256 `90dd0b03...` (114,979,035 B), binary sha256
  `b93f6811...` (308,139,304 B), LICENSE/NOTICE identities retained,
  `signature_verification: not-run`.
- Engine 29.1.3, runc 1.4.0-0ubuntu1, runner kernel 7.0.0-38-generic,
  Python 3.12.15, x86_64.
- Read-only post-run verification: `docker image inspect
  slaif-fixture-017r:local` no-such-object; no container matching
  `slaif-fixture-017s`; no leftover fixture owner/sentinel processes.
- The ONE attempt is consumed; no second attempt is authorized in S;
  additional local attempts require a later order.

## Verification record (all at literal implementation head d51f496
unless stated)

- Full local TESTING gate (process-local umask 022 in the same
  pytest invocation): `uv lock --check` 0; `uv sync --frozen --extra
  dev` 0; `ruff check` "All checks passed!"; `ruff format --check` 0
  (546 files); `mypy src tests` 0 (114 source files);
  `scripts/docs_consistency_check.py` 0 (19 claim docs); `compileall
  src scripts` 0; `artifact_policy_check --inspect` ok /
  `--install-smoke` ok, 0 violations; full pytest: **2969 passed, 28
  skipped, 0 failed** (494.68 s).
- Fixture suites at the implementation head: 584 tests (207 model +
  219 CI-runner + 33 controller + 76 stand-in + 49 local); P
  containment helper suite 61 tests unchanged in meaning; all pass
  in the full gate.
- Focused privacy scan of the round diff `2ce9dcd..d51f496` (7,996
  added lines) with the closed pattern set: key-literal 0 hits;
  private-upstream host/port 0 hits; long-base64 payloads 0 hits;
  bearer 0 hits; secret-assignment 1 hit classified benign:
  synthetic fake credential construction in
  `scripts/cache_native_fixture_local.py` (fixed `slaif-synthetic-`
  prefix plus truncated SHA256 of a per-run token; fake credential
  for the private loopback fake provider per order section 3; not a
  real credential). No real API keys, gateway keys, bearer headers,
  cookies, private URLs, or raw bodies appear in the diff.
- Development provenance: manifest B4 (source A5 `b4fb5ef`, objective
  `017-s`) 193 source inputs match the current checkout; `--verify`
  OK. Clean git-archive reproduction at the implementation head
  (`/home/janezp/oap-017s-work/archive-final-b4fb5ef-v1`, 0700):
  archive of `d51f496`; 193/193 source-input SHA256s verified against
  the manifest; `uv build` reproduced byte-identical artifacts — sdist
  `slaif_local_coding-0.1.0.tar.gz` 842,826 B sha256
  `4cc93e2d267f3945202bc0b20e3aad940d18c659a5f52cdf18ac5be7b611a0ca`
  and wheel `slaif_local_coding-0.1.0-py3-none-any.whl` 142,753 B
  sha256 `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (evidence `archive-final-b4fb5ef-v1-evidence.json`, 0600). One
  initial attempt that created its venv inside the archive tree
  before `uv build` (sdist picked up 17 venv files) is quarantined as
  `archive-final-b4fb5ef-v1-contaminated-venv-in-tree` and is NOT the
  archive proof.
- Frozen 21 strategic probes at the literal implementation head, repo
  Python 3.12 venv (the ambient python3 lacks `prometheus_client` —
  R interpreter diagnostic preserved): 21/21 pass (rc 0, all checks
  passed), all result heads `d51f496`, hash baseline unchanged
  (local `probes-final-d51f496.json`, 0600). Independently
  re-executed by strategic root with pre/post-run hash verification:
  21/21 with valid positives
  (`reviews/017-s-independent-frozen21-d51f4967bd87-validated.json`).
  Disclosure: the root's original JSON for the SAME retained
  execution recorded an overall false because the wrapper demanded a
  `passed` key on the resource probe's measured-only
  `preflight_peak_bytes` diagnostic (measured 1,054,410 B < 4 MiB
  bound); the corrected interpretation validates every assertion plus
  that sole typed bounded measurement using the same retained
  outputs — no rerun, no frozen probe/source/assertion edits
  (original preserved:
  `reviews/017-s-independent-frozen21-d51f4967bd87.json`).
- Installed-wheel observer controls in a fresh Python 3.12 venv
  outside the checkout (non-editable install of the
  implementation-head wheel, site-packages only, no repo on
  sys.path): 27/27 functional case checks pass (14 inventory-
  totality + 5 inventory-allocation + 8 private-ID-representation)
  with identity assertions (wheel `1f2ebaff...`, byte-identical to
  P/R — src/ unchanged); all 30 installed package modules byte-match
  the wheel. Operational note: the first driver invocation failed at
  import because the venv was initially populated with `--no-deps`;
  the venv was reinstalled with declared dependencies and the driver
  then passed 27/27 (harness operation only; no production or probe
  change).
- GitHub CI at `d51f496`: all 10 check annotations SUCCESS (run
  40241763371: test, operator-session, gateway-contract,
  cache-native-containment, cache-native-fixture, docker-published,
  docker + CodeQL/Analyze actions + Analyze python); test job 2969
  passed / 28 skipped (367.06 s) — identical to the local gate. The
  `cache-native-fixture` job is unchanged from R (Python-only,
  hosted-only entry guard, binary never executed); its closed
  success record at `2ce9dcd` remains the measured R record and is
  cited by the unchanged job.
- PR #25 metadata (pre-SELF): title and body updated to the current
  017-s state via REST PATCH (the `gh pr edit` mutation trips the
  classic-Projects deprecation error; REST PATCH is the equivalent
  edit) and remotely verified: body content byte-identical to the
  intended 353-line body (GitHub appends one trailing newline, the
  same normalization recorded in the R report); no blanket D01-D10
  claim; S scope = local fixture preparation/supervision + ONE
  Python-only rehearsal PASS; native/D09 NOT RUN; qualification
  PENDING strategic review.
- Mirror identity: `ARCHITECTURE-for-agents.md` byte-identical
  across repo root, `oap/strategic-instructions/` and the
  strategic-local mirror after the post-run docs pass (`cmp` on all
  pairs).

## Preserved failed CI runs (closed reasons only; no raw payloads
retained)

- 40238138746 at `305219b` (B1): `test` FAILED — 44 mypy
  no-untyped-def/type-arg errors confined to the then-untracked
  local test file (the file landed untyped in A1/A2 and only became
  tracked with the manifest commit, where the mypy gate first saw
  it). Repair: strict typing completed in `eee8cee` (A3); mypy clean
  at `fc7647e` and after. Other nine checks SUCCESS at that head.
- 40238951936 at `fc7647e` (B2): `test` FAILED — 28 failed / 2940
  passed / 28 skipped. 27 fake local-owner/opt-in tests inherited
  `GITHUB_ACTIONS=true` from the hosted runner and hit the CORRECT
  production local-hosted-env guard (the guard was never weakened):
  test premises made hermetic (setup deletes the ambient hosted vars)
  plus an explicit hosted-refusal negative proving the guard still
  fires. 1 expired-anchor test used a real-time computation
  (`max(1, now-2000)`) that a fresh runner's uptime could leave
  unexpired: replaced with a deterministic fake clock proving
  already-expired before IO, preserving the reason/run-id
  assertions. Repaired in `54ef177` (A4); local suite 49 tests; all
  10 checks SUCCESS from `2a9c44e` onward.

## Deviations and disclosures

- S CI test failures preserved and repaired as above (B1 44 mypy
  errors; B2 28 premise failures); the production local-hosted-env
  guard was never weakened and no test was skipped or the hosted
  context spoofed.
- Slug double-prefix reconciliation (in-flight registration-seam
  review): the producer (`_new_container`) already prepended the
  `017s-` prefix while the guarded prepared-slug guard added it
  again, so the actual target was rejected (7/8 in the selected
  audit); the closed producer/guard pair was reconciled to a single
  prefix while keeping the existing-name positive, arbitrary-name
  refusal and R grammar intact.
- Root-side private-probe adaptations (attribution): strategic root
  adapted only UNFROZEN private probe fixtures/harnesses during the
  in-flight rechecks (no production changes, no frozen-21 changes);
  selected-fake results are recorded in
  `reviews/017-s-*-py312.json` and `reviews/017-s-*.md` evidence.
  Production validation was never loosened to satisfy probe
  fixtures.
- My archive-gate attempt that created the fresh venv inside the
  clean archive tree before `uv build` (sdist contamination, 17
  venv files, hash mismatch) is disclosed above and quarantined; the
  valid archive proof is the no-venv-in-tree reproduction.
- Wheel-driver first invocation failed on `--no-deps` import and was
  rerun with declared dependencies (operational note above); the
  frozen21 first nohup launch completed successfully
  (`probes-final-d51f496.json`), and a duplicate session launch of
  the same gate was closed as redundant.
- Carried P-round deviations (premature full-suite run against
  known-stale provenance; overbroad `pkill -INT -f "pytest -q"` and
  its unknown collateral impact) are recorded in the immutable P
  report `017-p-observation-native-fixture-prerequisites.md` and are
  not recast here.
- Carried R-round deviations: the prohibited `git add -A` before
  commit `529a38d` (independently verified to contain exactly the
  four intended paths; exact-path staging used for every commit
  since, including all S commits), and the stale-filename gate label
  B6 whose actual head was `2ce9dcd` — both recorded in the
  immutable R report and not recast here.
- The R report's supplemental paragraph cited earlier WIP hashes
  while describing final-source passes; those hashes are historical.
  Strategy's actual POST-R final-source supplemental evidence
  (15 probes, all PASS at `2ce9dcd`) is
  `reviews/017-r-independent-supplemental-final-2ce9dcd90412.json`.
  The R report bytes are immutable and uncorrected here.
- Bounded 017-r fixture preparation: ACCEPTED at head `2ce9dcd`
  (strategic decision, with the recorded wording limitations in
  `reviews/017-r-decision.md`); the serial foreground handoff itself
  remains a later separately authorized order.
- umask discipline (carried from P/R): host umask is 0002; `umask
  022` was scoped in the same shell invocation as every required
  pytest run this round. No global/home/fixture/validator permission
  changes; owned evidence/driver files 0600, owned roots 0700,
  source archive and venv permissions unchanged.
- No secrets are forwarded to the fixture; the env file carried
  exactly the two synthetic keys and was removed on every path.

## NOT RUN / remaining (distinct from passes)

- Native Codex launch of any kind (including help/version): NOT RUN
  in S; `codex_invoked: false`, attach plan inert
  (`executed: false`).
- Worker stop/suspension: NOT RUN; `worker_stopped: false`; no host
  PID signalling of any process.
- Actual serial foreground handoff execution: NOT RUN — preparation
  and runbook only; a later active order must authorize and record
  it.
- D09 genuine native formats / native process+chunk collector:
  NOT RUN.
- Local S rehearsal attempts: exactly ONE consumed (PASS); no second
  attempt in S; additional attempts require a later order.
- Public archive signature verification: NOT RUN (archive SHA256
  only).
- Required-syntax scope audits for ls+cat and unguarded/labeled loop
  literals (and remaining matrix gaps): PENDING.
- Handoff-preparation qualification: PENDING strategic review of the
  actual outcomes (measured facts in this report). 017-p capability
  qualification: PENDING strategic review. Bounded 017-r: accepted
  (wording limitations recorded).
- Objectives 018-024 v1 runtime work: NOT RUN. No v1 runtime is
  active or qualified. Whole 017 remains incomplete: the D01-D10
  criteria, D09, the scope audits and the native handoff are not all
  earned. No real Codex E2E, model/GPU/gateway call, benchmark,
  RC/tag/registry/release/deployment/cutover occurred in S; no
  protected service, profile, daemon or host package was changed.

## Closing

No secrets are forwarded to the fixture. This report-only commit
changes only
`oap/reports/017-s-local-fixture-preparation-and-supervision.md`; its
sole parent is the implementation head
`d51f4967bd8737575631b758819533da559c2520`. After publication: no
further mutation of any kind; read-only verification only; then the
single response FIFO OK, then same-instance blocking wait for the
next control.
