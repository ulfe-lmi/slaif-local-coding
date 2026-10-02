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
- the DERIVED real-Codex compatibility qualification facts (orders
  014-a/014-b): one manifest-verified, closed-schema facts file from the
  append-only testing ledger is the single source — the ledger's
  ``MANIFEST.sha256`` must cover exactly the ledger directory with
  matching hashes, the facts must be the gate's closed v2 record, the
  overall verdict and every required product arm must be PASS, the
  retained qualified client identity must match, the protected state
  must be unchanged, the disposable state removed, and the tested wheel
  must equal the candidate provenance manifest's wheel. Any tampering,
  missing field, mismatched wheel/client/arm, or BLOCKED result fails
  closed. No independent manual verdict assertions exist;
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

SOURCE-REF BINDING (order 014-c, workstream B — the RC4 defect, closed):
the record's source identity is bound to the LITERAL supplied 40-hex
``source`` commit, which must be the exact publication workflow head,
before anything is written. The builder computes the input map of that
commit with the repository's ref-based map implementation and requires,
fail-closed with sanitized exact classes:

- the source ref exists and is reachable from the current checkout;
- the source-ref map equals the committed provenance manifest map;
- the current checkout map equals that same map (the input map policy
  already excludes derived metadata and the OAP transcript);
- ``source_input_hashes`` is exactly the source-ref map;
- the dependency-lock and base-image facts are read FROM the source ref
  (``git show <source>:uv.lock`` / ``<source>:Dockerfile``), never from a
  later working tree.

A valid ancestor or a byte-identical wheel is insufficient: any altered
test, doc, schema, config, workflow, packaging, or sdist input after the
source freeze fails the builder. ``workflow_head_sha`` must equal
``image_source_commit`` (one qualified source boundary).

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
        --qualification-facts \
            oap/evidence/testing-ledger/NNN/real-codex-rc8-qualification.json \
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
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_codex_rc_qualification import validate_facts_record  # noqa: E402
from release_provenance_manifest import _dockerfile_base_images_text  # noqa: E402
from source_input_map import map_from_directory, map_from_git_commit  # noqa: E402

MANIFEST_PATH = Path("packaging/release_provenance_manifest.json")
HANDOFF_PATH = Path("packaging/rc_handoff.md")

# Order 014-e, workstream C: RC7 supersedes the rejected RC5 (RC5's
# product repair, scoped real-Codex qualification per immutable ledger
# 004, and pulled-image qualification passed, but a mandatory
# record-present gate required a tracked source correction after the
# immutable candidate freeze; the RC5 identity is occupied and immutable,
# archived under packaging/releases/0.1.0-rc5/); order 015-a,
# workstream D: RC8 supersedes RC7 (RC7's product state, scoped
# real-Codex qualification per immutable ledger 005, and pulled-image
# qualification passed; the independently verified product defects P01
# upstream-error-cause discard and P02 compiler-truncation collapse are
# repaired in RC8 without any claim that Local Coding caused the RC7-era
# rejected requests; the RC7 identity is occupied and immutable, archived
# under packaging/releases/0.1.0-rc7/). The 014-d RC6 attempt was
# abandoned before any push, tag, or publication: no RC6 identity exists
# and none may ever be created or reserved.
RC_IDENTIFIER = "0.1.0-rc8"
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
# Order 014-b, workstream B.3: the contextual DIRECT control may be a
# truthfully recorded blocker; it never blocks the record on its own.
DIRECT_CONTROL_VERDICTS = ("pass", "blocked", "not_run")
CLIENT_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_PATH_PATTERN = re.compile(r"^oap/evidence/testing-ledger/[0-9]{3}$")
# Order 014-b, workstream B.3: the single manifest-verified facts file the
# compatibility section is DERIVED from (exact closed path: a three-digit
# ledger number, the RC8 gate output name).
QUALIFICATION_FACTS_PATTERN = re.compile(
    r"^oap/evidence/testing-ledger/[0-9]{3}/real-codex-rc8-qualification\.json$"
)
# sha256sum-format ledger manifest line: 64-hex digest, two spaces, path.
LEDGER_MANIFEST_LINE = re.compile(r"^([0-9a-f]{64})  (\S.*)$")
# Order 014-b, workstream D: the retained qualified client is the exact
# Codex CLI 0.149.0 standalone release binary; the facts must match it.
QUALIFIED_CLIENT_VERSION = "0.149.0"
QUALIFIED_CLIENT_SHA256 = "bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827"
QUALIFICATION_TOPOLOGY = (
    "disposable-codex-home;loopback-adapter;port-18031;existing-backend;gateway-ingress-disabled"
)
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


