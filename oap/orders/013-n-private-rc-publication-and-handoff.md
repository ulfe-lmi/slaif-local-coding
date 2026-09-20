# OAP Work Order — 013-n

## Objective and exact source

AMEND_EXISTING_PR #15; Objective013; NO NEW PR. Publish and freeze the already
human-authorized private 0.1.0-rc1 artifact, then record and qualify its immutable
digest. No further source implementation is authorized in this round.

The exact approved image source S is
4d096e404e14badb78b4f99142bf08ef17f0f8a7.
This is the current remote PR head and verified report-only SELF child of
39f453eb931ddbcfba7a12627b32a77939686688. Active013-m, unique immutable report,
literal parent, changed path and exact remote/local bytes were independently
verified; report SHA25648813b404a7b316822dccff3c03ff80e1bf84b94773efbdf8999c37411212941.
Fresh report-head CI35532806219 is all5SUCCESS. All121 artifact inputs at S
independently match the qualified source/manifest. M1–M3 are accepted.

Repository ulfe-lmi/slaif-local-coding; PR
https://github.com/ulfe-lmi/slaif-local-coding/pull/15; branch
oap/013-mvp-release-publication; base main a04693e6792df6a8ad4262acfb46336a0f662202.
Qualified sourceA1368e12cf67314ff03e24dc9198254e08c33e30b and metadataB
39f453eb931ddbcfba7a12627b32a77939686688 have identical121 input hashes,
independently checked against the remote manifest. Wheel:
ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e.
Source archive:4fc43041cc6c5f1fd92590cb24fa260d8ce2dbd8d599393fdad10eaff8a58659.
CI35532178837 all5SUCCESS:1277passed27skipped; actual image has exactly17 locked
runtime dependencies plus product, independently compared to uv.lock; actual
linux/amd64 inspection passed; prior ignored-venv warning is absent. M1–M3
accepted after exact report/SELF/current-check review recorded above.

Authenticated GHCR baseline is PRIVATE; RC1 absent; preserve legacy0.1.0 and
sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a at
sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011,
and sha-be3c78b2016d5d40ce9155df8f94d14525c43d39 at
sha256:15778b30d6a929d01fa42dffccc363f89967d22d92610466bb531cca5027e113.
Frozen Gateway authority08ca421bee1ddca62078302b910e8be88cf705be stays unchanged.
Protected host independently rechecked unchanged immediately before activation:
user qwen-serving-vision.service active/running PID23961 since2026-09-06
18:57:26CEST; only18020 listening among18020/21/31/33/34; qwen-neumann profile
SHA3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb.
Actual coding provider remains qwen-neumann/qwen-LSI-A100 Responses at
http://maelstrom1.lmi.link:8001/v1, modelqwen3.8-27b; protected, not a benchmark VM.

## N1. Publish one image from literal S

Verify remote PR head equals S and its artifact inputs equal the qualified map.
Dispatch EXISTING release-image.yml with ref oap/013-mvp-release-publication
WHILE that remote branch is still exactly S, BEFORE pushing this order/active
or any derived metadata. Local OAP changes are excluded from all artifact inputs.
Verify the resulting workflow run head SHA and checkout are exactly S; record
run id/URL. No final Git tag or additional Git tag is needed.

Use the existing ephemeral packages:write workflow credential and reviewed
publisher. Authenticated verified-absent for BOTH sha-S and0.1.0-rc1 is required
before writes. Occupied/partial/inaccessible/unresolved states require a factual
report and strategic adjudication: never blindly retry, rebuild, overwrite or
repoint an identity. Publish only these two RC tag aliases. No legacy-tag write.
The workflow must build the exactS wheel/image, verify wheelW, and verify both
registry tags resolve to ONE actual digestD. Tags are aliases; OCI@D is the
authoritative immutable identity. Keep the package private.

## N2. Record actual facts without moving artifact inputs

Use existing rc_artifact_record.py to generate packaging/rc_record.json and its
deterministic human view packaging/rc_handoff.md from actualS,D,W, publishing
run head/id and observed successful-publication timestamp. Include the existing
tool/base/platform/lock/Gateway/config-input hashes and deployment/auth facts.
No placeholders, invented identifiers or benchmark procedure. The external
consumer pulls OCI@D, obtains Compose/config at S, verifies identity, and does
not rebuild the image or need OAP history.

Clean sourceS wheel/sdist must match the qualified identities above. Regenerate
excluded release_provenance_manifest.json in RC-published state using existing
tooling and truthful source binding. Record image-sourceS, metadata commitR and
reportSELF separately. Prove input maps atS and finalR are equal and S..R changes
only derived metadata/OAP paths. Preserve the source generator/test OBJECTIVE
constant from M; do not change source/tests merely to follow the new OAP suffix.
README/docs/build files/lock/config/src/helpers/tests are frozen. If a new source
defect is demonstrated, report it; do not silently alter or republish the image.

## N3. Qualify the actual pulled digest and publish the reviewable result

Full fresh CI required: test/docs/artifact gates, frozen Gateway contract, normal
Docker, operator-session, and REAL docker-published qualification against D.
The published job must RUN (no prepublication NOT RUN): authenticated digest
and tag pulls, matching registry digests, real image OS/architecture, source/
version/RC/wheel/Gateway/topology labels, retained wheelW, actual installed lock
inventory, noneditable install, canonical no-build pull deployment, signed
ingress/negative cases, fail-closed readiness, hardening, lifecycle and teardown.
Inspect failures and report them honestly; do not weaken any gate.

Read-only after baseline must show PRIVATE visibility, old tags unchanged and
both new aliases atD. No new credential or privilege expansion. No redundant
full local suite is needed when unchanged runtime is covered by fresh full CI.
Rewrite PR title/body around the final RC result and actual validation/record,
removing stale013-i/v4/zero-write claims. Concise reviewer-facing description.

## Safety and immutable report

No benchmark design/code/tasks/judges/controller/ledger/A100 setup/pilot/
experiment/statistics/telemetry/instrumentation or experiments/codex_adapter_benchmark.
No finalv0.1.0 tag, GitHub Release, final release claim, public visibility change,
protected-host cutover or Gateway routing mutation. No host Docker daemon use,
Qwen test inference, port18020/qwen-serving/model/checkpoint/patch/venv/systemd/
launch/API-key/firewall/VPN/network-binding/profile mutation. Protected checks
read-only before/after; actual Docker qualification runs only disposable CI.
Preserve Local/clean/unchanged, all prior OAP and the frozen artifacts. Routine
setup stays with coding. No secrets/customer content in evidence or credentials
in the handoff. Human release authority remains deferred.

Commit exact activated order/active013-n plus only the authorized derived metadata
on PR15. No merge/auto-merge/force-push. After implementationR is remote with fresh
green CI, publish exactly oap/reports/013-n-private-rc-publication-and-handoff.md
as report-only SELF child of literalR. Report S, RC1, OCI@D, W, tools, Gateway pin,
CI runs/checks, immutable handoff paths and limitations; explicit benchmarkNO,
finalpublicreleaseNO, protectedcutoverNO. Verify remote head/parent/path/bytes,
send exact response FIFO OK, then stop. Strategy alone reviews and may merge.
