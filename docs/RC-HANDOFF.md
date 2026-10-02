# Release-candidate handoff

Use the immutable OCI digest and matching source/configuration files recorded
for the candidate. The consumer pulls the image; it does not rebuild it.
This guide covers retrieval and identity verification only.

## Find the artifact record

After publication, `packaging/rc_record.json` is the machine-readable record and
`packaging/rc_handoff.md` is its deterministic human-readable view. Both contain
the actual values; a candidate without these records and a verified digest is
not ready for handoff. Their schema is `slaif-rc-record-v3`.

The record includes:

| Identity | Recorded facts |
| --- | --- |
| Product | Version `0.1.0`, explicit RC identifier such as `0.1.0-rc10`. |
| Source | Exact 40-hex image source commit and publication-run head SHA. |
| Image | Full OCI reference, authenticated `sha256` digest and tag aliases. |
| Package | Exact wheel SHA-256 and dependency-lock hash. |
| Build | Pinned backend and complete build environment, uv/Python scope and base-image digests. |
| Compatibility | Frozen Gateway revision and qualified platform `linux/amd64`. |
| Configuration | Direct path-to-SHA-256 source-input map, including templates and Compose files. |
| Deployment | Linux Docker Engine + Compose v2, host networking, private upstream and separate Gateway. |
| Approval | Private-registry authentication requirement, `final_public_release: false`, `cutover_performed: false`. |

The image-source commit and later record commit are different: recording the
resulting digest must not change the artifact. The provenance gate verifies
identical artifact inputs between them. See [artifact policy](RELEASE-ARTIFACT-POLICY.md).

## Retrieve by digest

Use a bounded GHCR reader credential with `read:packages` and access to this
private package. That credential scope is distinct from the Actions YAML
permission `packages: read`. Public visibility is not required.

Replace the placeholder with the literal digest from the selected record:

```bash
printf '%s' "$SLAIF_GHCR_TOKEN" | docker login ghcr.io \
  -u "$SLAIF_GHCR_USERNAME" --password-stdin
docker pull "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>"
docker image inspect \
  "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>" \
  --format '{{json .RepoDigests}}'
```

`RepoDigests` must contain the recorded full reference. If you also pull a tag,
verify it resolves to that same registry digest. An image `.Id` is a different
identity and does not substitute for the manifest digest. Tags are mutable aliases.

Obtain Compose and configuration templates from the **recorded image-source
commit**, following [INSTALL.md](../INSTALL.md). Do not fetch files from a moving
branch and assume they match. Compare their SHA-256 values with
`source_input_hashes` before preparing site-specific configuration.

## Verify the image

Inspect the pulled image's labels and compare with the record:

- `org.opencontainers.image.revision`: exact image-source commit.
- `org.opencontainers.image.version` and `slaif-local-coding.package.version`: `0.1.0`.
- `slaif-local-coding.wheel.sha256`: recorded wheel hash.
- `slaif-local-coding.gateway.peer.sha`: frozen Gateway authority.
- `slaif-local-coding.topology.mode` and `slaif-local-coding.qualification`:
  the recorded topology and RC qualification labels.

Verify the actual image platform and retained wheel hash as well. The publishing
workflow authenticates registry facts; the fresh `docker-published` CI run checks
the actual pulled digest, labels, runtime dependencies and deployment behavior.
The record's schema can validate digest syntax, but cannot authenticate an
arbitrary digest by itself.

## Approval and previous candidates

An RC is not a final public release or a protected-host cutover. Benchmark
execution belongs to the independent external agent/VM and is not performed or
defined by this repository. A later human approval may promote the **same tested
digest** without rebuilding; the original RC record remains immutable.

