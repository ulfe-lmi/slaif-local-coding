# OAP Work Order — 007-a

## Objective and authoritative topology

Objective007 is a NEW post-006 hardening/operability objective: make the current
Local↔Gateway source contract continuously and reproducibly tested in ordinary
GitHub Actions without any shared development filesystem. CREATE_NEW_PR from
current remote main; create exactly one branch
`oap/007-current-gateway-contract-ci` and exactly one PR. Coding never merges.

Strategy independently verified through GitHub before activation:

- Local repository `ulfe-lmi/slaif-local-coding`, remote main
  `efc4dbcd377dd796a670726b16ebc06bd54b6356`; merged-main CI run34723561535
  SUCCESS; no open PR; no007 order/report/branch/PR. Active history remains006-a.
- Gateway repository `ulfe-lmi/slaif-api-gateway`, remote main
  `65666f5886832034c52211fdd7604046557e6ada`, merge ofPR301; tree
  `06946cf96dcb24c56a4560f8299271cb9c4d60fb`; all nine queried final checks
  SUCCESS. Authority came from GitHub repo+commit only, never a host checkout.
- Current Gateway facts at that exact GitHub commit: Local server module ID
  `local-coding-v1`, module version`2`, replay mode
  `process_local_inclusive_horizon_fail_closed`, signed-mode skew/TTL required;
  Codex client module ID `codex-0.149-responses-v1`, version`4`.

Topology law: Local and Gateway live on different development machines. Coding
MUST NOT use or inspect any pre-existing/sibling/NFS/home/workspace or `/tmp`
Gateway checkout. Any local reproduction creates a fresh disposable checkout
from GitHub at the exact fixture repository/SHA and proves its origin/HEAD. CI
owns separate runner-local `local/` and `gateway/` checkouts. Do not assume Qwen,
Gateway service, Local service, Codex runtime, database or protected machine.

The human selected normal Sol/Luna OAP and Luna-xhigh with1M context. Strategy
created a new non-destructive profile-v2 layer
`oap-coding-luna-xhigh-1m` (gpt-5.6-luna/openai/xhigh/context1000000), changed
only strategic runtime selection, and visibly restarted the idle coding wrapper
in tmux pane `%0`. Do not change models/accounts/profiles during the round.
Preserve the installed but unused qwen-neumann files and every pre-existing
Codex-home file. Preserve the three empty untracked Local/clean/unchanged files.

Keep this one007-a round active through ordinary implementation, workflow/test
iterations, CI corrections, review preparation and report. A dependency/import/
workflow/test failure is work to solve, not grounds for an intermediate BLOCKED
report, human question or suffix. Publish only complete green closure unless a
genuine external authority/safety boundary remains after safe alternatives.

## A. One current peer-authority source of truth

Add one small content-free machine-readable fixture at the canonical Local test
boundary, preferably
`tests/fixtures/gateway/current_peer_authority.json`, containing exactly:

- schema/version;
- repository `ulfe-lmi/slaif-api-gateway`;
- commit `65666f5886832034c52211fdd7604046557e6ada`;
- Local server module ID/version/replay mode (`local-coding-v1`, `2`,
  `process_local_inclusive_horizon_fail_closed`);
- client module ID/version (`codex-0.149-responses-v1`, `4`);
- purpose `current_ci_compatibility_authority` (or an equally finite literal).

This fixture is the sole current Gateway pin consumed by workflow, preflight and
tests. Validate exact keys, types, repository grammar and40-lower-hex SHA; unknown/
missing fields fail closed. Do not repeat the SHA in YAML/scripts/docs except
immutable historical explanation or OAP transcript. Future peer advances update
this fixture in a normal reviewed Local PR; arbitrary Gateway main movement never
redefines compatibility.

Current acceptance-harness constants `GATEWAY_MAIN_SHA=5ea38325...`, app tree and
Objective005 evidence are historical. Do NOT edit/repoint them, the old reports,
or evidence. Add a regression that proves the historical pin remains separate
from the current peer fixture. The existing file
`tests/test_gateway162_validator_factory.py` is historically named but its nine
source-contract tests are still useful against current client module v4; clarify
that distinction without rewriting historical evidence.

## B. Strict current-peer verifier and tests

