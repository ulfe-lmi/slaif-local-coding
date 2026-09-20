# OAP Work Order — 013-l

## Objective and verified state

AMEND_EXISTING_PR #15, Objective 013, NO NEW PR. Close the concrete RC publication
integration gaps below using existing tooling. No general cleanup or new framework.
Repository ulfe-lmi/slaif-local-coding; PR
https://github.com/ulfe-lmi/slaif-local-coding/pull/15; branch
oap/013-mvp-release-publication; main a04693e6792df6a8ad4262acfb46336a0f662202.
Starting head db5bf49612de39d40c4d1c459dc323dab9d92c97 is the verified report-only
child of b3f8d9e1ee46be3e3d453c484af6d8267dbac8d6. K1–K3 are accepted.
CI 35526139281 and report-head CI 35526616712 are green; image-pull qualification
is explicitly NOT RUN before an RC exists. Strategy independently hashed all 119
recorded inputs at source 780d561ba2761643282e7fd41c3eba229a8cd6c6 and metadataB:
equal, with only the excluded manifest in A..B. No Git tags or Releases exist.

Protected baseline remains user qwen-serving-vision.service active PID 23961 since
2026-09-06 18:57:26CEST, only 18020 listening among 18020/21/31/33/34; profile
qwen-neumann hash 3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb.
Actual coding path remains qwen-neumann/qwen-LSI-A100 Responses at
http://maelstrom1.lmi.link:8001/v1, model qwen3.8-27b; protected, not a benchmark VM.
Frozen Gateway authority 08ca421bee1ddca62078302b910e8be88cf705be stays unchanged.

## L1. Connect the existing v2 record to the actual pulled-image gate

scripts/docker_qualification_ci.py still accepts only slaif-rc-record-v1, while
the generator emits v2. Its published qualification comparison also hardcodes
mvp-release-0.1.0, which rejects the RC label. These defects are hidden by the
prepublication skip and must be corrected before relying on the real pull gate.
Reuse the existing strict v2 loader rather than another schema implementation.
Preserve malformed-record failure and the RC/final distinction; no final release
is authorized. Select the exact expected RC label from the existing bound facts.
In the existing published-image inspection also verify linux/amd64, the platform
already declared by the record. Keep every existing signed-ingress, fail-closed,
wheel, no-build, hardening, lifecycle and teardown assertion.

Add only focused consumer-integration coverage: a generated v2 temporary fixture
is accepted by the real published-mode loader/constructor, and malformed data is
rejected. Reuse existing fixtures/tests; no full new mocked-Docker framework.
No fake RC record in packaging/. Actual digest qualification remains mandatory
after publication, not claimed from these prepublication tests.

## L2. Finish the existing handoff renderer and two current doc references

render_handoff in scripts/rc_artifact_record.py emits four braces in the plain
RepoDigests format string, making that command invalid. Emit the correct Docker
template and verify the literal rendered command. Also render the already present
build_toolchain and base_images facts in the human view, and link INSTALL.md at
the literal image-source commit for exact-source Compose/config retrieval. Keep
both views derived from the same record; no duplicated installer or benchmark
procedure. Preserve frozen-record/no-overwrite behavior.

docs/DEPLOYMENT.md current table still names RC-v1/provenance-v4: align it to
actual v2/v5. Make the publication introduction in docs/RELEASE-ARTIFACT-POLICY.md
durable procedural language instead of saying this round performs zero writes.
Explicitly historical/as-of sections can stay historical. README is settled;
do not rewrite it or expand this into another documentation cleanup.

## L3. Obtain actual private registry truth with the existing CI credential

Strategy's current gh credential lacks read:packages. Reuse the existing
docker-published job's ephemeral packages:read token for a READ-ONLY authenticated
registry check BEFORE its prepublication gate. Use the existing strict resolver;
record actual states/digests for 0.1.0, sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a,
sha-be3c78b2016d5d40ce9155df8f94d14525c43d39, and 0.1.0-rc1. Inaccessible/unresolved
is never verified absence. No tag mutation, login credential printing, new token,
workflow or service. Image qualification still says NOT RUN without a real record.
This round's CI gives the before baseline; later published CI gives after evidence.
Historical 0.1.0 and sha-fe334e87 resolve to
sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011 in prior
evidence; verify actual current truth, report discrepancies, never overwrite.
Do not invent the orphan digest. Read package visibility with that same credential
if available; otherwise state the exact access evidence/limitation, without adding
privileges or asking to make the package public. No registry-writing dispatch.

## Evidence and completion

Keep changes small and reuse the closed 013-j/k evidence. Focused local tests plus
full fresh normal CI supply the gate evidence; no redundant full local suite rerun
is required when unchanged checks are covered by fresh CI. Preserve all assertions.
Commit final sourceA, make two clean isolated wheel/sdist builds, require identical
bytes, run artifact policy/install smoke, then commit only regenerated excluded
manifestB and prove source-input equality. Existing tool pins remain unchanged.
Wheel should remain ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e;
sdist legitimately changes for the named docs/CI/tests. Explain any unexpected
wheel drift; never update its expected hash to hide unrelated input changes.

Report L1–L3, actual test names, source/metadata hashes, fresh CI, registry states
and access evidence concisely. Source round only: no claimed RC digest yet. Strategy
then selects literal reviewed sourceS for the already-human-authorized private
publication and derived-record round. No further product changes are planned.

## Safety and immutable publication contract

All human 013-i/j/k limits remain binding: no benchmark code/design/tasks/judges/
controller/ledger/A100 setup/pilot/experiment/telemetry/statistics/instrumentation,
no experiments/codex_adapter_benchmark, no src/config/uv.lock/runtime changes.
No registry writes/dispatch, final v0.1.0 Git tag, GitHub Release, public visibility
change, final release claim, protected-host cutover or Gateway routing mutation.
No host Docker daemon use, Qwen inference, port 18020/qwen-serving/model/checkpoint/
patch/venv/systemd/launch/API-key/firewall/VPN/network-binding/profile mutation.
Host checks read-only; safe repo-local fake tests may use free loopback 18031 and
must clean up. Recheck protected baseline before/after. No secrets/customer content
in logs/reports. Preserve Local/clean/unchanged; routine setup stays with coding.

Commit exact activated order/active 013-l on PR #15. No merge/auto-merge/force-push or
prior OAP edits. After fresh green CI, publish exactly
oap/reports/013-l-rc-pull-and-handoff-integration.md as report-only SELF child of
literal immediate pre-report Implementation head SHA. Verify remote head/parent/
path/bytes, send exact response FIFO OK, then make no further mutations.
