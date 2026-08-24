# OAP Work Order — 004-d

## Objective

Amend objective-004 PR #6 with bounded, privacy-preserving diagnostics for the
unexpected dependency-cache outcome pattern and failed governance-derived
sentinel attempts. Produce enough sanitized evidence to determine whether cache
reuse is cross-content contamination, expected same-fixture retry reuse, or a
metrics/observation issue. Do **not** claim sentinel success or advance
completeness.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-d`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-c` SELF:
  `bfc291a2a9f782fa051b137e68fee1c47c35e941`
- Prior implementation SHA:
  `e68da52b817fff6b560cded8e1b52a36f72c2aa6`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; implementation/report-head CI
  SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Preserve every prior order/report byte.

## Verified diagnostic need

`004-c` deterministic TTL work passed. Governance-only real-Codex sentinel runs
used command tools and exited 0 but produced no helper-known acknowledgment.
The final harness reported dependency `cache_hit +3`, `cache_miss +0`, despite a
newly generated fixture and three attempts. This pattern must be explained
before further model attempts.

## Bounded scope

### A. Disposable E2E diagnostics only

Extend the E2E helper/result contract with per-attempt and final sanitized
facts:

- fixture root/dependency SHA-256 values;
- per-attempt deltas for root observations, dependency observations, dependency
  cache misses/hits/invalid/budget outcomes, injected requests, and compiler
  attempts;
- dependency included/missing/omitted counts from selected working-set metadata;
- command-event started/completed/failed counts and tool-call count;
- sentinel result as boolean/fixed reason only;
- persistent-cache inventory after the run: logical-key SHA prefix (first 12),
  entry bytes, created-age bucket or relative ordering, stored index kind/path,
  stored source-hash prefix, model, schema/compiler versions, and pinned state.

Do not emit raw source, prompts, events, model output, tokens, credentials,
request/response bodies, full private paths, or customer data. Hash prefixes and
fixed counters are approved for the OAP report. Keep all raw temporary material
in caller-owned disposable boundaries.

### B. One bounded diagnostic execution

Use one fresh adapter/cache/temp Codex home and exactly one actual Codex
invocation. Do not run a second invocation or retry loop. Preserve the existing
governance-only prompt/delegated token design. The diagnostic may end in
`sentinel_missing`; that is acceptable evidence for this round.

Assert mechanical consistency:

- observed fixture dependency hash matches the dependency bytes on disk;
- if a dependency cache miss occurs, its stored index source hash equals the
  fixture dependency hash;
- if a cache hit occurs, report whether a stored entry with that same source
  hash existed before the call and whether any different-source entries exist;
- reconcile per-attempt metric deltas with cache inventory;
- distinguish cumulative adapter counters from attempt deltas.

### C. Tests/documentation

Add focused tests using canned cache/metrics fixtures for all new sanitized
fact extraction/reconciliation logic, including mismatch detection and absence
of raw fields. Update README/E2E documentation for diagnostic fields and fixed
privacy boundary. Leave `oap/COMPLETENESS.md` objective-004 completion at 35%
and branch total ~78%; add only factual wording that diagnostics are being
gathered.

## Explicit non-goals

No second/retry model invocation; no sentinel success claim; no completeness
increase; no production cache logging; no raw payload persistence; no runtime
pipeline semantic change except harmless dependency-free diagnostic plumbing; no
protected host/profile/model/key/network/systemd mutation; no rewrite of prior
OAP artifacts.

## Acceptance criteria

1. New helper facts expose all listed bounded diagnostics without raw content.
2. Focused tests prove extraction, reconciliation, mismatch detection, and
   privacy boundaries.
3. One fresh actual Codex invocation completes the diagnostic matrix even if
   sentinel remains missing.
4. Cache outcome anomaly is classified as one of: expected retry hit, stale/
   cross-content entry, observation/mismatch, metrics interpretation error, or
   unresolved-with-fixed-evidence.
5. All local gates and current implementation/report-head CI pass; docs do not
   overclaim.

## Required verification

Run exact lock/frozen sync/Ruff/check/format/mypy/full pytest/build/
compileall/shell syntax/diff check gates. No ordinary live suite skip may be
called pass; the separate diagnostic invocation is explicitly required. Include
secret/raw-content scan, scoped diff audit, and protected-host before/after
snapshot.

## Publication contract

Push to exact PR #6 branch; never create another PR or merge. Record literal
implementation head after non-report work is remote. Atomically publish exactly
one immutable `oap/reports/004-d-dependency-cache-diagnostics.md`; SELF must be
sole final commit, parent equals implementation head, change only that report,
and be remote PR head before response FIFO `OK`.
