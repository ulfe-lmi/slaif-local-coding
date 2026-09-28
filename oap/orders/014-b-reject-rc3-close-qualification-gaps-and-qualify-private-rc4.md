# OAP Work Order — 014-b

## Objective and disposition of 014-a

AMEND_EXISTING_PR; Objective 014; continue PR #19 only. Round 014-a is not
accepted and must not be merged. Preserve its immutable report and evidence,
but correct the independently verified release-gate, schema, privacy, and
bounded-execution defects. Treat the already-published RC3 as an immutable,
historically resolvable candidate that passed its scoped real-Codex smoke but
failed overall release-candidate acceptance. Produce and qualify the next
collision-safe private candidate, `0.1.0-rc4`, only after every prepublication
gate is successful.

This remains product repair and private release-candidate qualification under
the human's existing Objective-014 authority. It authorizes the private RC4
publication needed because RC3 is occupied and may not be overwritten. It does
not authorize a benchmark, public visibility, final release/tag, GitHub
Release, Gateway production mutation, protected-host cutover, or any vLLM,
model, checkpoint, CUDA, parser, context, GPU, service, network, key, or Codex
profile mutation.

## Authoritative continuation state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective/round: `014` / `014-b`.
- PR mode: `AMEND_EXISTING_PR`; use PR #19 and no other PR.
- Base: `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`.
- Head branch remains `oap/014-real-codex-compatibility-rc3`; do not rename,
  recreate, force-push, or replace it.
- Starting remote head/report SELF:
  `2cc49e60405d87b16e8271cd129374077dd46323`.
- The report commit changes only
  `oap/reports/014-a-real-codex-compatibility-repair-and-private-rc3.md`, its
  first parent is literal implementation SHA
  `fa8f03030c138a074844837bc7f918ac482d2cce`, and protocol structure is valid.
  Its COMPLETE/BENCHMARK_READY claims are rejected for the factual defects
  below.
- Keep PR #19 non-draft. Update its title/body to the final RC4 outcome. Coding
  never merges or enables auto-merge.
- Preserve the pre-existing untracked zero-byte paths `Local`, `clean`, and
  `unchanged`.

## Independently verified rejection evidence

### 1. Publication occurred with a failed security policy gate