The [RC1 record](../packaging/releases/0.1.0-rc1/rc_record.json),
[handoff](../packaging/releases/0.1.0-rc1/rc_handoff.md) and
[provenance](../packaging/releases/0.1.0-rc1/release_provenance_manifest.json)
remain byte-identical. RC1 predates the governance parser security
correction and is not a handoff target. The archived [RC2
record](../packaging/releases/0.1.0-rc2/rc_record.json),
[handoff](../packaging/releases/0.1.0-rc2/rc_handoff.md) and
[provenance](../packaging/releases/0.1.0-rc2/release_provenance_manifest.json)
also remain byte-identical; RC2 failed external real-Codex 0.149.0
qualification (immutable testing ledger 001) and is not a handoff target
either. The archived [RC3
record](../packaging/releases/0.1.0-rc3/rc_record.json),
[handoff](../packaging/releases/0.1.0-rc3/rc_handoff.md) and
[provenance](../packaging/releases/0.1.0-rc3/release_provenance_manifest.json)
also remain byte-identical; RC3's scoped real-Codex smoke passed (immutable
testing ledger 002) but the candidate was not accepted: its publication
preceded a successful aggregate security gate, and later review found the
record-schema and qualification-harness defects repaired in RC4. RC4
(`0.1.0-rc4`) qualified in scope (immutable testing ledger 003) but was
not accepted: the committed provenance bound a later source-input map to
the earlier immutable image source; its record set is archived
byte-identical under `packaging/releases/0.1.0-rc4/`. RC5
(`0.1.0-rc5`) passed its product repair, its scoped genuine-Codex
qualification (immutable testing ledger 004), and its pulled-image
qualification, but was not accepted: a mandatory record-present gate
required a tracked source correction after the immutable candidate
freeze; its record set is archived byte-identical under
`packaging/releases/0.1.0-rc5/`. The 014-d RC6 attempt was abandoned
before any push, tag, or publication, so no RC6 identity exists. The
RC7 record set is archived byte-identical under
`packaging/releases/0.1.0-rc7/`; the RC7 aliases
(`0.1.0-rc7`, `sha-ae627131...`) remain occupied and immutable. The RC8 record set is
archived byte-identical under `packaging/releases/0.1.0-rc8/`; the
RC8 aliases (`0.1.0-rc8`, `sha-718fff30...`) remain occupied and
immutable. RC8 qualified in scope (immutable testing ledger 006) and
was published as a private candidate — it repairs the independently
verified product defects P01 (upstream HTTP-error cause discard, now
a bounded private classification) and P02 (compiler truncation
collapse into invalid output, now a typed truncation with bounded
adaptive allowance and the `compiler-v3` behavior version) on top of
the RC7 fail-closed record-present machinery, without any claim that
Local Coding caused the rejected requests or task mistakes — but was
rejected as the FINAL Objective-015 handoff candidate solely because
its frozen read-only CI registry baseline (a member of the frozen
source-input map, immutable after publication) omitted the archived
RC7 alias pair. RC9 (`0.1.0-rc9`) carried that correction (every
archived RC alias pair digest-asserted in the read-only baseline,
with a deterministic regression and the intentional RC6 absence
preserved), qualified in scope (immutable testing ledger 007), and
was published as a private candidate — but was rejected as the FINAL
Objective-015 handoff candidate solely because its frozen historical
replay test was defective (the regression's fallback parser passed
the `tags =` assignment statement to `ast.literal_eval`, so the
015-a frozen-source replay died with `SyntaxError` before the alias
comparison and the claimed RC7-omission failure was never
mechanically demonstrated). Its record set is archived byte-identical
under `packaging/releases/0.1.0-rc9/`, and its aliases remain
occupied and immutable. The current candidate is RC10
(`0.1.0-rc10`), the collision-safe successor carrying the corrected
regression (the fallback parser parses the tuple expression and
fails closed on malformed, ambiguous, or non-string content; the
corrected replay reaches the alias comparison on the 015-a frozen
source and reports the exact RC7 omission). Each candidate has a separate source, wheel
and digest. Legacy private `0.1.0` tags are not handoff targets.
