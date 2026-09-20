# OAP Work Order — 013-j

## Objective and GitHub state

Objective 013 continuation, AMEND_EXISTING_PR #15, NO NEW PR. Close the exact
source-review gaps below before RC publication. Preserve the substantial 013-i
implementation. This is still RC stabilization, not benchmark implementation or
final release. No registry publication/dispatch in this corrective round; strategy
will bind the reviewed exact source for publication in the following continuation.

Repository ulfe-lmi/slaif-local-coding; PR
https://github.com/ulfe-lmi/slaif-local-coding/pull/15; branch
`oap/013-mvp-release-publication`; base main
`a04693e6792df6a8ad4262acfb46336a0f662202`.
Starting remote report head: `fac713577c69c9dff8355f4d8b9070238b514cd5`.
Reviewed implementation: `317cc27232e582e83f4664ed3eceb0dd68c4e2aa`.
Fresh implementation CI run 35510283615: test, gateway-contract, docker green;
docker-published explicitly NOT RUN before publication. Green CI does not establish
source/input truth, a usable operator recipe, or zero-write collision behavior.

Strategy has independently verified the 013-i SELF report commit changes only
its unique report and its first parent is literal implementation SHA 317cc272...;
remote report/order bytes match local. Report-head CI 35510949240 is also green.
Read-only host recheck: qwen-serving-vision.service active PID23961, ordinary
qwen-serving.service inactive; 18020 remains the sole listener among
18020/18021/18031/18033/18034. Protected qwen-neumann profile hash matches the
013-i baseline; runtime src/, config/, and uv.lock are unchanged. Current coding
profile/provider remains the 013-i protected qwen-neumann Responses path.

All human constraints and protected-host rules of 013-i remain binding. The old
pre-staged 013-i build-pin/final-publication draft has no authority. All historical
activated orders/reports remain immutable. Retain Gateway authority
`08ca421bee1ddca62078302b910e8be88cf705be`; no runtime/Gateway behavior change.

## Findings and exact remediation

### J1. Reject occupied or unresolved tags BEFORE registry writes

The reviewed publisher calls `_push_digest(sha_ref)` before comparing `sha_pre`
against the resulting digest. That can overwrite an occupied source tag before
reporting a collision. Its report/commit assertion of no overwrite is therefore
not supported by the code. Fix the ordering and prove actual side effects.

Use the simple safe policy for this RC: if EITHER source-SHA or candidate tag is
occupied, unauthorized/inaccessible, malformed, or unresolved, STOP BEFORE ANY
registry mutation. Report existing digests for strategy; do not repush/rebuild an
already frozen identity. Authenticated verified-absent for BOTH is the only write
precondition. Do not silently allocate a new RC number. No final-looking tag is
permitted by this RC publisher; validate the explicit expected RC1 identity,
source SHA, and repository before any Docker mutation. Preserve legacy 0.1.0 and
orphan identities. Serialize publication runs with workflow concurrency (do not
cancel an in-progress publisher). Recheck target state immediately before writes.

Add meaningful negative tests executing the publisher control flow with mocked
registry/Docker boundaries and asserting ZERO tag/push mutations on occupied source,
occupied RC, inaccessible, unknown status, invalid digest, and forbidden tag cases.
Test the successful verified-absent path and partial-publication recovery behavior.
The existing test of set membership and digest parsing does not prove this gate.
A sha-S tag is a mutable source alias, not content-addressed OCI identity: fix that
terminology in current docs/comments. Digest remains authoritative.

### J2. Finish durable documentation and executable operator paths

README still says 'being prepared and frozen', includes a Release status section
and Objective-013 tag history. Remove that transient/history material from the
landing page; move necessary historical disposition to specialist history. Keep
README concise, product-focused, and stable through later promotion. No need to
change README when a human later approves the same digest.