def _git(repo: Path, *args: str) -> str:
    """Run a read-only git command; sanitized exact-class failure (no
    stderr content in the message)."""
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if proc.returncode != 0:
        raise RCRecordError(f"git read-only command failed: {' '.join(args[:3])} (fail closed)")
    return proc.stdout.decode().strip()


def _git_blob(repo: Path, commit: str, path: str) -> bytes:
    """Read one blob at a literal commit (source-ref fact binding,
    order 014-c, workstream B.3). Missing/unreadable fails closed."""
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True)
    if proc.returncode != 0:
        raise RCRecordError(f"source ref does not carry readable blob {path!r} (fail closed)")
    return proc.stdout


def verify_source_ref_binding(
    repo: Path,
    source: str,
    head_sha: str,
    recorded_inputs: dict[str, str],
) -> dict[str, str]:
    """Order 014-c, workstream B: fail-closed source-ref binding.

    The literal supplied 40-hex ``source`` commit is the record's only
    source identity. BEFORE anything is written, the builder proves:

    1. the publication workflow head IS the exact source ref
       (``head_sha == source``) — ``image_source_commit`` and
       ``workflow_head_sha`` name one qualified source boundary;
    2. the source ref exists in this repository;
    3. the source ref is reachable from the current checkout (the
       publication head is never on a lost branch);
    4. the source-ref input map (computed with the repository's
       ref-based map implementation) equals the committed provenance
       manifest's recorded map;
    5. the current checkout's input map equals that same map — the
       input-map policy already excludes derived metadata
       (record/handoff/manifest) and the OAP transcript, so only
       ALLOWED derived differences can exist in the tree.

    A valid ancestor or a byte-identical wheel is insufficient: any
    altered test, doc, schema, config, workflow, packaging input, sdist
    input, or other mapped path after the source freeze fails the
    builder with a sanitized exact class. Returns the proven source-ref
    map (which the record carries as ``source_input_hashes``).
    """
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RCRecordError("source ref must be 40-hex (fail closed)")
    if source != head_sha:
        raise RCRecordError(
            "workflow head is not the exact supplied source ref (fail closed): "
            "image_source_commit and workflow_head_sha must identify the same "
            "qualified source boundary"
        )
    if (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", source], capture_output=True
        ).returncode
        != 0
    ):
        raise RCRecordError("supplied source ref does not exist (fail closed)")
    head = _git(repo, "rev-parse", "HEAD")
    if head != source:
        if (
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "merge-base",
                    "--is-ancestor",
                    source,
                    head,
                ],
                capture_output=True,
            ).returncode
            != 0
        ):
            raise RCRecordError(
                "source ref is not reachable from the current checkout (fail "
                "closed): the publication head must be an ancestor of HEAD"
            )
    source_ref_map = map_from_git_commit(repo, source)
    if source_ref_map != recorded_inputs:
        missing = sorted(set(recorded_inputs) - set(source_ref_map))[:5]
        extra = sorted(set(source_ref_map) - set(recorded_inputs))[:5]
        altered = sorted(
            p
            for p in set(recorded_inputs) & set(source_ref_map)
            if recorded_inputs[p] != source_ref_map[p]
        )[:5]
        raise RCRecordError(
            "source-ref input map differs from the committed manifest map "
            f"(missing={missing} extra={extra} altered={altered}); the record's "
            "named image source does not carry the recorded source inputs "
            "(fail closed)"
        )
    working_map = map_from_directory(repo)
    if working_map != source_ref_map:
        missing = sorted(set(source_ref_map) - set(working_map))[:5]
        extra = sorted(set(working_map) - set(source_ref_map))[:5]
        altered = sorted(
            p for p in set(source_ref_map) & set(working_map) if source_ref_map[p] != working_map[p]
        )[:5]
        raise RCRecordError(
            "current checkout input map differs from the source-ref map "
            f"(missing={missing} extra={extra} altered={altered}); a mapped "
            "input changed after the source freeze (fail closed)"
        )
    return source_ref_map


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


