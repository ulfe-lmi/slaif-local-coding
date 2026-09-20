# Release-candidate (RC) handoff: retrieval and identity verification

This document is the **human-readable handoff** for the SLAIF Local Coding
0.1.0 release candidate. It covers **artifact retrieval and identity
verification only**. It is not an experimental or benchmark procedure, and
it authorizes no production cutover or final release.

## What the RC is

- Product: SLAIF Local Coding, version `0.1.0`, state **release
  candidate** (`final_public_release: false`). A final public release is a
  separate later human decision.
- The RC is published to the **private** GHCR package
  `ghcr.io/ulfe-lmi/slaif-local-coding` under the explicit candidate
  identity `0.1.0-rc1` plus the content-addressed source tag
  `sha-<image source commit>`.
- **The immutable image digest is the authoritative identity. Tags are
  aliases.** A pull must be verified against the recorded digest.
- The machine-readable record is `packaging/rc_record.json`
  (schema `slaif-rc-record-v1`), populated from verified facts during the
  publication round. Required facts it carries:
  - product version `0.1.0` and RC identifier `0.1.0-rc1`;
  - the exact **image source commit** (40-hex) the image was built from;
  - the OCI image reference and the **registry digest**
    (`sha256:<64-hex>`);
  - the OCI tag pair `[0.1.0-rc1, sha-<source commit>]`;
  - the **wheel SHA-256** bound to the image
    (`slaif-local-coding.wheel.sha256` label and in-image artifact);
  - the relevant **pinned tools** (build backend, uv, Python identity);
  - the **dependency lock hash** (`uv.lock` SHA-256);
  - the **frozen Gateway compatibility authority** commit;
  - the **config/template hashes** (in the provenance manifest `templates`
    section, cross-bound by the record's `wheel_sha256`,
    `dependency_lock_sha256`, and `gateway_authority_sha` facts; drift
    fails the provenance gate mechanically);
  - supported deployment assumptions (Linux Docker Engine + Compose v2,
    host network mode, private upstream, separate Gateway);
  - `private_registry_auth_required: true`;
  - `cutover_performed: false` and `final_public_release: false`.

## Retrieval (private registry, read-only credentials)

```bash
# Bounded read-only credentials via stdin only — never literal:
echo "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "$SLAIF_GHCR_USERNAME" --password-stdin

# Pull by the recorded DIGEST (authoritative identity):
docker pull "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>"

# The tag aliases resolve to the same digest (verify, do not trust):
docker pull "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1"
docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1" --format '{{.Id}}'
```

The pulled RC is **used, not rebuilt**: the handoff consumer pulls the
frozen digest and does not build the image from source.

## Identity verification

After pulling, verify the frozen identity mechanically:

1. **Digest equality:** the image ID of the digest pull equals the image
   IDs of both tag pulls.
2. **OCI labels** (on the digest-pulled image):
   - `org.opencontainers.image.revision` == the recorded image source
     commit;
   - `org.opencontainers.image.version` and
     `slaif-local-coding.package.version` == `0.1.0`;
   - `slaif-local-coding.wheel.sha256` == the recorded wheel SHA-256;
   - `slaif-local-coding.gateway.peer.sha` == the frozen Gateway
     compatibility authority;
   - `slaif-local-coding.topology.mode` == the supported topology label;
   - `slaif-local-coding.qualification` == the RC candidate label
     (private, not final release).
3. **In-image wheel provenance:** the retained wheel artifact inside the
   image hashes to the recorded wheel SHA-256.
4. **Record cross-check:** every fact in step 2 matches
   `packaging/rc_record.json` and the provenance manifest it binds.

## What this handoff is NOT

- Not a benchmark protocol: no tasks, judges, controllers, run ledgers, or
  instrumentation are part of this handoff; any benchmark is entirely
  external.
- Not a cutover: `cutover_performed` remains `false`; the live cutover is a
  separate human-authorized act (see RELEASE-CUTOVER-RUNBOOK.md).
- Not a final release: `final_public_release` remains `false`; promotion
  of the SAME tested digest can happen later without rebuilding or
  changing embedded labels, but only by explicit later decision.
- Not permission to reuse the historical private `0.1.0` tag: that tag is
  legacy Objective-013 output that was never published to users and is not
  the RC benchmark target.

## Build-time candidate identity vs later human approval

The candidate identity (`0.1.0-rc1`, its labels, and the recorded digest)
is fixed at build time from the exact recorded source commit. Later human
approval (final release) does not rebuild or relabel the tested image:
promotion references the **same** digest. The record fields
`final_public_release` and `cutover_performed` stay `false` in the RC
record and change only in later, separately authorized records.
