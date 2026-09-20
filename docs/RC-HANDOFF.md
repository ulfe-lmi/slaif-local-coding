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
  identity `0.1.0-rc1` plus the source ALIAS tag
  `sha-<image source commit>` (a mutable tag naming the image source
  commit — NOT a content-addressed identity).
- **The immutable image digest is the content-addressed, authoritative
  identity. Tags are aliases.** A pull must be verified against the
  recorded digest (via `RepoDigests` / the registry manifest digest —
  inspecting the image `.Id` alone is not proof of the manifest digest).
- The machine-readable record is `packaging/rc_record.json`
  (schema `slaif-rc-record-v2`), populated from verified facts during the
  publication round and SELF-CONTAINED. Required facts it carries:
  - product version `0.1.0` and RC identifier `0.1.0-rc1`;
  - the exact **image source commit** (40-hex) the image was built from;
  - the OCI image reference and the **authenticated registry digest**
    (`sha256:<64-hex>`);
  - the OCI tag pair `[0.1.0-rc1, sha-<source commit>]`;
  - the **publishing workflow run head SHA** (the publication is bound to
    the run's exact head, not an unrecorded checkout);
  - the **wheel SHA-256** bound to the image
    (`slaif-local-coding.wheel.sha256` label and in-image artifact);
  - the **dependency lock hash** (`uv.lock` SHA-256);
  - the **frozen Gateway compatibility authority** commit;
  - the **full pinned build environment** (the exact
    `[build-system].requires` pins) and the pinned toolchain (build
    backend, uv, Python scope);
  - the **digest-pinned base images** (uv-provider, build, runtime) and
    the **supported image platform** (`linux/amd64`, built and qualified);
  - the **DIRECT path->sha256 source-input map** (`source_input_hashes`:
    config templates, compose files, packaging/build inputs — carried in
    the record itself, validated against the image source and the
    qualified inputs; drift fails the provenance gate mechanically);
  - supported deployment assumptions (Linux Docker Engine + Compose v2,
    host network mode, private upstream, separate Gateway);
  - `private_registry_auth_required: true`;
  - `cutover_performed: false` and `final_public_release: false`.
- At actual publication a **deterministic human-readable handoff**
  (`packaging/rc_handoff.md`) is rendered from that same machine record:
  it contains the literal verified values and the
  retrieval/verification commands a separate consumer can follow, without
  OAP knowledge or an image rebuild. It is post-publication metadata,
  excluded from every artifact input, so recording a digest never
  requires another image.

## Retrieval (private registry, read-only credentials)

The external GHCR reader scope is `read:packages` (a classic PAT with
package read access for this package — distinct from the Actions YAML
`packages: read` keyword); credentials via password-stdin, bounded
read-only access, no request to make the package public.

```bash
# Bounded read-only credentials via stdin only — never literal:
echo "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "$SLAIF_GHCR_USERNAME" --password-stdin

# Pull by the recorded DIGEST (authoritative identity):
docker pull "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>"

# The tag aliases must resolve to the same registry digest (verify, do not
# trust). Inspecting the image .Id alone is NOT proof of the manifest
# digest — check RepoDigests / the registry manifest digest:
docker pull "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1"
docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1" \
  --format '{{range .RepoDigests}}{{.}}{{end}}'
# must contain ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>
```

The pulled RC is **used, not rebuilt**: the handoff consumer pulls the
frozen digest and does not build the image from source.

## Identity verification

After pulling, verify the frozen identity mechanically:

1. **Digest equality:** the `RepoDigests` of each tag pull contain the
   recorded registry digest, and the image IDs of the digest pull and the
   tag pulls are equal (the registry manifest digest is the authoritative
   check; the image ID equality is a secondary identity fact).
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
   `packaging/rc_record.json` (schema `slaif-rc-record-v2`) and the
   provenance manifest it binds; the record's `source_input_hashes` map
   equals the qualified source tree (verified mechanically by
   `scripts/source_input_map.py --ref <S> --manifest
   packaging/release_provenance_manifest.json`).
5. **Trust boundary:** the record's digest validation is SYNTACTIC — it
   cannot itself authenticate an arbitrary digest. The digest is
   authenticated by the publishing run's registry-API verification, bound
   to the publishing run's exact head SHA, and re-proven on the pulled
   image by the `docker-published` CI job (digest pull, tag->digest
   checks, full OCI label set, in-image wheel hash, signed-ingress
   contract run).

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