def _verify_ledger_manifest(repo: Path, ledger_dir: Path) -> None:
    """Verify the ledger's ``MANIFEST.sha256`` (fail closed).

    The manifest is in sha256sum format (64-hex digest, two spaces,
    repo-relative path) and must cover EXACTLY the regular files present
    in the ledger directory, excluding the manifest itself (a manifest
    cannot contain its own hash — the same convention ledgers 001/002
    use). Every recorded hash must match the file content, including the
    facts file. Extra files, missing entries, duplicate entries, or
    malformed lines are tampering and fail the derivation closed."""
    manifest = ledger_dir / "MANIFEST.sha256"
    if not manifest.is_file():
        raise RCRecordError("ledger MANIFEST.sha256 missing (fail closed)")
    recorded: dict[str, str] = {}
    lines = manifest.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise RCRecordError("ledger manifest is empty (fail closed)")
    for line_no, line in enumerate(lines, 1):
        match = LEDGER_MANIFEST_LINE.fullmatch(line)
        if match is None:
            raise RCRecordError(
                f"ledger manifest line {line_no} is not sha256sum format (fail closed)"
            )
        digest, rel = match.group(1), match.group(2)
        if rel in recorded:
            raise RCRecordError(f"ledger manifest duplicates {rel!r} (fail closed)")
        recorded[rel] = digest
    present: dict[str, str] = {}
    for path in sorted(ledger_dir.rglob("*")):
        if path.is_file():
            if path == manifest:
                continue
            rel = path.relative_to(repo).as_posix()
            if rel in present:
                raise RCRecordError(f"ledger file collision for {rel!r} (fail closed)")
            present[rel] = _sha256_file(path)
        elif path.is_dir():
            raise RCRecordError(
                f"ledger contains a subdirectory "
                f"{path.relative_to(ledger_dir).as_posix()!r} (fail closed)"
            )
    missing = sorted(set(recorded) - set(present))
    extra = sorted(set(present) - set(recorded))
    if missing or extra:
        raise RCRecordError(
            "ledger manifest does not cover exactly the ledger directory "
            f"(missing={missing[:3]} extra={extra[:3]}) (fail closed)"
        )
    for rel, digest in sorted(recorded.items()):
        if present[rel] != digest:
            raise RCRecordError(f"ledger manifest hash mismatch for {rel!r} (fail closed)")