Implement the smallest repository-only test helper/runner needed; no general
artifact/framework redesign. It must:

1. load the one fixture strictly;
2. require an explicit Gateway root in cross-repo CI;
3. require a real checkout whose exact `git rev-parse HEAD` equals the fixture
   SHA and whose normalized origin identifies the fixture repository, without
   printing embedded credentials;
4. require the expected `app/slaif_gateway` source paths;
5. add only that checkout's `app/` to import resolution;
6. execute the intended focused test files/selectors;
7. fail when zero tests execute, any test skips, or any failure/error occurs;
8. emit only safe repository/module/SHA/test-count facts.

Normal developer `uv run --frozen pytest -q` without a Gateway checkout remains
usable and retains the established skips. A separate strict environment flag or
runner may turn missing/wrong Gateway into failure only for the cross-repo job.
Do not globally require Gateway for unrelated Local tests.

Run the nine current equivalents in `tests/test_gateway162_validator_factory.py`
against the exact current checkout (zero-argument omission and canonical argument
lifecycle, exact validator/profile construction, malformed/ineligible requests,
terminal discriminator and identity/order/terminal negatives). Add a clearly
current-named focused test module that imports exact Gateway source and proves:

- server module ID/version2/replay-mode metadata and strict contract parsing;
- signed-mode required skew/TTL and malformed/stale metadata rejection;
- client module ID/version4 and request-derived zero-argument fact;
- Responses stream validator/profile lifecycle remains compatible;
- legal ID-less call/output continuation contract remains aligned with Local's
  current constructor/shape, including mandatory call-ID and optional item ID;
- an intentionally incompatible/mock module version, replay mode, policy fact or
  lifecycle causes a focused failure rather than being normalized away.

Use relevant existing Local helpers/tests rather than copying Gateway logic. The
cross job may also run narrowly selected current Local ID-less tests from
`tests/test_gateway_accounting_rehearsal.py` if they materially prove the boundary,
but it must not start the Objective005 full harness, Codex, fake service matrix or
provider. List exact files/selectors and executed/pass/skip counts in evidence.

Add self-tests for: exact checkout accepted; missing root fails strict mode;
wrong repository/root/SHA fails; malformed/unknown fixture fails; mocked
incompatible contract fact fails; strict result gate rejects skip/zero collection;
normal no-root developer behavior still skips only the Gateway-dependent module;
historical005 constants unchanged.

During the actual compatibility test phase, install/setup first and then prohibit
network/model/provider calls. Prefer a small Python socket-denial guard around the
pytest invocation and test that the guard trips, or an equally deterministic
runner-owned mechanism. Checkout/package acquisition are the only allowed network
operations. No HTTP service, subprocess that starts a server, database, Redis,
Codex or inference. Fail on attempted network rather than merely claiming absence.

## C. Dedicated GitHub Actions job

Add a dedicated `gateway-contract` job, in the existing CI workflow or a narrowly
named separate workflow, triggered on ordinary `pull_request` and pushes to
`main`. Never use `pull_request_target`. Set top-level/job permissions to
`contents: read`; request no secrets/elevated permissions. Use public checkout
credentials only, `persist-credentials: false`, and do not print tokens/remotes
with embedded credentials.

Conceptual steps:

1. checkout Local PR/main commit into runner-owned `local/`;
2. strictly read repository+SHA from the current-peer fixture and expose only
   those finite outputs;
3. use a second `actions/checkout` to fetch that exact Gateway repository/ref
   into runner-owned `gateway/`, never floating main;
4. independently compare actual Gateway HEAD/origin with fixture;
5. install Local and only the minimal reproducible Python dependencies needed for
   pure Gateway imports/tests;
6. run the strict, network-disabled focused contract runner with
   `SLAIF_GATEWAY_ROOT=<runner-owned gateway checkout>`;
7. explicitly assert nonzero expected execution and zero skips.

Derive dependency needs from imports at exact Gateway SHA. Local already has
FastAPI/httpx/Pydantic. If additional packages are truly needed, represent them
in a dedicated Local test-only locked extra/group or another reproducible pinned
mechanism; do not float-install ad hoc packages and do not install/start the full
Gateway stack, PostgreSQL, Redis, browser or containers for pure contract tests.
Do not package Gateway source into Local.

