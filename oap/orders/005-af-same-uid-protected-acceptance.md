# OAP Work Order — 005-af

## Objective and exact state

Resolve005-ae's local execution-identity mismatch without weakening the safe
evidence reader, finish/re-establish its preparation gates, then execute one
newly authorized bounded protected matrix. No new feature objective or PR;
AMEND_EXISTING_PR on Objective005 PR7. No service change, cutover or merge.

- ulfe-lmi/slaif-local-coding PR7:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Start immutable report `d06cee3f6ea365cdd25c00b45bfa09bfe1431c44`;
  report-only parent `c86228f0c1fce8c178f2c86ff113601408d0d7da`.
- Report oap/reports/005-ae-qualified-framing-and-single-protected-matrix.md.
- Code source `efc6bb4dc87a1a9253d42d09c49faf7aa5ff64de`; later changes only
  evidence/report. Exact order/topology/clean checkout verified; PR OPEN/CLEAN,
  final test SUCCESS34439184651/job102750441285;005-af unused.
- Gateway execute `50dcc3b85d614eb1d0c6196595bf22ef5779f846`; main authority
  `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`; report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`; app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`. Keep pins unchanged.

Reconcile GitHub, source/import identity, required checks and host before edits.
After activation only exact order and active005-af are expected new differences.
Read005-ae order/report and current evidence completely; its preparation,
security, qualification and stop requirements continue except for the explicit
execution-identity clarification below. Preserve every previous artifact and
UNKNOWN005-r/v fact; do not rewrite/retry/reinterpret005-q or005-ae.

## A. Same-UID preparation; no whole-harness elevation

Strategic read-only facts: current UID=EUID1029(janezp), Qwen PID23961 UID1029,
evidence owner1029/mode0600/regular/nlink1. The actual evidence reader accepts
the file as1029; a no-resource simulated UID0 reproduces the reported unsafe-file
error. The existing _docker helper already runs sudo -n docker.

Run the fake producer, fake validator, protected harness, Local/Gateway/Codex
processes and evidence handling as the current UID1029. Do NOT prefix the whole
runner with sudo, sudo -E, su, or another UID-changing wrapper. Privilege remains
confined to the existing bounded Docker helper. Do not change user groups,
Docker socket permissions, host policy, services or protected files. Do not
chown the repository, old evidence, Qwen resources or another user's files.

Use an owned private temporary directory and0600 regular, single-link evidence
files. Before any protected-mode command, record safe UID/EUID/file-owner/mode/
link facts and verify exact evidence hash/source. Retain the current symlink/
no-follow/regular-file/owner/link checks; never accept another owner simply to
pass. Validate the full fake result under the SAME UID and environment that
will execute the protected runner, before credential resolution. This is routine
coding setup; do not ask human/strategy to copy/chown files or run commands.

Expected implementation need is small or zero. Only bounded execution-context,
provenance/failure evidence, or outstanding005-ae preparation/negative tests may
change in existing support files. No opportunistic redesign. Any source/config
change requires fresh focused/full tests, fake qualification and green CI.
If ordinary same-UID credential access later fails, stop and report the exact
bounded class; do not elevate the whole runner, change permissions or substitute
another credential source.

## B. Freeze, qualify and enforce every prerequisite

Retain the fixed explicit/data-only/mixed SSE observer, opaque call correlation,
strict actual omission companion, generated source/module hashes and closed
37-fake/29-protected manifests. Include exact source hashes, not stale manual
summaries. Commands must have concrete paths or explicit parameter bindings.

Complete any remaining005-aeA ownership proof: actual missing/mismatched call-ID
and wrong-key companion requests at the Gateway boundary must be denied before
private/provider advancement and leave no pending accounting. Use the existing
two authorized Gateway test keys and negative-matrix scope, not extra inference.
Do not derive HMAC/no-scope-downgrade solely from a generic success flag. Retain
natural Codex present-ID shape separately from the actual ID-less companion.

Push exact order/active and any support changes, freeze a clean literal code
SHA, and require all implementation-head checks present and successful. Run
fresh full real-Codex0149 fake37/37 C1–C5/D and shared protected-mode synthetic
29/29 with oracle unavailable, plus the four serial healthy/observer-failure/
combined-failure/zero-access mapping cases. Preserve all signing/replay/tamper/
tool/HMAC/isolation/image-history/compiler/cache/rehydration/accounting/privacy/
cleanup/fake rollback-refusal predicates. Run frozen full pytest/Ruff/format/
mypy/compileall/shell/build/wheel-boundary/diff/pin/privacy checks. Routine build
alternatives remain coding's responsibility; no host package or lockfile changes.