Fix surviving current contradictions in ARCHITECTURE.md (the lead and current
state still say publication PENDING on R18/this PR) and RELEASE-CUTOVER-RUNBOOK.md
(the publication attribution still says 013-b). Review the relevant architecture,
configuration, security and deployment surfaces, not just the original checker
allowlist. Preserve immutable OAP records; historical prose must be unmistakably
historical and not a current release claim.

Make QUICKSTART/INSTALL commands a coherent operator session:
- Set/export the same image, config, and env-file paths for EVERY Compose command,
  including ps/logs/stop/start/restart/down/upgrade/rollback. Current command-local
  assignments on pull/up leave later commands resolving missing/wrong defaults.
- Obtain all files actually used. The minimal Compose+config retrieval path cannot
  subsequently require a missing packaging/readyz-wait.sh. Either use Docker/Compose
  health waiting directly or include the shell helper and curl prerequisite.
- State and implement coherent admin/root/file-ownership prerequisites for /opt
  creation and UID10001 config readability. Secret values stay out of argv/logs/
  checkout. Blank/unset required secret inputs must fail clearly.
- External GHCR reader scope is `read:packages` (PAT classic with package read
  access), distinct from Actions YAML `packages: read`; use password-stdin and
  bounded read-only access. No request to make the package public.
- Verify actual OCI digest/RepoDigests or registry manifest digest; inspecting .Id
  alone is not proof of the manifest digest. Include source/label/config identity
  verification with commands a separate consumer can follow.
- Advanced systemd instructions must use the supported signed Gateway-integrated
  template, correct checkout/ExecStart path, user-unit directory and cache-path
  preconditions. If using the complete existing runbook, link to its exact recipe
  instead of supplying a broken abbreviated one. Unsigned development mode is
  clearly separate. Do not instruct users to stop arbitrary port owners.
- Document the actual supported image OS/architecture, not just generic Linux.

Extend the small docs gate/negative fixtures to cover these concrete regressions
and relevant current architecture sections. Do not hide false claims outside the
scope list or create a giant style linter. Do not ban truthful prose stating that
Docker users do not need Python/uv; reject required build-tool commands instead.
Prove the documented primary lifecycle in disposable CI using synthetic secrets
and fake upstream. This is ordinary install qualification, not a benchmark; no
protected-host Docker run. Validate the exact paths/permissions/commands supplied
by the docs, including fresh shell/project retrieval assumptions.

### J3. Enforce the build environment that provenance claims

The generator currently emits hardcoded build dependency versions (packaging,
pathspec, pluggy, tomlkit, trove-classifiers) although only hatchling itself is
pinned. Record facts only when actually observed or mechanically enforced.
Pin the complete relevant build environment sufficiently, using the existing
build tooling/constraints rather than changing runtime dependencies. Bind recorded
tool versions to the enforced and observed resolution; fail on drift. Retain
hatchling==1.32.0 unless the actual evidence disproves it. Record exact Python
interpreter/base identities used; if wheel bytes are intentionally patch-independent,
state/prove that scope instead of presenting '3.12' as an exact runtime version.
No uv.lock/runtime dependency churn solely for this infrastructure correction.

After ALL documentation/build fixes, repeat two isolated clean builds of the same
final source input tree and require identical wheel AND sdist hashes. Preserve
artifact content policy, fresh-install smoke, and in-image wheel binding. README
changes intentionally require another new wheel hash; never reuse stale hashes.

### J4. Bind provenance to actual source inputs

The current manifest names generated_from.git_commit = 64068209..., whose README
and build files differ from those producing the new artifacts. An ancestor test
plus stripping that field during regeneration does not prove source identity.

Use a truthful sequence: commit all source inputs as A; build CLEAN A; generate the
manifest; commit only derived excluded metadata as B. Mechanically prove the
relevant source/artifact inputs are identical at A and B. The later image source S
will be the exact reviewed workflow checkout, with all inputs identical to that
qualified source. Never stage changed source under an old HEAD and present that
old commit as the built tree. No report may conflate source S, manifest generation
anchor, implementation/report-parent SHA, and post-publication record commit.