Threat model fork PRs: PR code already executes in an unprivileged ephemeral
runner, receives no secrets, and has read-only repository permission. The peer
fixture may propose a new public exact repo/SHA but does not gain credentials or
write authority; normal review decides whether that pin may merge. Checkout must
fail if unavailable. Do not use self-hosted runner/private host paths.

## D. Documentation and update workflow

Update current Local testing/integration/runbook documentation concisely:

1. Gateway merges a relevant contract and publishes exact authority.
2. Local updates the single peer fixture in a reviewed PR.
3. Local `gateway-contract` CI checks out and proves that exact pair.
4. Local merge establishes the new continuously supported pair.

Distinguish current continuously-supported peer authority from immutable
Objective005 acceptance pins. State how developers may optionally run the focused
tests using their own freshly obtained exact checkout, while normal no-root unit
development keeps the documented skip. No shared-machine instructions, `/tmp`
historical paths, Qwen or service setup. Document job failure/skip semantics and
minimal dependency source.

## E. Verification, scope and security

CPU-only. No Qwen/vLLM/GPU/protected credentials/model inference, no real Codex,
no Local/Gateway installed service, PostgreSQL, Redis, container, systemd,
firewall/VPN/network/profile mutation. Do not access a developer-machine Gateway
path. Local reproduction must clone/fetch from GitHub into a new owned disposable
directory at the fixture SHA and remove only that owned checkout after tests.

Run and record:

- focused fixture/verifier/strict-result/network-guard self-tests;
- strict current cross-repo command using a fresh GitHub checkout at fixture SHA,
  with exact test/pass/skip counts and zero skips;
- negative wrong-root/wrong-SHA and incompatible-fact cases;
- ordinary `uv run --frozen pytest -q` with no Gateway root, proving expected
  developer skips remain and no new global failure;
- `uv run --frozen ruff check .`;
- `uv run --frozen ruff format --check .`;
- `uv run --frozen mypy src tests` plus new scripts if not already included;
- `uv build`, compileall and shell syntax;
- wheel entry/byte inspection: exact Local runtime source and license/notice only,
  no Gateway source, peer checkout, test fixture, workflow or runner;
- workflow syntax/semantic inspection and relevant local action-equivalent steps;
- privacy scan for repository tokens/private URLs/credentials in logs/artifacts;
- GitHub checks `test` AND `gateway-contract` on final implementation head.

The existing ordinary test job must remain green without a Gateway checkout.
The new job must fail closed when checkout/SHA/import/tests/skips are wrong. No
test may call a model/provider/network after setup; include direct guard evidence.
Inspect/fix all workflow/CI failures in this same007-a branch before report.

Review production/package diff separately: expected production `src/` behavior
change is NONE. If source inspection suggests otherwise, resolve ownership within
the objective before mutation. No Gateway code modification. No immutable005/006
artifact edit. Strongest reason not to merge must be resolved, not listed.

## F. GitHub, report and strategic closure

Create one PR from exact Local main with the exact branch above. Push the current
fixture, test helper/runner, tests, workflow, docs and unchanged activated
order/active. No second PR/suffix. Iterate until both implementation-head GitHub
jobs and all local gates are green. Coding never merges.

Only after full closure publish exactly
`oap/reports/007-a-current-gateway-contract-ci.md` with literal implementation
head and `Report publication commit: SELF`; final SELF child changes only that
report and has the implementation head as first parent. Report exact Local and
Gateway GitHub SHAs, fixture bytes/hash, dependency method, strict executed/pass/
skip counts, negative cases, ordinary no-root behavior, workflow job/run IDs,
package/privacy/network proof, no-Qwen/no-service facts and limitations. Clearly
distinguish current peer CI authority from historical acceptance and
IMPLEMENTED/TESTED/MERGED/DEPLOYED/RELEASE-READY states.

Verify remote report bytes/path/parent/head and send exact response FIFO `OK`.
Strategy independently reviews every changed workflow/test/helper/fixture/doc,
GitHub Actions logs proving exact Gateway checkout and non-skipped execution,
report SELF, package/security and final report-head `test` + `gateway-contract`
checks. When satisfactory, strategy merges under standing authority, verifies
remote Local main, and waits for BOTH ordinary and cross-repo merged-main jobs.
No human confirmation, Qwen, deployment or release.
