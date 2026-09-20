# OAP Work Order — 013-k

## Objective and verified state

Objective013, AMEND_EXISTING_PR15, NO NEW PR. Finish the three small source
corrections below and the consequent artifact refresh. Preserve the existing
implementation and validation. This is not another general cleanup or hardening
round. Human explicitly wants the release candidate finished without benchmark
implementation or expansion into a large undertaking.

Repository ulfe-lmi/slaif-local-coding; PR
https://github.com/ulfe-lmi/slaif-local-coding/pull/15; branch
oap/013-mvp-release-publication; main a04693e6792df6a8ad4262acfb46336a0f662202.
Starting remote head25720c06dcd55e9433793a7e6068f36d1e5bcb40 is the verified
report-only SELF child of e1ef4970a658e33418b9688b25aeed55f18e6dd9.
Active013-j and its unique order/report are verified locally and remotely;
there is no remote013-k execution to replay. CI35523079595 and report-head
CI35523986067 are green, including the genuine19-phase operator session.
docker-published is explicitly NOT RUN before publication, not RC evidence.
Latest publication remains historical run35263999980; no RC has been published.

Read-only protected-host recheck: user qwen-serving-vision.service active PID23961
since2026-09-06 18:57:26CEST; only18020 listening among18020/21/31/33/34.
qwen-neumann config hash3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb
unchanged. Actual coding profile/provider remains qwen-neumann, qwen-LSI-A100,
Responses http://maelstrom1.lmi.link:8001/v1, qwen3.8-27b. This active executor
path is protected and is not a benchmark fixture. Frozen Gateway authority
08ca421bee1ddca62078302b910e8be88cf705be remains unchanged.

## K1. Make the actual publication build invocation work

release-image.yml exports SLAIF_GIT_SHA and SLAIF_WHEEL_SHA256 but omits
SLAIF_LOCAL_CODING_IMAGE before invoking two-file Compose build. compose.yaml
requires that variable. Compose interpolates each file before merging, so the
override's image value does not avoid the error. Existing Docker CI helpers set
the variable; their success does not qualify the release workflow invocation.

Supply the required nonsecret build selection in the release workflow and keep
the development usage comment consistent. Prove the actual workflow build command
and environment succeed from a fresh disposable CI checkout, including any
nonsecret temporary Compose inputs it actually needs. Reuse an existing Docker
job/helper for this focused check; do not create another framework or whole new
operator suite. The built image must retain source/wheel/RC labels and the same
pinned Docker design. No registry login/write/dispatch in this corrective round.
Do not weaken the canonical pull-only Compose or its explicit-image requirement.

## K2. Remove the remaining transient README paragraph

README still says cutover has NOT been performed, describes historical private
0.1.0 tags/OAP disposition, and says it carries no release-state claims. Remove
that history/current-deployment paragraph, retaining a short durable repository
boundary. Specialist history is already preserved elsewhere. Make registry-auth
wording conditional on image visibility instead of assuming images always stay
private. Correct the vision capability from exactly one to at most one image;
zero-image requests are supported. Retain installation links, limitations, credits,
and the rest of the reviewed landing page. No general docs rewrite.

The existing small docs gate should catch recurrence of this exact transient
README wording; one focused negative fixture is enough. No prose-style expansion.
README changes wheel METADATA: rebuild after the final text, never retain the
previous wheel hash3c4c36e666fb67f6a8ed0bbf1a60962e187e46ba1183f314eba03100ce2006af.

## K3. Enforce the promised explicit registry state precondition

plan_pre_write currently returns proceed for unknown statuses because it handles
known unauthorized/digest states and then falls through. Require explicit verified
ABSENT for both target states before proceeding. Keep the existing occupied/error/
partial-publication behavior and no-overwrite policy.

The mocked registry boundary currently converts every non-absent/non-unauthorized
state into DIGEST. Pass unknown statuses through unchanged and add a real unknown
status case for each target that executes main and asserts ZERO Docker mutations.
This is a small guard/test correction, not a new publisher design. The013-j report
names test_unknown_status_zero_mutations, which does not exist in its source;
correct that claim prospectively in this round's concise report. Prior report is
immutable. Do not reproduce report claims from memory instead of actual test names.

## Verification and bounded completion

Preserve J3–J6 tooling and all existing gate semantics. Commit final sourceA first;
perform two clean isolated builds and require equal wheel+sdist bytes. Regenerate
the excluded provenance manifest as metadataB, with exact observed tools and
source-input equality. Retain the six existing exact build pins, uv0.12.5,
Python3.12 scope and immutable base identities. No runtime dependency/uv.lock churn.
Run the normal frozen lint/type/test/artifact/fresh-install/syntax/Gateway gates
and fresh Docker/operator CI, plus the focused cases above. Avoid redundant broad
reruns once unchanged checks pass. The published-image gate stays explicit NOT RUN
until an actual RC exists; no invented RC record or digest.

After fresh green implementation CI, publish a concise evidence report covering
K1–K3, exact sourceA/metadataB, wheel/sdist/tool hashes, source-input equality, CI
URLs and exact skip accounting. Correct earlier claims only prospectively.
Do not add speculative fixes, new abstractions or unrelated cleanup. If a new
material defect remains beyond this scope, report it precisely for strategy.

## Safety and publication contract

All013-i/013-j human constraints remain binding. No benchmark implementation,
design, tasks/judges/controller/ledger, A100 setup, pilot/experiment, statistics,
telemetry/instrumentation, or experiments/codex_adapter_benchmark. No src runtime
change or product behavior change for benchmarking. No final public release,
v0.1.0 Git tag, GitHub Release, package visibility change, registry writes or
publication dispatch in this round. Strategy will review the exact corrected
source and issue the already-human-authorized private RC publication continuation.

Protected host remains read-only except safe repository-local tooling/fake tests.
No host Docker execution, Qwen inference, port18020 or qwen-serving changes,
models/checkpoints/patches/venv/systemd/launch flags, API-key changes, Gateway
routing, firewall/VPN/network binding, or active Codex profile changes. Candidate
fake tests may use free loopback18031 and must clean up. Recheck protected baseline
before/after. Never print secrets/raw customer content; CI uses synthetic secrets.
Routine setup/implementation stays with coding. Preserve Local/clean/unchanged.

Commit exact activated order and active013-k on PR15 only; no new PR, merge,
auto-merge, force-push, or prior OAP edits. Push all non-report work, then publish
exactly oap/reports/013-k-final-rc-source-corrections.md as report-only SELF child
of the literal immediate pre-report Implementation head SHA. Verify remote
head/parent/path/bytes, send exact response FIFO OK, and make no further mutations.
Image source is still NONE this round; do not conflate it with report parent.
