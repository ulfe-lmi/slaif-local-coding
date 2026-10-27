# OAP 017-z report — inert fixture identity contract

## Status

COMPLETE for the ordered scope: the SOFTWARE-ONLY, INERT versioned fixture
identity contract (descriptions, closed record, codec, configuration
fingerprint, bounded read-only host-ID collector, focused tests, docs) is
implemented and verified. No actual fixture, Docker, admission, native or
runtime work was performed or claimed; no `.oap-local/017-z` root exists.
Whole-017, native, D09 and v1 runtime delivery remain unearned, and every
018-024 stage remains required.

## GitHub / PR state (explicit)

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #25 — OPEN, AMENDED, same branch `oap/017-cache-read-observation`
- Base: `main` @ `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
- Starting remote head (prior 017-y report-only SELF):
  `cab238b2f225924bed6ebcfef833ba653e330799`
- Implementation head SHA: 27d62aad359cc51ab0794717b4148d5844fe9885
- Report publication commit: SELF
- No new PR. No merge, no auto-merge. Order and `oap/active` unchanged and
  committed with the source.

## What landed (all at the literal implementation head)

- `scripts/cache_native_fixture_identity.py` — stdlib-only, typed, no CLI,
  no import side effects. Two closed, explicitly named, immutable identity
  descriptions distinct from adapter cache profiles:
  `slaif-fixture-identity-original-v1` (controller 21001/21001, subject
  21002/21002, expected groups (21002,)) — REMAINS the current fixture
  identity, every old record/schema/constant meaning unchanged; and the
  INERT `slaif-fixture-identity-owner-uid-v1` candidate (subject UID/GID =
  the captured eligible host owner's real/effective/saved values, each
  triple equal, nonroot, strict finite Linux IDs 1..4294967294, distinct
  from the controller; expected subject groups exactly the primary GID,
  never host supplementary groups). Strict closed record
  `slaif-fixture-identity-record-v1` with a bounded mapping codec (<=4096 B,
  exactly one mapping, no duplicate keys; malformed/duplicate/over-bound/
  missing/extra/contradictory input refused with fixed non-echoing reasons;
  over-bound checked before any copy), construction enforcing the complete
  field laws (immutable group-vector ownership; oversized vectors refused
  before copy), and a deterministic canonical configuration fingerprint —
  a configuration digest, never a process hash, trusted receipt, admission,
  cache key or readiness certificate. Bounded READ-ONLY host-owner-ID
  collector: stdlib getresuid/getresgid plus cross-checked simple getters,
  one collection, explicit unsupported/unavailable outcome; no fs/proc
  traversal, env/config/profile read, network, subprocess, signal or
  privilege mutation. Typed objects, decoded data, profile names,
  fingerprints and caller flags never establish measured authority; no live
  profile is selected, no admission recorded, no ready/native verdict
  yieldable. The required later sealed-child integration boundary
  (canonical profile selection, collect/freeze actual owner IDs, bind to
  the ORIGINAL verified order/head/run and live admission before external
  work, revalidate the same context at use) is described, not implemented.
- `tests/test_cache_native_fixture_identity.py` — 19 focused tests (48
  collected cases): original 21002 exact description/round-trip/fingerprint
  cross-bound to the unchanged production constants; old 21002 record law
  re-proved unchanged through the production model validator (including its
  empty-group allowance); owner-UID derivation from one faithful eligible
  nonroot observation; mismatched triples, getter failure/missing support,
  root, controller collision, malformed/boolean/string/out-of-range IDs,
  missing/extra/contradictory fields, unknown profile/schema, duplicate
  keys, over-bound bytes; supplementary groups never inherited; caller
  mutation/alias refusal; original/new profile isolation for equal numeric
  tuples; deterministic fingerprints; pure data yields no authority;
  import/use performs no external operation or fixture state change; plus
  one ACTUAL safe current-host UID read exercised as OS-data-only evidence
  (never containment or executable capability).
- Docs: `ARCHITECTURE.md`, `TESTING.md`, the fixture contract (new
  section 11i), the stage ledger (017 row), and all THREE compact
  architecture copies made byte-identical again (root,
  `oap/strategic-instructions/`, and the external mirror, written in place
  preserving its 0600/uid1001 identity).
- Packaging: the helper is repository-only under the existing policy
  (pyproject top-level `scripts` exclusion and the artifact policy's
  forbidden `scripts/` prefix in BOTH artifacts); it enters neither wheel
  nor sdist and is bound by the committed source identity and the clean
  git-archive check. The new test file refreshes the development provenance
  input map normally: 197 -> 198 inputs. No published RC record rewritten.

## Verification (all at literal head 27d62aad359cc51ab0794717b4148d5844fe9885)

- Focused new suite: 48 passed (0.24 s).
- Relevant original fixture suites (11 files): 933 passed / 1 failed
  (202.33 s) — the sole failure is the expected intermediate
  `test_real_development_state_consistent` rejecting the then-UNTRACKED new
  test against the prior head (the strict artifact-state guard doing its
  job); it resolved by the source commit and passed at the committed state.
- Full frozen development gate (process-local umask 022, protected
  outputs): 3275 passed / 28 skipped (550.99 s); compileall, ruff check,
  ruff format, mypy src tests, docs consistency (19 claim docs), uv lock
  check, uv build, artifact policy inspect + install-smoke, dev provenance
  verify — GATE_COMPLETE.
- CI: all 10 implementation checks SUCCESS at the literal head.
- Clean git-archive reproduction: 198-input map verified (0 missing / 0
  mismatched); both artifacts byte-identical to the manifest; helper bytes
  bound at the literal head; 30/30 wheel-module bytes equal the archive
  source.
- Fresh-venv installed27: 27/27 (fresh non-editable install outside the
  checkout); actual 30 fresh site-packages module bytes equal wheel and git
  source at the literal head.
- Frozen21: 21/21 at the literal head, all probe hashes unchanged.
- Root-independent (separate scopes): 19 unchanged prior private probes
  110 checks PASS; new public identity probe 9/9 and constructor-boundary
  probe 10/10 PASS; preservation 183/183 plus known-temp 3/3.

## Artifacts / provenance (measured)

- Wheel: `1f2ebaff444be1ae...` (142753 B) — byte-identical across the
  measured P/R/S/T/U/V/W/X/Y/Z implementation line (Z touches no src/);
  earlier 017 observation rounds changed src and are not part of this wheel
  line.
- Sdist: `1c268b68fc6a1ba3...` (944390 B) — refreshed (new test + docs).
- Manifest: 198 inputs at source A `a7ec94b5ee79b27bce4ec2882e3cb07ae196a7f4`;
  manifest-only child B = the implementation head above.

## First failures and deviations (retained, not relabeled)

- The one focused-run failure above (intermediate dev-provenance state) —
  retained under the Z work root.
- First `fresh-module-identity` and first `archive-identity` runs retained a
  copied Y scope label ("Y FINAL head B4" / "verified-gone wording
  correction"); the first JSONs are retained as
  `-first-mislabeled-scope.json`, and the corrected measurements (identical
  results, corrected labels) are the current evidence. The frozen21 first
  note (retained as `-first-mislabeled-note.json`) was corrected the same
  way — probe results, hashes and head unchanged.
- Four manual output files (docs-consistency.out, docs-test.out,
  installed27-launch.out, manifest-generate.out) were created before the
  precreate-0600 protocol was in place, with ambient-umask modes 0664/0644;
  they were exact-path repaired to 0600 before this audit (bytes/inodes
  preserved). All other manual Z metadata is 0600/0700 from creation under
  the fresh 0700 Z root.
- No `/tmp` metadata was created this round (one attempted /tmp redirect
  aborted before any file existed).

## Append-only: 017-y publication-method qualification

Per `reviews/017-y-decision.md` (never editing Y): the 017-y report first
existed as an untracked canonical-path draft and was corrected before SELF;
a private draft copy was retained; root has NOT established atomic final
filesystem creation from the retained Y evidence (canonical inode 6848654
unchanged from the earlier draft). No retroactive atomic claim, no guessed
commands, no post-SELF change. The protected Y final bytes and the remote
report-only Git publication ARE verified. The first unpublished Y audit's
future 11:05 timestamp was corrected before SELF to actual 11:02:20Z (root
snapshot preserved). This is a bounded publication-evidence limitation, not
a source or actual-capability failure. This round's method was executed as
ordered: the report was finalized under the fresh private Z root FIRST,
then the previously absent canonical path was created atomically
(same-directory temp, fsync, no-overwrite, 0600).

## Historical pointers (immutable reports; no relabel)

- 017-x actual attempt: consumed at literal head
  `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da` (run
  `9fd5cf1d95924a47b8bf53e8624242a5`) — terminal FAIL, `capability` null.
- 017-y actual attempt: consumed at literal head
  `35a3bcd7322535dd4a699efc53c0c1c62d4c942e` (run
  `fbe526a3290d465298bc8da61ef2a304`) — closed driver PASS, subject
  identity measured, current executable UNKNOWN (no digest);
  `verified-gone` proves absence only. Neither is retried, reset or
  relabeled.

## Remaining gaps (explicit)

- The owner-UID candidate is INERT: not integrated, not qualified. A later
  profile requires private PID/mount/IPC/UTS/network namespaces, no host
  mounts/devices, rootfs-readonly, cap-drop-ALL/no-new-privileges/seccomp,
  exact bounded storage/memory/swap/pids/CPU, controller-private paths and
  EMPIRICAL keyring denial under the matching host UID — matching UID is
  NOT proof of safe containment. The later native artifact (308139304
  bytes) needs a later justified native-size byte/time measurement bound,
  not blind reuse of the Python 16 MiB/10 s bound.
- Actual native / D09 / v1 runtime delivery remains `NOT RUN`/unearned;
  every 018-024 stage remains required.

## Publication method (this round)

PR #25 title/body refreshed (concise current-state body, <=600 words)
before SELF. This report: finalized under the private Z root first, then
the absent canonical path created atomically (same-directory temp + fsync +
no-overwrite, 0600). The final self-inclusive metadata audit was performed
LAST, after all final manual metadata, with the actual measured UTC
timestamp.
