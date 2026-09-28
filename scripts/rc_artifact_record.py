"""RC artifact record generator + deterministic handoff renderer
(order 013-i, C12; order 013-j, J5: self-contained record with the direct
source-input hash map, build-environment pins, base-image identities,
supported platform, publishing-run head SHA, and the rendered
human-readable handoff).

Prepares the machine-readable RC artifact record
(``packaging/rc_record.json``, schema ``slaif-rc-record-v3``) and the
deterministic human-readable handoff (``packaging/rc_handoff.md``). Both
are populated from VERIFIED FACTS during the publication round only:

- the exact image source commit ``S`` the image was built from;
- the OCI registry digest ``D``;
- the publishing workflow run's EXACT head SHA (``GITHUB_SHA``) — a
  publication is bound to the workflow run's head, not to an unrecorded
  checkout;
- the provenance-manifest wheel SHA-256, the dependency-lock (uv.lock)
  SHA-256, and the frozen Gateway compatibility authority commit;
- the FULL pinned build environment (asserted equal to the enforced
  ``[build-system].requires`` pins), the pinned toolchain (backend/uv/
  python), the digest-pinned base images parsed from the Dockerfile, the
  supported image platform, and the DIRECT path->sha256 source-input map
  (config templates, compose files, packaging inputs — carried in the
  record itself, not cross-bound by unrelated wheel/lock/peer facts);
- the explicit real-Codex compatibility qualification facts (order 014-a,
  workstream D): exact client version + binary SHA-256, the closed
  ``standalone-loopback-no-gateway`` topology, the closed VISION/CACHE/
  BOTH arm verdicts, the contextual DIRECT control, and the sanitized
  testing-ledger evidence path (all closed-schema, no prose);
- ``private_registry_auth_required: true``, ``final_public_release:
  false``, ``cutover_performed: false`` (const-pinned in the schema).

TRUST BOUNDARY (order 013-j, J5): the generator's validation is SYNTACTIC.
Validating a digest's shape cannot itself authenticate an arbitrary
digest. Authentication of a real publication comes from three independent
facts bound together: (1) the publishing workflow run's exact head SHA
(``workflow_head_sha``), (2) the AUTHENTICATED registry digest verified by
the publishing run's registry-API steps (the publisher's before/after
verification), and (3) the pulled-image qualification of the
``docker-published`` CI job (digest pull, tag->digest checks, full OCI
label set, in-image wheel hash, signed-ingress contract run). A future
publication therefore requires a real run id and verified facts — never a
fake or unpublished record.

The record and the rendered handoff are post-publication metadata: they are
excluded from every wheel/sdist/image build input (pyproject top-level
exclusions), so recording a digest never requires another image. The
handoff rendering is a PURE function of the machine record: at actual
publication it contains the literal verified values and the
retrieval/verification commands a separate consumer can follow, without
OAP knowledge or an image rebuild.

Safety law: an existing ``packaging/rc_record.json`` (or
``packaging/rc_handoff.md``) is a frozen identity — the generator refuses
to overwrite it unless the freshly built content is byte-identical. No
other partial update is possible.

Usage (publication round only):

    python scripts/rc_artifact_record.py \\
        --source <40-hex image source commit> \\
        --digest sha256:<64-hex authenticated registry digest> \\
        --head-sha <40-hex workflow run head SHA> \\
        --published-at 2026-01-01T00:00:00Z \\
        [--run-id <int>] \\
        [--emit packaging/rc_record.json] \\
        [--emit-handoff packaging/rc_handoff.md]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from release_provenance_manifest import _dockerfile_base_images  # noqa: E402
from source_input_map import map_from_directory  # noqa: E402

MANIFEST_PATH = Path("packaging/release_provenance_manifest.json")
UV_LOCK_PATH = Path("uv.lock")
HANDOFF_PATH = Path("packaging/rc_handoff.md")

RC_IDENTIFIER = "0.1.0-rc3"
PRODUCT_VERSION = "0.1.0"
IMAGE_REFERENCE = "ghcr.io/ulfe-lmi/slaif-local-coding"
PUBLICATION_WORKFLOW = "release-image.yml"
RC_RECORD_SCHEMA = "slaif-rc-record-v3"
# Order 014-a, workstream D: the machine record must carry the real-Codex
# compatibility qualification facts with strict closed-schema validation
# (no unvalidated prose). Topology is the supported standalone loopback
# path: disposable Codex home/repository -> 127.0.0.1:18031 Local Coding
# -> tested Qwen/vLLM endpoint; NO SLAIF API Gateway is in the path.
COMPATIBILITY_TOPOLOGY = "standalone-loopback-no-gateway"
COMPATIBILITY_ARM_NAMES = ("vision", "cache", "both")
COMPATIBILITY_ARM_VERDICTS = ("pass", "blocked")
DIRECT_CONTROL_VERDICTS = ("pass", "not_run")
CLIENT_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_PATH_PATTERN = re.compile(r"^oap/evidence/testing-ledger/[0-9]{3}$")
IMAGE_PLATFORM = "linux/amd64"
DEPLOYMENT_ASSUMPTIONS = (
    "linux-docker-engine-compose-v2;host-network-mode;"
    "private-same-host-upstream;separate-gateway;loopback-default-bind"
)
PUBLISHED_AT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


class RCRecordError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_compatibility(compatibility: object) -> dict[str, object]:
    """Strict closed validation of the compatibility qualification facts
    (order 014-a, workstream D). Every key is required; the arm set is
    exactly the three product arms; verdicts are closed enums; the
    evidence path must be a sanitized testing-ledger directory."""
    expected = {
        "client_version",
        "client_sha256",
        "topology",
        "arm_verdicts",
        "direct_control",
        "evidence_path",
    }
    if not isinstance(compatibility, dict) or set(compatibility) != expected:
        raise RCRecordError(f"compatibility key set drift: expected {sorted(expected)}")
    client_version = compatibility["client_version"]
    if not isinstance(client_version, str) or not client_version.strip():
        raise RCRecordError("compatibility client_version must be a non-empty string")
    client_sha256 = compatibility["client_sha256"]
    if not isinstance(client_sha256, str) or not CLIENT_SHA256_PATTERN.fullmatch(client_sha256):
        raise RCRecordError("compatibility client_sha256 must be 64-hex")
    if compatibility["topology"] != COMPATIBILITY_TOPOLOGY:
        raise RCRecordError("compatibility topology drift (standalone loopback, no Gateway)")
    arms = compatibility["arm_verdicts"]
    if not isinstance(arms, dict) or set(arms) != set(COMPATIBILITY_ARM_NAMES):
        raise RCRecordError(
            "compatibility arm_verdicts must name exactly " + "/".join(COMPATIBILITY_ARM_NAMES)
        )
    for name in COMPATIBILITY_ARM_NAMES:
        if arms[name] not in COMPATIBILITY_ARM_VERDICTS:
            raise RCRecordError(
                f"compatibility arm {name!r} verdict must be one of "
                + "/".join(COMPATIBILITY_ARM_VERDICTS)
            )
    if compatibility["direct_control"] not in DIRECT_CONTROL_VERDICTS:
        raise RCRecordError(
            "compatibility direct_control must be one of " + "/".join(DIRECT_CONTROL_VERDICTS)
        )
    evidence_path = compatibility["evidence_path"]
    if not isinstance(evidence_path, str) or not EVIDENCE_PATH_PATTERN.fullmatch(evidence_path):
        raise RCRecordError("compatibility evidence_path must be oap/evidence/testing-ledger/NNN")
    return {
        "client_version": client_version,
        "client_sha256": client_sha256,
        "topology": COMPATIBILITY_TOPOLOGY,
        "arm_verdicts": {name: arms[name] for name in COMPATIBILITY_ARM_NAMES},
        "direct_control": compatibility["direct_control"],
        "evidence_path": evidence_path,
    }


def build_rc_record(
    repo: Path,
    source: str,
    digest: str,
    head_sha: str,
    published_at: str,
    run_id: int | None,
    compatibility: object,
) -> dict:
    """Build the RC record from verified facts. Pure transformation: no
    network, no registry access, no docker; the caller must supply the
    AUTHENTICATED registry digest of the pushed image, the publishing
    workflow run's head SHA (see the module trust-boundary note), and the
    explicitly qualified real-Codex compatibility facts (order 014-a)."""
    compatibility_facts = _validate_compatibility(compatibility)
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RCRecordError("source commit must be 40-hex")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise RCRecordError("digest must be sha256:<64-hex>")
    if not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise RCRecordError("head_sha (workflow run head) must be 40-hex")
    if not PUBLISHED_AT_PATTERN.fullmatch(published_at):
        raise RCRecordError("published_at must be RFC 3339 UTC (Z)")
    if run_id is not None and not (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    ):
        raise RCRecordError("run_id must be a positive integer or null")

    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    if manifest.get("schema") != "slaif-release-provenance-v5":
        raise RCRecordError("provenance manifest must be schema slaif-release-provenance-v5")
    wheel_sha256 = str(manifest["artifacts"]["wheel"]["sha256"])
    if not re.fullmatch(r"[0-9a-f]{64}", wheel_sha256):
        raise RCRecordError("manifest wheel sha256 is not 64-hex")
    gateway_authority_sha = str(manifest["gateway_peer"]["commit"])
    if not re.fullmatch(r"[0-9a-f]{40}", gateway_authority_sha):
        raise RCRecordError("manifest gateway peer commit is not 40-hex")
    build_environment = dict(manifest["build"]["build_environment"])
    recorded_inputs = {str(k): str(v) for k, v in manifest["source_inputs"].items()}
    # The record must be built from a checkout whose inputs equal the
    # recorded input map (i.e. at S with inputs identical to the qualified
    # source; an ancestor relationship is not sufficient — order 013-j, J4).
    working_inputs = map_from_directory(repo)
    if working_inputs != recorded_inputs:
        missing = sorted(set(recorded_inputs) - set(working_inputs))[:5]
        extra = sorted(set(working_inputs) - set(recorded_inputs))[:5]
        altered = sorted(
            p
            for p in set(recorded_inputs) & set(working_inputs)
            if recorded_inputs[p] != working_inputs[p]
        )[:5]
        raise RCRecordError(
            "working-tree source inputs differ from the manifest's recorded "
            f"input map (missing={missing} extra={extra} altered={altered}); "
            "the record must be built at the qualified source"
        )
    dependency_lock_sha256 = _sha256_file(repo / UV_LOCK_PATH)
    base_images = {
        stage: {"name": fact["name"], "digest": fact["digest"]}
        for stage, fact in _dockerfile_base_images(repo).items()
    }

    return {
        "schema": RC_RECORD_SCHEMA,
        "rc_identifier": RC_IDENTIFIER,
        "product_version": PRODUCT_VERSION,
        "image_source_commit": source,
        "oci_image_reference": IMAGE_REFERENCE,
        "oci_image_digest": digest,
        "oci_tags": [RC_IDENTIFIER, f"sha-{source}"],
        "published_at": published_at,
        "publication_workflow": PUBLICATION_WORKFLOW,
        "publication_workflow_run_id": run_id,
        "workflow_head_sha": head_sha,
        "private_registry_auth_required": True,
        "final_public_release": False,
        "cutover_performed": False,
        "wheel_sha256": wheel_sha256,
        "dependency_lock_sha256": dependency_lock_sha256,
        "gateway_authority_sha": gateway_authority_sha,
        "build_environment": build_environment,
        "build_toolchain": {
            "backend": "hatchling==1.32.0",
            "uv": "0.12.5",
            "python": "3.12",
        },
        "base_images": base_images,
        "image_platform": IMAGE_PLATFORM,
        "source_input_hashes": recorded_inputs,
        "deployment_assumptions": DEPLOYMENT_ASSUMPTIONS,
        "compatibility": compatibility_facts,
    }


def render_handoff(record: dict) -> str:
    """Deterministic human-readable handoff from the machine record ONLY
    (order 013-j, J5): literal verified values plus retrieval and
    verification commands a separate consumer can follow. No OAP knowledge
    and no image rebuild are required or referenced."""
    source = str(record["image_source_commit"])
    digest = str(record["oci_image_digest"])
    reference = str(record["oci_image_reference"])
    tags = list(record["oci_tags"])
    lines: list[str] = []
    lines.append(
        f"# SLAIF Local Coding {record['product_version']} — {record['rc_identifier']} RC handoff"
    )
    lines.append("")
    lines.append(
        "Rendered deterministically from `packaging/rc_record.json` "
        f"(schema `{record['schema']}`). Every value below is a literal "
        "verified value from that machine record. This document covers "
        "artifact retrieval and identity verification only: it is not an "
        "experimental or benchmark procedure, and it authorizes no "
        "production cutover or final release."
    )
    lines.append("")
    lines.append("## Identity (literal verified values)")
    lines.append("")
    lines.append(f"- Product version: `{record['product_version']}`")
    lines.append(f"- RC identifier: `{record['rc_identifier']}`")
    lines.append(f"- Image source commit: `{source}`")
    lines.append(f"- OCI reference: `{reference}`")
    lines.append(f"- OCI digest (authoritative identity): `{digest}`")
    lines.append(
        f"- Tag aliases: `{tags[0]}` and `{tags[1]}` (mutable; the digest is authoritative)"
    )
    lines.append(
        f"- Supported image platform: `{record['image_platform']}` (built and "
        "qualified; other architectures are not qualified)"
    )
    lines.append(f"- Published at (UTC): `{record['published_at']}`")
    lines.append(
        f"- Publication workflow: `{record['publication_workflow']}` "
        f"(run id: {record['publication_workflow_run_id']})"
    )
    lines.append(f"- Publishing run head SHA: `{record['workflow_head_sha']}`")
    lines.append(f"- Wheel SHA-256 bound to the image: `{record['wheel_sha256']}`")
    lines.append(f"- Dependency lock (uv.lock) SHA-256: `{record['dependency_lock_sha256']}`")
    lines.append(f"- Frozen Gateway compatibility authority: `{record['gateway_authority_sha']}`")
    lines.append(
        "- Build environment (enforced pins): "
        + ", ".join(f"{k}=={v}" for k, v in sorted(record["build_environment"].items()))
    )
    lines.append(
        "- Build toolchain: "
        + ", ".join(f"{k} `{v}`" for k, v in sorted(record["build_toolchain"].items()))
    )
    for stage in sorted(record["base_images"]):
        fact = record["base_images"][stage]
        lines.append(f"- Base image ({stage}): `{fact['name']}@{fact['digest']}`")
    lines.append(f"- Private registry auth required: `{record['private_registry_auth_required']}`")
    lines.append(
        f"- Final public release: `{record['final_public_release']}` (remains false; "
        "a final release is a separate later decision)"
    )
    lines.append(f"- Cutover performed: `{record['cutover_performed']}` (remains false)")
    lines.append("")
    compat = record["compatibility"]
    arms = compat["arm_verdicts"]
    lines.append("## Real-Codex compatibility qualification (literal verified values)")
    lines.append("")
    lines.append(
        f"- Qualified client: Codex CLI `{compat['client_version']}` "
        f"(binary SHA-256 `{compat['client_sha256']}`)"
    )
    lines.append(
        f"- Topology: `{compat['topology']}` — standalone loopback Local "
        "Coding qualification requires NO SLAIF API Gateway (gateway "
        "ingress disabled; no signed Gateway headers invented)"
    )
    lines.append(
        f"- Product arms: VISION `{arms['vision']}`, CACHE `{arms['cache']}`, "
        f"BOTH `{arms['both']}` (bounded genuine Codex sessions with local "
        "tool interaction against the repaired artifact-bound adapter and "
        "the designated backend; a `blocked` arm is a truthfully recorded "
        "blocker, never a pass)"
    )
    lines.append(f"- DIRECT control: `{compat['direct_control']}` (contextual, never a substitute)")
    lines.append(
        f"- Sanitized evidence: `{compat['evidence_path']}` (append-only, "
        "content-free, manifest-bound)"
    )
    lines.append(
        "- No benchmark ran; final public release remains false; the package "
        "remains private; protected cutover remains false."
    )
    lines.append("")
    lines.append("## Source input hashes (path -> sha256)")
    lines.append("")
    lines.append(
        "The exact configuration/compose/packaging/build inputs the record was validated against:"
    )
    lines.append("")
    lines.append("```text")
    for path in sorted(record["source_input_hashes"]):
        lines.append(f"{record['source_input_hashes'][path]}  {path}")
    lines.append("```")
    lines.append("")
    lines.append("## Retrieval (private registry, read-only credentials)")
    lines.append("")
    lines.append(
        "External GHCR reader scope: `read:packages` (a classic PAT with package "
        "read access for this package — distinct from the Actions YAML "
        "`packages: read` keyword). Credentials via stdin only, never literal:"
    )
    lines.append("")
    lines.append(
        f"Exact-source retrieval (Compose/config): "
        f"https://github.com/ulfe-lmi/slaif-local-coding/blob/{source}/INSTALL.md — "
        "retrieve the Compose and configuration files it references at this SAME "
        "literal image source commit (their hashes are the record's "
        "`source_input_hashes`, mechanically verified)."
    )
    lines.append("")
    lines.append("```bash")
    lines.append(
        'echo "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "$SLAIF_GHCR_USERNAME" --password-stdin'
    )
    lines.append(f'docker pull "{reference}@{digest}"')
    lines.append("```")
    lines.append("")
    lines.append(
        "The tag aliases must resolve to the SAME registry digest (verify, do "
        "not trust; inspecting the image `.Id` alone is NOT proof of the "
        "manifest digest — check `RepoDigests` / the registry manifest "
        "digest):"
    )
    lines.append("")
    lines.append("```bash")
    lines.append(f'docker pull "{reference}:{tags[0]}"')
    lines.append(
        f'docker image inspect "{reference}:{tags[0]}" '
        "--format '{{range .RepoDigests}}{{.}}{{end}}'"
    )
    lines.append(f"# must contain {reference}@{digest}")
    # f-string: doubled braces escape to the literal Go-template braces.
    lines.append(
        f"docker image inspect \"{reference}@{digest}\" --format '{{{{json .Config.Labels}}}}'"
    )
    lines.append("```")
    lines.append("")
    lines.append("## Identity verification")
    lines.append("")
    lines.append(
        f"1. `RepoDigests` of each tag pull contains `{reference}@{digest}` "
        "(the registry manifest digest, not just the image `.Id`)."
    )
    lines.append(
        f"2. OCI labels on `{digest}`: "
        f"`org.opencontainers.image.revision` == `{source}`; "
        f"`org.opencontainers.image.version` and "
        f"`slaif-local-coding.package.version` == `{record['product_version']}`; "
        f"`slaif-local-coding.wheel.sha256` == `{record['wheel_sha256']}`; "
        f"`slaif-local-coding.gateway.peer.sha` == "
        f"`{record['gateway_authority_sha']}`; "
        "`slaif-local-coding.topology.mode` == "
        "`linux-docker-host-network;loopback-default;"
        "lan-visible-only-with-full-signed-ingress`; "
        "`slaif-local-coding.qualification` == "
        "`rc-candidate-0.1.0-rc3; private; not final release`."
    )
    lines.append(
        "3. The in-image retained wheel artifact "
        "(`/opt/slaif/artifacts/slaif_local_coding-0.1.0-py3-none-any.whl`) "
        f"hashes to `{record['wheel_sha256']}`."
    )
    lines.append(
        "4. Every fact above matches `packaging/rc_record.json`; the source "
        "input hashes in that record equal the qualified source tree "
        "(mechanically verified by "
        "`scripts/source_input_map.py --ref <S> "
        "--manifest packaging/release_provenance_manifest.json`)."
    )
    lines.append("")
    lines.append("## What this handoff is NOT")
    lines.append("")
    lines.append(
        "- Not a benchmark protocol: no tasks, judges, controllers, "
        "run ledgers, or instrumentation."
    )
    lines.append(
        "- Not a cutover: `cutover_performed` remains `false`; the live "
        "cutover is a separate human-authorized act."
    )
    lines.append(
        "- Not a final release: `final_public_release` remains `false`; "
        "promotion of the SAME tested digest can happen later without "
        "rebuilding or changing embedded labels, but only by explicit "
        "later decision."
    )
    lines.append(
        "- Not permission to reuse the historical private `0.1.0` tag: that "
        "tag is legacy output that was never published to users and is not "
        "the RC target."
    )
    lines.append("")
    return "\n".join(lines) + "\n"


def _emit_frozen(path: Path, payload: str, label: str) -> str:
    """Atomically write; refuse to overwrite a frozen identity that is not
    byte-identical."""
    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        if existing != payload:
            raise RCRecordError(
                f"refusing to overwrite frozen {label} {path}: the freshly "
                "built content differs; an already frozen identity must not "
                "be rewritten"
            )
        return "unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return "written"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="40-hex image source commit")
    parser.add_argument(
        "--digest", required=True, help="authenticated registry digest sha256:<64-hex>"
    )
    parser.add_argument("--head-sha", required=True, help="40-hex publishing workflow run head SHA")
    parser.add_argument("--published-at", required=True, help="RFC 3339 UTC timestamp")
    parser.add_argument("--run-id", type=int, default=None, help="workflow run id (optional)")
    parser.add_argument(
        "--client-version",
        required=True,
        help="exact qualified Codex CLI version (e.g. 0.149.0)",
    )
    parser.add_argument(
        "--client-sha256",
        required=True,
        help="SHA-256 (64-hex) of the exact qualified Codex CLI binary",
    )
    parser.add_argument(
        "--arm-verdict",
        dest="arm_verdicts",
        action="append",
        required=True,
        metavar="NAME=VERDICT",
        help=(
            "required-arm verdict; repeat exactly once for each of "
            "vision/cache/both; VERDICT is pass or blocked"
        ),
    )
    parser.add_argument(
        "--direct-control",
        required=True,
        choices=sorted(DIRECT_CONTROL_VERDICTS),
        help="contextual DIRECT control result (pass or not_run)",
    )
    parser.add_argument(
        "--evidence-path",
        required=True,
        help="sanitized testing-ledger directory, e.g. oap/evidence/testing-ledger/002",
    )
    parser.add_argument("--emit", type=Path, default=Path("packaging/rc_record.json"))
    parser.add_argument("--emit-handoff", type=Path, default=HANDOFF_PATH)
    args = parser.parse_args()

    arms: dict[str, str] = {}
    for entry in args.arm_verdicts:
        name, sep, verdict = entry.partition("=")
        if (
            not sep
            or name not in COMPATIBILITY_ARM_NAMES
            or verdict not in COMPATIBILITY_ARM_VERDICTS
        ):
            parser.error(
                f"invalid --arm-verdict {entry!r}: expected NAME=VERDICT with NAME in "
                + "/".join(COMPATIBILITY_ARM_NAMES)
                + " and VERDICT in "
                + "/".join(COMPATIBILITY_ARM_VERDICTS)
            )
        if name in arms:
            parser.error(f"duplicate --arm-verdict for {name!r}")
        arms[name] = verdict
    if set(arms) != set(COMPATIBILITY_ARM_NAMES):
        missing = sorted(set(COMPATIBILITY_ARM_NAMES) - set(arms))
        parser.error("missing required --arm-verdict for: " + ", ".join(missing))

    compatibility = {
        "client_version": args.client_version,
        "client_sha256": args.client_sha256,
        "topology": COMPATIBILITY_TOPOLOGY,
        "arm_verdicts": arms,
        "direct_control": args.direct_control,
        "evidence_path": args.evidence_path,
    }

    repo = Path(__file__).resolve().parents[1]
    record = build_rc_record(
        repo,
        args.source,
        args.digest,
        args.head_sha,
        args.published_at,
        args.run_id,
        compatibility,
    )
    state = _emit_frozen(
        args.emit.resolve(), json.dumps(record, indent=2, sort_keys=True) + "\n", "RC record"
    )
    print(f"rc record {state}: {args.emit}")
    state = _emit_frozen(args.emit_handoff.resolve(), render_handoff(record), "RC handoff")
    print(f"rc handoff {state}: {args.emit_handoff}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