RC3 publication workflow run 36384605003 was dispatched at
2026-09-28T06:03:35Z from source
`307a929ffb30f4ea41c8be4e8a5ea25802e25142`. That exact source's aggregate
GitHub Advanced Security `CodeQL` check had already completed FAILURE at
2026-09-28T06:00:38Z with one new high-severity
`py/clear-text-storage-sensitive-data` alert. The workflow's `Analyze
(actions)` and `Analyze (python)` jobs succeeded, but those workflow jobs do
not supersede the separate aggregate policy check. The 014-a order required
fresh CI and CodeQL/security checks successful before registry mutation.

The same open alert, code-scanning alert #10, remained on final implementation
head `fa8f030...` and report SELF `2cc49e6...`; their aggregate `CodeQL` checks
also failed. The 014-a report's claims that prepublication/final CodeQL were
fully green are factually wrong.

### 2. The advertised RC record JSON Schema is internally inconsistent

`packaging/rc_artifact_record.schema.json` declares `$id` =
`slaif-rc-record-v3` but its `properties.schema.const` remains
`slaif-rc-record-v2`. `packaging/rc_record.json` correctly records v3, so the
record cannot validate against its advertised companion schema. Current docs
also incorrectly call the current record v2. Existing tests/custom loaders did
not exercise this companion-schema consistency.

This schema and its regression tests are sdist/source inputs. Correcting them
changes the frozen source-input map, so the correction cannot be attributed to
the already-published RC3 source. RC3 aliases are occupied and immutable;
therefore a new source commit and RC4 identity are required.

### 3. Qualification privacy claims do not match the implementation

`build_codex_argv()` places the fixed smoke prompt directly in the genuine
Codex process argv. It also places the provider `base_url` in `-c` argv; for
DIRECT this is the private backend URL. The qualification script itself
accepts the backend URL literally via `--upstream-base-url`, also exposing it
in process arguments. Codex 0.149 supports reading the prompt from stdin when
the positional prompt is absent or `-` is used. The 014-a order prohibited
prompt/private-URL exposure through argv. Ledger 002 remains truthful about
its sanitized committed files, but the underlying run does not satisfy the
process-list privacy gate.

### 4. The claimed execution bounds are not mechanically enforced

`subprocess.run(..., capture_output=True)` captures unbounded stdout/stderr;
`OUTPUT_CAPTURE_CAP` only truncates the recorded byte count after completion.
The gate requires at least one adapter request but enforces no upper request
ceiling. It records no mechanically bounded tool-call count and no compiler
call upper bound. Timeout/max-attempt settings alone do not establish every
bound required by 014-a.

### 5. Compatibility facts are manually asserted into the RC record

`rc_artifact_record.py` accepts client identity, arm verdicts, and evidence
path as independent CLI assertions. It validates syntax but does not derive
or cross-check them against the manifest-bound closed qualification facts,
wheel identity, protected-state verdict, or ledger manifest. The durable
handoff must be mechanically tied to its sanitized evidence.

## Immutable RC3 preservation

Do not delete, retag, repoint, overwrite, or republish either RC3 alias:

```text
source: 307a929ffb30f4ea41c8be4e8a5ea25802e25142
digest: sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436
tags: 0.1.0-rc3, sha-307a929ffb30f4ea41c8be4e8a5ea25802e25142
wheel: 897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d
publication run: 36384605003
```

Archive the current RC3 record, handoff, and provenance manifest byte-for-byte
under `packaging/releases/0.1.0-rc3/`, following the RC1/RC2 convention. Keep
`oap/evidence/testing-ledger/002/` byte-identical and describe it only as the
scoped RC3 real-Codex PASS evidence it is. Do not relabel or soften it. Ledger
001, RC1, and RC2 remain immutable.

Document RC3's overall non-acceptance in current history/release documentation:
its compatibility smoke passed, but publication preceded a successful
aggregate security gate and later strategic review found the record-schema and
qualification-harness defects above. This is not a claim that ledger 002's
recorded model/tool interactions failed.

## Workstream A — close the qualification-harness gaps

1. Resolve CodeQL alert #10 with the smallest sound code change. Do not dismiss,
   suppress, baseline, or downgrade the alert merely to make the check green.
   Prove that generated adapter/Codex configuration contains only an environment
   variable name, never the credential value.
2. Remove the smoke prompt from argv. Deliver the fixed synthetic prompt over
   stdin using Codex 0.149's documented stdin mode. Tests must prove no prompt
   substring appears in the argv.
3. Remove every private upstream URL from every process argv, including the
   qualification script's own invocation and genuine Codex's provider
   configuration. Supply the backend URL through a protected environment or
   mode-0600 disposable file; put controlled Codex provider/catalog settings in
   the disposable Codex home/config rather than `-c` arguments where needed.
   Preserve the loopback adapter URL where it is non-sensitive, but prefer one
   consistent protected configuration path. Delete disposable configuration.
4. Enforce a real stdout/stderr byte ceiling while each Codex process is
   running. Exceeding the cap must terminate the process/session, record only a
   sanitized failure class, clean up, and block the arm. Do not retain or emit
   raw output.
5. Establish explicit, tested upper bounds for adapter requests, compiler
   activity, model/tool interaction, attempts, duration, and arm count. Use a
   content-free event/counting method or another narrow deterministic mechanism
   to count tool activity without persisting raw tool arguments/output. An arm
   exceeding any ceiling fails closed. At least one genuine local tool
   interaction and its exact bounded sentinel remain required.
6. Preserve serial arm execution, fresh disposable state, gateway ingress
   disabled, static CACHE/BOTH identity, loopback 18031 adapter, protected host
   snapshots, wheel binding, and sanitized closed facts. Preserve the existing
   VISION/CACHE/BOTH semantics and DIRECT's contextual status.
7. Add focused pure tests for stdin delivery, argv secrecy, config permissions,
   cleanup, byte-cap termination, each activity ceiling, sanitized failure
   output, and unexpected-process cleanup. No ordinary CI dependency on a live
   backend.

## Workstream B — repair and bind machine-readable evidence

1. Correct the current RC-record schema identity consistently to
   `slaif-rc-record-v3`; update current docs/comments that incorrectly call the
   active record v2 while leaving archived historical v2 files byte-identical.
2. Add a regression that loads the companion JSON Schema and current record and
   at minimum proves their schema identity/required-key/closed compatibility
   contract is mutually consistent. Prefer actual standards validation if the
   repository already has a suitable locked dependency; do not add a dependency
   solely for this one assertion.
3. Make RC-record compatibility facts derive from one manifest-verified,
   closed-schema real-Codex facts file rather than independent manual CLI
   verdict assertions. Verify the ledger manifest, exact evidence path/client
   identity, overall and per-arm PASS, no-Gateway topology, wheel hash equal to
   the candidate manifest/in-image wheel, protected state unchanged, disposable
   state removed, and DIRECT's contextual result. Tampering, missing fields,
   mismatched wheel/client/arm, or a BLOCKED result must fail closed.
4. Keep the machine record content-free and deterministic. The handoff must
   render only validated facts. Tests must cover each mismatch class.

## Workstream C — source freeze and private RC4 publication

1. Reconcile explicit candidate constants, publisher guards, workflow labels,
   record/handoff generators, qualification gates, tests, and current docs from
   RC3 to RC4. The publisher accepts exactly `0.1.0-rc4`; final/stable denylist
   and collision behavior remain unchanged.
2. Freeze a new exact image-source commit `S4` only after every source/sdist/
   wheel/image/config input is final. Rebuild on the two available Python 3.12
   patch versions and prove byte-identical wheel and sdist. Record wheel `W4`
   and the complete new source-input map. No source input changes after `S4`.
3. Before any registry mutation, inspect the exact GitHub head and require all
   five CI jobs, CodeQL workflow analyses, and the separate aggregate GitHub
   Advanced Security `CodeQL` policy check completed SUCCESS with no pending,
   failed, cancelled, missing, or open high alert. Record exact check IDs/times.
   Workflow-job success alone is insufficient.
4. Authenticated strict checks must prove both `0.1.0-rc4` and `sha-<S4>` absent
   before any mutation and again immediately before writes. If either is
   occupied/partial/inaccessible, stop and report BLOCKED; do not select another
   number without continuation.
5. Dispatch the existing workflow from exact `S4`, publish exactly those two
   aliases to one new digest `D4`, and registry-verify them. Do not touch RC3,
   RC2, RC1, legacy/final/latest/stable tags or visibility.
6. Generate the current RC4 v3 record/handoff and published provenance from
   authenticated facts and the new bound compatibility evidence. Preserve the
   archived RC3 files byte-identically.
7. Final-head ordinary CI and the aggregate CodeQL policy check must all be
   successful. `docker-published` must pull and qualify actual `D4` by digest
   with the complete existing label/wheel/lock/hardening/readiness/security/
   teardown evidence.

## Workstream D — rerun genuine Codex qualification for RC4

Use the exact retained Codex CLI 0.149.0 binary first:

```text
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex
sha256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827
```

A later installed version remains allowed only if 0.149.0 becomes unusable for
a reason unrelated to the adapter; record exact version/hash/reason and rerun
all arms with that one version.

After RC4's source/check/publication gates are sound, rerun fresh VISION,
CACHE, BOTH, and safe DIRECT sessions using the corrected harness. Bind the
tested wheel exactly to retained in-image `W4`; separately rely on pulled-image
CI for container qualification. Require a genuine model/tool loop, bounded
sentinel, adapter/upstream evidence, configured image semantics, CACHE/BOTH
compiler evidence, zero internal 500/image-policy failure, enforced ceilings,
cleanup, and protected state invariance. If the backend/client or any required
arm fails, report BLOCKED; synthetic tests never substitute.

Commit sanitized evidence under the next ledger number, expected
`oap/evidence/testing-ledger/003/`, with its own manifest. Do not include raw
prompt, body, tool arguments/output, model output, credential, private URL,
session ID, source, or private path. Preserve ledgers 001/002 byte-identically.

## Required verification and acceptance

All 014-a requirements remain cumulative except that RC3 is preserved as the
rejected predecessor and RC4 is the target. At minimum require and report:

- exact diff/commit/PR identity and no second PR;
- ledger/archive byte-identity checks for 001, 002, RC1, RC2, and RC3;
- focused image-policy/full-app namespace-tool regressions still green;
- focused harness privacy/bounds/cleanup tests;
- companion RC schema/record consistency and evidence-binding tamper tests;
- Ruff, format, mypy, docs consistency, full pytest, compile/shell checks;
- two-patch exact build reproducibility, artifact inspection, fresh-wheel
  noneditable smoke, lock/source/provenance equality;
- fresh exact-`S4` prepublication CI plus aggregate CodeQL SUCCESS before the
  release workflow timestamp;
- authenticated absent-before/present-after RC4 tag evidence;
- actual pulled `D4` Docker qualification and all ordinary final-head jobs;
- final-head CodeQL workflow and aggregate policy SUCCESS, with no open alert;
- genuine corrected-harness VISION/CACHE/BOTH PASS and DIRECT result;
- protected service/profile/files/ports unchanged and loopback 18031 absent;
- private visibility (including an unauthenticated access denial check), no
  benchmark, no Gateway mutation, no protected cutover, no final release.

The final RC4 handoff must contain `S4`, `D4`, aliases, `W4`, build pins, lock
hash, source/config hashes, exact client version/hash, bound arm results,
platform, private-auth requirement, no-Gateway topology, benchmark-not-run,
final-release-false, and cutover-false. It must enable the separate benchmark
VM to pull by digest without rebuilding.

## Safety and protected host

The current protected fixture remains `qwen-serving-vision.service` on port
18020; 18031 is candidate loopback only. Recheck read-only before/after. Do not
run host Docker, restart/reconfigure services, alter vLLM/model/checkpoint/
packages/CUDA/flags/parsers/GPU/network/firewall/VPN/keys/profiles, access the
benchmark repository, or run any benchmark task. Bounded authenticated calls
to the existing endpoint are allowed without printing credentials or private
URLs.

## Report and verdict contract

Publish exactly
`oap/reports/014-b-reject-rc3-close-qualification-gaps-and-qualify-private-rc4.md`
as the final report-only SELF commit. It must identify the literal prior 014-a
SELF, new implementation head, `S4`, `D4`, `W4`, exact checks/runs/timestamps,
client/evidence/protected facts, and openly state why RC3 was not accepted. Do
not repeat the false claim that workflow analysis success meant the aggregate
CodeQL policy was green. Make no mutation after SELF, send exact FIFO `OK`, and
stop.

Propose exactly:

```text
BENCHMARK_READY
```

only if private RC4 exists, all source/final/post-publication security and CI
gates are successful, actual pulled `D4` passes, corrected bounded real-Codex
VISION/CACHE/BOTH all pass, the evidence-bound handoff is complete, and no
unresolved blocker remains. Otherwise propose:

```text
BENCHMARK_BLOCKED: <exact blocker>
```

Strategy alone accepts, merges, and issues the final verdict.