Add an explicit mechanically verified input map/equality rule covering all relevant
wheel/sdist/OCI/configuration inputs, including README, pyproject, uv.lock, src/,
Dockerfile, Compose/build override, .dockerignore, config/templates and the relevant
packaging inputs. Define exclusions for generated manifests/RC records/handoff and
OAP to avoid self-reference. Post-publication metadata cannot change those inputs.
Reject a valid-shaped but wrong old source, wrong dependency-lock hash, missing or
altered config/Compose hashes, and source/input drift even if it is an ancestor.
Tests must exercise these checks before a real RC record exists; conditional
returns in pre-publication tests are not negative evidence.

### J5. Complete one self-contained RC handoff record

The current RC record omits config/template hashes and its prose claims they are
'cross-bound' by unrelated wheel/lock/peer facts. The wheel does not contain those
config templates. Add the relevant exact path->hash map directly to the strict
record and validate it against S and qualified inputs. Include Compose identity,
actual build-tool/dependency pins and base identities, supported image platform,
product/RC IDs, source, digest/reference, wheel, lock, frozen Gateway authority,
private-auth requirement, final_public_release=false and cutover=false.

Prepare deterministic rendering of the human-readable handoff from those SAME
machine facts. During actual publication it must contain literal verified values
and retrieval/verification commands, without OAP knowledge or image rebuild. Exclude
post-publication generated handoff files from artifact inputs so recording a digest
does not require another image. No experimental procedure or benchmark code.

The generator's syntax validation cannot itself authenticate an arbitrary digest.
Correct that claim; document the trust boundary and bind real publication to the
workflow run's exact head SHA, authenticated registry digest, and pulled-image
qualification. Keep machine validation strict; future publication requires a real
run ID and verified facts, not a fake/unpublished record.

### J6. Correct prospective historical explanation without rewriting records

The 013-i report/docs call the 013-g/h image-source/report-parent relationship a
coincidence of equal facts. For 013-h that is false: its named implementation SHA
was fe334e87..., while its actual SELF parent was 881f1f36.... Correct the mutable
explanation in oap/README.md/report-template if it repeats that claim, and record
an explicit correction in this new report. Historical orders/reports stay unchanged.
Also report historical build hashes literally and accurately; the 013-i report's
historical sdist string differs from the original recorded full hash. Distinguish
transcription correction from a new measured build fact; use verifiable evidence.

## Evidence, scope, and publication contract

Run all normal frozen local gates and fresh CI: ruff/format, mypy, complete pytest
with skip accounting, two clean builds, artifact policy/fresh install, syntax,
strict frozen Gateway contract, full disposable Docker qualification. Preserve
existing assertion semantics. Include concise J1–J6 evidence and test names,
source/metadata commit chain, literal hashes, measured build versions, and CI URLs.
Record what changed in prior claims (collision safety and provenance especially).
Source report can be concise; link evidence rather than repeating the full order.

No registry write, dispatch, final tag/Release/visibility/promotion, benchmark
implementation/design/telemetry/experiment/A100 setup, protected-host Docker run,
Qwen inference/service mutation, Gateway routing, network/firewall/VPN/profile/
key changes, or src runtime change. In particular do not mutate port 18020,
qwen-serving checkout, model/checkpoint/patches/venv/systemd/launch flags, API keys,
firewall/VPN/network bindings, or active Codex profiles. Candidate fake services only per 013-i.
Recheck protected-host service/profile/listener baseline before/after. All other
013-i safety constraints apply. Routine implementation/setup stays with coding.

Push all implementation and exact activated order/active on PR #15 only. No merge,
auto-merge or force push. Preserve earlier orders/reports exactly. Publish the
unique report oap/reports/013-j-close-rc-source-review-gaps.md in a report-only
SELF child of the literal immediate pre-report Implementation head SHA; source
image is a separate field and no image is published this round. Verify the remote
head/parent/path/bytes, send exact response FIFO OK, and make no subsequent changes.
Strategy reviews, then independently authorizes the exact-source freeze continuation
under the human's already granted private-RC publication authority.
