# OAP Work Order — 013-m

## Objective and GitHub state

AMEND_EXISTING_PR #15; Objective013; NO NEW PR. Correct the demonstrated Docker
runtime dependency-lock bypass and finish the image inspection needed for RC
freeze. L's renderer, strict v2 consumer and authenticated registry baseline are
accepted; its actual platform assertion is incomplete. New independent Docker
log evidence establishes the runtime lock defect below. No RC may be frozen
from the L source state.
Repository ulfe-lmi/slaif-local-coding; PR
https://github.com/ulfe-lmi/slaif-local-coding/pull/15; branch
oap/013-mvp-release-publication; base main a04693e6792df6a8ad4262acfb46336a0f662202.
Starting remote head 2d2a6a5b32ced6a5f6c3512c84504b1965721213 is verified report-only
SELF child of implementation1689817984fa4b653d2208ee908f0673002fd250. Active013-l
and its exact unique remote/local order/report bytes were verified. SourceA
d0804e9194a8912abf9201e642aa5df71178fb05 and metadataB have all120 input hashes
equal. Source CI35529144342 is green (1236passed27skipped, Gateway18/18,
Docker15phases, operator19phases; published-image qualification explicitlyNOTRUN).
Fresh report-head CI35529984229 is also all-green at activation.
No Git tags/Releases exist. RC1 is authenticated verified-absent; preserve legacy
0.1.0 and sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a at
sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011 and orphan
sha-be3c78b2016d5d40ce9155df8f94d14525c43d39 at
sha256:15778b30d6a929d01fa42dffccc363f89967d22d92610466bb531cca5027e113.
No orphan investigation or cleanup is ordered.

Protected baseline independently rechecked18:44UTC: user visionunit active/running
PID23961 since2026-09-06 18:57:26CEST; only18020 listening among18020/21/31/33/34;
qwen-neumann profile SHA3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb.
Actual coding path qwen-neumann/qwen-LSI-A100 Responses at
http://maelstrom1.lmi.link:8001/v1, modelqwen3.8-27b, remains protected (not a
benchmark VM). Frozen Gateway authority08ca421bee1ddca62078302b910e8be88cf705be
remains unchanged.

## M1. Install and prove the actual frozen runtime dependencies

Independent CI35528765082 job106125494407 shows Dockerfile runtime step19
ignores VIRTUAL_ENV=/opt/slaif/venv and creates /build/.venv, then deletes /build.
Step21 resolves the wheel's dependencies anew into the empty runtime venv:
anyio4.15.1, pydantic2.13.5, uvicorn0.53.0 vs uv.lock4.14.2/2.13.4/0.52.4.
This is a concrete reproducibility defect despite green behavioral gates.

Make frozen sync target /opt/slaif/venv explicitly, and install the built wheel
without a second dependency resolution. Preserve uv.lock and all existing
runtime version selections, build pins, base digests, src and config bytes.
Extend the existing in-image provenance gate to inspect actual installed runtime
distribution names/versions against the frozen lock closure for the supported
Linux amd64/Python3.12 image (plus the product wheel). Reuse uv export/lock
capabilities and importlib.metadata; no new dependency-resolution framework.
Missing or wrong-version runtime dependencies must fail. Verify these negative
cases with focused tests, and prove the actual corrected image passes in fresh
disposable Docker CI, including the existing release-build-command proof.
Published mode must apply the same dependency check to the subsequently pulled
digest. No test-only labels or self-declared version map may substitute for
observing the installed environment. No new product instrumentation.
Primary uv authority: https://docs.astral.sh/uv/concepts/projects/config/ .

## M2. Inspect actual image OS/architecture

The L helper compares container inspect Platform (OS-only) to linux/amd64.
Read actual image Os/Architecture using docker image inspect at its image
reference/digest. Apply the assertion in ordinary build qualification as well
as published mode so source CI exercises the real Docker inspection now.
Preserve all existing wheel/label/hardening/signed-ingress/lifecycle assertions.
No new mocked-Docker framework. Real published-digest proof follows publication.
Primary Docker example uses image .Os/.Architecture, not container Platform:
https://docs.docker.com/reference/cli/docker/image/import/ .

## M3. Correct the optional visibility query; stop there

L's docker package-type lookup targets the legacy docker.pkg.github.com registry,
not GHCR; its empty list cannot establish GHCR visibility. Use the direct GET
/orgs/ulfe-lmi/packages/container/slaif-local-coding with the SAME existing
ephemeral packages:read token and explicit supported GitHub API version. Record
the visibility if returned, otherwise the exact nonsecret status as a limitation.
Do not add credentials, permissions, services, retries or a discovery framework.
Anonymous GHCR token exchange independently returned401; CI authenticated tag
resolution succeeds. Authentication is already available for private publication.
Primary REST authority distinguishes container from legacy docker:
https://docs.github.com/en/rest/packages/packages#get-a-package-for-an-organization .
Correct the L report's enum/platform assertions prospectively, never by editing
its immutable bytes. A denied optional visibility query is not another repair
loop or a reason to request broader access.

## Evidence, artifacts and scope

Focused local tests and full fresh normal CI (test, gateway-contract, docker,
operator-session, docker-published with honest prepublicationNOTRUN); no
redundant full local suite is
required. Two clean isolated wheel/sdist builds of final sourceA must agree;
regenerate excluded provenance metadataB and prove input equality. The wheel
must remain ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e.
Report actual runtime dependency inventory, real image platform, exact tests,
CI runs, source/metadata hashes and registry baseline. Preserve prior reports.
No README rewrite, general cleanup, new architecture, product features, runtime
dependency updates or uv.lock churn. This is the last demonstrated source fix
before strategy selects the exact reviewed publication source; no speculative
additional work. No registry writes or workflow dispatch in this source round.

All human limits remain binding: no benchmark design/code/tasks/judges/controller/
ledger/A100 setup/pilot/experiment/statistics/telemetry/instrumentation or
experiments/codex_adapter_benchmark. No final v0.1.0 Git tag, GitHub Release,
final release claim, public visibility change, protected-host cutover or Gateway
routing mutation. Preserve existing registry tags. Protected host read-only:
no host Docker daemon use, Qwen inference, port18020/qwen-serving/model/checkpoint/
patch/venv/systemd/launch/API-key/firewall/VPN/network-binding/profile mutation.
Candidate fake tests may use free loopback18031 and clean up. Verify before/after
protected baseline; no secrets/customer content in logs or artifacts. Preserve
Local/clean/unchanged; routine setup stays with coding.

Commit exact activated order/active013-m on PR15; no merge/auto-merge/force-push.
After fresh green CI publish exactly
oap/reports/013-m-runtime-lock-and-image-inspection.md as report-only SELF child
of the literal immediate Implementation head SHA. Concise factual report; do
not spend another repair loop refining an optional inaccessible visibility fact.
Verify remote head/parent/path/bytes, send exact response FIFO OK, then stop.