def derive_compatibility(repo: Path, facts_rel: str) -> dict[str, object]:
    """Derive the compatibility section from ONE manifest-verified,
    closed-schema real-Codex facts file (order 014-b, workstream B.3).

    Every mechanical check fails closed; the returned dictionary is then
    re-validated by ``_validate_compatibility`` before it enters the
    record. Nothing is accepted from independent CLI assertions."""
    if not isinstance(facts_rel, str) or QUALIFICATION_FACTS_PATTERN.fullmatch(facts_rel) is None:
        raise RCRecordError(
            "qualification facts path must match "
            "oap/evidence/testing-ledger/NNN/real-codex-rc8-qualification.json"
        )
    ledger_dir = repo / Path(facts_rel).parent
    if not ledger_dir.is_dir():
        raise RCRecordError("qualification ledger directory missing (fail closed)")
    _verify_ledger_manifest(repo, ledger_dir)
    facts_path = repo / facts_rel
    if not facts_path.is_file():
        raise RCRecordError("qualification facts file missing (fail closed)")
    try:
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RCRecordError(
            f"qualification facts unreadable ({type(exc).__name__}) (fail closed)"
        ) from None
    try:
        validate_facts_record(facts)
    except Exception as exc:
        raise RCRecordError(
            f"qualification facts fail the gate's closed schema ({exc}) (fail closed)"
        ) from None
    if facts["verdict"] != "PASS":
        raise RCRecordError("qualification overall verdict is not PASS (fail closed)")
    if facts["protected_state_unchanged"] is not True:
        raise RCRecordError("protected state changed (fail closed)")
    if facts["disposable_state_removed"] is not True:
        raise RCRecordError("disposable state not removed (fail closed)")
    if facts["topology"] != QUALIFICATION_TOPOLOGY:
        raise RCRecordError(
            "qualification topology is not the supported loopback no-gateway form (fail closed)"
        )
    client = facts["client"]
    if client["version"] != QUALIFIED_CLIENT_VERSION or client["sha256"] != QUALIFIED_CLIENT_SHA256:
        raise RCRecordError(
            "qualification client identity is not the retained qualified client (fail closed)"
        )
    arms = facts["arms"]
    for arm in ("VISION", "CACHE", "BOTH"):
        arm_facts = arms.get(arm)
        if not isinstance(arm_facts, dict) or arm_facts.get("verdict") != "PASS":
            raise RCRecordError(f"required product arm {arm} did not PASS (fail closed)")
    wheel = facts["wheel"]
    if wheel["binding"] != "equal":
        raise RCRecordError("qualification wheel binding is not equal (fail closed)")
    try:
        manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RCRecordError(
            f"provenance manifest unreadable ({type(exc).__name__}) (fail closed)"
        ) from None
    manifest_wheel = str(manifest.get("artifacts", {}).get("wheel", {}).get("sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_wheel):
        raise RCRecordError("provenance manifest wheel sha256 missing (fail closed)")
    if wheel["sha256"] != manifest_wheel:
        raise RCRecordError(
            "qualification wheel does not equal the candidate manifest wheel (fail closed)"
        )
    direct = arms.get("DIRECT")
    if not isinstance(direct, dict):
        direct_control = "not_run"
    elif direct.get("verdict") == "PASS":
        direct_control = "pass"
    else:
        direct_control = "blocked"
    return {
        "client_version": client["version"],
        "client_sha256": client["sha256"],
        "topology": COMPATIBILITY_TOPOLOGY,
        "arm_verdicts": {
            "vision": "pass" if arms["VISION"]["verdict"] == "PASS" else "blocked",
            "cache": "pass" if arms["CACHE"]["verdict"] == "PASS" else "blocked",
            "both": "pass" if arms["BOTH"]["verdict"] == "PASS" else "blocked",
        },
        "direct_control": direct_control,
        "evidence_path": Path(facts_rel).parent.as_posix(),
    }


def build_rc_record(
    repo: Path,
    source: str,
    digest: str,
    head_sha: str,
    published_at: str,
    run_id: int | None,
    qualification_facts: str,
) -> dict:
    """Build the RC record from verified facts. Pure transformation: no
    network, no registry access, no docker; the caller must supply the
    AUTHENTICATED registry digest of the pushed image, the publishing
    workflow run's head SHA (see the module trust-boundary note), and the
    manifest-verified closed-schema real-Codex qualification facts file
    from which the compatibility section is DERIVED (orders 014-a/014-b,
    workstream B.3) — never independent manual verdict assertions."""
    compatibility_facts = _validate_compatibility(derive_compatibility(repo, qualification_facts))
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
    # Order 014-c, workstream B: bind the record's source identity to the
    # LITERAL supplied source commit (the exact publication workflow head)
    # BEFORE anything is written. An ancestor relationship or a
    # byte-identical wheel is not sufficient — the RC4 defect.
    source_ref_map = verify_source_ref_binding(repo, source, head_sha, recorded_inputs)
    # The manifest's claimed source A must exist and honestly carry the
    # recorded map (the truthful A/B sequence: the manifest describes the
    # exact commit its input map was computed from). A descendant A with
    # an identical map is possible (derived-only child); a drifted A is
    # not — the RC4 rebind is caught by the source-ref map equality above.
    manifest_source = str(manifest.get("generated_from", {}).get("git_commit", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", manifest_source):
        raise RCRecordError("manifest generated_from.git_commit is not 40-hex (fail closed)")
    if (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", manifest_source],
            capture_output=True,
        ).returncode
        != 0
    ):
        raise RCRecordError("manifest generated_from.git_commit does not exist (fail closed)")
    if map_from_git_commit(repo, manifest_source) != recorded_inputs:
        raise RCRecordError(
            "manifest generated_from.git_commit does not carry the recorded "
            "input map (fail closed): the manifest must describe the exact "
            "source commit it was generated from"
        )
    # Dependency-lock and base-image facts are read FROM the source ref,
    # never from a later working tree (order 014-c, workstream B.3).
    dependency_lock_sha256 = hashlib.sha256(_git_blob(repo, source, "uv.lock")).hexdigest()
    dockerfile_text = _git_blob(repo, source, "Dockerfile").decode("utf-8")
    base_images = {
        stage: {"name": fact["name"], "digest": fact["digest"]}
        for stage, fact in _dockerfile_base_images_text(dockerfile_text).items()
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
        "source_input_hashes": source_ref_map,
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
        f"BOTH `{arms['both']}` (derived from the manifest-verified "
        "closed-schema gate facts; bounded genuine Codex sessions with "
        "local tool interaction against the artifact-bound loopback "
        "adapter and the designated backend; this record exists only when "
        "all three PASS — a `blocked` arm would have prevented it)"
    )
    lines.append(
        f"- DIRECT control: `{compat['direct_control']}` (contextual, "
        "derived from the same facts; never a substitute)"
    )
    lines.append(
        f"- Sanitized evidence: `{compat['evidence_path']}` (append-only, "
        "content-free, MANIFEST.sha256-bound)"
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
        f"`rc-candidate-{record['rc_identifier']}; private; not final release`."
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
        "--qualification-facts",
        required=True,
        help=(
            "repo-relative path of the manifest-verified closed-schema "
            "real-Codex qualification facts file; the compatibility "
            "section is derived from it (no manual verdict assertions)"
        ),
    )
    parser.add_argument("--emit", type=Path, default=Path("packaging/rc_record.json"))
    parser.add_argument("--emit-handoff", type=Path, default=HANDOFF_PATH)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    record = build_rc_record(
        repo,
        args.source,
        args.digest,
        args.head_sha,
        args.published_at,
        args.run_id,
        args.qualification_facts,
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
