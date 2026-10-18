# Development provenance (current-development artifact contract)

After the frozen `0.1.0-rc10` publication the repository keeps developing.
The frozen publication — `packaging/rc_record.json`, `packaging/rc_handoff.md`,
`packaging/release_provenance_manifest.json` (and its schema), the archived
`packaging/releases/` artifacts, the RC tags and the published images — stays
byte-identical and is never rebound to new source. Meanwhile the working tree
inevitably diverges from the frozen RC10 source-input map the moment any
document, test, script or workflow input changes. This page defines the
**separate current-development provenance contract** that keeps that
divergence honest without touching the frozen publication.

It is a validation contract, not a release: it authorizes no new RC, version,
tag or registry operation, and it never substitutes for release-candidate
qualification (see [Artifact policy](RELEASE-ARTIFACT-POLICY.md) and the
CACHE rework plan for the final-stage immutable identities).

## Artifact state law

Every verification first determines the artifact state at the current head:

- **frozen** — the mechanical source-input map at the current head equals the
  frozen RC10 recorded map. No development manifest is required; the frozen
  RC10 binding is re-proved and any built artifacts must match the frozen
  manifest's recorded hashes.
- **development** — the source-input map differs from the frozen publication.
  A valid, current development manifest is then **mandatory**; a missing,
  invalid or stale manifest fails closed. The gate never returns early,
  skips a failure, relaxes an exact hash, or replaces an accepted historical
  hash with a new one.

Order 016-c working-tree binding: **every** frozen/development verification
and CI emission path classifies from the committed map AND binds the actual
working-tree input map to it. Dirty or untracked mapped inputs never acquire
frozen or development authority (a clean frozen tree remains supported
without a development manifest); deliberately excluded OAP/derived-only
differences follow the existing explicit policy.

Order 016-d operator-session state selection: the operator-session CI's
`select_artifact_state` consumes the full authoritative state-aware
verification in **both** states before returning an expected wheel.
In the frozen state this additionally requires the actual working-tree
map binding AND the independent pre-rework frozen-publication baseline
validation: a pure committed-state classifier is not artifact
authorization, so dirty or untracked mapped inputs, and frozen
publication bytes that differ from the pinned baseline (even a
still-valid-JSON reformat), fail closed before any wheel is returned.
In the development state the closed manifest contract validation above
applies. The production invocation keeps the pinned freeze authority
(never a caller-controlled relaxation), and a clean frozen tree remains
supported without a development manifest.

The frozen binding is re-proved in **both** states: the map at the exact
frozen source commit must still equal the committed frozen manifest's
`source_inputs`, and the frozen source commit must remain an ancestor of the
verified head. The frozen RC10 record can therefore never quietly authorize
publication of altered development source (the rehearsal proves this
negative explicitly).

## Development manifest

`packaging/dev_provenance_manifest.json`, schema `slaif-dev-provenance-v1`
(`packaging/dev_provenance_manifest.schema.json`), records:

| Field | Meaning |
| --- | --- |
| `source_commit` | The exact development source commit A (40-hex). |
| `source_inputs` | The mechanical `path -> sha256` source-input map at A (same policy as the frozen contract: pyproject build policy + derived-metadata exclusions). |
| `artifacts` | Wheel and sdist `name`, `sha256`, `size_bytes`, `entry_count`, built **cleanly from `git archive A`** — a source proof, never a hash of arbitrary uncommitted inputs. |
| `toolchain` | Python version, uv version, `uv.lock` sha256. |
| `frozen_publication` | Cross-check facts (frozen manifest path, rc identifier, frozen source commit, frozen artifact hashes) that must still match the committed frozen manifest. |
| `self_referential_exclusions` | The development manifest paths deliberately excluded from artifacts and from their own input map. |
| `state` / `release` | Always `"development"` / `false`. |
| `qualification_label` | Deterministic non-release label `development-source-<A>; not a release candidate; not released`. |

A development manifest must never carry an RC or release identity of its
own; the schema pins the frozen publication constants so a drift is caught
independently of the manifest's self-reported facts.

## Source A / derived manifest B binding

- **A** is a clean source-input commit: the working-tree input map must equal
  A's input map (no uncommitted source drift) when the manifest is generated.
- **B** is the derived-metadata child commit that adds the manifest. The
  A..B diff may touch only the development manifest paths and the OAP
  transcript (`oap/`), and the input map must remain identical — the same
  A/B law as the frozen contract, with the development derived set.