Store generated results outside the checkout until the attempt finishes. Verify
source/hash/cardinality/status/counter/UID consistency and _validate_fake_gate
success as1029. No protected credential or traffic if anything is missing,
failed, pending, stale, unsafe or unobserved. No manual all-true attestation.

## C. Exactly one newly reviewed protected matrix

005-ae reached no credential/provider path. This order grants a new single
attempt after A+B, not permission to retry any failed protected boundary.
Use real unmodified Codex0.149.0 -> exact Gateway50dcc -> frozen Local candidate
and qualified observer -> unchanged protected vision Qwen. Exact Codex binary:
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex;
SHA256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.

Preserve900 seconds,64 aggregate observations, nine macro operations maximum1/
zero retries, existing per-operation compiler/inference/output limits, one
compiler/stream concurrency,16KiB/frame and128KiB/stream. All health/models/
readiness calls remain counted and scoped. No extra diagnostics/prompts/calls.

After full qualification and unchanged preflight only: same-UID process resolves
the active vision unit's exact MainPID, verifies unchanged identity and reads
only its unique nonempty VLLM_API_KEY into bounded memory, using the existing
005-o/r/v/ae mechanism. Pass it only through the task harness QWEN3090_API_KEY/
Local upstream header; discard afterward. Never print/hash/persist it, expose
argv, send it to Codex/public Gateway metadata, source Qwen config or inspect
unrelated environment entries. No new credential or privilege authority.

Require every protected C1–C5 criterion from005-aeC: readiness/model/nonstreaming,
real Codex two-turn function and same-session vision full-image→crop/history,
actual omission companion/HMAC, all semantic SSE/usage lifecycles, compiler/
governance/cache/rehydration, all identity/signing/replay/tamper/authorization/
key/session/owner/repository isolation/failure/accounting/privacy/cleanup, correct
finalization/release and zero pending/duplicates. Controlled failure stays on
the existing synthetic failure route, never deliberate Qwen failure.

FIRST unexpected failed/unobserved protected boundary stops all later protected
dispatch. Preserve exact actual counts, source, phase/ordinal, primary and
secondary failure/accounting/cleanup facts. No protected retry after repair,
alternate diagnostic call or Gateway/Qwen patch. Establish ownership from direct
bounded evidence and return. Real outcome is never inferred from fake success.

## Protected-host and publication law

Baseline: hinton1 vision active/running PID23961,UID1029,startSun2026-09-06
18:57:26CEST,NRestarts0,18020listener/health200; text inactive/MainPID0 expected;
seven Qwen worktree changes;18021/18030/18031 free. Preserve qwen3.8-27b/context
100000/one sequence/image and actual OAP profiles. Candidate127.0.0.1:18031;
existing verified-free ephemeral loopback Gateway port, with exact PID/port
cleanup. Existing PostgreSQL16 loopback/tmpfs/--rm/bounded Docker helper only.

No Qwen/model/checkpoint/patch/venv/unit/launch/GPU/key-file/network/firewall/VPN/
profile mutation, restart/instrumentation/second model; no Gateway implementation/
PR change, src/ feature change, new subsystem/relay or installed cutover. No raw
secrets/prompts/source/images/tool/model/SSE content, IDs/signatures/nonces/private
endpoints or arbitrary errors in logs/cache/evidence. Clean only exact owned
resources and preserve unrelated work. Verify protected state before/after with
permitted safe facts. Cutover, merge and release remain unauthorized/unclaimed.

Generate source-bound evidence under oap/evidence/005-af after testing, with actual
UID and file guard facts, full row/status/count/companion/accounting/cleanup data,
exact commands/pins/hashes and any NOT RUN reason. Do not overwrite old evidence.
Amend PR7 only, push all non-report changes plus exact transcript, capture literal
implementationSHA, then atomically publish exactly
oap/reports/005-af-same-uid-protected-acceptance.md with Implementation head SHA
and Report publication commit: SELF. Final commit report-only, parent exactly
implementationSHA; verify remote head/parent/path/bytes before response FIFO OK.
Never merge/auto-merge or create another PR. COMPLETE only with genuine ordered
acceptance; otherwise truthful PARTIAL/FAILED/BLOCKED. Distinguish IMPLEMENTED/
TESTED/REAL-E2E ACCEPTED/CUTOVER ACCEPTED/MERGED/RELEASE-READY. Return for review.