- **Every later source change requires a refreshed development manifest**
  (regenerate at the new source commit and commit it as the new derived
  metadata). A source move under a derived-metadata commit, an omitted input,
  an altered input, or a stale source all fail closed.
- A development diff must never touch the frozen release metadata
  (`packaging/rc_record.json`, `rc_handoff.md`, the frozen manifest and
  schema, `packaging/releases/`); touching them is not development.

## Self-reference exclusion

The development manifest and its schema are explicit build-policy
exclusions in `pyproject.toml`: they are never artifact inputs (no
self-hash fixed point is needed) and are excluded from the manifest's own
input map. Ordinary source, configuration, docs, tests and the frozen
packaging records are **not** excluded.

## Closed-contract validation (order 016-c)

The executable validation enforces the closed development contract on
**every public consumption path** — including callers of
`verify_development` that bypass the loader (e.g. the record-present
rehearsal): exact key sets and const/pattern values (mirroring
`packaging/dev_provenance_manifest.schema.json` — `additionalProperties:
false` at every level, schema and executable validation agree), repository
identity, non-release facts, safe artifact basenames, valid 64-hex hashes,
integer sizes/counts of at least 1 (booleans are not integers), source-input
path/hash records without path escape, toolchain facts, the exact current
`uv.lock` binding (`toolchain.uv_lock_sha256` must equal the actual
`uv.lock` bytes at verification time), frozen-publication constants and the
declared self-exclusions. Malformed nested objects, booleans used as
integers, unexpected keys and path-escaping records are all rejected.
Nothing usable is emitted on invalid state.

## Independent pre-rework freeze baseline (order 016-c)

Freeze immutability no longer rests on the A..HEAD diff alone (which cannot
see a frozen metadata change committed inside a newly authored source A).
Every development verification, the state gate and the CI emission paths
additionally enforce an **independent baseline**: at the pinned pre-rework
commit `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b` (remote main when
objective 016 began), every existing top-level publication
record/manifest/handoff (`packaging/rc_record.json`, `rc_handoff.md`,
`rc_artifact_record.schema.json`, `release_provenance_manifest.json` and its
schema) and every archived publication record under `packaging/releases/`
must still exist — in the verified head's tree **and** in the working tree —
with byte-identical content, and no new top-level or archived publication
record may have appeared (a new one would be new freeze authority, not
development). Path presence/deletion is part of the law; the working-tree
leg also catches dirty frozen metadata that the input map cannot see
(record/handoff/archive files are derived exclusions). The development
manifest never chooses the freeze authority: the production CLI uses the
pinned repository baseline, and the typed helper argument exists solely so
hermetic test fixtures can model their own explicit baseline.

## CI behavior

- The CI test job runs the state-aware gate after the fresh build: the
  freshly built wheel and sdist must bind to the hashes recorded for the
  current state (frozen manifest in the frozen state, development manifest
  in the development state).
- The Docker build and operator-session jobs emit and source the artifact
  state (`state`, `expected_wheel_sha256`, `qualification_label`,
  `source_commit`) and bind the built wheel to the expected hash; in the
  development state the image is labeled with the deterministic
  development/source qualification label and can never claim RC10
  qualification.
- The Gateway contract job and the actual pulled-historical-image job are
  unchanged: published-source qualification and the pulled-image gate
  continue to validate the immutable RC10 source and exact published
  digest.

## Commands

```bash
# Generate at the current clean source commit (writes the manifest).
python scripts/dev_provenance_manifest.py --generate [--source <40-hex>]

# Verify the current state at HEAD; with --dist, bind freshly built artifacts.
python scripts/dev_provenance_manifest.py --verify [--head <40-hex>] [--dist dist]

# Emit the CI artifact state to a shell-sourceable file (fails closed).
python scripts/dev_provenance_manifest.py --emit-state .ci-artifact-state.env
```

## Non-goals

- No new release candidate, version, tag or registry operation.
- No weakening of source-input inclusion, test collection, security,
  registry, packaging or actual pulled-image validation.
- No rebind, move or deletion of any existing RC10 record, manifest,
  handoff, tag or image to skip a gate.
- Not release-candidate qualification: final-stage immutable release
  identities remain defined by the artifact policy and the CACHE rework
  plan.
